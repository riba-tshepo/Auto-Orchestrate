"""Tests for domain memory store, schemas, hooks, and indexer.

Dependencies: Python >= 3.11 stdlib + pytest.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from lib.domain_memory.hooks import (
    normalise_error_fingerprint,
    on_fix_applied,
    on_pattern_discovered,
    on_research_complete,
    on_user_correction,
    on_validation_complete,
)
from lib.domain_memory.indexer import DomainIndexer
from lib.domain_memory.schemas import (
    CodebaseAnalysisEntry,
    DecisionEntry,
    FixEntry,
    PatternEntry,
    ResearchEntry,
    UserPreferenceEntry,
)
from lib.domain_memory.store import DomainMemoryStore


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def domain_dir(tmp_path: Path) -> Path:
    return tmp_path / ".domain"


@pytest.fixture
def store(domain_dir: Path) -> DomainMemoryStore:
    return DomainMemoryStore(
        domain_dir, session_id="test-session", command="test",
    )


# ---------------------------------------------------------------------------
# Schema tests
# ---------------------------------------------------------------------------


class TestSchemas:
    def test_research_entry_round_trip(self) -> None:
        entry = ResearchEntry(
            topic="JWT libs",
            findings=["jsonwebtoken is popular"],
            confidence=0.9,
        )
        d = entry.to_dict()
        assert d["topic"] == "JWT libs"
        assert d["confidence"] == 0.9
        restored = ResearchEntry.from_dict(d)
        assert restored.topic == "JWT libs"
        assert restored.confidence == 0.9

    def test_fix_entry_round_trip(self) -> None:
        entry = FixEntry(
            error_fingerprint="conn_refused_5432",
            error_message="ConnectionRefusedError",
            fix_description="Changed port in .env",
            verification_result="pass",
        )
        d = entry.to_dict()
        restored = FixEntry.from_dict(d)
        assert restored.error_fingerprint == "conn_refused_5432"
        assert restored.verification_result == "pass"

    def test_from_dict_ignores_extra_fields(self) -> None:
        d = {"topic": "test", "unknown_field": "ignored", "confidence": 0.5}
        entry = ResearchEntry.from_dict(d)
        assert entry.topic == "test"

    def test_pattern_entry(self) -> None:
        entry = PatternEntry(
            pattern_type="anti_pattern",
            domain="database",
            description="N+1 queries",
        )
        assert entry.to_dict()["pattern_type"] == "anti_pattern"

    def test_user_preference_entry(self) -> None:
        entry = UserPreferenceEntry(
            preference_type="library_choice",
            key="orm",
            value="sqlalchemy",
        )
        assert entry.to_dict()["source"] == "user_correction"


# ---------------------------------------------------------------------------
# Store tests
# ---------------------------------------------------------------------------


class TestDomainMemoryStore:
    def test_creates_domain_dir(self, domain_dir: Path) -> None:
        DomainMemoryStore(domain_dir)
        assert domain_dir.is_dir()

    def test_append_and_query(self, store: DomainMemoryStore) -> None:
        store.append("research_ledger", {"topic": "auth", "findings": ["f1"]})
        store.append("research_ledger", {"topic": "db", "findings": ["f2"]})

        results = store.query("research_ledger")
        assert len(results) == 2
        # Newest first
        assert results[0]["topic"] == "db"
        assert results[1]["topic"] == "auth"

    def test_auto_injected_metadata(self, store: DomainMemoryStore) -> None:
        store.append("fix_registry", {"error_fingerprint": "test"})
        results = store.query("fix_registry")
        assert results[0]["_session_id"] == "test-session"
        assert results[0]["_command"] == "test"
        assert "_timestamp" in results[0]

    def test_query_with_filters(self, store: DomainMemoryStore) -> None:
        store.append("fix_registry", {
            "error_fingerprint": "err_a", "fix_description": "fix A",
        })
        store.append("fix_registry", {
            "error_fingerprint": "err_b", "fix_description": "fix B",
        })
        results = store.query("fix_registry", filters={"error_fingerprint": "err_a"})
        assert len(results) == 1
        assert results[0]["fix_description"] == "fix A"

    def test_query_latest(self, store: DomainMemoryStore) -> None:
        for i in range(5):
            store.append("pattern_library", {"domain": f"d{i}"})
        latest = store.query_latest("pattern_library", n=2)
        assert len(latest) == 2
        assert latest[0]["domain"] == "d4"

    def test_search(self, store: DomainMemoryStore) -> None:
        store.append("research_ledger", {
            "topic": "JWT authentication", "findings": ["jose is fast"],
        })
        store.append("research_ledger", {
            "topic": "Database migration", "findings": ["alembic works"],
        })
        results = store.search("research_ledger", "JWT")
        assert len(results) == 1
        assert results[0]["topic"] == "JWT authentication"

    def test_search_in_list_fields(self, store: DomainMemoryStore) -> None:
        store.append("research_ledger", {
            "topic": "packages",
            "findings": ["SQLAlchemy is recommended"],
        })
        results = store.search("research_ledger", "SQLAlchemy")
        assert len(results) == 1

    def test_count(self, store: DomainMemoryStore) -> None:
        assert store.count("research_ledger") == 0
        store.append("research_ledger", {"topic": "t1"})
        store.append("research_ledger", {"topic": "t2"})
        assert store.count("research_ledger") == 2

    def test_lookup_fix(self, store: DomainMemoryStore) -> None:
        store.append("fix_registry", {
            "error_fingerprint": "err_x",
            "fix_description": "bad fix",
            "verification_result": "fail",
        })
        store.append("fix_registry", {
            "error_fingerprint": "err_x",
            "fix_description": "good fix",
            "verification_result": "pass",
        })
        fixes = store.lookup_fix("err_x")
        assert len(fixes) == 2
        # Verified fix first
        assert fixes[0]["verification_result"] == "pass"

    def test_invalid_store_name_raises(self, store: DomainMemoryStore) -> None:
        with pytest.raises(ValueError, match="Invalid store name"):
            store.append("nonexistent_store", {"data": "test"})

    def test_empty_store_returns_empty(self, store: DomainMemoryStore) -> None:
        assert store.query("research_ledger") == []

    def test_append_entry_with_schema(self, store: DomainMemoryStore) -> None:
        entry = ResearchEntry(topic="test", findings=["finding1"])
        store.append_entry("research_ledger", entry)
        results = store.query("research_ledger")
        assert len(results) == 1
        assert results[0]["topic"] == "test"


# ---------------------------------------------------------------------------
# Hook tests
# ---------------------------------------------------------------------------


class TestHooks:
    def test_on_research_complete(self, store: DomainMemoryStore) -> None:
        result = on_research_complete(
            store, topic="auth libs", findings=["jose is good"],
        )
        assert result is True
        entries = store.query("research_ledger")
        assert len(entries) == 1
        assert entries[0]["topic"] == "auth libs"

    def test_on_fix_applied(self, store: DomainMemoryStore) -> None:
        result = on_fix_applied(
            store,
            error_fingerprint="conn_refused",
            error_message="ConnectionRefusedError",
            fix_description="Changed port",
            verification_result="pass",
        )
        assert result is True
        fixes = store.lookup_fix("conn_refused")
        assert len(fixes) == 1

    def test_on_pattern_discovered(self, store: DomainMemoryStore) -> None:
        result = on_pattern_discovered(
            store,
            pattern_type="anti_pattern",
            domain="database",
            description="N+1 queries",
        )
        assert result is True

    def test_hooks_safe_with_none_store(self) -> None:
        assert on_research_complete(None, topic="t", findings=[]) is False
        assert on_fix_applied(None, "fp", "msg", "fix") is False
        assert on_user_correction(None, "type", "key", "val") is False

    def test_normalise_error_fingerprint(self) -> None:
        fp = normalise_error_fingerprint(
            "ConnectionRefusedError: /home/user/app/main.py line 42"
        )
        assert "/home/user" not in fp
        assert "42" not in fp or "<n>" in fp
        assert fp == fp.lower()

    def test_normalise_strips_hex(self) -> None:
        fp = normalise_error_fingerprint("SegFault at 0x7fff1234ABCD")
        assert "0x7fff" not in fp
        assert "<hex>" in fp


# ---------------------------------------------------------------------------
# Indexer tests
# ---------------------------------------------------------------------------


class TestDomainIndexer:
    def test_rebuild_and_search(self, store: DomainMemoryStore) -> None:
        store.append("research_ledger", {
            "topic": "JWT authentication",
            "findings": ["jose is lightweight"],
        })
        store.append("research_ledger", {
            "topic": "Database pooling",
            "findings": ["pgbouncer recommended"],
        })

        indexer = DomainIndexer(store)
        total = indexer.rebuild_index()
        assert total >= 2

        results = indexer.search_research("JWT")
        assert len(results) == 1
        assert "JWT" in results[0]["topic"]
        indexer.close()

    def test_lookup_fix_via_indexer(self, store: DomainMemoryStore) -> None:
        store.append("fix_registry", {
            "error_fingerprint": "timeout_api",
            "error_message": "API timeout",
            "fix_description": "Increased timeout to 30s",
            "verification_result": "pass",
        })

        indexer = DomainIndexer(store)
        indexer.rebuild_index()

        fixes = indexer.lookup_fix("timeout_api")
        assert len(fixes) == 1
        assert fixes[0]["verification_result"] == "pass"
        indexer.close()

    def test_get_file_analysis(self, store: DomainMemoryStore) -> None:
        store.append("codebase_analysis", {
            "file_path": "src/auth.py",
            "analysis_type": "security",
            "risk_level": "high",
        })

        indexer = DomainIndexer(store)
        indexer.rebuild_index()

        result = indexer.get_file_analysis("src/auth.py")
        assert result is not None
        assert result["risk_level"] == "high"
        indexer.close()

    def test_empty_index(self, store: DomainMemoryStore) -> None:
        indexer = DomainIndexer(store)
        indexer.rebuild_index()
        assert indexer.search_research("anything") == []
        indexer.close()
