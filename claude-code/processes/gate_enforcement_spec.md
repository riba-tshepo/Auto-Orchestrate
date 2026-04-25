# Gate Enforcement Specification

**Version**: 1.0  
**Date**: 2026-04-06  
**Produced by**: software-engineer (Task #7, SPEC T014)  
**Status**: Active

---

## Gate Identity Table

| Gate ID | Name | Process | Owner | Checklist Items |
|---------|------|---------|-------|----------------|
| `gate_1_intent_review` | Intent Review | P-004 | Product Manager + Engineering Manager | 7 |
| `gate_2_scope_lock` | Scope Lock | P-013 | Product Manager | 8 |
| `gate_3_dependency_acceptance` | Dependency Acceptance | P-019 | Technical Program Manager | 6 |
| `gate_4_sprint_readiness` | Sprint Readiness | P-025 | Engineering Manager + Tech Lead | 6 |

**Gate state file location**: `.orchestrate/{session_id}/gate-state.json`  
**JSON Schema**: `claude-code/processes/gate_state_schema.json` (JSON Schema Draft 7)

---

## State Machine

### Valid Transitions

| From | To | Trigger | Notes |
|------|----|---------|-------|
| `pending` | `in_review` | `/gate-review` command invoked for this gate | Automatically set when review begins |
| `in_review` | `passed` | All checklist items confirmed passed | `pass_timestamp` set; `checklist_items_passed` = `checklist_items_total` |
| `in_review` | `failed` | Any checklist item marked failed | `fail_reason` MUST be set |
| `failed` | `in_review` | `/gate-review` re-invoked for retry | Clears `fail_reason`; sets new `last_reviewed` |
| `passed` | `in_review` | `/gate-review` re-invoked with `--reopen` flag | Only with explicit `--reopen`; logs warning |

### Invalid Transitions (MUST be blocked)

| Attempted Transition | Error Message |
|---------------------|---------------|
| `pending` → `passed` | `[GATE-ERROR] Cannot mark gate as passed without review. Run /gate-review {gate_name} to begin review process.` |
| `pending` → `failed` | `[GATE-ERROR] Cannot mark gate as failed without review. Run /gate-review {gate_name} to begin review process.` |
| `passed` → `failed` | `[GATE-ERROR] Cannot mark a passed gate as failed. Use /gate-review {gate_name} --reopen to re-enter review state first.` |
| `passed` → `pending` | `[GATE-ERROR] Cannot revert a passed gate to pending. Use /gate-review {gate_name} --reopen to re-enter review state if needed.` |

### Enforcement Points

Gate N+1 advancement is BLOCKED if `gate_N.status != "passed"` AND `gate_N.override` is null.

| Pipeline Point | Gate Required | Blocking Command | Error Format |
|---------------|--------------|-----------------|--------------|
| Stage 2 (Scope Contract) START | `gate_1_intent_review.status == "passed"` | `/new-project` | `[GATE-BLOCK] Gate 1 (Intent Review) has not passed. Cannot advance to Scope Contract. Run /gate-review intent-review to complete gate review.` |
| Stage 3 (Dependency Coordination) START | `gate_2_scope_lock.status == "passed"` | `/new-project` | `[GATE-BLOCK] Gate 2 (Scope Lock) has not passed. Cannot advance to Dependency Coordination. Run /gate-review scope-lock to complete gate review.` |
| Stage 4 (Sprint Bridge) START | `gate_3_dependency_acceptance.status == "passed"` | `/new-project` | `[GATE-BLOCK] Gate 3 (Dependency Acceptance) has not passed. Cannot advance to Sprint Bridge. Run /gate-review dependency-acceptance to complete gate review.` |
| `/sprint-ceremony` execution | `gate_4_sprint_readiness.status == "passed"` | `/sprint-ceremony` | `[GATE-BLOCK] Gate 4 (Sprint Readiness) has not passed. Cannot begin sprint execution. Run /gate-review sprint-readiness to complete gate review.` |

**Error message format**: `[GATE-BLOCK] Gate {N} ({name}) is {status}. Cannot advance to {next_stage}. Run /gate-review {gate_name} to complete gate review.`

---

## Override Mechanism

Gate enforcement may be waived for a single gate when an authorized override is present.

**When allowed**: Any gate, any status. Overrides are an emergency mechanism — they should be rare and always documented.

**Required fields** (all three MUST be present for the override to be valid):

| Field | Type | Description |
|-------|------|-------------|
| `reason` | string (min 10 chars) | Detailed justification. Must explain why the gate cannot be passed through normal review. |
| `authorized_by` | string | Name or role of the person who authorized the override. Must be a named individual, not "system". |
| `timestamp` | ISO 8601 string | When the override was authorized. |

**Override check**:
```
if gate_N.override is non-null
    AND gate_N.override.reason is present (length >= 10)
    AND gate_N.override.authorized_by is present
    AND gate_N.override.timestamp is present:
    → enforcement waived for gate_N only
    → log: [GATE-OVERRIDE] Gate {N} ({name}) override active. Authorized by: {authorized_by}. Reason: {reason}
else:
    → enforcement applies
```

**Partial override** (missing fields): If `override` object exists but any required field is missing, the override is INVALID and enforcement still applies. Log: `[GATE-ERROR] Override for gate_{N}_{name} is malformed — missing required field: {field}. Enforcement not waived.`

---

## Initialization

When `/gate-review` is first invoked for a session that has no `gate-state.json`, the command MUST create the file with all 4 gates initialized to `status: "pending"`.

**Initial state template**:
```json
{
  "session_id": "{session_id}",
  "project_name": "{project_name}",
  "last_updated": "{current ISO 8601 timestamp}",
  "schema_version": "1.0",
  "gates": {
    "gate_1_intent_review": {
      "status": "pending",
      "owner": "product-manager",
      "checklist_items_total": 7,
      "checklist_items_passed": 0,
      "last_reviewed": null,
      "reviewed_by": null,
      "pass_timestamp": null,
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

---

## File Location Convention

**Runtime file**: `.orchestrate/{session_id}/gate-state.json`

- The `.orchestrate/{session_id}/` directory is created by the session-manager at session start.
- `gate-state.json` is created by `/gate-review` on first invocation for a session.
- If the directory exists but `gate-state.json` does not: create it (see Initialization above).
- If the directory does not exist: the session has not started. Do not create gate-state.json — instruct the user to run `/new-project` first.

---

## Commands That Read Gate State

| Command | Gate State Fields Read | Purpose |
|---------|----------------------|---------|
| `/new-project` | `gate_N.status`, `gate_N.override` | Block stage advancement if prior gate not passed |
| `/workflow` | All gate statuses | Display project progress dashboard |
| `/sprint-ceremony` | `gate_4_sprint_readiness.status`, `gate_4_sprint_readiness.override` | Block sprint execution if Gate 4 not passed |
| `/gate-review` | All gates | Determine current state before writing new state |

## Commands That Write Gate State

| Command | Gate State Fields Written | Conditions |
|---------|--------------------------|------------|
| `/gate-review` | `status`, `checklist_items_passed`, `last_reviewed`, `reviewed_by`, `pass_timestamp`, `fail_reason` | After completing gate review checklist |
| `/gate-review` | `override` | When user provides explicit override authorization |

**Only `/gate-review` writes to `gate-state.json`.** All other commands read only.

---

## Validation Steps

```bash
# Verify schema file is valid JSON
python3 -c "import json; json.load(open('claude-code/processes/gate_state_schema.json'))"
echo "Schema is valid JSON"

# Verify all 4 gate names in schema
grep -c "gate_[1-4]" claude-code/processes/gate_state_schema.json
# Expected: >= 4

# Verify enforcement spec exists with required sections
ls -la claude-code/processes/gate_enforcement_spec.md
grep "GATE-BLOCK\|Override\|State Machine\|Initialization" claude-code/processes/gate_enforcement_spec.md

# Verify gate-review.md updated
grep "Gate State Write" claude-code/commands/gate-review.md

# Verify new-project.md has gate checks
grep -c "GATE-BLOCK\|gate_state\|gate_1\|gate_2\|gate_3\|gate_4" claude-code/commands/new-project.md
# Expected: >= 3
```

---

*Implements SPEC T014 | Blocks: T015 (gate state tracking), T016 (enforcement integration), T017 (manifest registration)*
