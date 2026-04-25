#!/usr/bin/env python3
"""
Compliance Checker - Checks project conventions and standards.

Validates project structure, required files, naming conventions,
and configurable compliance rules.

Usage:
    compliance_checker.py [-o json|human] [--rules RULES_FILE] [--strict] TARGET_DIR

Examples:
    compliance_checker.py .
    compliance_checker.py --rules custom-rules.yaml src/
    compliance_checker.py -o human --strict .
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Add shared library to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "_shared" / "python"))

from layer0 import EXIT_ERROR, EXIT_FILE_NOT_FOUND, EXIT_SUCCESS, EXIT_VALIDATION_ERROR
from layer1 import OutputFormat, emit_error, emit_info, glob_files, output

# Try to import yaml
try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False


@dataclass
class Violation:
    """A compliance violation."""

    rule: str
    file: str | None
    message: str
    severity: str
    suggestion: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "rule": self.rule,
            "message": self.message,
            "severity": self.severity,
        }
        if self.file:
            result["file"] = self.file
        if self.suggestion:
            result["suggestion"] = self.suggestion
        return result


@dataclass
class Rule:
    """A compliance rule."""

    name: str
    description: str
    severity: str = "error"
    check_type: str = "custom"
    pattern: str | None = None
    required_files: list[str] = field(default_factory=list)
    forbidden_patterns: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "severity": self.severity,
            "check_type": self.check_type,
        }


@dataclass
class ComplianceReport:
    """Report containing compliance check results."""

    target: str
    is_compliant: bool
    violations: list[Violation] = field(default_factory=list)
    by_rule: dict[str, int] = field(default_factory=dict)
    by_file: dict[str, int] = field(default_factory=dict)
    rules_checked: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "target": self.target,
            "is_compliant": self.is_compliant,
            "summary": {
                "rules_checked": self.rules_checked,
                "total_violations": len(self.violations),
                "errors": sum(1 for v in self.violations if v.severity == "error"),
                "warnings": sum(1 for v in self.violations if v.severity == "warning"),
            },
            "violations": [v.to_dict() for v in self.violations],
            "by_rule": self.by_rule,
            "by_file": {k: v for k, v in self.by_file.items() if v > 0},
        }


# Default compliance rules
DEFAULT_RULES = [
    Rule(
        name="readme_exists",
        description="Project must have a README file",
        severity="error",
        check_type="required_file",
        required_files=["README.md", "README.rst", "README.txt", "README"],
    ),
    Rule(
        name="no_secrets_in_code",
        description="No hardcoded secrets or API keys in code",
        severity="error",
        check_type="forbidden_pattern",
        forbidden_patterns=[
            r'(?i)api[_-]?key\s*=\s*["\'][^"\']{20,}["\']',
            r'(?i)password\s*=\s*["\'][^"\']+["\']',
            r'(?i)secret[_-]?key\s*=\s*["\'][^"\']{20,}["\']',
            r'(?i)aws[_-]?access[_-]?key\s*=\s*["\'][^"\']+["\']',
            r'(?i)private[_-]?key\s*=\s*["\'][^"\']+["\']',
        ],
    ),
    Rule(
        name="no_debug_statements",
        description="No debug print statements in production code",
        severity="warning",
        check_type="forbidden_pattern",
        forbidden_patterns=[
            r'print\s*\(\s*["\']DEBUG',
            r"console\.log\s*\(",
            r"^\s*debugger\s*;",  # JavaScript debugger statement at line start
            r"import\s+pdb",
            r"breakpoint\s*\(\s*\)",
        ],
    ),
    Rule(
        name="proper_gitignore",
        description="Project should have a .gitignore file",
        severity="warning",
        check_type="required_file",
        required_files=[".gitignore"],
    ),
    Rule(
        name="no_todo_in_main",
        description="No TODO/FIXME/HACK comments in main code",
        severity="warning",
        check_type="forbidden_pattern",
        forbidden_patterns=[
            r"#\s*TODO:?\s",
            r"#\s*FIXME:?\s",
            r"#\s*HACK:?\s",
            r"//\s*TODO:?\s",
            r"//\s*FIXME:?\s",
        ],
    ),
    Rule(
        name="license_exists",
        description="Project should have a LICENSE file",
        severity="warning",
        check_type="required_file",
        required_files=["LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"],
    ),
    Rule(
        name="no_hardcoded_paths",
        description="No hardcoded absolute paths",
        severity="warning",
        check_type="forbidden_pattern",
        forbidden_patterns=[
            r'["\']/home/\w+/',
            r'["\']C:\\\\Users\\\\',
            r'["\']/Users/\w+/',
        ],
    ),
]


def load_compliance_rules(path: Path | None) -> list[Rule]:
    """
    Load compliance rules from file or use defaults.

    Args:
        path: Optional path to rules file

    Returns:
        List of Rule objects
    """
    if path is None:
        return DEFAULT_RULES

    if not path.exists():
        emit_info(f"Rules file not found: {path}, using defaults")
        return DEFAULT_RULES

    try:
        content = path.read_text(encoding="utf-8")

        if path.suffix in (".yaml", ".yml"):
            if not HAS_YAML:
                emit_info("PyYAML not installed, using default rules")
                return DEFAULT_RULES
            data = yaml.safe_load(content)
        else:
            data = json.loads(content)

        rules = []
        for rule_data in data.get("rules", []):
            rules.append(
                Rule(
                    name=rule_data.get("name", "unknown"),
                    description=rule_data.get("description", ""),
                    severity=rule_data.get("severity", "error"),
                    check_type=rule_data.get("check_type", "custom"),
                    pattern=rule_data.get("pattern"),
                    required_files=rule_data.get("required_files", []),
                    forbidden_patterns=rule_data.get("forbidden_patterns", []),
                )
            )
        return rules if rules else DEFAULT_RULES

    except Exception as e:
        emit_info(f"Error loading rules: {e}, using defaults")
        return DEFAULT_RULES


def check_required_files(target: Path, rules: list[Rule]) -> list[Violation]:
    """
    Check for required files.

    Args:
        target: Target directory
        rules: List of rules

    Returns:
        List of violations
    """
    violations: list[Violation] = []

    for rule in rules:
        if rule.check_type != "required_file":
            continue

        found = False
        for required_file in rule.required_files:
            if (target / required_file).exists():
                found = True
                break

        if not found:
            violations.append(
                Violation(
                    rule=rule.name,
                    file=None,
                    message=rule.description,
                    severity=rule.severity,
                    suggestion=f"Create one of: {', '.join(rule.required_files)}",
                )
            )

    return violations


def check_file_structure(target: Path, rules: list[Rule]) -> list[Violation]:
    """
    Check file structure compliance.

    Args:
        target: Target directory
        rules: List of rules

    Returns:
        List of violations
    """
    violations: list[Violation] = []

    # Check for common structural issues
    # This is a basic implementation - can be extended

    # Check for tests directory
    test_dirs = ["tests", "test", "spec", "__tests__"]
    any((target / d).is_dir() for d in test_dirs)

    # Check for source organization
    src_dirs = ["src", "lib", "app"]
    has_src_dir = any((target / d).is_dir() for d in src_dirs)

    # Look for code files in root (might indicate poor structure)
    root_code_files = list(target.glob("*.py")) + list(target.glob("*.js"))
    root_code_files = [
        f for f in root_code_files if f.name not in ("setup.py", "conftest.py", "__init__.py")
    ]

    if len(root_code_files) > 5 and not has_src_dir:
        violations.append(
            Violation(
                rule="file_structure",
                file=None,
                message=f"Found {len(root_code_files)} code files in project root",
                severity="warning",
                suggestion="Consider organizing code into src/ or lib/ directory",
            )
        )

    return violations


def check_naming_conventions(target: Path, rules: list[Rule]) -> list[Violation]:
    """
    Check naming convention compliance.

    Args:
        target: Target directory
        rules: List of rules

    Returns:
        List of violations
    """
    violations: list[Violation] = []

    # Check Python file naming (should be snake_case)
    for py_file in glob_files(target, "*.py", recursive=True):
        name = py_file.stem
        # Skip dunder files and test files
        if name.startswith("__") or name.startswith("test_"):
            continue

        # Check for camelCase or PascalCase
        if any(c.isupper() for c in name) and "_" not in name:
            violations.append(
                Violation(
                    rule="naming_convention",
                    file=str(py_file),
                    message=f"Python file '{name}' should use snake_case naming",
                    severity="warning",
                    suggestion=f"Rename to '{_to_snake_case(name)}.py'",
                )
            )

    return violations


def _to_snake_case(name: str) -> str:
    """Convert name to snake_case."""
    result = re.sub(r"([a-z])([A-Z])", r"\1_\2", name)
    return result.lower()


def check_forbidden_patterns(target: Path, rules: list[Rule]) -> list[Violation]:
    """
    Check for forbidden patterns in code.

    Args:
        target: Target directory
        rules: List of rules

    Returns:
        List of violations
    """
    violations: list[Violation] = []

    # File extensions to check
    code_extensions = ["*.py", "*.js", "*.ts", "*.jsx", "*.tsx", "*.go", "*.rb"]

    for rule in rules:
        if rule.check_type != "forbidden_pattern":
            continue

        for ext in code_extensions:
            for file_path in glob_files(target, ext, recursive=True):
                # Skip test files for some rules
                if "test" in str(file_path).lower() and rule.name == "no_todo_in_main":
                    continue

                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue

                for pattern in rule.forbidden_patterns:
                    matches = list(re.finditer(pattern, content))
                    if matches:
                        # Report first match per file per rule
                        match = matches[0]
                        line_num = content[: match.start()].count("\n") + 1
                        violations.append(
                            Violation(
                                rule=rule.name,
                                file=f"{file_path}:{line_num}",
                                message=f"{rule.description} (found: {match.group()[:50]}...)",
                                severity=rule.severity,
                            )
                        )
                        break  # One violation per pattern per file

    return violations


def check_compliance(target: Path, rules: list[Rule], strict: bool) -> ComplianceReport:
    """
    Run all compliance checks.

    Args:
        target: Target directory
        rules: List of rules
        strict: If True, warnings become errors

    Returns:
        ComplianceReport
    """
    report = ComplianceReport(target=str(target), is_compliant=True)
    report.rules_checked = len(rules)

    # Run all checks
    report.violations.extend(check_required_files(target, rules))
    report.violations.extend(check_file_structure(target, rules))
    report.violations.extend(check_naming_conventions(target, rules))
    report.violations.extend(check_forbidden_patterns(target, rules))

    # Upgrade warnings to errors in strict mode
    if strict:
        for violation in report.violations:
            if violation.severity == "warning":
                violation.severity = "error"

    # Count by rule
    for violation in report.violations:
        report.by_rule[violation.rule] = report.by_rule.get(violation.rule, 0) + 1
        if violation.file:
            file_key = violation.file.split(":")[0]
            report.by_file[file_key] = report.by_file.get(file_key, 0) + 1

    # Determine compliance
    errors = sum(1 for v in report.violations if v.severity == "error")
    report.is_compliant = errors == 0

    return report


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check project compliance with conventions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  compliance_checker.py .
  compliance_checker.py --rules custom-rules.yaml src/
  compliance_checker.py -o human --strict .
        """,
    )
    parser.add_argument(
        "target",
        help="Directory to check",
    )
    parser.add_argument(
        "-o",
        "--output",
        choices=["json", "human"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--rules",
        help="Custom rules file (JSON or YAML)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors",
    )

    args = parser.parse_args()

    target = Path(args.target)
    if not target.exists():
        emit_error(EXIT_FILE_NOT_FOUND, f"Target not found: {target}")
        return EXIT_FILE_NOT_FOUND

    if not target.is_dir():
        emit_error(EXIT_ERROR, f"Target is not a directory: {target}")
        return EXIT_ERROR

    rules_path = Path(args.rules) if args.rules else None
    rules = load_compliance_rules(rules_path)

    emit_info(f"Checking compliance of {target}...")

    report = check_compliance(target, rules, args.strict)

    output_format = OutputFormat(args.output)
    output(report.to_dict(), output_format)

    summary = report.to_dict()["summary"]
    status = "PASS" if report.is_compliant else "FAIL"
    emit_info(
        f"Compliance check: {status} ({summary['errors']} errors, {summary['warnings']} warnings)"
    )

    return EXIT_SUCCESS if report.is_compliant else EXIT_VALIDATION_ERROR


if __name__ == "__main__":
    sys.exit(main())
