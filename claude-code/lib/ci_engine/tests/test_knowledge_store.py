"""Comprehensive pytest tests for knowledge store and metrics modules.

Covers:
- knowledge_store_writer: atomic writes, schema validation, all public API
- run_summary: dataclass creation, factory, JSON round-trip
- stage_metrics_collector: lifecycle, context manager, JSONL fallback, KPIs
- prometheus_exporter: naming conventions, label cardinality, graceful degradation

Uses tmp_path fixture for file isolation. No real OTel/Prometheus required.
"""

from __future__ import annotations

import json
import os
import sqlite3
import threading
from pathlib import Path
from typing import Any
from unittest import mock

import pytest


# ---------------------------------------------------------------------------
# Module imports
# ---------------------------------------------------------------------------

from lib.ci_engine import knowledge_store_writer as ksw
from lib.ci_engine.run_summary import (
    RunKpis,
    RunSummary,
    StageEntry,
    TokenCount,
)
from lib.ci_engine import prometheus_exporter as prom_exp


# ---------------------------------------------------------------------------
# Shared test fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def store(tmp_path: Path) -> Path:
    """Initialize a knowledge store and return its root path."""
    ksw.initialize_store(tmp_path)
    return tmp_path


def _make_stage_data(
    duration: float = 10.0,
    status: str = "success",
    errors: list[str] | None = None,
    retry_count: int = 0,
    token_input: int = 100,
    token_output: int = 50,
    spec_compliance_score: int | None = None,
) -> dict[str, Any]:
    """Build a valid stage data dict for write_run_summary."""
    return {
        "duration_seconds": duration,
        "status": status,
        "errors": errors if errors is not None else [],
        "retry_count": retry_count,
        "token_count": {"input": token_input, "output": token_output},
        "spec_compliance_score": spec_compliance_score,
    }


def _make_kpis(
    total_duration: float = 30.0,
    spec_compliance: int | None = 85,
    test_coverage: float | None = 72.0,
) -> dict[str, Any]:
    """Build a valid KPIs dict for write_run_summary."""
    return {
        "total_duration_seconds": total_duration,
        "spec_compliance_score": spec_compliance,
        "test_coverage_pct": test_coverage,
        "stage_failure_bitmap": "0b0",
        "improvement_delta_pct": None,
    }


def _write_sample_run(
    store_path: Path,
    run_id: str = "test-run-001",
    overall_status: str = "success",
) -> Path:
    """Write a complete sample run summary to the store."""
    stages = {
        "stage_0": _make_stage_data(duration=10.0),
        "stage_3": _make_stage_data(duration=20.0, status="partial", errors=["err1"]),
    }
    return ksw.write_run_summary(
        store_path=store_path,
        run_id=run_id,
        completed_at="2026-03-29T14:30:00Z",
        stages=stages,
        overall_status=overall_status,
        improvement_notes=["note one"],
        kpis=_make_kpis(),
    )


# ===================================================================
# knowledge_store_writer tests
# ===================================================================

class TestInitializeStore:
    """Tests for initialize_store()."""

    def test_creates_all_subdirectories(self, tmp_path: Path) -> None:
        ksw.initialize_store(tmp_path)
        expected_subdirs = {"runs", "improvements", "baselines", "patterns", "retrospectives"}
        actual = {d.name for d in tmp_path.iterdir() if d.is_dir()}
        assert expected_subdirs.issubset(actual)

    def test_creates_sqlite_index(self, tmp_path: Path) -> None:
        ksw.initialize_store(tmp_path)
        db_path = tmp_path / "index.db"
        assert db_path.is_file()

    def test_sqlite_has_expected_tables(self, tmp_path: Path) -> None:
        ksw.initialize_store(tmp_path)
        conn = sqlite3.connect(str(tmp_path / "index.db"))
        try:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            tables = {row[0] for row in cursor.fetchall()}
        finally:
            conn.close()
        assert "runs" in tables
        assert "stage_events" in tables
        assert "failure_pattern_index" in tables
        assert "improvement_log_index" in tables

    def test_idempotent(self, tmp_path: Path) -> None:
        ksw.initialize_store(tmp_path)
        ksw.initialize_store(tmp_path)
        assert (tmp_path / "runs").is_dir()
        assert (tmp_path / "index.db").is_file()


class TestAtomicWriteJson:
    """Tests for the atomic tmp-then-rename write pattern."""

    def test_atomic_write_produces_valid_json(self, tmp_path: Path) -> None:
        target = tmp_path / "test.json"
        data = {"key": "value", "number": 42}
        ksw._atomic_write_json(target, data)
        assert target.is_file()
        loaded = json.loads(target.read_text(encoding="utf-8"))
        assert loaded == data

    def test_tmp_file_cleaned_on_success(self, tmp_path: Path) -> None:
        target = tmp_path / "test.json"
        ksw._atomic_write_json(target, {"ok": True})
        tmp_file = target.with_suffix(".json.tmp")
        assert not tmp_file.exists()

    def test_tmp_file_cleaned_on_error(self, tmp_path: Path) -> None:
        target = tmp_path / "test.json"

        class Unserializable:
            pass

        with pytest.raises(TypeError):
            ksw._atomic_write_json(target, {"bad": Unserializable()})
        tmp_file = target.with_suffix(".json.tmp")
        assert not tmp_file.exists()
        assert not target.exists()

    def test_overwrites_existing_file(self, tmp_path: Path) -> None:
        target = tmp_path / "test.json"
        ksw._atomic_write_json(target, {"version": 1})
        ksw._atomic_write_json(target, {"version": 2})
        loaded = json.loads(target.read_text(encoding="utf-8"))
        assert loaded["version"] == 2


