"""
Color output utilities for terminal output.

This module provides ANSI color codes and utilities for colorizing terminal text.
Used across CLI scripts for consistent colored output.

Example:
    from layer0.colors import colorize, GREEN, RED, BOLD
    print(colorize("Success!", GREEN))
    print(colorize("Error!", RED))
    print(colorize("Important", BOLD))
"""

# ANSI color codes
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"

# Text styles
BOLD = "\033[1m"
DIM = "\033[2m"
UNDERLINE = "\033[4m"

# Reset
RESET = "\033[0m"


def colorize(text: str, color: str) -> str:
    """Apply ANSI color code to text.

    Args:
        text: The text to colorize.
        color: ANSI color code (e.g., RED, GREEN, BOLD).

    Returns:
        Colorized text string with reset code appended.

    Example:
        >>> colorize("Hello", GREEN)
        '\\033[92mHello\\033[0m'
    """
    return f"{color}{text}{RESET}"


def strip_colors(text: str) -> str:
    """Remove ANSI color codes from text.

    Args:
        text: Text potentially containing ANSI codes.

    Returns:
        Text with all ANSI codes removed.
    """
    import re

    ansi_escape = re.compile(r"\033\[[0-9;]*m")
    return ansi_escape.sub("", text)
