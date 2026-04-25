#!/usr/bin/env python3
"""
Task structure validator.

Validates task definitions before execution to ensure they have all
required fields and proper structure.

Usage:
    python task_validator.py <task_id>
    python task_validator.py --json <task_json_string>
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "_shared" / "python"))
from layer0 import EXIT_SUCCESS, EXIT_ERROR, EXIT_INVALID_ARGS
from layer1 import emit_error, emit_warning, emit_info


class TaskValidator:
    """Validates task structure and required fields."""

    REQUIRED_FIELDS = ["id", "description", "status"]

    OPTIONAL_FIELDS = [
        "title",
        "assignee",
        "priority",
        "epic",
        "blockedBy",
        "blocking",
        "dependencies",
        "tags",
        "created_at",
        "updated_at",
        "due_date",
        "estimated_hours",
        "actual_hours",
        "metadata",
    ]

    VALID_STATUSES = ["pending", "in_progress", "blocked", "completed", "cancelled"]

    VALID_PRIORITIES = ["critical", "high", "medium", "low"]

    def __init__(self, task_data: dict[str, Any]):
        self.task = task_data
        self.issues: list[tuple[str, str]] = []  # (severity, message)

    def check_required_fields(self):
        """Check for presence of required fields."""
        for field in self.REQUIRED_FIELDS:
            if field not in self.task:
                self.issues.append(("CRITICAL", f"Missing required field: {field}"))

    def check_task_id(self):
        """Validate task ID format."""
        if "id" not in self.task:
            return  # Already reported as missing

        task_id = str(self.task["id"])

        # Check if ID is empty
        if not task_id or task_id.strip() == "":
            self.issues.append(("CRITICAL", "Task ID is empty"))
            return

        # Check for common ID patterns (numeric, hierarchical, etc.)
        # Examples: "1", "2.3", "TASK-123", "epic-1.task-2"
        if len(task_id) > 100:
            self.issues.append(
                ("WARNING", f"Task ID is unusually long ({len(task_id)} characters)")
            )

    def check_description(self):
        """Validate task description."""
        if "description" not in self.task:
            return

        desc = self.task["description"]

        if not desc or (isinstance(desc, str) and desc.strip() == ""):
            self.issues.append(("CRITICAL", "Task description is empty"))
            return

        # Check for very brief descriptions
        if isinstance(desc, str) and len(desc.strip()) < 10:
            self.issues.append(("WARNING", "Task description is very brief (add more context)"))

        # Check for vague descriptions
        vague_terms = ["fix", "update", "change", "improve"]
        if isinstance(desc, str):
            desc_lower = desc.lower()
            if any(term in desc_lower for term in vague_terms) and len(desc) < 50:
                self.issues.append(
                    ("INFO", "Description may be too vague (be specific about what to do)")
                )

    def check_status(self):
        """Validate task status."""
        if "status" not in self.task:
            return

        status = self.task["status"]

        if status not in self.VALID_STATUSES:
            self.issues.append(
                (
                    "WARNING",
                    f'Invalid status "{status}" (expected: {", ".join(self.VALID_STATUSES)})',
                )
            )

    def check_priority(self):
        """Validate task priority if present."""
        if "priority" not in self.task:
            return

        priority = self.task["priority"]

        if priority and priority not in self.VALID_PRIORITIES:
            self.issues.append(
                (
                    "WARNING",
                    f'Invalid priority "{priority}" (expected: {", ".join(self.VALID_PRIORITIES)})',
                )
            )

    def check_dependencies(self):
        """Validate task dependencies structure."""
        for dep_field in ["blockedBy", "blocking", "dependencies"]:
            if dep_field not in self.task:
                continue

            value = self.task[dep_field]

            # Should be a list
            if not isinstance(value, list):
                self.issues.append(
                    ("WARNING", f'Field "{dep_field}" should be a list, got {type(value).__name__}')
                )
                continue

            # Check for empty dependency lists (informational)
            if len(value) == 0 and dep_field == "blockedBy":
                # This is fine, not blocked
                pass

    def check_unknown_fields(self):
        """Check for unknown fields (informational)."""
        known_fields = set(self.REQUIRED_FIELDS + self.OPTIONAL_FIELDS)

        for field in self.task:
            if field not in known_fields:
                self.issues.append(("INFO", f"Unknown field: {field}"))

    def validate(self) -> bool:
        """Run all validation checks."""
        self.check_required_fields()
        self.check_task_id()
        self.check_description()
        self.check_status()
        self.check_priority()
        self.check_dependencies()
        self.check_unknown_fields()

        return True

    def print_report(self):
        """Print validation report."""
        severity_order = {"CRITICAL": 0, "WARNING": 1, "INFO": 2}
        sorted_issues = sorted(self.issues, key=lambda x: severity_order[x[0]])

        task_id = self.task.get("id", "unknown")

        if not sorted_issues:
            print(f"✅ Task {task_id}: Valid!")
            return

        print(f"\nTask {task_id} — Found {len(sorted_issues)} issue(s):\n")

        for severity, message in sorted_issues:
            icon = {"CRITICAL": "🔴", "WARNING": "🟡", "INFO": "ℹ️"}[severity]
            print(f"  {icon} [{severity}] {message}")

    def has_critical_issues(self) -> bool:
        """Check if any critical issues exist."""
        return any(sev == "CRITICAL" for sev, _ in self.issues)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate task structure")
    parser.add_argument("task_id", nargs="?", help="Task ID to validate (reads from task system)")
    parser.add_argument("--json", type=str, help="JSON string containing task data")
    args = parser.parse_args()

    # Get task data
    if args.json:
        try:
            task_data = json.loads(args.json)
        except json.JSONDecodeError as e:
            emit_error(f"Invalid JSON: {e}")
            sys.exit(EXIT_ERROR)
    elif args.task_id:
        # In a real implementation, would fetch from task system
        # For now, create minimal task structure
        task_data = {
            "id": args.task_id,
            "description": "[Would be fetched from task system]",
            "status": "pending",
        }
        print(f"Note: Using minimal task structure for {args.task_id}")
        print("In production, would fetch from task system.\n")
    else:
        parser.print_help()
        sys.exit(EXIT_INVALID_ARGS)

    validator = TaskValidator(task_data)
    validator.validate()
    validator.print_report()

    sys.exit(EXIT_ERROR if validator.has_critical_issues() else EXIT_SUCCESS)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(EXIT_ERROR)
    except Exception as exc:
        emit_error(f"Unexpected error: {exc}")
        sys.exit(EXIT_ERROR)
