# Technical Specification: Dependency & Coordination Management Processes (P-015 to P-021)

**Session**: auto-orc-20260405-procderive
**Date**: 2026-04-05
**Stage**: 2 — Process Specification
**Category**: 3 — Dependency & Coordination Management
**Source**: Process Architecture (Stage 1), Clarity of Intent (Stage 3: Dependency Map), Engineering Team Structure Guide
**Processes Covered**: P-015, P-016, P-017, P-018, P-019, P-020, P-021

> **Quick Reference**: A lightweight stub version is available at `processes/process_stubs/dependency_coordination_stub.md`

---

## Category Overview

Dependency & Coordination Management encompasses all processes that identify, document, negotiate, and track cross-team dependencies before and during development. These processes collectively produce the Dependency Charter artifact — the single source of truth for who depends on whom, what is needed, by when, and what happens when things go wrong. The Dependency Charter has four sections (Dependency Register, Shared Resource Conflicts, Critical Path, Communication Protocol), is 2-4 pages, and is owned by the TPM and primary squad TL.

All seven processes in this category derive from Clarity of Intent Stage 3 (Dependency Map) and the organizational escalation hierarchy. The category begins after the Scope Lock Gate (P-013) passes and the pre-sprint processes conclude when the Dependency Acceptance Gate (P-019) locks commitments. Post-gate, the Dependency Standup (P-020) and Dependency Escalation (P-021) processes govern ongoing tracking and blocker resolution throughout active sprints.

### Process Dependency Graph (Internal to Category)

```
P-013 (Scope Lock Gate — EXTERNAL prerequisite)
  |
  v
P-015: Cross-Team Dependency Registration
  |
  +---> P-016: Critical Path Analysis (requires P-015)
  |
  +---> P-017: Shared Resource Conflict Resolution (requires P-015)
  |
  +---> P-018: Communication Protocol Establishment (requires P-015)
  |
  v
P-019: Dependency Acceptance Gate (requires P-015, P-016, P-017, P-018)
  |
  v  (after Sprint Readiness Gate P-025 passes)
P-020: Dependency Standup (ongoing during active sprints)
  |
  v  (triggered by blocked dependency >48 hours)
P-021: Dependency Escalation
```

Note: P-016, P-017, and P-018 can execute in parallel once P-015 is complete. P-019 is a convergence gate requiring all four upstream processes. P-020 and P-021 are runtime processes that operate during active sprints.

### Agent Involvement Summary

| Agent ID | Processes (Primary) | Processes (Supporting) |
|----------|-------------------|----------------------|
| technical-program-manager | P-015, P-016, P-017, P-018, P-019, P-020, P-021 | — |
| software-engineer (Tech Lead) | — | P-015, P-016, P-019, P-020 |
| engineering-manager | — | P-015, P-017, P-018, P-019, P-021 |
| staff-principal-engineer | — | P-016 |
| product-manager | — | P-018, P-019 |
| infra-engineer | — | P-017 |
| infra-engineer | — | P-017 |

---

## P-015: Cross-Team Dependency Registration Process

### 1. Process ID and Name
**P-015** — Cross-Team Dependency Registration Process

### 2. Purpose
Enumerate all inter-team, external, and shared-resource dependencies in a structured register before development begins. Every connection between teams, every shared service, every external system, and every person or approval process that could block progress is documented with an owner, a deadline, a current status, and an escalation path. This process makes invisible dependencies visible. Undocumented dependencies discovered after Sprint 1 are the most expensive form of rework.

### 3. Derived From
Clarity of Intent — Stage 3: Dependency Map, Section 1 (Dependency Register)

Relevant source text: "The TPM and TL take the Scope Contract's deliverables and owner assignments and trace every connection between teams, every shared service, every external system, and every person or approval process that could block progress." and "Every dependency gets a row. No dependency is too small to document if it could block a sprint."

### 4. Primary Owner Agent
**technical-program-manager** — The TPM owns the Dependency Register, facilitates dependency discovery sessions with all squad TLs, and ensures completeness. The TPM's coordination-first perspective (TPM-001) and cross-team scope (3-10 teams) make this a natural fit.

### 5. Supporting Agents
- **software-engineer** (Tech Lead) — Each squad's TL identifies technical dependencies: API contracts, shared libraries, data schemas, infrastructure prerequisites, integration points. The TL's single-team technical depth surfaces dependencies that cross-team coordination alone would miss.
- **engineering-manager** — Each squad's EM validates that capacity exists to fulfill dependency commitments. The EM's people-first perspective (EM-001) ensures dependency timelines align with actual team availability, not aspirational availability.

### 6. Stages/Steps

| Step | Actor | Action | Output |
|------|-------|--------|--------|
| 1. Review Scope Contract Deliverables | TPM + Primary TL | Read the locked Scope Contract (P-013 output). Extract all deliverables and their owner squads. Map which deliverables consume outputs from other deliverables — these are dependency candidates. | Preliminary dependency candidate list |
| 2. Conduct Dependency Discovery Sessions | TPM + All Squad TLs | TPM meets with each squad TL (30 min per squad). For each deliverable the squad owns, TL identifies: (a) what the squad needs from other squads, (b) what the squad provides to other squads, (c) external systems or vendors required, (d) shared services (AppSec, Platform, Data Eng) needed. | Raw dependency list from all squads |
| 3. Consolidate and Deduplicate | TPM | Merge all squad dependency lists. Deduplicate (Squad A's "need from B" should match Squad B's "provide to A"). Flag mismatches — where one squad expects a dependency the other squad is unaware of. | Consolidated dependency list |
| 4. Assign Dependency IDs and Metadata | TPM | For each dependency, assign: unique ID (D1, D2...), dependent team, depended-on team, what is needed (specific artifact or deliverable), by-when date, initial status (Not Started / In Progress / Blocked / Complete), named owner. | Structured Dependency Register rows |
| 5. Define Escalation Paths | TPM + EMs | For each dependency, define the escalation path: owner → EM → Director → VP. The escalation path follows the organizational hierarchy of the depended-on team (not the dependent team). | Escalation paths per dependency |
| 6. Mark External Dependencies | TPM | Explicitly mark all external dependencies (vendor, third-party, regulatory body). External dependencies require a different escalation path (PM → VP Product) since they are outside engineering's control. | External dependencies flagged |
| 7. EM Capacity Validation | All Squad EMs | Each EM reviews the dependencies their squad must fulfill. Confirm that the stated "by when" dates are achievable given current team capacity and competing commitments. Flag any over-commitment. | Capacity-validated dependency dates |
| 8. Finalize Dependency Register | TPM | Enter the final Dependency Register into Dependency Charter Section 1. | Dependency Charter Section 1 complete |

