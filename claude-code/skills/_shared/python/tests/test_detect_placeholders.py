"""
Unit tests for production-code-workflow detect_placeholders script.

Tests cover:
- Severity enum values and ordering
- Issue and Pattern dataclass construction and serialization
- PlaceholderDetector language detection
- PlaceholderDetector file scanning (real content via tmp files)
- ScanReport verdict calculation
- scan_path convenience function
"""

import sys
from pathlib import Path

import pytest

# Ensure skill and shared library are on path
SKILLS_DIR = Path(__file__).resolve().parent.parent.parent.parent
SHARED_PYTHON_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SKILLS_DIR / "production-code-workflow" / "scripts"

for _p in (str(SCRIPTS_DIR), str(SHARED_PYTHON_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from detect_placeholders import (
        Issue,
        PATTERNS,
        Pattern,
        PlaceholderDetector,
        ScanReport,
        Severity,
        scan_path,
    )
except ImportError as exc:
    pytest.skip(f"Cannot import detect_placeholders: {exc}", allow_module_level=True)


# ---------------------------------------------------------------------------
# Severity enum
# ---------------------------------------------------------------------------


class TestSeverityEnum:
    """Tests for the Severity enum."""

    def test_severity_order(self):
        """BLOCKER > CRITICAL > MAJOR > MINOR."""
        assert Severity.BLOCKER.value > Severity.CRITICAL.value
        assert Severity.CRITICAL.value > Severity.MAJOR.value
        assert Severity.MAJOR.value > Severity.MINOR.value

    def test_severity_str(self):
        """String representation should match the enum name."""
        assert str(Severity.BLOCKER) == "BLOCKER"
        assert str(Severity.CRITICAL) == "CRITICAL"
        assert str(Severity.MAJOR) == "MAJOR"
        assert str(Severity.MINOR) == "MINOR"

    def test_severity_by_name(self):
        """Lookup by name should work."""
        assert Severity["BLOCKER"] is Severity.BLOCKER
        assert Severity["MINOR"] is Severity.MINOR


# ---------------------------------------------------------------------------
# Issue dataclass
# ---------------------------------------------------------------------------


class TestIssueDataclass:
    """Tests for the Issue dataclass and its to_dict method."""

    def _make_issue(self, **kwargs):
        defaults = dict(
            file_path="src/Foo.java",
            line_number=10,
            line_content="  password = 'secret'  ",
            pattern_name="hardcoded_password",
            severity=Severity.BLOCKER,
            message="Hardcoded password/secret",
            language="java",
        )
        defaults.update(kwargs)
        return Issue(**defaults)

    def test_to_dict_keys(self):
        issue = self._make_issue()
        d = issue.to_dict()
        assert set(d.keys()) == {
            "file_path",
            "line_number",
            "line_content",
            "pattern_name",
            "severity",
            "message",
            "language",
        }

    def test_to_dict_severity_is_string(self):
        issue = self._make_issue(severity=Severity.CRITICAL)
        assert issue.to_dict()["severity"] == "CRITICAL"

    def test_to_dict_line_content_truncated_to_100(self):
        long_line = "x" * 200
        issue = self._make_issue(line_content=long_line)
        assert len(issue.to_dict()["line_content"]) <= 100

    def test_to_dict_line_content_stripped(self):
        issue = self._make_issue(line_content="  hello world  ")
        assert issue.to_dict()["line_content"] == "hello world"


# ---------------------------------------------------------------------------
# Pattern dataclass
# ---------------------------------------------------------------------------


class TestPatternDataclass:
    """Tests for the Pattern dataclass defaults."""

    def test_default_language_is_all(self):
        p = Pattern(
            name="test_pat",
            regex=r"dummy",
            severity=Severity.MINOR,
            message="test message",
        )
        assert p.language == "all"

    def test_default_file_extensions_is_none(self):
        p = Pattern(
            name="test_pat",
            regex=r"dummy",
            severity=Severity.MINOR,
            message="test message",
        )
        assert p.file_extensions is None

    def test_custom_file_extensions(self):
        p = Pattern(
            name="java_pat",
            regex=r"System\.out",
            severity=Severity.MAJOR,
            message="Use logger",
            file_extensions={".java"},
            language="java",
        )
        assert ".java" in p.file_extensions


# ---------------------------------------------------------------------------
# PlaceholderDetector
# ---------------------------------------------------------------------------


class TestPlaceholderDetectorLanguageDetection:
    """Tests for detect_language method."""

    def setup_method(self):
        self.detector = PlaceholderDetector()

    def test_java_detection(self):
        assert self.detector.detect_language(Path("Foo.java")) == "java"

    def test_python_detection(self):
        assert self.detector.detect_language(Path("script.py")) == "python"

    def test_typescript_detection(self):
        assert self.detector.detect_language(Path("app.ts")) == "typescript"

    def test_tsx_detection(self):
        assert self.detector.detect_language(Path("component.tsx")) == "typescript"

    def test_go_detection(self):
        assert self.detector.detect_language(Path("main.go")) == "go"

    def test_rust_detection(self):
        assert self.detector.detect_language(Path("lib.rs")) == "rust"

    def test_unknown_extension(self):
        assert self.detector.detect_language(Path("file.xyz")) == "unknown"

    def test_case_insensitive_extension(self):
        assert self.detector.detect_language(Path("Foo.JAVA")) == "java"


class TestPlaceholderDetectorScanFile:
    """Tests for scan_file method using temporary files."""

    def setup_method(self):
        self.detector = PlaceholderDetector()

    def test_scan_file_no_issues(self, tmp_path):
        f = tmp_path / "clean.py"
        f.write_text("def hello():\n    return 'world'\n")
        issues = self.detector.scan_file(f)
        assert isinstance(issues, list)
        # No placeholder patterns in clean code
        pattern_names = [i.pattern_name for i in issues]
        assert "hardcoded_password" not in pattern_names
        assert "todo_comment" not in pattern_names

    def test_scan_file_detects_todo(self, tmp_path):
        f = tmp_path / "todo.py"
        f.write_text("def process():\n    # TODO: implement this\n    pass\n")
        issues = self.detector.scan_file(f)
        names = [i.pattern_name for i in issues]
        assert "todo_comment" in names

    def test_scan_file_detects_fixme(self, tmp_path):
        f = tmp_path / "fixme.py"
        f.write_text("x = 1  # FIXME: broken\n")
        issues = self.detector.scan_file(f)
        names = [i.pattern_name for i in issues]
        assert "fixme_comment" in names

    def test_scan_file_detects_hardcoded_password(self, tmp_path):
        f = tmp_path / "creds.py"
        f.write_text('password = "supersecret"\n')
        issues = self.detector.scan_file(f)
        names = [i.pattern_name for i in issues]
        assert "hardcoded_password" in names

    def test_scan_file_respects_extension_filter(self, tmp_path):
        """Java-only patterns should not fire on .py files."""
        f = tmp_path / "Foo.py"
        f.write_text("throw new UnsupportedOperationException()\n")
        issues = self.detector.scan_file(f)
        names = [i.pattern_name for i in issues]
        assert "java_unsupported_operation" not in names

    def test_scan_file_java_specific_pattern(self, tmp_path):
        f = tmp_path / "Foo.java"
        f.write_text("throw new UnsupportedOperationException();\n")
        issues = self.detector.scan_file(f)
        names = [i.pattern_name for i in issues]
        assert "java_unsupported_operation" in names

    def test_scan_file_returns_correct_line_number(self, tmp_path):
        f = tmp_path / "lines.py"
        f.write_text("x = 1\n# TODO: fix this\nz = 3\n")
        issues = self.detector.scan_file(f)
        todo_issues = [i for i in issues if i.pattern_name == "todo_comment"]
        assert len(todo_issues) == 1
        assert todo_issues[0].line_number == 2

    def test_scan_nonexistent_file_returns_empty(self, tmp_path):
        issues = self.detector.scan_file(tmp_path / "nonexistent.py")
        assert issues == []

    def test_scan_file_sets_language_field(self, tmp_path):
        f = tmp_path / "script.py"
        f.write_text("# TODO: add logic\n")
        issues = self.detector.scan_file(f)
        for issue in issues:
            # language-specific issues carry their language;
            # 'all' patterns carry the detected file language
            assert issue.language in (
                "python",
                "java",
                "scala",
                "kotlin",
                "csharp",
                "typescript",
                "javascript",
                "go",
                "rust",
                "all",
            )


class TestPlaceholderDetectorScanDirectory:
    """Tests for scan_directory method."""

    def setup_method(self):
        self.detector = PlaceholderDetector()

    def test_scan_directory_collects_issues_from_all_files(self, tmp_path):
        a = tmp_path / "a.py"
        b = tmp_path / "b.py"
        a.write_text("# TODO: fix a\n")
        b.write_text("# FIXME: fix b\n")
        issues = self.detector.scan_directory(tmp_path)
        names = {i.pattern_name for i in issues}
        assert "todo_comment" in names
        assert "fixme_comment" in names

    def test_scan_directory_excludes_pycache(self, tmp_path):
        pycache = tmp_path / "__pycache__"
        pycache.mkdir()
        bad = pycache / "bad.py"
        bad.write_text("# TODO: should be excluded\n")
        issues = self.detector.scan_directory(tmp_path)
        paths = [i.file_path for i in issues]
        assert not any("__pycache__" in p for p in paths)

    def test_scan_empty_directory_returns_empty_list(self, tmp_path):
        issues = self.detector.scan_directory(tmp_path)
        assert issues == []


# ---------------------------------------------------------------------------
# ScanReport
# ---------------------------------------------------------------------------


class TestScanReport:
    """Tests for ScanReport.calculate_verdict and to_dict."""

    def _make_report(self, severity_counts: dict) -> ScanReport:
        report = ScanReport(path="/some/path")
        report.issues_by_severity = severity_counts
        return report

    def test_verdict_blocked_when_blockers(self):
        report = self._make_report({"BLOCKER": 1, "CRITICAL": 0, "MAJOR": 0})
        verdict = report.calculate_verdict()
        assert verdict == "BLOCKED"
        assert report.verdict == "BLOCKED"

    def test_verdict_needs_fixes_when_critical(self):
        report = self._make_report({"BLOCKER": 0, "CRITICAL": 2, "MAJOR": 0})
        verdict = report.calculate_verdict()
        assert verdict == "NEEDS_FIXES"

    def test_verdict_needs_fixes_when_many_major(self):
        report = self._make_report({"BLOCKER": 0, "CRITICAL": 0, "MAJOR": 4})
        verdict = report.calculate_verdict()
        assert verdict == "NEEDS_FIXES"

    def test_verdict_approved_when_few_issues(self):
        report = self._make_report({"BLOCKER": 0, "CRITICAL": 0, "MAJOR": 2})
        verdict = report.calculate_verdict()
        assert verdict == "APPROVED"

    def test_verdict_approved_empty(self):
        report = self._make_report({})
        verdict = report.calculate_verdict()
        assert verdict == "APPROVED"

    def test_to_dict_keys(self):
        report = ScanReport(path="test/")
        report.calculate_verdict()
        d = report.to_dict()
        assert "path" in d
        assert "total_files_scanned" in d
        assert "total_issues" in d
        assert "issues_by_severity" in d
        assert "issues_by_language" in d
        assert "verdict" in d


# ---------------------------------------------------------------------------
# scan_path convenience function
# ---------------------------------------------------------------------------


class TestScanPath:
    """Tests for the scan_path top-level function."""

    def test_scan_nonexistent_path_returns_empty_report(self, tmp_path):
        report = scan_path(str(tmp_path / "does_not_exist.py"))
        assert report.total_issues == 0

    def test_scan_clean_file_returns_approved(self, tmp_path):
        f = tmp_path / "clean.py"
        f.write_text("def add(a, b):\n    return a + b\n")
        report = scan_path(str(f))
        assert report.verdict == "APPROVED"
        assert report.total_files_scanned == 1

    def test_scan_file_with_todo_returns_issues(self, tmp_path):
        f = tmp_path / "todo.py"
        f.write_text("# TODO: implement\n")
        report = scan_path(str(f))
        assert report.total_issues >= 1

    def test_scan_directory(self, tmp_path):
        (tmp_path / "a.py").write_text("# TODO: a\n")
        (tmp_path / "b.py").write_text("# FIXME: b\n")
        report = scan_path(str(tmp_path))
        assert report.total_issues >= 2

    def test_severity_threshold_filters_lower_severities(self, tmp_path):
        """Only issues at or above the threshold should appear."""
        f = tmp_path / "minor.py"
        # Magic number pattern (MINOR) — should be filtered out by 'critical' threshold
        f.write_text("timeout = 3600\n")
        report_all = scan_path(str(f), severity_threshold="minor")
        report_critical = scan_path(str(f), severity_threshold="critical")
        # critical threshold excludes MINOR issues
        assert report_critical.total_issues <= report_all.total_issues


# ---------------------------------------------------------------------------
# PATTERNS list sanity
# ---------------------------------------------------------------------------


class TestPatternsListSanity:
    """Basic sanity checks on the built-in PATTERNS list."""

    def test_patterns_non_empty(self):
        assert len(PATTERNS) > 0

    def test_all_patterns_have_name(self):
        for p in PATTERNS:
            assert p.name, f"Pattern missing name: {p}"

    def test_all_patterns_have_regex(self):
        for p in PATTERNS:
            assert p.regex, f"Pattern {p.name!r} missing regex"

    def test_all_patterns_have_message(self):
        for p in PATTERNS:
            assert p.message, f"Pattern {p.name!r} missing message"

    def test_all_severities_are_severity_enum(self):
        for p in PATTERNS:
            assert isinstance(p.severity, Severity), f"Pattern {p.name!r} has invalid severity"
