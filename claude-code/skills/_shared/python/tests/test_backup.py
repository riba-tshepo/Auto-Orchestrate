"""
Tests for layer3.backup module.

Tests backup utilities including create_backup, list_backups, restore_backup,
verify_backup, and prune_backups.
"""

from datetime import datetime
from pathlib import Path

from layer3.backup import (
    BackupInfo,
    BackupResult,
    create_backup,
    list_backups,
    prune_backups,
    restore_backup,
    verify_backup,
)


def test_backup_info_to_dict():
    """Test BackupInfo.to_dict() conversion."""
    backup_info = BackupInfo(
        name="test_20260130_120000.tar.gz",
        path="/backups/test.tar.gz",
        created_at=datetime(2026, 1, 30, 12, 0, 0),
        size_bytes=1024,
        source_path="/source/path",
        checksum="abc123",
        label="daily",
    )

    result = backup_info.to_dict()

    assert result["name"] == "test_20260130_120000.tar.gz"
    assert result["size_bytes"] == 1024
    assert result["label"] == "daily"


def test_backup_result_to_dict_success():
    """Test BackupResult.to_dict() with success."""
    result = BackupResult(success=True, message="Backup created successfully")

    result_dict = result.to_dict()

    assert result_dict["success"] is True
    assert result_dict["message"] == "Backup created successfully"


def test_backup_result_to_dict_with_errors():
    """Test BackupResult.to_dict() with errors."""
    result = BackupResult(success=False, message="Backup failed", errors=["Error 1", "Error 2"])

    result_dict = result.to_dict()

    assert result_dict["success"] is False
    assert result_dict["errors"] == ["Error 1", "Error 2"]


def test_create_backup_single_file(tmp_path):
    """Test create_backup() with a single file."""
    source_file = tmp_path / "source" / "test.txt"
    source_file.parent.mkdir()
    source_file.write_text("test content")

    backup_dir = tmp_path / "backups"

    result = create_backup(source_file, backup_dir)

    assert result.success is True
    assert result.backup_info is not None
    assert Path(result.backup_info.path).exists()
    assert result.backup_info.checksum != ""


def test_create_backup_directory(tmp_path):
    """Test create_backup() with a directory."""
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "file1.txt").write_text("content1")
    (source_dir / "file2.txt").write_text("content2")

    backup_dir = tmp_path / "backups"

    result = create_backup(source_dir, backup_dir, label="test")

    assert result.success is True
    assert result.backup_info.label == "test"
    assert Path(result.backup_info.path).exists()


def test_create_backup_nonexistent_source(tmp_path):
    """Test create_backup() with nonexistent source."""
    source = tmp_path / "nonexistent"
    backup_dir = tmp_path / "backups"

    result = create_backup(source, backup_dir)

    assert result.success is False
    assert "not found" in result.message.lower()


def test_create_backup_with_exclude(tmp_path):
    """Test create_backup() with exclude patterns."""
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "include.txt").write_text("keep")
    (source_dir / "exclude.tmp").write_text("skip")

    backup_dir = tmp_path / "backups"

    result = create_backup(source_dir, backup_dir, exclude=[".tmp"])

    assert result.success is True
    # Verify backup was created (detailed content check would need extraction)


def test_list_backups_empty_directory(tmp_path):
    """Test list_backups() with empty directory."""
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()

    backups = list_backups(backup_dir)

    assert backups == []


def test_list_backups_with_backups(tmp_path):
    """Test list_backups() with existing backups."""
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()

    # Create dummy backup files
    (backup_dir / "backup1_20260130_120000.tar.gz").write_bytes(b"data1")
    (backup_dir / "backup2_20260130_130000.tar.gz").write_bytes(b"data2")

    backups = list_backups(backup_dir)

    assert len(backups) == 2
    assert all(isinstance(b, BackupInfo) for b in backups)