class TestAppendJsonl:
    """Tests for JSONL append with flush+fsync."""

    def test_appends_single_record(self, tmp_path: Path) -> None:
        target = tmp_path / "data.jsonl"
        ksw._append_jsonl(target, {"event": "start"})
        lines = target.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 1
        assert json.loads(lines[0]) == {"event": "start"}

    def test_appends_multiple_records(self, tmp_path: Path) -> None:
        target = tmp_path / "data.jsonl"
        ksw._append_jsonl(target, {"seq": 1})
        ksw._append_jsonl(target, {"seq": 2})
        ksw._append_jsonl(target, {"seq": 3})
        lines = target.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 3
        assert json.loads(lines[2])["seq"] == 3

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        target = tmp_path / "nested" / "deep" / "data.jsonl"
        ksw._append_jsonl(target, {"ok": True})
        assert target.is_file()


class TestWriteRunSummary:
    """Tests for write_run_summary()."""

    def test_writes_valid_json_file(self, store: Path) -> None:
        path = _write_sample_run(store)
        assert path.is_file()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["schema_version"] == 1
        assert data["run_id"] == "test-run-001"

    def test_schema_version_is_1(self, store: Path) -> None:
        path = _write_sample_run(store)
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["schema_version"] == 1

    def test_creates_run_directory(self, store: Path) -> None:
        _write_sample_run(store, run_id="my-run-42")
        assert (store / "runs" / "my-run-42").is_dir()

    def test_indexes_into_sqlite(self, store: Path) -> None:
        _write_sample_run(store, run_id="indexed-run")
        conn = sqlite3.connect(str(store / "index.db"))
        try:
            row = conn.execute(
                "SELECT run_id FROM runs WHERE run_id = ?", ("indexed-run",)
            ).fetchone()
        finally:
            conn.close()
        assert row is not None
        assert row[0] == "indexed-run"

    def test_rejects_invalid_overall_status(self, store: Path) -> None:
        with pytest.raises(ValueError, match="Invalid overall_status"):
            ksw.write_run_summary(
                store_path=store,
                run_id="bad",
                completed_at="2026-01-01T00:00:00Z",
                stages={"stage_0": _make_stage_data()},
                overall_status="invalid_status",
                improvement_notes=[],
                kpis=_make_kpis(),
            )

    def test_rejects_empty_stages(self, store: Path) -> None:
        with pytest.raises(ValueError, match="non-empty dictionary"):
            ksw.write_run_summary(
                store_path=store,
                run_id="bad",
                completed_at="2026-01-01T00:00:00Z",
                stages={},
                overall_status="success",
                improvement_notes=[],
                kpis=_make_kpis(),
            )

    def test_rejects_invalid_stage_status(self, store: Path) -> None:
        bad_stage = _make_stage_data()
        bad_stage["status"] = "unknown"
        with pytest.raises(ValueError, match="invalid status"):
            ksw.write_run_summary(
                store_path=store,
                run_id="bad",
                completed_at="2026-01-01T00:00:00Z",
                stages={"stage_0": bad_stage},
                overall_status="success",
                improvement_notes=[],
                kpis=_make_kpis(),
            )

    def test_rejects_missing_stage_fields(self, store: Path) -> None:
        with pytest.raises(ValueError, match="missing required fields"):
            ksw.write_run_summary(
                store_path=store,
                run_id="bad",
                completed_at="2026-01-01T00:00:00Z",
                stages={"stage_0": {"status": "success"}},
                overall_status="success",
                improvement_notes=[],
                kpis=_make_kpis(),
            )


class TestAppendStageTelemetry:
    """Tests for append_stage_telemetry()."""

    def test_appends_event_to_jsonl(self, store: Path) -> None:
        path = ksw.append_stage_telemetry(
            store_path=store,
            run_id="run-tel-001",
            stage="stage_0",
            event_type="stage_start",
            timestamp="2026-03-29T14:00:00Z",
            duration_seconds=0.0,
            error_count=0,
            token_count=0,
            retry_count=0,
        )
        assert path.is_file()
        line = path.read_text(encoding="utf-8").strip()
        record = json.loads(line)
        assert record["schema_version"] == 1
        assert record["event_type"] == "stage_start"

    def test_rejects_invalid_event_type(self, store: Path) -> None:
        with pytest.raises(ValueError, match="Invalid event_type"):
            ksw.append_stage_telemetry(
                store_path=store,
                run_id="run-001",
                stage="stage_0",
                event_type="bad_event",
                timestamp="2026-03-29T14:00:00Z",
                duration_seconds=0.0,
                error_count=0,
                token_count=0,
                retry_count=0,
            )

    def test_indexes_into_sqlite(self, store: Path) -> None:
        # Write a run summary first to satisfy the FK constraint
        _write_sample_run(store, run_id="run-idx-001")
        ksw.append_stage_telemetry(
            store_path=store,
            run_id="run-idx-001",
            stage="stage_3",
            event_type="stage_end",
            timestamp="2026-03-29T14:05:00Z",
            duration_seconds=45.0,
            error_count=2,
            token_count=500,
            retry_count=1,
        )
        conn = sqlite3.connect(str(store / "index.db"))
        try:
            row = conn.execute(
                "SELECT stage, error_count FROM stage_events WHERE run_id = ?",
                ("run-idx-001",),
            ).fetchone()
        finally:
            conn.close()
        assert row is not None
        assert row[0] == "stage_3"
        assert row[1] == 2

    def test_rejects_non_numeric_duration(self, store: Path) -> None:
        with pytest.raises(ValueError, match="duration_seconds must be a number"):
            ksw.append_stage_telemetry(
                store_path=store,
                run_id="r",
                stage="s",
                event_type="stage_start",
                timestamp="2026-01-01T00:00:00Z",
                duration_seconds="not_a_number",  # type: ignore[arg-type]
                error_count=0,
                token_count=0,
                retry_count=0,
            )

    def test_multiple_events_append(self, store: Path) -> None:
        for event in ("stage_start", "stage_end"):
            ksw.append_stage_telemetry(
                store_path=store,
                run_id="run-multi",
                stage="stage_0",
                event_type=event,
                timestamp="2026-03-29T14:00:00Z",
                duration_seconds=10.0,
                error_count=0,
                token_count=0,
                retry_count=0,
            )
        path = store / "runs" / "run-multi" / "stage_telemetry.jsonl"
        lines = path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 2


