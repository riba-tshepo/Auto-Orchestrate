"""
Logging utilities for CLI scripts.

Provides structured logging with consistent formatting.
All output goes to stderr to keep stdout clean for JSON output.
"""

import logging
import sys

from layer0.exit_codes import exit_code_to_message

_logger: logging.Logger | None = None


def setup_logging(name: str = "script", level: int = logging.INFO) -> logging.Logger:
    """
    Set up logging with consistent formatting.

    Args:
        name: Logger name (typically script name)
        level: Logging level (default INFO)

    Returns:
        Configured logger instance
    """
    global _logger

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers
    logger.handlers.clear()

    # Create stderr handler
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)

    # Create formatter
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    _logger = logger

    return logger


def get_logger() -> logging.Logger:
    """Get the configured logger, or create default if not set up."""
    global _logger
    if _logger is None:
        _logger = setup_logging()
    return _logger


def emit_error(exit_code: int, message: str, details: str | None = None) -> None:
    """
    Emit an error message to stderr.

    Args:
        exit_code: The exit code associated with this error
        message: The error message
        details: Optional additional details
    """
    logger = get_logger()
    code_msg = exit_code_to_message(exit_code)
    full_msg = f"[{code_msg}] {message}"
    if details:
        full_msg += f"\n  Details: {details}"
    logger.error(full_msg)


def emit_warning(message: str, details: str | None = None) -> None:
    """
    Emit a warning message to stderr.

    Args:
        message: The warning message
        details: Optional additional details
    """
    logger = get_logger()
    full_msg = message
    if details:
        full_msg += f"\n  Details: {details}"
    logger.warning(full_msg)


def emit_info(message: str) -> None:
    """
    Emit an info message to stderr.

    Args:
        message: The info message
    """
    logger = get_logger()
    logger.info(message)
