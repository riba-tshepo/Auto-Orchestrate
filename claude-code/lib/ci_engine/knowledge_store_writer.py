"""Knowledge store writer for the continuous improvement engine.

Provides atomic file writes, JSONL append operations, SQLite3 indexing,
and baseline computation for cross-run learning in Auto-Orchestrate.

All writes are atomic (tmp-then-rename for JSON, append+flush+fsync for JSONL).
Thread-safe via a module-level threading lock for file operations and SQLite
WAL mode for concurrent reads.

Dependencies: Python >= 3.11 stdlib only.
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_SCHEMA_VERSION = 1

_VALID_OVERALL_STATUSES = frozenset({"success", "partial", "failed", "aborted"})
_VALID_STAGE_STATUSES = frozenset({"success", "partial", "failed", "skipped"})
_VALID_EVENT_TYPES = frozenset({
    "stage_start", "stage_end", "stage_error", "stage_retry", "stage_skip",
})
_VALID_IMPROVEMENT_SOURCES = frozenset({
    "retrospective_analyzer", "improvement_recommender", "manual",
})
_VALID_IMPROVEMENT_STATUSES = frozenset({
    "proposed", "accepted", "applied", "rejected", "deferred",
})

_STORE_SUBDIRS = ("runs", "improvements", "baselines", "patterns", "retrospectives")

_write_lock = threading.Lock()

_SQLITE_SCHEMA = """\
CREATE TABLE IF NOT EXISTS runs (
    run_id          TEXT PRIMARY KEY,
    completed_at    TEXT NOT NULL,
    overall_status  TEXT NOT NULL,
    total_duration  REAL NOT NULL,
    spec_compliance INTEGER,
    test_coverage   REAL,
    created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS stage_events (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id          TEXT NOT NULL,
    stage           TEXT NOT NULL,
    event_type      TEXT NOT NULL,
    timestamp       TEXT NOT NULL,
    duration_seconds REAL NOT NULL,
    error_count     INTEGER NOT NULL,
    token_count     INTEGER NOT NULL,
    retry_count     INTEGER NOT NULL,
    FOREIGN KEY (run_id) REFERENCES runs(run_id)
);

CREATE TABLE IF NOT EXISTS failure_pattern_index (
    pattern_id      TEXT PRIMARY KEY,
    classification  TEXT NOT NULL,
    frequency       INTEGER NOT NULL,
    last_seen       TEXT NOT NULL,
    severity        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS improvement_log_index (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp       TEXT NOT NULL,
    session_id      TEXT NOT NULL,
    target_stage    TEXT NOT NULL,
    priority        INTEGER NOT NULL,
    status          TEXT NOT NULL,
    action_summary  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_runs_completed_at ON runs(completed_at);
CREATE INDEX IF NOT EXISTS idx_stage_events_run_id ON stage_events(run_id);
CREATE INDEX IF NOT EXISTS idx_stage_events_stage ON stage_events(stage);
CREATE INDEX IF NOT EXISTS idx_stage_events_timestamp ON stage_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_stage_events_stage_timestamp ON stage_events(stage, timestamp);
CREATE INDEX IF NOT EXISTS idx_improvement_log_timestamp ON improvement_log_index(timestamp);
CREATE INDEX IF NOT EXISTS idx_improvement_log_target ON improvement_log_index(target_stage);
CREATE INDEX IF NOT EXISTS idx_failure_pattern_class ON failure_pattern_index(classification);
"""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _utc_now_iso() -> str:
    """Return current UTC time as ISO 8601 string with Z suffix."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _db_path(store_path: Path) -> Path:
    """Return the path to the SQLite index database."""
    return store_path / "index.db"


def _get_connection(store_path: Path) -> sqlite3.Connection:
    """Open a SQLite connection with WAL mode for concurrency."""
    db = _db_path(store_path)
    conn = sqlite3.connect(str(db), timeout=10)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _ensure_schema(conn: sqlite3.Connection) -> None:
    """Create tables and indexes if they do not exist."""
    conn.executescript(_SQLITE_SCHEMA)


def _atomic_write_json(target_path: Path, data: dict) -> None:
    """Write JSON atomically via tmp-then-rename.

    The caller MUST ensure target_path.parent exists before calling.
    """
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


def _append_jsonl(target_path: Path, record: dict) -> None:
    """Append a single JSON record to a JSONL file with flush and fsync."""
    os.makedirs(target_path.parent, exist_ok=True)
    with open(target_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False))
        fh.write("\n")
        fh.flush()
        os.fsync(fh.fileno())


def _validate_stage_entry(name: str, data: dict) -> None:
    """Validate a single stage entry from a run summary."""
    required_keys = {
        "duration_seconds", "status", "errors", "retry_count",
        "token_count", "spec_compliance_score",
    }
    missing = required_keys - set(data.keys())
    if missing:
        raise ValueError(
            f"Stage '{name}' is missing required fields: {sorted(missing)}"
        )
    if data["status"] not in _VALID_STAGE_STATUSES:
        raise ValueError(
            f"Stage '{name}' has invalid status '{data['status']}'. "
            f"Must be one of {sorted(_VALID_STAGE_STATUSES)}"
        )
    if not isinstance(data["duration_seconds"], (int, float)):
        raise ValueError(
            f"Stage '{name}' duration_seconds must be a number"
        )
    if not isinstance(data["errors"], list):
        raise ValueError(f"Stage '{name}' errors must be a list")
    if not isinstance(data["retry_count"], int):
        raise ValueError(f"Stage '{name}' retry_count must be an integer")
    tc = data["token_count"]
    if not isinstance(tc, dict) or "input" not in tc or "output" not in tc:
        raise ValueError(
            f"Stage '{name}' token_count must have 'input' and 'output' keys"
        )


def _load_json_safe(path: Path) -> dict | None:
    """Load a JSON file, returning None if the file does not exist."""
    if not path.is_file():
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _read_jsonl(path: Path) -> list[dict]:
    """Read all valid records from a JSONL file, skipping bad lines."""
    records: list[dict] = []
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


def _collect_run_summaries(store_path: Path) -> list[dict]:
    """Load all run_summary.json files sorted by completed_at ascending."""
    runs_dir = store_path / "runs"
    if not runs_dir.is_dir():
        return []
    summaries: list[dict] = []
    for run_dir in runs_dir.iterdir():
        if not run_dir.is_dir():
            continue
        summary_path = run_dir / "run_summary.json"
        data = _load_json_safe(summary_path)
        if data is not None:
            summaries.append(data)
    summaries.sort(key=lambda s: s.get("completed_at", ""))
    return summaries


def _exponential_smooth(values: list[float], alpha: float) -> float:
    """Compute exponential smoothing over a list of values.

    For the first observation S(1) = X(1).
    For subsequent: S(t) = alpha * X(t) + (1 - alpha) * S(t-1).
    """
    if not values:
        return 0.0
    smoothed = values[0]
    for val in values[1:]:
        smoothed = alpha * val + (1.0 - alpha) * smoothed
    return round(smoothed, 4)


def _compute_metric_baseline(
    raw_values: list[float],
    alpha: float,
) -> dict[str, Any]:
    """Build a baseline metric object with smoothed, min, max, raw_values."""
    return {
        "smoothed": _exponential_smooth(raw_values, alpha),
        "min": min(raw_values) if raw_values else 0.0,
        "max": max(raw_values) if raw_values else 0.0,
        "raw_values": raw_values,
    }


def _index_run_summary(conn: sqlite3.Connection, data: dict) -> None:
    """Insert or update a run summary in the SQLite index.

    Attempts INSERT first. On duplicate run_id (IntegrityError), updates
    only the mutable fields (completed_at, overall_status, and KPIs)
    rather than replacing the entire row.
    """
    kpis = data.get("kpis", {})
    run_id = data["run_id"]
    completed_at = data["completed_at"]
    overall_status = data["overall_status"]
    total_duration = kpis.get("total_duration_seconds", 0.0)
    spec_compliance = kpis.get("spec_compliance_score")
    test_coverage = kpis.get("test_coverage_pct")

    try:
        conn.execute(
            "INSERT INTO runs "
            "(run_id, completed_at, overall_status, total_duration, "
            "spec_compliance, test_coverage) VALUES (?, ?, ?, ?, ?, ?)",
            (
                run_id,
                completed_at,
                overall_status,
                total_duration,
                spec_compliance,
                test_coverage,
            ),
        )
    except sqlite3.IntegrityError:
        logger.warning(
            "Duplicate run_id %s detected; updating existing record",
            run_id,
        )
        conn.execute(
            "UPDATE runs SET completed_at = ?, overall_status = ?, "
            "total_duration = ?, spec_compliance = ?, test_coverage = ? "
            "WHERE run_id = ?",
            (
                completed_at,
                overall_status,
                total_duration,
                spec_compliance,
                test_coverage,
                run_id,
            ),
        )


def _index_stage_event(conn: sqlite3.Connection, run_id: str, record: dict) -> None:
    """Insert a stage event into the SQLite index."""
    conn.execute(
        "INSERT INTO stage_events "
        "(run_id, stage, event_type, timestamp, duration_seconds, "
        "error_count, token_count, retry_count) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            run_id,
            record["stage"],
            record["event_type"],
            record["timestamp"],
            record["duration_seconds"],
            record["error_count"],
            record["token_count"],
            record["retry_count"],
        ),
    )


def _index_improvement(conn: sqlite3.Connection, record: dict) -> None:
    """Insert an improvement log entry into the SQLite index."""
    action_summary = record.get("action", "")[:200]
    conn.execute(
        "INSERT INTO improvement_log_index "
        "(timestamp, session_id, target_stage, priority, status, action_summary) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            record["timestamp"],
            record["session_id"],
            record["target_stage"],
            record["priority"],
            record["status"],
            action_summary,
        ),
    )


