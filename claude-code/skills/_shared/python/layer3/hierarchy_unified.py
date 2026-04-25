"""
Unified task hierarchy operations.

This module provides consolidated functions for working with task parent-child
relationships, replacing scattered hierarchy operations across the codebase.

Example:
    from layer3.hierarchy_unified import get_task_children, get_task_ancestors

    children = get_task_children(tasks, "2")
    ancestors = get_task_ancestors(tasks, "2.3.1")
"""

from __future__ import annotations

from typing import Any

from layer2.task_ops import get_parent_id, parse_task_id


def get_task_children(
    tasks: list[dict[str, Any]],
    parent_id: str,
) -> list[dict[str, Any]]:
    """Get all direct children of a task.

    Args:
        tasks: List of task dictionaries.
        parent_id: Parent task ID to find children for.

    Returns:
        List of child task dictionaries.

    Example:
        >>> tasks = [
        ...     {"id": "2", "title": "Epic"},
        ...     {"id": "2.1", "title": "Subtask 1"},
        ...     {"id": "2.2", "title": "Subtask 2"},
        ... ]
        >>> children = get_task_children(tasks, "2")
        >>> len(children)
        2
    """
    return [task for task in tasks if task.get("parent_id") == parent_id]


def get_task_descendants(
    tasks: list[dict[str, Any]],
    parent_id: str,
) -> list[dict[str, Any]]:
    """Get all descendants (children, grandchildren, etc.) of a task.

    Args:
        tasks: List of task dictionaries.
        parent_id: Parent task ID to find descendants for.

    Returns:
        List of all descendant task dictionaries.

    Example:
        >>> tasks = [
        ...     {"id": "2", "title": "Epic"},
        ...     {"id": "2.1", "title": "Child"},
        ...     {"id": "2.1.1", "title": "Grandchild"},
        ... ]
        >>> descendants = get_task_descendants(tasks, "2")
        >>> len(descendants)
        2
    """
    descendants = []
    direct_children = get_task_children(tasks, parent_id)

    for child in direct_children:
        descendants.append(child)
        # Recursively get descendants of this child
        descendants.extend(get_task_descendants(tasks, child["id"]))

    return descendants


def get_task_ancestors(
    tasks: list[dict[str, Any]],
    task_id: str,
) -> list[dict[str, Any]]:
    """Get all ancestors (parent, grandparent, etc.) of a task.

    Args:
        tasks: List of task dictionaries.
        task_id: Task ID to find ancestors for.

    Returns:
        List of ancestor task dictionaries, ordered from immediate parent to epic.

    Example:
        >>> tasks = [
        ...     {"id": "2", "title": "Epic"},
        ...     {"id": "2.1", "title": "Parent"},
        ...     {"id": "2.1.1", "title": "Task"},
        ... ]
        >>> ancestors = get_task_ancestors(tasks, "2.1.1")
        >>> [a["id"] for a in ancestors]
        ['2.1', '2']
    """
    ancestors = []
    current_id = get_parent_id(task_id)

    while current_id:
        # Find task with this ID
        ancestor = next((t for t in tasks if t["id"] == current_id), None)
        if ancestor:
            ancestors.append(ancestor)
        current_id = get_parent_id(current_id)

    return ancestors


def get_task_siblings(
    tasks: list[dict[str, Any]],
    task_id: str,
) -> list[dict[str, Any]]:
    """Get all siblings (tasks with same parent) of a task.

    Args:
        tasks: List of task dictionaries.
        task_id: Task ID to find siblings for.

    Returns:
        List of sibling task dictionaries (excluding the task itself).

    Example:
        >>> tasks = [
        ...     {"id": "2.1", "title": "Sibling 1"},
        ...     {"id": "2.2", "title": "Me"},
        ...     {"id": "2.3", "title": "Sibling 2"},
        ... ]
        >>> siblings = get_task_siblings(tasks, "2.2")
        >>> [s["id"] for s in siblings]
        ['2.1', '2.3']
    """
    parent_id = get_parent_id(task_id)
    if not parent_id:
        # Task is an epic, has no siblings
        return []

    siblings = get_task_children(tasks, parent_id)
    return [s for s in siblings if s["id"] != task_id]


def get_epic_tasks(tasks: list[dict[str, Any]], epic_id: str) -> list[dict[str, Any]]:
    """Get all tasks belonging to an epic (including the epic itself).

    Args:
        tasks: List of task dictionaries.
        epic_id: Epic ID to find tasks for.

    Returns:
        List of all tasks in the epic (epic + all descendants).

    Example:
        >>> tasks = [
        ...     {"id": "2", "title": "Epic"},
        ...     {"id": "2.1", "title": "Task 1"},
        ...     {"id": "2.2", "title": "Task 2"},
        ...     {"id": "3", "title": "Other Epic"},
        ... ]
        >>> epic_tasks = get_epic_tasks(tasks, "2")
        >>> len(epic_tasks)
        3
    """
    epic = next((t for t in tasks if t["id"] == epic_id), None)
    if not epic:
        return []

    return [epic] + get_task_descendants(tasks, epic_id)


def count_task_tree(tasks: list[dict[str, Any]], parent_id: str) -> int:
    """Count total tasks in a subtree (parent + all descendants).

    Args:
        tasks: List of task dictionaries.
        parent_id: Parent task ID to count from.

    Returns:
        Total count of tasks in the tree.

    Example:
        >>> tasks = [
        ...     {"id": "2", "title": "Epic"},
        ...     {"id": "2.1", "title": "Child"},
        ...     {"id": "2.1.1", "title": "Grandchild"},
        ... ]
        >>> count_task_tree(tasks, "2")
        3
    """
    descendants = get_task_descendants(tasks, parent_id)
    return 1 + len(descendants)  # 1 for parent + descendants


def get_task_depth(task_id: str) -> int:
    """Get nesting depth of a task.

    Args:
        task_id: Task ID to check depth for.

    Returns:
        Depth level (0 for epic, 1 for subtask, etc.).

    Example:
        >>> get_task_depth("2")
        0
        >>> get_task_depth("2.1")
        1
        >>> get_task_depth("2.1.1")
        2
    """
    components = parse_task_id(task_id)
    return int(components.depth)


def find_task_by_id(
    tasks: list[dict[str, Any]],
    task_id: str,
) -> dict[str, Any] | None:
    """Find task by ID.

    Args:
        tasks: List of task dictionaries.
        task_id: Task ID to find.

    Returns:
        Task dictionary if found, None otherwise.

    Example:
        >>> tasks = [{"id": "2.1", "title": "Task"}]
        >>> task = find_task_by_id(tasks, "2.1")
        >>> task["title"]
        'Task'
    """
    return next((t for t in tasks if t["id"] == task_id), None)
