# Command Conventions

## PROGRESS-001 — Standard Progress Output Format

All commands use this format for progress output:

```
[<COMMAND>] [<STEP>] <message>
```

Examples:
- `[AUTO-ORC] [STEP 3] Spawning orchestrator — iteration 5 of 100`
- `[AUTO-DBG] [STEP 3] Spawning debugger — iteration 3 of 50`
- `[AUTO-AUD] [STEP 3] Spawning auditor — cycle 2 of 5`

Prefix codes:

| Command | Prefix |
|---------|--------|
| auto-orchestrate | `AUTO-ORC` |
| auto-debug | `AUTO-DBG` |
| auto-audit | `AUTO-AUD` |

Commands should reference this file in their PROGRESS-001 rule: "See `commands/CONVENTIONS.md` for format."
