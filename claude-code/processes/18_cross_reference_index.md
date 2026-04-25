# Cross-Reference Index

**Version**: 1.0
**Date**: 2026-04-05
**Scope**: All 93 processes across 17 categories

---

## 1. Process-to-Agent Mapping

For each of the 13 agents, which processes they own (primary) and which they support.

### product-manager

**Owns (Primary)**: P-001, P-002, P-003, P-007, P-008, P-009, P-010, P-011, P-013, P-014, P-024, P-026, P-029, P-036, P-070, P-072, P-073, P-075, P-079

**Supports**: P-004, P-005, P-012, P-017, P-018, P-019, P-022, P-023, P-025, P-027, P-028, P-031, P-034, P-038, P-041, P-042, P-048, P-054, P-061, P-065, P-066, P-071, P-076, P-078, P-082, P-091

### engineering-manager

**Owns (Primary)**: P-004, P-005, P-006, P-022, P-023, P-025, P-027, P-028, P-062, P-063, P-064, P-065, P-066, P-071, P-077, P-078, P-081, P-082, P-084, P-090, P-091, P-092

**Supports**: P-001, P-002, P-003, P-011, P-013, P-014, P-015, P-017, P-019, P-021, P-030, P-039, P-041, P-042, P-043, P-047, P-055, P-056, P-057, P-069, P-074, P-076, P-080, P-083, P-085, P-086, P-087, P-089

### technical-program-manager

**Owns (Primary)**: P-015, P-016, P-017, P-018, P-019, P-020, P-021, P-030, P-048, P-069, P-074, P-076, P-083, P-093

**Supports**: P-005, P-014, P-025, P-042, P-056, P-061, P-063, P-065, P-071, P-077, P-079, P-082, P-091

### software-engineer

**Owns (Primary)**: P-031, P-060, P-067, P-068

**Supports**: P-001, P-007, P-008, P-009, P-010, P-013, P-014, P-015, P-016, P-019, P-020, P-022, P-024, P-025, P-026, P-027, P-028, P-029, P-032, P-033, P-035, P-037, P-038, P-039, P-040, P-047, P-055, P-056, P-058, P-059, P-066, P-075, P-085, P-086, P-090, P-091, P-092, P-093

### staff-principal-engineer

**Owns (Primary)**: P-080, P-085, P-086, P-087

**Supports**: P-006, P-007, P-013, P-016, P-047, P-050, P-060, P-067, P-084, P-088

### security-engineer

**Owns (Primary)**: P-012, P-038, P-039, P-040, P-041, P-042, P-043

**Supports**: P-008, P-010, P-013, P-047, P-055, P-063, P-067, P-068, P-075, P-076, P-077, P-083, P-088

### qa-engineer

**Owns (Primary)**: P-032, P-033, P-034, P-035, P-037

**Supports**: P-008, P-024, P-025, P-036, P-048, P-049, P-058

### platform-engineer

**Owns (Primary)**: P-039, P-044, P-046, P-089

**Supports**: P-017, P-031, P-033, P-037, P-045, P-048, P-051, P-052, P-081, P-090

### cloud-engineer

**Owns (Primary)**: P-045, P-047, P-088

**Supports**: P-017, P-046

### sre

**Owns (Primary)**: P-054, P-055, P-056, P-057, P-059

**Supports**: P-009, P-032, P-035, P-048, P-049, P-050, P-052, P-053, P-055, P-066, P-076, P-081

### data-engineer

**Owns (Primary)**: P-049, P-050

**Supports**: P-009, P-042, P-051, P-073

### ml-engineer

**Owns (Primary)**: P-051, P-052, P-053

**Supports**: (none — ml-engineer is primarily a process owner within Cat 8)

### technical-writer

**Owns (Primary)**: P-058, P-061

**Supports**: P-044, P-059, P-060, P-080, P-090, P-092, P-093

---

## 2. Process-to-Clarity-of-Intent-Stage Mapping

### Stage 1: Intent Frame

Processes that govern or support the Intent Frame stage.

