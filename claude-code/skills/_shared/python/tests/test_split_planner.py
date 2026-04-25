"""
Unit tests for refactor-executor split_planner script.

Tests cover:
- Boundary dataclass construction and serialisation
- ProposedFile dataclass construction and serialisation
- ImportChange dataclass construction and serialisation
- SplitPlan dataclass construction and to_dict
- identify_logical_boundaries from analysis dicts
- group_by_responsibility function grouping
- build_dependency_graph function call parsing
- generate_split_plan integration (using analysis dict fixture)
- _identify_imports_needed helper
- estimate_new_files helper
- format_as_markdown output structure
"""

import sys
from pathlib import Path

import pytest

SKILLS_DIR = Path(__file__).resolve().parent.parent.parent.parent
SHARED_PYTHON_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SKILLS_DIR / "refactor-executor" / "scripts"

for _p in (str(SCRIPTS_DIR), str(SHARED_PYTHON_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from split_planner import (
        Boundary,
        ImportChange,
        ProposedFile,
        SplitPlan,
        _identify_imports_needed,
        build_dependency_graph,
        estimate_new_files,
        format_as_markdown,
        generate_split_plan,
        group_by_responsibility,
        identify_logical_boundaries,
    )
except ImportError as exc:
    pytest.skip(f"Cannot import split_planner: {exc}", allow_module_level=True)


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------


def _make_analysis(
    file_path: str = "module.py",
    functions: list[dict] | None = None,
    classes: list[dict] | None = None,
) -> dict:
    """Build a minimal analysis dict matching file_analyzer output."""
    if functions is None:
        functions = []
    if classes is None:
        classes = []
    return {
        "files": [
            {
                "path": file_path,
                "functions": functions,
                "classes": classes,
            }
        ]
    }


def _func(name: str, start: int = 1, end: int = 10) -> dict:
    return {"name": name, "line_start": start, "line_end": end, "lines": end - start + 1}


def _cls(name: str, start: int = 1, end: int = 30) -> dict:
    return {"name": name, "line_start": start, "line_end": end, "lines": end - start + 1}


# ---------------------------------------------------------------------------
# Boundary dataclass
# ---------------------------------------------------------------------------


class TestBoundaryDataclass:
    """Tests for Boundary to_dict."""

    def test_to_dict_keys(self):
        b = Boundary(
            start_line=1, end_line=50,
            boundary_type="class", name="MyClass",
            reason="Class definition forms a natural module boundary",
        )
        d = b.to_dict()
        assert set(d.keys()) == {"start_line", "end_line", "type", "name", "reason"}

    def test_to_dict_values(self):
        b = Boundary(
            start_line=5, end_line=30,
            boundary_type="function_group", name="parse_* functions",
            reason="Group of 3 related functions",
        )
        d = b.to_dict()
        assert d["start_line"] == 5
        assert d["end_line"] == 30
        assert d["type"] == "function_group"
        assert d["name"] == "parse_* functions"


# ---------------------------------------------------------------------------
# ProposedFile dataclass
# ---------------------------------------------------------------------------


class TestProposedFileDataclass:
    """Tests for ProposedFile to_dict."""

    def _make(self, **kwargs) -> ProposedFile:
        defaults = dict(
            name="module_parser.py",
            functions=["parse_header", "parse_body"],
            classes=[],
            estimated_lines=120,
            imports_needed=["re"],
            description="Group 2 parsing functions",
        )
        defaults.update(kwargs)
        return ProposedFile(**defaults)

    def test_to_dict_keys(self):
        d = self._make().to_dict()
        assert set(d.keys()) == {
            "name", "functions", "classes", "estimated_lines",
            "imports_needed", "description",
        }

    def test_to_dict_values(self):
        pf = self._make(name="out.py", estimated_lines=200)
        d = pf.to_dict()
        assert d["name"] == "out.py"
        assert d["estimated_lines"] == 200


# ---------------------------------------------------------------------------
# ImportChange dataclass
# ---------------------------------------------------------------------------


class TestImportChangeDataclass:
    """Tests for ImportChange to_dict."""

    def test_to_dict_keys(self):
        ic = ImportChange(
            affected_file="<files importing from module>",
            old_import="from module import parse_header",
            new_import="from module_parser import parse_header",
        )
        d = ic.to_dict()
        assert set(d.keys()) == {"affected_file", "old_import", "new_import"}

    def test_to_dict_values(self):
        ic = ImportChange(
            affected_file="caller.py",
            old_import="from big import foo",
            new_import="from small import foo",
        )
        d = ic.to_dict()
        assert d["affected_file"] == "caller.py"
        assert "big" in d["old_import"]
        assert "small" in d["new_import"]


# ---------------------------------------------------------------------------
# SplitPlan dataclass
# ---------------------------------------------------------------------------


class TestSplitPlanDataclass:
    """Tests for SplitPlan to_dict structure."""

    def test_to_dict_keys(self):
        plan = SplitPlan(original_file="module.py")
        d = plan.to_dict()
        assert "original_file" in d
        assert "summary" in d
        assert "boundaries" in d
        assert "proposed_files" in d
        assert "import_changes" in d
        assert "dependency_graph" in d

    def test_to_dict_summary_keys(self):
        plan = SplitPlan(original_file="module.py")
        summary = plan.to_dict()["summary"]
        assert "proposed_files" in summary
        assert "total_estimated_lines" in summary
        assert "boundaries_identified" in summary

    def test_warnings_none_when_empty(self):
        plan = SplitPlan(original_file="module.py")
        d = plan.to_dict()
        assert d["warnings"] is None

    def test_warnings_present_when_not_empty(self):
        plan = SplitPlan(original_file="module.py", warnings=["circular dep"])
        d = plan.to_dict()
        assert d["warnings"] == ["circular dep"]


# ---------------------------------------------------------------------------
# identify_logical_boundaries
# ---------------------------------------------------------------------------


class TestIdentifyLogicalBoundaries:
    """Tests for boundary identification from analysis dict."""

    def test_returns_list(self):
        analysis = _make_analysis()
        result = identify_logical_boundaries(analysis)
        assert isinstance(result, list)

    def test_empty_files_returns_empty(self):
        result = identify_logical_boundaries({"files": []})
        assert result == []

    def test_class_creates_boundary(self):
        analysis = _make_analysis(classes=[_cls("MyClass", 1, 30)])
        boundaries = identify_logical_boundaries(analysis)
        types = [b.boundary_type for b in boundaries]
        assert "class" in types

    def test_function_group_creates_boundary(self):
        """Multiple functions sharing a prefix should create a function_group boundary."""
        funcs = [
            _func("parse_header", 1, 10),
            _func("parse_body", 11, 20),
            _func("parse_footer", 21, 30),
        ]
        analysis = _make_analysis(functions=funcs)
        boundaries = identify_logical_boundaries(analysis)
        types = [b.boundary_type for b in boundaries]
        assert "function_group" in types

    def test_boundaries_sorted_by_start_line(self):
        funcs = [
            _func("parse_header", 50, 60),
            _func("parse_body", 10, 20),
        ]
        analysis = _make_analysis(functions=funcs)
        boundaries = identify_logical_boundaries(analysis)
        starts = [b.start_line for b in boundaries]
        assert starts == sorted(starts)

    def test_single_function_not_grouped(self):
        """A single function with a unique prefix should not form a function_group boundary."""
        funcs = [_func("unique_function", 1, 10)]
        analysis = _make_analysis(functions=funcs)
        boundaries = identify_logical_boundaries(analysis)
        types = [b.boundary_type for b in boundaries]
        assert "function_group" not in types


# ---------------------------------------------------------------------------
# group_by_responsibility
# ---------------------------------------------------------------------------


class TestGroupByResponsibility:
    """Tests for function responsibility grouping."""

    def test_returns_dict(self):
        funcs = [_func("parse_x"), _func("validate_y")]
        result = group_by_responsibility(funcs)
        assert isinstance(result, dict)

    def test_parse_prefix_maps_to_parsing(self):
        funcs = [_func("parse_header"), _func("parse_body")]
        groups = group_by_responsibility(funcs)
        assert "parsing" in groups
        assert "parse_header" in groups["parsing"]

    def test_validate_prefix_maps_to_validation(self):
        funcs = [_func("validate_input"), _func("validate_output")]
        groups = group_by_responsibility(funcs)
        assert "validation" in groups

    def test_unknown_prefix_goes_to_misc(self):
        funcs = [_func("zylophone_function")]
        groups = group_by_responsibility(funcs)
        assert "misc" in groups

    def test_load_prefix_maps_to_io(self):
        funcs = [_func("load_config")]
        groups = group_by_responsibility(funcs)
        assert "io" in groups


# ---------------------------------------------------------------------------
# build_dependency_graph
# ---------------------------------------------------------------------------


class TestBuildDependencyGraph:
    """Tests for dependency graph extraction from source code."""

    def test_returns_dict(self):
        source = "def foo():\n    pass\n"
        result = build_dependency_graph(source)
        assert isinstance(result, dict)

    def test_independent_functions_have_empty_deps(self):
        source = "def foo():\n    x = 1\n\ndef bar():\n    y = 2\n"
        graph = build_dependency_graph(source)
        assert graph.get("foo", []) == []
        assert graph.get("bar", []) == []

    def test_detects_call_within_function(self):
        source = (
            "def helper():\n"
            "    return 1\n"
            "\n"
            "def main():\n"
            "    result = helper()\n"
            "    return result\n"
        )
        graph = build_dependency_graph(source)
        assert "helper" in graph.get("main", [])

    def test_no_self_references(self):
        source = "def recursive():\n    return recursive()\n"
        graph = build_dependency_graph(source)
        assert "recursive" not in graph.get("recursive", [])

    def test_empty_source_returns_empty_dict(self):
        assert build_dependency_graph("") == {}


# ---------------------------------------------------------------------------
# generate_split_plan integration
# ---------------------------------------------------------------------------


class TestGenerateSplitPlan:
    """Integration tests for generate_split_plan."""

    def test_returns_split_plan(self):
        analysis = _make_analysis()
        plan = generate_split_plan(analysis, min_size=10)
        assert isinstance(plan, SplitPlan)

    def test_empty_files_returns_unknown_original_file(self):
        plan = generate_split_plan({"files": []}, min_size=10)
        assert plan.original_file == "unknown"

    def test_class_above_min_size_creates_proposed_file(self):
        analysis = _make_analysis(
            file_path="module.py",
            classes=[_cls("BigClass", 1, 100)],
        )
        plan = generate_split_plan(analysis, min_size=50)
        assert len(plan.proposed_files) >= 1
        names = [pf.name for pf in plan.proposed_files]
        assert any("bigclass" in n for n in names)

    def test_class_below_min_size_not_proposed(self):
        analysis = _make_analysis(
            file_path="module.py",
            classes=[_cls("TinyClass", 1, 10)],
        )
        plan = generate_split_plan(analysis, min_size=50)
        class_proposals = [pf for pf in plan.proposed_files if "tinyclass" in pf.name]
        assert len(class_proposals) == 0


# ---------------------------------------------------------------------------
# _identify_imports_needed
# ---------------------------------------------------------------------------


class TestIdentifyImportsNeeded:
    """Tests for import dependency helper."""

    def test_no_deps_returns_empty(self):
        result = _identify_imports_needed(["foo"], {"foo": []})
        assert result == []

    def test_internal_dep_not_included(self):
        """If dep is within the same proposed module, no import needed."""
        result = _identify_imports_needed(["foo", "bar"], {"foo": ["bar"]})
        assert result == []

    def test_external_dep_included(self):
        """If dep is outside the proposed module, it should appear in imports."""
        result = _identify_imports_needed(["foo"], {"foo": ["external_util"]})
        assert "external_util" in result

    def test_result_is_sorted(self):
        result = _identify_imports_needed(
            ["foo"],
            {"foo": ["zebra_util", "alpha_util", "mid_util"]}
        )
        assert result == sorted(result)


# ---------------------------------------------------------------------------
# estimate_new_files
# ---------------------------------------------------------------------------


class TestEstimateNewFiles:
    """Tests for estimate_new_files helper."""

    def test_returns_proposed_files_list(self):
        plan = SplitPlan(
            original_file="module.py",
            proposed_files=[
                ProposedFile(
                    name="module_a.py", functions=["f1"], classes=[],
                    estimated_lines=50, imports_needed=[], description="desc"
                )
            ],
        )
        result = estimate_new_files(plan)
        assert result is plan.proposed_files
        assert len(result) == 1

    def test_returns_empty_list_when_no_proposed_files(self):
        plan = SplitPlan(original_file="module.py")
        result = estimate_new_files(plan)
        assert result == []


# ---------------------------------------------------------------------------
# format_as_markdown
# ---------------------------------------------------------------------------


class TestFormatAsMarkdown:
    """Tests for markdown format output."""

    def test_returns_string(self):
        plan = SplitPlan(original_file="module.py")
        result = format_as_markdown(plan)
        assert isinstance(result, str)

    def test_contains_original_file_name(self):
        plan = SplitPlan(original_file="my_module.py")
        result = format_as_markdown(plan)
        assert "my_module.py" in result

    def test_contains_heading(self):
        plan = SplitPlan(original_file="module.py")
        result = format_as_markdown(plan)
        assert result.startswith("# Split Plan")

    def test_includes_warnings_section_when_warnings_present(self):
        plan = SplitPlan(
            original_file="module.py",
            warnings=["circular dependency detected"],
        )
        result = format_as_markdown(plan)
        assert "Warnings" in result
        assert "circular dependency detected" in result

    def test_no_warnings_section_when_no_warnings(self):
        plan = SplitPlan(original_file="module.py")
        result = format_as_markdown(plan)
        assert "## Warnings" not in result

    def test_includes_proposed_files_section(self):
        plan = SplitPlan(
            original_file="module.py",
            proposed_files=[
                ProposedFile(
                    name="module_parser.py",
                    functions=["parse_x"],
                    classes=[],
                    estimated_lines=100,
                    imports_needed=[],
                    description="Parsing functions",
                )
            ],
        )
        result = format_as_markdown(plan)
        assert "module_parser.py" in result
        assert "Parsing functions" in result