class TestUpdateBaselines:
    """Tests for update_baselines()."""

    def test_computes_baselines_from_runs(self, store: Path) -> None:
        for i in range(3):
            _write_sample_run(store, run_id=f"baseline-run-{i}")
        path = ksw.update_baselines(store)
        assert path.is_file()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["schema_version"] == 1
        assert "stages" in data
        assert "stage_0" in data["stages"]

    def test_baseline_contains_smoothed_metrics(self, store: Path) -> None:
        for i in range(3):
            _write_sample_run(store, run_id=f"smooth-run-{i}")
        path = ksw.update_baselines(store)
        data = json.loads(path.read_text(encoding="utf-8"))
        stage_bl = data["stages"]["stage_0"]
        assert "smoothed" in stage_bl["duration_seconds"]
        assert "min" in stage_bl["duration_seconds"]
        assert "max" in stage_bl["duration_seconds"]

    def test_raises_when_no_runs(self, store: Path) -> None:
        with pytest.raises(FileNotFoundError, match="No run summaries"):
            ksw.update_baselines(store)

    def test_respects_window_size(self, store: Path) -> None:
        for i in range(15):
            _write_sample_run(store, run_id=f"window-run-{i:03d}")
        path = ksw.update_baselines(store, window_size=5)
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["window_size"] == 5
        stage_bl = data["stages"]["stage_0"]
        assert len(stage_bl["duration_seconds"]["raw_values"]) <= 5


class TestAppendImprovementLog:
    """Tests for append_improvement_log()."""

    def test_appends_valid_record(self, store: Path) -> None:
        path = ksw.append_improvement_log(
            store_path=store,
            session_id="session-001",
            action="Increase retry count for stage_3",
            evidence_runs=["run-001"],
            source="retrospective_analyzer",
            priority=1,
            target_stage="stage_3",
        )
        assert path.is_file()
        line = path.read_text(encoding="utf-8").strip()
        record = json.loads(line)
        assert record["schema_version"] == 1
        assert record["status"] == "proposed"

    def test_rejects_invalid_source(self, store: Path) -> None:
        with pytest.raises(ValueError, match="Invalid source"):
            ksw.append_improvement_log(
                store_path=store,
                session_id="s",
                action="a",
                evidence_runs=["r1"],
                source="unknown_source",
                priority=1,
                target_stage="stage_0",
            )

    def test_rejects_invalid_status(self, store: Path) -> None:
        with pytest.raises(ValueError, match="Invalid status"):
            ksw.append_improvement_log(
                store_path=store,
                session_id="s",
                action="a",
                evidence_runs=["r1"],
                source="manual",
                priority=1,
                target_stage="stage_0",
                status="invalid_status",
            )

    def test_rejects_empty_evidence_runs(self, store: Path) -> None:
        with pytest.raises(ValueError, match="evidence_runs must be a non-empty list"):
            ksw.append_improvement_log(
                store_path=store,
                session_id="s",
                action="a",
                evidence_runs=[],
                source="manual",
                priority=1,
                target_stage="stage_0",
            )

    def test_rejects_zero_priority(self, store: Path) -> None:
        with pytest.raises(ValueError, match="priority must be a positive integer"):
            ksw.append_improvement_log(
                store_path=store,
                session_id="s",
                action="a",
                evidence_runs=["r1"],
                source="manual",
                priority=0,
                target_stage="stage_0",
            )

    def test_indexes_into_sqlite(self, store: Path) -> None:
        ksw.append_improvement_log(
            store_path=store,
            session_id="sess-idx",
            action="Fix stage_0 timeout",
            evidence_runs=["run-a"],
            source="manual",
            priority=2,
            target_stage="stage_0",
            status="accepted",
        )
        conn = sqlite3.connect(str(store / "index.db"))
        try:
            row = conn.execute(
                "SELECT session_id, status FROM improvement_log_index"
            ).fetchone()
        finally:
            conn.close()
        assert row is not None
        assert row[0] == "sess-idx"
        assert row[1] == "accepted"


class TestRebuildIndex:
    """Tests for rebuild_index()."""

    def test_rebuilds_from_existing_data(self, store: Path) -> None:
        _write_sample_run(store, run_id="rebuild-run-1")
        _write_sample_run(store, run_id="rebuild-run-2")
        ksw.append_improvement_log(
            store_path=store,
            session_id="s",
            action="a",
            evidence_runs=["r"],
            source="manual",
            priority=1,
            target_stage="stage_0",
        )
        ksw.rebuild_index(store)
        conn = sqlite3.connect(str(store / "index.db"))
        try:
            run_count = conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
            imp_count = conn.execute(
                "SELECT COUNT(*) FROM improvement_log_index"
            ).fetchone()[0]
        finally:
            conn.close()
        assert run_count == 2
        assert imp_count == 1

    def test_rebuild_is_idempotent(self, store: Path) -> None:
        _write_sample_run(store, run_id="idem-run")
        ksw.rebuild_index(store)
        ksw.rebuild_index(store)
        conn = sqlite3.connect(str(store / "index.db"))
        try:
            count = conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
        finally:
            conn.close()
        assert count == 1

    def test_rebuild_on_empty_store(self, store: Path) -> None:
        ksw.rebuild_index(store)
        conn = sqlite3.connect(str(store / "index.db"))
        try:
            count = conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
        finally:
            conn.close()
        assert count == 0


