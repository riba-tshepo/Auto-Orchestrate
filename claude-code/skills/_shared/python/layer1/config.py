"""
Configuration management utilities.

This module provides functions for loading and managing configuration
from JSON files with validation and error handling.

Example:
    from layer1.config import load_config, save_config

    config = load_config("/path/to/config.json", default={"key": "value"})
    save_config("/path/to/config.json", config)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from layer0.constants import DEFAULT_ENCODING


class ConfigError(Exception):
    """Base exception for configuration errors."""

    pass


class ConfigNotFoundError(ConfigError):
    """Raised when configuration file is not found."""

    pass


class ConfigValidationError(ConfigError):
    """Raised when configuration validation fails."""

    pass


def load_config(
    path: str | Path,
    *,
    default: dict[str, Any] | None = None,
    required_keys: list[str] | None = None,
) -> dict[str, Any]:
    """Load configuration from JSON file.

    Args:
        path: Path to configuration file.
        default: Default config to return if file doesn't exist. Defaults to None.
        required_keys: List of required keys to validate. Defaults to None.

    Returns:
        Configuration dictionary.

    Raises:
        ConfigNotFoundError: If file not found and no default provided.
        ConfigValidationError: If required keys are missing.
        json.JSONDecodeError: If file contains invalid JSON.

    Example:
        >>> config = load_config("config.json", default={"mode": "prod"})
        >>> print(config["mode"])
        'prod'
    """
    path = Path(path)

    if not path.exists():
        if default is not None:
            return default
        raise ConfigNotFoundError(f"Configuration file not found: {path}")

    with open(path, encoding=DEFAULT_ENCODING) as f:
        config: dict[str, Any] = json.load(f)

    # Validate required keys
    if required_keys:
        missing = [key for key in required_keys if key not in config]
        if missing:
            raise ConfigValidationError(
                f"Missing required configuration keys: {', '.join(missing)}"
            )

    return config


def save_config(
    path: str | Path,
    config: dict[str, Any],
    *,
    create_dirs: bool = True,
) -> None:
    """Save configuration to JSON file.

    Args:
        path: Path to configuration file.
        config: Configuration dictionary to save.
        create_dirs: Create parent directories if they don't exist. Defaults to True.

    Raises:
        OSError: If file write fails.

    Example:
        >>> save_config("config.json", {"mode": "dev", "debug": True})
    """
    path = Path(path)

    if create_dirs:
        path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding=DEFAULT_ENCODING) as f:
        json.dump(config, f, indent=2, sort_keys=True)
        f.write("\n")  # Trailing newline


def merge_config(
    base: dict[str, Any],
    override: dict[str, Any],
) -> dict[str, Any]:
    """Merge two configuration dictionaries.

    The override dict takes precedence over base. Nested dicts are merged recursively.

    Args:
        base: Base configuration.
        override: Override configuration.

    Returns:
        Merged configuration dictionary.

    Example:
        >>> base = {"a": 1, "b": {"c": 2}}
        >>> override = {"b": {"d": 3}}
        >>> merge_config(base, override)
        {'a': 1, 'b': {'c': 2, 'd': 3}}
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_config(result[key], value)
        else:
            result[key] = value

    return result
