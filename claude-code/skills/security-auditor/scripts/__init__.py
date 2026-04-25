"""
Security Auditor scripts.

Scripts for scanning vulnerabilities, detecting patterns, and mapping severity.

Available scripts:
- vulnerability_scanner: Scan dependencies for known CVEs
- pattern_detector: Detect security anti-patterns in code
- severity_mapper: Map findings to CVSS scores and priorities
"""

from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent

__all__ = [
    "vulnerability_scanner",
    "pattern_detector",
    "severity_mapper",
]