def _index_failure_patterns(conn: sqlite3.Connection, data: dict) -> None:
    """Replace all failure pattern index entries from patterns data."""
    conn.execute("DELETE FROM failure_pattern_index")
    for pattern in data.get("patterns", []):
        conn.execute(
            "INSERT INTO failure_pattern_index "
            "(pattern_id, classification, frequency, last_seen, severity) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                pattern["pattern_id"],
                pattern["classification"],
                pattern["frequency"],
                pattern["last_seen"],
                pattern["severity"],
            ),
        )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def initialize_store(store_path: Path) -> None:
    """Create the knowledge store directory structure and SQLite index.

    Creates all subdirectories (runs/, improvements/, baselines/,
    patterns/, retrospectives/) and initializes the SQLite3 schema.
    Idempotent: safe to call multiple times.

    Args:
        store_path: Root path of the knowledge store.

    Raises:
        OSError: If directory or database creation fails.
    """
    store_path = Path(store_path)
    for subdir in _STORE_SUBDIRS:
        os.makedirs(store_path / subdir, exist_ok=True)

    with _write_lock:
        conn = _get_connection(store_path)
        try:
            _ensure_schema(conn)
            conn.commit()
        finally:
            conn.close()

    logger.info("Knowledge store initialized at %s", store_path)