| Process ID | Process Name | Role in Stage 1 |
|-----------|-------------|-----------------|
| P-001 | Intent Articulation Process | Produces the Intent Brief (core artifact) |
| P-002 | OKR Alignment Verification Process | Validates strategic context (Question 3) |
| P-003 | Boundary Definition Process | Defines project boundaries (Question 4) |
| P-004 | Intent Review Gate Process | Gate for Stage 1 — all 5 criteria evaluated |
| P-005 | Strategic Prioritization Process | Upstream — determines which projects get Intent Briefs |
| P-006 | Technology Vision Alignment Process | Constrains Intent Briefs via architectural mandates |

### Stage 2: Scope Contract

Processes that govern or support the Scope Contract stage.

| Process ID | Process Name | Role in Stage 2 |
|-----------|-------------|-----------------|
| P-007 | Deliverable Decomposition Process | Scope Contract Section 2 (Deliverables) |
| P-008 | Definition of Done Authoring Process | Scope Contract Section 3 (Definition of Done) |
| P-009 | Success Metrics Definition Process | Scope Contract Section 5 (Success Metrics) |
| P-010 | Assumptions and Risks Registration Process | Scope Contract Section 6 (Assumptions and Risks) |
| P-011 | Exclusion Documentation Process | Scope Contract Section 4 (Explicit Exclusions) |
| P-012 | AppSec Scope Review Process | Security assessment of Scope Contract |
| P-013 | Scope Lock Gate Process | Gate for Stage 2 — Scope Contract versioned and locked |
| P-014 | Scope Change Control Process | Post-lock change management |
| P-032 | Test Architecture Design Process | Test strategy aligned to Scope Contract DoD |
| P-075 | Risk Register at Scope Lock Process | Risk classification for Scope Lock gate |

### Stage 3: Dependency Map

Processes that govern or support the Dependency Map stage.

| Process ID | Process Name | Role in Stage 3 |
|-----------|-------------|-----------------|
| P-015 | Cross-Team Dependency Registration Process | Dependency Charter Section 1 (Register) |
| P-016 | Critical Path Analysis Process | Dependency Charter Section 3 (Critical Path) |
| P-017 | Shared Resource Conflict Resolution Process | Dependency Charter Section 2 (Resource Conflicts) |
| P-018 | Communication Protocol Establishment Process | Dependency Charter Section 4 (Communication) |
| P-019 | Dependency Acceptance Gate Process | Gate for Stage 3 — all owners committed |
| P-083 | Shared Resource Allocation Process | Cross-project resource negotiation |
| P-093 | Technical Onboarding for Cross-Team Dependencies | Dependency context transfer |

### Stage 4: Sprint Bridge

Processes that govern or support the Sprint Bridge stage and active sprint execution.

| Process ID | Process Name | Role in Stage 4 |
|-----------|-------------|-----------------|
| P-022 | Sprint Goal Authoring Process | Sprint Kickoff Brief Section 1 (Sprint Goal) |
| P-023 | Intent Trace Validation Process | Sprint Kickoff Brief Section 2 (Intent Trace) |
| P-024 | Story Writing Process | Sprint Kickoff Brief Section 3 (Stories) |
| P-025 | Sprint Readiness Gate Process | Gate for Stage 4 — readiness check before planning |
| P-026 | Daily Standup Process | Active sprint daily synchronization |
| P-027 | Sprint Review Process | End-of-sprint demonstration and feedback |
| P-028 | Sprint Retrospective Process | End-of-sprint improvement ceremony |
| P-029 | Backlog Refinement Process | Weekly backlog grooming |
| P-030 | Sprint-Level Dependency Tracking Process | Sprint Kickoff Brief Section 4 (Dependencies) |
| P-031 | Feature Development Process | IC-level implementation workflow |
| P-091 | New Project Onboarding Process | Project kickoff for squad members |

### Post-Delivery (After Stage 4)

| Process ID | Process Name | Role Post-Delivery |
|-----------|-------------|-------------------|
| P-048 | Production Release Management Process | Release execution |
| P-070 | Project Post-Mortem Process | Project-level retrospective |
| P-071 | Quarterly Process Health Review | Process framework health check |
| P-072 | OKR Retrospective Process | OKR scoring and learnings |
| P-073 | Post-Launch Outcome Measurement Process | 30/60/90-day metric measurement |

### Cross-Stage (Continuous)

