"""Stage metrics collector for the continuous improvement engine.

Captures all 12 DMAIC KPIs (6 per-stage, 6 cross-run) with three-tier
graceful degradation:

  Tier 1: OTel spans/metrics + Prometheus registry + JSONL fallback
  Tier 2: OTel spans/metrics + JSONL fallback (no prometheus-client)
  Tier 3: JSONL fallback only (no opentelemetry-sdk, no prometheus-client)

Thread-safe. All record_* methods are safe for concurrent use.
JSONL writes are serialized via a threading lock.

Dependencies: Python >= 3.11 stdlib only (OTel and Prometheus are optional).
"""

from __future__ import annotations

import collections
import json
import logging
import os
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from lib.ci_engine import knowledge_store_writer

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional dependency detection
# ---------------------------------------------------------------------------

try:
    from opentelemetry import trace as otel_trace
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import (
        InMemoryMetricReader,
    )
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.trace import StatusCode

    HAS_OTEL = True
except ImportError:
    HAS_OTEL = False

try:
    from prometheus_client import (
        CollectorRegistry,
        Counter as PromCounter,
        Gauge as PromGauge,
        Histogram as PromHistogram,
    )

    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_STAGE_NAMES: frozenset[str] = frozenset({
    "researcher",
    "product_manager",
    "spec_creator",
    "software_engineer",
    "test_writer",
    "codebase_stats",
    "validator",
    "technical_writer",
})

STAGE_NAME_TO_NUMBER: dict[str, int] = {
    "researcher": 0,
    "product_manager": 1,
    "spec_creator": 2,
    "software_engineer": 3,
    "test_writer": 4,
    "codebase_stats": 45,
    "validator": 5,
    "technical_writer": 6,
}

VALID_ERROR_TYPES: frozenset[str] = frozenset({
    "transient",
    "spec_gap",
    "dependency",
    "hallucination",
    "resource_exhaustion",
    "configuration",
    "permissions",
    "timeout",
})

VALID_STATUS_VALUES: frozenset[str] = frozenset({
    "success",
    "partial",
    "failure",
})

STAGE_DURATION_BUCKETS = (
    1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0, 600.0, float("inf"),
)

RUN_DURATION_BUCKETS = (
    60.0, 120.0, 300.0, 600.0, 1200.0, 1800.0, 3600.0, float("inf"),
)

_SERVICE_NAME = "auto-orchestrate-ci-engine"
_SERVICE_VERSION = "1.0.0"

_SUCCESS_RATE_WINDOW = 10

# Bit position for each stage in the failure bitmap
_STAGE_BIT_POSITIONS: dict[str, int] = {
    "researcher": 0,
    "product_manager": 1,
    "spec_creator": 2,
    "software_engineer": 3,
    "test_writer": 4,
    "codebase_stats": 5,
    "validator": 6,
    "technical_writer": 7,
}

# Composite quality score weights for improvement_delta_pct
_WEIGHT_SPEC_COMPLIANCE = 0.4
_WEIGHT_TEST_COVERAGE = 0.3
_WEIGHT_ERROR_RATE = 0.3


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _utc_now_iso() -> str:
    """Return current UTC time as ISO 8601 string with microseconds."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _validate_stage_name(stage_name: str) -> None:
    """Raise ValueError if stage_name is not recognized."""
    if stage_name not in VALID_STAGE_NAMES:
        raise ValueError(
            f"Invalid stage_name '{stage_name}'. "
            f"Must be one of {sorted(VALID_STAGE_NAMES)}"
        )


def _validate_error_type(error_type: str) -> None:
    """Raise ValueError if error_type is not recognized."""
    if error_type not in VALID_ERROR_TYPES:
        raise ValueError(
            f"Invalid error_type '{error_type}'. "
            f"Must be one of {sorted(VALID_ERROR_TYPES)}"
        )


def _validate_status(status: str) -> None:
    """Raise ValueError if status is not recognized."""
    if status not in VALID_STATUS_VALUES:
        raise ValueError(
            f"Invalid status '{status}'. "
            f"Must be one of {sorted(VALID_STATUS_VALUES)}"
        )


def _read_recent_stage_ends(
    telemetry_path: Path,
    stage_name: str,
    window: int,
) -> list[dict]:
    """Read the last *window* stage_end events for a given stage from JSONL."""
    matches: list[dict] = []
    if not telemetry_path.is_file():
        return matches
    with open(telemetry_path, "r", encoding="utf-8") as fh:
        for line in fh:
            stripped = line.strip()
            if not stripped:
                continue
            try:
                record = json.loads(stripped)
            except json.JSONDecodeError:
                continue
            if (
                record.get("event_type") == "stage_end"
                and record.get("stage_name") == stage_name
            ):
                matches.append(record)
    return matches[-window:]


def _compute_success_rate(
    telemetry_path: Path,
    stage_name: str,
) -> float:
    """Compute rolling success rate over the last 10 stage_end events."""
    recent = _read_recent_stage_ends(
        telemetry_path, stage_name, _SUCCESS_RATE_WINDOW,
    )
    if not recent:
        return 1.0
    successes = sum(
        1 for r in recent
        if r.get("data", {}).get("status") == "success"
    )
    return round(successes / len(recent), 4)


def _load_previous_run_composite(
    telemetry_path: Path,
    current_run_sequence: int,
) -> float | None:
    """Load the composite quality score from the previous run's finalize event."""
    if not telemetry_path.is_file():
        return None
    candidates: list[dict] = []
    with open(telemetry_path, "r", encoding="utf-8") as fh:
        for line in fh:
            stripped = line.strip()
            if not stripped:
                continue
            try:
                record = json.loads(stripped)
            except json.JSONDecodeError:
                continue
            if record.get("event_type") == "run_finalize":
                candidates.append(record)
    if not candidates:
        return None
    last = candidates[-1]
    return last.get("data", {}).get("composite_score")


