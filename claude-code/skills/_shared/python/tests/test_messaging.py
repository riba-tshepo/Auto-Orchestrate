"""
Tests for layer2.messaging module.

Tests file-based inter-agent messaging: send, receive, broadcast, peek.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from layer2.messaging import (
    MESSAGE_FILE_SUFFIX,
    MESSAGES_DIR_NAME,
    PENDING_DIR_NAME,
    PROCESSED_DIR_NAME,
    SESSIONS_DIR_NAME,
    _validate_identifier,
    broadcast_message,
    get_known_agents,
    peek_messages,
    receive_messages,
    send_message,
)

SESSION_ID = "test-session-001"


def _patch_claude_home(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    """Patch _get_claude_home to use tmp_path as the base directory.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
        tmp_path: Pytest tmp_path fixture.

    Returns:
        The fake .claude home directory path.
    """
    claude_home = tmp_path / ".claude"
    claude_home.mkdir()
    monkeypatch.setattr(
        "layer2.messaging._get_claude_home", lambda: claude_home
    )
    return claude_home


def _messages_root(claude_home: Path, session_id: str) -> Path:
    """Return the messages root for a given session under the fake home.

    Args:
        claude_home: Fake .claude home directory.
        session_id: Session identifier.

    Returns:
        Path to the messages root directory.
    """
    return Path(claude_home / SESSIONS_DIR_NAME / session_id / MESSAGES_DIR_NAME)


def _read_json(path: Path) -> dict[str, Any]:
    """Read and parse a JSON file.

    Args:
        path: Path to JSON file.

    Returns:
        Parsed dictionary.
    """
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


class TestSendMessage:
    """Tests for the send_message function."""

    def test_creates_file_in_pending_directory(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """send_message creates a JSON file in the recipient's pending dir."""
        # Arrange
        claude_home = _patch_claude_home(monkeypatch, tmp_path)
        payload = {"type": "task_complete", "task_id": "5"}

        # Act
        message_id = send_message("orchestrator", "software-engineer", payload, SESSION_ID)

        # Assert
        pending_dir = (
            _messages_root(claude_home, SESSION_ID) / "software-engineer" / PENDING_DIR_NAME
        )
        assert pending_dir.is_dir()
        files = list(pending_dir.glob(f"*{MESSAGE_FILE_SUFFIX}"))
        assert len(files) == 1
        assert message_id in files[0].name

    def test_message_contains_required_fields(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Written message file has all required fields."""
        # Arrange
        claude_home = _patch_claude_home(monkeypatch, tmp_path)
        payload = {"action": "start"}

        # Act
        message_id = send_message("agent_a", "agent_b", payload, SESSION_ID)

        # Assert
        pending_dir = (
            _messages_root(claude_home, SESSION_ID) / "agent_b" / PENDING_DIR_NAME
        )
        files = list(pending_dir.glob(f"*{MESSAGE_FILE_SUFFIX}"))
        msg = _read_json(files[0])
        assert msg["message_id"] == message_id
        assert msg["from_agent"] == "agent_a"
        assert msg["to_agent"] == "agent_b"
        assert msg["timestamp"]
        assert msg["payload"] == payload

    def test_rejects_empty_agent_name(self) -> None:
        """send_message rejects empty agent names."""
        with pytest.raises(ValueError, match="must not be empty"):
            send_message("", "agent_b", {}, SESSION_ID)

    def test_rejects_agent_name_with_slash(self) -> None:
        """send_message rejects agent names with path separators."""
        with pytest.raises(ValueError, match="forbidden characters"):
            send_message("agent_a", "../etc", {}, SESSION_ID)

    def test_rejects_empty_session_id(self) -> None:
        """send_message rejects empty session IDs."""
        with pytest.raises(ValueError, match="must not be empty"):
            send_message("agent_a", "agent_b", {}, "")


class TestReceiveMessages:
    """Tests for the receive_messages function."""

    def test_returns_messages_in_fifo_order(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """receive_messages returns messages oldest-first."""
        # Arrange
        _patch_claude_home(monkeypatch, tmp_path)
        send_message("a", "receiver", {"seq": 1}, SESSION_ID)
        send_message("b", "receiver", {"seq": 2}, SESSION_ID)
        send_message("c", "receiver", {"seq": 3}, SESSION_ID)

        # Act
        messages = receive_messages("receiver", SESSION_ID)

        # Assert
        assert len(messages) == 3
        assert messages[0]["payload"]["seq"] == 1
        assert messages[1]["payload"]["seq"] == 2
        assert messages[2]["payload"]["seq"] == 3

    def test_moves_files_to_processed(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """receive_messages moves files from pending/ to processed/."""
        # Arrange
        claude_home = _patch_claude_home(monkeypatch, tmp_path)
        send_message("sender", "consumer", {"data": "test"}, SESSION_ID)

        root = _messages_root(claude_home, SESSION_ID)
        pending = root / "consumer" / PENDING_DIR_NAME
        processed = root / "consumer" / PROCESSED_DIR_NAME
        assert len(list(pending.glob(f"*{MESSAGE_FILE_SUFFIX}"))) == 1

        # Act
        messages = receive_messages("consumer", SESSION_ID)

        # Assert
        assert len(messages) == 1
        remaining_pending = list(pending.glob(f"*{MESSAGE_FILE_SUFFIX}"))
        assert len(remaining_pending) == 0
        processed_files = list(processed.glob(f"*{MESSAGE_FILE_SUFFIX}"))
        assert len(processed_files) == 1

    def test_empty_queue_returns_empty_list(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """receive_messages returns empty list when no messages exist."""
        # Arrange
        _patch_claude_home(monkeypatch, tmp_path)

        # Act
        messages = receive_messages("nobody", SESSION_ID)

        # Assert
        assert messages == []

    def test_second_receive_returns_empty(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Second call to receive_messages returns empty (messages consumed)."""
        # Arrange
        _patch_claude_home(monkeypatch, tmp_path)
        send_message("sender", "consumer", {"data": "once"}, SESSION_ID)

        # Act
        first = receive_messages("consumer", SESSION_ID)
        second = receive_messages("consumer", SESSION_ID)

        # Assert
        assert len(first) == 1
        assert second == []


class TestPeekMessages:
    """Tests for the peek_messages function."""

    def test_does_not_consume_messages(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """peek_messages reads messages without moving them."""
        # Arrange
        claude_home = _patch_claude_home(monkeypatch, tmp_path)
        send_message("sender", "peeked", {"info": "hello"}, SESSION_ID)

        # Act
        peeked = peek_messages("peeked", SESSION_ID)

        # Assert
        assert len(peeked) == 1
        assert peeked[0]["payload"]["info"] == "hello"
        # Verify file still in pending
        pending = (
            _messages_root(claude_home, SESSION_ID)
            / "peeked"
            / PENDING_DIR_NAME
        )
        assert len(list(pending.glob(f"*{MESSAGE_FILE_SUFFIX}"))) == 1

    def test_peek_then_receive_works(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """After peeking, receive still returns the messages."""
        # Arrange
        _patch_claude_home(monkeypatch, tmp_path)
        send_message("sender", "target", {"val": 42}, SESSION_ID)

        # Act
        peeked = peek_messages("target", SESSION_ID)
        received = receive_messages("target", SESSION_ID)

        # Assert
        assert len(peeked) == 1
        assert len(received) == 1
        assert peeked[0]["message_id"] == received[0]["message_id"]

    def test_peek_empty_queue(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """peek_messages returns empty list for non-existent agent."""
        # Arrange
        _patch_claude_home(monkeypatch, tmp_path)

        # Act
        result = peek_messages("ghost", SESSION_ID)

        # Assert
        assert result == []


class TestGetKnownAgents:
    """Tests for the get_known_agents function."""

    def test_lists_agent_directories(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """get_known_agents returns names of agents with message dirs."""
        # Arrange
        _patch_claude_home(monkeypatch, tmp_path)
        send_message("alpha", "beta", {"x": 1}, SESSION_ID)
        send_message("alpha", "gamma", {"x": 2}, SESSION_ID)

        # Act
        agents = get_known_agents(SESSION_ID)

        # Assert
        assert "beta" in agents
        assert "gamma" in agents

    def test_returns_empty_for_unknown_session(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """get_known_agents returns empty list for non-existent session."""
        # Arrange
        _patch_claude_home(monkeypatch, tmp_path)

        # Act
        agents = get_known_agents("nonexistent-session")

        # Assert
        assert agents == []

    def test_returns_sorted(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """get_known_agents returns agent names in sorted order."""
        # Arrange
        _patch_claude_home(monkeypatch, tmp_path)
        send_message("x", "charlie", {}, SESSION_ID)
        send_message("x", "alpha", {}, SESSION_ID)
        send_message("x", "bravo", {}, SESSION_ID)

        # Act
        agents = get_known_agents(SESSION_ID)

        # Assert
        assert agents == sorted(agents)


class TestBroadcastMessage:
    """Tests for the broadcast_message function."""

    def test_sends_to_all_known_agents(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """broadcast_message sends to all agents except the sender."""
        # Arrange
        _patch_claude_home(monkeypatch, tmp_path)
        # Create known agents by sending initial messages
        send_message("setup", "agent_a", {"init": True}, SESSION_ID)
        send_message("setup", "agent_b", {"init": True}, SESSION_ID)
        send_message("setup", "broadcaster", {"init": True}, SESSION_ID)
        # Consume the setup messages
        receive_messages("agent_a", SESSION_ID)
        receive_messages("agent_b", SESSION_ID)

        # Act
        count = broadcast_message(
            "broadcaster", {"event": "shutdown"}, SESSION_ID
        )

        # Assert
        assert count == 2  # agent_a and agent_b, not broadcaster
        msgs_a = receive_messages("agent_a", SESSION_ID)
        msgs_b = receive_messages("agent_b", SESSION_ID)
        assert len(msgs_a) == 1
        assert msgs_a[0]["payload"]["event"] == "shutdown"
        assert len(msgs_b) == 1

    def test_respects_exclude_list(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """broadcast_message skips agents in the exclude list."""
        # Arrange
        _patch_claude_home(monkeypatch, tmp_path)
        send_message("setup", "agent_x", {}, SESSION_ID)
        send_message("setup", "agent_y", {}, SESSION_ID)
        send_message("setup", "agent_z", {}, SESSION_ID)
        receive_messages("agent_x", SESSION_ID)
        receive_messages("agent_y", SESSION_ID)
        receive_messages("agent_z", SESSION_ID)

        # Act
        count = broadcast_message(
            "broadcaster",
            {"event": "update"},
            SESSION_ID,
            exclude=["agent_y"],
        )

        # Assert — known agents are agent_x, agent_y, agent_z;
        # broadcaster is excluded as from_agent, agent_y is in exclude list
        assert count == 2  # agent_x and agent_z only
        msgs_y = peek_messages("agent_y", SESSION_ID)
        # agent_y should have no new messages (only had setup which was consumed)
        assert len(msgs_y) == 0

    def test_broadcast_to_empty_session(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """broadcast_message returns 0 when no known agents exist."""
        # Arrange
        _patch_claude_home(monkeypatch, tmp_path)

        # Act
        count = broadcast_message(
            "lonely_agent", {"hello": "anyone?"}, SESSION_ID
        )

        # Assert
        assert count == 0


class TestValidateIdentifier:
    """Tests for the _validate_identifier helper."""

    def test_rejects_empty_string(self) -> None:
        """Empty strings are rejected."""
        with pytest.raises(ValueError, match="must not be empty"):
            _validate_identifier("", "test_field")

    def test_rejects_whitespace_only(self) -> None:
        """Whitespace-only strings are rejected."""
        with pytest.raises(ValueError, match="must not be empty"):
            _validate_identifier("   ", "test_field")

    def test_rejects_path_traversal(self) -> None:
        """Path traversal attempts are rejected."""
        with pytest.raises(ValueError, match="forbidden characters"):
            _validate_identifier("../secret", "test_field")

    def test_rejects_null_byte(self) -> None:
        """Null bytes are rejected."""
        with pytest.raises(ValueError, match="forbidden characters"):
            _validate_identifier("agent\x00evil", "test_field")

    def test_accepts_valid_names(self) -> None:
        """Valid agent-style names pass validation."""
        _validate_identifier("orchestrator", "test_field")
        _validate_identifier("agent-1", "test_field")
        _validate_identifier("my_agent_v2", "test_field")
