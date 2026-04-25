"""
Codebase Stats scripts.

Scripts for collecting codebase metrics, comparing trends, and scanning for technical debt.

Available scripts:
- metric_collector: Collect LOC, function counts, complexity metrics
- trend_comparator: Compare metric snapshots over time
- debt_scanner: Scan for TODO/FIXME/HACK comments
"""

from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent

__all__ = [
    "metric_collector",
    "trend_comparator",
    "debt_scanner",
]
