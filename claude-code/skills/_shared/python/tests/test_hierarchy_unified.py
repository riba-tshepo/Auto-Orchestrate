"""
Tests for layer3.hierarchy_unified module.

Tests task hierarchy operations including children, descendants, ancestors, and siblings.
"""

import pytest

from layer3.hierarchy_unified import (
    count_task_tree,
    find_task_by_id,
    get_epic_tasks,
    get_task_ancestors,
    get_task_children,
    get_task_depth,
    get_task_descendants,
    get_task_siblings,
)


@pytest.fixture
def sample_tasks():
    """Provide sample task hierarchy for testing."""
    return [
        {"id": "2", "title": "Epic 2", "parent_id": None},
        {"id": "2.1", "title": "Task 2.1", "parent_id": "2"},
        {"id": "2.2", "title": "Task 2.2", "parent_id": "2"},
        {"id": "2.1.1", "title": "Task 2.1.1", "parent_id": "2.1"},
        {"id": "2.1.2", "title": "Task 2.1.2", "parent_id": "2.1"},
        {"id": "3", "title": "Epic 3", "parent_id": None},
    ]


def test_get_task_children(sample_tasks):
    """Test getting direct children of a task."""
    children = get_task_children(sample_tasks, "2")

    assert len(children) == 2
    assert any(t["id"] == "2.1" for t in children)
    assert any(t["id"] == "2.2" for t in children)


def test_get_task_children_nested(sample_tasks):
    """Test getting children of a nested task."""
    children = get_task_children(sample_tasks, "2.1")

    assert len(children) == 2
    assert any(t["id"] == "2.1.1" for t in children)


def test_get_task_descendants(sample_tasks):
    """Test getting all descendants of a task."""
    descendants = get_task_descendants(sample_tasks, "2")

    # Should get 2.1, 2.2, 2.1.1, 2.1.2
    assert len(descendants) == 4
    ids = [t["id"] for t in descendants]
    assert "2.1" in ids
    assert "2.2" in ids
    assert "2.1.1" in ids
    assert "2.1.2" in ids


def test_get_task_ancestors(sample_tasks):
    """Test getting ancestors of a nested task."""
    ancestors = get_task_ancestors(sample_tasks, "2.1.1")

    # Should get 2.1 (parent) and 2 (epic)
    assert len(ancestors) == 2
    assert ancestors[0]["id"] == "2.1"
    assert ancestors[1]["id"] == "2"


def test_get_task_ancestors_epic(sample_tasks):
    """Test that epic has no ancestors."""
    ancestors = get_task_ancestors(sample_tasks, "2")
    assert len(ancestors) == 0


def test_get_task_siblings(sample_tasks):
    """Test getting siblings of a task."""
    siblings = get_task_siblings(sample_tasks, "2.1")

    assert len(siblings) == 1
    assert siblings[0]["id"] == "2.2"


def test_get_task_siblings_epic(sample_tasks):
    """Test that epic has no siblings."""
    siblings = get_task_siblings(sample_tasks, "2")
    assert len(siblings) == 0


def test_get_epic_tasks(sample_tasks):
    """Test getting all tasks in an epic."""
    epic_tasks = get_epic_tasks(sample_tasks, "2")

    # Should include epic itself + 4 descendants
    assert len(epic_tasks) == 5
    ids = [t["id"] for t in epic_tasks]
    assert "2" in ids
    assert "2.1" in ids
    assert "2.1.1" in ids


def test_count_task_tree(sample_tasks):
    """Test counting tasks in a subtree."""
    count = count_task_tree(sample_tasks, "2")
    assert count == 5  # 2 + 2.1 + 2.2 + 2.1.1 + 2.1.2

    count = count_task_tree(sample_tasks, "2.1")
    assert count == 3  # 2.1 + 2.1.1 + 2.1.2


def test_get_task_depth():
    """Test getting task depth."""
    assert get_task_depth("2") == 0
    assert get_task_depth("2.1") == 1
    assert get_task_depth("2.1.1") == 2
    assert get_task_depth("2.1.1.1") == 3


def test_find_task_by_id(sample_tasks):
    """Test finding a task by ID."""
    task = find_task_by_id(sample_tasks, "2.1")

    assert task is not None
    assert task["id"] == "2.1"
    assert task["title"] == "Task 2.1"


def test_find_task_by_id_not_found(sample_tasks):
    """Test finding nonexistent task returns None."""
    task = find_task_by_id(sample_tasks, "99.99")
    assert task is None
