#!/usr/bin/env python3
"""Research depth coherence validator (RES-014, RESEARCH-DEPTH-001).

Parses a research output Markdown file and checks that it satisfies the contract
for its declared RESEARCH_DEPTH tier. Emits a structured JSON verdict.

Usage:
    python3 depth_check.py --file research.md --tier deep
    python3 depth_check.py --file research.md --tier exhaustive --strict
    python3 depth_check.py --selftest

Exit codes:
    0 = PASS (all contract items satisfied)
    1 = WARN (optional items missing; core contract met)
    2 = FAIL (at least one core contract item violated)
    3 = ERROR (file unreadable, invalid tier, etc.)

Stdlib-only. No external dependencies.
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


VALID_TIERS = ("minimal", "normal", "deep", "exhaustive")

# Per-tier contract (RES-014 authoritative table).
# Fields:
#   query_floor: minimum count of Sources-table rows expected
#   require_cve: whether a CVE Findings section (or table) must appear
#   require_risks_remedies: whether a Risks & Remedies section is mandatory
#   require_recommended_versions: whether a Recommended Versions table is mandatory
#   sources_per_high: minimum independent sources per HIGH-severity finding
#   require_production_incidents: whether a Production Incident Patterns section is mandatory
#   require_domain_partition: whether output MUST be partitioned into per-domain sections
#   required_domains: per-domain section names for exhaustive
CONTRACT = {
    "minimal": {
        "query_floor": 0,
        "require_cve": True,
        "require_risks_remedies": False,
        "require_recommended_versions": False,
        "sources_per_high": 1,
        "require_production_incidents": False,
        "require_domain_partition": False,
        "required_domains": [],
    },
    "normal": {
        "query_floor": 3,
        "require_cve": True,
        "require_risks_remedies": True,
        "require_recommended_versions": True,
        "sources_per_high": 1,
        "require_production_incidents": False,
        "require_domain_partition": False,
        "required_domains": [],
    },
    "deep": {
        "query_floor": 10,
        "require_cve": True,
        "require_risks_remedies": True,
        "require_recommended_versions": True,
        "sources_per_high": 2,
        "require_production_incidents": True,
        "require_domain_partition": False,
        "required_domains": [],
    },
    "exhaustive": {
        "query_floor": 30,
        "require_cve": True,
        "require_risks_remedies": True,
        "require_recommended_versions": True,
        "sources_per_high": 3,
        "require_production_incidents": True,
        "require_domain_partition": True,
        "required_domains": [
            "Security Findings",
            "Performance Findings",
            "Operational Findings",
        ],
    },
}


@dataclass
class CheckResult:
    name: str
    expected: str
    actual: str
    result: str  # "pass" | "warn" | "fail"
    severity: str = "core"  # "core" | "optional"


@dataclass
class Verdict:
    path: str
    declared_tier: str
    result: str  # "pass" | "warn" | "fail"
    checks: list = field(default_factory=list)
    shortfalls: list = field(default_factory=list)
    contract: dict = field(default_factory=dict)

    def add(self, check: CheckResult) -> None:
        self.checks.append(check)
        if check.result == "fail":
            self.shortfalls.append(check.name)

    def exit_code(self) -> int:
        has_fail = any(c.result == "fail" and c.severity == "core" for c in self.checks)
        has_warn = any(c.result in ("fail", "warn") and c.severity == "optional" for c in self.checks)
        if has_fail:
            return 2
        if has_warn:
            return 1
        return 0


# ------------ Parsing ------------


def parse_sections(text: str) -> dict:
    """Split markdown into top-level sections keyed by heading title.

    Matches both `## Heading` and `### Heading` — we flatten to a dict of
    title -> raw body text.
    """
    sections = {}
    current_title = None
    current_body = []
    for line in text.splitlines():
        m = re.match(r"^(#{2,3})\s+(.+?)\s*$", line)
        if m:
            if current_title is not None:
                sections[current_title] = "\n".join(current_body).strip()
            current_title = m.group(2).strip()
            current_body = []
        else:
            if current_title is not None:
                current_body.append(line)
    if current_title is not None:
        sections[current_title] = "\n".join(current_body).strip()
    return sections


def section_matches(sections: dict, patterns: list) -> Optional[str]:
    """Return the first section title matching any of `patterns` (case-insensitive
    substring), or None."""
    lowered = [(t, t.lower()) for t in sections]
    for pat in patterns:
        p = pat.lower()
        for orig, low in lowered:
            if p in low:
                return orig
    return None


def count_sources_rows(sources_body: str) -> int:
    """Count data rows in the Sources markdown table.

    Format expected:
        | # | URL/Path | Type | Date | Age Flag |
        |---|---|---|---|---|
        | 1 | https://... | WebSearch | 2026-04-18 | |
        | 2 | ... | ... | ... | ... |

    Data rows are `|<ws><digits>|...`. Header/separator rows are excluded.
    """
    count = 0
    for line in sources_body.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        # Skip separator rows (| --- | --- |)
        if re.match(r"^\|[\s\-|:]+\|$", line):
            continue
        # Skip header rows (by convention the first data column should be a number)
        first_cell = line.split("|", 2)
        if len(first_cell) < 2:
            continue
        cell = first_cell[1].strip()
        if re.fullmatch(r"\d+", cell):
            count += 1
    return count


def find_high_findings(section_body: str) -> list:
    """Return raw markdown rows flagged HIGH in a severity-containing table.

    Looks for lines containing `HIGH` (case-sensitive by convention) inside
    a pipe-delimited row.
    """
    rows = []
    for line in section_body.splitlines():
        line = line.strip()
        if line.startswith("|") and "HIGH" in line:
            rows.append(line)
    return rows


def count_sources_in_row(row: str) -> int:
    """Approximate source count in a single HIGH-finding row.

    Count: (a) distinct URLs, (b) markdown link refs `[text](url)`, (c) CVE IDs.
    De-duplicate by surface form.
    """
    surfaces = set()
    # URLs
    for m in re.finditer(r"https?://[^\s|)\]]+", row):
        surfaces.add(m.group(0))
    # Bracketed markdown links
    for m in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", row):
        surfaces.add(m.group(2))
    # CVE IDs (counted as source references even without URL)
    for m in re.finditer(r"CVE-\d{4}-\d+", row):
        surfaces.add(m.group(0))
    return len(surfaces)


# ------------ Checks ------------


def run_checks(path: Path, tier: str, strict: bool = False) -> Verdict:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        v = Verdict(path=str(path), declared_tier=tier, result="fail")
        v.add(CheckResult("file_readable", "file exists and UTF-8 readable",
                          f"error: {e}", "fail"))
        return v

    contract = CONTRACT[tier]
    v = Verdict(path=str(path), declared_tier=tier, contract=contract, result="pass")
    sections = parse_sections(text)

    # --- Check 1: Sources section present + query floor ---
    sources_title = section_matches(sections, ["Sources"])
    if sources_title is None:
        v.add(CheckResult("sources_section", "present", "absent", "fail"))
    else:
        n = count_sources_rows(sections[sources_title])
        floor = contract["query_floor"]
        if floor == 0:
            v.add(CheckResult("query_floor", f">={floor}", str(n), "pass"))
        elif n >= floor:
            v.add(CheckResult("query_floor", f">={floor}", str(n), "pass"))
        else:
            # minimal tier cache-hit exception: 0-1 acceptable if "CACHED-RESEARCH"
            # marker appears anywhere in the file
            if tier == "minimal" and "CACHED-RESEARCH" in text:
                v.add(CheckResult("query_floor", f">={floor} (or cache-hit)",
                                  f"{n} (cache-hit detected)", "pass"))
            else:
                v.add(CheckResult("query_floor", f">={floor}", str(n), "fail"))

    # --- Check 2: CVE section ---
    cve_title = section_matches(sections, ["CVE", "Security Findings"])
    if contract["require_cve"]:
        if cve_title is None:
            v.add(CheckResult("cve_section", "present", "absent", "fail"))
        else:
            v.add(CheckResult("cve_section", "present", f"present ({cve_title})", "pass"))

    # --- Check 3: Risks & Remedies section ---
    rr_title = section_matches(sections, ["Risks & Remedies", "Risks and Remedies",
                                           "Implementation Risks"])
    if contract["require_risks_remedies"]:
        if rr_title is None:
            v.add(CheckResult("risks_remedies_section", "present", "absent", "fail"))
        else:
            v.add(CheckResult("risks_remedies_section", "present",
                              f"present ({rr_title})", "pass"))

    # --- Check 4: Recommended Versions table ---
    rv_title = section_matches(sections, ["Recommended Versions"])
    if contract["require_recommended_versions"]:
        if rv_title is None:
            v.add(CheckResult("recommended_versions_table", "present", "absent", "fail"))
        else:
            v.add(CheckResult("recommended_versions_table", "present",
                              f"present ({rv_title})", "pass"))

    # --- Check 5: Production Incident Patterns (deep+) ---
    pip_title = section_matches(sections, ["Production Incident Patterns",
                                            "Production Incidents"])
    if contract["require_production_incidents"]:
        if pip_title is None:
            v.add(CheckResult("production_incidents_section", "present", "absent", "fail"))
        else:
            v.add(CheckResult("production_incidents_section", "present",
                              f"present ({pip_title})", "pass"))

    # --- Check 6: Domain partition (exhaustive) ---
    if contract["require_domain_partition"]:
        missing = []
        for dom in contract["required_domains"]:
            if section_matches(sections, [dom]) is None:
                missing.append(dom)
        if missing:
            v.add(CheckResult("domain_partition",
                              f"all of {contract['required_domains']}",
                              f"missing: {missing}", "fail"))
        else:
            v.add(CheckResult("domain_partition",
                              f"all of {contract['required_domains']}",
                              "all present", "pass"))

    # --- Check 7: Sources per HIGH finding ---
    min_sources = contract["sources_per_high"]
    if min_sources > 1 and rr_title is not None:
        high_rows = find_high_findings(sections[rr_title])
        under = []
        for row in high_rows:
            n = count_sources_in_row(row)
            if n < min_sources:
                # Truncate row for reporting
                preview = row[:80] + ("..." if len(row) > 80 else "")
                under.append(f"{n} src: {preview}")
        if under:
            v.add(CheckResult("sources_per_high_finding",
                              f">={min_sources} sources per HIGH row",
                              f"{len(under)} row(s) below floor",
                              "fail" if strict else "warn",
                              severity="core" if strict else "optional"))
        else:
            v.add(CheckResult("sources_per_high_finding",
                              f">={min_sources} sources per HIGH row",
                              f"{len(high_rows)} HIGH row(s), all satisfied",
                              "pass"))

    # Finalize aggregate result
    core_fail = any(c.result == "fail" and c.severity == "core" for c in v.checks)
    any_warn = any(c.result in ("fail", "warn") and c.severity == "optional"
                   for c in v.checks)
    v.result = "fail" if core_fail else ("warn" if any_warn else "pass")
    return v


# ------------ Self-test ------------


SELFTEST_DEEP_PASS = """# Research

