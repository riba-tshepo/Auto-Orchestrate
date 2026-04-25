"""Tests for layer2.token_budget module."""

from __future__ import annotations

from layer2.token_budget import (
    CHARS_PER_TOKEN,
    CRITICAL_THRESHOLD,
    DEFAULT_CONTEXT_LIMIT,
    WARNING_THRESHOLD,
    create_tracker,
    estimate_tokens,
    get_usage_report,
    reset_tracker,
    track_usage,
    warn_if_approaching_limit,
)

# ---------------------------------------------------------------------------
# estimate_tokens
# ---------------------------------------------------------------------------


class TestEstimateTokens:
    """Tests for estimate_tokens."""

    def test_basic_approximation(self) -> None:
        # Arrange
        text = "a" * 100

        # Act
        result = estimate_tokens(text)

        # Assert
        assert result == 100 // CHARS_PER_TOKEN

    def test_empty_string_returns_zero(self) -> None:
        # Arrange / Act
        result = estimate_tokens("")

        # Assert
        assert result == 0

    def test_integer_division_truncates(self) -> None:
        # Arrange — 7 chars should give 1 token (7 // 4 = 1)
        text = "a" * 7

        # Act
        result = estimate_tokens(text)

        # Assert
        assert result == 1

    def test_single_char(self) -> None:
        # Arrange / Act
        result = estimate_tokens("x")

        # Assert
        assert result == 0  # 1 // 4 == 0


# ---------------------------------------------------------------------------
# create_tracker
# ---------------------------------------------------------------------------


class TestCreateTracker:
    """Tests for create_tracker."""

    def test_initializes_with_defaults(self) -> None:
        # Arrange / Act
        tracker = create_tracker("orchestrator")

        # Assert
        assert tracker["agent_name"] == "orchestrator"
        assert tracker["context_limit"] == DEFAULT_CONTEXT_LIMIT
        assert tracker["total_chars"] == 0
        assert tracker["estimated_tokens"] == 0
        assert tracker["entries"] == []
        assert "created_at" in tracker

    def test_custom_context_limit(self) -> None:
        # Arrange / Act
        tracker = create_tracker("software-engineer", context_limit=100_000)

        # Assert
        assert tracker["context_limit"] == 100_000

    def test_created_at_is_iso_format(self) -> None:
        # Arrange / Act
        tracker = create_tracker("test-agent")

        # Assert — should be parseable ISO-8601
        from datetime import datetime

        datetime.fromisoformat(tracker["created_at"])


# ---------------------------------------------------------------------------
# track_usage
# ---------------------------------------------------------------------------


class TestTrackUsage:
    """Tests for track_usage."""

    def test_adds_entry_and_updates_totals(self) -> None:
        # Arrange
        tracker = create_tracker("test-agent")
        text = "a" * 400  # 100 tokens

        # Act
        result = track_usage(tracker, text, label="spawn prompt")

        # Assert
        assert result is tracker  # same reference
        assert tracker["total_chars"] == 400
        assert tracker["estimated_tokens"] == 100
        assert len(tracker["entries"]) == 1
        assert tracker["entries"][0]["label"] == "spawn prompt"
        assert tracker["entries"][0]["chars"] == 400
        assert tracker["entries"][0]["tokens"] == 100

    def test_multiple_entries_accumulate(self) -> None:
        # Arrange
        tracker = create_tracker("test-agent")

        # Act
        track_usage(tracker, "a" * 200, label="first")
        track_usage(tracker, "b" * 800, label="second")

        # Assert
        assert tracker["total_chars"] == 1000
        assert tracker["estimated_tokens"] == 250
        assert len(tracker["entries"]) == 2

    def test_empty_text_adds_zero_entry(self) -> None:
        # Arrange
        tracker = create_tracker("test-agent")

        # Act
        track_usage(tracker, "", label="empty")

        # Assert
        assert tracker["total_chars"] == 0
        assert tracker["estimated_tokens"] == 0
        assert len(tracker["entries"]) == 1
        assert tracker["entries"][0]["tokens"] == 0

    def test_default_label_is_empty_string(self) -> None:
        # Arrange
        tracker = create_tracker("test-agent")

        # Act
        track_usage(tracker, "some text")

        # Assert
        assert tracker["entries"][0]["label"] == ""

    def test_entry_has_timestamp(self) -> None:
        # Arrange
        tracker = create_tracker("test-agent")

        # Act
        track_usage(tracker, "hello world")

        # Assert
        from datetime import datetime

        datetime.fromisoformat(tracker["entries"][0]["timestamp"])


# ---------------------------------------------------------------------------
# get_usage_report
# ---------------------------------------------------------------------------


