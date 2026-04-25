# Technical Specification: Capacity & Resource Management Processes (P-082 to P-084)

**Category**: 15 — Capacity & Resource Management
**Date**: 2026-04-05
**Status**: Draft
**Derived From**: Process Architecture (Category 15); Clarity of Intent (Stages 2–3); Engineering Team Structure Guide (Organizational Hierarchy, Role Catalog)

---

## Overview

This specification defines three processes that govern how the engineering organization plans, allocates, and protects its human capacity. Together they ensure that squads are not over-committed (P-082), shared specialist resources are not double-booked (P-083), and critical knowledge is not trapped in single individuals (P-084).

These processes operate at different cadences — quarterly, per-project, and annually — but are tightly connected. Quarterly capacity declarations (P-082) feed into shared resource allocation decisions (P-083), and succession planning (P-084) informs long-term capacity resilience.

---

## P-082: Quarterly Capacity Planning Process

### Process ID
P-082

### Process Name
Quarterly Capacity Planning Process

### Purpose
VPs submit quarterly headcount plans. Directors allocate squads to programs. EMs validate squad capacity against sprint commitments. This process prevents over-committing squads by ensuring capacity declarations are grounded in actuals (PTO, on-call burden, new hire ramp-up), not theoretical maximums.

### Derived From
- Process Architecture: Stage 0 research Category 13; VP and Director responsibilities; quarterly OKR cycle
- Clarity of Intent: Stage 2 Scope Contract (Section 6 — Assumptions and Risks: "Mobile team has capacity in Q3" is the exact class of assumption this process validates)
- Engineering Team Structure Guide: VP of Engineering responsibilities (headcount planning, engineering budget); Director responsibilities (squad-to-program allocation); EM responsibilities (sprint health, impediment removal)

### Primary Owner Agent
`engineering-manager` (operating at VP scope for headcount plan submission, Director scope for allocation decisions, EM scope for squad-level validation)

### Supporting Agents
- `product-manager` — GPM/PM provides product demand signals that drive capacity requirements
- `technical-program-manager` — TPM provides cross-program demand aggregation and identifies contention across programs

### Stages/Steps

**Stage 1: Demand Aggregation (Week 1 of quarterly planning)**
1. GPMs and PMs submit product demand signals for the upcoming quarter — list of programs, projects, and initiatives requiring engineering capacity.
2. TPMs aggregate cross-program demand and identify where multiple programs compete for the same squad or specialist capacity.
3. Output: Demand Signal Register — a consolidated list of all capacity requests by squad, program, and sprint window.

**Stage 2: Headcount Plan Submission (Week 1–2)**
1. Each VP reviews the Demand Signal Register against their current headcount.
2. VP submits a quarterly headcount plan to the CTO, documenting: current headcount, open requisitions, expected attritions, planned hires, and net available capacity.
3. CTO reviews and approves headcount plans or requests adjustments.
4. Output: Approved Headcount Plan per VP domain.

**Stage 3: Squad-to-Program Allocation (Week 2–3)**
1. Directors take the approved headcount plan and the Demand Signal Register.
2. Directors allocate squads to programs and projects for the quarter, documenting which squad works on which initiative and for how many sprints.
3. Allocation conflicts (same squad demanded by multiple programs) escalated to VP for prioritization decision.
4. Output: Quarterly Allocation Map — squad-to-program assignments for the quarter.

**Stage 4: Squad Capacity Validation (Week 3–4)**
1. Each EM validates their squad's actual capacity for each sprint in the quarter.
2. EM accounts for: PTO calendar, on-call rotation burden (hours lost per sprint), new hire ramp-up (new hires operate at ~50% capacity for first 2 sprints, ~75% for next 2), training commitments, and guild/chapter participation time.
3. EM produces a Capacity Declaration: available story points (or equivalent) per sprint, with confidence level.
4. Output: Squad Capacity Declarations — one per squad, per sprint.

