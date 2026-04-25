---
name: qa
description: Guide the user through Quality Assurance & Testing processes (P-032 to P-037).
---

# /qa — Quality Assurance & Testing

Guides execution of QA and testing processes using qa-engineer and software-engineer agents.

## Processes Covered

| Process ID | Name | Owner | Description |
|------------|------|-------|-------------|
| P-032 | Test Architecture Design | qa-engineer | Design the test coverage strategy for a project — unit, integration, contract, performance — aligned to the deliverable Definition of Done established at Stage 2 (Scope Contract). |
| P-033 | Automated Test Framework | qa-engineer | SDET implements automated test suites integrated into the CI/CD pipeline so that all automated tests run on every pull request. Test failures block merge. |
| P-034 | Definition of Done Enforcement | qa-engineer | Verify all Definition of Done criteria before a story is counted as complete. CI gates enforce all automatable criteria. Human verification is required for criteria that cannot be automated. |
| P-035 | Performance Testing | qa-engineer | Establish performance baselines before optimization and validate P50/P95/P99 latency against SLOs before release. Performance testing is part of the Definition of Done for performance-sensitive deliverables. |
| P-036 | Acceptance Criteria Verification | software-engineer | PM or QA formally verifies each story against its acceptance criteria before story closure. This is the final human gate before a story enters the "done" column. |
| P-037 | Contract Testing | qa-engineer | Validate API contracts between services on every PR that touches API definitions. Prevent consumer services from breaking when provider APIs change. |

## Agents

- **qa-engineer**: Owns test planning, test execution, defect management, and quality metrics
- **software-engineer**: Supports unit testing and code coverage processes

## When to Use

Use /qa when:
- Creating or executing test plans
- Managing defect backlogs
- Running quality gate checks
- Generating test coverage reports

## How to Use

1. Select the process you need from the table above
2. The command will route to qa-engineer or software-engineer as appropriate
3. Follow process steps in `claude-code/processes/05_quality_assurance_testing.md`

## Dispatch Mode

When invoked via the Command Dispatcher (a dispatch context file exists at the invoking session's `dispatch-receipts/dispatch-context-TRIG-*.json`), operate in dispatch mode:

1. **Skip interactive guidance** — Do not present process menus or ask for user selection
2. **Read dispatch context** — Parse the dispatch context file for `trigger_id`, `stage`, `condition_summary`, and `relevant_artifacts`
3. **Focused analysis** — Analyze only the processes relevant to the trigger (typically P-032 Test Architecture for TRIG-002, or specific flagged processes for TRIG-010)
4. **Structured output** — Produce findings in this format:

```
## Dispatch Findings

**Trigger**: <trigger_id> (<process_ids>)
**Severity**: <max severity across findings>
**Findings Count**: <N>

### Finding <N>: <title>
- **Process**: <process_id> (<process_name>)
- **Severity**: HIGH | CRITICAL
- **Location**: <file, module, or test area>
- **Recommendation**: <actionable test strategy or fix>
- **Stage Impact**: Stage <N> (<what must change>)

## Recommended Next Action
- **Type**: inject_into_stage | create_task
- **Target Stage**: <N>
- **Instruction**: <what the target stage must address>
```

5. **Return immediately** — Do not wait for user input. The loop controller creates the dispatch receipt from this output.

See `_shared/protocols/command-dispatch.md` for the full dispatch protocol.

## Receipt Writing (STATE-001)

After completing analysis (standalone or dispatch mode), write a receipt:

1. `mkdir -p .pipeline-state/command-receipts .pipeline-state/process-log`
2. Write `.pipeline-state/command-receipts/qa-<YYYYMMDD>-<HHMMSS>.json`:

```json
{
  "command": "qa",
  "receipt_id": "qa-<YYYYMMDD>-<HHMMSS>",
  "timestamp": "<ISO-8601>",
  "session_context": {
    "session_id": "<dispatch session_id or null>",
    "pipeline": "<auto-orchestrate|auto-audit|auto-debug|standalone>"
  },
  "inputs": {
    "mode": "<standalone|dispatch>",
    "process_ids": ["P-032", "P-033"]
  },
  "outputs": {
    "findings": [{"process": "P-032", "severity": "HIGH", "title": "..."}],
    "severity_max": "HIGH"
  },
  "artifacts": [],
  "processes_executed": ["P-032", "P-033"],
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

- `/active-dev` — Continuous quality during sprint
- `/release-prep` — Release qualification testing
- `/gate-review` — Gate 2/4 quality criteria review

## Process Reference

Full process definitions: `claude-code/processes/05_quality_assurance_testing.md`
