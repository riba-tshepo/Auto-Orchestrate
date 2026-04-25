#!/usr/bin/env python3
"""
RAID Log Appender — atomic append-only writer for the per-session RAID log.

Implements P-010 (Assumptions and Risks Registration), P-074 (RAID Log
Maintenance), P-075 (Risk Register at Scope Lock). Enforces the RAID-001
constraint: append-only, no overwrites, schema-validated, dedup-checked.

Usage:
    append_raid.py --session SESSION_ID --entry-json JSON_STRING
    append_raid.py --session SESSION_ID --entry-file PATH
    append_raid.py --session SESSION_ID --list-current
    append_raid.py --session SESSION_ID --validate

Examples:
    append_raid.py --session auto-orc-20260425-myapp \\
        --entry-json '{"id":"raid-001","type":"Risk","description":"...",...}'
    append_raid.py --session auto-orc-20260425-myapp --list-current

Exit codes:
    0  EXIT_SUCCESS       — entry appended successfully
    2  EXIT_INVALID_INPUT — schema violation; entry rejected
    10 EXIT_DUPLICATE     — id already exists (and not an update_of)
    20 EXIT_NOT_FOUND     — session directory or referenced entry missing
    30 EXIT_IO_ERROR      — file lock / write failure
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# --- Use _shared/python/layer0 for exit codes ---
SCRIPT_DIR = Path(__file__).parent
SHARED_PY = SCRIPT_DIR.parent.parent / "_shared" / "python"
if SHARED_PY.exists():
    sys.path.insert(0, str(SHARED_PY))
    try:
        from layer0.exit_codes import (  # type: ignore
            EXIT_SUCCESS,
            EXIT_INVALID_INPUT,
        )
    except ImportError:
        EXIT_SUCCESS = 0
        EXIT_INVALID_INPUT = 2
else:
    EXIT_SUCCESS = 0
    EXIT_INVALID_INPUT = 2

EXIT_DUPLICATE = 10
EXIT_NOT_FOUND = 20
EXIT_IO_ERROR = 30

VALID_TYPES = {"Risk", "Assumption", "Issue", "Dependency"}
VALID_SEVERITIES = {"CRITICAL", "HIGH", "MEDIUM", "LOW", None}
VALID_STATUSES = {"open", "mitigating", "resolved", "accepted", "escalated"}
PROCESS_ID_PATTERN = re.compile(r"^P-\d{3}$")


def session_root(session_id: str) -> Path:
    return Path.cwd() / ".orchestrate" / session_id


def raid_log_path(session_id: str) -> Path:
    return session_root(session_id) / "raid-log.json"


def validate_entry(entry: dict, existing_ids: set[str]) -> tuple[bool, str | None]:
    required = {"id", "type", "description", "owner", "status", "source_process", "timestamp"}
    missing = required - entry.keys()
    if missing:
        return False, f"missing required fields: {sorted(missing)}"

    if entry["type"] not in VALID_TYPES:
        return False, f"type must be one of {sorted(VALID_TYPES)}; got {entry['type']!r}"

    sev = entry.get("severity")
    if sev not in VALID_SEVERITIES:
        return False, f"severity must be one of CRITICAL/HIGH/MEDIUM/LOW or null; got {sev!r}"

    if entry["type"] in {"Risk", "Issue"} and sev is None:
        return False, f"{entry['type']} entries require non-null severity"

    if entry["status"] not in VALID_STATUSES:
        return False, f"status must be one of {sorted(VALID_STATUSES)}; got {entry['status']!r}"

    desc = entry["description"]
    if not isinstance(desc, str) or not (10 <= len(desc) <= 500):
        return False, "description must be a string between 10 and 500 chars"

    if not PROCESS_ID_PATTERN.match(entry["source_process"]):
        return False, f"source_process must match P-NNN; got {entry['source_process']!r}"

    try:
        datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return False, f"timestamp must be ISO-8601; got {entry['timestamp']!r}"

    if sev in {"CRITICAL", "HIGH"} and not entry.get("mitigation"):
        return False, f"{sev} severity requires a mitigation field"

    update_of = entry.get("update_of")
    if update_of and update_of not in existing_ids:
        return False, f"update_of references non-existent id {update_of!r}"

    if entry["id"] in existing_ids and not update_of:
        return False, f"id {entry['id']!r} already exists; set update_of to add a status update"

    return True, None


def load_existing_ids(log_path: Path) -> set[str]:
    if not log_path.exists():
        return set()
    ids = set()
    with log_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    ids.add(json.loads(line)["id"])
                except (json.JSONDecodeError, KeyError):
                    pass
    return ids


def append_entry(log_path: Path, entry: dict) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(entry, ensure_ascii=False) + "\n"
    fd = os.open(str(log_path), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    try:
        os.write(fd, line.encode("utf-8"))
        os.fsync(fd)
    finally:
        os.close(fd)


def list_current(log_path: Path) -> list[dict]:
    if not log_path.exists():
        return []
    by_root: dict[str, dict] = {}
    with log_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            root_id = e.get("update_of") or e["id"]
            while root_id in by_root and by_root[root_id].get("update_of"):
                root_id = by_root[root_id]["update_of"]
            by_root[root_id] = e
    return list(by_root.values())


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="RAID log appender (atomic, append-only).")
    p.add_argument("--session", required=True, help="Session ID (auto-orc-YYYYMMDD-slug)")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--entry-json", help="JSON-encoded entry to append")
    g.add_argument("--entry-file", help="Path to JSON file with entry to append")
    g.add_argument("--list-current", action="store_true", help="List collapsed current entries")
    g.add_argument("--validate", action="store_true", help="Validate entire log without writing")
    p.add_argument("-o", "--output", choices=("json", "human"), default="json")

    args = p.parse_args(argv)
    log_path = raid_log_path(args.session)

    if args.list_current:
        entries = list_current(log_path)
        if args.output == "json":
            json.dump({"count": len(entries), "entries": entries}, sys.stdout, indent=2)
            sys.stdout.write("\n")
        else:
            print(f"{len(entries)} current entries:")
            for e in entries:
                print(f"  [{e['type']}/{e.get('severity', '-')}] {e['id']} ({e['status']}) — {e['description'][:80]}")
        return EXIT_SUCCESS

    if args.validate:
        if not log_path.exists():
            print(json.dumps({"valid": True, "entries": 0}))
            return EXIT_SUCCESS
        with log_path.open("r", encoding="utf-8") as f:
            for ln, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    e = json.loads(line)
                except json.JSONDecodeError as exc:
                    print(json.dumps({"valid": False, "line": ln, "error": str(exc)}))
                    return EXIT_INVALID_INPUT
                ok, err = validate_entry(e, load_existing_ids(log_path) - {e["id"]})
                if not ok:
                    print(json.dumps({"valid": False, "line": ln, "error": err}))
                    return EXIT_INVALID_INPUT
        print(json.dumps({"valid": True}))
        return EXIT_SUCCESS

    if args.entry_json:
        try:
            entry = json.loads(args.entry_json)
        except json.JSONDecodeError as exc:
            print(json.dumps({"error": f"invalid JSON: {exc}"}))
            return EXIT_INVALID_INPUT
    else:
        try:
            entry = json.loads(Path(args.entry_file).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError) as exc:
            print(json.dumps({"error": f"failed to read entry file: {exc}"}))
            return EXIT_INVALID_INPUT

    existing = load_existing_ids(log_path)
    ok, err = validate_entry(entry, existing)
    if not ok:
        print(json.dumps({"error": err}))
        return EXIT_INVALID_INPUT if "already exists" not in err else EXIT_DUPLICATE

    try:
        append_entry(log_path, entry)
    except OSError as exc:
        print(json.dumps({"error": f"write failed: {exc}"}))
        return EXIT_IO_ERROR

    result = {
        "appended": True,
        "id": entry["id"],
        "appended_at": datetime.now(timezone.utc).isoformat(),
        "total_entries": len(existing) + 1,
        "log_path": str(log_path),
    }
    print(json.dumps(result, indent=2))
    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
