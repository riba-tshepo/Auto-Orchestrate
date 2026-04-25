---
name: risk
description: Guide the user through Risk & Change Management processes (P-074 to P-077).
---

# /risk — Risk & Change Management

Guides execution of Risk and Change Management processes using technical-program-manager and engineering-manager agents.

## Processes Covered

| Process ID | Process Name | Primary Agent | Lifecycle Stage |
|------------|--------------|---------------|-----------------|
| P-074 | RAID Log Maintenance Process | technical-program-manager | Continuous |
| P-075 | Risk Register at Scope Lock Process | technical-program-manager | Gate 2 (Scope Lock) |
| P-076 | Pre-Launch Risk Review Process (CAB) | engineering-manager | Gate 4 (Pre-Launch) |
| P-077 | Quarterly Risk Review Process | technical-program-manager | Continuous (quarterly) |

## Agents

- **technical-program-manager**: Owns RAID log management and risk mitigation planning (P-074, P-075, P-077)
- **engineering-manager**: Owns Change Advisory Board (CAB) and change control processes (P-076)

## When to Use

Use `/risk` when you need to:
- Maintain or review the RAID (Risks, Assumptions, Issues, Dependencies) log
- Document risk register at scope lock (Gate 2)
- Prepare for or conduct a Change Advisory Board review before release
- Perform quarterly risk review and update risk mitigation plans
- Assess risk acceptance criteria for gate reviews

## Dispatch Mode

When invoked via the Command Dispatcher (a dispatch context file exists at the invoking session's `dispatch-receipts/dispatch-context-TRIG-*.json`), operate in dispatch mode:

1. **Skip interactive guidance** — Do not present process menus or ask for user selection
2. **Read dispatch context** — Parse the dispatch context file for `trigger_id`, `stage`, `condition_summary`, and `relevant_artifacts`
3. **Focused analysis** — Analyze only the processes relevant to the trigger (typically P-074 RAID Log for TRIG-007 CRITICAL items, or specific flagged processes)
4. **Structured output** — Produce findings in this format:

```
## Dispatch Findings

**Trigger**: <trigger_id> (<process_ids>)
**Severity**: <max severity across findings>
**Findings Count**: <N>

### Finding <N>: <title>
- **Process**: <process_id> (<process_name>)
- **Severity**: HIGH | CRITICAL
- **Category**: Risk | Assumption | Issue | Dependency
- **Impact**: <what happens if unaddressed>
- **Mitigation**: <recommended action>
- **Stage Impact**: Stage <N> (<what must change>)

## Recommended Next Action
- **Type**: inject_into_stage | gate_block
- **Target Stage**: <N>
- **Instruction**: <what the target stage must address>
```

5. **Return immediately** — Do not wait for user input. The loop controller creates the dispatch receipt from this output.

See `_shared/protocols/command-dispatch.md` for the full dispatch protocol.

## Receipt Writing (STATE-001)

After completing analysis (standalone or dispatch mode), write a receipt:

1. `mkdir -p .pipeline-state/command-receipts .pipeline-state/process-log`
2. Write `.pipeline-state/command-receipts/risk-<YYYYMMDD>-<HHMMSS>.json`:

```json
{
  "command": "risk",
  "receipt_id": "risk-<YYYYMMDD>-<HHMMSS>",
  "timestamp": "<ISO-8601>",
  "session_context": {
    "session_id": "<dispatch session_id or null>",
    "pipeline": "<auto-orchestrate|auto-audit|auto-debug|standalone>"
  },
  "inputs": {
    "mode": "<standalone|dispatch>",
    "process_ids": ["P-074", "P-075"]
  },
  "outputs": {
    "findings": [{"process": "P-074", "severity": "HIGH", "title": "..."}],
    "risk_items": [{"category": "Risk", "severity": "HIGH", "mitigation": "..."}],
    "severity_max": "HIGH"
  },
  "artifacts": [],
  "processes_executed": ["P-074", "P-075"],
  "next_recommended_action": null,
  "dispatch_context": {
    "trigger_id": "<TRIG-XXX or null>",
    "invoked_by": "<session_id or null>"
  }
}
```

3. For each process executed, append to `.pipeline-state/process-log/<process-id>.jsonl` (STATE-003).

If write fails, log warning and continue — receipt writing MUST NOT block command execution. See `_shared/protocols/cross-pipeline-state.md` for the full receipt schema.

## Related Commands

- `/new-project` — RAID log initialized in Phase 2 (P-074)
- `/release-prep` — CAB review required before release (P-076)
- `/gate-review` — Risk acceptance as gate criteria

## Process Reference

Full process definitions: `~/.claude/processes/13_risk_change_management.md`

## Usage

```
/risk
```

What risk or change management activity do you need help with? I can:
- Facilitate RAID log updates
- Prepare risk register for scope lock
- Conduct CAB review for change approval
- Run quarterly risk assessment
- Generate risk mitigation plans
