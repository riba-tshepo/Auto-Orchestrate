# Technical Specification: Intent & Strategic Alignment Processes
## Category 1 — Processes P-001 through P-006

**Session**: auto-orc-20260405-procderive
**Date**: 2026-04-05
**Stage**: 2 — Formal Process Specification
**Source**: Stage 1 Process Architecture (Category 1); Clarity of Intent Framework (Stage 1); Engineering Team Structure Guide
**Status**: Draft

---

## Document Purpose

This specification formally defines the six processes that comprise Category 1: Intent & Strategic Alignment. These processes govern how strategic intent enters the engineering organization, how it is validated against company objectives, how boundaries are established, and how gate reviews enforce quality before downstream execution begins.

All six processes trace to the Clarity of Intent framework (primarily Stage 1: Intent Frame) and to the organizational hierarchy responsibilities defined in the Engineering Team Structure Guide.

---

## Agent Roster (Referenced in This Specification)

| Agent ID | Roles Covered |
|----------|--------------|
| product-manager | APM, PM, GPM, CPO; Scrum Master; Agile Coach |
| engineering-manager | EM (M4-M5), Director, VP, CTO |
| technical-program-manager | TPM; Program Manager; Release Manager; RTE |
| staff-principal-engineer | Staff (L6), Principal (L7), Distinguished (L8), Fellow (L9) |
| software-engineer | L3-L5 IC; Tech Lead (TL) |

---

## P-001: Intent Articulation Process

### 1. Process ID and Name

**ID**: P-001
**Name**: Intent Articulation Process

### 2. Purpose

Produce a two-page Intent Brief answering five mandatory questions — outcome, beneficiaries, strategic context, boundaries, and cost of inaction — before any solution design begins. The Intent Brief is the foundational artifact that all downstream processes consume. Without it, no project enters the engineering pipeline.

### 3. Derived From

- **Clarity of Intent** — Stage 1: Intent Frame (full stage)
- Specifically: the five questions that form the Intent Brief (Sections "What outcome are we trying to achieve?", "Who specifically benefits and how?", "What is the strategic context?", "What are the boundaries of this project?", "What happens if we don't do this?")

### 4. Primary Owner Agent

**product-manager** — The lead PM co-authors the Intent Brief with the Project Sponsor. The PM facilitates the structured questioning process and is responsible for ensuring the document meets quality standards before gate submission.

### 5. Supporting Agents

| Agent | Role in This Process |
|-------|---------------------|
| engineering-manager | The Director or VP acts as the Project Sponsor. They provide the business need, strategic rationale, and confirm organizational commitment. |

### 6. Stages/Steps

| Step | Action | Owner | Duration | Detail |
|------|--------|-------|----------|--------|
| 1 | **Trigger identification** | Sponsor (engineering-manager scope) | — | A business need, market signal, OKR initiative, or competitive pressure triggers the need for a new project. The Sponsor determines that an Intent Brief is required. |
| 2 | **Facilitated session scheduling** | product-manager | Day 0 | PM schedules a facilitated working session with the Sponsor. Maximum window: 1-3 working days from trigger to completed draft. |
| 3 | **Five-question articulation** | product-manager + Sponsor | Days 1-2 | PM facilitates the Sponsor through each of the five mandatory questions: (a) **Outcome**: State the desired end-state in measurable terms with a timeline. Must be observable and measurable after the project ships. (b) **Beneficiaries**: Name the specific user segment, internal team, or customer cohort. Describe before/after from their perspective. (c) **Strategic context**: Connect the project to a specific company OKR, quarterly theme, or documented competitive pressure. Must reference a real, trackable OKR. (d) **Boundaries**: Explicitly enumerate what the project is NOT. Minimum one exclusion required. Each exclusion states a reason and a future home. (e) **Cost of inaction**: Describe what happens if this project does not proceed. Forces the Sponsor to articulate urgency and acceptable risk level. |
| 4 | **Internal review** | product-manager + Sponsor | Day 2-3 | PM and Sponsor review the draft Intent Brief for completeness, specificity, and brevity. The document must not exceed two pages. Vague or aspirational language is revised. |
| 5 | **Gate submission** | product-manager | Day 3 | PM submits the Intent Brief to the Intent Review Gate (P-004). The brief is distributed to all gate reviewers at least 24 hours before the scheduled review. |

### 7. Inputs

| Input | Source | Required/Optional |
|-------|--------|-------------------|
| Business need or market signal | Sponsor / executive leadership | Required |
| Company OKR documentation | Confluence / Notion / OKR tracking system | Required |
| Related project and roadmap context | PM / engineering-manager | Optional (supports boundary definition) |

### 8. Outputs/Artifacts

| Output | Format | Destination |
|--------|--------|-------------|
| **Intent Brief** | Structured document, max 2 pages, answering all 5 mandatory questions | Project root (Confluence / Notion); consumed by P-002, P-003, P-004 |
| **Gate submission packet** | Intent Brief + OKR reference documentation | Distributed to P-004 reviewers |

### 9. Gate/Checkpoint

This process does not contain its own gate. Its output is consumed by the **Intent Review Gate (P-004)**. The Intent Brief must pass P-004 before any downstream process (Scope Contract, Dependency Map, Sprint Bridge) can begin.

**Pre-submission quality check** (internal, not a formal gate):
- All 5 questions answered
- No question answered with vague language (e.g., "our users", "improve experience", "leadership wants this")
- Document fits within 2 pages
- At least 1 explicit exclusion present

