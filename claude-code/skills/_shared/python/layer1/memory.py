"""
Persistent memory store for agents.

Provides load/save/clear operations for agent memory that survives
accidental terminations. Uses atomic writes to prevent corruption.

Storage location: ~/.claude/sessions/{session_id}/memory/{agent_name}.json
"""

from __future__ import annotations

import json
import logging
import os
import re
import tempfile
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_AGENT_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")
_SESSION_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")


def _validate_identifier(value: str, label: str) -> None:
    """Validate that an identifier contains only safe characters.

    Args:
        value: The identifier string to validate.
        label: Human-readable label for error messages (e.g. "agent_name").

    Raises:
        ValueError: If the identifier is empty or contains unsafe characters.
    """
    if not value:
        raise ValueError(f"{label} must not be empty")
    if not _AGENT_NAME_PATTERN.match(value):
        raise ValueError(
            f"{label} must contain only alphanumeric characters, hyphens, "
            f"and underscores, got: {value!r}"
        )


def get_memory_path(agent_name: str, session_id: str) -> Path:
    """Get the filesystem path where agent memory is stored.

    Args:
        agent_name: Name of the agent (alphanumeric, hyphens, underscores).
        session_id: Session identifier (alphanumeric, hyphens, underscores).

    Returns:
        Path to the memory JSON file.

    Raises:
        ValueError: If agent_name or session_id contain invalid characters.
    """
    _validate_identifier(agent_name, "agent_name")
    _validate_identifier(session_id, "session_id")

    base_dir = Path.home() / ".claude" / "sessions" / session_id / "memory"
    return base_dir / f"{agent_name}.json"


def load_memory(agent_name: str, session_id: str) -> dict[str, Any]:
    """Load agent memory from disk.

    Reads the JSON memory file for the given agent and session. Returns an
    empty dict if the file does not exist or contains invalid JSON.

    Args:
        agent_name: Name of the agent.
        session_id: Session identifier.

    Returns:
        Dictionary of stored memory data, or empty dict if not found or corrupt.

    Raises:
        ValueError: If agent_name or session_id contain invalid characters.
    """
    memory_path = get_memory_path(agent_name, session_id)

    if not memory_path.is_file():
        logger.debug("Memory file not found: %s", memory_path)
        return {}

    try:
        raw = memory_path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        logger.warning("Corrupted memory file %s: %s", memory_path, exc)
        return {}
    except OSError as exc:
        logger.warning("Failed to read memory file %s: %s", memory_path, exc)
        return {}

    if not isinstance(data, dict):
        logger.warning("Memory file %s does not contain a JSON object", memory_path)
        return {}

    logger.debug("Loaded memory for agent=%s session=%s", agent_name, session_id)
    return data


def save_memory(agent_name: str, session_id: str, data: dict[str, Any]) -> Path:
    """Save agent memory to disk atomically.

    Writes the data as pretty-printed JSON using a temp-file-plus-rename
    pattern to prevent corruption if the process is interrupted mid-write.

    Args:
        agent_name: Name of the agent.
        session_id: Session identifier.
        data: Dictionary of memory data to persist.

    Returns:
        Path to the written memory file.

    Raises:
        ValueError: If agent_name or session_id contain invalid characters.
        TypeError: If data is not a dict.
        OSError: If the file cannot be written.
    """
    if not isinstance(data, dict):
        raise TypeError(f"data must be a dict, got {type(data).__name__}")

    memory_path = get_memory_path(agent_name, session_id)
    memory_path.parent.mkdir(parents=True, exist_ok=True)

    serialized = json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n"

    fd, temp_path = tempfile.mkstemp(
        dir=memory_path.parent,
        prefix=f".{memory_path.name}.",
        suffix=".tmp",
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(serialized)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(temp_path, memory_path)
    except Exception:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise

    logger.debug("Saved memory for agent=%s session=%s", agent_name, session_id)
    return memory_path


def clear_memory(agent_name: str, session_id: str) -> bool:
    """Delete agent memory file.

    Args:
        agent_name: Name of the agent.
        session_id: Session identifier.

    Returns:
        True if the memory file existed and was deleted, False otherwise.

    Raises:
        ValueError: If agent_name or session_id contain invalid characters.
        OSError: If the file exists but cannot be deleted.
    """
    memory_path = get_memory_path(agent_name, session_id)

    if not memory_path.is_file():
        logger.debug("No memory to clear for agent=%s session=%s", agent_name, session_id)
        return False

    memory_path.unlink()
    logger.debug("Cleared memory for agent=%s session=%s", agent_name, session_id)
    return True
