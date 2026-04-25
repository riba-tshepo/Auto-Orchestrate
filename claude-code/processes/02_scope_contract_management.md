# Technical Specification: Scope & Contract Management Processes (P-007 to P-014)

**Session**: auto-orc-20260405-procderive
**Date**: 2026-04-05
**Stage**: 2 — Process Specification
**Category**: 2 — Scope & Contract Management
**Source**: Process Architecture (Stage 1), Clarity of Intent (Stage 2: Scope Contract), Engineering Team Structure Guide
**Processes Covered**: P-007, P-008, P-009, P-010, P-011, P-012, P-013, P-014

---

## Category Overview

Scope & Contract Management encompasses all processes that translate a locked Intent Brief into a versioned, controlled Scope Contract and manage changes to that contract throughout the project lifecycle. These processes collectively produce the Scope Contract artifact — the single source of truth for what "done" means. The Scope Contract has six sections (Outcome Restatement, Deliverables, Definition of Done, Explicit Exclusions, Success Metrics, Assumptions and Risks), is 3-5 pages, and is owned by the PM and TL.

All eight processes in this category derive from Clarity of Intent Stage 2 (Scope Contract) and the Change Control section. The category begins after the Intent Review Gate (P-004) passes and concludes when the Scope Lock Gate (P-013) locks the contract at v1.0. Post-lock, the Scope Change Control Process (P-014) governs all modifications.

### Process Dependency Graph (Internal to Category)

```
P-004 (Intent Review Gate — EXTERNAL prerequisite)
  |
  v
P-007: Deliverable Decomposition
  |
  +---> P-008: Definition of Done Authoring (requires P-007)
  |       |
  +---> P-011: Exclusion Documentation (requires P-007)
  |
  +---> P-009: Success Metrics Definition (requires P-007)
  |
  +---> P-010: Assumptions & Risks Registration (requires P-007, P-008)
  |
  +---> P-012: AppSec Scope Review (requires P-007, P-008)
  |
  v
P-013: Scope Lock Gate (requires P-007 through P-012)
  |
  v
P-014: Scope Change Control (requires P-013)
```

### Agent Involvement Summary

| Agent ID | Processes (Primary) | Processes (Supporting) |
|----------|-------------------|----------------------|
| product-manager | P-007, P-008, P-009, P-010, P-011, P-013, P-014 | P-012 |
| software-engineer (Tech Lead) | — | P-007, P-008, P-010, P-013, P-014 |
| staff-principal-engineer | — | P-007, P-013 |
| security-engineer (AppSec) | P-012 | P-008, P-010, P-013 |
| qa-engineer | — | P-008, P-013 |
| data-engineer | — | P-009 |
| sre | — | P-009 |
| engineering-manager | — | P-011, P-013, P-014 |
| technical-program-manager | — | P-010, P-014 |

---

## P-007: Deliverable Decomposition Process

### 1. Process ID and Name
**P-007** — Deliverable Decomposition Process

### 2. Purpose
Break the Intent Brief outcome into discrete deliverables, each with a named owner squad and a one-sentence description. The deliverables table becomes the backbone of the Scope Contract. Without a clear decomposition, work is unowned, gaps surface late, and squads duplicate effort or leave critical pieces unaddressed.

### 3. Derived From
Clarity of Intent — Stage 2: Scope Contract, Section 2 (Deliverables)

Relevant source text: "List every distinct deliverable the project will produce. Each deliverable gets a one-sentence description and a clear owner (which squad or role is responsible)."

### 4. Primary Owner Agent
**product-manager** — The PM proposes the deliverable list, ensures each deliverable traces to the Intent Brief outcome, and assigns owner squads in coordination with the TL.

### 5. Supporting Agents
- **software-engineer** (Tech Lead) — Validates technical feasibility and completeness of the decomposition; identifies missing technical deliverables
- **staff-principal-engineer** — Reviews cross-team deliverables for architectural completeness; ensures deliverables align with system boundaries

### 6. Stages/Steps

| Step | Actor | Action | Output |
|------|-------|--------|--------|
| 1. Review Intent Brief | PM + TL | Read the locked Intent Brief. Extract the outcome statement, beneficiaries, and boundaries. Confirm understanding of what the project must achieve. | Shared understanding of project intent |
| 2. Propose Deliverable List | PM | Draft an initial list of deliverables required to achieve the stated outcome. Each deliverable is a distinct, shippable unit of work. Format: ID, name, one-sentence description. | Draft deliverables list |
| 3. Validate Feasibility | TL | Review each proposed deliverable for technical feasibility. Identify missing technical deliverables (infrastructure, migrations, SDK integrations) that the PM may not have included. Add any missing items. | Validated and augmented deliverables list |
| 4. Assign Owner Squads | PM + TL | For each deliverable, assign exactly one owner squad. If a deliverable spans squads, either split it into squad-scoped deliverables or escalate to Staff/Principal Engineer for architectural resolution. | Owner-assigned deliverables |
| 5. Cross-Team Review | staff-principal-engineer | Review all deliverables that involve more than one squad or cross architectural boundaries. Confirm the decomposition respects system boundaries and does not create hidden coupling. | Architecturally validated deliverables |
| 6. Finalize Table | PM | Enter the final deliverables table into Scope Contract Section 2. Format: ID, Deliverable Name, Description, Owner Squad. | Scope Contract Section 2 complete |

### 7. Inputs
- Locked Intent Brief (output of P-004 Intent Review Gate)
- Squad ownership map (organizational context from Engineering Team Structure Guide)
- Architectural context (system boundaries, service ownership)

### 8. Outputs/Artifacts
- **Deliverables Table** (Section 2 of Scope Contract) — Each row contains: deliverable ID, deliverable name, one-sentence description, owner squad
- Format reference:

| # | Deliverable | Description | Owner |
|---|------------|-------------|-------|
| 1 | [Name] | [One-sentence description of what this produces] | [Squad Name] |

### 9. Gate/Checkpoint
**Scope Lock Gate (P-013)** — The deliverables table is reviewed as part of the full Scope Contract. Pass criteria specific to this process:
- Every deliverable has exactly one named owner squad
- No deliverable description is vague or ambiguous
- All deliverables collectively cover the Intent Brief outcome (no gaps)
- No deliverable is duplicated across squads