### 10. Success Criteria

| Criterion | Measurement |
|-----------|-------------|
| All 5 questions answered with measurable specifics | Review against each question; no vague or aspirational language |
| Outcome statement is measurable and has a timeline | Outcome includes a metric, a target value, and a time horizon |
| Minimum 1 explicit exclusion stated | Boundaries section contains at least 1 "NOT" item with reason and future home |
| Strategic context references a real, documented OKR | OKR exists in official tracking system; is currently active |
| Document does not exceed 2 pages | Physical length check |

### 11. Dependencies

| Direction | Process | Nature |
|-----------|---------|--------|
| **Depends on** | None | P-001 is a starting-point process (Program 0). It has no upstream process dependency. |
| **Depended on by** | P-002 (OKR Alignment Verification) | P-002 consumes the Intent Brief to verify OKR linkage |
| **Depended on by** | P-003 (Boundary Definition) | P-003 refines the exclusion list within the Intent Brief |
| **Depended on by** | P-004 (Intent Review Gate) | P-004 evaluates the Intent Brief against pass criteria |
| **Depended on by** | P-007+ (all Scope Contract processes) | Downstream processes cannot begin without a locked Intent Brief |

### 12. Traceability

| Trace | Reference |
|-------|-----------|
| Clarity of Intent — Stage 1: Intent Frame | Full stage; all 5 questions |
| Clarity of Intent — Stage 1: The Intent Brief | Artifact definition, length constraint, question structure |
| Engineering Team Structure Guide — Section 2.1 | Sponsor role (Director/VP); PM role under CPO reporting line |
| Engineering Team Structure Guide — Section 8 | Product and Program Management Structure; PM responsibilities |

---

## P-002: OKR Alignment Verification Process

### 1. Process ID and Name

**ID**: P-002
**Name**: OKR Alignment Verification Process

### 2. Purpose

Validate that the project connects to a documented, active company OKR before the Intent Review Gate passes. This process prevents engineering investment on work that is not strategically aligned. It operationalizes Question 3 of the Intent Brief ("What is the strategic context?") by requiring verifiable evidence of OKR linkage, not just a thematic reference.

### 3. Derived From

- **Clarity of Intent** — Stage 1, Question 3: "What is the strategic context?"
- **Clarity of Intent** — Stage 1, Gate: Intent Review pass criteria (strategic context references a real OKR)
- **Engineering Team Structure Guide** — Section 1: OKRs for goal alignment top-to-bottom

### 4. Primary Owner Agent

**product-manager** — The PM is responsible for identifying and documenting the OKR linkage within the Intent Brief.

### 5. Supporting Agents

| Agent | Role in This Process |
|-------|---------------------|
| engineering-manager | The Engineering Director confirms the referenced OKR is authentic and currently active during the Intent Review Gate. |

### 6. Stages/Steps

| Step | Action | Owner | Detail |
|------|--------|-------|--------|
| 1 | **Retrieve current OKR documentation** | product-manager | PM accesses the official company OKR tracking system (Confluence / Notion / dedicated OKR tool) and retrieves the current quarter's Objectives and Key Results. |
| 2 | **Map project outcome to specific Key Result** | product-manager | PM identifies the specific Key Result that the project's intended outcome will impact. The linkage must be causal, not thematic — the project outcome must directly contribute to moving the Key Result metric. |
| 3 | **Document OKR reference in Intent Brief** | product-manager | PM writes the OKR reference into the "strategic context" section of the Intent Brief, including: (a) the Objective text, (b) the specific Key Result text, (c) the causal rationale explaining how this project moves the Key Result. |
| 4 | **Director confirmation** | engineering-manager (Director) | During the Intent Review Gate (P-004), the Director for the affected area confirms: (a) the referenced OKR exists in the official system, (b) the OKR is currently active (not deprecated or deferred), (c) the causal linkage is credible. |

### 7. Inputs

| Input | Source | Required/Optional |
|-------|--------|-------------------|
| Intent Brief draft (with strategic context section) | P-001 output | Required |
| Company OKR documentation | OKR tracking system (Confluence / Notion) | Required |

### 8. Outputs/Artifacts

| Output | Format | Destination |
|--------|--------|-------------|
| **OKR reference** | Documented within Intent Brief strategic context section | Intent Brief (Section: Strategic Context) |
| **Director sign-off** | Verbal or written confirmation at P-004 gate | Gate decision record |

### 9. Gate/Checkpoint

P-002 does not have its own standalone gate. Its output is evaluated as one of the five pass criteria within the **Intent Review Gate (P-004)**:

> "Strategic context references a real OKR or documented priority."

**Pass condition**: The Director confirms the OKR is real, active, and causally linked to the project outcome.
**Fail condition**: The OKR does not exist, is not active, or the linkage is only thematic (not causal).

### 10. Success Criteria

| Criterion | Measurement |
|-----------|-------------|
| Referenced OKR exists in the official OKR tracking system | Verified by Director during P-004 gate |
| The project outcome is causally linked to the Key Result | Not merely thematic — the PM can articulate the causal mechanism |
| The OKR is a current company priority | Not deprecated, deferred, or from a prior quarter without explicit carry-forward |

### 11. Dependencies

| Direction | Process | Nature |
|-----------|---------|--------|
| **Depends on** | P-001 (Intent Articulation) | The Intent Brief must exist before OKR alignment can be verified |
| **Depended on by** | P-004 (Intent Review Gate) | OKR alignment is a required pass criterion for the gate |

