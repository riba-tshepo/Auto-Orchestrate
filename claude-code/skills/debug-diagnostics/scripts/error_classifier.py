#!/usr/bin/env python3
"""Classify error messages into categories using regex pattern matching.

Usage:
    echo "ConnectionRefusedError: [Errno 111]" | python3 error_classifier.py
    python3 error_classifier.py --file /path/to/error.log
    python3 error_classifier.py --help

Output: JSON object with category, error_type, message, file, line, confidence.
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


PATTERNS = {
    "syntax": [
        (r"SyntaxError", "SyntaxError", 0.95),
        (r"IndentationError", "IndentationError", 0.95),
        (r"TabError", "TabError", 0.95),
        (r"unexpected token", "UnexpectedToken", 0.90),
        (r"Unexpected identifier", "UnexpectedIdentifier", 0.90),
        (r"invalid syntax", "InvalidSyntax", 0.90),
        (r"unexpected EOF", "UnexpectedEOF", 0.90),
        (r"Cannot use import", "ImportSyntax", 0.85),
    ],
    "dependency": [
        (r"ModuleNotFoundError", "ModuleNotFoundError", 0.95),
        (r"ImportError", "ImportError", 0.90),
        (r"Cannot find module", "ModuleNotFound", 0.90),
        (r"MODULE_NOT_FOUND", "ModuleNotFound", 0.90),
        (r"ERR_MODULE_NOT_FOUND", "ModuleNotFound", 0.90),
        (r"ERESOLVE", "DependencyResolve", 0.90),
        (r"npm ERR!", "NpmError", 0.80),
        (r"missing go\.sum entry", "GoSumMissing", 0.90),
        (r"command not found", "CommandNotFound", 0.75),
        (r"pkg_resources\.DistributionNotFound", "DistributionNotFound", 0.90),
    ],
    "docker": [
        (r"failed to build", "DockerBuildFailed", 0.90),
        (r"COPY failed", "DockerCopyFailed", 0.95),
        (r"Exited \(\d+\)", "ContainerExited", 0.90),
        (r"OOMKilled", "OOMKilled", 0.95),
        (r"container died", "ContainerDied", 0.90),
        (r"port is already allocated", "PortConflict", 0.95),
        (r"healthcheck.*unhealthy", "HealthcheckFailed", 0.90),
        (r"health_check failed", "HealthcheckFailed", 0.90),
        (r"Couldn't connect to Docker daemon", "DaemonNotRunning", 0.95),
        (r"image not found", "ImageNotFound", 0.90),
        (r"manifest unknown", "ManifestUnknown", 0.90),
        (r"pull access denied", "PullAccessDenied", 0.90),
        (r"no space left on device", "DiskFull", 0.85),
    ],
    "permission": [
        (r"PermissionError", "PermissionError", 0.95),
        (r"EACCES", "EACCES", 0.95),
        (r"EPERM", "EPERM", 0.90),
        (r"Permission denied", "PermissionDenied", 0.90),
        (r"Operation not permitted", "OperationNotPermitted", 0.90),
        (r"403 Forbidden", "Forbidden", 0.85),
        (r"Read-only file system", "ReadOnlyFS", 0.90),
    ],
    "database": [
        (r"psycopg2\.OperationalError", "PostgresOperational", 0.95),
        (r"sqlalchemy\.exc\.", "SQLAlchemyError", 0.90),
        (r"django\.db\.utils\.", "DjangoDBError", 0.90),
        (r"SequelizeConnectionError", "SequelizeConnection", 0.90),
        (r"PrismaClient", "PrismaError", 0.90),
        (r"MongoServerError", "MongoError", 0.90),
        (r"pymongo\.errors\.", "PyMongoError", 0.90),
        (r"redis\.exceptions\.", "RedisError", 0.90),
        (r"PROTOCOL_CONNECTION_LOST", "DBConnectionLost", 0.90),
        (r"migration.*fail", "MigrationFailed", 0.85),
        (r"alembic", "AlembicError", 0.85),
        # ConnectionRefused on known DB ports
        (r"(?:Connection refused|ECONNREFUSED).*(?:5432|3306|27017|6379)", "DBConnectionRefused", 0.85),
        (r"pq:", "PostgresError", 0.85),
    ],
    "network": [
        (r"ConnectionRefusedError", "ConnectionRefused", 0.80),
        (r"ECONNREFUSED", "ConnectionRefused", 0.80),
        (r"ETIMEDOUT", "Timeout", 0.85),
        (r"TimeoutError", "Timeout", 0.80),
        (r"socket\.gaierror", "DNSFailure", 0.90),
        (r"ENOTFOUND", "DNSFailure", 0.90),
        (r"no such host", "DNSFailure", 0.90),
        (r"ECONNRESET", "ConnectionReset", 0.85),
        (r"ssl\.SSLError", "SSLError", 0.85),
        (r"TLS handshake", "TLSError", 0.85),
        (r"fetch failed", "FetchFailed", 0.75),
        (r"i/o timeout", "IOTimeout", 0.85),
        (r"dial tcp", "DialTCP", 0.80),
    ],
    "configuration": [
        (r"missing required", "MissingRequired", 0.80),
        (r"unbound variable", "UnboundVariable", 0.90),
        (r"configparser\.Error", "ConfigParseError", 0.90),
        (r"yaml\.YAMLError", "YAMLError", 0.90),
        (r"toml\.TomlDecodeError", "TOMLError", 0.90),
        (r"\.env.*not found", "EnvFileNotFound", 0.85),
        (r"flag provided but not defined", "FlagUndefined", 0.90),
    ],
    "runtime": [
        (r"TypeError", "TypeError", 0.85),
        (r"ValueError", "ValueError", 0.85),
        (r"AttributeError", "AttributeError", 0.85),
        (r"KeyError", "KeyError", 0.75),
        (r"IndexError", "IndexError", 0.85),
        (r"RuntimeError", "RuntimeError", 0.80),
        (r"ReferenceError", "ReferenceError", 0.85),
        (r"RangeError", "RangeError", 0.85),
        (r"ZeroDivisionError", "ZeroDivisionError", 0.90),
        (r"RecursionError", "RecursionError", 0.90),
        (r"MemoryError", "MemoryError", 0.90),
        (r"panic:", "GoPanic", 0.90),
        (r"segmentation fault", "SegFault", 0.90),
        (r"signal SIGSEGV", "SegFault", 0.90),
        (r"UnhandledPromiseRejection", "UnhandledPromise", 0.85),
        (r"fatal error:", "FatalError", 0.80),
    ],
}

# Category priority for disambiguation (higher = checked first)
CATEGORY_PRIORITY = [
    "docker",
    "syntax",
    "dependency",
    "permission",
    "database",
    "network",
    "configuration",
    "runtime",
]


def extract_location(text: str) -> tuple[Optional[str], Optional[int]]:
    """Extract file path and line number from error text."""
    # Python traceback: File "path", line N
    m = re.search(r'File "([^"]+)", line (\d+)', text)
    if m:
        return m.group(1), int(m.group(2))

    # Node.js: at path:line:col
    m = re.search(r"at (?:\S+ \()?([^:()]+):(\d+):\d+\)?", text)
    if m:
        return m.group(1), int(m.group(2))

    # Go: path:line
    m = re.search(r"(\S+\.go):(\d+)", text)
    if m:
        return m.group(1), int(m.group(2))

    # Generic: filename.ext:line
    m = re.search(r"(\S+\.\w{1,5}):(\d+)", text)
    if m:
        return m.group(1), int(m.group(2))

    return None, None


def classify(text: str) -> dict:
    """Classify error text into a category with metadata."""
    best_match = None
    best_confidence = 0.0

    for category in CATEGORY_PRIORITY:
        for pattern, error_type, confidence in PATTERNS[category]:
            if re.search(pattern, text, re.IGNORECASE):
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = {
                        "category": category,
                        "error_type": error_type,
                        "confidence": confidence,
                    }
                    # If high confidence match in priority category, stop
                    if confidence >= 0.90:
                        break
        if best_match and best_confidence >= 0.90:
            break

    if not best_match:
        best_match = {
            "category": "runtime",
            "error_type": "Unknown",
            "confidence": 0.3,
        }

    file_path, line = extract_location(text)

    # Extract first meaningful error message line
    message = ""
    for raw_line in text.strip().splitlines():
        stripped = raw_line.strip()
        if stripped and not stripped.startswith(("Traceback", "  ", "at ")):
            message = stripped[:200]
            break
    if not message:
        message = text.strip()[:200]

    return {
        "category": best_match["category"],
        "error_type": best_match["error_type"],
        "message": message,
        "file": file_path,
        "line": line,
        "confidence": best_match["confidence"],
    }


def main():
    parser = argparse.ArgumentParser(
        description="Classify error messages into categories"
    )
    parser.add_argument("--file", "-f", help="Read error from file instead of stdin")
    args = parser.parse_args()

    if args.file:
        with open(args.file) as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    if not text.strip():
        emit_error("No input provided")
        sys.exit(EXIT_INVALID_ARGS)

    result = classify(text)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(EXIT_ERROR)
    except Exception as exc:
        emit_error(f"Unhandled exception: {exc}")
        sys.exit(EXIT_ERROR)