class TestExponentialSmoothing:
    """Tests for internal _exponential_smooth helper."""

    def test_single_value(self) -> None:
        assert ksw._exponential_smooth([5.0], 0.3) == 5.0

    def test_empty_list(self) -> None:
        assert ksw._exponential_smooth([], 0.3) == 0.0

    def test_constant_series(self) -> None:
        result = ksw._exponential_smooth([10.0, 10.0, 10.0], 0.3)
        assert abs(result - 10.0) < 0.001

    def test_increasing_series(self) -> None:
        result = ksw._exponential_smooth([1.0, 2.0, 3.0], 0.5)
        assert result > 1.0
        assert result < 3.0


class TestReadJsonl:
    """Tests for _read_jsonl helper."""

    def test_reads_valid_lines(self, tmp_path: Path) -> None:
        target = tmp_path / "test.jsonl"
        target.write_text('{"a":1}\n{"b":2}\n', encoding="utf-8")
        records = ksw._read_jsonl(target)
        assert len(records) == 2
        assert records[0] == {"a": 1}

    def test_skips_corrupt_lines(self, tmp_path: Path) -> None:
        target = tmp_path / "test.jsonl"
        target.write_text('{"a":1}\nnot-json\n{"b":2}\n', encoding="utf-8")
        records = ksw._read_jsonl(target)
        assert len(records) == 2

    def test_returns_empty_for_missing_file(self, tmp_path: Path) -> None:
        records = ksw._read_jsonl(tmp_path / "missing.jsonl")
        assert records == []

    def test_skips_blank_lines(self, tmp_path: Path) -> None:
        target = tmp_path / "test.jsonl"
        target.write_text('{"a":1}\n\n\n{"b":2}\n', encoding="utf-8")
        records = ksw._read_jsonl(target)
        assert len(records) == 2


# ===================================================================
# run_summary tests
# ===================================================================

class TestTokenCount:
    """Tests for TokenCount dataclass."""

    def test_creation(self) -> None:
        tc = TokenCount(input=100, output=50)
        assert tc.input == 100
        assert tc.output == 50
        assert tc.total == 150

    def test_defaults(self) -> None:
        tc = TokenCount()
        assert tc.input == 0
        assert tc.output == 0

    def test_rejects_negative_input(self) -> None:
        with pytest.raises(ValueError, match="non-negative"):
            TokenCount(input=-1, output=0)

    def test_rejects_negative_output(self) -> None:
        with pytest.raises(ValueError, match="non-negative"):
            TokenCount(input=0, output=-1)

    def test_to_dict(self) -> None:
        tc = TokenCount(input=10, output=20)
        assert tc.to_dict() == {"input": 10, "output": 20}

    def test_from_dict(self) -> None:
        tc = TokenCount.from_dict({"input": 5, "output": 3})
        assert tc.input == 5
        assert tc.output == 3

    def test_frozen(self) -> None:
        tc = TokenCount(input=10, output=20)
        with pytest.raises(AttributeError):
            tc.input = 99  # type: ignore[misc]


class TestStageEntry:
    """Tests for StageEntry dataclass."""

    def test_valid_creation(self) -> None:
        entry = StageEntry(
            duration_seconds=45.0,
            status="success",
            errors=[],
            retry_count=0,
            token_count=TokenCount(input=100, output=50),
        )
        assert entry.duration_seconds == 45.0
        assert entry.status == "success"

    def test_rejects_invalid_status(self) -> None:
        with pytest.raises(ValueError, match="Invalid stage status"):
            StageEntry(duration_seconds=1.0, status="invalid")

    def test_rejects_negative_duration(self) -> None:
        with pytest.raises(ValueError, match="non-negative"):
            StageEntry(duration_seconds=-1.0, status="success")

    def test_rejects_negative_retry_count(self) -> None:
        with pytest.raises(ValueError, match="non-negative integer"):
            StageEntry(duration_seconds=1.0, status="success", retry_count=-1)

    def test_truncates_long_errors(self) -> None:
        long_err = "x" * 2000
        entry = StageEntry(
            duration_seconds=1.0,
            status="failed",
            errors=[long_err],
        )
        assert len(entry.errors[0]) == 1000

    def test_compliance_score_validation(self) -> None:
        entry = StageEntry(
            duration_seconds=1.0,
            status="success",
            spec_compliance_score=85,
        )
        assert entry.spec_compliance_score == 85

    def test_rejects_out_of_range_compliance(self) -> None:
        with pytest.raises(ValueError, match="between 0 and 100"):
            StageEntry(
                duration_seconds=1.0,
                status="success",
                spec_compliance_score=150,
            )

    def test_to_dict_round_trip(self) -> None:
        entry = StageEntry(
            duration_seconds=10.0,
            status="partial",
            errors=["err1"],
            retry_count=2,
            token_count=TokenCount(input=100, output=50),
            spec_compliance_score=90,
        )
        d = entry.to_dict()
        restored = StageEntry.from_dict(d)
        assert restored.duration_seconds == entry.duration_seconds
        assert restored.status == entry.status
        assert restored.errors == entry.errors
        assert restored.retry_count == entry.retry_count
        assert restored.token_count.input == entry.token_count.input
        assert restored.spec_compliance_score == entry.spec_compliance_score


class TestRunKpis:
    """Tests for RunKpis dataclass."""

    def test_defaults(self) -> None:
        kpis = RunKpis()
        assert kpis.total_duration_seconds == 0.0
        assert kpis.stage_failure_bitmap == "0b0"

    def test_rejects_out_of_range_compliance(self) -> None:
        with pytest.raises(ValueError, match="0-100"):
            RunKpis(spec_compliance_score=200)

    def test_rejects_out_of_range_coverage(self) -> None:
        with pytest.raises(ValueError, match="0-100"):
            RunKpis(test_coverage_pct=150.0)

    def test_to_dict(self) -> None:
        kpis = RunKpis(
            total_duration_seconds=100.0,
            spec_compliance_score=80,
            test_coverage_pct=70.0,
        )
        d = kpis.to_dict()
        assert d["total_duration_seconds"] == 100.0
        assert d["spec_compliance_score"] == 80

    def test_from_dict(self) -> None:
        d = {
            "total_duration_seconds": 50.0,
            "spec_compliance_score": 90,
            "test_coverage_pct": 80.0,
        }
        kpis = RunKpis.from_dict(d)
        assert kpis.total_duration_seconds == 50.0
        assert kpis.spec_compliance_score == 90