**Stage 5: Over-Commitment Detection and Resolution (Week 4)**
1. EM compares total sprint commitments (from allocated programs) against Squad Capacity Declaration.
2. If commitments exceed capacity: EM escalates to Director with specific data (e.g., "Squad has 40 SP capacity; commitments total 55 SP in Sprint 3").
3. Director resolves by: re-prioritizing work, deferring lower-priority items, or requesting additional capacity from VP.
4. Resolution documented in the Quarterly Allocation Map.
5. Output: Finalized, validated Quarterly Capacity Plan.

### Inputs
| Input | Source |
|-------|--------|
| Company OKR demands | P-005 Strategic Prioritization Process |
| Headcount actuals (current team rosters) | HR / People systems |
| PTO calendar | HR / team calendars |
| On-call rotation schedule and burden metrics | SRE / on-call management tooling |
| New hire ramp-up estimates | EM knowledge; onboarding process data |
| Product demand signals | GPM / PM roadmap submissions |
| Cross-program demand | TPM aggregation |

### Outputs / Artifacts

| Artifact | Description | Owner | Format |
|----------|-------------|-------|--------|
| Demand Signal Register | Consolidated capacity requests by squad, program, sprint | TPM | Spreadsheet / planning tool |
| Approved Headcount Plan | Per-VP headcount: current, open reqs, expected attrition, planned hires, net capacity | VP (approved by CTO) | Document |
| Quarterly Allocation Map | Squad-to-program assignments for the quarter | Director | Spreadsheet / planning tool |
| Squad Capacity Declarations | Available story points per sprint per squad, with deductions itemized | EM | Document / planning tool |
| Finalized Quarterly Capacity Plan | Validated, conflict-resolved capacity commitments | Director (validated by EM) | Document |

### Gate / Checkpoint
**Quarterly Capacity Review Gate**

- **Participants**: CTO, VPs, Directors, TPMs
- **Format**: 90-minute quarterly planning review meeting
- **Timing**: End of Week 4 of quarterly planning cycle (before the quarter begins)

**Pass Criteria**:
- All VPs have submitted headcount plans and received CTO approval
- All Directors have produced Quarterly Allocation Maps
- All EMs have submitted Squad Capacity Declarations based on actuals (not theoretical maximum)
- All over-commitments have been identified and resolved (or have a documented resolution plan with a deadline)
- No squad is allocated at greater than 85% of its declared capacity (15% buffer for unplanned work, incidents, and technical debt)

**If the gate does not pass**: Resolve capacity conflicts before the quarter starts. Starting a quarter with unresolved over-commitments guarantees missed commitments and team burnout.

### Success Criteria
- Squad capacity declarations are realistic — based on actuals (PTO, on-call, ramp-up), not theoretical maximum velocity
- Over-commitments are identified and resolved during planning, not discovered during execution when the cost of adjustment is highest
- Headcount plans submitted to CTO within the quarterly planning window
- Quarter-over-quarter improvement: fewer mid-quarter capacity surprises (measured by unplanned re-prioritization events)

### Dependencies

| Dependency | Direction | Description |
|------------|-----------|-------------|
| P-005: Strategic Prioritization | Upstream | Strategic priorities define the demand that drives capacity planning |
| P-083: Shared Resource Allocation | Downstream | Capacity declarations feed into shared resource allocation decisions |
| P-086: Technical Debt Tracking | Bidirectional | Technical debt remediation requires capacity allocation; capacity planning must reserve capacity for debt work |
| P-071: OKR Cascade (implied) | Upstream | OKR commitments represent the demand side of the capacity equation |

### Traceability

| Trace Point | Reference |
|-------------|-----------|
| Clarity of Intent, Stage 2, Section 6 | "Mobile team has capacity in Q3" — this is the exact class of assumption that P-082 validates before Scope Lock |
| Clarity of Intent, Stage 3, Section 2 | Shared Resource Conflicts section depends on capacity data from this process |
| Engineering Team Structure Guide, VP of Engineering | "Manages headcount planning and engineering budget for their org" |
| Engineering Team Structure Guide, Director of Engineering | "Manages Engineering Managers; owns product area roadmap execution" |
| Engineering Team Structure Guide, EM | "Maintains sprint health; removes impediments" |
| Process Architecture, Execution Order | Program 0 (recurring governance) — trigger: quarterly |