def write_run_summary(
    store_path: Path,
    run_id: str,
    completed_at: str,
    stages: dict[str, dict[str, Any]],
    overall_status: str,
    improvement_notes: list[str],
    kpis: dict[str, Any],
) -> Path:
    """Write a run_summary.json to the knowledge store.

    Validates inputs, writes atomically via tmp-then-rename, and updates
    the SQLite3 index.

    Args:
        store_path:       Root path of the knowledge store.
        run_id:           Unique run identifier.
        completed_at:     ISO 8601 UTC timestamp.
        stages:           Dictionary of stage data matching spec Section 3.1.
        overall_status:   One of "success", "partial", "failed", "aborted".
        improvement_notes: List of improvement note strings.
        kpis:             Dictionary of KPI data matching spec Section 3.1.

    Returns:
        Path to the written run_summary.json file.

    Raises:
        ValueError: If required fields are missing or have invalid values.
        OSError:    If file write or rename fails.
    """
    store_path = Path(store_path)

    if overall_status not in _VALID_OVERALL_STATUSES:
        raise ValueError(
            f"Invalid overall_status '{overall_status}'. "
            f"Must be one of {sorted(_VALID_OVERALL_STATUSES)}"
        )

    if not isinstance(stages, dict) or not stages:
        raise ValueError("stages must be a non-empty dictionary")

    for stage_name, stage_data in stages.items():
        _validate_stage_entry(stage_name, stage_data)

    if not isinstance(improvement_notes, list):
        raise ValueError("improvement_notes must be a list")

    if not isinstance(kpis, dict):
        raise ValueError("kpis must be a dictionary")

    summary = {
        "schema_version": _SCHEMA_VERSION,
        "run_id": run_id,
        "completed_at": completed_at,
        "stages": stages,
        "overall_status": overall_status,
        "improvement_notes": improvement_notes,
        "kpis": kpis,
    }

    run_dir = store_path / "runs" / run_id
    os.makedirs(run_dir, exist_ok=True)
    target = run_dir / "run_summary.json"

    with _write_lock:
        _atomic_write_json(target, summary)
        try:
            conn = _get_connection(store_path)
            try:
                _ensure_schema(conn)
                _index_run_summary(conn, summary)
                conn.commit()
            finally:
                conn.close()
        except sqlite3.Error:
            logger.warning(
                "SQLite index update failed after writing %s", target,
                exc_info=True,
            )

    logger.info("Wrote run summary for %s", run_id)
    return target