### 12. Traceability

| Trace | Reference |
|-------|-----------|
| Clarity of Intent — Stage 1, Question 3 | "Connect this project to a company OKR, a quarterly theme, or a competitive pressure" |
| Clarity of Intent — Stage 1, Gate: Intent Review | Pass criteria: "The strategic context references a real OKR or documented priority" |
| Engineering Team Structure Guide — Section 1 | "Quarterly OKRs for goal alignment top-to-bottom" |
| Engineering Team Structure Guide — Section 3.1 | Director of Engineering: "Owns product area roadmap execution" — confirms authority to validate OKR linkage |

---

## P-003: Boundary Definition Process

### 1. Process ID and Name

**ID**: P-003
**Name**: Boundary Definition Process

### 2. Purpose

Explicitly enumerate what this project is NOT building. The Clarity of Intent framework asserts that explicit exclusions prevent scope drift more effectively than detailed inclusions. This process ensures that at minimum one explicit boundary is defined before the Intent Review Gate, and that each exclusion includes a rationale and a future home designation.

### 3. Derived From

- **Clarity of Intent** — Stage 1, Question 4: "What are the boundaries of this project?"
- **Clarity of Intent** — Stage 1, Gate: Intent Review pass criteria ("At least one explicit boundary — what this is NOT — is stated")
- **Clarity of Intent** — Stage 2, Scope Contract Section 4: Explicit Exclusions (downstream consumer of this output)

### 4. Primary Owner Agent

**product-manager** — The PM facilitates the boundary-definition discussion and documents exclusions in the Intent Brief.

### 5. Supporting Agents

| Agent | Role in This Process |
|-------|---------------------|
| engineering-manager | The Sponsor (Director/VP) confirms that each exclusion is intentional and that no critical scope has been accidentally excluded. |

### 6. Stages/Steps

| Step | Action | Owner | Detail |
|------|--------|-------|--------|
| 1 | **Scope adjacency brainstorm** | product-manager + Sponsor | PM and Sponsor brainstorm all items that could reasonably be considered part of the project scope — features, user segments, platforms, integrations, and technical investments that are related but not necessarily required. |
| 2 | **IN/OUT classification** | product-manager + Sponsor | Each candidate item is classified as IN (this project) or OUT (excluded). Items classified as IN feed P-001 (the Intent Brief outcome and beneficiary answers). Items classified as OUT proceed to Step 3. |
| 3 | **Exclusion documentation** | product-manager | Each OUT item is documented with three fields: (a) **What is excluded**: clear statement of the excluded item, (b) **Why it is excluded**: reason — different problem, different user segment, separate initiative, insufficient data, etc., (c) **Future home**: where this item will be addressed (e.g., "Q4 roadmap candidate", "Payments team backlog", "Requires separate Intent Brief", or "Will not be addressed"). |
| 4 | **Minimum threshold check** | product-manager | PM verifies that the Intent Brief contains at least one explicit exclusion. If zero exclusions exist, the PM and Sponsor revisit Step 1 — every project has boundaries. |
| 5 | **Sponsor confirmation** | engineering-manager (Sponsor) | Sponsor reviews the exclusion list and confirms: (a) no critical scope has been accidentally excluded, (b) each exclusion rationale is accurate, (c) future home designations are realistic. |

### 7. Inputs

| Input | Source | Required/Optional |
|-------|--------|-------------------|
| Intent Brief draft (in progress) | P-001 | Required |
| Related project and roadmap context | PM, Sponsor, engineering-manager | Required |
| Previous project exclusion lists (if related projects exist) | Historical project documentation | Optional |

### 8. Outputs/Artifacts

| Output | Format | Destination |
|--------|--------|-------------|
| **Explicit exclusion list** | Structured list within Intent Brief; each item with reason and future home | Intent Brief (Section: Boundaries) |
| **Exclusion rationale** | Documented per-item justification | Same section; carried forward to Scope Contract Section 4 (Explicit Exclusions) in Stage 2 |

### 9. Gate/Checkpoint

P-003 does not have its own standalone gate. Its output is evaluated as one of the five pass criteria within the **Intent Review Gate (P-004)**:

> "At least one explicit boundary (what this is NOT) is stated."

**Pass condition**: At least one exclusion exists, with a reason and a future home.
**Fail condition**: No exclusions stated, or exclusions are vague ("we won't do other stuff").

### 10. Success Criteria

| Criterion | Measurement |
|-----------|-------------|
| At least 1 explicit boundary stated | Count of exclusion items >= 1 |
| Each exclusion states why it is excluded | Every OUT item has a documented reason |
| Each exclusion states a future home or "will not be addressed" | Every OUT item has a future home field populated |
| No critical scope accidentally excluded | Sponsor has confirmed the exclusion list |

### 11. Dependencies

| Direction | Process | Nature |
|-----------|---------|--------|
| **Depends on** | P-001 (Intent Articulation) | Occurs during Intent Brief authoring; requires the Intent Brief to exist |
| **Depended on by** | P-004 (Intent Review Gate) | At least 1 exclusion is a required pass criterion |
| **Depended on by** | P-009 (Explicit Exclusion Authoring — Scope Contract Stage) | Scope Contract Section 4 carries forward and expands the exclusion list from this process |

### 12. Traceability

