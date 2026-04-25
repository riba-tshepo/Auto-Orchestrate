#!/usr/bin/env bash
# =============================================================================
# Claude Code Configuration Installer
# Installs: skills, agents, commands, _shared, manifest.json, settings.json
# =============================================================================

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log()  { echo -e "${GREEN}[✔]${NC} $*"; }
warn() { echo -e "${YELLOW}[!]${NC} $*"; }
err()  { echo -e "${RED}[✘]${NC} $*"; exit 1; }

# --- Argument parsing ----------------------------------------------------------
CHECK_MODE=0
SOURCE_DIR=""
for arg in "$@"; do
  if [[ "$arg" == "--check" ]]; then
    CHECK_MODE=1
  elif [[ -z "$SOURCE_DIR" ]]; then
    SOURCE_DIR="$arg"
  fi
done
SOURCE_DIR="${SOURCE_DIR:-claude-code}"

CLAUDE_DIR="$HOME/.claude"
BACKUP_DIR="$CLAUDE_DIR/backup-$(date +%Y%m%d-%H%M%S)"

# --- check_mode: drift detection (no writes) ----------------------------------
check_mode() {
  if [[ ! -d "$SOURCE_DIR" ]]; then
    echo -e "${RED}[ERROR]${NC} Source directory '$SOURCE_DIR' not found."
    exit 2
  fi

  local drift_count=0
  local missing_list
  local src_count dst_count

  # --- Agents ---
  missing_list=""
  src_count=0
  dst_count=0
  if [[ -d "$SOURCE_DIR/agents" ]]; then
    while IFS= read -r src_file; do
      basename_file="$(basename "$src_file")"
      src_count=$((src_count + 1))
      if [[ -f "$CLAUDE_DIR/agents/$basename_file" ]]; then
        dst_count=$((dst_count + 1))
      else
        missing_list="${missing_list:+$missing_list, }${basename_file%.md}"
      fi
    done < <(find "$SOURCE_DIR/agents" -maxdepth 1 -name "*.md" | sort)
    if [[ $src_count -eq $dst_count ]]; then
      echo -e "${GREEN}[OK]${NC} agents: ${dst_count}/${src_count}"
    else
      echo -e "${RED}[DRIFT]${NC} agents: ${dst_count}/${src_count} (missing: ${missing_list})"
      drift_count=$((drift_count + 1))
    fi
  else
    echo -e "${YELLOW}[SKIP]${NC} agents: source directory not found"
  fi

  # --- Commands ---
  missing_list=""
  src_count=0
  dst_count=0
  if [[ -d "$SOURCE_DIR/commands" ]]; then
    while IFS= read -r src_file; do
      basename_file="$(basename "$src_file")"
      src_count=$((src_count + 1))
      if [[ -f "$CLAUDE_DIR/commands/$basename_file" ]]; then
        dst_count=$((dst_count + 1))
      else
        missing_list="${missing_list:+$missing_list, }${basename_file%.md}"
      fi
    done < <(find "$SOURCE_DIR/commands" -maxdepth 1 -name "*.md" | sort)
    if [[ $src_count -eq $dst_count ]]; then
      echo -e "${GREEN}[OK]${NC} commands: ${dst_count}/${src_count}"
    else
      echo -e "${RED}[DRIFT]${NC} commands: ${dst_count}/${src_count} (missing: ${missing_list})"
      drift_count=$((drift_count + 1))
    fi
  else
    echo -e "${YELLOW}[SKIP]${NC} commands: source directory not found"
  fi

  # --- Skills ---
  missing_list=""
  src_count=0
  dst_count=0
  if [[ -d "$SOURCE_DIR/skills" ]]; then
    while IFS= read -r src_dir; do
      skill_name="$(basename "$src_dir")"
      src_count=$((src_count + 1))
      if [[ -d "$CLAUDE_DIR/skills/$skill_name" ]]; then
        dst_count=$((dst_count + 1))
      else
        missing_list="${missing_list:+$missing_list, }${skill_name}"
      fi
    done < <(find "$SOURCE_DIR/skills" -mindepth 1 -maxdepth 1 -type d | sort)
    if [[ $src_count -eq $dst_count ]]; then
      echo -e "${GREEN}[OK]${NC} skills: ${dst_count}/${src_count}"
    else
      echo -e "${RED}[DRIFT]${NC} skills: ${dst_count}/${src_count} (missing: ${missing_list})"
      drift_count=$((drift_count + 1))
    fi
  else
    echo -e "${YELLOW}[SKIP]${NC} skills: source directory not found"
  fi

  # --- Orchestrator Integrity ---
  if [[ -f "$SOURCE_DIR/agents/orchestrator.md" ]] && [[ -f "$CLAUDE_DIR/agents/orchestrator.md" ]]; then
    src_hash=$(sha256sum "$SOURCE_DIR/agents/orchestrator.md" | awk '{print $1}')
    dst_hash=$(sha256sum "$CLAUDE_DIR/agents/orchestrator.md" | awk '{print $1}')
    if [[ "$src_hash" == "$dst_hash" ]]; then
      echo -e "${GREEN}[OK]${NC} orchestrator.md: integrity verified"
    else
      echo -e "${RED}[DRIFT]${NC} orchestrator.md: SHA256 mismatch (source vs runtime)"
      drift_count=$((drift_count + 1))
    fi
  else
    echo -e "${YELLOW}[SKIP]${NC} orchestrator.md: one or both files missing, skipping integrity check"
  fi

  # --- File Integrity (SHA256) ---
  for integrity_file in manifest.json settings.json; do
    if [[ -f "$SOURCE_DIR/$integrity_file" ]] && [[ -f "$CLAUDE_DIR/$integrity_file" ]]; then
      src_hash=$(sha256sum "$SOURCE_DIR/$integrity_file" | awk '{print $1}')
      dst_hash=$(sha256sum "$CLAUDE_DIR/$integrity_file" | awk '{print $1}')
      if [[ "$src_hash" == "$dst_hash" ]]; then
        echo -e "${GREEN}[OK]${NC} $integrity_file: integrity verified"
      else
        echo -e "${RED}[DRIFT]${NC} $integrity_file: SHA256 mismatch"
        drift_count=$((drift_count + 1))
      fi
    elif [[ ! -f "$CLAUDE_DIR/$integrity_file" ]]; then
      echo -e "${RED}[DRIFT]${NC} $integrity_file: MISSING"
      drift_count=$((drift_count + 1))
    fi
  done

  # --- Processes ---
  missing_list=""
  src_count=0
  dst_count=0
  if [[ -d "$SOURCE_DIR/processes" ]]; then
    while IFS= read -r src_entry; do
      entry_name="$(basename "$src_entry")"
      src_count=$((src_count + 1))
      if [[ -e "$CLAUDE_DIR/processes/$entry_name" ]]; then
        dst_count=$((dst_count + 1))
      else
        missing_list="${missing_list:+$missing_list, }${entry_name}"
      fi
    done < <(find "$SOURCE_DIR/processes" -mindepth 1 -maxdepth 1 | sort)
    if [[ $src_count -eq $dst_count ]]; then
      echo -e "${GREEN}[OK]${NC} processes: ${dst_count}/${src_count}"
    else
      echo -e "${RED}[DRIFT]${NC} processes: ${dst_count}/${src_count} (missing: ${missing_list})"
      drift_count=$((drift_count + 1))
    fi
  else
    echo -e "${YELLOW}[SKIP]${NC} processes: source directory not found"
  fi

  # --- Mandatory docs ---
  for doc_file in ARCHITECTURE.md INTEGRATION.md; do
    if [[ -f "$CLAUDE_DIR/$doc_file" ]]; then
      echo -e "${GREEN}[OK]${NC} $doc_file: present"
    else
      echo -e "${RED}[DRIFT]${NC} $doc_file: MISSING (mandatory)"
      drift_count=$((drift_count + 1))
    fi
  done

  # --- Python Dependencies Check ---
  if command -v python3 &>/dev/null || command -v python &>/dev/null; then
    local PYTHON_CMD
    PYTHON_CMD="$(command -v python3 || command -v python)"
    local py_ok=0
    local py_fail=0
    local py_missing=""

    for module_dir in "$CLAUDE_DIR/lib/ci_engine" "$CLAUDE_DIR/lib/domain_memory"; do
      if [[ -d "$module_dir" ]]; then
        module_name="$(basename "$module_dir")"
        if PYTHONPATH="$CLAUDE_DIR/lib" $PYTHON_CMD -c "import $module_name" 2>/dev/null; then
          py_ok=$((py_ok + 1))
        else
          py_fail=$((py_fail + 1))
          py_missing="${py_missing:+$py_missing, }${module_name}"
        fi
      fi
    done

    if [[ $py_fail -eq 0 ]] && [[ $py_ok -gt 0 ]]; then
      echo -e "${GREEN}[OK]${NC} python modules: ${py_ok} importable"
    elif [[ $py_fail -gt 0 ]]; then
      echo -e "${RED}[DRIFT]${NC} python modules: ${py_fail} failed import (${py_missing})"
      drift_count=$((drift_count + 1))
    else
      echo -e "${YELLOW}[SKIP]${NC} python modules: none installed"
    fi
  else
    echo -e "${YELLOW}[SKIP]${NC} python: not installed"
  fi

  echo ""
  if [[ $drift_count -eq 0 ]]; then
    echo -e "${GREEN}[PASS]${NC} No drift detected"
    exit 0
  else
    echo -e "${RED}[DRIFT]${NC} ${drift_count} component(s) out of sync — run install.sh to fix"
    exit 1
  fi
}