class TestGetUsageReport:
    """Tests for get_usage_report."""

    def test_ok_status_below_warning(self) -> None:
        # Arrange
        tracker = create_tracker("test-agent", context_limit=1000)
        track_usage(tracker, "a" * 400)  # 100 tokens = 10%

        # Act
        report = get_usage_report(tracker)

        # Assert
        assert report["status"] == "ok"
        assert report["percentage"] == 0.1
        assert report["estimated_tokens"] == 100
        assert report["total_chars"] == 400
        assert report["context_limit"] == 1000

    def test_warning_status_at_threshold(self) -> None:
        # Arrange — 80% of 1000 = 800 tokens = 3200 chars
        tracker = create_tracker("test-agent", context_limit=1000)
        track_usage(tracker, "a" * 3200)

        # Act
        report = get_usage_report(tracker)

        # Assert
        assert report["status"] == "warning"
        assert report["percentage"] == WARNING_THRESHOLD

    def test_critical_status_at_threshold(self) -> None:
        # Arrange — 90% of 1000 = 900 tokens = 3600 chars
        tracker = create_tracker("test-agent", context_limit=1000)
        track_usage(tracker, "a" * 3600)

        # Act
        report = get_usage_report(tracker)

        # Assert
        assert report["status"] == "critical"
        assert report["percentage"] == CRITICAL_THRESHOLD

    def test_includes_agent_name(self) -> None:
        # Arrange
        tracker = create_tracker("my-agent")

        # Act
        report = get_usage_report(tracker)

        # Assert
        assert report["agent_name"] == "my-agent"

    def test_zero_limit_returns_zero_percentage(self) -> None:
        # Arrange
        tracker = create_tracker("test-agent", context_limit=0)
        tracker["estimated_tokens"] = 100  # manually set to avoid division

        # Act
        report = get_usage_report(tracker)

        # Assert
        assert report["percentage"] == 0.0


# ---------------------------------------------------------------------------
# warn_if_approaching_limit
# ---------------------------------------------------------------------------


class TestWarnIfApproachingLimit:
    """Tests for warn_if_approaching_limit."""

    def test_no_warning_below_threshold(self) -> None:
        # Arrange
        tracker = create_tracker("test-agent", context_limit=1000)
        track_usage(tracker, "a" * 400)  # 10%

        # Act
        should_warn, message = warn_if_approaching_limit(tracker)

        # Assert
        assert should_warn is False
        assert message == ""

    def test_warning_at_80_percent(self) -> None:
        # Arrange — 80% of 1000 = 800 tokens = 3200 chars
        tracker = create_tracker("test-agent", context_limit=1000)
        track_usage(tracker, "a" * 3200)

        # Act
        should_warn, message = warn_if_approaching_limit(tracker)

        # Assert
        assert should_warn is True
        assert "WARNING" in message
        assert "test-agent" in message
        assert "80%" in message

    def test_critical_at_90_percent(self) -> None:
        # Arrange — 90% of 1000 = 900 tokens = 3600 chars
        tracker = create_tracker("test-agent", context_limit=1000)
        track_usage(tracker, "a" * 3600)

        # Act
        should_warn, message = warn_if_approaching_limit(tracker)

        # Assert
        assert should_warn is True
        assert "CRITICAL" in message
        assert "test-agent" in message
        assert "90%" in message

    def test_critical_overrides_warning(self) -> None:
        # Arrange — 95% should be critical, not warning
        tracker = create_tracker("test-agent", context_limit=1000)
        track_usage(tracker, "a" * 3800)  # 950 tokens = 95%

        # Act
        should_warn, message = warn_if_approaching_limit(tracker)

        # Assert
        assert "CRITICAL" in message

    def test_message_includes_token_counts(self) -> None:
        # Arrange
        tracker = create_tracker("orch", context_limit=1000)
        track_usage(tracker, "a" * 3200)  # 800 tokens

        # Act
        _, message = warn_if_approaching_limit(tracker)

        # Assert
        assert "800/1000" in message


# ---------------------------------------------------------------------------
# reset_tracker
# ---------------------------------------------------------------------------


class TestResetTracker:
    """Tests for reset_tracker."""

    def test_clears_usage_keeps_config(self) -> None:
        # Arrange
        tracker = create_tracker("test-agent", context_limit=50_000)
        track_usage(tracker, "a" * 4000, label="work")

        # Act
        result = reset_tracker(tracker)

        # Assert
        assert result is tracker
        assert tracker["agent_name"] == "test-agent"
        assert tracker["context_limit"] == 50_000
        assert tracker["total_chars"] == 0
        assert tracker["estimated_tokens"] == 0
        assert tracker["entries"] == []
        # created_at should still be present
        assert "created_at" in tracker

    def test_reset_allows_new_tracking(self) -> None:
        # Arrange
        tracker = create_tracker("test-agent", context_limit=1000)
        track_usage(tracker, "a" * 2000)
        reset_tracker(tracker)

        # Act
        track_usage(tracker, "b" * 400)

        # Assert
        assert tracker["total_chars"] == 400
        assert tracker["estimated_tokens"] == 100
        assert len(tracker["entries"]) == 1
