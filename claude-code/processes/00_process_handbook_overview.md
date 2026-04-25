# Engineering Processes Handbook — Master Overview

**Version**: 1.0
**Date**: 2026-04-05
**Source**: Clarity of Intent Framework, Engineering Team Structure Guide, Process Architecture (Stage 1), Process Specifications (Stage 2)
**Status**: Production

---

## Executive Summary

This handbook consolidates 93 formally specified engineering processes across 17 categories into a single, navigable reference. Every process in this handbook is derived from two foundational documents:

1. **The Clarity of Intent Framework** — A 4-stage process (Intent Frame, Scope Contract, Dependency Map, Sprint Bridge) that translates project vision into aligned, executable work. Each stage produces a specific artifact and enforces a gate review before the next stage begins.

2. **The Engineering Team Structure Guide** — A comprehensive organizational model defining 13 agent roles across 7 reporting layers (Board/CEO through IC), operating in a hybrid hierarchical + squad model.

The process framework covers the full lifecycle of engineering work: from strategic intent articulation through scope definition, dependency management, sprint execution, quality assurance, security compliance, infrastructure provisioning, data/ML operations, site reliability, documentation, organizational audit, post-delivery measurement, risk management, communication, capacity planning, technical excellence standards, and onboarding.

### How It Derives from the Clarity of Intent Framework

The Clarity of Intent framework provides the backbone for project delivery:

- **Stage 1 (Intent Frame)** produces the Intent Brief and is governed by Category 1 processes (P-001 through P-006)
- **Stage 2 (Scope Contract)** produces the Scope Contract and is governed by Category 2 processes (P-007 through P-014)
- **Stage 3 (Dependency Map)** produces the Dependency Charter and is governed by Category 3 processes (P-015 through P-021)
- **Stage 4 (Sprint Bridge)** produces the Sprint Kickoff Brief and is governed by Category 4 processes (P-022 through P-031)

The remaining 13 categories (5 through 17) provide the supporting infrastructure, governance, and operational processes that make the core delivery pipeline reliable and sustainable.

---

## Master Process Table

All 93 processes organized by category with ID, name, and primary owner agent.

