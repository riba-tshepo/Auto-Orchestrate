---
name: story-generator
description: |
  Convert deliverables and epics into INVEST-compliant user stories with acceptance criteria.
  Implements P-024 (Story Writing) and supports P-029 (Backlog Refinement). Produces
  stories in the canonical format (As a <role>, I want <goal>, so that <benefit>) with
  ≥2 acceptance criteria per story, Fibonacci point estimate, and split detection for
  stories too large for a sprint.
  Use when user says "write user story", "story writing", "backlog refinement",
  "convert deliverable to stories", "user story format", "acceptance criteria".
triggers:
  - write user story
  - story writing
  - backlog refinement
  - convert deliverable to stories
  - user story format
  - acceptance criteria seeds
---

# Story Generator Skill

You convert Scope Contract deliverables (or epic descriptions) into INVEST-compliant user stories with acceptance criteria, point estimates, and split decisions.

## When to use

| Trigger | Process | Pipeline node |
|---------|---------|---------------|
| Stage P4 (Sprint Bridge) co-agent | P-024 (Story Writing) | product-manager produces P4-stories.md |
| PHASE: BACKLOG_REFINEMENT (iteration boundary or post-Sprint Retro) | P-029 (Backlog Refinement) | product-manager refines NOT-READY items |

## How to use

### Step 1: Read inputs
- Scope Contract at `.orchestrate/<session>/planning/P2-scope-contract.md` (Deliverables table)
- Sprint Retro action items at `.orchestrate/<session>/meetings/meeting-p-028-sprint-retro-*.json` (if doing Backlog Refinement)
- Existing backlog at `.pipeline-state/workflow/task-board.json`

### Step 2: For each deliverable, draft 1–N stories

Use the canonical format:

> As a `<persona/role>`,
> I want `<capability/action>`,
> so that `<benefit/outcome>`.

Each story MUST have:
- ≥2 testable acceptance criteria (Given/When/Then format preferred)
- A Fibonacci estimate (1, 2, 3, 5, 8, 13)
- A named assignee role (e.g., `software-engineer`, not a person)
- Priority (P0/P1/P2)

### Step 3: Apply INVEST checks

Read `references/invest-criteria.md` and verify each story is:
- **I**ndependent — no dependency on another story in the same sprint
- **N**egotiable — implementation details are flexible, outcomes are not
- **V**aluable — has clear user/business value
- **E**stimable — engineers can produce a credible point estimate
- **S**mall — fits in a sprint (typically ≤8 points)
- **T**estable — acceptance criteria are verifiable

Stories that fail **S** (Small) MUST be split. Document the split decision in the output.

### Step 4: Run the validator

```
python3 ~/.claude/skills/story-generator/scripts/validate_story.py \
  --input .orchestrate/<session>/planning/P4-stories.md
```

The validator returns JSON with per-story INVEST verdicts and overall pass/fail.

### Step 5: Write output

Write the story document to:
- `.orchestrate/<session>/planning/P4-stories.md` (when invoked at P4)
- `.orchestrate/<session>/meetings/meeting-p-029-backlog-refinement-iter-<N>.md` (when invoked at PHASE: BACKLOG_REFINEMENT)

Follow the structure in `references/story-template.md`.

## Output format

```markdown
# Sprint Stories — [Sprint Name]

**Source deliverables**: [from Scope Contract]
**Generated at**: <ISO-8601>
**Sprint capacity**: <X> points; **Total estimated**: <Y> points; **Within capacity**: yes/no

## Stories

### Story <ID>: <Title>

**As a** <role>
**I want** <capability>
**so that** <benefit>

**Priority**: P0 | P1 | P2
**Estimate**: <Fibonacci> points
**Assignee**: <agent role>

**Acceptance Criteria**:
1. Given <context>, When <action>, Then <outcome>
2. Given <context>, When <action>, Then <outcome>

**INVEST verdict**: PASS | FAIL (<which criterion failed>)

---

## Stories Split (too large for one sprint)

[Document any deliverable that was split into multiple stories]

## Stories Deferred (NOT-READY items)

[Items that lack acceptance criteria or estimates and need more refinement]
```

## Related skills

- `spec-creator` — produces the Scope Contract that this skill consumes
- `validator` — verifies stories at Stage 5 against acceptance criteria
- `okr-retrospective-tracker` — verifies story outcomes traced to OKRs at Phase 8

## Reference

- `references/invest-criteria.md` — INVEST framework explanation + checklist
- `references/story-template.md` — canonical story format with examples
- Canonical processes: P-024 in `processes/04_sprint_delivery_execution.md`
