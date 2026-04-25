# Cross-Pipeline Shared State Protocol

**Version**: 2.0.0  
**Status**: Active  
**RFC 2119 Keywords**: MUST, SHOULD, MAY

## Overview

The three autonomous pipeline commands (`auto-orchestrate`, `auto-audit`, `auto-debug`) operate with isolated session directories (`.orchestrate/`, `.audit/`, `.debug/`). This protocol defines a shared state layer at `.pipeline-state/` that enables cross-pipeline knowledge transfer without violating session isolation. As of v2.0.0, all 20 commands participate in the shared state layer via command receipts and process logging.

## Constraints

| ID | Rule |
|----|------|
| SHARED-001 | **Shared knowledge at startup** — All pipelines MUST read shared knowledge stores (`research-cache.jsonl`, `fix-registry.jsonl`, `codebase-analysis.jsonl`) at startup before performing their first action. Stale entries (past `ttl_hours`) are treated as hints, not facts. |
| SHARED-002 | **Escalation to shared store** — Escalation handoffs MUST be written to the shared `.pipeline-state/escalation-log.jsonl`, not to session-local directories. This ensures the target pipeline can discover and consume the handoff regardless of which session directory structure it uses. |
| SHARED-003 | **Research cache before researcher** — Before spawning a researcher agent, the loop controller MUST check `.pipeline-state/research-cache.jsonl` for non-stale entries matching the research query. If a cached result exists with `ttl_hours` not expired, it SHOULD be used directly instead of re-researching. |
| SHARED-004 | **Fix-registry append-only and shared** — The fix-registry (`.pipeline-state/fix-registry.jsonl`) is append-only and shared across all pipelines. Before diagnosing an error, `auto-debug` MUST check if a verified fix (`verification_result: "pass"`) already exists for the error fingerprint. Consumers MUST NOT modify or delete existing entries. |

---

## Directory Structure

```
.pipeline-state/
├── research-cache.jsonl       # Research findings reusable across pipelines
├── fix-registry.jsonl         # Error → fix mappings from auto-debug
├── codebase-analysis.jsonl    # Codebase insights from any pipeline
├── escalation-log.jsonl       # Cross-pipeline escalation history
├── pipeline-context.json      # Current pipeline state summary (overwritten)
├── command-receipts/           # Standardized output from every command (STATE-001)
│   ├── <command>-<YYYYMMDD>-<HHMMSS>.json
│   └── ...
├── process-log/                # Per-process execution history (STATE-003)
│   ├── P-001.jsonl
│   └── ...P-093.jsonl
└── workflow/                   # Workflow state integration
    ├── active-session.json
    ├── task-board.json          # Single source of truth (WORKFLOW-SYNC-001)
    ├── focus-stack.json         # Replaces task-focus.json
    └── dashboard-cache.json
```

## Stores

### research-cache.jsonl (append-only)

Written by: `auto-orchestrate` (Stage 0), `auto-audit` (before remediation)  
Read by: All pipelines at startup

```json
{
  "id": "<SHA-256 of query>",
  "query": "latest stable version of fastapi",
  "result": "0.115.0",
  "source": "pypi.org",
  "source_session": "auto-orc-20260414-myapp",
  "source_command": "auto-orchestrate",
  "timestamp": "2026-04-14T10:00:00Z",
  "ttl_hours": 24,
  "tags": ["dependency", "python", "fastapi"]
}
```

**TTL**: Entries older than `ttl_hours` are considered stale. Consumers SHOULD re-verify stale entries but MAY use them as hints.

### fix-registry.jsonl (append-only)

Written by: `auto-debug` (after verified fix)  
Read by: `auto-debug` (before diagnosis), `auto-audit` (before remediation)

```json
{
  "error_fingerprint": "<16-char hex from AD-GAP-002>",
  "error_type": "ConnectionRefusedError",
  "error_context": "PostgreSQL connection on port 5432",
  "fix_description": "Corrected DATABASE_URL port from 5433 to 5432",
  "files_modified": [".env"],
  "verification_result": "pass",
  "source_session": "auto-dbg-20260414-connref",
  "timestamp": "2026-04-14T11:00:00Z",
  "confidence": "high"
}
```

