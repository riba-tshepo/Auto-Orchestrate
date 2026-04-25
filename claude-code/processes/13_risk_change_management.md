# Technical Specification: Risk & Change Management Processes (P-074 to P-077)

**Session**: auto-orc-20260405-procderive
**Date**: 2026-04-05
**Stage**: 2 — Process Specification
**Category**: 13 — Risk & Change Management
**Source**: Process Architecture (Stage 1), Clarity of Intent (Change Control section, Stage 2 Section 6), Engineering Team Structure Guide
**Processes Covered**: P-074, P-075, P-076, P-077

---

## Category Overview

Risk & Change Management encompasses all processes that identify, classify, track, review, and escalate risks and changes across the project lifecycle. These four processes span from scope definition (P-075 at Scope Lock) through ongoing execution (P-074 weekly RAID maintenance), pre-deployment governance (P-076 CAB review), and quarterly strategic oversight (P-077 Quarterly Risk Review). Together they form a continuous risk management chain that prevents risks from being identified once and then forgotten, and ensures high-impact production changes receive appropriate scrutiny before deployment.

The category has two temporal patterns:
1. **Event-driven processes**: P-075 (triggered at Scope Lock) and P-076 (triggered before HIGH-risk deployments)
2. **Cadence-driven processes**: P-074 (weekly) and P-077 (quarterly)

The primary tracking artifact across all four processes is the **RAID Log** (Risks, Assumptions, Issues, Dependencies) — the TPM's central coordination tool. P-075 seeds it, P-074 maintains it, P-076 consumes it for deployment decisions, and P-077 analyzes it for systemic patterns.

### Process Dependency Graph (Internal to Category)

```
P-010 (Assumptions & Risks Registration — EXTERNAL, Category 2)
  |
  v
P-075: Risk Register at Scope Lock (validates and classifies all risks before Scope Lock)
  |
  v
P-074: RAID Log Maintenance (weekly throughout project; seeded from P-075)
  |                        \
  |                         +---> P-076: Pre-Launch Risk Review / CAB
  |                                (triggered per HIGH-risk deployment)
  v
P-077: Quarterly Risk Review (consumes RAID Log trends across all projects)
```

### Cross-Category Dependencies

| External Process | Category | Relationship | Detail |
|-----------------|----------|-------------|--------|
| P-010 (Assumptions & Risks Registration) | Cat 2: Scope & Contract | Upstream to P-075 | P-010 produces raw assumptions/risks; P-075 classifies and validates them |
| P-013 (Scope Lock Gate) | Cat 2: Scope & Contract | Gate consumer of P-075 | P-075 output is a mandatory gate input |
| P-014 (Scope Change Control) | Cat 2: Scope & Contract | Feeds P-074 | Approved scope changes introduce new risk items into the RAID Log |
| P-034, P-035 (DoD, Performance Tests) | Cat 5: Quality Assurance | Upstream to P-076 | Must pass before CAB review |
| P-039 (SAST/DAST) | Cat 6: Security Processes | Upstream to P-076 | Security scans must be clean before CAB |
| P-048 (Production Release Management) | Cat 8: Release Management | Downstream of P-076 | CAB approval is a prerequisite for HIGH-risk releases |
| P-065 (Director Weekly EM Sync) | Cat 11: Organizational Audit | Consumes P-074 | Director reviews RAID Log during weekly sync |
| P-062-P-068 (Audit Layer Processes) | Cat 11: Organizational Audit | Feed P-074 | Audit findings that represent risks enter the RAID Log |

### Agent Involvement Summary

| Agent ID | Processes (Primary) | Processes (Supporting) |
|----------|-------------------|----------------------|
| technical-program-manager | P-074, P-076 | P-075, P-077 |
| product-manager | P-075 | P-074, P-076 |
| engineering-manager (Director/VP) | P-077 | P-074, P-076 |
| software-engineer (Tech Lead) | — | P-075 |
| security-engineer (AppSec) | — | P-075, P-076, P-077 |
| sre | — | P-076 |

---

## P-074: RAID Log Maintenance Process

### 1. Process ID and Name
**P-074** — RAID Log Maintenance Process

### 2. Purpose
Maintain a living, weekly-updated RAID Log (Risks, Assumptions, Issues, Dependencies) throughout the project lifecycle. The TPM updates all items weekly with current status, latest action, next action, and owner. The Director reviews the RAID Log in the weekly EM sync. Items not closed within their target date are escalated one organizational layer up. This process prevents risk management from reverting to informal hallway conversations and ensures that the risk register seeded at Scope Lock remains an active tracking tool throughout execution.

### 3. Derived From
- Clarity of Intent — Stage 3: Dependency Charter, Section 4 (Communication Protocol): "RAID log update — Weekly — TPM updates; reviewed by Director — Track risks, assumptions, issues, dependencies at project level"
- Engineering Team Structure Guide — TPM role: "Coordinates delivery across 3-10 engineering teams; manages cross-team dependencies, RAID logs, and milestone trackers; owns program-level risk escalation"
- Engineering Team Structure Guide — Section 8.4 (TPM cross-team coordination): "RAID log: Risks, Assumptions, Issues, Dependencies — the TPM's primary tracking tool"

