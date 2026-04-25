"""
Tests for layer1.config module.

Tests configuration loading, saving, and merging utilities.
"""

import pytest

from layer1.config import (
    ConfigNotFoundError,
    ConfigValidationError,
    load_config,
    merge_config,
    save_config,
)


def test_load_config_with_default(temp_dir):
    """Test load_config() returns default when file doesn't exist."""
    nonexistent = temp_dir / "nonexistent.json"
    default = {"key": "value"}

    result = load_config(nonexistent, default=default)
    assert result == default


def test_load_config_file_not_found_no_default(temp_dir):
    """Test load_config() raises ConfigNotFoundError when file missing and no default."""
    nonexistent = temp_dir / "nonexistent.json"

    with pytest.raises(ConfigNotFoundError):
        load_config(nonexistent)


def test_save_and_load_config(temp_dir):
    """Test saving and loading configuration."""
    config_path = temp_dir / "config.json"
    config_data = {"mode": "production", "debug": False, "timeout": 30}

    save_config(config_path, config_data)
    loaded = load_config(config_path)

    assert loaded == config_data


def test_save_config_creates_directories(temp_dir):
    """Test that save_config() creates parent directories."""
    nested_path = temp_dir / "nested" / "dir" / "config.json"
    config_data = {"test": True}

    save_config(nested_path, config_data)

    assert nested_path.exists()
    assert load_config(nested_path) == config_data


def test_load_config_with_required_keys(temp_dir):
    """Test load_config() validates required keys."""
    config_path = temp_dir / "config.json"
    config_data = {"name": "test", "version": "1.0"}

    save_config(config_path, config_data)

    # Should pass with present keys
    result = load_config(config_path, required_keys=["name"])
    assert result["name"] == "test"

    # Should fail with missing keys
    with pytest.raises(ConfigValidationError):
        load_config(config_path, required_keys=["name", "missing_key"])


def test_merge_config_basic():
    """Test basic config merge."""
    base = {"a": 1, "b": 2}
    override = {"b": 3, "c": 4}

    result = merge_config(base, override)

    assert result["a"] == 1  # From base
    assert result["b"] == 3  # Overridden
    assert result["c"] == 4  # New from override


def test_merge_config_nested():
    """Test nested dict merge."""
    base = {"settings": {"debug": False, "timeout": 30}}
    override = {"settings": {"debug": True, "retries": 3}}

    result = merge_config(base, override)

    assert result["settings"]["debug"] is True  # Overridden
    assert result["settings"]["timeout"] == 30  # Preserved from base
    assert result["settings"]["retries"] == 3  # New from override


def test_merge_config_does_not_mutate():
    """Test that merge_config() doesn't mutate inputs."""
    base = {"a": 1}
    override = {"b": 2}

    result = merge_config(base, override)

    assert "b" not in base  # Base unchanged
    assert result == {"a": 1, "b": 2}
