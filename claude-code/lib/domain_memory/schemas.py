"""Entry schemas for each domain memory store.

Each schema is a frozen dataclass with ``to_dict()`` / ``from_dict()``
serialisation helpers.  All fields use stdlib types only.

Dependencies: Python >= 3.11 stdlib only.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Base mixin
# ---------------------------------------------------------------------------

class _DictMixin:
    """Adds ``to_dict`` and ``from_dict`` to dataclasses."""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)  # type: ignore[arg-type]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Any:
        known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        filtered = {k: v for k, v in data.items() if k in known}
        return cls(**filtered)


# ---------------------------------------------------------------------------
# research_ledger.jsonl
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ResearchEntry(_DictMixin):
    """A single research finding from Stage 0 or manual research."""

    topic: str
    findings: list[str] = field(default_factory=list)
    cves: list[dict[str, str]] = field(default_factory=list)
    remedies: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    confidence: float = 0.5
    stage: str = "stage_0"


# ---------------------------------------------------------------------------
# decision_log.jsonl
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DecisionEntry(_DictMixin):
    """An architecture or design decision record."""

    decision: str
    alternatives: list[str] = field(default_factory=list)
    rationale: str = ""
    constraints: list[str] = field(default_factory=list)
    stage: str = "stage_1"
    risk_level: str = "medium"
    evidence_run_ids: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# pattern_library.jsonl
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PatternEntry(_DictMixin):
    """A discovered pattern (success or anti-pattern)."""

    pattern_type: str  # "success" | "anti_pattern"
    domain: str  # e.g. "database", "auth", "api"
    description: str
    code_example: str = ""
    resolution: str = ""
    discovered_in_stage: str = ""
    frequency: int = 1


# ---------------------------------------------------------------------------
# fix_registry.jsonl
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FixEntry(_DictMixin):
    """Maps an error fingerprint to the fix that resolved it."""

    error_fingerprint: str
    error_message: str
    fix_description: str
    files_modified: list[str] = field(default_factory=list)
    verification_result: str = "unknown"  # "pass" | "fail" | "unknown"
    fix_duration_seconds: float = 0.0


# ---------------------------------------------------------------------------
# codebase_analysis.jsonl
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CodebaseAnalysisEntry(_DictMixin):
    """Per-file or per-module analysis result."""

    file_path: str
    analysis_type: str  # "security_audit", "complexity", "tech_debt", ...
    risk_level: str = "low"  # "low" | "medium" | "high" | "critical"
    findings: list[str] = field(default_factory=list)
    tech_debt_score: float = 0.0
    module: str = ""
    last_analyzed_run: str = ""


# ---------------------------------------------------------------------------
# user_preferences.jsonl
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class UserPreferenceEntry(_DictMixin):
    """A user correction or explicit preference."""

    preference_type: str  # "library_choice", "style", "architecture", ...
    key: str
    value: str
    context: str = ""
    source: str = "user_correction"  # "user_correction" | "explicit"