### 4. Primary Owner Agent
**technical-program-manager** — The TPM owns the RAID Log as their primary tracking artifact. They are responsible for weekly updates, item accuracy, and escalation of overdue items.

### 5. Supporting Agents
- **engineering-manager** (Director) — Reviews RAID Log weekly in EM sync (P-065); approves escalation paths; ensures squad-level risks are surfaced
- **product-manager** — Contributes assumption updates (validated/invalidated) and business-context risk items; updates risk items arising from scope changes (P-014)

### 6. Stages/Steps

| Step | Actor | Action | Output |
|------|-------|--------|--------|
| 1. Seed RAID Log | TPM + PM | At project start, import all entries from the classified risk register produced by P-075 (Scope Contract Section 6). Each entry gets a RAID Log ID, category (R/A/I/D), status (Open/In Progress/Mitigated/Closed), target closure date, and owner. | Seeded RAID Log with initial entries |
| 2. Weekly Item Update | TPM | For every open item: update status, record latest action taken, define next action required, confirm owner is still correct. Mark resolved items as Closed with closure date and resolution summary. | Updated RAID Log (weekly snapshot) |
| 3. Add New Items | TPM + All squad TLs | During dependency standups, sprint reviews, and retrospectives, capture new risks, issues, and dependency changes. Each new item follows the same format: ID, category, severity, status, owner, target date. | New RAID Log entries |
| 4. Director Review | Engineering Manager (Director) | Director reviews RAID Log in weekly EM sync (P-065). Focus areas: (a) any HIGH items trending overdue, (b) items without active owners, (c) patterns across squads suggesting systemic issues. Director may reassign items or adjust priorities. | Director-reviewed RAID Log; escalation decisions |
| 5. Escalation of Overdue Items | TPM | Any item not closed within its target date is escalated one organizational layer up (TL -> EM -> Director -> VP). Escalation is documented in the RAID Log with date, escalation target, and reason. | Escalation records in RAID Log |
| 6. Quarterly Summary Preparation | TPM | At quarter end, prepare a RAID Log summary for the Quarterly Risk Review (P-077): open items by category, age distribution, severity distribution, resolution rate, and trend analysis. | Quarterly RAID Log summary report |

### 7. Inputs
- **Classified Risk Register** from P-075 — Initial entries at project start
- **Scope Change Requests** from P-014 — New risks introduced by approved scope changes
- **Dependency standup notes** — New blockers and dependency status changes
- **Sprint review outcomes** — New issues discovered during development
- **Audit findings** from P-062 through P-068 — Organizational audit findings that represent project risks
- **Incident post-mortem action items** — Action items from post-mortems (per process architecture: "Action items entered in RAID Log (P-074)")

### 8. Outputs/Artifacts
- **RAID Log** — The master tracking artifact. Each entry contains:

| Field | Description |
|-------|------------|
| ID | Unique identifier (e.g., R-001, A-003, I-007, D-012) |
| Category | Risk / Assumption / Issue / Dependency |
| Description | Clear statement of the item |
| Severity | HIGH / MEDIUM / LOW |
| Status | Open / In Progress / Mitigated / Closed |
| Owner | Named person or role responsible for resolution |
| Target Date | Date by which item should be resolved |
| Latest Action | Most recent action taken |
| Next Action | Next step required |
| Escalation History | Record of any escalations (date, target, reason) |

- **Weekly RAID Log snapshot** — Versioned weekly for audit trail
- **Quarterly RAID Log summary** — Aggregated report for P-077

### 9. Gate/Checkpoint
- **Director Weekly Review** (in P-065 EM sync) — Director confirms RAID Log has been updated that week and reviews HIGH-severity open items
- **Escalation Trigger** — Any item overdue beyond its target date without documented extension triggers automatic escalation

### 10. Success Criteria
- RAID Log updated every week without gaps throughout the project lifecycle
- Every item has a named owner and target closure date at all times
- No item stays open beyond its target date without being escalated one layer up
- New items from dependency standups, sprint reviews, and scope changes are captured within 1 business day of discovery
- Director has reviewed the RAID Log at least once per week
- Quarterly summary is prepared and delivered to P-077 on schedule

### 11. Dependencies

| Dependency | Process | Type | Detail |
|-----------|---------|------|--------|
| Risk Register at Scope Lock | P-075 | Hard prerequisite | RAID Log is seeded from the classified risk register |
| Assumptions & Risks Registration | P-010 | Hard prerequisite (indirect) | P-010 produces the raw entries that P-075 classifies and P-074 tracks |
| Scope Change Control | P-014 | Ongoing input | Approved scope changes introduce new risk items |
| Director Weekly EM Sync | P-065 | Cadence dependency | Director review happens within this meeting |
| Dependency Standups | P-017 (if applicable) | Ongoing input | New blockers and dependency status changes feed new items |

### 12. Traceability
- **Upstream**: P-075 (Risk Register at Scope Lock) — provides the initial RAID Log seed
- **Upstream**: P-010 (Assumptions & Risks Registration) — the original source of assumptions and risks before classification
- **Upstream**: P-014 (Scope Change Control) — approved changes feed new risk items
- **Upstream**: P-062-P-068 (Audit Layer Processes) — audit findings feed into the RAID Log
- **Downstream**: P-076 (Pre-Launch Risk Review / CAB) — CAB consumes RAID Log to assess deployment risk posture
- **Downstream**: P-077 (Quarterly Risk Review) — quarterly summary enables strategic risk analysis
- **Cross-reference**: P-065 (Director Weekly EM Sync) — the RAID Log is a standing agenda item
- **Artifact**: RAID Log (living document, versioned weekly)

