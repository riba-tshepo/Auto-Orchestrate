#!/usr/bin/env python3
"""Prettier Wrapper - Formats Markdown files consistently.

A wrapper around Prettier that auto-detects installation,
applies consistent markdown settings, and provides helpful
error messages.

Usage:
    python3 prettier_wrapper.py [--check|--write] [--config FILE] FILE_OR_DIR

Examples:
    python3 prettier_wrapper.py README.md
    python3 prettier_wrapper.py --check docs/
    python3 prettier_wrapper.py --write --config .prettierrc docs/

Dependencies: Python >= 3.11 stdlib only.  Prettier (npm) required at runtime.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Shared library imports
# ---------------------------------------------------------------------------

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent.parent / "_shared" / "python"),
)

from layer0 import EXIT_ERROR, EXIT_SUCCESS  # noqa: E402
from layer0.colors import GREEN, RED, RESET, YELLOW  # noqa: E402


# ---------------------------------------------------------------------------
# Logging helpers (coloured stderr, matching the original bash output)
# ---------------------------------------------------------------------------

def _supports_color() -> bool:
    """Return True when stderr is a TTY that likely supports ANSI."""
    return hasattr(sys.stderr, "isatty") and sys.stderr.isatty()


_USE_COLOR = _supports_color()


def _c(code: str) -> str:
    return code if _USE_COLOR else ""


def log_info(msg: str) -> None:
    print(f"{_c(GREEN)}INFO:{_c(RESET)} {msg}", file=sys.stderr)


def log_warning(msg: str) -> None:
    print(f"{_c(YELLOW)}WARN:{_c(RESET)} {msg}", file=sys.stderr)


def log_error(msg: str) -> None:
    print(f"{_c(RED)}ERROR:{_c(RESET)} {msg}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Prettier detection
# ---------------------------------------------------------------------------

def find_prettier() -> list[str] | None:
    """Locate a usable Prettier command.

    Search order:
      1. Local ``node_modules/.bin/prettier``
      2. Globally installed ``prettier``
      3. ``npx prettier`` (downloads on demand)

    Returns:
        A command list suitable for :func:`subprocess.run`, or *None* when
        Prettier cannot be found.
    """
    local_bin = Path("node_modules/.bin/prettier")
    if local_bin.is_file():
        return [str(local_bin)]

    global_bin = shutil.which("prettier")
    if global_bin:
        return [global_bin]

    npx_bin = shutil.which("npx")
    if npx_bin:
        return [npx_bin, "prettier"]

    return None


# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------

_DEFAULT_CONFIG: dict[str, object] = {
    "printWidth": 80,
    "proseWrap": "always",
    "tabWidth": 2,
    "useTabs": False,
    "singleQuote": False,
    "trailingComma": "none",
}

_CONFIG_CANDIDATES: tuple[str, ...] = (
    ".prettierrc",
    ".prettierrc.json",
    ".prettierrc.yaml",
    ".prettierrc.yml",
    "prettier.config.js",
)


def find_existing_config() -> str | None:
    """Return the path to the first existing Prettier config, or *None*."""
    for name in _CONFIG_CANDIDATES:
        if Path(name).is_file():
            return name
    return None


# ---------------------------------------------------------------------------
# Prettier execution
# ---------------------------------------------------------------------------

def run_prettier(
    cmd: list[str],
    config_path: str,
    mode: str,
    target: str,
) -> bool:
    """Invoke Prettier and return *True* on success.

    Args:
        cmd: Base command list (e.g. ``["prettier"]``).
        config_path: Path to the config file.
        mode: ``"check"`` or ``"write"``.
        target: File or glob pattern to format.
    """
    args = list(cmd)
    args.extend(["--config", config_path])
    args.append("--check" if mode == "check" else "--write")
    args.append(target)

    result = subprocess.run(args, capture_output=False)
    return result.returncode == 0


def format_target(
    target: str,
    cmd: list[str],
    config_path: str,
    mode: str,
) -> bool:
    """Format (or check) a single file or directory of Markdown files.

    For directories the glob ``<dir>/**/*.md`` is passed to Prettier so it
    discovers files recursively.
    """
    target_path = Path(target)

    if target_path.is_file():
        actual_target = str(target_path)
    elif target_path.is_dir():
        actual_target = str(target_path / "**" / "*.md")
    else:
        log_error(f"Target not found: {target}")
        return False

    ok = run_prettier(cmd, config_path, mode, actual_target)

    if mode == "check":
        if ok:
            if target_path.is_file():
                log_info(f"File is properly formatted: {target}")
            else:
                log_info(f"All files in {target} are properly formatted")
        else:
            if target_path.is_file():
                log_warning(f"File needs formatting: {target}")
            else:
                log_warning(f"Some files in {target} need formatting")
    else:
        if ok:
            if target_path.is_file():
                log_info(f"Formatted: {target}")
            else:
                log_info(f"Formatted all Markdown files in: {target}")
        else:
            if target_path.is_file():
                log_error(f"Failed to format: {target}")
            else:
                log_warning("Some files could not be formatted")

    return ok


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        description="Format Markdown files using Prettier.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Default Markdown settings (when no config provided):\n"
            "    - Print width: 80\n"
            "    - Prose wrap: always\n"
            "    - Tab width: 2"
        ),
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--check",
        action="store_const",
        const="check",
        dest="mode",
        help="Check if files are formatted (don't modify)",
    )
    group.add_argument(
        "--write",
        action="store_const",
        const="write",
        dest="mode",
        help="Format files in place (default)",
    )
    parser.set_defaults(mode="write")

    parser.add_argument(
        "--config",
        metavar="FILE",
        help="Use custom Prettier config file",
    )
    parser.add_argument(
        "target",
        help="File or directory to format",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)

    # --- Locate Prettier ---------------------------------------------------
    cmd = find_prettier()
    if cmd is None:
        log_error("Prettier is not installed")
        log_info("Install Prettier with one of:")
        log_info("  npm install --save-dev prettier")
        log_info("  npm install -g prettier")
        log_info("  Or ensure npx is available")
        return EXIT_ERROR

    log_info(f"Using Prettier: {' '.join(cmd)}")

    # --- Validate target ----------------------------------------------------
    if not Path(args.target).exists():
        log_error(f"Target not found: {args.target}")
        return EXIT_ERROR

    # --- Resolve config -----------------------------------------------------
    temp_config_path: str | None = None
    config_path: str

    try:
        if args.config:
            if not Path(args.config).is_file():
                log_error(f"Config file not found: {args.config}")
                return EXIT_ERROR
            config_path = args.config
            log_info(f"Using config: {config_path}")
        else:
            existing = find_existing_config()
            if existing:
                config_path = existing
                log_info(f"Using existing config: {config_path}")
            else:
                fd, temp_config_path = tempfile.mkstemp(suffix=".json")
                with os.fdopen(fd, "w") as fh:
                    json.dump(_DEFAULT_CONFIG, fh, indent=2)
                config_path = temp_config_path
                log_info("Using default Markdown config")

        # --- Run formatting -------------------------------------------------
        ok = format_target(args.target, cmd, config_path, args.mode)
        return EXIT_SUCCESS if ok else EXIT_ERROR

    finally:
        if temp_config_path and Path(temp_config_path).exists():
            os.unlink(temp_config_path)


if __name__ == "__main__":
    sys.exit(main())
