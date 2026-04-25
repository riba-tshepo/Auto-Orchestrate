---
name: sprint-goal-linker
description: |
  Author Sprint Goals and validate intent traces. Implements P-022 (Sprint
  Goal Authoring) and P-023 (Intent Trace Validation). Provides outcome-focused
  Sprint Goal templates, the canonical 3-line intent trace format
  (Project Intent → Scope Deliverable → Sprint Goal), and OKR alignment checks.
  Use when user says "sprint goal", "intent trace", "sprint goal authoring",
  "sprint kickoff goal", "validate intent trace".
triggers:
  - sprint goal
  - intent trace
  - sprint goal authoring
  - sprint kickoff goal
  - validate intent trace
---

# Sprint Goal Linker Skill

You author the Sprint Goal — a single sentence that defines what will be true at sprint end that is not true today — and validate the Intent Trace that connects the sprint to the project's original intent.

## When to use

| Trigger | Process | Pipeline node |
|---------|---------|---------------|
| Stage P4 (Sprint Bridge) lead | P-022 (Sprint Goal Authoring), P-023 (Intent Trace Validation) | engineering-manager produces Sprint Goal + Intent Trace in P4-sprint-kickoff-brief.md |

## How to use

### Step 1: Read the upstream artifacts

- Intent Brief: `.orchestrate/<session>/planning/P1-intent-brief.md` (Outcome statement)
- Scope Contract: `.orchestrate/<session>/planning/P2-scope-contract.md` (Deliverables, Success Metrics)
- Dependency Charter: `.orchestrate/<session>/planning/P3-dependency-charter.md` (timeline constraints)

### Step 2: Author the Sprint Goal

A Sprint Goal is **one sentence** that:

- States an **outcome**, not an output (what will be true, not what will be produced)
- Connects to a **specific deliverable** in the Scope Contract
- Is **achievable** within the sprint timebox
- Is **measurable** at sprint end (you can answer "did we achieve it?" definitively)

Read `references/sprint-goal-pattern.md` for the framing patterns.

### Step 3: Build the Intent Trace

Intent Trace is the canonical 3-line trace:

```
Project Intent: <verbatim from Intent Brief outcome>
        ↓
Scope Deliverable: <which deliverable from Scope Contract this sprint advances>
        ↓
Sprint Goal: <the sentence from Step 2>
```

Read `references/intent-trace-template.md` for the format.

### Step 4: Validate the trace

The trace passes validation if:

1. **Continuity**: each level connects to the previous (Sprint Goal advances Scope Deliverable; Scope Deliverable serves Project Intent)
2. **Specificity**: each level is more specific than the previous (Project Intent is broadest; Sprint Goal is most concrete)
3. **OKR alignment**: the Project Intent's strategic context cites a real OKR; the Sprint Goal preserves that connection
4. **Testability**: the Sprint Goal can be verified at sprint review (P-027) with definitive yes/no

If any check fails, surface to the engineering-manager (P4 lead) for revision.

### Step 5: Embed in P4 Sprint Kickoff Brief

The Sprint Goal becomes Section 1 of the Sprint Kickoff Brief. The Intent Trace becomes Section 2.

Example:

```markdown
## 1. Sprint Goal

By sprint end, the inventory service routes 25% of US-East-1 read traffic through
the new multi-region adapter without measurable latency regression (p95 ≤ 230ms).

## 2. Intent Trace

**Project Intent**: Reduce regional-inconsistency oversells by 80% within Q3 to
recover from CS escalation #4521.

         ↓ (advances)

**Scope Deliverable D-2**: Multi-region inventory adapter with consistency
guarantees per the Scope Contract Definition of Done.

         ↓ (advances)

**Sprint Goal**: By sprint end, the inventory service routes 25% of US-East-1
read traffic through the new multi-region adapter without measurable latency
regression (p95 ≤ 230ms).
```

## Sprint Goal anti-patterns

| Anti-pattern | Example | Fix |
|--------------|---------|-----|
| Output, not outcome | "Ship 5 user stories" | "By sprint end, returning customers can complete checkout via the new mobile flow" |
| Multiple goals | "Improve performance and reduce errors and add new features" | Pick the most important; defer the rest |
| Unmeasurable | "Make the app better" | "By sprint end, p95 latency on /checkout is ≤ 200ms" |
| Untraceable to deliverable | "Refactor the auth module" | Tie to a Scope Contract deliverable; if no deliverable supports refactoring, defer to a refactor sprint |
| All-or-nothing without partial credit framing | "Deploy multi-region" | "Deploy multi-region read traffic at 25% — full traffic deferred to next sprint" |
| Aspirational without commitment | "Try to improve search relevance" | "By sprint end, ship the BM25-tuned search to canary at 10%" |

## Intent Trace validation logic (inline, no script)

The validator (in this skill's body, not a separate script) checks:

1. **Project Intent is verbatim from Intent Brief** — paste from P1-intent-brief.md Section 1
2. **Scope Deliverable is one of the items in Scope Contract Section 2** — must reference an existing deliverable ID/name
3. **Sprint Goal references either**:
   - A measurable outcome from Success Metrics (P2 Section 5), OR
   - A specific user-facing capability from a Scope Contract deliverable's DoD
4. **The trace is downward-specific** — Project Intent is broadest (user/business outcome); Sprint Goal is most concrete (this sprint's deliverable)

If any check fails:
- Continuity break: "Sprint Goal does not advance the Scope Deliverable. The Sprint Goal X serves... but the Scope Deliverable Y requires..."
- Specificity violation: "Sprint Goal is broader than Scope Deliverable; sprint goals must narrow toward an outcome"
- OKR reference missing: "Intent Brief Section 3 must cite a specific OKR; current state is unverified"
- Testability fail: "Sprint Goal cannot be verified at sprint review; provide a measurable outcome"

## Related skills

- `spec-creator` — produces the Scope Contract that the Intent Trace references
- `story-generator` — converts the Sprint Goal into specific user stories with acceptance criteria
- `okr-retrospective-tracker` — at Phase 8, scores whether the Sprint Goal's stated outcome was achieved
- `validator` — at Stage 5, verifies the Sprint Goal's measurable outcome is met before declaring sprint complete

## Reference

- `references/sprint-goal-pattern.md` — outcome-not-output framing examples
- `references/intent-trace-template.md` — 3-line trace format
- Canonical processes: P-022 in `processes/04_sprint_delivery_execution.md`; P-023 in same file