### 7. Inputs
- Locked Scope Contract (output of P-013 Scope Lock Gate) — deliverables table, owner squads, Definition of Done, assumptions/risks
- Organizational squad map (Engineering Team Structure Guide) — team boundaries, reporting lines, shared service teams
- Team capacity data (sprint velocity, planned leave, competing project commitments)
- External vendor/partner contact information and contract SLAs

### 8. Outputs/Artifacts
- **Dependency Register** (Section 1 of Dependency Charter) — Each row contains: dependency ID, dependent team, depended-on team, what is needed, by-when date, status, named owner, escalation path
- Format reference:

| ID | Dependent Team | Depends On | What Is Needed | By When | Status | Owner | Escalation Path |
|----|---------------|------------|----------------|---------|--------|-------|-----------------|
| D1 | [Team A] | [Team B] | [Specific artifact/API/deliverable needed] | [Sprint X start/end] | [Not Started / In Progress / Blocked / Complete] | [Named person, typically TL or EM] | [Owner → EM → Director → VP] |

### 9. Gate/Checkpoint
**Dependency Acceptance Gate (P-019)** — The Dependency Register is reviewed as part of the full Dependency Charter. Pass criteria specific to this process:
- Every dependency has a named owner and a "needed by" date
- Every dependency has a current status and an escalation path
- External dependencies are explicitly marked as external with appropriate escalation paths
- No dependency has been claimed by one squad but is unknown to the depended-on squad (no mismatches)

### 10. Success Criteria
- No dependency is undocumented — TPM has confirmed completeness with all squad TLs involved in the project
- Every dependency has a named owner, "needed by" date, current status, and escalation path
- External dependencies (vendor, third-party) are explicitly marked as external with PM-led escalation paths
- Every EM has validated that their squad's dependency commitments are achievable given current capacity
- The Dependency Register can be read by any engineer on the project and understood without additional context
- Zero dependency mismatches between squads (what Squad A expects from Squad B matches what Squad B has committed to)

### 11. Dependencies
| Dependency | Process | Type | Detail |
|-----------|---------|------|--------|
| Scope Lock Gate passed | P-013 | Hard prerequisite | Cannot register dependencies without a locked Scope Contract defining deliverables and owner squads |
| Deliverable Decomposition | P-007 | Informational | The deliverables table is the primary input; consumed via the Scope Contract |
| Assumptions & Risks Register | P-010 | Informational | Known risks from Scope Contract Section 6 may surface dependency-related risks |

### 12. Traceability
- **Upstream**: Scope Contract (P-007 through P-013) — deliverables and owner squads are the dependency discovery targets
- **Downstream**: P-016 (Critical Path Analysis) — uses the complete register to compute the critical path
- **Downstream**: P-017 (Shared Resource Conflict Resolution) — register identifies resource conflicts
- **Downstream**: P-018 (Communication Protocol) — register determines which teams need to communicate
- **Downstream**: P-019 (Dependency Acceptance Gate) — register is a mandatory input
- **Downstream (runtime)**: P-020 (Dependency Standup) — statuses are updated against the register
- **Downstream (runtime)**: P-021 (Dependency Escalation) — escalation paths come from the register
- **Artifact**: Dependency Charter Section 1

---

## P-016: Critical Path Analysis Process

### 1. Process ID and Name
**P-016** — Critical Path Analysis Process

### 2. Purpose
Identify the sequence of dependencies that determines the project's minimum timeline. If any item on the critical path slips, the entire project slips. Non-critical items have float — they can slip without affecting the overall timeline. Without critical path analysis, teams optimize the wrong dependencies and discover timeline impacts too late.

### 3. Derived From
Clarity of Intent — Stage 3: Dependency Map, Section 3 (Critical Path)

Relevant source text: "Identify the sequence of dependencies that determines the project's minimum timeline. If any item on the critical path slips, the entire project slips." and "The critical path tells every team what matters most and what they cannot afford to delay. Items not on the critical path have float — they can slip without affecting the overall timeline."

### 4. Primary Owner Agent
**technical-program-manager** — The TPM maps the dependency graph and identifies the longest chain. This requires the TPM's cross-team visibility (TPM-001) and milestone tracking expertise.

### 5. Supporting Agents
- **software-engineer** (Tech Lead) — Validates technical sequencing: confirms that the proposed dependency ordering reflects actual technical constraints (e.g., API must exist before integration can begin), not just scheduling preferences
- **staff-principal-engineer** — Reviews cross-org sequencing for architectural risks: validates that the critical path respects system boundaries, identifies hidden coupling, and flags architectural bottlenecks that could invalidate the timeline

### 6. Stages/Steps

| Step | Actor | Action | Output |
|------|-------|--------|--------|
| 1. Build Dependency Graph | TPM + Primary TL | Take the complete Dependency Register (P-015 output) and map all dependencies as a directed acyclic graph (DAG). Each node is a deliverable; each edge is a dependency with a duration estimate. | Dependency DAG |
| 2. Identify Critical Path | TPM | Compute the longest path through the DAG from project start to completion. This is the critical path — the minimum possible project duration. | Critical path sequence |
| 3. Calculate Float | TPM | For each non-critical path item, calculate the maximum slip that would not delay the project. Float = difference between the item's latest allowable completion and earliest possible completion. | Float schedule for all non-critical items |
| 4. Technical Sequencing Validation | Primary TL + Squad TLs | Each TL reviews the dependency ordering on the critical path for their squad's deliverables. Confirm the sequencing reflects actual technical constraints. Flag any dependency that could be parallelized or reordered. | Validated critical path |
| 5. Architectural Risk Review | staff-principal-engineer | Review the critical path for architectural risks: hidden coupling, system boundary violations, single points of failure, shared infrastructure bottlenecks. | Architectural risk assessment for critical path |
| 6. Set Escalation Trigger Dates | TPM | For each item on the critical path, set an escalation trigger date — the date by which, if the item is not on track, escalation (P-021) must begin. Trigger date = "needed by" date minus buffer (typically 2-3 business days). | Escalation trigger dates for critical path items |
| 7. Document Critical Path | TPM | Document the critical path in narrative and visual form in Dependency Charter Section 3. Include: sequence diagram, float schedule, escalation trigger dates. | Dependency Charter Section 3 complete |