**Lookup protocol**: Before applying a new fix, auto-debug SHOULD check if the error fingerprint already exists in the fix-registry. If a verified fix exists (`verification_result: "pass"`), suggest it immediately.

### codebase-analysis.jsonl (append-only)

Written by: All pipelines (via stage receipts)  
Read by: All pipelines at startup

```json
{
  "file_path": "src/api/routes.py",
  "insight_type": "risk|pattern|debt|dependency",
  "description": "Route handler has no input validation — injection risk",
  "severity": "high",
  "source_session": "auto-aud-20260414-specchk",
  "source_command": "auto-audit",
  "timestamp": "2026-04-14T12:00:00Z"
}
```

### escalation-log.jsonl (append-only)

Written by: Any pipeline that escalates to another  
Read by: Target pipeline on startup

```json
{
  "from_command": "auto-debug",
  "from_session": "auto-dbg-20260414-connref",
  "to_command": "auto-orchestrate",
  "escalation_type": "architectural",
  "category": "design_flaw",
  "context": "Connection pooling design doesn't support multi-tenant isolation",
  "consumed": false,
  "consumed_by": null,
  "timestamp": "2026-04-14T13:00:00Z"
}
```

### command-receipts/ (one file per invocation)

Written by: All commands (STATE-001)  
Read by: Big Three at boot and stage transitions (STATE-002)

Directory: `.pipeline-state/command-receipts/`  
Filename pattern: `<command>-<YYYYMMDD>-<HHMMSS>.json`

**Receipt Schema** (all fields required unless marked optional):

```json
{
  "command": "<command-name>",
  "receipt_id": "<command>-<YYYYMMDD>-<HHMMSS>",
  "timestamp": "<ISO-8601>",
  "session_context": {
    "session_id": "<if applicable, else null>",
    "pipeline": "<auto-orchestrate|auto-audit|auto-debug|standalone>"
  },
  "inputs": {},
  "outputs": {},
  "artifacts": [],
  "processes_executed": ["P-XXX"],
  "next_recommended_action": "<command or null>",
  "dispatch_context": {
    "trigger_id": "<if invoked via dispatch, else null>",
    "invoked_by": "<pipeline session that dispatched, else null>"
  }
}
```

**Command-specific `inputs` and `outputs`**:

| Command | `inputs` | `outputs` |
|---------|----------|-----------|
| new-project | `{ "project_name", "trigger_gate" }` | `{ "handoff_receipt_path", "session_id" }` |
| gate-review | `{ "gate_id", "session_id" }` | `{ "verdict": "PASS\|FAIL", "checklist_passed", "checklist_total" }` |
| sprint-ceremony | `{ "ceremony_type" }` | `{ "action_items": [], "sprint_goal" }` |
| active-dev | `{ "activity_type" }` | `{ "processes_reviewed": [], "guidance_given" }` |
| release-prep | `{ "release_name" }` | `{ "checklist_status": {}, "blocking_items": [] }` |
| post-launch | `{ "activity_type" }` | `{ "metrics_reviewed": [], "action_items": [] }` |
| security | `{ "mode", "process_ids": [] }` | `{ "findings": [], "severity_max" }` |
| qa | `{ "mode", "process_ids": [] }` | `{ "findings": [], "severity_max" }` |
| infra | `{ "mode", "process_ids": [] }` | `{ "findings": [], "severity_max" }` |
| risk | `{ "mode", "process_ids": [] }` | `{ "findings": [], "risk_items": [] }` |
| data-ml-ops | `{ "mode", "process_ids": [] }` | `{ "findings": [], "severity_max" }` |
| org-ops | `{ "mode", "process_ids": [] }` | `{ "findings": [], "category" }` |
| process-lookup | `{ "query" }` | `{ "matched_processes": [] }` |
| assign-agent | `{ "task_description" }` | `{ "assigned_agent", "rationale" }` |
| workflow | `{ "view_type" }` | `{ "gate_statuses": {} }` |
| auto-orchestrate | `{ "task_description", "scope" }` | `{ "terminal_state", "stages_completed": [], "tasks_total", "tasks_completed" }` |
| auto-audit | `{ "spec_path" }` | `{ "verdict", "compliance_score", "cycles_run" }` |
| auto-debug | `{ "error_description" }` | `{ "errors_resolved", "errors_remaining", "escalations" }` |

