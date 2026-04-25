"""
Inter-agent messaging module for file-based message passing.

Provides send, receive, broadcast, peek, and agent discovery
functions using a file-based queue under ~/.claude/sessions/.
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SESSIONS_DIR_NAME = "sessions"
MESSAGES_DIR_NAME = "messages"
PENDING_DIR_NAME = "pending"
PROCESSED_DIR_NAME = "processed"
MESSAGE_FILE_SUFFIX = ".json"
MESSAGE_ENCODING = "utf-8"


def _get_claude_home() -> Path:
    """Return the base Claude configuration directory.

    Returns:
        Path to ~/.claude directory.
    """
    return Path.home() / ".claude"


def _get_messages_root(session_id: str) -> Path:
    """Return the messages root directory for a session.

    Args:
        session_id: Session identifier.

    Returns:
        Path to the messages directory for the given session.
    """
    return _get_claude_home() / SESSIONS_DIR_NAME / session_id / MESSAGES_DIR_NAME


def _get_agent_dir(session_id: str, agent_name: str) -> Path:
    """Return the agent's message directory.

    Args:
        session_id: Session identifier.
        agent_name: Name of the agent.

    Returns:
        Path to the agent's message directory.
    """
    return _get_messages_root(session_id) / agent_name


def _get_pending_dir(session_id: str, agent_name: str) -> Path:
    """Return the agent's pending messages directory.

    Args:
        session_id: Session identifier.
        agent_name: Name of the agent.

    Returns:
        Path to the pending directory.
    """
    return _get_agent_dir(session_id, agent_name) / PENDING_DIR_NAME


def _get_processed_dir(session_id: str, agent_name: str) -> Path:
    """Return the agent's processed messages directory.

    Args:
        session_id: Session identifier.
        agent_name: Name of the agent.

    Returns:
        Path to the processed directory.
    """
    return _get_agent_dir(session_id, agent_name) / PROCESSED_DIR_NAME


def _validate_identifier(value: str, name: str) -> None:
    """Validate that an identifier is safe for filesystem use.

    Args:
        value: The identifier string to validate.
        name: Human-readable name for error messages.

    Raises:
        ValueError: If the identifier is empty or contains unsafe characters.
    """
    if not value or not value.strip():
        raise ValueError(f"{name} must not be empty")
    forbidden = {".", "..", "/", "\\", "\x00"}
    if value in forbidden or "/" in value or "\\" in value or "\x00" in value:
        raise ValueError(
            f"{name} contains forbidden characters: {value!r}"
        )


def _build_message(
    from_agent: str,
    to_agent: str,
    payload: dict[str, Any],
    message_id: str,
    timestamp: str,
) -> dict[str, Any]:
    """Build a message dictionary.

    Args:
        from_agent: Sender agent name.
        to_agent: Recipient agent name.
        payload: Message payload.
        message_id: Unique message identifier.
        timestamp: ISO-8601 timestamp string.

    Returns:
        Complete message dictionary.
    """
    return {
        "message_id": message_id,
        "from_agent": from_agent,
        "to_agent": to_agent,
        "timestamp": timestamp,
        "payload": payload,
    }


def _atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    """Write JSON data atomically using temp file + rename.

    Args:
        path: Destination file path.
        data: Dictionary to serialize as JSON.

    Raises:
        OSError: If the write or rename fails.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_path = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    try:
        with os.fdopen(fd, "w", encoding=MESSAGE_ENCODING) as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        os.replace(temp_path, path)
    except Exception:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise


def _read_message_file(path: Path) -> dict[str, Any] | None:
    """Read and parse a message JSON file.

    Args:
        path: Path to the message file.

    Returns:
        Parsed message dictionary, or None if the file is unreadable.
    """
    try:
        text = path.read_text(encoding=MESSAGE_ENCODING)
        data: dict[str, Any] = json.loads(text)
        return data
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Failed to read message file %s: %s", path, exc)
        return None


def _list_message_files(directory: Path) -> list[Path]:
    """List message files in a directory sorted by filename (FIFO).

    Args:
        directory: Directory to scan.

    Returns:
        List of message file paths sorted by name (timestamp prefix).
    """
    if not directory.is_dir():
        return []
    files = [
        f for f in directory.iterdir()
        if f.is_file() and f.suffix == MESSAGE_FILE_SUFFIX and not f.name.startswith(".")
    ]
    files.sort(key=lambda p: p.name)
    return files


