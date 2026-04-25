# Unified Output Standard

> **Authority**: This document is the single source of truth for how ALL commands
> (auto-orchestrate, auto-debug, auto-audit) create output files. Every agent
> and skill MUST follow these rules. The subagent-protocol-base.md defers to
> this document for file creation details.

## 1. File Naming Convention (MANDATORY)

ALL output files MUST use: `YYYY-MM-DD_<slug>.<ext>`

| Component | Rule | Example |
|-----------|------|---------|
| Date | ISO 8601 date, UTC | `2026-04-03` |
| Slug | Lowercase kebab-case descriptor | `auth-research`, `audit-report-cycle-1` |
| Extension | `.md` for reports, `.json` for structured data, `.jsonl` for append-only logs | — |
| Separator | Underscore between date and slug | `2026-04-03_auth-research.md` |

**No exceptions.** Audit reports, debug reports, research findings — all use this pattern.

## 2. Session Directory Structure

### 2.1 `.orchestrate/<session-id>/`

```
.orchestrate/<session-id>/
├── checkpoint.json                    # Session state (atomic write)
├── MANIFEST.jsonl                     # Session-level manifest (one per session)
├── proposed-tasks.json                # Task proposals from orchestrator
├── stage-0/                           # Research outputs
│   ├── YYYY-MM-DD_<slug>.md           # Research findings (1+ per task)
│   └── stage-receipt.json             # Stage completion receipt
├── stage-1/                           # Architecture outputs
│   ├── proposed-tasks.json            # Epic decomposition
│   └── stage-receipt.json
├── stage-2/                           # Specification outputs
│   ├── YYYY-MM-DD_<slug>.md           # Spec documents (1+ per task)
│   └── stage-receipt.json
├── stage-3/                           # Implementation tracking
│   ├── stage-receipt.json             # Receipt (code written to project files)
│   └── changes.md                     # Files modified (from DONE block)
├── stage-4/                           # Test tracking
│   ├── stage-receipt.json             # Receipt (tests written to project)
│   └── changes.md                     # Test files created
├── stage-4.5/                         # Codebase metrics
│   ├── YYYY-MM-DD_<slug>.md           # Metrics report
│   └── stage-receipt.json
├── stage-5/                           # Validation outputs
│   ├── YYYY-MM-DD_<slug>.md           # Validation report
│   └── stage-receipt.json
├── stage-6/                           # Documentation tracking
│   ├── stage-receipt.json             # Receipt (docs updated in project)
│   └── changes.md                     # Doc files modified
└── dispatch-receipts/                 # Command Dispatcher receipts
    ├── dispatch-context-TRIG-NNN.json # Context file for Skill invocation
    └── dispatch-YYYYMMDD-TRIG-NNN-XXXX.json  # Receipt from domain guide
```

**Stage-3, stage-4, stage-6** write code/tests/docs to the **project directory** (not `.orchestrate/`). Their `stage-receipt.json` + `changes.md` track what was modified. This is by design — implementation artifacts belong in the project, not the session directory.

### 2.2 `.debug/<session-id>/`

```
.debug/<session-id>/
├── checkpoint.json                    # Session state
├── MANIFEST.jsonl                     # Session-level manifest
├── error-history.jsonl                # Append-only error tracking
├── reports/                           # Debug reports
│   └── YYYY-MM-DD_<slug>.md           # Per-error debug report
├── diagnostics/                       # Diagnostic data
│   └── YYYY-MM-DD_<slug>.md           # Category-specific diagnostics
├── logs/                              # Supplementary logs (optional)
│   └── YYYY-MM-DD_<slug>.log
└── dispatch-receipts/                 # Command Dispatcher receipts
    ├── dispatch-context-TRIG-NNN.json # Context file for Skill invocation
    └── dispatch-YYYYMMDD-TRIG-NNN-XXXX.json  # Receipt from domain guide
```

### 2.3 `.audit/<session-id>/`

