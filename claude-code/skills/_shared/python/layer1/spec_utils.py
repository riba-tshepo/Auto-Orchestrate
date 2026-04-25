"""Shared specification parsing utilities.

Provides common functions for extracting keywords, inferring types, and
determining priority from specification text. Used by spec_parser.py,
spec_validator.py, and any skill that needs to analyze specification content.

Dependencies: Python >= 3.11 stdlib only.
"""

from __future__ import annotations

import re


# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

IMPERATIVE_PATTERNS: list[str] = [
    r"\b(?:must|shall|should|will|needs? to)\b",
    r"\b(?:required|mandatory|essential)\b",
]

PRIORITY_MAP: dict[str, str] = {
    "must": "MUST",
    "shall": "MUST",
    "required": "MUST",
    "mandatory": "MUST",
    "essential": "MUST",
    "should": "SHOULD",
    "recommended": "SHOULD",
    "may": "MAY",
    "optional": "MAY",
    "nice to have": "MAY",
}

TYPE_INDICATORS: dict[str, list[str]] = {
    "functional": [
        "user", "api", "endpoint", "crud", "create", "read", "update",
        "delete", "login", "register", "search", "filter", "export",
        "import", "upload", "download", "notify", "email", "payment",
        "report",
    ],
    "non-functional": [
        "performance", "scalab", "reliab", "availab", "security",
        "latency", "throughput", "uptime", "response time", "load",
        "concurrent",
    ],
    "service": [
        "docker", "container", "service", "deploy", "infrastructure",
        "database", "cache", "queue", "broker", "proxy", "nginx",
    ],
    "security": [
        "auth", "encrypt", "ssl", "tls", "rbac", "permission", "token",
        "password", "hash", "sanitiz", "injection", "xss", "csrf",
    ],
}

_STOP_WORDS: frozenset[str] = frozenset({
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "must", "shall", "can", "need", "to", "of",
    "in", "for", "on", "with", "at", "by", "from", "as", "into", "through",
    "that", "this", "it", "its", "and", "or", "but", "not", "no", "all",
    "each", "every", "any", "some", "when", "where", "how", "what", "which",
    "who", "whom", "system", "application", "feature", "support",
})


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_keywords(text: str) -> list[str]:
    """Extract meaningful keywords from a requirement description.

    Args:
        text: The requirement text to extract keywords from.

    Returns:
        Up to 10 deduplicated keywords, preserving order of first appearance.
    """
    words = re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", text.lower())
    keywords = [w for w in words if w not in _STOP_WORDS and len(w) > 2]
    seen: set[str] = set()
    return [k for k in keywords if k not in seen and not seen.add(k)][:10]


def infer_type(text: str) -> str:
    """Infer requirement type from description text.

    Args:
        text: The requirement text to classify.

    Returns:
        One of: 'functional', 'non-functional', 'service', 'security'.
        Defaults to 'functional' if no indicators match.
    """
    lower = text.lower()
    scores: dict[str, int] = {}
    for rtype, indicators in TYPE_INDICATORS.items():
        scores[rtype] = sum(1 for ind in indicators if ind in lower)
    if not any(scores.values()):
        return "functional"
    return max(scores, key=scores.get)


def infer_priority(text: str) -> str:
    """Infer priority from imperative language in text.

    Args:
        text: The requirement text to analyze.

    Returns:
        One of: 'MUST', 'SHOULD', 'MAY'. Defaults to 'SHOULD'.
    """
    lower = text.lower()
    for keyword, priority in PRIORITY_MAP.items():
        if keyword in lower:
            return priority
    return "SHOULD"
