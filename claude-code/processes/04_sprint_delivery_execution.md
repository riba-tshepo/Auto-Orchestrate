# Technical Specification: Sprint & Delivery Execution Processes (P-022 to P-031)

**Session**: auto-orc-20260405-procderive
**Date**: 2026-04-05
**Stage**: 2 — Process Specification
**Category**: 4 — Sprint & Delivery Execution
**Source**: Process Architecture (Stage 1), Clarity of Intent (Stage 4: Sprint Bridge), Engineering Team Structure Guide (Section 11: Delivery Methodology)
**Processes Covered**: P-022, P-023, P-024, P-025, P-026, P-027, P-028, P-029, P-030, P-031

> **Quick Reference**: A lightweight stub version is available at `processes/process_stubs/sprint_planning_stub.md`

---

## Category Overview

Sprint & Delivery Execution encompasses all processes that translate locked scope and committed dependencies into sprint-level work, execute that work through daily development cycles, and close each sprint with structured review and improvement ceremonies. This is the largest process category (10 processes) because it covers the full sprint lifecycle: preparation (P-022 through P-025), active execution (P-026, P-030, P-031), sprint closure (P-027, P-028), and continuous refinement (P-029).

All ten processes derive primarily from Clarity of Intent Stage 4 (Sprint Bridge) and the Engineering Team Structure Guide Section 11 (Delivery Methodology and Framework). The category begins after the Dependency Acceptance Gate (P-019) passes and the Sprint Readiness Gate (P-025) authorizes sprint planning. The Sprint Kickoff Brief — a one-page per-squad document produced by P-022, P-023, P-024, and P-030 — is the primary pre-sprint artifact. During active sprints, P-026 (Daily Standup), P-030 (Sprint-Level Dependency Tracking), and P-031 (Feature Development) govern daily execution. P-027 (Sprint Review), P-028 (Sprint Retrospective), and P-029 (Backlog Refinement) close the loop.

### Process Dependency Graph (Internal to Category)

```
P-019 (Dependency Acceptance Gate — EXTERNAL prerequisite)
P-013 (Scope Lock Gate — EXTERNAL prerequisite)
  |
  v
P-022: Sprint Goal Authoring
  |
  +---> P-023: Intent Trace Validation (requires P-022)
  |
  +---> P-024: Story Writing (requires P-022)
  |
  +---> P-030: Sprint-Level Dependency Tracking (requires P-019)
  |
  v
P-025: Sprint Readiness Gate (requires P-022, P-023, P-024, P-030)
  |
  v  (sprint begins)
P-026: Daily Standup (runs every working day during sprint)
  |
P-031: Feature Development (runs continuously during sprint)
  |
  v  (sprint ends)
P-027: Sprint Review (requires sprint completion)
  |
  v
P-028: Sprint Retrospective (requires P-027)
  |
P-029: Backlog Refinement (runs weekly, feeds next P-024 cycle)
```

Note: P-022, P-024, and P-030 can begin in parallel once external prerequisites are met. P-023 depends on P-022 completing first. P-025 is a convergence gate requiring all four preparation processes. P-026, P-030, and P-031 operate concurrently during active sprints. P-027, P-028, and P-029 form the sprint closure sequence. The entire graph repeats every sprint (typically 2 weeks).

### Agent Involvement Summary

| Agent ID | Processes (Primary) | Processes (Supporting) |
|----------|-------------------|----------------------|
| engineering-manager | P-022, P-023, P-025, P-027, P-028 | P-026, P-030 |
| product-manager | P-024, P-026, P-029 | P-022, P-023, P-025, P-027, P-028 |
| software-engineer | P-031 | P-022, P-024, P-025, P-026, P-027, P-028, P-029 |
| technical-program-manager | P-030 | P-025 |
| qa-engineer | — | P-024, P-031 |
| platform-engineer | — | P-031 |

---

## P-022: Sprint Goal Authoring Process

### 1. Process ID and Name
**P-022** — Sprint Goal Authoring Process

### 2. Purpose
Produce a single-sentence sprint goal connected to a specific Scope Contract deliverable. The sprint goal is the north star for all sprint work — every story, task, and decision in the sprint should serve this goal. Without a clear sprint goal, teams drift toward task completion rather than outcome achievement, and sprint reviews devolve into status meetings rather than outcome inspections.

### 3. Derived From
Clarity of Intent — Stage 4: Sprint Bridge, Section 1 (Sprint Goal)

Relevant source text: "One sentence. What will be true at the end of this sprint that is not true today?" with examples: Good — "By the end of Sprint 1, the tokenization SDK is integrated in the staging environment and the threat model review is complete." Bad — "Make progress on checkout."

Engineering Team Structure Guide — Section 11.2: Sprint Planning ceremony ("Select sprint backlog; define sprint goal; assign work") and Section 11.4 OKR cascade ("Sprint Goals — 2-week increments; each sprint goal pays into a Key Result").

### 4. Primary Owner Agent
**engineering-manager** — The EM owns the sprint goal authoring process because EMs own delivery outcomes (EM-001 people-first, but delivery accountability is explicit in the EM scope: "1:1s, sprint health, hiring within squad, impediment removal"). The EM translates the Scope Contract deliverable into a sprint-level commitment that is achievable given team capacity (EM-006 data-driven — velocity data informs goal ambition).

### 5. Supporting Agents
- **software-engineer** (Tech Lead) — The TL validates the sprint goal's technical achievability. The TL's single-team technical depth ensures the goal reflects real technical constraints, not aspirational scheduling. If the TL flags that the goal requires dependencies not yet resolved, the goal must be adjusted.
- **product-manager** — The PM validates that the sprint goal aligns to a specific Scope Contract deliverable and advances the project's intended outcome. The PM's outcomes-over-outputs orientation (PM-001) prevents sprint goals that describe activities rather than observable conditions.

### 6. Stages/Steps

| Step | Actor | Action | Output |
|------|-------|--------|--------|
| 1. Select Target Deliverable | EM + TL + PM | Review the Scope Contract deliverables. Identify which deliverable(s) should be advanced this sprint, considering: dependency readiness (P-019 commitments), team velocity (rolling 3-sprint average), and deliverable sequencing from the critical path (P-016). | Selected deliverable(s) for this sprint |
| 2. Assess Capacity | EM | Calculate available capacity for this sprint: team size minus planned leave, on-call rotations, carry-over work from previous sprint, and non-project commitments (operational work, tech debt). Use rolling 3-sprint velocity average as the baseline. | Sprint capacity assessment |
| 3. Draft Sprint Goal | EM + TL | Write the sprint goal as one sentence in the form: "By the end of Sprint N, [observable condition] that is not true today." The observable condition must be specific enough that at sprint end, the team can unambiguously assess whether the goal was achieved. | Draft sprint goal |
| 4. PM Alignment Check | PM | PM reviews the draft sprint goal against the Scope Contract. Confirms: (a) the goal maps to a specific deliverable, (b) the goal advances the project's intended outcome as stated in the Intent Brief, (c) the goal's ambition is appropriate given the deliverable's remaining scope. | PM-validated sprint goal |
| 5. TL Feasibility Check | TL | TL reviews the goal for technical achievability within the sprint. Confirms: (a) no unresolved dependencies block the goal, (b) the technical work required fits within the capacity assessment, (c) no hidden technical debt or prerequisite work was overlooked. | TL-validated sprint goal |
| 6. Publish Sprint Goal | EM | Enter the sprint goal into the Sprint Kickoff Brief Section 1. The goal must be visible to every team member before sprint planning begins. | Sprint Kickoff Brief Section 1 complete |

### 7. Inputs
- Locked Scope Contract (output of P-013) — deliverables table, Definition of Done, deliverable sequencing
- Locked Dependency Charter (output of P-019) — committed dependency timelines, current statuses
- Team velocity data — rolling 3-sprint average (Engineering Team Structure Guide Section 11.2)
- Team capacity data — planned leave, on-call schedule, competing commitments
- Previous sprint outcome — carry-over stories, unfinished work
- Critical Path analysis (P-016 output) — deliverable sequencing constraints

### 8. Outputs/Artifacts
- **Sprint Goal Statement** (Section 1 of Sprint Kickoff Brief) — One sentence in the form "By the end of Sprint N, [observable condition] that is not true today"
- **Deliverable Mapping** — Explicit reference to the Scope Contract deliverable the goal serves

### 9. Gate/Checkpoint
**Sprint Readiness Gate (P-025)** — The sprint goal is the first item checked at the readiness gate. Pass criteria specific to this process:
- Sprint goal is stated as one sentence
- Sprint goal references a specific observable condition, not an activity ("integrated" not "working on")
- Sprint goal traces to a named Scope Contract deliverable
- EM, TL, and PM have all validated the goal

### 10. Success Criteria
- Sprint goal is exactly one sentence
- Sprint goal describes an observable condition ("what will be true"), not an activity ("what we will work on")
- Sprint goal traces to a specific Scope Contract deliverable by name and ID
- TL has confirmed technical achievability given current dependency statuses
- PM has confirmed alignment to project intent
- Every engineer on the squad can recite the sprint goal after reading the Sprint Kickoff Brief
- At sprint end, the goal is unambiguously assessable as achieved, partially achieved, or not achieved

### 11. Dependencies
| Dependency | Process | Type | Detail |
|-----------|---------|------|--------|
| Scope Lock Gate passed | P-013 | Hard prerequisite | Cannot author a sprint goal without knowing which deliverables exist and what done looks like |
| Dependency Acceptance Gate passed | P-019 | Hard prerequisite | Dependency commitments must be locked before committing to a sprint goal that depends on them |
| Critical Path Analysis | P-016 | Informational | Deliverable sequencing from the critical path informs which deliverable to target this sprint |
| Previous Sprint Review | P-027 | Informational (sprints 2+) | Carry-over work and feedback from the previous sprint review informs the next sprint goal |