### 10. Success Criteria
- Every deliverable has exactly one named owner squad (no shared ownership, no orphans)
- No deliverable is vague — each has a one-sentence description of what it produces
- All deliverables collectively implement the outcome stated in the Intent Brief
- Cross-team deliverables have been reviewed and validated by staff-principal-engineer
- The deliverables table can be read by any engineer and understood without additional context

### 11. Dependencies
| Dependency | Process | Type | Detail |
|-----------|---------|------|--------|
| Intent Review Gate passed | P-004 | Hard prerequisite | Cannot begin decomposition without a locked Intent Brief |
| Boundary Definition | P-003 | Informational | Exclusions from the Intent Brief guide what NOT to decompose |

### 12. Traceability
- **Upstream**: Intent Brief (P-001) locked by Intent Review Gate (P-004) — the outcome statement is the decomposition target
- **Downstream**: P-008 (DoD Authoring), P-009 (Success Metrics), P-010 (Assumptions/Risks), P-011 (Exclusion Documentation), P-012 (AppSec Review) — all consume the deliverables table
- **Gate**: Scope Lock Gate (P-013) — deliverables table is a mandatory input
- **Artifact**: Scope Contract Section 2

---

## P-008: Definition of Done Authoring Process

### 1. Process ID and Name
**P-008** — Definition of Done Authoring Process

### 2. Purpose
Write binary, testable acceptance criteria for every deliverable in the Scope Contract before development begins. The Definition of Done (DoD) eliminates ambiguity about what "complete" means. The rule is absolute: if a deliverable does not have a Definition of Done, it is not in scope. Undone definitions are the primary source of scope disputes.

### 3. Derived From
Clarity of Intent — Stage 2: Scope Contract, Section 3 (Definition of Done)

Relevant source text: "For each deliverable, define the acceptance criteria — the specific, testable conditions that must be true for the deliverable to be considered complete. Use the format 'It is done when...'" and "If a deliverable does not have a Definition of Done, it is not in scope."

### 4. Primary Owner Agent
**product-manager** — The PM drafts initial acceptance criteria and ensures business-facing completeness conditions are captured.

### 5. Supporting Agents
- **software-engineer** (Tech Lead) — Provides technical acceptance criteria: performance thresholds, API contracts, error handling, backward compatibility
- **qa-engineer** (QA Lead) — Reviews every criterion for testability; ensures each is binary (pass/fail); flags criteria that cannot be automated
- **security-engineer** (AppSec) — Adds security-specific criteria for deliverables touching user data, authentication, payments, or infrastructure

### 6. Stages/Steps

| Step | Actor | Action | Output |
|------|-------|--------|--------|
| 1. Draft Business Criteria | PM | For each deliverable from P-007, write initial acceptance criteria using "It is done when..." format. Focus on user-facing and business-facing conditions. | Draft DoD per deliverable |
| 2. Add Technical Criteria | TL | For each deliverable, add technical criteria: performance budgets (e.g., "P95 latency < 200ms"), API contract conformance, error handling behaviors, backward compatibility requirements. | Technically augmented DoD |
| 3. Testability Review | QA Lead | Review every criterion. Confirm each is binary (can be verified as true or false). Flag and rewrite any criterion using vague language ("good enough", "reasonable", "appropriate", "performant"). Identify which criteria require automated tests vs. manual verification. | Testability-validated DoD |
| 4. Security Criteria | AppSec | Identify all deliverables that touch user data, authentication, payment flows, or infrastructure. Add security-specific DoD criteria: threat model completion, SAST/DAST scan results, PCI compliance checks, access control verification. | Security-augmented DoD |
| 5. Finalize Table | PM | Consolidate all criteria into Scope Contract Section 3. Verify every deliverable from Section 2 has a corresponding DoD entry. | Scope Contract Section 3 complete |

### 7. Inputs
- Deliverables table from P-007 (Scope Contract Section 2)
- QA test strategy (existing team testing standards)
- AppSec scope review output (from P-012, or preliminary assessment)
- Existing performance budgets and SLA targets

### 8. Outputs/Artifacts
- **Definition of Done Table** (Section 3 of Scope Contract) — Each row contains: deliverable name, acceptance criteria (multiple "It is done when..." statements)
- Format reference:

| Deliverable | Done When |
|------------|-----------|
| [Name] | [Criterion 1]; [Criterion 2]; [Criterion 3] |

### 9. Gate/Checkpoint
**Scope Lock Gate (P-013)** — Pass criteria specific to this process:
- Every deliverable has a written DoD with testable criteria
- No criterion uses vague language
- Security criteria included for all security-relevant deliverables
- QA Lead has confirmed testability of all criteria

### 10. Success Criteria
- Every deliverable in Section 2 has a corresponding DoD entry in Section 3 (1:1 mapping, no gaps)
- Every criterion is binary — can be verified as met or not met
- No criterion uses vague language ("good enough", "reasonable", "appropriate")
- Security criteria included for all deliverables touching user data, auth, or infrastructure
- QA Lead has signed off on testability of all criteria
- At least one criterion per deliverable is automatable in CI

### 11. Dependencies
| Dependency | Process | Type | Detail |
|-----------|---------|------|--------|
| Deliverable Decomposition | P-007 | Hard prerequisite | Cannot write DoD without deliverables defined |
| AppSec Scope Review | P-012 | Soft prerequisite | AppSec criteria can be added in parallel; must be complete before P-013 |

### 12. Traceability
- **Upstream**: P-007 (Deliverables Table) — each deliverable requires a DoD entry
- **Downstream**: P-013 (Scope Lock Gate) — DoD completeness is a gate pass criterion
- **Downstream (execution)**: Sprint stories (P-023) derive acceptance criteria from the DoD
- **Downstream (verification)**: QA test plans map 1:1 to DoD criteria
- **Artifact**: Scope Contract Section 3

---

## P-009: Success Metrics Definition Process

### 1. Process ID and Name
**P-009** — Success Metrics Definition Process

### 2. Purpose
Define 2-4 measurable metrics that trace directly to the Intent Brief outcome. These metrics are the organization's commitment to measuring whether the project achieved its intended business result. Without explicit success metrics, teams ship deliverables but cannot determine if the project succeeded.

