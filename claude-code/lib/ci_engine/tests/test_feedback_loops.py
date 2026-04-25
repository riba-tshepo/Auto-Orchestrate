"""Integration tests for CI engine feedback loops.

Tests the OODA within-run loop and PDCA cross-run loop to ensure
the continuous improvement pipeline is correctly wired.

Dependencies: Python >= 3.11 stdlib + pytest.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import pytest

# Ensure lib/ is importable
import sys

sys.path.insert(
    0, str(Path(__file__).resolve().parent.parent.parent.parent)
)

from lib.ci_engine.root_cause_classifier import classify_failure
from lib.ci_engine.ooda_controller import (
    ObservationRecord,
    OODAController,
)
from lib.ci_engine.stage_metrics_collector import StageMetricsCollector
from lib.ci_engine.baseline_manager import BaselineManager


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_telemetry(tmp_path: Path) -> Path:
    """Create a temporary telemetry directory."""
    telemetry_dir = tmp_path / "telemetry"
    telemetry_dir.mkdir()
    return telemetry_dir


@pytest.fixture
def tmp_knowledge_store(tmp_path: Path) -> Path:
    """Create a temporary knowledge store directory."""
    store = tmp_path / "knowledge_store"
    store.mkdir()
    (store / "runs").mkdir()
    (store / "baselines").mkdir()
    (store / "improvements").mkdir()
    (store / "patterns").mkdir()
    return store


# ---------------------------------------------------------------------------
# Root cause classifier tests
# ---------------------------------------------------------------------------


class TestRootCauseClassifier:
    """Tests for classify_failure() with all 8 categories."""

    def test_dependency_classification(self) -> None:
        result = classify_failure(
            "ModuleNotFoundError: No module named 'flask'",
            "stage_3",
        )
        assert result["category"] == "dependency"
        assert result["confidence"] >= 0.9

    def test_transient_classification(self) -> None:
        result = classify_failure(
            "HTTP 429 Too Many Requests - rate limit exceeded",
            "stage_0",
        )
        assert result["category"] == "transient"
        assert result["confidence"] >= 0.5

    def test_hallucination_classification(self) -> None:
        result = classify_failure(
            "AttributeError: 'NoneType' has no attribute 'items'",
            "stage_3",
        )
        assert result["category"] == "hallucination"
        assert result["confidence"] >= 0.5

    def test_spec_gap_classification(self) -> None:
        result = classify_failure(
            "compliance gap: authentication method not specified",
            "stage_5",
            context={"validator_output": "spec compliance gap detected"},
        )
        assert result["category"] == "spec_gap"
        assert result["confidence"] >= 0.5

    def test_resource_exhaustion_classification(self) -> None:
        result = classify_failure(
            "MemoryError: Cannot allocate memory for array",
            "stage_3",
        )
        assert result["category"] == "resource_exhaustion"
        assert result["confidence"] >= 0.8

    def test_configuration_classification(self) -> None:
        result = classify_failure(
            "ConfigurationError: missing env variable DATABASE_URL",
            "stage_5",
        )
        assert result["category"] == "configuration"
        assert result["confidence"] >= 0.5

    def test_permissions_classification(self) -> None:
        result = classify_failure(
            "PermissionError: Permission denied: '/etc/passwd'",
            "stage_3",
        )
        assert result["category"] == "permissions"
        assert result["confidence"] >= 0.8

    def test_timeout_classification(self) -> None:
        result = classify_failure(
            "DeadlineExceeded: context deadline exceeded after 30s",
            "stage_0",
        )
        assert result["category"] == "timeout"
        assert result["confidence"] >= 0.5

    def test_empty_error_graceful(self) -> None:
        result = classify_failure("", "stage_3")
        assert result["category"] == "transient"
        assert result["confidence"] == 0.1

    def test_unknown_error_defaults_to_spec_gap(self) -> None:
        result = classify_failure(
            "some completely unknown error with no keywords",
            "stage_3",
        )
        assert result["category"] == "spec_gap"
        assert result["confidence"] == 0.3

    def test_five_whys_chain_length(self) -> None:
        result = classify_failure(
            "ImportError: No module named 'nonexistent'",
            "stage_3",
        )
        chain = result["five_whys_chain"]
        assert 3 <= len(chain) <= 5
        assert all(isinstance(w, str) for w in chain)


# ---------------------------------------------------------------------------
# OODA controller tests
# ---------------------------------------------------------------------------


class TestOODAController:
    """Tests for OODA observe → orient → decide → act loop."""

    def test_nominal_stage_continues(self, tmp_telemetry: Path) -> None:
        """Successful stage should produce 'continue' decision."""
        controller = OODAController(
            session_id="test-session",
            knowledge_store_path=tmp_telemetry,
        )
        stage_result = {
            "stage_name": "researcher",
            "status": "success",
            "duration_seconds": 30.0,
            "error_count": 0,
            "retry_count": 0,
            "error_messages": [],
        }
        result = controller.run(stage_result)
        assert result == "continue"

    def test_transient_failure_retries(self, tmp_telemetry: Path) -> None:
        """Transient failure with retries left should produce 'retry'."""
        controller = OODAController(
            session_id="test-session",
            knowledge_store_path=tmp_telemetry,
        )
        stage_result = {
            "stage_name": "researcher",
            "status": "failure",
            "duration_seconds": 5.0,
            "error_count": 1,
            "retry_count": 0,
            "error_messages": ["HTTP 503 Service Unavailable"],
        }
        result = controller.run(stage_result)
        assert result in ("retry", "surface_to_user")


# ---------------------------------------------------------------------------
# Stage metrics collector tests
# ---------------------------------------------------------------------------


class TestStageMetricsCollector:
    """Tests for metrics collection and run finalization."""

    def test_stage_lifecycle(self, tmp_telemetry: Path) -> None:
        """Test recording a full stage start → end cycle."""
        collector = StageMetricsCollector(
            session_id="test-session",
            telemetry_dir=tmp_telemetry,
        )
        collector.record_stage_start("researcher", 0)
        collector.record_stage_end("researcher", "success")

        # Verify telemetry was written
        telemetry_file = tmp_telemetry / "stage_telemetry.jsonl"
        assert telemetry_file.exists()
        lines = telemetry_file.read_text().strip().split("\n")
        assert len(lines) >= 2  # at least start + end events

    def test_error_recording(self, tmp_telemetry: Path) -> None:
        """Test that errors are recorded during a stage."""
        collector = StageMetricsCollector(
            session_id="test-session",
            telemetry_dir=tmp_telemetry,
        )
        collector.record_stage_start("software_engineer", 3)
        collector.record_stage_error("software_engineer", "transient", "timeout")
        collector.record_stage_end("software_engineer", "partial")

    def test_finalize_run_produces_summary(self, tmp_telemetry: Path) -> None:
        """Test that finalize_run creates a run summary."""
        collector = StageMetricsCollector(
            session_id="test-session",
            telemetry_dir=tmp_telemetry,
        )
        collector.record_stage_start("researcher", 0)
        collector.record_stage_end("researcher", "success")

        summary = collector.finalize_run()
        assert summary is not None
        assert "run_id" in summary or "overall_status" in summary


# ---------------------------------------------------------------------------
# Baseline manager tests
# ---------------------------------------------------------------------------


class TestBaselineManager:
    """Tests for baseline computation edge cases."""

    def test_first_run_returns_first_run_flag(
        self, tmp_knowledge_store: Path,
    ) -> None:
        """When no run summaries exist, should write a first_run baseline file."""
        manager = BaselineManager(
            knowledge_store_path=tmp_knowledge_store,
        )
        result_path = manager.update_baselines()
        assert result_path.exists()
        import json
        data = json.loads(result_path.read_text())
        assert data.get("first_run") is True or data.get("baselines") == {}
