# Handoff Pipeline Test Scenarios
**Version**: 1.0
**Date**: 2026-04-14
**Scope**: /new-project → /auto-orchestrate → /sprint-ceremony handoff chain
**Test Method**: Executable Claude Code session scripts (follow step-by-step)
**Related Specs**:
- `~/.claude/processes/gate_enforcement_spec.md`
- `~/.claude/processes/pipeline_chains_spec.md`
- `~/.claude/commands/auto-orchestrate.md` (Handoff Resume section)

> **IMPORTANT**: Run all tests in an isolated test directory (not a production project). Tests create and modify `.sessions/`, `.orchestrate/`, and other session artifacts.

---

## Prerequisites

- Claude Code installed and configured
- `~/.claude/` directory with all command files
- Empty project directory for test execution (e.g., `/tmp/handoff-test-{date}/`)
- No in-progress sessions in `.sessions/index.json`
- Test isolation: `mkdir -p /tmp/handoff-test && cd /tmp/handoff-test`

---

## HS-001: Happy Path — Full Pipeline from Gate 2 to sprint-ceremony

**Gap Covered**: GAP-PIPE-001, GAP-PIPE-005
**Risk**: High

### Preconditions
- Empty project directory (no existing sessions)
- `~/.claude/` commands directory contains: `new-project.md`, `auto-orchestrate.md`, `sprint-ceremony.md`, `gate-review.md`
- No `.sessions/index.json` in the test directory

### Steps
1. Start a new Claude Code session in the test directory
2. Run: `/new-project "Build a simple REST API for user management"`
3. Complete Stage 1 (Intent Frame): provide intent brief, confirm Gate 1 (Intent Review)
4. Complete Stage 2 (Scope Contract): define deliverables, confirm Gate 2 (Scope Lock)
5. Observe that Phase 5 (Sprint Bridge) triggers handoff-receipt.json creation
6. Run: `/auto-orchestrate` (should pick up handoff-receipt.json from Stage 4 bridge)
7. Allow pipeline to complete Stages 0-6 (or simulate completion by writing checkpoint)
8. After Stage 6: verify `[COMPLETE] Implementation done. Return path: /sprint-ceremony` is displayed
9. Run: `/sprint-ceremony sprint-planning`
10. Observe `[GATE-PASS] Gate 4 (Sprint Readiness) passed. Proceeding with ceremony.`

### Expected Output
```
[GATE-PASS] Gate 4 (Sprint Readiness) passed. Proceeding with ceremony.
[COMPLETE] Implementation done. Return path: /sprint-ceremony
Session: auto-orc-{date}-{slug}
```

### Validation Commands
```bash
# Verify handoff receipt was created with completed status
SESSION_ID=$(python3 -c "
import json, os, glob
receipts = glob.glob('.orchestrate/*/handoff-receipt.json')
if receipts:
    r = json.load(open(receipts[0]))
    print(r.get('session_id', 'NOT_FOUND'))
else:
    print('NO_RECEIPT')
")
echo "Session ID: $SESSION_ID"

# Verify auto_orchestrate_status is "completed"
test -f ".orchestrate/$SESSION_ID/handoff-receipt.json" && \
  grep '"auto_orchestrate_status": "completed"' ".orchestrate/$SESSION_ID/handoff-receipt.json" && \
  echo "HANDOFF_STATUS: PASS" || echo "HANDOFF_STATUS: FAIL"

# Verify gate-state.json exists with Gate 4 passed
test -f ".orchestrate/$SESSION_ID/gate-state.json" && \
  python3 -c "
import json
gs = json.load(open('.orchestrate/$SESSION_ID/gate-state.json'))
g4 = gs['gates']['gate_4_sprint_readiness']
assert g4['status'] == 'passed', f'Expected passed, got {g4[\"status\"]}'
print('GATE4_STATUS: PASS')
" || echo "GATE4_CHECK: FAIL"
```

### Pass Criteria
- [ ] `/new-project` completes all 4 stages including Sprint Bridge (Phase 5)
- [ ] `handoff-receipt.json` exists in `.orchestrate/{session_id}/`
- [ ] `/auto-orchestrate` runs to Stage 6 completion
- [ ] `handoff-receipt.json` contains `"auto_orchestrate_status": "completed"`
- [ ] `/sprint-ceremony` displays `[GATE-PASS]` message
- [ ] Sprint Planning ceremony proceeds to agenda items

---

## HS-002: Gate-Blocked — sprint-ceremony Blocked When Gate 4 Not Passed

**Gap Covered**: GAP-NEW-002, GAP-PIPE-005
**Risk**: High