| ID | Process Name | Category | Primary Owner Agent |
|----|-------------|----------|-------------------|
| P-001 | Intent Articulation Process | 1. Intent & Strategic Alignment | product-manager |
| P-002 | OKR Alignment Verification Process | 1. Intent & Strategic Alignment | product-manager |
| P-003 | Boundary Definition Process | 1. Intent & Strategic Alignment | product-manager |
| P-004 | Intent Review Gate Process | 1. Intent & Strategic Alignment | engineering-manager |
| P-005 | Strategic Prioritization Process | 1. Intent & Strategic Alignment | engineering-manager |
| P-006 | Technology Vision Alignment Process | 1. Intent & Strategic Alignment | engineering-manager |
| P-007 | Deliverable Decomposition Process | 2. Scope & Contract Management | product-manager |
| P-008 | Definition of Done Authoring Process | 2. Scope & Contract Management | product-manager |
| P-009 | Success Metrics Definition Process | 2. Scope & Contract Management | product-manager |
| P-010 | Assumptions and Risks Registration Process | 2. Scope & Contract Management | product-manager |
| P-011 | Exclusion Documentation Process | 2. Scope & Contract Management | product-manager |
| P-012 | AppSec Scope Review Process | 2. Scope & Contract Management | security-engineer |
| P-013 | Scope Lock Gate Process | 2. Scope & Contract Management | product-manager |
| P-014 | Scope Change Control Process | 2. Scope & Contract Management | product-manager |
| P-015 | Cross-Team Dependency Registration Process | 3. Dependency & Coordination | technical-program-manager |
| P-016 | Critical Path Analysis Process | 3. Dependency & Coordination | technical-program-manager |
| P-017 | Shared Resource Conflict Resolution Process | 3. Dependency & Coordination | technical-program-manager |
| P-018 | Communication Protocol Establishment Process | 3. Dependency & Coordination | technical-program-manager |
| P-019 | Dependency Acceptance Gate Process | 3. Dependency & Coordination | technical-program-manager |
| P-020 | Dependency Standup Process | 3. Dependency & Coordination | technical-program-manager |
| P-021 | Dependency Escalation Process | 3. Dependency & Coordination | technical-program-manager |
| P-022 | Sprint Goal Authoring Process | 4. Sprint & Delivery Execution | engineering-manager |
| P-023 | Intent Trace Validation Process | 4. Sprint & Delivery Execution | engineering-manager |
| P-024 | Story Writing Process | 4. Sprint & Delivery Execution | product-manager |
| P-025 | Sprint Readiness Gate Process | 4. Sprint & Delivery Execution | engineering-manager |
| P-026 | Daily Standup Process | 4. Sprint & Delivery Execution | product-manager |
| P-027 | Sprint Review Process | 4. Sprint & Delivery Execution | engineering-manager |
| P-028 | Sprint Retrospective Process | 4. Sprint & Delivery Execution | engineering-manager |
| P-029 | Backlog Refinement Process | 4. Sprint & Delivery Execution | product-manager |
| P-030 | Sprint-Level Dependency Tracking Process | 4. Sprint & Delivery Execution | technical-program-manager |
| P-031 | Feature Development Process | 4. Sprint & Delivery Execution | software-engineer |
| P-032 | Test Architecture Design Process | 5. Quality Assurance & Testing | qa-engineer |
| P-033 | Automated Test Framework Process | 5. Quality Assurance & Testing | qa-engineer |
| P-034 | Definition of Done Enforcement Process | 5. Quality Assurance & Testing | qa-engineer |
| P-035 | Performance Testing Process | 5. Quality Assurance & Testing | qa-engineer |
| P-036 | Acceptance Criteria Verification Process | 5. Quality Assurance & Testing | product-manager |
| P-037 | Contract Testing Process | 5. Quality Assurance & Testing | qa-engineer |
| P-038 | Threat Modeling Process | 6. Security & Compliance | security-engineer |
| P-039 | SAST/DAST CI Integration Process | 6. Security & Compliance | platform-engineer |
| P-040 | CVE Triage Process | 6. Security & Compliance | security-engineer |
| P-041 | Security Exception Process | 6. Security & Compliance | security-engineer |
| P-042 | Compliance Review Process | 6. Security & Compliance | security-engineer |
| P-043 | Security Champions Training Process | 6. Security & Compliance | security-engineer |
| P-044 | Golden Path Adoption Process | 7. Infrastructure & Platform | platform-engineer |
| P-045 | Infrastructure Provisioning Process | 7. Infrastructure & Platform | cloud-engineer |
| P-046 | Environment Self-Service Process | 7. Infrastructure & Platform | platform-engineer |
| P-047 | Cloud Architecture Review Board (CARB) Process | 7. Infrastructure & Platform | cloud-engineer |
| P-048 | Production Release Management Process | 7. Infrastructure & Platform | technical-program-manager |
| P-049 | Data Pipeline Quality Assurance Process | 8. Data & ML Operations | data-engineer |
| P-050 | Data Schema Migration Process | 8. Data & ML Operations | data-engineer |
| P-051 | ML Experiment Logging Process | 8. Data & ML Operations | ml-engineer |
| P-052 | Model Canary Deployment Process | 8. Data & ML Operations | ml-engineer |
| P-053 | Data Drift Monitoring Process | 8. Data & ML Operations | ml-engineer |
| P-054 | SLO Definition and Review Process | 9. SRE & Operations | sre |
| P-055 | Incident Response Process | 9. SRE & Operations | sre |
| P-056 | Post-Mortem Process | 9. SRE & Operations | sre |
| P-057 | On-Call Rotation Management Process | 9. SRE & Operations | sre |
| P-058 | API Documentation Process | 10. Documentation & Knowledge Management | technical-writer |
| P-059 | Runbook Authoring Process | 10. Documentation & Knowledge Management | sre |
| P-060 | ADR Publication Process | 10. Documentation & Knowledge Management | software-engineer |
| P-061 | Release Notes Process | 10. Documentation & Knowledge Management | technical-writer |
| P-062 | Board/CEO Audit Layer Process (Layer 1) | 11. Organizational Hierarchy Audit | engineering-manager |
| P-063 | CTO/CPO/CISO Executive Audit Layer Process (Layer 2) | 11. Organizational Hierarchy Audit | engineering-manager |
| P-064 | VP Delivery Audit Layer Process (Layer 3) | 11. Organizational Hierarchy Audit | engineering-manager |
| P-065 | Director Engineering Audit Layer Process (Layer 4) | 11. Organizational Hierarchy Audit | engineering-manager |
| P-066 | Engineering Manager Audit Layer Process (Layer 5) | 11. Organizational Hierarchy Audit | engineering-manager |
| P-067 | Tech Lead/Staff Engineer Audit Layer Process (Layer 6) | 11. Organizational Hierarchy Audit | software-engineer |
| P-068 | IC/Squad Engineer Audit Layer Process (Layer 7) | 11. Organizational Hierarchy Audit | software-engineer |
| P-069 | Audit Finding Flow Process | 11. Organizational Hierarchy Audit | technical-program-manager |
| P-070 | Project Post-Mortem Process | 12. Post-Delivery & Retrospective | product-manager |
| P-071 | Quarterly Process Health Review | 12. Post-Delivery & Retrospective | engineering-manager |
| P-072 | OKR Retrospective Process | 12. Post-Delivery & Retrospective | product-manager |
| P-073 | Post-Launch Outcome Measurement Process | 12. Post-Delivery & Retrospective | product-manager |
| P-074 | RAID Log Maintenance Process | 13. Risk & Change Management | technical-program-manager |
| P-075 | Risk Register at Scope Lock Process | 13. Risk & Change Management | product-manager |
| P-076 | Pre-Launch Risk Review Process (CAB) | 13. Risk & Change Management | technical-program-manager |
| P-077 | Quarterly Risk Review Process | 13. Risk & Change Management | engineering-manager |
| P-078 | OKR Cascade Communication Process | 14. Communication & Alignment | engineering-manager |
| P-079 | Stakeholder Update Cadence Process | 14. Communication & Alignment | product-manager |
| P-080 | Guild Standards Communication Process | 14. Communication & Alignment | staff-principal-engineer |
| P-081 | DORA Metrics Review and Sharing Process | 14. Communication & Alignment | engineering-manager |
| P-082 | Quarterly Capacity Planning Process | 15. Capacity & Resource Management | engineering-manager |
| P-083 | Shared Resource Allocation Process | 15. Capacity & Resource Management | technical-program-manager |
| P-084 | Succession Planning Process | 15. Capacity & Resource Management | engineering-manager |
| P-085 | RFC (Request for Comments) Process | 16. Technical Excellence & Standards | staff-principal-engineer |
| P-086 | Technical Debt Tracking Process | 16. Technical Excellence & Standards | staff-principal-engineer |
| P-087 | Language Tier Policy Change Process | 16. Technical Excellence & Standards | staff-principal-engineer |
| P-088 | Architecture Pattern Change Process | 16. Technical Excellence & Standards | cloud-engineer |
| P-089 | Developer Experience Survey Process | 16. Technical Excellence & Standards | platform-engineer |
| P-090 | New Engineer Onboarding Process | 17. Onboarding & Knowledge Transfer | engineering-manager |
| P-091 | New Project Onboarding Process | 17. Onboarding & Knowledge Transfer | engineering-manager |
| P-092 | Knowledge Transfer Process | 17. Onboarding & Knowledge Transfer | engineering-manager |
| P-093 | Technical Onboarding for Cross-Team Dependencies Process | 17. Onboarding & Knowledge Transfer | technical-program-manager |

