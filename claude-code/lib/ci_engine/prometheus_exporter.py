"""Prometheus exporter for Auto-Orchestrate pipeline metrics.

Thin wrapper around prometheus-client (>= 0.21.1) that reads
stage_telemetry.jsonl and exposes all 12 DMAIC KPIs at a /metrics
HTTP endpoint for Prometheus scraping.

Uses a custom CollectorRegistry (never the global default) to avoid
polluting other instrumentation in the same process.

Graceful degradation: if prometheus-client is not installed, all public
functions degrade to no-ops and log a warning. No ImportError is raised
at module load time.

Dependencies: Python >= 3.11 stdlib only (prometheus-client is optional).
"""

from __future__ import annotations

import json
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional dependency detection
# ---------------------------------------------------------------------------

try:
    from prometheus_client import (
        CollectorRegistry,
        Counter as PromCounter,
        Gauge as PromGauge,
        Histogram as PromHistogram,
        generate_latest,
        CONTENT_TYPE_LATEST,
    )

    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

STAGE_DURATION_BUCKETS = (
    1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0, 600.0, float("inf"),
)

RUN_DURATION_BUCKETS = (
    60.0, 120.0, 300.0, 600.0, 1200.0, 1800.0, 3600.0, float("inf"),
)

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

_DEFAULT_PORT = 9090
_DEFAULT_HOST = "0.0.0.0"


# ---------------------------------------------------------------------------
# JSONL reader
# ---------------------------------------------------------------------------

