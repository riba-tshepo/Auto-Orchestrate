---
name: okr-retrospective-tracker
description: |
  Score OKR achievement and produce structured retrospectives. Implements P-072
  (OKR Retrospective) and P-073 (Post-Launch Outcome Measurement at 30/60/90
  days). Provides Google-style 0.0–1.0 scoring per Key Result, retrospective
  templates (4 L's framework), 30/60/90-day milestone tracking, and intent
  back-trace to the original Intent Brief.
  Use when user says "okr retrospective", "outcome measurement", "30 60 90",
  "retrospective tracker", "score okr", "post-launch outcomes".
triggers:
  - okr retrospective
  - outcome measurement
  - 30 60 90
  - retrospective tracker
  - score okr
  - post-launch outcomes
---

# OKR Retrospective Tracker Skill

You score OKR achievement and produce structured retrospectives that close the loop on whether the Intent Brief's outcomes were realized.

## When to use

| Trigger | Process | Pipeline node |
|---------|---------|---------------|
| Phase 8 (Post-Launch) | P-072 (OKR Retrospective) | product-manager + engineering-manager produce retro at 30/60/90 days post-launch |
| Phase 8 (Post-Launch) | P-073 (Post-Launch Outcome Measurement 30/60/90) | product-manager measures outcomes at scheduled milestones |
| Phase 9 (Continuous Governance — risk sub-routine) | P-077 (Quarterly Risk Review) cross-link | engineering-manager references OKR achievement in quarterly risk review |

## How to use

### Step 1: Identify the OKRs in scope

Read:
- `.orchestrate/<session>/planning/P1-intent-brief.md` (Strategic Context section — references the OKR)
- `.orchestrate/<session>/planning/P2-scope-contract.md` (Success Metrics section — defines the Key Results)
- Production telemetry / dashboards (for actual measurements)

Each OKR has:
- **Objective** (qualitative statement of intent)
- **Key Results** (3–5 measurable outcomes)

### Step 2: Score each Key Result

Use Google's 0.0–1.0 scoring model:

| Score | Meaning |
|-------|---------|
| 1.0 | Hit the target (rarely; suggests the target was set too low) |
| 0.7 | "Stretch" achieved — most ambitious target reached |
| 0.6–0.7 | Solid achievement; on track |
| 0.4–0.5 | Partial; significant progress but missed target |
| 0.0–0.3 | Failed to make material progress |

Run the scoring script:

```
python3 ~/.claude/skills/okr-retrospective-tracker/scripts/score_okr.py \
  --target-value 100 --actual-value 78 --metric-direction higher_better
```

Returns:
```json
{
  "score": 0.78,
  "interpretation": "solid_achievement",
  "rationale": "Actual 78 vs target 100; achieved 78% of target",
  "score_band": "0.6-0.8 — solid achievement"
}
```

### Step 3: Build the OKR Retrospective document

Read `references/okr-scoring-rubric.md` for full scoring guidance and `references/30-60-90-template.md` for the milestone template. The retrospective has these sections:

```markdown
# OKR Retrospective — <Project / Outcome Name>

**Retrospective milestone**: <30-day | 60-day | 90-day | Final>
**Original Intent Brief**: `.orchestrate/<session>/planning/P1-intent-brief.md`
**Scope Contract**: `.orchestrate/<session>/planning/P2-scope-contract.md`
**Retrospective date**: <ISO-8601>

## Intent Back-Trace

**Original outcome statement** (from Intent Brief):
> <verbatim from P1>

**Original strategic context** (the OKR):
> <verbatim from P1 Section 3>

## Key Results Achievement

| KR | Target | Actual (at <milestone>) | Score | Interpretation |
|----|--------|-------------------------|-------|----------------|
| KR1: Reduce checkout abandonment by 15% | 15% reduction | 12% reduction | 0.80 | Solid achievement — close to target |
| KR2: ... | ... | ... | ... | ... |

**Aggregate OKR score**: <average of KR scores, weighted if needed>
**Achievement narrative**: <2–3 sentences>

## What Worked (Liked)

- <Specific things that worked — name the pattern, not just the outcome>
- ...

## What Didn't Work (Lacked)

- <Specific gaps — what didn't go to plan>
- ...

## What We Learned (Learned)

- <Insights for future projects, even when they didn't change the outcome>
- ...

## What We Need (Longed-for)

- <What would have made this better — process, tooling, capacity>
- ...

## Action Items

| # | Action | Owner | Due | Status |
|---|--------|-------|-----|--------|
| A1 | ... | ... | ... | open |
| A2 | ... | ... | ... | open |

Action items are appended to the RAID log via `raid-logger` so they're tracked across future sessions.

## Outcome Measurement (30/60/90)

If this is a 30/60/90 milestone:

### Milestone snapshot at <date>

[For each Key Result, show the trajectory]

| KR | Day 0 baseline | Day 30 | Day 60 | Day 90 | Trend |
|----|----------------|--------|--------|--------|-------|
| KR1 | 24% abandonment | 20% | 17% | 13% | ✓ on track |

### Trajectory analysis

- **On-track KRs**: <list>
- **At-risk KRs**: <list with reasoning>
- **Recommended interventions**: <if any KR is at-risk>

## Next milestone

**Next checkpoint**: <60-day or 90-day or "final post-launch retro">
**Next checkpoint date**: <ISO-8601>
**Pre-checkpoint actions**: <any data collection or experiments needed>
```

### Step 4: Write outputs

- Retrospective document at: `.orchestrate/<session>/phase-receipts/phase-8-okr-retrospective-<milestone>.md`
- Action items appended to RAID log via `raid-logger` (severity = MEDIUM unless an at-risk KR escalates to HIGH)
- (At 90-day or Final) Update Intent Brief footer with retrospective links for future cross-session learning

## Outcome measurement schedule

For Phase 8 (Post-Launch), the orchestrator schedules 3 retrospectives:

- **Day 30**: Initial outcome read; identify off-track KRs early
- **Day 60**: Intervention check; were Day-30 corrections effective?
- **Day 90**: Final retrospective; closure on the OKR cycle

For longer outcomes (e.g., quarterly OKRs), extend to Day 180 or end-of-quarter.

## Anti-patterns

| Anti-pattern | Fix |
|--------------|-----|
| Only scoring at the end (no Day 30 / Day 60 reads) | Schedule milestones so corrections can happen mid-cycle |
| Scoring 1.0 frequently | Targets set too low; aim for 0.6–0.7 stretch goals |
| Cherry-picking KRs to score (skipping the failed ones) | Score every KR; "0.2 — failed" is valuable signal |
| Action items without owners | Every action item gets a named agent; otherwise drops |
| Retrospective without RAID log update | Lessons learned vanish without persistence; always `raid-logger` |
| Same Key Results next quarter | If KRs achieved 0.7+, raise targets; if KRs failed 0.3-, change strategy or retire the OKR |

## Related skills

- `raid-logger` — append retrospective action items as RAID entries
- `release-notes-generator` — release notes consume the OKR achievement narrative
- `validator` — at any milestone, validates that measured outcomes match Intent Brief
- `slo-definer` — operational KRs may be SLO-shaped; cross-reference

## Reference

- `references/okr-scoring-rubric.md` — full 0.0–1.0 scoring rubric with examples
- `references/30-60-90-template.md` — milestone template with worked example
- Canonical processes: P-072 in `processes/12_post_delivery_retrospective.md`; P-073 in same file