### Risk Level
HIGH — Over-committed squads produce neither the committed volume nor quality. Capacity planning failures cascade into missed sprint goals, dependency failures, and team attrition.

### Cadence
Quarterly

---

## P-083: Shared Resource Allocation Process

### Process ID
P-083

### Process Name
Shared Resource Allocation Process

### Purpose
TPM and Directors negotiate shared resource time allocations (AppSec, Platform, Data Engineering, SRE) across competing projects during Stage 3 Dependency Map. This process prevents shared resources from being double-booked, which is the most common cause of sprint failures in cross-team projects.

### Derived From
- Process Architecture: Stage 0 research Category 13; Stage 3 Dependency Charter Section 2 (Shared Resource Conflicts); TPM role
- Clarity of Intent: Stage 3 Dependency Map — Section 2 explicitly documents shared resource conflicts and their resolution
- Engineering Team Structure Guide: TPM role ("coordinates delivery across 3–10 engineering teams; manages cross-team dependencies"); Director role (adjudicates conflicts)

### Primary Owner Agent
`technical-program-manager`

### Supporting Agents
- `engineering-manager` — Director adjudicates conflicts when competing demands exceed available capacity; EM for shared team provides availability data
- `security-engineer` — AppSec confirms availability for security review windows
- `cloud-engineer` — Platform/SRE confirms availability for infrastructure support windows

### Stages/Steps

**Stage 1: Shared Resource Demand Identification**
1. TPM reviews all active projects and their Dependency Charters (produced in Stage 3 of the Clarity of Intent process).
2. For each project, TPM extracts shared resource needs: which shared team, what type of work, how many person-days, and in which sprint window.
3. Output: Shared Resource Demand Matrix — a consolidated view of all shared resource requests across all active projects.

**Stage 2: Conflict Detection**
1. TPM maps demands against available capacity of each shared resource team.
2. Conflicts identified: same shared resource (team or individual) needed by multiple projects in the same sprint window, with total demand exceeding available capacity.
3. Each conflict documented with: competing projects, resource requested, sprint window, and magnitude of the conflict (e.g., "AppSec engineer needed for 8 days in Sprint 2, but only 5 days available").
4. Output: Conflict Register — list of all double-booking conflicts with severity and impact.

**Stage 3: Conflict Resolution Negotiation**
1. TPM convenes affected project leads (TLs and PMs) and shared resource EMs to negotiate resolution.
2. Resolution strategies applied in order of preference:
   - **Time-shift**: Can one project move its shared resource need to a different sprint without affecting its critical path?
   - **Parallelize**: Can the shared resource work on both projects simultaneously (e.g., split days)?
   - **Substitute**: Can a different team member with similar skills fulfill one of the requests?
   - **Escalate**: If no resolution is achievable at TPM level, escalate to Director for prioritization decision.
3. Output: Proposed allocation decisions for each conflict.

**Stage 4: Director Adjudication (for unresolved conflicts)**
1. Director reviews escalated conflicts with business context: which project has higher strategic priority (referencing P-005 Strategic Prioritization)?
2. Director makes allocation decision and documents the rationale.
3. Deprioritized project receives a documented impact assessment: what slips, by how much, and what mitigation is available.
4. Output: Director Allocation Decision — documented and communicated to all affected parties.

**Stage 5: Allocation Documentation and Communication**
1. Final allocation decisions documented in the Shared Resource Allocation Register.
2. Each shared resource team EM receives a confirmed allocation schedule for the quarter or project period.
3. Allocation decisions incorporated into Dependency Charters for affected projects.
4. Output: Shared Resource Allocation Register — the authoritative record of who is allocated where and when.

### Inputs
| Input | Source |
|-------|--------|
| Dependency Charters (Section 2: Shared Resource Conflicts) | P-015 Cross-Team Dependency Registration; P-017 Shared Resource Conflict Resolution |
| Squad Capacity Declarations for shared teams | P-082 Quarterly Capacity Planning |
| Active project registry | TPM tracking |
| Strategic priority ranking | P-005 Strategic Prioritization |

