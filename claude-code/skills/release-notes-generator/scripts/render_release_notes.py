#!/usr/bin/env python3
"""
Release Notes Renderer — convert structured changelog JSON to markdown.

Takes the JSON output from `parse_git_log.py` and renders it as markdown
release notes following the canonical template (Highlights, Features, Fixes,
Performance, Security, Breaking Changes, Dependencies, Contributors).

Usage:
    render_release_notes.py --input STRUCTURED.json --version VERSION
                            --release-date YYYY-MM-DD [--output PATH]
                            [--issue-base-url URL]

Examples:
    render_release_notes.py --input structured.json --version 2.4.0
                             --release-date 2026-04-25
                             --issue-base-url https://github.com/example/repo

Exit codes:
    0  EXIT_SUCCESS
    2  EXIT_INVALID_INPUT
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SHARED_PY = SCRIPT_DIR.parent.parent / "_shared" / "python"
if SHARED_PY.exists():
    sys.path.insert(0, str(SHARED_PY))
    try:
        from layer0.exit_codes import EXIT_SUCCESS, EXIT_INVALID_INPUT  # type: ignore
    except ImportError:
        EXIT_SUCCESS = 0
        EXIT_INVALID_INPUT = 2
else:
    EXIT_SUCCESS = 0
    EXIT_INVALID_INPUT = 2


SECTION_ORDER = [
    ("feat", "🚀 Features"),
    ("fix", "🐛 Fixes"),
    ("perf", "⚡ Performance"),
    ("security", "🔒 Security"),
]


def format_issue_links(issue_refs: list[int], base_url: str | None) -> str:
    if not issue_refs:
        return ""
    if base_url:
        return " " + ", ".join(f"[#{n}]({base_url}/issues/{n})" for n in issue_refs)
    return " " + ", ".join(f"#{n}" for n in issue_refs)


def render_commit_line(commit: dict, base_url: str | None) -> str:
    scope = f"({commit['scope']})" if commit.get("scope") else ""
    issue_links = format_issue_links(commit.get("issue_refs", []), base_url)
    author = commit["author"]["name"]
    desc = commit["description"]
    line = f"- **{desc}**{issue_links} — by @{author}"
    if scope:
        line = f"- **{scope[1:-1]}: {desc}**{issue_links} — by @{author}"
    return line


def render(data: dict, version: str, release_date: str, base_url: str | None) -> str:
    lines = []
    lines.append(f"## [{version}] — {release_date}")
    lines.append("")

    # Highlights section (placeholder — humans curate)
    total_feat = len(data.get("categories", {}).get("feat", []))
    total_fix = len(data.get("categories", {}).get("fix", []))
    total_perf = len(data.get("categories", {}).get("perf", []))
    total_sec = len(data.get("categories", {}).get("security", []))
    breaking_count = data.get("breaking_changes_count", 0)
    summary_bits = []
    if total_feat:
        summary_bits.append(f"{total_feat} new feature{'s' if total_feat != 1 else ''}")
    if total_fix:
        summary_bits.append(f"{total_fix} bug fix{'es' if total_fix != 1 else ''}")
    if total_perf:
        summary_bits.append(f"{total_perf} performance improvement{'s' if total_perf != 1 else ''}")
    if total_sec:
        summary_bits.append(f"{total_sec} security fix{'es' if total_sec != 1 else ''}")
    if breaking_count:
        summary_bits.append(f"**{breaking_count} BREAKING CHANGE{'S' if breaking_count != 1 else ''}**")

    summary = ", ".join(summary_bits) if summary_bits else "Internal improvements only."
    lines.append(f"> **Highlights**: {summary}. _A human reviewer should rewrite this paragraph "
                 f"to highlight the 3–5 most user-impactful changes._")
    lines.append("")

    # Standard sections
    categories = data.get("categories", {})
    for cat_key, cat_title in SECTION_ORDER:
        items = categories.get(cat_key, [])
        # Skip breaking changes from per-category sections (they go in their own section)
        non_breaking = [c for c in items if not c.get("breaking")]
        if not non_breaking:
            continue
        lines.append(f"### {cat_title}")
        lines.append("")
        for c in non_breaking:
            lines.append(render_commit_line(c, base_url))
        lines.append("")

    # Breaking changes
    breaking = data.get("breaking_changes", [])
    if breaking:
        lines.append("### ⚠️ Breaking Changes")
        lines.append("")
        lines.append("> Read this section before upgrading.")
        lines.append("")
        for c in breaking:
            scope = f"({c['scope']}) " if c.get("scope") else ""
            lines.append(f"#### {scope}{c['description']}")
            lines.append("")
            if c.get("breaking_change_text"):
                lines.append(f"**What changed**: {c['breaking_change_text']}")
            lines.append("")
            lines.append(f"_Reviewer: add **Why**, **Migration**, **Affected users** sections per the template._")
            lines.append("")
            issue_links = format_issue_links(c.get("issue_refs", []), base_url)
            lines.append(f"References: {issue_links.lstrip(' ')} — by @{c['author']['name']}")
            lines.append("")

    # Dependencies (placeholder — humans add)
    lines.append("### 📦 Dependencies")
    lines.append("")
    lines.append("_Reviewer: list significant dependency bumps (CVE patches, major version changes). "
                 "Use `git diff <from>..<to> -- package*.json requirements*.txt` to identify._")
    lines.append("")

    # Contributors
    contribs = data.get("contributors", [])
    if contribs:
        lines.append("### 👥 Contributors")
        lines.append("")
        names = [f"@{c['name']}" for c in contribs]
        lines.append(f"Thanks to everyone who contributed to this release: {', '.join(names)}.")
        lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Render release notes from structured changelog JSON.")
    p.add_argument("--input", required=True, help="Path to structured.json from parse_git_log.py")
    p.add_argument("--version", required=True, help="Release version (e.g., 2.4.0)")
    p.add_argument("--release-date", required=True, help="Release date (YYYY-MM-DD)")
    p.add_argument("--issue-base-url", help="Base URL for issue/PR links (e.g., https://github.com/org/repo)")
    p.add_argument("--output", help="Path to write markdown (default: stdout)")
    args = p.parse_args(argv)

    try:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Failed to read input: {exc}", file=sys.stderr)
        return EXIT_INVALID_INPUT

    md = render(data, args.version, args.release_date, args.issue_base_url)

    if args.output:
        Path(args.output).write_text(md, encoding="utf-8")
        print(f"Wrote release notes to {args.output}")
    else:
        sys.stdout.write(md)

    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
