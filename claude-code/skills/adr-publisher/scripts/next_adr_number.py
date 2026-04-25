#!/usr/bin/env python3
"""
Next ADR Number — finds the next sequential ADR number for `docs/adr/`.

Scans the project's `docs/adr/` directory for existing files matching
`NNNN-*.md` and returns max+1, zero-padded to 4 digits.

Usage:
    next_adr_number.py [--adr-dir PATH] [-o json|human]

Examples:
    next_adr_number.py                    # default: ./docs/adr/
    next_adr_number.py --adr-dir docs/adrs/   # custom location
    next_adr_number.py -o human          # plain integer output

Exit codes:
    0  EXIT_SUCCESS       — number returned
    20 EXIT_NOT_FOUND     — adr directory does not exist (returns 1 as default)
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
        from layer0.exit_codes import EXIT_SUCCESS  # type: ignore
    except ImportError:
        EXIT_SUCCESS = 0
else:
    EXIT_SUCCESS = 0

EXIT_NOT_FOUND = 20

ADR_FILENAME_RE = re.compile(r"^(\d{4})-[a-z0-9-]+\.md$")


def find_next_number(adr_dir: Path) -> tuple[int, list[int]]:
    if not adr_dir.exists() or not adr_dir.is_dir():
        return 1, []
    existing = []
    for f in adr_dir.iterdir():
        if f.is_file():
            m = ADR_FILENAME_RE.match(f.name)
            if m:
                existing.append(int(m.group(1)))
    if not existing:
        return 1, existing
    return max(existing) + 1, sorted(existing)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Find next ADR number for docs/adr/")
    p.add_argument("--adr-dir", default="docs/adr", help="ADR directory (default: docs/adr)")
    p.add_argument("-o", "--output", choices=("json", "human"), default="json")
    args = p.parse_args(argv)

    adr_dir = Path(args.adr_dir)
    next_n, existing = find_next_number(adr_dir)
    next_padded = f"{next_n:04d}"

    result = {
        "next_number": next_n,
        "next_padded": next_padded,
        "existing_count": len(existing),
        "highest_existing": max(existing) if existing else None,
        "adr_dir": str(adr_dir),
        "adr_dir_exists": adr_dir.exists(),
    }

    if args.output == "json":
        json.dump(result, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print(next_padded)

    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
