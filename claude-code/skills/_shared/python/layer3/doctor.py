"""
Diagnostic utilities for system health checks.

This module provides diagnostic functions for validating the Claude Code
environment, checking dependencies, and troubleshooting common issues.

Example:
    from layer3.doctor import check_environment, diagnose_system

    result = check_environment()
    if not result.healthy:
        print(result.issues)
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

from layer0.constants import CLAUDE_DIR, DEFAULT_MANIFEST_PATH, DEFAULT_TASKS_FILE
from layer1.config import load_config


@dataclass
class DiagnosticResult:
    """Result of a diagnostic check.

    Attributes:
        healthy: Whether the check passed.
        component: Component that was checked.
        message: Human-readable status message.
        issues: List of issues found (empty if healthy).
        suggestions: List of suggested fixes.
    """

    healthy: bool
    component: str
    message: str
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)


@dataclass
class SystemHealth:
    """Overall system health status.

    Attributes:
        healthy: Whether all checks passed.
        results: List of individual diagnostic results.
        python_version: Python version string.
        claude_dir: Path to Claude directory.
    """

    healthy: bool
    results: list[DiagnosticResult]
    python_version: str
    claude_dir: Path


def check_python_version(min_version: tuple[int, int] = (3, 10)) -> DiagnosticResult:
    """Check if Python version meets minimum requirement.

    Args:
        min_version: Minimum required Python version as (major, minor). Defaults to (3, 10).

    Returns:
        DiagnosticResult for Python version check.

    Example:
        >>> result = check_python_version()
        >>> print(result.healthy)
        True
    """
    current = sys.version_info[:2]
    required = min_version

    if current >= required:
        return DiagnosticResult(
            healthy=True,
            component="Python Version",
            message=f"Python {current[0]}.{current[1]} meets requirement >={required[0]}.{required[1]}",
        )
    else:
        return DiagnosticResult(
            healthy=False,
            component="Python Version",
            message=f"Python {current[0]}.{current[1]} is below requirement {required[0]}.{required[1]}",
            issues=[
                f"Current: {current[0]}.{current[1]}",
                f"Required: >={required[0]}.{required[1]}",
            ],
            suggestions=["Upgrade Python to 3.10 or later"],
        )


def check_claude_directory() -> DiagnosticResult:
    """Check if Claude directory exists and is accessible.

    Returns:
        DiagnosticResult for Claude directory check.
    """
    if CLAUDE_DIR.exists() and CLAUDE_DIR.is_dir():
        return DiagnosticResult(
            healthy=True,
            component="Claude Directory",
            message=f"Claude directory found at {CLAUDE_DIR}",
        )
    else:
        return DiagnosticResult(
            healthy=False,
            component="Claude Directory",
            message=f"Claude directory not found: {CLAUDE_DIR}",
            issues=[f"Directory does not exist: {CLAUDE_DIR}"],
            suggestions=[f"Create directory: mkdir -p {CLAUDE_DIR}"],
        )


def check_manifest() -> DiagnosticResult:
    """Check if manifest.json exists and is valid JSON.

    Returns:
        DiagnosticResult for manifest check.
    """
    if not DEFAULT_MANIFEST_PATH.exists():
        return DiagnosticResult(
            healthy=False,
            component="Manifest",
            message=f"Manifest file not found: {DEFAULT_MANIFEST_PATH}",
            issues=["manifest.json does not exist"],
            suggestions=["Run initialization to create manifest.json"],
        )

    try:
        manifest = load_config(DEFAULT_MANIFEST_PATH)
        agent_count = len(manifest.get("agents", []))
        skill_count = len(manifest.get("skills", []))

        return DiagnosticResult(
            healthy=True,
            component="Manifest",
            message=f"Manifest valid: {agent_count} agents, {skill_count} skills",
        )
    except Exception as e:
        return DiagnosticResult(
            healthy=False,
            component="Manifest",
            message="Manifest file is invalid",
            issues=[f"JSON parse error: {str(e)}"],
            suggestions=["Restore manifest.json from backup", "Re-initialize system"],
        )


def check_tasks_file() -> DiagnosticResult:
    """Check if tasks.json exists and is valid JSON.

    Returns:
        DiagnosticResult for tasks file check.
    """
    if not DEFAULT_TASKS_FILE.exists():
        return DiagnosticResult(
            healthy=True,  # Optional file
            component="Tasks File",
            message="No tasks file found (this is normal for new installations)",
        )

    try:
        tasks = load_config(DEFAULT_TASKS_FILE)
        task_count = len(tasks.get("tasks", []))

        return DiagnosticResult(
            healthy=True,
            component="Tasks File",
            message=f"Tasks file valid: {task_count} tasks",
        )
    except Exception as e:
        return DiagnosticResult(
            healthy=False,
            component="Tasks File",
            message="Tasks file is invalid",
            issues=[f"JSON parse error: {str(e)}"],
            suggestions=["Restore tasks.json from backup", "Remove corrupted file"],
        )


def diagnose_system() -> SystemHealth:
    """Run all diagnostic checks and return system health status.

    Returns:
        SystemHealth with overall status and individual check results.

    Example:
        >>> health = diagnose_system()
        >>> if not health.healthy:
        ...     for result in health.results:
        ...         if not result.healthy:
        ...             print(f"{result.component}: {result.message}")
    """
    results = [
        check_python_version(),
        check_claude_directory(),
        check_manifest(),
        check_tasks_file(),
    ]

    all_healthy = all(r.healthy for r in results)

    return SystemHealth(
        healthy=all_healthy,
        results=results,
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        claude_dir=CLAUDE_DIR,
    )


def check_environment() -> DiagnosticResult:
    """Quick environment health check.

    Returns:
        DiagnosticResult summarizing environment health.
    """
    health = diagnose_system()

    if health.healthy:
        return DiagnosticResult(
            healthy=True,
            component="Environment",
            message="All checks passed",
        )
    else:
        failed = [r for r in health.results if not r.healthy]
        return DiagnosticResult(
            healthy=False,
            component="Environment",
            message=f"{len(failed)} check(s) failed",
            issues=[f"{r.component}: {r.message}" for r in failed],
            suggestions=sum([r.suggestions for r in failed], []),
        )
