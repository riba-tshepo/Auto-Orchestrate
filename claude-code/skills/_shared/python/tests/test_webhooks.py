"""
Tests for layer2.webhooks module.

Tests the HTTP webhook dispatcher including endpoint configuration,
URL validation, send/retry logic, event dispatch, and hooks integration.
"""

from __future__ import annotations

import json
from http.client import HTTPResponse
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, call, patch

import pytest

from layer2.hooks import (
    VALID_EVENT_TYPES,
    clear_all_hooks,
    get_registered_hooks,
)
from layer2.webhooks import (
    ALLOWED_SCHEMES,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
    DEFAULT_WEBHOOK_CONFIG,
    RETRY_BASE_DELAY,
    configure_endpoints,
    dispatch_event,
    load_endpoints,
    register_webhook_bridge,
    send_webhook,
)


@pytest.fixture(autouse=True)
def _clean_hooks():
    """Ensure every test starts and ends with a clean hook registry."""
    clear_all_hooks()
    yield
    clear_all_hooks()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_endpoint(
    url: str = "https://hooks.example.com/callback",
    events: list[str] | None = None,
    enabled: bool = True,
    name: str = "test-hook",
) -> dict[str, Any]:
    """Create a minimal endpoint configuration dict."""
    return {
        "url": url,
        "events": events if events is not None else ["task_created"],
        "enabled": enabled,
        "name": name,
    }


def _mock_http_response(status: int = 200) -> MagicMock:
    """Create a mock context manager mimicking ``urllib.request.urlopen``."""
    mock_resp = MagicMock(spec=HTTPResponse)
    mock_resp.status = status
    mock_resp.__enter__ = MagicMock(return_value=mock_resp)
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


class TestConstants:
    """Verify module-level constants are correctly defined."""

    def test_default_webhook_config(self):
        assert DEFAULT_WEBHOOK_CONFIG == "webhook_endpoints.json"

    def test_default_timeout(self):
        assert DEFAULT_TIMEOUT == 10

    def test_default_max_retries(self):
        assert DEFAULT_MAX_RETRIES == 3

    def test_retry_base_delay(self):
        assert RETRY_BASE_DELAY == 1.0

    def test_allowed_schemes_contains_https(self):
        assert "https" in ALLOWED_SCHEMES

    def test_allowed_schemes_excludes_http_by_default(self):
        assert "http" not in ALLOWED_SCHEMES


# ---------------------------------------------------------------------------
# configure_endpoints
# ---------------------------------------------------------------------------


class TestConfigureEndpoints:
    """Tests for configure_endpoints()."""

    def test_writes_valid_config(self, tmp_path: Path):
        """Endpoint config is written as valid JSON."""
        cfg = tmp_path / "hooks.json"
        ep = _make_endpoint()

        result = configure_endpoints([ep], config_path=cfg)

        assert result == cfg
        assert cfg.exists()

        data = json.loads(cfg.read_text("utf-8"))
        assert "endpoints" in data
        assert len(data["endpoints"]) == 1
        assert data["endpoints"][0]["url"] == ep["url"]

    def test_rejects_http_url_by_default(self, tmp_path: Path):
        """HTTP URLs are rejected when allow_insecure is False."""
        cfg = tmp_path / "hooks.json"
        ep = _make_endpoint(url="http://insecure.example.com/hook")

        with pytest.raises(ValueError, match="scheme.*not allowed"):
            configure_endpoints([ep], config_path=cfg)

    def test_allows_http_when_insecure_flag_set(self, tmp_path: Path):
        """HTTP URLs are permitted when allow_insecure is True."""
        cfg = tmp_path / "hooks.json"
        ep = _make_endpoint(url="http://insecure.example.com/hook")

        result = configure_endpoints([ep], config_path=cfg, allow_insecure=True)
        assert result == cfg

    def test_rejects_invalid_scheme(self, tmp_path: Path):
        """Non-http/https schemes are always rejected."""
        cfg = tmp_path / "hooks.json"
        ep = _make_endpoint(url="ftp://files.example.com/upload")

        with pytest.raises(ValueError, match="scheme.*not allowed"):
            configure_endpoints([ep], config_path=cfg)

    def test_rejects_missing_url(self, tmp_path: Path):
        """Endpoint without a url field raises ValueError."""
        cfg = tmp_path / "hooks.json"
        with pytest.raises(ValueError, match="missing required 'url'"):
            configure_endpoints([{"events": ["task_created"]}], config_path=cfg)

    def test_rejects_unknown_event_type(self, tmp_path: Path):
        """Unknown event types in the events list are rejected."""
        cfg = tmp_path / "hooks.json"
        ep = _make_endpoint(events=["nonexistent_event"])

        with pytest.raises(ValueError, match="Unknown event type"):
            configure_endpoints([ep], config_path=cfg)

    def test_defaults_enabled_to_true(self, tmp_path: Path):
        """Endpoint without explicit enabled defaults to True."""
        cfg = tmp_path / "hooks.json"
        ep = {"url": "https://hooks.example.com/cb", "events": ["task_created"]}

        configure_endpoints([ep], config_path=cfg)
        data = json.loads(cfg.read_text("utf-8"))
        assert data["endpoints"][0]["enabled"] is True

    def test_atomic_write_does_not_corrupt_on_error(self, tmp_path: Path):
        """If writing fails mid-way, the original config is not corrupted."""
        cfg = tmp_path / "hooks.json"
        ep = _make_endpoint()
        configure_endpoints([ep], config_path=cfg)

        original_content = cfg.read_text("utf-8")

        # Simulate a write error by patching os.fdopen to raise.
        with patch("layer2.webhooks.os.fdopen", side_effect=OSError("disk full")), \
             pytest.raises(OSError, match="disk full"):
                configure_endpoints(
                    [_make_endpoint(name="new")],
                    config_path=cfg,
                )

        # Original file should be unchanged.
        assert cfg.read_text("utf-8") == original_content

    def test_rejects_url_without_host(self, tmp_path: Path):
        """A URL missing a network location is rejected."""
        cfg = tmp_path / "hooks.json"
        ep = _make_endpoint(url="https://")

        with pytest.raises(ValueError, match="missing a network location"):
            configure_endpoints([ep], config_path=cfg)