```
.audit/<session-id>/
├── checkpoint.json                    # Session state
├── MANIFEST.jsonl                     # Session-level manifest
├── cycle-1/                           # Per-cycle subdirectory
│   ├── YYYY-MM-DD_audit-report.md     # Human-readable audit report
│   ├── gap-report.json                # Machine-readable compliance matrix
│   └── stage-receipt.json             # Cycle completion receipt
├── cycle-2/
│   ├── YYYY-MM-DD_audit-report.md
│   ├── gap-report.json
│   └── stage-receipt.json
├── cycle-N/
│   └── ...
└── dispatch-receipts/                 # Command Dispatcher receipts
    ├── dispatch-context-TRIG-NNN.json # Context file for Skill invocation
    └── dispatch-YYYYMMDD-TRIG-NNN-XXXX.json  # Receipt from domain guide
```

## 3. MANIFEST.jsonl

Each session directory has ONE `MANIFEST.jsonl` at its root. Per-stage manifests are NOT used.

**Location**: `.<command>/<session-id>/MANIFEST.jsonl`

**Format**: One JSON object per line (no pretty-printing). Agents append; never overwrite.

**Required fields**:

```json
{
  "id": "<slug>-<date>",
  "file": "YYYY-MM-DD_<slug>.md",
  "title": "Human-readable title",
  "date": "YYYY-MM-DD",
  "status": "complete|partial|blocked",
  "stage": "stage_0|cycle_1|triage|...",
  "agent": "researcher|auditor|debugger|...",
  "topics": ["topic1", "topic2"],
  "key_findings": ["Finding 1", "Finding 2", "Finding 3"],
  "actionable": true,
  "needs_followup": [],
  "linked_tasks": [],
  "timestamp": "<ISO-8601>"
}
```

The global manifest at `~/.claude/MANIFEST.jsonl` continues to exist for cross-session discovery. Session manifests are the primary source for within-session tracking.

## 4. Stage Receipt (Domain Memory Bridge)

Every stage/phase/cycle completion MUST write a `stage-receipt.json` to the stage or cycle directory. This is the **standard artifact** that domain memory hooks consume.

### 4.1 Slim schema v2.0.0 (PRIMARY — STAGE-RECEIPT-DIET-001)

When `checkpoint.optimizations.stage_receipt_diet == true` (default for new sessions on fresh install), producers write the slim format below. Consumers MUST read both v1 and v2 (see 4.2).

```json
{
  "schema_version": "2.0.0",
  "format": "slim",
  "session_id": "<session-id>",
  "stage": "stage_0|stage_1|...|stage_6|cycle_1|triage|fix|verify",
  "agent": "researcher|software-engineer|auditor|debugger|...",
  "status": "complete|partial|blocked|skipped",
  "completed_at": "<ISO-8601>",
  "key_findings": ["Finding 1", "Finding 2"],
  "artifacts": [
    ".orchestrate/<session>/stage-0/2026-04-25_research.md",
    "src/auth.py"
  ],
  "errors": []
}
```

**Dropped from v1** (re-derivable on demand):
- `command` — implied by `session_id` (which embeds the command name)
- `duration_seconds` — observability data, can be re-derived from checkpoint timestamps
- `outputs.files_created` / `outputs.files_modified` — collapsed into a single `artifacts` array
- `outputs.manifest_entries` / `domain_memory_writes` — counts can be re-computed by reading the actual files
- `retry_count` — already tracked in checkpoint.iteration_history

Token saving: ~75 tok per receipt × ~3 reads per receipt × ~8 receipts per session ≈ ~1.8k *direct* receipt-payload reduction; total realized saving (per the plan) ≈ 40k tokens once consumer agents (Phase 5e debugger, Phase 5v auditor) avoid re-injecting full receipt blobs.

### 4.2 Verbose schema v1.0.0 (LEGACY / FALLBACK)

Produced when the flag is `false`. Consumers MUST be tolerant of this shape:

```json
{
  "schema_version": "1.0.0",
  "session_id": "<session-id>",
  "command": "auto-orchestrate|auto-debug|auto-audit",
  "stage": "stage_0|stage_1|...|stage_6|cycle_1|triage|fix|verify",
  "agent": "researcher|software-engineer|auditor|debugger|...",
  "status": "complete|partial|blocked|skipped",
  "completed_at": "<ISO-8601>",
  "duration_seconds": 45.2,
  "outputs": {
    "files_created": ["YYYY-MM-DD_research.md"],
    "files_modified": ["src/auth.py", "tests/test_auth.py"],
    "manifest_entries": 1
  },
  "domain_memory_writes": {
    "research_ledger": 1,
    "fix_registry": 0,
    "pattern_library": 0,
    "decision_log": 0,
    "codebase_analysis": 0,
    "user_preferences": 0
  },
  "key_findings": ["Finding 1", "Finding 2"],
  "errors": [],
  "retry_count": 0
}
```

