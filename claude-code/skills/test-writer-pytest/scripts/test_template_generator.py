#!/usr/bin/env python3
"""
Test Template Generator - Generates pytest test templates.

Creates test file templates based on function discovery output,
with support for fixtures and parametrization.

Usage:
    test_template_generator.py [--output-dir DIR] [--fixture-file FILE] [--parametrize] DISCOVERY_JSON

Examples:
    test_template_generator.py functions.json
    test_template_generator.py --output-dir tests/ discovery.json
    test_template_generator.py --parametrize --fixture-file conftest.py functions.json
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
from layer1 import OutputFormat, emit_error, emit_info, output, safe_write


@dataclass
class TestTemplate:
    """A generated test template."""

    function_name: str
    test_name: str
    content: str
    is_parametrized: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "function_name": self.function_name,
            "test_name": self.test_name,
            "is_parametrized": self.is_parametrized,
        }


@dataclass
class TestFile:
    """A generated test file."""

    path: str
    module_name: str
    templates: list[TestTemplate] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    fixtures_used: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "path": self.path,
            "module_name": self.module_name,
            "test_count": len(self.templates),
            "templates": [t.to_dict() for t in self.templates],
            "imports": self.imports,
            "fixtures_used": self.fixtures_used,
        }

    def generate_content(self) -> str:
        """Generate the full test file content."""
        lines = [
            '"""',
            f"Tests for {self.module_name} module.",
            "",
            "Auto-generated test templates - fill in the test implementations.",
            '"""',
            "",
            "import pytest",
        ]

        # Add imports
        for imp in self.imports:
            lines.append(imp)

        lines.append("")
        lines.append("")

        # Add test templates
        for template in self.templates:
            lines.append(template.content)
            lines.append("")

        return "\n".join(lines)


@dataclass
class GenerationReport:
    """Report containing generation results."""

    source_file: str
    templates_generated: int
    files_created: list[TestFile] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source_file": self.source_file,
            "summary": {
                "templates_generated": self.templates_generated,
                "files_created": len(self.files_created),
                "functions_skipped": len(self.skipped),
            },
            "files": [f.to_dict() for f in self.files_created],
            "skipped": self.skipped if self.skipped else None,
        }


def parse_fixture_file(fixture_path: Path | None) -> list[str]:
    """
    Parse fixture file to find available fixtures.

    Args:
        fixture_path: Path to conftest.py or fixture file

    Returns:
        List of fixture names
    """
    if fixture_path is None or not fixture_path.exists():
        return []

    try:
        content = fixture_path.read_text(encoding="utf-8")
    except Exception:
        return []

    fixtures: list[str] = []

    # Find @pytest.fixture decorated functions
    pattern = r"@pytest\.fixture[^\n]*\n(?:@[^\n]+\n)*def\s+(\w+)\s*\("
    for match in re.finditer(pattern, content):
        fixtures.append(match.group(1))

    return fixtures


def generate_fixture_imports(fixture_file: Path | None) -> str:
    """
    Generate import statement for fixtures.

    Args:
        fixture_file: Path to fixture file

    Returns:
        Import statement or empty string
    """
    if fixture_file is None:
        return ""

    # Fixtures from conftest.py are auto-discovered
    if fixture_file.name == "conftest.py":
        return ""

    module_name = fixture_file.stem
    return f"from {module_name} import *"


