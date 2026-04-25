"""5 Whys root cause classifier for pipeline failure analysis.

Classifies pipeline failures into one of eight categories (transient, spec_gap,
dependency, hallucination, resource_exhaustion, configuration, permissions,
timeout) using keyword-based pattern matching and contextual signals. Produces
a structured 5 Whys chain tracing each failure to its root cause.

Designed for integration with retrospective_analyzer.py, which invokes
classify_failure() for each detected regression or stage failure.

Dependencies: Python >= 3.11 stdlib only.
"""

from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_MAX_WHY_LENGTH = 200

_VALID_STAGES = frozenset({
    "stage_0", "stage_1", "stage_2", "stage_3", "stage_4",
    "stage_4_5", "stage_5", "stage_6", "overall",
})

_VALID_CATEGORIES = frozenset({
    "transient", "spec_gap", "dependency", "hallucination",
    "resource_exhaustion", "configuration", "permissions", "timeout",
})

# ---------------------------------------------------------------------------
# Keyword sets for pattern-based classification
# ---------------------------------------------------------------------------

_TRANSIENT_KEYWORDS: tuple[str, ...] = (
    "timeout",
    "rate limit",
    "rate_limit",
    "429",
    "503",
    "eagain",
    "connection reset",
    "connection refused",
    "temporary",
    "transient",
    "retry",
    "econnreset",
    "etimedout",
    "socket hang up",
)

_DEPENDENCY_KEYWORDS: tuple[str, ...] = (
    "no module named",
    "cannot import",
    "package not found",
    "command not found",
    "modulenotfounderror",
    "importerror",
    "filenotfounderror",
    "version mismatch",
    "version conflict",
    "incompatible version",
    "missing dependency",
    "pip install",
    "module not installed",
)

_HALLUCINATION_KEYWORDS: tuple[str, ...] = (
    "assertionerror",
    "attributeerror",
    "has no attribute",
    "unexpected keyword argument",
    "incorrect output",
    "wrong result",
    "typeerror",
    "got an unexpected",
    "not callable",
    "object is not subscriptable",
    "takes 0 positional arguments",
    "missing required argument",
)

_SPEC_GAP_KEYWORDS: tuple[str, ...] = (
    "not specified",
    "ambiguous",
    "undefined behavior",
    "missing requirement",
    "acceptance criteria gap",
    "spec compliance",
    "compliance gap",
    "not defined in spec",
    "unspecified",
    "missing field",
    "schema mismatch",
    "undocumented",
)

_RESOURCE_EXHAUSTION_KEYWORDS: tuple[str, ...] = (
    "out of memory", "oom", "oomkilled", "disk full", "no space left",
    "resource limit", "memory limit", "cannot allocate memory",
    "resource exhausted", "quota exceeded", "storage full",
    "insufficient memory", "heap space", "gc overhead",
)

_CONFIGURATION_KEYWORDS: tuple[str, ...] = (
    "config error", "invalid config", "configuration error",
    "missing env", "environment variable", "bad configuration",
    "misconfigured", "invalid setting", "config not found",
    "missing configuration", "invalid option", "unrecognized option",
)

_PERMISSIONS_KEYWORDS: tuple[str, ...] = (
    "permission denied", "access denied", "forbidden", "403",
    "unauthorized", "401", "insufficient permissions",
    "operation not permitted", "eacces", "eperm",
    "authentication failed", "credentials",
)

_TIMEOUT_KEYWORDS: tuple[str, ...] = (
    "timed out", "deadline exceeded", "context deadline",
    "read timeout", "write timeout", "connect timeout",
    "operation timed out", "request timeout", "gateway timeout",
    "504", "context canceled",
)

