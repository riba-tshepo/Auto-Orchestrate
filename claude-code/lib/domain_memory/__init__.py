"""Domain memory — project-level, cross-session knowledge store.

Provides persistent, queryable domain knowledge that grows across all
pipeline sessions (auto-orchestrate, auto-debug, auto-audit). All stores
use append-only JSONL with file-level locking for concurrency safety.

Location: ``.domain/`` at the project root.

Dependencies: Python >= 3.11 stdlib only.
"""

from __future__ import annotations

from .schemas import (
    CodebaseAnalysisEntry,
    DecisionEntry,
    FixEntry,
    PatternEntry,
    ResearchEntry,
    UserPreferenceEntry,
)
from .store import DomainMemoryStore

__all__ = [
    "DomainMemoryStore",
    "ResearchEntry",
    "DecisionEntry",
    "PatternEntry",
    "FixEntry",
    "CodebaseAnalysisEntry",
    "UserPreferenceEntry",
]
