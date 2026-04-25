"""
Tests for layer0.exit_codes module.

Tests exit code constants and message conversion.
"""

from layer0.exit_codes import (
    EXIT_ERROR,
    EXIT_FILE_NOT_FOUND,
    EXIT_SUCCESS,
    EXIT_VALIDATION_ERROR,
    exit_code_to_message,
)


def test_exit_success_is_zero():
    """Test that EXIT_SUCCESS is 0."""
    assert EXIT_SUCCESS == 0


def test_exit_codes_are_positive():
    """Test that error exit codes are positive integers."""
    assert EXIT_ERROR > 0
    assert EXIT_FILE_NOT_FOUND > 0
    assert EXIT_VALIDATION_ERROR > 0


def test_exit_code_to_message_success():
    """Test message for success code."""
    assert exit_code_to_message(EXIT_SUCCESS) == "Success"


def test_exit_code_to_message_known_codes():
    """Test messages for known exit codes."""
    assert "error" in exit_code_to_message(EXIT_ERROR).lower()
    assert "not found" in exit_code_to_message(EXIT_FILE_NOT_FOUND).lower()
    assert "validation" in exit_code_to_message(EXIT_VALIDATION_ERROR).lower()


def test_exit_code_to_message_unknown():
    """Test message for unknown exit code."""
    result = exit_code_to_message(999)
    assert "Unknown" in result or "999" in result