### 7. Inputs
- Complete Dependency Register (P-015 output — Dependency Charter Section 1)
- Deliverable duration estimates from squad TLs
- Sprint calendar and milestone dates

### 8. Outputs/Artifacts
- **Critical Path Diagram** (Section 3 of Dependency Charter) — Visual representation of the longest dependency chain from project start to completion
- **Float Schedule** — For each non-critical item: item name, earliest completion, latest allowable completion, float (in days/sprints)
- **Escalation Trigger Dates** — For each critical path item: the date by which escalation must begin if the item is not on track
- Format reference (narrative form):

```
[External/Internal]: [First dependency item]
  → [Team]: [Deliverable] (Duration: X days)
    → [Team]: [Deliverable] (Duration: Y days)
      → [Team]: [Deliverable] (Duration: Z days)
        → [Final integration/release milestone]

Total critical path duration: X+Y+Z days
```

### 9. Gate/Checkpoint
**Dependency Acceptance Gate (P-019)** — Pass criteria specific to this process:
- Critical path is documented in narrative and visual form
- Critical path is understood by all parties (each team on the critical path acknowledges their position)
- Every critical path item has an escalation trigger date
- Non-critical items have documented float

### 10. Success Criteria
- Critical path documented and all teams on the critical path acknowledge their position and responsibility
- Every item on the critical path has an escalation trigger date (not just a "needed by" date)
- Non-critical items have documented float values
- Technical sequencing has been validated by relevant TLs (no dependency ordering that contradicts technical reality)
- Architectural risks on the critical path have been reviewed by staff-principal-engineer
- The critical path can be explained to any engineer in one paragraph

### 11. Dependencies
| Dependency | Process | Type | Detail |
|-----------|---------|------|--------|
| Dependency Register complete | P-015 | Hard prerequisite | Cannot compute critical path without the complete dependency graph |
| Deliverable duration estimates | Squad TLs | Informational | Duration estimates needed for path length calculation; obtained during P-015 discovery sessions or separately |

### 12. Traceability
- **Upstream**: P-015 (Dependency Register) — the register is the input graph for path analysis
- **Downstream**: P-019 (Dependency Acceptance Gate) — critical path documentation is a gate pass criterion
- **Downstream (runtime)**: P-020 (Dependency Standup) — critical path items get priority attention in standups
- **Downstream (runtime)**: P-021 (Dependency Escalation) — escalation trigger dates drive escalation timing
- **Cross-reference**: P-017 (Shared Resource Conflicts) — resource conflicts on the critical path are highest priority for resolution
- **Artifact**: Dependency Charter Section 3

---

## P-017: Shared Resource Conflict Resolution Process

### 1. Process ID and Name
**P-017** — Shared Resource Conflict Resolution Process

### 2. Purpose
Identify and resolve competing demands on shared resources — environments, infrastructure, people (AppSec, Platform, Data Engineering, SRE) — before development begins. Unresolved resource conflicts become Sprint 1 blockers. This process prevents the common failure mode where multiple deliverables assume exclusive access to the same shared resource at the same time.

### 3. Derived From
Clarity of Intent — Stage 3: Dependency Map, Section 2 (Shared Resource Conflicts)

Relevant source text: "Identify any shared resources (people, environments, infrastructure) that multiple deliverables compete for." with resolution examples including "Provision a second staging namespace on shared cluster" and "Timebox threat model to 3 days in Sprint 1; AppSec Lead to backfill."

### 4. Primary Owner Agent
**technical-program-manager** — The TPM identifies conflicts across the full project scope and facilitates resolution negotiations between competing squads. This requires TPM's cross-team coordination mandate (TPM-001).

### 5. Supporting Agents
- **engineering-manager** — EMs for affected squads negotiate priority and time-sharing arrangements for people resources. The EM's capacity planning expertise (EM-006 data-driven) ensures negotiations are grounded in real availability data.
- **infra-engineer** — Resolves environment and CI/CD conflicts: staging namespace provisioning, shared pipeline contention, developer tooling access. Platform-engineer BUILDS the platform infrastructure that resolves environment conflicts.
- **infra-engineer** — Resolves infrastructure conflicts: compute capacity, shared cluster resources, cloud account access, network configuration. Cloud-engineer PROVISIONS the underlying infrastructure needed to eliminate infrastructure contention.

### 6. Stages/Steps

| Step | Actor | Action | Output |
|------|-------|--------|--------|
| 1. Identify Shared Resources | TPM | Scan the Dependency Register (P-015 output) for shared resources: staging environments, CI/CD pipelines, AppSec engineer time, Platform team bandwidth, Data Engineering capacity, SRE support, shared test infrastructure. | Shared resource inventory |
| 2. Map Competing Demands | TPM + Squad TLs | For each shared resource, identify which deliverables compete for it and when. Map the time overlap: does Squad A need staging in Sprint 1 at the same time Squad B needs staging? | Resource conflict matrix |
| 3. Classify Conflict Severity | TPM | Classify each conflict: (a) Critical — on the critical path (P-016); unresolved will delay the project, (b) High — not on critical path but will block a sprint goal, (c) Medium — causes inconvenience or rework but has workarounds. | Severity-classified conflicts |
| 4. Propose Resolutions | TPM + Supporting Agents | For each conflict, propose a resolution. Common patterns: parallel provisioning (infra-engineer provisions additional environment), time-slicing (EM negotiates staggered access), scope adjustment (PM defers non-critical work), capacity augmentation (infra-engineer provisions additional infrastructure). | Proposed resolution per conflict |
| 5. Validate Resolutions with Owners | TPM + Resolution Owners | Each proposed resolution owner confirms feasibility and timeline. For environment provisioning: infra-engineer confirms it can be done by the stated deadline. For people conflicts: EM confirms the negotiated time allocation is real. | Feasibility-validated resolutions |
| 6. Document in Dependency Charter | TPM | Enter the final shared resource conflicts and resolutions into Dependency Charter Section 2. | Dependency Charter Section 2 complete |

