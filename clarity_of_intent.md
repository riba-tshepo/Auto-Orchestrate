# Clarity of Intent Process

**A structured method for translating project vision into aligned, executable work across engineering teams.**

---

## Why This Process Exists

Every project starts with someone's intent — a business outcome, a user problem, a technical improvement. Between that intent and the first line of code, meaning gets lost. Product and engineering interpret goals differently. Scope drifts because "done" was never defined. Dependencies between squads surface weeks too late. Leadership's quarterly objectives arrive at sprint planning as vague epics that nobody can act on.

This process exists to close those gaps. It works by forcing intent through four progressively concrete stages — each one producing a specific artifact that the next stage consumes. Nothing moves forward until the current stage's artifact is reviewed and accepted by the people who need to act on it.

The process is designed for organizations with 8+ squads and 80+ engineers, where ambient understanding breaks down and written clarity becomes the only reliable coordination mechanism.

---

## The Four Stages

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   STAGE 1              STAGE 2              STAGE 3              STAGE 4          │
│   Intent Frame    →    Scope Contract   →   Dependency Map   →   Sprint Bridge    │
│                                                                     │
│   "Why are we         "What exactly       "Who else is          "What does this    │
│    doing this?"        are we building     involved and          look like in a     │
│                        and what does       what do we            2-week sprint?"    │
│                        done look like?"    need from them?"                         │
│                                                                     │
│   Owner: Sponsor +    Owner: PM + TL      Owner: TPM + TL       Owner: EM + TL    │
│   PM                                                                               │
│                                                                     │
│   Artifact:           Artifact:           Artifact:             Artifact:          │
│   Intent Brief        Scope Contract      Dependency Charter    Sprint Kickoff     │
│                                                                  Brief             │
│                                                                     │
│   Gate: Intent        Gate: Scope         Gate: Dependency      Gate: Sprint       │
│   Review              Lock                Acceptance            Readiness          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

Each stage has one artifact and one gate. The gate is a short, structured review where specific people confirm they understand and accept what was produced. A project cannot advance to the next stage without passing the gate.

---

## Stage 1: Intent Frame

**Purpose:** Capture *why* this project exists and *what outcome* it serves — before anyone discusses solutions.

**Owner:** Project Sponsor (typically a Director, VP, or GPM) together with the lead Product Manager.

**Time to complete:** 1–3 days.

### What happens in this stage

The sponsor and PM sit down and write a single document — the Intent Brief — that answers five questions. These questions are deliberately non-technical. The point is to establish business intent before engineering thinking begins.

### The Intent Brief

The Intent Brief is the foundational artifact. It should be no longer than two pages. If it takes more than two pages to explain why a project exists, the intent is not yet clear enough.

**The five questions the Intent Brief must answer:**

#### 1. What outcome are we trying to achieve?

State the desired end-state in measurable terms. This is not a feature description — it is a change in a metric, a user behavior, or a business condition.

- **Good:** "Reduce median checkout abandonment rate from 34% to 20% within 90 days of launch."
- **Bad:** "Improve the checkout experience."
- **Bad:** "Build a new checkout flow."

The outcome must be something the team can observe and measure after the project ships. If you cannot describe how you would know the project succeeded, the intent is not clear.

#### 2. Who specifically benefits and how?

Name the user segment, internal team, or customer cohort. Describe the before and after from their perspective.

- **Good:** "Mobile users on Android who currently abandon checkout at the payment step because the form requires 14 fields. After this project, they complete payment in 4 taps using saved payment methods."
- **Bad:** "Our users."

#### 3. What is the strategic context?

Connect this project to a company OKR, a quarterly theme, or a competitive pressure. This answers the question every engineer will eventually ask: "Why are we doing this instead of something else?"

- **Good:** "This directly supports Q3 OKR: 'Increase mobile conversion rate by 15%.' It is the highest-leverage initiative on the mobile tribe's roadmap based on funnel analysis from March 2026."
- **Bad:** "Leadership wants this."

#### 4. What are the boundaries of this project?

State what this project is *not*. Explicit exclusions prevent scope drift more effectively than detailed inclusions.