def _read_telemetry_records(telemetry_path: Path) -> list[dict[str, Any]]:
    """Read all valid JSON records from a JSONL file, skipping bad lines."""
    records: list[dict[str, Any]] = []
    if not telemetry_path.is_file():
        return records
    with open(telemetry_path, "r", encoding="utf-8") as fh:
        for line_num, line in enumerate(fh, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                records.append(json.loads(stripped))
            except json.JSONDecodeError:
                logger.warning(
                    "Skipping corrupt JSONL line %d in %s",
                    line_num, telemetry_path,
                )
    return records


# ---------------------------------------------------------------------------
# Metric hydration from JSONL
# ---------------------------------------------------------------------------

def _hydrate_metrics(
    registry: Any,
    telemetry_path: Path,
) -> None:
    """Read stage_telemetry.jsonl and populate Prometheus metrics.

    Creates fresh instruments on the registry each time, then replays
    all events from the JSONL file to set counters, histograms, and
    gauges to their correct cumulative values.
    """
    if not HAS_PROMETHEUS:
        return

    records = _read_telemetry_records(telemetry_path)
    if not records:
        logger.info("No telemetry records found at %s", telemetry_path)
        return

    stage_duration = PromHistogram(
        "pipeline_stage_duration_seconds",
        "Duration of pipeline stage execution in seconds",
        labelnames=["stage"],
        buckets=STAGE_DURATION_BUCKETS,
        registry=registry,
    )
    stage_error_total = PromCounter(
        "pipeline_stage_error_total",
        "Total errors encountered during stage execution",
        labelnames=["stage", "error_type"],
        registry=registry,
    )
    stage_retry_total = PromCounter(
        "pipeline_stage_retry_total",
        "Total retry attempts for stage execution",
        labelnames=["stage"],
        registry=registry,
    )
    stage_token_input_total = PromCounter(
        "pipeline_stage_token_input_total",
        "Total input tokens consumed by stage",
        labelnames=["stage"],
        registry=registry,
    )
    stage_token_output_total = PromCounter(
        "pipeline_stage_token_output_total",
        "Total output tokens produced by stage",
        labelnames=["stage"],
        registry=registry,
    )
    stage_success_rate = PromGauge(
        "pipeline_stage_success_rate",
        "Rolling 10-run success rate for stage (0.0-1.0)",
        labelnames=["stage"],
        registry=registry,
    )
    run_duration = PromHistogram(
        "pipeline_run_duration_seconds",
        "Duration of complete pipeline run in seconds",
        buckets=RUN_DURATION_BUCKETS,
        registry=registry,
    )
    run_failure_bitmap = PromGauge(
        "pipeline_run_stage_failure_bitmap",
        "Bitmask of stages that failed during run",
        registry=registry,
    )
    run_spec_compliance = PromGauge(
        "pipeline_run_spec_compliance_score",
        "Specification compliance score (0-100)",
        registry=registry,
    )
    run_test_coverage = PromGauge(
        "pipeline_run_test_coverage_pct",
        "Test coverage percentage (0-100)",
        registry=registry,
    )
    run_improvement_delta = PromGauge(
        "pipeline_run_improvement_delta_pct",
        "Improvement delta vs previous run (percentage)",
        registry=registry,
    )
    run_research_completeness = PromGauge(
        "pipeline_run_research_completeness_score",
        "Research completeness score (0-100)",
        registry=registry,
    )

    for record in records:
        event_type = record.get("event_type", "")
        stage_name = record.get("stage_name", "")
        data = record.get("data", {})

        if event_type == "stage_end" and stage_name in VALID_STAGE_NAMES:
            duration_val = data.get("duration_seconds")
            if isinstance(duration_val, (int, float)):
                stage_duration.labels(stage=stage_name).observe(duration_val)

            token_in = data.get("token_input", 0)
            if isinstance(token_in, (int, float)) and token_in > 0:
                stage_token_input_total.labels(
                    stage=stage_name,
                ).inc(token_in)

            token_out = data.get("token_output", 0)
            if isinstance(token_out, (int, float)) and token_out > 0:
                stage_token_output_total.labels(
                    stage=stage_name,
                ).inc(token_out)

            success_rate_val = data.get("success_rate")
            if isinstance(success_rate_val, (int, float)):
                stage_success_rate.labels(stage=stage_name).set(
                    success_rate_val,
                )

        elif event_type == "stage_error" and stage_name in VALID_STAGE_NAMES:
            error_type = data.get("error_type", "")
            if error_type in VALID_ERROR_TYPES:
                stage_error_total.labels(
                    stage=stage_name, error_type=error_type,
                ).inc()

        elif event_type == "stage_retry" and stage_name in VALID_STAGE_NAMES:
            stage_retry_total.labels(stage=stage_name).inc()

        elif event_type == "run_finalize":
            kpis = data.get("kpis", {})

            run_dur = kpis.get("run_total_duration_seconds")
            if isinstance(run_dur, (int, float)):
                run_duration.observe(run_dur)

            bitmap = kpis.get("run_stage_failure_bitmap")
            if isinstance(bitmap, int):
                run_failure_bitmap.set(bitmap)

            spec_score = kpis.get("spec_compliance_score")
            if isinstance(spec_score, (int, float)):
                run_spec_compliance.set(spec_score)

            test_cov = kpis.get("test_coverage_pct")
            if isinstance(test_cov, (int, float)):
                run_test_coverage.set(test_cov)

            delta = kpis.get("improvement_delta_pct")
            if isinstance(delta, (int, float)):
                run_improvement_delta.set(delta)

            research_score = kpis.get("research_completeness_score")
            if isinstance(research_score, (int, float)):
                run_research_completeness.set(research_score)

    logger.info(
        "Hydrated Prometheus metrics from %d telemetry records",
        len(records),
    )


# ---------------------------------------------------------------------------
# Registry factory
# ---------------------------------------------------------------------------

def create_registry_from_telemetry(
    telemetry_path: Path,
) -> Any:
    """Create a populated CollectorRegistry from a stage_telemetry.jsonl file.

    Returns a CollectorRegistry with all 12 DMAIC KPIs populated, or None
    if prometheus-client is not installed.

    Args:
        telemetry_path: Path to the stage_telemetry.jsonl file.

    Returns:
        A prometheus_client.CollectorRegistry instance, or None if
        prometheus-client is not available.
    """
    if not HAS_PROMETHEUS:
        logger.warning(
            "prometheus-client not installed; "
            "create_registry_from_telemetry returning None"
        )
        return None

    registry = CollectorRegistry()
    _hydrate_metrics(registry, telemetry_path)
    return registry


def create_registry_from_collector(
    collector: Any,
) -> Any:
    """Extract the CollectorRegistry from a StageMetricsCollector.

    If the collector was initialized at Tier 1, it already has a
    CollectorRegistry with live metrics. This function returns it
    directly. Otherwise returns None.

    Args:
        collector: A StageMetricsCollector instance.

    Returns:
        The collector's prometheus_client.CollectorRegistry, or None.
    """
    if not HAS_PROMETHEUS:
        logger.warning(
            "prometheus-client not installed; "
            "create_registry_from_collector returning None"
        )
        return None

    registry = getattr(collector, "prometheus_registry", None)
    if registry is None:
        logger.warning(
            "Collector has no Prometheus registry (tier=%s); "
            "falling back to JSONL hydration",
            getattr(collector, "tier", "unknown"),
        )
        telemetry_path = getattr(collector, "telemetry_path", None)
        if telemetry_path is not None:
            return create_registry_from_telemetry(telemetry_path)
        return None

    return registry


# ---------------------------------------------------------------------------
# Metrics HTTP handler
# ---------------------------------------------------------------------------

class _MetricsHandler(BaseHTTPRequestHandler):
    """HTTP handler that serves Prometheus metrics at /metrics."""

    registry: Any = None

    def do_GET(self) -> None:
        """Handle GET requests; only /metrics returns metrics output."""
        if self.path == "/metrics":
            self._serve_metrics()
        elif self.path == "/health":
            self._serve_health()
        else:
            self.send_response(404)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"Not Found\n")

    def _serve_metrics(self) -> None:
        """Generate and serve Prometheus exposition format."""
        if self.registry is None:
            self.send_response(503)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"No metrics registry configured\n")
            return

        output = generate_latest(self.registry)
        self.send_response(200)
        self.send_header("Content-Type", CONTENT_TYPE_LATEST)
        self.end_headers()
        self.wfile.write(output)

    def _serve_health(self) -> None:
        """Serve a simple health check response."""
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"ok\n")

    def log_message(self, format: str, *args: Any) -> None:
        """Route HTTP log messages through the module logger."""
        logger.debug(format, *args)