### 7. Inputs
- Dependency Register (P-015 output — Dependency Charter Section 1)
- Critical Path analysis (P-016 output — for severity classification)
- Resource availability calendars (team capacity, environment availability, shared service bandwidth)
- Infrastructure inventory (existing environments, clusters, shared services)

### 8. Outputs/Artifacts
- **Shared Resource Conflicts Table** (Section 2 of Dependency Charter) — Each row contains: resource name, competing demands (which deliverables/squads), resolution, resolution owner, resolution deadline
- Format reference:

| Resource | Competing Demands | Resolution | Owner | Deadline |
|----------|------------------|------------|-------|----------|
| [Resource name] | [Squad A needs X; Squad B needs Y; overlap in Sprint Z] | [Specific resolution: provision, time-slice, defer, augment] | [Named person/team] | [Date by which resolution must be in place] |

### 9. Gate/Checkpoint
**Dependency Acceptance Gate (P-019)** — Pass criteria specific to this process:
- All shared resource conflicts have a documented resolution
- Resolution owners have confirmed feasibility
- No conflict is marked "TBD" without an owner and a deadline for resolution
- Critical-path conflicts (highest severity) are resolved, not just planned

### 10. Success Criteria
- Every shared resource conflict has a documented resolution with a named owner and deadline
- Resolution owners have confirmed feasibility (not just acknowledged the conflict)
- No conflict is marked "TBD" without an owner and deadline
- Critical-path conflicts are fully resolved before the Dependency Acceptance Gate
- Platform-engineer and infra-engineer have confirmed environment/infrastructure resolutions are technically feasible
- EMs have confirmed people-resource time allocations are real (no over-commitment)

### 11. Dependencies
| Dependency | Process | Type | Detail |
|-----------|---------|------|--------|
| Dependency Register complete | P-015 | Hard prerequisite | Cannot identify resource conflicts without the dependency graph |
| Critical Path Analysis | P-016 | Soft prerequisite | Severity classification benefits from knowing which conflicts are on the critical path; can proceed in parallel with preliminary severity estimates |

### 12. Traceability
- **Upstream**: P-015 (Dependency Register) — register identifies which teams share resources
- **Upstream**: P-016 (Critical Path) — critical path determines which conflicts have highest severity
- **Downstream**: P-019 (Dependency Acceptance Gate) — all conflicts must have resolutions for the gate to pass
- **Downstream (runtime)**: P-020 (Dependency Standup) — unresolved or newly discovered conflicts are surfaced
- **Cross-reference**: P-083 (Shared Resource Allocation) — P-017 identifies conflicts that P-083 resolves through formal allocation negotiation at the Director level
- **Artifact**: Dependency Charter Section 2

---

## P-018: Communication Protocol Establishment Process

### 1. Process ID and Name
**P-018** — Communication Protocol Establishment Process

### 2. Purpose
Define how dependency status will be tracked and communicated throughout the project: standup cadence, RAID log update frequency, escalation triggers, and participation requirements. Without a defined communication protocol, blockers surface too late, status information is inconsistent, and escalation happens ad hoc rather than through defined channels.

### 3. Derived From
Clarity of Intent — Stage 3: Dependency Map, Section 4 (Communication Protocol)

Relevant source text: "Define how dependency status will be tracked and communicated throughout the project." with three mechanisms: "Dependency standup — Twice weekly, 15 min", "RAID log update — Weekly", and "Escalation trigger — Any dependency blocked for > 48 hours with no resolution path."

### 4. Primary Owner Agent
**technical-program-manager** — The TPM proposes and owns the communication protocol. This aligns with the TPM's RAID log ownership and dependency board management responsibilities.

### 5. Supporting Agents
- **engineering-manager** — EMs agree to participation commitments for their squads (TL attendance at dependency standups, EM availability for escalation). The EM validates that the communication cadence is sustainable given existing meeting load.
- **product-manager** — PM agrees to provide business context updates at dependency standups and confirms availability for escalation decisions that require business prioritization.

### 6. Stages/Steps

| Step | Actor | Action | Output |
|------|-------|--------|--------|
| 1. Propose Communication Cadence | TPM | Based on project complexity and number of squads involved, propose: (a) Dependency standup cadence (default: twice-weekly, 15 min), (b) RAID log update cadence (default: weekly by TPM), (c) Escalation trigger definition (default: dependency blocked >48 hours with no resolution path). Adjust defaults based on project risk: higher risk = higher cadence. | Proposed communication protocol |
| 2. Identify Participants | TPM | For each communication mechanism, list required participants. Dependency standup: TLs from all involved squads + TPM. RAID log: TPM updates, Engineering Director reviews. Escalation: defined path per dependency from P-015. | Participant lists per mechanism |
| 3. Validate Participation Availability | TPM + EMs | Each EM confirms their squad's TL can attend the proposed dependency standup schedule. Check for conflicts with existing ceremonies (sprint planning, daily standups, retrospectives). Adjust timing if needed. | Confirmed attendance commitments |
| 4. Define Escalation Triggers Per Dependency | TPM | For each dependency in the register (P-015), define the specific escalation trigger condition. Default: blocked >48 hours. Critical-path items may have shorter triggers (e.g., blocked >24 hours). | Dependency-specific escalation triggers |
| 5. Document Protocol | TPM | Enter the final communication protocol into Dependency Charter Section 4. Include: mechanism, cadence, participants, purpose for each. | Dependency Charter Section 4 complete |
| 6. Calendar Invites | TPM | Send recurring calendar invites for dependency standups. Include agenda template in the invite body so the format is known before the first meeting. | Calendar invites sent |

### 7. Inputs
- Dependency Register (P-015 output — determines which teams must communicate)
- Critical Path analysis (P-016 output — determines which dependencies need tighter communication cadence)
- Team calendars (existing ceremony schedules, meeting load)
- RAID Log template (organizational standard)

### 8. Outputs/Artifacts
- **Communication Protocol Table** (Section 4 of Dependency Charter) — Each row contains: mechanism, cadence, participants, purpose
- **Escalation Trigger Definitions** — Per-dependency conditions that trigger escalation (P-021)
- **Calendar Invites** — Recurring invites for dependency standups with agenda template
- Format reference:

