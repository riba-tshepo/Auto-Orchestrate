"""
Manifest digest builder (MANIFEST-DIGEST-001).

Token-budget optimization #2: subagents receive a 2k digest instead of the full
~19k manifest.json. Only the orchestrator and session-manager (which validate
the manifest end-to-end) plus tasks marked `needs_full_manifest: true` get the
full manifest.

The digest contains the minimum information any non-special-case agent needs to
route work: agent names with their dispatch_triggers, and skill names with
their triggers. Chaining metadata, activation_rules, full descriptions, and
JSON Schema-only fields are dropped.

Cached per session in process memory.
"""

from __future__ import annotations

import json
from pathlib import Path

_DIGEST_CACHE: dict[str, str] = {}


def build_digest(manifest_path: str | Path) -> str:
    """
    Build a slim text digest of the manifest for subagent spawn prompts.

    Args:
        manifest_path: Absolute path to manifest.json.

    Returns:
        A markdown-flavoured digest (~2k tokens). Cached per absolute path.
    """
    key = str(Path(manifest_path).resolve())
    if key in _DIGEST_CACHE:
        return _DIGEST_CACHE[key]

    with open(key, encoding="utf-8") as f:
        manifest = json.load(f)

    lines: list[str] = []
    lines.append("# Manifest Digest (MANIFEST-DIGEST-001)")
    lines.append("")
    lines.append(
        "This is a SLIM digest of `~/.claude/manifest.json`. It contains agent "
        "names with their dispatch_triggers and skill names with their triggers — "
        "the minimum needed for routing decisions. If you need the full manifest "
        "(chaining metadata, activation_rules, full descriptions, JSON-Schema "
        "fields), set `needs_full_manifest: true` on your task and the loop "
        "controller will inject the full manifest in the next spawn."
    )
    lines.append("")

    # Agents
    lines.append("## Agents")
    lines.append("")
    lines.append("| Name | Dispatch Triggers |")
    lines.append("|---|---|")
    for agent in manifest.get("agents", []):
        name = agent.get("name", "")
        triggers = agent.get("dispatch_triggers", [])
        triggers_str = ", ".join(triggers) if triggers else "—"
        lines.append(f"| `{name}` | {triggers_str} |")
    lines.append("")

    # Skills
    lines.append("## Skills")
    lines.append("")
    lines.append("| Name | Triggers |")
    lines.append("|---|---|")
    for skill in manifest.get("skills", []):
        name = skill.get("name", "")
        triggers = skill.get("dispatch_triggers", []) or skill.get("triggers", [])
        triggers_str = ", ".join(triggers) if triggers else "—"
        lines.append(f"| `{name}` | {triggers_str} |")
    lines.append("")

    # Stats summary
    stats = manifest.get("stats", {})
    if stats:
        lines.append("## Stats")
        lines.append(f"- Total agents: {stats.get('total_agents', len(manifest.get('agents', [])))}")
        lines.append(f"- Total skills: {stats.get('total_skills', len(manifest.get('skills', [])))}")
        lines.append(f"- Total commands: {stats.get('total_commands', len(manifest.get('commands', [])))}")
        lines.append("")

    digest = "\n".join(lines)
    _DIGEST_CACHE[key] = digest
    return digest


def estimate_digest_tokens(manifest_path: str | Path) -> int:
    """Char-based token estimate for the built digest."""
    return len(build_digest(manifest_path)) // 4


def estimate_full_manifest_tokens(manifest_path: str | Path) -> int:
    """Char-based token estimate for the full manifest JSON."""
    return Path(manifest_path).stat().st_size // 4


def clear_cache() -> None:
    """Clear the digest cache (test/long-running-process use only)."""
    _DIGEST_CACHE.clear()


def needs_full_manifest(agent_name: str, task: dict | None = None) -> bool:
    """
    Decide whether a spawn target should receive the full manifest.

    Returns True for:
    - The orchestrator (MAIN-013, AGENT-ACTIVATE-001 routing)
    - The session-manager (MANIFEST-001 boot-time validation)
    - Any task with `needs_full_manifest: true` set explicitly.
    """
    if agent_name in ("orchestrator", "session-manager"):
        return True
    if task and task.get("needs_full_manifest") is True:
        return True
    return False
