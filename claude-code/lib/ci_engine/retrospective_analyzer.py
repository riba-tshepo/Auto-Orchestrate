"""Retrospective analyzer for the continuous improvement engine.

Implements the Check phase of the PDCA meta-loop. After each orchestration
run, the analyzer loads stage telemetry and run summaries, compares KPIs
against rolling baselines, classifies regressions via 5 Whys root cause
analysis, evaluates automation trigger thresholds, and produces a structured
retro.json artifact with improvement actions appended to improvement_log.jsonl.

All writes are atomic (tmp-then-rename for JSON, deduplicating append for JSONL).
Thread-safe via a module-level threading lock.

Dependencies: Python >= 3.11 stdlib only.
"""

from __future__ import annotations

import fcntl
import json
import logging
import os
import re
import tempfile
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_SCHEMA_VERSION = 1

_SESSION_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9\-]{3,128}$")

_VALID_STAGES = frozenset({
    "stage_0", "stage_1", "stage_2", "stage_3", "stage_4",
    "stage_4_5", "stage_5", "stage_6", "overall",
})

_VALID_FAILURE_CATEGORIES = frozenset({
    "transient", "spec_gap", "dependency", "hallucination",
    "resource_exhaustion", "configuration", "permissions", "timeout",
})

_REGRESSION_THRESHOLD_PCT = 20.0
_IMPROVEMENT_THRESHOLD_PCT = 10.0

_MAX_OBSERVATION_LENGTH = 500
_MAX_ROOT_CAUSE_LENGTH = 300
_MAX_WHY_LENGTH = 200
_MAX_ACTION_LENGTH = 500

_LOCK_TIMEOUT_SECONDS = 5

_IMPROVEMENT_LOG_MAX_LINES = 500
_IMPROVEMENT_LOG_RETAIN_LINES = 250
_IMPROVEMENT_LOG_TTL_RUNS = 30

_write_lock = threading.Lock()

# ---------------------------------------------------------------------------
# Transient error keyword sets for root cause classification
# ---------------------------------------------------------------------------

_TRANSIENT_KEYWORDS = frozenset({
    "timeout", "rate limit", "429", "503", "eagain",
    "connection reset", "temporary", "transient",
})

_DEPENDENCY_KEYWORDS = frozenset({
    "no module named", "cannot import", "package not found",
    "command not found", "modulenotfounderror", "importerror",
})

_HALLUCINATION_KEYWORDS = frozenset({
    "assertionerror", "attributeerror", "has no attribute",
    "unexpected keyword argument", "incorrect output", "wrong result",
    "typeerror",
})

_SPEC_GAP_KEYWORDS = frozenset({
    "not specified", "ambiguous", "undefined behavior",
    "missing requirement", "acceptance criteria gap",
    "spec compliance", "compliance gap",
})


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _utc_now_iso() -> str:
    """Return current UTC time as ISO 8601 string with Z suffix."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _validate_session_id(session_id: str) -> None:
    """Validate session_id against the allowed pattern."""
    if not session_id or not isinstance(session_id, str):
        raise ValueError("session_id must be a non-empty string")
    if ".." in session_id or "/" in session_id or "\\" in session_id:
        raise ValueError(
            f"session_id contains path traversal characters: {session_id!r}"
        )
    if not _SESSION_ID_PATTERN.match(session_id):
        raise ValueError(
            f"session_id does not match required pattern "
            f"'^[a-z0-9][a-z0-9\\-]{{3,128}}$': {session_id!r}"
        )


def _validate_path_within_store(
    resolved_path: Path,
    store_path: Path,
) -> None:
    """Ensure a resolved path stays within the knowledge store."""
    store_resolved = store_path.resolve()
    path_resolved = resolved_path.resolve()
    if not str(path_resolved).startswith(str(store_resolved)):
        raise ValueError(
            f"Path {path_resolved} escapes knowledge store {store_resolved}"
        )


def _clamp_str(value: str, max_length: int) -> str:
    """Truncate a string to max_length."""
    return value[:max_length] if len(value) > max_length else value


def _load_json(path: Path) -> dict[str, Any]:
    """Load a JSON file, raising FileNotFoundError if missing."""
    if not path.is_file():
        raise FileNotFoundError(f"Required file not found: {path}")
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _load_json_optional(path: Path) -> dict[str, Any] | None:
    """Load a JSON file, returning None if it does not exist."""
    if not path.is_file():
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read all valid records from a JSONL file, skipping bad lines."""
    records: list[dict[str, Any]] = []
    if not path.is_file():
        raise FileNotFoundError(f"Required file not found: {path}")
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


def _read_jsonl_optional(path: Path) -> list[dict[str, Any]]:
    """Read JSONL records, returning empty list if file missing."""
    if not path.is_file():
        return []
    records: list[dict[str, Any]] = []
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


def _atomic_write_json(target_path: Path, data: dict[str, Any]) -> None:
    """Write JSON atomically via tmp-then-rename."""
    os.makedirs(target_path.parent, exist_ok=True)
    fd, tmp_path_str = tempfile.mkstemp(
        dir=str(target_path.parent),
        suffix=".tmp",
    )
    tmp_path = Path(tmp_path_str)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False, sort_keys=False)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(str(tmp_path), str(target_path))
    except BaseException:
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise


def _collect_run_summaries(store_path: Path) -> list[dict[str, Any]]:
    """Load all run_summary.json files sorted by completed_at ascending."""
    runs_dir = store_path / "runs"
    if not runs_dir.is_dir():
        return []
    summaries: list[dict[str, Any]] = []
    for run_dir in runs_dir.iterdir():
        if not run_dir.is_dir():
            continue
        summary_path = run_dir / "run_summary.json"
        if summary_path.is_file():
            try:
                with open(summary_path, "r", encoding="utf-8") as fh:
                    summaries.append(json.load(fh))
            except (json.JSONDecodeError, OSError):
                logger.warning("Skipping invalid run summary: %s", summary_path)
    summaries.sort(key=lambda s: s.get("completed_at", ""))
    return summaries


def _format_delta(prev: float | int | None, curr: float | int) -> str:
    """Format a human-readable delta string with sign prefix."""
    if prev is None:
        return "N/A"
    diff = curr - prev
    if isinstance(diff, float) and not diff.is_integer():
        return f"{diff:+.1f}"
    return f"{int(diff):+d}"


def _pct_change(baseline: float, current: float) -> float:
    """Compute percentage change from baseline to current."""
    if baseline == 0.0:
        return 0.0 if current == 0.0 else 100.0
    return ((current - baseline) / abs(baseline)) * 100.0