# --- Run check mode if requested ----------------------------------------------
if [[ $CHECK_MODE -eq 1 ]]; then
  check_mode
fi

# --- Pre-flight checks --------------------------------------------------------
if [[ ! -d "$SOURCE_DIR" ]]; then
  err "Source directory '$SOURCE_DIR' not found. Usage: $0 [source-dir]"
fi

echo ""
echo "  ╔══════════════════════════════════════════════════════╗"
echo "  ║       Claude Code Configuration Installer           ║"
echo "  ╚══════════════════════════════════════════════════════╝"
echo ""
echo "  Source:      $SOURCE_DIR"
echo "  Destination: $CLAUDE_DIR"
echo ""

# --- Create directories if needed ---------------------------------------------
mkdir -p "$CLAUDE_DIR"/{skills,agents,commands,processes}

# --- Backup existing config if present ----------------------------------------
backup_if_exists() {
  local target="$1"
  if [[ -e "$target" ]]; then
    mkdir -p "$BACKUP_DIR"
    cp -r "$target" "$BACKUP_DIR/"
    warn "Backed up existing $(basename "$target") → $BACKUP_DIR/"
  fi
}

# --- Orchestrator integrity check ---------------------------------------------
check_orchestrator_integrity() {
  local src_file="$SOURCE_DIR/agents/orchestrator.md"
  local dst_file="$CLAUDE_DIR/agents/orchestrator.md"

  if [[ ! -f "$src_file" ]]; then
    warn "orchestrator.md not found in source — integrity check skipped"
    return 0
  fi

  local src_hash dst_hash
  src_hash=$(sha256sum "$src_file" | awk '{print $1}')

  if [[ ! -f "$dst_file" ]]; then
    warn "orchestrator.md not installed yet — skipping runtime drift check"
    return 0
  fi

  dst_hash=$(sha256sum "$dst_file" | awk '{print $1}')

  if [[ "$src_hash" != "$dst_hash" ]]; then
    warn "INTEGRITY DRIFT: orchestrator.md runtime copy differs from source"
    warn "  Source:  $src_hash"
    warn "  Runtime: $dst_hash"
    warn "  Run install.sh to restore from source"
    return 1
  fi

  log "orchestrator.md integrity verified (SHA256 match)"
  return 0
}

