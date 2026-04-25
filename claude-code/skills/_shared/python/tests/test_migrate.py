"""
Tests for layer3.migrate module.

Tests migration utilities including detect_version, parse_version, and
compare_versions.
"""

import json

import pytest

from layer3.migrate import (
    MigrationInfo,
    VersionInfo,
    compare_versions,
    detect_version,
    get_nested_key,
    parse_version,
)


def test_version_info_to_dict():
    """Test VersionInfo.to_dict() conversion."""
    version_info = VersionInfo(
        version="1.2.3", source_file="/path/to/file.json", format_type="json", key_path="version"
    )

    result = version_info.to_dict()

    assert result["version"] == "1.2.3"
    assert result["source_file"] == "/path/to/file.json"
    assert result["format"] == "json"


def test_migration_info_to_dict():
    """Test MigrationInfo.to_dict() conversion."""
    migration_info = MigrationInfo(
        path="/path/to/migration.py", from_version="1.0.0", to_version="2.0.0", name="Add new field"
    )

    result = migration_info.to_dict()

    assert result["from_version"] == "1.0.0"
    assert result["to_version"] == "2.0.0"
    assert result["name"] == "Add new field"


def test_parse_version_semantic():
    """Test parse_version() with semantic versioning."""
    assert parse_version("1.2.3") == (1, 2, 3)
    assert parse_version("2.0.0") == (2, 0, 0)
    assert parse_version("0.1.0") == (0, 1, 0)


def test_parse_version_with_prefix():
    """Test parse_version() with v prefix."""
    assert parse_version("v1.2.3") == (1, 2, 3)
    assert parse_version("V2.0.0") == (2, 0, 0)


def test_parse_version_simple():
    """Test parse_version() with simple versions."""
    assert parse_version("1") == (1,)
    assert parse_version("2.0") == (2, 0)


def test_parse_version_with_suffix():
    """Test parse_version() with suffix (beta, alpha)."""
    assert parse_version("1.2.3-beta") == (1, 2, 3)
    assert parse_version("2.0.0-alpha.1") == (2, 0, 0)


def test_parse_version_invalid():
    """Test parse_version() with invalid input."""
    assert parse_version("invalid") == (0,)
    assert parse_version("") == (0,)


def test_compare_versions_equal():
    """Test compare_versions() with equal versions."""
    assert compare_versions("1.2.3", "1.2.3") == 0
    assert compare_versions("2.0.0", "2.0.0") == 0


def test_compare_versions_less_than():
    """Test compare_versions() with v1 < v2."""
    assert compare_versions("1.2.3", "1.2.4") == -1
    assert compare_versions("1.0.0", "2.0.0") == -1
    assert compare_versions("0.9.0", "1.0.0") == -1


def test_compare_versions_greater_than():
    """Test compare_versions() with v1 > v2."""
    assert compare_versions("1.2.4", "1.2.3") == 1
    assert compare_versions("2.0.0", "1.0.0") == 1
    assert compare_versions("1.0.0", "0.9.0") == 1


def test_compare_versions_different_lengths():
    """Test compare_versions() with different length versions."""
    assert compare_versions("1.2", "1.2.0") == 0
    assert compare_versions("1.2.1", "1.2") == 1
    assert compare_versions("1.2", "1.2.1") == -1


def test_detect_version_json_file(tmp_path):
    """Test detect_version() with JSON file."""
    test_file = tmp_path / "package.json"
    data = {"version": "1.2.3", "name": "test"}
    test_file.write_text(json.dumps(data))

    version_info = detect_version(test_file, key_path="version")

    assert version_info.version == "1.2.3"
    assert version_info.format_type == "json"
    assert version_info.key_path == "version"


def test_detect_version_nested_key(tmp_path):
    """Test detect_version() with nested key path."""
    test_file = tmp_path / "config.json"
    data = {"meta": {"version": "2.0.0"}}
    test_file.write_text(json.dumps(data))

    version_info = detect_version(test_file, key_path="meta.version")

    assert version_info.version == "2.0.0"
    assert version_info.key_path == "meta.version"


def test_detect_version_file_not_found(tmp_path):
    """Test detect_version() with nonexistent file."""
    test_file = tmp_path / "nonexistent.json"

    with pytest.raises(FileNotFoundError):
        detect_version(test_file)


def test_detect_version_key_not_found(tmp_path):
    """Test detect_version() with missing key."""
    test_file = tmp_path / "config.json"
    data = {"name": "test"}
    test_file.write_text(json.dumps(data))

    with pytest.raises(ValueError) as exc_info:
        detect_version(test_file, key_path="version")

    assert "not found" in str(exc_info.value)


def test_get_nested_key_simple():
    """Test get_nested_key() with simple key."""
    data = {"name": "test", "value": 42}

    result = get_nested_key(data, "name")

    assert result == "test"


def test_get_nested_key_nested():
    """Test get_nested_key() with nested key path."""
    data = {"meta": {"version": "1.0.0", "author": "test"}}

    result = get_nested_key(data, "meta.version")

    assert result == "1.0.0"


def test_get_nested_key_missing():
    """Test get_nested_key() with missing key."""
    data = {"name": "test"}

    result = get_nested_key(data, "nonexistent")

    assert result is None


def test_get_nested_key_deeply_nested():
    """Test get_nested_key() with deeply nested path."""
    data = {"level1": {"level2": {"level3": "value"}}}

    result = get_nested_key(data, "level1.level2.level3")

    assert result == "value"