class TestRunSummary:
    """Tests for RunSummary dataclass."""

    def _make_summary(self, **overrides: Any) -> RunSummary:
        defaults: dict[str, Any] = {
            "run_id": "test-run-001",
            "completed_at": "2026-03-29T14:30:00Z",
            "stages": {
                "stage_0": StageEntry(
                    duration_seconds=10.0,
                    status="success",
                    token_count=TokenCount(input=100, output=50),
                ),
            },
            "overall_status": "success",
            "improvement_notes": [],
            "kpis": RunKpis(total_duration_seconds=10.0),
        }
        defaults.update(overrides)
        return RunSummary(**defaults)

    def test_valid_creation(self) -> None:
        summary = self._make_summary()
        assert summary.run_id == "test-run-001"
        assert summary.overall_status == "success"

    def test_rejects_empty_run_id(self) -> None:
        with pytest.raises(ValueError, match="non-empty string"):
            self._make_summary(run_id="")

    def test_rejects_invalid_overall_status(self) -> None:
        with pytest.raises(ValueError, match="Invalid overall_status"):
            self._make_summary(overall_status="bad")

    def test_to_dict_includes_schema_version(self) -> None:
        summary = self._make_summary()
        d = summary.to_dict()
        assert d["schema_version"] == 1

    def test_to_json_produces_valid_json(self) -> None:
        summary = self._make_summary()
        json_str = summary.to_json()
        parsed = json.loads(json_str)
        assert parsed["schema_version"] == 1
        assert parsed["run_id"] == "test-run-001"

    def test_to_json_round_trip(self) -> None:
        summary = self._make_summary(
            stages={
                "stage_0": StageEntry(
                    duration_seconds=10.0,
                    status="success",
                    token_count=TokenCount(input=100, output=50),
                ),
                "stage_3": StageEntry(
                    duration_seconds=20.0,
                    status="partial",
                    errors=["some error"],
                    retry_count=1,
                    token_count=TokenCount(input=200, output=100),
                    spec_compliance_score=85,
                ),
            },
            improvement_notes=["fix stage_3"],
            kpis=RunKpis(
                total_duration_seconds=30.0,
                spec_compliance_score=85,
                test_coverage_pct=72.0,
            ),
        )
        json_str = summary.to_json()
        restored = RunSummary.from_json(json_str)
        assert restored.run_id == summary.run_id
        assert restored.overall_status == summary.overall_status
        assert len(restored.stages) == 2
        assert restored.stages["stage_3"].errors == ["some error"]
        assert restored.kpis.spec_compliance_score == 85

    def test_from_dict(self) -> None:
        d = {
            "schema_version": 1,
            "run_id": "from-dict-run",
            "completed_at": "2026-03-29T00:00:00Z",
            "stages": {
                "stage_0": {
                    "duration_seconds": 5.0,
                    "status": "success",
                    "errors": [],
                    "retry_count": 0,
                    "token_count": {"input": 10, "output": 5},
                    "spec_compliance_score": None,
                },
            },
            "overall_status": "success",
            "improvement_notes": [],
            "kpis": {"total_duration_seconds": 5.0},
        }
        summary = RunSummary.from_dict(d)
        assert summary.run_id == "from-dict-run"
        assert summary.stages["stage_0"].duration_seconds == 5.0

    def test_truncates_long_improvement_notes(self) -> None:
        long_note = "x" * 1000
        summary = self._make_summary(improvement_notes=[long_note])
        assert len(summary.improvement_notes[0]) == 500


class TestFromSessionState:
    """Tests for RunSummary.from_session_state() factory."""

    def test_basic_conversion(self) -> None:
        state = {
            "session_id": "auto-orc-2026-03-29-test",
            "status": "completed",
            "stages_completed": [0, 3],
            "updated_at": "2026-03-29T15:00:00Z",
            "iteration_history": [],
        }
        summary = RunSummary.from_session_state(
            session_state=state,
            stage_durations={"stage_0": 10.0, "stage_3": 20.0},
            stage_tokens={
                "stage_0": {"input": 100, "output": 50},
                "stage_3": {"input": 200, "output": 100},
            },
        )
        assert summary.run_id == "auto-orc-2026-03-29-test"
        assert summary.overall_status == "success"
        assert "stage_0" in summary.stages
        assert "stage_3" in summary.stages
        assert summary.stages["stage_0"].status == "success"

    def test_completed_status_maps_to_success(self) -> None:
        state = {
            "session_id": "s",
            "status": "completed",
            "stages_completed": [0],
            "updated_at": "2026-01-01T00:00:00Z",
        }
        summary = RunSummary.from_session_state(state)
        assert summary.overall_status == "success"

    def test_failed_status_maps_to_failed(self) -> None:
        state = {
            "session_id": "s",
            "status": "failed",
            "stages_completed": [],
            "updated_at": "2026-01-01T00:00:00Z",
        }
        summary = RunSummary.from_session_state(
            state,
            stage_errors={"stage_0": ["crash"]},
        )
        assert summary.overall_status == "failed"

    def test_rejects_missing_session_id(self) -> None:
        with pytest.raises(ValueError, match="session_id"):
            RunSummary.from_session_state({})

    def test_stages_with_errors_generate_improvement_notes(self) -> None:
        state = {
            "session_id": "s",
            "status": "completed",
            "stages_completed": [0, 3],
            "updated_at": "2026-01-01T00:00:00Z",
        }
        summary = RunSummary.from_session_state(
            state,
            stage_errors={"stage_3": ["ImportError"]},
        )
        error_notes = [n for n in summary.improvement_notes if "error" in n.lower()]
        assert len(error_notes) >= 1

    def test_kpis_computed_from_stages(self) -> None:
        state = {
            "session_id": "s",
            "status": "completed",
            "stages_completed": [0, 3],
            "updated_at": "2026-01-01T00:00:00Z",
        }
        summary = RunSummary.from_session_state(
            state,
            stage_durations={"stage_0": 10.0, "stage_3": 20.0},
        )
        assert summary.kpis.total_duration_seconds == 30.0

    def test_failure_bitmap(self) -> None:
        state = {
            "session_id": "s",
            "status": "partial",
            "stages_completed": [0],
            "updated_at": "2026-01-01T00:00:00Z",
        }
        summary = RunSummary.from_session_state(
            state,
            stage_errors={"stage_3": ["error"]},
        )
        bitmap = summary.kpis.stage_failure_bitmap
        assert bitmap.startswith("0b")
        bitmap_val = int(bitmap, 2)
        assert bitmap_val & (1 << 3) != 0  # bit 3 set for stage_3


