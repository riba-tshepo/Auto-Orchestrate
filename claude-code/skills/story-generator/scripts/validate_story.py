#!/usr/bin/env python3
"""
Story Validator — INVEST compliance checker for user stories.

Parses a markdown stories document and verifies each story passes INVEST:
Independent, Negotiable, Valuable, Estimable, Small, Testable.

Usage:
    validate_story.py --input PATH [-o json|human]
    validate_story.py --story-text "..." [-o json|human]

Exit codes:
    0  EXIT_SUCCESS       — all stories pass INVEST
    2  EXIT_INVALID_INPUT — file unreadable or no stories found
    40 EXIT_INVEST_FAIL   — at least one story fails INVEST
"""
from __future__ import annotations

import argparse
import json
import re
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

EXIT_INVEST_FAIL = 40

FIBONACCI = {1, 2, 3, 5, 8, 13, 21}
MAX_SPRINT_POINTS = 8

STORY_HEADER_RE = re.compile(r"^###\s+Story\s+([A-Z]{2,4}-\d+)\s*:\s*(.+?)\s*$", re.MULTILINE)
AS_A_RE = re.compile(r"\*\*As a\*\*\s+(.+)")
I_WANT_RE = re.compile(r"\*\*I want\*\*\s+(.+)")
SO_THAT_RE = re.compile(r"\*\*so that\*\*\s+(.+)", re.IGNORECASE)
ESTIMATE_RE = re.compile(r"\*\*Estimate\*\*:\s*(\d+)")
ASSIGNEE_RE = re.compile(r"\*\*Assignee\*\*:\s*(\S+)")
GWT_RE = re.compile(r"^\d+\.\s*Given\s+.+?,?\s*When\s+.+?,?\s*Then\s+", re.IGNORECASE | re.MULTILINE)


def parse_stories(text: str) -> list[dict]:
    stories = []
    matches = list(STORY_HEADER_RE.finditer(text))
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end]
        story_id, title = match.group(1), match.group(2)

        as_a = AS_A_RE.search(body)
        i_want = I_WANT_RE.search(body)
        so_that = SO_THAT_RE.search(body)
        estimate_m = ESTIMATE_RE.search(body)
        assignee_m = ASSIGNEE_RE.search(body)

        ac_lines = GWT_RE.findall(body)
        # Count AC by counting numbered list items in an "Acceptance Criteria" section
        ac_section_match = re.search(r"\*\*Acceptance Criteria\*\*:\s*\n((?:\d+\.\s*.*\n?)+)", body, re.IGNORECASE)
        ac_count = 0
        ac_gwt_count = 0
        if ac_section_match:
            ac_block = ac_section_match.group(1)
            ac_count = len(re.findall(r"^\d+\.\s+", ac_block, re.MULTILINE))
            ac_gwt_count = len(re.findall(r"\d+\.\s*Given\s+.+?When\s+.+?Then\s+", ac_block, re.IGNORECASE | re.DOTALL))

        stories.append({
            "id": story_id,
            "title": title,
            "as_a": as_a.group(1).strip() if as_a else None,
            "i_want": i_want.group(1).strip() if i_want else None,
            "so_that": so_that.group(1).strip() if so_that else None,
            "estimate": int(estimate_m.group(1)) if estimate_m else None,
            "assignee": assignee_m.group(1).strip() if assignee_m else None,
            "ac_count": ac_count,
            "ac_gwt_count": ac_gwt_count,
            "raw_body": body,
        })
    return stories


def check_invest(story: dict) -> dict:
    failures = []
    notes = []

    # Independent — heuristic: no "depends on" or "blocked by" language in body
    if re.search(r"\b(depends on|blocked by)\b", story["raw_body"], re.IGNORECASE):
        if not re.search(r"already in done|completed", story["raw_body"], re.IGNORECASE):
            failures.append("I (Independent): story references unresolved dependency")

    # Negotiable — heuristic: no implementation-specific keywords in As a/I want/so that
    impl_kw = re.compile(
        r"\b(SendGrid|Stripe|Postgres|MySQL|Redis|Kafka|nginx|React|Vue|Django|Express)\b",
        re.IGNORECASE,
    )
    for field in ("as_a", "i_want", "so_that"):
        if story[field] and impl_kw.search(story[field]):
            failures.append(f"N (Negotiable): {field} contains implementation-specific tech name")

    # Valuable — so_that must be present and non-empty
    if not story["so_that"] or len(story["so_that"]) < 10:
        failures.append("V (Valuable): so_that clause missing or too short (<10 chars)")

    # Estimable — must have Fibonacci estimate
    if story["estimate"] is None:
        failures.append("E (Estimable): no Estimate field")
    elif story["estimate"] not in FIBONACCI:
        failures.append(f"E (Estimable): estimate {story['estimate']} not in Fibonacci sequence {sorted(FIBONACCI)}")

    # Small — ≤8 points
    if story["estimate"] is not None and story["estimate"] > MAX_SPRINT_POINTS:
        failures.append(f"S (Small): estimate {story['estimate']} exceeds sprint cap ({MAX_SPRINT_POINTS}) — split required")

    # Testable — ≥2 AC and at least one in G/W/T format
    if story["ac_count"] < 2:
        failures.append(f"T (Testable): only {story['ac_count']} acceptance criteria; need ≥2")
    if story["ac_gwt_count"] == 0:
        failures.append("T (Testable): no acceptance criteria in Given/When/Then format")

    # Required fields
    for field in ("as_a", "i_want"):
        if not story[field]:
            failures.append(f"required field missing: {field}")
    if not story["assignee"]:
        notes.append("Assignee field missing (recommended but not blocking)")

    return {
        "story_id": story["id"],
        "title": story["title"],
        "verdict": "PASS" if not failures else "FAIL",
        "failures": failures,
        "notes": notes,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Validate user stories against INVEST criteria.")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--input", help="Path to markdown stories document")
    g.add_argument("--story-text", help="Inline markdown for a single story")
    p.add_argument("-o", "--output", choices=("json", "human"), default="json")
    args = p.parse_args(argv)

    if args.input:
        try:
            text = Path(args.input).read_text(encoding="utf-8")
        except OSError as exc:
            print(json.dumps({"error": f"failed to read {args.input}: {exc}"}))
            return EXIT_INVALID_INPUT
    else:
        text = args.story_text

    stories = parse_stories(text)
    if not stories:
        print(json.dumps({"error": "no stories found (expected '### Story <ID>: ...' headers)"}))
        return EXIT_INVALID_INPUT

    results = [check_invest(s) for s in stories]
    fails = [r for r in results if r["verdict"] == "FAIL"]
    summary = {
        "total": len(results),
        "passed": len(results) - len(fails),
        "failed": len(fails),
        "stories": results,
    }

    if args.output == "json":
        json.dump(summary, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"INVEST validation: {summary['passed']}/{summary['total']} passed")
        for r in results:
            mark = "✓" if r["verdict"] == "PASS" else "✗"
            print(f"  {mark} {r['story_id']}: {r['title']}")
            for f in r["failures"]:
                print(f"      - {f}")

    return EXIT_SUCCESS if not fails else EXIT_INVEST_FAIL


if __name__ == "__main__":
    sys.exit(main())
