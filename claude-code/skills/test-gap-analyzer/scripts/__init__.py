"""
Test Coverage scripts.

Scripts for analyzing coverage, detecting gaps, and generating test stubs.

Available scripts:
- coverage_analyzer: Parse Cobertura, LCOV, coverage.py formats
- gap_detector: Identify untested functions by complexity
- test_stub_generator: Generate pytest/unittest test skeletons
"""

from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent

__all__ = [
    "coverage_analyzer",
    "gap_detector",
    "test_stub_generator",
]