**Backward compatibility**: If `.pipeline-state/command-receipts/` does not exist, commands MUST create it via `mkdir -p`. If receipt writing fails (permissions, disk full), the command MUST log a warning and proceed — receipt writing is never a blocking operation.

### process-log/ (append-only, per-process)

Written by: Any command that executes a process (STATE-003)  
Read by: auto-orchestrate phases for coverage stats and gap analysis

Directory: `.pipeline-state/process-log/`  
One file per process: `P-001.jsonl`, `P-002.jsonl`, ... `P-093.jsonl`

```json
{
  "process_id": "P-038",
  "command_source": "security",
  "session_id": "auto-orc-20260414-myapp",
  "timestamp": "2026-04-14T10:30:00Z",
  "result": "completed|skipped|blocked|deferred",
  "artifacts_produced": ["threat-model.md"],
  "receipt_id": "security-20260414-103000"
}
```

**Write protocol**: Open file in append mode. Write one complete JSON line. Flush and close. Create file if it does not exist.

### workflow/ (integrated workflow state)

Written by: `workflow-start`, `workflow-end`, `workflow-focus`, `workflow-dash`, Big Three (auto-orchestrate writes task-board.json, focus-stack.json, active-session.json)  
Read by: Big Three for session context awareness; workflow-* commands for display

Directory: `.pipeline-state/workflow/`

**active-session.json** (overwritten):
```json
{
  "session_state": "active|ended",
  "source": "auto-orchestrate|auto-audit|auto-debug|workflow-start",
  "session_id": "<session-id or null>",
  "started_at": "<ISO-8601>",
  "ended_at": "<ISO-8601 or null>",
  "task_count": 12,
  "tasks_completed": 5,
  "tasks_in_progress": 1,
  "last_updated": "<ISO-8601>"
}
```

**task-board.json** (overwritten — WORKFLOW-SYNC-001):
```json
{
  "schema_version": "1.0.0",
  "source": "auto-orchestrate|standalone",
  "session_id": "<session-id or null>",
  "last_updated": "<ISO-8601>",
  "iteration": 0,
  "pipeline_stage": null,
  "tasks": [
    {
      "id": "<task-id>",
      "subject": "<subject>",
      "status": "pending|in_progress|completed|failed|blocked",
      "dispatch_hint": "<stage hint>",
      "blockedBy": ["<task-id>"],
      "stage": 0,
      "updated_at": "<ISO-8601>"
    }
  ],
  "stages_completed": [],
  "terminal_state": null
}
```

**focus-stack.json** (overwritten — replaces task-focus.json):
```json
{
  "source": "auto-orchestrate|workflow-focus",
  "session_id": "<session-id or null>",
  "focused_task_id": "<task-id or null>",
  "focused_task_subject": "<subject>",
  "focused_at": "<ISO-8601>",
  "stack": ["<task-id>"],
  "last_updated": "<ISO-8601>"
}
```

**Backward compatibility**: Readers SHOULD check `focus-stack.json` first. If not found, fall back to `task-focus.json`. On next write, always write to `focus-stack.json` only.

**dashboard-cache.json** (overwritten):
```json
{
  "generated_at": "<ISO-8601>",
  "summary": {
    "total": 12,
    "completed": 5,
    "in_progress": 1,
    "blocked": 2,
    "pending": 4
  },
  "blocked_tasks": [{"id": "...", "blocked_by": "..."}]
}
```

### Sync Rules (WORKFLOW-SYNC-001, WORKFLOW-SYNC-002)