### Preconditions
- An auto-orchestrate session exists in `.sessions/index.json` with status `in_progress` or `complete`
- `.orchestrate/{session_id}/gate-state.json` exists with `gate_4_sprint_readiness.status != "passed"` (e.g., `"pending"` or `"failed"`)

### Setup Commands
```bash
# Create a minimal gate-state.json with Gate 4 NOT passed
SESSION_ID="auto-orc-20260414-test"
mkdir -p ".orchestrate/$SESSION_ID"
cat > ".orchestrate/$SESSION_ID/gate-state.json" << 'GSEOF'
{
  "session_id": "auto-orc-20260414-test",
  "project_name": "Test Project",
  "schema_version": "1.0",
  "gates": {
    "gate_1_intent_review": {"status": "passed", "passed_at": "2026-04-14T09:00:00Z"},
    "gate_2_scope_lock": {"status": "passed", "passed_at": "2026-04-14T10:00:00Z"},
    "gate_3_dependency_acceptance": {"status": "passed", "passed_at": "2026-04-14T11:00:00Z"},
    "gate_4_sprint_readiness": {"status": "pending", "fail_reason": null}
  }
}
GSEOF

# Create minimal sessions/index.json
mkdir -p ".sessions"
cat > ".sessions/index.json" << 'SIEOF'
{
  "schema_version": "1.0",
  "sessions": [
    {
      "session_id": "auto-orc-20260414-test",
      "command": "auto-orchestrate",
      "status": "complete",
      "created_at": "2026-04-14T09:00:00Z"
    }
  ]
}
SIEOF
```

### Steps
1. With preconditions set up (Gate 4 in "pending" state)
2. Run: `/sprint-ceremony sprint-planning`
3. Observe: `[GATE-BLOCK]` message is displayed
4. Verify: ceremony does NOT proceed to agenda items

### Expected Output
```
[GATE-BLOCK] Gate 4 (Sprint Readiness) has not passed. Cannot begin sprint execution.
Current status: pending
Run /gate-review sprint-readiness to complete gate review.
```

### Validation Commands
```bash
# The gate-review command should be suggested
# Verify gate-state.json has Gate 4 in pending/failed state
python3 -c "
import json
gs = json.load(open('.orchestrate/auto-orc-20260414-test/gate-state.json'))
g4 = gs['gates']['gate_4_sprint_readiness']
assert g4['status'] != 'passed', f'Gate 4 should NOT be passed for this test'
print('GATE4_NOT_PASSED: PASS (precondition verified)')
"

# Verify sprint-ceremony output contains [GATE-BLOCK]
# (Run manually and capture output, then grep)
# grep '[GATE-BLOCK]' ceremony_output.txt && echo "GATE_BLOCK_DISPLAYED: PASS"
```

### Pass Criteria
- [ ] `/sprint-ceremony` displays `[GATE-BLOCK]` message
- [ ] Message includes `"Run /gate-review sprint-readiness to complete gate review."`
- [ ] Ceremony does NOT proceed to Sprint Planning agenda
- [ ] No `[GATE-PASS]` message is displayed

---

## HS-003: Partial Completion — auto-orchestrate Interrupted at Stage 3, Session Resumed

**Gap Covered**: GAP-PIPE-001
**Risk**: Medium

### Preconditions
- An auto-orchestrate session exists with checkpoint showing:
  - `stages_completed`: [0, 1, 2]
  - `current_stage`: 3
  - `session_state`: "active"

### Setup Commands
```bash
SESSION_ID="auto-orc-20260414-resume-test"
mkdir -p ".orchestrate/$SESSION_ID"

# Create a checkpoint simulating Stage 3 in-progress
cat > ".orchestrate/$SESSION_ID/checkpoint.json" << 'CPEOF'
{
  "session_id": "auto-orc-20260414-resume-test",
  "session_state": "active",
  "current_stage": 3,
  "stages_completed": [0, 1, 2],
  "task_description": "Implement user authentication module",
  "created_at": "2026-04-14T09:00:00Z",
  "last_updated": "2026-04-14T12:00:00Z"
}
CPEOF

# Add session to index
mkdir -p ".sessions"
cat > ".sessions/index.json" << 'SIEOF'
{
  "schema_version": "1.0",
  "sessions": [
    {
      "session_id": "auto-orc-20260414-resume-test",
      "command": "auto-orchestrate",
      "status": "in_progress",
      "created_at": "2026-04-14T09:00:00Z"
    }
  ]
}
SIEOF
```

### Steps
1. With preconditions set (checkpoint at Stage 3)
2. Run: `/auto-orchestrate c` (continue most recent session)
3. Observe: `[RESUME]` message displayed, pipeline continues from Stage 3
4. Verify: Stages 0, 1, 2 are NOT re-executed
5. Allow Stage 3+ to complete