| Process ID | Process Name | When Active |
|-----------|-------------|------------|
| P-020 | Dependency Standup Process | Twice-weekly during active sprints |
| P-021 | Dependency Escalation Process | Triggered when dependency blocked >48h |
| P-034 | Definition of Done Enforcement Process | Per-story during sprints |
| P-035 | Performance Testing Process | Pre-release |
| P-036 | Acceptance Criteria Verification Process | Per-story during sprints |
| P-037 | Contract Testing Process | Per-PR on API changes |
| P-038 | Threat Modeling Process | Sprint 1 for new features |
| P-039 | SAST/DAST CI Integration Process | Every PR (continuous) |
| P-040 | CVE Triage Process | Per dependency update PR |
| P-054 | SLO Definition and Review Process | New service + quarterly review |
| P-055 | Incident Response Process | Continuous from production deployment |
| P-056 | Post-Mortem Process | After SEV-1/SEV-2 incidents |
| P-057 | On-Call Rotation Management Process | Continuous |
| P-058 | API Documentation Process | Per API-changing story |
| P-059 | Runbook Authoring Process | Before production deployment |
| P-060 | ADR Publication Process | Per significant technical decision |
| P-061 | Release Notes Process | Per production release |
| P-062-P-069 | Organizational Audit Processes | Per-cadence at each organizational layer |
| P-074 | RAID Log Maintenance Process | Weekly during active projects |

---

## 3. Process-to-Organizational-Layer Mapping

Mapping processes to the 7 organizational reporting layers defined in the Engineering Team Structure Guide.

### Layer 1: Board/CEO

| Process ID | Process Name | Layer 1 Role |
|-----------|-------------|-------------|
| P-062 | Board/CEO Audit Layer Process | Direct — CTO presents to Board |
| P-006 | Technology Vision Alignment Process | CTO chairs annual review |

### Layer 2: CTO/CPO/CISO

| Process ID | Process Name | Layer 2 Role |
|-----------|-------------|-------------|
| P-063 | CTO/CPO/CISO Executive Audit Layer Process | Direct — monthly executive audit |
| P-006 | Technology Vision Alignment Process | CTO owns technology vision |
| P-005 | Strategic Prioritization Process | VP-level scoring and sequencing |
| P-078 | OKR Cascade Communication Process | CTO derives engineering OKRs |

### Layer 3: VP of Engineering

| Process ID | Process Name | Layer 3 Role |
|-----------|-------------|-------------|
| P-064 | VP Delivery Audit Layer Process | Direct — weekly VP audit |
| P-005 | Strategic Prioritization Process | VP final authority on sequencing |
| P-077 | Quarterly Risk Review Process | VP reviews cross-Director risk patterns |
| P-081 | DORA Metrics Review | VP reviews cross-domain DORA trends |
| P-082 | Quarterly Capacity Planning Process | VP submits headcount plans |

### Layer 4: Director of Engineering

| Process ID | Process Name | Layer 4 Role |
|-----------|-------------|-------------|
| P-065 | Director Engineering Audit Layer Process | Direct — weekly EM sync + gate reviews |
| P-004 | Intent Review Gate Process | Director chairs |
| P-013 | Scope Lock Gate Process | Director attends |
| P-014 | Scope Change Control Process | Director approves scope expansion |
| P-071 | Quarterly Process Health Review | Director aggregates metrics |
| P-077 | Quarterly Risk Review Process | Director reviews RAID trends |

### Layer 5: Engineering Manager

| Process ID | Process Name | Layer 5 Role |
|-----------|-------------|-------------|
| P-066 | Engineering Manager Audit Layer Process | Direct — per-sprint audit |
| P-022 | Sprint Goal Authoring Process | EM authors sprint goals |
| P-025 | Sprint Readiness Gate Process | EM conducts readiness check |
| P-027 | Sprint Review Process | EM and PM prepare demo |
| P-028 | Sprint Retrospective Process | EM facilitates |
| P-084 | Succession Planning Process | EM identifies successors |
| P-090 | New Engineer Onboarding Process | EM owns onboarding plan |

### Layer 6: Tech Lead / Staff Engineer

