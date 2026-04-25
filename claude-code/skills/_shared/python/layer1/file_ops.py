"""
File operation utilities for CLI scripts.

Provides safe file operations with proper error handling.
"""

import fnmatch
import os
import shutil
import tempfile
from collections.abc import Iterator
from pathlib import Path


def file_exists(path: str | Path) -> bool:
    """Check if file exists and is a file."""
    return Path(path).is_file()


def is_directory(path: str | Path) -> bool:
    """Check if path exists and is a directory."""
    return Path(path).is_dir()


def read_file(path: str | Path, encoding: str = "utf-8") -> str:
    """
    Read file contents.

    Args:
        path: Path to file
        encoding: File encoding (default UTF-8)

    Returns:
        File contents as string

    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If file can't be read
    """
    return Path(path).read_text(encoding=encoding)


def write_file(
    path: str | Path, content: str, encoding: str = "utf-8", create_parents: bool = True
) -> None:
    """
    Write content to file.

    Args:
        path: Path to file
        content: Content to write
        encoding: File encoding (default UTF-8)
        create_parents: Create parent directories if needed

    Raises:
        PermissionError: If file can't be written
    """
    path = Path(path)
    if create_parents:
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding=encoding)


def safe_write(
    path: str | Path, content: str, encoding: str = "utf-8", backup: bool = False
) -> Path | None:
    """
    Atomically write content to file.

    Uses temp file + rename pattern for atomic writes.
    Optionally creates backup of existing file.

    Args:
        path: Path to file
        content: Content to write
        encoding: File encoding (default UTF-8)
        backup: Create backup of existing file

    Returns:
        Path to backup file if backup=True and file existed, else None

    Raises:
        PermissionError: If file can't be written
    """
    path = Path(path)
    backup_path = None

    # Create parent directories
    path.parent.mkdir(parents=True, exist_ok=True)

    # Create backup if requested and file exists
    if backup and path.exists():
        backup_path = path.with_suffix(path.suffix + ".bak")
        shutil.copy2(path, backup_path)

    # Write to temp file then rename
    fd, temp_path = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding=encoding) as f:
            f.write(content)
        os.replace(temp_path, path)
    except Exception:
        # Clean up temp file on error
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise

    return backup_path


def ensure_directory(path: str | Path) -> Path:
    """
    Ensure directory exists, creating if necessary.

    Args:
        path: Directory path

    Returns:
        Path object for directory

    Raises:
        PermissionError: If directory can't be created
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def glob_files(
    path: str | Path, pattern: str = "*", recursive: bool = True, include_hidden: bool = False
) -> Iterator[Path]:
    """
    Find files matching glob pattern.

    Args:
        path: Base directory
        pattern: Glob pattern (e.g., "*.py", "**/*.js")
        recursive: Search subdirectories
        include_hidden: Include hidden files (starting with .)

    Yields:
        Matching file paths
    """
    path = Path(path)

    if recursive and "**" not in pattern:
        pattern = f"**/{pattern}"

    for file_path in path.glob(pattern):
        if file_path.is_file() and (include_hidden or not file_path.name.startswith(".")):
            yield file_path


def match_globs(path: str | Path, include: list[str], exclude: list[str]) -> bool:
    """
    Check if path matches include patterns and doesn't match exclude patterns.

    Args:
        path: Path to check
        include: List of include glob patterns
        exclude: List of exclude glob patterns

    Returns:
        True if path should be included
    """
    path_str = str(path)

    # Must match at least one include pattern
    included = any(fnmatch.fnmatch(path_str, p) for p in include) if include else True

    # Must not match any exclude pattern
    excluded = any(fnmatch.fnmatch(path_str, p) for p in exclude) if exclude else False

    return included and not excluded