### 12. Traceability
- **Upstream**: P-013 (Scope Lock Gate) — deliverables and Definition of Done define the goal's target space
- **Upstream**: P-019 (Dependency Acceptance Gate) — locked dependency commitments constrain what is achievable
- **Downstream**: P-023 (Intent Trace Validation) — sprint goal is the third line of the intent trace
- **Downstream**: P-024 (Story Writing) — stories are decomposed from the sprint goal's target deliverable
- **Downstream**: P-025 (Sprint Readiness Gate) — sprint goal is the first pass criterion
- **Downstream**: P-027 (Sprint Review) — sprint goal is the assessment baseline at review
- **OKR cascade**: Company OKR → Engineering OKR → Team OKR → Sprint Goal → Stories (Engineering Team Structure Guide Section 11.4)
- **Artifact**: Sprint Kickoff Brief Section 1

---

## P-023: Intent Trace Validation Process

### 1. Process ID and Name
**P-023** — Intent Trace Validation Process

### 2. Purpose
Verify that a three-line intent trace (project intent, scope deliverable, sprint goal) is visible in every Sprint Kickoff Brief. The intent trace is the traceability mechanism that connects an engineer's daily work to the project's business intent. Without it, engineers lose context within the first sprint and begin making decisions that optimize locally but misalign globally. The Clarity of Intent framework's effectiveness depends on this trace being maintained and visible at all times.

### 3. Derived From
Clarity of Intent — Stage 4: Sprint Bridge, Section 2 (Intent Trace)

Relevant source text: "A three-line trace from the sprint goal to the project intent, so every engineer can see the connection." with format:
```
Project Intent:    Reduce mobile checkout abandonment from 34% to 20%
Scope Deliverable: Payment tokenization integration (Deliverable 3)
Sprint Goal:       Tokenization SDK integrated in staging; threat model complete
```

Also derived from the Clarity of Intent measurement signal: "Intent alignment — At any point, ask a random engineer on the project: 'Why are we building this?' — can they answer in one sentence? — Healthy state: Yes, consistently."

### 4. Primary Owner Agent
**engineering-manager** — The EM owns the Sprint Kickoff Brief and is responsible for ensuring the intent trace is present. The EM's people-first orientation (EM-001) extends to ensuring every team member understands why their work matters — the intent trace is the mechanism for this.

### 5. Supporting Agents
- **product-manager** — The PM validates the accuracy of the intent trace. The PM confirms that the "Project Intent" line matches the Intent Brief outcome statement verbatim, and the "Scope Deliverable" line matches a deliverable from the locked Scope Contract. The PM's ownership of the Intent Brief (co-authored, PM-001) and Scope Contract (PM owns, Stage 2) makes them the authoritative validator.

### 6. Stages/Steps

| Step | Actor | Action | Output |
|------|-------|--------|--------|
| 1. Extract Intent Statement | EM | Copy the outcome statement from the locked Intent Brief (P-001/P-004 output) verbatim. Do not paraphrase. If the intent has been updated via a Scope Change Request (P-014), use the latest version. | Project Intent line |
| 2. Extract Scope Deliverable | EM | Copy the deliverable name and ID from the locked Scope Contract that this sprint's goal serves. The deliverable must match the one selected in P-022 (Sprint Goal Authoring). | Scope Deliverable line |
| 3. Extract Sprint Goal | EM | Copy the sprint goal authored in P-022 verbatim. | Sprint Goal line |
| 4. Compose Intent Trace | EM | Assemble the three lines in the Sprint Kickoff Brief Section 2 using the exact format: `Project Intent: [verbatim]`, `Scope Deliverable: [name and ID]`, `Sprint Goal: [verbatim]`. | Intent Trace in Sprint Kickoff Brief |
| 5. PM Accuracy Review | PM | PM reviews the trace for accuracy: (a) Project Intent line matches the current Intent Brief outcome statement, (b) Scope Deliverable line references a real deliverable from the current Scope Contract version, (c) Sprint Goal line matches P-022 output. If any line is inaccurate, PM flags the specific discrepancy. | PM-validated intent trace |
| 6. Engineer Comprehension Check | EM | At sprint planning (or as part of the Sprint Readiness Gate P-025), the EM asks one or more engineers to read the trace and explain the project intent in one sentence. This is not a test — it validates that the trace is clear enough to communicate intent. | Comprehension confirmation |

### 7. Inputs
- Locked Intent Brief (output of P-004 Intent Review Gate) — outcome statement
- Locked Scope Contract (output of P-013 Scope Lock Gate) — deliverable name and ID
- Sprint Goal (output of P-022) — one-sentence sprint goal
- Current Scope Contract version (may have been updated via P-014 Scope Change Control)

### 8. Outputs/Artifacts
- **Intent Trace** (Section 2 of Sprint Kickoff Brief) — Three-line trace in the format:
```
Project Intent:    [Intent Brief outcome statement — verbatim]
Scope Deliverable: [Scope Contract deliverable name and ID]
Sprint Goal:       [One-sentence sprint goal from P-022]
```

### 9. Gate/Checkpoint
**Sprint Readiness Gate (P-025)** — Intent trace visibility is the second pass criterion. Pass criteria specific to this process:
- Intent trace is present in the Sprint Kickoff Brief
- All three lines are accurate (validated by PM)
- At least one engineer can explain the project intent after reading the trace

### 10. Success Criteria
- Intent trace is present in every Sprint Kickoff Brief for every sprint
- Project Intent line is a verbatim copy from the current Intent Brief (not paraphrased)
- Scope Deliverable line references a real deliverable from the current Scope Contract version
- Sprint Goal line matches the P-022 output exactly
- A randomly selected engineer on the team can explain the project intent in one sentence after reading the trace
- The intent trace is updated if a Scope Change Request (P-014) modifies the Intent Brief or Scope Contract

### 11. Dependencies
| Dependency | Process | Type | Detail |
|-----------|---------|------|--------|
| Intent Review Gate passed | P-004 | Hard prerequisite | The Intent Brief must be locked to provide the Project Intent line |
| Scope Lock Gate passed | P-013 | Hard prerequisite | The Scope Contract must be locked to provide the Scope Deliverable line |
| Sprint Goal authored | P-022 | Hard prerequisite | The sprint goal must exist before the trace can be composed |
| Scope Change Control | P-014 | Conditional | If scope has changed, the trace must reflect the latest versions of Intent Brief and Scope Contract |

### 12. Traceability
- **Upstream**: P-004 (Intent Review Gate) — Intent Brief outcome statement is the first trace line
- **Upstream**: P-013 (Scope Lock Gate) — Scope Contract deliverable is the second trace line
- **Upstream**: P-022 (Sprint Goal Authoring) — sprint goal is the third trace line
- **Downstream**: P-025 (Sprint Readiness Gate) — intent trace visibility is a gate pass criterion
- **Downstream**: P-027 (Sprint Review) — the trace provides context for evaluating sprint outcomes against project intent
- **Measurement**: Clarity of Intent measurement signal "Intent alignment" directly tests this process's effectiveness
- **Artifact**: Sprint Kickoff Brief Section 2

---

## P-024: Story Writing Process

### 1. Process ID and Name
**P-024** — Story Writing Process

### 2. Purpose
Decompose Scope Contract deliverables into sprint-sized stories with binary, testable acceptance criteria written in Given/When/Then format or as checklist conditions. Stories are the atomic unit of delivery — they connect the abstract (deliverable) to the concrete (what an engineer builds in a day or two). Without properly written stories and acceptance criteria, "done" becomes subjective, QA cannot verify work, and sprint reviews cannot assess completion.

### 3. Derived From
Clarity of Intent — Stage 4: Sprint Bridge, Section 3 (Stories and Acceptance Criteria)

Relevant source text: "Each story in the sprint backlog gets acceptance criteria written in 'Given / When / Then' format or as a checklist of testable conditions." with tabular examples including story, acceptance criteria, points, and assignee.

Also derived from Engineering Team Structure Guide Section 11.2: Sprint artifacts ("Sprint Backlog: Team-owned list of work committed for the current sprint") and Definition of Done ("Agreed criteria that work must meet before it's counted as complete").

### 4. Primary Owner Agent
**product-manager** — The PM owns story writing because PMs own what gets built and why (PM-001 outcomes over outputs). The PM's core competency is translating deliverables into user-facing value statements with measurable acceptance criteria (PM-006: "every user story has binary pass/fail criteria"). The PM defines what done looks like; the TL defines how to build it.

### 5. Supporting Agents
- **software-engineer** (Tech Lead) — The TL validates technical scope and sizing. The TL ensures each story is completable within a single sprint, identifies technical dependencies between stories, and flags stories that require prerequisite work not yet accounted for. The TL's level-aware behavior (SE complexity classification) helps size stories appropriately.
- **qa-engineer** — QA validates the testability of acceptance criteria. Every criterion must be binary (pass or fail) and testable without ambiguity. QA's Definition of Done enforcement mandate (QA-001) ensures criteria are not vague. QA also identifies stories that need specific test types (integration, performance, security) beyond unit tests.

### 6. Stages/Steps

| Step | Actor | Action | Output |
|------|-------|--------|--------|
| 1. Identify Sprint Scope | PM + TL | Take the deliverable(s) targeted by the sprint goal (P-022). Identify which portions of the deliverable can be completed this sprint, informed by the Definition of Done from the Scope Contract Section 3. | Sprint scope within the target deliverable |
| 2. Decompose into Stories | PM + TL | Break the sprint scope into discrete stories. Each story represents a user-facing or system-facing capability that can be independently implemented, tested, and demonstrated. Use the format: "As a [persona], I want [action] so that [outcome]" for user-facing stories. Technical stories follow: "[Component/system] must [capability] so that [downstream need]." | Draft story list |
| 3. Write Acceptance Criteria | PM | For each story, write acceptance criteria in Given/When/Then format or as a testable checklist. Each criterion must be binary — a reviewer can determine "met" or "not met" without interpretation. Criteria derive from the Scope Contract Definition of Done for the parent deliverable. | Stories with acceptance criteria |
| 4. QA Testability Review | QA | QA reviews each story's acceptance criteria. For each criterion, QA asks: "Can I write a test (manual or automated) that proves this criterion is met?" If no, QA flags the criterion as untestable and suggests a rewrite. QA also identifies criteria that need specific test types. | QA-validated acceptance criteria |
| 5. TL Sizing and Sequencing | TL | TL reviews each story for size: can it be completed within the sprint? Stories estimated at >50% of a single engineer's sprint capacity should be split. TL also identifies technical sequencing: which stories must be completed before others? | Sized and sequenced story backlog |
| 6. Point Estimation | TL + Engineers | Team estimates story points using planning poker or similar technique. The estimate reflects complexity and uncertainty, not calendar time. Use team's established scale (typically Fibonacci: 1, 2, 3, 5, 8, 13). Stories estimated at 13+ should be split. | Point-estimated stories |
| 7. Assign Stories | EM + TL | Assign stories to individual engineers based on expertise, development goals, and load balancing. Each story has exactly one assignee responsible for delivery (though pairing/collaboration is encouraged). | Sprint backlog with assignees |
| 8. Enter Sprint Backlog | PM | Stories entered into the team's sprint backlog tool. Each entry includes: story description, acceptance criteria, point estimate, assignee, parent deliverable reference (Scope Contract ID). | Populated sprint backlog |