### Outputs / Artifacts

| Artifact | Description | Owner | Format |
|----------|-------------|-------|--------|
| Shared Resource Demand Matrix | Consolidated view of all shared resource requests across projects | TPM | Spreadsheet |
| Conflict Register | List of double-booking conflicts with severity and competing parties | TPM | Spreadsheet / tracking tool |
| Director Allocation Decision | Documented prioritization decision for escalated conflicts | Director | Document |
| Shared Resource Allocation Register | Authoritative record of shared resource allocations by project, sprint, and person-days | TPM | Spreadsheet / planning tool |

### Gate / Checkpoint
**Shared Resource Allocation Confirmation**

- **Participants**: TPM, Directors for shared resource teams, EMs for shared resource teams, project TLs and PMs for affected projects
- **Format**: 30-minute review per shared resource team (can be batched); or async confirmation with 48-hour response window
- **Timing**: Before Dependency Acceptance Gate (P-019) for per-project allocation; during quarterly planning (P-082) for quarterly allocation

**Pass Criteria**:
- No shared resource is double-booked without Director awareness and an explicit prioritization decision
- All conflicts have been resolved through negotiation or Director adjudication
- All shared resource team EMs have confirmed the allocation is feasible within their team's capacity
- Deprioritized projects have documented impact assessments and mitigation plans
- Allocation decisions are recorded in the Shared Resource Allocation Register

**If the gate does not pass**: Resolve remaining conflicts before the Dependency Acceptance Gate (P-019). Proceeding with unresolved shared resource conflicts will cause sprint failures.

### Success Criteria
- No shared resource is double-booked without Director awareness and decision
- All conflicts escalated to Director level — not resolved unilaterally by individual TPMs without authority
- Sprint failures attributable to shared resource unavailability trending to zero quarter-over-quarter
- Shared resource teams report that their allocation schedule matches reality (measured via quarterly survey or retrospective)

### Dependencies

| Dependency | Direction | Description |
|------------|-----------|-------------|
| P-015: Cross-Team Dependency Registration | Upstream | Dependency Register identifies which shared resources are needed |
| P-017: Shared Resource Conflict Resolution | Upstream | Conflict resolution at the Dependency Charter level feeds into this allocation process |
| P-082: Quarterly Capacity Planning | Upstream | Capacity declarations for shared teams provide the supply-side data |
| P-019: Dependency Acceptance Gate | Downstream | Allocation decisions must be confirmed before the Dependency Acceptance Gate passes |
| P-005: Strategic Prioritization | Upstream | Strategic priority ranking informs Director adjudication decisions |

### Traceability

| Trace Point | Reference |
|-------------|-----------|
| Clarity of Intent, Stage 3, Section 2 | Shared Resource Conflicts — "Identify any shared resources (people, environments, infrastructure) that multiple deliverables compete for" |
| Clarity of Intent, Stage 3, Section 4 | Communication Protocol — dependency standup tracks shared resource allocation status |
| Engineering Team Structure Guide, TPM | "Coordinates delivery across 3–10 engineering teams; manages cross-team dependencies" |
| Engineering Team Structure Guide, Director | "Resolves cross-team technical disputes" |
| Process Architecture, Execution Order | Program 7 (blockedBy P-015); feeds into Program 8 (P-019 Dependency Acceptance Gate) |

### Risk Level
HIGH — Double-booked shared resources are the single most common cause of sprint failures in cross-team projects. When an AppSec engineer is promised to three projects in the same sprint, all three projects slip.

### Cadence
Per-project (triggered at Stage 3 Dependency Map); Quarterly (as part of P-082 Quarterly Capacity Planning)

---

## P-084: Succession Planning Process

### Process ID
P-084

### Process Name
Succession Planning Process

### Purpose
Every L5+ engineer has a potential successor identified annually. EMs own succession planning for ICs in their squad. Directors own succession planning for EM-level roles. This process prevents organizational fragility caused by key-person dependencies — ensuring that critical knowledge, relationships, and decision-making capability are distributed rather than concentrated in individuals who could leave, transfer, or become unavailable.