| Mechanism | Cadence | Participants | Purpose |
|-----------|---------|-------------|---------|
| Dependency standup | [Twice-weekly/Daily], [duration] min | [TLs from squads X, Y, Z] + TPM | Surface blockers on dependency items; update statuses |
| RAID log update | [Weekly] | TPM updates; reviewed by [Director] | Track risks, assumptions, issues, dependencies at project level |
| Escalation trigger | As needed | [Defined path per dependency] | Any dependency blocked for > [X] hours with no resolution path |

### 9. Gate/Checkpoint
**Dependency Acceptance Gate (P-019)** — Pass criteria specific to this process:
- Communication protocol is agreed upon by all parties
- Specific meeting cadence is agreed to and calendared
- RAID log update frequency and owner are named
- Escalation trigger conditions are documented per dependency

### 10. Success Criteria
- Specific meeting cadence agreed to and calendared (not just proposed)
- RAID log update frequency and owner named (TPM by default)
- Escalation trigger conditions documented per dependency (not just a generic "48 hours" rule for all)
- All required participants have confirmed their availability
- No critical-path dependency has a communication gap (no team on the critical path is excluded from the standup)
- The communication protocol is lightweight enough to sustain for the project duration (no meeting fatigue)

### 11. Dependencies
| Dependency | Process | Type | Detail |
|-----------|---------|------|--------|
| Dependency Register complete | P-015 | Hard prerequisite | Cannot define communication protocol without knowing which teams must communicate |
| Critical Path Analysis | P-016 | Soft prerequisite | Critical-path items may warrant tighter communication cadence; can use preliminary critical path |

### 12. Traceability
- **Upstream**: P-015 (Dependency Register) — determines participant list
- **Upstream**: P-016 (Critical Path) — determines which dependencies need heightened communication
- **Downstream**: P-019 (Dependency Acceptance Gate) — protocol agreement is a gate pass criterion
- **Downstream (runtime)**: P-020 (Dependency Standup) — the standup process executes the protocol defined here
- **Downstream (runtime)**: P-021 (Dependency Escalation) — escalation triggers defined here govern when P-021 activates
- **Artifact**: Dependency Charter Section 4

---

## P-019: Dependency Acceptance Gate Process

### 1. Process ID and Name
**P-019** — Dependency Acceptance Gate Process

### 2. Purpose
A 45-minute gate meeting where every dependency owner verbally confirms their commitment and delivery timeline. This is the third of four gates in the Clarity of Intent process (after Intent Review P-004 and Scope Lock P-013, before Sprint Readiness P-025). Development does not start until this gate passes. The gate converts documented dependencies into binding commitments — a dependency that has been written down but not verbally committed to is not a real commitment.

### 3. Derived From
Clarity of Intent — Stage 3: Gate: Dependency Acceptance

Relevant source text: "45-minute meeting. TPM walks through the Dependency Charter. Each dependency owner verbally confirms their commitment and timeline." and the six pass criteria listed under the Dependency Acceptance gate.

### 4. Primary Owner Agent
**technical-program-manager** — The TPM chairs the gate meeting, drives through each dependency for verbal confirmation, and records the gate decision. This is the TPM's most critical gate responsibility in the Clarity of Intent process.

### 5. Supporting Agents
- **engineering-manager** — All squad EMs confirm capacity allocation is real (not over-committed). The EM's data-driven approach (EM-006) ensures commitments are backed by actual capacity data, not optimistic estimates.
- **software-engineer** (Tech Lead) — All squad TLs review their technical dependencies and confirm delivery feasibility. The TL's technical depth ensures commitments are technically achievable, not just schedulable.
- **product-manager** — PM attends to provide business context for prioritization decisions and to confirm that dependency timelines align with business milestones.

### 6. Stages/Steps

| Step | Actor | Action | Output |
|------|-------|--------|--------|
| 1. Pre-Gate Distribution | TPM | Distribute the complete Dependency Charter (all 4 sections) to all participants 24 hours before the gate meeting. Include a read-ahead request: each participant must review dependencies involving their squad before the meeting. | Dependency Charter distributed |
| 2. Pre-Gate Alignment | TPM | Before the formal gate, TPM contacts each dependency owner individually to pre-align on any concerns. The gate meeting should ratify commitments, not discover problems for the first time. | Pre-alignment notes; known concerns documented |
| 3. Gate Meeting: Dependency Walk-Through | TPM (chair) | TPM walks through each dependency in the register (Section 1). For each dependency, the owner is asked to verbally confirm: "I commit to delivering [what is needed] by [date]." | Verbal confirmation per dependency |
| 4. Gate Meeting: Capacity Confirmation | EMs | Each EM confirms that their squad's commitments are backed by real capacity. If an EM identifies over-commitment, the specific conflict is documented and must be resolved before the gate can pass. | Capacity confirmation per squad |
| 5. Gate Meeting: Critical Path Review | TPM | TPM walks through the critical path (Section 3). Each team on the critical path acknowledges their position and the escalation trigger dates. | Critical path acknowledgment |
| 6. Gate Meeting: Protocol Confirmation | All | Confirm the communication protocol (Section 4): standup cadence, RAID log, escalation triggers. All participants agree to the commitments. | Protocol confirmation |
| 7. Gate Decision | TPM | Binary decision: PASS or FAIL. PASS requires ALL six criteria to be met (see Gate/Checkpoint below). If FAIL, TPM documents specific blockers, assigns resolution owners, and sets a follow-up date (typically 24-48 hours). | Gate decision record |

### 7. Inputs
- Complete Dependency Charter (4 sections from P-015, P-016, P-017, P-018)
- Capacity validation from each EM (sprint velocity, planned leave, competing commitments)
- Pre-alignment notes from TPM's individual outreach

### 8. Outputs/Artifacts
- **Gate Decision Record** — PASS or FAIL with rationale
- **Verbal Commitment Records** — Record of each dependency owner's verbal commitment (names, dates, what was committed to)
- **If FAIL: Blocker List** — Specific blockers preventing gate passage, each with a resolution owner and deadline
- **If PASS: Locked Dependency Charter v1.0** — The Dependency Charter becomes the baseline for dependency tracking during execution