| Process ID | Process Name | Layer 6 Role |
|-----------|-------------|-------------|
| P-067 | Tech Lead/Staff Engineer Audit Layer Process | Direct — per-PR and per-feature audit |
| P-060 | ADR Publication Process | TL authors ADRs |
| P-085 | RFC (Request for Comments) Process | Principal Engineers author RFCs |
| P-086 | Technical Debt Tracking Process | Staff Engineer quarterly measurement |
| P-087 | Language Tier Policy Change Process | Guild Lead approves tier changes |
| P-080 | Guild Standards Communication Process | Guild Lead publishes standards |

### Layer 7: IC / Squad Engineer

| Process ID | Process Name | Layer 7 Role |
|-----------|-------------|-------------|
| P-068 | IC/Squad Engineer Audit Layer Process | Direct — per-story self-audit |
| P-031 | Feature Development Process | IC implements stories |
| P-040 | CVE Triage Process | Security Champions at IC layer |
| P-026 | Daily Standup Process | All engineers participate |

---

## 4. Process Dependency Graph

### All Cross-Category Dependencies

The following table lists every dependency where a process in one category depends on a process in a different category.

| Consuming Process | Providing Process | Dependency Nature |
|------------------|------------------|------------------|
| P-001 (Cat 1) | P-005 (Cat 1) | Approved projects trigger Intent Briefs |
| P-001 (Cat 1) | P-006 (Cat 1) | Technology vision constrains Intent Briefs |
| P-005 (Cat 1) | P-082 (Cat 15) | Capacity data required for prioritization |
| P-007 (Cat 2) | P-004 (Cat 1) | Intent Brief locked before Scope Contract |
| P-009 (Cat 2) | P-004 (Cat 1) | Intent outcome feeds success metrics |
| P-011 (Cat 2) | P-003 (Cat 1) | Intent Brief boundaries carried forward |
| P-012 (Cat 2) | P-007 (Cat 2) | Deliverables must exist for AppSec assessment |
| P-013 (Cat 2) | P-012 (Cat 2) | AppSec scope review required for gate |
| P-015 (Cat 3) | P-013 (Cat 2) | Scope Lock gate must pass before dependency mapping |
| P-019 (Cat 3) | P-015 (Cat 3) | Dependency register required for gate |
| P-020 (Cat 3) | P-019 (Cat 3) | Dependency standups begin after gate passes |
| P-021 (Cat 3) | P-020 (Cat 3) | Escalation triggered by standup blockers |
| P-022 (Cat 4) | P-013 (Cat 2) | Scope Contract locked for sprint goal authoring |
| P-022 (Cat 4) | P-019 (Cat 3) | Dependencies accepted before sprint prep |
| P-023 (Cat 4) | P-004 (Cat 1) | Intent Brief needed for intent trace |
| P-025 (Cat 4) | P-022 (Cat 4) | Sprint goal required for readiness |
| P-025 (Cat 4) | P-030 (Cat 4) | Dependency tracking in kickoff brief |
| P-030 (Cat 4) | P-015 (Cat 3) | Dependency Charter provides sprint dependencies |
| P-031 (Cat 4) | P-025 (Cat 4) | Sprint readiness gate must pass |
| P-031 (Cat 4) | P-034 (Cat 5) | DoD enforcement for story completion |
| P-032 (Cat 5) | P-013 (Cat 2) | Scope Contract deliverables define test targets |
| P-033 (Cat 5) | P-032 (Cat 5) | Test architecture drives framework implementation |
| P-034 (Cat 5) | P-033 (Cat 5) | Automated framework enforces CI gates |
| P-034 (Cat 5) | P-024 (Cat 4) | Stories must have criteria for DoD check |
| P-035 (Cat 5) | P-054 (Cat 9) | SLOs define performance test thresholds |
| P-035 (Cat 5) | P-045 (Cat 7) | Infrastructure for load test environments |
| P-036 (Cat 5) | P-034 (Cat 5) | CI gates pass before acceptance verification |
| P-037 (Cat 5) | P-033 (Cat 5) | Test framework infrastructure needed |
| P-038 (Cat 6) | P-012 (Cat 2) | AppSec scope review confirms availability |
| P-039 (Cat 6) | P-033 (Cat 5) | CI/CD infrastructure must exist |
| P-040 (Cat 6) | P-039 (Cat 6) | SAST/DAST catches some CVEs; manual fills gaps |
| P-041 (Cat 6) | P-039 (Cat 6) | SAST/DAST finding triggers exception request |
| P-042 (Cat 6) | P-012 (Cat 2) | Scope review identifies compliance-relevant features |
| P-042 (Cat 6) | P-074 (Cat 13) | Remediation tracked in RAID Log |
| P-044 (Cat 7) | P-089 (Cat 16) | Developer NPS measures golden path satisfaction |
| P-045 (Cat 7) | P-047 (Cat 7) | CARB review for large infrastructure changes |
| P-046 (Cat 7) | P-045 (Cat 7) | IaC infrastructure enables self-service |
| P-046 (Cat 7) | P-044 (Cat 7) | Golden path provides templates |
| P-047 (Cat 7) | P-006 (Cat 1) | Technology vision provides architectural guardrails |
| P-048 (Cat 7) | P-034 (Cat 5) | DoD verification complete before release |
| P-048 (Cat 7) | P-035 (Cat 5) | Performance tests passed before release |
| P-048 (Cat 7) | P-039 (Cat 6) | SAST/DAST clean before release |
| P-048 (Cat 7) | P-076 (Cat 13) | CAB approval for high-risk changes |
| P-049 (Cat 8) | P-008 (Cat 2) | DoD for data pipelines |
| P-049 (Cat 8) | P-054 (Cat 9) | SLO definitions for data freshness |
| P-050 (Cat 8) | P-033 (Cat 5) | CI/CD integration for migration execution |
| P-051 (Cat 8) | P-049 (Cat 8) | Data pipelines provide versioned training data |
| P-052 (Cat 8) | P-051 (Cat 8) | Experiment logging required before model promotion |
| P-052 (Cat 8) | P-054 (Cat 9) | SLOs define promotion thresholds |
| P-053 (Cat 8) | P-052 (Cat 8) | Model must be in production |
| P-053 (Cat 8) | P-049 (Cat 8) | Data pipeline quality affects drift signals |
| P-055 (Cat 9) | P-054 (Cat 9) | SLOs define severity thresholds |
| P-055 (Cat 9) | P-059 (Cat 10) | Runbooks used during incidents |
| P-056 (Cat 9) | P-055 (Cat 9) | Incident must be resolved first |
| P-057 (Cat 9) | P-054 (Cat 9) | SLOs define alert thresholds |
| P-057 (Cat 9) | P-055 (Cat 9) | Incidents generate on-call demand |
| P-058 (Cat 10) | P-031 (Cat 4) | API implementation produces documentation need |
| P-058 (Cat 10) | P-034 (Cat 5) | DoD enforcement includes "API docs updated" |
| P-058 (Cat 10) | P-037 (Cat 5) | Contract tests validated against spec |
| P-059 (Cat 10) | P-048 (Cat 7) | Runbook required before production release |
| P-061 (Cat 10) | P-048 (Cat 7) | Release triggers release notes |
| P-062 (Cat 11) | P-063 (Cat 11) | Layer 2 aggregates data for Layer 1 |
| P-063 (Cat 11) | P-064 (Cat 11) | Layer 3 provides data for Layer 2 |
| P-064 (Cat 11) | P-065 (Cat 11) | Layer 4 provides data for Layer 3 |
| P-065 (Cat 11) | P-066 (Cat 11) | Layer 5 provides data for Layer 4 |
| P-066 (Cat 11) | P-067 (Cat 11) | Layer 6 provides data for Layer 5 |
| P-067 (Cat 11) | P-068 (Cat 11) | Layer 7 produces work reviewed by Layer 6 |
| P-069 (Cat 11) | P-062-P-068 (Cat 11) | All audit layers feed finding flow |
| P-069 (Cat 11) | P-074 (Cat 13) | Findings tracked in RAID Log |
| P-070 (Cat 12) | P-073 (Cat 12) | 30-day data needed for post-mortem |
| P-071 (Cat 12) | P-070 (Cat 12) | Post-mortem action items feed process health |
| P-072 (Cat 12) | P-073 (Cat 12) | Success metric data feeds OKR scoring |
| P-073 (Cat 12) | P-013 (Cat 2) | Scope Contract defines metrics to measure |
| P-074 (Cat 13) | P-010 (Cat 2) | RAID Log seeded from Scope Contract assumptions |
| P-074 (Cat 13) | P-065 (Cat 11) | Director reviews RAID Log in weekly sync |
| P-075 (Cat 13) | P-007 (Cat 2) | Scope shape needed for risk identification |
| P-075 (Cat 13) | P-013 (Cat 2) | Scope Lock gate consumes risk register |
| P-076 (Cat 13) | P-035 (Cat 5) | Performance tests must pass before CAB |
| P-076 (Cat 13) | P-039 (Cat 6) | SAST/DAST clean before CAB |
| P-078 (Cat 14) | P-005 (Cat 1) | Strategic priorities feed OKR cascade |
| P-078 (Cat 14) | P-072 (Cat 12) | OKR retrospective provides input for next cascade |
| P-082 (Cat 15) | P-005 (Cat 1) | Strategic priorities define capacity demand |
| P-083 (Cat 15) | P-015 (Cat 3) | Dependency Charter identifies shared resource needs |
| P-083 (Cat 15) | P-017 (Cat 3) | Resource conflict data |
| P-088 (Cat 16) | P-047 (Cat 7) | CARB is the operational review process |
| P-088 (Cat 16) | P-006 (Cat 1) | Technology vision guides pattern decisions |
| P-088 (Cat 16) | P-085 (Cat 16) | RFC decisions inform pattern standards |
| P-090 (Cat 17) | P-044 (Cat 7) | Golden path for environment setup |
| P-090 (Cat 17) | P-089 (Cat 16) | Onboarding experience feeds developer NPS |
| P-091 (Cat 17) | P-019 (Cat 3) | Dependency Acceptance gate triggers project onboarding |
| P-091 (Cat 17) | P-025 (Cat 4) | Sprint Readiness gate requires engineer comprehension |
| P-093 (Cat 17) | P-019 (Cat 3) | New dependencies identified at Dependency Acceptance |
| P-093 (Cat 17) | P-058 (Cat 10) | API documentation shared for dependency context |
| P-093 (Cat 17) | P-059 (Cat 10) | Runbooks shared for dependency context |

