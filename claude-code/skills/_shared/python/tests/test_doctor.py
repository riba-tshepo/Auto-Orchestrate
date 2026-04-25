"""
Tests for layer3.doctor module.

Tests diagnostic and system health check utilities.
"""

from pathlib import Path

from layer3.doctor import (
    DiagnosticResult,
    SystemHealth,
    check_claude_directory,
    check_environment,
    check_python_version,
    diagnose_system,
)


def test_check_python_version_current():
    """Test Python version check with current version."""
    # Check against an older version that current should satisfy
    result = check_python_version(min_version=(3, 6))

    assert isinstance(result, DiagnosticResult)
    assert result.component == "Python Version"
    # Current version should be >= 3.6
    assert result.healthy is True


def test_check_python_version_too_high():
    """Test Python version check with impossible requirement."""
    # Check against a future version
    result = check_python_version(min_version=(99, 99))

    assert result.healthy is False
    assert len(result.issues) > 0
    assert len(result.suggestions) > 0


def test_check_claude_directory():
    """Test Claude directory check."""
    result = check_claude_directory()

    assert isinstance(result, DiagnosticResult)
    assert result.component == "Claude Directory"
    # Result depends on whether ~/.claude exists
    assert isinstance(result.healthy, bool)


def test_diagnose_system():
    """Test full system diagnostics."""
    health = diagnose_system()

    assert isinstance(health, SystemHealth)
    assert isinstance(health.healthy, bool)
    assert isinstance(health.results, list)
    assert len(health.results) > 0
    assert isinstance(health.python_version, str)
    assert isinstance(health.claude_dir, Path)


def test_diagnose_system_has_required_checks():
    """Test that diagnose_system() runs all required checks."""
    health = diagnose_system()

    components = [r.component for r in health.results]

    assert "Python Version" in components
    assert "Claude Directory" in components
    assert "Manifest" in components


def test_check_environment():
    """Test quick environment check."""
    result = check_environment()

    assert isinstance(result, DiagnosticResult)
    assert result.component == "Environment"
    assert isinstance(result.healthy, bool)


def test_diagnostic_result_structure():
    """Test DiagnosticResult structure."""
    result = DiagnosticResult(
        healthy=True, component="Test Component", message="All good", issues=[], suggestions=[]
    )

    assert result.healthy is True
    assert result.component == "Test Component"
    assert len(result.issues) == 0
