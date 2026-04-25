"""
Tests for layer1.file_ops module.

Tests file operation utilities including read_file, write_file, safe_write,
ensure_directory, glob_files, and match_globs.
"""

from pathlib import Path

import pytest

from layer1.file_ops import (
    ensure_directory,
    file_exists,
    glob_files,
    is_directory,
    match_globs,
    read_file,
    safe_write,
    write_file,
)


def test_file_exists_with_existing_file(tmp_path):
    """Test file_exists() with an existing file."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")
    assert file_exists(test_file) is True


def test_file_exists_with_nonexistent_file(tmp_path):
    """Test file_exists() with a nonexistent file."""
    test_file = tmp_path / "nonexistent.txt"
    assert file_exists(test_file) is False


def test_file_exists_with_directory(tmp_path):
    """Test file_exists() with a directory (should return False)."""
    test_dir = tmp_path / "testdir"
    test_dir.mkdir()
    assert file_exists(test_dir) is False


def test_is_directory_with_directory(tmp_path):
    """Test is_directory() with an existing directory."""
    test_dir = tmp_path / "testdir"
    test_dir.mkdir()
    assert is_directory(test_dir) is True


def test_is_directory_with_file(tmp_path):
    """Test is_directory() with a file (should return False)."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")
    assert is_directory(test_file) is False


def test_read_file_success(tmp_path):
    """Test read_file() reads file contents correctly."""
    test_file = tmp_path / "test.txt"
    content = "Hello, world!"
    test_file.write_text(content)

    result = read_file(test_file)
    assert result == content


def test_read_file_nonexistent_raises(tmp_path):
    """Test read_file() raises FileNotFoundError for nonexistent file."""
    test_file = tmp_path / "nonexistent.txt"

    with pytest.raises(FileNotFoundError):
        read_file(test_file)


def test_write_file_creates_new_file(tmp_path):
    """Test write_file() creates a new file with content."""
    test_file = tmp_path / "test.txt"
    content = "Test content"

    write_file(test_file, content)

    assert test_file.exists()
    assert test_file.read_text() == content


def test_write_file_creates_parent_directories(tmp_path):
    """Test write_file() creates parent directories when needed."""
    test_file = tmp_path / "subdir" / "deep" / "test.txt"
    content = "Content"

    write_file(test_file, content, create_parents=True)

    assert test_file.exists()
    assert test_file.read_text() == content


def test_safe_write_atomic_write(tmp_path):
    """Test safe_write() performs atomic write."""
    test_file = tmp_path / "test.txt"
    content = "New content"

    backup_path = safe_write(test_file, content)

    assert test_file.exists()
    assert test_file.read_text() == content
    assert backup_path is None  # No backup for new file


def test_safe_write_with_backup(tmp_path):
    """Test safe_write() creates backup of existing file."""
    test_file = tmp_path / "test.txt"
    original_content = "Original"
    new_content = "New"

    test_file.write_text(original_content)
    backup_path = safe_write(test_file, new_content, backup=True)

    assert test_file.read_text() == new_content
    assert backup_path is not None
    assert Path(backup_path).read_text() == original_content


def test_ensure_directory_creates_new(tmp_path):
    """Test ensure_directory() creates a new directory."""
    test_dir = tmp_path / "newdir"

    result = ensure_directory(test_dir)

    assert test_dir.exists()
    assert test_dir.is_dir()
    assert result == test_dir


def test_ensure_directory_creates_nested(tmp_path):
    """Test ensure_directory() creates nested directories."""
    test_dir = tmp_path / "level1" / "level2" / "level3"

    ensure_directory(test_dir)

    assert test_dir.exists()
    assert test_dir.is_dir()


def test_glob_files_finds_matching_files(tmp_path):
    """Test glob_files() finds files matching pattern."""
    (tmp_path / "test1.py").write_text("")
    (tmp_path / "test2.py").write_text("")
    (tmp_path / "test.txt").write_text("")

    results = list(glob_files(tmp_path, "*.py", recursive=False))

    assert len(results) == 2
    assert all(f.suffix == ".py" for f in results)


def test_glob_files_recursive(tmp_path):
    """Test glob_files() searches recursively."""
    (tmp_path / "test.py").write_text("")
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (subdir / "test2.py").write_text("")

    results = list(glob_files(tmp_path, "*.py", recursive=True))

    assert len(results) == 2


def test_glob_files_excludes_hidden(tmp_path):
    """Test glob_files() excludes hidden files by default."""
    (tmp_path / "visible.py").write_text("")
    (tmp_path / ".hidden.py").write_text("")

    results = list(glob_files(tmp_path, "*.py", include_hidden=False))

    assert len(results) == 1
    assert results[0].name == "visible.py"


def test_match_globs_include_only(tmp_path):
    """Test match_globs() with include patterns only."""
    path = "test.py"

    assert match_globs(path, ["*.py"], []) is True
    assert match_globs(path, ["*.txt"], []) is False


def test_match_globs_with_exclude(tmp_path):
    """Test match_globs() with exclude patterns."""
    path = "test.py"

    assert match_globs(path, ["*.py"], ["test_*.py"]) is True
    assert match_globs(path, ["*.py"], ["test.py"]) is False


def test_match_globs_empty_include_matches_all(tmp_path):
    """Test match_globs() with empty include list matches all."""
    path = "anything.xyz"

    assert match_globs(path, [], []) is True
    assert match_globs(path, [], ["*.xyz"]) is False