---

## 5. Gate/Checkpoint Master List

### Formal Stage Gates (4 Clarity of Intent Gates)

| Gate Name | Process ID | Stage | Chair | Format | Duration | Pass Criteria Summary |
|-----------|-----------|-------|-------|--------|----------|----------------------|
| Intent Review Gate | P-004 | Stage 1 | Engineering Director | 30-min meeting or 48h async | 30 min | All 5 Intent Brief questions answered with specifics; measurable outcome with timeline; at least 1 exclusion; real OKR reference; all reviewers can explain project purpose |
| Scope Lock Gate | P-013 | Stage 2 | PM | 60-min meeting | 60 min | Every deliverable has owner; every deliverable has testable DoD; exclusions acknowledged; metrics trace to intent; HIGH assumptions have validation plans; all participants confirm responsibilities |
| Dependency Acceptance Gate | P-019 | Stage 3 | TPM | 45-min meeting | 45 min | Every dependency has owner and date; every owner verbally committed; critical path documented; escalation paths defined; no unresolved HIGH blockers; communication protocol agreed |
| Sprint Readiness Gate | P-025 | Stage 4 | EM | Start of sprint planning | 10-15 min | Sprint goal connected to Scope Contract; intent trace visible; all stories have criteria; dependencies have status and contingency; every engineer knows what/why/done |