| Trace | Reference |
|-------|-----------|
| Clarity of Intent — Stage 1, Question 4 | "State what this project is NOT. Explicit exclusions prevent scope drift more effectively than detailed inclusions." |
| Clarity of Intent — Stage 1, Gate: Intent Review | Pass criteria: "At least one explicit boundary (what this is NOT) is stated" |
| Clarity of Intent — Stage 2, Scope Contract Section 4 | Explicit Exclusions table (downstream consumer); each exclusion has Exclusion, Reason, Future Home columns |
| Clarity of Intent — Change Control | Scope Change Requests reference the original boundary definitions from this process |

---

## P-004: Intent Review Gate Process

### 1. Process ID and Name

**ID**: P-004
**Name**: Intent Review Gate Process

### 2. Purpose

Structured review gate confirming that the Intent Brief meets all five quality criteria before the project proceeds to Scope Contract authoring (Stage 2). This is the first formal checkpoint in the Clarity of Intent pipeline. Failing this gate is not a failure — it means the intent is not yet clear enough to build on. The gate prevents ambiguity from propagating into scope definition, dependency mapping, and sprint planning.

### 3. Derived From

- **Clarity of Intent** — Stage 1: Gate: Intent Review (full gate definition)
- **Clarity of Intent** — Stage 1: "Each stage has one artifact and one gate. The gate is a short, structured review where specific people confirm they understand and accept what was produced."

### 4. Primary Owner Agent

**engineering-manager** — The Engineering Director for the affected area chairs the gate review. The Director has authority to issue a PASS or FAIL decision.

### 5. Supporting Agents

| Agent | Role in This Process |
|-------|---------------------|
| product-manager | PM presents the Intent Brief at the gate review. Answers questions from reviewers. Owns revision if the gate fails. |
| engineering-manager (Tribe Leads) | Participate as reviewers. Must confirm they can explain the project's purpose to their teams. |

### 6. Stages/Steps

| Step | Action | Owner | Duration | Detail |
|------|--------|-------|----------|--------|
| 1 | **Pre-distribution** | product-manager | T-24h before gate | PM distributes the finalized Intent Brief to all gate participants at least 24 hours before the scheduled review. Ensures reviewers have time to read and prepare questions. |
| 2 | **Gate meeting convened** | engineering-manager (Director) | 30 min (sync) or 48h window (async) | **Sync format**: 30-minute meeting. Director chairs. PM presents. Each section of the Intent Brief is reviewed against the five pass criteria. **Async format**: Intent Brief posted to designated review channel with a 48-hour response window. Each reviewer must respond with explicit PASS or FAIL with rationale. |
| 3 | **Five-criteria evaluation** | All participants | During gate | Each pass criterion is evaluated: (a) All 5 questions answered with specifics — no vague or aspirational language, (b) Outcome is measurable and has a timeline, (c) At least 1 explicit boundary (what this is NOT) is stated, (d) Strategic context references a real OKR or documented priority (Director confirms per P-002), (e) All reviewers confirm: "I can explain this project's purpose to my team in one sentence." |
| 4 | **Comprehension check** | engineering-manager (Director) | During gate | Director asks each reviewer: "Can you explain this project's purpose to your team in one sentence?" Each reviewer responds. If any reviewer cannot, the gate fails on that criterion. |
| 5 | **Decision recording** | engineering-manager (Director) | End of gate | Director records the gate decision: **PASS**: Intent Brief is locked. No further modifications without a formal change request. Stage 2 (Scope Contract) may begin. **FAIL**: Specific revisions required are documented. A revision owner (typically PM + Sponsor) and a deadline are assigned within the gate meeting. The brief is revised and the gate is re-run. |
| 6 | **Post-gate actions** | product-manager | Immediately after | If PASS: Intent Brief is versioned and locked in the project root. PM notifies downstream process owners (Scope Contract authors) that Stage 2 may begin. If FAIL: PM and Sponsor revise the Intent Brief per documented feedback and resubmit (return to P-001 Step 4). |

### 7. Inputs

| Input | Source | Required/Optional |
|-------|--------|-------------------|
| Intent Brief (final draft) | P-001 output | Required |
| OKR documentation reference | P-002 output; OKR tracking system | Required |
| Exclusion list | P-003 output (within Intent Brief) | Required |

### 8. Outputs/Artifacts

| Output | Format | Destination |
|--------|--------|-------------|
| **Gate decision record** | PASS or FAIL with documented rationale | Project root (version-controlled) |
| **Revision requirements** (if FAIL) | List of specific items to address, with owner and deadline | PM; Sponsor |
| **Locked Intent Brief** (if PASS) | Versioned, immutable document | Project root (Confluence / Notion); consumed by Stage 2 processes (P-007 onwards) |

### 9. Gate/Checkpoint

**This IS the gate.** P-004 is a formal gate process, not a process that feeds into a gate. The gate has binary pass criteria:

| # | Criterion | Pass Condition | Fail Condition |
|---|-----------|----------------|----------------|
| 1 | All 5 questions answered with specifics | Each question has a concrete, specific answer | Any question answered with vague or aspirational language |
| 2 | Outcome is measurable and has a timeline | Outcome includes metric, target, and time horizon | Outcome is a feature description or vague aspiration |
| 3 | At least 1 explicit boundary stated | Boundaries section contains >= 1 exclusion with reason and future home | No exclusions, or exclusions are vague |
| 4 | Strategic context references real OKR | Director confirms OKR is real, active, and causally linked | OKR does not exist, is inactive, or linkage is only thematic |
| 5 | All reviewers can explain the project purpose | Every reviewer articulates a one-sentence explanation | Any reviewer cannot explain the project purpose |

