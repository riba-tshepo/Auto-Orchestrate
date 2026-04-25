"""Improvement recommender for the continuous improvement engine.

Generates prioritized improvement targets from cross-run analysis using
impact x frequency scoring, 3-run confirmation, pattern decay, and
contradictory target detection. Reads retro.json files and improvement_log.jsonl,
writes improvement_targets.json atomically.

Dependencies: Python >= 3.11 stdlib only.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_SCHEMA_VERSION = 1

_VALID_STAGES = frozenset({
    "stage_0", "stage_1", "stage_2", "stage_3",
    "stage_4", "stage_4_5", "stage_5", "stage_6",
    "overall",
})

_VALID_TARGET_STATUSES = frozenset({
    "proposed", "confirmed", "applied", "retired",
})

_VALID_ROOT_CAUSE_CATEGORIES = frozenset({
    "transient", "spec_gap", "dependency", "hallucination",
    "configuration", "resource_exhaustion",
})

_SEVERITY_WEIGHTS: dict[str, float] = {
    "critical": 0.40,
    "high": 0.30,
    "medium": 0.20,
    "low": 0.10,
}

_STAGE_CRITICALITY_WEIGHTS: dict[str, float] = {
    "stage_0": 0.25,
    "stage_1": 0.20,
    "stage_2": 0.20,
    "stage_3": 0.15,
    "stage_5": 0.10,
    "stage_4": 0.05,
    "stage_4_5": 0.03,
    "stage_6": 0.02,
    "overall": 0.15,
}

_METRIC_DEVIATION_CAP = 0.35
_MAX_EVIDENCE_RUNS = 20
_MAX_EXAMPLE_ERRORS = 5
_MAX_ACTION_LENGTH = 500

_RUN_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9\-]{3,128}$")

_CONTRADICTION_PAIRS: list[tuple[str, str]] = [
    ("increase", "decrease"),
    ("add", "remove"),
    ("enable", "disable"),
    ("raise", "lower"),
    ("expand", "reduce"),
]

_NORMALISE_PATTERN = re.compile(
    r"(?:"
    r"(?:/[^\s:]+)"
    r"|(?:line\s+\d+)"
    r"|(?:0x[0-9a-fA-F]+)"
    r"|(?:\b\d{4,}\b)"
    r")",
)

_DEPENDENCY_SIGNALS = (
    "importerror", "modulenotfounderror", "no module named",
    "dependency", "package not found",
)

_TRANSIENT_SIGNALS = (
    "timeout", "rate limit", "429", "503", "transient",
    "connection reset",
)

_HALLUCINATION_SIGNALS = (
    "attributeerror", "has no attribute", "hallucination",
    "incorrect output", "assertionerror",
)

_SPEC_GAP_SIGNALS = (
    "spec", "ambiguous", "undefined behavior",
    "missing requirement", "compliance gap",
)

_write_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _utc_now_iso() -> str:
    """Return current UTC time as ISO 8601 string with Z suffix."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _clamp(value: float, lo: float, hi: float) -> float:
    """Clamp a value to [lo, hi]."""
    return max(lo, min(hi, value))


def _atomic_write_json(target_path: Path, data: dict[str, Any]) -> None:
    """Write JSON atomically via tmp-then-rename with fsync."""
    os.makedirs(target_path.parent, exist_ok=True)
    tmp_path = target_path.with_suffix(target_path.suffix + ".tmp")
    try:
        with open(tmp_path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False, sort_keys=False)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.rename(tmp_path, target_path)
    except BaseException:
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise


def _append_jsonl(target_path: Path, record: dict[str, Any]) -> None:
    """Append a single JSON record to a JSONL file with flush and fsync."""
    os.makedirs(target_path.parent, exist_ok=True)
    with open(target_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False))
        fh.write("\n")
        fh.flush()
        os.fsync(fh.fileno())