---

## P-075: Risk Register at Scope Lock Process

### 1. Process ID and Name
**P-075** — Risk Register at Scope Lock Process

### 2. Purpose
Classify all Scope Contract assumptions and risks with severity ratings (HIGH/MEDIUM/LOW) and ensure every HIGH-severity item has a validation plan with a named owner and deadline before the Scope Lock Gate (P-013) passes. This process is the bridge between informal risk identification (P-010) and formal, ongoing risk tracking (P-074). It converts the raw assumptions and risks table from the Scope Contract into a classified, actionable risk register that can be tracked throughout execution.

### 3. Derived From
- Clarity of Intent — Stage 2: Scope Contract, Section 6 (Assumptions and Risks): "List assumptions the scope depends on and risks that could invalidate the plan. Each risk gets a severity and a mitigation owner."
- Clarity of Intent — Scope Lock Gate pass criteria: "All assumptions rated HIGH have been validated or have a validation plan with a deadline"
- Process Architecture — P-075: "All Scope Contract assumptions and risks classified as HIGH/MEDIUM/LOW. HIGH-severity items must have a validation plan with owner and deadline before Scope Lock gate passes."

### 4. Primary Owner Agent
**product-manager** — The PM owns the risk register within the Scope Contract and facilitates the classification process. The PM ensures all HIGH items have validation/mitigation plans before presenting at Scope Lock.

### 5. Supporting Agents
- **software-engineer** (Tech Lead) — Validates technical risk severity ratings; identifies technical risks that P-010 may have underestimated or missed; provides feasibility assessment for mitigation strategies
- **security-engineer** (AppSec) — Validates security risk severity ratings; ensures compliance and security risks are appropriately classified; confirms mitigation plans for security-related HIGH items are adequate
- **technical-program-manager** — Reviews dependency-related risks for cross-team impact; ensures RAID Log seeding format is compatible with ongoing tracking

### 6. Stages/Steps

| Step | Actor | Action | Output |
|------|-------|--------|--------|
| 1. Import P-010 Output | PM | Retrieve the assumptions and risks table from P-010 (Scope Contract Section 6 draft). This is the raw input — items identified but not yet formally classified for gate readiness. | Raw assumptions and risks list |
| 2. Classify Assumptions | PM + TL | For each assumption: rate severity using the matrix — impact if false (HIGH/MEDIUM/LOW) x likelihood of being false (HIGH/MEDIUM/LOW). The combined rating determines the overall severity. Any assumption where impact-if-false is HIGH gets an overall HIGH rating regardless of likelihood. | Classified assumptions with severity ratings |
| 3. Classify Risks | PM + TL + AppSec | For each risk: rate severity using probability x impact. Security risks are co-rated by AppSec. Technical risks are co-rated by TL. Business risks are rated by PM. | Classified risks with severity ratings |
| 4. Validate HIGH Assumptions | PM + TL | For every HIGH assumption: document a validation plan — what will be done to confirm or invalidate the assumption, who owns the validation, and by what deadline. Validation must complete before the assumption could cause a sprint-stopping surprise (typically before or during Sprint 1). | Validation plans for all HIGH assumptions |
| 5. Assign HIGH Risk Mitigation | PM + TL + AppSec | For every HIGH risk: document a mitigation strategy — specific actions to reduce probability or impact, who owns the mitigation, and the timeline. No HIGH risk may be left with "unknown" mitigation. | Mitigation strategies for all HIGH risks |
| 6. Finalize Risk Register | PM | Compile the classified, assigned risk register into Scope Contract Section 6 final form. Confirm every item has: description, type (Assumption/Risk), severity, mitigation/validation plan, owner. | Finalized Risk Register (Scope Contract Section 6) |
| 7. Seed RAID Log | PM + TPM | Transfer all entries into the RAID Log format for ongoing tracking by P-074. Each entry gets a RAID Log ID and initial status. | Seeded RAID Log |

### 7. Inputs
- **Assumptions and Risks Table** from P-010 — Raw list of assumptions and risks with initial severity assessments
- **Scope Contract draft** (Sections 2-5) — Deliverables, DoD, exclusions, and success metrics provide context for risk assessment
- **Technical design context** — Architecture decisions that influence technical risk severity
- **AppSec scope assessment** from P-012 — Security risk findings
- **Historical project data** — Retrospective findings from similar projects that inform risk patterns

### 8. Outputs/Artifacts
- **Classified Risk Register** (embedded in Scope Contract Section 6) — Each row contains:

| Item | Type | Severity | Mitigation/Validation Plan | Owner | Deadline |
|------|------|----------|---------------------------|-------|----------|
| [Description] | Assumption / Risk | HIGH / MEDIUM / LOW | [Specific plan] | [Named person/role] | [Date] |

- **RAID Log seed** — All entries formatted for ongoing tracking in P-074
- **Severity Classification Matrix** (reference):

