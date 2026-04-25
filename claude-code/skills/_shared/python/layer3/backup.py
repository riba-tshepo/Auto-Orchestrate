"""
Backup utilities for file and directory backup management.

Provides backup creation, listing, restoration, and pruning.
"""

import hashlib
import tarfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class BackupInfo:
    """Information about a backup."""

    name: str
    path: str
    created_at: datetime
    size_bytes: int
    source_path: str
    checksum: str = ""
    label: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "path": self.path,
            "created_at": self.created_at.isoformat(),
            "size_bytes": self.size_bytes,
            "source_path": self.source_path,
            "checksum": self.checksum,
            "label": self.label,
        }


@dataclass
class BackupResult:
    """Result of a backup operation."""

    success: bool
    backup_info: BackupInfo | None = None
    message: str = ""
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "success": self.success,
            "message": self.message,
        }
        if self.backup_info:
            result["backup"] = self.backup_info.to_dict()
        if self.errors:
            result["errors"] = self.errors
        return result


def _calculate_checksum(path: Path) -> str:
    """Calculate SHA256 checksum of a file."""
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def create_backup(
    source: str | Path,
    backup_dir: str | Path,
    label: str = "",
    exclude: list[str] | None = None,
) -> BackupResult:
    """
    Create a backup of a file or directory.

    Args:
        source: Source path to backup
        backup_dir: Directory to store backups
        label: Optional label for the backup
        exclude: List of patterns to exclude

    Returns:
        BackupResult with backup info
    """
    source = Path(source).resolve()
    backup_dir = Path(backup_dir).resolve()
    exclude = exclude or []

    if not source.exists():
        return BackupResult(
            success=False,
            message=f"Source not found: {source}",
            errors=[f"Source path does not exist: {source}"],
        )

    # Create backup directory
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Generate backup name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    source_name = source.name
    backup_name = f"{source_name}_{timestamp}.tar.gz"
    backup_path = backup_dir / backup_name

    try:
        # Create tarball
        with tarfile.open(backup_path, "w:gz") as tar:

            def filter_func(tarinfo):
                for pattern in exclude:
                    if pattern in tarinfo.name:
                        return None
                return tarinfo

            tar.add(source, arcname=source.name, filter=filter_func)

        # Calculate checksum
        checksum = _calculate_checksum(backup_path)

        backup_info = BackupInfo(
            name=backup_name,
            path=str(backup_path),
            created_at=datetime.now(),
            size_bytes=backup_path.stat().st_size,
            source_path=str(source),
            checksum=checksum,
            label=label,
        )

        return BackupResult(
            success=True,
            backup_info=backup_info,
            message=f"Backup created: {backup_name}",
        )

    except Exception as e:
        return BackupResult(success=False, message=f"Backup failed: {e}", errors=[str(e)])


def list_backups(
    backup_dir: str | Path, sort_by: str = "created_at", limit: int | None = None
) -> list[BackupInfo]:
    """
    List backups in a directory.

    Args:
        backup_dir: Directory containing backups
        sort_by: Sort field ("created_at", "size", "name")
        limit: Maximum number of backups to return

    Returns:
        List of BackupInfo objects
    """
    backup_dir = Path(backup_dir)

    if not backup_dir.exists():
        return []

    backups = []
    for path in backup_dir.glob("*.tar.gz"):
        stat = path.stat()
        backups.append(
            BackupInfo(
                name=path.name,
                path=str(path),
                created_at=datetime.fromtimestamp(stat.st_mtime),
                size_bytes=stat.st_size,
                source_path="",  # Would need metadata file to know this
            )
        )

    # Sort
    if sort_by == "created_at":
        backups.sort(key=lambda b: b.created_at, reverse=True)
    elif sort_by == "size":
        backups.sort(key=lambda b: b.size_bytes, reverse=True)
    elif sort_by == "name":
        backups.sort(key=lambda b: b.name)

    if limit:
        backups = backups[:limit]

    return backups


def restore_backup(
    backup_path: str | Path, target_dir: str | Path, overwrite: bool = False
) -> BackupResult:
    """
    Restore a backup.

    Args:
        backup_path: Path to backup archive
        target_dir: Directory to restore to
        overwrite: Overwrite existing files

    Returns:
        BackupResult with restoration info
    """
    backup_path = Path(backup_path)
    target_dir = Path(target_dir)

    if not backup_path.exists():
        return BackupResult(
            success=False,
            message=f"Backup not found: {backup_path}",
            errors=[f"Backup file does not exist: {backup_path}"],
        )

    target_dir.mkdir(parents=True, exist_ok=True)

    try:
        with tarfile.open(backup_path, "r:gz") as tar:
            # Check for existing files
            if not overwrite:
                for member in tar.getmembers():
                    target_path = target_dir / member.name
                    if target_path.exists():
                        return BackupResult(
                            success=False,
                            message=f"Target exists: {target_path}",
                            errors=[f"File exists and overwrite=False: {target_path}"],
                        )

            tar.extractall(target_dir)

        return BackupResult(
            success=True,
            message=f"Restored to {target_dir}",
        )

    except Exception as e:
        return BackupResult(success=False, message=f"Restore failed: {e}", errors=[str(e)])


def verify_backup(backup_path: str | Path, expected_checksum: str = "") -> BackupResult:
    """
    Verify a backup's integrity.

    Args:
        backup_path: Path to backup archive
        expected_checksum: Expected SHA256 checksum (optional)

    Returns:
        BackupResult with verification info
    """
    backup_path = Path(backup_path)

    if not backup_path.exists():
        return BackupResult(
            success=False,
            message=f"Backup not found: {backup_path}",
            errors=[f"Backup file does not exist: {backup_path}"],
        )

    errors = []

    # Test archive integrity
    try:
        with tarfile.open(backup_path, "r:gz") as tar:
            # Try to read all members
            for _member in tar.getmembers():
                pass  # Just verify we can read the archive
    except Exception as e:
        errors.append(f"Archive integrity check failed: {e}")

    # Verify checksum if provided
    if expected_checksum:
        actual_checksum = _calculate_checksum(backup_path)
        if actual_checksum != expected_checksum:
            errors.append(f"Checksum mismatch: expected {expected_checksum}, got {actual_checksum}")

    if errors:
        return BackupResult(success=False, message="Verification failed", errors=errors)

    return BackupResult(
        success=True,
        message="Backup verified successfully",
    )


def prune_backups(
    backup_dir: str | Path,
    keep_count: int | None = None,
    keep_days: int | None = None,
    dry_run: bool = False,
) -> BackupResult:
    """
    Prune old backups.

    Args:
        backup_dir: Directory containing backups
        keep_count: Keep this many most recent backups
        keep_days: Keep backups from last N days
        dry_run: Don't actually delete, just report what would be deleted

    Returns:
        BackupResult with pruning info
    """
    backup_dir = Path(backup_dir)
    backups = list_backups(backup_dir, sort_by="created_at")

    to_delete = []
    now = datetime.now()

    for i, backup in enumerate(backups):
        should_delete = False

        if keep_count is not None and i >= keep_count:
            should_delete = True

        if keep_days is not None:
            age_days = (now - backup.created_at).days
            if age_days > keep_days:
                should_delete = True

        if should_delete:
            to_delete.append(backup)

    if not dry_run:
        for backup in to_delete:
            Path(backup.path).unlink()

    action = "Would delete" if dry_run else "Deleted"
    return BackupResult(
        success=True,
        message=f"{action} {len(to_delete)} backup(s)",
    )
