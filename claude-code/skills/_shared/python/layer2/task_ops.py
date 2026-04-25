"""
Task operations utilities.

This module provides helper functions for working with Claude Code's
native task system. These utilities simplify common task-related operations.

Note: This module provides UTILITIES for working with tasks, not a TaskList
implementation. Claude Code's TaskList is a native tool, not a Python class.

Example:
    from layer2.task_ops import parse_task_id, validate_task_status

    is_valid = parse_task_id("2.3.1")
    validate_task_status("completed")
"""

from __future__ import annotations

import re
from dataclasses import dataclass


class TaskOperationError(Exception):
    """Base exception for task operation errors."""

    pass


class InvalidTaskIdError(TaskOperationError):
    """Raised when task ID format is invalid."""

    pass


class InvalidTaskStatusError(TaskOperationError):
    """Raised when task status is invalid."""

    pass


# Valid task statuses
VALID_TASK_STATUSES = {
    "pending",
    "in_progress",
    "completed",
    "blocked",
    "cancelled",
}


@dataclass
class TaskIdComponents:
    """Parsed components of a task ID.

    Attributes:
        full_id: Complete task ID (e.g., "2.3.1").
        parent_id: Parent task ID if exists (e.g., "2.3").
        epic_id: Top-level epic ID (e.g., "2").
        depth: Nesting depth (0 for epic, 1 for subtask, etc.).
    """

    full_id: str
    parent_id: str | None
    epic_id: str
    depth: int


def parse_task_id(task_id: str) -> TaskIdComponents:
    """Parse task ID into components.

    Args:
        task_id: Task ID to parse (e.g., "2.3.1").

    Returns:
        TaskIdComponents with parsed information.

    Raises:
        InvalidTaskIdError: If task ID format is invalid.

    Example:
        >>> components = parse_task_id("2.3.1")
        >>> print(components.epic_id)
        '2'
        >>> print(components.depth)
        2
    """
    if not task_id:
        raise InvalidTaskIdError("Task ID cannot be empty")

    # Task ID format: N or N.M or N.M.P (numeric components separated by dots)
    if not re.match(r"^\d+(\.\d+)*$", task_id):
        raise InvalidTaskIdError(f"Invalid task ID format: {task_id}")

    parts = task_id.split(".")
    depth = len(parts) - 1
    epic_id = parts[0]
    parent_id = ".".join(parts[:-1]) if depth > 0 else None

    return TaskIdComponents(
        full_id=task_id,
        parent_id=parent_id,
        epic_id=epic_id,
        depth=depth,
    )


def validate_task_status(status: str) -> bool:
    """Validate task status value.

    Args:
        status: Status string to validate.

    Returns:
        True if status is valid.

    Raises:
        InvalidTaskStatusError: If status is not valid.

    Example:
        >>> validate_task_status("completed")
        True
        >>> validate_task_status("invalid")
        # Raises InvalidTaskStatusError
    """
    if status not in VALID_TASK_STATUSES:
        raise InvalidTaskStatusError(
            f"Invalid task status: {status}. "
            f"Valid statuses: {', '.join(sorted(VALID_TASK_STATUSES))}"
        )
    return True


def is_epic(task_id: str) -> bool:
    """Check if task ID represents an epic (top-level task).

    Args:
        task_id: Task ID to check.

    Returns:
        True if task is an epic, False otherwise.

    Example:
        >>> is_epic("2")
        True
        >>> is_epic("2.3")
        False
    """
    components = parse_task_id(task_id)
    return components.depth == 0


def get_parent_id(task_id: str) -> str | None:
    """Extract parent task ID from a task ID.

    Args:
        task_id: Task ID to extract parent from.

    Returns:
        Parent task ID, or None if task is an epic.

    Example:
        >>> get_parent_id("2.3.1")
        '2.3'
        >>> get_parent_id("2")
        None
    """
    components = parse_task_id(task_id)
    return components.parent_id


def get_epic_id(task_id: str) -> str:
    """Extract epic ID from any task ID.

    Args:
        task_id: Task ID to extract epic from.

    Returns:
        Epic ID (top-level task ID).

    Example:
        >>> get_epic_id("2.3.1")
        '2'
        >>> get_epic_id("2")
        '2'
    """
    components = parse_task_id(task_id)
    return components.epic_id


def format_task_reference(task_id: str, title: str) -> str:
    """Format task as markdown reference.

    Args:
        task_id: Task ID.
        title: Task title.

    Returns:
        Markdown-formatted task reference.

    Example:
        >>> format_task_reference("2.3", "Implement feature")
        'Task 2.3: Implement feature'
    """
    return f"Task {task_id}: {title}"
