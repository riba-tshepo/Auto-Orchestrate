#!/usr/bin/env python3
"""
Test Stub Generator - Generates test stubs for untested functions.

Creates test file skeletons based on coverage gap analysis.

Usage:
    test_stub_generator.py [--output-dir DIR] [--style pytest|unittest] [--overwrite] [--limit N] GAPS_JSON

Examples:
    test_stub_generator.py gaps.json
    test_stub_generator.py --output-dir tests/ --style pytest gaps.json
    test_stub_generator.py --limit 10 gaps.json
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Add shared library to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "_shared" / "python"))

from layer0 import EXIT_ERROR, EXIT_FILE_NOT_FOUND, EXIT_SUCCESS
from layer1 import OutputFormat, emit_error, emit_info, emit_warning, ensure_directory, output


@dataclass
class TestStub:
    """A generated test stub."""

    function_name: str
    test_name: str
    source_file: str
    test_file: str
    import_path: str
    content: str
    priority: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "function_name": self.function_name,
            "test_name": self.test_name,
            "source_file": self.source_file,
            "test_file": self.test_file,
            "import_path": self.import_path,
            "priority": self.priority,
        }


@dataclass
class GenerationReport:
    """Report of test stub generation."""

    gaps_file: str
    output_dir: str
    style: str
    stubs: list[TestStub] = field(default_factory=list)
    files_created: list[str] = field(default_factory=list)
    files_updated: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "gaps_file": self.gaps_file,
            "output_dir": self.output_dir,
            "style": self.style,
            "summary": {
                "stubs_generated": len(self.stubs),
                "files_created": len(self.files_created),
                "files_updated": len(self.files_updated),
                "skipped": len(self.skipped),
            },
            "stubs": [s.to_dict() for s in self.stubs],
            "files_created": self.files_created,
            "files_updated": self.files_updated,
            "skipped": self.skipped,
            "errors": self.errors if self.errors else None,
        }


def camel_case(name: str) -> str:
    """
    Convert snake_case to CamelCase.

    Args:
        name: Snake case name

    Returns:
        CamelCase name
    """
    parts = name.split("_")
    return "".join(part.capitalize() for part in parts if part)


def snake_case(name: str) -> str:
    """
    Ensure name is in snake_case.

    Args:
        name: Name to convert

    Returns:
        Snake case name
    """
    # Handle CamelCase
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def generate_import_path(source_file: str) -> str:
    """
    Generate Python import path from source file.

    Args:
        source_file: Path to source file

    Returns:
        Import path string
    """
    path = Path(source_file)

    # Remove .py extension
    parts = list(path.parts)
    if parts[-1].endswith(".py"):
        parts[-1] = parts[-1][:-3]

    # Remove common prefixes
    while parts and parts[0] in (".", "..", "src", "lib"):
        parts = parts[1:]

    return ".".join(parts)


def generate_test_filename(source_file: str) -> str:
    """
    Generate test filename from source file.

    Args:
        source_file: Path to source file

    Returns:
        Test filename
    """
    path = Path(source_file)
    name = path.stem

    if not name.startswith("test_"):
        name = f"test_{name}"

    return f"{name}.py"


def generate_stub_pytest(function_name: str, import_path: str, source_file: str) -> str:
    """
    Generate pytest-style test stub.

    Args:
        function_name: Name of function to test
        import_path: Import path for the function
        source_file: Source file path

    Returns:
        Test stub content
    """
    test_name = f"test_{snake_case(function_name)}"

    return f'''"""Tests for {function_name} from {source_file}."""

import pytest

from {import_path} import {function_name}


class Test{camel_case(function_name)}:
    """Tests for {function_name}."""

    def {test_name}_basic(self):
        """Test basic functionality of {function_name}."""
        # Arrange
        # TODO: Set up test data

        # Act
        # TODO: Call {function_name}

        # Assert
        # TODO: Add assertions
        pytest.skip("Test not implemented")

    def {test_name}_edge_case(self):
        """Test edge cases for {function_name}."""
        # TODO: Test edge cases
        pytest.skip("Test not implemented")

    def {test_name}_error_handling(self):
        """Test error handling in {function_name}."""
        # TODO: Test error cases
        pytest.skip("Test not implemented")
'''


def generate_stub_unittest(function_name: str, import_path: str, source_file: str) -> str:
    """
    Generate unittest-style test stub.

    Args:
        function_name: Name of function to test
        import_path: Import path for the function
        source_file: Source file path

    Returns:
        Test stub content
    """
    test_name = f"test_{snake_case(function_name)}"
    class_name = f"Test{camel_case(function_name)}"

    return f'''"""Tests for {function_name} from {source_file}."""

import unittest

from {import_path} import {function_name}


class {class_name}(unittest.TestCase):
    """Tests for {function_name}."""

    def setUp(self):
        """Set up test fixtures."""
        pass

    def tearDown(self):
        """Clean up after tests."""
        pass

    def {test_name}_basic(self):
        """Test basic functionality of {function_name}."""
        # Arrange
        # TODO: Set up test data

        # Act
        # TODO: Call {function_name}

        # Assert
        # TODO: Add assertions
        self.skipTest("Test not implemented")

    def {test_name}_edge_case(self):
        """Test edge cases for {function_name}."""
        # TODO: Test edge cases
        self.skipTest("Test not implemented")

    def {test_name}_error_handling(self):
        """Test error handling in {function_name}."""
        # TODO: Test error cases
        self.skipTest("Test not implemented")


if __name__ == "__main__":
    unittest.main()
'''


def generate_stub(gap: dict, style: str = "pytest") -> TestStub:
    """
    Generate a test stub for a coverage gap.

    Args:
        gap: Coverage gap dictionary
        style: Test framework style

    Returns:
        TestStub
    """
    function_name = gap.get("name", "unknown")
    source_file = gap.get("file", "")
    priority = gap.get("priority", 0)

    import_path = generate_import_path(source_file)
    test_file = generate_test_filename(source_file)
    test_name = f"test_{snake_case(function_name)}"

    if style == "pytest":
        content = generate_stub_pytest(function_name, import_path, source_file)
    else:
        content = generate_stub_unittest(function_name, import_path, source_file)

    return TestStub(
        function_name=function_name,
        test_name=test_name,
        source_file=source_file,
        test_file=test_file,
        import_path=import_path,
        content=content,
        priority=priority,
    )


def write_stubs(
    stubs: list[TestStub], output_dir: Path, overwrite: bool = False
) -> tuple[list[str], list[str], list[str]]:
    """
    Write test stubs to files.

    Args:
        stubs: List of test stubs
        output_dir: Output directory
        overwrite: Overwrite existing files

    Returns:
        Tuple of (created, updated, skipped) file lists
    """
    created = []
    updated = []
    skipped = []

    # Group stubs by test file
    stubs_by_file: dict[str, list[TestStub]] = {}
    for stub in stubs:
        if stub.test_file not in stubs_by_file:
            stubs_by_file[stub.test_file] = []
        stubs_by_file[stub.test_file].append(stub)

    for test_file, file_stubs in stubs_by_file.items():
        test_path = output_dir / test_file

        if test_path.exists() and not overwrite:
            skipped.append(str(test_path))
            continue

        # Combine stubs for this file
        content_parts = []
        for stub in file_stubs:
            content_parts.append(stub.content)

        # Write file
        ensure_directory(test_path.parent)
        test_path.write_text("\n\n".join(content_parts))

        if test_path.exists():
            updated.append(str(test_path))
        else:
            created.append(str(test_path))

    return created, updated, skipped


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate test stubs for untested functions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  test_stub_generator.py gaps.json
  test_stub_generator.py --output-dir tests/ --style pytest gaps.json
  test_stub_generator.py --limit 10 gaps.json
        """,
    )
    parser.add_argument(
        "gaps_json",
        help="Coverage gaps JSON file (from gap_detector)",
    )
    parser.add_argument(
        "--output-dir",
        default="tests",
        help="Output directory for test files (default: tests)",
    )
    parser.add_argument(
        "--style",
        choices=["pytest", "unittest"],
        default="pytest",
        help="Test framework style (default: pytest)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing test files",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Limit number of stubs to generate (0 = no limit)",
    )
    parser.add_argument(
        "-o",
        "--output",
        choices=["json", "human"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't write files, just show what would be generated",
    )

    args = parser.parse_args()

    gaps_path = Path(args.gaps_json)
    if not gaps_path.exists():
        emit_error(EXIT_FILE_NOT_FOUND, f"Gaps file not found: {gaps_path}")
        return EXIT_FILE_NOT_FOUND

    output_dir = Path(args.output_dir)

    emit_info(f"Generating test stubs from {gaps_path}...")

    try:
        data = json.loads(gaps_path.read_text())
    except json.JSONDecodeError as e:
        emit_error(EXIT_ERROR, f"Failed to parse JSON: {e}")
        return EXIT_ERROR

    # Extract gaps
    gaps = data.get("gaps", data.get("critical_gaps", []))
    if isinstance(data, list):
        gaps = data

    # Apply limit
    if args.limit > 0:
        gaps = gaps[: args.limit]

    report = GenerationReport(
        gaps_file=str(gaps_path),
        output_dir=str(output_dir),
        style=args.style,
    )

    # Generate stubs
    for gap in gaps:
        stub = generate_stub(gap, args.style)
        report.stubs.append(stub)

    # Write files unless dry run
    if not args.dry_run:
        created, updated, skipped = write_stubs(report.stubs, output_dir, args.overwrite)
        report.files_created = created
        report.files_updated = updated
        report.skipped = skipped

    output_format = OutputFormat(args.output)
    output(report.to_dict(), output_format)

    emit_info(
        f"Generated {len(report.stubs)} test stubs, created {len(report.files_created)} files"
    )

    if report.skipped:
        emit_warning(f"Skipped {len(report.skipped)} existing files (use --overwrite)")

    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