### Derived From
- Process Architecture: Stage 0 research Category 13; EM and Director performance management responsibilities
- Engineering Team Structure Guide: EM responsibilities ("performance reviews, compensation inputs, career development"); Director responsibilities ("drives hiring, leveling decisions, and performance management"); IC ladder (L5+ roles carry system-level and cross-team scope)
- Clarity of Intent: Implicit — the Assumptions and Risks framework (Stage 2, Section 6) covers organizational risks; succession gaps are a category of organizational risk

### Primary Owner Agent
`engineering-manager` (EM scope for IC succession; Director scope for EM succession)

### Supporting Agents
- `staff-principal-engineer` — Staff Engineers may be succession candidates for TL or Staff roles; Principal Engineers may advise on technical leadership succession requirements

### Stages/Steps

**Stage 1: L5+ Roster Identification (Annual, Q1)**
1. EM produces a complete roster of all L5+ ICs in their squad: Senior Engineers (L5), Staff Engineers (L6), and any Tech Leads.
2. Director produces a roster of all EMs in their organization.
3. VP produces a roster of all Directors and Principal/Distinguished Engineers in their domain.
4. Output: L5+ Roster — complete list of positions requiring succession candidates.

**Stage 2: Successor Candidate Identification (Annual, Q1)**
1. For each L5+ position, the responsible manager (EM for ICs, Director for EMs, VP for Directors) identifies one or more potential successor candidates.
2. Each candidate is assessed on three dimensions:
   - **Technical readiness**: Does the candidate have the technical skills to step into the role? If not, what specific gaps exist?
   - **Leadership readiness**: Does the candidate demonstrate the influence, communication, and decision-making skills required at the target level?
   - **Timeline**: How soon could the candidate be ready — immediately, within 6 months, or within 12 months?
3. Positions with no identified successor candidate are flagged as "Single Point of Failure" (SPOF) and escalated to the next management level.
4. Output: Succession Candidate Matrix — position, candidate(s), readiness assessment, and timeline.

**Stage 3: Development Plan Creation (Annual, Q1–Q2)**
1. For each succession candidate, the responsible manager creates a targeted development plan.
2. Development plan includes:
   - Specific skill gaps to address (technical and leadership)
   - Development actions: stretch assignments, mentorship pairings, training, cross-team rotations, shadowing opportunities
   - Timeline and milestones: what progress is expected by the mid-year check-in?
   - Responsible parties: who mentors, who provides stretch assignments, who reviews progress?
3. Development plans are shared with the succession candidate (succession planning is not secret — candidates benefit from knowing they are being developed for larger scope).
4. Output: Individual Development Plans for succession candidates.

**Stage 4: SPOF Mitigation (Ongoing)**
1. For positions flagged as SPOF (no viable successor candidate):
   - EM or Director develops a mitigation plan: knowledge documentation, cross-training, pair programming rotations, or targeted hiring.
   - If the SPOF is a highly specialized role (e.g., sole expert in a critical system), Director escalates to VP for strategic mitigation — potentially including redundant hiring or system simplification.
2. Output: SPOF Mitigation Plans — documented and tracked.

**Stage 5: Mid-Year Review (Annual, Q3)**
1. Responsible managers review progress on development plans and SPOF mitigations.
2. Succession Candidate Matrix updated: has readiness improved? Have new candidates emerged? Have any candidates departed or changed roles?
3. SPOF list reviewed: have mitigations been effective?
4. Output: Updated Succession Candidate Matrix and SPOF status report.

**Stage 6: Annual Succession Review (Annual, Q4)**
1. Directors present succession plans for their organizations to VPs.
2. VPs present aggregated succession health to CTO.
3. Organizational succession health metrics calculated (see Success Criteria).
4. Output: Annual Succession Health Report.

