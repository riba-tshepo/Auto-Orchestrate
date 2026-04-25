"""Baseline manager for the continuous improvement engine.

Manages rolling per-stage baselines with exponential smoothing over a
configurable window of recent runs. Reads run summaries from the knowledge
store, computes per-stage per-metric baselines, and writes the result to
stage_baselines.json via atomic writes.

Thread-safe: all file I/O is serialized through a threading lock.
Dependencies: Python >= 3.11 stdlib only.
"""

from __future__ import annotations

import json
import logging
import os
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_SCHEMA_VERSION = 2

_VALID_STAGES = frozenset({
    "stage_0", "stage_1", "stage_2", "stage_3",
    "stage_4", "stage_4_5", "stage_5", "stage_6",
})

_VALID_METRICS = frozenset({
    "duration_seconds",
    "error_rate",
    "retry_rate",
    "token_count_avg",
    "success_rate",
})

_DEFAULT_WINDOW_SIZE = 10
_DEFAULT_SMOOTHING_ALPHA = 0.3


def _utc_now_iso() -> str:
    """Return current UTC time as ISO 8601 string with Z suffix."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _exponential_smooth(raw_values: list[float], alpha: float) -> float:
    """Recompute exponential smoothing from raw values.

    S(1) = X(1), then S(t) = alpha * X(t) + (1 - alpha) * S(t-1).
    Always recomputes from scratch to prevent floating-point drift.

    Args:
        raw_values: Ordered observations (oldest first). Must be non-empty.
        alpha: Smoothing factor in (0.0, 1.0).

    Returns:
        The smoothed value, rounded to 4 decimal places.
    """
    smoothed = raw_values[0]
    for value in raw_values[1:]:
        smoothed = alpha * value + (1.0 - alpha) * smoothed
    return round(smoothed, 4)


def _compute_metric_baseline(
    raw_values: list[float],
    alpha: float,
) -> dict[str, Any]:
    """Build a baseline metric object with smoothed, min, max, raw_values."""
    return {
        "smoothed": _exponential_smooth(raw_values, alpha),
        "min": min(raw_values),
        "max": max(raw_values),
        "raw_values": raw_values,
    }


def _atomic_write_json(target_path: Path, data: dict[str, Any]) -> None:
    """Write JSON atomically via tmp-then-rename with fsync."""
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


def _load_json_safe(path: Path) -> dict[str, Any] | None:
    """Load a JSON file, returning None if the file does not exist."""
    if not path.is_file():
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _migrate_baselines(data: dict[str, Any]) -> dict[str, Any]:
    """Migrate baseline data from older schema versions to current.

    Performs graceful migration:
    - Version 1 -> 2: No structural changes required; data is compatible.
      Logs a warning about the version mismatch.
    - Missing version: Treated as version 1.

    Args:
        data: Raw baseline data loaded from JSON.

    Returns:
        The data dict, potentially updated with the current schema_version.
    """
    file_version = data.get("schema_version", 1)
    if file_version == _SCHEMA_VERSION:
        return data
    logger.warning(
        "Baseline schema version mismatch: file has v%d, expected v%d; "
        "attempting graceful read",
        file_version,
        _SCHEMA_VERSION,
    )
    if file_version == 1:
        data["schema_version"] = _SCHEMA_VERSION
    return data


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
        data = _load_json_safe(summary_path)
        if data is not None:
            summaries.append(data)
    summaries.sort(key=lambda s: s.get("completed_at", ""))
    return summaries


def _validate_stage(stage: str) -> None:
    """Raise ValueError if stage is not a recognized identifier."""
    if stage not in _VALID_STAGES:
        raise ValueError(
            f"Invalid stage '{stage}'. "
            f"Must be one of {sorted(_VALID_STAGES)}"
        )


def _validate_metric(metric: str) -> None:
    """Raise ValueError if metric is not a recognized identifier."""
    if metric not in _VALID_METRICS:
        raise ValueError(
            f"Invalid metric '{metric}'. "
            f"Must be one of {sorted(_VALID_METRICS)}"
        )


@dataclass
class BaselineManager:
    """Manages rolling per-stage baselines for the CI engine.

    Maintains exponentially smoothed baselines over a rolling window of
    the last N runs. Reads run summaries from the knowledge store, computes
    per-stage per-metric baselines, and writes the result to
    stage_baselines.json.

    Attributes:
        knowledge_store_path: Root path to the knowledge store directory.
        window_size: Maximum number of runs in the rolling window.
            Must be 10 for schema_version=1.
        smoothing_alpha: Exponential smoothing factor.
            Must be 0.3 for schema_version=1. Must be in (0.0, 1.0).
    """

    knowledge_store_path: Path
    window_size: int = _DEFAULT_WINDOW_SIZE
    smoothing_alpha: float = _DEFAULT_SMOOTHING_ALPHA

    def __post_init__(self) -> None:
        self.knowledge_store_path = Path(self.knowledge_store_path)
        self._lock = threading.Lock()

        if not (0.0 < self.smoothing_alpha < 1.0):
            raise ValueError(
                f"smoothing_alpha must be in (0.0, 1.0), got {self.smoothing_alpha}"
            )
        if self.window_size < 1:
            raise ValueError(
                f"window_size must be >= 1, got {self.window_size}"
            )

    def update_baselines(self) -> Path:
        """Recompute and write stage baselines from recent run summaries.

        Enumerates all run_summary.json files, takes the last window_size
        runs sorted by completed_at, computes exponential-smoothed baselines
        per stage per metric with FIFO eviction and full recomputation, and
        writes the result atomically to stage_baselines.json.

        Returns:
            Path to the written stage_baselines.json file.

        Raises:
            FileNotFoundError: If no run summaries exist in the store.
            OSError: If the atomic write operation fails.
        """
        summaries = self._load_run_summaries()

        if not summaries:
            baselines_data: dict[str, Any] = {
                "schema_version": _SCHEMA_VERSION,
                "first_run": True,
                "baselines": {},
            }
        else:
            stages_baselines = self._compute_stage_baselines(summaries)
            baselines_data = {
                "schema_version": _SCHEMA_VERSION,
                "updated_at": _utc_now_iso(),
                "window_size": self.window_size,
                "smoothing_alpha": self.smoothing_alpha,
                "stages": stages_baselines,
            }

        baselines_dir = self.knowledge_store_path / "baselines"
        os.makedirs(baselines_dir, exist_ok=True)
        target = baselines_dir / "stage_baselines.json"

        with self._lock:
            _atomic_write_json(target, baselines_data)

        logger.info(
            "Updated baselines from %d runs (%d stages)",
            len(summaries),
            len(baselines_data.get("stages", {})),
        )
        return target

    def get_baseline(
        self,
        stage: str,
        metric: str,
    ) -> float | None:
        """Retrieve the current smoothed baseline for a stage-metric pair.

        Loads stage_baselines.json and returns the smoothed value for the
        requested stage and metric. Returns None if no baseline data exists
        (no prior runs, file missing, or stage/metric absent).

        Args:
            stage: Pipeline stage identifier (e.g., "stage_0").
            metric: Metric name (e.g., "duration_seconds").

        Returns:
            The smoothed baseline value as a float, or None if no
            baseline data exists.

        Raises:
            ValueError: If stage or metric is not a recognized identifier.
        """
        _validate_stage(stage)
        _validate_metric(metric)

        baselines_path = (
            self.knowledge_store_path / "baselines" / "stage_baselines.json"
        )

        with self._lock:
            data = _load_json_safe(baselines_path)

        if data is None:
            return None

        data = _migrate_baselines(data)

        if data.get("first_run"):
            return None

        stages = data.get("stages", {})
        stage_data = stages.get(stage)
        if stage_data is None:
            return None

        metric_data = stage_data.get(metric)
        if metric_data is None:
            return None

        smoothed = metric_data.get("smoothed")
        if smoothed is None:
            return None

        return float(smoothed)

    def compute_deviation(
        self,
        stage: str,
        metric: str,
        current_value: float,
    ) -> float | None:
        """Compute the percentage deviation of a value from its baseline.

        A positive value means the current value is higher than the baseline.
        For metrics where lower is better (duration, errors, retries), a
        positive deviation indicates regression. For metrics where higher
        is better (success_rate), a positive deviation indicates improvement.

        Args:
            stage: Pipeline stage identifier.
            metric: Metric name.
            current_value: The observed value from the current run.

        Returns:
            Percentage deviation as a float, or None if no baseline exists
            or the baseline is zero.

        Raises:
            ValueError: If stage or metric is not a recognized identifier.
        """
        _validate_stage(stage)
        _validate_metric(metric)

        baseline = self.get_baseline(stage, metric)
        if baseline is None:
            return None

        if baseline == 0.0:
            return None

        deviation_pct = ((current_value - baseline) / baseline) * 100.0
        return round(deviation_pct, 4)

    def _load_run_summaries(self) -> list[dict[str, Any]]:
        """Load and sort run summaries from the knowledge store.

        Returns:
            List of run summary dicts, sorted by completed_at ascending
            (oldest first), limited to the last window_size entries.
            Returns an empty list if no run summaries exist (first-run).
        """
        with self._lock:
            all_summaries = _collect_run_summaries(self.knowledge_store_path)

        if not all_summaries:
            logger.info(
                "No run summaries found; returning first-run baselines"
            )
            return []

        return all_summaries[-self.window_size:]

    def _compute_stage_baselines(
        self,
        summaries: list[dict[str, Any]],
    ) -> dict[str, dict[str, Any]]:
        """Compute per-stage baselines from a list of run summaries.

        For each stage, computes smoothed, min, max, and raw_values for
        all five metrics (duration_seconds, error_rate, retry_rate,
        token_count_avg, success_rate). Uses FIFO eviction with full
        recomputation from raw_values to prevent floating-point drift.

        Args:
            summaries: List of run summary dicts (oldest first).

        Returns:
            Dictionary keyed by stage name, containing baseline objects.
        """
        stage_names: set[str] = set()
        for summary in summaries:
            stage_names.update(summary.get("stages", {}).keys())

        stages_baselines: dict[str, dict[str, Any]] = {}
        alpha = self.smoothing_alpha

        for stage_name in sorted(stage_names):
            durations: list[float] = []
            error_rates: list[float] = []
            retry_rates: list[float] = []
            token_avgs: list[float] = []
            success_rates: list[float] = []

            for summary in summaries:
                stage_data = summary.get("stages", {}).get(stage_name)
                if stage_data is None:
                    continue

                durations.append(
                    float(stage_data.get("duration_seconds", 0.0))
                )

                errors = stage_data.get("errors", [])
                error_rate = 1.0 if len(errors) > 0 else 0.0
                error_rates.append(error_rate)

                retry_count = stage_data.get("retry_count", 0)
                retry_rate = 1.0 if retry_count > 0 else 0.0
                retry_rates.append(retry_rate)

                tc = stage_data.get("token_count", {})
                total_tokens = tc.get("input", 0) + tc.get("output", 0)
                token_avgs.append(float(total_tokens))

                status = stage_data.get("status", "")
                success_rate = 1.0 if status == "success" else 0.0
                success_rates.append(success_rate)

            run_count = len(durations)
            if run_count == 0:
                continue

            stages_baselines[stage_name] = {
                "run_count": run_count,
                "duration_seconds": _compute_metric_baseline(
                    durations, alpha
                ),
                "error_rate": _compute_metric_baseline(
                    error_rates, alpha
                ),
                "retry_rate": _compute_metric_baseline(
                    retry_rates, alpha
                ),
                "token_count_avg": _compute_metric_baseline(
                    token_avgs, alpha
                ),
                "success_rate": _compute_metric_baseline(
                    success_rates, alpha
                ),
            }

        return stages_baselines
