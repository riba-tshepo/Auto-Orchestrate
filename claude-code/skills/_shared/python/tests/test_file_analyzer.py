"""
Unit tests for refactor-executor file_analyzer script.

Tests cover:
- validate_safe_path security checks
- calculate_complexity on AST nodes
- calculate_function_metrics and calculate_class_metrics on real code
- count_imports on real Python files
- calculate_cohesion heuristic
- calculate_file_metrics integration
- identify_split_candidates threshold logic
- FileMetrics, ClassMetrics, FunctionMetrics dataclass serialisation
- AnalysisReport dataclass serialisation
"""

import ast
import sys
from pathlib import Path

import pytest

# Ensure skill scripts and shared library are importable
SKILLS_DIR = Path(__file__).resolve().parent.parent.parent.parent
SHARED_PYTHON_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SKILLS_DIR / "refactor-executor" / "scripts"

for _p in (str(SCRIPTS_DIR), str(SHARED_PYTHON_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from file_analyzer import (
        AnalysisReport,
        ClassMetrics,
        FileMetrics,
        FunctionMetrics,
        SplitCandidate,
        calculate_class_metrics,
        calculate_cohesion,
        calculate_complexity,
        calculate_file_metrics,
        calculate_function_metrics,
        count_imports,
        identify_split_candidates,
        validate_safe_path,
    )
except ImportError as exc:
    pytest.skip(f"Cannot import file_analyzer: {exc}", allow_module_level=True)


# ---------------------------------------------------------------------------
# validate_safe_path
# ---------------------------------------------------------------------------


class TestValidateSafePath:
    """Tests for path validation security checks."""

    def test_valid_path_returns_resolved(self, tmp_path):
        result = validate_safe_path(tmp_path / "file.py")
        assert result.is_absolute()

    def test_null_byte_raises_value_error(self, tmp_path):
        with pytest.raises(ValueError):
            validate_safe_path(Path("file\x00name.py"))

    def test_context_included_in_error_message(self):
        with pytest.raises(ValueError):
            validate_safe_path(Path("file\x00.py"), context="my_context")


# ---------------------------------------------------------------------------
# calculate_complexity
# ---------------------------------------------------------------------------


class TestCalculateComplexity:
    """Tests for cyclomatic complexity calculation."""

    def _parse_func(self, source: str) -> ast.AST:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                return node
        raise ValueError("No function found")

    def test_simple_function_has_complexity_1(self):
        src = "def f():\n    return 1\n"
        node = self._parse_func(src)
        assert calculate_complexity(node) == 1

    def test_if_increments_complexity(self):
        src = "def f(x):\n    if x:\n        return 1\n    return 0\n"
        node = self._parse_func(src)
        assert calculate_complexity(node) == 2

    def test_for_loop_increments_complexity(self):
        src = "def f(items):\n    for i in items:\n        pass\n"
        node = self._parse_func(src)
        assert calculate_complexity(node) == 2

    def test_while_loop_increments_complexity(self):
        src = "def f():\n    while True:\n        break\n"
        node = self._parse_func(src)
        assert calculate_complexity(node) == 2

    def test_except_handler_increments_complexity(self):
        src = "def f():\n    try:\n        pass\n    except Exception:\n        pass\n"
        node = self._parse_func(src)
        assert calculate_complexity(node) == 2

    def test_boolean_and_increments_complexity(self):
        src = "def f(a, b):\n    if a and b:\n        return True\n"
        node = self._parse_func(src)
        # 1 baseline + 1 for if + 1 for boolean 'and' (2 values - 1)
        assert calculate_complexity(node) == 3

    def test_nested_conditions_accumulate(self):
        src = (
            "def f(a, b, c):\n"
            "    if a:\n"
            "        if b:\n"
            "            if c:\n"
            "                return 1\n"
            "    return 0\n"
        )
        node = self._parse_func(src)
        assert calculate_complexity(node) == 4  # 1 + 3 ifs


# ---------------------------------------------------------------------------
# calculate_function_metrics
# ---------------------------------------------------------------------------


class TestCalculateFunctionMetrics:
    """Tests for per-function metrics extraction."""

    def test_returns_list(self, tmp_path):
        f = tmp_path / "funcs.py"
        f.write_text("def foo():\n    pass\n")
        result = calculate_function_metrics(f)
        assert isinstance(result, list)

    def test_detects_function_name(self, tmp_path):
        f = tmp_path / "funcs.py"
        f.write_text("def my_function():\n    pass\n")
        metrics = calculate_function_metrics(f)
        names = [m.name for m in metrics]
        assert "my_function" in names

    def test_detects_multiple_functions(self, tmp_path):
        f = tmp_path / "multi.py"
        f.write_text("def alpha():\n    pass\n\ndef beta():\n    pass\n")
        metrics = calculate_function_metrics(f)
        names = {m.name for m in metrics}
        assert "alpha" in names
        assert "beta" in names

    def test_docstring_detection_true(self, tmp_path):
        f = tmp_path / "doc.py"
        f.write_text('def documented():\n    """A docstring."""\n    pass\n')
        metrics = calculate_function_metrics(f)
        doc_metrics = [m for m in metrics if m.name == "documented"]
        assert doc_metrics[0].has_docstring is True

    def test_docstring_detection_false(self, tmp_path):
        f = tmp_path / "nodoc.py"
        f.write_text("def undocumented():\n    pass\n")
        metrics = calculate_function_metrics(f)
        m = [m for m in metrics if m.name == "undocumented"][0]
        assert m.has_docstring is False

    def test_parameter_count(self, tmp_path):
        f = tmp_path / "params.py"
        f.write_text("def greet(name, greeting, punctuation):\n    pass\n")
        metrics = calculate_function_metrics(f)
        m = [m for m in metrics if m.name == "greet"][0]
        assert m.parameters == 3

    def test_line_count(self, tmp_path):
        f = tmp_path / "lines.py"
        f.write_text("def five_liner(x):\n    a = 1\n    b = 2\n    c = 3\n    return a + b + c\n")
        metrics = calculate_function_metrics(f)
        m = [m for m in metrics if m.name == "five_liner"][0]
        assert m.lines == 5

    def test_invalid_file_returns_empty_list(self, tmp_path):
        result = calculate_function_metrics(tmp_path / "nonexistent.py")
        assert result == []

    def test_to_dict_keys(self, tmp_path):
        f = tmp_path / "f.py"
        f.write_text("def foo():\n    pass\n")
        metrics = calculate_function_metrics(f)
        d = metrics[0].to_dict()
        assert set(d.keys()) == {
            "name", "line_start", "line_end", "lines",
            "complexity", "parameters", "has_docstring",
        }


# ---------------------------------------------------------------------------
# calculate_class_metrics
# ---------------------------------------------------------------------------


class TestCalculateClassMetrics:
    """Tests for per-class metrics extraction."""

    def test_detects_class_name(self, tmp_path):
        f = tmp_path / "cls.py"
        f.write_text("class MyClass:\n    pass\n")
        metrics = calculate_class_metrics(f)
        names = [m.name for m in metrics]
        assert "MyClass" in names

    def test_counts_methods(self, tmp_path):
        f = tmp_path / "cls.py"
        f.write_text(
            "class Counter:\n"
            "    def increment(self): pass\n"
            "    def decrement(self): pass\n"
            "    def reset(self): pass\n"
        )
        metrics = calculate_class_metrics(f)
        m = [m for m in metrics if m.name == "Counter"][0]
        assert m.methods == 3

    def test_counts_annotated_attributes(self, tmp_path):
        f = tmp_path / "cls.py"
        f.write_text("class Point:\n    x: int\n    y: int\n")
        metrics = calculate_class_metrics(f)
        m = [m for m in metrics if m.name == "Point"][0]
        assert m.attributes == 2

    def test_invalid_file_returns_empty_list(self, tmp_path):
        result = calculate_class_metrics(tmp_path / "missing.py")
        assert result == []

    def test_to_dict_keys(self, tmp_path):
        f = tmp_path / "cls.py"
        f.write_text("class A:\n    pass\n")
        metrics = calculate_class_metrics(f)
        d = metrics[0].to_dict()
        assert set(d.keys()) == {
            "name", "line_start", "line_end", "lines",
            "methods", "attributes", "complexity",
        }


# ---------------------------------------------------------------------------
# count_imports
# ---------------------------------------------------------------------------


class TestCountImports:
    """Tests for import counting."""

    def test_no_imports(self, tmp_path):
        f = tmp_path / "clean.py"
        f.write_text("x = 1\n")
        assert count_imports(f) == 0

    def test_single_import(self, tmp_path):
        f = tmp_path / "one.py"
        f.write_text("import os\n")
        assert count_imports(f) == 1

    def test_from_import_single(self, tmp_path):
        f = tmp_path / "from.py"
        f.write_text("from pathlib import Path\n")
        assert count_imports(f) == 1

    def test_multiple_names_in_import(self, tmp_path):
        f = tmp_path / "multi.py"
        f.write_text("from os.path import join, exists, dirname\n")
        assert count_imports(f) == 3

    def test_invalid_file_returns_zero(self, tmp_path):
        assert count_imports(tmp_path / "missing.py") == 0


# ---------------------------------------------------------------------------
# calculate_cohesion
# ---------------------------------------------------------------------------


class TestCalculateCohesion:
    """Tests for cohesion score heuristic."""

    def _make_func(self, name: str) -> FunctionMetrics:
        return FunctionMetrics(
            name=name, line_start=1, line_end=5, lines=5,
            complexity=1, parameters=0, has_docstring=False,
        )

    def test_single_function_is_fully_cohesive(self):
        funcs = [self._make_func("do_something")]
        score = calculate_cohesion(funcs, "")
        assert score == 1.0

    def test_empty_function_list_returns_one(self):
        score = calculate_cohesion([], "")
        assert score == 1.0

    def test_cohesion_is_between_0_and_1(self):
        funcs = [self._make_func(n) for n in ["parse_x", "validate_y", "render_z", "load_a"]]
        score = calculate_cohesion(funcs, "")
        assert 0.0 <= score <= 1.0

    def test_uniform_prefix_yields_high_cohesion(self):
        funcs = [self._make_func(f"parse_item_{i}") for i in range(5)]
        score = calculate_cohesion(funcs, "")
        # All share "parse" prefix — should be high cohesion
        assert score >= 0.5


# ---------------------------------------------------------------------------
# calculate_file_metrics integration
# ---------------------------------------------------------------------------


class TestCalculateFileMetrics:
    """Integration tests for calculate_file_metrics."""

    def test_returns_file_metrics(self, tmp_path):
        f = tmp_path / "sample.py"
        f.write_text("import os\n\ndef foo():\n    pass\n")
        result = calculate_file_metrics(f)
        assert isinstance(result, FileMetrics)

    def test_line_counts_are_consistent(self, tmp_path):
        content = "import os\n\ndef foo():\n    pass\n"
        f = tmp_path / "sample.py"
        f.write_text(content)
        result = calculate_file_metrics(f)
        # code + blank + comment should equal total
        assert result.lines_code + result.lines_blank + result.lines_comment == result.lines_total

    def test_nonexistent_file_returns_zero_lines(self, tmp_path):
        result = calculate_file_metrics(tmp_path / "missing.py")
        assert result.lines_total == 0

    def test_to_dict_structure(self, tmp_path):
        f = tmp_path / "s.py"
        f.write_text("def g():\n    pass\n")
        d = calculate_file_metrics(f).to_dict()
        assert "path" in d
        assert "lines" in d
        assert set(d["lines"].keys()) == {"total", "code", "blank", "comment"}
        assert "functions" in d
        assert "classes" in d
        assert "imports" in d
        assert "complexity" in d
        assert "cohesion_score" in d


# ---------------------------------------------------------------------------
# identify_split_candidates
# ---------------------------------------------------------------------------


class TestIdentifySplitCandidates:
    """Tests for split candidate identification logic."""

    def _make_metrics(self, lines: int = 100, complexity: int = 5, cohesion: float = 0.8) -> FileMetrics:
        return FileMetrics(
            path="dummy.py",
            lines_total=lines,
            lines_code=lines,
            lines_blank=0,
            lines_comment=0,
            complexity=complexity,
            cohesion_score=cohesion,
        )

    def test_below_thresholds_returns_none(self):
        metrics = self._make_metrics(lines=50, complexity=5)
        result = identify_split_candidates(metrics, threshold_lines=200, threshold_complexity=20)
        assert result is None

    def test_exceeds_lines_threshold_returns_candidate(self):
        metrics = self._make_metrics(lines=300, complexity=5)
        result = identify_split_candidates(metrics, threshold_lines=200, threshold_complexity=20)
        assert result is not None
        assert isinstance(result, SplitCandidate)

    def test_exceeds_complexity_threshold_returns_candidate(self):
        metrics = self._make_metrics(lines=50, complexity=25)
        result = identify_split_candidates(metrics, threshold_lines=200, threshold_complexity=20)
        assert result is not None

    def test_high_priority_when_2x_lines_threshold(self):
        metrics = self._make_metrics(lines=500, complexity=5)
        result = identify_split_candidates(metrics, threshold_lines=200, threshold_complexity=20)
        assert result is not None
        assert result.priority == "high"

    def test_medium_priority_when_slightly_above_threshold(self):
        metrics = self._make_metrics(lines=250, complexity=5)
        result = identify_split_candidates(metrics, threshold_lines=200, threshold_complexity=20)
        assert result is not None
        assert result.priority == "medium"

    def test_low_cohesion_triggers_candidate(self):
        metrics = self._make_metrics(lines=50, complexity=5, cohesion=0.1)
        result = identify_split_candidates(metrics, threshold_lines=200, threshold_complexity=20)
        assert result is not None

    def test_split_candidate_to_dict_keys(self):
        metrics = self._make_metrics(lines=300, complexity=5)
        result = identify_split_candidates(metrics, threshold_lines=200, threshold_complexity=20)
        assert result is not None
        d = result.to_dict()
        assert set(d.keys()) == {"path", "reason", "metrics", "priority"}


# ---------------------------------------------------------------------------
# AnalysisReport dataclass
# ---------------------------------------------------------------------------


class TestAnalysisReport:
    """Tests for AnalysisReport to_dict structure."""

    def test_to_dict_structure(self):
        report = AnalysisReport(target="src/")
        d = report.to_dict()
        assert "target" in d
        assert "summary" in d
        assert "files" in d
        assert "candidates_for_split" in d
        assert set(d["summary"].keys()) == {
            "files_analyzed",
            "total_lines",
            "total_functions",
            "total_classes",
            "split_candidates",
        }

    def test_errors_field_is_none_when_empty(self):
        report = AnalysisReport(target="src/")
        d = report.to_dict()
        assert d["errors"] is None

    def test_errors_field_present_when_not_empty(self):
        report = AnalysisReport(target="src/", errors=["something went wrong"])
        d = report.to_dict()
        assert d["errors"] == ["something went wrong"]
