---
name: cab-reviewer
description: |
  Conduct Pre-Launch Risk Review (Change Advisory Board / CAB) for HIGH-risk
  releases. Implements P-076 (Pre-Launch Risk Review) and supports P-048
  (Production Release Management). Produces a structured CAB Decision Record
  with risk classification, participant reviews, decision (Approve / Approve
  with Conditions / Reject / Defer), and conditions to satisfy before deploy.
  Tied to the `cab-review` human gate (HUMAN-GATE-001 #7) per CAB-GATE-001.
  Use when user says "cab review", "change advisory board", "pre-launch risk
  review", "production change approval".
triggers:
  - cab review
  - change advisory board
  - pre-launch risk review
  - production change approval
---

# CAB Reviewer Skill

You produce a Change Advisory Board (CAB) Decision Record for HIGH-risk releases. The CAB Decision Record is the input to the `cab-review` human gate (HUMAN-GATE-001 #7) and the precursor to the `release-readiness` gate at Phase 7.

## When to use

| Trigger | Process | Pipeline node |
|---------|---------|---------------|
| Phase 7 prelude when `release_flag == true` AND change is HIGH/CRITICAL risk | P-076 (Pre-Launch Risk Review) | technical-program-manager chairs CAB; spawns participant reviewers |

The CAB does NOT fire for LOW or MEDIUM risk changes — those proceed directly to the release-readiness gate.

## How to use

### Step 1: Classify risk

Read `references/risk-classification-rubric.md` and assess the change against the rubric. Risk classification is multi-dimensional:

- **Blast radius**: How many users, systems, services affected if this fails?
- **Reversibility**: Can we roll back? In how long?
- **Compliance/security**: Does this touch PII / payment / regulated data?
- **Novelty**: Is this a well-trodden path or a first-of-its-kind change?
- **Detection time**: How quickly would we detect a problem?

Classify as `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL`. CAB fires for HIGH and CRITICAL.

### Step 2: Spawn participant reviewers

The CAB chair (technical-program-manager) coordinates parallel reviews from:

- **technical-program-manager** (chair) — owns the Decision Record, classifies risk, runs the meeting
- **security-engineer** — security risk review (P-038, P-039, P-042)
- **sre** — operational risk review (rollback procedure, SLO impact, on-call readiness)
- **product-manager** — business risk + customer impact assessment
- **engineering-manager** — engineering capacity for rollback / incident response

Each writes their review to `.orchestrate/<session>/phase-7/cab/<role>-review.md`. The chair aggregates into the Decision Record.

### Step 3: Build the CAB Decision Record

Use the template in `references/cab-decision-record-template.md`. The record has 7 mandatory sections:

1. **Change Summary** — what is being deployed; scope; user impact
2. **Risk Classification** — final tier (HIGH or CRITICAL) with rubric scoring
3. **Participant Reviews** — verbatim sections from each reviewer
4. **Recommended Verdict** — Approve / Approve with Conditions / Reject / Defer
5. **Conditions** (if "Approve with Conditions") — list of conditions to satisfy before deploy
6. **Rollback Plan** — exact rollback procedure with timing estimates
7. **Decision Trail** — who reviewed, when, and final disposition

### Step 4: Submit to the cab-review human gate

Write the Decision Record to:
- `.orchestrate/<session>/phase-7/cab-decision-record.md`

The orchestrator's loop controller writes `gate-pending-cab-review.json` containing:
- `recommended_verdict` (from the Decision Record)
- `risk_classification`
- `evaluator_breakdown` (links to participant reviews)

The user reviews and writes `gate-approval-cab-review.json` with their decision.

### Step 5: Handle the approval outcome

| User decision | Pipeline behavior |
|---------------|-------------------|
| `approved` | Conditions (if any) become blocking findings on the release-readiness gate; proceed to Phase 7 RELEASE_PREP |
| `approved_with_edits` | User added/modified conditions; proceed with the edited list |
| `rejected` | Re-enter Stage 5 with feedback; CAB re-fires after remediation |
| `stop` | Terminate session with `terminal_state: "gate_rejected"` |

## Recommended verdicts and when to use them

### Approve

- Risk is HIGH but mitigations are confirmed in place
- All participant reviews are positive (no blockers)
- Rollback plan is rehearsed and time-bounded

### Approve with Conditions

- Most risk is mitigated, but a small set of conditions must be met before deploy
- Examples: "Confirm PagerDuty rotation includes new service", "Verify rollback rehearsal happens within 24h of deploy"
- Conditions become explicit checkbox items on the release-readiness artifact

### Reject

- A reviewer flags an unmitigated CRITICAL risk
- Rollback is impossible or takes longer than acceptable downtime
- Compliance review failed

### Defer

- Rare. Used when the change is sound but the timing is wrong (e.g., upcoming high-traffic event, compliance audit window)
- Re-fire CAB after the deferral window

## Outputs

- `.orchestrate/<session>/phase-7/cab-decision-record.md` — the Decision Record markdown
- `gate-pending-cab-review.json` (written by orchestrator from this skill's outputs)
- Per-reviewer artifacts in `.orchestrate/<session>/phase-7/cab/<role>-review.md`
- (After approval) Conditions cascade to the release-readiness gate's blocking findings

## Related skills

- `threat-modeler` — security review input for security-engineer's CAB review
- `slo-definer` — SLO impact input for sre's CAB review
- `release-notes-generator` — user-impact context for product-manager's CAB review
- `raid-logger` — register CAB conditions as RAID entries with severity HIGH
- `validator` — at Stage 5, verifies CAB conditions are satisfied before deploy

## Reference

- `references/cab-decision-record-template.md` — full template
- `references/risk-classification-rubric.md` — multi-dimensional risk rubric
- Canonical processes: P-076 in `processes/13_risk_change_management.md`; P-048 in `processes/07_infrastructure_platform.md`
- Pipeline constraint: `CAB-GATE-001` in `commands/auto-orchestrate.md`