# ---------------------------------------------------------------------------
# Exporter server
# ---------------------------------------------------------------------------

class PrometheusExporter:
    """Lightweight HTTP server that exposes pipeline metrics for scraping.

    Serves Prometheus exposition format at /metrics and a health check
    at /health. Can be started from either a live StageMetricsCollector
    (Tier 1 registry) or a stage_telemetry.jsonl file.

    Usage with a live collector::

        exporter = PrometheusExporter.from_collector(collector, port=9090)
        exporter.start()
        # ... pipeline runs ...
        exporter.stop()

    Usage with a JSONL file::

        exporter = PrometheusExporter.from_telemetry(
            Path("stage_telemetry.jsonl"), port=9090,
        )
        exporter.start()
        # ... scrape /metrics ...
        exporter.stop()
    """

    def __init__(
        self,
        registry: Any,
        host: str = _DEFAULT_HOST,
        port: int = _DEFAULT_PORT,
    ) -> None:
        if not HAS_PROMETHEUS:
            logger.warning(
                "prometheus-client not installed; "
                "PrometheusExporter will not serve metrics"
            )
        self._registry = registry
        self._host = host
        self._port = port
        self._server: HTTPServer | None = None
        self._thread: threading.Thread | None = None
        self._started = False

    @classmethod
    def from_collector(
        cls,
        collector: Any,
        host: str = _DEFAULT_HOST,
        port: int = _DEFAULT_PORT,
    ) -> PrometheusExporter:
        """Create an exporter from a live StageMetricsCollector.

        Args:
            collector: A StageMetricsCollector instance.
            host: Bind address for the HTTP server.
            port: Bind port for the HTTP server.

        Returns:
            A PrometheusExporter instance.
        """
        registry = create_registry_from_collector(collector)
        return cls(registry=registry, host=host, port=port)

    @classmethod
    def from_telemetry(
        cls,
        telemetry_path: Path,
        host: str = _DEFAULT_HOST,
        port: int = _DEFAULT_PORT,
    ) -> PrometheusExporter:
        """Create an exporter by replaying a stage_telemetry.jsonl file.

        Args:
            telemetry_path: Path to the JSONL telemetry file.
            host: Bind address for the HTTP server.
            port: Bind port for the HTTP server.

        Returns:
            A PrometheusExporter instance.
        """
        registry = create_registry_from_telemetry(telemetry_path)
        return cls(registry=registry, host=host, port=port)

    def start(self) -> None:
        """Start the HTTP server in a background daemon thread.

        The server binds to (host, port) and serves until stop() is
        called. If prometheus-client is not installed, this method
        logs a warning and returns without starting.

        Raises:
            RuntimeError: If the exporter is already started.
            OSError: If the port is already in use.
        """
        if self._started:
            raise RuntimeError(
                "PrometheusExporter is already started; "
                "call stop() before calling start() again"
            )

        if not HAS_PROMETHEUS or self._registry is None:
            logger.warning(
                "Cannot start PrometheusExporter: "
                "prometheus-client not available or no registry"
            )
            return

        handler_class = type(
            "_BoundMetricsHandler",
            (_MetricsHandler,),
            {"registry": self._registry},
        )

        self._server = HTTPServer(
            (self._host, self._port), handler_class,
        )
        self._thread = threading.Thread(
            target=self._server.serve_forever,
            name="prometheus-exporter",
            daemon=True,
        )
        self._thread.start()
        self._started = True

        logger.info(
            "PrometheusExporter started at http://%s:%d/metrics",
            self._host, self._port,
        )

    def stop(self) -> None:
        """Stop the HTTP server and wait for the thread to exit.

        Safe to call multiple times. If the server was never started,
        this method is a no-op.
        """
        if not self._started:
            return

        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
            self._server = None

        if self._thread is not None:
            self._thread.join(timeout=5.0)
            self._thread = None

        self._started = False
        logger.info("PrometheusExporter stopped")

    @property
    def is_running(self) -> bool:
        """Return True if the exporter server is currently running."""
        return self._started

    @property
    def registry(self) -> Any:
        """Return the underlying CollectorRegistry, or None."""
        return self._registry

    @property
    def url(self) -> str:
        """Return the metrics endpoint URL."""
        return f"http://{self._host}:{self._port}/metrics"

    def __enter__(self) -> PrometheusExporter:
        self.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        self.stop()