### 4.3 Tolerant consumer protocol

Every consumer of `stage-receipt.json` MUST handle both shapes:

```python
def read_stage_receipt(path: str) -> dict:
    raw = json.load(open(path))
    sv = raw.get("schema_version", "1.0.0")
    if sv.startswith("2.") or raw.get("format") == "slim":
        # Slim: collapse artifacts back into outputs structure for legacy code paths
        raw.setdefault("outputs", {"files_created": raw.get("artifacts", []),
                                    "files_modified": [],
                                    "manifest_entries": 0})
        raw.setdefault("duration_seconds", None)
        raw.setdefault("retry_count", 0)
        raw.setdefault("domain_memory_writes", {})
        raw.setdefault("command", _infer_command_from_session(raw["session_id"]))
    return raw
```

**Re-fattening insurance**: If a downstream agent (e.g. debugger) determines it needs a dropped field for a specific case, set `needs_full_receipt: true` on the spawn — the producer re-emits a v1 receipt for that one stage. Logged as `[STAGE-RECEIPT-DIET-001 FALLBACK]`.

**Purpose**: Provides a machine-readable, uniform record of what happened in each stage across all commands. Domain memory hooks read this to extract and persist knowledge.

## 5. Checkpoint Recovery Protocol

On session start (Step 2b of any command), scan for orphaned temporary files:

1. If `checkpoint.tmp.json` exists AND `checkpoint.json` does NOT exist:
   - Rename `checkpoint.tmp.json` → `checkpoint.json`
   - Log: `[RECOVERY] Recovered checkpoint from orphaned tmp file`

2. If BOTH `checkpoint.tmp.json` AND `checkpoint.json` exist:
   - Keep `checkpoint.json` (it's the completed write)
   - Delete `checkpoint.tmp.json` (it's stale)
   - Log: `[RECOVERY] Cleaned up stale checkpoint.tmp.json`

3. If only `checkpoint.json` exists: normal path, no action needed.

## 6. Gap Report Schema Reference

The `gap-report.json` file (used by `.audit/` and `.orchestrate/stage-5/`) follows this schema:

```json
{
  "session_id": "<session-id>",
  "audit_cycle": 1,
  "date": "YYYY-MM-DD",
  "spec_path": "<path-to-spec>",
  "compliance_score": 75.0,
  "verdict": "PASS|ACCEPTABLE|FAIL",
  "threshold": 90,
  "total_requirements": 20,
  "summary": {
    "pass": 15,
    "partial": 3,
    "missing": 1,
    "fail": 1,
    "skipped": 0
  },
  "gaps": [
    {
      "id": "REQ-001",
      "source": "spec.md:42",
      "type": "functional|security|service|non-functional",
      "priority": "MUST|SHOULD|MAY",
      "status": "PASS|PARTIAL|MISSING|FAIL",
      "description": "Requirement description",
      "evidence": ["file.py:10 — implementation found"],
      "remediation": "Suggested fix"
    }
  ],
  "services": {
    "total": 3,
    "healthy": 2,
    "unhealthy": 1,
    "details": []
  }
}
```

## 7. Cross-Command Consistency Rules

| Rule | Description |
|------|-------------|
| **NAME-001** | ALL output files use `YYYY-MM-DD_<slug>.<ext>` |
| **MANIFEST-SESSION** | Each session has ONE `MANIFEST.jsonl` at session root |
| **RECEIPT-001** | Every stage/cycle writes `stage-receipt.json` |
| **CHECKPOINT-001** | Atomic write: tmp → rename. Recovery on startup. |
| **STRUCTURE-001** | All commands use subdirectories for phases/stages |
| **DOMAIN-BRIDGE** | Stage receipts are the standard input for domain memory hooks |
