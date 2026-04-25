"""Integration hooks for pipeline stages.

Each hook is called at a specific point in the pipeline to persist
domain knowledge.  Hooks are designed to be called from the orchestrator
agent, debugger agent, or auditor agent at the appropriate stage
completion point.

All hooks are safe to call when domain memory is unavailable —
they log a warning and return without error.

Dependencies: Python >= 3.11 stdlib only.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

from .schemas import (
    CodebaseAnalysisEntry,
    DecisionEntry,
    FixEntry,
    PatternEntry,
    ResearchEntry,
    UserPreferenceEntry,
)
from .store import DomainMemoryStore

logger = logging.getLogger(__name__)


def _safe_append(
    store: DomainMemoryStore | None,
    store_name: str,
    entry: Any,
) -> bool:
    """Safely append to domain memory, returning False on failure."""
    if store is None:
        logger.debug("Domain memory not available; skipping %s append", store_name)
        return False
    try:
        store.append_entry(store_name, entry)
        return True
    except Exception:
        logger.exception("Failed to append to %s", store_name)
        return False


# ---------------------------------------------------------------------------
# Stage hooks
# ---------------------------------------------------------------------------

def on_research_complete(
    store: DomainMemoryStore | None,
    topic: str,
    findings: list[str],
    cves: list[dict[str, str]] | None = None,
    remedies: list[str] | None = None,
    recommendations: list[str] | None = None,
    sources: list[str] | None = None,
    confidence: float = 0.5,
    stage: str = "stage_0",
) -> bool:
    """Persist research findings after Stage 0 completes.

    Called by the orchestrator or researcher agent after research output
    is written.
    """
    entry = ResearchEntry(
        topic=topic,
        findings=findings,
        cves=cves or [],
        remedies=remedies or [],
        recommendations=recommendations or [],
        sources=sources or [],
        confidence=confidence,
        stage=stage,
    )
    return _safe_append(store, "research_ledger", entry)


def on_architecture_complete(
    store: DomainMemoryStore | None,
    decision: str,
    alternatives: list[str] | None = None,
    rationale: str = "",
    constraints: list[str] | None = None,
    stage: str = "stage_1",
    risk_level: str = "medium",
) -> bool:
    """Persist architecture decisions after Stage 1 completes."""
    entry = DecisionEntry(
        decision=decision,
        alternatives=alternatives or [],
        rationale=rationale,
        constraints=constraints or [],
        stage=stage,
        risk_level=risk_level,
    )
    return _safe_append(store, "decision_log", entry)


def on_pattern_discovered(
    store: DomainMemoryStore | None,
    pattern_type: str,
    domain: str,
    description: str,
    code_example: str = "",
    resolution: str = "",
    discovered_in_stage: str = "",
) -> bool:
    """Persist a discovered pattern (success or anti-pattern)."""
    entry = PatternEntry(
        pattern_type=pattern_type,
        domain=domain,
        description=description,
        code_example=code_example,
        resolution=resolution,
        discovered_in_stage=discovered_in_stage,
    )
    return _safe_append(store, "pattern_library", entry)


def on_fix_applied(
    store: DomainMemoryStore | None,
    error_fingerprint: str,
    error_message: str,
    fix_description: str,
    files_modified: list[str] | None = None,
    verification_result: str = "unknown",
    fix_duration_seconds: float = 0.0,
) -> bool:
    """Persist a fix-to-error mapping after a debugger resolves an issue.

    The ``error_fingerprint`` should be a normalised string (lowercase,
    paths/numbers stripped) so the same logical error maps to the same key.
    """
    entry = FixEntry(
        error_fingerprint=error_fingerprint,
        error_message=error_message,
        fix_description=fix_description,
        files_modified=files_modified or [],
        verification_result=verification_result,
        fix_duration_seconds=fix_duration_seconds,
    )
    return _safe_append(store, "fix_registry", entry)


def on_validation_complete(
    store: DomainMemoryStore | None,
    file_path: str,
    analysis_type: str,
    risk_level: str = "low",
    findings: list[str] | None = None,
    tech_debt_score: float = 0.0,
    module: str = "",
    last_analyzed_run: str = "",
) -> bool:
    """Persist file/module analysis after validation or audit."""
    entry = CodebaseAnalysisEntry(
        file_path=file_path,
        analysis_type=analysis_type,
        risk_level=risk_level,
        findings=findings or [],
        tech_debt_score=tech_debt_score,
        module=module,
        last_analyzed_run=last_analyzed_run,
    )
    return _safe_append(store, "codebase_analysis", entry)


def on_user_correction(
    store: DomainMemoryStore | None,
    preference_type: str,
    key: str,
    value: str,
    context: str = "",
) -> bool:
    """Persist a user correction or explicit preference."""
    entry = UserPreferenceEntry(
        preference_type=preference_type,
        key=key,
        value=value,
        context=context,
        source="user_correction",
    )
    return _safe_append(store, "user_preferences", entry)


# ---------------------------------------------------------------------------
# Error fingerprint normalisation
# ---------------------------------------------------------------------------

_PATH_PATTERN = re.compile(r"(?:/[\w./-]+)+")
_NUMBER_PATTERN = re.compile(r"\b\d+\b")
_HEX_PATTERN = re.compile(r"0x[0-9a-fA-F]+")


def normalise_error_fingerprint(error_message: str) -> str:
    """Create a stable fingerprint from an error message.

    Strips file paths, large numbers, and hex addresses so the same
    logical error maps to the same key across different runs.

    Args:
        error_message: Raw error message text.

    Returns:
        Lowercase, normalised fingerprint string.
    """
    text = error_message.lower().strip()
    text = _PATH_PATTERN.sub("<path>", text)
    text = _HEX_PATTERN.sub("<hex>", text)
    text = _NUMBER_PATTERN.sub("<n>", text)
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"[^a-z0-9_<>]", "", text)
    return text[:200]