### 3. Derived From
Clarity of Intent — Stage 2: Scope Contract, Section 5 (Success Metrics)

Relevant source text: "Define 2-4 metrics that the team will track to determine whether the project achieved its intended outcome. These must trace directly back to the outcome in the Intent Brief."

### 4. Primary Owner Agent
**product-manager** — The PM traces the Intent Brief outcome to measurable signals and defines targets.

### 5. Supporting Agents
- **data-engineer** — Validates that metric instrumentation exists or can be built; confirms data pipeline availability
- **sre** — Validates that observability infrastructure can capture the required signals; confirms monitoring and alerting feasibility

### 6. Stages/Steps

| Step | Actor | Action | Output |
|------|-------|--------|--------|
| 1. Trace Outcome to Signals | PM | Take the Intent Brief outcome statement. Identify 2-4 measurable signals that would indicate the outcome has been achieved. Each signal must be something the organization can observe and measure. | Candidate metrics list (2-4 items) |
| 2. Define Metric Structure | PM | For each metric, define: baseline (current value), target (desired value), measurement method (how it will be measured), and timeline (when the target should be reached). | Structured metrics with baselines and targets |
| 3. Validate Instrumentation | data-engineer | For each metric, confirm: (a) instrumentation already exists, or (b) instrumentation is a named deliverable in P-007's deliverables table, or (c) instrumentation must be added as a new deliverable. Flag any metric that cannot be instrumented. | Instrumentation feasibility assessment |
| 4. Validate Observability | SRE | For each metric, confirm: (a) observability infrastructure can capture the signal, (b) dashboards or alerting can be configured, (c) no infrastructure changes are required, or flag the required changes. | Observability feasibility assessment |
| 5. Finalize Metrics Table | PM | Enter validated metrics into Scope Contract Section 5. If any metric requires new instrumentation not yet in the deliverables list, coordinate with P-007 to add the deliverable. | Scope Contract Section 5 complete |

### 7. Inputs
- Locked Intent Brief (outcome statement from P-001/P-004)
- Deliverables table from P-007 (to check if instrumentation deliverables exist)
- Existing analytics and observability infrastructure inventory
- Current baseline measurements (if available)

### 8. Outputs/Artifacts
- **Success Metrics Table** (Section 5 of Scope Contract) — Each row contains: metric name, baseline, target, measurement method, timeline
- Format reference:

| Metric | Baseline | Target | Measurement Method | Timeline |
|--------|----------|--------|-------------------|----------|
| [Name] | [Current value] | [Target value] | [How measured] | [When target should be reached] |

### 9. Gate/Checkpoint
**Scope Lock Gate (P-013)** — Pass criteria specific to this process:
- Success metrics trace to the Intent Brief outcome
- 2-4 metrics defined (not more)
- Each metric has baseline, target, method, and timeline
- Instrumentation feasibility confirmed by data-engineer or instrumentation is a named deliverable

### 10. Success Criteria
- 2-4 metrics defined (not fewer, not more — focus is required)
- Every metric traces causally (not just thematically) to the Intent Brief outcome
- Every metric has a baseline, target, measurement method, and timeline
- At least one metric is measurable within 30 days of launch
- Instrumentation for every metric either exists or is a named deliverable
- data-engineer and SRE have confirmed feasibility

### 11. Dependencies
| Dependency | Process | Type | Detail |
|-----------|---------|------|--------|
| Intent Review Gate passed | P-004 | Hard prerequisite | Outcome statement is the source for metric derivation |
| Deliverable Decomposition | P-007 | Soft prerequisite | Needed to verify instrumentation is in scope; can proceed in parallel if outcome is clear |

### 12. Traceability
- **Upstream**: Intent Brief outcome statement (P-001) — metrics must trace causally to this outcome
- **Downstream**: P-013 (Scope Lock Gate) — metrics table is a mandatory input
- **Downstream (post-launch)**: Post-launch outcome measurement processes consume these metrics to determine project success
- **Cross-reference**: If instrumentation is missing, feeds back to P-007 to add a deliverable
- **Artifact**: Scope Contract Section 5

---

## P-010: Assumptions and Risks Registration Process

### 1. Process ID and Name
**P-010** — Assumptions and Risks Registration Process

### 2. Purpose
Log all scope assumptions with severity ratings and all risks with mitigation owners before Scope Lock. HIGH-severity assumptions must have a validation plan with an owner and deadline before the gate passes. This process converts implicit team assumptions into explicit, tracked items that can be validated or mitigated, preventing surprises during development.

### 3. Derived From
Clarity of Intent — Stage 2: Scope Contract, Section 6 (Assumptions and Risks)

Relevant source text: "List assumptions the scope depends on and risks that could invalidate the plan. Each risk gets a severity and a mitigation owner."

### 4. Primary Owner Agent
**product-manager** — The PM facilitates the identification session and owns the assumptions/risks register in the Scope Contract.

### 5. Supporting Agents
- **software-engineer** (Tech Lead) — Identifies technical risks: performance, scalability, integration complexity, technical debt
- **technical-program-manager** — Identifies dependency-related risks and cross-team coordination risks
- **security-engineer** (AppSec) — Identifies security risks: compliance exposure, threat surface changes, data handling risks

### 6. Stages/Steps

| Step | Actor | Action | Output |
|------|-------|--------|--------|
| 1. Structured Identification Session | PM + TL | Conduct a structured assumption and risk identification session. Review each deliverable and its DoD. For each, ask: "What are we assuming is true?" and "What could go wrong?" | Raw list of assumptions and risks |
| 2. Technical Risk Identification | TL | Add technical risks: performance under load, integration points, migration risks, backward compatibility, technical debt implications. | Technically augmented risk list |
| 3. Dependency & Coordination Risks | TPM | Add dependency-related risks: vendor timelines, cross-team capacity, shared resource availability, external API stability. | Dependency-augmented risk list |
| 4. Security Risk Identification | AppSec | Add security risks: new attack surface, compliance requirements (PCI, SOC2, GDPR), data handling changes, authentication flow modifications. | Security-augmented risk list |
| 5. Classify and Rate | PM | Classify each item as Assumption or Risk. Rate severity: HIGH, MEDIUM, LOW. | Classified and rated register |
| 6. Assign Validation/Mitigation | PM + TL | For every HIGH assumption: assign a validation owner and deadline. For every risk: assign a mitigation strategy and owner. No HIGH item may be left with "unknown" status without an explicit plan to resolve the unknown. | Fully assigned register |
| 7. Seed RAID Log | PM | Enter into Scope Contract Section 6. Seed the project RAID Log (P-074) with initial entries from this register. | Scope Contract Section 6 complete; RAID Log seeded |