# ---------------------------------------------------------------------------
# Standalone metrics server
# ---------------------------------------------------------------------------


def serve_metrics(
    registry: Any = None,
    port: int = _DEFAULT_PORT,
    addr: str = _DEFAULT_HOST,
) -> bool:
    """Start Prometheus HTTP server to expose /metrics endpoint.

    Starts a background HTTP server using prometheus_client's built-in
    start_http_server. The server runs in a daemon thread and serves
    metrics at http://{addr}:{port}/metrics.

    Args:
        registry: Optional CollectorRegistry. If None, uses the
            prometheus_client default registry.
        port: TCP port to bind. Default 9090.
        addr: Bind address. Default "0.0.0.0".

    Returns:
        True if the server started successfully, False if
        prometheus_client is unavailable or startup failed.
    """
    if not HAS_PROMETHEUS:
        logger.warning(
            "prometheus_client not available; metrics server not started"
        )
        return False
    try:
        from prometheus_client import start_http_server
        start_http_server(port, addr=addr, registry=registry)
        logger.info(
            "Prometheus metrics server started on %s:%d", addr, port
        )
        return True
    except Exception:
        logger.exception("Failed to start Prometheus metrics server")
        return False


# ---------------------------------------------------------------------------
# Convenience: generate metrics text without starting a server
# ---------------------------------------------------------------------------

def generate_metrics_text(
    telemetry_path: Path,
) -> str:
    """Generate Prometheus exposition format text from a JSONL file.

    Useful for writing metrics to a file or embedding in a response
    without starting an HTTP server.

    Args:
        telemetry_path: Path to the stage_telemetry.jsonl file.

    Returns:
        Prometheus exposition format as a UTF-8 string.
        Returns an empty string if prometheus-client is not installed.
    """
    if not HAS_PROMETHEUS:
        logger.warning(
            "prometheus-client not installed; "
            "generate_metrics_text returning empty string"
        )
        return ""

    registry = create_registry_from_telemetry(telemetry_path)
    if registry is None:
        return ""

    return generate_latest(registry).decode("utf-8")