### Expected Output
```
[RESUME] Resuming session auto-orc-20260414-resume-test
Stages completed: [0, 1, 2]
Resuming from Stage 3...
```

### Validation Commands
```bash
# Verify checkpoint shows correct resume point
python3 -c "
import json
cp = json.load(open('.orchestrate/auto-orc-20260414-resume-test/checkpoint.json'))
assert cp['stages_completed'] == [0, 1, 2], 'Wrong stages completed'
assert cp['current_stage'] == 3, 'Wrong current stage'
print('CHECKPOINT_STATE: PASS')
print('Stages completed:', cp['stages_completed'])
print('Resume from Stage:', cp['current_stage'])
"

# After resume, verify Stage 3 was completed (checkpoint updated)
# python3 -c "
# import json
# cp = json.load(open('.orchestrate/auto-orc-20260414-resume-test/checkpoint.json'))
# assert 3 in cp['stages_completed'], 'Stage 3 should be completed after resume'
# print('STAGE3_COMPLETED: PASS')
# "
```

### Pass Criteria
- [ ] `/auto-orchestrate c` displays `[RESUME]` message with session ID
- [ ] Pipeline resumes from Stage 3, not Stage 0
- [ ] Stages 0, 1, 2 outputs are NOT regenerated (check file timestamps)
- [ ] Session continues to completion

---

## HS-004: Missing Handoff Receipt — auto-orchestrate Started Without /new-project

**Gap Covered**: GAP-PIPE-001, GAP-PIPE-005
**Risk**: Medium

### Preconditions
- No `.orchestrate/` directory in test project
- No `.sessions/index.json`
- No `handoff-receipt.json` anywhere

### Steps
1. Start with completely empty test directory
2. Run: `/auto-orchestrate "Build a REST API for task management"`
3. Observe: No `[HANDOFF]` message, fresh start proceeds normally
4. Pipeline should run to completion (Stages 0-6)
5. At Stage 6 completion: verify `[COMPLETE]` message shown WITHOUT "Return path"

### Expected Output
```
[COMPLETE] Implementation pipeline complete.
Session: auto-orc-{date}-{slug}
Stage 6 documentation: .orchestrate/auto-orc-{date}-{slug}/stage-6/
```

(No "Return path: /sprint-ceremony" because no handoff-receipt.json exists)

### Validation Commands
```bash
# Verify no handoff receipt was expected/required
SESSION_ID=$(python3 -c "
import json, glob
checkpoints = glob.glob('.orchestrate/*/checkpoint.json')
if checkpoints:
    cp = json.load(open(checkpoints[0]))
    print(cp.get('session_id', 'NOT_FOUND'))
else:
    print('NO_CHECKPOINT')
")
echo "Fresh session ID: $SESSION_ID"

# Verify session completed without errors
test -f ".orchestrate/$SESSION_ID/checkpoint.json" && \
  python3 -c "
import json
cp = json.load(open('.orchestrate/$SESSION_ID/checkpoint.json'))
print('Session state:', cp.get('session_state'))
print('Stages completed:', cp.get('stages_completed'))
" || echo "NO_CHECKPOINT_FOUND"

# Verify no handoff receipt was created (session started independently)
test -f ".orchestrate/$SESSION_ID/handoff-receipt.json" && \
  echo "HANDOFF_RECEIPT: EXISTS (unexpected for independent session)" || \
  echo "HANDOFF_RECEIPT: NOT_FOUND (expected for independent start)"
```

### Pass Criteria
- [ ] `/auto-orchestrate` starts without error despite no handoff-receipt.json
- [ ] No `[HANDOFF]` or `[CHAIN]` error messages appear
- [ ] Pipeline completes all Stages 0-6 successfully
- [ ] Stage 6 completion message does NOT include "Return path" (no receipt to read)
- [ ] Session is recorded in `.sessions/index.json`

---

## HS-005: Multiple Sessions — Correct Session Selected When >1 auto-orchestrate Sessions Exist

**Gap Covered**: GAP-PIPE-005, GAP-NEW-002
**Risk**: Medium

### Preconditions
- Two completed auto-orchestrate sessions in `.sessions/index.json`
- Different gate-state.json for each (one with Gate 4 passed, one without)

