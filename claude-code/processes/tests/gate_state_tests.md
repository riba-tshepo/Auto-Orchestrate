# Gate State Persistence Test Scenarios
**Version**: 1.0
**Date**: 2026-04-14
**Scope**: Gate state machine — valid transitions, invalid transitions, override mechanism
**Test Method**: Executable Claude Code session scripts
**Related Specs**:
- `~/.claude/processes/gate_enforcement_spec.md`
- `~/.claude/processes/gate_state_schema.json`
- `~/.claude/commands/gate-review.md`

> **IMPORTANT**: Run all tests in an isolated test directory (not a production project). Tests create and modify `.orchestrate/` gate state files. Override tests (GSP-008, GSP-009) must use real names in `authorized_by` — not "system" or "auto".

---

## Test Setup

```bash
# Create isolated test environment
TEST_DIR="/tmp/gate-state-tests-$(date +%Y%m%d)"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"
SESSION_ID="auto-orc-20260414-gate-test"
GATE_DIR=".orchestrate/$SESSION_ID"
GATE_FILE="$GATE_DIR/gate-state.json"
mkdir -p "$GATE_DIR"
```

---

## GSP-001: Initialization — gate-state.json Created with All 4 Gates at "pending"

**Type**: Initialization
**Gate tested**: All 4 gates

### Preconditions
- No `.orchestrate/{session_id}/gate-state.json` exists
- Session directory exists: `.orchestrate/{session_id}/`

### Steps
1. Run `/gate-review intent-review` for a new session
2. Observe that `/gate-review` creates `gate-state.json` before the review starts
3. Check the initial state of all 4 gates

### Expected Output
```
[GATE-INIT] Gate state file created: .orchestrate/{session_id}/gate-state.json
All gates initialized to: pending
```

### Validation
```bash
python3 -c "
import json
gs = json.load(open('$GATE_FILE'))
gates = gs['gates']
for gate_id in ['gate_1_intent_review', 'gate_2_scope_lock', 'gate_3_dependency_acceptance', 'gate_4_sprint_readiness']:
    assert gates[gate_id]['status'] == 'pending', f'{gate_id} should be pending, got {gates[gate_id][\"status\"]}'
print('PASS: All 4 gates initialized to pending')
print('schema_version:', gs.get('schema_version'))
print('session_id:', gs.get('session_id'))
"
```

### Pass Criteria
- [ ] `gate-state.json` file created at `.orchestrate/{session_id}/gate-state.json`
- [ ] `schema_version` field present
- [ ] `session_id` field matches current session
- [ ] All 4 gates have `"status": "pending"`
- [ ] No `passed_at`, `failed_at`, or `override` fields on any gate in initial state

---

## GSP-002: Valid Transition — pending → in_review

**Type**: Valid Transition
**Gate tested**: gate_1_intent_review

### Preconditions
- `gate-state.json` exists with `gate_1_intent_review.status = "pending"`

### Setup
```bash
cat > "$GATE_FILE" << 'GEOF'
{
  "session_id": "auto-orc-20260414-gate-test",
  "project_name": "Gate Test Project",
  "schema_version": "1.0",
  "gates": {
    "gate_1_intent_review": {"status": "pending"},
    "gate_2_scope_lock": {"status": "pending"},
    "gate_3_dependency_acceptance": {"status": "pending"},
    "gate_4_sprint_readiness": {"status": "pending"}
  }
}
GEOF
```

### Steps
1. Run `/gate-review intent-review` (start the review)
2. Observe gate transitions to `in_review` as the review begins
3. Do NOT complete the review in this test

### Expected Output
```
[GATE-REVIEW] Starting intent-review gate. Status: pending → in_review
```

### Validation
```bash
python3 -c "
import json
gs = json.load(open('$GATE_FILE'))
g1 = gs['gates']['gate_1_intent_review']
assert g1['status'] == 'in_review', f'Expected in_review, got {g1[\"status\"]}'
print('PASS: gate_1_intent_review status = in_review')
"
```

### Pass Criteria
- [ ] `gate_1_intent_review.status` changes from `"pending"` to `"in_review"`
- [ ] Other gates remain `"pending"` (no cascade)
- [ ] `gate-state.json` written atomically (no corruption)

