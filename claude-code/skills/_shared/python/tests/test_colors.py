"""
Tests for layer0.colors module.

Tests ANSI color code utilities including colorize() and strip_colors().
"""

from layer0.colors import (
    BOLD,
    GREEN,
    RED,
    RESET,
    YELLOW,
    colorize,
    strip_colors,
)


def test_colorize_adds_color_codes():
    """Test that colorize() wraps text with ANSI codes."""
    result = colorize("Hello", GREEN)
    assert result == f"{GREEN}Hello{RESET}"
    assert result.startswith(GREEN)
    assert result.endswith(RESET)


def test_colorize_with_different_colors():
    """Test colorize() with multiple color codes."""
    red_text = colorize("Error", RED)
    yellow_text = colorize("Warning", YELLOW)
    bold_text = colorize("Important", BOLD)

    assert RED in red_text
    assert YELLOW in yellow_text
    assert BOLD in bold_text


def test_colorize_empty_string():
    """Test colorize() with empty string."""
    result = colorize("", GREEN)
    assert result == f"{GREEN}{RESET}"


def test_strip_colors_removes_ansi_codes():
    """Test that strip_colors() removes ANSI escape sequences."""
    colored = colorize("Hello", RED)
    stripped = strip_colors(colored)
    assert stripped == "Hello"
    assert RESET not in stripped
    assert RED not in stripped


def test_strip_colors_plain_text():
    """Test strip_colors() with text that has no ANSI codes."""
    plain = "Plain text"
    result = strip_colors(plain)
    assert result == plain


def test_strip_colors_multiple_codes():
    """Test strip_colors() with multiple ANSI codes."""
    text = f"{RED}Red{RESET} {GREEN}Green{RESET} {BOLD}Bold{RESET}"
    stripped = strip_colors(text)
    assert stripped == "Red Green Bold"
    assert RESET not in stripped
