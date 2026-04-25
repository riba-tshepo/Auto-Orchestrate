"""
Tests for layer2.validation module.

Tests validation utilities including validate_path, validate_file_exists,
validate_directory_exists, validate_json_schema, and validate_range.
"""

from layer2.validation import (
    ValidationError,
    ValidationResult,
    validate_directory_exists,
    validate_file_exists,
    validate_json_schema,
    validate_path,
    validate_range,
)


def test_validation_error_with_message():
    """Test ValidationError with message."""
    error = ValidationError("Test error")

    assert error.message == "Test error"
    assert error.field is None
    assert str(error) == "Test error"


def test_validation_error_with_field():
    """Test ValidationError with field name."""
    error = ValidationError("Invalid value", field="username")

    assert error.message == "Invalid value"
    assert error.field == "username"


def test_validation_result_default_valid():
    """Test ValidationResult defaults to valid."""
    result = ValidationResult(is_valid=True)

    assert result.is_valid is True
    assert result.errors == []
    assert result.warnings == []


def test_validation_result_add_error():
    """Test ValidationResult.add_error() marks as invalid."""
    result = ValidationResult(is_valid=True)

    result.add_error("Error message")

    assert result.is_valid is False
    assert "Error message" in result.errors


def test_validation_result_add_warning():
    """Test ValidationResult.add_warning() keeps valid status."""
    result = ValidationResult(is_valid=True)

    result.add_warning("Warning message")

    assert result.is_valid is True
    assert "Warning message" in result.warnings


def test_validation_result_to_dict():
    """Test ValidationResult.to_dict() conversion."""
    result = ValidationResult(is_valid=False)
    result.add_error("Error")
    result.add_warning("Warning")

    result_dict = result.to_dict()

    assert result_dict["is_valid"] is False
    assert result_dict["errors"] == ["Error"]
    assert result_dict["warnings"] == ["Warning"]


def test_validation_result_merge():
    """Test ValidationResult.merge() combines results."""
    result1 = ValidationResult(is_valid=True)
    result1.add_warning("Warning 1")

    result2 = ValidationResult(is_valid=False)
    result2.add_error("Error 2")

    result1.merge(result2)

    assert result1.is_valid is False
    assert "Warning 1" in result1.warnings
    assert "Error 2" in result1.errors


def test_validate_path_valid(tmp_path):
    """Test validate_path() with valid path."""
    test_file = tmp_path / "test.txt"

    result = validate_path(test_file, must_exist=False)

    assert result.is_valid is True
    assert len(result.errors) == 0


def test_validate_path_must_exist_missing(tmp_path):
    """Test validate_path() with must_exist and missing path."""
    test_file = tmp_path / "nonexistent.txt"

    result = validate_path(test_file, must_exist=True)

    assert result.is_valid is False
    assert any("does not exist" in e for e in result.errors)


def test_validate_path_must_exist_present(tmp_path):
    """Test validate_path() with must_exist and existing path."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")

    result = validate_path(test_file, must_exist=True)

    assert result.is_valid is True


def test_validate_file_exists_success(tmp_path):
    """Test validate_file_exists() with existing file."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")

    result = validate_file_exists(test_file)

    assert result.is_valid is True


def test_validate_file_exists_missing(tmp_path):
    """Test validate_file_exists() with missing file."""
    test_file = tmp_path / "nonexistent.txt"

    result = validate_file_exists(test_file)

    assert result.is_valid is False
    assert any("not found" in e for e in result.errors)


def test_validate_file_exists_is_directory(tmp_path):
    """Test validate_file_exists() with directory instead of file."""
    test_dir = tmp_path / "testdir"
    test_dir.mkdir()

    result = validate_file_exists(test_dir)

    assert result.is_valid is False
    assert any("Not a file" in e for e in result.errors)


def test_validate_directory_exists_success(tmp_path):
    """Test validate_directory_exists() with existing directory."""
    test_dir = tmp_path / "testdir"
    test_dir.mkdir()

    result = validate_directory_exists(test_dir)

    assert result.is_valid is True


def test_validate_directory_exists_missing(tmp_path):
    """Test validate_directory_exists() with missing directory."""
    test_dir = tmp_path / "nonexistent"

    result = validate_directory_exists(test_dir)

    assert result.is_valid is False
    assert any("not found" in e for e in result.errors)


def test_validate_directory_exists_is_file(tmp_path):
    """Test validate_directory_exists() with file instead of directory."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")

    result = validate_directory_exists(test_file)

    assert result.is_valid is False
    assert any("Not a directory" in e for e in result.errors)


def test_validate_json_schema_all_required_present():
    """Test validate_json_schema() with all required fields present."""
    data = {"name": "test", "age": 25}

    result = validate_json_schema(data, required_fields=["name", "age"])

    assert result.is_valid is True


def test_validate_json_schema_missing_required():
    """Test validate_json_schema() with missing required field."""
    data = {"name": "test"}

    result = validate_json_schema(data, required_fields=["name", "age"])

    assert result.is_valid is False
    assert any("Missing required field: age" in e for e in result.errors)


def test_validate_json_schema_unknown_field_warning():
    """Test validate_json_schema() warns about unknown fields."""
    data = {"name": "test", "unknown": "value"}

    result = validate_json_schema(data, required_fields=["name"], optional_fields=[])

    assert result.is_valid is True
    assert any("Unknown field: unknown" in w for w in result.warnings)


def test_validate_range_within_bounds():
    """Test validate_range() with value within bounds."""
    result = validate_range(50, "value", min_val=0, max_val=100)

    assert result.is_valid is True


def test_validate_range_below_minimum():
    """Test validate_range() with value below minimum."""
    result = validate_range(-5, "value", min_val=0, max_val=100)

    assert result.is_valid is False
    assert any("at least 0" in e for e in result.errors)


def test_validate_range_above_maximum():
    """Test validate_range() with value above maximum."""
    result = validate_range(150, "value", min_val=0, max_val=100)

    assert result.is_valid is False
    assert any("at most 100" in e for e in result.errors)


def test_validate_range_no_bounds():
    """Test validate_range() with no bounds (always valid)."""
    result = validate_range(999, "value")

    assert result.is_valid is True


def test_validate_range_min_only():
    """Test validate_range() with only minimum bound."""
    result = validate_range(50, "value", min_val=10)

    assert result.is_valid is True


def test_validate_range_max_only():
    """Test validate_range() with only maximum bound."""
    result = validate_range(50, "value", max_val=100)

    assert result.is_valid is True