- **Good:** "This project does NOT include: redesigning the product detail page, adding new payment providers, changing the pricing model, or supporting desktop — those are separate initiatives."
- **Bad:** No boundaries stated.

#### 5. What happens if we don't do this?

Describe the cost of inaction. This forces the sponsor to articulate urgency and helps the team calibrate how much risk is acceptable in the solution.

- **Good:** "Checkout abandonment continues at 34%. At current traffic, that represents approximately $2.1M in unrealized quarterly revenue. Competitors with streamlined mobile checkout (specifically X and Y) are gaining market share in our core demographic."
- **Bad:** "We fall behind."

### Gate: Intent Review

**Participants:** Sponsor, lead PM, Engineering Director for the affected area, relevant Tribe Lead(s).

**Format:** 30-minute meeting or async review with a 48-hour response window.

**Pass criteria:**
- All five questions are answered with specifics — no vague or aspirational language
- The outcome is measurable and has a timeline
- At least one explicit boundary (what this is NOT) is stated
- The strategic context references a real OKR or documented priority
- All reviewers confirm they could explain this project's purpose to their teams

**If the gate does not pass:** The sponsor and PM revise the Intent Brief. This is not a failure — it means the intent was not yet clear enough to build on. Better to discover this now than after two sprints of misaligned work.

---

## Stage 2: Scope Contract

**Purpose:** Translate the Intent Brief into a concrete description of *what will be built*, *what done looks like*, and *what is explicitly excluded*.

**Owner:** Product Manager and Tech Lead for the primary squad, with input from Staff/Principal Engineers for cross-team technical decisions.

**Time to complete:** 3–5 days.

**Prerequisite:** Intent Review gate passed.

### What happens in this stage

The PM and TL take the Intent Brief and produce a Scope Contract — a document that both product and engineering sign off on. The Scope Contract is the single source of truth for what "done" means. When scope disputes arise later (and they will), this document is the referee.

### The Scope Contract

The Scope Contract has six sections. It should be 3–5 pages. If it's shorter, it's probably missing critical detail. If it's longer, it's probably including solution design that belongs in a technical design document, not the scope.

#### Section 1: Outcome Restatement

Copy the outcome statement from the Intent Brief verbatim. This ensures the Scope Contract stays anchored to the original intent. If the PM or TL feels the outcome needs modification based on what they've learned, they must go back to the sponsor and update the Intent Brief first — not silently adjust the scope.

#### Section 2: Deliverables

List every distinct deliverable the project will produce. Each deliverable gets a one-sentence description and a clear owner (which squad or role is responsible).

| # | Deliverable | Description | Owner |
|---|------------|-------------|-------|
| 1 | Saved payment method API | Backend API enabling retrieval and selection of stored payment methods | Payments Squad |
| 2 | Mobile checkout UI redesign | New 3-step checkout flow for Android and iOS | Mobile Squad |
| 3 | Payment tokenization integration | Integration with payment provider's tokenization SDK | Payments Squad |
| 4 | A/B test framework setup | Feature flags and experiment configuration for gradual rollout | Platform Squad |
| 5 | Analytics event instrumentation | Checkout funnel events for measuring abandonment reduction | Mobile Squad + Data Eng |

#### Section 3: Definition of Done

For each deliverable, define the acceptance criteria — the specific, testable conditions that must be true for the deliverable to be considered complete. Use the format "It is done when..."

| Deliverable | Done When |
|------------|-----------|
| Saved payment method API | API returns stored payment methods in < 200ms P95; handles 0 stored methods gracefully; passes AppSec threat model review; OpenAPI spec published |
| Mobile checkout UI redesign | 3-step flow implemented; accessibility audit passed (WCAG 2.1 AA); design review approved by UX lead; renders correctly on Android 12+ and iOS 16+ |
| Payment tokenization | Tokens generated and validated end-to-end in staging; PCI compliance review passed; fallback to manual entry works when tokenization fails |
| A/B test framework | Feature flags configured; 5%/25%/50%/100% rollout stages defined; kill switch tested and documented |
| Analytics instrumentation | All 7 funnel events firing in staging; data validated in analytics dashboard; data eng confirms events match schema |

