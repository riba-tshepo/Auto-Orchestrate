"""Run summary schema and serializer for the continuous improvement engine.

Provides dataclass-based schema for run_summary.json (spec Section 3.1),
a factory method to parse existing checkpoint.json session state, and a
JSON serializer that produces schema_version=1 output.

This module is a pure data model — it performs NO file I/O. All persistence
is handled by knowledge_store_writer.py.

Dependencies: Python >= 3.11 stdlib only.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)

_SCHEMA_VERSION = 1

_VALID_OVERALL_STATUSES = frozenset({"success", "partial", "failed", "aborted"})
_VALID_STAGE_STATUSES = frozenset({"success", "partial", "failed", "skipped"})

_MAX_STAGES = 20
_MAX_ERROR_MESSAGE_LENGTH = 1000
_MAX_IMPROVEMENT_NOTE_LENGTH = 500
_MAX_IMPROVEMENT_NOTES = 100


# ---------------------------------------------------------------------------
# Token count
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class TokenCount:
    """Token usage for a single stage."""

    input: int = 0
    output: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.input, int) or self.input < 0:
            raise ValueError(
                f"TokenCount.input must be a non-negative integer, got {self.input!r}"
            )
        if not isinstance(self.output, int) or self.output < 0:
            raise ValueError(
                f"TokenCount.output must be a non-negative integer, got {self.output!r}"
            )

    @property
    def total(self) -> int:
        """Return combined input + output token count."""
        return self.input + self.output

    def to_dict(self) -> dict[str, int]:
        """Serialize to a plain dictionary."""
        return {"input": self.input, "output": self.output}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TokenCount:
        """Deserialize from a dictionary with input/output keys."""
        if not isinstance(data, dict):
            raise ValueError(f"TokenCount expects a dict, got {type(data).__name__}")
        return cls(
            input=int(data.get("input", 0)),
            output=int(data.get("output", 0)),
        )


# ---------------------------------------------------------------------------
# Stage entry
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class StageEntry:
    """Data for a single pipeline stage within a run summary."""

    duration_seconds: float
    status: str
    errors: list[str] = field(default_factory=list)
    retry_count: int = 0
    token_count: TokenCount = field(default_factory=TokenCount)
    spec_compliance_score: Optional[int] = None

    def __post_init__(self) -> None:
        if not isinstance(self.duration_seconds, (int, float)):
            raise ValueError(
                f"duration_seconds must be a number, got {type(self.duration_seconds).__name__}"
            )
        self.duration_seconds = float(self.duration_seconds)
        if self.duration_seconds < 0:
            raise ValueError(
                f"duration_seconds must be non-negative, got {self.duration_seconds}"
            )

        if self.status not in _VALID_STAGE_STATUSES:
            raise ValueError(
                f"Invalid stage status {self.status!r}. "
                f"Must be one of {sorted(_VALID_STAGE_STATUSES)}"
            )

        if not isinstance(self.errors, list):
            raise ValueError("errors must be a list of strings")
        self.errors = [
            str(e)[:_MAX_ERROR_MESSAGE_LENGTH] for e in self.errors
        ]

        if not isinstance(self.retry_count, int) or self.retry_count < 0:
            raise ValueError(
                f"retry_count must be a non-negative integer, got {self.retry_count!r}"
            )

        if not isinstance(self.token_count, TokenCount):
            raise ValueError(
                f"token_count must be a TokenCount instance, got {type(self.token_count).__name__}"
            )

        if self.spec_compliance_score is not None:
            if not isinstance(self.spec_compliance_score, int):
                raise ValueError(
                    f"spec_compliance_score must be int or None, got {type(self.spec_compliance_score).__name__}"
                )
            min_score = 0
            max_score = 100
            if not (min_score <= self.spec_compliance_score <= max_score):
                raise ValueError(
                    f"spec_compliance_score must be between {min_score} and {max_score}, "
                    f"got {self.spec_compliance_score}"
                )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dictionary matching spec Section 3.1."""
        return {
            "duration_seconds": self.duration_seconds,
            "status": self.status,
            "errors": list(self.errors),
            "retry_count": self.retry_count,
            "token_count": self.token_count.to_dict(),
            "spec_compliance_score": self.spec_compliance_score,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StageEntry:
        """Deserialize from a dictionary."""
        if not isinstance(data, dict):
            raise ValueError(f"StageEntry expects a dict, got {type(data).__name__}")

        token_raw = data.get("token_count", {})
        token_count = (
            token_raw if isinstance(token_raw, TokenCount)
            else TokenCount.from_dict(token_raw if isinstance(token_raw, dict) else {})
        )

        return cls(
            duration_seconds=float(data.get("duration_seconds", 0.0)),
            status=str(data.get("status", "skipped")),
            errors=list(data.get("errors", [])),
            retry_count=int(data.get("retry_count", 0)),
            token_count=token_count,
            spec_compliance_score=data.get("spec_compliance_score"),
        )


# ---------------------------------------------------------------------------
# KPIs
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class RunKpis:
    """Key performance indicators for a completed run."""

    total_duration_seconds: float = 0.0
    spec_compliance_score: Optional[int] = None
    test_coverage_pct: Optional[float] = None
    stage_failure_bitmap: str = "0b0"
    improvement_delta_pct: Optional[float] = None

    def __post_init__(self) -> None:
        if not isinstance(self.total_duration_seconds, (int, float)):
            raise ValueError("total_duration_seconds must be a number")
        self.total_duration_seconds = float(self.total_duration_seconds)

        if self.spec_compliance_score is not None:
            if not isinstance(self.spec_compliance_score, int):
                raise ValueError("spec_compliance_score must be int or None")
            min_score = 0
            max_score = 100
            if not (min_score <= self.spec_compliance_score <= max_score):
                raise ValueError(
                    f"spec_compliance_score must be 0-100, got {self.spec_compliance_score}"
                )

        if self.test_coverage_pct is not None:
            self.test_coverage_pct = float(self.test_coverage_pct)
            min_pct = 0.0
            max_pct = 100.0
            if not (min_pct <= self.test_coverage_pct <= max_pct):
                raise ValueError(
                    f"test_coverage_pct must be 0-100, got {self.test_coverage_pct}"
                )

        if not isinstance(self.stage_failure_bitmap, str):
            raise ValueError("stage_failure_bitmap must be a string")

        if self.improvement_delta_pct is not None:
            self.improvement_delta_pct = float(self.improvement_delta_pct)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dictionary matching spec Section 3.1."""
        return {
            "total_duration_seconds": self.total_duration_seconds,
            "spec_compliance_score": self.spec_compliance_score,
            "test_coverage_pct": self.test_coverage_pct,
            "stage_failure_bitmap": self.stage_failure_bitmap,
            "improvement_delta_pct": self.improvement_delta_pct,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RunKpis:
        """Deserialize from a dictionary."""
        if not isinstance(data, dict):
            raise ValueError(f"RunKpis expects a dict, got {type(data).__name__}")
        return cls(
            total_duration_seconds=float(data.get("total_duration_seconds", 0.0)),
            spec_compliance_score=data.get("spec_compliance_score"),
            test_coverage_pct=data.get("test_coverage_pct"),
            stage_failure_bitmap=str(data.get("stage_failure_bitmap", "0b0")),
            improvement_delta_pct=data.get("improvement_delta_pct"),
        )


# ---------------------------------------------------------------------------
# Run summary
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class RunSummary:
    """Complete run summary matching the knowledge store spec Section 3.1.

    This is the canonical in-memory representation of a run_summary.json file.
    Use ``from_session_state()`` to construct from a checkpoint.json session,
    or ``from_dict()`` to deserialize from an existing run_summary.json.
    Use ``to_json()`` to serialize to a valid JSON string with schema_version=1.
    """

    run_id: str
    completed_at: str
    stages: dict[str, StageEntry]
    overall_status: str
    improvement_notes: list[str] = field(default_factory=list)
    kpis: RunKpis = field(default_factory=RunKpis)

    def __post_init__(self) -> None:
        if not self.run_id or not isinstance(self.run_id, str):
            raise ValueError("run_id must be a non-empty string")

        if not self.completed_at or not isinstance(self.completed_at, str):
            raise ValueError("completed_at must be a non-empty ISO 8601 string")

        if not isinstance(self.stages, dict):
            raise ValueError("stages must be a dictionary")
        if len(self.stages) > _MAX_STAGES:
            raise ValueError(
                f"stages exceeds maximum of {_MAX_STAGES} entries"
            )

        if self.overall_status not in _VALID_OVERALL_STATUSES:
            raise ValueError(
                f"Invalid overall_status {self.overall_status!r}. "
                f"Must be one of {sorted(_VALID_OVERALL_STATUSES)}"
            )

        if not isinstance(self.improvement_notes, list):
            raise ValueError("improvement_notes must be a list")
        self.improvement_notes = [
            str(n)[:_MAX_IMPROVEMENT_NOTE_LENGTH]
            for n in self.improvement_notes[:_MAX_IMPROVEMENT_NOTES]
        ]

        if not isinstance(self.kpis, RunKpis):
            raise ValueError("kpis must be a RunKpis instance")

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dictionary matching spec Section 3.1.

        The output includes ``schema_version: 1`` as required by the spec.
        """
        return {
            "schema_version": _SCHEMA_VERSION,
            "run_id": self.run_id,
            "completed_at": self.completed_at,
            "stages": {
                name: entry.to_dict() for name, entry in self.stages.items()
            },
            "overall_status": self.overall_status,
            "improvement_notes": list(self.improvement_notes),
            "kpis": self.kpis.to_dict(),
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize to a JSON string with schema_version=1.

        Args:
            indent: JSON indentation level. Default 2 for readability.

        Returns:
            A valid JSON string matching the run_summary.json spec.
        """
        return json.dumps(
            self.to_dict(),
            indent=indent,
            ensure_ascii=False,
            sort_keys=False,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RunSummary:
        """Deserialize from a run_summary.json dictionary.

        Args:
            data: Dictionary parsed from a run_summary.json file.

        Returns:
            A validated RunSummary instance.

        Raises:
            ValueError: If required fields are missing or invalid.
        """
        if not isinstance(data, dict):
            raise ValueError(f"RunSummary expects a dict, got {type(data).__name__}")

        raw_stages = data.get("stages", {})
        if not isinstance(raw_stages, dict):
            raise ValueError("stages must be a dictionary")
        stages = {
            name: StageEntry.from_dict(entry)
            for name, entry in raw_stages.items()
        }

        raw_kpis = data.get("kpis", {})
        kpis = (
            raw_kpis if isinstance(raw_kpis, RunKpis)
            else RunKpis.from_dict(raw_kpis if isinstance(raw_kpis, dict) else {})
        )

        return cls(
            run_id=str(data.get("run_id", "")),
            completed_at=str(data.get("completed_at", "")),
            stages=stages,
            overall_status=str(data.get("overall_status", "failed")),
            improvement_notes=list(data.get("improvement_notes", [])),
            kpis=kpis,
        )

    @classmethod
    def from_json(cls, json_str: str) -> RunSummary:
        """Deserialize from a JSON string.

        Args:
            json_str: A JSON string from a run_summary.json file.

        Returns:
            A validated RunSummary instance.

        Raises:
            json.JSONDecodeError: If the string is not valid JSON.
            ValueError: If the parsed data fails validation.
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def from_session_state(
        cls,
        session_state: dict[str, Any],
        stage_durations: Optional[dict[str, float]] = None,
        stage_errors: Optional[dict[str, list[str]]] = None,
        stage_retries: Optional[dict[str, int]] = None,
        stage_tokens: Optional[dict[str, dict[str, int]]] = None,
        stage_compliance: Optional[dict[str, int]] = None,
        test_coverage_pct: Optional[float] = None,
        improvement_delta_pct: Optional[float] = None,
    ) -> RunSummary:
        """Construct a RunSummary from an existing checkpoint.json session state.

        Parses the checkpoint.json format used by Auto-Orchestrate to extract
        run metadata and maps it to the run_summary.json schema.

        The checkpoint.json contains ``session_id``, ``status``,
        ``stages_completed`` (list of stage numbers), ``updated_at``,
        and ``iteration_history`` (list of iteration records). This method
        converts that into the knowledge store run summary format.

        Stage-level telemetry (durations, errors, retries, tokens) is not
        stored in checkpoint.json, so callers supply it via optional dicts
        keyed by stage name (e.g., ``{"stage_0": 45.2, "stage_3": 180.7}``).

        Args:
            session_state: Parsed checkpoint.json dictionary.
            stage_durations: Map of stage name to duration in seconds.
            stage_errors: Map of stage name to list of error messages.
            stage_retries: Map of stage name to retry count.
            stage_tokens: Map of stage name to ``{"input": N, "output": M}``.
            stage_compliance: Map of stage name to spec compliance score.
            test_coverage_pct: Test coverage percentage if known.
            improvement_delta_pct: Improvement delta vs. previous run if known.

        Returns:
            A validated RunSummary instance.

        Raises:
            ValueError: If session_state is missing required fields.
        """
        if not isinstance(session_state, dict):
            raise ValueError("session_state must be a dictionary")

        run_id = str(session_state.get("session_id", ""))
        if not run_id:
            raise ValueError("session_state must contain a non-empty 'session_id'")

        completed_at = session_state.get("updated_at", "")
        if not completed_at:
            completed_at = _utc_now_iso()

        stage_durations = stage_durations or {}
        stage_errors = stage_errors or {}
        stage_retries = stage_retries or {}
        stage_tokens = stage_tokens or {}
        stage_compliance = stage_compliance or {}

        stages_completed: list[Any] = session_state.get("stages_completed", [])
        checkpoint_status = str(session_state.get("status", ""))

        all_stage_keys = set()
        for stage_num in stages_completed:
            all_stage_keys.add(f"stage_{stage_num}")
        for key_source in (stage_durations, stage_errors, stage_retries, stage_tokens, stage_compliance):
            all_stage_keys.update(key_source.keys())

        stages: dict[str, StageEntry] = {}
        for stage_name in sorted(all_stage_keys):
            tokens_raw = stage_tokens.get(stage_name, {})
            token_count = TokenCount(
                input=int(tokens_raw.get("input", 0)),
                output=int(tokens_raw.get("output", 0)),
            )

            errors = stage_errors.get(stage_name, [])
            status = _derive_stage_status(
                stage_name=stage_name,
                stages_completed=stages_completed,
                errors=errors,
            )

            stages[stage_name] = StageEntry(
                duration_seconds=float(stage_durations.get(stage_name, 0.0)),
                status=status,
                errors=errors,
                retry_count=int(stage_retries.get(stage_name, 0)),
                token_count=token_count,
                spec_compliance_score=stage_compliance.get(stage_name),
            )

        overall_status = _derive_overall_status(
            checkpoint_status=checkpoint_status,
            stages=stages,
        )

        improvement_notes = _extract_improvement_notes(
            session_state=session_state,
            stages=stages,
        )

        failure_bitmap = _compute_failure_bitmap(stages)
        final_compliance = _pick_final_compliance(stages, stage_compliance)

        total_duration = sum(
            entry.duration_seconds for entry in stages.values()
        )

        kpis = RunKpis(
            total_duration_seconds=total_duration,
            spec_compliance_score=final_compliance,
            test_coverage_pct=test_coverage_pct,
            stage_failure_bitmap=failure_bitmap,
            improvement_delta_pct=improvement_delta_pct,
        )

        return cls(
            run_id=run_id,
            completed_at=completed_at,
            stages=stages,
            overall_status=overall_status,
            improvement_notes=improvement_notes,
            kpis=kpis,
        )


# ---------------------------------------------------------------------------
# Internal helpers (pure functions, no I/O)
# ---------------------------------------------------------------------------

def _utc_now_iso() -> str:
    """Return current UTC time as ISO 8601 string with Z suffix."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _derive_stage_status(
    stage_name: str,
    stages_completed: list[Any],
    errors: list[str],
) -> str:
    """Derive a stage status from checkpoint data.

    A stage is "success" if it appears in stages_completed and has no errors,
    "partial" if completed but has errors, "failed" if it has errors but is
    not in stages_completed, and "skipped" if absent from both.
    """
    stage_num = _parse_stage_number(stage_name)
    completed = stage_num is not None and stage_num in stages_completed

    has_errors = len(errors) > 0

    if completed and not has_errors:
        return "success"
    if completed and has_errors:
        return "partial"
    if has_errors:
        return "failed"
    return "skipped"


def _parse_stage_number(stage_name: str) -> Any:
    """Extract the numeric portion from a stage name like 'stage_3' or 'stage_4.5'.

    Returns an int for whole numbers, a float for fractional stages (e.g. 4.5),
    or None if parsing fails.
    """
    prefix = "stage_"
    if not stage_name.startswith(prefix):
        return None
    suffix = stage_name[len(prefix):]
    try:
        if "." in suffix:
            return float(suffix)
        return int(suffix)
    except ValueError:
        return None


def _derive_overall_status(
    checkpoint_status: str,
    stages: dict[str, StageEntry],
) -> str:
    """Derive overall run status from checkpoint status and stage data.

    Maps checkpoint.json status values to the knowledge store's overall_status
    enum. Falls back to stage analysis if the checkpoint status is ambiguous.
    """
    status_mapping: dict[str, str] = {
        "completed": "success",
        "success": "success",
        "failed": "failed",
        "aborted": "aborted",
        "cancelled": "aborted",
    }

    if checkpoint_status in status_mapping:
        return status_mapping[checkpoint_status]

    if not stages:
        return "failed"

    statuses = {entry.status for entry in stages.values()}
    if statuses == {"success"}:
        return "success"
    if "failed" in statuses:
        any_success = any(
            e.status in ("success", "partial") for e in stages.values()
        )
        if any_success:
            return "partial"
        return "failed"
    if "partial" in statuses:
        return "partial"
    if statuses == {"skipped"}:
        return "aborted"

    return "partial"


def _extract_improvement_notes(
    session_state: dict[str, Any],
    stages: dict[str, StageEntry],
) -> list[str]:
    """Extract improvement notes from session state and stage analysis.

    Generates notes for stages with errors or retries, and for compliance
    scores below a threshold.
    """
    notes: list[str] = []
    compliance_threshold = 90

    for stage_name, entry in sorted(stages.items()):
        if entry.errors:
            error_summary = "; ".join(entry.errors[:3])
            notes.append(f"{stage_name} errors: {error_summary}")

        if entry.retry_count > 0:
            notes.append(
                f"{stage_name} required {entry.retry_count} retries"
            )

        if (
            entry.spec_compliance_score is not None
            and entry.spec_compliance_score < compliance_threshold
        ):
            notes.append(
                f"{stage_name} spec compliance {entry.spec_compliance_score}% "
                f"(below {compliance_threshold}% threshold)"
            )

    iteration_history = session_state.get("iteration_history", [])
    if isinstance(iteration_history, list) and iteration_history:
        last_iteration = iteration_history[-1]
        if isinstance(last_iteration, dict):
            summary = last_iteration.get("summary", "")
            if summary and isinstance(summary, str):
                notes.append(f"Last iteration: {summary[:_MAX_IMPROVEMENT_NOTE_LENGTH]}")

    return notes[:_MAX_IMPROVEMENT_NOTES]


def _compute_failure_bitmap(stages: dict[str, StageEntry]) -> str:
    """Compute a binary string bitmask where bit N=1 if stage N failed.

    Returns a Python binary literal string (e.g., "0b0001000").
    Stages with fractional numbers (e.g., stage_4.5) are skipped.
    """
    if not stages:
        return "0b0"

    max_bit = 0
    failure_bits: dict[int, bool] = {}

    for stage_name, entry in stages.items():
        stage_num = _parse_stage_number(stage_name)
        if stage_num is None or not isinstance(stage_num, int):
            continue
        if stage_num < 0:
            continue
        if stage_num > max_bit:
            max_bit = stage_num
        failure_bits[stage_num] = entry.status in ("failed",)

    if not failure_bits:
        return "0b0"

    bits = ["0"] * (max_bit + 1)
    for bit_pos, is_failed in failure_bits.items():
        if is_failed:
            bits[bit_pos] = "1"

    bitmap_str = "".join(reversed(bits))
    return f"0b{bitmap_str}"


def _pick_final_compliance(
    stages: dict[str, StageEntry],
    stage_compliance: Optional[dict[str, int]],
) -> Optional[int]:
    """Pick the final spec compliance score from the validator stage.

    Prefers stage_5 (validator). Falls back to the highest-numbered stage
    with a compliance score.
    """
    validator_stage = "stage_5"
    if validator_stage in stages:
        score = stages[validator_stage].spec_compliance_score
        if score is not None:
            return score

    best_score: Optional[int] = None
    best_stage_num: float = -1.0

    for stage_name, entry in stages.items():
        if entry.spec_compliance_score is not None:
            stage_num = _parse_stage_number(stage_name)
            num_val = float(stage_num) if stage_num is not None else -1.0
            if num_val > best_stage_num:
                best_stage_num = num_val
                best_score = entry.spec_compliance_score

    return best_score