### 7. Inputs
- Locked Scope Contract (output of P-013) — deliverables table (Section 2), Definition of Done (Section 3)
- Sprint Goal (output of P-022) — defines which deliverable(s) to target
- Team velocity data — rolling 3-sprint average determines how many points the team should commit to
- Refined backlog (output of P-029) — stories from previous refinement sessions that are already "ready"
- Previous sprint carry-over — incomplete stories from the previous sprint

### 8. Outputs/Artifacts
- **Sprint Backlog** — Complete set of stories for the sprint, each containing:

| Story | Acceptance Criteria | Points | Assignee | Parent Deliverable |
|-------|-------------------|--------|----------|-------------------|
| [Story title] | [Given/When/Then or checklist] | [Fibonacci] | [Engineer name] | [Scope Contract deliverable ID] |

- **Sprint Kickoff Brief Section 3** — Stories and acceptance criteria table (subset published in the brief)

### 9. Gate/Checkpoint
**Sprint Readiness Gate (P-025)** — All stories must have written acceptance criteria before sprint planning begins. Pass criteria specific to this process:
- Every story in the sprint backlog has written acceptance criteria
- Every criterion is testable (QA has validated)
- No story is sized larger than can be completed in the sprint
- Total committed points align with team velocity (rolling 3-sprint average, not aspirational)

### 10. Success Criteria
- Every story in the sprint backlog has written, binary acceptance criteria
- Every criterion is testable — QA can write a manual or automated test for it
- No story exceeds the team's single-sprint capacity threshold (typically 8 story points)
- Total committed story points are within +/- 10% of rolling 3-sprint velocity average
- Each story traces to a specific Scope Contract deliverable (parent deliverable reference)
- PM has authored acceptance criteria that define observable outcomes, not implementation steps
- TL has confirmed that story sequencing respects technical dependencies

### 11. Dependencies
| Dependency | Process | Type | Detail |
|-----------|---------|------|--------|
| Scope Lock Gate passed | P-013 | Hard prerequisite | Deliverables and Definition of Done must be locked |
| Sprint Goal authored | P-022 | Hard prerequisite | Sprint goal defines which deliverable(s) to decompose |
| Backlog Refinement | P-029 | Informational | Previously refined stories may already be ready; reduces P-024 effort |
| Test Architecture Design | P-032 | Informational | Test architecture informs which acceptance criteria need specific test types |

### 12. Traceability
- **Upstream**: P-013 (Scope Lock Gate) — deliverables and Definition of Done are the decomposition targets
- **Upstream**: P-022 (Sprint Goal) — goal defines which deliverables to target this sprint
- **Upstream**: P-029 (Backlog Refinement) — pre-refined stories flow into sprint planning
- **Downstream**: P-025 (Sprint Readiness Gate) — story completeness is a gate pass criterion
- **Downstream**: P-031 (Feature Development) — stories with acceptance criteria are the input to development
- **Downstream**: P-027 (Sprint Review) — completed stories are demonstrated against their acceptance criteria
- **Cross-reference**: P-032 (Test Architecture Design) — test strategy informs acceptance criteria test types
- **Artifact**: Sprint Backlog; Sprint Kickoff Brief Section 3

---

## P-025: Sprint Readiness Gate Process

### 1. Process ID and Name
**P-025** — Sprint Readiness Gate Process

### 2. Purpose
Structured readiness check at the start of sprint planning that verifies all prerequisites are met before backlog assignment begins. This is the fourth and final gate in the Clarity of Intent process (after Intent Review P-004, Scope Lock P-013, and Dependency Acceptance P-019). It prevents the team from starting a sprint with vague goals, missing acceptance criteria, or untracked dependencies — the three most common causes of sprint failure. Sprint planning does not proceed until this gate passes.

### 3. Derived From
Clarity of Intent — Stage 4: Gate: Sprint Readiness

Relevant source text: "This is the sprint planning meeting itself — but with a structured readiness check at the start." and the five pass criteria: sprint goal connected, intent trace visible, all stories have acceptance criteria, dependencies have status and contingency, every engineer can answer what/why/how-done.

### 4. Primary Owner Agent
**engineering-manager** — The EM chairs the Sprint Readiness Gate because the EM owns the Sprint Kickoff Brief and the sprint planning ceremony (Engineering Team Structure Guide Section 11.2). The EM's data-driven approach (EM-006) ensures readiness is assessed against concrete criteria, not subjective readiness feelings.

### 5. Supporting Agents
- **product-manager** — The PM confirms backlog readiness: all stories have acceptance criteria (PM-006), the sprint goal aligns to a Scope Contract deliverable (PM-001), and the intent trace is accurate. The PM also plays the Scrum Master role in facilitating the readiness check.
- **software-engineer** — All squad engineers participate in the readiness check. Each engineer must be able to answer: "What am I building, why does it matter, and how will I know it's done?" Engineers who cannot answer these three questions signal a readiness failure.
- **technical-program-manager** — The TPM reviews cross-team alignment: are dependencies due this sprint on track? Have contingencies been defined? The TPM brings the cross-team perspective that the squad-level readiness check might miss.

### 6. Stages/Steps

| Step | Actor | Action | Output |
|------|-------|--------|--------|
| 1. Assemble Sprint Planning | EM | EM convenes the sprint planning meeting. All squad members, PM, and TPM (if cross-team dependencies exist) attend. Before any backlog discussion begins, EM announces: "We start with a readiness check." | Sprint planning assembled |
| 2. Sprint Goal Check | EM | EM reads the sprint goal aloud. Asks: "Does everyone understand what will be true at the end of this sprint?" Verifies the goal connects to a named Scope Contract deliverable. If no sprint goal exists, gate fails immediately. | Sprint goal verified or gate fails |
| 3. Intent Trace Check | EM + PM | EM displays the intent trace (P-023 output). PM confirms all three lines are accurate. EM asks one engineer: "Can you explain in one sentence why we are building this?" If the engineer cannot, the trace is unclear — gate fails on this criterion but other checks continue. | Intent trace verified or flagged |
| 4. Story Readiness Check | PM | PM confirms: every story in the sprint backlog has written acceptance criteria. EM reads one or two representative stories aloud with their criteria. If any story lacks criteria, it is removed from the sprint backlog until criteria are written. | Story readiness verified |
| 5. Dependency Status Check | TPM (or EM if no TPM) | Review all dependencies from the Dependency Charter that are due this sprint (P-030 output). For each: current status (on track / at risk / blocked) and contingency plan. If any dependency is blocked with no contingency, gate fails on this criterion. | Dependency status verified |
| 6. Engineer Comprehension Check | EM | EM asks 2-3 engineers (rotating each sprint): "What are you building? Why does it matter? How will you know it's done?" Answers should reference the sprint goal, the project intent, and their story's acceptance criteria. This check validates that the Sprint Kickoff Brief has been read and understood. | Engineer comprehension verified |
| 7. Gate Decision | EM | Binary decision: PASS or FAIL. PASS requires ALL five criteria met (see Gate/Checkpoint below). If FAIL, EM documents which criteria failed and assigns remediation: specific action, owner, and deadline (typically same day — gate should be re-run before sprint starts). If PASS, sprint planning proceeds to backlog assignment. | Gate decision record |

### 7. Inputs
- Sprint Kickoff Brief (produced by P-022, P-023, P-024, P-030) — all four sections
- Sprint backlog with stories and acceptance criteria (P-024 output)
- Dependency status updates (P-030 output; P-020 standup data)
- Team roster and availability for this sprint

### 8. Outputs/Artifacts
- **Gate Decision Record** — PASS or FAIL with rationale per criterion
- **Sprint Planning Authorization** — If PASS, backlog assignment and sprint commitment proceed
- **Remediation Actions** — If FAIL, specific actions with owners and deadlines to achieve readiness
- **Sprint Kickoff Brief v1.0** — If PASS, the brief is locked as the sprint's baseline document

### 9. Gate/Checkpoint
**This IS the gate.** Binary pass criteria — ALL must be met:
1. Sprint goal is stated as one sentence and connects to a named Scope Contract deliverable
2. Intent trace is visible in the Sprint Kickoff Brief and all three lines are accurate
3. All stories in the sprint backlog have written, binary acceptance criteria
4. All dependencies due this sprint have a current status and a documented contingency plan
5. Every engineer can answer: "What am I building, why does it matter, and how will I know it's done?"

### 10. Success Criteria
- Gate passes before any backlog assignment begins — no sprint starts without readiness verification
- No sprint starts with stories that lack acceptance criteria
- No sprint starts with untracked dependencies (every dependency due this sprint is visible and has a contingency)
- Gate failures are resolved within the same day — the sprint does not slip by more than one day due to readiness issues
- Gate failure rate decreases over time as teams internalize the readiness criteria
- The Sprint Kickoff Brief becomes the team's reference document throughout the sprint

### 11. Dependencies
| Dependency | Process | Type | Detail |
|-----------|---------|------|--------|
| Sprint Goal authored | P-022 | Hard prerequisite | Sprint goal must exist for criterion 1 |
| Intent Trace validated | P-023 | Hard prerequisite | Intent trace must be present for criterion 2 |
| Stories written | P-024 | Hard prerequisite | Stories with criteria must exist for criterion 3 |
| Sprint-level dependency tracking | P-030 | Hard prerequisite | Dependency statuses and contingencies must exist for criterion 4 |
| Dependency Acceptance Gate passed | P-019 | Hard prerequisite (Sprint 1) | For the first sprint, the Dependency Acceptance Gate must have passed |