def generate_test_method(
    func_info: dict[str, Any], parametrize: bool, available_fixtures: list[str]
) -> TestTemplate:
    """
    Generate a test method for a function.

    Args:
        func_info: Function information dictionary
        parametrize: Whether to generate parametrized test
        available_fixtures: List of available fixture names

    Returns:
        TestTemplate
    """
    func_name = func_info.get("name", "unknown")
    is_async = func_info.get("is_async", False)
    signature = func_info.get("signature", {})
    parameters = signature.get("parameters", [])
    return_type = signature.get("return_type")
    docstring = func_info.get("docstring", "")

    # Generate test name
    test_name = f"test_{func_name}"

    # Determine what fixtures might be useful
    fixtures_to_use = []
    for param in parameters:
        param_name = param.get("name", "").lstrip("*")
        if param_name in available_fixtures:
            fixtures_to_use.append(param_name)

    # Build parameter list for test function
    test_params = fixtures_to_use.copy()

    lines = []

    # Add parametrize decorator if requested
    if parametrize and parameters:
        # Filter out self, cls, and fixture params
        test_input_params = [
            p
            for p in parameters
            if p.get("name") not in ("self", "cls", "*args", "**kwargs")
            and p.get("name") not in fixtures_to_use
        ]

        if test_input_params:
            param_names = [p.get("name", "x") for p in test_input_params[:2]]
            lines.append(f'@pytest.mark.parametrize("{", ".join(param_names)}", [')
            lines.append("    # Add test cases here")

            # Generate example based on types
            example_values = []
            for param in test_input_params[:2]:
                annotation = param.get("annotation", "")
                if "int" in annotation.lower():
                    example_values.append("1")
                elif "str" in annotation.lower():
                    example_values.append('"example"')
                elif "bool" in annotation.lower():
                    example_values.append("True")
                elif "list" in annotation.lower():
                    example_values.append("[]")
                elif "dict" in annotation.lower():
                    example_values.append("{}")
                else:
                    example_values.append("None")

            if len(example_values) == 1:
                lines.append(f"    ({example_values[0]},),")
            else:
                lines.append(f"    ({', '.join(example_values)}),")

            lines.append("])")
            test_params.extend(param_names)

    # Build function signature
    async_prefix = "async " if is_async else ""
    param_str = ", ".join(test_params) if test_params else ""

    lines.append(f"{async_prefix}def {test_name}({param_str}):")

    # Add docstring
    if docstring:
        short_doc = docstring.split("\n")[0][:60]
        lines.append(f'    """Test {func_name}: {short_doc}..."""')
    else:
        lines.append(f'    """Test {func_name} function."""')

    # Add test body
    lines.append("    # Arrange")
    lines.append("    # TODO: Set up test data")
    lines.append("    ")
    lines.append("    # Act")

    if is_async:
        lines.append(f"    # result = await {func_name}(...)")
    else:
        lines.append(f"    # result = {func_name}(...)")

    lines.append("    ")
    lines.append("    # Assert")

    if return_type == "bool":
        lines.append("    # assert result is True")
    elif return_type == "None" or return_type is None:
        lines.append("    # assert result is None")
    elif return_type and "list" in return_type.lower():
        lines.append("    # assert isinstance(result, list)")
        lines.append("    # assert len(result) > 0")
    elif return_type and "dict" in return_type.lower():
        lines.append("    # assert isinstance(result, dict)")
    else:
        lines.append("    # assert result == expected")

    lines.append("    pytest.skip('Test not implemented')")

    return TestTemplate(
        function_name=func_name,
        test_name=test_name,
        content="\n".join(lines),
        is_parametrized=parametrize and bool(parameters),
    )


def generate_test_class(
    class_name: str, methods: list[dict[str, Any]], parametrize: bool, available_fixtures: list[str]
) -> str:
    """
    Generate a test class for a source class.

    Args:
        class_name: Name of the class being tested
        methods: List of method info dictionaries
        parametrize: Whether to generate parametrized tests
        available_fixtures: List of available fixture names

    Returns:
        Test class code as string
    """
    lines = [
        f"class Test{class_name}:",
        f'    """Tests for {class_name} class."""',
        "",
    ]

    for method in methods:
        if method.get("name", "").startswith("_"):
            continue

        template = generate_test_method(method, parametrize, available_fixtures)
        # Indent the method content
        indented = "\n".join("    " + line for line in template.content.split("\n"))
        lines.append(indented)
        lines.append("")

    return "\n".join(lines)