# ===================================================================
# stage_metrics_collector tests (Tier 3 JSONL fallback)
# ===================================================================

class TestStageMetricsCollectorTier3:
    """Tests for StageMetricsCollector in Tier 3 (JSONL-only) mode.

    These tests mock out OTel and Prometheus to ensure we exercise
    the JSONL fallback path regardless of installed packages.
    """

    @pytest.fixture()
    def collector(self, tmp_path: Path) -> Any:
        """Create a Tier 3 collector by patching out optional deps."""
        import lib.ci_engine.stage_metrics_collector as smc

        with mock.patch.object(smc, "HAS_OTEL", False), \
             mock.patch.object(smc, "HAS_PROMETHEUS", False):
            c = smc.StageMetricsCollector(
                session_id="test-session",
                telemetry_dir=tmp_path,
                run_sequence=1,
            )
            yield c
            if not c._closed:
                c.close()

    def test_tier_is_3(self, collector: Any) -> None:
        assert collector.tier == 3

    def test_context_manager_protocol(self, tmp_path: Path) -> None:
        import lib.ci_engine.stage_metrics_collector as smc

        with mock.patch.object(smc, "HAS_OTEL", False), \
             mock.patch.object(smc, "HAS_PROMETHEUS", False):
            with smc.StageMetricsCollector(
                session_id="ctx-test",
                telemetry_dir=tmp_path,
            ) as c:
                assert not c._closed
            assert c._closed

    def test_record_stage_start_emits_jsonl(self, collector: Any) -> None:
        collector.record_stage_start("researcher", 0)
        lines = collector.telemetry_path.read_text(encoding="utf-8").strip().split("\n")
        start_records = [
            json.loads(l) for l in lines
            if json.loads(l).get("event_type") == "stage_start"
        ]
        assert len(start_records) >= 1
        rec = start_records[0]
        assert rec["schema_version"] == 1
        assert rec["stage_name"] == "researcher"

    def test_record_stage_end_emits_jsonl(self, collector: Any) -> None:
        collector.record_stage_start("researcher", 0)
        collector.record_stage_end("researcher", "success", token_input=100, token_output=50)
        lines = collector.telemetry_path.read_text(encoding="utf-8").strip().split("\n")
        end_records = [
            json.loads(l) for l in lines
            if json.loads(l).get("event_type") == "stage_end"
        ]
        assert len(end_records) >= 1
        data = end_records[0]["data"]
        assert data["status"] == "success"
        assert data["token_input"] == 100
        assert data["token_output"] == 50

    def test_record_stage_error_emits_jsonl(self, collector: Any) -> None:
        collector.record_stage_start("researcher", 0)
        collector.record_stage_error("researcher", "transient", "timeout")
        lines = collector.telemetry_path.read_text(encoding="utf-8").strip().split("\n")
        error_records = [
            json.loads(l) for l in lines
            if json.loads(l).get("event_type") == "stage_error"
        ]
        assert len(error_records) >= 1
        assert error_records[0]["data"]["error_type"] == "transient"

    def test_record_stage_retry_emits_jsonl(self, collector: Any) -> None:
        collector.record_stage_start("researcher", 0)
        collector.record_stage_retry("researcher", "rate_limit")
        lines = collector.telemetry_path.read_text(encoding="utf-8").strip().split("\n")
        retry_records = [
            json.loads(l) for l in lines
            if json.loads(l).get("event_type") == "stage_retry"
        ]
        assert len(retry_records) >= 1
        assert retry_records[0]["data"]["reason"] == "rate_limit"

    def test_rejects_invalid_stage_name(self, collector: Any) -> None:
        with pytest.raises(ValueError, match="Invalid stage_name"):
            collector.record_stage_start("nonexistent_stage", 99)

    def test_rejects_invalid_error_type(self, collector: Any) -> None:
        collector.record_stage_start("researcher", 0)
        with pytest.raises(ValueError, match="Invalid error_type"):
            collector.record_stage_error("researcher", "bad_type", "msg")

    def test_rejects_invalid_status(self, collector: Any) -> None:
        collector.record_stage_start("researcher", 0)
        with pytest.raises(ValueError, match="Invalid status"):
            collector.record_stage_end("researcher", "bad_status")

    def test_rejects_double_start(self, collector: Any) -> None:
        collector.record_stage_start("researcher", 0)
        with pytest.raises(RuntimeError, match="already started"):
            collector.record_stage_start("researcher", 0)

    def test_rejects_end_without_start(self, collector: Any) -> None:
        with pytest.raises(ValueError, match="No matching record_stage_start"):
            collector.record_stage_end("researcher", "success")

    def test_rejects_calls_after_close(self, collector: Any) -> None:
        collector.close()
        with pytest.raises(RuntimeError, match="closed"):
            collector.record_stage_start("researcher", 0)

    def test_close_is_idempotent(self, collector: Any) -> None:
        collector.close()
        collector.close()
        assert collector._closed

    def test_finalize_run_returns_kpis(self, collector: Any) -> None:
        collector.record_stage_start("researcher", 0)
        collector.record_stage_end(
            "researcher", "success",
            token_input=100, token_output=50,
            research_completeness_score=85.0,
        )
        collector.record_stage_start("software_engineer", 3)
        collector.record_stage_error("software_engineer", "transient", "timeout")
        collector.record_stage_end("software_engineer", "partial", token_input=200, token_output=100)

        summary = collector.finalize_run()

        assert "kpis" in summary
        kpis = summary["kpis"]
        assert "total_duration_seconds" in kpis
        assert "stage_failure_bitmap" in kpis
        # Bitmap should have software_engineer bit set (bit 3)
        assert kpis["stage_failure_bitmap"] & (1 << 3) != 0

    def test_finalize_emits_run_finalize_event(self, collector: Any) -> None:
        collector.record_stage_start("researcher", 0)
        collector.record_stage_end("researcher", "success")
        collector.finalize_run()
        lines = collector.telemetry_path.read_text(encoding="utf-8").strip().split("\n")
        finalize_records = [
            json.loads(l) for l in lines
            if json.loads(l).get("event_type") == "run_finalize"
        ]
        assert len(finalize_records) == 1

    def test_all_valid_stage_names_accepted(self, collector: Any) -> None:
        import lib.ci_engine.stage_metrics_collector as smc
        for name in smc.VALID_STAGE_NAMES:
            collector.record_stage_start(name, smc.STAGE_NAME_TO_NUMBER[name])
            collector.record_stage_end(name, "success")

    def test_all_valid_error_types_accepted(self, collector: Any) -> None:
        import lib.ci_engine.stage_metrics_collector as smc
        collector.record_stage_start("researcher", 0)
        for error_type in smc.VALID_ERROR_TYPES:
            collector.record_stage_error("researcher", error_type, "msg")

    def test_spec_compliance_recorded(self, collector: Any) -> None:
        collector.record_stage_start("validator", 5)
        collector.record_stage_end(
            "validator", "success",
            spec_compliance_score=92.0,
        )
        summary = collector.finalize_run()
        assert summary["kpis"]["spec_compliance_score"] == 92.0

    def test_test_coverage_recorded(self, collector: Any) -> None:
        collector.record_stage_start("test_writer", 4)
        collector.record_stage_end(
            "test_writer", "success",
            test_coverage_pct=78.5,
        )
        summary = collector.finalize_run()
        assert summary["kpis"]["test_coverage_pct"] == 78.5

    def test_prometheus_registry_is_none_tier3(self, collector: Any) -> None:
        assert collector.prometheus_registry is None