### 12. Traceability
- **Upstream**: P-022 (Sprint Goal), P-023 (Intent Trace), P-024 (Stories), P-030 (Dependencies) — all four Sprint Kickoff Brief sections
- **Upstream**: P-019 (Dependency Acceptance Gate) — the gate chain: P-004 → P-013 → P-019 → **P-025**
- **Downstream**: P-026 (Daily Standup) — standup operates within a sprint that passed readiness
- **Downstream**: P-031 (Feature Development) — development starts only after the gate passes
- **Downstream**: P-027 (Sprint Review) — the locked Sprint Kickoff Brief is the baseline for review
- **Gate chain**: P-004 (Intent Review) → P-013 (Scope Lock) → P-019 (Dependency Acceptance) → **P-025 (Sprint Readiness)**
- **Artifact**: Gate Decision Record; locked Sprint Kickoff Brief v1.0

---

## P-026: Daily Standup Process

### 1. Process ID and Name
**P-026** — Daily Standup Process

### 2. Purpose
A 15-minute, blocker-focused synchronization ceremony every working day during an active sprint. The daily standup surfaces blockers within 24 hours of arising, enabling same-day impediment removal. This is not a status report — it is a coordination mechanism. The three-question format (what I completed, what I will complete, what blocks me) keeps the team aligned without consuming the time it is meant to protect.

### 3. Derived From
Clarity of Intent — Stage 4 operational process (referenced in Sprint Bridge context)

Engineering Team Structure Guide — Section 11.2: Scrum ceremonies ("Daily Standup — Every workday — 15 min maximum — Synchronize; surface blockers; no status reporting")

Product-manager agent role: Scrum Master facilitation responsibilities.

### 4. Primary Owner Agent
**product-manager** (Scrum Master role) — The PM facilitates the daily standup in their Scrum Master capacity. The PM-as-Scrum-Master is responsible for: enforcing the 15-minute timebox, keeping discussion blocker-focused (not status-focused), and ensuring blockers are captured for follow-up. The PM's Scrum Master scope (product-manager agent: "Sprint ceremonies, impediment removal") explicitly includes standup facilitation.

### 5. Supporting Agents
- **software-engineer** — All engineers participate. Each engineer provides their three-question update: yesterday / today / blockers. Engineers are responsible for surfacing blockers immediately rather than waiting for the standup.
- **engineering-manager** — The EM observes (does not facilitate) and notes blockers requiring managerial action: impediment removal, resource negotiation, escalation. The EM's impediment removal responsibility (EM scope: "impediment removal") activates when blockers surface.

### 6. Stages/Steps

| Step | Actor | Action | Output |
|------|-------|--------|--------|
| 1. Open Standup | PM (Scrum Master) | Open the standup with time reminder: "We have 15 minutes." Pull up the sprint board showing current story statuses. | Standup opened; board visible |
| 2. Three-Question Round | Each Engineer | Each engineer answers three questions: (a) What did I complete since last standup? (b) What will I complete before next standup? (c) What is blocking me? Answers reference specific stories from the sprint backlog. Updates take 1-2 minutes per person maximum. | Blocker list; sprint board updates |
| 3. Blocker Capture | PM (Scrum Master) | Record every blocker mentioned. Classify: (a) technical blocker (TL to resolve after standup), (b) dependency blocker (TPM to resolve via P-020/P-021), (c) impediment (EM to resolve — resource, access, environment). No blocker resolution during standup — capture and assign for after. | Classified blocker list |
| 4. Cross-Dependency Flag | PM (Scrum Master) | If any blocker involves a cross-team dependency from the Dependency Charter, flag it for the TPM. Dependency blockers feed into the next Dependency Standup (P-020). | Cross-team dependency flags |
| 5. Close Standup | PM (Scrum Master) | Confirm: "All blockers captured. [Names] — please stay for after-standup on [topics]." Close at 15 minutes regardless of whether all engineers have spoken (escalate to EM if standups consistently exceed 15 minutes). | Standup closed; after-standup topics assigned |
| 6. Impediment Routing | EM | After standup, EM reviews the blocker list. Assigns impediment removal actions: EM handles resource/access/environment impediments directly; routes dependency blockers to TPM; routes technical blockers to TL for resolution. | Impediment removal actions assigned |

### 7. Inputs
- Current sprint backlog with story statuses (from sprint board/tracking tool)
- Previous standup blocker list and resolution status
- Dependency Charter (for cross-team blocker identification)

### 8. Outputs/Artifacts
- **Updated Sprint Board** — Story statuses updated: not started / in progress / in review / done
- **Blocker List** — Captured blockers with classification and assigned resolver
- **Cross-Team Dependency Flags** — Blockers that feed into P-020 (Dependency Standup)
- **Impediment Removal Actions** — EM-assigned actions for impediment resolution

### 9. Gate/Checkpoint
No formal gate — this is a recurring operational process. However:
- If standups consistently exceed 15 minutes, the EM must investigate the root cause (too many engineers, discussions drifting to problem-solving, blocked work causing lengthy updates)
- If a blocker goes unresolved for more than 2 standups (2 business days), the EM escalates per the dependency escalation process (P-021) or resolves the impediment directly

### 10. Success Criteria
- Standup completes in 15 minutes or less (strict timebox)
- Every team member speaks at every standup (no silent participants)
- All blockers surfaced within 24 hours of arising
- No problem-solving during standup — blockers are captured and resolved after
- Cross-team dependency blockers reach the TPM within the same business day
- Impediment removal actions are assigned by EM within 1 hour of standup
- Sprint board reflects current state after every standup

### 11. Dependencies
| Dependency | Process | Type | Detail |
|-----------|---------|------|--------|
| Sprint Readiness Gate passed | P-025 | Hard prerequisite | Sprint must be active for daily standups to run |
| Sprint backlog populated | P-024 | Hard prerequisite | Stories must exist in the backlog for engineers to report against |

### 12. Traceability
- **Upstream**: P-025 (Sprint Readiness Gate) — sprint must be active
- **Upstream**: P-024 (Story Writing) — stories in the backlog are what engineers report on
- **Parallel**: P-020 (Dependency Standup) — cross-team blockers from daily standup feed into the dependency standup; these are complementary (daily standup = within-squad; dependency standup = cross-squad)
- **Downstream**: P-021 (Dependency Escalation) — persistent blockers trigger escalation
- **Downstream**: P-028 (Sprint Retrospective) — standup effectiveness is a retrospective topic
- **Engineering Team Structure Guide**: Section 11.2 — standup is one of four Scrum ceremonies
- **Artifact**: Updated sprint board; blocker list

---

## P-027: Sprint Review Process

### 1. Process ID and Name
**P-027** — Sprint Review Process

### 2. Purpose
Demonstrate completed work to stakeholders at the end of every sprint and assess completion against the sprint goal. The sprint review is an inspection of working software — not a status meeting. Each completed story is demonstrated against its acceptance criteria, the sprint goal is assessed as achieved/partially achieved/not achieved, and stakeholder feedback is captured for backlog refinement. The sprint review closes the feedback loop between delivery and intent.

### 3. Derived From
Clarity of Intent — Stage 4 operational process (sprint cycle reference)

Engineering Team Structure Guide — Section 11.2: Scrum ceremonies ("Sprint Review — End of each sprint — 1-2 hours — Demo completed work to stakeholders; gather feedback")

### 4. Primary Owner Agent
**engineering-manager** — The EM owns the sprint review because the EM owns delivery outcomes (EM scope). The EM prepares the demo agenda aligned to the sprint goal, chairs the review, and ensures the sprint goal completion assessment is recorded. The EM's data-driven approach (EM-006) ensures the assessment is objective.

### 5. Supporting Agents
- **product-manager** — The PM facilitates stakeholder feedback collection and triages feedback items into the backlog. The PM determines whether feedback constitutes a scope change (triggers P-014), a new backlog item, or is deferred. The PM's outcomes-over-outputs orientation (PM-001) ensures feedback is evaluated against the project's intended outcome.
- **software-engineer** — Engineers demo their completed stories. Each engineer demonstrates their work against the story's acceptance criteria, showing stakeholders that criteria are met. The engineer who built the work is the best person to explain it.

### 6. Stages/Steps

| Step | Actor | Action | Output |
|------|-------|--------|--------|
| 1. Prepare Demo Agenda | EM + PM | Create a demo agenda aligned to the sprint goal. Order: (a) restate sprint goal, (b) demo completed stories in dependency order, (c) report on incomplete stories with reason, (d) sprint goal assessment, (e) open for stakeholder feedback. Estimated duration: 1-2 hours. | Sprint review agenda |
| 2. Restate Sprint Goal and Intent Trace | EM | Open the review by reading the sprint goal and intent trace (P-023). This grounds the demo in the project's intent — stakeholders evaluate work against purpose, not just functionality. | Context established |
| 3. Demo Completed Stories | Engineers | Each engineer demos their completed story against acceptance criteria. For each criterion: show evidence of completion (working feature, test output, API response, etc.). PM or QA confirms criterion verification. | Story demonstrations with criteria evidence |
| 4. Report Incomplete Stories | EM + TL | For each story not completed: state the reason (blocked, underestimated, dependency late, scope larger than anticipated). Identify the next action: carry forward to next sprint, split, or descope. This is not blame — it is a factual assessment for planning purposes. | Incomplete story report with next actions |
| 5. Sprint Goal Assessment | EM | Assess the sprint goal: (a) **Achieved** — the observable condition stated in the goal is now true, (b) **Partially Achieved** — some aspects of the goal are true but not all, state what is missing, (c) **Not Achieved** — the condition is not true, state why. Record the assessment. | Sprint goal completion assessment |
| 6. Stakeholder Feedback | PM | Open the floor for stakeholder feedback. PM captures each feedback item with: description, stakeholder source, and preliminary triage (new backlog item / scope change candidate / deferred / noted). | Stakeholder feedback log |
| 7. Feedback Triage | PM | After the review, PM triages feedback items: (a) items that represent scope changes are processed through P-014 (Scope Change Control), (b) items that are new backlog stories are added to the product backlog for P-029 (Backlog Refinement), (c) items that are deferred are documented with rationale. | Triaged feedback actions |

