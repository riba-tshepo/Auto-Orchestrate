"""
Tests for layer1.memory module.

Tests persistent memory store for agents including save, load, clear,
atomic writes, corruption handling, and input validation.
"""

from __future__ import annotations

import json
import os
from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from layer1.memory import clear_memory, get_memory_path, load_memory, save_memory

AGENT = "test-agent"
SESSION = "sess-001"


@pytest.fixture()
def memory_home(tmp_path: Path) -> Generator[Path, None, None]:
    """Redirect HOME so memory files go to tmp_path."""
    with patch.dict(os.environ, {"HOME": str(tmp_path)}), \
         patch.object(Path, "home", return_value=tmp_path):
        yield tmp_path


# --- get_memory_path ---


def test_get_memory_path_structure(memory_home: Path) -> None:
    """get_memory_path returns the expected directory structure."""
    result = get_memory_path(AGENT, SESSION)
    expected = memory_home / ".claude" / "sessions" / SESSION / "memory" / f"{AGENT}.json"
    assert result == expected


def test_get_memory_path_rejects_empty_agent() -> None:
    """get_memory_path raises ValueError for empty agent_name."""
    with pytest.raises(ValueError, match="agent_name must not be empty"):
        get_memory_path("", SESSION)


def test_get_memory_path_rejects_empty_session() -> None:
    """get_memory_path raises ValueError for empty session_id."""
    with pytest.raises(ValueError, match="session_id must not be empty"):
        get_memory_path(AGENT, "")


def test_get_memory_path_rejects_path_traversal() -> None:
    """get_memory_path rejects identifiers with path traversal characters."""
    with pytest.raises(ValueError, match="agent_name must contain only"):
        get_memory_path("../etc/passwd", SESSION)

    with pytest.raises(ValueError, match="session_id must contain only"):
        get_memory_path(AGENT, "../../root")


def test_get_memory_path_rejects_slashes() -> None:
    """get_memory_path rejects identifiers containing slashes."""
    with pytest.raises(ValueError, match="agent_name must contain only"):
        get_memory_path("foo/bar", SESSION)


# --- save_memory ---


def test_save_memory_creates_file(memory_home: Path) -> None:
    """save_memory creates a JSON file with correct content."""
    data: dict[str, Any] = {"turn": 5, "status": "active"}
    result_path = save_memory(AGENT, SESSION, data)

    assert result_path.is_file()
    loaded = json.loads(result_path.read_text(encoding="utf-8"))
    assert loaded == data


def test_save_memory_creates_parent_dirs(memory_home: Path) -> None:
    """save_memory creates intermediate directories if they don't exist."""
    data: dict[str, Any] = {"key": "value"}
    result_path = save_memory("new-agent", "new-session", data)

    assert result_path.parent.is_dir()
    assert result_path.is_file()


def test_save_memory_pretty_prints(memory_home: Path) -> None:
    """save_memory writes pretty-printed JSON with sorted keys."""
    data: dict[str, Any] = {"zebra": 1, "alpha": 2}
    result_path = save_memory(AGENT, SESSION, data)

    raw = result_path.read_text(encoding="utf-8")
    assert raw == json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def test_save_memory_overwrites_existing(memory_home: Path) -> None:
    """save_memory overwrites previously saved data."""
    save_memory(AGENT, SESSION, {"old": True})
    save_memory(AGENT, SESSION, {"new": True})

    result_path = get_memory_path(AGENT, SESSION)
    loaded = json.loads(result_path.read_text(encoding="utf-8"))
    assert loaded == {"new": True}


def test_save_memory_rejects_non_dict(memory_home: Path) -> None:
    """save_memory raises TypeError when data is not a dict."""
    with pytest.raises(TypeError, match="data must be a dict"):
        save_memory(AGENT, SESSION, [1, 2, 3])  # type: ignore[arg-type]


def test_save_memory_atomic_write_no_partial_file(memory_home: Path) -> None:
    """Atomic write leaves no temp files on success."""
    save_memory(AGENT, SESSION, {"key": "value"})

    memory_dir = get_memory_path(AGENT, SESSION).parent
    tmp_files = list(memory_dir.glob(".*tmp"))
    assert tmp_files == []


