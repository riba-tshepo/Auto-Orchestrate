#!/usr/bin/env python3
"""
Git Log Parser — extract structured changelog data from git log.

Reads `git log <from>..<to>` and categorizes commits via conventional-commits
prefixes (feat, fix, perf, security, etc.). Detects breaking changes, extracts
issue/PR references, and aggregates contributors.

Usage:
    parse_git_log.py --from-ref REF --to-ref REF [--output PATH] [-o json|human]

Examples:
    parse_git_log.py --from-ref v2.3.0 --to-ref HEAD
    parse_git_log.py --from-ref v2.3.0 --to-ref HEAD --output changelog.json

Exit codes:
    0  EXIT_SUCCESS       — parsed successfully
    2  EXIT_INVALID_INPUT — invalid args
    20 EXIT_NOT_FOUND     — refs don't exist or git command failed
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
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

EXIT_NOT_FOUND = 20

# Conventional commits regex
CC_RE = re.compile(
    r"^(?P<type>feat|fix|perf|security|docs|chore|refactor|test|style|ci|build)"
    r"(?:\((?P<scope>[a-z0-9_-]+)\))?"
    r"(?P<bang>!)?"
    r":\s*(?P<desc>.+)$"
)
ISSUE_RE = re.compile(r"#(\d+)")
COAUTHOR_RE = re.compile(r"^Co-authored-by:\s*(.+?)\s*<(.+?)>", re.MULTILINE)
BREAKING_RE = re.compile(r"^BREAKING CHANGE:\s*(.+)", re.MULTILINE)

# Default included types
DEFAULT_INCLUDE = {"feat", "fix", "perf", "security"}


def run_git_log(from_ref: str, to_ref: str) -> list[dict]:
    """Run git log and return list of commit dicts."""
    fmt = "%H%x1f%an%x1f%ae%x1f%aI%x1f%s%x1f%b%x1e"
    cmd = ["git", "log", f"{from_ref}..{to_ref}", "--no-merges", f"--pretty=format:{fmt}"]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"git log failed: {exc.stderr.strip()}") from exc
    except FileNotFoundError as exc:
        raise RuntimeError(f"git not found: {exc}") from exc

    commits = []
    for chunk in out.stdout.split("\x1e"):
        chunk = chunk.strip()
        if not chunk:
            continue
        parts = chunk.split("\x1f")
        if len(parts) < 6:
            continue
        sha, author_name, author_email, date, subject, body = parts[:6]
        commits.append({
            "sha": sha,
            "author_name": author_name,
            "author_email": author_email,
            "date": date,
            "subject": subject,
            "body": body,
        })
    return commits


def parse_commit(commit: dict) -> dict:
    """Parse a single commit dict into structured form."""
    m = CC_RE.match(commit["subject"])
    if m:
        commit_type = m.group("type")
        scope = m.group("scope")
        breaking = bool(m.group("bang"))
        desc = m.group("desc")
    else:
        commit_type = "unknown"
        scope = None
        breaking = False
        desc = commit["subject"]

    # Detect BREAKING CHANGE in body
    breaking_change_text = None
    bc_match = BREAKING_RE.search(commit["body"])
    if bc_match:
        breaking = True
        breaking_change_text = bc_match.group(1).strip()

    # Extract issue refs from subject + body
    issue_refs = sorted(set(int(x) for x in ISSUE_RE.findall(commit["subject"] + "\n" + commit["body"])))

    # Co-authors
    coauthors = [(name, email) for name, email in COAUTHOR_RE.findall(commit["body"])]

    return {
        "sha": commit["sha"][:8],
        "type": commit_type,
        "scope": scope,
        "breaking": breaking,
        "description": desc,
        "breaking_change_text": breaking_change_text,
        "issue_refs": issue_refs,
        "author": {"name": commit["author_name"], "email": commit["author_email"]},
        "coauthors": [{"name": n, "email": e} for n, e in coauthors],
        "date": commit["date"],
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Parse git log into structured changelog data.")
    p.add_argument("--from-ref", required=True, help="Starting ref (e.g., v2.3.0)")
    p.add_argument("--to-ref", default="HEAD", help="Ending ref (default: HEAD)")
    p.add_argument("--include-types", nargs="*", default=None,
                   help=f"Commit types to include (default: {sorted(DEFAULT_INCLUDE)})")
    p.add_argument("--output", help="Path to write JSON output (default: stdout)")
    p.add_argument("-o", "--output-format", choices=("json", "human"), default="json")
    args = p.parse_args(argv)

    include = set(args.include_types) if args.include_types else DEFAULT_INCLUDE

    try:
        commits = run_git_log(args.from_ref, args.to_ref)
    except RuntimeError as exc:
        print(json.dumps({"error": str(exc)}))
        return EXIT_NOT_FOUND

    parsed = [parse_commit(c) for c in commits]

    # Categorize
    categories = defaultdict(list)
    breaking_changes = []
    contributors = set()

    for p_commit in parsed:
        contributors.add((p_commit["author"]["name"], p_commit["author"]["email"]))
        for ca in p_commit["coauthors"]:
            contributors.add((ca["name"], ca["email"]))

        if p_commit["breaking"]:
            breaking_changes.append(p_commit)

        if p_commit["type"] in include or p_commit["breaking"]:
            categories[p_commit["type"]].append(p_commit)

    structured = {
        "from_ref": args.from_ref,
        "to_ref": args.to_ref,
        "total_commits": len(parsed),
        "categorized_count": sum(len(v) for v in categories.values()),
        "breaking_changes_count": len(breaking_changes),
        "categories": dict(categories),
        "breaking_changes": breaking_changes,
        "contributors": sorted([{"name": n, "email": e} for n, e in contributors],
                              key=lambda x: x["name"].lower()),
        "contributor_count": len(contributors),
    }

    out_text = json.dumps(structured, indent=2, default=str)
    if args.output:
        Path(args.output).write_text(out_text + "\n", encoding="utf-8")
        if args.output_format == "human":
            print(f"Wrote {len(parsed)} commits ({structured['categorized_count']} categorized) "
                  f"to {args.output}")
    else:
        if args.output_format == "json":
            print(out_text)
        else:
            print(f"Total commits: {len(parsed)}")
            for cat, items in categories.items():
                print(f"  {cat}: {len(items)}")
            print(f"Breaking changes: {len(breaking_changes)}")
            print(f"Contributors: {len(contributors)}")

    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