### 7. Inputs
- Sprint backlog with story statuses (completed / incomplete)
- Sprint goal and intent trace (from Sprint Kickoff Brief)
- Acceptance criteria for each story (P-024 output)
- Dependency status (any dependencies that impacted sprint execution)

### 8. Outputs/Artifacts
- **Sprint Goal Completion Assessment** — Achieved / Partially Achieved / Not Achieved with explanation
- **Stakeholder Feedback Log** — Each feedback item with source, description, and triage decision
- **Incomplete Story Report** — Stories not completed with reasons and next actions (carry forward / split / descope)
- **Backlog Additions** — New stories generated from stakeholder feedback, queued for P-029 refinement

### 9. Gate/Checkpoint
No formal gate — this is a recurring inspection ceremony. However:
- Sprint goal completion rate is a tracked health metric. The Clarity of Intent measurement signal specifies: "Sprint goal completion rate — Percentage of sprints where the stated sprint goal was fully achieved — > 80%." Completion rates below 80% over a rolling quarter trigger a process review.
- If the sprint goal is assessed as "Not Achieved" for two consecutive sprints, the EM must escalate to the Director to investigate systemic causes (capacity, dependency failures, goal over-ambition).

### 10. Success Criteria
- Sprint review covers all stories attempted in the sprint (completed and incomplete)
- Sprint goal completion status is documented with a clear assessment (not ambiguous)
- All incomplete stories have a documented reason and next action
- Stakeholder feedback is captured and triaged within 24 hours of the review
- Feedback items that constitute scope changes are routed to P-014 (not silently absorbed)
- Sprint goal completion rate remains above 80% on a rolling quarterly basis
- The review is conducted as an inspection of working software, not a slide presentation

### 11. Dependencies
| Dependency | Process | Type | Detail |
|-----------|---------|------|--------|
| Sprint Readiness Gate passed | P-025 | Hard prerequisite | A sprint must have been planned and executed |
| Feature Development | P-031 | Hard prerequisite | Stories must have been worked on during the sprint |
| Story Writing | P-024 | Informational | Acceptance criteria from P-024 are the assessment baseline |

### 12. Traceability
- **Upstream**: P-025 (Sprint Readiness Gate) — the sprint must have passed readiness and been executed
- **Upstream**: P-024 (Story Writing) — acceptance criteria are the demo verification baseline
- **Upstream**: P-031 (Feature Development) — completed and incomplete stories are the demo content
- **Downstream**: P-028 (Sprint Retrospective) — sprint goal assessment and completion data feed the retrospective
- **Downstream**: P-029 (Backlog Refinement) — feedback items become backlog entries for refinement
- **Downstream**: P-014 (Scope Change Control) — feedback that constitutes scope change triggers the change process
- **Downstream**: P-022 (Sprint Goal Authoring — next sprint) — this sprint's outcome informs next sprint's goal
- **Measurement**: Clarity of Intent signal "Sprint goal completion rate > 80%"
- **Artifact**: Sprint Goal Completion Assessment; Stakeholder Feedback Log

---

## P-028: Sprint Retrospective Process

### 1. Process ID and Name
**P-028** — Sprint Retrospective Process

### 2. Purpose
Structured team improvement ceremony at the end of every sprint that celebrates wins, addresses dysfunction, and produces specific action items with owners tracked to closure. The retrospective is the team's primary mechanism for continuous improvement. Without it, process problems compound sprint over sprint. Without follow-through on action items, retrospectives become demoralizing rituals that erode trust in the improvement process.

### 3. Derived From
Clarity of Intent — Stage 4 operational process (sprint cycle)

Engineering Team Structure Guide — Section 11.2: Scrum ceremonies ("Retrospective — End of each sprint — 1-1.5 hours — Improve team process; celebrate wins; address dysfunction")

Engineering-manager agent: EM facilitates sprint retrospectives as part of team health ownership.

### 4. Primary Owner Agent
**engineering-manager** — The EM facilitates the retrospective because the EM owns team health (EM-001 people-first). The retrospective is the EM's primary mechanism for detecting and addressing team dysfunction, process inefficiency, and morale issues. The EM's data-driven approach (EM-006) ensures the retrospective includes quantitative inputs (DORA metrics, velocity) alongside qualitative team sentiment.

### 5. Supporting Agents
- **product-manager** — The PM participates as a team member and provides the product/stakeholder perspective. The PM surfaces feedback from the sprint review (P-027) that has process implications (e.g., "stakeholders consistently ask for things that are out of scope" → boundary enforcement issue).
- **software-engineer** — All engineers participate. Engineers provide the ground-level view of what worked and what did not. The retrospective is a safe space for engineers to surface issues without attribution.

### 6. Stages/Steps

| Step | Actor | Action | Output |
|------|-------|--------|--------|
| 1. Review Previous Action Items | EM | Before starting the new retrospective, review action items from the previous sprint's retrospective. For each: (a) **Completed** — celebrate, confirm the improvement was felt, (b) **In Progress** — update status, confirm it is still being worked, (c) **Not Started** — investigate why; reassign or deprioritize with explanation. | Previous action item status review |
| 2. Present Quantitative Data | EM | Present sprint-level data as objective input: (a) Sprint goal completion assessment (from P-027), (b) DORA metrics trends (deployment frequency, lead time, change failure rate, MTTR), (c) Sprint velocity vs. rolling average, (d) Blocker count and resolution times from standup data (P-026). Data does not replace discussion — it grounds it. | Quantitative sprint health data |
| 3. Facilitate 4 L's Framework | EM | Use the 4 L's retrospective format: **Liked** (what went well — celebrate), **Learned** (new insights gained), **Lacked** (what was missing or insufficient), **Longed For** (what the team wishes it had). Each team member contributes to each category. Timebox: 30-40 minutes. | Team input across 4 L's |
| 4. Identify Patterns | EM | Group related items. Identify recurring themes. Pay special attention to items that appeared in previous retrospectives but were not resolved — these are systemic issues requiring escalation, not just action items. | Themed patterns |
| 5. Generate Action Items | Team | For each significant theme or issue, generate a specific action item: (a) What will we do differently? (b) Who owns this action? (c) By when? Action items must be specific enough to verify: "Update the CI pipeline to run SAST before integration tests" not "Improve CI." Limit to 2-3 action items per retrospective — focus on the highest-impact improvements. | Action items with owners and deadlines |
| 6. Enter Action Items in Backlog | EM | Enter retrospective action items into the team's backlog. These items are tracked alongside sprint work and reviewed at the next retrospective (Step 1). | Action items in team backlog |
| 7. Escalate Systemic Issues | EM | If any theme is systemic (appeared in 3+ retrospectives without resolution, or requires Director-level action), EM escalates to the Director. The EM does not absorb systemic issues — they require organizational response. | Escalation to Director (if needed) |

### 7. Inputs
- Sprint outcome data from P-027 (Sprint Review) — goal assessment, incomplete stories, feedback
- DORA metrics (deployment frequency, lead time for changes, change failure rate, MTTR)
- Sprint velocity (actual vs. rolling 3-sprint average)
- Blocker data from P-026 (Daily Standup) — count, resolution times, types
- Previous retrospective action items and their status
- Dependency escalation data from P-021 (if any escalations occurred this sprint)

### 8. Outputs/Artifacts
- **Retrospective Action Items** — 2-3 specific improvement actions, each with: description, owner, deadline
- **Previous Action Item Status** — Review of last sprint's items: completed / in progress / not started
- **Team Health Signals** — Qualitative assessment of team morale, collaboration, and process satisfaction
- **Escalation Record** — Systemic issues escalated to Director (if applicable)

### 9. Gate/Checkpoint
No formal gate — this is a recurring improvement ceremony. However:
- Action items from previous retrospectives must be reviewed at every retrospective (Step 1)
- Action items from >=80% of retrospectives should be closed within 2 sprints (Clarity of Intent measurement signal)
- If fewer than 80% of action items are closing within 2 sprints, the EM must assess whether the team is generating too many items or facing systemic blockers

### 10. Success Criteria
- Retrospective produces at least 1 actionable improvement item per sprint
- Previous sprint's action items are reviewed at every retrospective (no action items forgotten)
- Action items from >=80% of retrospectives are closed within 2 sprints
- Systemic issues (3+ retrospectives without resolution) are escalated to the Director
- DORA metrics trends are included as quantitative input (EM-006 data-driven)
- The retrospective is a safe space — engineers surface issues without attribution or blame
- Team health signals improve or stabilize over rolling quarters

### 11. Dependencies
| Dependency | Process | Type | Detail |
|-----------|---------|------|--------|
| Sprint Review completed | P-027 | Hard prerequisite | Sprint outcome data (goal assessment, feedback) is a primary input |
| Daily Standup data | P-026 | Informational | Blocker counts and resolution times are quantitative inputs |
| Dependency Escalation data | P-021 | Informational | Escalation patterns during the sprint are retrospective inputs |

### 12. Traceability
- **Upstream**: P-027 (Sprint Review) — sprint goal assessment and feedback are primary inputs
- **Upstream**: P-026 (Daily Standup) — blocker data is a quantitative input
- **Upstream**: P-021 (Dependency Escalation) — escalation patterns are inputs
- **Downstream**: P-022 (Sprint Goal Authoring — next sprint) — improvement actions may affect how the next sprint goal is set
- **Downstream**: P-029 (Backlog Refinement) — action items enter the backlog for tracking
- **Downstream**: P-070 (Project Post-Mortem) — cumulative retrospective data feeds the project post-mortem
- **Downstream**: P-071 (Process Health Review) — retrospective patterns are inputs to the quarterly process health review
- **Measurement**: Clarity of Intent signal "Action items from >=80% of retrospectives closed within 2 sprints"
- **Artifact**: Retrospective action items in team backlog

---

## P-029: Backlog Refinement Process

### 1. Process ID and Name
**P-029** — Backlog Refinement Process

### 2. Purpose
Weekly PM-led backlog grooming ensuring the next sprint's stories have written acceptance criteria before sprint planning begins. Backlog refinement is the bridge between the Scope Contract and sprint planning — it ensures that stories arrive at sprint planning in a "ready" state, not as vague descriptions that consume planning time. Sprint planning should never produce new stories from scratch; it should assign and commit to stories that are already refined.

### 3. Derived From
Clarity of Intent — Stage 4: Story Writing Process prerequisite; Sprint Readiness Gate prerequisite (all stories must have acceptance criteria before planning begins)