### 7. Inputs
- Deliverables table from P-007
- Definition of Done from P-008
- Dependency context (preliminary, refined in P-015)
- Historical project data (retrospective findings from similar projects)
- AppSec scope assessment (from P-012 or preliminary)

### 8. Outputs/Artifacts
- **Assumptions and Risks Table** (Section 6 of Scope Contract) — Each row contains: item description, type (Assumption/Risk), severity (HIGH/MEDIUM/LOW), mitigation/validation plan, owner
- **Initial RAID Log seed** — Entries fed into the project RAID Log for ongoing tracking
- Format reference:

| Item | Type | Severity | Mitigation/Validation | Owner |
|------|------|----------|----------------------|-------|
| [Description] | Assumption/Risk | HIGH/MEDIUM/LOW | [Plan with deadline] | [Named person/role] |

### 9. Gate/Checkpoint
**Scope Lock Gate (P-013)** — Pass criteria specific to this process:
- All HIGH assumptions have validation plans with named owners and deadlines
- No HIGH assumption is marked "unknown" without a plan to resolve
- Every risk has a mitigation strategy and a named owner
- All items have severity ratings

### 10. Success Criteria
- Every assumption and risk has a severity rating (HIGH/MEDIUM/LOW)
- Every HIGH assumption has a named validation owner and a deadline
- No HIGH assumption is marked "unknown" without a plan to resolve the unknown
- Every risk has a mitigation strategy and a named owner
- Security risks are included for all deliverables with security implications
- RAID Log is seeded and ready for ongoing tracking during execution

### 11. Dependencies
| Dependency | Process | Type | Detail |
|-----------|---------|------|--------|
| Deliverable Decomposition | P-007 | Hard prerequisite | Scope shape must be known to identify risks |
| Definition of Done Authoring | P-008 | Hard prerequisite | DoD criteria reveal hidden assumptions about technical capabilities |
| AppSec Scope Review | P-012 | Soft prerequisite | Security risks are best identified after AppSec reviews scope; can proceed in parallel with security risks added later |

### 12. Traceability
- **Upstream**: P-007 (Deliverables) and P-008 (DoD) — scope shape drives risk identification
- **Downstream**: P-013 (Scope Lock Gate) — assumptions/risks table is a mandatory gate input
- **Downstream**: P-074 (RAID Log) — initial entries seeded from this process
- **Downstream**: P-015 (Dependency Registration) — dependency-related risks inform the Dependency Charter
- **Artifact**: Scope Contract Section 6

---

## P-011: Exclusion Documentation Process

### 1. Process ID and Name
**P-011** — Exclusion Documentation Process

### 2. Purpose
Carry forward Intent Brief boundaries into the Scope Contract and add any new exclusions discovered during scoping. Each exclusion states why it is excluded and where it will be addressed (if at all). Explicit exclusions prevent scope drift more effectively than detailed inclusions. Unacknowledged exclusions become hidden scope assumptions that create conflict during development.

### 3. Derived From
Clarity of Intent — Stage 2: Scope Contract, Section 4 (Explicit Exclusions)

Relevant source text: "Carry forward the boundaries from the Intent Brief and add any new exclusions discovered during scoping. Each exclusion should state *why* it is excluded and *where* it will be addressed (if at all)."

### 4. Primary Owner Agent
**product-manager** — The PM owns the exclusions list and ensures continuity from the Intent Brief boundaries.

### 5. Supporting Agents
- **engineering-manager** — EMs review the exclusions list to confirm no squad is implicitly planning or expecting to own excluded work

### 6. Stages/Steps

| Step | Actor | Action | Output |
|------|-------|--------|--------|
| 1. Copy Intent Brief Boundaries | PM | Copy all explicit boundaries/exclusions from the locked Intent Brief (Section 4) into the Scope Contract Section 4. These are the baseline exclusions established during Stage 1. | Baseline exclusions in Scope Contract |
| 2. Discover New Exclusions | PM + TL | During deliverable decomposition (P-007), identify items that could reasonably be considered in-scope but are being excluded. Common sources: adjacent features, platform improvements, related user flows, technical debt items. | New exclusion candidates |
| 3. Document Each Exclusion | PM | For each exclusion (carried forward and new), document: (a) the excluded item, (b) reason for exclusion, (c) future home — which team/backlog/initiative will address it, or "will not be addressed." | Fully documented exclusions |
| 4. EM Review | Engineering Managers | Each EM with deliverables in the project reviews the exclusions list. Confirm no squad is implicitly planning to work on excluded items. Surface any disagreements before Scope Lock. | EM-confirmed exclusions |
| 5. Finalize Table | PM | Enter finalized exclusions into Scope Contract Section 4. | Scope Contract Section 4 complete |

### 7. Inputs
- Locked Intent Brief (boundaries section from P-003/P-004)
- Deliverable decomposition output from P-007 (items considered but not included)
- Squad roadmaps (to identify implicit expectations)

### 8. Outputs/Artifacts
- **Explicit Exclusions Table** (Section 4 of Scope Contract) — Each row contains: excluded item, reason for exclusion, future home
- Format reference:

| Exclusion | Reason | Future Home |
|-----------|--------|-------------|
| [Item] | [Why excluded] | [Backlog/initiative/team or "Will not be addressed"] |

### 9. Gate/Checkpoint
**Scope Lock Gate (P-013)** — Pass criteria specific to this process:
- All Intent Brief boundaries are present in the Scope Contract
- Exclusions are explicit and acknowledged by all gate participants
- No participant objects to an exclusion without a documented resolution