---

## Process Lifecycle Diagram

The following diagram shows how the 17 process categories flow from strategic intent through delivery to post-delivery measurement. The core delivery pipeline (Categories 1-4) is the backbone; all other categories provide supporting capabilities.

```
                              STRATEGIC LAYER
    ┌─────────────────────────────────────────────────────────────────┐
    │                                                                 │
    │  Cat 14: Communication     Cat 15: Capacity &    Cat 16: Tech  │
    │  & Alignment               Resource Mgmt         Excellence    │
    │  (P-078 to P-081)          (P-082 to P-084)      (P-085-P-089) │
    │                                                                 │
    └──────────────────────────────┬──────────────────────────────────┘
                                   │
                                   ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                    CORE DELIVERY PIPELINE                       │
    │                                                                 │
    │  Cat 1: Intent &      Cat 2: Scope &      Cat 3: Dependency   │
    │  Strategic Alignment   Contract Mgmt       & Coordination      │
    │  (P-001 to P-006)     (P-007 to P-014)    (P-015 to P-021)   │
    │        │                    │                    │              │
    │        ▼                    ▼                    ▼              │
    │  Intent Brief ──────► Scope Contract ────► Dependency Charter  │
    │  Gate: P-004           Gate: P-013         Gate: P-019         │
    │                                                                 │
    │                    Cat 4: Sprint & Delivery Execution           │
    │                    (P-022 to P-031)                             │
    │                         │                                       │
    │                         ▼                                       │
    │                    Sprint Kickoff Brief                         │
    │                    Gate: P-025                                  │
    │                         │                                       │
    │                         ▼                                       │
    │                    Active Sprint Execution                      │
    │                         │                                       │
    │                         ▼                                       │
    │                    Production Release                           │
    │                                                                 │
    └──────────────────────────────┬──────────────────────────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
          ▼                        ▼                        ▼
    ┌───────────┐           ┌───────────┐           ┌───────────┐
    │ QUALITY   │           │ SECURITY  │           │ INFRA     │
    │ Cat 5     │           │ Cat 6     │           │ Cat 7     │
    │ P-032-037 │           │ P-038-043 │           │ P-044-048 │
    └───────────┘           └───────────┘           └───────────┘
          │                        │                        │
          ▼                        ▼                        ▼
    ┌───────────┐           ┌───────────┐           ┌───────────┐
    │ DATA/ML   │           │ SRE       │           │ DOCS      │
    │ Cat 8     │           │ Cat 9     │           │ Cat 10    │
    │ P-049-053 │           │ P-054-057 │           │ P-058-061 │
    └───────────┘           └───────────┘           └───────────┘
                                   │
                                   ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                     GOVERNANCE LAYER                            │
    │                                                                 │
    │  Cat 11: Organizational    Cat 13: Risk &     Cat 17:          │
    │  Hierarchy Audit           Change Mgmt        Onboarding &     │
    │  (P-062 to P-069)         (P-074 to P-077)   Knowledge Xfer   │
    │                                               (P-090 to P-093) │
    │                                                                 │
    └──────────────────────────────┬──────────────────────────────────┘
                                   │
                                   ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                     POST-DELIVERY LAYER                         │
    │                                                                 │
    │  Cat 12: Post-Delivery & Retrospective (P-070 to P-073)       │
    │  - Project Post-Mortem (P-070)                                  │
    │  - Quarterly Process Health Review (P-071)                      │
    │  - OKR Retrospective (P-072)                                    │
    │  - Post-Launch Outcome Measurement at 30/60/90 days (P-073)    │
    │                                                                 │
    └─────────────────────────────────────────────────────────────────┘
```