# --- Install components -------------------------------------------------------

# Skills (auto-discovered by Claude Code)
if [[ -d "$SOURCE_DIR/skills" ]]; then
  backup_if_exists "$CLAUDE_DIR/skills"
  rm -rf "$CLAUDE_DIR/skills"
  mkdir -p "$CLAUDE_DIR/skills"
  cp -r "$SOURCE_DIR/skills/"* "$CLAUDE_DIR/skills/" 2>/dev/null || true
  log "Skills installed"
else
  warn "No skills directory found in $SOURCE_DIR — skipping"
fi

# Agents (flat .md files)
if [[ -d "$SOURCE_DIR/agents" ]]; then
  backup_if_exists "$CLAUDE_DIR/agents"
  rm -rf "$CLAUDE_DIR/agents"
  mkdir -p "$CLAUDE_DIR/agents"
  cp -r "$SOURCE_DIR/agents/"* "$CLAUDE_DIR/agents/" 2>/dev/null || true
  log "Agents installed"

  # Verify orchestrator.md integrity
  check_orchestrator_integrity
else
  warn "No agents directory found in $SOURCE_DIR — skipping"
fi

# Commands
if [[ -d "$SOURCE_DIR/commands" ]]; then
  backup_if_exists "$CLAUDE_DIR/commands"
  rm -rf "$CLAUDE_DIR/commands"
  mkdir -p "$CLAUDE_DIR/commands"
  cp -r "$SOURCE_DIR/commands/"* "$CLAUDE_DIR/commands/" 2>/dev/null || true
  log "Commands installed"