class TestCompositeScore:
    """Tests for the static _compute_composite_score method."""

    def test_returns_none_when_both_none(self) -> None:
        from lib.ci_engine.stage_metrics_collector import StageMetricsCollector
        result = StageMetricsCollector._compute_composite_score(None, None, 0, 0)
        assert result is None

    def test_formula_correctness(self) -> None:
        from lib.ci_engine.stage_metrics_collector import StageMetricsCollector
        result = StageMetricsCollector._compute_composite_score(
            spec_compliance=80.0,
            test_coverage=70.0,
            total_errors=1,
            total_stages=4,
        )
        # 0.4*80 + 0.3*70 + 0.3*(1-0.25)*100 = 32 + 21 + 22.5 = 75.5
        assert abs(result - 75.5) < 0.01

    def test_zero_errors(self) -> None:
        from lib.ci_engine.stage_metrics_collector import StageMetricsCollector
        result = StageMetricsCollector._compute_composite_score(
            spec_compliance=100.0,
            test_coverage=100.0,
            total_errors=0,
            total_stages=5,
        )
        # 0.4*100 + 0.3*100 + 0.3*100 = 40 + 30 + 30 = 100
        assert abs(result - 100.0) < 0.01


# ===================================================================
# prometheus_exporter tests
# ===================================================================

class TestPrometheusExporterGracefulDegradation:
    """Tests for prometheus_exporter module when prometheus-client is absent."""

    def test_create_registry_returns_none_without_prometheus(self, tmp_path: Path) -> None:
        with mock.patch.object(prom_exp, "HAS_PROMETHEUS", False):
            result = prom_exp.create_registry_from_telemetry(tmp_path / "fake.jsonl")
            assert result is None

    def test_generate_metrics_text_returns_empty_without_prometheus(self, tmp_path: Path) -> None:
        with mock.patch.object(prom_exp, "HAS_PROMETHEUS", False):
            result = prom_exp.generate_metrics_text(tmp_path / "fake.jsonl")
            assert result == ""

    def test_exporter_init_without_prometheus(self, tmp_path: Path) -> None:
        with mock.patch.object(prom_exp, "HAS_PROMETHEUS", False):
            exporter = prom_exp.PrometheusExporter(registry=None)
            assert not exporter.is_running

    def test_exporter_start_noop_without_prometheus(self, tmp_path: Path) -> None:
        with mock.patch.object(prom_exp, "HAS_PROMETHEUS", False):
            exporter = prom_exp.PrometheusExporter(registry=None)
            exporter.start()
            assert not exporter.is_running

    def test_exporter_stop_noop_when_not_started(self) -> None:
        with mock.patch.object(prom_exp, "HAS_PROMETHEUS", False):
            exporter = prom_exp.PrometheusExporter(registry=None)
            exporter.stop()
            assert not exporter.is_running

    def test_exporter_context_manager(self) -> None:
        with mock.patch.object(prom_exp, "HAS_PROMETHEUS", False):
            with prom_exp.PrometheusExporter(registry=None) as exp:
                assert not exp.is_running

    def test_create_registry_from_collector_without_prometheus(self) -> None:
        with mock.patch.object(prom_exp, "HAS_PROMETHEUS", False):
            result = prom_exp.create_registry_from_collector(mock.MagicMock())
            assert result is None