def _load_json_safe(path: Path) -> dict[str, Any] | None:
    """Load a JSON file, returning None if the file does not exist."""
    if not path.is_file():
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read all valid records from a JSONL file, skipping bad lines."""
    records: list[dict[str, Any]] = []
    if not path.is_file():
        return records
    with open(path, "r", encoding="utf-8") as fh:
        for line_num, line in enumerate(fh, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                records.append(json.loads(stripped))
            except json.JSONDecodeError:
                logger.warning(
                    "Skipping corrupt JSONL line %d in %s", line_num, path
                )
    return records


def _validate_run_id(run_id: str) -> None:
    """Raise ValueError if run_id is empty or has invalid characters."""
    if not run_id or not isinstance(run_id, str):
        raise ValueError("run_id must be a non-empty string")
    if not _RUN_ID_PATTERN.match(run_id):
        raise ValueError(
            f"run_id '{run_id}' does not match required pattern"
        )


def _normalise_error(text: str) -> str:
    """Strip file paths, line numbers, hex addrs, long numerics."""
    return _NORMALISE_PATTERN.sub("", text).strip().lower()


def _stable_pattern_id(classification: str, normalised: str) -> str:
    """Derive a deterministic fingerprint from classification + text."""
    raw = f"{classification}:{normalised}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]


def _determine_severity(
    overall_status: str | None,
    retry_count: int,
    deviation_pct: float | None,
    spec_compliance: float | None,
) -> str:
    """Classify severity per spec Section 4.5."""
    if overall_status in ("failed", "aborted"):
        return "critical"
    if retry_count > 2:
        return "high"
    if spec_compliance is not None and spec_compliance < 70:
        return "high"
    if retry_count >= 1:
        return "medium"
    if deviation_pct is not None and abs(deviation_pct) > 20.0:
        return "medium"
    return "low"


def _has_contradiction(action_a: str, action_b: str) -> bool:
    """Return True if two action strings contain opposing keywords."""
    lower_a = action_a.lower()
    lower_b = action_b.lower()
    for word_x, word_y in _CONTRADICTION_PAIRS:
        a_has_x = word_x in lower_a
        a_has_y = word_y in lower_a
        b_has_x = word_x in lower_b
        b_has_y = word_y in lower_b
        if (a_has_x and b_has_y) or (a_has_y and b_has_x):
            return True
    return False


def _next_sequential_id(existing_ids: set[str], prefix: str) -> str:
    """Generate the next sequential ID with the given prefix."""
    max_num = 0
    plen = len(prefix)
    for eid in existing_ids:
        if eid.startswith(prefix):
            try:
                max_num = max(max_num, int(eid[plen:]))
            except ValueError:
                pass
    return f"{prefix}{max_num + 1:03d}"


def _classify_text(combined: str) -> str:
    """Classify root cause from combined text signals."""
    if any(kw in combined for kw in _DEPENDENCY_SIGNALS):
        return "dependency"
    if any(kw in combined for kw in _TRANSIENT_SIGNALS):
        return "transient"
    if any(kw in combined for kw in _HALLUCINATION_SIGNALS):
        return "hallucination"
    if any(kw in combined for kw in _SPEC_GAP_SIGNALS):
        return "spec_gap"
    return "spec_gap"


def _derive_action(
    stage: str,
    classification: str,
    root_cause: str,
    observation: str,
) -> str:
    """Derive an actionable improvement description."""
    if root_cause:
        text = f"Address {classification} in {stage}: {root_cause}"
    elif observation:
        text = f"Address {classification} in {stage}: {observation}"
    else:
        text = f"Investigate recurring {classification} issue in {stage}"
    return text[:_MAX_ACTION_LENGTH]


def _cap_list(items: list[str], cap: int) -> list[str]:
    """Return the last `cap` items from a list (FIFO eviction)."""
    return items[-cap:]


def _merge_into_failure_pattern(
    pattern: dict[str, Any],
    obs: dict[str, Any],
) -> None:
    """Merge an observation into an existing failure pattern."""
    pattern["frequency"] = pattern.get("frequency", 0) + 1
    pattern["last_seen"] = obs["last_observed"]
    affected = set(pattern.get("affected_stages", []))
    stage = obs.get("target_stage", "")
    if stage:
        affected.add(stage)
    pattern["affected_stages"] = sorted(affected)
    run_ids = pattern.get("evidence_run_ids", [])
    for rid in obs.get("evidence_runs", []):
        if rid not in run_ids:
            run_ids.append(rid)
    pattern["evidence_run_ids"] = _cap_list(run_ids, _MAX_EVIDENCE_RUNS)
    examples = pattern.get("example_errors", [])
    for err in obs.get("example_errors", []):
        if err and err not in examples:
            examples.append(err)
    pattern["example_errors"] = _cap_list(examples, _MAX_EXAMPLE_ERRORS)
    pattern["severity"] = obs.get("severity", pattern.get("severity", "medium"))


def _create_failure_pattern(
    pattern_id: str,
    obs: dict[str, Any],
) -> dict[str, Any]:
    """Create a new failure pattern from an observation."""
    stage = obs.get("target_stage", "overall")
    action_text = obs.get("action", "")
    first_error = obs["example_errors"][0] if obs.get("example_errors") else ""
    return {
        "pattern_id": pattern_id,
        "failure_mode": (first_error or action_text)[:300],
        "classification": obs.get("classification", "spec_gap"),
        "frequency": len(obs.get("evidence_runs", [])),
        "first_seen": obs["first_observed"],
        "last_seen": obs["last_observed"],
        "affected_stages": [stage] if stage else [],
        "severity": obs.get("severity", "medium"),
        "example_errors": _cap_list(obs.get("example_errors", []), _MAX_EXAMPLE_ERRORS),
        "recommended_action": action_text[:300] if action_text else None,
        "evidence_run_ids": _cap_list(obs.get("evidence_runs", []), _MAX_EVIDENCE_RUNS),
        "decay_score": 1.0,
    }


# ---------------------------------------------------------------------------
# ImprovementRecommender
# ---------------------------------------------------------------------------

@dataclass
class ImprovementRecommender:
    """Generates prioritized improvement targets from cross-run analysis.

    Attributes:
        knowledge_store_path: Root path to the knowledge store directory.
        window_size: Number of recent runs to analyze. Default: 10.
        confirmation_threshold: Minimum evidence runs before confirmation.
        decay_window: Runs after which an unobserved pattern fully decays.
    """

    knowledge_store_path: Path
    window_size: int = 10
    confirmation_threshold: int = 3
    decay_window: int = 10

    def __post_init__(self) -> None:
        self.knowledge_store_path = Path(self.knowledge_store_path)
        if self.window_size < 1:
            raise ValueError(f"window_size must be >= 1, got {self.window_size}")
        if self.confirmation_threshold < 1:
            raise ValueError(
                f"confirmation_threshold must be >= 1, got {self.confirmation_threshold}"
            )
        if self.decay_window < 1:
            raise ValueError(f"decay_window must be >= 1, got {self.decay_window}")

    # -------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------

    def generate_targets(self, run_id: str) -> Path:
        """Generate improvement targets from cross-run analysis.

        Args:
            run_id: The run ID that triggered this generation.

        Returns:
            Path to the written improvement_targets.json file.

        Raises:
            ValueError: If run_id is empty or invalid.
            OSError: If file write operations fail.
        """
        _validate_run_id(run_id)

        retros = self._load_recent_retros()
        total_runs = len(retros)
        run_ids_in_window = self._extract_run_ids(retros)

        context = self._load_all_context()
        observations = self._extract_observations(
            retros, context["log_entries"], run_ids_in_window
        )

        failure_patterns = self._update_failure_patterns(
            context["failure_patterns"], observations, total_runs
        )
        success_patterns = self._update_success_patterns(
            context["success_patterns"], retros, total_runs
        )

        targets = self._build_and_rank_targets(
            observations, context["existing_targets"],
            total_runs, run_ids_in_window, retros, run_id,
        )

        return self._persist_all(
            run_id, total_runs, targets,
            failure_patterns, success_patterns,
        )

    # -------------------------------------------------------------------
    # Data loading
    # -------------------------------------------------------------------

    def _load_recent_retros(self) -> list[dict[str, Any]]:
        """Load retro.json files from recent runs, oldest first."""
        runs_dir = self.knowledge_store_path / "runs"
        if not runs_dir.is_dir():
            return []
        retros: list[dict[str, Any]] = []
        for run_dir in runs_dir.iterdir():
            if not run_dir.is_dir():
                continue
            data = _load_json_safe(run_dir / "retro.json")
            if data is not None:
                retros.append(data)
        retros.sort(key=lambda r: r.get("generated_at", ""))
        return retros[-self.window_size:]

    def _load_all_context(self) -> dict[str, Any]:
        """Load patterns, existing targets, and log entries."""
        return {
            "failure_patterns": self._load_patterns("failure"),
            "success_patterns": self._load_patterns("success"),
            "existing_targets": self._load_existing_targets(),
            "log_entries": self._load_improvement_log(),
        }

    def _load_patterns(self, pattern_type: str) -> dict[str, Any]:
        """Load failure_patterns.json or success_patterns.json."""
        path = self.knowledge_store_path / "patterns" / f"{pattern_type}_patterns.json"
        data = _load_json_safe(path)
        if data is not None:
            return data
        return {
            "schema_version": _SCHEMA_VERSION,
            "updated_at": _utc_now_iso(),
            "total_runs_analyzed": 0,
            "patterns": [],
        }

    def _load_existing_targets(self) -> list[dict[str, Any]]:
        """Load existing improvement_targets.json targets list."""
        path = self.knowledge_store_path / "improvements" / "improvement_targets.json"
        data = _load_json_safe(path)
        if data is not None:
            return data.get("targets", [])
        return []

    def _load_improvement_log(self) -> list[dict[str, Any]]:
        """Load all entries from improvement_log.jsonl."""
        path = self.knowledge_store_path / "improvements" / "improvement_log.jsonl"
        return _read_jsonl(path)

    # -------------------------------------------------------------------
    # Observation extraction
    # -------------------------------------------------------------------

    @staticmethod
    def _extract_run_ids(retros: list[dict[str, Any]]) -> list[str]:
        """Extract ordered unique run/session IDs from retros."""
        ids: list[str] = []
        for retro in retros:
            sid = retro.get("session_id", "")
            if sid and sid not in ids:
                ids.append(sid)
        return ids

    def _extract_observations(
        self,
        retros: list[dict[str, Any]],
        log_entries: list[dict[str, Any]],
        run_ids_in_window: list[str],
    ) -> list[dict[str, Any]]:
        """Extract failure observations from retros and log entries."""
        obs_map: dict[str, dict[str, Any]] = {}
        for retro in retros:
            self._extract_retro_observations(retro, obs_map)
        self._merge_log_observations(log_entries, run_ids_in_window, obs_map)
        return list(obs_map.values())

    def _extract_retro_observations(
        self,
        retro: dict[str, Any],
        obs_map: dict[str, dict[str, Any]],
    ) -> None:
        """Extract observations from a single retro into obs_map."""
        session_id = retro.get("session_id", "")
        generated_at = retro.get("generated_at", _utc_now_iso())

        for item in retro.get("what_went_poorly", []):
            self._merge_poorly_item(
                item, session_id, generated_at, obs_map
            )

    def _merge_poorly_item(
        self,
        item: dict[str, Any],
        session_id: str,
        generated_at: str,
        obs_map: dict[str, dict[str, Any]],
    ) -> None:
        """Merge a single what_went_poorly item into obs_map."""
        stage = item.get("stage", "overall")
        observation_text = item.get("observation", "")
        root_cause = item.get("root_cause", "")

        rc = self._classify_from_retro(item)
        classification = rc["classification"]
        normalised = _normalise_error(observation_text or root_cause)
        fingerprint = _stable_pattern_id(classification, normalised)

        if fingerprint in obs_map:
            entry = obs_map[fingerprint]
            if session_id and session_id not in entry["evidence_runs"]:
                entry["evidence_runs"].append(session_id)
            entry["last_observed"] = generated_at
            entry["example_errors"] = _cap_list(
                entry["example_errors"] + [observation_text],
                _MAX_EXAMPLE_ERRORS,
            )
        else:
            obs_map[fingerprint] = {
                "fingerprint": fingerprint,
                "target_stage": stage,
                "action": _derive_action(
                    stage, classification, root_cause, observation_text
                ),
                "classification": classification,
                "severity": rc["severity"],
                "evidence_runs": [session_id] if session_id else [],
                "first_observed": generated_at,
                "last_observed": generated_at,
                "max_deviation_pct": rc.get("max_deviation_pct"),
                "example_errors": [observation_text] if observation_text else [],
            }

    def _merge_log_observations(
        self,
        log_entries: list[dict[str, Any]],
        run_ids_in_window: list[str],
        obs_map: dict[str, dict[str, Any]],
    ) -> None:
        """Merge improvement log entries into obs_map."""
        for entry in log_entries:
            session_id = entry.get("session_id", "")
            if session_id not in run_ids_in_window:
                continue
            target_stage = entry.get("target_stage", "overall")
            action_text = entry.get("action", "")
            classification = entry.get("root_cause_category") or "spec_gap"
            if classification not in _VALID_ROOT_CAUSE_CATEGORIES:
                classification = "spec_gap"
            timestamp = entry.get("timestamp", _utc_now_iso())
            normalised = _normalise_error(action_text)
            fingerprint = _stable_pattern_id(classification, normalised)

            if fingerprint in obs_map:
                existing = obs_map[fingerprint]
                if session_id not in existing["evidence_runs"]:
                    existing["evidence_runs"].append(session_id)
                existing["last_observed"] = max(
                    existing["last_observed"], timestamp
                )
            else:
                obs_map[fingerprint] = {
                    "fingerprint": fingerprint,
                    "target_stage": target_stage,
                    "action": action_text[:_MAX_ACTION_LENGTH],
                    "classification": classification,
                    "severity": "medium",
                    "evidence_runs": [session_id] if session_id else [],
                    "first_observed": timestamp,
                    "last_observed": timestamp,
                    "max_deviation_pct": None,
                    "example_errors": [],
                }

    def _classify_from_retro(
        self,
        poorly_item: dict[str, Any],
    ) -> dict[str, Any]:
        """Extract classification metadata from a what_went_poorly entry."""
        five_whys = poorly_item.get("five_whys", [])
        root_cause = poorly_item.get("root_cause", "")
        observation = poorly_item.get("observation", "")
        combined = f"{observation} {root_cause} {' '.join(five_whys)}".lower()

        classification = _classify_text(combined)
        severity = _determine_severity(
            poorly_item.get("_overall_status"),
            poorly_item.get("_retry_count", 0),
            poorly_item.get("_deviation_pct"),
            poorly_item.get("_spec_compliance"),
        )
        return {
            "classification": classification,
            "severity": severity,
            "max_deviation_pct": poorly_item.get("_deviation_pct"),
        }

    # -------------------------------------------------------------------
    # Scoring
    # -------------------------------------------------------------------

    def _compute_impact_score(
        self,
        severity: str,
        target_stage: str,
        max_deviation_pct: float | None,
    ) -> float:
        """Compute impact score per spec Section 6.2."""
        severity_w = _SEVERITY_WEIGHTS.get(severity, 0.10)
        stage_w = _STAGE_CRITICALITY_WEIGHTS.get(target_stage, 0.05)
        deviation_w = 0.0
        if max_deviation_pct is not None:
            deviation_w = _clamp(
                abs(max_deviation_pct) / 100.0, 0.0, _METRIC_DEVIATION_CAP
            )
        return round(_clamp(severity_w + stage_w + deviation_w, 0.0, 1.0), 4)

    def _compute_frequency_score(self, occurrences: int) -> float:
        """Compute frequency score per spec Section 6.3."""
        return round(_clamp(occurrences / self.window_size, 0.0, 1.0), 4)

    def _compute_decay_score(self, runs_since_last_seen: int) -> float:
        """Compute decay score per spec Section 6.5."""
        return round(max(0.0, 1.0 - runs_since_last_seen / self.decay_window), 4)

    # -------------------------------------------------------------------
    # Target building and ranking
    # -------------------------------------------------------------------

    def _build_and_rank_targets(
        self,
        observations: list[dict[str, Any]],
        existing_targets: list[dict[str, Any]],
        total_runs: int,
        run_ids_in_window: list[str],
        retros: list[dict[str, Any]],
        run_id: str,
    ) -> list[dict[str, Any]]:
        """Build targets, apply decay/lifecycle/contradictions, rank."""
        targets = self._build_targets(observations, existing_targets)
        targets = self._apply_decay(targets, run_ids_in_window)
        targets = self._detect_contradictions(targets, run_id)
        targets = self._apply_lifecycle_transitions(
            targets, run_ids_in_window, retros
        )
        targets.sort(
            key=lambda t: t.get("_adjusted_score", 0.0), reverse=True
        )
        return targets

    def _build_targets(
        self,
        observations: list[dict[str, Any]],
        existing_targets: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Build target objects from observations, merging with existing."""
        existing_by_fp, used_ids = self._index_existing_targets(
            existing_targets
        )
        targets: list[dict[str, Any]] = []

        for obs in observations:
            target = self._build_single_target(
                obs, existing_by_fp, used_ids
            )
            targets.append(target)

        self._carry_over_unmatched(existing_by_fp, targets)
        return targets

    def _index_existing_targets(
        self,
        existing_targets: list[dict[str, Any]],
    ) -> tuple[dict[str, dict[str, Any]], set[str]]:
        """Build fingerprint->target map and used ID set."""
        by_fp: dict[str, dict[str, Any]] = {}
        used_ids: set[str] = set()
        for target in existing_targets:
            fp = target.get("_fingerprint", "")
            tid = target.get("target_id", "")
            if tid:
                used_ids.add(tid)
            if fp:
                by_fp[fp] = target
        return by_fp, used_ids

    def _build_single_target(
        self,
        obs: dict[str, Any],
        existing_by_fp: dict[str, dict[str, Any]],
        used_ids: set[str],
    ) -> dict[str, Any]:
        """Build one target dict from an observation."""
        fp = obs["fingerprint"]
        evidence_runs = obs["evidence_runs"][-_MAX_EVIDENCE_RUNS:]
        occurrences = len(evidence_runs)

        impact = self._compute_impact_score(
            obs["severity"], obs["target_stage"], obs.get("max_deviation_pct")
        )
        frequency = self._compute_frequency_score(occurrences)
        combined = round(impact * frequency, 4)
        status = "confirmed" if occurrences >= self.confirmation_threshold else "proposed"
        target_id, first_observed, status = self._resolve_existing(
            fp, existing_by_fp, used_ids, obs, status
        )

        root_cause_cat: str | None = obs.get("classification")
        if root_cause_cat and root_cause_cat not in _VALID_ROOT_CAUSE_CATEGORIES:
            root_cause_cat = None

        return {
            "target_id": target_id, "target_stage": obs["target_stage"],
            "action": obs["action"][:_MAX_ACTION_LENGTH],
            "evidence_runs": evidence_runs,
            "impact_score": impact, "frequency_score": frequency,
            "combined_score": combined, "status": status,
            "root_cause_category": root_cause_cat,
            "first_observed": first_observed,
            "last_observed": obs["last_observed"],
            "_fingerprint": fp, "_adjusted_score": combined,
        }

    def _resolve_existing(
        self,
        fp: str,
        existing_by_fp: dict[str, dict[str, Any]],
        used_ids: set[str],
        obs: dict[str, Any],
        status: str,
    ) -> tuple[str, str, str]:
        """Resolve target_id, first_observed, status from existing data."""
        if fp in existing_by_fp:
            prev = existing_by_fp.pop(fp)
            tid = prev.get("target_id") or _next_sequential_id(used_ids, "it-")
            status = self._reconcile_status(prev.get("status", "proposed"), status)
            first = prev.get("first_observed", obs["first_observed"])
        else:
            tid = _next_sequential_id(used_ids, "it-")
            first = obs["first_observed"]
        used_ids.add(tid)
        return tid, first, status

    @staticmethod
    def _reconcile_status(prev_status: str, new_status: str) -> str:
        """Preserve applied/retired status from previous target."""
        if prev_status in ("applied", "retired"):
            return prev_status
        if prev_status == "confirmed" and new_status == "proposed":
            return "confirmed"
        return new_status

    @staticmethod
    def _carry_over_unmatched(
        existing_by_fp: dict[str, dict[str, Any]],
        targets: list[dict[str, Any]],
    ) -> None:
        """Carry over existing targets not matched by observations."""
        for fp, prev in existing_by_fp.items():
            prev["_fingerprint"] = fp
            prev["_adjusted_score"] = prev.get("combined_score", 0.0)
            targets.append(prev)

    # -------------------------------------------------------------------
    # Decay
    # -------------------------------------------------------------------

    def _apply_decay(
        self,
        targets: list[dict[str, Any]],
        run_ids_in_window: list[str],
    ) -> list[dict[str, Any]]:
        """Apply pattern decay to all targets based on staleness."""
        for target in targets:
            evidence = target.get("evidence_runs", [])
            runs_since = self._runs_since_last_seen(
                evidence, run_ids_in_window
            )
            decay = self._compute_decay_score(runs_since)
            combined = target.get("combined_score", 0.0)
            target["_adjusted_score"] = round(combined * decay, 4)
            target["_decay_score"] = decay

            if decay == 0.0 and target.get("status") != "retired":
                target["status"] = "retired"
                logger.info(
                    "Retiring target %s due to full decay",
                    target.get("target_id", "unknown"),
                )
        return targets

    def _runs_since_last_seen(
        self,
        evidence_runs: list[str],
        run_ids_in_window: list[str],
    ) -> int:
        """Count how many runs have elapsed since the last evidence run."""
        if not run_ids_in_window or not evidence_runs:
            return self.decay_window
        latest_index = -1
        for i, rid in enumerate(run_ids_in_window):
            if rid in evidence_runs:
                latest_index = i
        if latest_index < 0:
            return self.decay_window
        return len(run_ids_in_window) - 1 - latest_index

    # -------------------------------------------------------------------
    # Contradiction detection
    # -------------------------------------------------------------------

    def _detect_contradictions(
        self,
        targets: list[dict[str, Any]],
        run_id: str,
    ) -> list[dict[str, Any]]:
        """Detect and resolve contradictory targets per spec Section 6.6."""
        by_stage: dict[str, list[dict[str, Any]]] = {}
        for t in targets:
            by_stage.setdefault(t.get("target_stage", "overall"), []).append(t)

        for stage, group in by_stage.items():
            if len(group) >= 2:
                self._resolve_stage_contradictions(group, stage, run_id)
        return targets

    def _resolve_stage_contradictions(
        self,
        group: list[dict[str, Any]],
        stage: str,
        run_id: str,
    ) -> None:
        """Resolve contradictions within a single stage's targets."""
        group.sort(
            key=lambda x: (
                x.get("_adjusted_score", 0.0),
                x.get("last_observed", ""),
            ),
            reverse=True,
        )
        retired_fps: set[str] = set()
        log_path = self.knowledge_store_path / "improvements" / "improvement_log.jsonl"

        for i in range(len(group)):
            if group[i].get("_fingerprint", "") in retired_fps:
                continue
            for j in range(i + 1, len(group)):
                fp_j = group[j].get("_fingerprint", "")
                if fp_j in retired_fps:
                    continue
                if _has_contradiction(
                    group[i].get("action", ""),
                    group[j].get("action", ""),
                ):
                    group[j]["status"] = "retired"
                    retired_fps.add(fp_j)
                    self._log_contradiction(
                        log_path, run_id, stage, group[i], group[j]
                    )

    def _log_contradiction(
        self,
        log_path: Path,
        run_id: str,
        stage: str,
        winner: dict[str, Any],
        loser: dict[str, Any],
    ) -> None:
        """Append a contradiction resolution entry to the log."""
        logger.info(
            "Contradiction in %s: retiring %s in favor of %s",
            stage,
            loser.get("target_id", "?"),
            winner.get("target_id", "?"),
        )
        record = {
            "schema_version": _SCHEMA_VERSION,
            "timestamp": _utc_now_iso(),
            "session_id": run_id,
            "source": "improvement_recommender",
            "entry_type": "contradiction_resolved",
            "target_stage": stage,
            "retired_target_id": loser.get("target_id", ""),
            "retained_target_id": winner.get("target_id", ""),
            "action": (
                f"Retired '{loser.get('action', '')[:100]}' as "
                f"contradictory to '{winner.get('action', '')[:100]}'"
            ),
            "priority": 0,
            "evidence_runs": 0,
            "status": "retired",
        }
        with _write_lock:
            _append_jsonl(log_path, record)

    # -------------------------------------------------------------------
    # Lifecycle transitions
    # -------------------------------------------------------------------

    def _apply_lifecycle_transitions(
        self,
        targets: list[dict[str, Any]],
        run_ids_in_window: list[str],
        retros: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Apply status transitions per spec Section 3.4."""
        acknowledged_ids = self._collect_acknowledged_ids(retros)

        for target in targets:
            status = target.get("status", "proposed")
            if status == "retired":
                continue
            evidence = target.get("evidence_runs", [])
            target_id = target.get("target_id", "")

            if status == "proposed":
                target["status"] = self._transition_proposed(
                    evidence, run_ids_in_window
                )
            elif status == "confirmed" and target_id in acknowledged_ids:
                target["status"] = "applied"
        return targets

    @staticmethod
    def _collect_acknowledged_ids(
        retros: list[dict[str, Any]],
    ) -> set[str]:
        """Collect target IDs referenced in improvement notes."""
        ids: set[str] = set()
        for retro in retros:
            for note in retro.get("improvement_actions", []):
                tid = note.get("target_id")
                if tid:
                    ids.add(tid)
        return ids

    def _transition_proposed(
        self,
        evidence: list[str],
        run_ids_in_window: list[str],
    ) -> str:
        """Determine new status for a proposed target."""
        if len(evidence) >= self.confirmation_threshold:
            return "confirmed"
        runs_since = self._runs_since_first_seen(evidence, run_ids_in_window)
        if runs_since >= 5:
            return "retired"
        return "proposed"

    @staticmethod
    def _runs_since_first_seen(
        evidence_runs: list[str],
        run_ids_in_window: list[str],
    ) -> int:
        """Count runs since the first evidence run in the window."""
        if not evidence_runs or not run_ids_in_window:
            return 0
        for i, rid in enumerate(run_ids_in_window):
            if rid in evidence_runs:
                return len(run_ids_in_window) - 1 - i
        return len(run_ids_in_window)

    # -------------------------------------------------------------------
    # Pattern file updates
    # -------------------------------------------------------------------

    def _update_failure_patterns(
        self,
        patterns_data: dict[str, Any],
        observations: list[dict[str, Any]],
        total_runs: int,
    ) -> dict[str, Any]:
        """Update failure_patterns.json with new observations.

        After merging observations, applies decay to all patterns based on
        staleness (runs since last seen). Patterns with decay_score == 0.0
        are auto-retired and removed from the active set.
        """
        existing = patterns_data.get("patterns", [])
        by_id, by_fp = self._index_failure_patterns(existing)
        used_ids = set(by_id.keys())

        for obs in observations:
            self._merge_or_create_failure_pattern(
                obs, by_id, by_fp, used_ids
            )

        self._apply_decay_to_patterns(by_id, total_runs)

        active = [
            p for p in by_id.values() if p.get("decay_score", 1.0) > 0.0
        ]
        retired_count = len(by_id) - len(active)
        if retired_count > 0:
            logger.info(
                "Auto-retired %d failure pattern(s) with fully decayed scores",
                retired_count,
            )
        patterns_data["patterns"] = active
        patterns_data["updated_at"] = _utc_now_iso()
        patterns_data["total_runs_analyzed"] = total_runs
        return patterns_data

    def _apply_decay_to_patterns(
        self,
        by_id: dict[str, dict[str, Any]],
        total_runs: int,
    ) -> None:
        """Recompute decay_score for each failure pattern based on staleness.

        Uses _compute_decay_score with an estimate of runs since last seen
        derived from the pattern's last_seen timestamp relative to total_runs.
        Patterns not recently observed receive progressively lower scores.
        """
        for pattern in by_id.values():
            evidence_runs = pattern.get("evidence_run_ids", [])
            frequency = pattern.get("frequency", 0)
            if total_runs <= 0 or frequency <= 0:
                pattern["decay_score"] = 0.0
                continue
            runs_since = max(0, total_runs - frequency)
            decay = self._compute_decay_score(runs_since)
            pattern["decay_score"] = decay

    @staticmethod
    def _index_failure_patterns(
        existing: list[dict[str, Any]],
    ) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
        """Build id->pattern and fingerprint->id maps."""
        by_id: dict[str, dict[str, Any]] = {}
        by_fp: dict[str, str] = {}
        for p in existing:
            pid = p.get("pattern_id", "")
            if not pid:
                continue
            by_id[pid] = p
            mode = p.get("failure_mode", "")
            cls = p.get("classification", "")
            fp = _stable_pattern_id(cls, _normalise_error(mode))
            by_fp[fp] = pid
        return by_id, by_fp

    @staticmethod
    def _merge_or_create_failure_pattern(
        obs: dict[str, Any],
        by_id: dict[str, dict[str, Any]],
        by_fp: dict[str, str],
        used_ids: set[str],
    ) -> None:
        """Merge observation into existing pattern or create new."""
        fp = obs["fingerprint"]
        if fp in by_fp:
            _merge_into_failure_pattern(by_id[by_fp[fp]], obs)
        else:
            new_id = _next_sequential_id(used_ids, "fp-")
            used_ids.add(new_id)
            pattern = _create_failure_pattern(new_id, obs)
            by_id[new_id] = pattern
            by_fp[fp] = new_id

    def _update_success_patterns(
        self,
        patterns_data: dict[str, Any],
        retros: list[dict[str, Any]],
        total_runs: int,
    ) -> dict[str, Any]:
        """Update success_patterns.json from retro what_went_well entries."""
        by_mode, used_ids = self._index_success_patterns(
            patterns_data.get("patterns", [])
        )

        for retro in retros:
            self._process_retro_success(retro, by_mode, used_ids)

        active = [p for p in by_mode.values() if p.get("decay_score", 0.0) > 0.0]
        patterns_data["patterns"] = active
        patterns_data["updated_at"] = _utc_now_iso()
        patterns_data["total_runs_analyzed"] = total_runs
        return patterns_data

    @staticmethod
    def _index_success_patterns(
        existing: list[dict[str, Any]],
    ) -> tuple[dict[str, dict[str, Any]], set[str]]:
        """Build normalised_mode->pattern map and used ID set."""
        by_mode: dict[str, dict[str, Any]] = {}
        used_ids: set[str] = set()
        for p in existing:
            pid = p.get("pattern_id", "")
            mode = _normalise_error(p.get("success_mode", ""))
            if pid:
                used_ids.add(pid)
            if mode:
                by_mode[mode] = p
        return by_mode, used_ids

    def _process_retro_success(
        self,
        retro: dict[str, Any],
        by_mode: dict[str, dict[str, Any]],
        used_ids: set[str],
    ) -> None:
        """Process what_went_well from a single retro."""
        session_id = retro.get("session_id", "")
        generated_at = retro.get("generated_at", _utc_now_iso())

        for item in retro.get("what_went_well", []):
            observation = item.get("observation", "")
            if not observation:
                continue
            stage = item.get("stage", "overall")
            norm = _normalise_error(observation)

            if norm in by_mode:
                self._merge_success_pattern(
                    by_mode[norm], session_id, generated_at, stage
                )
            else:
                new_id = _next_sequential_id(used_ids, "sp-")
                used_ids.add(new_id)
                by_mode[norm] = {
                    "pattern_id": new_id,
                    "success_mode": observation[:500],
                    "associated_stages": [stage] if stage else [],
                    "frequency": 1,
                    "first_seen": generated_at,
                    "last_seen": generated_at,
                    "correlated_metrics": {},
                    "evidence_run_ids": [session_id] if session_id else [],
                    "recommended_practice": None,
                    "confidence": 0.0,
                    "decay_score": 1.0,
                }

    def _merge_success_pattern(
        self,
        pattern: dict[str, Any],
        session_id: str,
        generated_at: str,
        stage: str,
    ) -> None:
        """Merge a new observation into an existing success pattern."""
        pattern["frequency"] = pattern.get("frequency", 0) + 1
        pattern["last_seen"] = generated_at
        stages = set(pattern.get("associated_stages", []))
        if stage:
            stages.add(stage)
        pattern["associated_stages"] = sorted(stages)
        run_ids = pattern.get("evidence_run_ids", [])
        if session_id and session_id not in run_ids:
            run_ids.append(session_id)
        pattern["evidence_run_ids"] = _cap_list(run_ids, _MAX_EVIDENCE_RUNS)
        pattern["confidence"] = self._compute_success_confidence(
            pattern["frequency"], pattern.get("correlated_metrics", {})
        )
        pattern["decay_score"] = 1.0

    @staticmethod
    def _compute_success_confidence(
        frequency: int,
        correlated_metrics: dict[str, Any],
    ) -> float:
        """Compute success pattern confidence per spec Section 5.5."""
        if not correlated_metrics:
            return round(min(1.0, frequency / 5.0 * 0.5), 4)
        improvements = []
        for metric_data in correlated_metrics.values():
            if isinstance(metric_data, dict):
                pct = metric_data.get("improvement_pct", 0.0)
                improvements.append(abs(pct))
        if not improvements:
            return round(min(1.0, frequency / 5.0 * 0.5), 4)
        avg_magnitude = _clamp(
            sum(improvements) / len(improvements) / 100.0, 0.0, 1.0
        )
        return round(min(1.0, (frequency / 5.0) * avg_magnitude), 4)

    # -------------------------------------------------------------------
    # Persistence
    # -------------------------------------------------------------------

    def _persist_all(
        self,
        run_id: str,
        total_runs: int,
        targets: list[dict[str, Any]],
        failure_patterns: dict[str, Any],
        success_patterns: dict[str, Any],
    ) -> Path:
        """Write all output files atomically."""
        clean_targets = self._strip_internal_keys(targets)

        output = {
            "schema_version": _SCHEMA_VERSION,
            "generated_at": _utc_now_iso(),
            "generated_by": "improvement_recommender",
            "run_id": run_id,
            "window_runs": min(total_runs, self.window_size),
            "targets": clean_targets,
        }

        improvements_dir = self.knowledge_store_path / "improvements"
        target_path = improvements_dir / "improvement_targets.json"
        patterns_dir = self.knowledge_store_path / "patterns"

        with _write_lock:
            _atomic_write_json(target_path, output)
            _atomic_write_json(
                patterns_dir / "failure_patterns.json", failure_patterns
            )
            _atomic_write_json(
                patterns_dir / "success_patterns.json", success_patterns
            )

        logger.info(
            "Generated %d improvement targets for run %s "
            "(%d confirmed, %d proposed)",
            len(clean_targets),
            run_id,
            sum(1 for t in clean_targets if t["status"] == "confirmed"),
            sum(1 for t in clean_targets if t["status"] == "proposed"),
        )
        return target_path

    @staticmethod
    def _strip_internal_keys(
        targets: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Remove internal keys (prefixed with _) from target dicts."""
        return [
            {k: v for k, v in t.items() if not k.startswith("_")}
            for t in targets
        ]