**All five criteria must pass for the gate to pass. Any single failure causes the entire gate to fail.**

### 10. Success Criteria

| Criterion | Measurement |
|-----------|-------------|
| Gate passes or fails with a documented, specific reason | Decision record exists with per-criterion evaluation |
| No reviewer abstains | All invited reviewers actively confirm or raise objections; abstention is not permitted |
| If FAIL, revision owner and deadline assigned within the gate meeting | Revision assignment documented before the meeting ends |
| Gate cycle time does not exceed 48 hours (sync) or 72 hours (async) | Measured from Intent Brief distribution to decision |

### 11. Dependencies

| Direction | Process | Nature |
|-----------|---------|--------|
| **Depends on** | P-001 (Intent Articulation) | The Intent Brief must be complete |
| **Depends on** | P-002 (OKR Alignment Verification) | OKR reference must be present in the Intent Brief |
| **Depends on** | P-003 (Boundary Definition) | At least 1 exclusion must be present in the Intent Brief |
| **Depended on by** | P-007 (Deliverable Decomposition) | Scope Contract authoring cannot begin until this gate passes |
| **Depended on by** | All Stage 2 processes (P-007 through P-014) | The locked Intent Brief is the input to the entire Scope Contract stage |

### 12. Traceability

| Trace | Reference |
|-------|-----------|
| Clarity of Intent — Stage 1: Gate: Intent Review | Full gate definition including participants, format, and pass criteria |
| Clarity of Intent — "Each stage has one artifact and one gate" | P-004 is the gate for Stage 1 |
| Clarity of Intent — "If the gate does not pass" | Revision loop described: "The sponsor and PM revise the Intent Brief. This is not a failure — it means the intent was not yet clear enough to build on." |
| Engineering Team Structure Guide — Section 2.1 | Director of Engineering chairs the gate; has authority over product area |
| Engineering Team Structure Guide — Section 3.1 | Director responsibilities: "Owns product area roadmap execution" |
| Clarity of Intent — Roles and Responsibilities Summary | Stage 1 column: Sponsor writes, PM co-authors, TL reviews for feasibility, EM attends |

---

## P-005: Strategic Prioritization Process

### 1. Process ID and Name

**ID**: P-005
**Name**: Strategic Prioritization Process

### 2. Purpose

Compare competing projects against company OKRs to determine sequencing and resource allocation at the quarterly planning cycle. This process ensures that engineering capacity is allocated to the highest-leverage initiatives and that no project enters the pipeline without a capacity allocation. It operates upstream of P-001 — it determines which Intent Briefs get written and in what order.

### 3. Derived From

- **Clarity of Intent** — Stage 1: Strategic context requirement (Question 3 presumes that OKRs and priorities exist; this process creates the ranked priority list)
- **Engineering Team Structure Guide** — Section 3.1: VP of Engineering ("Owns delivery accountability for their domain or region; manages headcount planning and engineering budget"), Director of Engineering ("Owns product area roadmap execution")
- **Engineering Team Structure Guide** — Section 8: Product and Program Management Structure (GPM role in portfolio management)

### 4. Primary Owner Agent

**engineering-manager** — Specifically at GPM + Director + VP scope. The VP of Engineering has final authority on sequencing decisions. The Director scores and ranks projects within their domain. The GPM (product-manager agent scope) leads the product side.

### 5. Supporting Agents

| Agent | Role in This Process |
|-------|---------------------|
| product-manager | GPM compiles candidate projects and their OKR linkages. Provides the product perspective on strategic urgency and market context. |
| technical-program-manager | Provides the program portfolio view — cross-project dependencies, resource conflicts, and timeline interactions. |

### 6. Stages/Steps

| Step | Action | Owner | Detail |
|------|--------|-------|--------|
| 1 | **Candidate compilation** | product-manager (GPM) | GPM compiles all candidate projects for the upcoming quarter. Each candidate includes: (a) project name and one-sentence description, (b) OKR linkage (which Objective and Key Result it supports), (c) estimated engineering effort (T-shirt size or story points), (d) requesting Sponsor. |
| 2 | **Scoring** | engineering-manager (VP + Directors) | VP and Directors score each project on four dimensions: (a) **OKR impact weight**: How much does this project move the Key Result? (b) **Strategic urgency**: Is there a time-sensitive competitive or market pressure? (c) **Engineering feasibility**: Can this be delivered within the quarter given current architecture and team capability? (d) **Dependency risk**: How many cross-team or external dependencies does this project require? Scoring uses a standardized rubric (e.g., 1-5 scale per dimension). |
| 3 | **Ranking and sequencing** | engineering-manager (VP) | Projects are ranked by composite score. VP determines sequencing — which projects start first, which are deferred, which are declined. Resource allocation is proposed: which teams, how much capacity, for how long. |
| 4 | **Communication** | engineering-manager (VP + Directors) | Sequencing decisions are communicated to all PMs and EMs. Each PM receives: (a) their project's rank and start date, (b) allocated engineering capacity, (c) rationale for the sequencing decision. This becomes the basis for P-001 — PMs with approved, sequenced projects begin writing Intent Briefs. |

### 7. Inputs

