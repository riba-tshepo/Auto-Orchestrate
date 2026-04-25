#!/usr/bin/env python3
"""
Schema Validator - Validates JSON/YAML files against schemas.

Supports JSON Schema draft-07 validation with detailed error reporting
including line numbers.

Usage:
    schema_validator.py [-o json|human] [--schema SCHEMA_FILE] DATA_FILE

Examples:
    schema_validator.py --schema schema.json data.json
    schema_validator.py -o human --schema config-schema.yaml config.yaml
    schema_validator.py manifest.json  # Uses embedded schema if present
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

from layer0 import EXIT_ERROR, EXIT_FILE_NOT_FOUND, EXIT_SUCCESS, EXIT_VALIDATION_ERROR
from layer1 import OutputFormat, emit_error, emit_info, output

# Try to import jsonschema, fall back to basic validation
try:
    import jsonschema

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

# Try to import yaml
try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False


@dataclass
class ValidationIssue:
    """A validation error or warning."""

    path: str
    message: str
    line: int | None = None
    severity: str = "error"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "path": self.path,
            "message": self.message,
            "severity": self.severity,
        }
        if self.line is not None:
            result["line"] = self.line
        return result


@dataclass
class ValidationReport:
    """Report containing validation results."""

    data_file: str
    schema_file: str | None
    is_valid: bool
    errors: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "data_file": self.data_file,
            "schema_file": self.schema_file,
            "is_valid": self.is_valid,
            "errors": [e.to_dict() for e in self.errors],
            "warnings": [w.to_dict() for w in self.warnings],
            "summary": {
                "error_count": len(self.errors),
                "warning_count": len(self.warnings),
            },
        }


def load_json_file(path: Path) -> tuple[Any, str]:
    """
    Load JSON file.

    Args:
        path: Path to JSON file

    Returns:
        Tuple of (data, raw_content)
    """
    content = path.read_text(encoding="utf-8")
    data = json.loads(content)
    return data, content


def load_yaml_file(path: Path) -> tuple[Any, str]:
    """
    Load YAML file.

    Args:
        path: Path to YAML file

    Returns:
        Tuple of (data, raw_content)

    Raises:
        ImportError: If PyYAML not installed
    """
    if not HAS_YAML:
        raise ImportError(
            "PyYAML is required for YAML validation. Install with: pip install pyyaml"
        )

    content = path.read_text(encoding="utf-8")
    data = yaml.safe_load(content)
    return data, content


def load_schema(path: Path) -> dict[str, Any]:
    """
    Load schema from JSON or YAML file.

    Args:
        path: Path to schema file

    Returns:
        Schema dictionary
    """
    ext = path.suffix.lower()
    if ext in (".yaml", ".yml"):
        schema, _ = load_yaml_file(path)
    else:
        schema, _ = load_json_file(path)

    if not isinstance(schema, dict):
        raise ValueError("Schema must be a JSON object")

    return schema


def locate_error_line(content: str, json_path: str) -> int | None:
    """
    Attempt to locate the line number for a JSON path.

    Args:
        content: Raw file content
        json_path: JSON path like "$.foo.bar" or "/foo/bar"

    Returns:
        Line number or None
    """
    # Convert JSON path to key sequence
    path_parts = []
    if json_path.startswith("$."):
        path_parts = json_path[2:].split(".")
    elif json_path.startswith("/"):
        path_parts = [p for p in json_path[1:].split("/") if p]

    if not path_parts:
        return 1

    # Try to find the last key in the path
    target_key = path_parts[-1]

    # Handle array indices
    array_match = re.match(r"(\w+)\[(\d+)\]", target_key)
    if array_match:
        target_key = array_match.group(1)

    # Search for the key in content
    lines = content.splitlines()
    for i, line in enumerate(lines, 1):
        # Look for "key": pattern
        if re.search(rf'["\']?{re.escape(target_key)}["\']?\s*:', line):
            return i
        # Look for key: pattern (YAML)
        if re.match(rf"\s*{re.escape(target_key)}\s*:", line):
            return i

    return None


def validate_with_jsonschema(
    data: Any, schema: dict[str, Any], content: str
) -> list[ValidationIssue]:
    """
    Validate data using jsonschema library.

    Args:
        data: Data to validate
        schema: JSON Schema
        content: Raw content for line number lookup

    Returns:
        List of validation issues
    """
    issues: list[ValidationIssue] = []

    validator_class = jsonschema.Draft7Validator
    validator = validator_class(schema)

    for error in validator.iter_errors(data):
        path = "/" + "/".join(str(p) for p in error.absolute_path) if error.absolute_path else "/"
        line = locate_error_line(content, path)

        issues.append(
            ValidationIssue(
                path=path,
                message=error.message,
                line=line,
                severity="error",
            )
        )

    return issues


def validate_basic(data: Any, schema: dict[str, Any], content: str) -> list[ValidationIssue]:
    """
    Basic validation when jsonschema is not available.

    Only checks type and required properties at top level.

    Args:
        data: Data to validate
        schema: JSON Schema
        content: Raw content for line number lookup

    Returns:
        List of validation issues
    """
    issues: list[ValidationIssue] = []

    # Check type
    schema_type = schema.get("type")
    if schema_type:
        type_map = {
            "object": dict,
            "array": list,
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "null": type(None),
        }
        expected_type = type_map.get(schema_type)
        if expected_type and not isinstance(data, expected_type):
            issues.append(
                ValidationIssue(
                    path="/",
                    message=f"Expected type '{schema_type}', got '{type(data).__name__}'",
                    line=1,
                )
            )

    # Check required properties
    if isinstance(data, dict):
        required = schema.get("required", [])
        for prop in required:
            if prop not in data:
                issues.append(
                    ValidationIssue(
                        path=f"/{prop}",
                        message=f"Required property '{prop}' is missing",
                        line=None,
                    )
                )

        # Check properties
        properties = schema.get("properties", {})
        for prop, prop_schema in properties.items():
            if prop in data:
                prop_type = prop_schema.get("type")
                if prop_type:
                    type_map = {
                        "object": dict,
                        "array": list,
                        "string": str,
                        "number": (int, float),
                        "integer": int,
                        "boolean": bool,
                        "null": type(None),
                    }
                    expected_type = type_map.get(prop_type)
                    if expected_type and not isinstance(data[prop], expected_type):
                        line = locate_error_line(content, f"/{prop}")
                        issues.append(
                            ValidationIssue(
                                path=f"/{prop}",
                                message=f"Property '{prop}' expected type '{prop_type}', got '{type(data[prop]).__name__}'",
                                line=line,
                            )
                        )

    return issues


def validate_against_schema(
    data: Any, schema: dict[str, Any], content: str
) -> list[ValidationIssue]:
    """
    Validate data against schema.

    Uses jsonschema if available, falls back to basic validation.

    Args:
        data: Data to validate
        schema: JSON Schema
        content: Raw content for line number lookup

    Returns:
        List of validation issues
    """
    if HAS_JSONSCHEMA:
        return validate_with_jsonschema(data, schema, content)
    else:
        emit_info("jsonschema not installed, using basic validation")
        return validate_basic(data, schema, content)


def check_common_issues(data: Any, content: str) -> list[ValidationIssue]:
    """
    Check for common issues without a schema.

    Args:
        data: Parsed data
        content: Raw content

    Returns:
        List of warnings
    """
    warnings: list[ValidationIssue] = []

    # Check for trailing commas (JSON only - would cause parse error)
    # Check for duplicate keys (would only keep last in Python)
    # These are already handled by JSON parser

    # Check for empty objects/arrays that might be unintentional
    def check_empty(obj: Any, path: str = "/") -> None:
        if isinstance(obj, dict):
            if not obj:
                line = locate_error_line(content, path)
                warnings.append(
                    ValidationIssue(
                        path=path,
                        message="Empty object found",
                        line=line,
                        severity="warning",
                    )
                )
            for key, value in obj.items():
                check_empty(value, f"{path}{key}/")
        elif isinstance(obj, list):
            if not obj:
                line = locate_error_line(content, path)
                warnings.append(
                    ValidationIssue(
                        path=path,
                        message="Empty array found",
                        line=line,
                        severity="warning",
                    )
                )
            for i, item in enumerate(obj):
                check_empty(item, f"{path}[{i}]/")

    check_empty(data)

    return warnings


def validate_json_file(data_file: Path, schema_file: Path | None) -> ValidationReport:
    """
    Validate JSON file against schema.

    Args:
        data_file: Path to JSON file
        schema_file: Optional path to schema file

    Returns:
        ValidationReport
    """
    # Load data
    data, content = load_json_file(data_file)

    # Load or detect schema
    schema = None
    if schema_file:
        schema = load_schema(schema_file)
    elif isinstance(data, dict) and "$schema" in data:
        # Try to load embedded schema reference
        schema_ref = data.get("$schema")
        if isinstance(schema_ref, str) and not schema_ref.startswith("http"):
            schema_path = data_file.parent / schema_ref
            if schema_path.exists():
                schema = load_schema(schema_path)

    errors: list[ValidationIssue] = []
    warnings: list[ValidationIssue] = []

    if schema:
        errors = validate_against_schema(data, schema, content)
    else:
        warnings.append(
            ValidationIssue(
                path="/",
                message="No schema provided; only checking for common issues",
                line=None,
                severity="warning",
            )
        )

    # Check for common issues
    warnings.extend(check_common_issues(data, content))

    return ValidationReport(
        data_file=str(data_file),
        schema_file=str(schema_file) if schema_file else None,
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


def validate_yaml_file(data_file: Path, schema_file: Path | None) -> ValidationReport:
    """
    Validate YAML file against schema.

    Args:
        data_file: Path to YAML file
        schema_file: Optional path to schema file

    Returns:
        ValidationReport
    """
    # Load data
    data, content = load_yaml_file(data_file)

    # Load schema
    schema = None
    if schema_file:
        schema = load_schema(schema_file)

    errors: list[ValidationIssue] = []
    warnings: list[ValidationIssue] = []

    if schema:
        errors = validate_against_schema(data, schema, content)
    else:
        warnings.append(
            ValidationIssue(
                path="/",
                message="No schema provided; only checking for common issues",
                line=None,
                severity="warning",
            )
        )

    # Check for common issues
    warnings.extend(check_common_issues(data, content))

    return ValidationReport(
        data_file=str(data_file),
        schema_file=str(schema_file) if schema_file else None,
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate JSON/YAML files against schemas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  schema_validator.py --schema schema.json data.json
  schema_validator.py -o human --schema config-schema.yaml config.yaml
  schema_validator.py manifest.json  # Uses embedded schema if present
        """,
    )
    parser.add_argument(
        "data_file",
        help="JSON or YAML file to validate",
    )
    parser.add_argument(
        "-o",
        "--output",
        choices=["json", "human"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--schema",
        help="Schema file (JSON or YAML)",
    )

    args = parser.parse_args()

    data_file = Path(args.data_file)
    if not data_file.exists():
        emit_error(EXIT_FILE_NOT_FOUND, f"Data file not found: {data_file}")
        return EXIT_FILE_NOT_FOUND

    schema_file = None
    if args.schema:
        schema_file = Path(args.schema)
        if not schema_file.exists():
            emit_error(EXIT_FILE_NOT_FOUND, f"Schema file not found: {schema_file}")
            return EXIT_FILE_NOT_FOUND

    emit_info(f"Validating {data_file}...")

    try:
        ext = data_file.suffix.lower()
        if ext in (".yaml", ".yml"):
            report = validate_yaml_file(data_file, schema_file)
        else:
            report = validate_json_file(data_file, schema_file)
    except json.JSONDecodeError as e:
        emit_error(EXIT_VALIDATION_ERROR, f"Invalid JSON: {e}")
        return EXIT_VALIDATION_ERROR
    except Exception as e:
        emit_error(EXIT_ERROR, f"Validation failed: {e}")
        return EXIT_ERROR

    output_format = OutputFormat(args.output)
    output(report.to_dict(), output_format)

    if report.is_valid:
        emit_info(f"Validation passed with {len(report.warnings)} warning(s)")
        return EXIT_SUCCESS
    else:
        emit_info(
            f"Validation failed: {len(report.errors)} error(s), {len(report.warnings)} warning(s)"
        )
        return EXIT_VALIDATION_ERROR


if __name__ == "__main__":
    sys.exit(main())