### 9. Gate/Checkpoint
**This IS the gate.** Binary pass criteria — ALL must be met:
1. Every dependency has a named owner and a "needed by" date
2. Every dependency owner has verbally confirmed they can deliver by the stated date
3. The critical path is documented and understood by all parties
4. At least one escalation path is defined for blocked dependencies
5. No HIGH-severity blocker is unresolved without a resolution plan and deadline
6. Communication protocol is agreed upon

### 10. Success Criteria
- All dependency owners are on record as having committed to their delivery dates
- No EM has flagged capacity over-commitment without resolution
- Gate FAIL results in a specific follow-up action with a named owner and a deadline (not an open-ended "we'll figure it out")
- Gate meeting completes within 45 minutes (if pre-alignment was done properly, the meeting ratifies rather than negotiates)
- The locked Dependency Charter v1.0 is published and accessible to all project participants

### 11. Dependencies
| Dependency | Process | Type | Detail |
|-----------|---------|------|--------|
| Dependency Register | P-015 | Hard prerequisite | Section 1 must be complete |
| Critical Path Analysis | P-016 | Hard prerequisite | Section 3 must be complete |
| Shared Resource Conflict Resolution | P-017 | Hard prerequisite | Section 2 must be complete; all conflicts must have resolutions |
| Communication Protocol | P-018 | Hard prerequisite | Section 4 must be complete |
| Shared Resource Allocation | P-083 | Hard prerequisite | Director-level resource allocation negotiations must be complete |

### 12. Traceability
- **Upstream**: P-015, P-016, P-017, P-018 — all four Dependency Charter sections must be complete
- **Upstream**: P-083 (Shared Resource Allocation) — Director-level allocation decisions feed into resource conflict resolutions
- **Downstream**: P-022 (Sprint Goal Authoring) — sprint goals are authored against locked dependency commitments
- **Downstream**: P-030 (Sprint-Level Dependency Tracking) — sprint-level tracking derives from the locked charter
- **Downstream**: P-091 (New Project Onboarding) — onboarding uses the locked charter for cross-team context
- **Downstream**: P-093 (Technical Onboarding for Cross-Team Dependencies) — technical onboarding uses the charter
- **Gate chain**: P-004 (Intent Review) → P-013 (Scope Lock) → **P-019 (Dependency Acceptance)** → P-025 (Sprint Readiness)
- **Artifact**: Locked Dependency Charter v1.0

---

## P-020: Dependency Standup Process

### 1. Process ID and Name
**P-020** — Dependency Standup Process

### 2. Purpose
A twice-weekly, 15-minute cross-squad standup during active sprints to surface blockers on dependency items, update statuses in the Dependency Charter, and trigger escalation when needed. This is the runtime execution of the communication protocol established in P-018. Without regular dependency check-ins, blockers compound silently and surface only when they have already caused sprint failure.

### 3. Derived From
Clarity of Intent — Stage 3: Communication Protocol (Dependency standup cadence)

Relevant source text: "Dependency standup — Twice weekly, 15 min — TLs from all involved squads + TPM — Surface blockers on dependency items; update statuses."

### 4. Primary Owner Agent
**technical-program-manager** — The TPM facilitates the standup, enforces the 15-minute timebox, updates the RAID log after each session, and triggers escalation (P-021) when blockers are identified.

### 5. Supporting Agents
- **software-engineer** (Tech Lead) — TLs from all involved squads report the status of dependencies they own: on track, at risk, or blocked. TLs provide technical context for status changes and identify emerging dependencies not in the original register.

### 6. Stages/Steps

| Step | Actor | Action | Output |
|------|-------|--------|--------|
| 1. Open Standup | TPM | Open the standup. State the time: "We have 15 minutes." Display the current Dependency Register with statuses from the last update. | Standup opened; current state visible |
| 2. Status Round | Each TL | Each TL reports status of dependencies they own. Three categories only: (a) **On Track** — progressing as committed, (b) **At Risk** — may not meet the "needed by" date; state what is causing the risk, (c) **Blocked** — cannot progress; state the blocker. | Updated statuses per dependency |
| 3. Blocker Triage | TPM | For each "Blocked" item: (a) Can it be unblocked in the standup? If yes, assign action and deadline. (b) Is it blocked >48 hours? If yes, trigger P-021 (Dependency Escalation) immediately. | Blocker triage decisions |
| 4. At-Risk Mitigation | TPM + Relevant TLs | For each "At Risk" item: identify mitigation action and owner. Rule: no "at risk" dependency survives one full standup cycle (i.e., 3-4 business days) without an assigned owner working on mitigation. | Mitigation actions assigned |
| 5. Update RAID Log | TPM | After the standup, TPM updates the RAID Log with: new risks identified, dependency status changes, actions assigned, escalation triggers activated. | Updated RAID Log |
| 6. Close Standup | TPM | Confirm next standup date/time. Summarize actions in a brief written summary to all participants. | Standup summary distributed |

### 7. Inputs
- Current Dependency Charter (locked at P-019, statuses updated continuously)
- Last RAID Log update
- Previous standup summary and open action items

### 8. Outputs/Artifacts
- **Updated Dependency Statuses** — Each dependency in the register has a current status (On Track / At Risk / Blocked)
- **Escalation Triggers** — Any dependency meeting escalation criteria triggers P-021
- **RAID Log Update** — Risks, assumptions, issues, dependencies updated
- **Standup Summary** — Brief written summary of status changes and actions, distributed to all participants

### 9. Gate/Checkpoint
No formal gate — this is a recurring operational process. However:
- Any dependency blocked >48 hours with no resolution path triggers P-021 (Dependency Escalation)
- Any "at risk" dependency without a mitigation owner for one full standup cycle (3-4 business days) is escalated to the EM level

### 10. Success Criteria
- Standup runs in 15 minutes or less (strict timebox)
- Every dependency status is updated after each standup (no stale statuses)
- No "at risk" dependency survives one full standup cycle without an assigned mitigation owner
- Blocked items trigger escalation (P-021) within the same business day they are identified
- RAID log is updated by TPM after every standup
- Standup summary is distributed to all participants within 1 hour of standup completion

