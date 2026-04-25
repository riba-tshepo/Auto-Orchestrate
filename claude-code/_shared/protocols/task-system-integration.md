# Task System Integration Reference

This reference defines portable task management using Claude Code's native task tools.
Skills and templates SHOULD reference this file for consistent task handling.

---

## Subagent Availability Warning

**CRITICAL**: TaskCreate, TaskList, TaskUpdate, and TaskGet are ONLY available to the **auto-orchestrate loop** (main Claude Code instance). They are **NOT available** to any subagent (orchestrator, product-manager, software-engineer, technical-writer, session-manager).

Subagents MUST use the file-based task proposal protocol instead:
- **To propose tasks**: Write to `.orchestrate/<session-id>/proposed-tasks.json`
- **To read task state**: Parse the `## Current Task State` section from the spawn prompt
- **To propose updates**: Include `PROPOSED_ACTIONS` JSON block in return value

See `claude-code/_shared/references/TOOL-AVAILABILITY.md` for complete details.

---

## Claude Code Native Task Tools

### TaskList
Get all tasks with status overview.

```
TaskList
```

**Purpose**: View all tasks, their status, dependencies, and ownership.

### TaskGet
Get full details of a specific task.

```
TaskGet(taskId="1")
```

**Purpose**: Get complete task context including description and dependencies.

### TaskCreate
Create a new task.

```
TaskCreate(
  subject="Task title",
  description="Detailed description",
  activeForm="Working on task"
)
```

**Purpose**: Add a new task to track work.

### TaskUpdate
Update task status or properties.

```
TaskUpdate(taskId="1", status="in_progress")
TaskUpdate(taskId="1", status="completed")
TaskUpdate(taskId="2", addBlockedBy=["1"])
```

**Purpose**: Change task status, set focus, mark complete, or add dependencies.

---

## Task Lifecycle

### Starting Work
1. Use `TaskList` to see available tasks
2. Use `TaskUpdate` with `status: in_progress` to set focus

### During Work
1. Use `TaskGet` to review task details
2. Track blockers with `addBlockedBy`

### Completing Work
1. Use `TaskUpdate` with `status: completed` to mark done
2. Blocked tasks automatically become unblocked

---

## Token Mapping (Legacy to Native)

For skills using legacy token placeholders:

| Token | Claude Code Native |
|-------|-------------------|
| `{{TASK_SHOW}}` | `TaskGet` |
| `{{TASK_FOCUS}}` | `TaskUpdate` (status: in_progress) |
| `{{TASK_COMPLETE}}` | `TaskUpdate` (status: completed) |
| `{{TASK_LIST}}` | `TaskList` |
| `{{TASK_ADD}}` | `TaskCreate` |
| `{{OUTPUT_DIR}}` | `claudedocs/research-outputs` |
| `{{MANIFEST_PATH}}` | `{{OUTPUT_DIR}}/MANIFEST.jsonl` |

---

## Usage in Skills

Reference this file from SKILL.md:

```markdown
### Task System Integration

@_shared/protocols/task-system-integration.md

Execute lifecycle:
1. Get task: Use `TaskGet` with task ID
2. Set focus: Use `TaskUpdate` with status: in_progress
3. Complete: Use `TaskUpdate` with status: completed
```

---

## Usage in Templates

Include task lifecycle section in templates:

```markdown
### Task Lifecycle

1. MUST get task details: Use `TaskGet`
2. MUST set focus: Use `TaskUpdate` (status: in_progress)
3. MUST complete task: Use `TaskUpdate` (status: completed)
```

---

## Task Persistence Protocol
## Task Persistence Protocol

Tasks managed by Claude Code's native `TaskCreate`/`TaskList`/`TaskUpdate` tools are **conversation-scoped** — they are lost if the conversation ends unexpectedly or Claude Code crashes. The persistence protocol provides crash recovery through session-scoped checkpoint files.

### Checkpoint File

- **Primary Path**: `.orchestrate/<session-id>/tasks.json` (project-local, when SESSION_ID and `.orchestrate/` available)
- **Legacy Fallback Path**: `~/.claude/sessions/<session-id>-tasks.json` (read-only crash recovery)
- **Standalone Fallback**: `~/.claude/sessions/workflow-tasks.json` (backward compatibility when no session ID)
- **Format**: JSON with schema version, timestamp, session state, session ID, and full task array