else
  warn "No commands directory found in $SOURCE_DIR — skipping"
fi

# Shared resources (protocols, templates, references, style-guides, schemas, tokens)
if [[ -d "$SOURCE_DIR/_shared" ]]; then
  backup_if_exists "$CLAUDE_DIR/_shared"
  rm -rf "$CLAUDE_DIR/_shared"
  mkdir -p "$CLAUDE_DIR/_shared"
  cp -r "$SOURCE_DIR/_shared/"* "$CLAUDE_DIR/_shared/" 2>/dev/null || true
  log "Shared resources installed"
else
  warn "No _shared directory found in $SOURCE_DIR — skipping"
fi

# Lib (CI engine + domain memory)
if [[ -d "$SOURCE_DIR/lib" ]]; then
  backup_if_exists "$CLAUDE_DIR/lib"
  rm -rf "$CLAUDE_DIR/lib"
  mkdir -p "$CLAUDE_DIR/lib"
  cp -r "$SOURCE_DIR/lib/"* "$CLAUDE_DIR/lib/" 2>/dev/null || true
  log "Lib (ci_engine, domain_memory) installed"
else
  warn "No lib directory found in $SOURCE_DIR — skipping"
fi

# --- Python Dependencies ---
log "Checking Python dependencies..."

# Check if Python 3 is available
if command -v python3 &>/dev/null; then
  PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
  PYTHON_CMD="python"
else
  warn "Python not found. CI engine features (OODA loop, PDCA telemetry) will be unavailable."
  PYTHON_CMD=""
fi

if [[ -n "$PYTHON_CMD" ]]; then
  # Install dependencies if requirements.txt has non-comment, non-empty lines
  if [[ -f "$SOURCE_DIR/requirements.txt" ]] && grep -qvE '^\s*(#|$)' "$SOURCE_DIR/requirements.txt" 2>/dev/null; then
    log "Installing Python dependencies from requirements.txt..."
    if $PYTHON_CMD -m pip install --user -r "$SOURCE_DIR/requirements.txt" 2>/dev/null; then
      log "Python dependencies installed successfully."
    else
      warn "pip install failed. Try: $PYTHON_CMD -m pip install --user -r $SOURCE_DIR/requirements.txt"
    fi
  else
    log "No third-party Python dependencies required."
  fi

  # Post-install verification: attempt to import CI engine modules
  log "Verifying Python module imports..."
  verify_failed=0
  for module_dir in "$CLAUDE_DIR/lib/ci_engine" "$CLAUDE_DIR/lib/domain_memory"; do
    if [[ -d "$module_dir" ]]; then
      module_name="$(basename "$module_dir")"
      if PYTHONPATH="$CLAUDE_DIR/lib" $PYTHON_CMD -c "import $module_name" 2>/dev/null; then
        log "  $module_name: import OK"
      else
        warn "  $module_name: import FAILED"
        verify_failed=1
      fi
    fi
  done

  if [[ $verify_failed -eq 1 ]]; then
    warn "Some Python modules failed to import. CI engine features may be degraded."
  fi
fi

# Processes (orchestration process definitions)
if [[ -d "$SOURCE_DIR/processes" ]]; then
  backup_if_exists "$CLAUDE_DIR/processes"
  rm -rf "$CLAUDE_DIR/processes"
  mkdir -p "$CLAUDE_DIR/processes"
  cp -r "$SOURCE_DIR/processes/"* "$CLAUDE_DIR/processes/" 2>/dev/null || true
  log "Processes installed"
else
  warn "No processes directory found in $SOURCE_DIR — skipping"
fi

