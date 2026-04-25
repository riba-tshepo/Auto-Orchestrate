"""
Tests for layer2.task_ops module.

Tests task ID parsing and validation utilities.
"""

import pytest

from layer2.task_ops import (
    VALID_TASK_STATUSES,
    InvalidTaskIdError,
    InvalidTaskStatusError,
    format_task_reference,
    get_epic_id,
    get_parent_id,
    is_epic,
    parse_task_id,
    validate_task_status,
)


def test_parse_task_id_epic():
    """Test parsing an epic-level task ID."""
    components = parse_task_id("2")

    assert components.full_id == "2"
    assert components.epic_id == "2"
    assert components.parent_id is None
    assert components.depth == 0


def test_parse_task_id_subtask():
    """Test parsing a subtask ID."""
    components = parse_task_id("2.3")

    assert components.full_id == "2.3"
    assert components.epic_id == "2"
    assert components.parent_id == "2"
    assert components.depth == 1


def test_parse_task_id_nested():
    """Test parsing a deeply nested task ID."""
    components = parse_task_id("2.3.1")

    assert components.full_id == "2.3.1"
    assert components.epic_id == "2"
    assert components.parent_id == "2.3"
    assert components.depth == 2


def test_parse_task_id_invalid_empty():
    """Test that empty task ID raises error."""
    with pytest.raises(InvalidTaskIdError):
        parse_task_id("")


def test_parse_task_id_invalid_format():
    """Test that invalid format raises error."""
    with pytest.raises(InvalidTaskIdError):
        parse_task_id("abc")

    with pytest.raises(InvalidTaskIdError):
        parse_task_id("1.2.a")


def test_validate_task_status_valid():
    """Test validation of valid task statuses."""
    for status in VALID_TASK_STATUSES:
        assert validate_task_status(status) is True


def test_validate_task_status_invalid():
    """Test that invalid status raises error."""
    with pytest.raises(InvalidTaskStatusError):
        validate_task_status("invalid_status")

    with pytest.raises(InvalidTaskStatusError):
        validate_task_status("")


def test_is_epic():
    """Test is_epic() function."""
    assert is_epic("2") is True
    assert is_epic("10") is True
    assert is_epic("2.3") is False
    assert is_epic("2.3.1") is False


def test_get_parent_id():
    """Test get_parent_id() extraction."""
    assert get_parent_id("2") is None
    assert get_parent_id("2.3") == "2"
    assert get_parent_id("2.3.1") == "2.3"


def test_get_epic_id():
    """Test get_epic_id() extraction."""
    assert get_epic_id("2") == "2"
    assert get_epic_id("2.3") == "2"
    assert get_epic_id("2.3.1") == "2"


def test_format_task_reference():
    """Test format_task_reference() output."""
    result = format_task_reference("2.3", "Implement feature")
    assert result == "Task 2.3: Implement feature"
    assert "2.3" in result
    assert "Implement feature" in result