### Governance Gates

| Gate Name | Process ID | Chair | Cadence | Purpose |
|-----------|-----------|-------|---------|---------|
| CISO Approval Gate | P-041 | CISO | Per security exception | No security exception without CISO sign-off |
| CARB Review Gate | P-047 | Cloud Architect | Weekly | New cloud services, pattern changes, cost commitments |
| CAB Review Gate | P-076 | Release Manager | Per HIGH-risk release | HIGH-risk production change review |
| Go/No-Go Release Gate | P-048 | Release Manager | Per release | All quality, security, reliability gates pass |

### Per-Story Gates

| Gate Name | Process ID | Verifier | Cadence | Purpose |
|-----------|-----------|----------|---------|---------|
| CI Gates (automated) | P-031, P-034 | CI/CD pipeline | Per PR | Tests pass, SAST clean, coverage thresholds |
| Acceptance Criteria Verification | P-036 | PM or QA | Per story | Each criterion marked PASS/FAIL |
| DoD Enforcement | P-034 | QA + PM | Per story | Full DoD checklist confirmed |
| Contract Test Gate | P-037 | CI/CD pipeline | Per API-touching PR | Contract violations block merge |

### Audit Checkpoints

| Checkpoint | Process ID | Auditor | Cadence | Scope |
|------------|-----------|---------|---------|-------|
| Board/CEO Technology Review | P-062 | Board/CEO | Quarterly | Technology strategy, security, major decisions |
| Executive Audit | P-063 | CTO | Monthly/Quarterly | Cross-domain OKR progress, DORA, security |
| VP Delivery Audit | P-064 | VP | Weekly/Monthly | Director-level delivery health |
| Director EM Sync | P-065 | Director | Weekly + per-gate | Squad delivery, gate decisions, DORA trends |
| EM Sprint Audit | P-066 | EM | Per-sprint | IC performance, DoD compliance, on-call burden |
| TL/Staff Code Audit | P-067 | TL/Staff | Per-PR | Code quality, ADR completeness, architecture |
| IC Self-Audit | P-068 | IC | Per-story | Acceptance criteria, DoD self-check |