Engineering Team Structure Guide — Section 11.2: Sprint artifacts ("Product Backlog: PM-owned ordered list of all potential work; refined weekly")

Product-manager agent role: "writing user stories, managing product backlogs, defining acceptance criteria."

### 4. Primary Owner Agent
**product-manager** — The PM owns the product backlog (Engineering Team Structure Guide Section 11.2) and is responsible for ensuring it is refined weekly. The PM's acceptance criteria mandate (PM-006: "every user story has binary pass/fail criteria") applies to backlog refinement — stories do not move to "ready" status until criteria are written.

### 5. Supporting Agents
- **software-engineer** (Tech Lead) — The TL validates technical feasibility and sizing during refinement. The TL identifies stories that are too large (need splitting), technically dependent on other work (need sequencing), or technically ambiguous (need spike/research). The TL's technical depth ensures refined stories are implementable, not just well-described.

### 6. Stages/Steps

| Step | Actor | Action | Output |
|------|-------|--------|--------|
| 1. Select Stories for Refinement | PM | Review the product backlog. Select stories for the upcoming 1-2 sprints. Prioritize stories that: (a) serve the next sprint's likely deliverable target (informed by the critical path and Scope Contract), (b) are currently in "not ready" state (missing criteria, unclear scope, unsized). | Stories selected for refinement |
| 2. Criteria Authoring | PM | For each selected story, write or update acceptance criteria in Given/When/Then format or as testable checklists. Criteria must be binary — passable/failable by QA or the PM themselves. Reference the parent deliverable's Definition of Done from the Scope Contract. | Stories with draft acceptance criteria |
| 3. Technical Feasibility Review | TL | TL reviews each refined story. Checks: (a) Is it implementable with current infrastructure and dependencies? (b) Is it sized correctly (completable in one sprint, <8 story points)? (c) Are there hidden technical prerequisites? (d) Should it be split into smaller stories? | TL-validated stories |
| 4. Story Splitting | PM + TL | Stories that are too large (TL flags) are split into smaller stories. Each resulting story must be independently testable and demonstrable. Splitting follows vertical slicing — each slice delivers user-visible value, not horizontal layers. | Split stories (if applicable) |
| 5. Story Ordering | PM | Order the refined stories by priority. Priority considers: (a) deliverable dependencies from the critical path, (b) business value (PM judgment), (c) technical dependencies (TL input), (d) risk reduction (higher-risk stories earlier). | Prioritized, ordered backlog |
| 6. Mark Stories as "Ready" | PM | Stories that have acceptance criteria, are appropriately sized, and are technically feasible are marked as "ready" in the backlog tool. Only "ready" stories can be pulled into sprint planning (P-024). | Ready-state stories in backlog |

### 7. Inputs
- Product backlog (PM-owned, all potential work for the project)
- Locked Scope Contract (P-013) — deliverables and Definition of Done as the criteria baseline
- Critical Path analysis (P-016) — deliverable ordering influences story priority
- Previous sprint feedback (P-027) — stakeholder feedback generates new backlog items
- Retrospective action items (P-028) — improvement actions that are implemented as stories
- Scope Change Requests (P-014) — approved scope changes add or modify backlog items

### 8. Outputs/Artifacts
- **Refined Backlog** — Stories marked as "ready" with: description, acceptance criteria, preliminary size estimate, parent deliverable reference
- **Not-Ready Items** — Stories that still need criteria authoring (recycled to next refinement session)
- **Split Stories** — Large stories broken into sprint-sized vertical slices

### 9. Gate/Checkpoint
No formal gate — this is a recurring operational process. However:
- The Sprint Readiness Gate (P-025) enforces the downstream quality criterion: all stories in the sprint backlog must have acceptance criteria. Backlog refinement is the process that ensures this criterion is met.
- A healthy backlog always has at least 1 sprint's worth of "ready" stories. If the ready-story count drops below one sprint's worth, PM must increase refinement urgency.

### 10. Success Criteria
- Next sprint's stories have written acceptance criteria before sprint planning begins
- No story enters sprint planning in "not ready" state
- Backlog always has at least 1 sprint's worth of "ready" stories (buffer)
- Large stories (>8 points or > 1 sprint) are split before entering sprint planning
- Refinement session runs weekly and takes no more than 1 hour
- Stories trace to a specific Scope Contract deliverable (parent deliverable reference maintained)

### 11. Dependencies
| Dependency | Process | Type | Detail |
|-----------|---------|------|--------|
| Story Writing Process | P-024 | Bidirectional | P-029 feeds refined stories into P-024; P-024 may send "not ready" stories back to P-029 |
| Scope Lock Gate passed | P-013 | Hard prerequisite | Deliverables and Definition of Done must exist to write meaningful criteria |
| Sprint Review feedback | P-027 | Informational | Feedback items from sprint review become new backlog entries |
| Retrospective action items | P-028 | Informational | Improvement actions may be implemented as backlog stories |
| Scope Change Control | P-014 | Conditional | Approved scope changes modify the backlog |

### 12. Traceability
- **Upstream**: P-013 (Scope Lock Gate) — Scope Contract deliverables and DoD inform criteria
- **Upstream**: P-027 (Sprint Review) — feedback items become new backlog entries
- **Upstream**: P-028 (Sprint Retrospective) — action items enter the backlog
- **Upstream**: P-014 (Scope Change Control) — approved changes modify the backlog
- **Downstream**: P-024 (Story Writing) — refined stories flow into sprint story writing
- **Downstream**: P-025 (Sprint Readiness Gate) — refined stories ensure the gate's story-readiness criterion is met
- **Engineering Team Structure Guide**: Section 11.2 — "Product Backlog: PM-owned ordered list of all potential work; refined weekly"
- **Artifact**: Refined backlog with "ready" status markers

---

## P-030: Sprint-Level Dependency Tracking Process

### 1. Process ID and Name
**P-030** — Sprint-Level Dependency Tracking Process

### 2. Purpose
Track which dependencies from the Dependency Charter must be resolved within the current sprint for the sprint goal to be achievable, and document a contingency plan for each. This process bridges project-level dependency management (Category 3) with sprint-level execution (Category 4). Without sprint-level dependency tracking, teams discover dependency failures at sprint end rather than at sprint start, turning preventable risks into sprint-failing surprises.

### 3. Derived From
Clarity of Intent — Stage 4: Sprint Bridge, Section 4 (Dependencies Due This Sprint)

Relevant source text: "Pull from the Dependency Charter — which dependencies must be resolved during this sprint for the sprint goal to be achievable?" with a table format showing dependency, needed-by date, current status, and contingency if late.

### 4. Primary Owner Agent
**technical-program-manager** — The TPM owns sprint-level dependency tracking because the TPM owns the Dependency Charter (Category 3) and the RAID log. The TPM's cross-team visibility (TPM-001) enables them to track dependency statuses across all involved squads and flag risks before they become blockers.

### 5. Supporting Agents
- **engineering-manager** — The EM owns contingency execution. When a dependency is late and the contingency is activated, the EM adjusts the sprint plan accordingly: reassigning engineers, descoping stories, or executing the workaround defined in the contingency plan.

### 6. Stages/Steps

| Step | Actor | Action | Output |
|------|-------|--------|--------|
| 1. Extract Sprint Dependencies | TPM | From the locked Dependency Charter (P-019 output), extract all dependencies with "needed by" dates that fall within the current sprint. Include dependencies needed before sprint start that are not yet complete. | Sprint dependency list |
| 2. Check Current Status | TPM | For each sprint dependency, check the current status: On Track / At Risk / Blocked. Status comes from the last Dependency Standup (P-020) or direct communication with the dependency owner. | Current status per sprint dependency |
| 3. Document Contingency Plans | TPM + EM | For each sprint dependency, document a specific contingency plan: "If [dependency] is not delivered by [date], then [specific action]." Contingencies must be actionable — not "we'll figure it out." Common contingency patterns: use mock/stub (proceed with fake data), descope dependent stories, reorder sprint work to delay the dependent stories, escalate (P-021). | Documented contingency per dependency |
| 4. Publish in Sprint Kickoff Brief | TPM | Enter the sprint-level dependency tracking table into the Sprint Kickoff Brief Section 4. | Sprint Kickoff Brief Section 4 complete |
| 5. Daily Monitoring | TPM + EM | During the sprint, TPM monitors dependency statuses through the Dependency Standup (P-020). If a dependency status changes to "At Risk" or "Blocked," TPM notifies the EM immediately. EM evaluates whether to activate the contingency. | Ongoing dependency status updates |
| 6. Contingency Activation | EM | If a dependency is confirmed late, EM activates the contingency plan. This may involve: adjusting the sprint backlog, reassigning engineers, notifying the PM of scope impact, or triggering P-021 (Dependency Escalation). | Contingency activation record |

### 7. Inputs
- Locked Dependency Charter (output of P-019) — complete dependency register with "needed by" dates, owners, escalation paths
- Dependency Standup updates (P-020) — latest status for each dependency
- Sprint calendar — sprint start and end dates, key milestones within the sprint
- Team sprint plan (P-024 output) — which stories depend on which dependencies

### 8. Outputs/Artifacts
- **Sprint-Level Dependency Tracking Table** (Section 4 of Sprint Kickoff Brief):

| Dependency | Needed By | Current Status | Contingency if Late |
|------------|-----------|---------------|---------------------|
| [Dependency name from charter] | [Sprint N, Day X] | [On Track / At Risk / Blocked] | [Specific contingency action] |

- **Contingency Activation Records** — Documentation of when and why a contingency was activated during the sprint

### 9. Gate/Checkpoint
**Sprint Readiness Gate (P-025)** — Dependency statuses and contingencies are the fourth pass criterion. Pass criteria specific to this process:
- All dependencies due this sprint are listed with current statuses
- Every dependency has a documented, specific contingency plan
- No dependency is in "Blocked" status without an active escalation (P-021) or an activated contingency

### 10. Success Criteria
- Every dependency due this sprint has a documented, specific contingency plan (not "TBD" or "we'll figure it out")
- Contingency plans are actionable and specific: they name the alternative action, the responsible person, and the impact on the sprint
- No sprint goal is missed due to an untracked dependency (every dependency failure was either prevented or handled by the contingency)
- Dependency status changes are communicated to the EM within the same business day they are detected
- Sprint Kickoff Brief Section 4 is complete before the Sprint Readiness Gate (P-025)

