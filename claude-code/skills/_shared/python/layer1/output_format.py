"""
Output formatting utilities for CLI scripts.

Supports JSON, human-readable, and table formats.
JSON output goes to stdout; other formats may use stderr for metadata.
"""

import json
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Any


class OutputFormat(Enum):
    """Supported output formats."""

    JSON = "json"
    HUMAN = "human"
    TABLE = "table"


def output(
    data: dict[str, Any], format_type: OutputFormat = OutputFormat.JSON, file: Any = None
) -> None:
    """
    Output data in the specified format.

    Args:
        data: Dictionary to output
        format_type: Output format (JSON, HUMAN, or TABLE)
        file: Output file (default stdout)
    """
    if file is None:
        file = sys.stdout

    if format_type == OutputFormat.JSON:
        json.dump(data, file, indent=2, default=str)
        file.write("\n")
    elif format_type == OutputFormat.HUMAN:
        output_str = format_human(data)
        file.write(output_str)
        file.write("\n")
    elif format_type == OutputFormat.TABLE:
        output_str = format_table(data)
        file.write(output_str)
        file.write("\n")


def format_human(data: dict[str, Any], indent: int = 0) -> str:
    """
    Format dictionary as human-readable text.

    Args:
        data: Dictionary to format
        indent: Current indentation level

    Returns:
        Formatted string
    """
    lines = []
    prefix = "  " * indent

    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"{prefix}{key}:")
            lines.append(format_human(value, indent + 1))
        elif isinstance(value, list):
            lines.append(f"{prefix}{key}:")
            for item in value:
                if isinstance(item, dict):
                    lines.append(format_human(item, indent + 1))
                else:
                    lines.append(f"{prefix}  - {item}")
        else:
            lines.append(f"{prefix}{key}: {value}")

    return "\n".join(lines)


def format_table(data: dict[str, Any], headers: list[str] | None = None, key: str = "items") -> str:
    """
    Format data as ASCII table.

    Args:
        data: Dictionary containing items to tabulate
        headers: Column headers (auto-detected if not provided)
        key: Key in data dict containing list of items

    Returns:
        ASCII table string
    """
    items = data.get(key, [])
    if not items:
        return "(no items)"

    if not isinstance(items, list):
        items = [items]

    # Get headers from first item if not provided
    if headers is None and items:
        headers = list(items[0].keys()) if isinstance(items[0], dict) else ["value"]

    if not headers:
        return "(no data)"

    # Calculate column widths
    widths = {h: len(str(h)) for h in headers}
    for item in items:
        if isinstance(item, dict):
            for h in headers:
                val_len = len(str(item.get(h, "")))
                widths[h] = max(widths[h], val_len)
        else:
            widths[headers[0]] = max(widths[headers[0]], len(str(item)))

    # Build table
    lines = []

    # Header row
    header_row = " | ".join(h.ljust(widths[h]) for h in headers)
    lines.append(header_row)

    # Separator
    separator = "-+-".join("-" * widths[h] for h in headers)
    lines.append(separator)

    # Data rows
    for item in items:
        if isinstance(item, dict):
            row = " | ".join(str(item.get(h, "")).ljust(widths[h]) for h in headers)
        else:
            row = str(item).ljust(widths[headers[0]])
        lines.append(row)

    return "\n".join(lines)


@dataclass
class CLIOutput:
    """Standard CLI output structure."""

    success: bool
    data: dict[str, Any]
    message: str = ""
    errors: list[str] | None = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for output."""
        result = {
            "success": self.success,
            "data": self.data,
        }
        if self.message:
            result["message"] = self.message
        if self.errors:
            result["errors"] = self.errors
        return result
