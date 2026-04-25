---
name: workflow-focus
description: |
  Show or set task focus for single-task workflow discipline.
  Use when user says "focus", "set focus", "focus on task", "switch task".
triggers:
  - focus
  - set focus
  - focus on task
  - switch task
  - change focus
---

# Focus Management

Manage single-task workflow discipline with focus commands.

## Session Checkpoint Path

Determine the checkpoint file path based on session context:

1. If `SESSION_ID` is provided AND `.orchestrate/` exists in cwd (auto-orchestrate context): use `.orchestrate/<SESSION_ID>/tasks.json` (primary)
2. If `SESSION_ID` is provided but `.orchestrate/` does NOT exist (standalone usage): use `~/.claude/sessions/<SESSION_ID>-tasks.json` (legacy fallback)
3. If `SESSION_ID` is NOT provided (standalone usage): use `~/.claude/sessions/workflow-tasks.json` (legacy fallback)

Store this resolved path as `CHECKPOINT_PATH` for use in all subsequent steps.

## Usage Modes

### Mode 1: Show Current Focus (no arguments)

When no task ID is provided, display the currently focused task:

1. Use `TaskList` to get all tasks
2. Find tasks with `status: in_progress`
3. Display the focused task details

If no task is in progress:
```
No task currently focused.

Use /workflow-focus <task-id> to set focus, or /workflow-next to get a suggestion.
```

If a task is focused:
```
Current Focus: #3

Subject: Implement user authentication
Status: in_progress
Owner: agent-1

Description:
Add JWT-based authentication with login/logout endpoints...

Blocked by: (none)
Blocks: #5, #6
```

### Mode 2: Set Focus (with task ID argument)

When user provides a task ID (e.g., `/workflow-focus 3`):

1. **Get task details** using `TaskGet` with the provided ID
2. **Validate task exists** - if not found, inform user
3. **Check if blocked** - warn if task has unresolved blockers
4. **Set focus** using `TaskUpdate`:
   - Set `status: in_progress` on the target task
5. **Display task details** showing what's now focused

Example output:
```
Focus set to #3: Implement user authentication

Status: in_progress
Description: Add JWT-based authentication...

Dependencies:
  Blocked by: (none - ready to work)
  Blocks: #5 (Deploy), #6 (User docs)

Ready to begin work on this task.
```

### Save Checkpoint After Focus Change (PERSIST-001)

After setting or displaying focus, save the current task state:

1. Output: `Saving session checkpoint...`
2. Use `TaskList` to get the latest task state
3. Use `Write` to save to `CHECKPOINT_PATH` (determined in Session Checkpoint Path section) with:
   - `schema_version`: `"1.0.0"`
   - `updated_at`: current ISO-8601 timestamp
   - `session_state`: `"active"`
   - `tasks`: array of all tasks with id, subject, description, status, blockedBy, blocks, owner, metadata
4. Output: `Session checkpoint saved.`

This captures the `in_progress` status change to disk, ensuring recovery after a crash mid-task.

## Focus Discipline

**One Active Task Rule**: Maintain single-task focus per session.
- Setting focus on a new task means you're committing to it
- Complete or explicitly pause before switching
- Prevents context switching and multitasking
- Aligns with "Always Be Shipping" philosophy

## Handling Blocked Tasks

If the requested task has blockers:
```
Warning: Task #5 is blocked by:
  - #3: Implement user authentication (in_progress)
  - #4: Add input validation (pending)

Consider focusing on a blocker first, or use /workflow-next for suggestions.
```

## Success Criteria

Focus is properly set when:
- `TaskList` shows the task with `status: in_progress`
- Task details are displayed clearly
- Dependencies are understood
- Next actions are identified

## Tips

- Use `/workflow-next` to get smart task suggestions
- Use `/workflow-dash` to see the full project state
- Mark tasks complete with `TaskUpdate` when done

## Shared State Integration

After setting or displaying focus, update workflow state:

```bash
mkdir -p .pipeline-state/workflow
```

Write `.pipeline-state/workflow/task-focus.json` (atomic write via `.tmp` + rename):
```json
{
  "focused_task_id": "<task-id or null>",
  "focused_task_subject": "<subject>",
  "focused_at": "<ISO-8601>",
  "last_updated": "<ISO-8601>"
}
```

If `.pipeline-state/` does not exist or write fails, log warning and continue — this is non-blocking.

## Inputs

- `SESSION_ID` (optional) — If provided, scopes all checkpoint reads/writes to `~/.claude/sessions/<SESSION_ID>-tasks.json`. Without it, falls back to `~/.claude/sessions/workflow-tasks.json`. Passed automatically by auto-orchestrate and session-manager.
- `task_id` (optional) — The task ID to focus on. If omitted, shows current focus.