---

## Agent Responsibility Matrix

The 13 agents and their relationship to each of the 17 process categories. **O** = Owner (primary responsibility for at least one process in the category), **S** = Supporting (named supporting agent), **I** = Informed (receives outputs or is affected).

| Agent | Cat 1 | Cat 2 | Cat 3 | Cat 4 | Cat 5 | Cat 6 | Cat 7 | Cat 8 | Cat 9 | Cat 10 | Cat 11 | Cat 12 | Cat 13 | Cat 14 | Cat 15 | Cat 16 | Cat 17 |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|--------|--------|--------|--------|--------|--------|--------|--------|
| product-manager | O | O | S | O | O | S | — | — | S | S | S | O | O | O | S | — | S |
| engineering-manager | O | S | S | O | — | S | — | — | S | — | O | O | O | O | O | S | O |
| technical-program-manager | S | S | O | O | — | — | O | — | — | S | O | S | O | S | O | — | O |
| software-engineer | S | S | S | O | S | S | — | — | S | O | O | — | S | — | — | S | S |
| staff-principal-engineer | S | S | S | — | — | — | S | — | — | S | S | — | S | O | S | O | — |
| security-engineer | — | O | — | — | — | O | S | — | S | — | S | — | — | — | — | S | — |
| qa-engineer | — | S | — | S | O | — | — | S | — | S | — | — | — | — | — | — | — |
| platform-engineer | — | — | S | S | S | O | O | S | — | — | — | — | — | S | — | O | S |
| cloud-engineer | — | — | S | — | — | — | O | — | — | — | — | — | — | — | — | O | — |
| sre | — | — | — | — | S | — | S | S | O | O | — | — | S | S | — | — | — |
| data-engineer | — | — | — | — | — | S | — | O | — | — | — | — | — | — | — | — | — |
| ml-engineer | — | — | — | — | — | — | — | O | — | — | — | — | — | — | — | — | — |
| technical-writer | — | — | — | — | — | — | S | — | — | O | — | — | — | S | — | — | S |

