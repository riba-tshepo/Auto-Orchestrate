# Organizational Operations

Guide the user through continuous organizational processes that run independently of any single project.

## Phase: Running the Organization (Continuous)

### Organizational Audit (Category 11)

**Primary agents**: `engineering-manager`, `staff-principal-engineer`
**Reference**: `processes/11_organizational_audit.md`

7-layer audit hierarchy with distinct cadences:
- **Board/CEO Audit** (P-062) — Annual strategic review
- **CTO Audit** (P-063) — Quarterly technology portfolio review
- **VP Audit** (P-064) — Quarterly department health assessment
- **Director Audit** (P-065) — Monthly team portfolio review
- **EM Audit** (P-066) — Bi-weekly team health and delivery metrics
- **Tech Lead/Staff Audit** (P-067) — Weekly technical quality review
- **IC Audit** (P-068) — Continuous self-assessment and growth tracking
- **Audit Finding Flow** (P-069) — How findings escalate up and actions flow down

### Communication & Alignment (Category 14)

**Primary agents**: `engineering-manager`, `product-manager`, `technical-program-manager`
**Reference**: `processes/14_communication_alignment.md`

- **OKR Cascade** (P-078) — Company -> Department -> Team -> Individual alignment
- **Stakeholder Updates** (P-079) — Regular status communications
- **Guild Standards** (P-080) — Cross-team technical community standards
- **DORA Metrics Review** (P-081) — Deployment frequency, lead time, MTTR, change failure rate

### Capacity & Resource Management (Category 15)

**Primary agents**: `engineering-manager`, `technical-program-manager`
**Reference**: `processes/15_capacity_resource_management.md`

- **Quarterly Capacity Planning** (P-082) — Team capacity vs. demand forecasting
- **Shared Resource Allocation** (P-083) — Cross-team resource negotiation
- **Succession Planning** (P-084) — Key person risk mitigation

### Technical Excellence & Standards (Category 16)

**Primary agents**: `staff-principal-engineer`, `platform-engineer`
**Reference**: `processes/16_technical_excellence_standards.md`

- **RFC Process** (P-085) — Formal design proposal and review
- **Tech Debt Tracking** (P-086) — Register, prioritize, schedule remediation
- **Language Tier Policy** (P-087) — Approved languages and adoption criteria
- **Architecture Patterns** (P-088) — Canonical patterns and anti-patterns
- **Developer Experience Survey** (P-089) — Quarterly DX health measurement

### Onboarding & Knowledge Transfer (Category 17)

**Primary agents**: `engineering-manager`, `technical-writer`
**Reference**: `processes/17_onboarding_knowledge_transfer.md`

- **New Engineer Onboarding** (P-090) — 30/60/90 day onboarding plan
- **Project Onboarding** (P-091) — Getting up to speed on an existing project
- **Knowledge Transfer** (P-092) — Structured handoff between team members
- **Cross-Team Dependency Onboarding** (P-093) — Understanding external team interfaces

## Cadence Summary

| Cadence | Processes |
|---------|-----------|
| Continuous | IC Audit (P-068), Guild Standards (P-080) |
| Weekly | Tech Lead/Staff Audit (P-067) |
| Bi-weekly | EM Audit (P-066) |
| Monthly | Director Audit (P-065), Stakeholder Updates (P-079) |
| Quarterly | CTO Audit (P-063), VP Audit (P-064), Capacity Planning (P-082), DORA Review (P-081), DX Survey (P-089), Process Health Review (P-071), Risk Review (P-077) |
| Annual | Board/CEO Audit (P-062) |

## Dispatch Mode

When invoked via the Command Dispatcher (a dispatch context file exists at the invoking session's `dispatch-receipts/dispatch-context-TRIG-*.json`), operate in dispatch mode:

1. **Skip interactive guidance** — Do not present process menus or ask for user selection
2. **Read dispatch context** — Parse the dispatch context file for `trigger_id`, `stage`, `condition_summary`, and `relevant_artifacts`
3. **Focused analysis** — Analyze only the processes relevant to the trigger (typically P-062 through P-069 audit processes for TRIG-012 flagged items)
4. **Structured output** — Produce findings in this format:

```
## Dispatch Findings

**Trigger**: <trigger_id> (<process_ids>)
**Severity**: <max severity across findings>
**Findings Count**: <N>

### Finding <N>: <title>
- **Process**: <process_id> (<process_name>)
- **Severity**: HIGH | CRITICAL
- **Category**: Audit | Communication | Capacity | Standards | Onboarding
- **Impact**: <what happens if unaddressed>
- **Recommendation**: <actionable organizational fix>
- **Stage Impact**: Stage <N> (<what must change>)

## Recommended Next Action
- **Type**: inject_into_stage | informational
- **Target Stage**: <N>
- **Instruction**: <what the target stage must address>
```

5. **Return immediately** — Do not wait for user input. The loop controller creates the dispatch receipt from this output.

See `_shared/protocols/command-dispatch.md` for the full dispatch protocol.

## Receipt Writing (STATE-001)

After completing analysis (standalone or dispatch mode), write a receipt:

1. `mkdir -p .pipeline-state/command-receipts .pipeline-state/process-log`
2. Write `.pipeline-state/command-receipts/org-ops-<YYYYMMDD>-<HHMMSS>.json`:

```json
{
  "command": "org-ops",
  "receipt_id": "org-ops-<YYYYMMDD>-<HHMMSS>",
  "timestamp": "<ISO-8601>",
  "session_context": {
    "session_id": "<dispatch session_id or null>",
    "pipeline": "<auto-orchestrate|auto-audit|auto-debug|standalone>"
  },
  "inputs": {
    "mode": "<standalone|dispatch>",
    "process_ids": ["P-062", "P-063"]
  },
  "outputs": {
    "findings": [{"process": "P-062", "severity": "HIGH", "title": "..."}],
    "category": "Audit|Communication|Capacity|Standards|Onboarding",
    "severity_max": "HIGH"
  },
  "artifacts": [],
  "processes_executed": ["P-062", "P-063"],
  "next_recommended_action": null,
  "dispatch_context": {
    "trigger_id": "<TRIG-XXX or null>",
    "invoked_by": "<session_id or null>"
  }
}
```

3. For each process executed, append to `.pipeline-state/process-log/<process-id>.jsonl` (STATE-003).

If write fails, log warning and continue — receipt writing MUST NOT block command execution. See `_shared/protocols/cross-pipeline-state.md` for the full receipt schema.

## Usage

What organizational operation do you need help with? I can:
- Run an audit at any organizational layer
- Prepare OKR cascade or DORA metrics review
- Draft an RFC or architecture decision
- Set up onboarding plans for new team members
- Review and prioritize tech debt