**The rule:** If a deliverable does not have a Definition of Done, it is not in scope. Undone definitions are the primary source of scope disputes. Write them now, not after development starts.

#### Section 4: Explicit Exclusions

Carry forward the boundaries from the Intent Brief and add any new exclusions discovered during scoping. Each exclusion should state *why* it is excluded and *where* it will be addressed (if at all).

| Exclusion | Reason | Future Home |
|-----------|--------|-------------|
| Desktop checkout redesign | Separate initiative; different user behavior patterns | Q4 roadmap candidate |
| New payment provider integration | Current provider supports tokenization; adding providers is a separate workstream | Payments team backlog |
| Guest checkout flow changes | Guest checkout abandonment is a different problem with different root causes | Requires separate Intent Brief |

#### Section 5: Success Metrics

Define 2–4 metrics that the team will track to determine whether the project achieved its intended outcome. These must trace directly back to the outcome in the Intent Brief.

| Metric | Baseline | Target | Measurement Method | Timeline |
|--------|----------|--------|-------------------|----------|
| Mobile checkout abandonment rate | 34% | 20% | Analytics funnel dashboard | 90 days post-launch |
| Median checkout completion time (mobile) | 4 min 12 sec | < 1 min 30 sec | Analytics event timestamps | 30 days post-launch |
| Saved payment method adoption | 0% | 40% of returning users | Backend API usage logs | 60 days post-launch |

#### Section 6: Assumptions and Risks

List assumptions the scope depends on and risks that could invalidate the plan. Each risk gets a severity and a mitigation owner.

| Item | Type | Severity | Mitigation | Owner |
|------|------|----------|------------|-------|
| Payment provider supports tokenization in all target markets | Assumption | HIGH if false | Verify with provider before development begins | PM |
| Mobile team has capacity in Q3 | Assumption | HIGH if false | Confirm with Mobile EM during dependency mapping | PM + EM |
| Tokenization adds latency to checkout flow | Risk | MEDIUM | Performance budget: tokenization must complete in < 500ms; load test before launch | TL |
| PCI compliance review takes longer than 2 weeks | Risk | MEDIUM | Start review in parallel with development, not after | AppSec + PM |

### Gate: Scope Lock

**Participants:** PM, TL, Engineering Director, all squad EMs whose teams have deliverables, AppSec representative (if security-relevant), Staff/Principal Engineer (if cross-team architecture is involved).

**Format:** 60-minute meeting. The PM presents the Scope Contract. Each section is reviewed. Disagreements are resolved in the room or assigned a 48-hour resolution owner.

**Pass criteria:**
- Every deliverable has a named owner squad
- Every deliverable has a written Definition of Done with testable criteria
- Exclusions are explicit and acknowledged by all parties
- Success metrics trace to the Intent Brief outcome
- All assumptions rated HIGH have been validated or have a validation plan with a deadline
- Every participant confirms: "My team understands what we are responsible for and what done looks like"

**After Scope Lock:** The Scope Contract is versioned. Any subsequent scope change requires a formal Scope Change Request (see the Change Control section below). The PM is the gatekeeper for scope changes — no one else can modify the Scope Contract.

---

## Stage 3: Dependency Map

**Purpose:** Identify every cross-team dependency, external blocker, and shared resource constraint — and get explicit commitments from all parties *before* development begins.

**Owner:** Technical Program Manager (TPM) and the primary squad's Tech Lead.

**Time to complete:** 3–5 days.

**Prerequisite:** Scope Lock gate passed.

### What happens in this stage

The TPM and TL take the Scope Contract's deliverables and owner assignments and trace every connection between teams, every shared service, every external system, and every person or approval process that could block progress. The output is a Dependency Charter — a document that makes invisible dependencies visible and assigns each one an owner who is accountable for its resolution.

### The Dependency Charter

#### Section 1: Dependency Register

Every dependency gets a row. No dependency is too small to document if it could block a sprint.