### 11. Dependencies
| Dependency | Process | Type | Detail |
|-----------|---------|------|--------|
| Dependency Acceptance Gate passed | P-019 | Hard prerequisite | Cannot run dependency standups without a locked Dependency Charter |
| Sprint Readiness Gate passed | P-025 | Timing prerequisite | Dependency standups begin when active sprints begin (P-020 is in Program 12: Active Sprint) |
| Communication Protocol | P-018 | Structural prerequisite | Standup cadence, participants, and format were defined in P-018 |

### 12. Traceability
- **Upstream**: P-019 (Dependency Acceptance Gate) — the locked Dependency Charter is the status tracking baseline
- **Upstream**: P-018 (Communication Protocol) — standup cadence and format were defined here
- **Downstream**: P-021 (Dependency Escalation) — blocked items trigger escalation
- **Parallel**: P-026 (Daily Standup) — team-level standups handle within-squad work; dependency standup handles cross-squad dependencies. These are complementary, not redundant.
- **Artifact**: Updated RAID Log; standup summaries

---

## P-021: Dependency Escalation Process

### 1. Process ID and Name
**P-021** — Dependency Escalation Process

### 2. Purpose
Escalate any dependency blocked for more than 48 hours with no resolution path. Each dependency's Dependency Charter entry includes its escalation path (Owner → EM → Director → VP), and this process defines the time-bound SLA for each escalation tier. Without a defined escalation process, blocked dependencies persist indefinitely at the working level while leadership remains unaware.

### 3. Derived From
Clarity of Intent — Stage 3: Dependency Charter escalation paths; Communication Protocol escalation triggers; Organizational hierarchy (Engineering Team Structure Guide — EM → Director → VP reporting chain)

Relevant source text: "Escalation trigger — As needed — EM → Director → VP (defined path per dependency) — Any dependency blocked for > 48 hours with no resolution path."

### 4. Primary Owner Agent
**technical-program-manager** — The TPM initiates escalation, tracks the escalation through each tier, and records the resolution in the RAID log. The TPM's cross-team visibility ensures escalation reaches the right level of the organization.

### 5. Supporting Agents
- **engineering-manager** — EMs are the first escalation tier. The EM attempts resolution within their Director's scope. If unresolved within 24 hours, the EM escalates to the Director. The EM's reporting-line access (EM → Director → VP) provides the escalation channel.

### 6. Stages/Steps

| Step | Actor | Action | Output |
|------|-------|--------|--------|
| 1. Escalation Trigger | TPM (or P-020 standup) | A dependency has been in "Blocked" status for >48 hours with no resolution path identified. TPM initiates escalation by notifying the dependency's EM per the escalation path defined in the Dependency Register. | Escalation initiated; EM notified |
| 2. Tier 1: EM Resolution Attempt | EM (of the blocking team) | EM has 24 hours to attempt resolution. Resolution options: reassign resources, negotiate with the blocking party, propose a workaround, or identify an alternative dependency path. EM communicates resolution attempt to TPM. | Resolution attempt within 24 hours |
| 3. Tier 2: Director Escalation | EM → Director | If unresolved after 24 hours at Tier 1, EM escalates to their Director. Director has authority to: reprioritize across squads, override resource allocation, authorize scope adjustment, negotiate with peer Directors for cross-org resolution. Director has 24 hours to resolve or escalate. | Director-level resolution attempt within 24 hours |
| 4. Tier 3: VP Escalation | Director → VP | If unresolved after 24 hours at Tier 2, Director escalates to VP. VP has authority to: make binding cross-org priority decisions, authorize budget for additional resources, override competing project commitments, accept scope reduction if dependency cannot be met. | VP-level resolution decision |
| 5. Resolution Recording | TPM | Regardless of the tier at which resolution occurs, TPM records: (a) escalation timeline (when each tier was triggered), (b) resolution decision, (c) impact on the Dependency Charter (updated status, revised dates, scope changes), (d) lessons learned for retrospective. | Escalation record in RAID Log |
| 6. Dependency Charter Update | TPM | Update the Dependency Register with the resolution: new owner (if changed), revised "needed by" date (if changed), updated status, any scope change resulting from the escalation. | Updated Dependency Register |

### 7. Inputs
- Blocked dependency record from P-020 (Dependency Standup) or direct observation
- RAID Log (current state of risks and issues)
- Escalation path from the Dependency Register (P-015 — each dependency has a defined path)
- Organizational hierarchy (Engineering Team Structure Guide — EM → Director → VP chain)

### 8. Outputs/Artifacts
- **Escalation Record** — Added to RAID Log with: dependency ID, escalation trigger date/time, tier progression timestamps, resolution decision, impact on project timeline
- **Updated Dependency Status** — Dependency Register updated with resolution outcome
- **Scope Change Request** (if applicable) — If the resolution requires scope adjustment, a Scope Change Request (P-014) is initiated

### 9. Gate/Checkpoint
No formal gate — this is a time-bound triggered process with strict SLAs:
- **Tier 1 (EM)**: Triggered at 48-hour block mark; 24-hour resolution window
- **Tier 2 (Director)**: Triggered at 72-hour block mark (48 + 24); 24-hour resolution window
- **Tier 3 (VP)**: Triggered at 96-hour block mark (48 + 24 + 24); resolution required

### 10. Success Criteria
- Every blocked dependency reaches an escalation owner within the defined SLA
- No dependency stays in "blocked" status for more than 5 business days without a VP-level resolution decision
- Escalation records are complete: timestamps, decisions, and impacts documented in RAID log
- Resolution decisions are reflected in updated Dependency Charter entries
- If resolution requires scope change, P-014 (Scope Change Control) is invoked — no silent scope changes

### 11. Dependencies
| Dependency | Process | Type | Detail |
|-----------|---------|------|--------|
| Dependency Standup | P-020 | Primary trigger | Most escalations are triggered by blocked items surfaced in the dependency standup |
| Escalation paths defined | P-015 | Structural prerequisite | Each dependency's escalation path must have been defined during dependency registration |
| Scope Change Control | P-014 | Conditional downstream | If resolution requires scope adjustment, P-014 governs the change |

### 12. Traceability
- **Upstream**: P-020 (Dependency Standup) — blocked items trigger escalation
- **Upstream**: P-015 (Dependency Register) — escalation paths are defined per dependency
- **Downstream**: P-014 (Scope Change Control) — if resolution requires scope change
- **Downstream**: P-028 (Sprint Retrospective) — escalation patterns are retrospective inputs
- **Downstream**: P-070 (Project Post-Mortem) — escalation frequency and resolution times are post-mortem metrics
- **Cross-reference**: Engineering Team Structure Guide — organizational hierarchy (EM → Director → VP) defines the escalation tiers
- **Artifact**: RAID Log escalation records; updated Dependency Register

