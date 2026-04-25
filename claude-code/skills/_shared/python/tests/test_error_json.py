"""
Tests for layer1.error_json module.

Tests structured JSON error output functions.
"""

import json

from layer0.exit_codes import EXIT_FILE_NOT_FOUND, EXIT_SUCCESS
from layer1.error_json import emit_error, emit_success, format_error_json


def test_format_error_json_structure():
    """Test that format_error_json() returns valid JSON with correct structure."""
    result = format_error_json(
        code=EXIT_FILE_NOT_FOUND, message="File not found", context={"path": "/tmp/test.txt"}
    )

    data = json.loads(result)
    assert "error" in data
    assert data["error"]["code"] == EXIT_FILE_NOT_FOUND
    assert data["error"]["message"] == "File not found"
    assert "context" in data["error"]
    assert data["error"]["context"]["path"] == "/tmp/test.txt"


def test_format_error_json_without_context():
    """Test format_error_json() without context data."""
    result = format_error_json(code=1, message="Generic error")

    data = json.loads(result)
    assert "error" in data
    assert "context" not in data["error"]
    assert data["error"]["code"] == 1


def test_emit_success_structure(capsys):
    """Test that emit_success() prints valid JSON to stdout."""
    emit_success("Operation completed", {"result": 42})

    captured = capsys.readouterr()
    data = json.loads(captured.out)

    assert "success" in data
    assert data["success"]["code"] == EXIT_SUCCESS
    assert data["success"]["message"] == "Operation completed"
    assert data["success"]["data"]["result"] == 42


def test_emit_success_without_data(capsys):
    """Test emit_success() without data parameter."""
    emit_success("Done")

    captured = capsys.readouterr()
    data = json.loads(captured.out)

    assert "success" in data
    assert "data" not in data["success"]


def test_emit_error_without_exit(capsys):
    """Test emit_error() with exit_after=False."""
    # Use exit_after=False to avoid sys.exit() in test
    emit_error(code=10, message="Test error", context={"detail": "test"}, exit_after=False)

    captured = capsys.readouterr()
    data = json.loads(captured.err)

    assert "error" in data
    assert data["error"]["code"] == 10
    assert data["error"]["message"] == "Test error"
