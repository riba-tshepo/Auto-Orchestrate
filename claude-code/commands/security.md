---
name: security
description: Guide the user through Security & Compliance processes (P-038 to P-043).
---

# /security — Security & Compliance

Guides execution of Security and Compliance processes using security-engineer and infra-engineer agents.

## Processes Covered

| Process ID | Name | Owner | Description |
|------------|------|-------|-------------|
| P-038 | Threat Modeling | security-engineer | Security Champion runs a STRIDE-based threat model for every new feature before development begins. AppSec reviews the output. No CRITICAL findings can be unresolved before feature development proceeds. |
| P-039 | SAST/DAST CI Integration | security-engineer + infra-engineer | Static Analysis Security Testing (SAST) and Dynamic Analysis Security Testing (DAST) scans integrated into the CI/CD pipeline. CRITICAL and HIGH findings block merge. |
| P-040 | CVE Triage | security-engineer | Security Champion reviews dependency update PRs for CVEs before approving. HIGH and CRITICAL CVEs escalate to AppSec immediately. Dependency update PRs cannot be merged with unreviewed HIGH/CRITICAL CVEs. |
| P-041 | Security Exception | security-engineer | Formal review and approval path for any deviation from security standards. AppSec reviews, CISO approves, Engineering Director is informed. Time-bounded exceptions only. |
| P-042 | Compliance Review | security-engineer | GRC team runs SOC 2 / ISO 27001 / GDPR compliance reviews on defined schedules and against new data-handling features. Findings tracked to closure with named owners and deadlines. |
| P-043 | Security Champions Training | security-engineer | AppSec Lead runs quarterly training for all Security Champions covering the current threat landscape, OWASP Top 10 updates, tool usage, and recent CVE patterns relevant to the codebase. |

## Agents

- **security-engineer**: Owns security reviews, vulnerability assessments, and compliance audits
- **infra-engineer**: Co-owns SAST/DAST pipeline integration (P-039)

## When to Use

Use /security when:
- Running security reviews before release
- Performing vulnerability assessments
- Managing compliance requirements
- Setting up SAST/DAST pipelines

## How to Use

1. Select the process you need from the table above
2. The command will route to security-engineer or infra-engineer as appropriate
3. Follow process steps in `claude-code/processes/06_security_compliance.md`

## Dispatch Mode

When invoked via the Command Dispatcher (a dispatch context file exists at the invoking session's `dispatch-receipts/dispatch-context-TRIG-*.json`), operate in dispatch mode:

1. **Skip interactive guidance** — Do not present process menus or ask for user selection
2. **Read dispatch context** — Parse the dispatch context file for `trigger_id`, `stage`, `condition_summary`, and `relevant_artifacts`
3. **Focused analysis** — Analyze only the processes relevant to the trigger (typically P-038 Threat Modeling for TRIG-001/TRIG-009, or the specific flagged process)
4. **Structured output** — Produce findings in this format:

```
## Dispatch Findings

**Trigger**: <trigger_id> (<process_ids>)
**Severity**: <max severity across findings>
**Findings Count**: <N>

### Finding <N>: <title>
- **Process**: <process_id> (<process_name>)
- **Severity**: HIGH | CRITICAL
- **Location**: <file, endpoint, or component>
- **Recommendation**: <actionable fix>
- **Stage Impact**: Stage <N> (<what must change>)

## Recommended Next Action
- **Type**: inject_into_stage | create_task | gate_block
- **Target Stage**: <N>
- **Instruction**: <what the target stage must address>
```

5. **Return immediately** — Do not wait for user input. The loop controller creates the dispatch receipt from this output.

See `_shared/protocols/command-dispatch.md` for the full dispatch protocol.

## Receipt Writing (STATE-001)

After completing analysis (standalone or dispatch mode), write a receipt:

1. `mkdir -p .pipeline-state/command-receipts .pipeline-state/process-log`
2. Generate receipt ID: `security-<YYYYMMDD>-<HHMMSS>`
3. Write `.pipeline-state/command-receipts/security-<YYYYMMDD>-<HHMMSS>.json`:

```json
{
  "command": "security",
  "receipt_id": "security-<YYYYMMDD>-<HHMMSS>",
  "timestamp": "<ISO-8601>",
  "session_context": {
    "session_id": "<dispatch session_id or null>",
    "pipeline": "<auto-orchestrate|auto-audit|auto-debug|standalone>"
  },
  "inputs": {
    "mode": "<standalone|dispatch>",
    "process_ids": ["P-038", "P-039"]
  },
  "outputs": {
    "findings": [{"process": "P-038", "severity": "HIGH", "title": "..."}],
    "severity_max": "HIGH"
  },
  "artifacts": [],
  "processes_executed": ["P-038", "P-039"],
  "next_recommended_action": null,
  "dispatch_context": {
    "trigger_id": "<TRIG-XXX or null>",
    "invoked_by": "<session_id or null>"
  }
}
```

4. For each process executed, append to `.pipeline-state/process-log/<process-id>.jsonl` (STATE-003):
```json
{"process_id":"P-038","command_source":"security","session_id":"...","timestamp":"...","result":"completed","artifacts_produced":[],"receipt_id":"security-<YYYYMMDD>-<HHMMSS>"}
```

If `.pipeline-state/` does not exist, create via `mkdir -p`. If write fails, log warning and continue — receipt writing MUST NOT block command execution.

See `_shared/protocols/cross-pipeline-state.md` for the full receipt schema.

## Related Commands

- `/release-prep` — Pre-release security gate
- `/gate-review` — Security acceptance criteria

## Process Reference

Full process definitions: `claude-code/processes/06_security_compliance.md`