def append_stage_telemetry(
    store_path: Path,
    run_id: str,
    stage: str,
    event_type: str,
    timestamp: str,
    duration_seconds: float,
    error_count: int,
    token_count: int,
    retry_count: int,
) -> Path:
    """Append a single stage telemetry event to stage_telemetry.jsonl.

    Validates the event_type, appends with flush+fsync, and updates
    the SQLite3 index.

    Args:
        store_path:       Root path of the knowledge store.
        run_id:           Unique run identifier.
        stage:            Stage identifier (e.g., "stage_0").
        event_type:       Event type string.
        timestamp:        ISO 8601 UTC timestamp.
        duration_seconds: Seconds elapsed since stage start.
        error_count:      Cumulative error count.
        token_count:      Cumulative token count (input + output).
        retry_count:      Cumulative retry count.

    Returns:
        Path to the stage_telemetry.jsonl file.

    Raises:
        ValueError: If event_type is not in the allowed set.
        OSError:    If file write fails.
    """
    store_path = Path(store_path)

    if event_type not in _VALID_EVENT_TYPES:
        raise ValueError(
            f"Invalid event_type '{event_type}'. "
            f"Must be one of {sorted(_VALID_EVENT_TYPES)}"
        )

    if not isinstance(duration_seconds, (int, float)):
        raise ValueError("duration_seconds must be a number")
    if not isinstance(error_count, int):
        raise ValueError("error_count must be an integer")
    if not isinstance(token_count, int):
        raise ValueError("token_count must be an integer")
    if not isinstance(retry_count, int):
        raise ValueError("retry_count must be an integer")

    record = {
        "schema_version": _SCHEMA_VERSION,
        "stage": stage,
        "event_type": event_type,
        "timestamp": timestamp,
        "duration_seconds": float(duration_seconds),
        "error_count": error_count,
        "token_count": token_count,
        "retry_count": retry_count,
    }

    run_dir = store_path / "runs" / run_id
    os.makedirs(run_dir, exist_ok=True)
    target = run_dir / "stage_telemetry.jsonl"

    with _write_lock:
        _append_jsonl(target, record)
        try:
            conn = _get_connection(store_path)
            try:
                _ensure_schema(conn)
                _index_stage_event(conn, run_id, record)
                conn.commit()
            finally:
                conn.close()
        except sqlite3.Error:
            logger.warning(
                "SQLite index update failed after appending to %s", target,
                exc_info=True,
            )

    logger.info("Appended %s event for %s/%s", event_type, run_id, stage)
    return target


