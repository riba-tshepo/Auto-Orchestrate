"""
Migration utilities for schema versioning.

Provides version detection, parsing, and migration path planning.
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class VersionInfo:
    """Information about a detected version."""

    version: str
    source_file: str
    format_type: str
    key_path: str
    raw_value: Any = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version": self.version,
            "source_file": self.source_file,
            "format": self.format_type,
            "key_path": self.key_path,
        }


@dataclass
class MigrationInfo:
    """Information about a migration file."""

    path: str
    from_version: str
    to_version: str
    name: str = ""
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "path": self.path,
            "from_version": self.from_version,
            "to_version": self.to_version,
            "name": self.name,
            "description": self.description,
        }


def parse_version(version_str: str) -> tuple[int, ...]:
    """
    Parse version string into comparable tuple.

    Supports:
    - Semantic versioning: 1.2.3, 1.2.3-beta
    - Simple versions: 1, 2.0
    - Prefixed versions: v1.2.3

    Args:
        version_str: Version string to parse

    Returns:
        Tuple of version components as integers
    """
    # Remove common prefixes
    version_str = version_str.lstrip("vV")

    # Extract numeric parts
    parts = re.split(r"[.\-_]", version_str)
    result = []

    for part in parts:
        # Extract leading digits
        match = re.match(r"^(\d+)", part)
        if match:
            result.append(int(match.group(1)))
        else:
            break

    return tuple(result) if result else (0,)


def compare_versions(v1: str, v2: str) -> int:
    """
    Compare two version strings.

    Args:
        v1: First version
        v2: Second version

    Returns:
        -1 if v1 < v2, 0 if equal, 1 if v1 > v2
    """
    t1 = parse_version(v1)
    t2 = parse_version(v2)

    # Pad shorter tuple
    max_len = max(len(t1), len(t2))
    t1 = t1 + (0,) * (max_len - len(t1))
    t2 = t2 + (0,) * (max_len - len(t2))

    if t1 < t2:
        return -1
    elif t1 > t2:
        return 1
    return 0


def detect_version(
    path: str | Path, key_path: str = "version", format_hint: str | None = None
) -> VersionInfo:
    """
    Detect version from a file.

    Args:
        path: Path to file
        key_path: Dot-separated path to version field (e.g., "meta.version")
        format_hint: File format hint ("json", "yaml", or auto-detect)

    Returns:
        VersionInfo with detected version

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If version can't be detected
    """
    path = Path(path)

    # Auto-detect format
    if format_hint is None:
        suffix = path.suffix.lower()
        if suffix in (".json",):
            format_hint = "json"
        elif suffix in (".yaml", ".yml"):
            format_hint = "yaml"
        else:
            format_hint = "json"  # Default to JSON

    # Read and parse file
    content = path.read_text()

    if format_hint == "json":
        data = json.loads(content)
    elif format_hint == "yaml":
        try:
            import yaml  # type: ignore[import-untyped]

            data = yaml.safe_load(content)
        except ImportError as err:
            raise ImportError("PyYAML is required for YAML files") from err
    else:
        raise ValueError(f"Unsupported format: {format_hint}")

    # Navigate to key
    value = data
    for key in key_path.split("."):
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            raise ValueError(f"Key path '{key_path}' not found in {path}")

    return VersionInfo(
        version=str(value),
        source_file=str(path),
        format_type=format_hint,
        key_path=key_path,
        raw_value=value,
    )


def get_nested_key(data: dict[str, Any], key_path: str) -> Any:
    """
    Get value at nested key path.

    Args:
        data: Dictionary to navigate
        key_path: Dot-separated key path

    Returns:
        Value at key path, or None if not found
    """
    value = data
    for key in key_path.split("."):
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None
    return value