# ---------------------------------------------------------------------------
# Stage state tracker (per-stage in-flight data)
# ---------------------------------------------------------------------------

class _StageState:
    """Mutable state for a single in-flight stage execution."""

    __slots__ = (
        "stage_name", "stage_number", "start_mono", "start_wall",
        "error_count", "retry_count", "span",
    )

    def __init__(
        self,
        stage_name: str,
        stage_number: int,
        start_mono: float,
        start_wall: str,
    ) -> None:
        self.stage_name = stage_name
        self.stage_number = stage_number
        self.start_mono = start_mono
        self.start_wall = start_wall
        self.error_count: int = 0
        self.retry_count: int = 0
        self.span: Any = None


# ---------------------------------------------------------------------------
# StageMetricsCollector
# ---------------------------------------------------------------------------

class StageMetricsCollector:
    """Collects all 12 DMAIC KPIs with three-tier graceful degradation.

    Use as a context manager to ensure resources are released:

        with StageMetricsCollector(session_id, telemetry_dir) as collector:
            collector.record_stage_start("researcher", 0)
            ...
            collector.record_stage_end("researcher", "success")
            summary = collector.finalize_run()
    """

    def __init__(
        self,
        session_id: str,
        telemetry_dir: Path,
        run_sequence: int = 1,
    ) -> None:
        self._session_id = session_id
        self._telemetry_dir = Path(telemetry_dir)
        self._run_sequence = run_sequence
        self._closed = False

        self._lock = threading.Lock()

        # Per-stage in-flight state keyed by stage_name
        self._active_stages: dict[str, _StageState] = {}

        # Completed stage data keyed by stage_name
        self._completed_stages: dict[str, dict[str, Any]] = {}

        # Rolling outcome deque for O(1) success rate computation
        self._recent_outcomes: collections.deque[bool] = collections.deque(
            maxlen=_SUCCESS_RATE_WINDOW,
        )

        # Run-level accumulators
        self._failure_bitmap: int = 0
        self._first_start_mono: float | None = None
        self._last_end_mono: float | None = None
        self._spec_compliance_score: float | None = None
        self._test_coverage_pct: float | None = None
        self._research_completeness_score: float | None = None
        self._total_error_count: int = 0
        self._total_stages_run: int = 0

        # JSONL telemetry file path
        os.makedirs(self._telemetry_dir, exist_ok=True)
        self._telemetry_path = self._telemetry_dir / "stage_telemetry.jsonl"

        # Determine degradation tier and initialize backends
        self._tier = self._detect_tier()
        self._init_otel()
        self._init_prometheus()

        tier_labels = {
            1: "Tier 1 (OTel + Prometheus + JSONL)",
            2: "Tier 2 (OTel + JSONL, prometheus-client not found)",
            3: "Tier 3 (JSONL fallback, opentelemetry-sdk not found)",
        }
        logger.info(
            "StageMetricsCollector initialized at %s", tier_labels[self._tier],
        )

    # -- Tier detection -----------------------------------------------------

    @staticmethod
    def _detect_tier() -> int:
        """Select the degradation tier based on available packages."""
        if HAS_OTEL and HAS_PROMETHEUS:
            return 1
        if HAS_OTEL:
            return 2
        return 3

    # -- OTel initialization ------------------------------------------------

    def _init_otel(self) -> None:
        """Initialize local OTel tracer and meter providers (Tier 1/2)."""
        self._tracer_provider: Any = None
        self._meter_provider: Any = None
        self._tracer: Any = None
        self._stage_meter: Any = None
        self._run_meter: Any = None
        self._root_span: Any = None
        self._root_span_ctx: Any = None

        # OTel instruments (set to None for Tier 3)
        self._otel_stage_duration: Any = None
        self._otel_stage_error: Any = None
        self._otel_stage_retry: Any = None
        self._otel_stage_token_input: Any = None
        self._otel_stage_token_output: Any = None
        self._otel_run_duration: Any = None

        if self._tier >= 3:
            return

        resource = Resource.create({
            "service.name": _SERVICE_NAME,
            "service.version": _SERVICE_VERSION,
        })

        self._tracer_provider = TracerProvider(resource=resource)
        self._metric_reader = InMemoryMetricReader()
        self._meter_provider = MeterProvider(
            resource=resource,
            metric_readers=[self._metric_reader],
        )

        self._tracer = self._tracer_provider.get_tracer(
            "auto_orchestrate.ci_engine.stage",
        )

        self._stage_meter = self._meter_provider.get_meter(
            "auto_orchestrate.ci_engine.stage",
        )
        self._run_meter = self._meter_provider.get_meter(
            "auto_orchestrate.ci_engine.run",
        )

        # Per-stage instruments
        self._otel_stage_duration = self._stage_meter.create_histogram(
            name="pipeline_stage_duration_seconds",
            description="Duration of pipeline stage execution in seconds",
            unit="s",
        )
        self._otel_stage_error = self._stage_meter.create_counter(
            name="pipeline_stage_error_total",
            description="Total errors encountered during stage execution",
            unit="errors",
        )
        self._otel_stage_retry = self._stage_meter.create_counter(
            name="pipeline_stage_retry_total",
            description="Total retry attempts for stage execution",
            unit="retries",
        )
        self._otel_stage_token_input = self._stage_meter.create_counter(
            name="pipeline_stage_token_input_total",
            description="Total input tokens consumed by stage",
            unit="tokens",
        )
        self._otel_stage_token_output = self._stage_meter.create_counter(
            name="pipeline_stage_token_output_total",
            description="Total output tokens produced by stage",
            unit="tokens",
        )

        # Cross-run instruments
        self._otel_run_duration = self._run_meter.create_histogram(
            name="pipeline_run_duration_seconds",
            description="Duration of complete pipeline run in seconds",
            unit="s",
        )

        # Start root span for the pipeline run
        self._root_span = self._tracer.start_span("pipeline.run")
        self._root_span.set_attribute("session.id", self._session_id)
        self._root_span.set_attribute(
            "pipeline.run_sequence", self._run_sequence,
        )
        self._root_span_ctx = otel_trace.set_span_in_context(self._root_span)

    # -- Prometheus initialization ------------------------------------------

    def _init_prometheus(self) -> None:
        """Initialize Prometheus metrics registry (Tier 1 only)."""
        self._prom_registry: Any = None
        self._prom_stage_duration: Any = None
        self._prom_stage_error: Any = None
        self._prom_stage_retry: Any = None
        self._prom_stage_token_input: Any = None
        self._prom_stage_token_output: Any = None
        self._prom_stage_success_rate: Any = None
        self._prom_run_duration: Any = None
        self._prom_run_failure_bitmap: Any = None
        self._prom_run_spec_compliance: Any = None
        self._prom_run_test_coverage: Any = None
        self._prom_run_improvement_delta: Any = None
        self._prom_run_research_completeness: Any = None

        if self._tier != 1:
            return

        self._prom_registry = CollectorRegistry()

        self._prom_stage_duration = PromHistogram(
            "pipeline_stage_duration_seconds",
            "Duration of pipeline stage execution in seconds",
            labelnames=["stage"],
            buckets=STAGE_DURATION_BUCKETS,
            registry=self._prom_registry,
        )
        self._prom_stage_error = PromCounter(
            "pipeline_stage_error_total",
            "Total errors encountered during stage execution",
            labelnames=["stage", "error_type"],
            registry=self._prom_registry,
        )
        self._prom_stage_retry = PromCounter(
            "pipeline_stage_retry_total",
            "Total retry attempts for stage execution",
            labelnames=["stage"],
            registry=self._prom_registry,
        )
        self._prom_stage_token_input = PromCounter(
            "pipeline_stage_token_input_total",
            "Total input tokens consumed by stage",
            labelnames=["stage"],
            registry=self._prom_registry,
        )
        self._prom_stage_token_output = PromCounter(
            "pipeline_stage_token_output_total",
            "Total output tokens produced by stage",
            labelnames=["stage"],
            registry=self._prom_registry,
        )
        self._prom_stage_success_rate = PromGauge(
            "pipeline_stage_success_rate",
            "Rolling 10-run success rate for stage (0.0-1.0)",
            labelnames=["stage"],
            registry=self._prom_registry,
        )
        self._prom_run_duration = PromHistogram(
            "pipeline_run_duration_seconds",
            "Duration of complete pipeline run in seconds",
            buckets=RUN_DURATION_BUCKETS,
            registry=self._prom_registry,
        )
        self._prom_run_failure_bitmap = PromGauge(
            "pipeline_run_stage_failure_bitmap",
            "Bitmask of stages that failed during run",
            registry=self._prom_registry,
        )
        self._prom_run_spec_compliance = PromGauge(
            "pipeline_run_spec_compliance_score",
            "Specification compliance score (0-100)",
            registry=self._prom_registry,
        )
        self._prom_run_test_coverage = PromGauge(
            "pipeline_run_test_coverage_pct",
            "Test coverage percentage (0-100)",
            registry=self._prom_registry,
        )
        self._prom_run_improvement_delta = PromGauge(
            "pipeline_run_improvement_delta_pct",
            "Improvement delta vs previous run (percentage)",
            registry=self._prom_registry,
        )
        self._prom_run_research_completeness = PromGauge(
            "pipeline_run_research_completeness_score",
            "Research completeness score (0-100)",
            registry=self._prom_registry,
        )

    # -- Context manager ----------------------------------------------------

    def __enter__(self) -> StageMetricsCollector:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        self.close()

    # -- Guard --------------------------------------------------------------

    def _ensure_open(self) -> None:
        """Raise RuntimeError if the collector has been closed."""
        if self._closed:
            raise RuntimeError(
                "StageMetricsCollector has been closed; "
                "record_* methods cannot be called after close()"
            )

    # -- JSONL emission -----------------------------------------------------

    def _emit_jsonl(
        self,
        event_type: str,
        stage_name: str,
        stage_number: int,
        data: dict[str, Any],
    ) -> None:
        """Append a single JSONL telemetry event with flush+fsync."""
        record = {
            "schema_version": 1,
            "timestamp": _utc_now_iso(),
            "event_type": event_type,
            "session_id": self._session_id,
            "stage_name": stage_name,
            "stage_number": stage_number,
            "data": data,
        }
        with open(self._telemetry_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False))
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())

    # -- OTel attribute helpers ---------------------------------------------

    def _stage_attributes(
        self, stage_name: str, stage_number: int,
    ) -> dict[str, str | int]:
        """Build the required OTel attribute dict for a stage."""
        return {
            "stage.name": stage_name,
            "session.id": self._session_id,
            "pipeline.stage_number": stage_number,
            "pipeline.run_sequence": self._run_sequence,
        }

    # -- Knowledge store integration ----------------------------------------

    def _emit_to_knowledge_store(
        self,
        stage_name: str,
        event_type: str,
        duration_seconds: float,
        error_count: int,
        token_count: int,
        retry_count: int,
    ) -> None:
        """Write telemetry event to the knowledge store via the writer."""
        try:
            knowledge_store_writer.append_stage_telemetry(
                store_path=self._telemetry_dir,
                run_id=f"{self._session_id}-run-{self._run_sequence}",
                stage=stage_name,
                event_type=event_type,
                timestamp=_utc_now_iso(),
                duration_seconds=duration_seconds,
                error_count=error_count,
                token_count=token_count,
                retry_count=retry_count,
            )
        except (ValueError, OSError):
            logger.warning(
                "Failed to write to knowledge store for %s/%s",
                stage_name,
                event_type,
                exc_info=True,
            )

    # -- Public API ---------------------------------------------------------

    def record_stage_start(
        self,
        stage_name: str,
        stage_number: int,
    ) -> None:
        """Record the start of a pipeline stage.

        Args:
            stage_name: One of the 8 valid stage names.
            stage_number: Numeric stage index (0-6, with codebase_stats=45).

        Raises:
            ValueError: If stage_name is not recognized.
            RuntimeError: If called twice without an intervening record_stage_end,
                          or if the collector is closed.
        """
        self._ensure_open()
        _validate_stage_name(stage_name)

        mono_now = time.monotonic()
        wall_now = _utc_now_iso()

        with self._lock:
            if stage_name in self._active_stages:
                raise RuntimeError(
                    f"Stage '{stage_name}' already started. "
                    "Call record_stage_end() before starting again."
                )

            state = _StageState(stage_name, stage_number, mono_now, wall_now)

            # Track first stage start for run duration
            if self._first_start_mono is None:
                self._first_start_mono = mono_now

            # Start OTel span (Tier 1/2)
            if self._tier <= 2 and self._tracer is not None:
                span = self._tracer.start_span(
                    f"pipeline.{stage_name}",
                    context=self._root_span_ctx,
                    attributes=self._stage_attributes(
                        stage_name, stage_number,
                    ),
                )
                state.span = span

            self._active_stages[stage_name] = state

        # JSONL emission (outside lock to minimize hold time)
        self._emit_jsonl(
            event_type="stage_start",
            stage_name=stage_name,
            stage_number=stage_number,
            data={"run_sequence": self._run_sequence},
        )

        self._emit_to_knowledge_store(
            stage_name=stage_name,
            event_type="stage_start",
            duration_seconds=0.0,
            error_count=0,
            token_count=0,
            retry_count=0,
        )

        logger.info(
            "Stage '%s' started (run_sequence=%d)",
            stage_name, self._run_sequence,
        )

    def record_stage_end(
        self,
        stage_name: str,
        status: str,
        token_input: int = 0,
        token_output: int = 0,
        spec_compliance_score: float | None = None,
        test_coverage_pct: float | None = None,
        research_completeness_score: float | None = None,
    ) -> None:
        """Record the end of a pipeline stage.

        Args:
            stage_name: Must match a prior record_stage_start() call.
            status: One of "success", "partial", "failure".
            token_input: Input tokens consumed (>= 0).
            token_output: Output tokens produced (>= 0).
            spec_compliance_score: Stage 5 validator score (0-100), or None.
            test_coverage_pct: Stage 4/4.5 coverage (0-100), or None.
            research_completeness_score: Stage 0 score (0-100), or None.

        Raises:
            ValueError: If stage_name has no matching start or status is invalid.
            RuntimeError: If the collector is closed.
        """
        self._ensure_open()
        _validate_status(status)

        mono_now = time.monotonic()

        with self._lock:
            state = self._active_stages.pop(stage_name, None)
            if state is None:
                raise ValueError(
                    f"No matching record_stage_start() for stage '{stage_name}'"
                )

            duration = mono_now - state.start_mono
            self._last_end_mono = mono_now
            self._total_stages_run += 1

            # Store optional cross-run scores
            if spec_compliance_score is not None:
                self._spec_compliance_score = spec_compliance_score
            if test_coverage_pct is not None:
                self._test_coverage_pct = test_coverage_pct
            if research_completeness_score is not None:
                self._research_completeness_score = research_completeness_score

            error_count = state.error_count
            retry_count = state.retry_count
            span = state.span

            # Track completed stage data for finalize_run()
            self._completed_stages[stage_name] = {
                "status": status,
                "duration_seconds": round(duration, 6),
                "error_count": error_count,
                "retry_count": retry_count,
            }

            # Append outcome for O(1) success rate lookups
            self._recent_outcomes.append(status == "success")

        # Compute success rate (O(1) from deque, cold-start fallback)
        success_rate = self._get_success_rate(stage_name)

        # OTel recording (Tier 1/2)
        if self._tier <= 2:
            attrs = self._stage_attributes(
                stage_name, STAGE_NAME_TO_NUMBER[stage_name],
            )
            if self._otel_stage_duration is not None:
                self._otel_stage_duration.record(duration, attributes=attrs)
            if self._otel_stage_token_input is not None:
                self._otel_stage_token_input.add(token_input, attributes=attrs)
            if self._otel_stage_token_output is not None:
                self._otel_stage_token_output.add(
                    token_output, attributes=attrs,
                )
            if span is not None:
                if status == "success":
                    span.set_status(StatusCode.OK)
                elif status == "failure":
                    span.set_status(StatusCode.ERROR, "Stage failed")
                span.set_attribute("stage.duration_seconds", duration)
                span.set_attribute("stage.token_input", token_input)
                span.set_attribute("stage.token_output", token_output)
                span.set_attribute("stage.status", status)
                span.set_attribute("stage.success_rate", success_rate)
                span.end()

        # Prometheus recording (Tier 1)
        if self._tier == 1:
            self._prom_stage_duration.labels(stage=stage_name).observe(
                duration,
            )
            self._prom_stage_token_input.labels(stage=stage_name).inc(
                token_input,
            )
            self._prom_stage_token_output.labels(stage=stage_name).inc(
                token_output,
            )
            self._prom_stage_success_rate.labels(stage=stage_name).set(
                success_rate,
            )

        # Build JSONL data payload
        jsonl_data: dict[str, Any] = {
            "duration_seconds": round(duration, 6),
            "status": status,
            "token_input": token_input,
            "token_output": token_output,
            "success_rate": success_rate,
        }
        if spec_compliance_score is not None:
            jsonl_data["spec_compliance_score"] = spec_compliance_score
        if test_coverage_pct is not None:
            jsonl_data["test_coverage_pct"] = test_coverage_pct
        if research_completeness_score is not None:
            jsonl_data["research_completeness_score"] = (
                research_completeness_score
            )

        self._emit_jsonl(
            event_type="stage_end",
            stage_name=stage_name,
            stage_number=STAGE_NAME_TO_NUMBER[stage_name],
            data=jsonl_data,
        )

        self._emit_to_knowledge_store(
            stage_name=stage_name,
            event_type="stage_end",
            duration_seconds=round(duration, 6),
            error_count=error_count,
            token_count=token_input + token_output,
            retry_count=retry_count,
        )

        logger.info(
            "Stage '%s' ended: status=%s, duration=%.3fs",
            stage_name, status, duration,
        )

    def record_stage_error(
        self,
        stage_name: str,
        error_type: str,
        error_message: str,
    ) -> None:
        """Record an error during stage execution.

        Args:
            stage_name: Must match a prior record_stage_start() call.
            error_type: One of "transient", "spec_gap", "dependency",
                        "hallucination".
            error_message: Human-readable error description.

        Raises:
            ValueError: If error_type is not valid.
            RuntimeError: If the collector is closed.
        """
        self._ensure_open()
        _validate_error_type(error_type)

        stage_number = STAGE_NAME_TO_NUMBER.get(stage_name, -1)

        with self._lock:
            state = self._active_stages.get(stage_name)
            if state is not None:
                state.error_count += 1

            self._total_error_count += 1

            # Set the failure bit for this stage
            bit_pos = _STAGE_BIT_POSITIONS.get(stage_name)
            if bit_pos is not None:
                self._failure_bitmap |= (1 << bit_pos)

            failure_bitmap_snapshot = self._failure_bitmap
            span = state.span if state is not None else None

        # OTel span event (Tier 1/2)
        if self._tier <= 2 and span is not None:
            span.add_event(
                "exception",
                attributes={
                    "error.type": error_type,
                    "error.message": error_message,
                },
            )
            span.set_status(StatusCode.ERROR, error_message[:256])

        # Prometheus counter (Tier 1)
        if self._tier == 1:
            self._prom_stage_error.labels(
                stage=stage_name, error_type=error_type,
            ).inc()

        # OTel counter (Tier 1/2)
        if self._tier <= 2 and self._otel_stage_error is not None:
            attrs = self._stage_attributes(stage_name, stage_number)
            self._otel_stage_error.add(1, attributes=attrs)

        self._emit_jsonl(
            event_type="stage_error",
            stage_name=stage_name,
            stage_number=stage_number,
            data={
                "error_type": error_type,
                "error_message": error_message,
                "stage_failure_bitmap": failure_bitmap_snapshot,
            },
        )

        logger.warning(
            "Stage '%s' error: [%s] %s",
            stage_name, error_type, error_message[:200],
        )

    def record_stage_retry(
        self,
        stage_name: str,
        reason: str,
    ) -> None:
        """Record a retry attempt for a stage.

        Args:
            stage_name: Must match a prior record_stage_start() call.
            reason: Classification of why the retry was triggered.

        Raises:
            RuntimeError: If the collector is closed.
        """
        self._ensure_open()

        stage_number = STAGE_NAME_TO_NUMBER.get(stage_name, -1)

        with self._lock:
            state = self._active_stages.get(stage_name)
            retry_number = 0
            if state is not None:
                state.retry_count += 1
                retry_number = state.retry_count
            span = state.span if state is not None else None

        # OTel span event (Tier 1/2)
        if self._tier <= 2 and span is not None:
            span.add_event(
                "retry",
                attributes={
                    "retry.reason": reason,
                    "retry.number": retry_number,
                },
            )

        # OTel counter (Tier 1/2)
        if self._tier <= 2 and self._otel_stage_retry is not None:
            attrs = self._stage_attributes(stage_name, stage_number)
            self._otel_stage_retry.add(1, attributes=attrs)

        # Prometheus counter (Tier 1)
        if self._tier == 1:
            self._prom_stage_retry.labels(stage=stage_name).inc()

        self._emit_jsonl(
            event_type="stage_retry",
            stage_name=stage_name,
            stage_number=stage_number,
            data={
                "retry_number": retry_number,
                "reason": reason,
            },
        )

        logger.info(
            "Stage '%s' retry #%d: %s", stage_name, retry_number, reason,
        )

    def finalize_run(self) -> dict[str, Any]:
        """Finalize metrics for the current pipeline run.

        Collects completed stage data into a run summary, persists it via
        knowledge_store_writer, emits a run_finalize telemetry event, and
        returns all 12 KPI values.

        Returns:
            dict with run summary including ``run_id``, ``completed_at``,
            ``overall_status``, ``stages``, and ``kpis``.  KPIs that were
            not emitted are absent from the nested ``kpis`` dict.
        """
        self._ensure_open()

        kpis: dict[str, Any] = {}

        with self._lock:
            failure_bitmap = self._failure_bitmap
            first_start = self._first_start_mono
            last_end = self._last_end_mono
            spec_score = self._spec_compliance_score
            test_cov = self._test_coverage_pct
            research_score = self._research_completeness_score
            total_errors = self._total_error_count
            total_stages = self._total_stages_run
            completed_stages_snapshot = dict(self._completed_stages)

        # KPI 7: run_total_duration_seconds
        run_duration: float | None = None
        if first_start is not None and last_end is not None:
            run_duration = last_end - first_start
            kpis["run_total_duration_seconds"] = round(run_duration, 6)

            if self._tier <= 2 and self._otel_run_duration is not None:
                self._otel_run_duration.record(run_duration)

            if self._tier == 1:
                self._prom_run_duration.observe(run_duration)

        # KPI 8: run_stage_failure_bitmap
        kpis["run_stage_failure_bitmap"] = failure_bitmap
        if self._tier == 1:
            self._prom_run_failure_bitmap.set(failure_bitmap)

        # KPI 9: spec_compliance_score
        if spec_score is not None:
            kpis["spec_compliance_score"] = spec_score
            if self._tier == 1:
                self._prom_run_spec_compliance.set(spec_score)

        # KPI 10: test_coverage_pct
        if test_cov is not None:
            kpis["test_coverage_pct"] = test_cov
            if self._tier == 1:
                self._prom_run_test_coverage.set(test_cov)

        # KPI 12: research_completeness_score
        if research_score is not None:
            kpis["research_completeness_score"] = research_score
            if self._tier == 1:
                self._prom_run_research_completeness.set(research_score)

        # KPI 11: improvement_delta_pct
        current_composite = self._compute_composite_score(
            spec_score, test_cov, total_errors, total_stages,
        )
        if current_composite is not None:
            previous_composite = _load_previous_run_composite(
                self._telemetry_path, self._run_sequence,
            )
            if previous_composite is not None and previous_composite > 0:
                delta = (
                    (current_composite - previous_composite)
                    / previous_composite
                ) * 100.0
                kpis["improvement_delta_pct"] = round(delta, 4)
                if self._tier == 1:
                    self._prom_run_improvement_delta.set(
                        kpis["improvement_delta_pct"],
                    )

        # End root span (Tier 1/2)
        if self._tier <= 2 and self._root_span is not None:
            self._root_span.set_attribute(
                "pipeline.failure_bitmap", failure_bitmap,
            )
            if run_duration is not None:
                self._root_span.set_attribute(
                    "pipeline.total_duration_seconds", run_duration,
                )
            self._root_span.end()
            self._root_span = None

        # Build run summary with completed stage data
        overall_status = "success" if failure_bitmap == 0 else "partial"
        summary: dict[str, Any] = {
            "run_id": self._session_id,
            "completed_at": _utc_now_iso(),
            "run_sequence": self._run_sequence,
            "overall_status": overall_status,
            "stages": {
                name: {
                    "status": data["status"],
                    "duration_seconds": data["duration_seconds"],
                    "error_count": data["error_count"],
                    "retry_count": data["retry_count"],
                }
                for name, data in completed_stages_snapshot.items()
            },
            "kpis": {
                "total_duration_seconds": (
                    round(run_duration, 6) if run_duration is not None else 0.0
                ),
                "spec_compliance_score": spec_score,
                "test_coverage_pct": test_cov,
                "stage_failure_bitmap": failure_bitmap,
                "total_error_count": total_errors,
            },
        }

        # Write finalize event to JSONL for future delta computation
        finalize_data: dict[str, Any] = {
            "run_sequence": self._run_sequence,
            "kpis": kpis,
            "summary": summary,
        }
        if current_composite is not None:
            finalize_data["composite_score"] = current_composite

        self._emit_jsonl(
            event_type="run_finalize",
            stage_name="",
            stage_number=-1,
            data=finalize_data,
        )

        # Persist run summary to knowledge store
        try:
            knowledge_store_writer.write_run_summary(
                store_path=self._telemetry_dir.parent,
                run_id=summary["run_id"],
                completed_at=summary["completed_at"],
                stages=summary["stages"],
                overall_status=summary["overall_status"],
                improvement_notes=[],
                kpis=summary["kpis"],
            )
        except Exception:
            logger.warning(
                "Failed to write run summary to knowledge store",
                exc_info=True,
            )

        logger.info(
            "Run finalized: bitmap=%d, kpi_count=%d, stages=%d",
            failure_bitmap, len(kpis), len(completed_stages_snapshot),
        )

        return summary

    def close(self) -> None:
        """Release all resources held by the collector.

        After calling close(), all record_* methods raise RuntimeError.
        """
        if self._closed:
            return

        self._closed = True

        # End any still-active spans
        with self._lock:
            for state in self._active_stages.values():
                if state.span is not None:
                    try:
                        state.span.set_status(
                            StatusCode.ERROR, "Collector closed before stage end",
                        ) if self._tier <= 2 else None
                        state.span.end() if self._tier <= 2 else None
                    except Exception:
                        logger.warning(
                            "Failed to end span for stage '%s'",
                            state.stage_name,
                            exc_info=True,
                        )
            self._active_stages.clear()

        # End root span if not already ended
        if self._tier <= 2 and self._root_span is not None:
            try:
                self._root_span.end()
            except Exception:
                logger.warning(
                    "Failed to end root span", exc_info=True,
                )
            self._root_span = None

        # Shut down OTel providers
        if self._tier <= 2:
            if self._tracer_provider is not None:
                try:
                    self._tracer_provider.shutdown()
                except Exception:
                    logger.warning(
                        "TracerProvider shutdown failed", exc_info=True,
                    )
            if self._meter_provider is not None:
                try:
                    self._meter_provider.shutdown()
                except Exception:
                    logger.warning(
                        "MeterProvider shutdown failed", exc_info=True,
                    )

        logger.info("StageMetricsCollector closed")

    # -- Internal computation helpers ---------------------------------------

    def _get_success_rate(self, stage_name: str) -> float:
        """Return the rolling success rate for a stage.

        Uses the in-memory deque for O(1) computation when populated.
        Falls back to the module-level ``_compute_success_rate()`` JSONL
        scanner only on cold start (empty deque).

        Args:
            stage_name: The stage to compute success rate for.

        Returns:
            Success rate as a float between 0.0 and 1.0.
        """
        with self._lock:
            if self._recent_outcomes:
                successes = sum(self._recent_outcomes)
                total = len(self._recent_outcomes)
                return round(successes / total, 4)

        # Cold-start fallback: scan JSONL history
        return _compute_success_rate(self._telemetry_path, stage_name)

    @staticmethod
    def _compute_composite_score(
        spec_compliance: float | None,
        test_coverage: float | None,
        total_errors: int,
        total_stages: int,
    ) -> float | None:
        """Compute the composite quality score for improvement delta.

        Formula: 0.4 * spec_compliance + 0.3 * test_coverage
                 + 0.3 * (1 - normalized_error_rate) * 100

        Returns None if neither spec_compliance nor test_coverage is available.
        """
        if spec_compliance is None and test_coverage is None:
            return None

        sc = spec_compliance if spec_compliance is not None else 0.0
        tc = test_coverage if test_coverage is not None else 0.0

        # Normalize error rate: errors per stage, capped at 1.0
        if total_stages > 0:
            normalized_error_rate = min(total_errors / total_stages, 1.0)
        else:
            normalized_error_rate = 0.0

        composite = (
            _WEIGHT_SPEC_COMPLIANCE * sc
            + _WEIGHT_TEST_COVERAGE * tc
            + _WEIGHT_ERROR_RATE * (1.0 - normalized_error_rate) * 100.0
        )
        return round(composite, 4)

    @property
    def tier(self) -> int:
        """Return the active degradation tier (1, 2, or 3)."""
        return self._tier

    @property
    def telemetry_path(self) -> Path:
        """Return the path to the JSONL telemetry file."""
        return self._telemetry_path

    @property
    def prometheus_registry(self) -> Any:
        """Return the Prometheus CollectorRegistry (Tier 1), or None."""
        return self._prom_registry