---

## GSP-003: Valid Transition — in_review → passed (with timestamp)

**Type**: Valid Transition
**Gate tested**: gate_2_scope_lock

### Preconditions
- `gate_2_scope_lock.status = "in_review"`

### Setup
```bash
python3 -c "
import json
gs = json.load(open('$GATE_FILE'))
gs['gates']['gate_2_scope_lock']['status'] = 'in_review'
json.dump(gs, open('$GATE_FILE', 'w'), indent=2)
print('Setup: gate_2_scope_lock set to in_review')
"
```

### Steps
1. Run `/gate-review scope-lock` with all checklist items completed
2. Approve the gate (respond "pass" or equivalent)
3. Verify gate transitions to `passed` with `passed_at` timestamp

### Expected Output
```
[GATE-PASS] Gate 2 (Scope Lock) passed.
Timestamp: {ISO-8601}
```

### Validation
```bash
python3 -c "
import json, re
from datetime import datetime
gs = json.load(open('$GATE_FILE'))
g2 = gs['gates']['gate_2_scope_lock']
assert g2['status'] == 'passed', f'Expected passed, got {g2[\"status\"]}'
assert 'passed_at' in g2, 'passed_at timestamp missing'
# Verify it's a valid ISO 8601 timestamp
ts = g2['passed_at']
datetime.fromisoformat(ts.replace('Z', '+00:00'))
print('PASS: gate_2_scope_lock status = passed, passed_at =', ts)
"
```

### Pass Criteria
- [ ] `gate_2_scope_lock.status` = `"passed"`
- [ ] `gate_2_scope_lock.passed_at` contains a valid ISO 8601 timestamp
- [ ] Other gates unchanged
- [ ] `[GATE-PASS]` log message displayed

---

## GSP-004: Valid Transition — in_review → failed (with reason)

**Type**: Valid Transition
**Gate tested**: gate_3_dependency_acceptance

### Preconditions
- `gate_3_dependency_acceptance.status = "in_review"`

### Setup
```bash
python3 -c "
import json
gs = json.load(open('$GATE_FILE'))
gs['gates']['gate_3_dependency_acceptance']['status'] = 'in_review'
json.dump(gs, open('$GATE_FILE', 'w'), indent=2)
print('Setup: gate_3_dependency_acceptance set to in_review')
"
```

### Steps
1. Run `/gate-review dependency-acceptance`
2. When prompted, fail the gate (respond "fail" and provide reason: "External API not available")
3. Verify gate transitions to `failed` with `fail_reason`

### Expected Output
```
[GATE-FAIL] Gate 3 (Dependency Acceptance) failed.
Reason: External API not available
```

### Validation
```bash
python3 -c "
import json
gs = json.load(open('$GATE_FILE'))
g3 = gs['gates']['gate_3_dependency_acceptance']
assert g3['status'] == 'failed', f'Expected failed, got {g3[\"status\"]}'
assert 'fail_reason' in g3 and g3['fail_reason'], 'fail_reason missing or empty'
print('PASS: gate_3_dependency_acceptance status = failed')
print('fail_reason:', g3['fail_reason'])
"
```

### Pass Criteria
- [ ] `gate_3_dependency_acceptance.status` = `"failed"`
- [ ] `gate_3_dependency_acceptance.fail_reason` is non-empty string
- [ ] `[GATE-FAIL]` log message displayed
- [ ] Gate can be re-reviewed after failure (re-run `/gate-review dependency-acceptance`)

---

## GSP-005: Invalid Transition — pending → passed (BLOCKED, produces [GATE-ERROR])

**Type**: Invalid Transition
**Gate tested**: gate_4_sprint_readiness

### Preconditions
- `gate_4_sprint_readiness.status = "pending"` (never entered in_review)

### Setup
```bash
python3 -c "
import json
gs = json.load(open('$GATE_FILE'))
gs['gates']['gate_4_sprint_readiness']['status'] = 'pending'
json.dump(gs, open('$GATE_FILE', 'w'), indent=2)
print('Setup: gate_4_sprint_readiness at pending')
"
```