def test_save_memory_returns_correct_path(memory_home: Path) -> None:
    """save_memory returns the same path as get_memory_path."""
    result_path = save_memory(AGENT, SESSION, {"a": 1})
    expected_path = get_memory_path(AGENT, SESSION)
    assert result_path == expected_path


# --- load_memory ---


def test_load_memory_returns_saved_data(memory_home: Path) -> None:
    """load_memory returns data previously saved with save_memory."""
    original: dict[str, Any] = {"turn": 10, "files": ["a.py", "b.py"]}
    save_memory(AGENT, SESSION, original)

    loaded = load_memory(AGENT, SESSION)
    assert loaded == original


def test_load_memory_returns_empty_dict_for_missing(memory_home: Path) -> None:
    """load_memory returns empty dict when no memory file exists."""
    result = load_memory("nonexistent-agent", "no-session")
    assert result == {}


def test_load_memory_returns_empty_dict_for_corrupted(memory_home: Path) -> None:
    """load_memory returns empty dict when file contains invalid JSON."""
    memory_path = get_memory_path(AGENT, SESSION)
    memory_path.parent.mkdir(parents=True, exist_ok=True)
    memory_path.write_text("{invalid json!!!", encoding="utf-8")

    result = load_memory(AGENT, SESSION)
    assert result == {}


def test_load_memory_returns_empty_dict_for_non_object(memory_home: Path) -> None:
    """load_memory returns empty dict when file contains a JSON array."""
    memory_path = get_memory_path(AGENT, SESSION)
    memory_path.parent.mkdir(parents=True, exist_ok=True)
    memory_path.write_text("[1, 2, 3]", encoding="utf-8")

    result = load_memory(AGENT, SESSION)
    assert result == {}


def test_load_memory_handles_empty_file(memory_home: Path) -> None:
    """load_memory returns empty dict for a zero-byte file."""
    memory_path = get_memory_path(AGENT, SESSION)
    memory_path.parent.mkdir(parents=True, exist_ok=True)
    memory_path.write_text("", encoding="utf-8")

    result = load_memory(AGENT, SESSION)
    assert result == {}


def test_load_memory_handles_unicode(memory_home: Path) -> None:
    """load_memory correctly handles Unicode characters."""
    data: dict[str, Any] = {"greeting": "Dumela"}
    save_memory(AGENT, SESSION, data)

    loaded = load_memory(AGENT, SESSION)
    assert loaded == data


# --- clear_memory ---


def test_clear_memory_removes_file(memory_home: Path) -> None:
    """clear_memory deletes the memory file and returns True."""
    save_memory(AGENT, SESSION, {"data": True})
    memory_path = get_memory_path(AGENT, SESSION)
    assert memory_path.is_file()

    result = clear_memory(AGENT, SESSION)
    assert result is True
    assert not memory_path.exists()


def test_clear_memory_returns_false_when_missing(memory_home: Path) -> None:
    """clear_memory returns False when no memory file exists."""
    result = clear_memory("no-agent", "no-session")
    assert result is False


def test_clear_memory_then_load_returns_empty(memory_home: Path) -> None:
    """After clear_memory, load_memory returns empty dict."""
    save_memory(AGENT, SESSION, {"important": "data"})
    clear_memory(AGENT, SESSION)

    result = load_memory(AGENT, SESSION)
    assert result == {}


# --- Round-trip integration ---


def test_full_round_trip(memory_home: Path) -> None:
    """Full save-load-update-load-clear cycle works correctly."""
    # Save initial data
    data_v1: dict[str, Any] = {"version": 1, "items": []}
    save_memory(AGENT, SESSION, data_v1)
    assert load_memory(AGENT, SESSION) == data_v1

    # Update data
    data_v2: dict[str, Any] = {"version": 2, "items": ["task-1"]}
    save_memory(AGENT, SESSION, data_v2)
    assert load_memory(AGENT, SESSION) == data_v2

    # Clear
    assert clear_memory(AGENT, SESSION) is True
    assert load_memory(AGENT, SESSION) == {}
    assert clear_memory(AGENT, SESSION) is False