def send_message(
    from_agent: str,
    to_agent: str,
    message: dict[str, Any],
    session_id: str,
) -> str:
    """Send a message to another agent.

    Creates a JSON file in the recipient agent's pending/ directory
    using atomic writes (temp file + rename).

    Args:
        from_agent: Name of the sending agent.
        to_agent: Name of the receiving agent.
        message: Payload dictionary to send.
        session_id: Current session identifier.

    Returns:
        The generated message_id (UUID string).

    Raises:
        ValueError: If agent names or session_id are invalid.
    """
    _validate_identifier(from_agent, "from_agent")
    _validate_identifier(to_agent, "to_agent")
    _validate_identifier(session_id, "session_id")

    message_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()
    timestamp_prefix = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")

    msg = _build_message(from_agent, to_agent, message, message_id, timestamp)

    filename = f"{timestamp_prefix}_{message_id}{MESSAGE_FILE_SUFFIX}"
    pending_dir = _get_pending_dir(session_id, to_agent)
    file_path = pending_dir / filename

    _atomic_write_json(file_path, msg)
    logger.info(
        "Message %s sent from %s to %s", message_id, from_agent, to_agent
    )
    return message_id


def receive_messages(
    agent_name: str, session_id: str
) -> list[dict[str, Any]]:
    """Receive all pending messages for an agent.

    Reads all files from the agent's pending/ directory, moves them
    to processed/, and returns them sorted by timestamp (FIFO).

    Args:
        agent_name: Name of the receiving agent.
        session_id: Current session identifier.

    Returns:
        List of message dictionaries sorted by timestamp (oldest first).
    """
    _validate_identifier(agent_name, "agent_name")
    _validate_identifier(session_id, "session_id")

    pending_dir = _get_pending_dir(session_id, agent_name)
    processed_dir = _get_processed_dir(session_id, agent_name)

    files = _list_message_files(pending_dir)
    if not files:
        return []

    processed_dir.mkdir(parents=True, exist_ok=True)

    messages: list[dict[str, Any]] = []
    for file_path in files:
        msg = _read_message_file(file_path)
        if msg is not None:
            messages.append(msg)
            dest = processed_dir / file_path.name
            try:
                file_path.rename(dest)
            except OSError as exc:
                logger.warning(
                    "Failed to move message %s to processed: %s",
                    file_path.name,
                    exc,
                )
        else:
            logger.warning("Skipping unreadable message file: %s", file_path)

    logger.info(
        "Agent %s received %d message(s)", agent_name, len(messages)
    )
    return messages


def peek_messages(
    agent_name: str, session_id: str
) -> list[dict[str, Any]]:
    """Peek at pending messages without consuming them.

    Reads all files from the agent's pending/ directory without
    moving them to processed/.

    Args:
        agent_name: Name of the agent.
        session_id: Current session identifier.

    Returns:
        List of message dictionaries sorted by timestamp (oldest first).
    """
    _validate_identifier(agent_name, "agent_name")
    _validate_identifier(session_id, "session_id")

    pending_dir = _get_pending_dir(session_id, agent_name)
    files = _list_message_files(pending_dir)

    messages: list[dict[str, Any]] = []
    for file_path in files:
        msg = _read_message_file(file_path)
        if msg is not None:
            messages.append(msg)

    return messages


def get_known_agents(session_id: str) -> list[str]:
    """List agents that have message directories.

    Scans the session's messages/ directory for agent subdirectories.

    Args:
        session_id: Current session identifier.

    Returns:
        Sorted list of agent names with message directories.
    """
    _validate_identifier(session_id, "session_id")

    messages_root = _get_messages_root(session_id)
    if not messages_root.is_dir():
        return []

    agents = [
        entry.name
        for entry in messages_root.iterdir()
        if entry.is_dir() and not entry.name.startswith(".")
    ]
    agents.sort()
    return agents


def broadcast_message(
    from_agent: str,
    message: dict[str, Any],
    session_id: str,
    exclude: list[str] | None = None,
) -> int:
    """Broadcast a message to all known agent queues.

    Sends the message to every known agent except the sender and
    any agents in the exclude list.

    Args:
        from_agent: Name of the sending agent.
        message: Payload dictionary to broadcast.
        session_id: Current session identifier.
        exclude: Optional list of agent names to exclude.

    Returns:
        Number of agents the message was sent to.
    """
    _validate_identifier(from_agent, "from_agent")
    _validate_identifier(session_id, "session_id")

    excluded_set = {from_agent}
    if exclude:
        excluded_set.update(exclude)

    agents = get_known_agents(session_id)
    count = 0
    for agent in agents:
        if agent not in excluded_set:
            send_message(from_agent, agent, message, session_id)
            count += 1

    logger.info(
        "Broadcast from %s to %d agent(s)", from_agent, count
    )
    return count