def generate_test_file(
    module_functions: list[dict[str, Any]],
    module_name: str,
    output_dir: Path,
    parametrize: bool,
    available_fixtures: list[str],
) -> TestFile:
    """
    Generate a test file for a module.

    Args:
        module_functions: Functions from one module
        module_name: Name of the source module
        output_dir: Output directory for test files
        parametrize: Whether to generate parametrized tests
        available_fixtures: List of available fixture names

    Returns:
        TestFile
    """
    test_file_name = f"test_{module_name}.py"
    test_file_path = output_dir / test_file_name

    test_file = TestFile(
        path=str(test_file_path),
        module_name=module_name,
        fixtures_used=available_fixtures,
    )

    # Add import for the module being tested
    test_file.imports.append(f"from {module_name} import *")

    # Group functions by class
    standalone_functions: list[dict] = []
    class_methods: dict[str, list[dict]] = {}

    for func in module_functions:
        if func.get("is_method") and func.get("class_name"):
            class_name = func["class_name"]
            if class_name not in class_methods:
                class_methods[class_name] = []
            class_methods[class_name].append(func)
        else:
            standalone_functions.append(func)

    # Generate tests for standalone functions
    for func in standalone_functions:
        # Skip private functions
        if func.get("name", "").startswith("_"):
            continue

        template = generate_test_method(func, parametrize, available_fixtures)
        test_file.templates.append(template)

    # Generate test classes for classes
    for class_name, methods in class_methods.items():
        class_content = generate_test_class(class_name, methods, parametrize, available_fixtures)
        test_file.templates.append(
            TestTemplate(
                function_name=class_name,
                test_name=f"Test{class_name}",
                content=class_content,
                is_parametrized=parametrize,
            )
        )

    return test_file


def generate_all(
    discovery_data: dict[str, Any],
    output_dir: Path,
    fixture_file: Path | None,
    parametrize: bool,
    write_files: bool,
) -> GenerationReport:
    """
    Generate test templates for all discovered functions.

    Args:
        discovery_data: Output from function_discoverer
        output_dir: Directory to write test files
        fixture_file: Optional fixture file path
        parametrize: Whether to generate parametrized tests
        write_files: Whether to actually write files

    Returns:
        GenerationReport
    """
    report = GenerationReport(
        source_file=discovery_data.get("target", ""),
        templates_generated=0,
    )

    # Parse available fixtures
    available_fixtures = parse_fixture_file(fixture_file)

    # Group functions by file/module
    by_module: dict[str, list[dict]] = {}
    for func in discovery_data.get("functions", []):
        file_path = func.get("file", "")
        module_name = Path(file_path).stem if file_path else "unknown"

        if module_name not in by_module:
            by_module[module_name] = []
        by_module[module_name].append(func)

    # Generate test files for each module
    for module_name, functions in by_module.items():
        # Skip test modules
        if module_name.startswith("test_"):
            continue

        test_file = generate_test_file(
            functions, module_name, output_dir, parametrize, available_fixtures
        )
        report.files_created.append(test_file)
        report.templates_generated += len(test_file.templates)

        # Write the file if requested
        if write_files:
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
                content = test_file.generate_content()
                safe_write(test_file.path, content)
            except Exception as e:
                report.skipped.append(f"Failed to write {test_file.path}: {e}")

    return report


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate pytest test templates from function discovery",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  test_template_generator.py functions.json
  test_template_generator.py --output-dir tests/ discovery.json
  test_template_generator.py --parametrize --fixture-file conftest.py functions.json
        """,
    )
    parser.add_argument(
        "discovery_json",
        help="JSON output from function_discoverer",
    )
    parser.add_argument(
        "-o",
        "--output",
        choices=["json", "human"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--output-dir",
        default="tests",
        help="Directory to write test files (default: tests)",
    )
    parser.add_argument(
        "--fixture-file",
        help="Path to conftest.py or fixture file",
    )
    parser.add_argument(
        "--parametrize",
        action="store_true",
        help="Generate parametrized tests",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate templates without writing files",
    )

    args = parser.parse_args()

    discovery_path = Path(args.discovery_json)
    if not discovery_path.exists():
        emit_error(EXIT_FILE_NOT_FOUND, f"File not found: {discovery_path}")
        return EXIT_FILE_NOT_FOUND

    try:
        with open(discovery_path, encoding="utf-8") as f:
            discovery_data = json.load(f)
    except json.JSONDecodeError as e:
        emit_error(EXIT_ERROR, f"Invalid JSON: {e}")
        return EXIT_ERROR

    output_dir = Path(args.output_dir)
    fixture_file = Path(args.fixture_file) if args.fixture_file else None

    emit_info(f"Generating test templates from {discovery_path}...")

    report = generate_all(
        discovery_data,
        output_dir,
        fixture_file,
        args.parametrize,
        write_files=not args.dry_run,
    )

    output_format = OutputFormat(args.output)
    output(report.to_dict(), output_format)

    summary = report.to_dict()["summary"]
    action = "Would create" if args.dry_run else "Created"
    emit_info(
        f"{action} {summary['files_created']} test files "
        f"with {summary['templates_generated']} test templates"
    )

    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