# ---------------------------------------------------------------------------
# load_endpoints
# ---------------------------------------------------------------------------


class TestLoadEndpoints:
    """Tests for load_endpoints()."""

    def test_returns_empty_list_when_no_config(self, tmp_path: Path):
        """Missing config file returns an empty list."""
        cfg = tmp_path / "nonexistent.json"
        assert load_endpoints(config_path=cfg) == []

    def test_reads_saved_config(self, tmp_path: Path):
        """Endpoints saved by configure_endpoints are loaded back."""
        cfg = tmp_path / "hooks.json"
        ep = _make_endpoint()
        configure_endpoints([ep], config_path=cfg)

        loaded = load_endpoints(config_path=cfg)
        assert len(loaded) == 1
        assert loaded[0]["url"] == ep["url"]
        assert loaded[0]["events"] == ep["events"]

    def test_loads_multiple_endpoints(self, tmp_path: Path):
        """Multiple endpoints round-trip through save/load."""
        cfg = tmp_path / "hooks.json"
        eps = [
            _make_endpoint(url="https://a.example.com/hook", name="a"),
            _make_endpoint(url="https://b.example.com/hook", name="b"),
        ]
        configure_endpoints(eps, config_path=cfg)

        loaded = load_endpoints(config_path=cfg)
        assert len(loaded) == 2


# ---------------------------------------------------------------------------
# send_webhook
# ---------------------------------------------------------------------------


class TestSendWebhook:
    """Tests for send_webhook()."""

    @patch("layer2.webhooks.urllib.request.urlopen")
    def test_successful_send(self, mock_urlopen: MagicMock):
        """A 200 response is reported as successful."""
        mock_urlopen.return_value = _mock_http_response(200)

        result = send_webhook(
            "https://hooks.example.com/cb",
            {"event_type": "task_created", "payload": {}},
        )

        assert result["success"] is True
        assert result["status_code"] == 200
        assert result["attempts"] == 1
        assert result["error"] is None
        assert result["url"] == "https://hooks.example.com/cb"

    @patch("layer2.webhooks.time.sleep")
    @patch("layer2.webhooks.urllib.request.urlopen")
    def test_retry_with_exponential_backoff(
        self,
        mock_urlopen: MagicMock,
        mock_sleep: MagicMock,
    ):
        """Retries use exponential backoff delays."""
        mock_urlopen.side_effect = [
            OSError("connection refused"),
            OSError("connection refused"),
            _mock_http_response(200),
        ]

        result = send_webhook(
            "https://hooks.example.com/cb",
            {"event_type": "task_created"},
            max_retries=3,
        )

        assert result["success"] is True
        assert result["attempts"] == 3

        # Backoff: 1*2^0=1, 1*2^1=2
        assert mock_sleep.call_args_list == [call(1.0), call(2.0)]

    @patch("layer2.webhooks.time.sleep")
    @patch("layer2.webhooks.urllib.request.urlopen")
    def test_all_retries_exhausted(
        self,
        mock_urlopen: MagicMock,
        mock_sleep: MagicMock,
    ):
        """When all retries fail, result indicates failure."""
        mock_urlopen.side_effect = OSError("connection refused")

        result = send_webhook(
            "https://hooks.example.com/cb",
            {"event_type": "task_created"},
            max_retries=3,
        )

        assert result["success"] is False
        assert result["status_code"] == 0
        assert result["attempts"] == 3
        assert result["error"] is not None
        assert "connection refused" in result["error"]

    @patch("layer2.webhooks.urllib.request.urlopen")
    def test_sends_json_content_type(self, mock_urlopen: MagicMock):
        """The POST request includes a JSON Content-Type header."""
        mock_urlopen.return_value = _mock_http_response(200)

        send_webhook("https://hooks.example.com/cb", {"event_type": "task_created"})

        sent_request = mock_urlopen.call_args[0][0]
        assert sent_request.get_header("Content-type") == "application/json"

    @patch("layer2.webhooks.urllib.request.urlopen")
    def test_sends_post_method(self, mock_urlopen: MagicMock):
        """The request method is POST."""
        mock_urlopen.return_value = _mock_http_response(200)

        send_webhook("https://hooks.example.com/cb", {"event_type": "task_created"})

        sent_request = mock_urlopen.call_args[0][0]
        assert sent_request.get_method() == "POST"