| ID | Dependent Team | Depends On | What Is Needed | By When | Status | Owner | Escalation Path |
|----|---------------|------------|----------------|---------|--------|-------|-----------------|
| D1 | Mobile Squad | Payments Squad | Saved payment method API (endpoints and contract) | Sprint 2 start | Not started | Payments TL | Payments EM → Director |
| D2 | Mobile Squad | Platform Squad | Feature flag configuration for A/B test | Sprint 3 start | In progress | Platform EM | Platform Director |
| D3 | Payments Squad | External: Payment Provider | Tokenization SDK access and sandbox credentials | Before Sprint 1 | Blocked — awaiting provider response | PM | PM → VP Product |
| D4 | Mobile Squad | Data Engineering | Analytics event schema review and approval | Sprint 2 end | Not started | Data Eng TL | Data Director |
| D5 | All squads | AppSec | Threat model review and PCI pre-assessment | Sprint 1 end | Not started | AppSec Lead | CISO |

#### Section 2: Shared Resource Conflicts

Identify any shared resources (people, environments, infrastructure) that multiple deliverables compete for.

| Resource | Competing Demands | Resolution |
|----------|------------------|------------|
| Staging environment | Mobile Squad needs staging for UI testing; Payments Squad needs staging for API integration testing | Provision a second staging namespace on shared cluster — Platform Squad to action by Sprint 1, Day 3 |
| AppSec Engineer (single person) | Threat model for this project + ongoing CVE triage for other teams | Timebox threat model to 3 days in Sprint 1; AppSec Lead to backfill CVE triage |

#### Section 3: Critical Path

Identify the sequence of dependencies that determines the project's minimum timeline. If any item on the critical path slips, the entire project slips.

```
External: Payment provider SDK access (D3)
  → Payments Squad: Build tokenization integration (Deliverable 3)
    → Payments Squad: Build saved payment API (Deliverable 1)
      → Mobile Squad: Integrate API into checkout flow (Deliverable 2)
        → All: A/B test rollout (Deliverable 4)
          → Data Eng: Validate analytics events (Deliverable 5)
```

The critical path tells every team what matters most and what they cannot afford to delay. Items not on the critical path have float — they can slip without affecting the overall timeline.

#### Section 4: Communication Protocol

Define how dependency status will be tracked and communicated throughout the project.

| Mechanism | Cadence | Participants | Purpose |
|-----------|---------|-------------|---------|
| Dependency standup | Twice weekly, 15 min | TLs from all involved squads + TPM | Surface blockers on dependency items; update statuses |
| RAID log update | Weekly | TPM updates; reviewed by Director | Track risks, assumptions, issues, dependencies at project level |
| Escalation trigger | As needed | EM → Director → VP (defined path per dependency) | Any dependency blocked for > 48 hours with no resolution path |

### Gate: Dependency Acceptance

**Participants:** TPM, all squad TLs and EMs involved, Engineering Director, PM.

**Format:** 45-minute meeting. TPM walks through the Dependency Charter. Each dependency owner verbally confirms their commitment and timeline.

**Pass criteria:**
- Every dependency has a named owner and a "needed by" date
- Every dependency owner has verbally confirmed they can deliver by the stated date
- The critical path is documented and understood by all parties
- At least one escalation path is defined for blocked dependencies
- No HIGH-severity blocker is unresolved without a resolution plan and deadline
- Communication protocol is agreed upon

**If the gate does not pass:** Resolve the gaps before proceeding to Sprint Bridge. Starting development with unresolved dependencies is the most expensive form of rework.

---

## Stage 4: Sprint Bridge

**Purpose:** Translate the Scope Contract and Dependency Charter into the first sprint's concrete work — user stories, tasks, acceptance criteria — so that every engineer knows what they are building in the first two weeks.

**Owner:** Engineering Manager and Tech Lead for each involved squad.

**Time to complete:** 1–2 days (typically done as part of the first sprint planning).

**Prerequisite:** Dependency Acceptance gate passed.

### What happens in this stage

The EM and TL take the Scope Contract deliverables and break down the first sprint's work into stories and tasks. The Sprint Kickoff Brief connects every story back to the Scope Contract deliverable it serves, so engineers can always trace their daily work to the project's intent.

### The Sprint Kickoff Brief

Each squad produces its own Sprint Kickoff Brief for the first sprint. The brief is a one-page document that the EM presents at the sprint planning meeting.

