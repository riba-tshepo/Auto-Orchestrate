"""
Token/context budget tracker for agent context windows.

Provides functions to estimate token usage and track cumulative consumption
against a context window limit. Token estimation uses a character-based
approximation (1 token ~ 4 characters), which is rough but sufficient for
budget tracking purposes. Actual tokenizer counts will vary by model.

This is a Layer 2 module. It imports only from stdlib (layer0/layer1 have
no dependencies needed here).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_CONTEXT_LIMIT: int = 200_000
"""Default context window size in tokens."""

WARNING_THRESHOLD: float = 0.80
"""80% usage triggers a warning."""

CRITICAL_THRESHOLD: float = 0.90
"""90% usage triggers a critical warning."""

CHARS_PER_TOKEN: int = 4
"""Rough approximation: 1 token ~ 4 characters."""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def estimate_tokens(text: str) -> int:
    """Estimate token count from text using character-based approximation.

    Args:
        text: The input text to estimate tokens for.

    Returns:
        Estimated number of tokens (integer division of len(text) / CHARS_PER_TOKEN).
    """
    return len(text) // CHARS_PER_TOKEN


def create_tracker(
    agent_name: str,
    context_limit: int = DEFAULT_CONTEXT_LIMIT,
) -> dict[str, Any]:
    """Create a new token usage tracker for an agent.

    Args:
        agent_name: Identifier for the agent being tracked.
        context_limit: Maximum token budget for the context window.

    Returns:
        A tracker dict with zeroed counters and metadata.
    """
    return {
        "agent_name": agent_name,
        "context_limit": context_limit,
        "total_chars": 0,
        "estimated_tokens": 0,
        "entries": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def track_usage(
    tracker: dict[str, Any],
    text: str,
    label: str = "",
) -> dict[str, Any]:
    """Record token usage for a text chunk.

    Appends an entry to the tracker's history and updates cumulative totals.

    Args:
        tracker: The tracker dict to update.
        text: The text whose tokens should be recorded.
        label: Optional human-readable label for this entry.

    Returns:
        The updated tracker dict (same reference, mutated in place).
    """
    chars = len(text)
    tokens = estimate_tokens(text)

    tracker["entries"].append(
        {
            "label": label,
            "chars": chars,
            "tokens": tokens,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )
    tracker["total_chars"] += chars
    tracker["estimated_tokens"] += tokens

    return tracker


def get_usage_report(tracker: dict[str, Any]) -> dict[str, Any]:
    """Get a usage report for the tracker.

    Args:
        tracker: The tracker dict to report on.

    Returns:
        A dict containing total_chars, estimated_tokens, percentage (0.0-1.0),
        and status ("ok", "warning", or "critical").
    """
    limit = tracker["context_limit"]
    tokens = tracker["estimated_tokens"]

    percentage = tokens / limit if limit > 0 else 0.0

    if percentage >= CRITICAL_THRESHOLD:
        status = "critical"
    elif percentage >= WARNING_THRESHOLD:
        status = "warning"
    else:
        status = "ok"

    return {
        "agent_name": tracker["agent_name"],
        "total_chars": tracker["total_chars"],
        "estimated_tokens": tokens,
        "context_limit": limit,
        "percentage": percentage,
        "status": status,
    }


def warn_if_approaching_limit(tracker: dict[str, Any]) -> tuple[bool, str]:
    """Check if the tracker is approaching its context limit.

    Args:
        tracker: The tracker dict to check.

    Returns:
        A tuple of (should_warn, message). Returns (False, "") when usage
        is below WARNING_THRESHOLD.
    """
    report = get_usage_report(tracker)
    percentage = report["percentage"]
    agent = report["agent_name"]

    if percentage >= CRITICAL_THRESHOLD:
        pct_display = f"{percentage:.0%}"
        return (
            True,
            f"CRITICAL: {agent} at {pct_display} of context budget "
            f"({report['estimated_tokens']}/{report['context_limit']} tokens)",
        )

    if percentage >= WARNING_THRESHOLD:
        pct_display = f"{percentage:.0%}"
        return (
            True,
            f"WARNING: {agent} at {pct_display} of context budget "
            f"({report['estimated_tokens']}/{report['context_limit']} tokens)",
        )

    return (False, "")


def reset_tracker(tracker: dict[str, Any]) -> dict[str, Any]:
    """Reset usage counters while keeping agent_name and context_limit.

    Args:
        tracker: The tracker dict to reset.

    Returns:
        The updated tracker dict (same reference, mutated in place)
        with zeroed counters and cleared entries.
    """
    tracker["total_chars"] = 0
    tracker["estimated_tokens"] = 0
    tracker["entries"] = []

    return tracker