| File | Written by | Read by | Big Three running? |
|------|-----------|---------|-------------------|
| active-session.json | workflow-start, workflow-end, Big Three (on start/stop) | All | Read/write for Big Three; read-only for workflow-* |
| task-board.json | auto-orchestrate (at every iteration, Step 4.8e) | workflow-dash, workflow-next | Write by auto-orchestrate only; read-only for all others |
| focus-stack.json | workflow-focus (standalone), auto-orchestrate (when running) | workflow-focus, workflow-dash | Read-only for workflow-focus when Big Three active |
| dashboard-cache.json | workflow-dash | workflow-dash (cache) | Read-only always (generated from task-board.json) |

**Lock detection**: To determine if a Big Three session is active, check `pipeline-context.json`:
- If `active_command` is one of `["auto-orchestrate", "auto-audit", "auto-debug"]` AND `last_updated` is within the last 5 minutes → Big Three is active → enforce WORKFLOW-SYNC-002
- Otherwise → full read/write access for workflow-* commands

### pipeline-context.json (overwritten)

Written by: Whichever pipeline is currently active  
Read by: Other pipelines on startup for situational awareness

```json
{
  "active_command": "auto-orchestrate",
  "active_session": "auto-orc-20260414-myapp",
  "current_stage": 3,
  "stages_completed": [0, 1, 2],
  "last_updated": "2026-04-14T14:00:00Z",
  "files_modified_recently": ["src/api/routes.py", "src/models/user.py"],
  "active_errors": [],
  "compliance_score": null
}
```

## Constraints

| ID | Rule |
|----|------|
| STATE-001 | **Universal receipt writing** — Every command invocation MUST write a receipt to `.pipeline-state/command-receipts/`. Receipt filename: `<command>-<YYYYMMDD>-<HHMMSS>.json`. Receipt schema defined in the command-receipts section above. Commands MUST create `.pipeline-state/command-receipts/` via `mkdir -p` if it does not exist. Receipt writing MUST NOT block command execution — log warnings on failure. |
| STATE-002 | **Receipt consumption by Big Three** — `auto-orchestrate`, `auto-audit`, and `auto-debug` MUST read relevant receipts from `.pipeline-state/command-receipts/` at boot (during shared state initialization) and at each stage transition (during dispatch evaluation). Receipts older than the current session's `created_at` timestamp are treated as **context** (informational), not **directives** (actionable). Receipts from within the current session are actionable. |
| STATE-003 | **Process execution logging** — When a command executes a process (P-001 through P-093), it MUST append a log entry to `.pipeline-state/process-log/<process-id>.jsonl`. This enables process coverage tracking across all commands and sessions. |
| WORKFLOW-SYNC-001 | **Task board single source of truth** — `.pipeline-state/workflow/task-board.json` is the canonical task state when auto-orchestrate is active. auto-orchestrate WRITES this file at every iteration (Step 4.8e). `/workflow-dash`, `/workflow-next`, and `/workflow-focus` READ this file. No other command writes to `task-board.json` while auto-orchestrate is active. When auto-orchestrate is not running, `/workflow-*` commands have full read/write access to `task-board.json`. |
| WORKFLOW-SYNC-002 | **Read-only workflow mode** — When `pipeline-context.json` shows an active Big Three session (any of auto-orchestrate, auto-audit, auto-debug with `last_updated` < 5 minutes ago), `/workflow-*` commands operate in read-only mode for all `workflow/` files except `dashboard-cache.json` (which they may regenerate from `task-board.json`). Full read/write access resumes when no Big Three session is active. |
| RAID-001 | **Single RAID log** — P-010 (Stage 1 RAID seeding) and P-074 (risk management updates) share a single RAID log per session at `.orchestrate/{session_id}/raid-log.json`. Append-only JSONL format. The `/risk` domain guide also reads/appends to this file when invoked in dispatch mode. Entry schema: `{ "id", "type": "Risk|Assumption|Issue|Dependency", "description", "severity", "owner", "status", "source_process", "timestamp" }`. |

## Integration Points

