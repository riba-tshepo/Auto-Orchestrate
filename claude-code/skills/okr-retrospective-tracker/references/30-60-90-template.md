# 30/60/90 Day Outcome Measurement Template

P-073 mandates outcome measurement at 30, 60, and 90 days post-launch. This template provides the per-milestone structure.

## Schedule

The orchestrator's Phase 8 schedules these retrospectives automatically when the launch artifact is dated:

```
launch_date = <Phase 7 release date>
day_30 = launch_date + 30 days
day_60 = launch_date + 60 days
day_90 = launch_date + 90 days  # = "Final" retrospective
```

For each scheduled date, the orchestrator (re-)spawns the okr-retrospective-tracker skill with the appropriate milestone parameter.

## Per-milestone template

```markdown
# Outcome Measurement — Day <30 | 60 | 90>

**Project**: <name from Intent Brief>
**Launch date**: <ISO-8601>
**Measurement date**: <ISO-8601>
**Days since launch**: <integer>

## Linked artifacts

- Intent Brief: `.orchestrate/<session>/planning/P1-intent-brief.md`
- Scope Contract (Success Metrics section): `.orchestrate/<session>/planning/P2-scope-contract.md`
- Phase 7 Release Readiness Artifact: `.orchestrate/<session>/phase-7/release-readiness-artifact.md`
- Prior milestone retro (if any): `.orchestrate/<session>/phase-receipts/phase-8-okr-retrospective-day-<N>.md`

## KR trajectory

| KR | Baseline (Day 0) | Day 30 | Day 60 | Day 90 | Final score | Interpretation |
|----|------------------|--------|--------|--------|-------------|----------------|
| KR1 | <baseline value> | <value> | <value> | <value> | <0.0–1.0> | <on-track / at-risk / failed> |
| KR2 | ... | | | | | |
| KR3 | ... | | | | | |

(For Day 30, only fill Day 30 column; Day 60 fills both; Day 90 fills all.)

## Trajectory analysis

### On-track KRs

- **KR1**: <description>. Trajectory: <description>. Confidence in 90-day target: <high / medium / low>.

### At-risk KRs

- **KR2**: <description>. Why at-risk: <reason>. Recommended intervention: <action>.

### Failed KRs (only at Day 60+)

- **KR3**: <description>. Failure mode: <reason>. Decision: <retire / retry-with-revised-target / pivot>.

## Interventions

If any KR is at-risk:

| # | Intervention | Why | Owner | Due |
|---|--------------|-----|-------|-----|
| I1 | <action> | <reason> | <agent> | <date> |

If no interventions are needed (all on-track), state explicitly: "No interventions required at this milestone."

## Lessons emerging (so far)

What is the project teaching us, even mid-stream?

- <Insight>
- <Insight>

These feed into the **Final** (Day 90) retrospective's "What We Learned" section.

## Next milestone

**Next checkpoint**: Day <60 | 90 | "Final" closure>
**Pre-checkpoint actions**: <data collection, experiments, instrumented changes>

---
```

## Worked example — Day 30 retrospective

```markdown
# Outcome Measurement — Day 30

**Project**: Multi-region inventory failover
**Launch date**: 2026-04-25
**Measurement date**: 2026-05-25
**Days since launch**: 30

## Linked artifacts

- Intent Brief: `.orchestrate/auto-orc-20260420-inventory/planning/P1-intent-brief.md`
- Scope Contract: `.orchestrate/auto-orc-20260420-inventory/planning/P2-scope-contract.md`
- Phase 7 Release Readiness: `.orchestrate/auto-orc-20260420-inventory/phase-7/release-readiness-artifact.md`

## KR trajectory

| KR | Baseline (Day 0) | Day 30 | Day 60 | Day 90 | Final score | Interpretation |
|----|------------------|--------|--------|--------|-------------|----------------|
| KR1: Cross-region failover < 30s p95 | 90s p95 (manual) | 18s p95 (automated) | TBD | TBD | TBD | ✓ on track to hit stretch (target: ≤15s) |
| KR2: Reduce oversells from regional inconsistency by 80% | 47/month | 12/month → 74% reduction | TBD | TBD | TBD | ⚠️ behind 80% target; investigate |
| KR3: Customer NPS for inventory accuracy +10pp | 42 (Mar baseline) | 45 (May survey) | TBD | TBD | TBD | ✓ on track |

## Trajectory analysis

### On-track KRs

- **KR1**: Cross-region failover automated; 18s p95 well below 30s target. Confident we'll hit the 15s stretch by Day 90.
- **KR3**: NPS at +3pp at Day 30; trajectory consistent with 10pp by Day 90 if pattern holds.

### At-risk KRs

- **KR2**: 74% reduction (12/47) is short of the 80% target. Why at-risk: 8 of the 12 remaining oversells were from a third edge case (race during inventory writes from supplier feeds) we didn't anticipate.
  - **Recommended intervention**: Add inventory-write serialization for supplier feed path; expected to close ~5 of 8 remaining oversells.

### Failed KRs

(none at Day 30)

## Interventions

| # | Intervention | Why | Owner | Due |
|---|--------------|-----|-------|-----|
| I1 | Implement supplier-feed write serialization | Close 5/8 of remaining KR2 gap | software-engineer | 2026-06-08 (Day 44) |
| I2 | Instrument supplier-feed-specific SLI for oversells | Distinguish supplier vs customer-induced oversells | sre | 2026-06-01 (Day 37) |

## Lessons emerging (so far)

- The threat model (P-038) caught customer-side write contention but missed supplier-side; expand threat-modeler invocation to include data-source actors.
- Day-30 measurement was valuable: caught KR2 gap with 60 days runway to fix. Worth scheduling Day-15 mini-checks for high-stakes launches.

## Next milestone

**Next checkpoint**: Day 60 (2026-06-24)
**Pre-checkpoint actions**:
- I1 deployed and measured (target: by 2026-06-08)
- I2 instrumented and producing per-source breakdown (target: by 2026-06-01)
- Run 1 game-day failover exercise to verify KR1 holds under simulated regional outage
```

## When to use Day 60 vs Day 90

- **Day 30**: Catch problems early; ~70% of KR drift is visible
- **Day 60**: Verify Day-30 interventions worked; intervene again if needed
- **Day 90**: Final score; close the OKR cycle; feed lessons into next quarter

For OKRs with longer measurement cycles (e.g., enterprise sales metrics), extend to Day 180 or align with quarterly closes. The pattern stays the same; only the dates shift.

## Skipping milestones

DO NOT skip Day 30. It's the most valuable; gives the most runway to course-correct.

You may skip Day 60 if Day 30 showed all KRs on-track AND no new risks surfaced. Document the skip explicitly: "Day 60 retrospective skipped per Day 30 confidence; Day 90 will be the next checkpoint."

Day 90 is mandatory; it's the closure on the OKR cycle.
