## Gate Enforcement Check (Required Before Any Ceremony)

Before facilitating any sprint ceremony, verify that Gate 4 (Sprint Readiness) has been passed.

### Step 1: Resolve Session ID

Check `.sessions/index.json` for the most recent auto-orchestrate session:

```bash
# Read most recent auto-orchestrate session with status "in_progress" or "complete"
python3 -c "
import json, os
idx_path = '.sessions/index.json'
if not os.path.exists(idx_path):
    print('NO_SESSIONS')
    exit()
sessions = json.load(open(idx_path)).get('sessions', [])
orc_sessions = [s for s in sessions if s.get('command','') == 'auto-orchestrate' and s.get('status','') in ('in_progress','complete')]
orc_sessions.sort(key=lambda x: x.get('created_at',''), reverse=True)
if orc_sessions:
    print(orc_sessions[0]['session_id'])
else:
    print('NO_SESSIONS')
"
```

**If multiple auto-orchestrate sessions found**: Present selection list (most recent first):
```
Multiple project sessions found. Which session is this sprint for?
1. auto-orc-20260414-myproj (2026-04-14, complete)
2. auto-orc-20260413-otherproj (2026-04-13, in_progress)
Enter number (default: 1):
```

**If NO_SESSIONS**: Advisory warning only (do not block — backward compatible):
```
[GATE-WARN] No auto-orchestrate session found. Gate 4 check skipped.
(If this sprint follows /new-project planning, ensure /gate-review sprint-readiness was completed.)
```
Proceed to ceremony selection.

### Step 2: Read Gate State

Read `.orchestrate/{session_id}/gate-state.json`:

```bash
GATE_STATE_PATH=".orchestrate/{session_id}/gate-state.json"
test -f "$GATE_STATE_PATH" && python3 -c "
import json
gs = json.load(open('$GATE_STATE_PATH'))
g4 = gs['gates']['gate_4_sprint_readiness']
print(g4['status'])
override = g4.get('override')
if override and override.get('reason') and override.get('authorized_by') and override.get('timestamp'):
    print('OVERRIDE_VALID')
" || echo "FILE_NOT_FOUND"
```

### Step 3: Enforce Gate

**If gate_4_sprint_readiness.status == "passed"**:
```
[GATE-PASS] Gate 4 (Sprint Readiness) passed. Proceeding with ceremony.
```
Continue to ceremony selection.

**If gate_4_sprint_readiness.status != "passed" AND no valid override**:
```
[GATE-BLOCK] Gate 4 (Sprint Readiness) has not passed. Cannot begin sprint execution.
Current status: {status}
Run /gate-review sprint-readiness to complete gate review.
```
**STOP — do not proceed with ceremony.**

**If OVERRIDE_VALID**:
```
[GATE-OVERRIDE] Gate 4 (Sprint Readiness) override active.
Authorized by: {override.authorized_by}
Reason: {override.reason}
Proceeding with ceremony.
```
Continue to ceremony selection.

**If FILE_NOT_FOUND** (gate-state.json does not exist):
```
[GATE-WARN] Gate state file not found for session {session_id}.
(If Gate 4 has not been reviewed, run /gate-review sprint-readiness first.)
Proceed without gate check? (Y/n, default: n)
```
If Y: proceed. If N or no response: stop.

---


# Sprint Ceremony

Facilitate a sprint ceremony with the right structure and agents.

## Instructions

Identify which ceremony from: $ARGUMENTS

### Available Ceremonies

#### Sprint Planning (P-022, P-023, P-024)
**Facilitator**: `engineering-manager`
**Participants**: `product-manager`, `software-engineer`, `qa-engineer`

Agenda:
1. Review sprint goal — PM presents, EM validates capacity
2. Story selection — Team pulls from refined backlog
3. Task breakdown — Engineers decompose stories
4. Capacity check — EM validates against team availability
5. Commitment — Team agrees to sprint scope
6. Sprint Readiness Gate (P-025) — All criteria met?

Output: Sprint backlog with committed stories, sprint goal, capacity allocation.

#### Daily Standup (P-026)
**Facilitator**: `engineering-manager`
**Participants**: All ICs

Format (per person, max 2 min):
1. What I completed since last standup
2. What I'm working on today
3. Blockers or risks

