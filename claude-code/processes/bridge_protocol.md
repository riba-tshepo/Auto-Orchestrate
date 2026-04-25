# System Bridge Protocol: Organizational Workflow → Auto-Orchestrate

**Version**: 1.0  
**Date**: 2026-04-06  
**Produced by**: software-engineer (Task #6, SPEC T009)  
**Status**: Active

---

## Overview

Two autonomous pipelines exist within the engineering system. The **organizational workflow** (`/new-project`) runs a 4-stage human-facing pipeline (Intent → Scope → Dependencies → Sprint) producing artifacts that define *what* to build and *why*. The **auto-orchestrate pipeline** (`/auto-orchestrate`) runs a 7-stage technical pipeline (Research → Epic → Spec → Implement → Test → Validate → Document) that actually *builds it*. Without this bridge, every handoff between the two pipelines requires complete manual re-entry of project context, creating duplication, translation errors, and lost traceability. This protocol defines the exact mechanism for extracting structured context from the organizational pipeline and injecting it into auto-orchestrate with zero information loss.

---

## Trigger Conditions

The bridge is activated under two conditions:

**Condition A — Early handoff (after Gate 2: Scope Lock)**:  
When the Scope Contract is complete and the team elects to begin autonomous implementation immediately, before sprint planning is finalized. Use when: scope is fully locked, dependencies are pre-cleared or low-risk, and the team wants implementation running in parallel with sprint ceremony.

**Condition B — Full handoff (after Gate 4: Sprint Readiness)**:  
When all four organizational gates have passed and the Sprint Kickoff Brief is complete. This is the recommended path. Use when: all dependencies are committed, sprint goal is authored, and the team is ready for autonomous implementation to begin the sprint.

**Condition C — Deferred handoff**:  
When `/auto-orchestrate` is unavailable at the time of gate passage. Write the handoff receipt with `auto_orchestrate_status: "deferred"` and resume with `/auto-orchestrate c --session_id {session_id}` when available.

---

## Extraction Table: Scope Contract → task_description

| task_description Field | Source in Scope Contract | Process Ref | Required |
|------------------------|--------------------------|-------------|----------|
| `Project: {project_name}` | Document title / Intent Brief header | P-001 | YES |
| `Objective: {problem_statement}` | Intent Brief problem statement | P-001 | YES |
| `Deliverables: {deliverables_list}` | Decomposed deliverables list | P-007 | YES |
| `Definition of Done: {dod_summary}` | Per-epic DoD (summarized) | P-008 | YES |
| `Excluded: {exclusions_list}` | Explicit exclusions document | P-011 | YES |
| `Constraints: {constraints}` | RAID log — Risks and Assumptions | P-010 | NO (default: "") |

**Extraction algorithm**:
```
task_description = concat([
  "Project: {scope_contract.project_name}",
  "Objective: {scope_contract.problem_statement}",
  "Deliverables: {scope_contract.deliverables_list}",
  "Definition of Done: {scope_contract.dod_summary}",
  "Excluded: {scope_contract.exclusions_list}",
  "Constraints: {scope_contract.constraints}"
])
```

**Scope flag derivation**:
```
scope_contract.tech_scope → scope flag:
  "frontend"   → "F"
  "backend"    → "B"
  "fullstack"  → "S"
  (default)    → "S"
```

---

## Session ID Format

```
session_id = "auto-orc-{YYYYMMDD}-{project_slug}"

project_slug = first 8 characters of project_name:
  - lowercased
  - spaces replaced with hyphens
  - non-alphanumeric characters removed (except hyphens)
  - truncated to 8 characters

Examples:
  "Customer Portal Redesign" → "auto-orc-20260406-customer-"
  "API Gateway v2"           → "auto-orc-20260406-api-gatew"
  "Auth Service"             → "auto-orc-20260406-auth-serv"
```

---

## Handoff Receipt Schema

**File path**: `.orchestrate/{session_id}/handoff-receipt.json`  
**Created by**: `/new-project` Phase 5 (or `/gate-review` post-Gate 4)  
**Read by**: `/auto-orchestrate` at session start to restore context

```json
{
  "session_id": "auto-orc-20260406-{slug}",
  "handoff_timestamp": "2026-04-06T12:00:00Z",
  "source_pipeline": "organizational-workflow",
  "source_command": "/new-project",
  "source_stage": "Gate 2: Scope Lock",
  "source_gate_status": "PASSED",
  "project_name": "{string — full project name}",
  "scope_contract_path": "{absolute or relative path to scope contract artifact}",
  "task_description": "{full multi-line string passed to /auto-orchestrate}",
  "scope_flag": "F|B|S",
  "auto_orchestrate_command": "/auto-orchestrate \"{task_description}\" --scope {scope_flag} --session_id {session_id}",
  "auto_orchestrate_status": "launched|deferred|completed",
  "return_path": {
    "description": "After /auto-orchestrate completes, link outputs back to project stage",
    "stage6_artifacts_path": ".orchestrate/{session_id}/stage-6/",
    "org_workflow_stage": "Stage 4: Sprint Bridge",
    "next_command": "/sprint-ceremony"
  }
}
```

**Field constraints**:
- `session_id`: MUST match pattern `^auto-orc-[0-9]{8}-[a-z0-9-]+$`
- `handoff_timestamp`: ISO 8601 with timezone (UTC preferred)
- `source_gate_status`: MUST be `"PASSED"` — bridge MUST NOT be triggered on a failed gate
- `scope_flag`: One of `"F"`, `"B"`, `"S"` — no other values
- `auto_orchestrate_status`: `"launched"` on initial write; update to `"completed"` after AO pipeline exits

---

## Launch Command Template

```bash
/auto-orchestrate "{task_description}" --scope {scope_flag} --session_id {session_id}
```

**Full example**:
```bash
/auto-orchestrate "Project: Customer Portal Redesign
Objective: Customers cannot self-serve password resets, causing 40% of tier-1 support volume.
Deliverables: Self-service password reset flow, email verification, audit log UI
Definition of Done: Reset flow completes in <30s, zero support tickets for covered scenarios, audit log queryable by admin
Excluded: SSO integration, multi-factor auth, password strength policy UI
Constraints: Must not modify existing session management code; GDPR data residency applies" \
  --scope F \
  --session_id auto-orc-20260406-customer-
```

---

## Return Path: auto-orchestrate → Organizational Workflow

After `/auto-orchestrate` completes its Stage 6 (documentation), implementation artifacts are available in:

```
.orchestrate/{session_id}/stage-6/    ← Documentation outputs
.orchestrate/{session_id}/stage-5/    ← Validation reports
.orchestrate/{session_id}/stage-4/    ← Test suites
.orchestrate/{session_id}/stage-3/    ← Implementation files (referenced)
```

**Return steps**:
1. Update `handoff-receipt.json`: set `auto_orchestrate_status: "completed"` and `completed_timestamp`.
2. Link Stage 6 documentation to the organizational project record.
3. Present Stage 5 validation report to the Engineering Manager as sprint completion evidence.
4. Run `/sprint-ceremony` to conduct the sprint retrospective and close the sprint.

**Integration point**: The Stage 6 documentation output feeds directly into Sprint 1 execution records and satisfies P-058 (Technical Documentation), P-059 (API Documentation), and P-061 (Runbook) process requirements.

---

## Error Handling and Pipeline Unavailability Fallback

### /auto-orchestrate unavailable at handoff time

If `/auto-orchestrate` cannot be launched (tool not installed, session conflict, or system unavailability):

1. Write the handoff receipt to `.orchestrate/{session_id}/handoff-receipt.json` with `auto_orchestrate_status: "deferred"`.
2. Record the reason in a `deferral_reason` field: `"auto-orchestrate unavailable at handoff time"`.
3. Proceed with manual implementation sprint — do not block the team.
4. When auto-orchestrate becomes available, resume with:
   ```bash
   /auto-orchestrate c --session_id {session_id}
   ```
   The continuation path reads the handoff receipt to restore full project context without re-entry.

### Scope Contract incomplete at trigger time

If the Scope Contract artifact is missing required fields at the time of bridge invocation:

1. Do NOT write the handoff receipt.
2. Return to `/new-project` Stage 2 to complete the Scope Contract.
3. The bridge MUST NOT proceed with incomplete `deliverables_list` or missing `problem_statement` — these fields are non-negotiable inputs to the auto-orchestrate researcher.

### Gate not passed

If the bridge is invoked before Gate 2 (Scope Lock) has passed:

1. Do NOT write the handoff receipt.
2. Do NOT launch `/auto-orchestrate`.
3. Return error: `[BRIDGE-BLOCK] Gate 2 (Scope Lock) has not passed. Bridge protocol requires gate_2_scope_lock.status == "passed". Run /gate-review scope-lock to complete gate review.`

---

## Integration with Gate State

The bridge protocol reads `gate-state.json` (defined in SPEC T014) to confirm gate passage before writing the handoff receipt. The check is:

```
if gate_state.gates.gate_2_scope_lock.status != "passed":
    → BRIDGE-BLOCK error (see Error Handling)

if gate_state.gates.gate_4_sprint_readiness.status == "passed":
    → Condition B handoff (preferred)
else:
    → Condition A handoff (early, allowed)
```

---

## Implementation Notes for `/new-project` Phase 5

The Phase 5 addition to `claude-code/commands/new-project.md` (appended separately) provides the user-facing trigger. This bridge_protocol.md document is the reference implementation. Any discrepancy between Phase 5 instructions and this document: **this document takes precedence**.

---

*Implements SPEC T009 | References: T003 (orchestrator install guard), T014 (gate state schema), T019 (process injection)*