def update_baselines(
    store_path: Path,
    window_size: int = 10,
    smoothing_alpha: float = 0.3,
) -> Path:
    """Recompute stage baselines from the last N run summaries.

    Reads run summaries sorted by completed_at, computes exponential
    smoothing for each metric per stage, and writes stage_baselines.json
    atomically.

    Args:
        store_path:      Root path of the knowledge store.
        window_size:     Number of runs in the rolling window. Default 10.
        smoothing_alpha: Exponential smoothing factor. Default 0.3.

    Returns:
        Path to the written stage_baselines.json file.

    Raises:
        FileNotFoundError: If no run summaries exist.
        OSError:           If file write fails.
    """
    store_path = Path(store_path)
    all_summaries = _collect_run_summaries(store_path)

    if not all_summaries:
        raise FileNotFoundError(
            f"No run summaries found in {store_path / 'runs'}"
        )

    windowed = all_summaries[-window_size:]

    stage_names: set[str] = set()
    for summary in windowed:
        stage_names.update(summary.get("stages", {}).keys())

    stages_baselines: dict[str, Any] = {}

    for stage_name in sorted(stage_names):
        durations: list[float] = []
        error_rates: list[float] = []
        retry_rates: list[float] = []
        token_avgs: list[float] = []
        success_rates: list[float] = []

        for summary in windowed:
            stage_data = summary.get("stages", {}).get(stage_name)
            if stage_data is None:
                continue

            durations.append(float(stage_data.get("duration_seconds", 0.0)))

            status = stage_data.get("status", "")
            error_rate = 1.0 if len(stage_data.get("errors", [])) > 0 else 0.0
            error_rates.append(error_rate)

            retry_rate = (
                1.0 if stage_data.get("retry_count", 0) > 0 else 0.0
            )
            retry_rates.append(retry_rate)

            tc = stage_data.get("token_count", {})
            total_tokens = tc.get("input", 0) + tc.get("output", 0)
            token_avgs.append(float(total_tokens))

            success_rate = 1.0 if status == "success" else 0.0
            success_rates.append(success_rate)

        run_count = len(durations)
        if run_count == 0:
            continue

        stages_baselines[stage_name] = {
            "run_count": run_count,
            "duration_seconds": _compute_metric_baseline(
                durations, smoothing_alpha
            ),
            "error_rate": _compute_metric_baseline(
                error_rates, smoothing_alpha
            ),
            "retry_rate": _compute_metric_baseline(
                retry_rates, smoothing_alpha
            ),
            "token_count_avg": _compute_metric_baseline(
                token_avgs, smoothing_alpha
            ),
            "success_rate": _compute_metric_baseline(
                success_rates, smoothing_alpha
            ),
        }

    baselines_data = {
        "schema_version": _SCHEMA_VERSION,
        "updated_at": _utc_now_iso(),
        "window_size": window_size,
        "smoothing_alpha": smoothing_alpha,
        "stages": stages_baselines,
    }

    baselines_dir = store_path / "baselines"
    os.makedirs(baselines_dir, exist_ok=True)
    target = baselines_dir / "stage_baselines.json"

    with _write_lock:
        _atomic_write_json(target, baselines_data)

    logger.info(
        "Updated baselines from %d runs (%d stages)",
        len(windowed),
        len(stages_baselines),
    )
    return target


