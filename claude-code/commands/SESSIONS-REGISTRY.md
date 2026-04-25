# Sessions Registry

**Purpose**: Cross-command session index providing a shared view of all active and historical sessions across `auto-orchestrate`, `auto-debug`, and `auto-audit` within a project.

---

## Directory Layout

```
<project-root>/
  .sessions/
    index.json        # Cross-command session registry (this file)
```

The `.sessions/` directory is created at the project root (same level as `.orchestrate/`, `.debug/`, `.audit/`).

---

## Registry File: `.sessions/index.json`

### Format

```json
{
  "schema_version": "1.0.0",
  "sessions": [
    {
      "session_id": "auto-orc-2026-03-29-myproject",
      "command": "auto-orchestrate",
      "start_time": "2026-03-29T10:00:00Z",
      "status": "in_progress",
      "working_dir": "/home/user/projects/myproject"
    },
    {
      "session_id": "auto-dbg-2026-03-29-nullpointer",
      "command": "auto-debug",
      "start_time": "2026-03-29T11:30:00Z",
      "status": "complete",
      "working_dir": "/home/user/projects/myproject"
    }
  ]
}
```

### Required Fields Per Entry

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | string | Unique session identifier (e.g. `auto-orc-YYYY-MM-DD-slug`) |
| `command` | string | One of: `auto-orchestrate`, `auto-debug`, `auto-audit` |
| `start_time` | string | ISO 8601 UTC timestamp |
| `status` | string | One of: `in_progress`, `complete`, `superseded`, `failed` |
| `working_dir` | string | Absolute path to project root at session start |

---

## Read/Write Protocol

### On Session Start (Step 2c of each command)

1. Create `.sessions/` if it does not exist: `mkdir -p .sessions`
2. Create `.sessions/index.json` if it does not exist (with `{"schema_version": "1.0.0", "sessions": []}`)
3. Append a new entry with `status: "in_progress"` to `sessions[]`
4. Write the updated JSON back atomically (write to `.sessions/index.tmp.json`, then rename)

### On Session Supersede (Step 2b of each command)

1. Read `.sessions/index.json`
2. For each entry matching the session being superseded: set `status: "superseded"`, add `"superseded_at"` (ISO 8601)
3. Write updated JSON atomically

### On Session Completion or Failure

1. Read `.sessions/index.json`
2. Update own entry to `status: "complete"` or `status: "failed"`
3. Write updated JSON atomically

---

## Concurrent Access and Cross-Command Collision Detection

- Before superseding local sessions (Step 2b), read `.sessions/index.json` to detect active sessions from OTHER commands in the same `working_dir`
- If a session from a different command is `in_progress` in the same project: log `[CROSS-002] Cross-command session detected: <session_id> (<command>) is in_progress — proceed with caution`
- Do NOT automatically supersede sessions from other commands — only log the warning

---

*This file is referenced in the crash recovery and session supersede sections of `auto-orchestrate.md`, `auto-debug.md`, and `auto-audit.md`.*