| Input | Source | Required/Optional |
|-------|--------|-------------------|
| All pending Intent Brief candidates / project proposals | PMs, Sponsors, GPM | Required |
| Current company OKR documentation | OKR tracking system | Required |
| Engineering capacity forecasts | P-082 (Quarterly Capacity Planning); EMs | Required |
| Cross-project dependency information | technical-program-manager | Optional (improves sequencing quality) |

### 8. Outputs/Artifacts

| Output | Format | Destination |
|--------|--------|-------------|
| **Quarterly project priority ranking** | Ranked list with composite scores | VP, Directors, GPMs, PMs, EMs |
| **Resource allocation decisions** | Team-to-project mapping with capacity percentages | Directors, EMs |
| **Sequencing rationale** | Documented reasoning for each ranking/deferral/decline decision | All stakeholders; referenced in future Intent Briefs |

### 9. Gate/Checkpoint

**Quarterly OKR planning meeting** — This is the decision forum, not a pass/fail gate in the same sense as P-004. However, it functions as a checkpoint with the following requirements:

- Director + VP + GPM must attend (quorum requirement)
- Every project on the proposed roadmap must trace to at least one active OKR
- No project is approved to start without a named capacity allocation
- Decisions are recorded and distributed within 48 hours

### 10. Success Criteria

| Criterion | Measurement |
|-----------|-------------|
| Every project on the roadmap traces to at least one OKR | 100% OKR linkage in the ranked list |
| No project starts without a capacity allocation | Every approved project has a team and capacity percentage assigned |
| Prioritization decisions are documented and communicated to all affected EMs | Communication sent within 48 hours of planning meeting; all EMs acknowledge receipt |
| Sequencing rationale is available for reference | Any PM or EM can access the documented rationale for their project's ranking |

### 11. Dependencies

| Direction | Process | Nature |
|-----------|---------|--------|
| **Depends on** | P-082 (Quarterly Capacity Planning) | Capacity data is required for resource allocation decisions |
| **Depends on** | Company OKR cycle | OKRs must be set before projects can be prioritized against them |
| **Depended on by** | P-001 (Intent Articulation) | Approved, sequenced projects trigger Intent Brief authoring |
| **Depended on by** | P-006 (Technology Vision Alignment) | Strategic priorities feed into technology investment decisions |

### 12. Traceability

| Trace | Reference |
|-------|-----------|
| Clarity of Intent — Stage 1, Question 3 | The strategic context requirement presumes a prioritization process exists: "Why are we doing this instead of something else?" |
| Clarity of Intent — Stage 1, Good example | "It is the highest-leverage initiative on the mobile tribe's roadmap based on funnel analysis" — implies a ranked comparison |
| Engineering Team Structure Guide — Section 3.1: VP of Engineering | "Owns delivery accountability for their domain"; "Manages headcount planning and engineering budget" |
| Engineering Team Structure Guide — Section 3.1: Director of Engineering | "Owns product area roadmap execution" |
| Engineering Team Structure Guide — Section 1: Key principles | "Quarterly OKRs for goal alignment top-to-bottom" |

---

## P-006: Technology Vision Alignment Process

### 1. Process ID and Name

**ID**: P-006
**Name**: Technology Vision Alignment Process

### 2. Purpose

Annual review of technology strategy against company direction by the CTO and VPs. This process ensures that multi-year architectural investments align with where the company is going, not just where it is today. It operates at a longer time horizon than P-005 (quarterly prioritization) and produces architectural mandates that constrain and guide all downstream technical decisions.

### 3. Derived From

- **Engineering Team Structure Guide** — Section 3.1: CTO responsibilities ("Sets the technology vision and architecture strategy for the entire organization"; "Owns technical risk and communicates it at board level"; "Drives R&D direction")
- **Engineering Team Structure Guide** — Section 2.1: Organizational Hierarchy — Layer 1 (CTO) and Layer 2 (VP) responsibilities
- **Engineering Team Structure Guide** — Section 3.1: Distinguished Engineer ("company-wide" scope)
- **Clarity of Intent** — Stage 1, Strategic context requirement (implies a stable technology vision exists for projects to reference)

### 4. Primary Owner Agent

**engineering-manager** — Specifically at CTO scope. The CTO owns the technology vision and chairs the annual review.

### 5. Supporting Agents

| Agent | Role in This Process |
|-------|---------------------|
| staff-principal-engineer | Distinguished Engineers (L8) and Principal Engineers (L7) review the current technology portfolio, identify architectural gaps, and validate proposed investment decisions. Their cross-org scope makes them uniquely positioned to assess technology alignment. |
| engineering-manager (VPs) | VPs present domain-level technology gaps and opportunities from their respective areas. They provide the ground-truth view of what is working and what is not. |

### 6. Stages/Steps

| Step | Action | Owner | Detail |
|------|--------|-------|--------|
| 1 | **Technology portfolio review** | engineering-manager (CTO) + staff-principal-engineer (Distinguished Engineers) | CTO and Distinguished Engineers review the current technology portfolio against the company's 3-year strategic plan. Assessment covers: (a) current architecture strengths and liabilities, (b) technology bets that are paying off vs. those that are not, (c) emerging technology opportunities relevant to the company's direction, (d) technical debt that threatens strategic goals. |
| 2 | **Domain-level gap analysis** | engineering-manager (VPs) | Each VP presents their domain's technology gaps and opportunities: (a) what architectural capabilities are missing for their roadmap, (b) what technology investments are needed in the next 12-24 months, (c) what cross-domain technology alignment issues exist (e.g., conflicting platform choices, duplicated infrastructure). |
| 3 | **Investment decision ratification** | engineering-manager (CTO) | CTO ratifies or defers major architectural investment decisions: (a) new platform adoptions, (b) technology sunset / migration decisions, (c) build vs. buy decisions at strategic scale, (d) cross-cutting architectural mandates (e.g., "all new services must use event-driven architecture"). Each decision includes a rationale, an owner VP, and a timeline. |
| 4 | **Vision document update and cascade** | engineering-manager (CTO) + staff-principal-engineer | The Technology Vision document is updated with: (a) ratified investment decisions, (b) architectural mandates and their rationale, (c) technology roadmap for the next 12-24 months. The updated document is cascaded to VP and Director levels. Distinguished and Principal Engineers are responsible for representing the vision within their scope of influence. |

