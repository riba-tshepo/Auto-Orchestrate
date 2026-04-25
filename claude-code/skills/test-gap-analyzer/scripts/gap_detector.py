#!/usr/bin/env python3
"""
Gap Detector - Detects test coverage gaps.

Identifies untested functions and prioritizes by complexity.

Usage:
    gap_detector.py [-o json|human|table] [--complexity-threshold N] [--priority complexity|lines|risk] COVERAGE_JSON SOURCE_DIR

Examples:
    gap_detector.py coverage.json src/
    gap_detector.py --complexity-threshold 5 coverage.json project/
    gap_detector.py --priority risk coverage.json src/
"""

import argparse
import ast
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Add shared library to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "_shared" / "python"))

from layer0 import EXIT_ERROR, EXIT_FILE_NOT_FOUND, EXIT_SUCCESS
from layer1 import OutputFormat, emit_error, emit_info, emit_warning, glob_files, output


@dataclass
class FunctionInfo:
    """Information about a function."""

    name: str
    file: str
    line: int
    end_line: int
    complexity: int = 1
    lines_of_code: int = 0
    is_covered: bool = False
    coverage_percent: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "file": self.file,
            "line": self.line,
            "end_line": self.end_line,
            "complexity": self.complexity,
            "lines_of_code": self.lines_of_code,
            "is_covered": self.is_covered,
            "coverage_percent": round(self.coverage_percent, 2),
        }


@dataclass
class CoverageGap:
    """A coverage gap (untested function)."""

    function: FunctionInfo
    priority: int
    risk_score: float
    reason: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            **self.function.to_dict(),
            "priority": self.priority,
            "risk_score": round(self.risk_score, 2),
            "reason": self.reason,
        }


@dataclass
class GapReport:
    """Report of coverage gaps."""

    coverage_file: str
    source_dir: str
    gaps: list[CoverageGap] = field(default_factory=list)
    critical_gaps: list[CoverageGap] = field(default_factory=list)
    total_functions: int = 0
    covered_functions: int = 0
    coverage_percent: float = 0.0
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "coverage_file": self.coverage_file,
            "source_dir": self.source_dir,
            "summary": {
                "total_functions": self.total_functions,
                "covered_functions": self.covered_functions,
                "uncovered_functions": len(self.gaps),
                "coverage_percent": round(self.coverage_percent, 2),
                "critical_gaps": len(self.critical_gaps),
            },
            "critical_gaps": [g.to_dict() for g in self.critical_gaps],
            "gaps": [g.to_dict() for g in self.gaps],
            "errors": self.errors if self.errors else None,
        }