def test_list_backups_with_limit(tmp_path):
    """Test list_backups() with limit parameter."""
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()

    for i in range(5):
        (backup_dir / f"backup{i}.tar.gz").write_bytes(b"data")

    backups = list_backups(backup_dir, limit=3)

    assert len(backups) == 3


def test_restore_backup_success(tmp_path):
    """Test restore_backup() successfully restores backup."""
    # Create a backup
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "test.txt").write_text("original content")

    backup_dir = tmp_path / "backups"
    create_result = create_backup(source_dir, backup_dir)

    # Restore to new location
    restore_dir = tmp_path / "restored"
    result = restore_backup(create_result.backup_info.path, restore_dir)

    assert result.success is True
    assert (restore_dir / "source" / "test.txt").exists()


def test_restore_backup_nonexistent(tmp_path):
    """Test restore_backup() with nonexistent backup."""
    backup_path = tmp_path / "nonexistent.tar.gz"
    restore_dir = tmp_path / "restored"

    result = restore_backup(backup_path, restore_dir)

    assert result.success is False
    assert "not found" in result.message.lower()


def test_restore_backup_no_overwrite(tmp_path):
    """Test restore_backup() respects overwrite=False."""
    # Create backup
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "test.txt").write_text("content")

    backup_dir = tmp_path / "backups"
    create_result = create_backup(source_dir, backup_dir)

    # Create existing file at restore location
    restore_dir = tmp_path / "restored"
    restore_dir.mkdir()
    (restore_dir / "source").mkdir()
    (restore_dir / "source" / "test.txt").write_text("existing")

    result = restore_backup(create_result.backup_info.path, restore_dir, overwrite=False)

    assert result.success is False
    assert "exists" in result.message.lower()


def test_verify_backup_valid(tmp_path):
    """Test verify_backup() with valid backup."""
    # Create backup
    source_file = tmp_path / "source" / "test.txt"
    source_file.parent.mkdir()
    source_file.write_text("content")

    backup_dir = tmp_path / "backups"
    create_result = create_backup(source_file, backup_dir)

    result = verify_backup(create_result.backup_info.path)

    assert result.success is True


def test_verify_backup_with_checksum(tmp_path):
    """Test verify_backup() with checksum validation."""
    source_file = tmp_path / "source" / "test.txt"
    source_file.parent.mkdir()
    source_file.write_text("content")

    backup_dir = tmp_path / "backups"
    create_result = create_backup(source_file, backup_dir)

    result = verify_backup(
        create_result.backup_info.path, expected_checksum=create_result.backup_info.checksum
    )

    assert result.success is True


def test_verify_backup_wrong_checksum(tmp_path):
    """Test verify_backup() with incorrect checksum."""
    source_file = tmp_path / "source" / "test.txt"
    source_file.parent.mkdir()
    source_file.write_text("content")

    backup_dir = tmp_path / "backups"
    create_result = create_backup(source_file, backup_dir)

    result = verify_backup(create_result.backup_info.path, expected_checksum="wrongchecksum123")

    assert result.success is False
    assert result.success is False


def test_prune_backups_by_count(tmp_path):
    """Test prune_backups() with keep_count."""
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()

    # Create dummy backups
    for i in range(5):
        (backup_dir / f"backup{i}.tar.gz").write_bytes(b"data")

    result = prune_backups(backup_dir, keep_count=2, dry_run=False)

    assert result.success is True
    remaining = list(backup_dir.glob("*.tar.gz"))
    assert len(remaining) == 2


def test_prune_backups_dry_run(tmp_path):
    """Test prune_backups() with dry_run=True."""
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()

    for i in range(3):
        (backup_dir / f"backup{i}.tar.gz").write_bytes(b"data")

    result = prune_backups(backup_dir, keep_count=1, dry_run=True)

    assert result.success is True
    assert "Would delete" in result.message
    # All files should still exist
    remaining = list(backup_dir.glob("*.tar.gz"))
    assert len(remaining) == 3
