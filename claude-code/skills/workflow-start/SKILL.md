---
name: workflow-start
description: |
  Start a work session with task overview.
  Use when user says "start", "begin session", "start work", "start working".
triggers:
  - start
  - begin session
  - start work
  - start working
  - begin work
---

# Start Work Session

Begin a new work session by reviewing tasks and establishing focus.

## Session Checkpoint Path

Determine the checkpoint file path based on session context:

1. If `SESSION_ID` is provided AND `.orchestrate/` exists in cwd (auto-orchestrate context): use `.orchestrate/<SESSION_ID>/tasks.json` (primary)
2. If `SESSION_ID` is provided but `.orchestrate/` does NOT exist (standalone usage): use `~/.claude/sessions/<SESSION_ID>-tasks.json` (legacy fallback)
3. If `SESSION_ID` is NOT provided (standalone usage): use `~/.claude/sessions/workflow-tasks.json` (legacy fallback)

Store this resolved path as `CHECKPOINT_PATH` for use in all subsequent steps.


## Step 0: Crash Recovery (PERSIST-002)

Before anything else, check for tasks from a previous session:

1. Use `TaskList` to check current task state
2. If `TaskList` returns **empty** (no tasks exist):
   a. Output: `Checking for previous session data...`
   b. Use `Read` to check `CHECKPOINT_PATH` (determined above)
   c. If the checkpoint file exists and `session_state` is `"active"`:
      - Output: `Previous session found (checkpoint: <updated_at>). Recovering tasks...`
      - For each task in the checkpoint, use `TaskCreate` to recreate it (subject, description, activeForm)
        - Output: `Recovering task <i> of <total>: <subject>`
      - After all tasks are created, use `TaskUpdate` to restore dependencies (`addBlockedBy`) and status (`in_progress` or `completed`)
      - Display recovery complete message:
        ```
        Recovery complete: Restored <N> tasks from previous session.
        ```
   d. If the checkpoint file does not exist or `session_state` is `"ended"`:
      - Output: `No previous session to recover. Starting fresh.`
      - Skip recovery — this is a fresh session
3. If `TaskList` returns tasks, skip recovery — the session is already populated

## Step 1: Get Current State

Use `TaskList` to retrieve all existing tasks and their status.

## Step 2: Display Session Overview

Present the current task landscape:

```
=== Session Started ===

Current Tasks:
  IN PROGRESS: 1
  PENDING: 5
  BLOCKED: 2
  COMPLETED: 3

Active Task: #3 - Implement user authentication
```

If no tasks exist:
```
=== Session Started ===

No tasks found. This appears to be a fresh session.

Use TaskCreate to add tasks, or describe what you'd like to work on.
```

## Step 3: Identify or Set Focus

### If tasks with `in_progress` status exist:
Display the current focus and confirm continuation:
```
Resuming focus on: #3 - Implement user authentication

Description: Add JWT-based authentication...

Continue with this task, or use /workflow-focus <id> to switch.
```

### If no task is in progress:
Find the best candidate using these criteria:
1. Tasks with `status: pending` and empty `blockedBy`
2. Prefer tasks that unblock others (check `blocks` array)
3. Suggest the top candidate

```
No active task. Suggested focus:

#4: Add input validation
  - Unblocked and ready
  - Blocks 2 other tasks

Use /workflow-focus 4 to start, or /workflow-next for more options.
```

## Step 4: Session Context

Provide helpful context:
- How many tasks are blocked and by what
- What was last completed
- Recommended next action

## Step 5: Save Checkpoint (PERSIST-001)

After displaying the session overview, save the current task state:

1. Output: `Saving session checkpoint...`
2. Use `TaskList` to get the latest task state
3. Use `Write` to save the checkpoint to `CHECKPOINT_PATH` (determined in Session Checkpoint Path section) with:
   - `schema_version`: `"1.0.0"`
   - `updated_at`: current ISO-8601 timestamp
   - `session_state`: `"active"`
   - `tasks`: array of all tasks with id, subject, description, status, blockedBy, blocks, owner, metadata
4. Output: `Session checkpoint saved.`

## Success Criteria

Session successfully started when:
- Current task state is understood
- Focus is established (existing or new)
- User knows what to work on next
- Blockers and dependencies are clear

## Next Steps

- Use `/workflow-focus <id>` to change focus to a different task
- Use `/workflow-next` to get next task suggestions
- Use `/workflow-dash` for full project dashboard
- Use `/workflow-end` when done to wrap up the session

## Shared State Integration

After displaying the session overview, write workflow state for cross-pipeline visibility:

```bash
mkdir -p .pipeline-state/workflow
```

Write `.pipeline-state/workflow/active-session.json` (atomic write via `.tmp` + rename):
```json
{
  "session_state": "active",
  "started_at": "<ISO-8601>",
  "ended_at": null,
  "task_count": 12,
  "tasks_completed": 5,
  "tasks_in_progress": 1,
  "last_updated": "<ISO-8601>"
}
```

If `.pipeline-state/` does not exist or write fails, log warning and continue — this is non-blocking.

## Inputs

- `SESSION_ID` (optional) — If provided, scopes all checkpoint reads/writes to `~/.claude/sessions/<SESSION_ID>-tasks.json`. Without it, falls back to `~/.claude/sessions/workflow-tasks.json`. Passed automatically by auto-orchestrate and session-manager.
