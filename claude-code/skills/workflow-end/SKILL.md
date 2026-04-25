---
name: workflow-end
description: |
  End current work session with status review and wrap-up.
  Use when user says "end", "end session", "done for now", "wrap up", "finish session".
triggers:
  - end
  - end session
  - done for now
  - wrap up
  - finish session
  - stop working
---

# End Work Session

Properly close your current work session with status review.

## Session Checkpoint Path

Determine the checkpoint file path based on session context:

1. If `SESSION_ID` is provided AND `.orchestrate/` exists in cwd (auto-orchestrate context): use `.orchestrate/<SESSION_ID>/tasks.json` (primary)
2. If `SESSION_ID` is provided but `.orchestrate/` does NOT exist (standalone usage): use `~/.claude/sessions/<SESSION_ID>-tasks.json` (legacy fallback)
3. If `SESSION_ID` is NOT provided (standalone usage): use `~/.claude/sessions/workflow-tasks.json` (legacy fallback)

Store this resolved path as `CHECKPOINT_PATH` for use in all subsequent steps.

## Step 1: Review Current State

Use `TaskList` to get the current task status.

## Step 2: Check Active Task

Identify any task with `status: in_progress`:

If a task is in progress:
```
Active task found: #3 - Implement user authentication

Options:
1. Mark as completed (if work is done)
2. Leave in progress (to resume later)
3. Add notes about current state
```

Ask the user what they'd like to do with the active task.

## Step 3: Complete Tasks If Requested

If user confirms task completion:
- Use `TaskUpdate` to set `status: completed`
- Note any tasks that become unblocked

```
Marked #3 as completed.

Newly unblocked:
  - #5: Deploy to production
  - #6: Write user docs
```

## Step 4: Session Summary

Display session wrap-up:

```
=== Session Ended ===

Completed this session:
  - #3: Implement user authentication

Still in progress:
  - (none)

Remaining tasks:
  - 4 pending
  - 2 blocked

Next suggested task: #5 - Deploy to production
```

## Step 5: Save Final Checkpoint (PERSIST-001)

After displaying the session summary, save the final task state:

1. Output: `Saving final session checkpoint...`
2. Use `TaskList` to get the latest task state
3. Use `Write` to save the checkpoint to `CHECKPOINT_PATH` (determined in Session Checkpoint Path section) with:
   - `schema_version`: `"1.0.0"`
   - `updated_at`: current ISO-8601 timestamp
   - `session_state`: `"ended"`
   - `tasks`: array of all tasks with id, subject, description, status, blockedBy, blocks, owner, metadata
4. Output: `Final session checkpoint saved. Session ended.`

Setting `session_state` to `"ended"` signals that this was an intentional close — `workflow-start` will NOT attempt crash recovery from an ended session.

## Step 6: Capture Session Notes (Optional)

If user provided a session note in the command (e.g., `/workflow-end Finished auth, needs testing`):

Store this context for future reference by updating the completed task's description or metadata.

## Success Criteria

Session successfully ended when:
- Active task status is resolved (completed or intentionally left in progress)
- Session progress is summarized
- User understands what's left to do
- Context is preserved for next session

## Important Notes

- Tasks persist across sessions - use `/workflow-start` to resume later
- Completed tasks remain in the list for reference
- Use `/workflow-dash` anytime to check project state

## Shared State Integration

After ending the session, update workflow state:

```bash
mkdir -p .pipeline-state/workflow
```

Write `.pipeline-state/workflow/active-session.json` (atomic write via `.tmp` + rename):
```json
{
  "session_state": "ended",
  "started_at": "<from previous active-session.json>",
  "ended_at": "<ISO-8601>",
  "task_count": 12,
  "tasks_completed": 10,
  "tasks_in_progress": 0,
  "last_updated": "<ISO-8601>"
}
```

If `.pipeline-state/` does not exist or write fails, log warning and continue — this is non-blocking.

## Inputs

- `SESSION_ID` (optional) — If provided, scopes all checkpoint reads/writes to `~/.claude/sessions/<SESSION_ID>-tasks.json`. Without it, falls back to `~/.claude/sessions/workflow-tasks.json`. Passed automatically by auto-orchestrate and session-manager.