---

## Cross-Category Interface Summary

### Upstream Dependencies (from other categories)

| Source Process | Source Category | What It Provides | Consumed By |
|---------------|----------------|-----------------|-------------|
| P-013: Scope Lock Gate | 2 — Scope & Contract Management | Locked Scope Contract (deliverables, owners, DoD, exclusions, metrics, risks) | P-015 (primary input for dependency discovery) |
| P-007: Deliverable Decomposition | 2 — Scope & Contract Management | Deliverables table with owner squads | P-015 (deliverables are dependency candidates) |
| P-010: Assumptions & Risks | 2 — Scope & Contract Management | Known risks that may have dependency implications | P-015 (informational input) |
| P-014: Scope Change Control | 2 — Scope & Contract Management | Scope changes that may introduce new dependencies | P-015 (re-entry for scope changes) |

### Downstream Dependencies (to other categories)

| Target Process | Target Category | What It Consumes | Provided By |
|---------------|----------------|-----------------|-------------|
| P-022: Sprint Goal Authoring | 4 — Sprint & Delivery Execution | Locked Dependency Charter with commitments | P-019 |
| P-025: Sprint Readiness Gate | 4 — Sprint & Delivery Execution | Dependency acceptance as prerequisite | P-019 |
| P-030: Sprint-Level Dependency Tracking | 4 — Sprint & Delivery Execution | Dependency Charter baseline for sprint tracking | P-019 |
| P-091: New Project Onboarding | Onboarding & Knowledge Transfer | Cross-team dependency context | P-019 |
| P-093: Technical Onboarding for Cross-Team Dependencies | Onboarding & Knowledge Transfer | Dependency Charter for technical onboarding | P-019 |
| P-014: Scope Change Control | 2 — Scope & Contract Management | Scope change triggered by dependency escalation | P-021 |
| P-028: Sprint Retrospective | 4 — Sprint & Delivery Execution | Escalation patterns as retrospective input | P-021 |
| P-070: Project Post-Mortem | Project Closure | Dependency tracking metrics | P-020, P-021 |

### Critical Path Position

This category occupies days 7-12 of the Clarity of Intent critical path:

```
P-001 → P-004 → P-007 → P-013 → [P-015 → P-016 + P-017 + P-018 → P-019] → P-022 → P-025
                                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                   Category 3: 3-5 working days
```

---

## Appendix: Dependency Charter Template

The complete Dependency Charter produced by P-015 through P-018 and locked at P-019 follows this structure:

### Section 1: Dependency Register (P-015)

| ID | Dependent Team | Depends On | What Is Needed | By When | Status | Owner | Escalation Path |
|----|---------------|------------|----------------|---------|--------|-------|-----------------|
| D1 | [Team] | [Team/External] | [Specific need] | [Date] | [Status] | [Owner] | [Path] |

### Section 2: Shared Resource Conflicts (P-017)

| Resource | Competing Demands | Resolution | Owner | Deadline |
|----------|------------------|------------|-------|----------|
| [Resource] | [Demands] | [Resolution] | [Owner] | [Date] |

### Section 3: Critical Path (P-016)

```
[Sequence diagram showing the longest dependency chain]
Total critical path duration: X days
```

| Non-Critical Item | Earliest Completion | Latest Allowable | Float |
|-------------------|-------------------|------------------|-------|
| [Item] | [Date] | [Date] | [Days] |

### Section 4: Communication Protocol (P-018)

| Mechanism | Cadence | Participants | Purpose |
|-----------|---------|-------------|---------|
| Dependency standup | Twice weekly, 15 min | TLs + TPM | Surface blockers; update statuses |
| RAID log update | Weekly | TPM updates; Director reviews | Project-level risk/dependency tracking |
| Escalation trigger | As needed | Per-dependency path | Blocked >48 hours with no resolution |

---

*End of specification.*

---

## Cross-Category Dependencies

### Dependencies FROM Other Categories (Inputs)

| Source Process | Source Category | Consuming Process | Nature |
|---------------|----------------|-------------------|--------|
| P-013 (Scope Lock Gate) | Cat 2: Scope & Contract | P-015 (Cross-Team Dependency Registration) | Scope Contract must be locked before dependency mapping |

### Dependencies TO Other Categories (Outputs)

| Providing Process | Consuming Process | Target Category | Nature |
|------------------|-------------------|-----------------|--------|
| P-019 (Dependency Acceptance Gate) | P-022 (Sprint Goal Authoring) | Cat 4: Sprint & Delivery | Dependencies accepted before sprint preparation |
| P-019 (Dependency Acceptance Gate) | P-091 (New Project Onboarding) | Cat 17: Onboarding | Gate triggers project onboarding |
| P-019 (Dependency Acceptance Gate) | P-093 (Technical Onboarding for Dependencies) | Cat 17: Onboarding | New dependencies need technical context transfer |
| P-015 (Cross-Team Dependency Registration) | P-030 (Sprint-Level Dependency Tracking) | Cat 4: Sprint & Delivery | Dependency Charter provides sprint dependencies |
| P-015 (Cross-Team Dependency Registration) | P-083 (Shared Resource Allocation) | Cat 15: Capacity & Resource | Dependency Charter identifies shared resource needs |

## Agent Assignments Summary

| Process | Primary Owner | Supporting Agents |
|---------|--------------|-------------------|
| P-015: Cross-Team Dependency Registration | technical-program-manager | software-engineer (TL), engineering-manager |
| P-016: Critical Path Analysis | technical-program-manager | software-engineer (TL), staff-principal-engineer |
| P-017: Shared Resource Conflict Resolution | technical-program-manager | engineering-manager, infra-engineer |
| P-018: Communication Protocol Establishment | technical-program-manager | engineering-manager, product-manager |
| P-019: Dependency Acceptance Gate | technical-program-manager | engineering-manager, software-engineer, product-manager |
| P-020: Dependency Standup | technical-program-manager | software-engineer (TLs) |
| P-021: Dependency Escalation | technical-program-manager | engineering-manager |