#### Section 1: Sprint Goal

One sentence. What will be true at the end of this sprint that is not true today?

- **Good:** "By the end of Sprint 1, the tokenization SDK is integrated in the staging environment and the threat model review is complete."
- **Bad:** "Make progress on checkout."

#### Section 2: Intent Trace

A three-line trace from the sprint goal to the project intent, so every engineer can see the connection.

```
Project Intent:   Reduce mobile checkout abandonment from 34% to 20%
Scope Deliverable: Payment tokenization integration (Deliverable 3)
Sprint Goal:      Tokenization SDK integrated in staging; threat model complete
```

#### Section 3: Stories and Acceptance Criteria

Each story in the sprint backlog gets acceptance criteria written in "Given / When / Then" format or as a checklist of testable conditions.

| Story | Acceptance Criteria | Points | Assignee |
|-------|-------------------|--------|----------|
| Integrate tokenization SDK into payment service | SDK initializes on service startup; token generated for test card in sandbox; error handling for SDK timeout (> 500ms); unit tests cover happy path + 3 error cases | 5 | Engineer A |
| Conduct threat model for tokenization flow | Threat model document complete using STRIDE methodology; reviewed by AppSec; no CRITICAL findings unresolved; findings logged in security backlog | 3 | Security Champion + AppSec |
| Set up staging namespace for payments testing | Namespace provisioned; CI/CD deploys to namespace; environment variables configured; smoke test passes | 2 | Platform Engineer B |

#### Section 4: Dependencies Due This Sprint

Pull from the Dependency Charter — which dependencies must be resolved *during* this sprint for the sprint goal to be achievable?

| Dependency | Needed By | Current Status | Contingency if Late |
|------------|-----------|---------------|---------------------|
| Payment provider sandbox credentials (D3) | Sprint 1, Day 2 | Provider confirmed delivery by Monday | Use mock SDK responses; flag to PM for escalation if not received by Day 3 |
| AppSec availability for threat model (D5) | Sprint 1, Day 5–8 | AppSec Lead confirmed slot on Thursday | If postponed, defer threat model to Sprint 2 and adjust scope accordingly |

#### Section 5: Definition of Done (Sprint Level)

Restate the team's standard Definition of Done so it is visible in the kickoff. Every story must meet all of these criteria to be counted as complete.

- Code reviewed by at least one peer
- Automated tests written and passing in CI
- SAST scan clean (no new critical or high findings)
- Documentation updated (API docs, runbook, or README as applicable)
- Acceptance criteria verified by PM or QA
- Deployed to staging and smoke-tested

### Gate: Sprint Readiness

**Participants:** EM, TL, PM, all squad engineers.

**Format:** This is the sprint planning meeting itself — but with a structured readiness check at the start.

**Pass criteria (readiness check before planning begins):**
- Sprint goal is stated and connects to a Scope Contract deliverable
- Intent trace is visible (project intent → deliverable → sprint goal)
- All stories have written acceptance criteria
- All dependencies due this sprint have a current status and a contingency
- Every engineer can answer: "What am I building, why does it matter, and how will I know it's done?"

---

## Change Control: When Scope Needs to Change

Scope will change. The goal of this process is not to prevent change — it is to make change visible, deliberate, and traceable.

### Scope Change Request

Any team member can identify a scope change need. Only the PM can approve a change to the Scope Contract. All changes go through this process:

**Step 1 — Raise:** The person identifying the change writes a Scope Change Request with four fields.

| Field | Content |
|-------|---------|
| What is changing? | Specific deliverable(s) being added, removed, or modified |
| Why is it changing? | New information, technical discovery, market shift, or dependency failure |
| What is the impact? | Effect on timeline, other deliverables, dependencies, and success metrics |
| What is the recommendation? | Accept the change, reject it, or defer it to a future project |

**Step 2 — Assess:** PM and TL review the impact. If the change affects other squads, the TPM is consulted.

**Step 3 — Decide:** PM decides for changes within the existing scope boundary. Engineering Director decides for changes that expand the scope boundary or affect the timeline by more than one sprint.

**Step 4 — Update:** If approved, the Scope Contract is versioned (v1.1, v1.2, etc.) with the change documented. The PM communicates the change to all affected squads.