### 7. Inputs

| Input | Source | Required/Optional |
|-------|--------|-------------------|
| Company 3-year strategic plan | CEO / Board / executive leadership | Required |
| Current architecture portfolio | staff-principal-engineer; infra-engineer | Required |
| VP technology reports (domain-level) | engineering-manager (VPs) | Required |
| Industry technology trends | staff-principal-engineer; external research | Optional |
| Technical debt inventory | software-engineer (Tech Leads); sre | Optional (improves gap analysis quality) |

### 8. Outputs/Artifacts

| Output | Format | Destination |
|--------|--------|-------------|
| **Updated Technology Vision document** | Strategic document covering architecture direction, mandates, and 12-24 month technology roadmap | All VPs, Directors, Principal/Distinguished Engineers |
| **Major investment decisions** | Decision records with rationale, owner VP, and timeline | VP-level and above; referenced in P-005 prioritization |
| **Architectural mandates** | Documented constraints that apply to all new technical decisions | All engineering teams; enforced through P-007 (Deliverable Decomposition) and technical design reviews |

### 9. Gate/Checkpoint

**Annual CTO review board** — This functions as the formal checkpoint:

- CTO chairs; all VPs attend
- Distinguished/Principal Engineers participate as technical advisors
- Each major investment decision is ratified or explicitly deferred with a rationale
- The updated Technology Vision document is approved before cascade

### 10. Success Criteria

| Criterion | Measurement |
|-----------|-------------|
| All major technology investments trace to business outcomes | Every investment decision in the vision document references a business goal or strategic initiative |
| Architectural mandates are documented and communicated before they affect squad work | Mandates published and cascaded to Director level within 2 weeks of the review board |
| Distinguished/Principal Engineers can represent the vision | Each Distinguished/Principal Engineer can articulate the key technology decisions and their rationale |
| Vision document is updated annually | Document has a current-year version; no version gap > 12 months |

### 11. Dependencies

| Direction | Process | Nature |
|-----------|---------|--------|
| **Depends on** | P-005 (Strategic Prioritization) | Strategic priorities feed into technology investment decisions |
| **Depends on** | Company strategic planning cycle | The 3-year plan must exist for technology alignment |
| **Depended on by** | P-001 (Intent Articulation) | The Technology Vision constrains what Intent Briefs can propose (e.g., mandated platform choices) |
| **Depended on by** | P-005 (Strategic Prioritization) — bidirectional | Technology vision decisions influence which projects are strategically important |
| **Depended on by** | Technical design review processes | Architectural mandates from this process are enforced during design reviews |

### 12. Traceability

| Trace | Reference |
|-------|-----------|
| Engineering Team Structure Guide — Section 3.1: CTO | "Sets the technology vision and architecture strategy for the entire organization" |
| Engineering Team Structure Guide — Section 3.1: CTO | "Owns technical risk and communicates it at board level" |
| Engineering Team Structure Guide — Section 3.1: CTO | "Drives R&D direction; evaluates build vs. buy decisions at strategic scale" |
| Engineering Team Structure Guide — Section 3.1: VP of Engineering | "Sets cross-org engineering standards and architectural guardrails" |
| Engineering Team Structure Guide — Section 2.3: IC Track | Distinguished Engineer (L8) scope = VP scope; Fellow (L9) scope = CTO scope |
| Engineering Team Structure Guide — Section 1: Key principles | "Staff+ engineers lead by influence, not authority. Give them strategic mandates or they leave." |
| Clarity of Intent — Stage 1, Question 3 | Strategic context requirement implies a coherent technology vision exists for projects to align against |

---

## Cross-Process Dependency Map

```
                    Company OKR Cycle
                          │
                          ▼
    ┌──────────────────────────────────────────┐
    │  P-005: Strategic Prioritization         │◄──── P-082 (Capacity Planning)
    │  (Quarterly; VP + Director + GPM)        │
    └──────────────┬───────────────────────────┘
                   │ Approved projects
                   │ trigger Intent Briefs
                   ▼
    ┌──────────────────────────────────────────┐
    │  P-001: Intent Articulation              │
    │  (PM + Sponsor; 1-3 days)                │
    │                                          │
    │  Concurrent sub-processes:               │
    │  ├── P-002: OKR Alignment Verification   │
    │  └── P-003: Boundary Definition          │
    └──────────────┬───────────────────────────┘
                   │ Intent Brief submitted
                   ▼
    ┌──────────────────────────────────────────┐
    │  P-004: Intent Review Gate               │
    │  (Director chairs; 30 min / 48h async)   │
    │                                          │
    │  Pass → Locked Intent Brief → Stage 2    │
    │  Fail → Revise → Re-submit               │
    └──────────────┬───────────────────────────┘
                   │
                   ▼
              Stage 2: Scope Contract (P-007+)


    ┌──────────────────────────────────────────┐
    │  P-006: Technology Vision Alignment      │
    │  (Annual; CTO + VPs + Distinguished Eng) │
    │                                          │
    │  Feeds: P-005 (priorities)               │
    │  Constrains: P-001 (technical mandates)  │
    └──────────────────────────────────────────┘
```

