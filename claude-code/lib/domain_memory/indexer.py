"""SQLite WAL-mode index for fast domain memory queries.

The index is a **derived artifact** — it can always be rebuilt from the
JSONL source-of-truth files.  WAL mode allows concurrent readers with
a single writer.

Dependencies: Python >= 3.11 stdlib only.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from pathlib import Path
from typing import Any

from .store import VALID_STORES, DomainMemoryStore

logger = logging.getLogger(__name__)

_DB_NAME = "domain_index.db"


class DomainIndexer:
    """SQLite FTS5 index over domain memory JSONL files.

    Usage::

        indexer = DomainIndexer(store)
        indexer.rebuild_index()
        results = indexer.search_research("JWT authentication")
    """

    def __init__(self, store: DomainMemoryStore) -> None:
        self._store = store
        self._db_path = store.domain_dir / _DB_NAME
        self._conn: sqlite3.Connection | None = None

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(
                str(self._db_path),
                isolation_level="DEFERRED",
            )
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA synchronous=NORMAL")
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    # -- Schema creation ----------------------------------------------------

    def _create_tables(self) -> None:
        conn = self._get_conn()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS research (
                rowid INTEGER PRIMARY KEY,
                timestamp TEXT,
                session_id TEXT,
                topic TEXT,
                findings TEXT,
                cves TEXT,
                remedies TEXT,
                recommendations TEXT,
                confidence REAL,
                stage TEXT
            );

            CREATE TABLE IF NOT EXISTS fixes (
                rowid INTEGER PRIMARY KEY,
                timestamp TEXT,
                session_id TEXT,
                error_fingerprint TEXT,
                error_message TEXT,
                fix_description TEXT,
                files_modified TEXT,
                verification_result TEXT
            );

            CREATE TABLE IF NOT EXISTS patterns (
                rowid INTEGER PRIMARY KEY,
                timestamp TEXT,
                session_id TEXT,
                pattern_type TEXT,
                domain TEXT,
                description TEXT,
                resolution TEXT,
                frequency INTEGER
            );

            CREATE TABLE IF NOT EXISTS codebase (
                rowid INTEGER PRIMARY KEY,
                timestamp TEXT,
                session_id TEXT,
                file_path TEXT,
                analysis_type TEXT,
                risk_level TEXT,
                findings TEXT,
                tech_debt_score REAL,
                module TEXT
            );

            CREATE TABLE IF NOT EXISTS decisions (
                rowid INTEGER PRIMARY KEY,
                timestamp TEXT,
                session_id TEXT,
                decision TEXT,
                rationale TEXT,
                stage TEXT,
                risk_level TEXT
            );

            CREATE TABLE IF NOT EXISTS preferences (
                rowid INTEGER PRIMARY KEY,
                timestamp TEXT,
                session_id TEXT,
                preference_type TEXT,
                key TEXT,
                value TEXT,
                context TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_research_topic ON research(topic);
            CREATE INDEX IF NOT EXISTS idx_fixes_fingerprint ON fixes(error_fingerprint);
            CREATE INDEX IF NOT EXISTS idx_patterns_domain ON patterns(domain);
            CREATE INDEX IF NOT EXISTS idx_codebase_filepath ON codebase(file_path);
            CREATE INDEX IF NOT EXISTS idx_preferences_key ON preferences(key);
        """)
        conn.commit()

    # -- Rebuild from JSONL -------------------------------------------------

    def rebuild_index(self) -> int:
        """Drop and rebuild the entire index from JSONL files.

        Returns:
            Total number of entries indexed.
        """
        conn = self._get_conn()
        for table in ("research", "fixes", "patterns", "codebase",
                       "decisions", "preferences"):
            conn.execute(f"DROP TABLE IF EXISTS {table}")  # noqa: S608
        conn.commit()

        self._create_tables()

        total = 0
        store_to_table = {
            "research_ledger": "research",
            "fix_registry": "fixes",
            "pattern_library": "patterns",
            "codebase_analysis": "codebase",
            "decision_log": "decisions",
            "user_preferences": "preferences",
        }

        for store_name, table in store_to_table.items():
            entries = self._store._read_all(store_name)
            if not entries:
                continue

            for entry in entries:
                self._insert_entry(conn, table, entry)
                total += 1

        conn.commit()
        logger.info("Rebuilt domain index: %d entries across %d stores",
                     total, len(store_to_table))
        return total

    def _insert_entry(
        self, conn: sqlite3.Connection, table: str, entry: dict,
    ) -> None:
        """Insert a single entry into the appropriate table."""
        ts = entry.get("_timestamp", "")
        sid = entry.get("_session_id", "")

        if table == "research":
            conn.execute(
                "INSERT INTO research (timestamp, session_id, topic, "
                "findings, cves, remedies, recommendations, confidence, stage) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (ts, sid, entry.get("topic", ""),
                 json.dumps(entry.get("findings", [])),
                 json.dumps(entry.get("cves", [])),
                 json.dumps(entry.get("remedies", [])),
                 json.dumps(entry.get("recommendations", [])),
                 entry.get("confidence", 0.5),
                 entry.get("stage", "")),
            )
        elif table == "fixes":
            conn.execute(
                "INSERT INTO fixes (timestamp, session_id, error_fingerprint, "
                "error_message, fix_description, files_modified, verification_result) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (ts, sid, entry.get("error_fingerprint", ""),
                 entry.get("error_message", ""),
                 entry.get("fix_description", ""),
                 json.dumps(entry.get("files_modified", [])),
                 entry.get("verification_result", "unknown")),
            )
        elif table == "patterns":
            conn.execute(
                "INSERT INTO patterns (timestamp, session_id, pattern_type, "
                "domain, description, resolution, frequency) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (ts, sid, entry.get("pattern_type", ""),
                 entry.get("domain", ""),
                 entry.get("description", ""),
                 entry.get("resolution", ""),
                 entry.get("frequency", 1)),
            )
        elif table == "codebase":
            conn.execute(
                "INSERT INTO codebase (timestamp, session_id, file_path, "
                "analysis_type, risk_level, findings, tech_debt_score, module) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (ts, sid, entry.get("file_path", ""),
                 entry.get("analysis_type", ""),
                 entry.get("risk_level", "low"),
                 json.dumps(entry.get("findings", [])),
                 entry.get("tech_debt_score", 0.0),
                 entry.get("module", "")),
            )
        elif table == "decisions":
            conn.execute(
                "INSERT INTO decisions (timestamp, session_id, decision, "
                "rationale, stage, risk_level) VALUES (?, ?, ?, ?, ?, ?)",
                (ts, sid, entry.get("decision", ""),
                 entry.get("rationale", ""),
                 entry.get("stage", ""),
                 entry.get("risk_level", "medium")),
            )
        elif table == "preferences":
            conn.execute(
                "INSERT INTO preferences (timestamp, session_id, "
                "preference_type, key, value, context) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (ts, sid, entry.get("preference_type", ""),
                 entry.get("key", ""),
                 entry.get("value", ""),
                 entry.get("context", "")),
            )

    # -- Query methods ------------------------------------------------------

    def search_research(self, topic: str, limit: int = 20) -> list[dict]:
        """Search research entries by topic substring."""
        conn = self._get_conn()
        self._create_tables()
        rows = conn.execute(
            "SELECT * FROM research WHERE topic LIKE ? "
            "ORDER BY timestamp DESC LIMIT ?",
            (f"%{topic}%", limit),
        ).fetchall()
        return [dict(r) for r in rows]

    def lookup_fix(self, error_fingerprint: str) -> list[dict]:
        """Look up fixes by exact error fingerprint."""
        conn = self._get_conn()
        self._create_tables()
        rows = conn.execute(
            "SELECT * FROM fixes WHERE error_fingerprint = ? "
            "ORDER BY CASE verification_result WHEN 'pass' THEN 0 ELSE 1 END, "
            "timestamp DESC",
            (error_fingerprint,),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_file_analysis(self, file_path: str) -> dict | None:
        """Get the latest analysis for a file."""
        conn = self._get_conn()
        self._create_tables()
        row = conn.execute(
            "SELECT * FROM codebase WHERE file_path = ? "
            "ORDER BY timestamp DESC LIMIT 1",
            (file_path,),
        ).fetchone()
        return dict(row) if row else None

    def get_patterns(self, domain: str, limit: int = 50) -> list[dict]:
        """Get patterns for a domain area."""
        conn = self._get_conn()
        self._create_tables()
        rows = conn.execute(
            "SELECT * FROM patterns WHERE domain LIKE ? "
            "ORDER BY frequency DESC, timestamp DESC LIMIT ?",
            (f"%{domain}%", limit),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_user_preference(self, key: str) -> dict | None:
        """Get the latest user preference for a key."""
        conn = self._get_conn()
        self._create_tables()
        row = conn.execute(
            "SELECT * FROM preferences WHERE key = ? "
            "ORDER BY timestamp DESC LIMIT 1",
            (key,),
        ).fetchone()
        return dict(row) if row else None