| | Impact if False/Occurs: HIGH | Impact: MEDIUM | Impact: LOW |
|---|---|---|---|
| **Likelihood HIGH** | HIGH | HIGH | MEDIUM |
| **Likelihood MEDIUM** | HIGH | MEDIUM | LOW |
| **Likelihood LOW** | HIGH | MEDIUM | LOW |

Note: Any item where impact is HIGH receives an overall HIGH rating regardless of likelihood, per the principle that high-impact risks must be actively managed even if unlikely.

### 9. Gate/Checkpoint
**Scope Lock Gate (P-013)** — Pass criteria specific to P-075:
- Every assumption and risk has a severity rating (no items left unclassified)
- Every HIGH assumption has a validation plan with a named owner and a deadline
- Every HIGH risk has a mitigation strategy with a named owner
- No HIGH item is marked "unknown" without a documented plan to resolve the unknown before Sprint 1
- AppSec has co-validated severity ratings for all security-related items

### 10. Success Criteria
- Every assumption and risk in the Scope Contract has a severity rating (HIGH/MEDIUM/LOW)
- Every HIGH assumption has a named validation owner and a deadline
- Every HIGH risk has a documented mitigation strategy and a named owner
- No HIGH assumption is left at "unknown" without a plan to resolve before Sprint 1
- Security risks are co-validated by AppSec
- RAID Log is seeded and ready for weekly maintenance by TPM (P-074)
- The classified risk register is reviewed and accepted at the Scope Lock Gate (P-013)

### 11. Dependencies

| Dependency | Process | Type | Detail |
|-----------|---------|------|--------|
| Assumptions & Risks Registration | P-010 | Hard prerequisite | Provides the raw assumptions and risks table |
| Deliverable Decomposition | P-007 | Hard prerequisite (indirect) | Scope shape must be known to classify risks accurately |
| Definition of Done Authoring | P-008 | Hard prerequisite (indirect) | DoD criteria reveal hidden assumptions about technical capabilities |
| AppSec Scope Review | P-012 | Soft prerequisite | Security risk classification benefits from AppSec assessment; can proceed in parallel |
| Scope Lock Gate | P-013 | Gate consumer | P-013 requires P-075 output to pass |

### 12. Traceability
- **Upstream**: P-010 (Assumptions & Risks Registration) — raw risk data is the primary input
- **Upstream**: P-007 (Deliverables), P-008 (DoD), P-012 (AppSec Review) — context for accurate classification
- **Downstream**: P-013 (Scope Lock Gate) — classified risk register is a mandatory gate input
- **Downstream**: P-074 (RAID Log Maintenance) — seeded RAID Log entries are tracked weekly
- **Downstream**: P-076 (Pre-Launch Risk Review) — HIGH risks identified here may trigger CAB review at deployment time
- **Cross-reference**: P-014 (Scope Change Control) — post-lock scope changes may introduce new risks that require re-classification
- **Artifact**: Scope Contract Section 6 (classified risk register), RAID Log seed

---

## P-076: Pre-Launch Risk Review Process (CAB)

### 1. Process ID and Name
**P-076** — Pre-Launch Risk Review Process (Change Advisory Board)

### 2. Purpose
The Change Advisory Board (CAB) reviews all HIGH-risk production changes before deployment. The CAB assesses risk posture, rollback readiness, monitoring coverage, and communication plans. Outcomes are: Approve, Approve with conditions, Reject, or Defer. This process ensures that high-impact production changes receive structured, multi-perspective scrutiny before they reach users. Unreviewed HIGH-risk changes are the primary source of major production incidents.

### 3. Derived From
- Engineering Team Structure Guide — Section 7.6 (Release Management): "Release Manager role: Owns go/no-go decisions for production releases; chairs the Change Advisory Board (CAB); manages change management communication across stakeholders"
- Engineering Team Structure Guide — CAB section: "Composition: Release Manager (chair), SRE Lead, AppSec Engineer, Product Manager, Engineering Manager for affected systems. Trigger: Any change rated as HIGH risk (major infrastructure changes, database schema migrations, new external integrations, security control changes). Decision types: Approve, Approve with conditions, Reject, Defer for more information"
- Process Architecture — P-076: "Change Advisory Board reviews all HIGH-risk production changes before deployment"
- Process Architecture — P-048 (Production Release Management): "CAB review triggered if HIGH-risk change (P-076)"

### 4. Primary Owner Agent
**technical-program-manager** (Release Manager chairs) — The Release Manager, organizationally a TPM-track role, chairs the CAB and owns the process. The Release Manager schedules reviews, facilitates the board, records decisions, and tracks conditions to completion.

### 5. Supporting Agents
- **sre** — Provides reliability risk assessment: rollback readiness, monitoring coverage, SLO impact, blast radius analysis
- **security-engineer** (AppSec) — Provides security risk assessment: attack surface changes, compliance implications, security control modifications
- **product-manager** — Confirms business readiness: customer communication, feature flag strategy, business continuity
- **engineering-manager** (EM for affected systems) — Confirms team readiness: on-call staffing, runbook completeness, rollback capability

### 6. Stages/Steps