```json
{
  "schema_version": "1.0.0",
  "session_id": "<session-id>",
  "updated_at": "<ISO-8601>",
  "session_state": "active",
  "tasks": [
    {
      "id": "abc123",
      "subject": "Task title",
      "description": "Detailed description",
      "status": "pending|in_progress|completed",
      "blockedBy": [],
      "blocks": [],
      "owner": null,
      "metadata": {}
    }
  ]
}
```

### PERSIST-001: Save Checkpoint After Task Reads (Session-Aware)

After any `TaskList` call in a workflow command, MUST save the current task state to a session-scoped checkpoint file. Use the `Write` tool to write the JSON checkpoint. Set `session_state` to `"active"` during normal operation.

**Session-Scoped Path Pattern**:
- If `SESSION_ID` is available AND `.orchestrate/` exists in cwd: `.orchestrate/<SESSION_ID>/tasks.json` (primary)
- If `SESSION_ID` is available but `.orchestrate/` does NOT exist: `~/.claude/sessions/<SESSION_ID>-tasks.json` (legacy fallback)
- If `SESSION_ID` is NOT available (backward compatibility): `~/.claude/sessions/workflow-tasks.json`

**Implementation**:
```python
# Determine checkpoint path based on session context
import os
if SESSION_ID and os.path.exists('.orchestrate'):
    checkpoint_path = f".orchestrate/{SESSION_ID}/tasks.json"
    legacy_path = f"~/.claude/sessions/{SESSION_ID}-tasks.json"  # read-only fallback only
elif SESSION_ID:
    checkpoint_path = f"~/.claude/sessions/{SESSION_ID}-tasks.json"
else:
    checkpoint_path = "~/.claude/sessions/workflow-tasks.json"  # standalone fallback

# Write checkpoint
Write(checkpoint_path, {
    "schema_version": "1.0.0",
    "session_id": SESSION_ID or null,
    "updated_at": "<ISO-8601>",
    "session_state": "active",
    "tasks": task_list
})
```

### PERSIST-002: Restore on Empty Session (Session-Aware)

On session start (`workflow-start`), if `TaskList` returns empty:
1. Determine checkpoint path:
   - If `SESSION_ID` exists AND `.orchestrate/` in cwd: Check `.orchestrate/<SESSION_ID>/tasks.json` (primary)
   - If primary not found: Check `~/.claude/sessions/<SESSION_ID>-tasks.json` (legacy fallback, read-only)
   - If NOT found or no `SESSION_ID`: Fall back to `~/.claude/sessions/workflow-tasks.json`
2. If checkpoint exists and `session_state` is `"active"`:
   - Recreate each task via `TaskCreate` (subject, description, activeForm)
   - Restore dependencies via `TaskUpdate` (addBlockedBy, addBlocks)
   - Restore status via `TaskUpdate` (status: in_progress or completed)
3. Display recovery message: `"Restored N tasks from session <session-id>"`

**Implementation**:
```python
# Determine which checkpoint to restore
import os
if SESSION_ID and os.path.exists('.orchestrate'):
    primary_checkpoint = f".orchestrate/{SESSION_ID}/tasks.json"
    legacy_checkpoint = f"~/.claude/sessions/{SESSION_ID}-tasks.json"  # read-only fallback
    fallback_checkpoint = "~/.claude/sessions/workflow-tasks.json"
elif SESSION_ID:
    primary_checkpoint = f"~/.claude/sessions/{SESSION_ID}-tasks.json"
    legacy_checkpoint = None
    fallback_checkpoint = "~/.claude/sessions/workflow-tasks.json"
else:
    primary_checkpoint = "~/.claude/sessions/workflow-tasks.json"
    legacy_checkpoint = None
    fallback_checkpoint = None

# Try primary, then fallback
try:
    checkpoint_data = Read(primary_checkpoint)
except FileNotFoundError:
    if fallback_checkpoint:
        checkpoint_data = Read(fallback_checkpoint)
    else:
        # No checkpoint available
        checkpoint_data = None

# Restore tasks if checkpoint exists
if checkpoint_data and checkpoint_data["session_state"] == "active":
    for task in checkpoint_data["tasks"]:
        TaskCreate(...)
        TaskUpdate(...)
```

### PERSIST-003: Atomic Write (Session-Aware)

When saving checkpoints, MUST write the complete JSON content in a single `Write` tool call to the session-scoped checkpoint path. This ensures the file is always in a valid state.