# ---------------------------------------------------------------------------
# dispatch_event
# ---------------------------------------------------------------------------


class TestDispatchEvent:
    """Tests for dispatch_event()."""

    @patch("layer2.webhooks.send_webhook")
    def test_dispatches_to_matching_endpoints(
        self,
        mock_send: MagicMock,
        tmp_path: Path,
    ):
        """Events are sent only to endpoints subscribed to the event type."""
        cfg = tmp_path / "hooks.json"
        configure_endpoints(
            [
                _make_endpoint(
                    url="https://a.example.com/hook",
                    events=["task_created"],
                    name="a",
                ),
                _make_endpoint(
                    url="https://b.example.com/hook",
                    events=["task_completed"],
                    name="b",
                ),
            ],
            config_path=cfg,
        )
        mock_send.return_value = {"url": "", "status_code": 200, "success": True, "attempts": 1, "error": None}

        event = {"event_type": "task_created", "payload": {}}
        results = dispatch_event(event, config_path=cfg)

        assert len(results) == 1
        mock_send.assert_called_once()
        sent_url = mock_send.call_args[0][0]
        assert sent_url == "https://a.example.com/hook"

    @patch("layer2.webhooks.send_webhook")
    def test_skips_disabled_endpoints(
        self,
        mock_send: MagicMock,
        tmp_path: Path,
    ):
        """Disabled endpoints are not dispatched to."""
        cfg = tmp_path / "hooks.json"
        configure_endpoints(
            [
                _make_endpoint(enabled=False),
            ],
            config_path=cfg,
        )

        event = {"event_type": "task_created", "payload": {}}
        results = dispatch_event(event, config_path=cfg)

        assert results == []
        mock_send.assert_not_called()

    def test_returns_empty_for_missing_event_type(self, tmp_path: Path):
        """An event without event_type returns an empty result list."""
        cfg = tmp_path / "hooks.json"
        results = dispatch_event({"payload": {}}, config_path=cfg)
        assert results == []

    @patch("layer2.webhooks.send_webhook")
    def test_returns_empty_when_no_config(
        self,
        mock_send: MagicMock,
        tmp_path: Path,
    ):
        """When no config file exists, dispatch returns empty list."""
        cfg = tmp_path / "nonexistent.json"
        results = dispatch_event(
            {"event_type": "task_created"},
            config_path=cfg,
        )
        assert results == []
        mock_send.assert_not_called()


# ---------------------------------------------------------------------------
# register_webhook_bridge
# ---------------------------------------------------------------------------


class TestRegisterWebhookBridge:
    """Tests for register_webhook_bridge()."""

    def test_registers_hooks_for_all_event_types(self):
        """A callback is registered for every valid event type."""
        register_webhook_bridge()

        hooks = get_registered_hooks()
        for event_type in VALID_EVENT_TYPES:
            assert event_type in hooks, f"No hook registered for {event_type}"
            assert len(hooks[event_type]) >= 1

    @patch("layer2.webhooks.dispatch_event")
    def test_bridge_callback_calls_dispatch(self, mock_dispatch: MagicMock):
        """The registered bridge callback invokes dispatch_event."""
        register_webhook_bridge()

        hooks = get_registered_hooks()
        event_type = "task_created"
        callback = hooks[event_type][0]

        test_event: dict[str, Any] = {
            "event_type": event_type,
            "timestamp": "2025-01-01T00:00:00+00:00",
            "payload": {"task_id": "TSK-001"},
        }
        callback(test_event)

        mock_dispatch.assert_called_once_with(test_event, config_path=None)