| Step | Actor | Action | Output |
|------|-------|--------|--------|
| 1. HIGH-Risk Classification | Submitting Team (TL/EM) | Identify the change as HIGH-risk using the trigger criteria. Submit a CAB Review Request to the Release Manager. The request must include: change description, risk assessment, rollback plan, monitoring plan, and communication plan. | CAB Review Request |
| 2. Schedule CAB Review | Release Manager (TPM) | Schedule the CAB review meeting. Must be completed before the release window. Minimum 24 hours notice to all CAB participants. Distribute the CAB Review Request to all participants in advance. | Scheduled CAB meeting; materials distributed |
| 3. Risk Assessment Review | CAB (all participants) | Review the change from each perspective: (a) SRE assesses reliability risk — rollback time, blast radius, SLO impact, monitoring gaps; (b) AppSec assesses security risk — attack surface, compliance, security controls; (c) PM assesses business risk — customer impact, communication readiness; (d) EM assesses operational risk — team readiness, on-call coverage, runbook quality. | Multi-perspective risk assessment |
| 4. Decision | CAB (consensus; Release Manager records) | CAB reaches a decision through structured discussion. Decision options: **Approve** (change proceeds as planned), **Approve with conditions** (change proceeds after specified conditions are met), **Reject** (change does not proceed; documented rationale with actionable feedback), **Defer** (more information needed before decision). | CAB Decision Record |
| 5. Condition Tracking (if applicable) | Release Manager (TPM) | If "Approve with conditions": each condition is documented with an owner and a deadline. Release Manager tracks conditions to completion. The release cannot proceed until all conditions are verified as met. | Condition tracking log; condition completion verification |
| 6. Decision Communication | Release Manager (TPM) | Communicate the CAB decision to the submitting team within 24 hours. If Rejected, include specific, actionable rationale so the team knows what to change. If Deferred, specify what additional information is needed. | Decision communication record |

### 7. Inputs
- **CAB Review Request** — Submitted by the team proposing the HIGH-risk change. Contains:

| Section | Content |
|---------|---------|
| Change Description | What is being deployed; affected systems and services |
| Risk Assessment | Why this change is HIGH-risk; specific risk factors |
| Rollback Plan | Step-by-step rollback procedure; estimated rollback time; rollback decision criteria |
| Monitoring Plan | What metrics/alerts will be watched during and after deployment; who is watching |
| Communication Plan | Internal and external communication if issues arise; customer notification plan if applicable |

- **RAID Log** (from P-074) — Current risk posture for the project; any open HIGH items relevant to this deployment
- **Performance test results** (from P-035) — Must pass before CAB review
- **SAST/DAST results** (from P-039) — Security scans must be clean before CAB review
- **Runbook** (from P-059, if applicable) — Operational procedures for the change

### 8. Outputs/Artifacts
- **CAB Decision Record** — Documents:

| Field | Content |
|-------|---------|
| Change ID | Unique identifier for the change |
| Date | CAB review date |
| Participants | Names and roles of all CAB participants |
| Decision | Approve / Approve with conditions / Reject / Defer |
| Rationale | Summary of the risk assessment discussion and reasoning |
| Conditions (if applicable) | Specific conditions, owners, and deadlines |
| Rejection Feedback (if applicable) | Actionable guidance for resubmission |

- **Condition Completion Log** (if Approve with conditions) — Tracks each condition to verified completion

### 9. Gate/Checkpoint
- **CAB Decision Gate**: No HIGH-risk change may proceed to production deployment without a recorded CAB decision of Approve or Approve with conditions (with all conditions met)
- **Prerequisite Gates**: Performance tests (P-035) passed; SAST/DAST clean (P-039); DoD complete (P-034)

### 10. Success Criteria
- All HIGH-risk changes are reviewed by CAB before production deployment — zero exceptions
- CAB decision is made within 48 hours of submission
- Rejected changes have documented, actionable rationale that enables resubmission
- All conditions (for "Approve with conditions") are tracked to completion and verified before release
- CAB decision is communicated to the submitting team within 24 hours
- No HIGH-risk change bypasses CAB without being flagged as a process violation

### 11. Dependencies

| Dependency | Process | Type | Detail |
|-----------|---------|------|--------|
| Performance Tests | P-035 | Hard prerequisite | Performance tests must pass before CAB review |
| SAST/DAST Scans | P-039 | Hard prerequisite | Security scans must be clean before CAB review |
| Definition of Done | P-034 | Hard prerequisite | All stories in DoD-complete state |
| RAID Log Maintenance | P-074 | Informational | Current risk posture informs CAB assessment |
| Production Release Management | P-048 | Downstream | CAB approval is a prerequisite for HIGH-risk releases |

### 12. Traceability
- **Upstream**: P-034 (DoD), P-035 (Performance Tests), P-039 (SAST/DAST) — prerequisite quality gates
- **Upstream**: P-074 (RAID Log) — informs the CAB of current project risk posture
- **Upstream**: P-075 (Risk Register at Scope Lock) — HIGH risks identified at scope time may trigger CAB review at deployment
- **Downstream**: P-048 (Production Release Management) — CAB approval enables the release to proceed
- **Cross-reference**: P-059 (Runbook Authoring) — runbooks are a CAB input for operational readiness
- **Cross-reference**: P-061 (Release Notes) — CAB-approved changes are documented in release notes
- **Artifact**: CAB Decision Record, Condition Completion Log

### HIGH-Risk Change Triggers

The following change types automatically trigger a CAB review:

| Trigger Category | Examples |
|-----------------|----------|
| Major infrastructure changes | Cloud provider migration, Kubernetes cluster upgrades, network topology changes |
| Database schema migrations with destructive changes | Column drops, table renames, data type changes that could lose data |
| New third-party integrations | New payment providers, external API dependencies, vendor SDK integrations |
| Security control changes | Authentication flow modifications, encryption algorithm changes, access control policy updates |
| Non-standard rollout | Any change bypassing the standard canary -> gradual -> full deployment pipeline |

---

## P-077: Quarterly Risk Review Process

### 1. Process ID and Name
**P-077** — Quarterly Risk Review Process

### 2. Purpose
Director and VP review RAID Log trends quarterly to identify systemic risks — risks that appear across multiple squads or projects and indicate organizational-level problems rather than project-level issues. Based on findings, leadership adjusts roadmap priorities or resource allocation. This process elevates risk management from individual project tracking to strategic organizational governance, preventing individual RAID items from obscuring systemic patterns that require structural intervention.

### 3. Derived From
- Process Architecture — P-077: "Director and VP review RAID log trends quarterly to identify systemic risks. Adjust roadmap or resource allocation based on findings."
- Clarity of Intent — "How to Know the Process Is Working" section: "Track these signals at the quarterly retrospective" — including "Scope changes per project" and "Late dependency discovery"
- Engineering Team Structure Guide — Director and VP quarterly governance responsibilities

### 4. Primary Owner Agent
**engineering-manager** (Director + VP level) — Directors own the review for their areas; VPs own the cross-Director pattern analysis. The Director facilitates the review meeting and owns the action items.

### 5. Supporting Agents
- **technical-program-manager** — Prepares the quarterly RAID Log summary data; provides cross-project perspective on risk patterns; maintains the data that powers the review
- **security-engineer** (AppSec) — Provides security risk trend analysis; identifies recurring security patterns across projects (e.g., recurring PCI compliance delays, repeated threat model findings)

### 6. Stages/Steps

| Step | Actor | Action | Output |
|------|-------|--------|--------|
| 1. Prepare Quarterly RAID Log Summary | TPM | Aggregate RAID Log data across all active projects. Produce summary report containing: (a) open items by category (R/A/I/D), (b) age distribution of open items, (c) severity distribution, (d) resolution rate (items closed vs. items opened), (e) items escalated and escalation outcomes, (f) trend comparison with previous quarter. | Quarterly RAID Log Summary Report |
| 2. Director Area Review | Director | Review the summary for their area. Identify: (a) which risk categories are growing (more items opened than closed), (b) which categories are being effectively resolved, (c) recurring patterns — risks that appear in multiple squads or multiple projects, (d) overdue items that have been open for more than one quarter. | Director's risk assessment for their area |
| 3. VP Cross-Director Review | VP | Review risk assessments from all Directors. Identify: (a) cross-Director patterns — risks appearing in multiple Directors' areas, (b) organization-wide systemic risks, (c) resource allocation implications — are certain teams consistently over-risked? | VP cross-organizational risk assessment |
| 4. Systemic Risk Identification | Director + VP | Classify systemic risks — defined as risks appearing in more than 2 squads. For each systemic risk, conduct root cause analysis: is this a tooling problem, a process gap, a skills gap, a staffing problem, or an architectural issue? | Systemic risk register with root cause analysis |
| 5. Roadmap and Resource Adjustments | VP + Director | Propose adjustments: (a) roadmap re-prioritization to address systemic risks, (b) resource reallocation (e.g., adding capacity to consistently under-resourced teams), (c) process changes (fed back to P-071 Quarterly Process Health Review), (d) investment decisions (e.g., platform improvements to address recurring infrastructure risks). | Proposed roadmap/resource adjustments |
| 6. Action Item Assignment | Director | Assign specific, time-bound action items for each proposed adjustment. Each action item has an owner and a deadline within the next quarter. Action items are entered into the RAID Log (P-074) for ongoing tracking. | Quarterly risk review action items |

### 7. Inputs
- **Quarterly RAID Log Summary** — Prepared by TPM; aggregated data across all active projects
- **Previous quarter's risk review action items** — Status check on prior quarter's commitments
- **Security risk trend report** — From AppSec; recurring security patterns
- **Process health review data** (from P-071, if available) — Process-level signals that may correlate with risk patterns
- **DORA metrics** (from P-081, if available) — Delivery performance data that may indicate risk areas
- **Incident post-mortem trends** — Patterns in production incidents that indicate systemic risk

### 8. Outputs/Artifacts
- **Quarterly Risk Review Report** — Contains:

| Section | Content |
|---------|---------|
| RAID Log Trend Summary | Open items by category, severity, age; resolution rate; quarter-over-quarter trends |
| Systemic Risks Identified | Risks appearing in >2 squads with root cause analysis |
| Roadmap Adjustment Proposals | Specific re-prioritization recommendations tied to systemic risks |
| Resource Allocation Changes | Recommended staffing or capacity adjustments |
| Action Items | Specific, owned, time-bound actions for the next quarter |
| Previous Quarter Follow-up | Status of prior quarter's action items |

- **Updated RAID Log** — Action items from the review entered as new tracked items in P-074

