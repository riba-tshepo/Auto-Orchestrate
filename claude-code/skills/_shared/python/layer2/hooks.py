"""
Event hook framework for internal state changes.

Provides a publish-subscribe system for lifecycle events such as agent
start/stop, task creation/completion/failure, and epic creation/completion.
Callbacks are stored in an in-memory registry keyed by event type.
"""

from __future__ import annotations

import contextlib
import logging
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Event type constants
# ---------------------------------------------------------------------------

AGENT_STARTED: str = "agent_started"
AGENT_STOPPED: str = "agent_stopped"
TASK_CREATED: str = "task_created"
TASK_COMPLETED: str = "task_completed"
TASK_FAILED: str = "task_failed"
EPIC_CREATED: str = "epic_created"
EPIC_COMPLETED: str = "epic_completed"

VALID_EVENT_TYPES: set[str] = {
    AGENT_STARTED,
    AGENT_STOPPED,
    TASK_CREATED,
    TASK_COMPLETED,
    TASK_FAILED,
    EPIC_CREATED,
    EPIC_COMPLETED,
}

# ---------------------------------------------------------------------------
# Type alias
# ---------------------------------------------------------------------------

HookCallback = Callable[[dict[str, Any]], None]

# ---------------------------------------------------------------------------
# Module-level hook registry
# ---------------------------------------------------------------------------

_hook_registry: dict[str, list[HookCallback]] = {}


def _validate_event_type(event_type: str) -> None:
    """Validate that *event_type* is a recognised event.

    Args:
        event_type: The event type string to validate.

    Raises:
        ValueError: If *event_type* is not in ``VALID_EVENT_TYPES``.
    """
    if event_type not in VALID_EVENT_TYPES:
        raise ValueError(
            f"Unknown event type '{event_type}'. "
            f"Valid types: {sorted(VALID_EVENT_TYPES)}"
        )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def register_hook(event_type: str, callback: HookCallback) -> None:
    """Register a callback for a given event type.

    Args:
        event_type: One of the ``VALID_EVENT_TYPES`` constants.
        callback: A callable accepting a single ``dict[str, Any]`` argument.

    Raises:
        ValueError: If *event_type* is not recognised.
    """
    _validate_event_type(event_type)
    _hook_registry.setdefault(event_type, []).append(callback)


def unregister_hook(event_type: str, callback: HookCallback) -> None:
    """Remove a previously registered callback for an event type.

    If the callback is not found in the registry the call is a no-op.

    Args:
        event_type: One of the ``VALID_EVENT_TYPES`` constants.
        callback: The exact callable reference that was registered.

    Raises:
        ValueError: If *event_type* is not recognised.
    """
    _validate_event_type(event_type)
    hooks = _hook_registry.get(event_type)
    if hooks is None:
        return
    with contextlib.suppress(ValueError):
        hooks.remove(callback)


def emit_event(
    event_type: str, payload: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Emit an event, invoking all registered callbacks for the event type.

    Each callback receives a copy of the full event dict.  If a callback
    raises an exception it is logged and the remaining callbacks still
    execute (the emit chain is never broken).

    Args:
        event_type: One of the ``VALID_EVENT_TYPES`` constants.
        payload: Optional data to include in the event dict.

    Returns:
        The constructed event dict with keys ``event_type``, ``timestamp``,
        and ``payload``.

    Raises:
        ValueError: If *event_type* is not recognised.
    """
    _validate_event_type(event_type)

    event: dict[str, Any] = {
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload if payload is not None else {},
    }

    for callback in _hook_registry.get(event_type, []):
        try:
            callback(event)
        except Exception:
            logger.exception(
                "Hook callback %r failed for event '%s'",
                callback,
                event_type,
            )

    return event


def get_registered_hooks() -> dict[str, list[HookCallback]]:
    """Return a shallow copy of the current hook registry.

    Returns:
        A dict mapping event types to lists of registered callbacks.
    """
    return {k: list(v) for k, v in _hook_registry.items()}


def clear_all_hooks() -> None:
    """Remove all registered hooks from the registry."""
    _hook_registry.clear()
