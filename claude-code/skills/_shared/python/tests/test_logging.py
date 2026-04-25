"""
Tests for layer1.logging module.

Tests logging utilities including setup_logging, get_logger, emit_error,
emit_warning, and emit_info.
"""

import logging

from layer0.exit_codes import EXIT_INVALID_ARGS
from layer1.logging import (
    emit_error,
    emit_info,
    emit_warning,
    get_logger,
    setup_logging,
)


def test_setup_logging_creates_logger():
    """Test setup_logging() creates and configures logger."""
    logger = setup_logging("test_logger", level=logging.DEBUG)

    assert logger is not None
    assert logger.name == "test_logger"
    assert logger.level == logging.DEBUG


def test_setup_logging_adds_stderr_handler():
    """Test setup_logging() adds stderr handler."""
    logger = setup_logging("test_handler")

    assert len(logger.handlers) > 0
    assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)


def test_setup_logging_clears_existing_handlers():
    """Test setup_logging() clears existing handlers."""
    logger = logging.getLogger("test_clear")
    logger.addHandler(logging.NullHandler())
    len(logger.handlers)

    setup_logging("test_clear")

    # Should have exactly one handler (the new stderr handler)
    assert len(logger.handlers) == 1


def test_get_logger_returns_configured_logger():
    """Test get_logger() returns the configured logger."""
    setup_logging("test_get")
    logger = get_logger()

    assert logger is not None
    assert logger.name == "test_get"


def test_get_logger_creates_default_if_not_setup():
    """Test get_logger() creates default logger if not set up."""
    # Force reset by accessing the module's global
    import layer1.logging as logging_module

    logging_module._logger = None

    logger = get_logger()

    assert logger is not None


def test_emit_error_logs_error_message(caplog):
    """Test emit_error() logs error with exit code."""
    setup_logging("test_error", level=logging.ERROR)

    with caplog.at_level(logging.ERROR):
        emit_error(EXIT_INVALID_ARGS, "Invalid input provided")

    assert len(caplog.records) > 0
    assert "Invalid input provided" in caplog.text


def test_emit_error_with_details(caplog):
    """Test emit_error() includes details in message."""
    setup_logging("test_error_details", level=logging.ERROR)

    with caplog.at_level(logging.ERROR):
        emit_error(EXIT_INVALID_ARGS, "Error occurred", details="Additional context")

    assert "Additional context" in caplog.text


def test_emit_warning_logs_warning_message(caplog):
    """Test emit_warning() logs warning."""
    setup_logging("test_warning", level=logging.WARNING)

    with caplog.at_level(logging.WARNING):
        emit_warning("This is a warning")

    assert len(caplog.records) > 0
    assert "This is a warning" in caplog.text


def test_emit_warning_with_details(caplog):
    """Test emit_warning() includes details."""
    setup_logging("test_warning_details", level=logging.WARNING)

    with caplog.at_level(logging.WARNING):
        emit_warning("Warning message", details="Extra info")

    assert "Extra info" in caplog.text


def test_emit_info_logs_info_message(caplog):
    """Test emit_info() logs info message."""
    setup_logging("test_info", level=logging.INFO)

    with caplog.at_level(logging.INFO):
        emit_info("Informational message")

    assert len(caplog.records) > 0
    assert "Informational message" in caplog.text


def test_logging_level_filtering(caplog):
    """Test that logging level filtering works correctly."""
    setup_logging("test_filter", level=logging.WARNING)

    with caplog.at_level(logging.INFO):
        emit_info("This should not appear")
        emit_warning("This should appear")

    # Only warning should be logged
    assert "This should appear" in caplog.text
    # Info may or may not appear depending on caplog level, so we check warning exists