def append_improvement_log(
    store_path: Path,
    session_id: str,
    action: str,
    evidence_runs: list[str],
    source: str,
    priority: int,
    target_stage: str,
    status: str = "proposed",
) -> Path:
    """Append an improvement entry to improvement_log.jsonl.

    Validates inputs, appends with flush+fsync, and updates the SQLite3
    index.

    Args:
        store_path:     Root path of the knowledge store.
        session_id:     Session ID generating this improvement.
        action:         Description of the improvement action.
        evidence_runs:  List of run IDs supporting this improvement.
        source:         Generating component identifier.
        priority:       Priority ranking (1 = highest).
        target_stage:   Stage this improvement targets.
        status:         Improvement status. Default "proposed".

    Returns:
        Path to the improvement_log.jsonl file.

    Raises:
        ValueError: If required fields are missing or invalid.
        OSError:    If file write fails.
    """
    store_path = Path(store_path)

    if source not in _VALID_IMPROVEMENT_SOURCES:
        raise ValueError(
            f"Invalid source '{source}'. "
            f"Must be one of {sorted(_VALID_IMPROVEMENT_SOURCES)}"
        )

    if status not in _VALID_IMPROVEMENT_STATUSES:
        raise ValueError(
            f"Invalid status '{status}'. "
            f"Must be one of {sorted(_VALID_IMPROVEMENT_STATUSES)}"
        )

    if not isinstance(evidence_runs, list) or len(evidence_runs) < 1:
        raise ValueError("evidence_runs must be a non-empty list")

    if not isinstance(priority, int) or priority < 1:
        raise ValueError("priority must be a positive integer")

    if not action or not isinstance(action, str):
        raise ValueError("action must be a non-empty string")

    if not target_stage or not isinstance(target_stage, str):
        raise ValueError("target_stage must be a non-empty string")

    record = {
        "schema_version": _SCHEMA_VERSION,
        "timestamp": _utc_now_iso(),
        "session_id": session_id,
        "action": action,
        "evidence_runs": evidence_runs,
        "source": source,
        "priority": priority,
        "target_stage": target_stage,
        "status": status,
    }

    improvements_dir = store_path / "improvements"
    os.makedirs(improvements_dir, exist_ok=True)
    target = improvements_dir / "improvement_log.jsonl"

    with _write_lock:
        _append_jsonl(target, record)
        try:
            conn = _get_connection(store_path)
            try:
                _ensure_schema(conn)
                _index_improvement(conn, record)
                conn.commit()
            finally:
                conn.close()
        except sqlite3.Error:
            logger.warning(
                "SQLite index update failed after appending to %s", target,
                exc_info=True,
            )

    logger.info(
        "Appended improvement log: %s (target: %s)", action[:80], target_stage
    )
    return target


def rebuild_index(store_path: Path) -> None:
    """Rebuild the SQLite3 index from all JSON/JSONL source files.

    Drops all tables, recreates the schema, and re-indexes every file
    in the knowledge store. Idempotent and safe to call at any time.

    Args:
        store_path: Root path of the knowledge store.

    Raises:
        OSError: If the database file cannot be created or written.
    """
    store_path = Path(store_path)

    with _write_lock:
        conn = _get_connection(store_path)
        try:
            conn.executescript(
                "DROP TABLE IF EXISTS improvement_log_index;\n"
                "DROP TABLE IF EXISTS failure_pattern_index;\n"
                "DROP TABLE IF EXISTS stage_events;\n"
                "DROP TABLE IF EXISTS runs;\n"
            )
            _ensure_schema(conn)

            # Re-index all run summaries and telemetry
            runs_dir = store_path / "runs"
            if runs_dir.is_dir():
                for run_dir in sorted(runs_dir.iterdir()):
                    if not run_dir.is_dir():
                        continue
                    run_id = run_dir.name

                    summary_path = run_dir / "run_summary.json"
                    summary_data = _load_json_safe(summary_path)
                    if summary_data is not None:
                        _index_run_summary(conn, summary_data)

                    telemetry_path = run_dir / "stage_telemetry.jsonl"
                    for record in _read_jsonl(telemetry_path):
                        _index_stage_event(conn, run_id, record)

            # Re-index failure patterns
            patterns_path = store_path / "patterns" / "failure_patterns.json"
            patterns_data = _load_json_safe(patterns_path)
            if patterns_data is not None:
                _index_failure_patterns(conn, patterns_data)

            # Re-index improvement log
            log_path = store_path / "improvements" / "improvement_log.jsonl"
            for record in _read_jsonl(log_path):
                _index_improvement(conn, record)

            conn.commit()
        finally:
            conn.close()

    logger.info("Rebuilt SQLite index at %s", _db_path(store_path))