# Manifest (required for orchestrator routing)
if [[ -f "$SOURCE_DIR/manifest.json" ]]; then
  backup_if_exists "$CLAUDE_DIR/manifest.json"
  cp "$SOURCE_DIR/manifest.json" "$CLAUDE_DIR/manifest.json"
  log "Manifest installed"
else
  warn "No manifest.json found in $SOURCE_DIR — skipping"
fi

# Settings
if [[ -f "$SOURCE_DIR/settings.json" ]]; then
  backup_if_exists "$CLAUDE_DIR/settings.json"
  cp "$SOURCE_DIR/settings.json" "$CLAUDE_DIR/settings.json"
  log "Settings installed"
else
  warn "No settings.json found in $SOURCE_DIR — skipping"
fi

# Documentation files
# Mandatory: ARCHITECTURE.md and INTEGRATION.md (orchestrator reference docs)
for doc_file in ARCHITECTURE.md INTEGRATION.md; do
  if [[ -f "$SOURCE_DIR/$doc_file" ]]; then
    backup_if_exists "$CLAUDE_DIR/$doc_file"
    cp "$SOURCE_DIR/$doc_file" "$CLAUDE_DIR/$doc_file"
    log "$doc_file installed"
  else
    err "MANDATORY: $doc_file not found in $SOURCE_DIR — installation aborted"
  fi
done

# Optional: PERMISSION-MODES.md
if [[ -f "$SOURCE_DIR/PERMISSION-MODES.md" ]]; then
  backup_if_exists "$CLAUDE_DIR/PERMISSION-MODES.md"
  cp "$SOURCE_DIR/PERMISSION-MODES.md" "$CLAUDE_DIR/PERMISSION-MODES.md"
  log "PERMISSION-MODES.md installed"
else
  warn "No PERMISSION-MODES.md found in $SOURCE_DIR — skipping"
fi

# --- Post-install verification ------------------------------------------------
verify_pass=1
verify_src_agents=0
verify_dst_agents=0
verify_src_commands=0
verify_dst_commands=0
verify_src_skills=0
verify_dst_skills=0

verify_src_agents=$(find "$SOURCE_DIR/agents" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l || echo 0)
verify_dst_agents=$(find "$CLAUDE_DIR/agents" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l || echo 0)
verify_src_commands=$(find "$SOURCE_DIR/commands" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l || echo 0)
verify_dst_commands=$(find "$CLAUDE_DIR/commands" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l || echo 0)
verify_src_skills=$(find "$SOURCE_DIR/skills" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l || echo 0)
verify_dst_skills=$(find "$CLAUDE_DIR/skills" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l || echo 0)
verify_src_processes=$(find "$SOURCE_DIR/processes" -mindepth 1 -maxdepth 1 2>/dev/null | wc -l || echo 0)
verify_dst_processes=$(find "$CLAUDE_DIR/processes" -mindepth 1 -maxdepth 1 2>/dev/null | wc -l || echo 0)

echo "  Agents:    ${verify_dst_agents} installed / ${verify_src_agents} in source"
echo "  Commands:  ${verify_dst_commands} installed / ${verify_src_commands} in source"
echo "  Skills:    ${verify_dst_skills} installed / ${verify_src_skills} in source"
echo "  Processes: ${verify_dst_processes} installed / ${verify_src_processes} in source"
echo ""

if [[ "$verify_dst_agents" -ne "$verify_src_agents" ]] || \
   [[ "$verify_dst_commands" -ne "$verify_src_commands" ]] || \
   [[ "$verify_dst_skills" -ne "$verify_src_skills" ]] || \
   [[ "$verify_dst_processes" -ne "$verify_src_processes" ]]; then
  verify_pass=0
fi

if [[ $verify_pass -eq 1 ]]; then
  echo -e "  ${GREEN}[PASS]${NC} All components installed"
else
  echo -e "  ${RED}[FAIL]${NC} Component count mismatch — re-run install.sh"
  exit 1
fi

# --- Summary ------------------------------------------------------------------
echo ""
echo "  ╔══════════════════════════════════════════════════════╗"
echo "  ║            Installation Complete!                    ║"
echo "  ╚══════════════════════════════════════════════════════╝"
echo ""
echo "  Installed to: $CLAUDE_DIR"
echo ""

if [[ -d "$BACKUP_DIR" ]]; then
  warn "Previous config backed up to: $BACKUP_DIR"
  echo ""
fi