**The one rule:** No silent scope changes. If a deliverable is added, removed, or redefined without updating the Scope Contract, the process has failed and should be raised as a retrospective item.

---

## Roles and Responsibilities Summary

| Role | Stage 1: Intent Frame | Stage 2: Scope Contract | Stage 3: Dependency Map | Stage 4: Sprint Bridge |
|------|----------------------|------------------------|------------------------|----------------------|
| **Sponsor** | Writes Intent Brief with PM | Reviews and approves Scope Contract | Informed | Informed |
| **Product Manager** | Co-authors Intent Brief | Owns Scope Contract; defines deliverables and success metrics | Provides business context for dependency prioritization | Validates sprint goal traces to scope |
| **Tech Lead** | Reviews Intent Brief for feasibility signals | Co-authors Scope Contract; defines technical acceptance criteria | Co-owns Dependency Charter; identifies technical dependencies | Breaks deliverables into stories; writes acceptance criteria |
| **Engineering Manager** | Attends Intent Review | Reviews Scope Contract for capacity fit | Confirms team capacity for dependency commitments | Owns Sprint Kickoff Brief; runs sprint planning |
| **TPM** | — | — | Owns Dependency Charter; runs dependency standups | Reviews Sprint Kickoff Brief for cross-team alignment |
| **Staff/Principal Engineer** | — | Reviews cross-team architectural implications | Reviews critical path for technical risks | Available for technical design questions |
| **AppSec / Security Champion** | — | Reviews for security scope items | Confirms security review availability | Participates in threat modeling stories |
| **Squad Engineers** | — | — | — | Confirm they understand stories, acceptance criteria, and intent |

---

## Timing Guide

The entire process — from Intent Frame to Sprint Readiness — should take **8–12 working days** for a standard cross-team project. Rushing it creates the exact ambiguity problems the process is designed to prevent.

| Stage | Duration | Can Overlap With |
|-------|----------|-----------------|
| Stage 1: Intent Frame | 1–3 days | Nothing — this must come first |
| Stage 2: Scope Contract | 3–5 days | Can begin preliminary technical research during Stage 1 |
| Stage 3: Dependency Map | 3–5 days | Can begin during late Stage 2 once deliverables are identified |
| Stage 4: Sprint Bridge | 1–2 days | Typically done as part of first sprint planning |

For smaller projects (single squad, no cross-team dependencies), Stages 1 and 2 can be compressed into a single document and a single gate review. Stage 3 can be reduced to a checklist. Stage 4 remains the same.

---

## How to Know the Process Is Working

Track these signals at the quarterly retrospective. If the process is working, these should improve over time.

| Signal | How to Measure | Healthy State |
|--------|---------------|---------------|
| Scope changes per project | Count of Scope Change Requests filed after Scope Lock | Declining quarter-over-quarter; < 2 major changes per project |
| Late dependency discovery | Dependencies discovered after Sprint 1 that were not in the Dependency Charter | < 1 per project |
| Sprint goal completion rate | Percentage of sprints where the stated sprint goal was fully achieved | > 80% |
| Intent alignment | At any point, ask a random engineer on the project: "Why are we building this?" — can they answer in one sentence? | Yes, consistently |
| Time-to-first-sprint | Working days from project kickoff to first sprint start | 8–12 days; stable, not growing |

---

## Quick Reference: The Four Artifacts

| Artifact | Length | Owner | Answers | Lives In |
|----------|--------|-------|---------|----------|
| **Intent Brief** | 1–2 pages | Sponsor + PM | Why are we doing this? What outcome? What boundaries? | Confluence / Notion — project root |
| **Scope Contract** | 3–5 pages | PM + TL | What are we building? What does done look like? What is excluded? | Confluence / Notion — project root; versioned |
| **Dependency Charter** | 2–4 pages | TPM + TL | Who else is involved? What do we need from them and by when? | Confluence / Notion — project root; linked from RAID log |
| **Sprint Kickoff Brief** | 1 page per squad | EM + TL | What are we doing in this sprint and how does it connect to the project intent? | Team wiki or sprint planning doc |