**Path determination follows PERSIST-001 rules**:
- Primary (with SESSION_ID + .orchestrate/): `.orchestrate/<SESSION_ID>/tasks.json`
- Legacy fallback (with SESSION_ID, no .orchestrate/): `~/.claude/sessions/<SESSION_ID>-tasks.json`
- Standalone fallback: `~/.claude/sessions/workflow-tasks.json`
---

## Task Count Limits

System-wide caps to prevent unbounded task creation from exhausting the context window.

| ID | Rule | Compliance |
|----|------|------------|
| LIMIT-001 | Total tasks (all statuses) MUST NOT exceed **50**. Before any `TaskCreate`, check `TaskList` count. If >= 50, refuse creation and log `[LIMIT-001] Task cap reached (50)`. Consolidate remaining work into fewer, broader tasks | Required |
| LIMIT-002 | Active (non-completed) tasks MUST NOT exceed **30**. Before any `TaskCreate`, count non-completed tasks. If >= 30, refuse creation and log `[LIMIT-002] Active task cap reached (30)` | Required |
| LIMIT-003 | The auto-orchestrate loop MUST check LIMIT-001 and LIMIT-002 before every TaskCreate call (it is the sole entity with TaskCreate access). Subagents limit themselves to 20 tasks per proposal file | Required |
| LIMIT-004 | User MAY override `MAX_TASKS` via auto-orchestrate `max_tasks` argument (cap: 100). Override does not affect `MAX_ACTIVE_TASKS` (30) | Optional |

### Default Constants

| Constant | Default | Description |
|----------|---------|-------------|
| `MAX_TASKS` | 50 | Total task cap (all statuses) |
| `MAX_ACTIVE_TASKS` | 30 | Non-completed task cap |

---

## Continuation Depth Limits

Caps on continuation chains to prevent unbounded spawning from partial task results.

| ID | Rule | Compliance |
|----|------|------------|
| CONT-001 | Every continuation task MUST carry `CONTINUATION_DEPTH: N` and `ORIGINAL_TASK_ID: <id>` in its description. Original task = depth 0; each continuation increments depth by 1 | Required |
| CONT-002 | Continuation depth MUST NOT exceed **3**. At depth 3, mark task as completed with note "Continuation depth limit reached — consolidate remaining work manually". Log `[CONT-002] Max continuation depth (3) reached for ORIGINAL_TASK_ID: <id>`. Do NOT create another continuation | Required |
| CONT-003 | Callers creating continuation tasks MUST propagate `ORIGINAL_TASK_ID`, `CONTINUATION_DEPTH`, and `needs_followup` to the new task description | Required |

### Default Constants

| Constant | Default | Description |
|----------|---------|-------------|
| `MAX_CONTINUATION_DEPTH` | 3 | Maximum continuation chain length |

---

## TaskList Size Guard

Compact processing mode when task count grows large, preventing TaskList responses from exhausting context.

| ID | Rule | Compliance |
|----|------|------------|
| GUARD-001 | When `TaskList` returns >**25** tasks, agents MUST use summary mode instead of processing the full list | Required |
| GUARD-002 | In summary mode: count tasks by status, extract ONLY `in_progress` tasks + unblocked `pending` tasks (empty `blockedBy`). Ignore completed tasks entirely. Log `[GUARD-002] Summary mode: N completed, M in_progress, P pending (Q unblocked)` | Required |
| GUARD-003 | During orchestrator boot, if >25 tasks: record summary counts only, process only actionable tasks in the execution loop. Do NOT iterate over completed tasks | Required |

### Default Constants

| Constant | Default | Description |
|----------|---------|-------------|
| `TASKLIST_SUMMARY_THRESHOLD` | 25 | Task count triggering summary mode |

---

## External System Configurations

### Linear

```yaml
TASK_SHOW: "linear issue view"
TASK_FOCUS: "linear issue update --status in-progress"
TASK_COMPLETE: "linear issue update --status done"
```

### Jira

```yaml
TASK_SHOW: "jira issue view"
TASK_FOCUS: "jira issue move --status 'In Progress'"
TASK_COMPLETE: "jira issue move --status 'Done'"
```

### GitHub Issues

```yaml
TASK_SHOW: "gh issue view"
TASK_FOCUS: "gh issue edit --add-label 'in-progress'"
TASK_COMPLETE: "gh issue close"
```