### 10. Success Criteria
- All Intent Brief boundaries are present in the Scope Contract exclusions
- New exclusions discovered during scoping are added
- Every exclusion has a reason and a future home (or explicit "will not be addressed" designation)
- No EM reports that their squad was implicitly expecting to own excluded work
- The exclusions list is clear enough that any engineer reading it understands what is NOT part of this project

### 11. Dependencies
| Dependency | Process | Type | Detail |
|-----------|---------|------|--------|
| Boundary Definition | P-003 | Hard prerequisite | Intent Brief boundaries are the baseline exclusions |
| Deliverable Decomposition | P-007 | Soft prerequisite | New exclusions are discovered during decomposition; can proceed in parallel |

### 12. Traceability
- **Upstream**: P-003 (Boundary Definition) — baseline exclusions from Intent Brief
- **Upstream**: P-007 (Deliverable Decomposition) — new exclusions discovered during scoping
- **Downstream**: P-013 (Scope Lock Gate) — exclusions acknowledgment is a gate pass criterion
- **Downstream**: P-014 (Scope Change Control) — if excluded items are later added to scope, they go through change control
- **Artifact**: Scope Contract Section 4

---

## P-012: AppSec Scope Review Process

### 1. Process ID and Name
**P-012** — AppSec Scope Review Process

### 2. Purpose
AppSec reviews the Scope Contract for security-relevant deliverables and confirms availability for threat modeling in Sprint 1. Early AppSec engagement prevents security reviews from becoming release blockers. This process embeds security into the scope definition phase rather than treating it as a late-stage gate.

### 3. Derived From
Clarity of Intent — Stage 2: Scope Contract, Assumptions and Risks (AppSec early engagement); Scope Lock gate participant requirements

Relevant source text: "PCI compliance review takes longer than 2 weeks — Risk — MEDIUM — Start review in parallel with development, not after" and Scope Lock participants include "AppSec representative (if security-relevant)."

### 4. Primary Owner Agent
**security-engineer** (AppSec Lead) — Owns the security scope assessment and Sprint 1 availability commitment.

### 5. Supporting Agents
- **product-manager** — Facilitates the review request; flags security-relevant deliverables for AppSec attention

### 6. Stages/Steps

| Step | Actor | Action | Output |
|------|-------|--------|--------|
| 1. Flag Security-Relevant Deliverables | PM | Review the deliverables table (P-007) and flag all deliverables that involve: user data handling, authentication/authorization changes, payment flows, infrastructure changes, new external integrations, PII processing. | Flagged deliverables list |
| 2. AppSec Scope Review | AppSec Lead | Review the full Scope Contract (all 6 sections) with focus on flagged deliverables. Assess: (a) threat surface changes, (b) compliance implications (PCI, SOC2, GDPR, HIPAA as applicable), (c) data flow changes, (d) new attack vectors. | AppSec scope assessment |
| 3. Confirm Sprint 1 Availability | AppSec Lead | Check AppSec team capacity calendar. Confirm availability for threat model review (P-038) during Sprint 1. If unavailable, propose an alternative timeline and document the deferral reason. | Sprint 1 availability confirmation or documented deferral |
| 4. Add Security DoD Criteria | AppSec Lead | For each security-relevant deliverable, verify that Section 3 (DoD) includes security-specific acceptance criteria. Add any missing criteria: threat model completion, SAST/DAST scan requirements, compliance checks, access control verification. | Security DoD additions |
| 5. Sign Off | AppSec Lead | Provide AppSec sign-off for the Scope Lock gate record. Confirm: all security-relevant deliverables identified, Sprint 1 slot confirmed (or deferral documented), security DoD criteria complete. | AppSec sign-off record |

### 7. Inputs
- Scope Contract draft (all 6 sections, from P-007 through P-011)
- AppSec team capacity calendar
- Organizational security policies and compliance requirements
- Existing threat models for affected systems

### 8. Outputs/Artifacts
- **AppSec Scope Assessment** — Document identifying all security-relevant deliverables and their security implications
- **Security-Specific DoD Additions** — Criteria added to Scope Contract Section 3 for security-relevant deliverables
- **Sprint 1 Availability Confirmation** — AppSec commitment to threat model slot in Sprint 1 (or documented deferral with reason)
- **AppSec Sign-Off Record** — Formal record for the Scope Lock gate

### 9. Gate/Checkpoint
**Scope Lock Gate (P-013)** — Pass criteria specific to this process:
- AppSec representative must attend the Scope Lock gate if security-relevant deliverables exist
- All security-relevant deliverables are identified and acknowledged by AppSec
- Sprint 1 threat model slot is confirmed or explicitly deferred with documented reason

### 10. Success Criteria
- All security-relevant deliverables identified and acknowledged by AppSec
- Sprint 1 threat model slot confirmed (or explicitly deferred with documented reason and alternative timeline)
- Security DoD criteria added for all security-relevant deliverables
- No security-relevant deliverable lacks security-specific acceptance criteria
- AppSec sign-off is on record before the Scope Lock gate

### 11. Dependencies
| Dependency | Process | Type | Detail |
|-----------|---------|------|--------|
| Deliverable Decomposition | P-007 | Hard prerequisite | Must know what deliverables exist to assess security relevance |
| Definition of Done Authoring | P-008 | Soft prerequisite | AppSec adds to existing DoD; can work in parallel if deliverables are known |

### 12. Traceability
- **Upstream**: P-007 (Deliverables) and P-008 (DoD) — scope shape determines security assessment scope
- **Downstream**: P-013 (Scope Lock Gate) — AppSec sign-off is a gate input for security-relevant projects
- **Downstream**: P-038 (Threat Modeling, if applicable) — Sprint 1 threat model is a downstream execution activity
- **Downstream**: P-008 (DoD) — security criteria feed back into Section 3
- **Cross-reference**: P-010 (Assumptions/Risks) — security risks feed into Section 6
- **Artifact**: AppSec scope assessment, security DoD additions, Sprint 1 availability confirmation

---

## P-013: Scope Lock Gate Process

### 1. Process ID and Name
**P-013** — Scope Lock Gate Process

### 2. Purpose
A 60-minute structured review confirming all squads understand their deliverables, their Definition of Done, and all exclusions. Upon passage, the Scope Contract is versioned as v1.0 and locked. All subsequent modifications require the Scope Change Control Process (P-014). This gate is the single point where the entire project team aligns on what "done" means before development begins.