def _make_poorly_entry(
    stage: str,
    observation: str,
    rc: dict[str, Any],
) -> dict[str, Any]:
    """Build a what_went_poorly entry from classification results."""
    chain = rc.get("five_whys_chain", [])
    return {
        "stage": stage,
        "observation": _clamp_str(observation, _MAX_OBSERVATION_LENGTH),
        "root_cause": _clamp_str(
            chain[-1] if chain else "Unknown root cause",
            _MAX_ROOT_CAUSE_LENGTH,
        ),
        "five_whys": [
            _clamp_str(w, _MAX_WHY_LENGTH) for w in chain[:5]
        ],
    }


# ---------------------------------------------------------------------------
# Root cause classifier (inline, no external dependency)
# ---------------------------------------------------------------------------

def classify_failure(
    error_message: str,
    stage: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Classify a pipeline failure into a root cause category.

    Args:
        error_message: The error message or traceback from the failed stage.
        stage: The pipeline stage where the failure occurred.
        context: Optional additional context with retry_count,
            retry_succeeded, validator_output, spec_sections.

    Returns:
        Dictionary with category, confidence, and five_whys_chain.

    Raises:
        ValueError: If error_message is empty or stage is invalid.
    """
    if not error_message or not isinstance(error_message, str):
        raise ValueError("error_message must be a non-empty string")
    if not stage or not isinstance(stage, str):
        raise ValueError("stage must be a non-empty string")

    ctx = context or {}
    scores = _compute_category_scores(error_message, ctx)

    best_category = max(scores, key=lambda k: scores[k])
    best_confidence = scores[best_category]
    if best_confidence == 0.0:
        best_category = "spec_gap"
        best_confidence = 0.3

    five_whys = _generate_five_whys(
        error_message, stage, best_category, ctx
    )

    return {
        "category": best_category,
        "confidence": round(best_confidence, 2),
        "five_whys_chain": five_whys,
    }


def _compute_category_scores(
    error_message: str,
    ctx: dict[str, Any],
) -> dict[str, float]:
    """Score each failure category based on keyword matching."""
    error_lower = error_message.lower()
    validator_output = ctx.get("validator_output", "")
    validator_lower = validator_output.lower() if validator_output else ""
    retry_count = ctx.get("retry_count", 0)
    retry_succeeded = ctx.get("retry_succeeded", False)

    scores: dict[str, float] = {
        "transient": 0.0, "dependency": 0.0,
        "spec_gap": 0.0, "hallucination": 0.0,
    }

    scores["dependency"] = _score_dependency(error_lower)
    scores["transient"] = _score_transient(
        error_lower, retry_count, retry_succeeded
    )
    scores["spec_gap"] = _score_spec_gap(error_lower, validator_lower)
    scores["hallucination"] = _score_hallucination(error_lower)
    return scores


def _score_dependency(error_lower: str) -> float:
    """Score dependency category."""
    if "importerror" in error_lower or "modulenotfounderror" in error_lower:
        return 0.95
    hits = sum(1 for kw in _DEPENDENCY_KEYWORDS if kw in error_lower)
    return min(0.7 + hits * 0.1, 0.9) if hits > 0 else 0.0


def _score_transient(
    error_lower: str, retry_count: int, retry_succeeded: bool,
) -> float:
    """Score transient category."""
    score = 0.0
    if retry_succeeded and retry_count > 0:
        score = 0.8
    hits = sum(1 for kw in _TRANSIENT_KEYWORDS if kw in error_lower)
    if hits > 0:
        score = max(score, min(0.5 + hits * 0.1, 0.85))
    return score


def _score_spec_gap(error_lower: str, validator_lower: str) -> float:
    """Score spec_gap category."""
    hits = sum(
        1 for kw in _SPEC_GAP_KEYWORDS
        if kw in error_lower or kw in validator_lower
    )
    score = min(0.5 + hits * 0.1, 0.85) if hits > 0 else 0.0
    if "spec_compliance" in validator_lower:
        score = max(score, 0.7)
    return score


def _score_hallucination(error_lower: str) -> float:
    """Score hallucination category."""
    hits = sum(1 for kw in _HALLUCINATION_KEYWORDS if kw in error_lower)
    return min(0.5 + hits * 0.15, 0.85) if hits > 0 else 0.0


def _generate_five_whys(
    error_message: str,
    stage: str,
    category: str,
    context: dict[str, Any],
) -> list[str]:
    """Generate a 5 Whys chain based on the failure category."""
    error_short = _clamp_str(error_message.strip(), _MAX_WHY_LENGTH)
    first = _clamp_str(f"{stage} failed: {error_short}", _MAX_WHY_LENGTH)

    templates: dict[str, list[str]] = {
        "dependency": _whys_dependency(stage),
        "transient": _whys_transient(context.get("retry_count", 0)),
        "hallucination": _whys_hallucination(),
        "spec_gap": _whys_spec_gap(),
    }
    tail = templates.get(category, templates["spec_gap"])
    return ([first] + tail)[:5]


def _whys_dependency(stage: str) -> list[str]:
    """Tail whys for dependency failures."""
    return [
        "Required dependency is not available in the execution environment",
        f"{stage} assumed the dependency was installed based on earlier stage output",
        "The specification did not include explicit dependency verification",
        "Stage 0 research did not verify dependency availability before recommending it",
    ]


def _whys_transient(retry_count: int) -> list[str]:
    """Tail whys for transient failures."""
    whys = [
        "A transient error occurred (network, rate limit, or resource exhaustion)",
        "No retry-with-backoff strategy was configured for this failure mode",
    ]
    if retry_count > 0:
        whys.append(f"The stage required {retry_count} retries before resolution")
    whys.append(
        "The specification did not mandate resilience patterns for external calls"
    )
    return whys


def _whys_hallucination() -> list[str]:
    """Tail whys for hallucination failures."""
    return [
        "The generated code is syntactically valid but semantically incorrect",
        "The LLM produced output that does not match the actual API or expected behavior",
        "The specification did not provide reference implementations or example I/O pairs",
        "Stage 0 research did not include verified API signatures or usage examples",
    ]


def _whys_spec_gap() -> list[str]:
    """Tail whys for spec gap failures."""
    return [
        "The implementation followed the specification but the spec was insufficient",
        "Key requirements or edge cases were not enumerated in the specification",
        "The spec-creator stage did not surface all acceptance criteria",
        "Stage 0 research did not identify known edge cases from prior failure patterns",
    ]


# ---------------------------------------------------------------------------
# Improvement log append with file locking and deduplication
# ---------------------------------------------------------------------------

def _acquire_lock(lock_path: Path) -> int:
    """Acquire an advisory file lock, returning the lock file descriptor."""
    os.makedirs(lock_path.parent, exist_ok=True)
    lock_fd = os.open(str(lock_path), os.O_CREAT | os.O_RDWR)
    try:
        import signal

        def _timeout_handler(signum: int, frame: Any) -> None:
            raise TimeoutError(
                f"Could not acquire lock on {lock_path} "
                f"within {_LOCK_TIMEOUT_SECONDS} seconds"
            )

        old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(_LOCK_TIMEOUT_SECONDS)
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX)
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
    except (TimeoutError, OSError):
        os.close(lock_fd)
        raise
    return lock_fd


def _release_lock(lock_fd: int, lock_path: Path) -> None:
    """Release an advisory file lock and clean up."""
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
    finally:
        os.close(lock_fd)
    try:
        lock_path.unlink(missing_ok=True)
    except OSError:
        pass


def _read_existing_log(
    log_path: Path,
) -> tuple[list[str], set[tuple[str, str, str]]]:
    """Read existing JSONL lines and extract dedup keys."""
    lines: list[str] = []
    keys: set[tuple[str, str, str]] = set()
    if not log_path.is_file():
        return lines, keys
    with open(log_path, "r", encoding="utf-8") as fh:
        for line in fh:
            stripped = line.strip()
            if not stripped:
                continue
            lines.append(stripped)
            try:
                record = json.loads(stripped)
                keys.add((
                    record.get("session_id", ""),
                    record.get("target_stage", ""),
                    record.get("action", ""),
                ))
            except json.JSONDecodeError:
                pass
    return lines, keys


def _deduplicate_entries(
    entries: list[dict[str, Any]],
    existing_keys: set[tuple[str, str, str]],
) -> list[str]:
    """Return JSON strings for entries not already in existing_keys."""
    new_lines: list[str] = []
    for entry in entries:
        key = (
            entry.get("session_id", ""),
            entry.get("target_stage", ""),
            entry.get("action", ""),
        )
        if key in existing_keys:
            logger.debug(
                "Skipping duplicate improvement entry: %s/%s",
                key[1], key[2][:60],
            )
            continue
        existing_keys.add(key)
        new_lines.append(json.dumps(entry, ensure_ascii=False))
    return new_lines


def _write_lines_atomically(
    log_path: Path,
    all_lines: list[str],
) -> None:
    """Write all lines to log_path via tmp-then-replace."""
    fd, tmp_str = tempfile.mkstemp(
        dir=str(log_path.parent), suffix=".tmp",
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            for line_str in all_lines:
                fh.write(line_str)
                fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_str, str(log_path))
    except BaseException:
        try:
            Path(tmp_str).unlink(missing_ok=True)
        except OSError:
            pass
        raise


def _rotate_improvement_log(log_path: Path, all_lines: list[str]) -> list[str]:
    """Rotate the improvement log when it exceeds the max line threshold.

    Renames the current file to ``<name>.1`` as a backup, then returns
    only the newest ``_IMPROVEMENT_LOG_RETAIN_LINES`` entries for the
    fresh file.
    """
    if len(all_lines) <= _IMPROVEMENT_LOG_MAX_LINES:
        return all_lines

    archive_path = log_path.with_name(log_path.name + ".1")
    try:
        if log_path.is_file():
            os.replace(str(log_path), str(archive_path))
            logger.info(
                "Rotated improvement log to %s (%d lines archived)",
                archive_path,
                len(all_lines),
            )
    except OSError:
        logger.warning(
            "Failed to rotate improvement log to %s", archive_path
        )

    retained = all_lines[-_IMPROVEMENT_LOG_RETAIN_LINES:]
    logger.info(
        "Retained newest %d entries after rotation", len(retained)
    )
    return retained


def _prune_old_entries(lines: list[str]) -> list[str]:
    """Remove entries whose run_sequence is more than 30 runs old.

    Determines the current (newest) run_sequence from the last entry
    that has the field, then filters out entries that are too old.
    Entries without a ``run_sequence`` field are always retained.
    """
    if not lines:
        return lines

    newest_seq: int | None = None
    for raw_line in reversed(lines):
        try:
            record = json.loads(raw_line)
            seq = record.get("run_sequence")
            if seq is not None:
                newest_seq = int(seq)
                break
        except (json.JSONDecodeError, ValueError, TypeError):
            continue

    if newest_seq is None:
        return lines

    cutoff = newest_seq - _IMPROVEMENT_LOG_TTL_RUNS
    pruned: list[str] = []
    removed = 0
    for raw_line in lines:
        try:
            record = json.loads(raw_line)
            seq = record.get("run_sequence")
            if seq is not None and int(seq) < cutoff:
                removed += 1
                continue
        except (json.JSONDecodeError, ValueError, TypeError):
            pass
        pruned.append(raw_line)

    if removed > 0:
        logger.info(
            "Pruned %d entries older than run_sequence %d (cutoff %d)",
            removed,
            newest_seq,
            cutoff,
        )
    return pruned


def _append_improvement_entries(
    log_path: Path,
    session_id: str,
    entries: list[dict[str, Any]],
) -> None:
    """Append improvement entries with locking, dedup, TTL, and rotation."""
    if not entries:
        return

    os.makedirs(log_path.parent, exist_ok=True)
    lock_path = log_path.with_suffix(log_path.suffix + ".lock")

    lock_fd = _acquire_lock(lock_path)
    try:
        existing_lines, existing_keys = _read_existing_log(log_path)
        new_lines = _deduplicate_entries(entries, existing_keys)
        if not new_lines:
            return

        combined = existing_lines + new_lines
        combined = _prune_old_entries(combined)
        combined = _rotate_improvement_log(log_path, combined)

        _write_lines_atomically(log_path, combined)
        logger.info(
            "Appended %d improvement entries to %s", len(new_lines), log_path
        )
    finally:
        _release_lock(lock_fd, lock_path)


# ---------------------------------------------------------------------------
# RetrospectiveAnalyzer
# ---------------------------------------------------------------------------

@dataclass
class RetrospectiveAnalyzer:
    """Generates structured retrospective analysis for completed pipeline runs.

    Implements the Check phase of the PDCA meta-loop. Loads per-stage
    telemetry, compares against rolling baselines, classifies regressions
    and improvements, applies 5 Whys root cause analysis, and produces
    a retro.json artifact.

    Attributes:
        knowledge_store_path: Root path to the knowledge store directory.
        session_id: Orchestration session identifier for the run.
        baseline_window: Number of prior runs in the rolling baseline.
        smoothing_alpha: Exponential smoothing factor for baselines.
    """

    knowledge_store_path: Path
    session_id: str
    baseline_window: int = 10
    smoothing_alpha: float = 0.3

    def __post_init__(self) -> None:
        self.knowledge_store_path = Path(self.knowledge_store_path)
        _validate_session_id(self.session_id)
        if not (0.0 < self.smoothing_alpha < 1.0):
            raise ValueError(
                f"smoothing_alpha must be in (0.0, 1.0), got {self.smoothing_alpha}"
            )
        if self.baseline_window < 1:
            raise ValueError(
                f"baseline_window must be >= 1, got {self.baseline_window}"
            )

    def analyze_run(self) -> dict[str, Any]:
        """Execute full retrospective analysis for the current session.

        Returns:
            The retro.json content as a Python dictionary.

        Raises:
            FileNotFoundError: If required input files do not exist.
            ValueError: If input data fails validation.
            OSError: If atomic write operations fail.
        """
        telemetry = self._load_telemetry()
        run_summary = self._load_run_summary()
        baselines = self._load_baselines()
        recent_runs = self._load_recent_runs()

        current_kpis = self._extract_current_kpis(run_summary, telemetry)
        kpi_delta = self._compute_kpi_deltas(current_kpis, baselines)

        well, poorly = self._analyze_stages(run_summary, baselines)
        self._add_overall_observation(well, poorly, run_summary)

        trigger_actions = self._evaluate_triggers(
            run_summary, baselines, recent_runs
        )
        improvement_actions = self._build_improvement_actions(
            poorly, trigger_actions
        )

        retro = self._assemble_retro(
            well, poorly, improvement_actions, kpi_delta
        )
        self._persist_retro(retro, improvement_actions, poorly)
        return retro

    def _analyze_stages(
        self,
        run_summary: dict[str, Any],
        baselines: dict[str, Any] | None,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Classify each stage and build well/poorly lists."""
        stages_data = run_summary.get("stages", {})
        baseline_stages = baselines.get("stages", {}) if baselines else {}
        well: list[dict[str, Any]] = []
        poorly: list[dict[str, Any]] = []

        for stage_name in sorted(stages_data.keys()):
            stage_info = stages_data[stage_name]
            canon = self._canonicalize_stage(stage_name)
            if canon not in _VALID_STAGES:
                continue

            bl = baseline_stages.get(stage_name)
            cur = self._extract_stage_metrics(stage_info)
            bl_m = self._extract_baseline_metrics(bl) if bl else None
            cls = self._classify_stage(stage_name, cur, bl_m)

            if cls == "improvement":
                self._append_well_item(well, canon, cur, bl_m)
            elif cls == "regression":
                self._append_regression_item(poorly, canon, cur, bl_m, stage_info)

            self._append_failure_item(poorly, canon, stage_info, cls)

        return well, poorly

    def _append_well_item(
        self,
        well: list[dict[str, Any]],
        canon: str,
        cur: dict[str, float],
        bl_m: dict[str, float] | None,
    ) -> None:
        """Append a positive observation for an improved stage."""
        obs = self._build_improvement_observation(canon, cur, bl_m)
        well.append({
            "stage": canon,
            "observation": _clamp_str(obs, _MAX_OBSERVATION_LENGTH),
        })

    def _append_regression_item(
        self,
        poorly: list[dict[str, Any]],
        canon: str,
        cur: dict[str, float],
        bl_m: dict[str, float] | None,
        stage_info: dict[str, Any],
    ) -> None:
        """Append a negative observation with root cause for a regression."""
        obs = self._build_regression_observation(canon, cur, bl_m, stage_info)
        errors = stage_info.get("errors", [])
        error_msg = "; ".join(str(e) for e in errors) if errors else obs
        rc = classify_failure(
            error_message=error_msg,
            stage=canon,
            context={
                "retry_count": stage_info.get("retry_count", 0),
                "retry_succeeded": stage_info.get("status") == "success",
            },
        )
        poorly.append(_make_poorly_entry(canon, obs, rc))

    @staticmethod
    def _append_failure_item(
        poorly: list[dict[str, Any]],
        canon: str,
        stage_info: dict[str, Any],
        classification: str,
    ) -> None:
        """Append a negative observation for failed stages (non-regression)."""
        status = stage_info.get("status", "")
        if classification == "regression":
            return
        if status not in ("failed", "partial"):
            return
        errors = stage_info.get("errors", [])
        if not errors:
            return

        error_msg = "; ".join(str(e) for e in errors)
        rc = classify_failure(
            error_message=error_msg,
            stage=canon,
            context={
                "retry_count": stage_info.get("retry_count", 0),
                "retry_succeeded": status != "failed",
            },
        )
        obs = (
            f"{canon} completed with status '{status}'; "
            f"{len(errors)} errors: {errors[0]}"
        )
        retry = stage_info.get("retry_count", 0)
        if retry > 0:
            obs += f"; {retry} retries"
        poorly.append(_make_poorly_entry(canon, obs, rc))

    @staticmethod
    def _add_overall_observation(
        well: list[dict[str, Any]],
        poorly: list[dict[str, Any]],
        run_summary: dict[str, Any],
    ) -> None:
        """Add overall-level observation if all stages succeeded."""
        if run_summary.get("overall_status") == "success" and not poorly:
            well.append({
                "stage": "overall",
                "observation": _clamp_str(
                    "All stages completed successfully with no regressions",
                    _MAX_OBSERVATION_LENGTH,
                ),
            })

    def _assemble_retro(
        self,
        well: list[dict[str, Any]],
        poorly: list[dict[str, Any]],
        actions: list[dict[str, Any]],
        kpi_delta: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """Assemble the retro.json dict, stripping internal keys."""
        clean = [
            {k: v for k, v in a.items() if not k.startswith("_")}
            for a in actions
        ]
        return {
            "schema_version": _SCHEMA_VERSION,
            "session_id": self.session_id,
            "generated_at": _utc_now_iso(),
            "what_went_well": well,
            "what_went_poorly": poorly,
            "improvement_actions": clean,
            "kpi_delta": kpi_delta,
        }

    def _persist_retro(
        self,
        retro: dict[str, Any],
        actions: list[dict[str, Any]],
        poorly: list[dict[str, Any]],
    ) -> None:
        """Write retro.json and append to improvement_log.jsonl."""
        retro_path = (
            self.knowledge_store_path / "runs" / self.session_id / "retro.json"
        )
        _validate_path_within_store(retro_path, self.knowledge_store_path)
        with _write_lock:
            _atomic_write_json(retro_path, retro)
        logger.info("Wrote retro.json for session %s", self.session_id)

        log_entries = self._build_log_entries(actions, poorly)
        if log_entries:
            log_path = (
                self.knowledge_store_path
                / "improvements"
                / "improvement_log.jsonl"
            )
            _validate_path_within_store(log_path, self.knowledge_store_path)
            _append_improvement_entries(log_path, self.session_id, log_entries)

    # -------------------------------------------------------------------
    # Data loading
    # -------------------------------------------------------------------

    def _load_telemetry(self) -> list[dict[str, Any]]:
        """Load stage_telemetry.jsonl for the current session."""
        path = (
            self.knowledge_store_path
            / "runs"
            / self.session_id
            / "stage_telemetry.jsonl"
        )
        _validate_path_within_store(path, self.knowledge_store_path)
        return _read_jsonl(path)

    def _load_run_summary(self) -> dict[str, Any]:
        """Load run_summary.json for the current session.

        Falls back to reconstructing a minimal summary from telemetry
        when the file is missing or contains corrupt JSON.
        """
        path = (
            self.knowledge_store_path
            / "runs"
            / self.session_id
            / "run_summary.json"
        )
        _validate_path_within_store(path, self.knowledge_store_path)
        try:
            return _load_json(path)
        except FileNotFoundError:
            logger.warning(
                "run_summary.json not found for session %s; "
                "reconstructing from telemetry",
                self.session_id,
            )
            return self._reconstruct_summary_from_telemetry()
        except json.JSONDecodeError:
            logger.warning(
                "run_summary.json contains invalid JSON for session %s; "
                "reconstructing from telemetry",
                self.session_id,
            )
            return self._reconstruct_summary_from_telemetry()

    def _reconstruct_summary_from_telemetry(self) -> dict[str, Any]:
        """Build a minimal run summary from stage_telemetry.jsonl.

        Reads all stage_end events from telemetry and infers the overall
        run status from individual stage statuses.  Returns a dict
        compatible with the shape expected by downstream analysis methods.
        """
        telemetry_path = (
            self.knowledge_store_path
            / "runs"
            / self.session_id
            / "stage_telemetry.jsonl"
        )
        _validate_path_within_store(
            telemetry_path, self.knowledge_store_path
        )
        events = _read_jsonl_optional(telemetry_path)

        stages: dict[str, dict[str, Any]] = {}
        for event in events:
            if event.get("event") != "stage_end":
                continue
            stage_name = event.get("stage", "")
            if not stage_name:
                continue
            status = event.get("status", "unknown")
            stages[stage_name] = {
                "status": status,
                "duration_seconds": event.get("duration_seconds"),
                "errors": event.get("errors", []),
                "retry_count": event.get("retry_count", 0),
            }

        statuses = {s.get("status") for s in stages.values()}
        if not stages:
            overall_status = "unknown"
        elif statuses <= {"success"}:
            overall_status = "success"
        elif "failure" in statuses or "error" in statuses:
            overall_status = "failure"
        else:
            overall_status = "partial"

        logger.info(
            "Reconstructed summary from telemetry for session %s "
            "with %d stages (overall: %s)",
            self.session_id,
            len(stages),
            overall_status,
        )

        return {
            "run_id": self.session_id,
            "session_id": self.session_id,
            "overall_status": overall_status,
            "stages": stages,
            "kpis": {},
            "completed_at": _utc_now_iso(),
            "_reconstructed_from_telemetry": True,
        }

    def _load_baselines(self) -> dict[str, Any] | None:
        """Load stage_baselines.json if it exists."""
        path = (
            self.knowledge_store_path / "baselines" / "stage_baselines.json"
        )
        return _load_json_optional(path)

    def _load_recent_runs(self) -> list[dict[str, Any]]:
        """Load the most recent run summaries for consecutive-run checks."""
        all_summaries = _collect_run_summaries(self.knowledge_store_path)
        return all_summaries[-self.baseline_window:]

    # -------------------------------------------------------------------
    # KPI extraction and comparison
    # -------------------------------------------------------------------

    def _extract_current_kpis(
        self,
        run_summary: dict[str, Any],
        telemetry: list[dict[str, Any]],
    ) -> dict[str, float | None]:
        """Extract recognized KPI values from the run summary."""
        kpis_data = run_summary.get("kpis", {})
        stages = run_summary.get("stages", {})

        total_errors = sum(
            len(s.get("errors", []))
            for s in stages.values()
        )
        total_retries = sum(
            s.get("retry_count", 0)
            for s in stages.values()
        )
        total_stages = len(stages)
        success_count = sum(
            1 for s in stages.values()
            if s.get("status") == "success"
        )
        success_rate = (
            (success_count / total_stages * 100.0) if total_stages > 0 else 0.0
        )

        return {
            "spec_compliance_score": kpis_data.get("spec_compliance_score"),
            "total_duration_s": kpis_data.get("total_duration_seconds"),
            "test_coverage_pct": kpis_data.get("test_coverage_pct"),
            "stage_error_count": float(total_errors),
            "stage_retry_count": float(total_retries),
            "stage_success_rate": round(success_rate, 1),
        }

    def _compute_kpi_deltas(
        self,
        current_kpis: dict[str, float | None],
        baselines: dict[str, Any] | None,
    ) -> dict[str, dict[str, Any]]:
        """Compute KPI deltas between current values and baselines."""
        baseline_kpis = self._extract_baseline_kpis(baselines)
        result: dict[str, dict[str, Any]] = {}

        for kpi_name, curr_val in current_kpis.items():
            if curr_val is None:
                continue
            prev_val = baseline_kpis.get(kpi_name)
            result[kpi_name] = {
                "prev": prev_val,
                "curr": curr_val,
                "delta": _format_delta(prev_val, curr_val),
            }

        return result

    def _extract_baseline_kpis(
        self,
        baselines: dict[str, Any] | None,
    ) -> dict[str, float | None]:
        """Extract aggregate KPI baselines from stage_baselines.json."""
        if baselines is None:
            return {}
        stages_bl = baselines.get("stages", {})
        if not stages_bl:
            return {}

        total_dur = total_err = total_ret = total_succ = 0.0
        count = 0
        for sd in stages_bl.values():
            total_dur += sd.get("duration_seconds", {}).get("smoothed", 0.0)
            total_err += sd.get("error_rate", {}).get("smoothed", 0.0)
            total_ret += sd.get("retry_rate", {}).get("smoothed", 0.0)
            total_succ += sd.get("success_rate", {}).get("smoothed", 0.0)
            count += 1

        avg_succ = (total_succ / count * 100.0) if count > 0 else 0.0
        return {
            "total_duration_s": total_dur,
            "stage_error_count": total_err * count,
            "stage_retry_count": total_ret * count,
            "stage_success_rate": round(avg_succ, 1),
            "spec_compliance_score": None,
            "test_coverage_pct": None,
        }

    # -------------------------------------------------------------------
    # Stage classification
    # -------------------------------------------------------------------

    def _extract_stage_metrics(
        self, stage_info: dict[str, Any],
    ) -> dict[str, float]:
        """Extract numeric metrics from a stage entry."""
        tc = stage_info.get("token_count", {})
        return {
            "duration_seconds": float(stage_info.get("duration_seconds", 0.0)),
            "error_count": float(len(stage_info.get("errors", []))),
            "retry_count": float(stage_info.get("retry_count", 0)),
            "token_count": float(
                tc.get("input", 0) + tc.get("output", 0)
                if isinstance(tc, dict) else 0
            ),
        }

    def _extract_baseline_metrics(
        self, stage_baseline: dict[str, Any],
    ) -> dict[str, float]:
        """Extract smoothed baseline metrics for a stage."""
        dur = stage_baseline.get("duration_seconds", {})
        err = stage_baseline.get("error_rate", {})
        ret = stage_baseline.get("retry_rate", {})
        tok = stage_baseline.get("token_count_avg", {})
        return {
            "duration_seconds": dur.get("smoothed", 0.0),
            "error_count": err.get("smoothed", 0.0),
            "retry_count": ret.get("smoothed", 0.0),
            "token_count": tok.get("smoothed", 0.0),
        }

    def _classify_stage(
        self,
        stage: str,
        current_metrics: dict[str, float],
        baseline_metrics: dict[str, float] | None,
    ) -> str:
        """Classify a stage as regression, improvement, or steady.

        Regression: >20% unfavorable deviation (latency increase or error increase).
        Improvement: >10% favorable deviation.
        Steady: within [-10%, +20%] band.
        """
        if baseline_metrics is None:
            return "steady"
        dur_c = current_metrics.get("duration_seconds", 0.0)
        dur_b = baseline_metrics.get("duration_seconds", 0.0)
        err_c = current_metrics.get("error_count", 0.0)
        err_b = baseline_metrics.get("error_count", 0.0)

        if self._is_regression(dur_b, dur_c, err_b, err_c):
            return "regression"
        if self._is_improvement(dur_b, dur_c, err_b, err_c):
            return "improvement"
        return "steady"

    @staticmethod
    def _is_regression(
        dur_b: float, dur_c: float, err_b: float, err_c: float,
    ) -> bool:
        """Check if metrics indicate a regression (>20% unfavorable)."""
        if dur_b > 0.0 and _pct_change(dur_b, dur_c) > _REGRESSION_THRESHOLD_PCT:
            return True
        if err_c > err_b:
            if err_b == 0.0 and err_c > 0:
                return True
            if err_b > 0.0 and _pct_change(err_b, err_c) > _REGRESSION_THRESHOLD_PCT:
                return True
        return False

    @staticmethod
    def _is_improvement(
        dur_b: float, dur_c: float, err_b: float, err_c: float,
    ) -> bool:
        """Check if metrics indicate an improvement (>10% favorable)."""
        if dur_b > 0.0 and _pct_change(dur_b, dur_c) < -_IMPROVEMENT_THRESHOLD_PCT:
            return True
        if err_b > 0.0 and err_c == 0.0:
            return True
        if err_b > 0.0 and _pct_change(err_b, err_c) < -_IMPROVEMENT_THRESHOLD_PCT:
            return True
        return False

    # -------------------------------------------------------------------
    # Observation builders
    # -------------------------------------------------------------------

    @staticmethod
    def _canonicalize_stage(stage_name: str) -> str:
        """Normalize stage names like 'stage_4.5' to 'stage_4_5'."""
        return stage_name.replace(".", "_")

    @staticmethod
    def _build_improvement_observation(
        stage: str,
        current: dict[str, float],
        baseline: dict[str, float] | None,
    ) -> str:
        """Build observation text for a stage improvement."""
        dur_curr = current.get("duration_seconds", 0.0)
        if baseline:
            dur_bl = baseline.get("duration_seconds", 0.0)
            if dur_bl > 0:
                pct = abs(_pct_change(dur_bl, dur_curr))
                return (
                    f"{stage} latency improved: {dur_curr:.1f}s "
                    f"vs {dur_bl:.1f}s baseline ({pct:.0f}% reduction)"
                )
        return f"{stage} completed in {dur_curr:.1f}s with no errors"

    @staticmethod
    def _build_regression_observation(
        stage: str,
        current: dict[str, float],
        baseline: dict[str, float] | None,
        stage_info: dict[str, Any],
    ) -> str:
        """Build observation text for a stage regression."""
        parts: list[str] = []
        dur_curr = current.get("duration_seconds", 0.0)
        err_curr = current.get("error_count", 0.0)
        retry = stage_info.get("retry_count", 0)

        if baseline:
            dur_bl = baseline.get("duration_seconds", 0.0)
            if dur_bl > 0:
                pct = _pct_change(dur_bl, dur_curr)
                if pct > _REGRESSION_THRESHOLD_PCT:
                    parts.append(
                        f"latency {pct:.0f}% above baseline "
                        f"({dur_curr:.1f}s vs {dur_bl:.1f}s)"
                    )

        if err_curr > 0:
            parts.append(f"{int(err_curr)} errors")
        if retry > 0:
            parts.append(f"{retry} retries required")

        detail = ", ".join(parts) if parts else "regression detected"
        return f"{stage}: {detail}"

    @staticmethod
    def _build_failure_observation(
        stage: str,
        stage_info: dict[str, Any],
    ) -> str:
        """Build observation text for a failed stage."""
        status = stage_info.get("status", "failed")
        errors = stage_info.get("errors", [])
        retry = stage_info.get("retry_count", 0)
        parts = [f"{stage} completed with status '{status}'"]
        if errors:
            parts.append(f"{len(errors)} errors: {errors[0]}")
        if retry > 0:
            parts.append(f"{retry} retries")
        return "; ".join(parts)

    # -------------------------------------------------------------------
    # Automation triggers (Section 4)
    # -------------------------------------------------------------------

    def _evaluate_triggers(
        self,
        run_summary: dict[str, Any],
        baselines: dict[str, Any] | None,
        recent_runs: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Evaluate all five automation triggers in order."""
        triggers: list[dict[str, Any]] = []
        kpis = run_summary.get("kpis", {})
        stages = run_summary.get("stages", {})

        self._check_trigger_001(triggers, kpis, recent_runs)
        self._check_trigger_002(triggers, stages, recent_runs)
        self._check_trigger_003(triggers, kpis, stages, baselines, recent_runs)
        self._check_trigger_004(triggers, kpis, recent_runs)
        self._check_trigger_005(triggers, run_summary, recent_runs)
        return triggers

    def _check_trigger_001(
        self,
        out: list[dict[str, Any]],
        kpis: dict[str, Any],
        recent: list[dict[str, Any]],
    ) -> None:
        """TRIGGER-001: spec_compliance_score < 90."""
        score = kpis.get("spec_compliance_score")
        if score is None or score >= 90:
            return
        consec = self._count_consecutive_condition(
            recent,
            lambda r: (
                r.get("kpis", {}).get("spec_compliance_score") is not None
                and r.get("kpis", {}).get("spec_compliance_score") < 90
            ),
        )
        text = (
            f"Flag Stage 2 spec for revision: spec compliance score "
            f"is {score}% (below 90% threshold). Inject targeted prompt "
            f"into spec-creator to address compliance gaps."
        )
        if consec >= 3:
            text += (
                " [CI-ESCALATION] Persisted for 3+ consecutive runs; "
                "recommend manual specification review."
            )
        out.append({
            "trigger_id": "TRIGGER-001", "priority": 1,
            "target_stage": "stage_2",
            "action": _clamp_str(text, _MAX_ACTION_LENGTH),
            "evidence_runs": max(consec, 1),
        })

    def _check_trigger_002(
        self,
        out: list[dict[str, Any]],
        stages: dict[str, Any],
        recent: list[dict[str, Any]],
    ) -> None:
        """TRIGGER-002: stage_3.retry_count > 2."""
        retries = stages.get("stage_3", {}).get("retry_count", 0)
        if retries <= 2:
            return
        consec = self._count_consecutive_condition(
            recent,
            lambda r: r.get("stages", {}).get(
                "stage_3", {}
            ).get("retry_count", 0) > 2,
        )
        text = (
            f"Stage 3 required {retries} retries (threshold: 2). "
            "Inject dependency audit step into Stage 0 researcher."
        )
        if consec >= 3:
            text += " [CI-ESCALATION] Persisted for 3+ consecutive runs."
        elif consec >= 2:
            text += " Escalate to Stage 1 for task decomposition review."
        out.append({
            "trigger_id": "TRIGGER-002", "priority": 2,
            "target_stage": "stage_0",
            "action": _clamp_str(text, _MAX_ACTION_LENGTH),
            "evidence_runs": max(consec, 1),
        })

    def _check_trigger_003(
        self,
        out: list[dict[str, Any]],
        kpis: dict[str, Any],
        stages: dict[str, Any],
        baselines: dict[str, Any] | None,
        recent: list[dict[str, Any]],
    ) -> None:
        """TRIGGER-003: total_duration > 2x baseline."""
        total = kpis.get("total_duration_seconds")
        if total is None or baselines is None:
            return
        bl_total = sum(
            s.get("duration_seconds", {}).get("smoothed", 0.0)
            for s in baselines.get("stages", {}).values()
        )
        if bl_total <= 0 or total <= 2.0 * bl_total:
            return
        consec = self._count_consecutive_condition(
            recent,
            lambda r: (
                r.get("kpis", {}).get("total_duration_seconds", 0)
                > 2.0 * bl_total
            ),
        )
        slowest = self._find_slowest_stage(stages)
        text = (
            f"Total duration {total:.1f}s exceeds 2x baseline "
            f"({bl_total:.1f}s). Slowest stage: {slowest}. "
            "Profile all stages and flag slowest for optimization."
        )
        if consec >= 3:
            text += " [CI-ESCALATION] Duration overrun persisted 3+ runs."
        elif consec >= 2:
            text += " Reduce scope of next run."
        out.append({
            "trigger_id": "TRIGGER-003", "priority": 3,
            "target_stage": "stage_1",
            "action": _clamp_str(text, _MAX_ACTION_LENGTH),
            "evidence_runs": max(consec, 1),
        })

    def _check_trigger_004(
        self,
        out: list[dict[str, Any]],
        kpis: dict[str, Any],
        recent: list[dict[str, Any]],
    ) -> None:
        """TRIGGER-004: test_coverage_pct < 70."""
        cov = kpis.get("test_coverage_pct")
        if cov is None or cov >= 70:
            return
        consec = self._count_consecutive_condition(
            recent,
            lambda r: (
                r.get("kpis", {}).get("test_coverage_pct") is not None
                and r.get("kpis", {}).get("test_coverage_pct") < 70
            ),
        )
        text = (
            f"Test coverage is {cov:.1f}% (below 70% threshold). "
            "Escalate Stage 4 priority and inject uncovered code "
            "paths as explicit test targets."
        )
        if consec >= 3:
            text += " [CI-ESCALATION] Low coverage persisted 3+ runs."
        out.append({
            "trigger_id": "TRIGGER-004", "priority": 4,
            "target_stage": "stage_4",
            "action": _clamp_str(text, _MAX_ACTION_LENGTH),
            "evidence_runs": max(consec, 1),
        })

    def _check_trigger_005(
        self,
        out: list[dict[str, Any]],
        run_summary: dict[str, Any],
        recent: list[dict[str, Any]],
    ) -> None:
        """TRIGGER-005: 3 consecutive partial runs."""
        count = self._count_consecutive_condition(
            recent,
            lambda r: r.get("overall_status") == "partial",
        )
        if run_summary.get("overall_status") == "partial":
            count = max(count, 1)
        if count < 3:
            return
        failed = self._get_failed_stages_across_runs(recent[-3:])
        text = (
            f"3 consecutive partial runs detected. "
            f"Failing stages: {', '.join(failed) or 'various'}. "
            "[CI-ESCALATION] User review required. "
            "Automated improvement loop has not resolved systemic issues."
        )
        out.append({
            "trigger_id": "TRIGGER-005", "priority": 5,
            "target_stage": "overall",
            "action": _clamp_str(text, _MAX_ACTION_LENGTH),
            "evidence_runs": count,
        })

    @staticmethod
    def _count_consecutive_condition(
        runs: list[dict[str, Any]],
        condition: Any,
    ) -> int:
        """Count consecutive recent runs (from most recent) matching condition."""
        count = 0
        for run in reversed(runs):
            if condition(run):
                count += 1
            else:
                break
        return count

    @staticmethod
    def _find_slowest_stage(stages: dict[str, Any]) -> str:
        """Find the stage with the longest duration."""
        slowest = "unknown"
        max_dur = -1.0
        for name, data in stages.items():
            dur = data.get("duration_seconds", 0.0)
            if dur > max_dur:
                max_dur = dur
                slowest = name
        return slowest

    @staticmethod
    def _get_failed_stages_across_runs(
        runs: list[dict[str, Any]],
    ) -> list[str]:
        """Get unique failed stage names across multiple runs."""
        failed: set[str] = set()
        for run in runs:
            for name, data in run.get("stages", {}).items():
                if data.get("status") in ("failed", "partial"):
                    failed.add(name)
        return sorted(failed)

    # -------------------------------------------------------------------
    # Improvement action assembly
    # -------------------------------------------------------------------

    def _build_improvement_actions(
        self,
        what_went_poorly: list[dict[str, Any]],
        trigger_actions: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Build the improvement_actions array sorted by priority.

        Each action carries an internal _trigger_id key (excluded from
        retro.json output but used by _build_log_entries).
        """
        actions: list[dict[str, Any]] = []
        priority_counter = 1

        # Trigger-derived actions first (higher priority)
        for ta in trigger_actions:
            actions.append({
                "priority": priority_counter,
                "target_stage": ta["target_stage"],
                "action": ta["action"],
                "evidence_runs": ta["evidence_runs"],
                "_trigger_id": ta.get("trigger_id"),
            })
            priority_counter += 1

        # Regression-derived actions
        for item in what_went_poorly:
            stage = item.get("stage", "overall")
            root_cause = item.get("root_cause", "")
            # Avoid duplicating trigger-derived actions for the same stage
            already_covered = any(
                a["target_stage"] == stage for a in actions
            )
            if already_covered:
                continue

            action_text = (
                f"Address regression in {stage}: {root_cause}"
            )
            actions.append({
                "priority": priority_counter,
                "target_stage": stage,
                "action": _clamp_str(action_text, _MAX_ACTION_LENGTH),
                "evidence_runs": 1,
                "_trigger_id": None,
            })
            priority_counter += 1

        return actions

    def _compute_run_sequence(self) -> int:
        """Determine the 1-based sequence number of the current run."""
        all_summaries = _collect_run_summaries(self.knowledge_store_path)
        for idx, summary in enumerate(all_summaries, start=1):
            sid = summary.get("session_id") or summary.get("run_id", "")
            if sid == self.session_id:
                return idx
        return len(all_summaries) + 1

    def _build_log_entries(
        self,
        improvement_actions: list[dict[str, Any]],
        what_went_poorly: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Build improvement_log.jsonl entries from actions."""
        poorly_by_stage = self._index_poorly_by_stage(what_went_poorly)
        recent_log = self._load_recent_improvement_log()
        timestamp = _utc_now_iso()
        run_sequence = self._compute_run_sequence()

        return [
            self._action_to_log_entry(
                action, timestamp, poorly_by_stage, recent_log, run_sequence
            )
            for action in improvement_actions
        ]

    @staticmethod
    def _index_poorly_by_stage(
        poorly: list[dict[str, Any]],
    ) -> dict[str, dict[str, Any]]:
        """Index what_went_poorly items by stage (first occurrence)."""
        result: dict[str, dict[str, Any]] = {}
        for item in poorly:
            stage = item.get("stage", "")
            if stage and stage not in result:
                result[stage] = item
        return result

    def _action_to_log_entry(
        self,
        action: dict[str, Any],
        timestamp: str,
        poorly_by_stage: dict[str, dict[str, Any]],
        recent_log: list[dict[str, Any]],
        run_sequence: int = 0,
    ) -> dict[str, Any]:
        """Convert a single improvement action to a log entry."""
        target = action["target_stage"]
        text = action["action"]
        evidence = action["evidence_runs"]
        needs_review = evidence < 3

        if self._has_contradictory_action(recent_log, target, text):
            needs_review = True

        trigger_id = action.get("_trigger_id")
        root_cat, conf = self._classify_poorly_item(
            poorly_by_stage.get(target), target
        )
        if conf is not None and conf < 0.5:
            needs_review = True

        return {
            "schema_version": _SCHEMA_VERSION,
            "session_id": self.session_id,
            "timestamp": timestamp,
            "source": "retrospective_analyzer",
            "entry_type": "improvement_action",
            "run_sequence": run_sequence,
            "target_stage": target,
            "action": _clamp_str(text, _MAX_ACTION_LENGTH),
            "priority": action["priority"],
            "evidence_runs": evidence,
            "trigger_id": trigger_id,
            "root_cause_category": root_cat,
            "confidence": conf,
            "needs_review": needs_review,
        }

    @staticmethod
    def _classify_poorly_item(
        poorly_item: dict[str, Any] | None,
        stage: str,
    ) -> tuple[str | None, float | None]:
        """Extract root cause metadata from a poorly item."""
        if poorly_item is None:
            return None, None
        obs = poorly_item.get("observation", "")
        if not obs:
            return None, None
        rc = classify_failure(error_message=obs, stage=stage)
        return rc["category"], rc["confidence"]

    def _load_recent_improvement_log(self) -> list[dict[str, Any]]:
        """Load the last 5 entries from improvement_log.jsonl."""
        log_path = (
            self.knowledge_store_path
            / "improvements"
            / "improvement_log.jsonl"
        )
        records = _read_jsonl_optional(log_path)
        return records[-5:] if records else []

    @staticmethod
    def _has_contradictory_action(
        recent_entries: list[dict[str, Any]],
        target_stage: str,
        action_text: str,
    ) -> bool:
        """Check if a contradictory action exists for the same target stage.

        Detects basic contradictions like 'increase' vs 'decrease',
        'add' vs 'remove', 'enable' vs 'disable'.
        """
        contradiction_pairs = [
            ("increase", "decrease"),
            ("add", "remove"),
            ("enable", "disable"),
            ("raise", "lower"),
            ("expand", "reduce"),
        ]
        action_lower = action_text.lower()

        for entry in recent_entries:
            if entry.get("target_stage") != target_stage:
                continue
            existing_lower = entry.get("action", "").lower()

            for word_a, word_b in contradiction_pairs:
                if (
                    (word_a in action_lower and word_b in existing_lower)
                    or (word_b in action_lower and word_a in existing_lower)
                ):
                    logger.warning(
                        "Contradictory action detected for %s: "
                        "'%s' vs existing '%s'",
                        target_stage,
                        action_text[:60],
                        existing_lower[:60],
                    )
                    return True
        return False
