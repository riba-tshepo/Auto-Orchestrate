#!/usr/bin/env python3
"""Extract structured requirements from spec documents (Markdown, YAML, JSON).

Usage:
    python3 spec_parser.py --file docs/spec.md
    python3 spec_parser.py --file requirements.yaml
    python3 spec_parser.py --help

Output: JSON object with requirements array.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional

# Add shared library to path
sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent.parent / "_shared" / "python"),
)

from layer1.spec_utils import (  # noqa: E402
    IMPERATIVE_PATTERNS,
    PRIORITY_MAP,
    TYPE_INDICATORS,
    extract_keywords,
    infer_priority,
    infer_type,
)


def parse_markdown(content: str, source_path: str) -> list[dict]:
    """Parse requirements from a Markdown document."""
    requirements = []
    req_counter = 0
    lines = content.splitlines()

    # Strategy 1: Find tables with ID/requirement columns
    in_table = False
    table_headers = []
    id_col = -1
    desc_col = -1
    priority_col = -1

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Detect table headers
        if "|" in stripped and not in_table:
            cells = [c.strip() for c in stripped.split("|")]
            cells = [c for c in cells if c]  # Remove empty edge cells
            for j, cell in enumerate(cells):
                cl = cell.lower()
                if cl in ("id", "req-id", "requirement id", "#", "ref"):
                    id_col = j
                if any(k in cl for k in ("description", "requirement", "feature", "story", "detail")):
                    desc_col = j
                if any(k in cl for k in ("priority", "pri", "level", "importance")):
                    priority_col = j
            if desc_col >= 0:
                in_table = True
                table_headers = cells
                continue

        # Detect table separator (---|---|---)
        if in_table and re.match(r"^\|?\s*[-:]+\s*(\|\s*[-:]+\s*)+\|?\s*$", stripped):
            continue

        # Parse table rows
        if in_table and "|" in stripped:
            cells = [c.strip() for c in stripped.split("|")]
            cells = [c for c in cells if c]
            if len(cells) > desc_col:
                req_counter += 1
                req_id = cells[id_col] if id_col >= 0 and id_col < len(cells) else f"REQ-{req_counter:03d}"
                description = cells[desc_col] if desc_col < len(cells) else ""
                priority = cells[priority_col] if priority_col >= 0 and priority_col < len(cells) else infer_priority(description)

                if description and len(description) > 5:
                    requirements.append({
                        "id": req_id,
                        "source": f"{source_path}:L{i}",
                        "type": infer_type(description),
                        "priority": priority.upper() if priority else "SHOULD",
                        "description": description,
                        "acceptance_criteria": "",
                        "keywords": extract_keywords(description),
                    })
            continue
        elif in_table:
            in_table = False
            id_col = desc_col = priority_col = -1

    # Strategy 2: Find heading-based requirements (## Feature: ..., ### REQ-001: ...)
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        # Match headings with requirement-like content
        m = re.match(r"^#{1,4}\s+(?:(REQ-\d+|FR-\d+|NFR-\d+|US-\d+)[:\s]+)?(.+)$", stripped)
        if m:
            req_id_match = m.group(1)
            heading_text = m.group(2).strip()

            # Check if this heading describes a requirement (not a section header)
            if any(re.search(p, heading_text, re.IGNORECASE) for p in IMPERATIVE_PATTERNS):
                req_counter += 1
                req_id = req_id_match or f"REQ-{req_counter:03d}"
                # Check if already captured from table
                if not any(r["id"] == req_id for r in requirements):
                    requirements.append({
                        "id": req_id,
                        "source": f"{source_path}:L{i}",
                        "type": infer_type(heading_text),
                        "priority": infer_priority(heading_text),
                        "description": heading_text,
                        "acceptance_criteria": "",
                        "keywords": extract_keywords(heading_text),
                    })

    # Strategy 3: Find imperative sentences in prose (fallback)
    if not requirements:
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or stripped.startswith("|"):
                continue
            for pattern in IMPERATIVE_PATTERNS:
                if re.search(pattern, stripped, re.IGNORECASE):
                    # Found an imperative statement
                    req_counter += 1
                    requirements.append({
                        "id": f"REQ-{req_counter:03d}",
                        "source": f"{source_path}:L{i}",
                        "type": infer_type(stripped),
                        "priority": infer_priority(stripped),
                        "description": stripped[:200],
                        "acceptance_criteria": "",
                        "keywords": extract_keywords(stripped),
                    })
                    break  # One requirement per line

    # Strategy 4: Find acceptance criteria blocks and attach to nearest requirement
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if re.match(r"^(?:Given|When|Then|And|AC[-\s]?\d+)", stripped, re.IGNORECASE):
            # Find the most recent requirement and append AC
            if requirements:
                ac = requirements[-1]["acceptance_criteria"]
                requirements[-1]["acceptance_criteria"] = (ac + "\n" + stripped).strip()

    return requirements


def parse_yaml(content: str, source_path: str) -> list[dict]:
    """Parse requirements from a YAML document."""
    try:
        import yaml
        data = yaml.safe_load(content)
    except ImportError:
        # Fallback: basic YAML-like parsing
        return parse_markdown(content, source_path)
    except Exception:
        return []

    if not isinstance(data, dict):
        return []

    requirements = []
    req_list = data.get("requirements") or data.get("features") or data.get("stories") or []

    for idx, req in enumerate(req_list, 1):
        if isinstance(req, dict):
            desc = req.get("description") or req.get("name") or req.get("title") or ""
            requirements.append({
                "id": req.get("id", f"REQ-{idx:03d}"),
                "source": f"{source_path}:req[{idx}]",
                "type": req.get("type", infer_type(desc)),
                "priority": req.get("priority", infer_priority(desc)).upper(),
                "description": desc,
                "acceptance_criteria": req.get("acceptance_criteria", ""),
                "keywords": req.get("keywords", extract_keywords(desc)),
            })
        elif isinstance(req, str):
            requirements.append({
                "id": f"REQ-{idx:03d}",
                "source": f"{source_path}:req[{idx}]",
                "type": infer_type(req),
                "priority": infer_priority(req),
                "description": req,
                "acceptance_criteria": "",
                "keywords": extract_keywords(req),
            })

    return requirements


def parse_json(content: str, source_path: str) -> list[dict]:
    """Parse requirements from a JSON document."""
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return []

    if isinstance(data, list):
        req_list = data
    elif isinstance(data, dict):
        req_list = data.get("requirements") or data.get("features") or data.get("stories") or []
    else:
        return []

    requirements = []
    for idx, req in enumerate(req_list, 1):
        if isinstance(req, dict):
            desc = req.get("description") or req.get("name") or req.get("title") or ""
            requirements.append({
                "id": req.get("id", f"REQ-{idx:03d}"),
                "source": f"{source_path}:req[{idx}]",
                "type": req.get("type", infer_type(desc)),
                "priority": req.get("priority", infer_priority(desc)).upper(),
                "description": desc,
                "acceptance_criteria": req.get("acceptance_criteria", ""),
                "keywords": req.get("keywords", extract_keywords(desc)),
            })

    return requirements


def parse_spec(file_path: str) -> dict:
    """Parse a spec file and return structured requirements."""
    path = Path(file_path)
    if not path.exists():
        return {"error": f"File not found: {file_path}", "requirements": []}

    content = path.read_text(encoding="utf-8", errors="replace")
    suffix = path.suffix.lower()

    if suffix in (".yaml", ".yml"):
        requirements = parse_yaml(content, file_path)
    elif suffix == ".json":
        requirements = parse_json(content, file_path)
    else:
        # Default to markdown parsing (handles .md, .txt, .rst, etc.)
        requirements = parse_markdown(content, file_path)

    return {
        "spec_path": file_path,
        "format": suffix.lstrip(".") or "markdown",
        "total_requirements": len(requirements),
        "by_type": {
            t: sum(1 for r in requirements if r["type"] == t)
            for t in ("functional", "non-functional", "service", "security")
            if any(r["type"] == t for r in requirements)
        },
        "by_priority": {
            p: sum(1 for r in requirements if r["priority"] == p)
            for p in ("MUST", "SHOULD", "MAY")
            if any(r["priority"] == p for r in requirements)
        },
        "requirements": requirements,
    }


def main():
    parser = argparse.ArgumentParser(description="Extract requirements from spec documents")
    parser.add_argument("--file", "-f", required=True, help="Path to spec/requirements document")
    args = parser.parse_args()

    result = parse_spec(args.file)

    if "error" in result:
        print(json.dumps(result), file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
