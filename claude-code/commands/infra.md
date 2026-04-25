---
name: infra
description: Guide the user through Infrastructure & Platform processes (P-044 to P-048).
---

# /infra — Infrastructure & Platform

Guides execution of Infrastructure and Platform processes using infra-engineer and sre agents.

## Processes Covered

| Process ID | Name | Owner | Description |
|------------|------|-------|-------------|
| P-044 | Golden Path Adoption | infra-engineer | Create and maintain CI/CD templates as the default path for new services. The golden path must be the easiest option -- not the only option. Adoption is measured quarterly via developer NPS. |
| P-045 | Infrastructure Provisioning | infra-engineer | All cloud resources provisioned via Infrastructure as Code (IaC). Manual provisioning is a policy violation. All IaC changes reviewed before apply. |
| P-046 | Environment Self-Service | infra-engineer | Developers request and provision environments via the developer portal (Backstage/Port) without raising tickets. Reduces cognitive load and eliminates ticket queue delays. |
| P-047 | Cloud Architecture Review Board (CARB) | infra-engineer | Weekly review of new cloud service adoptions, architecture pattern changes, and cost commitments above defined thresholds. Prevents ungoverned cloud sprawl, vendor lock-in, security gaps, and cost overruns. |
| P-048 | Production Release Management | sre | Structured release process ensuring all quality, security, and reliability gates pass before production deployment. Release Manager owns the go/no-go decision. No release proceeds without explicit authorization. |

## Agents

- **infra-engineer**: Owns platform building (CI/CD, golden paths, DX) and cloud provisioning (IaC, IAM, FinOps, cost optimization) — P-044 through P-047
- **sre**: Owns production release management and reliability — P-048

## When to Use

Use /infra when:
- Provisioning or modifying infrastructure
- Managing cloud resources
- Setting up monitoring and alerting
- Running infrastructure health checks

## How to Use

1. Select the process you need from the table above
2. The command will route to infra-engineer or sre as appropriate
3. Follow process steps in `claude-code/processes/07_infrastructure_platform.md`

## Dispatch Mode

When invoked via the Command Dispatcher (a dispatch context file exists at the invoking session's `dispatch-receipts/dispatch-context-TRIG-*.json`), operate in dispatch mode:

1. **Skip interactive guidance** — Do not present process menus or ask for user selection
2. **Read dispatch context** — Parse the dispatch context file for `trigger_id`, `stage`, `condition_summary`, and `relevant_artifacts`
3. **Focused analysis** — Analyze only the processes relevant to the trigger (typically P-044/P-045 for TRIG-003/TRIG-011 infrastructure issues, or specific flagged processes)
4. **Structured output** — Produce findings in this format:

```
## Dispatch Findings

**Trigger**: <trigger_id> (<process_ids>)
**Severity**: <max severity across findings>
**Findings Count**: <N>

### Finding <N>: <title>
- **Process**: <process_id> (<process_name>)
- **Severity**: HIGH | CRITICAL
- **Location**: <infrastructure component, config file, or deployment target>
- **Recommendation**: <actionable infrastructure fix>
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
2. Write `.pipeline-state/command-receipts/infra-<YYYYMMDD>-<HHMMSS>.json`:

```json
{
  "command": "infra",
  "receipt_id": "infra-<YYYYMMDD>-<HHMMSS>",
  "timestamp": "<ISO-8601>",
  "session_context": {
    "session_id": "<dispatch session_id or null>",
    "pipeline": "<auto-orchestrate|auto-audit|auto-debug|standalone>"
  },
  "inputs": {
    "mode": "<standalone|dispatch>",
    "process_ids": ["P-044", "P-045"]
  },
  "outputs": {
    "findings": [{"process": "P-044", "severity": "HIGH", "title": "..."}],
    "severity_max": "HIGH"
  },
  "artifacts": [],
  "processes_executed": ["P-044", "P-045"],
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

- `/release-prep` — Infrastructure readiness for release (P-048)
- `/post-launch` — Post-launch infrastructure monitoring

## Process Reference

Full process definitions: `claude-code/processes/07_infrastructure_platform.md`
