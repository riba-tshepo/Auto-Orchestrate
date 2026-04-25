"""Core JSONL append/query engine for domain memory.

All writes use ``fcntl.flock(LOCK_EX)`` + ``flush`` + ``fsync`` for
crash-safe, concurrent-safe appends.  Reads scan the full JSONL without
locking (append-only files are safe for concurrent readers).

Dependencies: Python >= 3.11 stdlib only.
"""

from __future__ import annotations

import fcntl
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_STORES: frozenset[str] = frozenset({
    "research_ledger",
    "decision_log",
    "pattern_library",
    "fix_registry",
    "codebase_analysis",
    "user_preferences",
})

_LOCK_TIMEOUT_SECONDS = 5


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _validate_store_name(name: str) -> None:
    if name not in VALID_STORES:
        raise ValueError(
            f"Invalid store name '{name}'. Must be one of {sorted(VALID_STORES)}"
        )


def _jsonl_path(domain_dir: Path, store_name: str) -> Path:
    return domain_dir / f"{store_name}.jsonl"


# ---------------------------------------------------------------------------
# DomainMemoryStore
# ---------------------------------------------------------------------------

class DomainMemoryStore:
    """Project-level domain memory backed by append-only JSONL files.

    Usage::

        store = DomainMemoryStore(Path(".domain"))
        store.append("fix_registry", {
            "error_fingerprint": "conn_refused_5432",
            "fix_description": "Changed port in .env",
        })
        fixes = store.query("fix_registry", filters={"error_fingerprint": "conn_refused_5432"})
    """

    def __init__(
        self,
        domain_dir: Path | str,
        session_id: str = "",
        command: str = "",
    ) -> None:
        self._domain_dir = Path(domain_dir)
        self._session_id = session_id
        self._command = command
        os.makedirs(self._domain_dir, exist_ok=True)
        logger.info("DomainMemoryStore initialized at %s", self._domain_dir)

    @property
    def domain_dir(self) -> Path:
        return self._domain_dir

    # -- Write operations ---------------------------------------------------

    def append(self, store_name: str, entry: dict[str, Any]) -> None:
        """Append a single entry to a JSONL store (thread/process-safe).

        Metadata fields ``_timestamp``, ``_session_id``, and ``_command``
        are injected automatically.

        Args:
            store_name: One of :data:`VALID_STORES`.
            entry: Dict to persist.  Must be JSON-serialisable.
        """
        _validate_store_name(store_name)

        record = {
            "_timestamp": _utc_now_iso(),
            "_session_id": self._session_id,
            "_command": self._command,
            **entry,
        }

        path = _jsonl_path(self._domain_dir, store_name)
        line = json.dumps(record, separators=(",", ":"), default=str) + "\n"

        fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            os.write(fd, line.encode("utf-8"))
            os.fsync(fd)
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)

        logger.debug("Appended entry to %s (%d bytes)", store_name, len(line))

    def append_entry(self, store_name: str, entry: Any) -> None:
        """Append a schema dataclass entry (calls ``to_dict()``).

        Args:
            store_name: One of :data:`VALID_STORES`.
            entry: A schema dataclass with ``to_dict()`` method.
        """
        self.append(store_name, entry.to_dict())

    # -- Read operations ----------------------------------------------------

    def _read_all(self, store_name: str) -> list[dict[str, Any]]:
        """Read all entries from a JSONL store (no locking needed)."""
        _validate_store_name(store_name)
        path = _jsonl_path(self._domain_dir, store_name)
        if not path.is_file():
            return []

        entries: list[dict[str, Any]] = []
        with open(path, "r", encoding="utf-8") as fh:
            for line_no, line in enumerate(fh, 1):
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    entries.append(json.loads(stripped))
                except json.JSONDecodeError:
                    logger.warning(
                        "Skipping malformed line %d in %s", line_no, store_name,
                    )
        return entries

    def query(
        self,
        store_name: str,
        filters: dict[str, Any] | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Query a store with optional key-value filters.

        Filters match on exact equality for scalars and substring
        containment for strings.

        Args:
            store_name: One of :data:`VALID_STORES`.
            filters: Optional dict of field → value matches.
            limit: Maximum entries to return (newest first).

        Returns:
            List of matching entries, newest first.
        """
        entries = self._read_all(store_name)

        if filters:
            matched: list[dict[str, Any]] = []
            for entry in entries:
                if all(
                    self._matches(entry.get(k), v)
                    for k, v in filters.items()
                ):
                    matched.append(entry)
            entries = matched

        # Newest first, then limit
        entries.reverse()
        return entries[:limit]

    def query_latest(
        self,
        store_name: str,
        n: int = 10,
    ) -> list[dict[str, Any]]:
        """Return the last *n* entries (newest first)."""
        entries = self._read_all(store_name)
        entries.reverse()
        return entries[:n]

    def search(
        self,
        store_name: str,
        text: str,
        fields: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Substring search across specified fields.

        Args:
            store_name: One of :data:`VALID_STORES`.
            text: Search string (case-insensitive).
            fields: Fields to search in. If ``None``, searches all
                string-valued fields.

        Returns:
            Matching entries (newest first).
        """
        entries = self._read_all(store_name)
        text_lower = text.lower()
        results: list[dict[str, Any]] = []

        for entry in entries:
            search_fields = fields or [
                k for k, v in entry.items()
                if isinstance(v, (str, list)) and not k.startswith("_")
            ]
            for f in search_fields:
                val = entry.get(f, "")
                if isinstance(val, str) and text_lower in val.lower():
                    results.append(entry)
                    break
                if isinstance(val, list):
                    for item in val:
                        if isinstance(item, str) and text_lower in item.lower():
                            results.append(entry)
                            break

        results.reverse()
        return results

    def count(self, store_name: str) -> int:
        """Return the number of entries in a store."""
        return len(self._read_all(store_name))

    def lookup_fix(self, error_fingerprint: str) -> list[dict[str, Any]]:
        """Convenience: look up known fixes for an error fingerprint.

        Returns fixes newest-first, with ``verification_result == "pass"``
        sorted to the top.
        """
        fixes = self.query(
            "fix_registry",
            filters={"error_fingerprint": error_fingerprint},
            limit=20,
        )
        # Verified fixes first
        fixes.sort(
            key=lambda f: (f.get("verification_result") != "pass", 0),
        )
        return fixes

    def get_file_analysis(self, file_path: str) -> dict[str, Any] | None:
        """Convenience: get the latest analysis for a specific file."""
        results = self.query(
            "codebase_analysis",
            filters={"file_path": file_path},
            limit=1,
        )
        return results[0] if results else None

    def get_patterns(self, domain: str) -> list[dict[str, Any]]:
        """Convenience: get all patterns for a domain area."""
        return self.query(
            "pattern_library",
            filters={"domain": domain},
            limit=100,
        )

    # -- Internal helpers ---------------------------------------------------

    @staticmethod
    def _matches(field_value: Any, filter_value: Any) -> bool:
        """Check if a field value matches a filter value."""
        if field_value is None:
            return False
        if isinstance(filter_value, str) and isinstance(field_value, str):
            return filter_value.lower() in field_value.lower()
        return field_value == filter_value