### 9. Gate/Checkpoint
- **Quarterly Cadence Gate**: The review must be held on schedule every quarter — it cannot be deferred or skipped
- **Systemic Risk Escalation Threshold**: Any risk appearing in more than 2 squads must be escalated to VP if the Director has not already done so
- **Action Item Follow-through**: Previous quarter's action items are reviewed for completion; incomplete items are escalated or re-assigned

### 10. Success Criteria
- Quarterly risk review held on schedule every quarter without exceptions
- Systemic risks (appearing in >2 squads) are identified and escalated to VP
- Roadmap adjustments are made within 1 quarter of identifying a systemic risk
- Previous quarter's action items are reviewed and their status is documented
- All new action items have named owners and deadlines within the next quarter
- Quarter-over-quarter trends show improvement in risk resolution rates

### 11. Dependencies

| Dependency | Process | Type | Detail |
|-----------|---------|------|--------|
| RAID Log Maintenance | P-074 | Hard prerequisite | The RAID Log must be consistently maintained for quarterly data to be meaningful |
| Quarterly Process Health Review | P-071 | Informational (parallel) | Process health signals may correlate with risk patterns; reviews may be held in the same quarterly governance cycle |
| DORA Metrics Review | P-081 | Informational | Delivery performance data provides additional context for risk assessment |
| Risk Register at Scope Lock | P-075 | Indirect upstream | The quality of initial risk classification affects the data available for quarterly analysis |

### 12. Traceability
- **Upstream**: P-074 (RAID Log Maintenance) — the RAID Log is the primary data source for quarterly analysis
- **Upstream**: P-075 (Risk Register at Scope Lock) — initial risk classification quality affects quarterly analysis quality
- **Downstream**: P-074 (RAID Log) — action items from the review are entered as new tracked items
- **Downstream**: Roadmap and resource allocation decisions — systemic risk findings drive strategic adjustments
- **Cross-reference**: P-071 (Quarterly Process Health Review) — process health and risk health are reviewed in the same quarterly governance cycle
- **Cross-reference**: P-081 (DORA Metrics Review) — delivery metrics provide context for risk patterns
- **Artifact**: Quarterly Risk Review Report

---

## Cross-Category Interface Map

### Incoming Interfaces (from other categories)

| Source Process | Source Category | What It Provides | Consumed By |
|---------------|----------------|-----------------|-------------|
| P-010 (Assumptions & Risks Registration) | Cat 2: Scope & Contract | Raw assumptions and risks table | P-075 |
| P-012 (AppSec Scope Review) | Cat 2: Scope & Contract | Security risk findings for classification | P-075 |
| P-013 (Scope Lock Gate) | Cat 2: Scope & Contract | Gate that validates P-075 output | P-075 |
| P-014 (Scope Change Control) | Cat 2: Scope & Contract | Approved scope changes introducing new risks | P-074 |
| P-034 (Definition of Done) | Cat 5: Quality Assurance | DoD completion status as CAB prerequisite | P-076 |
| P-035 (Performance Tests) | Cat 5: Quality Assurance | Performance test results as CAB prerequisite | P-076 |
| P-039 (SAST/DAST) | Cat 6: Security Processes | Security scan results as CAB prerequisite | P-076 |
| P-062-P-068 (Audit Layers) | Cat 11: Organizational Audit | Findings that represent project risks | P-074 |
| P-065 (Director Weekly EM Sync) | Cat 11: Organizational Audit | Weekly review cadence for RAID Log | P-074 |
| P-071 (Quarterly Process Health) | Cat 12: Post-Delivery | Process health signals for risk correlation | P-077 |
| P-081 (DORA Metrics Review) | Cat 14: Communication & Alignment | Delivery metrics for risk context | P-077 |

### Outgoing Interfaces (to other categories)

| Source Process | Target Process | Target Category | What It Provides |
|---------------|---------------|----------------|-----------------|
| P-074 (RAID Log) | P-065 (Director EM Sync) | Cat 11: Organizational Audit | Weekly risk status for Director review |
| P-074 (RAID Log) | P-076 (CAB) | Cat 13: Risk & Change (internal) | Current risk posture for deployment decisions |
| P-074 (RAID Log) | P-077 (Quarterly Review) | Cat 13: Risk & Change (internal) | Quarterly aggregated risk data |
| P-075 (Risk Register) | P-013 (Scope Lock Gate) | Cat 2: Scope & Contract | Classified risk register as mandatory gate input |
| P-075 (Risk Register) | P-074 (RAID Log) | Cat 13: Risk & Change (internal) | Seeded RAID Log entries |
| P-076 (CAB Decision) | P-048 (Production Release) | Cat 8: Release Management | CAB approval enabling HIGH-risk releases |
| P-077 (Quarterly Review) | Roadmap/Resource decisions | Strategic governance | Systemic risk findings driving adjustments |

---

## Timing Guide

| Process | Cadence/Duration | Trigger | Blocker If Late |
|---------|-----------------|---------|-----------------|
| P-074: RAID Log Maintenance | Weekly (30 min TPM update + Director review in EM sync) | Active project existence | Risk items go untracked; Director loses visibility |
| P-075: Risk Register at Scope Lock | 0.5-1 day (one-time per project) | P-010 output available; before Scope Lock Gate | Scope Lock Gate (P-013) cannot pass |
| P-076: Pre-Launch Risk Review (CAB) | 1-2 hours (per HIGH-risk change) | HIGH-risk change identified before deployment | HIGH-risk release blocked |
| P-077: Quarterly Risk Review | Half-day (quarterly) | Quarterly governance cycle | Systemic risks go undetected; no strategic adjustments |

