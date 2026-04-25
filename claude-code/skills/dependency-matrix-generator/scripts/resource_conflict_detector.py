#!/usr/bin/env python3
"""
Resource Conflict Detector — find shared-resource conflicts in dependency register.

Identifies pairs of activities that compete for the same shared resource within
overlapping time windows.

Usage:
    resource_conflict_detector.py --input INPUT.json [--output OUTPUT.json] [-o json|human]

Input format (JSON) — activities with optional shared_resources + time windows:
    [
      {
        "id": "act-001",
        "shared_resources": ["ci-large-runner-pool"],
        "demand_window_start": "2026-05-01",
        "demand_window_end": "2026-05-15"
      },
      {"id": "act-002", "shared_resources": ["ci-large-runner-pool"], ...}
    ]

Exit codes:
    0  EXIT_SUCCESS — no conflicts (or conflicts found and reported)
    2  EXIT_INVALID_INPUT
    51 EXIT_CONFLICTS_FOUND — at least one conflict detected (use to gate)
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import date, datetime
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

EXIT_CONFLICTS_FOUND = 51


def parse_date(s: str) -> date | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s).date()
    except (ValueError, TypeError):
        return None


def windows_overlap(start_a: date, end_a: date, start_b: date, end_b: date) -> tuple[date, date] | None:
    """Return (overlap_start, overlap_end) if windows overlap, else None."""
    overlap_start = max(start_a, start_b)
    overlap_end = min(end_a, end_b)
    if overlap_start <= overlap_end:
        return overlap_start, overlap_end
    return None


def detect_conflicts(activities: list[dict]) -> list[dict]:
    by_resource = defaultdict(list)
    for a in activities:
        for res in a.get("shared_resources", []) or []:
            by_resource[res].append(a)

    conflicts = []
    for resource, items in by_resource.items():
        if len(items) < 2:
            continue
        # Pairwise check
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                a, b = items[i], items[j]
                a_start = parse_date(a.get("demand_window_start"))
                a_end = parse_date(a.get("demand_window_end"))
                b_start = parse_date(b.get("demand_window_start"))
                b_end = parse_date(b.get("demand_window_end"))
                if not (a_start and a_end and b_start and b_end):
                    # Missing windows — flag as potential
                    conflicts.append({
                        "resource": resource,
                        "activities": [a["id"], b["id"]],
                        "severity": "MEDIUM",
                        "reason": "missing demand windows; cannot verify conflict",
                        "overlap_start": None,
                        "overlap_end": None,
                        "overlap_days": None,
                    })
                    continue
                overlap = windows_overlap(a_start, a_end, b_start, b_end)
                if overlap:
                    o_start, o_end = overlap
                    overlap_days = (o_end - o_start).days + 1
                    severity = "HIGH" if overlap_days >= 7 else "MEDIUM" if overlap_days >= 3 else "LOW"
                    conflicts.append({
                        "resource": resource,
                        "activities": [a["id"], b["id"]],
                        "severity": severity,
                        "reason": f"both activities demand {resource} during the same window",
                        "overlap_start": o_start.isoformat(),
                        "overlap_end": o_end.isoformat(),
                        "overlap_days": overlap_days,
                    })
    return conflicts


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Detect shared-resource conflicts in dependency register.")
    p.add_argument("--input", required=True, help="Path to activities JSON")
    p.add_argument("--output", help="Path to write conflicts JSON")
    p.add_argument("-o", "--output-format", choices=("json", "human"), default="json")
    args = p.parse_args(argv)

    try:
        activities = json.loads(Path(args.input).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(json.dumps({"error": f"failed to read input: {exc}"}))
        return EXIT_INVALID_INPUT

    if not isinstance(activities, list):
        print(json.dumps({"error": "input must be a JSON list of activities"}))
        return EXIT_INVALID_INPUT

    conflicts = detect_conflicts(activities)

    result = {
        "activity_count": len(activities),
        "conflict_count": len(conflicts),
        "conflicts": conflicts,
    }

    out = json.dumps(result, indent=2)
    if args.output:
        Path(args.output).write_text(out + "\n", encoding="utf-8")
        if args.output_format == "human":
            print(f"Conflicts: {len(conflicts)} detected across {len(activities)} activities")
            for c in conflicts:
                print(f"  [{c['severity']}] {c['resource']}: {c['activities'][0]} vs {c['activities'][1]} "
                      f"({c.get('overlap_days', '?')} days overlap)")
    else:
        if args.output_format == "json":
            print(out)
        else:
            print(f"Conflicts: {len(conflicts)}")

    return EXIT_CONFLICTS_FOUND if conflicts else EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