class ComplexityVisitor(ast.NodeVisitor):
    """AST visitor to calculate cyclomatic complexity."""

    def __init__(self):
        self.complexity = 1  # Base complexity

    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_With(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        # and/or adds complexity
        self.complexity += len(node.values) - 1
        self.generic_visit(node)

    def visit_comprehension(self, node):
        self.complexity += 1
        self.generic_visit(node)


def calculate_complexity(func_node: ast.FunctionDef) -> int:
    """
    Calculate cyclomatic complexity of a function.

    Args:
        func_node: AST function node

    Returns:
        Complexity score
    """
    visitor = ComplexityVisitor()
    visitor.visit(func_node)
    return visitor.complexity


def extract_functions(source_dir: Path) -> list[FunctionInfo]:
    """
    Extract all functions from Python source files.

    Args:
        source_dir: Source directory

    Returns:
        List of FunctionInfo
    """
    functions = []

    for file_path in glob_files(source_dir, "*.py", recursive=True):
        try:
            content = file_path.read_text()
            tree = ast.parse(content)
        except Exception:
            continue

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Calculate complexity
                complexity = calculate_complexity(node)

                # Calculate lines of code
                end_line = getattr(node, "end_lineno", node.lineno)
                lines_of_code = end_line - node.lineno + 1

                functions.append(
                    FunctionInfo(
                        name=node.name,
                        file=str(file_path),
                        line=node.lineno,
                        end_line=end_line,
                        complexity=complexity,
                        lines_of_code=lines_of_code,
                    )
                )

    return functions


def load_coverage_data(coverage_file: Path) -> dict[str, dict]:
    """
    Load coverage data from JSON file.

    Args:
        coverage_file: Path to coverage JSON

    Returns:
        Dictionary mapping file path to coverage info
    """
    data = json.loads(coverage_file.read_text())

    coverage_map = {}

    # Handle different coverage formats
    if "files" in data:
        for file_info in data["files"]:
            if isinstance(file_info, dict):
                path = file_info.get("path", "")
                coverage_map[path] = {
                    "covered_lines": set(
                        range(1, file_info.get("lines", {}).get("covered", 0) + 1)
                    ),
                    "percent": file_info.get("lines", {}).get("percent", 0),
                }

    return coverage_map


def match_to_coverage(
    functions: list[FunctionInfo], coverage_map: dict[str, dict]
) -> list[FunctionInfo]:
    """
    Match functions to coverage data.

    Args:
        functions: List of functions
        coverage_map: Coverage data by file

    Returns:
        Updated function list with coverage info
    """
    for func in functions:
        file_coverage = None

        # Try to match file path
        for covered_file in coverage_map:
            if covered_file in func.file or func.file in covered_file:
                file_coverage = coverage_map[covered_file]
                break

        if file_coverage:
            covered_lines = file_coverage.get("covered_lines", set())
            func_lines = set(range(func.line, func.end_line + 1))

            if func_lines & covered_lines:
                func.is_covered = True
                overlap = len(func_lines & covered_lines)
                func.coverage_percent = (overlap / len(func_lines)) * 100

    return functions


def detect_gaps(
    functions: list[FunctionInfo], complexity_threshold: int = 5, priority_mode: str = "complexity"
) -> GapReport:
    """
    Detect coverage gaps and prioritize.

    Args:
        functions: List of functions with coverage info
        complexity_threshold: Threshold for high complexity
        priority_mode: How to prioritize gaps

    Returns:
        GapReport
    """
    report = GapReport(
        coverage_file="",
        source_dir="",
        total_functions=len(functions),
        covered_functions=sum(1 for f in functions if f.is_covered),
    )

    if report.total_functions > 0:
        report.coverage_percent = (report.covered_functions / report.total_functions) * 100

    # Find uncovered functions
    uncovered = [f for f in functions if not f.is_covered]

    for func in uncovered:
        # Calculate risk score
        risk_score = func.complexity * (func.lines_of_code / 10)

        # Determine priority based on mode
        if priority_mode == "complexity":
            priority = 1 if func.complexity > complexity_threshold else 2
        elif priority_mode == "lines":
            priority = 1 if func.lines_of_code > 50 else 2
        else:  # risk
            priority = 1 if risk_score > 10 else 2

        # Generate reason
        reasons = []
        if func.complexity > complexity_threshold:
            reasons.append(f"high complexity ({func.complexity})")
        if func.lines_of_code > 50:
            reasons.append(f"large function ({func.lines_of_code} lines)")
        if not reasons:
            reasons.append("no test coverage")

        gap = CoverageGap(
            function=func,
            priority=priority,
            risk_score=risk_score,
            reason=", ".join(reasons),
        )

        report.gaps.append(gap)

        if priority == 1:
            report.critical_gaps.append(gap)

    # Sort gaps by priority and risk
    report.gaps.sort(key=lambda g: (g.priority, -g.risk_score))
    report.critical_gaps.sort(key=lambda g: -g.risk_score)

    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect test coverage gaps and prioritize by risk",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  gap_detector.py coverage.json src/
  gap_detector.py --complexity-threshold 5 coverage.json project/
  gap_detector.py --priority risk coverage.json src/
        """,
    )
    parser.add_argument(
        "coverage_json",
        help="Coverage report JSON file",
    )
    parser.add_argument(
        "source_dir",
        help="Source directory to analyze",
    )
    parser.add_argument(
        "-o",
        "--output",
        choices=["json", "human", "table"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--complexity-threshold",
        type=int,
        default=5,
        help="Complexity threshold for critical gaps (default: 5)",
    )
    parser.add_argument(
        "--priority",
        choices=["complexity", "lines", "risk"],
        default="complexity",
        help="Priority mode (default: complexity)",
    )

    args = parser.parse_args()

    coverage_path = Path(args.coverage_json)
    source_path = Path(args.source_dir)

    if not coverage_path.exists():
        emit_error(EXIT_FILE_NOT_FOUND, f"Coverage file not found: {coverage_path}")
        return EXIT_FILE_NOT_FOUND

    if not source_path.exists():
        emit_error(EXIT_FILE_NOT_FOUND, f"Source directory not found: {source_path}")
        return EXIT_FILE_NOT_FOUND

    emit_info(f"Analyzing coverage gaps in {source_path}...")

    # Extract functions
    functions = extract_functions(source_path)
    emit_info(f"Found {len(functions)} functions")

    # Load coverage data
    try:
        coverage_map = load_coverage_data(coverage_path)
    except Exception as e:
        emit_error(EXIT_ERROR, f"Failed to load coverage: {e}")
        return EXIT_ERROR

    # Match coverage
    functions = match_to_coverage(functions, coverage_map)

    # Detect gaps
    report = detect_gaps(functions, args.complexity_threshold, args.priority)
    report.coverage_file = str(coverage_path)
    report.source_dir = str(source_path)

    output_format = OutputFormat(args.output)
    output(report.to_dict(), output_format)

    emit_info(
        f"Coverage: {report.coverage_percent:.1f}% "
        f"({report.covered_functions}/{report.total_functions} functions)"
    )

    if report.critical_gaps:
        emit_warning(f"Critical gaps: {len(report.critical_gaps)}")

    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
