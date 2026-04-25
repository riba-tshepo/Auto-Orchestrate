"""
Skill frontmatter reader (SKILL-FRONTMATTER-001).

Loads only the YAML frontmatter from a SKILL.md file for skill discovery /
routing decisions. The full SKILL.md body is loaded only when the skill is
actually invoked.

Token-budget optimization #3: a typical SKILL.md is ~2.5k tokens; frontmatter
is ~300 tok. Loading frontmatter-only during discovery saves ~80% per skill
considered.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml


_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


class FrontmatterError(ValueError):
    """Raised when SKILL.md frontmatter is missing or malformed."""


def read_frontmatter(skill_path: str | Path) -> dict:
    """
    Read and parse YAML frontmatter from a SKILL.md file.

    Args:
        skill_path: Path to a skill directory or directly to SKILL.md.

    Returns:
        Parsed frontmatter dict. Always contains "name" and "description".
        May contain "triggers", "license", "allowed-tools", "metadata".

    Raises:
        FileNotFoundError: SKILL.md not found at the resolved path.
        FrontmatterError: Frontmatter missing or malformed.
    """
    p = Path(skill_path)
    if p.is_dir():
        p = p / "SKILL.md"
    if not p.is_file():
        raise FileNotFoundError(f"SKILL.md not found at {p}")

    text = p.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise FrontmatterError(f"No YAML frontmatter found in {p}")

    match = _FRONTMATTER_RE.match(text)
    if not match:
        raise FrontmatterError(f"Invalid frontmatter format in {p}")

    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        raise FrontmatterError(f"Invalid YAML in {p}: {exc}") from exc

    if not isinstance(data, dict):
        raise FrontmatterError(f"Frontmatter must be a mapping in {p}")
    if "name" not in data:
        raise FrontmatterError(f"Missing required 'name' in {p}")
    if "description" not in data:
        raise FrontmatterError(f"Missing required 'description' in {p}")

    return data


def list_skills_with_triggers(skills_dir: str | Path) -> list[dict]:
    """
    Scan a skills/ directory and return one dict per skill with discovery info.

    Each entry: {"name", "description", "triggers", "path"}.
    "triggers" is the list under frontmatter.triggers, or empty list if absent.

    Skills with malformed frontmatter are skipped silently (caller can re-scan
    with the validator skill if a hard check is required).
    """
    base = Path(skills_dir)
    out: list[dict] = []
    for skill_md in sorted(base.glob("*/SKILL.md")):
        try:
            fm = read_frontmatter(skill_md)
        except (FrontmatterError, FileNotFoundError):
            continue
        out.append({
            "name": fm.get("name", ""),
            "description": fm.get("description", ""),
            "triggers": fm.get("triggers", []) or [],
            "path": str(skill_md),
        })
    return out


def estimate_frontmatter_tokens(skill_path: str | Path) -> int:
    """Char-based token estimate for the frontmatter region of a SKILL.md."""
    p = Path(skill_path)
    if p.is_dir():
        p = p / "SKILL.md"
    text = p.read_text(encoding="utf-8")
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return 0
    return len(match.group(0)) // 4
