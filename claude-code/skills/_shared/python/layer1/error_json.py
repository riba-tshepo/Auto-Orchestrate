"""
Standardized error JSON output utilities.

This module provides functions for emitting structured error messages
in JSON format, enabling consistent error handling across scripts.

Example:
    from layer1.error_json import emit_error
    from layer0.exit_codes import EXIT_FILE_NOT_FOUND

    emit_error(
        code=EXIT_FILE_NOT_FOUND,
        message="Configuration file not found",
        context={"path": "/path/to/config.json"}
    )
"""

from __future__ import annotations

import json
import sys
from typing import Any

from layer0.exit_codes import EXIT_SUCCESS, exit_code_to_message


def emit_error(
    code: int,
    message: str,
    context: dict[str, Any] | None = None,
    *,
    exit_after: bool = True,
) -> None:
    """Emit structured error as JSON to stderr and optionally exit.

    Args:
        code: Exit code from layer0.exit_codes.
        message: Human-readable error message.
        context: Optional additional context data.
        exit_after: If True, call sys.exit(code) after emitting. Defaults to True.

    Example:
        >>> emit_error(10, "File not found", {"path": "/tmp/file.txt"})
        # Prints to stderr: {"error": {...}} and exits with code 10
    """
    error_obj = {
        "error": {
            "code": code,
            "message": message,
            "description": exit_code_to_message(code),
        }
    }

    if context:
        error_obj["error"]["context"] = context

    print(json.dumps(error_obj, indent=2), file=sys.stderr)

    if exit_after:
        sys.exit(code)


def emit_success(
    message: str,
    data: dict[str, Any] | None = None,
) -> None:
    """Emit structured success message as JSON to stdout.

    Args:
        message: Human-readable success message.
        data: Optional result data.

    Example:
        >>> emit_success("Task completed", {"task_id": "123"})
        # Prints to stdout: {"success": {...}}
    """
    success_obj = {
        "success": {
            "code": EXIT_SUCCESS,
            "message": message,
        }
    }

    if data:
        success_obj["success"]["data"] = data

    print(json.dumps(success_obj, indent=2))


def format_error_json(
    code: int,
    message: str,
    context: dict[str, Any] | None = None,
) -> str:
    """Format error as JSON string without emitting.

    Args:
        code: Exit code.
        message: Error message.
        context: Optional context data.

    Returns:
        JSON-formatted error string.
    """
    error_obj = {
        "error": {
            "code": code,
            "message": message,
            "description": exit_code_to_message(code),
        }
    }

    if context:
        error_obj["error"]["context"] = context

    return json.dumps(error_obj, indent=2)