### 3. Derived From
Clarity of Intent — Stage 2: Gate: Scope Lock

Relevant source text: "60-minute meeting. The PM presents the Scope Contract. Each section is reviewed. Disagreements are resolved in the room or assigned a 48-hour resolution owner." and "After Scope Lock: The Scope Contract is versioned. Any subsequent scope change requires a formal Scope Change Request."

### 4. Primary Owner Agent
**product-manager** — The PM chairs the gate meeting, presents the Scope Contract, and is responsible for the gate pass/fail decision.

### 5. Supporting Agents
- **engineering-manager** — Engineering Director and all squad EMs attend; EMs confirm their teams' understanding and commitments
- **software-engineer** (Tech Lead) — Validates technical acceptance criteria during the review
- **staff-principal-engineer** — Reviews cross-team architecture implications (if applicable)
- **security-engineer** (AppSec) — Attends if security-relevant deliverables exist; confirms security criteria
- **qa-engineer** (QA Lead) — Confirms testability of DoD criteria

### 6. Stages/Steps

| Step | Actor | Action | Output |
|------|-------|--------|--------|
| 1. Distribute Scope Contract | PM | Distribute the complete Scope Contract (all 6 sections) to all gate participants at least 24 hours before the meeting. Include AppSec scope assessment and QA test strategy as supporting documents. | Pre-read distributed |
| 2. Section-by-Section Review | PM (presenter) | 60-minute meeting. PM presents each of the 6 sections in order. After each section, participants confirm understanding or raise objections. | Section-by-section review record |
| 3. Section 1 Review: Outcome Restatement | All | Confirm the outcome statement matches the locked Intent Brief verbatim. If modifications are needed, they must go back through P-004. | Outcome confirmed or flagged |
| 4. Section 2 Review: Deliverables | All EMs + TL | Confirm every deliverable has a named owner squad. Each EM confirms their squad understands what they are responsible for. | Deliverable ownership confirmed |
| 5. Section 3 Review: Definition of Done | TL + QA + AppSec | Confirm every deliverable has testable DoD criteria. QA confirms testability. AppSec confirms security criteria for relevant deliverables. | DoD completeness confirmed |
| 6. Section 4 Review: Exclusions | All | Confirm exclusions are explicit. All participants acknowledge what is NOT in scope. Surface any disagreements. | Exclusions acknowledged |
| 7. Section 5 Review: Success Metrics | PM + data-engineer + SRE | Confirm metrics trace to Intent Brief outcome. Confirm instrumentation feasibility. | Metrics confirmed |
| 8. Section 6 Review: Assumptions and Risks | PM + TL + TPM | Confirm all HIGH assumptions have validation plans. Confirm all risks have mitigation owners. | Risk register confirmed |
| 9. Resolve Disagreements | PM (facilitator) | Any disagreements are resolved in the room. If resolution is not possible in the meeting, assign a resolution owner with a 48-hour deadline. | Resolution assignments (if any) |
| 10. Gate Decision | PM | Record PASS or FAIL. If PASS: Scope Contract versioned as v1.0 and locked. If FAIL: document specific revisions required, assign owners, and schedule re-review. | Gate decision record |
| 11. Squad Commitment | All EMs | Each EM records: "My team understands what we are responsible for and what done looks like." | Written squad commitments |

### 7. Inputs
- Complete Scope Contract (6 sections from P-007 through P-011)
- AppSec scope review output (P-012)
- QA test strategy
- All supporting agents' sign-offs

### 8. Outputs/Artifacts
- **Gate Decision Record** — PASS or FAIL with documented rationale
- **Locked and Versioned Scope Contract v1.0** (if PASS) — The authoritative, immutable version of the Scope Contract
- **Revision Requirements** (if FAIL) — Specific items that must be fixed, with assigned owners and deadlines
- **Squad Commitment Records** — Written confirmations from each EM
- **Resolution Assignments** — Any 48-hour resolution items with owners

### 9. Gate/Checkpoint
**This IS the gate.** Binary pass criteria (ALL must be met):

| # | Criterion | Verified By |
|---|-----------|-------------|
| 1 | Every deliverable has a named owner squad | EMs |
| 2 | Every deliverable has a written DoD with testable criteria | TL + QA |
| 3 | Exclusions are explicit and acknowledged by all parties | All participants |
| 4 | Success metrics trace to the Intent Brief outcome | PM |
| 5 | All HIGH assumptions have validation plans with owners and deadlines | PM + TL |
| 6 | Every participant confirms: "My team understands what we are responsible for and what done looks like" | All EMs |

If ANY criterion is not met, the gate FAILS. Failure is not punitive — it means the Scope Contract is not yet clear enough to build on.

### 10. Success Criteria
- Gate passes with all six binary criteria confirmed
- No participant leaves the meeting without confirming their squad's responsibilities
- All disagreements are resolved or assigned with an owner and 48-hour deadline before the gate closes
- Scope Contract is versioned as v1.0 and stored in the project repository
- All participants can explain what their team is building and what done looks like

### 11. Dependencies
| Dependency | Process | Type | Detail |
|-----------|---------|------|--------|
| Deliverable Decomposition | P-007 | Hard prerequisite | Section 2 must be complete |
| Definition of Done Authoring | P-008 | Hard prerequisite | Section 3 must be complete |
| Success Metrics Definition | P-009 | Hard prerequisite | Section 5 must be complete |
| Assumptions/Risks Registration | P-010 | Hard prerequisite | Section 6 must be complete |
| Exclusion Documentation | P-011 | Hard prerequisite | Section 4 must be complete |
| AppSec Scope Review | P-012 | Hard prerequisite (if security-relevant) | AppSec sign-off must be on record |

### 12. Traceability
- **Upstream**: All Category 2 processes (P-007 through P-012) — their outputs compose the Scope Contract
- **Upstream**: P-004 (Intent Review Gate) — the Intent Brief is the foundation the Scope Contract builds on
- **Downstream**: P-014 (Scope Change Control) — all post-lock changes go through this process
- **Downstream**: P-015 through P-019 (Category 3: Dependency & Coordination) — Scope Lock is a prerequisite for dependency mapping
- **Downstream**: P-020 through P-026 (Category 4: Sprint Bridge) — Scope Lock is a prerequisite for sprint planning
- **Artifact**: Locked Scope Contract v1.0