### Periodic Review Checkpoints

| Checkpoint | Process ID | Owner | Cadence | Purpose |
|------------|-----------|-------|---------|---------|
| Quarterly Process Health Review | P-071 | Director + VP | Quarterly | Process framework health signals |
| OKR Retrospective | P-072 | PM | Quarterly | OKR scoring and learnings |
| Post-Launch Outcome Measurement | P-073 | PM | 30/60/90 days | Success metrics vs. targets |
| Quarterly Risk Review | P-077 | Director + VP | Quarterly | RAID Log trend analysis |
| Security Champions Training | P-043 | AppSec Lead | Quarterly | Threat landscape, OWASP, tool proficiency |
| SLO Error Budget Review | P-054 | SRE | Quarterly | Error budget burn; reliability investment |
| Technical Debt Report | P-086 | Staff Engineer | Quarterly | Codebase health metrics |
| Developer Experience Survey | P-089 | DX Engineer | Quarterly | Developer NPS and friction points |
| Succession Plan Review | P-084 | EM + Director | Annual | L5+ succession candidates |
| Technology Vision Review | P-006 | CTO | Annual | Multi-year architecture alignment |

---

## 6. Process Count Summary

| # | Category | Process IDs | Count |
|---|----------|-------------|-------|
| 1 | Intent & Strategic Alignment | P-001 to P-006 | 6 |
| 2 | Scope & Contract Management | P-007 to P-014 | 8 |
| 3 | Dependency & Coordination Management | P-015 to P-021 | 7 |
| 4 | Sprint & Delivery Execution | P-022 to P-031 | 10 |
| 5 | Quality Assurance & Testing | P-032 to P-037 | 6 |
| 6 | Security & Compliance | P-038 to P-043 | 6 |
| 7 | Infrastructure & Platform | P-044 to P-048 | 5 |
| 8 | Data & ML Operations | P-049 to P-053 | 5 |
| 9 | Site Reliability & Operations | P-054 to P-057 | 4 |
| 10 | Documentation & Knowledge Management | P-058 to P-061 | 4 |
| 11 | Organizational Hierarchy Audit (MANDATORY) | P-062 to P-069 | 8 |
| 12 | Post-Delivery & Retrospective | P-070 to P-073 | 4 |
| 13 | Risk & Change Management | P-074 to P-077 | 4 |
| 14 | Communication & Alignment | P-078 to P-081 | 4 |
| 15 | Capacity & Resource Management | P-082 to P-084 | 3 |
| 16 | Technical Excellence & Standards | P-085 to P-089 | 5 |
| 17 | Onboarding & Knowledge Transfer | P-090 to P-093 | 4 |
| **TOTAL** | | | **93** |
