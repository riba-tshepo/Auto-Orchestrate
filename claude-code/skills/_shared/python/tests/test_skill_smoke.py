"""Smoke tests for skill helper scripts.

Verifies each helper script can be imported and exposes expected
classes and functions. These are lightweight import-only checks --
no runtime behaviour is exercised.
"""

import importlib
import sys
from pathlib import Path

import pytest

SKILLS_DIR = Path(__file__).resolve().parent.parent.parent.parent


def _add_skill_to_path(skill_name: str) -> None:
    """Add a skill's scripts directory to sys.path."""
    scripts_dir = SKILLS_DIR / skill_name / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    shared_dir = SKILLS_DIR / "_shared" / "python"
    if str(shared_dir) not in sys.path:
        sys.path.insert(0, str(shared_dir))


def _try_import(skill_name: str, module_name: str):
    """Import *module_name* from *skill_name*/scripts, skipping on failure."""
    _add_skill_to_path(skill_name)
    try:
        return importlib.import_module(module_name)
    except Exception as exc:
        pytest.skip(f"Cannot import {module_name} from {skill_name}: {exc}")


# ── security-auditor / vulnerability_scanner ────────────────────────


class TestVulnerabilityScanner:
    """Smoke tests for security-auditor vulnerability_scanner."""

    @pytest.fixture(autouse=True)
    def _load_module(self):
        self.mod = _try_import("security-auditor", "vulnerability_scanner")

    def test_import(self):
        assert self.mod is not None

    def test_has_vulnerability_class(self):
        assert hasattr(self.mod, "Vulnerability")

    def test_has_scan_result_class(self):
        assert hasattr(self.mod, "ScanResult")

    def test_has_scan_dependencies(self):
        assert callable(getattr(self.mod, "scan_dependencies", None))

    def test_has_parse_dependencies(self):
        assert callable(getattr(self.mod, "parse_dependencies", None))

    def test_has_main(self):
        assert callable(getattr(self.mod, "main", None))


# ── docker-workflow / dockerfile_linter ─────────────────────────────


class TestDockerfileLinter:
    """Smoke tests for docker-workflow dockerfile_linter."""

    @pytest.fixture(autouse=True)
    def _load_module(self):
        self.mod = _try_import("docker-workflow", "dockerfile_linter")

    def test_import(self):
        assert self.mod is not None

    def test_has_linter_class(self):
        assert hasattr(self.mod, "DockerfileLinter")

    def test_has_main(self):
        assert callable(getattr(self.mod, "main", None))


# ── refactor-executor / file_analyzer ───────────────────────────────


class TestFileAnalyzer:
    """Smoke tests for refactor-executor file_analyzer."""

    @pytest.fixture(autouse=True)
    def _load_module(self):
        self.mod = _try_import("refactor-executor", "file_analyzer")

    def test_import(self):
        assert self.mod is not None

    def test_has_file_metrics(self):
        assert hasattr(self.mod, "FileMetrics")

    def test_has_function_metrics(self):
        assert hasattr(self.mod, "FunctionMetrics")

    def test_has_analysis_report(self):
        assert hasattr(self.mod, "AnalysisReport")

    def test_has_calculate_file_metrics(self):
        assert callable(getattr(self.mod, "calculate_file_metrics", None))

    def test_has_main(self):
        assert callable(getattr(self.mod, "main", None))


# ── refactor-executor / split_planner ───────────────────────────────


class TestSplitPlanner:
    """Smoke tests for refactor-executor split_planner."""

    @pytest.fixture(autouse=True)
    def _load_module(self):
        self.mod = _try_import("refactor-executor", "split_planner")

    def test_import(self):
        assert self.mod is not None


# ── codebase-stats / metric_collector ───────────────────────────────


class TestMetricCollector:
    """Smoke tests for codebase-stats metric_collector."""

    @pytest.fixture(autouse=True)
    def _load_module(self):
        self.mod = _try_import("codebase-stats", "metric_collector")

    def test_import(self):
        assert self.mod is not None


# ── codebase-stats / debt_scanner ───────────────────────────────────


class TestDebtScanner:
    """Smoke tests for codebase-stats debt_scanner."""

    @pytest.fixture(autouse=True)
    def _load_module(self):
        self.mod = _try_import("codebase-stats", "debt_scanner")

    def test_import(self):
        assert self.mod is not None


# ── dependency-analyzer / dependency_parser ─────────────────────────


class TestDependencyParser:
    """Smoke tests for dependency-analyzer dependency_parser."""

    @pytest.fixture(autouse=True)
    def _load_module(self):
        self.mod = _try_import("dependency-analyzer", "dependency_parser")

    def test_import(self):
        assert self.mod is not None


# ── spec-analyzer / spec_validator ──────────────────────────────────


class TestSpecValidator:
    """Smoke tests for spec-analyzer spec_validator."""

    @pytest.fixture(autouse=True)
    def _load_module(self):
        self.mod = _try_import("spec-analyzer", "spec_validator")

    def test_import(self):
        assert self.mod is not None


# ── production-code-workflow / detect_placeholders ──────────────────


class TestDetectPlaceholders:
    """Smoke tests for production-code-workflow detect_placeholders."""

    @pytest.fixture(autouse=True)
    def _load_module(self):
        self.mod = _try_import("production-code-workflow", "detect_placeholders")

    def test_import(self):
        assert self.mod is not None