### Agent Legend

| Agent ID | Roles Covered |
|----------|--------------|
| product-manager | APM, PM, GPM, CPO; Scrum Master; Agile Coach |
| engineering-manager | EM (M4-M5), Director, VP, CTO |
| technical-program-manager | TPM; Program Manager; Release Manager; RTE |
| software-engineer | L3-L5 IC; Tech Lead (TL) |
| staff-principal-engineer | Staff (L6), Principal (L7), Distinguished (L8), Fellow (L9) |
| security-engineer | CISO, AppSec Lead, Security Champion; SOC; GRC; Red/Blue/Purple |
| qa-engineer | QA Lead; Manual QA (L3-L5); SDET (L4-L6); Performance Engineer |
| platform-engineer | Platform Engineer; DevOps; Release Engineer; DX Engineer |
| cloud-engineer | Cloud Architect, Cloud Engineers (AWS/Azure/GCP); FinOps Engineer |
| sre | SRE (L4-L6); Observability Engineer; SRE Lead |
| data-engineer | Data Engineer (L4-L6); Analytics Engineer; Data Architect |
| ml-engineer | ML Engineer (L4-L6); MLOps Engineer; AI/ML Researcher |
| technical-writer | Technical Writer (L3-L5); Developer Advocate; Solutions Architect (L6-L7) |

---

## Cross-Process Dependency Summary

### Core Delivery Critical Path

The minimum sequence of processes from project initiation to post-launch measurement:

```
P-001 --> P-002 + P-003 --> P-004 --> P-007 --> P-008 + P-009 + P-011 + P-012
  --> P-013 --> P-015 --> P-016 + P-017 + P-018 --> P-019 --> P-022 --> P-023 + P-024
  --> P-025 --> P-026 + P-031 --> P-034 --> P-036 --> P-027 --> P-048 --> P-073
```

**Elapsed time for critical path**: 8-15 working days from intent to Sprint 1 readiness (consistent with the Clarity of Intent 8-12 day target).

### Process Execution Programs

Processes are organized into 18 execution programs based on dependency ordering:

