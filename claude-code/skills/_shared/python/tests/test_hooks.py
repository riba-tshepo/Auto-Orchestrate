"""
Tests for layer2.hooks module.

Tests the event hook publish-subscribe framework including registration,
unregistration, event emission, error resilience, and registry management.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pytest

from layer2.hooks import (
    AGENT_STARTED,
    AGENT_STOPPED,
    EPIC_COMPLETED,
    EPIC_CREATED,
    TASK_COMPLETED,
    TASK_CREATED,
    TASK_FAILED,
    VALID_EVENT_TYPES,
    clear_all_hooks,
    emit_event,
    get_registered_hooks,
    register_hook,
    unregister_hook,
)


@pytest.fixture(autouse=True)
def _clean_registry():
    """Ensure every test starts and ends with a clean hook registry."""
    clear_all_hooks()
    yield
    clear_all_hooks()


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_valid_event_types_contains_all_constants():
    """VALID_EVENT_TYPES includes every defined event constant."""
    expected = {
        AGENT_STARTED,
        AGENT_STOPPED,
        TASK_CREATED,
        TASK_COMPLETED,
        TASK_FAILED,
        EPIC_CREATED,
        EPIC_COMPLETED,
    }

    assert expected == VALID_EVENT_TYPES


# ---------------------------------------------------------------------------
# register_hook
# ---------------------------------------------------------------------------


def test_register_hook_adds_callback():
    """register_hook adds a callback to the registry for the event type."""
    received: list[dict[str, Any]] = []
    register_hook(TASK_CREATED, received.append)

    hooks = get_registered_hooks()

    assert TASK_CREATED in hooks
    assert len(hooks[TASK_CREATED]) == 1


def test_register_hook_rejects_invalid_event_type():
    """register_hook raises ValueError for an unknown event type."""
    with pytest.raises(ValueError, match="Unknown event type"):
        register_hook("not_a_real_event", lambda e: None)


def test_register_hook_multiple_callbacks_same_event():
    """Multiple callbacks can be registered for the same event type."""
    cb_a = lambda e: None  # noqa: E731
    cb_b = lambda e: None  # noqa: E731

    register_hook(AGENT_STARTED, cb_a)
    register_hook(AGENT_STARTED, cb_b)

    hooks = get_registered_hooks()

    assert len(hooks[AGENT_STARTED]) == 2


# ---------------------------------------------------------------------------
# unregister_hook
# ---------------------------------------------------------------------------


def test_unregister_hook_removes_callback():
    """unregister_hook removes a previously registered callback."""
    received: list[dict[str, Any]] = []
    register_hook(TASK_COMPLETED, received.append)
    unregister_hook(TASK_COMPLETED, received.append)

    hooks = get_registered_hooks()

    assert hooks.get(TASK_COMPLETED, []) == []


def test_unregister_hook_noop_for_missing_callback():
    """unregister_hook is a no-op when the callback was never registered."""
    unregister_hook(TASK_FAILED, lambda e: None)

    hooks = get_registered_hooks()

    assert hooks.get(TASK_FAILED) is None


def test_unregister_hook_rejects_invalid_event_type():
    """unregister_hook raises ValueError for an unknown event type."""
    with pytest.raises(ValueError, match="Unknown event type"):
        unregister_hook("bogus_event", lambda e: None)


# ---------------------------------------------------------------------------
# emit_event
# ---------------------------------------------------------------------------


def test_emit_event_calls_all_registered_callbacks():
    """emit_event invokes every callback registered for the event type."""
    calls_a: list[dict[str, Any]] = []
    calls_b: list[dict[str, Any]] = []

    register_hook(EPIC_CREATED, calls_a.append)
    register_hook(EPIC_CREATED, calls_b.append)

    emit_event(EPIC_CREATED, {"epic_id": "E-1"})

    assert len(calls_a) == 1
    assert len(calls_b) == 1
    assert calls_a[0]["payload"] == {"epic_id": "E-1"}
    assert calls_b[0]["payload"] == {"epic_id": "E-1"}


def test_emit_event_returns_event_dict():
    """emit_event returns the constructed event dict."""
    before = datetime.now(timezone.utc)
    event = emit_event(AGENT_STARTED, {"agent": "orchestrator"})
    after = datetime.now(timezone.utc)

    assert event["event_type"] == AGENT_STARTED
    assert event["payload"] == {"agent": "orchestrator"}

    ts = datetime.fromisoformat(event["timestamp"])
    assert before <= ts <= after


def test_emit_event_default_payload_is_empty_dict():
    """emit_event uses an empty dict when no payload is provided."""
    event = emit_event(AGENT_STOPPED)

    assert event["payload"] == {}


def test_emit_event_rejects_invalid_event_type():
    """emit_event raises ValueError for an unknown event type."""
    with pytest.raises(ValueError, match="Unknown event type"):
        emit_event("invented_event")


def test_emit_event_callback_exception_does_not_break_chain():
    """A failing callback does not prevent other callbacks from executing."""
    calls: list[dict[str, Any]] = []

    def bad_callback(event: dict[str, Any]) -> None:
        raise RuntimeError("boom")

    register_hook(TASK_FAILED, bad_callback)
    register_hook(TASK_FAILED, calls.append)

    event = emit_event(TASK_FAILED, {"task_id": "T-1"})

    assert len(calls) == 1
    assert calls[0] is event


def test_emit_event_no_registered_hooks_returns_event():
    """emit_event works when no hooks are registered for the event type."""
    event = emit_event(EPIC_COMPLETED)

    assert event["event_type"] == EPIC_COMPLETED
    assert event["payload"] == {}


# ---------------------------------------------------------------------------
# get_registered_hooks
# ---------------------------------------------------------------------------


def test_get_registered_hooks_returns_shallow_copy():
    """Mutating the returned dict does not affect the internal registry."""
    register_hook(TASK_CREATED, lambda e: None)
    hooks = get_registered_hooks()
    hooks[TASK_CREATED].clear()

    internal = get_registered_hooks()

    assert len(internal[TASK_CREATED]) == 1


def test_get_registered_hooks_empty_when_nothing_registered():
    """get_registered_hooks returns an empty dict when no hooks exist."""
    hooks = get_registered_hooks()

    assert hooks == {}


# ---------------------------------------------------------------------------
# clear_all_hooks
# ---------------------------------------------------------------------------


def test_clear_all_hooks_empties_registry():
    """clear_all_hooks removes every registered callback."""
    register_hook(AGENT_STARTED, lambda e: None)
    register_hook(TASK_CREATED, lambda e: None)
    register_hook(EPIC_COMPLETED, lambda e: None)

    clear_all_hooks()

    hooks = get_registered_hooks()

    assert hooks == {}
