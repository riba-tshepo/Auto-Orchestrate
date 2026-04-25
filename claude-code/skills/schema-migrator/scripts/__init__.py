"""
Schema Migrator scripts.

Scripts for version detection, migration validation, and backup management.

Available scripts:
- version_detector: Detect schema version from JSON/YAML files
- migration_validator: Validate migration file sequences
- backup_manager: Create, list, prune, and verify backups
"""

from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent

__all__ = [
    "version_detector",
    "migration_validator",
    "backup_manager",
]