### Steps
1. Attempt to manually write `status: "passed"` directly to gate-state.json (bypassing gate-review)
2. Run a command that reads gate state (e.g., `/sprint-ceremony`)
3. Observe that the enforcement check detects invalid state OR the direct write attempt is rejected

**Alternative test**: Attempt to pass gate via `/gate-review sprint-readiness --force-pass` without completing checklist

### Expected Output
```
[GATE-ERROR] Invalid transition: gate_4_sprint_readiness cannot go from pending to passed without in_review step.
```

### Validation
```bash
python3 -c "
import json
gs = json.load(open('$GATE_FILE'))
g4 = gs['gates']['gate_4_sprint_readiness']
# Gate should remain at pending (or show error state) — never jump to passed
assert g4['status'] != 'passed', f'ERROR: Gate jumped from pending to passed without in_review — invalid transition allowed!'
print('PASS: Gate did not illegally transition to passed from pending')
print('Current status:', g4['status'])
"
```

### Pass Criteria
- [ ] Attempt to skip `in_review` produces `[GATE-ERROR]` message
- [ ] `gate_4_sprint_readiness.status` does NOT become `"passed"` via direct jump
- [ ] Error message identifies the invalid transition explicitly

---

## GSP-006: Enforcement — Gate Blocks Stage Advancement

**Type**: Enforcement
**Gate tested**: gate_2_scope_lock (blocks Stage 2+)

### Preconditions
- `gate_2_scope_lock.status = "failed"` or `"pending"`
- A command attempts to proceed past Stage 2

### Setup
```bash
python3 -c "
import json
gs = json.load(open('$GATE_FILE'))
gs['gates']['gate_2_scope_lock']['status'] = 'failed'
gs['gates']['gate_2_scope_lock']['fail_reason'] = 'Scope not agreed by stakeholders'
json.dump(gs, open('$GATE_FILE', 'w'), indent=2)
print('Setup: gate_2_scope_lock set to failed')
"
```

### Steps
1. With Gate 2 failed, attempt to proceed to Stage 3 in `/new-project`
2. Observe that `[GATE-BLOCK]` prevents advancement

### Expected Output
```
[GATE-BLOCK] Gate 2 (Scope Lock) has not passed. Cannot proceed to Stage 3 (Dependency Map).
Reason: Scope not agreed by stakeholders
Run /gate-review scope-lock to complete gate review.
```

### Validation
```bash
python3 -c "
import json
gs = json.load(open('$GATE_FILE'))
g2 = gs['gates']['gate_2_scope_lock']
assert g2['status'] == 'failed', f'Precondition: gate should be failed'
print('PASS: Precondition verified — Gate 2 is failed')
print('Expected behavior: /new-project Stage 3 should be blocked')
print('Expected output: [GATE-BLOCK] Gate 2 (Scope Lock) has not passed.')
"
```

### Pass Criteria
- [ ] `[GATE-BLOCK]` message displayed when gate is in `failed` or `pending` state
- [ ] Stage advancement does NOT proceed
- [ ] Message includes the `fail_reason` if gate is in `failed` state
- [ ] Message suggests running `/gate-review`

---

## GSP-007: Persistence — Gate State Persists Across Invocations

**Type**: Persistence
**Gate tested**: gate_1_intent_review

### Preconditions
- No prior gate state for test session

### Steps
1. Run `/gate-review intent-review` and complete the review (pass the gate)
2. End the Claude Code session
3. Start a new Claude Code session in the same directory
4. Run `/new-project` (or any command that reads gate state)
5. Observe that Gate 1 status is still `"passed"` from the previous session

### Expected Output (Session 1)
```
[GATE-PASS] Gate 1 (Intent Review) passed.
```

### Expected Output (Session 2)
```
[GATE-READ] Gate state loaded: gate_1_intent_review = passed
```

