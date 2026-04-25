"""Layer 1: Basic I/O operations."""

from .config import (
    ConfigError,
    ConfigNotFoundError,
    ConfigValidationError,
    load_config,
    merge_config,
    save_config,
)
from .error_json import emit_error as emit_error_json
from .error_json import emit_success, format_error_json
from .file_ops import (
    ensure_directory,
    file_exists,
    glob_files,
    is_directory,
    match_globs,
    read_file,
    safe_write,
    write_file,
)
from .heartbeat import check_heartbeat, cleanup_stale_heartbeats, write_heartbeat
from .logging import emit_error, emit_info, emit_warning, get_logger, setup_logging
from .memory import clear_memory, get_memory_path, load_memory, save_memory
from .output_format import OutputFormat, format_human, format_table, output
from .manifest_digest import (
    build_digest,
    clear_cache as clear_digest_cache,
    estimate_digest_tokens,
    estimate_full_manifest_tokens,
    needs_full_manifest,
)
from .orchestrator_template import (
    build_spawn_prompt_body,
    estimate_tokens as estimate_template_tokens,
    extract_core,
    extract_meeting_template,
    extract_phase_template,
    extract_stage_template,
)
from .skill_frontmatter import (
    FrontmatterError,
    estimate_frontmatter_tokens,
    list_skills_with_triggers,
    read_frontmatter,
)
from .spec_utils import (
    IMPERATIVE_PATTERNS,
    PRIORITY_MAP,
    TYPE_INDICATORS,
    extract_keywords,
    infer_priority,
    infer_type,
)

__all__ = [
    # Logging
    "setup_logging",
    "get_logger",
    "emit_error",
    "emit_warning",
    "emit_info",
    # Output formatting
    "output",
    "format_human",
    "format_table",
    "OutputFormat",
    # File operations
    "read_file",
    "write_file",
    "safe_write",
    "ensure_directory",
    "glob_files",
    "match_globs",
    "file_exists",
    "is_directory",
    # Error JSON
    "emit_error_json",
    "emit_success",
    "format_error_json",
    # Config
    "load_config",
    "save_config",
    "merge_config",
    "ConfigError",
    "ConfigNotFoundError",
    "ConfigValidationError",
    # Heartbeat
    "write_heartbeat",
    "check_heartbeat",
    "cleanup_stale_heartbeats",
    # Memory
    "load_memory",
    "save_memory",
    "clear_memory",
    "get_memory_path",
    # Spec utilities
    "extract_keywords",
    "infer_type",
    "infer_priority",
    "IMPERATIVE_PATTERNS",
    "PRIORITY_MAP",
    "TYPE_INDICATORS",
    # Skill frontmatter (SKILL-FRONTMATTER-001)
    "read_frontmatter",
    "list_skills_with_triggers",
    "estimate_frontmatter_tokens",
    "FrontmatterError",
    # Manifest digest (MANIFEST-DIGEST-001)
    "build_digest",
    "estimate_digest_tokens",
    "estimate_full_manifest_tokens",
    "needs_full_manifest",
    "clear_digest_cache",
    # Orchestrator template extractor (TEMPLATE-EXTRACT-001)
    "build_spawn_prompt_body",
    "extract_core",
    "extract_stage_template",
    "extract_phase_template",
    "extract_meeting_template",
    "estimate_template_tokens",
]
