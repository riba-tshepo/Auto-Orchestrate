---
name: workflow-next
description: |
  Get intelligent next task suggestion based on dependencies and state.
  Use when user says "next", "next task", "what's next", "suggest task", "what should I work on".
triggers:
  - next
  - next task
  - what's next
  - suggest task
  - what should I work on
  - what to do next
---

# Next Task Suggestion

Get intelligent task recommendations based on dependencies and current state.

## Session Checkpoint Path

Determine the checkpoint file path based on session context:

1. If `SESSION_ID` is provided AND `.orchestrate/` exists in cwd (auto-orchestrate context): use `.orchestrate/<SESSION_ID>/tasks.json` (primary)
2. If `SESSION_ID` is provided but `.orchestrate/` does NOT exist (standalone usage): use `~/.claude/sessions/<SESSION_ID>-tasks.json` (legacy fallback)
3. If `SESSION_ID` is NOT provided (standalone usage): use `~/.claude/sessions/workflow-tasks.json` (legacy fallback)

Store this resolved path as `CHECKPOINT_PATH` for use in all subsequent steps.

## Usage Modes

### Mode 1: Show Suggestion Only (default)

Display next recommended task with reasoning.

### Mode 2: Auto-Focus (with --auto-focus flag)

Automatically set focus to the suggested task.

## Step 1: Get Task State

Use `TaskList` to retrieve all tasks.

## Step 2: Analyze and Rank

Filter and rank tasks using these criteria:

**Eligible Tasks** (must meet ALL):
- Status is `pending`
- `blockedBy` is empty (not blocked)

**Ranking Criteria** (in order of importance):
1. **Unblocks others**: Tasks that appear in other tasks' `blockedBy` arrays
2. **Dependencies resolved**: Tasks whose blockers were recently completed
3. **Task order**: Earlier task IDs (suggests logical ordering)

## Step 3: Generate Recommendation

Present the top suggestion with reasoning:

```
=== Next Task Suggestion ===

Recommended: #4 - Add input validation

Reasoning:
  - Unblocked and ready to start
  - Blocks 2 other tasks (#5, #6)
  - Completing this will enable more parallel work

Details:
  Status: pending
  Description: Add validation for user input fields...

Use /workflow-focus 4 to start working on this task.
```

If no eligible tasks:
```
No eligible tasks found.

Possible reasons:
  - All tasks are completed
  - All pending tasks are blocked
  - No tasks have been created

Check /workflow-dash for full status, or create new tasks with TaskCreate.
```

## Step 4: Auto-Focus (if requested)

When `--auto-focus` is specified:

1. Use `TaskUpdate` to set the suggested task to `status: in_progress`
2. Display confirmation:

```
Auto-focused on #4: Add input validation

Status: in_progress
Ready to begin work.
```

### Save Checkpoint After Auto-Focus (PERSIST-001)

When auto-focus is used (tasks are mutated), save the current task state:

1. Use `TaskList` to get the latest task state
2. Use `Write` to save to `CHECKPOINT_PATH` (determined in Session Checkpoint Path section) with:
   - `schema_version`: `"1.0.0"`
   - `updated_at`: current ISO-8601 timestamp
   - `session_state`: `"active"`
   - `tasks`: array of all tasks with id, subject, description, status, blockedBy, blocks, owner, metadata

Only save when tasks are mutated (auto-focus mode). Read-only suggestions do not require a checkpoint save.

## Alternative Suggestions

If the top suggestion isn't ideal, show alternatives:

```
Alternative options:
  #7: Setup CI/CD (unblocks #8)
  #9: Add logging (no blockers)
```

## Intelligent Suggestions

The `next` command considers:
- **Dependencies**: Only suggests unblocked tasks
- **Impact**: Prefers tasks that unblock others
- **Progress**: Favors completing task chains
- **Status**: Only pending tasks (not in_progress or completed)

## Success Criteria

Next task suggestion is successful when:
- Valid unblocked task is suggested
- Reasoning is clear and actionable
- Impact on other tasks is explained
- User can immediately start work

## Tips

- Run `/workflow-dash` first to understand project context
- Use `/workflow-focus <id>` to override the suggestion
- Check blocked tasks to understand dependencies

## Inputs

- `SESSION_ID` (optional) — If provided, scopes all checkpoint reads/writes to `~/.claude/sessions/<SESSION_ID>-tasks.json`. Without it, falls back to `~/.claude/sessions/workflow-tasks.json`. Passed automatically by auto-orchestrate and session-manager.