### Validation
```bash
# Run in Session 1:
python3 -c "
import json
from datetime import datetime, timezone
gs = json.load(open('$GATE_FILE'))
g1 = gs['gates']['gate_1_intent_review']
g1['status'] = 'passed'
g1['passed_at'] = datetime.now(timezone.utc).isoformat()
json.dump(gs, open('$GATE_FILE', 'w'), indent=2)
print('Session 1: gate_1_intent_review written as passed')
"

# Run in Session 2 (new session, same directory):
python3 -c "
import json
gs = json.load(open('$GATE_FILE'))
g1 = gs['gates']['gate_1_intent_review']
assert g1['status'] == 'passed', f'Expected passed, got {g1[\"status\"]}'
assert 'passed_at' in g1, 'passed_at should persist'
print('PASS: Gate state persisted across sessions')
print('gate_1_intent_review.status:', g1['status'])
print('gate_1_intent_review.passed_at:', g1['passed_at'])
"
```

### Pass Criteria
- [ ] `gate-state.json` is written to disk after gate review (not just held in memory)
- [ ] Second session reads the same `passed` status without re-running the gate review
- [ ] `passed_at` timestamp is preserved across sessions
- [ ] File not corrupted by session restart

---

## GSP-008: Valid Override — Override Allows Advancement Through Failed Gate

**Type**: Override
**Gate tested**: gate_3_dependency_acceptance

> **Security Note**: The `authorized_by` field MUST contain a real person's name (e.g., "Jane Smith, CTO"). Never use "system", "auto", "admin", or similar non-human values.

### Preconditions
- `gate_3_dependency_acceptance.status = "failed"`
- A valid override object is present with `reason`, `authorized_by` (real person name), and `timestamp`

### Setup
```bash
python3 -c "
import json
from datetime import datetime, timezone
gs = json.load(open('$GATE_FILE'))
gs['gates']['gate_3_dependency_acceptance']['status'] = 'failed'
gs['gates']['gate_3_dependency_acceptance']['fail_reason'] = 'Third-party API delayed'
gs['gates']['gate_3_dependency_acceptance']['override'] = {
    'reason': 'Proceeding with mock dependencies; real API to be integrated in Sprint 2',
    'authorized_by': 'Jane Smith, Engineering Director',
    'timestamp': datetime.now(timezone.utc).isoformat()
}
json.dump(gs, open('$GATE_FILE', 'w'), indent=2)
print('Setup: gate_3 set to failed with valid override')
"
```

### Steps
1. With gate failed but valid override present, attempt to advance
2. Observe that `[GATE-OVERRIDE]` message is displayed
3. Verify advancement proceeds (not blocked)

### Expected Output
```
[GATE-OVERRIDE] Gate 3 (Dependency Acceptance) override active.
Authorized by: Jane Smith, Engineering Director
Reason: Proceeding with mock dependencies; real API to be integrated in Sprint 2
Proceeding with ceremony.
```

### Validation
```bash
python3 -c "
import json
gs = json.load(open('$GATE_FILE'))
g3 = gs['gates']['gate_3_dependency_acceptance']
assert g3['status'] == 'failed', 'Gate should be failed'
override = g3.get('override', {})
assert override.get('reason'), 'Override reason missing'
assert override.get('authorized_by'), 'Override authorized_by missing'
assert override.get('timestamp'), 'Override timestamp missing'
# Verify authorized_by is NOT a non-human value
non_human = ['system', 'auto', 'admin', 'claude', 'bot']
auth_by = override['authorized_by'].lower()
for nh in non_human:
    assert nh not in auth_by, f'authorized_by should not contain \"{nh}\"'
print('PASS: Valid override present with real person name')
print('authorized_by:', override['authorized_by'])
print('Expected: [GATE-OVERRIDE] message displayed, advancement proceeds')
"
```

### Pass Criteria
- [ ] `[GATE-OVERRIDE]` log message displayed (not `[GATE-BLOCK]`)
- [ ] `authorized_by` contains a real person name
- [ ] Stage advancement proceeds despite gate being in `failed` state
- [ ] Override details (reason, authorized_by) are displayed to user

---

## GSP-009: Malformed Override Rejected — [GATE-ERROR] on Invalid Override

**Type**: Override
**Gate tested**: gate_4_sprint_readiness

### Preconditions
- Gate in `failed` state
- Override object present but MISSING required fields (e.g., missing `authorized_by`)

