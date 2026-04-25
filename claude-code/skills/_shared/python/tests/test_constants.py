"""
Tests for layer0.constants module.

Tests application-wide constants including paths and limits.
"""

from pathlib import Path

from layer0.constants import (
    CLAUDE_DIR,
    DEFAULT_ENCODING,
    DEFAULT_MANIFEST_PATH,
    DEFAULT_SESSION_DIR,
    MANIFEST_ROTATION_THRESHOLD,
    MAX_TASK_DESCRIPTION_LENGTH,
    MAX_TASKS_PER_EPIC,
)


def test_default_encoding_is_utf8():
    """Test that DEFAULT_ENCODING is set to utf-8."""
    assert DEFAULT_ENCODING == "utf-8"
    assert isinstance(DEFAULT_ENCODING, str)


def test_claude_dir_is_path():
    """Test that CLAUDE_DIR is a Path object in home directory."""
    assert isinstance(CLAUDE_DIR, Path)
    assert Path.home() / ".claude" == CLAUDE_DIR


def test_manifest_path_is_in_claude_dir():
    """Test that DEFAULT_MANIFEST_PATH is inside CLAUDE_DIR."""
    assert isinstance(DEFAULT_MANIFEST_PATH, Path)
    assert DEFAULT_MANIFEST_PATH.parent == CLAUDE_DIR
    assert DEFAULT_MANIFEST_PATH.name == "manifest.json"


def test_session_dir_is_in_claude_dir():
    """Test that DEFAULT_SESSION_DIR is inside CLAUDE_DIR."""
    assert isinstance(DEFAULT_SESSION_DIR, Path)
    assert DEFAULT_SESSION_DIR.parent == CLAUDE_DIR
    assert DEFAULT_SESSION_DIR.name == "sessions"


def test_rotation_threshold_is_positive():
    """Test that MANIFEST_ROTATION_THRESHOLD is a positive integer."""
    assert isinstance(MANIFEST_ROTATION_THRESHOLD, int)
    assert MANIFEST_ROTATION_THRESHOLD > 0
    assert MANIFEST_ROTATION_THRESHOLD == 200


def test_task_limits_are_positive():
    """Test that task limit constants are positive integers."""
    assert isinstance(MAX_TASK_DESCRIPTION_LENGTH, int)
    assert isinstance(MAX_TASKS_PER_EPIC, int)
    assert MAX_TASK_DESCRIPTION_LENGTH > 0
    assert MAX_TASKS_PER_EPIC > 0
