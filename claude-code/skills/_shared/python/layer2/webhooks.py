"""
HTTP webhook dispatcher for forwarding internal events to external endpoints.

Integrates with the hooks system (layer2.hooks) to bridge lifecycle events
to configured webhook URLs via HTTP POST requests with JSON payloads.
Uses only stdlib (urllib.request) — no external dependencies.
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from layer2.hooks import VALID_EVENT_TYPES, register_hook

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_WEBHOOK_CONFIG: str = "webhook_endpoints.json"
DEFAULT_TIMEOUT: int = 10
DEFAULT_MAX_RETRIES: int = 3
RETRY_BASE_DELAY: float = 1.0
ALLOWED_SCHEMES: set[str] = {"https"}

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _default_config_path() -> Path:
    """Return the default webhook configuration file path."""
    return Path.cwd() / DEFAULT_WEBHOOK_CONFIG


def _resolve_config_path(config_path: Path | None) -> Path:
    """Resolve the config path, falling back to the default."""
    return config_path if config_path is not None else _default_config_path()


def _validate_url(url: str, *, allow_insecure: bool = False) -> None:
    """Validate that a URL uses an allowed scheme.

    Args:
        url: The URL to validate.
        allow_insecure: When ``True``, permit ``http`` in addition to
            the schemes in ``ALLOWED_SCHEMES``.

    Raises:
        ValueError: If the URL scheme is not allowed.
    """
    parsed = urlparse(url)
    allowed = ALLOWED_SCHEMES | ({"http"} if allow_insecure else set())
    if parsed.scheme not in allowed:
        raise ValueError(
            f"URL scheme '{parsed.scheme}' is not allowed. "
            f"Allowed schemes: {sorted(allowed)}"
        )
    if not parsed.netloc:
        raise ValueError(f"URL '{url}' is missing a network location (host).")


def _validate_endpoint(endpoint: dict[str, Any], *, allow_insecure: bool = False) -> dict[str, Any]:
    """Validate and normalise a single endpoint configuration dict.

    Args:
        endpoint: Raw endpoint configuration.
        allow_insecure: Passed through to URL scheme validation.

    Returns:
        The normalised endpoint dict with defaults applied.

    Raises:
        ValueError: If required fields are missing or invalid.
    """
    if "url" not in endpoint:
        raise ValueError("Endpoint configuration missing required 'url' field.")
    _validate_url(endpoint["url"], allow_insecure=allow_insecure)

    if "events" not in endpoint or not isinstance(endpoint["events"], list):
        raise ValueError(
            "Endpoint configuration missing required 'events' field "
            "(must be a list of event type strings)."
        )

    for event_type in endpoint["events"]:
        if event_type not in VALID_EVENT_TYPES:
            raise ValueError(
                f"Unknown event type '{event_type}' in endpoint events. "
                f"Valid types: {sorted(VALID_EVENT_TYPES)}"
            )

    return {
        "url": endpoint["url"],
        "events": endpoint["events"],
        "enabled": endpoint.get("enabled", True),
        "name": endpoint.get("name", ""),
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def configure_endpoints(
    endpoints: list[dict[str, Any]],
    config_path: Path | None = None,
    *,
    allow_insecure: bool = False,
) -> Path:
    """Save webhook endpoint configurations to a JSON file.

    Each endpoint dict should have:
      - ``url`` (str): The webhook URL.
      - ``events`` (list[str]): Event types to subscribe to.
      - ``enabled`` (bool, optional): Whether the endpoint is active. Default ``True``.
      - ``name`` (str, optional): Human-readable label.

    Validates URL schemes (``https`` required; ``http`` allowed only when
    *allow_insecure* is ``True``). Uses atomic write (temp file + ``os.replace``).

    Args:
        endpoints: List of endpoint configuration dicts.
        config_path: Where to write the config. Falls back to the default
            config path if ``None``.
        allow_insecure: Allow ``http://`` URLs.

    Returns:
        The resolved path to the written config file.

    Raises:
        ValueError: If any endpoint fails validation.
    """
    resolved = _resolve_config_path(config_path)
    validated = [_validate_endpoint(ep, allow_insecure=allow_insecure) for ep in endpoints]

    data = json.dumps({"endpoints": validated}, indent=2, sort_keys=True)

    resolved.parent.mkdir(parents=True, exist_ok=True)

    fd, tmp_path = tempfile.mkstemp(
        dir=str(resolved.parent),
        prefix=".webhook_cfg_",
        suffix=".tmp",
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_path, str(resolved))
    except BaseException:
        # Clean up the temp file on any failure.
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise

    logger.info("Webhook config written to %s (%d endpoints)", resolved, len(validated))
    return resolved


def load_endpoints(config_path: Path | None = None) -> list[dict[str, Any]]:
    """Load configured webhook endpoints from the JSON config file.

    Args:
        config_path: Path to the config file. Falls back to the default if
            ``None``.

    Returns:
        A list of endpoint dicts. Returns an empty list when the config file
        does not exist.
    """
    resolved = _resolve_config_path(config_path)
    if not resolved.exists():
        return []

    with resolved.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    endpoints: list[dict[str, Any]] = data.get("endpoints", [])
    return endpoints


def send_webhook(
    url: str,
    event: dict[str, Any],
    timeout: int = DEFAULT_TIMEOUT,
    max_retries: int = DEFAULT_MAX_RETRIES,
) -> dict[str, Any]:
    """Send an HTTP POST webhook to *url* with a JSON payload.

    Uses ``urllib.request.urlopen`` with exponential backoff retry
    (delays: 1s, 2s, 4s, i.e. ``RETRY_BASE_DELAY * 2 ** attempt``).

    Args:
        url: Target URL.
        event: The event payload to serialize as JSON.
        timeout: Per-request timeout in seconds.
        max_retries: Maximum number of delivery attempts.

    Returns:
        A dict with keys ``url``, ``status_code``, ``success``, ``attempts``,
        and ``error``.
    """
    payload = json.dumps(event).encode("utf-8")
    last_error: str | None = None

    for attempt in range(max_retries):
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                status_code = resp.status
            logger.info(
                "Webhook delivered to %s (status=%d, attempt=%d)",
                url,
                status_code,
                attempt + 1,
            )
            return {
                "url": url,
                "status_code": status_code,
                "success": True,
                "attempts": attempt + 1,
                "error": None,
            }
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as exc:
            last_error = str(exc)
            logger.warning(
                "Webhook delivery to %s failed (attempt %d/%d): %s",
                url,
                attempt + 1,
                max_retries,
                last_error,
            )
            if attempt < max_retries - 1:
                delay = RETRY_BASE_DELAY * (2 ** attempt)
                time.sleep(delay)

    return {
        "url": url,
        "status_code": 0,
        "success": False,
        "attempts": max_retries,
        "error": last_error,
    }


def dispatch_event(
    event: dict[str, Any],
    config_path: Path | None = None,
) -> list[dict[str, Any]]:
    """Dispatch an event to all matching configured webhook endpoints.

    Reads the endpoint configuration, filters for endpoints whose ``events``
    list includes the event's ``event_type``, and sends the webhook to each.

    Args:
        event: An event dict with at least an ``event_type`` key.
        config_path: Path to the webhook configuration file.

    Returns:
        A list of result dicts from :func:`send_webhook` calls (one per
        matched endpoint).
    """
    event_type = event.get("event_type")
    if event_type is None:
        logger.error("dispatch_event called with event missing 'event_type' key")
        return []

    endpoints = load_endpoints(config_path)
    results: list[dict[str, Any]] = []

    for ep in endpoints:
        if not ep.get("enabled", True):
            continue
        if event_type not in ep.get("events", []):
            continue
        result = send_webhook(ep["url"], event)
        results.append(result)

    return results


def register_webhook_bridge(config_path: Path | None = None) -> None:
    """Register hook callbacks that bridge internal events to webhooks.

    For each event type in ``VALID_EVENT_TYPES``, registers a callback with
    the hooks system that forwards the event to :func:`dispatch_event`.

    Args:
        config_path: Path to the webhook configuration file. Passed through
            to :func:`dispatch_event` on each invocation.
    """
    for event_type in sorted(VALID_EVENT_TYPES):

        def _bridge_callback(
            event: dict[str, Any],
            _cfg: Path | None = config_path,
        ) -> None:
            dispatch_event(event, config_path=_cfg)

        register_hook(event_type, _bridge_callback)
        logger.debug("Webhook bridge registered for event type '%s'", event_type)