### Inputs
| Input | Source |
|-------|--------|
| L5+ team rosters | HR / People systems; EM knowledge |
| Performance review data | Annual performance review cycle |
| Career development conversations | EM 1:1s with ICs |
| Current development plans | Previous cycle succession planning |
| Attrition data and flight risk signals | HR analytics; EM observations |

### Outputs / Artifacts

| Artifact | Description | Owner | Format |
|----------|-------------|-------|--------|
| L5+ Roster | Complete list of positions requiring succession candidates | EM (IC level); Director (EM level); VP (Director level) | Spreadsheet |
| Succession Candidate Matrix | Position-to-candidate mapping with readiness assessment and timeline | EM / Director | Document / spreadsheet (restricted access) |
| Individual Development Plans | Targeted development actions for each succession candidate | EM / Director (in collaboration with candidate) | Document |
| SPOF Mitigation Plans | Mitigation strategies for positions with no successor candidate | EM / Director | Document |
| Annual Succession Health Report | Aggregated view of succession coverage, SPOF count, and development progress | VP (presented to CTO) | Document / presentation |

### Gate / Checkpoint
**Annual Succession Review Gate**

- **Participants**: VP, Directors, HR Business Partner
- **Format**: 60-minute review per VP domain; CTO reviews aggregated report
- **Timing**: Q4 annually (feeding into next year's Q1 planning)

**Pass Criteria**:
- All L5+ positions have been reviewed and have a documented succession candidate or a SPOF mitigation plan
- Development plans exist for all identified succession candidates
- SPOF positions have active mitigation plans with measurable progress
- Mid-year review was conducted and the Succession Candidate Matrix was updated
- No L5+ position has been in SPOF status for more than two consecutive annual cycles without escalation to VP

### Success Criteria
- All L5+ positions have a documented succession candidate (target: 100% coverage)
- Development plans are in place for all succession candidates (target: 100%)
- No "single point of failure" IC exists without a succession plan and active development underway
- SPOF count trending down year-over-year
- When unplanned departures of L5+ engineers occur, the team demonstrates resilience — no project delays exceeding one sprint attributable to knowledge loss

### Dependencies

| Dependency | Direction | Description |
|------------|-----------|-------------|
| P-082: Quarterly Capacity Planning | Bidirectional | Succession planning informs long-term capacity resilience; capacity constraints may limit development plan activities |
| Performance Review Cycle | Upstream | Performance data informs successor readiness assessment |
| Hiring Process | Bidirectional | SPOF mitigation may trigger targeted hiring; succession gaps inform headcount planning |

### Traceability

| Trace Point | Reference |
|-------------|-----------|
| Engineering Team Structure Guide, EM | "Owns people management: 1:1s, performance reviews, compensation inputs, career development" |
| Engineering Team Structure Guide, Director | "Drives hiring, leveling decisions, and performance management at the squad level" |
| Engineering Team Structure Guide, IC Ladder | L5+ engineers carry system-level (L5), cross-team (L6), cross-org (L7), and company-wide (L8) scope — loss of these individuals has proportionally larger impact |
| Engineering Team Structure Guide, Staff+ Scope | "Staff+ engineers lead by influence, not authority. Give them strategic mandates or they leave." — succession planning must account for the retention risk inherent in Staff+ roles |
| Process Architecture, Execution Order | Not tied to project execution order; annual cadence independent of project lifecycle |

### Risk Level
LOW (operational urgency) — Succession planning is a long-term resilience investment. The consequences of neglecting it are severe but slow-moving: organizational fragility accumulates invisibly until a key departure causes acute disruption.

### Cadence
Annual (with mid-year review checkpoint)

---

## Cross-Process Integration Map

The three Capacity & Resource Management processes form a layered system:

```
                    STRATEGIC DEMAND
                         │
                         ▼
            ┌────────────────────────────┐
            │  P-082: Quarterly Capacity  │  Cadence: Quarterly
            │  Planning Process           │
            │                            │
            │  VP → Director → EM cascade │
            │  Supply vs. demand matching │
            └──────────┬─────────────────┘
                       │
          Capacity declarations feed into
                       │
                       ▼
            ┌────────────────────────────┐
            │  P-083: Shared Resource     │  Cadence: Per-project + Quarterly
            │  Allocation Process         │
            │                            │
            │  TPM-led negotiation        │
            │  Director adjudication      │
            └──────────┬─────────────────┘
                       │
          Allocation decisions feed into
          Dependency Acceptance Gate (P-019)
                       │
                       ▼
            ┌────────────────────────────┐
            │  P-084: Succession          │  Cadence: Annual
            │  Planning Process           │
            │                            │
            │  EM/Director-led            │
            │  Long-term capacity         │
            │  resilience                 │
            └────────────────────────────┘
```

**Key integration points**:
- P-082 provides the supply-side data (how much capacity exists) that P-083 uses to detect conflicts.
- P-083 allocation decisions are a prerequisite for the Dependency Acceptance Gate (P-019) — projects cannot proceed to sprint planning with unresolved shared resource conflicts.
- P-084 feeds long-term capacity resilience data back into P-082 — SPOF positions represent hidden capacity risk that should be surfaced during quarterly planning.
- All three processes reference P-005 (Strategic Prioritization) directly or transitively for demand signals and prioritization decisions.

---

## Appendix: Agent Responsibility Summary

| Agent | P-082 Role | P-083 Role | P-084 Role |
|-------|-----------|-----------|-----------|
| `engineering-manager` (CTO) | Approves VP headcount plans | Informed | Reviews aggregated succession health |
| `engineering-manager` (VP) | Submits headcount plan | Informed; escalation path | Reviews Director succession plans |
| `engineering-manager` (Director) | Allocates squads to programs; adjudicates conflicts | Adjudicates shared resource conflicts | Owns EM-level succession plans; reviews IC succession |
| `engineering-manager` (EM) | Validates squad capacity; produces declarations | Provides shared team availability data | Owns IC-level succession plans; creates development plans |
| `product-manager` (GPM/PM) | Provides product demand signals | Participates in conflict negotiation | Not directly involved |
| `technical-program-manager` | Aggregates cross-program demand | Primary owner; drives conflict detection and resolution | Not directly involved |
| `security-engineer` | Not directly involved | Confirms AppSec availability | Not directly involved |
| `cloud-engineer` | Not directly involved | Confirms Platform/SRE availability | Not directly involved |
| `staff-principal-engineer` | Not directly involved | Not directly involved | May be succession candidate; advises on technical leadership requirements |

---

## Cross-Category Dependencies

### Dependencies FROM Other Categories (Inputs)

| Source Process | Source Category | Consuming Process | Nature |
|---------------|----------------|-------------------|--------|
| P-005 (Strategic Prioritization) | Cat 1: Intent & Strategic Alignment | P-082 (Quarterly Capacity Planning) | Strategic priorities define capacity demand |
| P-015 (Cross-Team Dependency Registration) | Cat 3: Dependency & Coordination | P-083 (Shared Resource Allocation) | Dependency Charter identifies shared resource needs |
| P-017 (Shared Resource Conflict Resolution) | Cat 3: Dependency & Coordination | P-083 (Shared Resource Allocation) | Resource conflict data |

### Dependencies TO Other Categories (Outputs)

| Providing Process | Consuming Process | Target Category | Nature |
|------------------|-------------------|-----------------|--------|
| P-082 (Quarterly Capacity Planning) | P-005 (Strategic Prioritization) | Cat 1: Intent & Strategic Alignment | Capacity data for resource allocation decisions |
| P-083 (Shared Resource Allocation) | P-019 (Dependency Acceptance Gate) | Cat 3: Dependency & Coordination | Resource allocations confirmed before gate |

## Agent Assignments Summary

| Process | Primary Owner | Supporting Agents |
|---------|--------------|-------------------|
| P-082: Quarterly Capacity Planning | engineering-manager (VP/Director/EM cascade) | product-manager, technical-program-manager |
| P-083: Shared Resource Allocation | technical-program-manager | engineering-manager (Director), security-engineer |
| P-084: Succession Planning | engineering-manager | staff-principal-engineer |
