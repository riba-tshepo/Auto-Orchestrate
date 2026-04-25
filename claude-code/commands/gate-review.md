# Gate Review

Run a gate review checklist for the specified gate.

## Instructions

Identify which gate to review from: $ARGUMENTS

If no gate specified, ask which one. Available gates:

### Gate 1: Intent Review (P-004)

**Owner**: Product Manager + Engineering Manager
**Participants**: Staff/Principal Engineer, TPM, stakeholders

Pass criteria:
- [ ] Problem statement is clear and specific
- [ ] Target users/personas identified
- [ ] OKR alignment documented (P-002)
- [ ] Boundaries defined — explicit in-scope, out-of-scope, deferred lists (P-003)
- [ ] Technology vision alignment confirmed by Staff/Principal (P-006)
- [ ] Strategic priority relative to competing initiatives established (P-005)
- [ ] Intent Brief artifact complete (1-2 pages)

**Fail action**: Return to PM for intent clarification. Do NOT proceed to scope.

### Gate 2: Scope Lock (P-013)

**Owner**: Product Manager
**Approvers**: Engineering Manager + Tech Lead

Pass criteria:
- [ ] All deliverables decomposed with acceptance criteria (P-007)
- [ ] Definition of Done defined per story AND per epic (P-008)
- [ ] Success metrics defined and measurable (P-009)
- [ ] Assumptions and risks registered in RAID log (P-010)
- [ ] Exclusions explicitly documented (P-011)
- [ ] AppSec scope review completed by security engineer (P-012)
- [ ] Change control process agreed (P-014)
- [ ] Scope Contract artifact complete (3-5 pages)

**Fail action**: Return to PM for scope refinement. Do NOT proceed to dependency mapping.

### Gate 3: Dependency Acceptance (P-019)

**Owner**: Technical Program Manager
**Approvers**: All dependent teams

Pass criteria:
- [ ] All cross-team dependencies registered (P-015)
- [ ] Critical path analyzed and documented (P-016)
- [ ] Resource conflicts resolved (P-017)
- [ ] Communication plan established with sync cadences (P-018)
- [ ] Each dependent team has explicitly acknowledged and committed
- [ ] Escalation protocol defined (P-021)
- [ ] Dependency Charter artifact complete (2-4 pages)

**Fail action**: Return to TPM to resolve outstanding dependencies. Do NOT proceed to sprint planning.

### Gate 4: Sprint Readiness (P-025)

**Owner**: Engineering Manager + Tech Lead

Pass criteria:
- [ ] Sprint goal authored and traceable to intent (P-022, P-023)
- [ ] All stories written with acceptance criteria (P-024)
- [ ] Stories estimated and fit within sprint capacity
- [ ] Dependencies cleared or explicitly derisked
- [ ] Team has committed to sprint scope
- [ ] Sprint Kickoff Brief artifact complete (1 page per squad)

**Fail action**: Return to refinement. Do NOT start sprint execution.

## Output

For the selected gate:
1. Read the relevant process file to get full criteria
2. Present the checklist
3. For each item, assess current state (pass/fail/unknown)
4. Provide overall gate verdict: PASS or FAIL with rationale

## Gate State Persistence

Gate state is persisted between /new-project pipeline stages using a structured schema.

**Schema file**: `claude-code/processes/gate_state_schema.json`  
**State file location**: `.orchestrate/{session_id}/gate-state.json`

### Reading Gate State

Before running a gate review, check if a prior gate state exists:
1. Look for `.orchestrate/{session_id}/gate-state.json`
2. If present, load and validate against `gate_state_schema.json`
3. Display previous gate outcomes (passed/failed/pending) for context

### Writing Gate State

After completing a gate review:
1. Record outcome: `passed`, `failed`, or `pending`
2. Record reviewer, timestamp, and any conditions/waivers
3. Write updated state to `.orchestrate/{session_id}/gate-state.json`
4. Validate written state against `gate_state_schema.json`

### Gate State Schema Reference

The schema at `claude-code/processes/gate_state_schema.json` defines:
- Required fields per gate (gate_id, status, reviewed_at, reviewer)
- Valid status values: `passed`, `failed`, `pending`, `waived`
- Optional fields: conditions, waiver_reason, next_review_date

## Gate State Write

After completing gate review, write the result to the session gate state file.

**File**: `.orchestrate/{session_id}/gate-state.json`