> **Note**: As of 2026-04-25, `/auto-orchestrate` is the only user-facing command. The previously separate `/auto-audit`, `/auto-debug`, and lifecycle/domain commands now run as internal phases within `/auto-orchestrate`. The integration points below describe one command's interaction with the cross-pipeline state directory.

### auto-orchestrate (the only command)

**On startup (Step 0f)**:
1. `mkdir -p .pipeline-state .pipeline-state/command-receipts .pipeline-state/process-log .pipeline-state/workflow`
2. Read `pipeline-context.json` — if another auto-orchestrate session was recently active, log context
3. Read `codebase-analysis.jsonl` — pass high-severity insights to researcher (Stage 0)
4. Read `command-receipts/` (STATE-002) — scan for receipts from prior auto-orchestrate sessions in this project. Receipts predating this session's `created_at` are context; same-session receipts are actionable. (Historical receipts from deleted commands like `/security`, `/qa`, `/auto-audit` are immutable audit trail — read for context but no longer produced.)
5. Read `workflow/active-session.json` — if a workflow session is active, log task state for awareness
6. Store `last_receipt_scan` timestamp for incremental scanning at stage transitions

**At each stage transition (Step 4.8c)**: Re-scan `command-receipts/` for receipts written since `last_receipt_scan` (STATE-002). New actionable receipts with HIGH/CRITICAL findings are treated as equivalent to internal phase transition conditions (e.g., security findings → Phase 5s).

**On Stage 0 completion**: Write research findings to `research-cache.jsonl`

**On Phase 5e completion (debug sub-loop)**: Write error→fix mappings to `fix-registry.jsonl` for verified fixes (formerly written by `/auto-debug`).

**On Phase 5v completion (audit sub-loop)**: Write file-level findings to `codebase-analysis.jsonl` (formerly written by `/auto-audit`).

**On termination**: Update `pipeline-context.json` with final state. Write receipt to `command-receipts/auto-orchestrate-<YYYYMMDD>-<HHMMSS>.json` (STATE-001). Write process log entries for all processes executed across phases (STATE-003). Write phase summary to `command-receipts/`.

### Phase receipts (within session)

In addition to the cross-session `command-receipts/` directory, each session writes per-phase receipts to `.orchestrate/<session>/phase-receipts/` per PHASE-LOOP-002. These are local to the session and consumed by the loop controller for phase coordination — they do not flow to `.pipeline-state/`.

**State commands** (`new-project`, `gate-review`):
- On completion: Write receipt to `command-receipts/<command>-<YYYYMMDD>-<HHMMSS>.json` (STATE-001) **in addition to** their existing state artifacts (`handoff-receipt.json`, `gate-state.json`)
- For each process executed: Append to `process-log/<process-id>.jsonl` (STATE-003)

**Utility commands** (`process-lookup`, `assign-agent`, `workflow`):
- On completion: Write receipt to `command-receipts/<command>-<YYYYMMDD>-<HHMMSS>.json` (STATE-001)

**Workflow skills** (`workflow-start`, `workflow-end`, `workflow-focus`, `workflow-dash`):
- Write to `workflow/` directory as defined in the workflow/ store section above

## Concurrency Safety

All `.jsonl` stores are append-only. Writers MUST:
1. Open file in append mode (`a`, not `w`)
2. Write a single complete JSON line (no multi-line entries)
3. Flush and close immediately

`pipeline-context.json` uses atomic write (write to `.tmp`, rename).

## Backward Compatibility

`.pipeline-state/` is optional. If the directory doesn't exist, commands proceed without shared state. The first command to run creates it via `mkdir -p`. No command should fail if `.pipeline-state/` is missing or if any store file is empty/missing. Subdirectories (`command-receipts/`, `process-log/`, `workflow/`) are also optional — commands create them via `mkdir -p` on first write. If reading and the directory is missing, treat as empty (no receipts exist yet).

## Privacy

`.pipeline-state/` SHOULD be added to `.gitignore` — it contains session-specific operational data, not project artifacts.