### Setup Commands
```bash
# Create two sessions
mkdir -p ".orchestrate/auto-orc-20260413-old-project"
mkdir -p ".orchestrate/auto-orc-20260414-new-project"

# Old session: Gate 4 NOT passed
cat > ".orchestrate/auto-orc-20260413-old-project/gate-state.json" << 'EOF1'
{
  "session_id": "auto-orc-20260413-old-project",
  "project_name": "Old Project",
  "schema_version": "1.0",
  "gates": {
    "gate_1_intent_review": {"status": "passed"},
    "gate_2_scope_lock": {"status": "passed"},
    "gate_3_dependency_acceptance": {"status": "passed"},
    "gate_4_sprint_readiness": {"status": "pending"}
  }
}
EOF1

# New session: Gate 4 passed
cat > ".orchestrate/auto-orc-20260414-new-project/gate-state.json" << 'EOF2'
{
  "session_id": "auto-orc-20260414-new-project",
  "project_name": "New Project",
  "schema_version": "1.0",
  "gates": {
    "gate_1_intent_review": {"status": "passed"},
    "gate_2_scope_lock": {"status": "passed"},
    "gate_3_dependency_acceptance": {"status": "passed"},
    "gate_4_sprint_readiness": {"status": "passed", "passed_at": "2026-04-14T12:00:00Z"}
  }
}
EOF2

# Create sessions index with both sessions
mkdir -p ".sessions"
cat > ".sessions/index.json" << 'SIEOF'
{
  "schema_version": "1.0",
  "sessions": [
    {
      "session_id": "auto-orc-20260413-old-project",
      "command": "auto-orchestrate",
      "status": "complete",
      "created_at": "2026-04-13T09:00:00Z"
    },
    {
      "session_id": "auto-orc-20260414-new-project",
      "command": "auto-orchestrate",
      "status": "complete",
      "created_at": "2026-04-14T09:00:00Z"
    }
  ]
}
SIEOF
```

### Steps
1. With preconditions set (2 sessions)
2. Run: `/sprint-ceremony sprint-review`
3. Observe: session selection list is presented (most recent first)
4. Select session 1 (auto-orc-20260414-new-project — the most recent)
5. Observe: `[GATE-PASS]` displayed for new-project session
6. Reset: re-run and select session 2 (auto-orc-20260413-old-project)
7. Observe: `[GATE-BLOCK]` displayed for old-project session

### Expected Output
```
Multiple project sessions found. Which session is this sprint for?
1. auto-orc-20260414-new-project (2026-04-14, complete)
2. auto-orc-20260413-old-project (2026-04-13, complete)
Enter number (default: 1):
```

After selecting session 1:
```
[GATE-PASS] Gate 4 (Sprint Readiness) passed. Proceeding with ceremony.
```

After selecting session 2:
```
[GATE-BLOCK] Gate 4 (Sprint Readiness) has not passed. Cannot begin sprint execution.
Current status: pending
Run /gate-review sprint-readiness to complete gate review.
```

### Validation Commands
```bash
# Verify sessions/index.json has both sessions
python3 -c "
import json
idx = json.load(open('.sessions/index.json'))
sessions = [s for s in idx['sessions'] if s['command'] == 'auto-orchestrate']
sessions.sort(key=lambda x: x['created_at'], reverse=True)
print('Sessions (most recent first):')
for i, s in enumerate(sessions, 1):
    print(f'  {i}. {s[\"session_id\"]} ({s[\"created_at\"][:10]}, {s[\"status\"]})')
assert len(sessions) == 2, f'Expected 2 sessions, got {len(sessions)}'
print('MULTIPLE_SESSIONS: PASS')
"

# Verify gate states are different
python3 -c "
import json
gs_new = json.load(open('.orchestrate/auto-orc-20260414-new-project/gate-state.json'))
gs_old = json.load(open('.orchestrate/auto-orc-20260413-old-project/gate-state.json'))
assert gs_new['gates']['gate_4_sprint_readiness']['status'] == 'passed', 'New project should have Gate 4 passed'
assert gs_old['gates']['gate_4_sprint_readiness']['status'] == 'pending', 'Old project should have Gate 4 pending'
print('GATE_STATES_DIFFER: PASS')
print('New project Gate 4:', gs_new['gates']['gate_4_sprint_readiness']['status'])
print('Old project Gate 4:', gs_old['gates']['gate_4_sprint_readiness']['status'])
"
```

### Pass Criteria
- [ ] `/sprint-ceremony` displays numbered session selection list when >1 sessions found
- [ ] Most recent session appears as option 1
- [ ] Selecting new-project session results in `[GATE-PASS]`
- [ ] Selecting old-project session results in `[GATE-BLOCK]`
- [ ] Selected session's gate-state.json is used for Gate 4 check (not the other session's)

---

*Generated by software-engineer | Session auto-orc-20260414-pipeflow | Stage 3 | Task T-016*
