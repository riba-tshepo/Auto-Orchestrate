"""
Validation utilities for CLI scripts.

Provides input validation with consistent error handling.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class ValidationError(Exception):
    """Raised when validation fails."""

    def __init__(self, message: str, field: str | None = None):
        self.message = message
        self.field = field
        super().__init__(message)


@dataclass
class ValidationResult:
    """Result of a validation operation."""

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        """Add an error message."""
        self.is_valid = False
        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
        }

    def merge(self, other: "ValidationResult") -> "ValidationResult":
        """Merge another validation result into this one."""
        self.is_valid = self.is_valid and other.is_valid
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        return self


def validate_path(path: str | Path, must_exist: bool = False) -> ValidationResult:
    """
    Validate a file path.

    Args:
        path: Path to validate
        must_exist: If True, path must exist

    Returns:
        Validation result
    """
    result = ValidationResult(is_valid=True)
    path = Path(path)

    # Check for null bytes or other invalid characters
    try:
        str(path.resolve())
    except (ValueError, OSError) as e:
        result.add_error(f"Invalid path: {e}")
        return result

    if must_exist and not path.exists():
        result.add_error(f"Path does not exist: {path}")

    return result


def validate_file_exists(path: str | Path) -> ValidationResult:
    """
    Validate that path exists and is a file.

    Args:
        path: Path to validate

    Returns:
        Validation result
    """
    result = ValidationResult(is_valid=True)
    path = Path(path)

    if not path.exists():
        result.add_error(f"File not found: {path}")
    elif not path.is_file():
        result.add_error(f"Not a file: {path}")

    return result


def validate_directory_exists(path: str | Path) -> ValidationResult:
    """
    Validate that path exists and is a directory.

    Args:
        path: Path to validate

    Returns:
        Validation result
    """
    result = ValidationResult(is_valid=True)
    path = Path(path)

    if not path.exists():
        result.add_error(f"Directory not found: {path}")
    elif not path.is_dir():
        result.add_error(f"Not a directory: {path}")

    return result


def validate_json_schema(
    data: dict[str, Any], required_fields: list[str], optional_fields: list[str] | None = None
) -> ValidationResult:
    """
    Validate JSON data against required and optional fields.

    Args:
        data: Data to validate
        required_fields: List of required field names
        optional_fields: List of optional field names (for unknown field detection)

    Returns:
        Validation result
    """
    result = ValidationResult(is_valid=True)
    optional_fields = optional_fields or []

    # Check required fields
    for field_name in required_fields:
        if field_name not in data:
            result.add_error(f"Missing required field: {field_name}")

    # Check for unknown fields
    known_fields = set(required_fields) | set(optional_fields)
    for field_name in data:
        if field_name not in known_fields:
            result.add_warning(f"Unknown field: {field_name}")

    return result


def validate_range(
    value: int | float,
    name: str,
    min_val: int | float | None = None,
    max_val: int | float | None = None,
) -> ValidationResult:
    """
    Validate that a value is within a range.

    Args:
        value: Value to validate
        name: Name of the value (for error messages)
        min_val: Minimum allowed value (inclusive)
        max_val: Maximum allowed value (inclusive)

    Returns:
        Validation result
    """
    result = ValidationResult(is_valid=True)

    if min_val is not None and value < min_val:
        result.add_error(f"{name} must be at least {min_val}, got {value}")

    if max_val is not None and value > max_val:
        result.add_error(f"{name} must be at most {max_val}, got {value}")

    return result
