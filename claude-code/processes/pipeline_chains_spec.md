# Pipeline Chains Specification
**Version**: 1.1.0
**Date**: 2026-04-14
**Schema Version**: 1.1.0

---

## 1. Overview

Pipeline chains track explicit chaining relationships between pipeline sessions. They extend `.sessions/index.json` with an optional `pipeline_chains` array field that records how multiple commands are linked together in sequence (e.g., `/new-project` → `/auto-orchestrate` → `/sprint-ceremony`).

**Purpose**:
- Provide cross-pipeline coordination tracking
- Enable commands to know their position in a larger workflow
- Allow users to trace which sessions are part of a unified delivery chain

**Key Constraint (R-007)**: Pipeline chains are ONLY created when a user explicitly requests pipeline chaining. They are NEVER created automatically by any command.

---

## 2. Schema Definition

The `pipeline_chains` array is an optional extension to `.sessions/index.json`. The full extended schema is:

```json
{
  "schema_version": "1.1.0",
  "sessions": [],
  "pipeline_chains": [
    {
      "chain_id": "chain-{YYYYMMDD}-{slug}",
      "created_at": "ISO-8601 timestamp",
      "description": "Human-readable description of this chain",
      "stages": [
        {
          "command": "new-project",
          "session_id": null,
          "status": "complete",
          "output_path": ".orchestrate/{session_id}/handoff-receipt.json",
          "completed_at": null
        },
        {
          "command": "auto-orchestrate",
          "session_id": "auto-orc-20260414-myproj",
          "status": "complete",
          "output_path": ".orchestrate/auto-orc-20260414-myproj/stage-6/",
          "completed_at": "2026-04-14T15:30:00Z"
        },
        {
          "command": "auto-audit",
          "session_id": null,
          "status": "pending",
          "trigger": "auto-orchestrate.complete",
          "spec_path": ".orchestrate/auto-orc-20260414-myproj/stage-2/YYYY-MM-DD_spec.md",
          "output_path": null,
          "completed_at": null
        }
      ]
    }
  ]
}
```

---

## 3. Stage Object Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `command` | string | YES | The command name (e.g., "auto-orchestrate") |
| `session_id` | string or null | YES | The session ID; null if not yet started |
| `status` | enum | YES | One of: "pending", "active", "complete", "failed", "skipped", "ready" |
| `output_path` | string or null | NO | Path to key output artifact from this stage |
| `trigger` | string or null | NO | What event triggers this stage (e.g., "auto-orchestrate.complete") |
| `spec_path` | string or null | NO | Path to spec file consumed by this stage |
| `completed_at` | ISO-8601 or null | NO | Timestamp when this stage was set to "complete" |

### Status Enum Values

| Status | Meaning |
|--------|---------|
| `pending` | Stage has not started. Waiting for trigger or user action. |
| `active` | Stage is currently running (session in progress). |
| `complete` | Stage finished successfully. |
| `failed` | Stage terminated with an error. |
| `skipped` | Stage was intentionally bypassed. |
| `ready` | Stage is unblocked and ready for user to invoke (distinct from "active"). |

**Path Safety**: `output_path` and `spec_path` values MUST be relative paths. Absolute paths and path traversal patterns (`../`) are NOT allowed.

---

## 4. Schema Version Backward-Compatibility Rule

```
When reading .sessions/index.json:
- If schema_version is absent or < "1.1.0": treat pipeline_chains as empty array []
- If schema_version is "1.1.0" or higher: read pipeline_chains normally
- NEVER reject or fail if pipeline_chains is absent — it is optional

When writing .sessions/index.json:
- Always write schema_version: "1.1.0"
- If pipeline_chains is empty or no chains: write "pipeline_chains": []
- Atomic write: write to .sessions/index.tmp.json, then rename to index.json
```

All commands that read `.sessions/index.json` must handle the absence of `pipeline_chains` gracefully by defaulting to an empty array `[]`.

---

## 5. Opt-In Constraint (R-007)

```
pipeline_chains entries are ONLY created when a user explicitly requests pipeline chaining.

Examples of explicit requests:
- "After auto-orchestrate completes, run auto-audit"
- "Chain this to sprint-ceremony"
- At /new-project Phase 5 when user specifies downstream pipeline

pipeline_chains entries are NEVER created automatically by any command.
```

This constraint prevents accidental cross-pipeline coupling and ensures users remain in control of pipeline sequencing.

---

## 6. Usage Examples

### Example 1: new-project → auto-orchestrate → sprint-ceremony chain

A user starting a full delivery cycle from planning through implementation to sprint execution:

```json
{
  "schema_version": "1.1.0",
  "sessions": [],
  "pipeline_chains": [
    {
      "chain_id": "chain-20260414-delivery-cycle",
      "created_at": "2026-04-14T09:00:00Z",
      "description": "Full delivery cycle: planning to sprint execution",
      "stages": [
        {
          "command": "new-project",
          "session_id": "new-proj-20260414-myapp",
          "status": "complete",
          "output_path": ".orchestrate/new-proj-20260414-myapp/handoff-receipt.json",
          "completed_at": "2026-04-14T10:30:00Z"
        },
        {
          "command": "auto-orchestrate",
          "session_id": "auto-orc-20260414-myapp",
          "status": "complete",
          "output_path": ".orchestrate/auto-orc-20260414-myapp/stage-6/",
          "completed_at": "2026-04-14T15:45:00Z"
        },
        {
          "command": "sprint-ceremony",
          "session_id": null,
          "status": "ready",
          "trigger": "auto-orchestrate.complete",
          "output_path": null,
          "completed_at": null
        }
      ]
    }
  ]
}
```

### Example 2: auto-orchestrate → auto-audit chain

A user who wants automated compliance verification after implementation:

```json
{
  "schema_version": "1.1.0",
  "sessions": [],
  "pipeline_chains": [
    {
      "chain_id": "chain-20260414-impl-audit",
      "created_at": "2026-04-14T09:00:00Z",
      "description": "Implementation with automated audit verification",
      "stages": [
        {
          "command": "auto-orchestrate",
          "session_id": "auto-orc-20260414-feature",
          "status": "active",
          "output_path": ".orchestrate/auto-orc-20260414-feature/stage-6/",
          "completed_at": null
        },
        {
          "command": "auto-audit",
          "session_id": null,
          "status": "pending",
          "trigger": "auto-orchestrate.complete",
          "spec_path": ".orchestrate/auto-orc-20260414-feature/stage-2/2026-04-14_spec.md",
          "output_path": null,
          "completed_at": null
        }
      ]
    }
  ]
}
```

---

## 7. Commands That Read/Write pipeline_chains

| Command | Operation | When |
|---------|-----------|------|
| `session-manager` | Read + Write | On session start/end when chain tracking is active |
| `auto-orchestrate` | Write (status update) | At Stage 6 completion when chain entry exists |
| `workflow` | Read | To display pipeline chain status in Current Project Status section |

---

*Generated by software-engineer | Session auto-orc-20260414-pipeflow | Stage 3 | Task T-005*
