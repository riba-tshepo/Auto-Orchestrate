#!/usr/bin/env python3
"""
Coverage Analyzer - Parses and analyzes test coverage reports.

Supports Cobertura XML, LCOV, and coverage.py formats.

Usage:
    coverage_analyzer.py [-o json|human|table] [--format cobertura|lcov|coverage_py] [--threshold PCT] COVERAGE_FILE

Examples:
    coverage_analyzer.py coverage.xml
    coverage_analyzer.py --format lcov coverage.info
    coverage_analyzer.py --threshold 80 .coverage
"""

import argparse
import re
import sqlite3
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Add shared library to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "_shared" / "python"))

from layer0 import EXIT_ERROR, EXIT_FILE_NOT_FOUND, EXIT_SUCCESS
from layer1 import OutputFormat, emit_error, emit_info, emit_warning, output


@dataclass
class FileCoverage:
    """Coverage data for a single file."""

    path: str
    lines_total: int = 0
    lines_covered: int = 0
    lines_missed: int = 0
    branches_total: int = 0
    branches_covered: int = 0
    functions_total: int = 0
    functions_covered: int = 0
    line_coverage_percent: float = 0.0
    branch_coverage_percent: float = 0.0

    def __post_init__(self):
        if self.lines_total > 0:
            self.line_coverage_percent = (self.lines_covered / self.lines_total) * 100
        if self.branches_total > 0:
            self.branch_coverage_percent = (self.branches_covered / self.branches_total) * 100

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "path": self.path,
            "lines": {
                "total": self.lines_total,
                "covered": self.lines_covered,
                "missed": self.lines_missed,
                "percent": round(self.line_coverage_percent, 2),
            },
            "branches": {
                "total": self.branches_total,
                "covered": self.branches_covered,
                "percent": round(self.branch_coverage_percent, 2),
            },
            "functions": {
                "total": self.functions_total,
                "covered": self.functions_covered,
            },
        }


@dataclass
class CoverageReport:
    """Full coverage report."""

    source_file: str
    format_type: str
    files: list[FileCoverage] = field(default_factory=list)
    threshold: float = 0.0
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        total_lines = sum(f.lines_total for f in self.files)
        covered_lines = sum(f.lines_covered for f in self.files)
        total_branches = sum(f.branches_total for f in self.files)
        covered_branches = sum(f.branches_covered for f in self.files)

        line_percent = (covered_lines / total_lines * 100) if total_lines > 0 else 0
        branch_percent = (covered_branches / total_branches * 100) if total_branches > 0 else 0

        # Group by directory
        by_directory: dict[str, dict] = {}
        for f in self.files:
            dir_path = str(Path(f.path).parent)
            if dir_path not in by_directory:
                by_directory[dir_path] = {
                    "files": 0,
                    "lines_total": 0,
                    "lines_covered": 0,
                }
            by_directory[dir_path]["files"] += 1
            by_directory[dir_path]["lines_total"] += f.lines_total
            by_directory[dir_path]["lines_covered"] += f.lines_covered

        # Calculate directory percentages
        for dir_data in by_directory.values():
            if dir_data["lines_total"] > 0:
                dir_data["percent"] = round(
                    dir_data["lines_covered"] / dir_data["lines_total"] * 100, 2
                )
            else:
                dir_data["percent"] = 0.0

        return {
            "source_file": self.source_file,
            "format": self.format_type,
            "summary": {
                "files_count": len(self.files),
                "lines_total": total_lines,
                "lines_covered": covered_lines,
                "line_coverage_percent": round(line_percent, 2),
                "branches_total": total_branches,
                "branches_covered": covered_branches,
                "branch_coverage_percent": round(branch_percent, 2),
                "meets_threshold": line_percent >= self.threshold,
                "threshold": self.threshold,
            },
            "by_directory": by_directory,
            "files": [f.to_dict() for f in self.files],
            "errors": self.errors if self.errors else None,
        }


def detect_format(path: Path) -> str:
    """
    Detect coverage file format.

    Args:
        path: Path to coverage file

    Returns:
        Format string
    """
    name = path.name.lower()
    suffix = path.suffix.lower()

    if name == ".coverage" or suffix == ".sqlite3":
        return "coverage_py"
    elif suffix == ".xml":
        return "cobertura"
    elif suffix in (".info", ".lcov"):
        return "lcov"
    elif suffix == ".json":
        return "json"
    else:
        # Try to detect from content
        try:
            content = path.read_bytes()[:1000]
            if b"<?xml" in content and b"coverage" in content.lower():
                return "cobertura"
            if b"SF:" in content:
                return "lcov"
        except Exception:
            pass
        return "unknown"


def parse_cobertura_xml(path: Path) -> CoverageReport:
    """
    Parse Cobertura XML coverage format.

    Args:
        path: Path to coverage.xml

    Returns:
        CoverageReport
    """
    report = CoverageReport(source_file=str(path), format_type="cobertura")

    try:
        tree = ET.parse(path)
        root = tree.getroot()
    except Exception as e:
        report.errors.append(f"Failed to parse XML: {e}")
        return report

    for package in root.findall(".//package"):
        for cls in package.findall(".//class"):
            filename = cls.get("filename", "")

            lines_total = 0
            lines_covered = 0
            branches_total = 0
            branches_covered = 0

            for line in cls.findall(".//line"):
                lines_total += 1
                hits = int(line.get("hits", 0))
                if hits > 0:
                    lines_covered += 1

                # Branch coverage
                if line.get("branch") == "true":
                    condition = line.get("condition-coverage", "")
                    match = re.match(r"(\d+)%\s*\((\d+)/(\d+)\)", condition)
                    if match:
                        branches_covered += int(match.group(2))
                        branches_total += int(match.group(3))

            report.files.append(
                FileCoverage(
                    path=filename,
                    lines_total=lines_total,
                    lines_covered=lines_covered,
                    lines_missed=lines_total - lines_covered,
                    branches_total=branches_total,
                    branches_covered=branches_covered,
                )
            )

    return report