## Summary
Ok.

## CVE / Security Findings
| Pkg | CVE | Severity | Description | Fixed In | Status |
|---|---|---|---|---|---|

## Implementation Risks & Remedies
| # | Risk | Severity | Remedy | Applies To |
|---|---|---|---|---|
| 1 | Deadlock under load | HIGH | Use async locks per https://example.com/a and https://example.com/b | Stage 3 |
| 2 | Memory leak | MEDIUM | Add cleanup | Stage 3 |

## Recommended Versions
| Package | Version | Source | Verified From | Date |
|---|---|---|---|---|
| foo | 1.2.3 | pypi | https://pypi.org/foo | 2026-04-18 |

## Production Incident Patterns
Known failure modes from post-mortems:
- [GitHub issue 123](https://github.com/x/y/issues/123) — outage cause
- [Vendor post-mortem](https://example.com/pm) — alternative data point

## Recommendations
1. **[HIGH]** Use async locks — see https://example.com/a and https://example.com/b

## Sources
| # | URL | Type | Date | Age |
|---|---|---|---|---|
| 1 | https://example.com/1 | WebSearch | 2026-04-18 | |
| 2 | https://example.com/2 | WebSearch | 2026-04-18 | |
| 3 | https://example.com/3 | WebSearch | 2026-04-18 | |
| 4 | https://example.com/4 | WebSearch | 2026-04-18 | |
| 5 | https://example.com/5 | WebSearch | 2026-04-18 | |
| 6 | https://example.com/6 | WebSearch | 2026-04-18 | |
| 7 | https://example.com/7 | WebSearch | 2026-04-18 | |
| 8 | https://example.com/8 | WebSearch | 2026-04-18 | |
| 9 | https://example.com/9 | WebSearch | 2026-04-18 | |
| 10 | https://example.com/10 | WebSearch | 2026-04-18 | |
"""

SELFTEST_NORMAL_MISSING_RR = """# Research

## Summary
Quick.

## CVE / Security Findings
No CVEs found.

## Recommended Versions
| Package | Version | Source | Verified From | Date |
|---|---|---|---|---|
| foo | 1.2.3 | pypi | https://pypi.org/foo | 2026-04-18 |

## Sources
| # | URL | Type | Date | Age |
|---|---|---|---|---|
| 1 | https://example.com/1 | WebSearch | 2026-04-18 | |
| 2 | https://example.com/2 | WebSearch | 2026-04-18 | |
| 3 | https://example.com/3 | WebSearch | 2026-04-18 | |
"""

SELFTEST_MINIMAL_CACHE_HIT = """# Research

## Summary
Cache hit.

[CACHED-RESEARCH] Results pulled from .pipeline-state/research-cache.jsonl

## CVE / Security Findings
No CVEs found.

## Sources
| # | URL | Type | Date | Age |
|---|---|---|---|---|
| 1 | cache://entry-abc | cached | 2026-04-18 | |
"""


def selftest() -> int:
    import tempfile
    cases = [
        ("deep_pass", SELFTEST_DEEP_PASS, "deep", 0),
        ("normal_missing_rr", SELFTEST_NORMAL_MISSING_RR, "normal", 2),
        ("minimal_cache_hit", SELFTEST_MINIMAL_CACHE_HIT, "minimal", 0),
    ]
    failures = []
    for name, content, tier, expected_exit in cases:
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write(content)
            path = Path(f.name)
        try:
            v = run_checks(path, tier)
            actual_exit = v.exit_code()
            if actual_exit != expected_exit:
                failures.append(
                    f"{name}: expected exit {expected_exit}, got {actual_exit}. "
                    f"shortfalls={v.shortfalls}"
                )
            else:
                print(f"  [OK] {name} (exit {actual_exit})")
        finally:
            path.unlink()
    if failures:
        print("SELFTEST FAILED:")
        for f in failures:
            print(f"  {f}")
        return 1
    print("SELFTEST PASSED (3/3 cases)")
    return 0


# ------------ CLI ------------


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--file", type=Path,
                   help="Path to research output markdown file")
    p.add_argument("--tier", choices=VALID_TIERS,
                   help="Declared RESEARCH_DEPTH tier")
    p.add_argument("--strict", action="store_true",
                   help="Treat warn-level issues as fail")
    p.add_argument("--selftest", action="store_true",
                   help="Run built-in self-tests and exit")
    p.add_argument("--json", action="store_true",
                   help="Emit full JSON verdict (default: summary + exit code)")
    args = p.parse_args()

    if args.selftest:
        return selftest()

    if not args.file or not args.tier:
        p.error("--file and --tier are required (or use --selftest)")

    verdict = run_checks(args.file, args.tier, strict=args.strict)

    if args.json:
        # Serialize verdict as JSON
        out = asdict(verdict)
        out["checks"] = [asdict(c) for c in verdict.checks]
        out["exit_code"] = verdict.exit_code()
        print(json.dumps(out, indent=2))
    else:
        print(f"[DEPTH-CHECK] {verdict.path}")
        print(f"  Declared tier: {verdict.declared_tier}")
        print(f"  Result: {verdict.result.upper()}")
        for c in verdict.checks:
            marker = {"pass": "OK", "warn": "WARN", "fail": "FAIL"}.get(c.result, "?")
            print(f"  [{marker}] {c.name}: expected {c.expected}, got {c.actual}")
        if verdict.shortfalls:
            print(f"  Shortfalls: {', '.join(verdict.shortfalls)}")
    return verdict.exit_code()


if __name__ == "__main__":
    sys.exit(main())