### 11. Dependencies
| Dependency | Process | Type | Detail |
|-----------|---------|------|--------|
| Dependency Acceptance Gate passed | P-019 | Hard prerequisite | The locked Dependency Charter is the source of sprint-level dependencies |
| Cross-Team Dependency Registration | P-015 | Structural prerequisite | The Dependency Register provides the dependency metadata |
| Dependency Standup | P-020 | Ongoing input | Status updates from the dependency standup feed into sprint-level tracking |
| Sprint Goal authored | P-022 | Informational | The sprint goal determines which dependencies are sprint-critical |

### 12. Traceability
- **Upstream**: P-019 (Dependency Acceptance Gate) — locked Dependency Charter is the tracking baseline
- **Upstream**: P-015 (Cross-Team Dependency Registration) — dependency metadata (owners, escalation paths)
- **Upstream**: P-020 (Dependency Standup) — status updates feed sprint tracking
- **Upstream**: P-022 (Sprint Goal) — determines which dependencies are sprint-critical
- **Downstream**: P-025 (Sprint Readiness Gate) — dependency status and contingency documentation is a gate criterion
- **Downstream**: P-021 (Dependency Escalation) — blocked dependencies trigger escalation
- **Downstream**: P-027 (Sprint Review) — dependency impacts on sprint outcome are reviewed
- **Artifact**: Sprint Kickoff Brief Section 4

---

## P-031: Feature Development Process

### 1. Process ID and Name
**P-031** — Feature Development Process

### 2. Purpose
End-to-end process for an individual contributor (IC) to implement a sprint story from assignment through acceptance verification. This is the process where code is actually written, tested, reviewed, and deployed to staging. Every story must meet the team's Definition of Done (DoD) before it is marked complete. The DoD checklist is the quality gate that prevents defect backlog accumulation. Stories closed without DoD verification are the primary source of quality debt.

### 3. Derived From
Clarity of Intent — Stage 4: Sprint Bridge, Section 5 (Definition of Done — Sprint Level) and Section 3 (Stories and Acceptance Criteria)

Relevant source text (Sprint DoD checklist):
- "Code reviewed by at least one peer"
- "Automated tests written and passing in CI"
- "SAST scan clean (no new critical or high findings)"
- "Documentation updated (API docs, runbook, or README as applicable)"
- "Acceptance criteria verified by PM or QA"
- "Deployed to staging and smoke-tested"

Software-engineer agent: SE workflow ("understand → implement → test → review → done") and core rules (SE-001 no placeholders, SE-006 enterprise-ready).

### 4. Primary Owner Agent
**software-engineer** — The IC engineer owns the feature development process because this is the core execution work: understanding the story, implementing the feature, writing tests, submitting for review, and verifying acceptance criteria. The software-engineer agent's workflow (understand → implement → test → review → done) maps directly to this process. The TL (also software-engineer agent) provides technical oversight.

### 5. Supporting Agents
- **qa-engineer** — QA verifies acceptance criteria in staging. The QA engineer's DoD enforcement mandate (QA-001: "work not meeting DoD is not complete") ensures that stories are only marked complete when all criteria are verified. QA also executes test types identified in the Test Architecture (P-032): integration tests, regression tests, accessibility checks.
- **platform-engineer** — The platform-engineer owns the CI/CD infrastructure that the feature development process depends on: CI pipelines running automated tests, SAST scanning, staging environment deployment. The platform-engineer does not participate in feature development directly but maintains the infrastructure that enables it.

### 6. Stages/Steps

| Step | Actor | Action | Output |
|------|-------|--------|--------|
| 1. Story Pickup | Engineer | Engineer picks up an assigned story from the sprint backlog. Reads the story description and all acceptance criteria. If any criterion is unclear, the engineer asks the PM for clarification before starting implementation. | Story understood; criteria clear |
| 2. Technical Planning | Engineer (+ TL for complex stories) | Engineer plans the implementation: identifies files to modify, dependencies to consume, APIs to call, data models to update. For L5/TL-complexity stories, TL reviews the approach before implementation begins. | Implementation plan (mental or documented) |
| 3. Feature Branch | Engineer | Engineer creates a feature branch from the team's main development branch. Branch naming follows team convention (e.g., `feature/PROJ-123-tokenization-sdk`). | Feature branch created |
| 4. Implementation | Engineer | Engineer implements the feature in the feature branch. Code must be production-ready (SE-001: no placeholders, SE-006: enterprise-ready). Input validation at system boundaries. Error handling with meaningful messages. Functions under 50 lines. Config via environment variables. | Feature implemented in branch |
| 5. Automated Tests | Engineer | Engineer writes automated tests: unit tests covering happy path and error cases, integration tests if the story involves cross-component interaction. Tests must pass locally before opening a PR. Coverage meets team standard (typically >70% for new code per P-032 Test Architecture). | Tests written and passing locally |
| 6. Pull Request | Engineer | Engineer opens a pull request (PR) against the main branch. PR description references the story ID and lists acceptance criteria for reviewer context. PR triggers CI pipeline. | PR opened; CI triggered |
| 7. CI Gates | Automated (platform-engineer infrastructure) | CI pipeline executes: (a) automated tests run and pass, (b) SAST scan runs and no new critical or high findings, (c) linting and formatting checks pass, (d) build succeeds. If any CI gate fails, the engineer fixes the issue and re-pushes. | CI gates passed |
| 8. Peer Code Review | Peer Engineer (>= 1 reviewer) | At least one peer reviews the PR. Review checks: code quality, test coverage, acceptance criteria alignment, security considerations, documentation updates. Reviewer approves or requests changes. | PR approved by peer |
| 9. Merge to Main | Engineer | After PR approval and CI gates passing, engineer merges to the main branch. Merge triggers deployment to staging environment. | Code merged; staging deployment triggered |
| 10. Staging Deployment and Smoke Test | Engineer | Engineer verifies the feature is deployed to staging and performs a smoke test: the feature works as expected in the staging environment. | Feature deployed and smoke-tested in staging |
| 11. Documentation Update | Engineer | If applicable, engineer updates: API documentation (OpenAPI spec), runbook entries, README, or other relevant documentation. Documentation is part of the DoD — not optional. | Documentation updated |
| 12. Acceptance Criteria Verification | QA (or PM) | QA verifies each acceptance criterion in staging. For each criterion: **Met** or **Not Met**. If any criterion is not met, the story is returned to the engineer with specific feedback. If all criteria are met, QA records the verification. | Acceptance criteria verification record |
| 13. Story Completion | Engineer | After all DoD items are verified (code reviewed, tests passing, SAST clean, docs updated, acceptance verified, staging deployed), engineer marks the story as complete in the sprint board. | Story marked complete |

### 7. Inputs
- Sprint story with acceptance criteria (P-024 output)
- Team Definition of Done checklist (Sprint Kickoff Brief Section 5)
- Test Architecture document (P-032) — test types and coverage targets
- CI/CD pipeline configuration (platform-engineer infrastructure)
- Staging environment access

### 8. Outputs/Artifacts
- **Merged, Tested, Staged Feature** — Code in the main branch, deployed to staging, smoke-tested
- **Acceptance Criteria Verification Record** — QA/PM sign-off on each criterion
- **Updated Documentation** — API docs, runbooks, or README as applicable
- **CI Gate Results** — Test results, SAST scan results, build artifacts
- **Story Completion Record** — Story marked complete in sprint board with all DoD items verified

### 9. Gate/Checkpoint
Two-level gate:
1. **CI Gates (automated)** — automated tests pass, SAST scan clean, build succeeds. These gates are enforced by the CI/CD pipeline (platform-engineer infrastructure) and cannot be bypassed.
2. **Acceptance Criteria Verification (human gate)** — QA or PM verifies each criterion in staging. This gate is enforced by the QA engineer's DoD mandate (QA-001). A story cannot be marked complete without this verification.

### 10. Success Criteria
- All six Sprint DoD checklist items are met before any story is marked complete:
  1. Code reviewed by at least one peer
  2. Automated tests written and passing in CI
  3. SAST scan clean (no new critical or high findings)
  4. Documentation updated (if applicable)
  5. Acceptance criteria verified by PM or QA
  6. Deployed to staging and smoke-tested
- No story is closed without acceptance criteria verification by PM or QA
- No story is closed with failing CI gates
- Stories that fail acceptance verification are returned to the engineer with specific feedback, not abandoned
- Feature branches are short-lived (merged within the sprint, not spanning multiple sprints)

### 11. Dependencies
| Dependency | Process | Type | Detail |
|-----------|---------|------|--------|
| Sprint Readiness Gate passed | P-025 | Hard prerequisite | Sprint must be active and stories assigned |
| Story Writing | P-024 | Hard prerequisite | Stories with acceptance criteria must exist before development begins |
| Test Architecture Design | P-032 | Informational | Test types and coverage targets inform what tests to write |
| DoD Enforcement | P-034 | Structural | QA enforces DoD verification at the acceptance criteria step |
| CI/CD Pipeline | Platform infrastructure | Structural | CI pipeline must be operational for automated gates |
| Staging Environment | Platform infrastructure | Structural | Staging must be available for deployment and verification |

### 12. Traceability
- **Upstream**: P-025 (Sprint Readiness Gate) — sprint must be active
- **Upstream**: P-024 (Story Writing) — stories and acceptance criteria are the development input
- **Upstream**: P-032 (Test Architecture Design) — test strategy informs testing approach
- **Downstream**: P-027 (Sprint Review) — completed features are demonstrated at the review
- **Downstream**: P-034 (DoD Enforcement) — QA enforces DoD as part of this process
- **Downstream**: P-038 (SAST/SCA scanning) — security scans are automated CI gates in this process
- **Cross-reference**: Software-engineer agent workflow: understand → implement → test → review → done
- **Cross-reference**: Clarity of Intent Sprint DoD checklist (six items)
- **Artifact**: Merged feature in staging; acceptance criteria verification record

---

## Cross-Process Dependency Map

### Internal Category Dependencies

The following diagram shows how the 10 processes in Category 4 relate to each other:

```
                         SPRINT PREPARATION
                         ==================
                    
  P-013 (Scope Lock)    P-019 (Dep. Acceptance)
        |                       |
        v                       v
  P-022: Sprint Goal -----> P-030: Sprint-Level
        |                   Dependency Tracking
        |                       |
        v                       |
  P-023: Intent Trace           |
        |                       |
        v                       |
  P-024: Story Writing          |
        |                       |
        +-------+-------+------+
                |
                v
        P-025: Sprint Readiness Gate
                |
                v
                
                         ACTIVE SPRINT
                         =============
                
        P-026: Daily Standup
                |
        P-031: Feature Development
        (P-030: ongoing monitoring)
                |
                v
                
                         SPRINT CLOSURE
                         ==============
                
        P-027: Sprint Review
                |
                v
        P-028: Sprint Retrospective
                |
        P-029: Backlog Refinement
                |
                +-----> feeds next sprint's P-024/P-022
```

### Upstream Dependencies (from other categories)

| Source Process | Source Category | What It Provides | Consumed By |
|---------------|----------------|-----------------|-------------|
| P-004: Intent Review Gate | 1 — Intent & Strategic Alignment | Locked Intent Brief (outcome statement) | P-023 (intent trace line 1) |
| P-013: Scope Lock Gate | 2 — Scope & Contract Management | Locked Scope Contract (deliverables, DoD, exclusions, metrics) | P-022 (deliverable selection), P-023 (trace line 2), P-024 (story decomposition), P-029 (criteria baseline) |
| P-014: Scope Change Control | 2 — Scope & Contract Management | Approved scope changes | P-023 (updated trace), P-029 (modified backlog) |
| P-016: Critical Path Analysis | 3 — Dependency & Coordination | Critical path and deliverable sequencing | P-022 (deliverable ordering), P-029 (story priority) |
| P-019: Dependency Acceptance Gate | 3 — Dependency & Coordination | Locked Dependency Charter with commitments | P-022 (goal feasibility), P-025 (prerequisite), P-030 (tracking baseline) |
| P-020: Dependency Standup | 3 — Dependency & Coordination | Ongoing dependency status updates | P-026 (cross-team blocker routing), P-030 (status monitoring) |
| P-021: Dependency Escalation | 3 — Dependency & Coordination | Escalation resolution outcomes | P-028 (retrospective input), P-030 (contingency activation) |
| P-032: Test Architecture Design | 5 — Quality Assurance & Testing | Test types, coverage targets, tooling | P-024 (acceptance criteria test types), P-031 (testing approach) |
| P-034: DoD Enforcement | 5 — Quality Assurance & Testing | QA verification of acceptance criteria | P-031 (acceptance verification step) |

### Downstream Dependencies (to other categories)

| Target Process | Target Category | What It Consumes | Provided By |
|---------------|----------------|-----------------|-------------|
| P-014: Scope Change Control | 2 — Scope & Contract Management | Scope change requests from sprint review feedback | P-027 |
| P-021: Dependency Escalation | 3 — Dependency & Coordination | Persistent blockers from standup | P-026 |
| P-034: DoD Enforcement | 5 — Quality Assurance & Testing | Stories needing acceptance verification | P-031 |
| P-038: SAST/SCA Scanning | 6 — Security & Compliance | Code changes needing security scan | P-031 |
| P-070: Project Post-Mortem | 16 — Post-Delivery & Retrospective | Cumulative sprint data, retrospective patterns | P-027, P-028 |
| P-071: Process Health Review | 16 — Post-Delivery & Retrospective | Sprint goal completion rates, retrospective action item closure rates | P-027, P-028 |

### Gate Chain Position

Category 4 contains the fourth and final gate in the Clarity of Intent process:

```
P-004 (Intent Review) → P-013 (Scope Lock) → P-019 (Dependency Acceptance) → P-025 (Sprint Readiness)
     Category 1              Category 2              Category 3                   Category 4
```

After the Sprint Readiness Gate (P-025), the process enters the recurring sprint cycle. There are no further formal gates — instead, the sprint review (P-027) and retrospective (P-028) serve as recurring inspection and adaptation ceremonies.

### Sprint Cycle Timing

Based on Engineering Team Structure Guide Section 11.2 (2-week sprint standard):

| Process | Timing Within Sprint Cycle | Duration |
|---------|---------------------------|----------|
| P-022: Sprint Goal Authoring | 1-2 days before sprint start | 1-2 hours |
| P-023: Intent Trace Validation | After P-022, before sprint start | 30 minutes |
| P-024: Story Writing | 1-2 days before sprint start (with P-029 pre-work) | 2-4 hours |
| P-025: Sprint Readiness Gate | Sprint Day 1, start of planning | 15-30 minutes |
| P-026: Daily Standup | Every working day (Days 1-10) | 15 minutes |
| P-029: Backlog Refinement | Mid-sprint (Day 5-7), weekly | 1 hour |
| P-030: Sprint-Level Dependency Tracking | Pre-sprint setup + daily monitoring | 30 minutes setup + ongoing |
| P-031: Feature Development | Days 1-10 (continuous) | Full sprint |
| P-027: Sprint Review | Sprint Day 10 (last day) | 1-2 hours |
| P-028: Sprint Retrospective | Sprint Day 10 (after review) | 1-1.5 hours |

### Measurement Signals

The following signals from the Clarity of Intent framework directly measure Category 4 process effectiveness:

| Signal | How to Measure | Healthy State | Process Source |
|--------|---------------|---------------|----------------|
| Sprint goal completion rate | Percentage of sprints with goal fully achieved | > 80% | P-022, P-027 |
| Intent alignment | Random engineer explains project intent in one sentence | Yes, consistently | P-023 |
| Late dependency discovery | Dependencies discovered after Sprint 1 not in charter | < 1 per project | P-030 |
| Scope changes per project | Count of Scope Change Requests after Scope Lock | < 2 major per project | P-027 (feedback triage) |
| Action item closure rate | Retrospective items closed within 2 sprints | >= 80% | P-028 |

---

## Appendix: Sprint Kickoff Brief Template

The complete Sprint Kickoff Brief produced by P-022, P-023, P-024, and P-030 (locked at P-025) follows this structure. Each squad produces its own brief.

### Section 1: Sprint Goal (P-022)

**Sprint Goal**: By the end of Sprint [N], [observable condition] that is not true today.

### Section 2: Intent Trace (P-023)

```
Project Intent:    [Intent Brief outcome statement — verbatim]
Scope Deliverable: [Scope Contract deliverable name and ID]
Sprint Goal:       [One-sentence sprint goal]
```

### Section 3: Stories and Acceptance Criteria (P-024)

| Story | Acceptance Criteria | Points | Assignee | Parent Deliverable |
|-------|-------------------|--------|----------|-------------------|
| [Story title] | [Given/When/Then or checklist] | [Fibonacci] | [Engineer name] | [Deliverable ID] |

### Section 4: Dependencies Due This Sprint (P-030)

| Dependency | Needed By | Current Status | Contingency if Late |
|------------|-----------|---------------|---------------------|
| [Dependency from charter] | [Sprint N, Day X] | [On Track / At Risk / Blocked] | [Specific action] |

### Section 5: Definition of Done — Sprint Level (Reference)

Every story must meet all of these criteria to be counted as complete:
- [ ] Code reviewed by at least one peer
- [ ] Automated tests written and passing in CI
- [ ] SAST scan clean (no new critical or high findings)
- [ ] Documentation updated (API docs, runbook, or README as applicable)
- [ ] Acceptance criteria verified by PM or QA
- [ ] Deployed to staging and smoke-tested

---

*End of specification.*

---

## Cross-Category Dependencies

### Dependencies FROM Other Categories (Inputs)

| Source Process | Source Category | Consuming Process | Nature |
|---------------|----------------|-------------------|--------|
| P-013 (Scope Lock Gate) | Cat 2: Scope & Contract | P-022 (Sprint Goal Authoring) | Scope Contract locked for sprint goals |
| P-019 (Dependency Acceptance Gate) | Cat 3: Dependency & Coordination | P-022 (Sprint Goal Authoring) | Dependencies accepted before sprint prep |
| P-004 (Intent Review Gate) | Cat 1: Intent & Strategic Alignment | P-023 (Intent Trace Validation) | Intent Brief for intent trace |
| P-015 (Dependency Registration) | Cat 3: Dependency & Coordination | P-030 (Sprint-Level Dependency Tracking) | Dependency Charter provides sprint dependencies |

### Dependencies TO Other Categories (Outputs)

| Providing Process | Consuming Process | Target Category | Nature |
|------------------|-------------------|-----------------|--------|
| P-031 (Feature Development) | P-034 (DoD Enforcement) | Cat 5: Quality Assurance | Story completion triggers DoD verification |
| P-031 (Feature Development) | P-058 (API Documentation) | Cat 10: Documentation | API changes need documentation |
| P-024 (Story Writing) | P-034 (DoD Enforcement) | Cat 5: Quality Assurance | Stories must have criteria for DoD check |
| P-025 (Sprint Readiness Gate) | P-031 (Feature Development) | Cat 4 (self) | Sprint readiness enables development |
| P-027 (Sprint Review) | P-079 (Stakeholder Update Cadence) | Cat 14: Communication | Sprint outcomes feed stakeholder updates |

## Agent Assignments Summary

| Process | Primary Owner | Supporting Agents |
|---------|--------------|-------------------|
| P-022: Sprint Goal Authoring | engineering-manager | software-engineer (TL), product-manager |
| P-023: Intent Trace Validation | engineering-manager | product-manager |
| P-024: Story Writing | product-manager | software-engineer (TL), qa-engineer |
| P-025: Sprint Readiness Gate | engineering-manager | product-manager, software-engineer, technical-program-manager |
| P-026: Daily Standup | product-manager (Scrum Master) | software-engineer, engineering-manager |
| P-027: Sprint Review | engineering-manager | product-manager, software-engineer |
| P-028: Sprint Retrospective | engineering-manager | product-manager, software-engineer |
| P-029: Backlog Refinement | product-manager | software-engineer (TL) |
| P-030: Sprint-Level Dependency Tracking | technical-program-manager | engineering-manager |
| P-031: Feature Development | software-engineer | qa-engineer, platform-engineer |