---

## P-014: Scope Change Control Process

### 1. Process ID and Name
**P-014** — Scope Change Control Process

### 2. Purpose
A 4-step (Raise, Assess, Decide, Update) process for any modification to the Scope Contract after Scope Lock. The PM is the sole gatekeeper for scope changes. This process ensures that scope changes are visible, deliberate, and traceable — not silent. The goal is not to prevent change but to make change controlled. Silent scope changes are the most common cause of delivery failure.

### 3. Derived From
Clarity of Intent — Change Control: When Scope Needs to Change

Relevant source text: "Any team member can identify a scope change need. Only the PM can approve a change to the Scope Contract. All changes go through this process" and "The one rule: No silent scope changes."

### 4. Primary Owner Agent
**product-manager** — The PM is the sole gatekeeper for scope changes. PM decides for within-boundary changes. Engineering Director decides for scope expansion or changes impacting more than one sprint.

### 5. Supporting Agents
- **software-engineer** (Tech Lead) — Assesses technical impact of proposed changes on deliverables, DoD, and timeline
- **technical-program-manager** — Assesses cross-squad impact of proposed changes; evaluates dependency implications
- **engineering-manager** (Director) — Approves scope expansion or changes with impact exceeding one sprint

### 6. Stages/Steps

| Step | Actor | Action | Output |
|------|-------|--------|--------|
| **STEP 1: RAISE** | Any team member | Document the change request using the 4-field Scope Change Request form: (1) What is changing? — specific deliverables being added, removed, or modified; (2) Why is it changing? — new information, technical discovery, market shift, or dependency failure; (3) What is the impact? — effect on timeline, other deliverables, dependencies, success metrics; (4) What is the recommendation? — accept, reject, or defer. | Scope Change Request (SCR) document |
| **STEP 2: ASSESS** | PM + TL | PM and TL review the SCR. Evaluate: (a) impact on existing deliverables and their DoD, (b) impact on timeline, (c) impact on success metrics, (d) impact on dependencies. If the change affects other squads, the TPM is consulted for cross-team impact assessment. | Impact assessment |
| **STEP 3: DECIDE** | PM or Director | Decision authority depends on scope of change: PM decides for changes within the existing scope boundary (modifications to existing deliverables, minor additions). Engineering Director decides for changes that expand the scope boundary or affect the timeline by more than one sprint. Decision recorded: APPROVED, REJECTED, or DEFERRED. | SCR decision record |
| **STEP 4: UPDATE** | PM | If APPROVED: (a) Version the Scope Contract (v1.1, v1.2, etc.) with the change documented, (b) update affected sections (deliverables, DoD, exclusions, metrics, risks as applicable), (c) communicate the change to all affected squads within 1 business day. If REJECTED or DEFERRED: document the rationale and communicate to the requester. | Updated Scope Contract (new version) or documented rejection |

### 7. Inputs
- **Scope Change Request** — 4-field form completed by the requesting team member
- **Current Scope Contract version** — The latest locked version (v1.0, v1.1, etc.)
- **Active sprint plan** — To assess timeline impact
- **Dependency Charter** (if it exists at this point) — To assess dependency impact

### 8. Outputs/Artifacts
- **Scope Change Request Decision Record** — Documents: the request, the assessment, the decision (APPROVED/REJECTED/DEFERRED), and the rationale
- **Updated and Versioned Scope Contract** (if APPROVED) — New version number (v1.1, v1.2, etc.) with change log entry
- **Communication Record** — Confirmation that all affected squads were notified within 1 business day

Scope Change Request form:

| Field | Content |
|-------|---------|
| What is changing? | Specific deliverable(s) being added, removed, or modified |
| Why is it changing? | New information, technical discovery, market shift, or dependency failure |
| What is the impact? | Effect on timeline, other deliverables, dependencies, and success metrics |
| What is the recommendation? | Accept the change, reject it, or defer it to a future project |

### 9. Gate/Checkpoint
- **Director Approval Gate**: Required when the change expands the scope boundary or impacts the timeline by more than one sprint
- **No Silent Changes Rule**: Any scope modification discovered without a corresponding SCR triggers a retroactive change request and is raised as a retrospective item

### 10. Success Criteria
- Every scope change is formally documented regardless of size
- No deliverable is modified without a versioned Scope Contract update
- All affected squads are notified within 1 business day of approval
- No silent scope changes — any undocumented change discovered triggers a retroactive change request and retrospective item
- Decision authority is correctly applied (PM for within-boundary, Director for expansion/multi-sprint impact)
- Scope Contract version history provides a complete audit trail of all changes

### 11. Dependencies
| Dependency | Process | Type | Detail |
|-----------|---------|------|--------|
| Scope Lock Gate | P-013 | Hard prerequisite | This process only applies after the Scope Contract is locked at v1.0 |
| Active sprint plan | Sprint Bridge processes | Informational | Needed to assess timeline impact of changes |

### 12. Traceability
- **Upstream**: P-013 (Scope Lock Gate) — this process governs all post-lock modifications
- **Downstream**: All execution processes — approved changes flow into sprint planning, dependency updates, and delivery tracking
- **Cross-reference**: P-010 (Assumptions/Risks) — scope changes may introduce new risks that must be registered
- **Cross-reference**: P-015 (Dependency Registration) — scope changes may create or modify dependencies
- **Audit trail**: Scope Contract version history (v1.0, v1.1, v1.2...) provides complete change traceability
- **Retrospective**: Undocumented scope changes are flagged as retrospective items per the "no silent changes" rule
- **Artifact**: Scope Change Request records, versioned Scope Contract

---

## Cross-Category Interface Map

### Incoming Interfaces (from other categories)

| Source Process | Source Category | What It Provides | Consumed By |
|---------------|----------------|-----------------|-------------|
| P-001 (Intent Articulation) | Cat 1: Intent & Strategic Alignment | Intent Brief with outcome, beneficiaries, boundaries | P-007, P-009, P-011 |
| P-003 (Boundary Definition) | Cat 1: Intent & Strategic Alignment | Explicit exclusions from Intent Brief | P-011 |
| P-004 (Intent Review Gate) | Cat 1: Intent & Strategic Alignment | Locked Intent Brief (gate PASS) | P-007 (hard prerequisite for entire category) |