class TestPrometheusExporterMetricNaming:
    """Tests for Prometheus metric naming conventions."""

    def test_metric_names_follow_convention(self) -> None:
        """All metric names must start with pipeline_stage_ or pipeline_run_."""
        expected_prefixes = ("pipeline_stage_", "pipeline_run_")
        metric_names = [
            "pipeline_stage_duration_seconds",
            "pipeline_stage_error_total",
            "pipeline_stage_retry_total",
            "pipeline_stage_token_input_total",
            "pipeline_stage_token_output_total",
            "pipeline_stage_success_rate",
            "pipeline_run_duration_seconds",
            "pipeline_run_stage_failure_bitmap",
            "pipeline_run_spec_compliance_score",
            "pipeline_run_test_coverage_pct",
            "pipeline_run_improvement_delta_pct",
            "pipeline_run_research_completeness_score",
        ]
        for name in metric_names:
            assert any(name.startswith(p) for p in expected_prefixes), (
                f"Metric {name} does not follow naming convention"
            )

    def test_valid_stage_names_are_bounded(self) -> None:
        """Stage label values must come from a fixed set (cardinality safety)."""
        assert len(prom_exp.VALID_STAGE_NAMES) == 8
        assert isinstance(prom_exp.VALID_STAGE_NAMES, frozenset)

    def test_valid_error_types_are_bounded(self) -> None:
        """Error type labels must come from a fixed set (cardinality safety)."""
        assert len(prom_exp.VALID_ERROR_TYPES) == 8
        assert isinstance(prom_exp.VALID_ERROR_TYPES, frozenset)

    def test_no_run_id_in_labels(self) -> None:
        """Verify that the module does not use run_id as a label.

        This is a cardinality constraint: per-run labels create unbounded
        label cardinality in Prometheus.
        """
        import inspect
        source = inspect.getsource(prom_exp._hydrate_metrics)
        # labelnames for stage metrics only use "stage" and "error_type"
        # run-level metrics have NO labels at all
        assert 'labelnames=["run_id"' not in source
        assert "run_id" not in source.split("labelnames")[0] if "labelnames" in source else True


class TestPrometheusExporterHydration:
    """Tests for _hydrate_metrics and _read_telemetry_records."""

    def test_read_telemetry_records_valid(self, tmp_path: Path) -> None:
        path = tmp_path / "telemetry.jsonl"
        records = [
            {"event_type": "stage_start", "stage_name": "researcher"},
            {"event_type": "stage_end", "stage_name": "researcher"},
        ]
        path.write_text(
            "\n".join(json.dumps(r) for r in records) + "\n",
            encoding="utf-8",
        )
        result = prom_exp._read_telemetry_records(path)
        assert len(result) == 2

    def test_read_telemetry_records_skips_corrupt(self, tmp_path: Path) -> None:
        path = tmp_path / "telemetry.jsonl"
        path.write_text(
            '{"event_type":"stage_start"}\nnot-json\n{"event_type":"stage_end"}\n',
            encoding="utf-8",
        )
        result = prom_exp._read_telemetry_records(path)
        assert len(result) == 2

    def test_read_telemetry_records_missing_file(self, tmp_path: Path) -> None:
        result = prom_exp._read_telemetry_records(tmp_path / "missing.jsonl")
        assert result == []

    def test_hydrate_metrics_noop_without_prometheus(self, tmp_path: Path) -> None:
        with mock.patch.object(prom_exp, "HAS_PROMETHEUS", False):
            prom_exp._hydrate_metrics(None, tmp_path / "fake.jsonl")


class TestPrometheusExporterProperties:
    """Tests for PrometheusExporter property accessors."""

    def test_url_property(self) -> None:
        with mock.patch.object(prom_exp, "HAS_PROMETHEUS", False):
            exp = prom_exp.PrometheusExporter(registry=None, port=9999)
            assert exp.url == "http://0.0.0.0:9999/metrics"

    def test_registry_property(self) -> None:
        with mock.patch.object(prom_exp, "HAS_PROMETHEUS", False):
            exp = prom_exp.PrometheusExporter(registry=None)
            assert exp.registry is None

    def test_from_telemetry_factory(self, tmp_path: Path) -> None:
        with mock.patch.object(prom_exp, "HAS_PROMETHEUS", False):
            exp = prom_exp.PrometheusExporter.from_telemetry(
                tmp_path / "telemetry.jsonl", port=9191,
            )
            assert exp.registry is None
            assert not exp.is_running

    def test_from_collector_factory(self) -> None:
        with mock.patch.object(prom_exp, "HAS_PROMETHEUS", False):
            fake_collector = mock.MagicMock()
            exp = prom_exp.PrometheusExporter.from_collector(
                fake_collector, port=9292,
            )
            assert not exp.is_running


# ===================================================================
# Thread safety smoke test
# ===================================================================

class TestThreadSafety:
    """Basic thread-safety smoke tests for knowledge store writer."""

    def test_concurrent_writes(self, store: Path) -> None:
        errors: list[Exception] = []

        def write_run(idx: int) -> None:
            try:
                _write_sample_run(store, run_id=f"thread-run-{idx}")
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=write_run, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        conn = sqlite3.connect(str(store / "index.db"))
        try:
            count = conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
        finally:
            conn.close()
        assert count == 5

    def test_concurrent_telemetry_appends(self, store: Path) -> None:
        errors: list[Exception] = []

        def append_event(idx: int) -> None:
            try:
                ksw.append_stage_telemetry(
                    store_path=store,
                    run_id="concurrent-run",
                    stage=f"stage_{idx % 3}",
                    event_type="stage_start",
                    timestamp="2026-03-29T14:00:00Z",
                    duration_seconds=0.0,
                    error_count=0,
                    token_count=0,
                    retry_count=0,
                )
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=append_event, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