---

## RAID Log Template Structure

```
RAID Log — [Project Name]
Last Updated: [Date]
Updated By: [TPM Name]

Section 1: Risks
  [Table: ID | Description | Severity | Status | Owner | Target Date | Mitigation Plan | Latest Action | Next Action | Escalation History]

Section 2: Assumptions
  [Table: ID | Description | Severity | Status | Owner | Target Date | Validation Plan | Latest Action | Next Action | Escalation History]

Section 3: Issues
  [Table: ID | Description | Severity | Status | Owner | Target Date | Resolution Plan | Latest Action | Next Action | Escalation History]

Section 4: Dependencies
  [Table: ID | Description | Severity | Status | Owner | Target Date | Resolution Plan | Latest Action | Next Action | Escalation History]

Change Log
  [Table: Date | Change Description | Changed By]
```

---

## CAB Review Request Template Structure

```
CAB Review Request — [Change ID]
Submitted By: [Name / Role]
Date: [Submission Date]
Requested Review Date: [Date]

Section 1: Change Description
  [What is being deployed; affected systems and services; scope of change]

Section 2: Risk Assessment
  [Why this change is HIGH-risk; specific risk factors; blast radius]

Section 3: Rollback Plan
  [Step-by-step rollback procedure; estimated rollback time; rollback decision criteria]

Section 4: Monitoring Plan
  [Metrics and alerts during/after deployment; who is watching; escalation if anomalies detected]

Section 5: Communication Plan
  [Internal notification plan; external/customer communication if issues arise]

Section 6: Prerequisites Checklist
  [ ] Performance tests passed (P-035)
  [ ] SAST/DAST clean (P-039)
  [ ] All stories DoD-complete (P-034)
  [ ] Runbook updated (P-059)
  [ ] On-call staffing confirmed
```

---

## Quarterly Risk Review Report Template Structure

```
Quarterly Risk Review — Q[N] [Year]
Prepared By: [TPM Name]
Reviewed By: [Director Name], [VP Name]
Date: [Review Date]

Section 1: RAID Log Trend Summary
  [Open items by category; severity distribution; age distribution; resolution rate; quarter-over-quarter comparison]

Section 2: Systemic Risks Identified
  [Risks appearing in >2 squads; root cause analysis for each]

Section 3: Previous Quarter Action Item Follow-up
  [Status of each action item from prior quarter; completed/incomplete/carried forward]

Section 4: Roadmap Adjustment Proposals
  [Re-prioritization recommendations tied to systemic risk findings]

Section 5: Resource Allocation Changes
  [Recommended staffing or capacity adjustments]

Section 6: New Action Items
  [Table: Action | Owner | Deadline | Linked Systemic Risk]
```

---

## Cross-Category Dependencies

### Dependencies FROM Other Categories (Inputs)

| Source Process | Source Category | Consuming Process | Nature |
|---------------|----------------|-------------------|--------|
| P-010 (Assumptions and Risks Registration) | Cat 2: Scope & Contract | P-074 (RAID Log Maintenance) | RAID Log seeded from Scope Contract |
| P-007 (Deliverable Decomposition) | Cat 2: Scope & Contract | P-075 (Risk Register at Scope Lock) | Scope shape needed for risk identification |
| P-035 (Performance Testing) | Cat 5: Quality Assurance | P-076 (CAB) | Performance results for CAB review |
| P-039 (SAST/DAST) | Cat 6: Security | P-076 (CAB) | Security scan results for CAB review |
| P-042 (Compliance Review) | Cat 6: Security | P-074 (RAID Log Maintenance) | Compliance remediation tracked |
| P-062-P-068 (Audit Layers) | Cat 11: Organizational Audit | P-074 (RAID Log Maintenance) | Audit findings tracked |

### Dependencies TO Other Categories (Outputs)

| Providing Process | Consuming Process | Target Category | Nature |
|------------------|-------------------|-----------------|--------|
| P-074 (RAID Log Maintenance) | P-065 (Director Audit) | Cat 11: Organizational Audit | Director reviews RAID Log weekly |
| P-075 (Risk Register) | P-013 (Scope Lock Gate) | Cat 2: Scope & Contract | Gate consumes risk register |
| P-076 (CAB) | P-048 (Production Release Mgmt) | Cat 7: Infrastructure | CAB approval for HIGH-risk changes |

## Agent Assignments Summary

| Process | Primary Owner | Supporting Agents |
|---------|--------------|-------------------|
| P-074: RAID Log Maintenance | technical-program-manager | engineering-manager (Director), product-manager |
| P-075: Risk Register at Scope Lock | product-manager | software-engineer (TL), security-engineer |
| P-076: Pre-Launch Risk Review (CAB) | technical-program-manager (Release Manager) | sre, security-engineer, product-manager, engineering-manager |
| P-077: Quarterly Risk Review | engineering-manager (Director + VP) | technical-program-manager, security-engineer |