| Program | Name | Processes | Blocked By |
|---------|------|-----------|------------|
| 0 | Foundation | P-001, P-005, P-006, P-043, P-054, P-062-P-068, P-071, P-074, P-078, P-081, P-082, P-086, P-089 | None |
| 1 | Intent Verification | P-002, P-003 | P-001 |
| 2 | Intent Gate | P-004 | P-001, P-002, P-003 |
| 3 | Scope Authoring | P-007, P-010 | P-004 |
| 4 | Scope Completion | P-008, P-009, P-011, P-012, P-032, P-075 | P-007, P-010 |
| 5 | Scope Gate | P-013 | P-007-P-012, P-075 |
| 6 | Dependency Mapping | P-015, P-033, P-039 | P-013, P-032 |
| 7 | Dependency Completion | P-016, P-017, P-018, P-083 | P-015 |
| 8 | Dependency Gate | P-019 | P-015-P-018, P-083 |
| 9 | Sprint Preparation | P-022, P-091, P-093 | P-019 |
| 10 | Sprint Kickoff | P-023, P-024, P-029, P-030 | P-022 |
| 11 | Sprint Gate | P-025 | P-022-P-024, P-030 |
| 12 | Active Sprint | P-026, P-020, P-031, P-038 | P-025 |
| 13 | Quality Gates | P-034, P-036, P-035, P-037 | P-031 |
| 14 | Sprint Close | P-027, P-028 | Sprint completion |
| 15 | Release Gate | P-076, P-048, P-058, P-059, P-061 | P-034, P-035, P-039 |
| 16 | Post-Launch | P-073, P-055, P-056 | P-048, P-054 |
| 17 | Project Close | P-070, P-072 | Project completion |

### Key Cross-Category Dependencies

| From Process | To Process | Nature |
|-------------|-----------|--------|
| P-004 (Cat 1) | P-007+ (Cat 2) | Intent Brief must be locked before Scope Contract begins |
| P-013 (Cat 2) | P-015 (Cat 3) | Scope Contract must be locked before Dependency Mapping |
| P-019 (Cat 3) | P-022 (Cat 4) | Dependencies accepted before Sprint Bridge |
| P-007 (Cat 2) | P-032 (Cat 5) | Deliverables defined before Test Architecture |
| P-012 (Cat 2) | P-038 (Cat 6) | AppSec Scope Review enables Threat Modeling |
| P-033 (Cat 5) | P-039 (Cat 6) | Test framework required for SAST/DAST integration |
| P-054 (Cat 9) | P-035 (Cat 5) | SLO definitions required for Performance Testing thresholds |
| P-054 (Cat 9) | P-055 (Cat 9) | SLOs define incident severity thresholds |
| P-031 (Cat 4) | P-058 (Cat 10) | Feature development produces API changes needing documentation |
| P-048 (Cat 7) | P-059 (Cat 10) | Runbooks required before production release |
| P-048 (Cat 7) | P-061 (Cat 10) | Release triggers release notes |
| P-082 (Cat 15) | P-005 (Cat 1) | Capacity data required for strategic prioritization |
| P-005 (Cat 1) | P-078 (Cat 14) | Strategic priorities feed OKR cascade |
| P-013 (Cat 2) | P-073 (Cat 12) | Scope Contract defines success metrics to measure post-launch |
| P-074 (Cat 13) | P-065 (Cat 11) | RAID Log reviewed in Director audit |
| P-069 (Cat 11) | P-074 (Cat 13) | Audit findings tracked in RAID Log |

### Four Formal Gates

| Gate | Process ID | Stage | Chaired By | Key Pass Criteria |
|------|-----------|-------|-----------|------------------|
| Intent Review | P-004 | Stage 1 | Engineering Director | All 5 questions answered; measurable outcome; OKR reference; boundary stated |
| Scope Lock | P-013 | Stage 2 | PM | Every deliverable owned; DoD written; exclusions acknowledged; metrics trace to intent |
| Dependency Acceptance | P-019 | Stage 3 | TPM | Every dependency owner committed; critical path documented; escalation paths defined |
| Sprint Readiness | P-025 | Stage 4 | EM | Sprint goal connected; intent trace visible; stories have criteria; engineers can explain what/why/done |

---

## How to Use This Handbook

### For Engineering Managers (EMs)

1. Start with the **Core Delivery Pipeline** (Categories 1-4) for any new project
2. Use Category 11 (**Organizational Audit**) to understand your weekly audit responsibilities (P-066)
3. Reference Category 15 (**Capacity & Resource Management**) for quarterly planning
4. Check Category 12 (**Post-Delivery**) for retrospective and measurement processes

### For Product Managers (PMs)

