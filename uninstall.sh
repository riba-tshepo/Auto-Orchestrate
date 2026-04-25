#!/usr/bin/env bash
# =============================================================================
# Claude Code Configuration Uninstaller
# Removes: skills, agents, commands, _shared, manifest.json, settings.json
# =============================================================================

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log()  { echo -e "${GREEN}[✔]${NC} $*"; }
warn() { echo -e "${YELLOW}[!]${NC} $*"; }
err()  { echo -e "${RED}[✘]${NC} $*"; exit 1; }

# --- Configuration ------------------------------------------------------------
CLAUDE_DIR="$HOME/.claude"
DRY_RUN=false
SKIP_CONFIRM=false

# --- Argument parsing ---------------------------------------------------------
for arg in "$@"; do
  case "$arg" in
    --dry-run)   DRY_RUN=true ;;
    --yes|-y)    SKIP_CONFIRM=true ;;
    --help|-h)
      echo "Usage: $0 [--dry-run] [--yes|-y]"
      echo ""
      echo "Options:"
      echo "  --dry-run    Show what would be removed without deleting"
      echo "  --yes, -y    Skip confirmation prompt"
      echo "  --help, -h   Show this help message"
      exit 0
      ;;
    *)
      err "Unknown argument: $arg"
      ;;
  esac
done

# --- Banner -------------------------------------------------------------------
echo ""
echo "  ╔══════════════════════════════════════════════════════╗"
if [[ "$DRY_RUN" == "true" ]]; then
echo "  ║     Claude Code Configuration Uninstaller (DRY RUN) ║"
else
echo "  ║       Claude Code Configuration Uninstaller          ║"
fi
echo "  ╚══════════════════════════════════════════════════════╝"
echo ""
echo "  Target: $CLAUDE_DIR"
echo ""

# --- Components to remove -----------------------------------------------------
COMPONENTS=(
  "$CLAUDE_DIR/skills"
  "$CLAUDE_DIR/agents"
  "$CLAUDE_DIR/commands"
  "$CLAUDE_DIR/_shared"
  "$CLAUDE_DIR/processes"
  "$CLAUDE_DIR/lib"
  "$CLAUDE_DIR/manifest.json"
  "$CLAUDE_DIR/settings.json"
  "$CLAUDE_DIR/ARCHITECTURE.md"
  "$CLAUDE_DIR/INTEGRATION.md"
  "$CLAUDE_DIR/PERMISSION-MODES.md"
)

# --- Dry run: show what would be removed --------------------------------------
if [[ "$DRY_RUN" == "true" ]]; then
  warn "DRY RUN — no files will be removed"
  echo ""
  found=0
  for component in "${COMPONENTS[@]}"; do
    if [[ -e "$component" ]]; then
      echo "  Would remove: $component"
      found=$((found + 1))
    else
      echo "  Not found (skip): $component"
    fi
  done
  echo ""
  if [[ $found -eq 0 ]]; then
    log "Nothing to remove — configuration is not installed"
  else
    warn "$found component(s) would be removed"
  fi
  exit 0
fi

# --- Confirmation prompt -------------------------------------------------------
if [[ "$SKIP_CONFIRM" == "false" ]]; then
  echo "  The following will be permanently removed from $CLAUDE_DIR:"
  echo ""
  for component in "${COMPONENTS[@]}"; do
    if [[ -e "$component" ]]; then
      echo "    - $component"
    fi
  done
  echo ""
  echo "  Backup directories ($CLAUDE_DIR/backup-*) will NOT be removed."
  echo ""
  read -r -p "  Proceed with uninstall? [y/N] " confirm
  case "$confirm" in
    [yY][eE][sS]|[yY]) ;;
    *)
      warn "Uninstall cancelled"
      exit 0
      ;;
  esac
  echo ""
fi

# --- Removal ------------------------------------------------------------------
removed=0
skipped=0

remove_component() {
  local component="$1"
  local label="$2"
  if [[ -e "$component" ]]; then
    rm -rf "$component"
    log "$label removed"
    removed=$((removed + 1))
  else
    warn "$label not found — skipping"
    skipped=$((skipped + 1))
  fi
}

remove_component "$CLAUDE_DIR/skills"            "Skills"
remove_component "$CLAUDE_DIR/agents"            "Agents"
remove_component "$CLAUDE_DIR/commands"          "Commands"
remove_component "$CLAUDE_DIR/_shared"           "Shared resources"
remove_component "$CLAUDE_DIR/processes"         "Processes"
remove_component "$CLAUDE_DIR/lib"               "Lib"
remove_component "$CLAUDE_DIR/manifest.json"     "Manifest"
remove_component "$CLAUDE_DIR/settings.json"     "Settings"
remove_component "$CLAUDE_DIR/ARCHITECTURE.md"   "ARCHITECTURE.md"
remove_component "$CLAUDE_DIR/INTEGRATION.md"    "INTEGRATION.md"
remove_component "$CLAUDE_DIR/PERMISSION-MODES.md" "PERMISSION-MODES.md"

# --- Summary ------------------------------------------------------------------
echo ""
echo "  ╔══════════════════════════════════════════════════════╗"
echo "  ║             Uninstall Complete!                      ║"
echo "  ╚══════════════════════════════════════════════════════╝"
echo ""
echo "  Removed: $removed component(s)"
if [[ $skipped -gt 0 ]]; then
  warn "Skipped: $skipped component(s) not found"
fi
echo ""
if [[ -d "$CLAUDE_DIR" ]]; then
  warn "Note: $CLAUDE_DIR directory was preserved (may still contain backups and other data)"
fi
echo ""
