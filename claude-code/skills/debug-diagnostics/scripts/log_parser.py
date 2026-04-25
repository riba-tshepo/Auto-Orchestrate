#!/usr/bin/env python3
"""Parse log files into structured JSON entries, filtering by severity level.

Usage:
    python3 log_parser.py --file /var/log/app.log
    python3 log_parser.py --file /var/log/app.log --level ERROR,CRITICAL
    docker compose logs 2>&1 | python3 log_parser.py
    python3 log_parser.py --help

Output: JSON array of structured log entries.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "_shared" / "python"))
from layer0 import EXIT_SUCCESS, EXIT_ERROR, EXIT_INVALID_ARGS, EXIT_VALIDATION_ERROR
from layer1 import emit_error, emit_warning, emit_info


# Common log level patterns
LEVELS = {"DEBUG", "INFO", "NOTICE", "WARNING", "WARN", "ERROR", "ERR", "CRITICAL", "FATAL", "PANIC", "ALERT", "EMERGENCY", "EMERG"}
LEVEL_ALIASES = {"WARN": "WARNING", "ERR": "ERROR", "EMERG": "EMERGENCY"}
SEVERITY_ORDER = ["DEBUG", "INFO", "NOTICE", "WARNING", "ERROR", "CRITICAL", "FATAL", "PANIC", "ALERT", "EMERGENCY"]

# Log format patterns
PATTERNS = [
    # JSON logs: {"level": "error", "msg": "...", "time": "..."}
    ("json", re.compile(r"^\s*\{.*\}\s*$")),

    # Syslog: Mar 24 10:30:45 hostname service[pid]: message
    ("syslog", re.compile(
        r"^(?P<timestamp>\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+"
        r"(?P<source>\S+)\s+(?P<service>\S+?)(?:\[(?P<pid>\d+)\])?:\s+"
        r"(?P<message>.+)$"
    )),

    # ISO timestamp with level: 2026-03-24T10:30:45 ERROR message
    ("iso_level", re.compile(
        r"^(?P<timestamp>\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)\s+"
        r"(?P<level>" + "|".join(LEVELS) + r")\s+"
        r"(?P<message>.+)$",
        re.IGNORECASE,
    )),

    # Python logging: level:name:message or WARNING:django.request:message
    ("python", re.compile(
        r"^(?P<level>" + "|".join(LEVELS) + r"):(?P<source>[^:]+):(?P<message>.+)$",
        re.IGNORECASE,
    )),

    # Docker compose logs: service_1 | message
    ("docker_compose", re.compile(
        r"^(?P<source>[\w_-]+(?:\s*\|\s*|\s+\| ))\s*(?P<message>.+)$"
    )),

    # Bracketed level: [ERROR] message or [2026-03-24 10:30:45] [ERROR] message
    ("bracketed", re.compile(
        r"^(?:\[(?P<timestamp>[^\]]+)\]\s*)?"
        r"\[(?P<level>" + "|".join(LEVELS) + r")\]\s+"
        r"(?P<message>.+)$",
        re.IGNORECASE,
    )),

    # Level prefix: ERROR: message or Error: message
    ("prefix", re.compile(
        r"^(?P<level>" + "|".join(LEVELS) + r"):\s+(?P<message>.+)$",
        re.IGNORECASE,
    )),
]


def normalize_level(level: Optional[str]) -> Optional[str]:
    """Normalize log level to standard form."""
    if not level:
        return None
    upper = level.upper()
    return LEVEL_ALIASES.get(upper, upper)


def infer_level(message: str) -> Optional[str]:
    """Infer log level from message content when not explicitly present."""
    lower = message.lower()
    if any(w in lower for w in ("error", "exception", "traceback", "failed", "failure")):
        return "ERROR"
    if any(w in lower for w in ("warning", "warn", "deprecated")):
        return "WARNING"
    if any(w in lower for w in ("critical", "fatal", "panic")):
        return "CRITICAL"
    return None


def parse_json_log(line: str) -> Optional[dict]:
    """Parse a JSON-formatted log line."""
    try:
        data = json.loads(line)
    except json.JSONDecodeError:
        return None

    level = None
    for key in ("level", "severity", "lvl", "loglevel"):
        if key in data:
            level = normalize_level(str(data[key]))
            break

    message = data.get("msg") or data.get("message") or data.get("text") or str(data)
    timestamp = data.get("time") or data.get("timestamp") or data.get("ts") or data.get("@timestamp")
    source = data.get("logger") or data.get("name") or data.get("source") or data.get("service")

    return {
        "timestamp": str(timestamp) if timestamp else None,
        "level": level or infer_level(str(message)),
        "message": str(message),
        "source": str(source) if source else None,
    }


def parse_line(line: str) -> Optional[dict]:
    """Parse a single log line into a structured entry."""
    line = line.rstrip()
    if not line:
        return None

    for fmt, pattern in PATTERNS:
        if fmt == "json":
            if pattern.match(line):
                return parse_json_log(line)
            continue

        m = pattern.match(line)
        if not m:
            continue

        groups = m.groupdict()
        level = normalize_level(groups.get("level"))
        message = groups.get("message", line)

        # For docker compose logs, try to extract level from message
        if fmt == "docker_compose" and not level:
            level = infer_level(message)

        return {
            "timestamp": groups.get("timestamp"),
            "level": level or infer_level(message),
            "message": message,
            "source": (groups.get("source", "") or "").strip(" |"),
        }

    # Fallback: unstructured line
    level = infer_level(line)
    if level:
        return {
            "timestamp": None,
            "level": level,
            "message": line,
            "source": None,
        }

    return None


def meets_level_filter(entry_level: Optional[str], min_levels: set[str]) -> bool:
    """Check if entry level meets the filter criteria."""
    if not min_levels:
        return True
    if not entry_level:
        return False
    return entry_level in min_levels


def main():
    parser = argparse.ArgumentParser(description="Parse log files into structured JSON")
    parser.add_argument("--file", "-f", help="Log file path (reads stdin if omitted)")
    parser.add_argument(
        "--level", "-l",
        default="ERROR,WARN,WARNING,CRITICAL,FATAL,PANIC,EMERGENCY",
        help="Comma-separated levels to include (default: ERROR,WARN,WARNING,CRITICAL,FATAL,PANIC,EMERGENCY)",
    )
    parser.add_argument("--all", "-a", action="store_true", help="Include all levels")
    parser.add_argument("--limit", "-n", type=int, default=100, help="Max entries to return (default: 100)")
    args = parser.parse_args()

    if args.all:
        level_filter = set()
    else:
        level_filter = {normalize_level(l.strip()) for l in args.level.split(",")}

    if args.file:
        with open(args.file) as f:
            lines = f.readlines()
    else:
        lines = sys.stdin.readlines()

    entries = []
    for line in lines:
        entry = parse_line(line)
        if entry and meets_level_filter(entry.get("level"), level_filter):
            entries.append(entry)
            if len(entries) >= args.limit:
                break

    print(json.dumps(entries, indent=2))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(EXIT_ERROR)
    except Exception as exc:
        emit_error(f"Unhandled exception: {exc}")
        sys.exit(EXIT_ERROR)