1. Begin every project with P-001 (**Intent Articulation**) and follow through P-004 (**Intent Review Gate**)
2. Own the Scope Contract processes in Category 2 (P-007 through P-014)
3. Use P-024 (**Story Writing**) and P-029 (**Backlog Refinement**) for sprint preparation
4. Measure outcomes with P-073 (**Post-Launch Outcome Measurement**)

### For Technical Program Managers (TPMs)

1. Own Category 3 (**Dependency & Coordination**) end-to-end
2. Maintain the RAID Log (P-074) throughout the project
3. Run dependency standups (P-020) and escalate blockers (P-021)
4. Manage production releases (P-048) and pre-launch CAB reviews (P-076)

### For Tech Leads and Staff Engineers

1. Participate in Scope Contract authoring (P-007, P-008) and gate reviews
2. Own technical audit layer (P-067) — review every PR and ADR
3. Use Category 16 (**Technical Excellence**) for RFCs (P-085), tech debt tracking (P-086), and standards
4. Publish Architecture Decision Records per P-060

### For Security Engineers

1. Engage early via P-012 (**AppSec Scope Review**) at Stage 2
2. Run threat models (P-038) in Sprint 1
3. Monitor SAST/DAST (P-039), triage CVEs (P-040), manage exceptions (P-041)
4. Train Security Champions quarterly (P-043)

### For SREs

1. Define SLOs for every service (P-054) before production deployment
2. Own incident response (P-055) and post-mortems (P-056)
3. Author runbooks (P-059) and manage on-call rotations (P-057)

### Navigating the Documents

- **This file** (`00_process_handbook_overview.md`): Start here for orientation, the master process table, and the agent responsibility matrix
- **Category files** (`01_` through `17_`): Full process specifications for each category
- **Cross-reference index** (`18_cross_reference_index.md`): Process-to-agent mappings, process-to-stage mappings, dependency graph, gate/checkpoint master list

### Process ID Convention

All processes use the format **P-NNN** where NNN is a zero-padded three-digit number from 001 to 093. Cross-references between processes always use this ID format.

---

## Document Index

| File | Contents |
|------|---------|
| `00_process_handbook_overview.md` | This document — master overview, process table, lifecycle diagram, agent matrix |
| `01_intent_strategic_alignment.md` | Category 1: P-001 to P-006 — Intent & Strategic Alignment |
| `02_scope_contract_management.md` | Category 2: P-007 to P-014 — Scope & Contract Management |
| `03_dependency_coordination.md` | Category 3: P-015 to P-021 — Dependency & Coordination |
| `04_sprint_delivery_execution.md` | Category 4: P-022 to P-031 — Sprint & Delivery Execution |
| `05_quality_assurance_testing.md` | Category 5: P-032 to P-037 — Quality Assurance & Testing |
| `06_security_compliance.md` | Category 6: P-038 to P-043 — Security & Compliance |
| `07_infrastructure_platform.md` | Category 7: P-044 to P-048 — Infrastructure & Platform |
| `08_data_ml_operations.md` | Category 8: P-049 to P-053 — Data & ML Operations |
| `09_sre_operations.md` | Category 9: P-054 to P-057 — SRE & Operations |
| `10_documentation_knowledge.md` | Category 10: P-058 to P-061 — Documentation & Knowledge Management |
| `11_organizational_audit.md` | Category 11: P-062 to P-069 — Organizational Hierarchy Audit |
| `12_post_delivery_retrospective.md` | Category 12: P-070 to P-073 — Post-Delivery & Retrospective |
| `13_risk_change_management.md` | Category 13: P-074 to P-077 — Risk & Change Management |
| `14_communication_alignment.md` | Category 14: P-078 to P-081 — Communication & Alignment |
| `15_capacity_resource_management.md` | Category 15: P-082 to P-084 — Capacity & Resource Management |
| `16_technical_excellence_standards.md` | Category 16: P-085 to P-089 — Technical Excellence & Standards |
| `17_onboarding_knowledge_transfer.md` | Category 17: P-090 to P-093 — Onboarding & Knowledge Transfer |
| `18_cross_reference_index.md` | Cross-reference index — agent mappings, stage mappings, dependency graph, gate list |
