#!/usr/bin/env python3
"""Check codebase compliance against extracted requirements.

Usage:
    python3 compliance_checker.py --requirements reqs.json --root /path/to/project
    python3 spec_parser.py -f spec.md | python3 compliance_checker.py --root .
    python3 compliance_checker.py --help

Output: JSON compliance matrix with per-requirement status and evidence.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Add shared library to path
sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent.parent / "_shared" / "python"),
)

from layer0 import EXIT_SUCCESS, EXIT_ERROR  # noqa: E402
from layer1 import emit_error, emit_warning, emit_info  # noqa: E402


# Directories to skip during scanning
SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "env",
    ".tox", ".mypy_cache", ".pytest_cache", "dist", "build",
    ".next", ".nuxt", "coverage", ".eggs", "*.egg-info",
}

# File extensions to scan
CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java",
    ".rb", ".php", ".cs", ".sql", ".sh", ".bash",
}

# Placeholder patterns indicating incomplete implementation
PLACEHOLDER_PATTERNS = [
    r"\bTODO\b", r"\bFIXME\b", r"\bHACK\b", r"\bPLACEHOLDER\b",
    r"\bNotImplementedError\b", r"raise\s+NotImplementedError",
    r'throw\s+new\s+Error\s*\(\s*["\']Not\s+implemented',
    r"\bpass\s*#.*(?:placeholder|todo|stub)",
]


def should_skip(path: Path) -> bool:
    """Check if a path should be skipped."""
    parts = path.parts
    return any(p in SKIP_DIRS or p.startswith(".") for p in parts[:-1])


def grep_project(root: Path, pattern: str, extensions: Optional[set] = None, max_results: int = 20) -> list[dict]:
    """Search project files for a pattern."""
    exts = extensions or CODE_EXTENSIONS
    results = []

    include_args = " ".join(f'--include="*{ext}"' for ext in exts)
    cmd = f'grep -rnl "{pattern}" {include_args} "{root}" 2>/dev/null | head -{max_results}'

    try:
        output = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=10
        ).stdout.strip()
    except (subprocess.TimeoutExpired, OSError):
        return results

    for line in output.splitlines():
        line = line.strip()
        if line and not should_skip(Path(line)):
            results.append({"file": line})

    return results


def grep_with_context(root: Path, pattern: str, max_results: int = 10) -> list[dict]:
    """Search with line numbers and context."""
    exts = CODE_EXTENSIONS
    include_args = " ".join(f'--include="*{ext}"' for ext in exts)
    cmd = f'grep -rn "{pattern}" {include_args} "{root}" 2>/dev/null | head -{max_results}'

    results = []
    try:
        output = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=10
        ).stdout.strip()
    except (subprocess.TimeoutExpired, OSError):
        return results

    for line in output.splitlines():
        match = re.match(r"^(.+?):(\d+):(.*)", line)
        if match and not should_skip(Path(match.group(1))):
            results.append({
                "file": match.group(1),
                "line": int(match.group(2)),
                "content": match.group(3).strip()[:100],
            })

    return results


def find_files(root: Path, pattern: str, max_results: int = 20) -> list[str]:
    """Find files matching a name pattern."""
    cmd = f'find "{root}" -name "{pattern}" -not -path "*/.git/*" -not -path "*/node_modules/*" -not -path "*/__pycache__/*" -not -path "*/.venv/*" 2>/dev/null | head -{max_results}'

    try:
        output = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=10
        ).stdout.strip()
    except (subprocess.TimeoutExpired, OSError):
        return []

    return [f for f in output.splitlines() if f.strip()]


def check_for_placeholders(root: Path, files: list[str]) -> list[dict]:
    """Check if files contain placeholder/TODO patterns."""
    findings = []
    for fpath in files[:10]:  # Limit to avoid timeout
        for pattern in PLACEHOLDER_PATTERNS:
            matches = grep_with_context(Path(fpath).parent, pattern, max_results=3)
            for m in matches:
                if m["file"] == fpath or fpath in m["file"]:
                    findings.append({
                        "file": m["file"],
                        "line": m["line"],
                        "pattern": pattern,
                        "content": m["content"],
                    })
    return findings


def check_for_tests(root: Path, keywords: list[str]) -> list[str]:
    """Check if tests exist for given keywords."""
    test_dirs = ["tests", "test", "spec", "__tests__"]
    test_files = []

    for keyword in keywords[:5]:
        # Search in test directories
        for test_dir in test_dirs:
            test_path = root / test_dir
            if test_path.exists():
                found = grep_project(test_path, keyword, max_results=5)
                test_files.extend(f["file"] for f in found)

        # Search for test files matching keyword
        for pattern in [f"*test*{keyword}*", f"*{keyword}*test*", f"test_{keyword}*"]:
            found = find_files(root, pattern, max_results=5)
            test_files.extend(found)

    return list(set(test_files))[:10]


def check_requirement(root: Path, requirement: dict) -> dict:
    """Check a single requirement against the codebase."""
    keywords = requirement.get("keywords", [])
    description = requirement.get("description", "")

    if not keywords:
        keywords = re.findall(r"[a-zA-Z_][a-zA-Z0-9_]{2,}", description.lower())[:5]

    evidence = {
        "files": [],
        "functions": [],
        "routes": [],
        "tests": [],
        "issues": [],
    }

    # Search for implementation files
    for keyword in keywords[:5]:
        # File name matches
        for pattern in [f"*{keyword}*"]:
            found = find_files(root, pattern, max_results=5)
            for f in found:
                if any(f.endswith(ext) for ext in CODE_EXTENSIONS):
                    evidence["files"].append(f)

        # Content matches
        matches = grep_with_context(root, keyword, max_results=5)
        for m in matches:
            if m["file"] not in evidence["files"]:
                evidence["files"].append(m["file"])
            # Check if match is a function/class definition
            content = m["content"]
            if re.search(r"(?:def|function|class|const|let|var)\s+\w*" + re.escape(keyword), content, re.IGNORECASE):
                evidence["functions"].append({
                    "file": m["file"],
                    "line": m["line"],
                    "definition": content,
                })
            # Check if match is a route/endpoint
            if re.search(r"(?:route|path|get|post|put|delete|patch|@app\.|@router\.)", content, re.IGNORECASE):
                evidence["routes"].append({
                    "file": m["file"],
                    "line": m["line"],
                    "route": content,
                })

    # Deduplicate files
    evidence["files"] = list(set(evidence["files"]))[:15]

    # Check for tests
    evidence["tests"] = check_for_tests(root, keywords)

    # Check for placeholder/TODO patterns in found files
    if evidence["files"]:
        placeholders = check_for_placeholders(root, evidence["files"][:5])
        evidence["issues"] = placeholders

    # Determine status
    has_files = len(evidence["files"]) > 0
    has_tests = len(evidence["tests"]) > 0
    has_issues = len(evidence["issues"]) > 0
    has_routes = len(evidence["routes"]) > 0 or len(evidence["functions"]) > 0

    if has_files and has_routes and has_tests and not has_issues:
        status = "PASS"
    elif has_files and (has_routes or has_tests) and not has_issues:
        status = "PARTIAL"
    elif has_files and has_issues:
        status = "FAIL"
    elif has_files:
        status = "PARTIAL"
    else:
        status = "MISSING"

    return {
        "id": requirement["id"],
        "source": requirement.get("source", ""),
        "type": requirement.get("type", "functional"),
        "priority": requirement.get("priority", "SHOULD"),
        "description": requirement.get("description", ""),
        "status": status,
        "evidence": {
            "files": evidence["files"][:10],
            "functions": evidence["functions"][:5],
            "routes": evidence["routes"][:5],
            "tests": evidence["tests"][:5],
            "issues": evidence["issues"][:5],
        },
        "details": _build_details(status, evidence),
    }


def _build_details(status: str, evidence: dict) -> str:
    """Build a human-readable details string."""
    if status == "PASS":
        return f"Implementation found in {len(evidence['files'])} file(s), {len(evidence['tests'])} test(s)"
    elif status == "PARTIAL":
        parts = []
        if evidence["files"]:
            parts.append(f"{len(evidence['files'])} file(s) found")
        if not evidence["tests"]:
            parts.append("no tests")
        if not evidence["routes"] and not evidence["functions"]:
            parts.append("no route/function definitions")
        return "; ".join(parts)
    elif status == "FAIL":
        issues = evidence["issues"]
        if issues:
            return f"Implementation exists but contains: {issues[0].get('content', 'issues')}"
        return "Implementation exists but appears broken"
    else:
        return "No implementation evidence found"


def main():
    parser = argparse.ArgumentParser(description="Check codebase compliance against requirements")
    parser.add_argument("--requirements", "-r", help="Requirements JSON file (or read from stdin)")
    parser.add_argument("--root", required=True, help="Project root directory")
    args = parser.parse_args()

    # Read requirements
    if args.requirements:
        with open(args.requirements) as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)

    requirements = data.get("requirements", data if isinstance(data, list) else [])
    root = Path(args.root).resolve()

    if not root.is_dir():
        emit_error(f"Root directory not found: {root}")
        sys.exit(EXIT_ERROR)

    # Check each requirement
    results = []
    for req in requirements:
        result = check_requirement(root, req)
        results.append(result)

    # Calculate summary
    total = len(results)
    summary = {
        "pass": sum(1 for r in results if r["status"] == "PASS"),
        "partial": sum(1 for r in results if r["status"] == "PARTIAL"),
        "missing": sum(1 for r in results if r["status"] == "MISSING"),
        "fail": sum(1 for r in results if r["status"] == "FAIL"),
        "skipped": sum(1 for r in results if r["status"] == "SKIPPED"),
    }

    score = (summary["pass"] + summary["partial"] * 0.5) / total * 100 if total > 0 else 0

    output = {
        "project_root": str(root),
        "total_requirements": total,
        "compliance_score": round(score, 1),
        "summary": summary,
        "results": results,
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(EXIT_ERROR)
    except Exception as exc:
        emit_error(f"Unhandled exception: {exc}")
        sys.exit(EXIT_ERROR)
