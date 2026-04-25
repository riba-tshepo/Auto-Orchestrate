"""
Heartbeat tracking system for agent liveness monitoring.

Provides functions to write, check, and clean up heartbeat files
that track whether agents are alive and responsive within a session.

Example:
    from layer1.heartbeat import write_heartbeat, check_heartbeat

    path = write_heartbeat("orchestrator", "session-123")
    status = check_heartbeat("orchestrator", "session-123")
    if status["is_stale"]:
        print(f"Agent stale for {status['age_seconds']:.1f}s")
"""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from layer0.constants import DEFAULT_SESSION_DIR

HEARTBEAT_SUBDIR = "heartbeats"
"""Subdirectory name within a session directory for heartbeat files."""

HEARTBEAT_FILENAME_SUFFIX = ".json"
"""File extension for heartbeat files."""

DEFAULT_STALENESS_THRESHOLD_SECONDS = 60
"""Default number of seconds before a heartbeat is considered stale."""

DEFAULT_CLEANUP_THRESHOLD_SECONDS = 300
"""Default number of seconds before a heartbeat is eligible for cleanup."""


def _heartbeat_dir(session_id: str, base_dir: str | Path | None = None) -> Path:
    """Resolve the heartbeat directory for a given session.

    Args:
        session_id: Unique session identifier.
        base_dir: Override for the sessions base directory. Uses
            DEFAULT_SESSION_DIR when None.

    Returns:
        Path to the heartbeats directory for the session.
    """
    base = Path(base_dir) if base_dir is not None else DEFAULT_SESSION_DIR
    return base / session_id / HEARTBEAT_SUBDIR


def _heartbeat_file(
    agent_name: str, session_id: str, base_dir: str | Path | None = None
) -> Path:
    """Resolve the heartbeat file path for a specific agent.

    Args:
        agent_name: Name of the agent (e.g. "orchestrator").
        session_id: Unique session identifier.
        base_dir: Override for the sessions base directory.

    Returns:
        Path to the agent's heartbeat JSON file.
    """
    return _heartbeat_dir(session_id, base_dir) / f"{agent_name}{HEARTBEAT_FILENAME_SUFFIX}"


def write_heartbeat(
    agent_name: str,
    session_id: str,
    base_dir: str | Path | None = None,
) -> Path:
    """Write a heartbeat file recording the current timestamp and PID.

    Creates the heartbeat directory structure if it does not exist.
    Uses an atomic write (temp file + rename) to prevent partial reads.

    Args:
        agent_name: Name of the agent writing the heartbeat.
        session_id: Unique session identifier.
        base_dir: Override for the sessions base directory. Uses
            DEFAULT_SESSION_DIR when None.

    Returns:
        Path to the written heartbeat file.

    Raises:
        OSError: If the heartbeat file or directories cannot be created.
    """
    hb_file = _heartbeat_file(agent_name, session_id, base_dir)
    hb_file.parent.mkdir(parents=True, exist_ok=True)

    payload: dict[str, Any] = {
        "agent_name": agent_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
    }

    content = json.dumps(payload, indent=2) + "\n"

    fd, temp_path = tempfile.mkstemp(
        dir=hb_file.parent, prefix=f".{hb_file.name}.", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(content)
        os.replace(temp_path, hb_file)
    except Exception:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise

    return hb_file


def check_heartbeat(
    agent_name: str,
    session_id: str,
    max_age_seconds: int = DEFAULT_STALENESS_THRESHOLD_SECONDS,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Check whether an agent's heartbeat is fresh or stale.

    Reads the heartbeat file for the given agent and computes the age
    relative to the current UTC time.

    Args:
        agent_name: Name of the agent to check.
        session_id: Unique session identifier.
        max_age_seconds: Maximum age in seconds before the heartbeat is
            considered stale.
        base_dir: Override for the sessions base directory.

    Returns:
        Dictionary with keys:
            - ``agent_name`` (str): The agent name.
            - ``timestamp`` (str | None): ISO-8601 timestamp from the
              heartbeat, or None if missing.
            - ``is_stale`` (bool): True when the heartbeat exceeds
              *max_age_seconds* or the file is missing/corrupt.
            - ``age_seconds`` (float | None): Seconds since the
              heartbeat was written, or None if unavailable.
            - ``pid`` (int | None): PID recorded in the heartbeat,
              or None if unavailable.
            - ``error`` (str | None): Description of any error
              encountered, or None on success.
    """
    hb_file = _heartbeat_file(agent_name, session_id, base_dir)

    result: dict[str, Any] = {
        "agent_name": agent_name,
        "timestamp": None,
        "is_stale": True,
        "age_seconds": None,
        "pid": None,
        "error": None,
    }

    if not hb_file.is_file():
        result["error"] = "heartbeat file not found"
        return result

    try:
        raw = hb_file.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (json.JSONDecodeError, OSError) as exc:
        result["error"] = f"failed to read heartbeat: {exc}"
        return result

    timestamp_str = data.get("timestamp")
    if not isinstance(timestamp_str, str):
        result["error"] = "heartbeat missing or invalid timestamp"
        return result

    try:
        heartbeat_time = datetime.fromisoformat(timestamp_str)
    except ValueError as exc:
        result["error"] = f"invalid timestamp format: {exc}"
        return result

    if heartbeat_time.tzinfo is None:
        heartbeat_time = heartbeat_time.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    age = (now - heartbeat_time).total_seconds()

    result["timestamp"] = timestamp_str
    result["age_seconds"] = age
    result["is_stale"] = age > max_age_seconds
    result["pid"] = data.get("pid")

    return result


def cleanup_stale_heartbeats(
    session_id: str,
    max_age_seconds: int = DEFAULT_CLEANUP_THRESHOLD_SECONDS,
    base_dir: str | Path | None = None,
) -> int:
    """Remove heartbeat files older than the specified threshold.

    Iterates over all ``*.json`` files in the session's heartbeats
    directory and deletes those whose timestamp exceeds *max_age_seconds*.
    Files that cannot be parsed are also removed.

    Args:
        session_id: Unique session identifier.
        max_age_seconds: Age threshold in seconds. Heartbeats older than
            this value are deleted.
        base_dir: Override for the sessions base directory.

    Returns:
        Number of heartbeat files removed.

    Raises:
        OSError: If a file cannot be deleted due to permission errors.
    """
    hb_dir = _heartbeat_dir(session_id, base_dir)

    if not hb_dir.is_dir():
        return 0

    removed = 0
    now = datetime.now(timezone.utc)

    for hb_file in hb_dir.glob(f"*{HEARTBEAT_FILENAME_SUFFIX}"):
        if not hb_file.is_file():
            continue

        should_remove = False

        try:
            raw = hb_file.read_text(encoding="utf-8")
            data = json.loads(raw)
            timestamp_str = data.get("timestamp")

            if not isinstance(timestamp_str, str):
                should_remove = True
            else:
                heartbeat_time = datetime.fromisoformat(timestamp_str)
                if heartbeat_time.tzinfo is None:
                    heartbeat_time = heartbeat_time.replace(tzinfo=timezone.utc)
                age = (now - heartbeat_time).total_seconds()
                should_remove = age > max_age_seconds
        except (json.JSONDecodeError, ValueError, OSError):
            should_remove = True

        if should_remove:
            hb_file.unlink()
            removed += 1

    return removed
