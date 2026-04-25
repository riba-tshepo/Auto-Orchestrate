"""
Application-wide constants.

This module defines constants used across the Claude Code plugin system.
These are foundational values that have zero dependencies.

Example:
    from layer0.constants import DEFAULT_ENCODING, DEFAULT_MANIFEST_PATH

    with open(DEFAULT_MANIFEST_PATH, "r", encoding=DEFAULT_ENCODING) as f:
        data = f.read()
"""

from pathlib import Path

# File encoding
DEFAULT_ENCODING: str = "utf-8"
"""Default character encoding for file operations."""

# Paths (relative to home directory)
CLAUDE_DIR: Path = Path.home() / ".claude"
"""Base directory for Claude Code data."""

DEFAULT_MANIFEST_PATH: Path = CLAUDE_DIR / "manifest.json"
"""Path to the skill/agent manifest registry."""

DEFAULT_SESSION_DIR: Path = CLAUDE_DIR / "sessions"
"""Directory containing work session data."""

DEFAULT_TASKS_FILE: Path = CLAUDE_DIR / "tasks.json"
"""Path to the tasks database."""

DEFAULT_HISTORY_FILE: Path = CLAUDE_DIR / "history.jsonl"
"""Path to the command history log."""

# Manifest constants
MANIFEST_ROTATION_THRESHOLD: int = 200
"""Maximum entries before rotating manifest to archive."""

# Task system constants
MAX_TASK_DESCRIPTION_LENGTH: int = 2000
"""Maximum length for task descriptions."""

MAX_TASKS_PER_EPIC: int = 50
"""Maximum number of tasks allowed in a single epic."""

# Session constants
DEFAULT_MAX_ITERATIONS: int = 100
"""Default maximum iterations for auto-orchestration."""

DEFAULT_STALL_THRESHOLD: int = 2
"""Default number of iterations without progress before flagging stall."""