**Schema reference**: `claude-code/processes/gate_state_schema.json`

If file does not exist: create it with all 4 gates initialized to `status: "pending"` (see `claude-code/processes/gate_enforcement_spec.md` — Initialization section for the full template).

For the reviewed gate:
- Set `status` to `"passed"` or `"failed"`
- Set `checklist_items_passed` to count of checked items
- Set `last_reviewed` to current ISO 8601 timestamp
- Set `reviewed_by` to the reviewing agent or user
- If passing: set `pass_timestamp` to current ISO 8601 timestamp
- If failing: set `fail_reason` to a human-readable explanation

**State machine constraints** (enforced — invalid transitions MUST be rejected):
- `pending → passed` is INVALID: must go through `in_review` first
- `pending → failed` is INVALID: must go through `in_review` first
- `passed → failed` is INVALID: use `--reopen` to enter `in_review` first
- `passed → pending` is INVALID: use `--reopen` to enter `in_review` if needed

**Example write** (Gate 1 passed):
```json
{
  "session_id": "auto-orc-20260406-myproj",
  "project_name": "My Project",
  "last_updated": "2026-04-06T10:30:00Z",
  "schema_version": "1.0",
  "gates": {
    "gate_1_intent_review": {
      "status": "passed",
      "owner": "product-manager",
      "checklist_items_total": 7,
      "checklist_items_passed": 7,
      "last_reviewed": "2026-04-06T10:30:00Z",
      "reviewed_by": "product-manager",
      "pass_timestamp": "2026-04-06T10:30:00Z",
      "fail_reason": null,
      "override": null
    },
    "gate_2_scope_lock": {
      "status": "pending",
      "owner": "product-manager",
      "checklist_items_total": 8,
      "checklist_items_passed": 0,
      "last_reviewed": null,
      "reviewed_by": null,
      "pass_timestamp": null,
      "fail_reason": null,
      "override": null
    },
    "gate_3_dependency_acceptance": {
      "status": "pending",
      "owner": "technical-program-manager",
      "checklist_items_total": 6,
      "checklist_items_passed": 0,
      "last_reviewed": null,
      "reviewed_by": null,
      "pass_timestamp": null,
      "fail_reason": null,
      "override": null
    },
    "gate_4_sprint_readiness": {
      "status": "pending",
      "owner": "engineering-manager",
      "checklist_items_total": 6,
      "checklist_items_passed": 0,
      "last_reviewed": null,
      "reviewed_by": null,
      "pass_timestamp": null,
      "fail_reason": null,
      "override": null
    }
  }
}
```

**Override authorization**: If the user provides an explicit override with reason and authorized-by, write the `override` object to the relevant gate. See `claude-code/processes/gate_enforcement_spec.md` — Override Mechanism.

## Receipt Writing (STATE-001)

In addition to updating `.orchestrate/{session_id}/gate-state.json`, write a cross-pipeline receipt:

1. `mkdir -p .pipeline-state/command-receipts .pipeline-state/process-log`
2. Write `.pipeline-state/command-receipts/gate-review-<YYYYMMDD>-<HHMMSS>.json`:

```json
{
  "command": "gate-review",
  "receipt_id": "gate-review-<YYYYMMDD>-<HHMMSS>",
  "timestamp": "<ISO-8601>",
  "session_context": {
    "session_id": "<session_id>",
    "pipeline": "<auto-orchestrate|standalone>"
  },
  "inputs": {
    "gate_id": "gate_1_intent_review|gate_2_scope_lock|gate_3_dependency_acceptance|gate_4_sprint_readiness",
    "session_id": "<session_id>"
  },
  "outputs": {
    "verdict": "PASS|FAIL",
    "checklist_passed": 7,
    "checklist_total": 7
  },
  "artifacts": [".orchestrate/<session>/gate-state.json"],
  "processes_executed": ["P-004"],
  "next_recommended_action": "<next gate or next phase command>",
  "dispatch_context": {
    "trigger_id": null,
    "invoked_by": null
  }
}
```

3. For each process executed, append to `.pipeline-state/process-log/<process-id>.jsonl` (STATE-003).

Note: The existing `gate-state.json` continues to be the authoritative gate state. The command receipt provides cross-pipeline visibility.

If write fails, log warning and continue. See `_shared/protocols/cross-pipeline-state.md` for the full receipt schema.
