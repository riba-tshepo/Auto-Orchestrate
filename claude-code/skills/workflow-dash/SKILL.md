---
name: workflow-dash
description: |
  Show project task dashboard with comprehensive overview.
  Use when user says "dash", "dashboard", "show tasks", "project status", "task overview".
triggers:
  - dash
  - dashboard
  - show tasks
  - project status
  - task overview
  - show dashboard
---

# Project Task Dashboard

Display comprehensive project overview showing all tasks grouped by status.

## Session Checkpoint Path

Determine the checkpoint file path based on session context:

1. If `SESSION_ID` is provided AND `.orchestrate/` exists in cwd (auto-orchestrate context): use `.orchestrate/<SESSION_ID>/tasks.json` (primary)
2. If `SESSION_ID` is provided but `.orchestrate/` does NOT exist (standalone usage): use `~/.claude/sessions/<SESSION_ID>-tasks.json` (legacy fallback)
3. If `SESSION_ID` is NOT provided (standalone usage): use `~/.claude/sessions/workflow-tasks.json` (legacy fallback)

Store this resolved path as `CHECKPOINT_PATH` for use in all subsequent steps.

## Execution Steps

### Step 1: Get All Tasks

Use `TaskList` to retrieve all tasks in the current session.

### Step 1b: Save Checkpoint (PERSIST-001)

After retrieving tasks, save the current state:

1. Output: `Saving session checkpoint...`
2. Use `Write` to save to `CHECKPOINT_PATH` (determined in Session Checkpoint Path section) with:
   - `schema_version`: `"1.0.0"`
   - `updated_at`: current ISO-8601 timestamp
   - `session_state`: `"active"`
   - `tasks`: array of all tasks with id, subject, description, status, blockedBy, blocks, owner, metadata
3. Output: `Session checkpoint saved.`

Dashboard reads are natural checkpoint moments — saving here ensures the checkpoint stays current even if the user only uses `/workflow-dash` between mutations.

### Step 2: Display Dashboard

Present tasks grouped by status:

**In Progress**
- Tasks with `status: in_progress`
- Show task ID, subject, and owner

**Blocked**
- Tasks with non-empty `blockedBy` array
- Show what's blocking each task

**Pending**
- Tasks with `status: pending` and empty `blockedBy`
- Ready to be picked up

**Completed**
- Tasks with `status: completed`
- Show completion count

## Dashboard Format

```
=== Project Dashboard ===

IN PROGRESS (1)
  #3: Implement user login [owner: agent-1]

BLOCKED (2)
  #5: Deploy to production (blocked by #3, #4)
  #6: Write user docs (blocked by #3)

PENDING (3)
  #4: Add input validation
  #7: Setup CI/CD
  #8: Performance optimization

COMPLETED (4)
  #1: Project setup
  #2: Database schema

Summary: 10 tasks | 1 active | 2 blocked | 3 pending | 4 done
```

## Dashboard Components

The dashboard shows:
- **Task Summary**: Total, pending, active, blocked, done
- **Blocking Analysis**: Which tasks are blockers
- **Ready Queue**: Tasks that can be started immediately
- **Progress**: Completion percentage

## Success Criteria

Dashboard is complete when user understands:
- Total project state (how many tasks, what status)
- Current focus and active work
- What's blocked and why
- What's ready to be picked up next
- Overall progress toward completion

## Use Cases

- **Session start**: Understand project state before work
- **Status check**: Quick progress review
- **Planning**: Identify what needs attention
- **Handoff**: Share project state with team/agents

## Shared State Integration

After generating the dashboard, cache it for cross-pipeline visibility:

```bash
mkdir -p .pipeline-state/workflow
```

Write `.pipeline-state/workflow/dashboard-cache.json` (atomic write via `.tmp` + rename):
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

If `.pipeline-state/` does not exist or write fails, log warning and continue — this is non-blocking.

## Inputs

- `SESSION_ID` (optional) — If provided, scopes all checkpoint reads/writes to `~/.claude/sessions/<SESSION_ID>-tasks.json`. Without it, falls back to `~/.claude/sessions/workflow-tasks.json`. Passed automatically by auto-orchestrate and session-manager.