### Outgoing Interfaces (to other categories)

| Source Process | Target Process | Target Category | What It Provides |
|---------------|---------------|----------------|-----------------|
| P-013 (Scope Lock Gate) | P-015 (Dependency Registration) | Cat 3: Dependency & Coordination | Locked Scope Contract with deliverables and owner squads |
| P-013 (Scope Lock Gate) | P-020+ (Sprint Bridge) | Cat 4: Sprint Bridge | Deliverables and DoD for sprint decomposition |
| P-010 (Assumptions/Risks) | P-074 (RAID Log) | Cat 12: Monitoring & Reporting | Initial RAID Log entries |
| P-012 (AppSec Scope Review) | P-038 (Threat Modeling) | Cat 6: Security Processes | Sprint 1 threat model commitment |
| P-009 (Success Metrics) | Post-launch measurement | Cat 15: Outcome Measurement | Success metrics for post-launch evaluation |

---

## Timing Guide

| Process | Typical Duration | Can Overlap With | Blocker If Late |
|---------|-----------------|-----------------|-----------------|
| P-007: Deliverable Decomposition | 1-2 days | First activity after P-004 passes | All downstream processes blocked |
| P-008: Definition of Done Authoring | 1-2 days | P-009, P-011 (parallel) | P-013 gate cannot pass |
| P-009: Success Metrics Definition | 0.5-1 day | P-008, P-011 (parallel) | P-013 gate cannot pass |
| P-010: Assumptions/Risks Registration | 0.5-1 day | P-011, P-012 (parallel) | P-013 gate cannot pass |
| P-011: Exclusion Documentation | 0.5-1 day | P-008, P-009, P-010 (parallel) | P-013 gate cannot pass |
| P-012: AppSec Scope Review | 1-2 days | P-009, P-010, P-011 (parallel) | P-013 gate cannot pass (if security-relevant) |
| P-013: Scope Lock Gate | 60 minutes (meeting) | Nothing — requires all above complete | Category 3 blocked |
| P-014: Scope Change Control | As needed (ongoing) | Runs throughout project lifecycle | N/A — reactive process |

**Total elapsed time for P-007 through P-013**: 3-5 working days (consistent with Clarity of Intent Stage 2 timeline)

---

## Appendix: Scope Contract Template Structure

For reference, the Scope Contract produced by processes P-007 through P-012 and locked by P-013 has the following structure:

```
SCOPE CONTRACT v[X.Y]
Project: [Name]
Date: [Lock date]
Locked By: [PM name at P-013 gate]

Section 1: Outcome Restatement
  [Verbatim copy from Intent Brief — P-001]

Section 2: Deliverables (P-007)
  [Table: ID | Deliverable | Description | Owner Squad]

Section 3: Definition of Done (P-008)
  [Table: Deliverable | Done When (binary criteria)]

Section 4: Explicit Exclusions (P-011)
  [Table: Exclusion | Reason | Future Home]

Section 5: Success Metrics (P-009)
  [Table: Metric | Baseline | Target | Measurement Method | Timeline]

Section 6: Assumptions and Risks (P-010)
  [Table: Item | Type | Severity | Mitigation/Validation | Owner]

Change Log (P-014 — post-lock only)
  [Table: Version | Date | Change | Approved By | Reason]
```

---

## Cross-Category Dependencies

### Dependencies FROM Other Categories (Inputs)

| Source Process | Source Category | Consuming Process | Nature |
|---------------|----------------|-------------------|--------|
| P-004 (Intent Review Gate) | Cat 1: Intent & Strategic Alignment | P-007 (Deliverable Decomposition) | Locked Intent Brief required |
| P-003 (Boundary Definition) | Cat 1: Intent & Strategic Alignment | P-011 (Exclusion Documentation) | Intent Brief boundaries carried forward |

### Dependencies TO Other Categories (Outputs)

| Providing Process | Consuming Process | Target Category | Nature |
|------------------|-------------------|-----------------|--------|
| P-013 (Scope Lock Gate) | P-015 (Cross-Team Dependency Registration) | Cat 3: Dependency & Coordination | Scope Contract locked before dependency mapping |
| P-013 (Scope Lock Gate) | P-022 (Sprint Goal Authoring) | Cat 4: Sprint & Delivery | Scope Contract deliverables drive sprint goals |
| P-013 (Scope Lock Gate) | P-032 (Test Architecture Design) | Cat 5: Quality Assurance | Deliverables and DoD define test targets |
| P-013 (Scope Lock Gate) | P-073 (Post-Launch Outcome Measurement) | Cat 12: Post-Delivery | Success metrics defined in Scope Contract |
| P-012 (AppSec Scope Review) | P-038 (Threat Modeling) | Cat 6: Security & Compliance | AppSec availability confirmed for Sprint 1 |
| P-010 (Assumptions and Risks) | P-074 (RAID Log Maintenance) | Cat 13: Risk & Change | RAID Log seeded from Scope Contract |
| P-007 (Deliverable Decomposition) | P-075 (Risk Register at Scope Lock) | Cat 13: Risk & Change | Scope shape needed for risk identification |

## Agent Assignments Summary

| Process | Primary Owner | Supporting Agents |
|---------|--------------|-------------------|
| P-007: Deliverable Decomposition | product-manager | software-engineer (TL), staff-principal-engineer |
| P-008: Definition of Done Authoring | product-manager | software-engineer (TL), qa-engineer, security-engineer |
| P-009: Success Metrics Definition | product-manager | data-engineer, sre |
| P-010: Assumptions and Risks Registration | product-manager | software-engineer (TL), technical-program-manager, security-engineer |
| P-011: Exclusion Documentation | product-manager | engineering-manager |
| P-012: AppSec Scope Review | security-engineer | product-manager |
| P-013: Scope Lock Gate | product-manager | engineering-manager, software-engineer, staff-principal-engineer, security-engineer, qa-engineer |
| P-014: Scope Change Control | product-manager | software-engineer (TL), technical-program-manager, engineering-manager |
