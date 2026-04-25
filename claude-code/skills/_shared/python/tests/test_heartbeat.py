"""Tests for the heartbeat liveness-monitoring module."""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from layer1.heartbeat import (
    DEFAULT_STALENESS_THRESHOLD_SECONDS,
    HEARTBEAT_SUBDIR,
    check_heartbeat,
    cleanup_stale_heartbeats,
    write_heartbeat,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def session_base(tmp_path: Path) -> Path:
    """Provide a temporary base directory that replaces ~/.claude/sessions."""
    return tmp_path / "sessions"


@pytest.fixture
def session_id() -> str:
    """Provide a deterministic session identifier for tests."""
    return "test-session-abc"


# ---------------------------------------------------------------------------
# write_heartbeat
# ---------------------------------------------------------------------------


class TestWriteHeartbeat:
    """Tests for write_heartbeat."""

    def test_creates_file_with_correct_json(
        self, session_base: Path, session_id: str
    ) -> None:
        """Heartbeat file is created with expected keys and values."""
        # Arrange / Act
        path = write_heartbeat("orchestrator", session_id, base_dir=session_base)

        # Assert
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["agent_name"] == "orchestrator"
        assert "timestamp" in data
        assert data["pid"] == os.getpid()

    def test_creates_directory_structure(
        self, session_base: Path, session_id: str
    ) -> None:
        """Parent directories are created automatically."""
        # Arrange - base does not exist yet
        assert not session_base.exists()

        # Act
        path = write_heartbeat("worker", session_id, base_dir=session_base)

        # Assert
        expected_dir = session_base / session_id / HEARTBEAT_SUBDIR
        assert expected_dir.is_dir()
        assert path.parent == expected_dir

    def test_overwrites_existing_heartbeat(
        self, session_base: Path, session_id: str
    ) -> None:
        """A second write replaces the first heartbeat atomically."""
        # Arrange
        write_heartbeat("agent-a", session_id, base_dir=session_base)

        # Act
        path = write_heartbeat("agent-a", session_id, base_dir=session_base)

        # Assert - only one file, content is valid JSON
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["agent_name"] == "agent-a"

    def test_timestamp_is_utc_iso_format(
        self, session_base: Path, session_id: str
    ) -> None:
        """Timestamp is a valid ISO-8601 string in UTC."""
        # Arrange / Act
        path = write_heartbeat("agent-b", session_id, base_dir=session_base)
        data = json.loads(path.read_text(encoding="utf-8"))

        # Assert
        ts = datetime.fromisoformat(data["timestamp"])
        assert ts.tzinfo is not None


# ---------------------------------------------------------------------------
# check_heartbeat
# ---------------------------------------------------------------------------


class TestCheckHeartbeat:
    """Tests for check_heartbeat."""

    def test_fresh_heartbeat_is_not_stale(
        self, session_base: Path, session_id: str
    ) -> None:
        """A just-written heartbeat should not be stale."""
        # Arrange
        write_heartbeat("agent-c", session_id, base_dir=session_base)

        # Act
        status = check_heartbeat(
            "agent-c", session_id, base_dir=session_base
        )

        # Assert
        assert status["is_stale"] is False
        assert status["timestamp"] is not None
        assert status["age_seconds"] is not None
        assert status["age_seconds"] < DEFAULT_STALENESS_THRESHOLD_SECONDS
        assert status["error"] is None

    def test_stale_heartbeat_detected(
        self, session_base: Path, session_id: str
    ) -> None:
        """An old heartbeat is flagged as stale."""
        # Arrange - write a heartbeat with a timestamp 120 seconds in the past
        hb_dir = session_base / session_id / HEARTBEAT_SUBDIR
        hb_dir.mkdir(parents=True, exist_ok=True)
        old_time = datetime.now(timezone.utc) - timedelta(seconds=120)
        payload = {
            "agent_name": "agent-d",
            "timestamp": old_time.isoformat(),
            "pid": 99999,
        }
        hb_file = hb_dir / "agent-d.json"
        hb_file.write_text(json.dumps(payload), encoding="utf-8")

        # Act
        status = check_heartbeat(
            "agent-d", session_id, max_age_seconds=60, base_dir=session_base
        )

        # Assert
        assert status["is_stale"] is True
        assert status["age_seconds"] is not None
        assert status["age_seconds"] >= 120
        assert status["error"] is None

    def test_missing_file_returns_stale_with_error(
        self, session_base: Path, session_id: str
    ) -> None:
        """A missing heartbeat file returns stale with an error message."""
        # Arrange - nothing written

        # Act
        status = check_heartbeat(
            "nonexistent", session_id, base_dir=session_base
        )

        # Assert
        assert status["is_stale"] is True
        assert status["timestamp"] is None
        assert status["age_seconds"] is None
        assert status["error"] is not None
        assert "not found" in status["error"]

    def test_corrupt_file_returns_stale_with_error(
        self, session_base: Path, session_id: str
    ) -> None:
        """A corrupt heartbeat file returns stale with an error message."""
        # Arrange
        hb_dir = session_base / session_id / HEARTBEAT_SUBDIR
        hb_dir.mkdir(parents=True, exist_ok=True)
        corrupt_file = hb_dir / "bad-agent.json"
        corrupt_file.write_text("{invalid json", encoding="utf-8")

        # Act
        status = check_heartbeat(
            "bad-agent", session_id, base_dir=session_base
        )

        # Assert
        assert status["is_stale"] is True
        assert status["error"] is not None
        assert "failed to read" in status["error"]

    def test_missing_timestamp_returns_stale_with_error(
        self, session_base: Path, session_id: str
    ) -> None:
        """A heartbeat file without a timestamp field returns stale."""
        # Arrange
        hb_dir = session_base / session_id / HEARTBEAT_SUBDIR
        hb_dir.mkdir(parents=True, exist_ok=True)
        hb_file = hb_dir / "no-ts-agent.json"
        hb_file.write_text(json.dumps({"agent_name": "no-ts-agent"}), encoding="utf-8")

        # Act
        status = check_heartbeat(
            "no-ts-agent", session_id, base_dir=session_base
        )

        # Assert
        assert status["is_stale"] is True
        assert status["error"] is not None
        assert "missing" in status["error"] or "invalid" in status["error"]

    def test_custom_max_age(
        self, session_base: Path, session_id: str
    ) -> None:
        """Custom max_age_seconds is respected."""
        # Arrange - write a heartbeat 3 seconds ago
        hb_dir = session_base / session_id / HEARTBEAT_SUBDIR
        hb_dir.mkdir(parents=True, exist_ok=True)
        old_time = datetime.now(timezone.utc) - timedelta(seconds=3)
        payload = {
            "agent_name": "agent-e",
            "timestamp": old_time.isoformat(),
            "pid": 11111,
        }
        hb_file = hb_dir / "agent-e.json"
        hb_file.write_text(json.dumps(payload), encoding="utf-8")

        # Act - threshold of 2 seconds means this is stale
        status_stale = check_heartbeat(
            "agent-e", session_id, max_age_seconds=2, base_dir=session_base
        )
        # Act - threshold of 10 seconds means this is fresh
        status_fresh = check_heartbeat(
            "agent-e", session_id, max_age_seconds=10, base_dir=session_base
        )

        # Assert
        assert status_stale["is_stale"] is True
        assert status_fresh["is_stale"] is False

    def test_returns_pid(
        self, session_base: Path, session_id: str
    ) -> None:
        """PID from the heartbeat file is included in the result."""
        # Arrange
        write_heartbeat("agent-f", session_id, base_dir=session_base)

        # Act
        status = check_heartbeat(
            "agent-f", session_id, base_dir=session_base
        )

        # Assert
        assert status["pid"] == os.getpid()


# ---------------------------------------------------------------------------
# cleanup_stale_heartbeats
# ---------------------------------------------------------------------------


class TestCleanupStaleHeartbeats:
    """Tests for cleanup_stale_heartbeats."""

    def test_removes_stale_files(
        self, session_base: Path, session_id: str
    ) -> None:
        """Heartbeats older than the threshold are removed."""
        # Arrange
        hb_dir = session_base / session_id / HEARTBEAT_SUBDIR
        hb_dir.mkdir(parents=True, exist_ok=True)
        old_time = datetime.now(timezone.utc) - timedelta(seconds=600)
        for name in ("stale-a", "stale-b"):
            payload = {
                "agent_name": name,
                "timestamp": old_time.isoformat(),
                "pid": 1,
            }
            (hb_dir / f"{name}.json").write_text(
                json.dumps(payload), encoding="utf-8"
            )

        # Act
        removed = cleanup_stale_heartbeats(
            session_id, max_age_seconds=300, base_dir=session_base
        )

        # Assert
        assert removed == 2
        assert not (hb_dir / "stale-a.json").exists()
        assert not (hb_dir / "stale-b.json").exists()

    def test_keeps_fresh_files(
        self, session_base: Path, session_id: str
    ) -> None:
        """Heartbeats within the threshold are not removed."""
        # Arrange
        write_heartbeat("fresh-agent", session_id, base_dir=session_base)

        # Act
        removed = cleanup_stale_heartbeats(
            session_id, max_age_seconds=300, base_dir=session_base
        )

        # Assert
        assert removed == 0
        hb_dir = session_base / session_id / HEARTBEAT_SUBDIR
        assert (hb_dir / "fresh-agent.json").exists()

    def test_removes_corrupt_files(
        self, session_base: Path, session_id: str
    ) -> None:
        """Corrupt heartbeat files are removed during cleanup."""
        # Arrange
        hb_dir = session_base / session_id / HEARTBEAT_SUBDIR
        hb_dir.mkdir(parents=True, exist_ok=True)
        (hb_dir / "corrupt.json").write_text("not json!", encoding="utf-8")

        # Act
        removed = cleanup_stale_heartbeats(
            session_id, max_age_seconds=300, base_dir=session_base
        )

        # Assert
        assert removed == 1
        assert not (hb_dir / "corrupt.json").exists()

    def test_missing_directory_returns_zero(
        self, session_base: Path, session_id: str
    ) -> None:
        """If the heartbeats directory does not exist, return 0."""
        # Arrange - no directory created

        # Act
        removed = cleanup_stale_heartbeats(
            session_id, base_dir=session_base
        )

        # Assert
        assert removed == 0

    def test_mixed_stale_and_fresh(
        self, session_base: Path, session_id: str
    ) -> None:
        """Only stale heartbeats are removed; fresh ones remain."""
        # Arrange
        hb_dir = session_base / session_id / HEARTBEAT_SUBDIR
        hb_dir.mkdir(parents=True, exist_ok=True)

        old_time = datetime.now(timezone.utc) - timedelta(seconds=400)
        stale_payload = {
            "agent_name": "stale-x",
            "timestamp": old_time.isoformat(),
            "pid": 2,
        }
        (hb_dir / "stale-x.json").write_text(
            json.dumps(stale_payload), encoding="utf-8"
        )

        write_heartbeat("fresh-y", session_id, base_dir=session_base)

        # Act
        removed = cleanup_stale_heartbeats(
            session_id, max_age_seconds=300, base_dir=session_base
        )

        # Assert
        assert removed == 1
        assert not (hb_dir / "stale-x.json").exists()
        assert (hb_dir / "fresh-y.json").exists()

    def test_files_without_timestamp_are_removed(
        self, session_base: Path, session_id: str
    ) -> None:
        """Heartbeat files missing a timestamp field are treated as stale."""
        # Arrange
        hb_dir = session_base / session_id / HEARTBEAT_SUBDIR
        hb_dir.mkdir(parents=True, exist_ok=True)
        (hb_dir / "no-ts.json").write_text(
            json.dumps({"agent_name": "no-ts"}), encoding="utf-8"
        )

        # Act
        removed = cleanup_stale_heartbeats(
            session_id, max_age_seconds=300, base_dir=session_base
        )

        # Assert
        assert removed == 1
