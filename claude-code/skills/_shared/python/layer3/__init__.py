"""Layer 3: Domain-specific operations."""

from .backup import (
    BackupInfo,
    BackupResult,
    create_backup,
    list_backups,
    prune_backups,
    restore_backup,
    verify_backup,
)
from .doctor import (
    DiagnosticResult,
    SystemHealth,
    check_claude_directory,
    check_environment,
    check_manifest,
    check_python_version,
    check_tasks_file,
    diagnose_system,
)
from .hierarchy_unified import (
    count_task_tree,
    find_task_by_id,
    get_epic_tasks,
    get_task_ancestors,
    get_task_children,
    get_task_depth,
    get_task_descendants,
    get_task_siblings,
)
from .migrate import (
    MigrationInfo,
    VersionInfo,
    compare_versions,
    detect_version,
    parse_version,
)

__all__ = [
    # Migration
    "detect_version",
    "parse_version",
    "compare_versions",
    "MigrationInfo",
    "VersionInfo",
    # Backup
    "create_backup",
    "list_backups",
    "restore_backup",
    "verify_backup",
    "prune_backups",
    "BackupInfo",
    "BackupResult",
    # Diagnostics
    "check_environment",
    "check_python_version",
    "check_claude_directory",
    "check_manifest",
    "check_tasks_file",
    "diagnose_system",
    "DiagnosticResult",
    "SystemHealth",
    # Hierarchy
    "get_task_children",
    "get_task_descendants",
    "get_task_ancestors",
    "get_task_siblings",
    "get_epic_tasks",
    "count_task_tree",
    "get_task_depth",
    "find_task_by_id",
]
