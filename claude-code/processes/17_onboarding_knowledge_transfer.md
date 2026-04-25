# Technical Specification: Onboarding & Knowledge Transfer Processes (P-090 to P-093)

**Spec ID**: auto-orc-20260405-procderive-spec-17
**Stage**: 2
**Date**: 2026-04-05
**Session**: auto-orc-20260405-procderive
**Input -- Process Architecture**: `.orchestrate/auto-orc-20260405-procderive/stage-1/2026-04-05_process-architecture.md` (Category 17)
**Input -- Clarity of Intent**: `clarity_of_intent.md` (Four-stage intent-to-sprint process)
**Input -- Org Structure**: `Engineering_Team_Structure_Guide.md` (Role catalog, reporting lines, squad model)
**Spec Author**: spec-creator
**Status**: FINAL

> **Quick Reference**: A lightweight stub version is available at `processes/process_stubs/onboarding_stub.md`

---

## Table of Contents

1. [Specification Overview](#1-specification-overview)
2. [Process Summary Matrix](#2-process-summary-matrix)
3. [P-090: New Engineer Onboarding Process](#3-p-090-new-engineer-onboarding-process)
4. [P-091: New Project Onboarding Process](#4-p-091-new-project-onboarding-process)
5. [P-092: Knowledge Transfer Process](#5-p-092-knowledge-transfer-process)
6. [P-093: Technical Onboarding for Cross-Team Dependencies Process](#6-p-093-technical-onboarding-for-cross-team-dependencies-process)
7. [Dependency Graph](#7-dependency-graph)
8. [Traceability Matrix](#8-traceability-matrix)
9. [Acceptance Criteria Summary](#9-acceptance-criteria-summary)

---

## 1. Specification Overview

Category 17 defines four processes that govern how knowledge enters, moves within, and is preserved across the engineering organization. These processes address three distinct knowledge transfer scenarios:

1. **A person joins the organization** (P-090) -- new hire onboarding
2. **A team starts a new project** (P-091) -- project context distribution
3. **A person leaves a team or project** (P-092) -- departure knowledge capture
4. **Two teams begin a new dependency relationship** (P-093) -- cross-team technical context sharing

Together, these processes ensure that no engineer begins work without sufficient context and no critical knowledge is lost when people or project assignments change. They directly support the Clarity of Intent principle that "every engineer can answer: what am I building, why does it matter, and how will I know it's done?"

### 1.1 Design Principles

- **Context before code**: No engineer writes production code without documented project context (Intent Brief, Scope Contract, Sprint Kickoff Brief).
- **Bus factor mitigation**: No single engineer holds undocumented critical knowledge for any system.
- **Golden path first**: Environment setup uses self-service platform tooling (P-044) to minimize manual provisioning friction.
- **Measurable ramp-up**: Onboarding milestones are time-bound and observable (first PR in week 1, independent navigation by day 30).

---

## 2. Process Summary Matrix

| Process ID | Process Name | Primary Owner | Trigger | Cadence | Risk Level | Program |
|------------|-------------|---------------|---------|---------|------------|---------|
| P-090 | New Engineer Onboarding | engineering-manager | New hire start date | Per hire event | MEDIUM | Standalone (no process dependency) |
| P-091 | New Project Onboarding | engineering-manager | Dependency Acceptance Gate (P-019) passed | Per project | HIGH | Program 9 (blockedBy P-019) |
| P-092 | Knowledge Transfer | engineering-manager | Engineer departure, role change, or project rotation | Per departure/rotation event | HIGH | Standalone (event-driven) |
| P-093 | Technical Onboarding for Cross-Team Dependencies | technical-program-manager | New cross-team dependency identified at Stage 3 | Per dependency relationship | MEDIUM | Program 9 (blockedBy P-019) |

---

## 3. P-090: New Engineer Onboarding Process

### 3.1 Identity

| Field | Value |
|-------|-------|
| **Process ID** | P-090 |
| **Process Name** | New Engineer Onboarding Process |
| **Purpose** | Structured onboarding for new engineering hires covering access provisioning, team context, technical standards, and development environment setup. Target: new engineer can submit a PR in week 1. |
| **Derived From** | Tech Lead mentorship responsibilities (Engineering_Team_Structure_Guide Section 3); EM onboarding ownership (Engineering_Team_Structure_Guide Section 3); Platform golden path -- self-service environment setup (P-044) |

### 3.2 Ownership

| Role | Agent | Responsibility |
|------|-------|---------------|
| **Primary Owner** | engineering-manager | Creates onboarding plan; assigns buddy; conducts 30-day and 90-day check-ins; owns overall onboarding success |
| **Supporting** | software-engineer (Tech Lead) | Runs technical onboarding: codebase walkthrough, architecture overview, coding standards, PR review norms |
| **Supporting** | infra-engineer | Golden path templates reduce environment setup friction; self-service access provisioning via IDP |
| **Supporting** | technical-writer | Maintains onboarding documentation: setup guides, team wikis, glossaries |

### 3.3 Stages and Steps

#### Stage 1: Pre-Arrival Preparation (T-5 business days)

| Step | Owner | Action | Output |
|------|-------|--------|--------|
| 1.1 | EM | Create onboarding plan: access checklist, buddy assignment, 30-day milestones, meeting schedule | Onboarding plan document |
| 1.2 | EM | Assign onboarding buddy (senior IC on the same squad, not the Tech Lead) | Buddy assignment recorded |
| 1.3 | EM | Request access provisioning: source control, CI/CD, cloud accounts, communication tools, project management tools | Access request tickets created |
| 1.4 | Platform Engineer | Verify golden path templates are current and tested | Golden path readiness confirmed |

#### Stage 2: Week 1 -- Environment and Context

| Step | Owner | Action | Output |
|------|-------|--------|--------|
| 2.1 | EM | Welcome session: team intro, org structure overview, squad mission, current project context | Session completed; new engineer has team context |
| 2.2 | Platform Engineer / New Engineer | Environment setup via golden path (P-044): clone repos, run setup scripts, verify local build passes | Working development environment |
| 2.3 | Tech Lead | Technical onboarding session: codebase walkthrough, architecture overview (ADRs), coding standards, PR review norms, testing expectations | New engineer understands technical landscape |
| 2.4 | EM / Tech Lead | Provide current project context: Intent Brief, Scope Contract, Sprint Kickoff Brief for active project | New engineer has project "why" and "what" |
| 2.5 | Buddy | First small task assigned: well-scoped, low-risk change (bug fix or minor improvement) | Task assigned in sprint backlog |
| 2.6 | New Engineer + Buddy | PR submitted and reviewed by buddy; feedback loop established | First PR submitted |

#### Stage 3: Week 2-4 -- Integration and Contribution

| Step | Owner | Action | Output |
|------|-------|--------|--------|
| 3.1 | New Engineer | Participate in all squad ceremonies: standups, sprint planning, sprint review, retrospective | Active participation observed |
| 3.2 | Buddy | Ongoing pairing sessions on progressively complex tasks | Increasing contribution velocity |
| 3.3 | Tech Lead | Code review feedback calibration: ensure new engineer understands quality bar | Consistent PR approval pattern |
| 3.4 | EM | Week 4 check-in meeting: review 30-day milestones; identify gaps; adjust plan if needed | 30-day milestone completion record |

#### Stage 4: Week 5-12 -- Autonomy and Baseline

| Step | Owner | Action | Output |
|------|-------|--------|--------|
| 4.1 | New Engineer | Independent task execution with decreasing buddy support | Self-directed contribution |
| 4.2 | Tech Lead | Assign progressively complex work; include in design discussions | Broadening technical contribution |
| 4.3 | EM | Week 12 (3-month) check-in: onboarding formally closed; performance baseline established | Onboarding completion record; performance baseline |
| 4.4 | EM | Collect onboarding feedback from new engineer for process improvement | Onboarding feedback captured |

### 3.4 Inputs

| Input | Source | Required/Optional |
|-------|--------|-------------------|
| Access checklist (tools, repos, environments) | EM / IT operations | Required |
| Onboarding documentation (setup guides, team wiki) | technical-writer | Required |
| Golden path templates (CI/CD, containerization, local setup) | infra-engineer (P-044) | Required |
| Current project context documents (Intent Brief, Scope Contract, Sprint Kickoff Brief) | PM / EM | Required |
| ADRs for active codebase | Tech Lead | Required |
| Team norms document (PR review expectations, coding standards, communication norms) | Tech Lead / EM | Optional but recommended |

### 3.5 Outputs and Artifacts

| Output | Format | Owner | Retention |
|--------|--------|-------|-----------|
| Onboarding plan | Document (wiki/Confluence) | EM | Retained for process improvement; archived after 90 days |
| 30-day milestone completion record | Checklist with EM sign-off | EM | Retained in HR/people system |
| 90-day onboarding completion record | Document with performance baseline | EM | Retained in HR/people system |
| Onboarding feedback | Survey or written feedback | New engineer | Fed into Developer Experience Survey (P-089) |
| First PR | Source control | New engineer | Standard code retention |

### 3.6 Gate/Checkpoint

**Gate**: 30-Day Onboarding Check-in

| Criterion | Verification Method | Pass/Fail |
|-----------|-------------------|-----------|
| Engineer has submitted at least one merged PR | Source control history | Binary |
| Engineer can navigate codebase and find documentation independently | EM observation + self-assessment | EM judgment |
| Engineer actively participates in standups and sprint review | EM observation | EM judgment |
| Development environment fully operational | Engineer self-report; confirmed by buddy | Binary |
| Engineer can explain current project's purpose in one sentence | Verbal check at 30-day meeting | Binary |

**Gate Owner**: Engineering Manager

**Gate Failure Action**: EM identifies specific gaps and creates remediation plan; extend buddy pairing; escalate systemic issues (e.g., broken golden path) to Platform EM.

### 3.7 Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Time to first PR | Calendar days from start date to first PR submission | Within week 1 (5 business days) |
| 30-day self-sufficiency | EM assessment at 30-day check-in | Engineer navigates codebase, finds docs, participates in ceremonies |
| Onboarding experience score | Fed into Developer Experience Survey (P-089) | Trending positive quarter-over-quarter |
| Environment setup time | Time from start to working local build | Less than 4 hours via golden path |

### 3.8 Dependencies

| Dependency | Process | Type | Criticality |
|------------|---------|------|-------------|
| Golden path templates must be current and functional | P-044 (Golden Path Adoption) | Infrastructure prerequisite | HIGH -- broken golden path blocks week 1 PR goal |
| Onboarding documentation must exist and be maintained | P-058 (API Documentation) / technical-writer | Documentation prerequisite | MEDIUM -- missing docs slow onboarding but do not block it |
| Developer Experience Survey captures onboarding feedback | P-089 (Developer Experience Survey) | Feedback loop | LOW -- survey is quarterly; onboarding feedback is per-event |

### 3.9 Traceability

| Trace | Reference |
|-------|-----------|
| Org Structure -- EM role | Engineering_Team_Structure_Guide Section 3.2: "Owns team health, hiring, onboarding, performance reviews" |
| Org Structure -- Tech Lead role | Engineering_Team_Structure_Guide Section 3.2: "Mentors junior and mid-level engineers" |
| Platform golden path | Engineering_Team_Structure_Guide Section 7: Platform as a Product; P-044 golden path adoption |
| Clarity of Intent -- Sprint Readiness | clarity_of_intent.md Stage 4: "Every engineer can answer: What am I building, why does it matter, and how will I know it's done?" |

---

## 4. P-091: New Project Onboarding Process

### 4.1 Identity

| Field | Value |
|-------|-------|
| **Process ID** | P-091 |
| **Process Name** | New Project Onboarding Process |
| **Purpose** | Structured process for bringing a squad up to speed on a new project: distributing Intent Brief, Scope Contract, Dependency Charter, and Sprint Kickoff Brief to all team members before Sprint 1 begins. |
| **Derived From** | Clarity of Intent -- Stage 4, Sprint Readiness Gate prerequisite: "every engineer can answer: what, why, how will I know it's done?" |

### 4.2 Ownership

| Role | Agent | Responsibility |
|------|-------|---------------|
| **Primary Owner** | engineering-manager | Schedules and facilitates project kickoff session; ensures all engineers attend or review recording; confirms readiness |
| **Supporting** | product-manager | Presents Intent Brief (why) and Scope Contract (what and done criteria) |
| **Supporting** | software-engineer (Tech Lead) | Presents technical design decisions, ADRs, architecture context |
| **Supporting** | technical-program-manager | Presents Dependency Charter (who we depend on, what we need, and when) |

### 4.3 Stages and Steps

#### Stage 1: Kickoff Preparation (After Dependency Acceptance Gate passes)

| Step | Owner | Action | Output |
|------|-------|--------|--------|
| 1.1 | EM | Schedule project kickoff session (60-90 minutes) within 2 business days of Dependency Acceptance Gate (P-019) passing | Calendar invite sent to all squad engineers |
| 1.2 | PM | Prepare Intent Brief and Scope Contract presentation; ensure documents are accessible in project wiki | Documents accessible and presentation ready |
| 1.3 | Tech Lead | Prepare technical context: architecture overview, ADRs, key design decisions, technical risks | Technical context presentation ready |
| 1.4 | TPM | Prepare Dependency Charter presentation: cross-team dependencies, timelines, contact persons, escalation paths | Dependency context presentation ready |
| 1.5 | EM | Distribute all documents (Intent Brief, Scope Contract, Dependency Charter, Sprint Kickoff Brief) to squad members for pre-reading | Documents distributed |

#### Stage 2: Project Kickoff Session

| Step | Owner | Action | Output |
|------|-------|--------|--------|
| 2.1 | PM | Present Intent Brief: project purpose, outcome, strategic context, boundaries, cost of inaction | Engineers understand the "why" |
| 2.2 | PM | Present Scope Contract: deliverables, definition of done, exclusions, success metrics, assumptions/risks | Engineers understand the "what" and "done" |
| 2.3 | Tech Lead | Present technical design: architecture, ADRs, technology choices, known technical risks | Engineers understand the "how" |
| 2.4 | TPM | Present Dependency Charter: cross-team dependencies, critical path, communication protocol | Engineers understand external dependencies |
| 2.5 | EM | Facilitate Q&A session: capture all questions; resolve or assign resolution owners | Q&A log with resolution status |

#### Stage 3: Readiness Confirmation

| Step | Owner | Action | Output |
|------|-------|--------|--------|
| 3.1 | EM | Distribute Sprint Kickoff Brief; confirm all engineers have read and acknowledged | Confirmed receipt from all engineers |
| 3.2 | EM | Conduct readiness spot-check: ask 2-3 engineers to articulate project intent, their deliverable, and done criteria | Verbal readiness confirmation |
| 3.3 | EM | Resolve any outstanding Q&A items from kickoff session before Sprint 1 begins | All questions resolved; Q&A log closed |
| 3.4 | EM | Record session (video or written summary) for engineers who could not attend | Session recording/summary available |

### 4.4 Inputs

| Input | Source | Required/Optional |
|-------|--------|-------------------|
| Intent Brief | PM / Sponsor (produced at Stage 1 of Clarity of Intent) | Required |
| Scope Contract | PM / Tech Lead (produced at Stage 2 of Clarity of Intent) | Required |
| Dependency Charter | TPM / Tech Lead (produced at Stage 3 of Clarity of Intent) | Required |
| Sprint Kickoff Brief | EM / Tech Lead (produced at Stage 4 of Clarity of Intent) | Required |
| ADRs and technical design documents | Tech Lead | Required |
| Session recording/summary for absent engineers | EM | Required if any engineer is absent |

### 4.5 Outputs and Artifacts

| Output | Format | Owner | Retention |
|--------|--------|-------|-----------|
| Project kickoff session record | Video recording or written summary | EM | Retained for project duration + 1 quarter |
| Q&A log | Document capturing questions raised and resolutions | EM | Retained for project duration |
| Confirmed receipt log | Acknowledgment from each engineer that Sprint Kickoff Brief was received and read | EM | Retained for Sprint 1 |
| Readiness spot-check results | EM notes from verbal checks | EM | Retained for Sprint 1 retrospective |

### 4.6 Gate/Checkpoint

**Gate**: Sprint Readiness Gate (P-025)

This process does not define its own gate. Instead, it feeds directly into the Sprint Readiness Gate (P-025), which is the formal gate defined in the Clarity of Intent Stage 4.

| Criterion from P-025 relevant to P-091 | Verification Method |
|-----------------------------------------|-------------------|
| Sprint goal is stated and connects to a Scope Contract deliverable | Sprint Kickoff Brief review |
| Intent trace is visible (project intent -> deliverable -> sprint goal) | Sprint Kickoff Brief Section 2 |
| Every engineer can answer: "What am I building, why does it matter, and how will I know it's done?" | EM spot-check during readiness confirmation |
| All dependencies due this sprint have a current status and a contingency | Sprint Kickoff Brief Section 4 |

**Gate Owner**: EM + Tech Lead + PM (collectively at sprint planning meeting)

**Gate Failure Action**: Defer Sprint 1 start; schedule additional context sessions; resolve outstanding questions. Do not begin development with unresolved context gaps.

### 4.7 Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Attendance/review rate | Percentage of squad engineers who attend kickoff or review recording | 100% |
| Question resolution | All questions raised at kickoff resolved before Sprint 1 | 100% resolution before Sprint 1 Day 1 |
| Intent articulation | Random engineer can explain project intent after kickoff | Yes -- verified by EM spot-check |
| Sprint 1 alignment | No misaligned implementation decisions in Sprint 1 traceable to missing project context | Zero context-related rework in Sprint 1 |

### 4.8 Dependencies

| Dependency | Process | Type | Criticality |
|------------|---------|------|-------------|
| Dependency Acceptance Gate must pass first | P-019 (Dependency Acceptance Gate) | Sequence prerequisite | BLOCKING -- P-091 cannot start until P-019 passes |
| Sprint Readiness Gate validates output | P-025 (Sprint Readiness Gate) | Downstream gate | HIGH -- P-091 output is an input to P-025 |
| Intent Brief must exist | P-001 through P-004 (Intent Frame processes) | Document prerequisite | BLOCKING -- cannot present what does not exist |
| Scope Contract must exist | P-007 through P-013 (Scope processes) | Document prerequisite | BLOCKING |
| Dependency Charter must exist | P-015 through P-019 (Dependency processes) | Document prerequisite | BLOCKING |

### 4.9 Traceability

| Trace | Reference |
|-------|-----------|
| Clarity of Intent -- Stage 4 | clarity_of_intent.md: Sprint Bridge -- "EM presents Sprint Kickoff Brief at sprint planning" |
| Clarity of Intent -- Sprint Readiness Gate | clarity_of_intent.md: "Every engineer can answer: What am I building, why does it matter, and how will I know it's done?" |
| Clarity of Intent -- Intent Trace | clarity_of_intent.md: Sprint Kickoff Brief Section 2 -- three-line trace from sprint goal to project intent |
| Process Architecture -- Program 9 | Process Architecture: P-091 is in Program 9 (blockedBy P-019) |

---

## 5. P-092: Knowledge Transfer Process

### 5.1 Identity

| Field | Value |
|-------|-------|
| **Process ID** | P-092 |
| **Process Name** | Knowledge Transfer Process |
| **Purpose** | Structured knowledge transfer when an engineer leaves the team or project. Ensures no single engineer is the sole owner of critical system knowledge. |
| **Derived From** | Engineering_Team_Structure_Guide key-person dependency risk; EM responsibilities (people management, team health); Tech Lead mentorship responsibilities |

### 5.2 Ownership

| Role | Agent | Responsibility |
|------|-------|---------------|
| **Primary Owner** | engineering-manager | Identifies knowledge risk; creates transfer plan; validates transfer completion before departure |
| **Supporting** | software-engineer (departing engineer) | Conducts knowledge transfer sessions; produces documentation; participates in pairing |
| **Supporting** | software-engineer (successor engineer) | Receives knowledge; validates understanding through independent operation |
| **Supporting** | technical-writer | Reviews produced documents for completeness, clarity, and adherence to documentation standards |

### 5.3 Trigger Conditions

This process is event-driven, not cadence-driven. It activates when any of the following occur:

| Trigger | Notice Period | Urgency |
|---------|--------------|---------|
| Engineer resigns or is terminated | Typically 2-4 weeks notice | HIGH -- transfer must complete before last day |
| Engineer transfers to another team internally | Typically 2-4 weeks transition | MEDIUM -- engineer remains accessible after transfer |
| Engineer rotates off a project | Variable | MEDIUM -- engineer remains on team, just changing project |
| Bus factor analysis reveals single-person knowledge risk | Proactive identification | LOW urgency but HIGH importance -- schedule transfer before a crisis forces it |

### 5.4 Stages and Steps

#### Stage 1: Knowledge Inventory (Days 1-2 after trigger)

| Step | Owner | Action | Output |
|------|-------|--------|--------|
| 1.1 | EM | Identify what the departing engineer owns uniquely: systems, services, processes, external relationships, tribal knowledge | Knowledge inventory document |
| 1.2 | EM + Tech Lead | Assess criticality of each knowledge area: what breaks or degrades if this knowledge is lost? | Criticality assessment (HIGH/MEDIUM/LOW per item) |
| 1.3 | EM | Assign successor engineer(s) for each HIGH and MEDIUM criticality knowledge area | Successor assignment matrix |
| 1.4 | EM | Draft knowledge transfer plan: what to document, what to pair on, what to shadow, timeline | Knowledge transfer plan |

#### Stage 2: Documentation Production (Days 3-10)

| Step | Owner | Action | Output |
|------|-------|--------|--------|
| 2.1 | Departing Engineer | Update runbooks for all owned systems: operational procedures, failure modes, recovery steps | Updated runbooks |
| 2.2 | Departing Engineer | Write or update ADRs for key design decisions that exist only in the engineer's memory | Updated ADRs |
| 2.3 | Departing Engineer | Produce system context documents: architecture diagrams, data flows, integration points, known gotchas | System context documents |
| 2.4 | Departing Engineer | Document external relationships: vendor contacts, cross-team contacts, escalation paths | Relationship register |
| 2.5 | Technical Writer | Review all produced documents for completeness, clarity, and adherence to documentation standards | Documentation review feedback |
| 2.6 | Departing Engineer | Address Technical Writer feedback; finalize documents | Final documentation set |

#### Stage 3: Pairing and Shadowing (Days 5-15, overlapping with Stage 2)

| Step | Owner | Action | Output |
|------|-------|--------|--------|
| 3.1 | Departing Engineer + Successor | Pairing sessions on each HIGH criticality system: successor drives, departing engineer observes and explains | Pairing session notes |
| 3.2 | Successor Engineer | Shadow departing engineer during incident response or on-call (if applicable in the transfer window) | Shadowing completed for on-call scenarios |
| 3.3 | Successor Engineer | Independently perform a routine operational task for each transferred system while departing engineer is available for questions | Independent operation demonstrated |
| 3.4 | Departing Engineer | Record answers to successor's questions that reveal documentation gaps | Documentation gaps addressed |

#### Stage 4: Transfer Validation (Days 12-15 or before last day)

| Step | Owner | Action | Output |
|------|-------|--------|--------|
| 4.1 | EM | Conduct transfer validation meeting: successor demonstrates understanding of each transferred system | Transfer validation record |
| 4.2 | Successor Engineer | Demonstrate ability to independently: deploy, monitor, troubleshoot, and recover each transferred system | Independent operation confirmed |
| 4.3 | EM | Confirm: all HIGH criticality items transferred; all documentation reviewed and published | Transfer completion sign-off |
| 4.4 | EM | If gaps remain and departure is imminent: document remaining gaps and assign remediation plan | Gap remediation plan (if needed) |

### 5.5 Inputs

| Input | Source | Required/Optional |
|-------|--------|-------------------|
| System inventory for departing engineer | EM + Tech Lead assessment | Required |
| Successor engineer assignment | EM | Required |
| Documentation standards (runbook template, ADR template) | technical-writer / team wiki | Required |
| Existing documentation for owned systems | Team wiki / docs repo | Required (even if incomplete -- gaps drive transfer priorities) |

### 5.6 Outputs and Artifacts

| Output | Format | Owner | Retention |
|--------|--------|-------|-----------|
| Knowledge inventory | Document listing all knowledge areas, criticality, and successor | EM | Retained permanently in team wiki |
| Knowledge transfer plan | Document with timeline, sessions, and milestones | EM | Retained for 6 months after transfer |
| Updated runbooks | Runbook documents per system | Successor engineer (new owner) | Retained permanently; updated on change |
| Updated ADRs | ADR documents | Successor engineer (new owner) | Retained permanently |
| System context documents | Architecture diagrams, data flow docs | Successor engineer (new owner) | Retained permanently; updated on change |
| Transfer completion record | EM sign-off document | EM | Retained in HR/people system |

### 5.7 Gate/Checkpoint

**Gate**: Knowledge Transfer Completion

| Criterion | Verification Method | Pass/Fail |
|-----------|-------------------|-----------|
| All HIGH criticality systems have a documented successor who has demonstrated independent operation | EM observation + successor self-assessment | Binary |
| All runbooks updated and reviewed by Technical Writer | Technical Writer sign-off | Binary |
| All ADRs for undocumented decisions captured | Tech Lead review | Binary |
| Successor can independently respond to a simulated incident for each transferred system | Simulated exercise or verbal walkthrough | Binary |
| No "I need to ask [departing engineer]" blockers anticipated | EM + successor assessment | Judgment |

**Gate Owner**: Engineering Manager

**Gate Failure Action**: If departure date is fixed and transfer is incomplete, EM documents remaining gaps, creates remediation plan, assigns additional engineers to close gaps post-departure, and escalates to Director if critical knowledge cannot be transferred in time.

### 5.8 Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Documentation completeness | All HIGH criticality systems have current runbooks and ADRs before departure | 100% |
| Successor readiness | Successor can independently operate transferred systems within 2 weeks of departure | Yes |
| Post-departure incidents | Number of "I have a question for [departed engineer]" incidents within 30 days | Zero |
| Knowledge preservation | No system outage or degraded response traceable to knowledge loss within 60 days | Zero |

### 5.9 Dependencies

| Dependency | Process | Type | Criticality |
|------------|---------|------|-------------|
| Runbook documentation standards must exist | P-059 (Runbook standards) | Documentation prerequisite | MEDIUM -- transfer can proceed with ad-hoc format, but standards improve quality |
| ADR standards must exist | Team documentation standards | Documentation prerequisite | MEDIUM |
| No blocking process dependency | N/A | N/A | P-092 is standalone and event-driven |

### 5.10 Traceability

| Trace | Reference |
|-------|-----------|
| Org Structure -- EM responsibilities | Engineering_Team_Structure_Guide Section 3.2: EM owns "team health, hiring, onboarding, performance reviews" |
| Org Structure -- Tech Lead mentorship | Engineering_Team_Structure_Guide Section 3.2: Tech Lead "mentors junior and mid-level engineers" |
| Key-person dependency risk | Engineering_Team_Structure_Guide: organizational principle of avoiding single points of failure |
| Bus factor principle | Engineering_Team_Structure_Guide: cognitive load management -- knowledge should be distributed, not concentrated |

---

## 6. P-093: Technical Onboarding for Cross-Team Dependencies Process

### 6.1 Identity

| Field | Value |
|-------|-------|
| **Process ID** | P-093 |
| **Process Name** | Technical Onboarding for Cross-Team Dependencies Process |
| **Purpose** | When a new dependency relationship is established between two squads (at Stage 3 of Clarity of Intent), the depending squad receives structured technical context on the dependency target -- architecture, APIs, SLOs, runbooks -- before Sprint 1 begins. |
| **Derived From** | Clarity of Intent -- Stage 3: Dependency Charter (dependency owner context requirements); Sprint Kickoff Brief Section 4 (Dependencies Due This Sprint) |

### 6.2 Ownership

| Role | Agent | Responsibility |
|------|-------|---------------|
| **Primary Owner** | technical-program-manager | Identifies dependency context transfer needs from Dependency Charter; ensures transfers are scheduled and completed before Sprint 1 |
| **Supporting** | software-engineer (providing squad's Tech Lead) | Presents technical context for the dependency: API contracts, SLOs, known limitations, incident history |
| **Supporting** | technical-writer | Verifies dependency documentation (API docs, runbooks) exists and is current |

### 6.3 Stages and Steps

#### Stage 1: Dependency Context Identification (After Dependency Acceptance Gate)

| Step | Owner | Action | Output |
|------|-------|--------|--------|
| 1.1 | TPM | Review Dependency Charter (from P-019): for each new cross-team dependency, identify what technical context the depending squad needs | Dependency context transfer list |
| 1.2 | TPM | For each dependency, schedule a knowledge transfer session between providing squad's TL and depending squad's TL | Sessions scheduled |
| 1.3 | Technical Writer | Verify API documentation (P-058) and runbooks (P-059) for each dependency target are current | Documentation currency report |

#### Stage 2: Technical Context Transfer Sessions

| Step | Owner | Action | Output |
|------|-------|--------|--------|
| 2.1 | Providing TL | Present API contracts: endpoints, request/response schemas, authentication, rate limits, error codes | Depending TL understands API surface |
| 2.2 | Providing TL | Present SLOs: availability targets, latency targets, error budgets, what happens when SLOs are breached | Depending TL understands reliability expectations |
| 2.3 | Providing TL | Present known limitations and gotchas: edge cases, known bugs, workarounds, planned deprecations | Depending TL aware of pitfalls |
| 2.4 | Providing TL | Share incident history: past outages, root causes, recovery procedures relevant to the dependency | Depending TL understands failure modes |
| 2.5 | Providing TL | Provide contact person for blockers and escalation path | Contact and escalation info recorded |
| 2.6 | Depending TL | Ask clarifying questions; document answers | Q&A captured in session notes |

#### Stage 3: Documentation Verification and Handoff

| Step | Owner | Action | Output |
|------|-------|--------|--------|
| 3.1 | TPM | Verify API documentation and runbooks shared with depending squad | Documentation handoff confirmed |
| 3.2 | Technical Writer | If documentation gaps were found in Stage 1.3, verify that gaps have been addressed or that remediation is planned | Documentation gap remediation status |
| 3.3 | Depending TL | Confirm readiness: "My team can locate API documentation, SLOs, and contact person for this dependency" | Readiness confirmation |
| 3.4 | TPM | Record transfer completion for each dependency in Dependency Charter | Dependency Charter updated with transfer status |

### 6.4 Inputs

| Input | Source | Required/Optional |
|-------|--------|-------------------|
| Dependency Charter entry for the specific dependency | TPM (from P-019 output) | Required |
| API documentation for dependency target | Providing squad / technical-writer (P-058) | Required |
| Runbooks for dependency target | Providing squad / technical-writer (P-059) | Required |
| SLO definitions for dependency target | SRE / providing squad (P-054) | Required |
| Incident history for dependency target | SRE / providing squad | Optional but recommended |

### 6.5 Outputs and Artifacts

| Output | Format | Owner | Retention |
|--------|--------|-------|-----------|
| Dependency context transfer record | Document per dependency: what was covered, what documentation was shared, readiness confirmation | TPM | Retained for project duration |
| API documentation verification | Confirmation that docs are current; or gap remediation plan | Technical Writer | Retained in documentation system |
| Depending team readiness confirmation | Written confirmation from depending TL | TPM | Retained for Sprint Readiness Gate (P-025) |
| Session notes / Q&A log | Notes from transfer session | Depending TL | Retained for project duration |

### 6.6 Gate/Checkpoint

**Gate**: Sprint Readiness Gate (P-025) -- dependency context subset

Like P-091, this process does not define its own formal gate. Its completion is validated as part of the Sprint Readiness Gate (P-025).

| Criterion from P-025 relevant to P-093 | Verification Method |
|-----------------------------------------|-------------------|
| All dependencies due this sprint have a current status and a contingency | Sprint Kickoff Brief Section 4 |
| Depending squad can locate API documentation, SLOs, and contact person for every Sprint 1 dependency | Depending TL confirmation |
| No unresolved technical questions about critical-path dependencies | Q&A log review |

**Gate Owner**: TPM + depending squad's EM

**Gate Failure Action**: Defer Sprint 1 work that depends on the unresolved dependency. Schedule additional context session. Escalate via Dependency Charter escalation path if providing squad is unresponsive.

### 6.7 Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Dependency context coverage | All critical-path dependencies have completed context transfer before Sprint 1 | 100% of critical-path dependencies |
| Documentation currency | API docs and runbooks verified current for all dependencies | 100% verified |
| Sprint 1 dependency surprises | Number of "we didn't know the API worked that way" incidents in Sprint 1 | Zero |
| Contact accessibility | Depending squad can reach dependency contact within 4 hours for blockers | Yes |

### 6.8 Dependencies

| Dependency | Process | Type | Criticality |
|------------|---------|------|-------------|
| Dependency Acceptance Gate must pass first | P-019 (Dependency Acceptance Gate) | Sequence prerequisite | BLOCKING -- P-093 cannot start until P-019 identifies the dependencies |
| API documentation must exist | P-058 (API Documentation) | Documentation prerequisite | HIGH -- if API docs do not exist, transfer is incomplete |
| Runbooks must exist | P-059 (Runbook Documentation) | Documentation prerequisite | HIGH -- if runbooks do not exist, operational context is missing |
| SLO definitions must exist | P-054 (SLO Definition and Review) | Data prerequisite | MEDIUM -- SLOs should exist for any service with cross-team consumers |
| Sprint Readiness Gate validates output | P-025 (Sprint Readiness Gate) | Downstream gate | HIGH -- P-093 output is checked at P-025 |

### 6.9 Traceability

| Trace | Reference |
|-------|-----------|
| Clarity of Intent -- Stage 3 | clarity_of_intent.md: Dependency Charter Section 1 -- "Every dependency gets a row" including "What Is Needed" and "Owner" |
| Clarity of Intent -- Stage 4 | clarity_of_intent.md: Sprint Kickoff Brief Section 4 -- "Dependencies Due This Sprint" |
| Clarity of Intent -- Communication Protocol | clarity_of_intent.md: Dependency Charter Section 4 -- communication cadence and escalation triggers |
| Process Architecture -- Program 9 | Process Architecture: P-093 is in Program 9 (blockedBy P-019) |

---

## 7. Dependency Graph

### 7.1 Inter-Process Dependencies Within Category 17

```
P-090 (New Engineer Onboarding)          P-092 (Knowledge Transfer)
  |                                        |
  | depends on P-044 (Golden Path)         | standalone (event-driven)
  | feeds into P-089 (Dev Experience)      | depends on P-059 (Runbooks)
  |                                        |
  [No dependency on P-091/P-092/P-093]     [No dependency on P-090/P-091/P-093]


P-091 (New Project Onboarding)           P-093 (Cross-Team Dependency Onboarding)
  |                                        |
  | BLOCKED BY P-019                       | BLOCKED BY P-019
  | feeds into P-025                       | feeds into P-025
  |                                        | depends on P-058, P-059, P-054
  |                                        |
  [P-091 and P-093 are peers in Program 9 -- execute in parallel after P-019]
```

### 7.2 External Process Dependencies

| This Process | Depends On | Dependency Type |
|-------------|------------|-----------------|
| P-090 | P-044 (Golden Path Adoption) | Infrastructure -- golden path templates must be current |
| P-090 | P-089 (Developer Experience Survey) | Feedback loop -- onboarding feedback captured |
| P-091 | P-019 (Dependency Acceptance Gate) | BLOCKING sequence prerequisite |
| P-091 | P-025 (Sprint Readiness Gate) | Downstream validation gate |
| P-091 | P-001 to P-004 (Intent Frame) | Document prerequisites -- Intent Brief must exist |
| P-091 | P-007 to P-013 (Scope) | Document prerequisites -- Scope Contract must exist |
| P-091 | P-015 to P-019 (Dependency) | Document prerequisites -- Dependency Charter must exist |
| P-092 | P-059 (Runbook Documentation) | Documentation standard prerequisite |
| P-093 | P-019 (Dependency Acceptance Gate) | BLOCKING sequence prerequisite |
| P-093 | P-025 (Sprint Readiness Gate) | Downstream validation gate |
| P-093 | P-058 (API Documentation) | Documentation prerequisite |
| P-093 | P-059 (Runbook Documentation) | Documentation prerequisite |
| P-093 | P-054 (SLO Definition and Review) | Data prerequisite |

### 7.3 Program Placement

| Process | Program | Blocked By | Can Execute In Parallel With |
|---------|---------|------------|------------------------------|
| P-090 | Standalone | No process blocker (triggered by hire event) | Any process |
| P-091 | Program 9 | P-019 | P-093, P-022 (Sprint Goal Authoring) |
| P-092 | Standalone | No process blocker (triggered by departure/rotation event) | Any process |
| P-093 | Program 9 | P-019 | P-091, P-022 (Sprint Goal Authoring) |

---

## 8. Traceability Matrix

This matrix maps each process back to its source documents and the specific sections that justify its existence.

| Process | Clarity of Intent Reference | Org Structure Reference | Process Architecture Reference |
|---------|---------------------------|------------------------|-------------------------------|
| P-090 | Stage 4: "every engineer can answer what/why/done" (applied to new hires) | Section 3.2: EM owns onboarding; TL mentors; Platform golden path | Category 17; Tech Lead mentorship; EM onboarding ownership |
| P-091 | Stage 4: Sprint Bridge; Sprint Readiness Gate; Sprint Kickoff Brief | Section 3.2: EM runs sprint planning; PM presents scope | Category 17; Clarity of Intent Stage 4 Sprint Readiness Gate |
| P-092 | N/A (not directly from Clarity of Intent; from org structure risk management) | Section 3.2: EM owns team health; cognitive load management principle | Category 17; key-person dependency risk; EM responsibilities |
| P-093 | Stage 3: Dependency Charter; Stage 4: Sprint Kickoff Brief Section 4 | Section 3.2: TPM cross-team delivery; TL technical direction | Category 17; Dependency Charter context requirements |

---

## 9. Acceptance Criteria Summary

The following criteria determine whether this specification is complete and ready for implementation.

| # | Criterion | Status |
|---|-----------|--------|
| 1 | All four processes (P-090 through P-093) have unique IDs, names, and purposes | COMPLETE |
| 2 | Each process has a named Primary Owner Agent and Supporting Agents from the 13-agent roster | COMPLETE |
| 3 | Each process has detailed stages/steps with owners, actions, and outputs | COMPLETE |
| 4 | Each process has documented inputs with source and required/optional classification | COMPLETE |
| 5 | Each process has documented outputs/artifacts with format, owner, and retention | COMPLETE |
| 6 | Each process has a gate/checkpoint with pass criteria and failure actions | COMPLETE |
| 7 | Each process has measurable success criteria with targets | COMPLETE |
| 8 | Each process has documented dependencies on other processes with criticality | COMPLETE |
| 9 | Each process traces to at least one source document (Clarity of Intent, Org Structure, or Process Architecture) | COMPLETE |
| 10 | Cross-process dependency graph is documented | COMPLETE |
| 11 | No process creates circular dependencies | VERIFIED -- P-090 and P-092 are standalone; P-091 and P-093 depend on upstream P-019 only |
| 12 | All processes align with the Clarity of Intent principle: context before code | VERIFIED |

---

*End of specification.*

---

## Cross-Category Dependencies

### Dependencies FROM Other Categories (Inputs)

| Source Process | Source Category | Consuming Process | Nature |
|---------------|----------------|-------------------|--------|
| P-019 (Dependency Acceptance Gate) | Cat 3: Dependency & Coordination | P-091 (New Project Onboarding) | Gate triggers project onboarding |
| P-019 (Dependency Acceptance Gate) | Cat 3: Dependency & Coordination | P-093 (Technical Onboarding for Dependencies) | New dependencies identified |
| P-044 (Golden Path Adoption) | Cat 7: Infrastructure | P-090 (New Engineer Onboarding) | Golden path for environment setup |
| P-058 (API Documentation) | Cat 10: Documentation | P-093 (Technical Onboarding for Dependencies) | API docs for dependency context |
| P-059 (Runbook Authoring) | Cat 10: Documentation | P-093 (Technical Onboarding for Dependencies) | Runbooks for dependency context |

### Dependencies TO Other Categories (Outputs)

| Providing Process | Consuming Process | Target Category | Nature |
|------------------|-------------------|-----------------|--------|
| P-091 (New Project Onboarding) | P-025 (Sprint Readiness Gate) | Cat 4: Sprint & Delivery | Engineer comprehension required for readiness |
| P-090 (New Engineer Onboarding) | P-089 (Developer Experience Survey) | Cat 16: Technical Excellence | Onboarding experience feeds developer NPS |

## Agent Assignments Summary

| Process | Primary Owner | Supporting Agents |
|---------|--------------|-------------------|
| P-090: New Engineer Onboarding | engineering-manager | software-engineer (TL), infra-engineer, technical-writer |
| P-091: New Project Onboarding | engineering-manager | product-manager, software-engineer (TL), technical-program-manager |
| P-092: Knowledge Transfer | engineering-manager | software-engineer, technical-writer |
| P-093: Technical Onboarding for Cross-Team Dependencies | technical-program-manager | software-engineer (providing TL), technical-writer |