def parse_lcov(path: Path) -> CoverageReport:
    """
    Parse LCOV coverage format.

    Args:
        path: Path to lcov.info

    Returns:
        CoverageReport
    """
    report = CoverageReport(source_file=str(path), format_type="lcov")

    try:
        content = path.read_text()
    except Exception as e:
        report.errors.append(f"Failed to read file: {e}")
        return report

    current_file = None
    lines_total = 0
    lines_covered = 0
    branches_total = 0
    branches_covered = 0
    functions_total = 0
    functions_covered = 0

    for line in content.splitlines():
        line = line.strip()

        if line.startswith("SF:"):
            # Start of new file
            if current_file:
                report.files.append(
                    FileCoverage(
                        path=current_file,
                        lines_total=lines_total,
                        lines_covered=lines_covered,
                        lines_missed=lines_total - lines_covered,
                        branches_total=branches_total,
                        branches_covered=branches_covered,
                        functions_total=functions_total,
                        functions_covered=functions_covered,
                    )
                )
            current_file = line[3:]
            lines_total = lines_covered = 0
            branches_total = branches_covered = 0
            functions_total = functions_covered = 0

        elif line.startswith("DA:"):
            # Line data
            parts = line[3:].split(",")
            if len(parts) >= 2:
                lines_total += 1
                if int(parts[1]) > 0:
                    lines_covered += 1

        elif line.startswith("BRDA:"):
            # Branch data
            parts = line[5:].split(",")
            if len(parts) >= 4:
                branches_total += 1
                if parts[3] != "-" and int(parts[3]) > 0:
                    branches_covered += 1

        elif line.startswith("FNF:"):
            functions_total = int(line[4:])
        elif line.startswith("FNH:"):
            functions_covered = int(line[4:])

        elif line == "end_of_record":
            if current_file:
                report.files.append(
                    FileCoverage(
                        path=current_file,
                        lines_total=lines_total,
                        lines_covered=lines_covered,
                        lines_missed=lines_total - lines_covered,
                        branches_total=branches_total,
                        branches_covered=branches_covered,
                        functions_total=functions_total,
                        functions_covered=functions_covered,
                    )
                )
            current_file = None

    return report


def parse_coverage_py(path: Path) -> CoverageReport:
    """
    Parse coverage.py SQLite database format.

    Args:
        path: Path to .coverage file

    Returns:
        CoverageReport
    """
    report = CoverageReport(source_file=str(path), format_type="coverage_py")

    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()

        # Get file data
        cursor.execute("SELECT id, path FROM file")
        files = {row[0]: row[1] for row in cursor.fetchall()}

        # Get line data
        cursor.execute("SELECT file_id, numbits FROM line_bits")
        line_data = cursor.fetchall()

        conn.close()

        for file_id, numbits in line_data:
            if file_id not in files:
                continue

            # Count bits (covered lines)
            lines_covered = bin(int.from_bytes(numbits, "little")).count("1")

            report.files.append(
                FileCoverage(
                    path=files[file_id],
                    lines_total=lines_covered,  # Approximate - would need source
                    lines_covered=lines_covered,
                    lines_missed=0,
                )
            )

    except Exception as e:
        report.errors.append(f"Failed to parse coverage.py database: {e}")

    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Parse and analyze test coverage reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  coverage_analyzer.py coverage.xml
  coverage_analyzer.py --format lcov coverage.info
  coverage_analyzer.py --threshold 80 .coverage
        """,
    )
    parser.add_argument(
        "coverage_file",
        help="Coverage report file",
    )
    parser.add_argument(
        "-o",
        "--output",
        choices=["json", "human", "table"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--format",
        choices=["cobertura", "lcov", "coverage_py", "auto"],
        default="auto",
        help="Coverage format (default: auto-detect)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.0,
        help="Coverage threshold percentage",
    )

    args = parser.parse_args()

    path = Path(args.coverage_file)
    if not path.exists():
        emit_error(EXIT_FILE_NOT_FOUND, f"File not found: {path}")
        return EXIT_FILE_NOT_FOUND

    # Detect or use specified format
    fmt = args.format if args.format != "auto" else detect_format(path)

    emit_info(f"Parsing {path} as {fmt} format...")

    # Parse based on format
    if fmt == "cobertura":
        report = parse_cobertura_xml(path)
    elif fmt == "lcov":
        report = parse_lcov(path)
    elif fmt == "coverage_py":
        report = parse_coverage_py(path)
    else:
        emit_error(EXIT_ERROR, f"Unknown format: {fmt}")
        return EXIT_ERROR

    report.threshold = args.threshold

    output_format = OutputFormat(args.output)
    output(report.to_dict(), output_format)

    summary = report.to_dict()["summary"]
    emit_info(
        f"Coverage: {summary['line_coverage_percent']}% "
        f"({summary['lines_covered']}/{summary['lines_total']} lines)"
    )

    if args.threshold > 0:
        if summary["meets_threshold"]:
            emit_info(f"Meets threshold of {args.threshold}%")
        else:
            emit_warning(f"Below threshold of {args.threshold}%")

    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