# Compiled regex patterns for higher-confidence matches
_IMPORT_ERROR_PATTERN = re.compile(
    r"(?:ImportError|ModuleNotFoundError)", re.IGNORECASE
)
_ATTRIBUTE_ERROR_PATTERN = re.compile(
    r"AttributeError:\s+.*has no attribute", re.IGNORECASE
)
_ASSERTION_ERROR_PATTERN = re.compile(
    r"AssertionError|assert\s+.*==\s+.*failed", re.IGNORECASE
)
_TIMEOUT_PATTERN = re.compile(
    r"(?:TimeoutError|asyncio\.TimeoutError|ReadTimeout|ConnectTimeout)",
    re.IGNORECASE,
)
_HTTP_ERROR_PATTERN = re.compile(r"(?:HTTP\s+)?(?:429|503|502|504)")
_OOM_PATTERN = re.compile(
    r"(?:OutOfMemoryError|MemoryError|OOMKilled|Cannot allocate memory)",
    re.IGNORECASE,
)
_PERMISSION_PATTERN = re.compile(
    r"(?:PermissionError|Permission denied|EACCES|EPERM)",
    re.IGNORECASE,
)
_TIMEOUT_SPECIFIC_PATTERN = re.compile(
    r"(?:TimeoutError|DeadlineExceeded|context deadline exceeded|gateway timeout)",
    re.IGNORECASE,
)
_CONFIG_PATTERN = re.compile(
    r"(?:ConfigError|ConfigurationError|InvalidConfig|config.*not found)",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------

def _count_keyword_hits(text: str, keywords: tuple[str, ...]) -> int:
    """Count how many keywords from the set appear in the text."""
    return sum(1 for kw in keywords if kw in text)


def _score_dependency(error_lower: str, context: dict[str, Any]) -> float:
    """Compute dependency failure confidence score."""
    if _IMPORT_ERROR_PATTERN.search(error_lower):
        return 0.95

    hit_count = _count_keyword_hits(error_lower, _DEPENDENCY_KEYWORDS)
    if hit_count == 0:
        return 0.0

    base_score = 0.7
    increment = min(hit_count * 0.1, 0.2)
    return min(base_score + increment, 0.9)


def _score_transient(
    error_lower: str,
    context: dict[str, Any],
) -> float:
    """Compute transient failure confidence score."""
    score = 0.0
    retry_count = context.get("retry_count", 0)
    retry_succeeded = context.get("retry_succeeded", False)

    if retry_succeeded and retry_count > 0:
        score = max(score, 0.8)

    if _TIMEOUT_PATTERN.search(error_lower):
        score = max(score, 0.7)

    if _HTTP_ERROR_PATTERN.search(error_lower):
        score = max(score, 0.65)

    hit_count = _count_keyword_hits(error_lower, _TRANSIENT_KEYWORDS)
    if hit_count > 0:
        keyword_score = min(0.5 + hit_count * 0.1, 0.85)
        score = max(score, keyword_score)

    consecutive_failures = context.get("consecutive_run_failures", 0)
    if consecutive_failures >= 2:
        score = min(score, 0.45)

    return score


def _score_spec_gap(
    error_lower: str,
    context: dict[str, Any],
) -> float:
    """Compute spec gap failure confidence score."""
    validator_output = context.get("validator_output", "")
    validator_lower = validator_output.lower() if validator_output else ""
    combined = error_lower + " " + validator_lower

    hit_count = _count_keyword_hits(combined, _SPEC_GAP_KEYWORDS)
    if hit_count == 0:
        return 0.0

    score = min(0.5 + hit_count * 0.1, 0.85)

    if "spec_compliance" in validator_lower or "compliance gap" in validator_lower:
        score = max(score, 0.7)

    spec_sections = context.get("spec_sections", [])
    if spec_sections and len(spec_sections) == 0:
        score = max(score, 0.6)

    return score


def _score_hallucination(
    error_lower: str,
    context: dict[str, Any],
) -> float:
    """Compute hallucination failure confidence score."""
    score = 0.0

    if _ATTRIBUTE_ERROR_PATTERN.search(error_lower):
        score = max(score, 0.7)

    if _ASSERTION_ERROR_PATTERN.search(error_lower):
        score = max(score, 0.7)

    hit_count = _count_keyword_hits(error_lower, _HALLUCINATION_KEYWORDS)
    if hit_count > 0:
        keyword_score = min(0.5 + hit_count * 0.15, 0.85)
        score = max(score, keyword_score)

    return score


def _score_resource_exhaustion(error_lower: str, context: dict[str, Any]) -> float:
    """Compute resource exhaustion failure confidence score."""
    if _OOM_PATTERN.search(error_lower):
        return 0.95
    hit_count = _count_keyword_hits(error_lower, _RESOURCE_EXHAUSTION_KEYWORDS)
    if hit_count == 0:
        return 0.0
    return min(0.6 + hit_count * 0.1, 0.9)


def _score_configuration(error_lower: str, context: dict[str, Any]) -> float:
    """Compute configuration failure confidence score."""
    if _CONFIG_PATTERN.search(error_lower):
        return 0.85
    hit_count = _count_keyword_hits(error_lower, _CONFIGURATION_KEYWORDS)
    if hit_count == 0:
        return 0.0
    return min(0.5 + hit_count * 0.1, 0.85)


def _score_permissions(error_lower: str, context: dict[str, Any]) -> float:
    """Compute permissions failure confidence score."""
    if _PERMISSION_PATTERN.search(error_lower):
        return 0.9
    hit_count = _count_keyword_hits(error_lower, _PERMISSIONS_KEYWORDS)
    if hit_count == 0:
        return 0.0
    return min(0.6 + hit_count * 0.1, 0.85)


def _score_timeout(error_lower: str, context: dict[str, Any]) -> float:
    """Compute timeout failure confidence score."""
    if _TIMEOUT_SPECIFIC_PATTERN.search(error_lower):
        return 0.85
    hit_count = _count_keyword_hits(error_lower, _TIMEOUT_KEYWORDS)
    if hit_count == 0:
        return 0.0
    score = min(0.5 + hit_count * 0.1, 0.85)
    consecutive = context.get("consecutive_run_failures", 0)
    if consecutive >= 2:
        score = min(score, 0.5)  # likely not timeout if keeps failing
    return score


# ---------------------------------------------------------------------------
# 5 Whys chain generation
# ---------------------------------------------------------------------------

def _clamp(text: str, max_length: int) -> str:
    """Truncate text to max_length, preserving readability."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def _build_dependency_chain(
    error_message: str,
    stage: str,
    context: dict[str, Any],
) -> list[str]:
    """Build a 5 Whys chain for dependency failures."""
    short_error = _clamp(error_message.strip(), _MAX_WHY_LENGTH)
    return [
        _clamp(f"{stage} failed: {short_error}", _MAX_WHY_LENGTH),
        _clamp(
            "Required dependency is not available in the execution environment",
            _MAX_WHY_LENGTH,
        ),
        _clamp(
            f"{stage} assumed the dependency was installed based on earlier "
            "stage output",
            _MAX_WHY_LENGTH,
        ),
        _clamp(
            "The specification did not include explicit dependency "
            "verification steps",
            _MAX_WHY_LENGTH,
        ),
        _clamp(
            "Stage 0 research did not verify dependency availability "
            "before recommending it",
            _MAX_WHY_LENGTH,
        ),
    ]


def _build_transient_chain(
    error_message: str,
    stage: str,
    context: dict[str, Any],
) -> list[str]:
    """Build a 5 Whys chain for transient failures."""
    short_error = _clamp(error_message.strip(), _MAX_WHY_LENGTH)
    retry_count = context.get("retry_count", 0)

    whys = [
        _clamp(f"{stage} failed: {short_error}", _MAX_WHY_LENGTH),
        _clamp(
            "A transient error occurred (network, rate limit, or resource "
            "exhaustion)",
            _MAX_WHY_LENGTH,
        ),
        _clamp(
            "No retry-with-backoff strategy was configured for this "
            "failure mode",
            _MAX_WHY_LENGTH,
        ),
    ]

    if retry_count > 0:
        whys.append(_clamp(
            f"The stage required {retry_count} retries before resolution",
            _MAX_WHY_LENGTH,
        ))

    whys.append(_clamp(
        "The specification did not mandate resilience patterns for "
        "external calls",
        _MAX_WHY_LENGTH,
    ))
    return whys[:5]


def _build_spec_gap_chain(
    error_message: str,
    stage: str,
    context: dict[str, Any],
) -> list[str]:
    """Build a 5 Whys chain for spec gap failures."""
    short_error = _clamp(error_message.strip(), _MAX_WHY_LENGTH)
    return [
        _clamp(f"{stage} failed: {short_error}", _MAX_WHY_LENGTH),
        _clamp(
            "The implementation followed the specification but the spec "
            "was insufficient",
            _MAX_WHY_LENGTH,
        ),
        _clamp(
            "Key requirements or edge cases were not enumerated in the "
            "specification",
            _MAX_WHY_LENGTH,
        ),
        _clamp(
            "The spec-creator stage did not surface all acceptance criteria",
            _MAX_WHY_LENGTH,
        ),
        _clamp(
            "Stage 0 research did not identify known edge cases from prior "
            "failure patterns",
            _MAX_WHY_LENGTH,
        ),
    ]


def _build_hallucination_chain(
    error_message: str,
    stage: str,
    context: dict[str, Any],
) -> list[str]:
    """Build a 5 Whys chain for hallucination failures."""
    short_error = _clamp(error_message.strip(), _MAX_WHY_LENGTH)
    return [
        _clamp(f"{stage} failed: {short_error}", _MAX_WHY_LENGTH),
        _clamp(
            "The generated code is syntactically valid but semantically "
            "incorrect",
            _MAX_WHY_LENGTH,
        ),
        _clamp(
            "The LLM produced output that does not match the actual API "
            "or expected behavior",
            _MAX_WHY_LENGTH,
        ),
        _clamp(
            "The specification did not provide reference implementations "
            "or example I/O pairs",
            _MAX_WHY_LENGTH,
        ),
        _clamp(
            "Stage 0 research did not include verified API signatures or "
            "usage examples",
            _MAX_WHY_LENGTH,
        ),
    ]


def _build_resource_exhaustion_chain(
    error_message: str,
    stage: str,
    context: dict[str, Any],
) -> list[str]:
    """Build a 5 Whys chain for resource exhaustion failures."""
    short_error = _clamp(error_message.strip(), _MAX_WHY_LENGTH)
    return [
        _clamp(f"{stage} failed: {short_error}", _MAX_WHY_LENGTH),
        _clamp(
            "Resource exhaustion",
            _MAX_WHY_LENGTH,
        ),
        _clamp(
            "Workload exceeded available resources",
            _MAX_WHY_LENGTH,
        ),
        _clamp(
            "No resource limit monitoring",
            _MAX_WHY_LENGTH,
        ),
        _clamp(
            "Capacity planning not included in spec",
            _MAX_WHY_LENGTH,
        ),
    ]


def _build_configuration_chain(
    error_message: str,
    stage: str,
    context: dict[str, Any],
) -> list[str]:
    """Build a 5 Whys chain for configuration failures."""
    short_error = _clamp(error_message.strip(), _MAX_WHY_LENGTH)
    return [
        _clamp(f"{stage} failed: {short_error}", _MAX_WHY_LENGTH),
        _clamp(
            "Configuration error",
            _MAX_WHY_LENGTH,
        ),
        _clamp(
            "Required configuration missing or invalid",
            _MAX_WHY_LENGTH,
        ),
        _clamp(
            "Configuration not validated at startup",
            _MAX_WHY_LENGTH,
        ),
        _clamp(
            "Spec did not enumerate all config requirements",
            _MAX_WHY_LENGTH,
        ),
    ]


def _build_permissions_chain(
    error_message: str,
    stage: str,
    context: dict[str, Any],
) -> list[str]:
    """Build a 5 Whys chain for permissions failures."""
    short_error = _clamp(error_message.strip(), _MAX_WHY_LENGTH)
    return [
        _clamp(f"{stage} failed: {short_error}", _MAX_WHY_LENGTH),
        _clamp(
            "Permission denied",
            _MAX_WHY_LENGTH,
        ),
        _clamp(
            "Insufficient access rights for required resource",
            _MAX_WHY_LENGTH,
        ),
        _clamp(
            "Security policy blocks the required operation",
            _MAX_WHY_LENGTH,
        ),
        _clamp(
            "Permission requirements not documented in spec",
            _MAX_WHY_LENGTH,
        ),
    ]


def _build_timeout_chain(
    error_message: str,
    stage: str,
    context: dict[str, Any],
) -> list[str]:
    """Build a 5 Whys chain for timeout failures."""
    short_error = _clamp(error_message.strip(), _MAX_WHY_LENGTH)
    return [
        _clamp(f"{stage} failed: {short_error}", _MAX_WHY_LENGTH),
        _clamp(
            "Operation timed out",
            _MAX_WHY_LENGTH,
        ),
        _clamp(
            "External service or resource unresponsive",
            _MAX_WHY_LENGTH,
        ),
        _clamp(
            "No timeout budget allocated for this operation",
            _MAX_WHY_LENGTH,
        ),
        _clamp(
            "Performance requirements not specified",
            _MAX_WHY_LENGTH,
        ),
    ]


_CHAIN_BUILDERS: dict[str, Any] = {
    "dependency": _build_dependency_chain,
    "transient": _build_transient_chain,
    "spec_gap": _build_spec_gap_chain,
    "hallucination": _build_hallucination_chain,
    "resource_exhaustion": _build_resource_exhaustion_chain,
    "configuration": _build_configuration_chain,
    "permissions": _build_permissions_chain,
    "timeout": _build_timeout_chain,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def classify_failure(
    error_message: str,
    stage: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Classify a pipeline failure into a root cause category.

    Uses keyword-based pattern matching and contextual signals (retry counts,
    validator output) to determine the most likely failure category and
    generate a 5 Whys root cause chain.

    Args:
        error_message: The error message or traceback string from the failed
            stage. May be empty or None for graceful degradation.
        stage: The pipeline stage identifier where the failure occurred
            (e.g. ``"stage_3"``).
        context: Optional dictionary with additional signals:
            - retry_count (int): Number of retries attempted.
            - retry_succeeded (bool): Whether a retry resolved the failure.
            - validator_output (str): Output from the stage 5 validator.
            - spec_sections (list[str]): Spec sections referenced.
            - consecutive_run_failures (int): Failures across consecutive runs.

    Returns:
        Dictionary with three keys:
            - category (str): One of ``'transient'``, ``'spec_gap'``,
              ``'dependency'``, ``'hallucination'``,
              ``'resource_exhaustion'``, ``'configuration'``,
              ``'permissions'``, ``'timeout'``.
            - confidence (float): Classification confidence from 0.0 to 1.0.
            - five_whys_chain (list[str]): 3 to 5 strings tracing the root
              cause.
    """
    ctx = context if context is not None else {}

    if not error_message or not isinstance(error_message, str):
        logger.warning(
            "Empty or null error_message received for stage=%r; "
            "returning transient with low confidence",
            stage,
        )
        return {
            "category": "transient",
            "confidence": 0.1,
            "five_whys_chain": [
                _clamp(
                    f"{stage} failed with an unspecified error",
                    _MAX_WHY_LENGTH,
                ),
                _clamp(
                    "No error message was captured from the failed stage",
                    _MAX_WHY_LENGTH,
                ),
                _clamp(
                    "The pipeline instrumentation did not propagate the "
                    "error details",
                    _MAX_WHY_LENGTH,
                ),
            ],
        }

    if not stage or not isinstance(stage, str):
        logger.warning(
            "Empty or null stage received; defaulting to 'overall'"
        )
        stage = "overall"

    error_lower = error_message.lower()

    scores: dict[str, float] = {
        "dependency": _score_dependency(error_lower, ctx),
        "transient": _score_transient(error_lower, ctx),
        "spec_gap": _score_spec_gap(error_lower, ctx),
        "hallucination": _score_hallucination(error_lower, ctx),
        "resource_exhaustion": _score_resource_exhaustion(error_lower, ctx),
        "configuration": _score_configuration(error_lower, ctx),
        "permissions": _score_permissions(error_lower, ctx),
        "timeout": _score_timeout(error_lower, ctx),
    }

    best_category = max(scores, key=lambda k: scores[k])
    best_confidence = scores[best_category]

    if best_confidence == 0.0:
        best_category = "spec_gap"
        best_confidence = 0.3
        logger.info(
            "No keyword signals matched for stage=%r; defaulting to "
            "spec_gap with confidence=0.3",
            stage,
        )

    best_confidence = round(best_confidence, 2)

    chain_builder = _CHAIN_BUILDERS[best_category]
    five_whys_chain = chain_builder(error_message, stage, ctx)

    logger.debug(
        "Classified failure: stage=%r category=%r confidence=%.2f",
        stage,
        best_category,
        best_confidence,
    )

    return {
        "category": best_category,
        "confidence": best_confidence,
        "five_whys_chain": five_whys_chain,
    }
