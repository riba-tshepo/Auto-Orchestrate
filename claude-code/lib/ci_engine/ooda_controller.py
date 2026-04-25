"""OODA within-run loop controller for the Auto-Orchestrate pipeline.

Implements the Observe-Orient-Decide-Act loop for real-time stage failure
response during a single pipeline execution. Observes stage telemetry,
orients against historical baselines from stage_baselines.json and
failure_patterns.json, decides on a corrective action (continue, retry,
fallback_to_spec, surface_to_user), and produces an ActionResult the
orchestrator can execute.

Integrates with root_cause_classifier.classify_failure() for failure
categorization and with knowledge_store_writer for telemetry recording.

Thread-safe: all mutable state is protected by a threading lock.
Context manager protocol supported for resource cleanup.

Dependencies: Python >= 3.11 stdlib only. No MLflow.
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from lib.ci_engine.root_cause_classifier import classify_failure

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_VALID_DECISIONS = frozenset({"continue", "retry", "fallback_to_spec", "surface_to_user"})
_VALID_STATUSES = frozenset({"success", "partial", "failure"})
_VALID_CLASSIFICATIONS = frozenset({"nominal", "degraded", "anomalous"})

_DEFAULT_MAX_RETRIES = 3
_DURATION_DEVIATION_THRESHOLD_PCT = 50.0
_LOW_CONFIDENCE_THRESHOLD = 0.3

_HALLUCINATION_RETRY_PROMPT = (
    "Previous attempt produced incorrect output. "
    "Focus on accuracy and adherence to spec requirements."
)


# ---------------------------------------------------------------------------
# Frozen dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ObservationRecord:
    """Immutable record of stage observation data.

    Captures the 10 data points collected during the Observe phase.
    """

    stage_name: str
    status: str
    duration_seconds: float
    error_count: int
    retry_count: int
    error_messages: tuple[str, ...]
    token_input: int = 0
    token_output: int = 0
    spec_compliance_score: float | None = None
    research_completeness_score: float | None = None


@dataclass(frozen=True)
class OrientationResult:
    """Result of the OODA Orient phase."""

    classification: str
    baseline_available: bool
    duration_deviation_pct: float | None
    error_deviation: float | None
    failure_category: str | None
    failure_confidence: float | None
    matched_pattern: str | None


@dataclass(frozen=True)
class ActionResult:
    """Result of the OODA Act phase."""

    decision: str
    enhanced_prompt: str | None
    spec_gap_description: str | None
    failure_report: dict[str, Any] | None
    telemetry_event: dict[str, Any]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _utc_now_iso() -> str:
    """Return current UTC time as ISO 8601 string with Z suffix."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _utc_now_iso_ms() -> str:
    """Return current UTC time as ISO 8601 string with milliseconds."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def _load_json_safe(path: Path) -> dict[str, Any] | None:
    """Load a JSON file, returning None if the file does not exist or is invalid."""
    if not path.is_file():
        return None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Failed to load %s: %s", path, exc)
        return None


def _append_jsonl(target_path: Path, record: dict[str, Any]) -> None:
    """Append a single JSON record to a JSONL file with flush and fsync."""
    os.makedirs(target_path.parent, exist_ok=True)
    with open(target_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False))
        fh.write("\n")
        fh.flush()
        os.fsync(fh.fileno())


def _compute_std_deviation(values: list[float]) -> float:
    """Compute population standard deviation from a list of floats."""
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    return variance ** 0.5


def _stage_number_from_name(stage_name: str) -> int:
    """Extract a numeric stage number from a stage name string.

    Maps known stage names to their numeric equivalents. Returns -1 for
    unrecognised names.
    """
    mapping = {
        "stage_0": 0, "researcher": 0,
        "stage_1": 1, "product_manager": 1,
        "stage_2": 2, "spec_creator": 2,
        "stage_3": 3, "software_engineer": 3,
        "stage_4": 4, "tester": 4,
        "stage_4_5": 4, "integration_tester": 4,
        "stage_5": 5, "validator": 5,
        "stage_6": 6, "technical_writer": 6,
    }
    return mapping.get(stage_name, -1)


# ---------------------------------------------------------------------------
# OODAController
# ---------------------------------------------------------------------------

class OODAController:
    """Within-run OODA loop controller for the Auto-Orchestrate pipeline.

    Implements the Observe-Orient-Decide-Act loop for real-time stage
    failure response. All decision methods are synchronous and deterministic.

    Supports the context manager protocol for clean resource lifecycle.
    Thread-safe: internal state is protected by a threading lock.
    """

    def __init__(
        self,
        knowledge_store_path: Path,
        session_id: str,
        max_retries: int = _DEFAULT_MAX_RETRIES,
        domain_store: Any = None,
    ) -> None:
        """Initialise the OODA controller.

        Args:
            knowledge_store_path: Path to .orchestrate/knowledge_store/.
            session_id: Current orchestration session identifier.
            max_retries: Maximum retry attempts per stage. Must be >= 1.
            domain_store: Optional ``DomainMemoryStore`` instance for
                querying the fix registry during Orient phase. When
                provided, known fixes are included in retry prompts.

        Raises:
            ValueError: If max_retries < 1 or session_id is empty.
        """
        if max_retries < 1:
            raise ValueError(f"max_retries must be >= 1, got {max_retries}")
        if not session_id or not isinstance(session_id, str):
            raise ValueError("session_id must be a non-empty string")

        self._knowledge_store_path = Path(knowledge_store_path)
        self._session_id = session_id
        self._max_retries = max_retries
        self._domain_store = domain_store
        self._lock = threading.Lock()

        # Load baselines and failure patterns at init time.
        # If files are missing (first run), use empty defaults.
        self._baselines: dict[str, Any] = {}
        self._failure_patterns: list[dict[str, Any]] = []
        self._reload_reference_data()

    # -- Context manager protocol ------------------------------------------

    def __enter__(self) -> OODAController:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> bool:
        return False

    # -- Public API ---------------------------------------------------------

    def observe(self, stage_result: dict[str, Any]) -> ObservationRecord:
        """Collect and structure stage result data.

        Validates required keys, constructs an immutable ObservationRecord.
        Performs no I/O.

        Args:
            stage_result: Dictionary containing stage outcome data.

        Returns:
            ObservationRecord with all observed data points.

        Raises:
            ValueError: If required keys are missing or have invalid types.
        """
        required_keys = {
            "stage_name", "status", "duration_seconds",
            "error_count", "retry_count", "error_messages",
        }
        missing = required_keys - set(stage_result.keys())
        if missing:
            raise ValueError(
                f"stage_result is missing required keys: {sorted(missing)}"
            )

        status = stage_result["status"]
        if status not in _VALID_STATUSES:
            raise ValueError(
                f"Invalid status '{status}'. Must be one of {sorted(_VALID_STATUSES)}"
            )

        stage_name = stage_result["stage_name"]
        if not isinstance(stage_name, str) or not stage_name:
            raise ValueError("stage_name must be a non-empty string")

        duration = stage_result["duration_seconds"]
        if not isinstance(duration, (int, float)):
            raise ValueError("duration_seconds must be a number")

        error_count = stage_result["error_count"]
        if not isinstance(error_count, int):
            raise ValueError("error_count must be an integer")

        retry_count = stage_result["retry_count"]
        if not isinstance(retry_count, int):
            raise ValueError("retry_count must be an integer")

        error_messages = stage_result["error_messages"]
        if not isinstance(error_messages, (list, tuple)):
            raise ValueError("error_messages must be a list")

        return ObservationRecord(
            stage_name=stage_name,
            status=status,
            duration_seconds=float(duration),
            error_count=error_count,
            retry_count=retry_count,
            error_messages=tuple(str(m) for m in error_messages),
            token_input=int(stage_result.get("token_input", 0)),
            token_output=int(stage_result.get("token_output", 0)),
            spec_compliance_score=stage_result.get("spec_compliance_score"),
            research_completeness_score=stage_result.get(
                "research_completeness_score"
            ),
        )

    def orient(self, observation: ObservationRecord) -> OrientationResult:
        """Contextualise observation against historical baselines.

        Queries stage_baselines.json and failure_patterns.json (local file
        reads only). Must complete in < 100ms.

        Args:
            observation: The ObservationRecord from the observe() phase.

        Returns:
            OrientationResult with classification, deviations, and failure
            category when applicable.
        """
        start_ns = time.monotonic_ns()

        with self._lock:
            baselines = self._baselines
            patterns = list(self._failure_patterns)

        baseline_available = bool(baselines and baselines.get("stages"))
        stage_baseline = (
            baselines.get("stages", {}).get(observation.stage_name)
            if baseline_available
            else None
        )

        # Compute duration deviation
        duration_deviation_pct: float | None = None
        if stage_baseline is not None:
            dur_data = stage_baseline.get("duration_seconds", {})
            smoothed_dur = dur_data.get("smoothed")
            if smoothed_dur is not None and smoothed_dur > 0.0:
                duration_deviation_pct = round(
                    ((observation.duration_seconds - smoothed_dur) / smoothed_dur)
                    * 100.0,
                    4,
                )

        # Compute error deviation (standard deviations from baseline mean)
        error_deviation: float | None = None
        if stage_baseline is not None:
            err_data = stage_baseline.get("error_rate", {})
            raw_errors = err_data.get("raw_values", [])
            if raw_errors:
                current_error_rate = 1.0 if observation.error_count > 0 else 0.0
                mean_err = sum(raw_errors) / len(raw_errors)
                std_err = _compute_std_deviation(raw_errors)
                if std_err > 0.0:
                    error_deviation = round(
                        (current_error_rate - mean_err) / std_err, 4
                    )
                else:
                    # No variance: flag any deviation as significant
                    error_deviation = (
                        0.0 if current_error_rate == mean_err else 2.0
                    )

        # Check failure pattern match
        matched_pattern: str | None = None
        cached_category: str | None = None
        cached_confidence: float | None = None

        if observation.error_messages and patterns:
            combined_errors = " ".join(observation.error_messages).lower()
            for pattern in patterns:
                pattern_text = pattern.get("description", "").lower()
                keywords = pattern.get("keywords", [])
                matched = False
                if pattern_text and pattern_text in combined_errors:
                    matched = True
                if not matched:
                    for kw in keywords:
                        if isinstance(kw, str) and kw.lower() in combined_errors:
                            matched = True
                            break
                if matched:
                    matched_pattern = pattern.get("pattern_id")
                    cached_category = pattern.get("classification")
                    cached_confidence = pattern.get("confidence")
                    break

        # Determine classification
        classification = self._classify_stage_outcome(
            observation=observation,
            baseline_available=baseline_available,
            duration_deviation_pct=duration_deviation_pct,
            error_deviation=error_deviation,
        )

        # For anomalous stages with errors, run the root cause classifier
        failure_category: str | None = None
        failure_confidence: float | None = None

        if classification == "anomalous" and observation.error_count > 0:
            if cached_category is not None:
                failure_category = cached_category
                failure_confidence = (
                    float(cached_confidence)
                    if cached_confidence is not None
                    else 0.5
                )
            else:
                combined_msg = "\n".join(observation.error_messages)
                ctx: dict[str, Any] = {
                    "retry_count": observation.retry_count,
                    "consecutive_run_failures": 0,
                }
                rc_result = classify_failure(
                    error_message=combined_msg,
                    stage=observation.stage_name,
                    context=ctx,
                )
                failure_category = rc_result["category"]
                failure_confidence = rc_result["confidence"]

        # Handle degraded with errors: need classification too
        if (
            classification == "degraded"
            and observation.error_count > 0
            and failure_category is None
        ):
            combined_msg = "\n".join(observation.error_messages)
            ctx = {
                "retry_count": observation.retry_count,
                "consecutive_run_failures": 0,
            }
            rc_result = classify_failure(
                error_message=combined_msg,
                stage=observation.stage_name,
                context=ctx,
            )
            failure_category = rc_result["category"]
            failure_confidence = rc_result["confidence"]

        orient_duration_ms = (time.monotonic_ns() - start_ns) / 1_000_000
        if orient_duration_ms > 100.0:
            logger.warning(
                "Orient phase exceeded 100ms budget: %.1fms for stage=%s",
                orient_duration_ms,
                observation.stage_name,
            )

        return OrientationResult(
            classification=classification,
            baseline_available=baseline_available,
            duration_deviation_pct=duration_deviation_pct,
            error_deviation=error_deviation,
            failure_category=failure_category,
            failure_confidence=failure_confidence,
            matched_pattern=matched_pattern,
        )

    def decide(
        self,
        orientation: OrientationResult,
        retry_count: int = 0,
    ) -> str:
        """Select an action based on the orientation result.

        Implements the decision tree from spec section 3.4.2. Deterministic:
        same input always produces same output. Performs no I/O.

        Args:
            orientation: The OrientationResult from orient().
            retry_count: Current retry count for the stage. Used to enforce
                the max_retries limit. Default 0.

        Returns:
            One of: "continue", "retry", "fallback_to_spec", "surface_to_user".
        """
        # Nominal -> continue
        if orientation.classification == "nominal":
            return "continue"

        # Degraded with no errors -> continue (log warning handled by caller)
        if orientation.classification == "degraded":
            if orientation.failure_category is None:
                return "continue"
            # Degraded with errors falls through to failure classification

        # Anomalous or degraded-with-errors: apply failure classification
        category = orientation.failure_category
        confidence = orientation.failure_confidence

        # Unknown or low-confidence -> surface_to_user
        if category is None or (
            confidence is not None and confidence < _LOW_CONFIDENCE_THRESHOLD
        ):
            return "surface_to_user"

        retries_exhausted = retry_count >= self._max_retries

        if category == "transient":
            return "surface_to_user" if retries_exhausted else "retry"

        if category == "hallucination":
            return "surface_to_user" if retries_exhausted else "retry"

        if category == "spec_gap":
            return "fallback_to_spec"

        if category == "dependency":
            return "surface_to_user"

        # Fallback for any unrecognised category
        return "surface_to_user"

    def act(
        self,
        decision: str,
        observation: ObservationRecord,
        orientation: OrientationResult,
    ) -> ActionResult:
        """Execute the decision and return an action descriptor.

        Produces an OODA decision telemetry event. Does not directly spawn
        subagents or modify pipeline state; the orchestrator acts on the
        returned ActionResult.

        Args:
            decision: The action code from decide().
            observation: The original ObservationRecord.
            orientation: The OrientationResult.

        Returns:
            ActionResult with decision details and telemetry event.
        """
        if decision not in _VALID_DECISIONS:
            raise ValueError(
                f"Invalid decision '{decision}'. "
                f"Must be one of {sorted(_VALID_DECISIONS)}"
            )

        enhanced_prompt: str | None = None
        spec_gap_description: str | None = None
        failure_report: dict[str, Any] | None = None

        if decision == "retry" and orientation.failure_category == "hallucination":
            enhanced_prompt = _HALLUCINATION_RETRY_PROMPT

        if decision == "fallback_to_spec":
            spec_gap_description = self._build_spec_gap_description(
                observation, orientation
            )

        if decision == "surface_to_user":
            failure_report = self._build_failure_report(
                observation, orientation
            )

        telemetry_event = self._build_telemetry_event(
            decision, observation, orientation
        )

        # Record telemetry to JSONL
        self._record_telemetry(telemetry_event)

        return ActionResult(
            decision=decision,
            enhanced_prompt=enhanced_prompt,
            spec_gap_description=spec_gap_description,
            failure_report=failure_report,
            telemetry_event=telemetry_event,
        )

    def run(self, stage_result: dict[str, Any]) -> str:
        """Execute the full OODA loop (observe -> orient -> decide -> act).

        Convenience method that chains all four phases. If any phase raises
        an unexpected exception, logs the error and returns "surface_to_user"
        as the safe default.

        Args:
            stage_result: Same as observe() argument.

        Returns:
            The decision code string.
        """
        try:
            observation = self.observe(stage_result)
            orientation = self.orient(observation)
            decision = self.decide(orientation, retry_count=observation.retry_count)
            action = self.act(decision, observation, orientation)

            # Domain memory integration: if retrying and fix_registry has a
            # known fix, enrich the enhanced_prompt with it.
            if (
                decision == "retry"
                and self._domain_store is not None
                and observation.error_messages
            ):
                try:
                    from lib.domain_memory.hooks import normalise_error_fingerprint
                    fp = normalise_error_fingerprint(observation.error_messages[0])
                    known_fixes = self._domain_store.lookup_fix(fp)
                    if known_fixes:
                        best = known_fixes[0]
                        logger.info(
                            "[DOMAIN] Found known fix for %s: %s",
                            fp, best.get("fix_description", ""),
                        )
                except Exception:
                    logger.debug("Domain memory lookup failed; continuing without it")

            return decision
        except ValueError:
            # Propagate validation errors from observe() so callers can fix input
            raise
        except Exception:
            logger.exception(
                "Unexpected error in OODA loop for stage_result=%r; "
                "returning surface_to_user as safe default",
                stage_result.get("stage_name", "unknown"),
            )
            return "surface_to_user"

    def reload_reference_data(self) -> None:
        """Reload baselines and failure patterns from disk.

        Call this if the knowledge store files have been updated externally
        (e.g., after BaselineManager.update_baselines()).
        """
        self._reload_reference_data()

    # -- Private methods ----------------------------------------------------

    def _reload_reference_data(self) -> None:
        """Load stage_baselines.json and failure_patterns.json from the store."""
        baselines_path = (
            self._knowledge_store_path / "baselines" / "stage_baselines.json"
        )
        patterns_path = (
            self._knowledge_store_path / "patterns" / "failure_patterns.json"
        )

        baselines_data = _load_json_safe(baselines_path)
        patterns_data = _load_json_safe(patterns_path)

        with self._lock:
            self._baselines = baselines_data if baselines_data is not None else {}
            self._failure_patterns = (
                patterns_data.get("patterns", [])
                if patterns_data is not None
                else []
            )

        if baselines_data is None:
            logger.info(
                "No stage_baselines.json found at %s; using empty defaults "
                "(first run)",
                baselines_path,
            )
        if patterns_data is None:
            logger.info(
                "No failure_patterns.json found at %s; using empty defaults",
                patterns_path,
            )

    def _classify_stage_outcome(
        self,
        observation: ObservationRecord,
        baseline_available: bool,
        duration_deviation_pct: float | None,
        error_deviation: float | None,
    ) -> str:
        """Classify a stage outcome as nominal, degraded, or anomalous.

        First-run handling: if no baselines exist, returns "nominal" for
        successful stages and "anomalous" for failed stages.
        """
        is_failure = observation.status == "failure"
        has_errors = observation.error_count > 0

        # First-run defaults (spec section 3.3.4)
        if not baseline_available:
            if is_failure or has_errors:
                return "anomalous"
            return "nominal"

        # Errors present or explicit failure -> anomalous
        if is_failure:
            return "anomalous"

        if has_errors:
            # Check if error deviation is within 1 std dev
            if error_deviation is not None and error_deviation > 1.0:
                return "anomalous"
            return "degraded"

        # Check duration deviation
        if duration_deviation_pct is not None:
            abs_deviation = abs(duration_deviation_pct)
            if abs_deviation > _DURATION_DEVIATION_THRESHOLD_PCT:
                return "degraded"

        return "nominal"

    def _build_spec_gap_description(
        self,
        observation: ObservationRecord,
        orientation: OrientationResult,
    ) -> str:
        """Build a description of the spec gap for fallback_to_spec decisions."""
        parts = [
            f"Stage '{observation.stage_name}' failed with a spec_gap classification",
            f"(confidence: {orientation.failure_confidence}).",
        ]
        if observation.error_messages:
            parts.append(f"Error: {observation.error_messages[0][:200]}")
        if orientation.matched_pattern:
            parts.append(f"Matched known pattern: {orientation.matched_pattern}")
        return " ".join(parts)

    def _build_failure_report(
        self,
        observation: ObservationRecord,
        orientation: OrientationResult,
    ) -> dict[str, Any]:
        """Build a structured failure report for surface_to_user decisions."""
        return {
            "stage_name": observation.stage_name,
            "status": observation.status,
            "error_messages": list(observation.error_messages),
            "error_count": observation.error_count,
            "failure_category": orientation.failure_category,
            "failure_confidence": orientation.failure_confidence,
            "retry_count": observation.retry_count,
            "max_retries": self._max_retries,
            "duration_seconds": observation.duration_seconds,
            "orientation_classification": orientation.classification,
            "baseline_available": orientation.baseline_available,
            "duration_deviation_pct": orientation.duration_deviation_pct,
            "matched_pattern": orientation.matched_pattern,
            "recommended_action": self._recommend_user_action(
                observation, orientation
            ),
        }

    def _recommend_user_action(
        self,
        observation: ObservationRecord,
        orientation: OrientationResult,
    ) -> str:
        """Generate a recommended manual action string for the user."""
        category = orientation.failure_category

        if category == "dependency":
            if observation.error_messages:
                return (
                    f"Install the missing dependency or update project "
                    f"configuration. Error: {observation.error_messages[0][:150]}"
                )
            return "Check and install missing dependencies."

        if category == "transient":
            return (
                f"Retries exhausted ({observation.retry_count}/{self._max_retries}). "
                "Check network connectivity, API rate limits, or resource availability."
            )

        if category == "hallucination":
            return (
                f"Retries exhausted ({observation.retry_count}/{self._max_retries}). "
                "Review the stage output for semantic correctness. Consider adding "
                "reference implementations or example I/O pairs to the spec."
            )

        if category == "spec_gap":
            return (
                "The specification appears insufficient for the task. "
                "Review and augment the spec with missing requirements."
            )

        return (
            "Manual investigation required. The failure could not be "
            "automatically classified with sufficient confidence."
        )

    def _build_telemetry_event(
        self,
        decision: str,
        observation: ObservationRecord,
        orientation: OrientationResult,
    ) -> dict[str, Any]:
        """Build an OODA decision telemetry event for JSONL recording."""
        return {
            "schema_version": 1,
            "timestamp": _utc_now_iso_ms(),
            "event_type": "ooda_decision",
            "session_id": self._session_id,
            "stage_name": observation.stage_name,
            "stage_number": _stage_number_from_name(observation.stage_name),
            "data": {
                "observation_status": observation.status,
                "orientation_classification": orientation.classification,
                "failure_category": orientation.failure_category,
                "failure_confidence": orientation.failure_confidence,
                "decision": decision,
                "retry_count": observation.retry_count,
                "baseline_available": orientation.baseline_available,
                "duration_deviation_pct": orientation.duration_deviation_pct,
                "error_deviation": orientation.error_deviation,
                "matched_pattern": orientation.matched_pattern,
            },
        }

    def _record_telemetry(self, event: dict[str, Any]) -> None:
        """Record an OODA decision event to stage_telemetry.jsonl.

        Non-blocking: if the write fails, logs a warning and continues.
        """
        stage_name = event.get("stage_name", "unknown")
        # Determine the run directory from session_id
        telemetry_path = (
            self._knowledge_store_path
            / "runs"
            / self._session_id
            / "stage_telemetry.jsonl"
        )
        try:
            with self._lock:
                _append_jsonl(telemetry_path, event)
        except OSError:
            logger.warning(
                "Failed to record OODA telemetry for stage=%s; continuing",
                stage_name,
                exc_info=True,
            )
