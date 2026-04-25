#!/usr/bin/env python3
"""
Technical specification document validator.

Validates specification documents for completeness and quality:
- Required sections present
- Acceptance criteria defined
- Goals clearly stated
- Dependencies documented
- Out of scope items listed

Usage:
    python spec_validator.py <spec_file.md>
"""

import argparse
import re
import sys
from pathlib import Path

# Add shared library to path
sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent.parent / "_shared" / "python"),
)

from layer0 import EXIT_SUCCESS, EXIT_ERROR, EXIT_VALIDATION_ERROR  # noqa: E402
from layer1 import emit_error, emit_warning, emit_info  # noqa: E402


class SpecValidator:
    """Validates technical specification documents."""

    REQUIRED_SECTIONS = [
        "Overview",
        "Problem Statement",
        "Goals",
        "Functional Requirements",
        "Non-Functional Requirements",
        "Acceptance Criteria",
        "Dependencies",
        "Out of Scope",
    ]

    def __init__(self, spec_path: Path):
        self.path = spec_path
        self.content = ""
        self.issues: list[tuple[str, str]] = []  # (severity, message)
        self.found_sections = []

    def load(self) -> bool:
        """Load specification content."""
        try:
            with open(self.path, encoding="utf-8") as f:
                self.content = f.read()
            return True
        except Exception as e:
            emit_error(f"Error reading {self.path}: {e}")
            return False

    def check_required_sections(self):
        """Check for presence of required sections."""
        # Match markdown headers (# Title, ## Title, etc.)
        header_pattern = r"^#+\s+(.+)$"

        for line in self.content.split("\n"):
            match = re.match(header_pattern, line.strip())
            if match:
                self.found_sections.append(match.group(1).strip())

        for required in self.REQUIRED_SECTIONS:
            # Case-insensitive partial match
            found = any(required.lower() in section.lower() for section in self.found_sections)

            if not found:
                self.issues.append(("CRITICAL", f"Missing required section: {required}"))

    def check_acceptance_criteria(self):
        """Check for well-defined acceptance criteria."""
        ac_section = self._extract_section("Acceptance Criteria")

        if not ac_section:
            return  # Already reported as missing section

        # Check for bullet points or numbered lists
        has_list_items = bool(re.search(r"^\s*[-*\d+.]\s+", ac_section, re.MULTILINE))

        if not has_list_items:
            self.issues.append(
                ("WARNING", "Acceptance Criteria should be a list of testable conditions")
            )

        # Check for vague criteria
        vague_terms = ["improve", "better", "enhance", "optimize"]
        for term in vague_terms:
            if term in ac_section.lower():
                self.issues.append(
                    ("INFO", f'Vague term "{term}" in Acceptance Criteria (be specific)')
                )

    def check_goals(self):
        """Check for clear, measurable goals."""
        goals_section = self._extract_section("Goals")

        if not goals_section:
            return

        # Check for empty or very short goals section
        if len(goals_section.strip()) < 50:
            self.issues.append(("WARNING", "Goals section is too brief (elaborate on objectives)"))

        # Check for measurable criteria keywords
        measurable_keywords = ["reduce", "increase", "achieve", "support", "enable"]
        has_measurable = any(kw in goals_section.lower() for kw in measurable_keywords)

        if not has_measurable:
            self.issues.append(("INFO", "Goals lack measurable criteria (use concrete metrics)"))

    def check_dependencies(self):
        """Check for documented dependencies."""
        deps_section = self._extract_section("Dependencies")

        if not deps_section:
            return

        # Check if dependencies section is just "None" or empty
        if deps_section.strip().lower() in ["none", "n/a", "-"]:
            self.issues.append(
                ("INFO", 'Dependencies listed as "None" (verify if truly no dependencies)')
            )

    def check_out_of_scope(self):
        """Check for out-of-scope items."""
        oos_section = self._extract_section("Out of Scope")

        if not oos_section:
            return

        # Check if section is empty or too brief
        if len(oos_section.strip()) < 20:
            self.issues.append(
                ("WARNING", "Out of Scope section is brief (explicitly state non-goals)")
            )

    def check_problem_statement(self):
        """Check for clear problem statement."""
        problem_section = self._extract_section("Problem Statement")

        if not problem_section:
            return

        # Check for brief problem statements
        if len(problem_section.strip()) < 100:
            self.issues.append(
                ("WARNING", "Problem Statement is brief (explain context and motivation)")
            )

        # Check for "why" questions
        why_keywords = ["why", "because", "reason", "motivation"]
        has_why = any(kw in problem_section.lower() for kw in why_keywords)

        if not has_why:
            self.issues.append(("INFO", 'Problem Statement lacks "why" (explain motivation)'))

    def _extract_section(self, section_name: str) -> str:
        """Extract content of a specific section."""
        # Find section by header
        pattern = rf"^#+\s+{re.escape(section_name)}.*?$"
        match = re.search(pattern, self.content, re.MULTILINE | re.IGNORECASE)

        if not match:
            return ""

        # Extract content until next header of same or higher level
        start = match.end()
        header_level = len(re.match(r"^(#+)", match.group()).group(1))

        # Find next header of same or higher level
        next_header = re.search(
            rf"^#{{{1},{header_level}}}[^#]", self.content[start:], re.MULTILINE
        )

        end = start + next_header.start() if next_header else len(self.content)

        return self.content[start:end].strip()

    def validate(self) -> bool:
        """Run all validation checks."""
        if not self.load():
            return False

        self.check_required_sections()
        self.check_problem_statement()
        self.check_goals()
        self.check_acceptance_criteria()
        self.check_dependencies()
        self.check_out_of_scope()

        return True

    def print_report(self):
        """Print validation report."""
        severity_order = {"CRITICAL": 0, "WARNING": 1, "INFO": 2}
        sorted_issues = sorted(self.issues, key=lambda x: severity_order[x[0]])

        if not sorted_issues:
            print(f"✅ {self.path.name}: Specification is complete!")
            return

        print(f"\n{self.path.name} — Found {len(sorted_issues)} issue(s):\n")

        for severity, message in sorted_issues:
            icon = {"CRITICAL": "🔴", "WARNING": "🟡", "INFO": "ℹ️"}[severity]
            print(f"  {icon} [{severity}] {message}")

        print(f"\nSections found: {', '.join(self.found_sections)}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate technical specification")
    parser.add_argument("spec", type=Path, help="Path to specification markdown file")
    args = parser.parse_args()

    if not args.spec.exists():
        emit_error(f"{args.spec} not found")
        sys.exit(EXIT_ERROR)

    validator = SpecValidator(args.spec)
    if not validator.validate():
        sys.exit(EXIT_ERROR)

    validator.print_report()

    # Exit with error if critical issues found
    has_critical = any(sev == "CRITICAL" for sev, _ in validator.issues)
    sys.exit(EXIT_VALIDATION_ERROR if has_critical else EXIT_SUCCESS)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(EXIT_ERROR)
    except Exception as exc:
        emit_error(f"Unhandled exception: {exc}")
        sys.exit(EXIT_ERROR)