EM actions: Update burndown, escalate blockers, adjust assignments if needed.

#### Sprint Review (P-027)
**Facilitator**: `engineering-manager`
**Participants**: `product-manager`, `software-engineer`, stakeholders

Agenda:
1. Sprint goal recap — Did we meet it?
2. Demo completed features — Engineers present working software
3. Stakeholder feedback — Capture and prioritize
4. Metrics — Velocity, burndown, DoD compliance
5. Backlog impact — PM updates priorities based on feedback

#### Demo Evidence from Pipeline (if available)

Session ID is resolved from the Gate Enforcement Check above.

```bash
# Check for Stage 6 documentation artifacts
STAGE6_PATH=".orchestrate/${SESSION_ID}/stage-6/"
if [ -d "$STAGE6_PATH" ]; then
  echo "[SPRINT-REVIEW] Stage 6 artifacts found:"
  ls "$STAGE6_PATH"
else
  echo "[SPRINT-REVIEW] No Stage 6 artifacts found for session ${SESSION_ID}"
fi
```

If Stage 6 artifacts found: reference them as implementation evidence for the demo.
If not found: proceed with demo using other available evidence.

#### DoD Compliance from Pipeline (if available)

```bash
# Check for Stage 5 validation report
STAGE5_PATH=".orchestrate/${SESSION_ID}/stage-5/"
if [ -d "$STAGE5_PATH" ]; then
  echo "[SPRINT-REVIEW] Stage 5 validation report found:"
  ls "$STAGE5_PATH"
else
  echo "[SPRINT-REVIEW] No Stage 5 validation report found"
fi
```

If Stage 5 validation report found: use it as DoD compliance evidence (errors: 0, warnings: 0 = DoD passed at technical level).
If not found: use manual DoD checklist.

#### Sprint Retrospective (P-028)
**Facilitator**: `engineering-manager`
**Participants**: Full team

Format:
1. **What went well** — Celebrate successes, reinforce good practices
2. **What didn't go well** — Identify pain points without blame
3. **Action items** — Concrete improvements for next sprint (max 3)
4. Review previous retro actions — Were they completed?

Output: Action items with owners and due dates.

#### Backlog Refinement (P-029)
**Facilitator**: `product-manager`
**Participants**: `engineering-manager`, `software-engineer`, `qa-engineer`

Agenda:
1. PM presents upcoming stories
2. Team asks clarifying questions
3. Acceptance criteria refined
4. Estimation (story points or t-shirt sizing)
5. Dependencies identified
6. Stories marked "ready" or sent back for more detail

## Receipt Writing (STATE-001)

After completing a ceremony facilitation, write a receipt:

1. `mkdir -p .pipeline-state/command-receipts .pipeline-state/process-log`
2. Write `.pipeline-state/command-receipts/sprint-ceremony-<YYYYMMDD>-<HHMMSS>.json`:

```json
{
  "command": "sprint-ceremony",
  "receipt_id": "sprint-ceremony-<YYYYMMDD>-<HHMMSS>",
  "timestamp": "<ISO-8601>",
  "session_context": {
    "session_id": "<orchestrate session_id if available, else null>",
    "pipeline": "<auto-orchestrate|standalone>"
  },
  "inputs": {
    "ceremony_type": "<planning|standup|review|retrospective|refinement>"
  },
  "outputs": {
    "action_items": ["..."],
    "sprint_goal": "<if planning ceremony>",
    "ceremony_completed": true
  },
  "artifacts": [],
  "processes_executed": ["P-022"],
  "next_recommended_action": null,
  "dispatch_context": {
    "trigger_id": null,
    "invoked_by": null
  }
}
```

3. For each process executed, append to `.pipeline-state/process-log/<process-id>.jsonl` (STATE-003).

**Ceremony-to-process mapping**:

| Ceremony | Processes |
|----------|-----------|
| Sprint Planning | P-022, P-023, P-024 |
| Daily Standup | P-026 |
| Sprint Review | P-027 |
| Sprint Retrospective | P-028 |
| Backlog Refinement | P-029 |

If write fails, log warning and continue. See `_shared/protocols/cross-pipeline-state.md` for the full receipt schema.

## Usage

Which ceremony do you need help with? Provide the ceremony name or I'll help you choose based on your sprint cadence.