### Process Execution Ordering

| Process | Cadence | Prerequisite |
|---------|---------|--------------|
| P-006 | Annual | Company 3-year strategic plan |
| P-005 | Quarterly | Company OKR cycle; P-082 capacity data |
| P-001 | Per-project | P-005 approval (or ad-hoc Sponsor trigger) |
| P-002 | Per-project (concurrent with P-001) | P-001 in progress |
| P-003 | Per-project (concurrent with P-001) | P-001 in progress |
| P-004 | Per-project | P-001, P-002, P-003 complete |

---

## Appendix A: Artifact Summary

| Artifact | Produced By | Consumed By | Format | Max Length |
|----------|------------|-------------|--------|------------|
| Intent Brief | P-001 | P-002, P-003, P-004, P-007+ | Structured document (5 questions answered) | 2 pages |
| OKR reference (within Intent Brief) | P-002 | P-004 (pass criterion) | Section within Intent Brief | N/A |
| Exclusion list (within Intent Brief) | P-003 | P-004 (pass criterion), P-009 (Scope Contract) | Section within Intent Brief | N/A |
| Gate decision record | P-004 | P-007+ (unlocks Stage 2) | PASS/FAIL with rationale | N/A |
| Locked Intent Brief | P-004 (on PASS) | All Stage 2 processes | Versioned, immutable document | 2 pages |
| Quarterly priority ranking | P-005 | P-001 (triggers Intent Briefs) | Ranked list with scores | N/A |
| Resource allocation decisions | P-005 | EMs, Directors | Team-to-project mapping | N/A |
| Technology Vision document | P-006 | P-001, P-005, design reviews | Strategic document | N/A |
| Architectural mandates | P-006 | All engineering teams | Documented constraints | N/A |

---

## Appendix B: Risk Register

| Process | Risk | Severity | Mitigation |
|---------|------|----------|------------|
| P-001 | All downstream processes blocked if Intent Brief is absent or ambiguous | HIGH | Gate P-004 enforces quality; revision loop prevents weak briefs from progressing |
| P-002 | Projects passing the gate without real OKR alignment waste engineering capacity | MEDIUM | Director confirmation at P-004; causal (not thematic) linkage required |
| P-003 | Missing exclusions are the primary source of scope drift | MEDIUM | Minimum 1 exclusion enforced at P-004; carried forward to Scope Contract |
| P-004 | Passing a weak Intent Brief propagates ambiguity through all downstream stages | HIGH | Binary pass criteria; all 5 criteria must pass; no abstentions allowed |
| P-005 | Poor prioritization causes thrashing and diluted focus | MEDIUM | Standardized scoring rubric; documented rationale; quarterly cadence |
| P-006 | Misaligned technology vision creates multi-year technical debt | MEDIUM | Annual review cadence; Distinguished/Principal Engineer participation; cascade mechanism |

---

## Cross-Category Dependencies

### Dependencies FROM Other Categories (Inputs)

| Source Process | Source Category | Consuming Process | Nature |
|---------------|----------------|-------------------|--------|
| P-082 (Quarterly Capacity Planning) | Cat 15: Capacity & Resource | P-005 (Strategic Prioritization) | Capacity data required for resource allocation decisions |

### Dependencies TO Other Categories (Outputs)

| Providing Process | Consuming Process | Target Category | Nature |
|------------------|-------------------|-----------------|--------|
| P-004 (Intent Review Gate) | P-007+ (Deliverable Decomposition) | Cat 2: Scope & Contract | Locked Intent Brief enables Scope Contract authoring |
| P-004 (Intent Review Gate) | P-023 (Intent Trace Validation) | Cat 4: Sprint & Delivery | Intent Brief needed for intent trace in Sprint Kickoff Brief |
| P-005 (Strategic Prioritization) | P-078 (OKR Cascade Communication) | Cat 14: Communication | Strategic priorities feed OKR cascade |
| P-005 (Strategic Prioritization) | P-082 (Quarterly Capacity Planning) | Cat 15: Capacity & Resource | Strategic priorities define capacity demand |
| P-006 (Technology Vision Alignment) | P-047 (CARB) | Cat 7: Infrastructure & Platform | Technology vision provides architectural guardrails |
| P-006 (Technology Vision Alignment) | P-088 (Architecture Pattern Change) | Cat 16: Technical Excellence | Technology vision guides pattern decisions |

## Agent Assignments Summary

| Process | Primary Owner | Supporting Agents |
|---------|--------------|-------------------|
| P-001: Intent Articulation | product-manager | engineering-manager |
| P-002: OKR Alignment Verification | product-manager | engineering-manager |
| P-003: Boundary Definition | product-manager | engineering-manager |
| P-004: Intent Review Gate | engineering-manager | product-manager, engineering-manager (Tribe Leads) |
| P-005: Strategic Prioritization | engineering-manager (VP/Director/GPM) | product-manager, technical-program-manager |
| P-006: Technology Vision Alignment | engineering-manager (CTO) | staff-principal-engineer, engineering-manager (VPs) |