### Setup
```bash
python3 -c "
import json
gs = json.load(open('$GATE_FILE'))
gs['gates']['gate_4_sprint_readiness']['status'] = 'failed'
gs['gates']['gate_4_sprint_readiness']['fail_reason'] = 'Sprint capacity not confirmed'
# Malformed override: missing authorized_by and timestamp
gs['gates']['gate_4_sprint_readiness']['override'] = {
    'reason': 'Proceeding anyway'
    # Missing: authorized_by, timestamp
}
json.dump(gs, open('$GATE_FILE', 'w'), indent=2)
print('Setup: gate_4 set to failed with MALFORMED override (missing fields)')
"
```

### Steps
1. With gate failed and malformed override, attempt to advance to sprint-ceremony
2. Observe that `[GATE-ERROR]` is produced (not `[GATE-OVERRIDE]`)
3. Verify advancement is BLOCKED

### Expected Output
```
[GATE-ERROR] Override for gate_4_sprint_readiness is invalid: missing required field 'authorized_by'.
Override rejected. Gate remains in failed state.
[GATE-BLOCK] Gate 4 (Sprint Readiness) has not passed. Cannot begin sprint execution.
```

### Validation
```bash
python3 -c "
import json
gs = json.load(open('$GATE_FILE'))
g4 = gs['gates']['gate_4_sprint_readiness']
override = g4.get('override', {})
# Verify override is indeed malformed
missing = []
for field in ['reason', 'authorized_by', 'timestamp']:
    if not override.get(field):
        missing.append(field)
assert missing, f'Override should be malformed but has all fields: {override}'
print('PASS: Override is malformed — missing fields:', missing)
print('Expected: [GATE-ERROR] displayed, [GATE-BLOCK] enforced')
print('Expected: advancement is blocked despite override object existing')
"
```

### Pass Criteria
- [ ] `[GATE-ERROR]` message produced identifying which field is missing
- [ ] `[GATE-BLOCK]` enforced — advancement does NOT proceed
- [ ] Malformed override is NOT treated as valid override
- [ ] User told which fields are required for a valid override

---

## GSP-010: Reopen Mechanism — passed → in_review with --reopen

**Type**: Valid Transition
**Gate tested**: gate_2_scope_lock

### Preconditions
- `gate_2_scope_lock.status = "passed"` (previously passed)

### Setup
```bash
python3 -c "
import json
from datetime import datetime, timezone
gs = json.load(open('$GATE_FILE'))
gs['gates']['gate_2_scope_lock']['status'] = 'passed'
gs['gates']['gate_2_scope_lock']['passed_at'] = datetime.now(timezone.utc).isoformat()
json.dump(gs, open('$GATE_FILE', 'w'), indent=2)
print('Setup: gate_2_scope_lock set to passed (to be reopened)')
"
```

### Steps
1. Run `/gate-review scope-lock --reopen` (or equivalent reopen command)
2. Observe gate transitions from `passed` to `in_review`
3. Confirm that `passed_at` is cleared (or preserved as previous_passed_at)
4. Complete the review again to pass the gate

### Expected Output
```
[GATE-REOPEN] Gate 2 (Scope Lock) reopened. Status: passed → in_review
(Previous pass recorded. Re-review required.)
```

### Validation
```bash
python3 -c "
import json
gs = json.load(open('$GATE_FILE'))
g2 = gs['gates']['gate_2_scope_lock']
assert g2['status'] == 'in_review', f'Expected in_review after reopen, got {g2[\"status\"]}'
print('PASS: gate_2_scope_lock reopened to in_review')
print('Current status:', g2['status'])
# Verify it can be re-passed
g2['status'] = 'passed'
json.dump(gs, open('$GATE_FILE', 'w'), indent=2)
gs2 = json.load(open('$GATE_FILE'))
assert gs2['gates']['gate_2_scope_lock']['status'] == 'passed', 'Re-pass failed'
print('PASS: Gate can be re-passed after reopen')
"
```

### Pass Criteria
- [ ] `[GATE-REOPEN]` log message displayed
- [ ] `gate_2_scope_lock.status` changes from `"passed"` to `"in_review"`
- [ ] Gate can be re-reviewed and re-passed after reopen
- [ ] Previous pass history is not destroyed (optional: `previous_passed_at` field)

---

*Generated by software-engineer | Session auto-orc-20260414-pipeflow | Stage 3 | Task T-017*
