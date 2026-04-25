# Engineering Processes Handbook

**Version**: 1.0 | **Date**: 2026-04-05 | **Status**: Production

---

## What This Directory Contains

This directory is the **Engineering Processes Handbook** — a comprehensive reference of 93 formally specified engineering processes organized across 17 categories and mapped to 13 specialized agent roles. It covers the full lifecycle of engineering work: from strategic intent articulation through delivery execution, quality assurance, security compliance, infrastructure, operations, and post-delivery measurement.

Every process in this handbook is derived from two foundational documents:

1. **[The Clarity of Intent Framework](../clarity_of_intent.md)** — A 4-stage process (Intent Frame, Scope Contract, Dependency Map, Sprint Bridge) that translates project vision into aligned, executable work. Each stage produces a specific artifact and enforces a gate review before the next stage begins.

2. **The Engineering Team Structure Guide** — An organizational model defining 13 agent roles across 7 reporting layers (Board/CEO through IC), operating in a hybrid hierarchical + squad model.

The Clarity of Intent framework provides the backbone for project delivery. Its four stages map directly to the first four process categories:

| Clarity of Intent Stage | Artifact Produced | Process Category | Gate Process |
|------------------------|-------------------|-----------------|-------------|
| Stage 1: Intent Frame | Intent Brief | Category 1 (P-001 to P-006) | P-004: Intent Review Gate |
| Stage 2: Scope Contract | Scope Contract | Category 2 (P-007 to P-014) | P-013: Scope Lock Gate |
| Stage 3: Dependency Map | Dependency Charter | Category 3 (P-015 to P-021) | P-019: Dependency Acceptance Gate |
| Stage 4: Sprint Bridge | Sprint Kickoff Brief | Category 4 (P-022 to P-031) | P-025: Sprint Readiness Gate |

The remaining 13 categories (5 through 17) provide the supporting infrastructure, governance, and operational processes that make the core delivery pipeline reliable and sustainable.

---

## File Index

| File | Category | Processes | Description |
|------|----------|-----------|-------------|
| [`00_process_handbook_overview.md`](00_process_handbook_overview.md) | Overview | All 93 | Master overview with full process table, lifecycle diagram, agent responsibility matrix, dependency graph, and execution programs |
| [`01_intent_strategic_alignment.md`](01_intent_strategic_alignment.md) | 1. Intent & Strategic Alignment | P-001 to P-006 (6) | Intent articulation, OKR alignment, boundary definition, intent review gate, strategic prioritization, technology vision alignment |
| [`02_scope_contract_management.md`](02_scope_contract_management.md) | 2. Scope & Contract Management | P-007 to P-014 (8) | Deliverable decomposition, definition of done, success metrics, assumptions/risks, exclusions, AppSec scope review, scope lock gate, scope change control |
| [`03_dependency_coordination.md`](03_dependency_coordination.md) | 3. Dependency & Coordination | P-015 to P-021 (7) | Cross-team dependency registration, critical path analysis, resource conflict resolution, communication protocols, dependency acceptance gate, standups, escalation |
| [`04_sprint_delivery_execution.md`](04_sprint_delivery_execution.md) | 4. Sprint & Delivery Execution | P-022 to P-031 (10) | Sprint goal authoring, intent trace validation, story writing, sprint readiness gate, daily standup, sprint review/retro, backlog refinement, dependency tracking, feature development |
| [`05_quality_assurance_testing.md`](05_quality_assurance_testing.md) | 5. Quality Assurance & Testing | P-032 to P-037 (6) | Test architecture design, automated test framework, DoD enforcement, performance testing, acceptance criteria verification, contract testing |
| [`06_security_compliance.md`](06_security_compliance.md) | 6. Security & Compliance | P-038 to P-043 (6) | Threat modeling, SAST/DAST CI integration, CVE triage, security exceptions, compliance review, security champions training |
| [`07_infrastructure_platform.md`](07_infrastructure_platform.md) | 7. Infrastructure & Platform | P-044 to P-048 (5) | Golden path adoption, infrastructure provisioning, environment self-service, Cloud Architecture Review Board, production release management |
| [`08_data_ml_operations.md`](08_data_ml_operations.md) | 8. Data & ML Operations | P-049 to P-053 (5) | Data pipeline QA, schema migration, ML experiment logging, model canary deployment, data drift monitoring |
| [`09_sre_operations.md`](09_sre_operations.md) | 9. SRE & Operations | P-054 to P-057 (4) | SLO definition and review, incident response, post-mortem, on-call rotation management |
| [`10_documentation_knowledge.md`](10_documentation_knowledge.md) | 10. Documentation & Knowledge Management | P-058 to P-061 (4) | API documentation, runbook authoring, ADR publication, release notes |
| [`11_organizational_audit.md`](11_organizational_audit.md) | 11. Organizational Hierarchy Audit | P-062 to P-069 (8) | Audit processes for all 7 organizational layers (Board/CEO through IC), plus audit finding flow |
| [`12_post_delivery_retrospective.md`](12_post_delivery_retrospective.md) | 12. Post-Delivery & Retrospective | P-070 to P-073 (4) | Project post-mortem, quarterly process health review, OKR retrospective, post-launch outcome measurement |
| [`13_risk_change_management.md`](13_risk_change_management.md) | 13. Risk & Change Management | P-074 to P-077 (4) | RAID log maintenance, risk register at scope lock, pre-launch risk review (CAB), quarterly risk review |
| [`14_communication_alignment.md`](14_communication_alignment.md) | 14. Communication & Alignment | P-078 to P-081 (4) | OKR cascade communication, stakeholder update cadence, guild standards communication, DORA metrics review and sharing |
| [`15_capacity_resource_management.md`](15_capacity_resource_management.md) | 15. Capacity & Resource Management | P-082 to P-084 (3) | Quarterly capacity planning, shared resource allocation, succession planning |
| [`16_technical_excellence_standards.md`](16_technical_excellence_standards.md) | 16. Technical Excellence & Standards | P-085 to P-089 (5) | RFC process, technical debt tracking, language tier policy, architecture pattern change, developer experience survey |
| [`17_onboarding_knowledge_transfer.md`](17_onboarding_knowledge_transfer.md) | 17. Onboarding & Knowledge Transfer | P-090 to P-093 (4) | New engineer onboarding, new project onboarding, knowledge transfer, technical onboarding for cross-team dependencies |
| [`18_cross_reference_index.md`](18_cross_reference_index.md) | Cross-Reference | All 93 | Process-to-agent mappings, process-to-stage mappings, dependency graph, gate/checkpoint master list |

**Supporting navigation documents:**

| File | Purpose |
|------|---------|
| [`AGENT_PROCESS_MAP.md`](AGENT_PROCESS_MAP.md) | Agent-to-process responsibility mapping — see all processes each agent owns and supports |
| [`QUICK_START.md`](QUICK_START.md) | Quick-start guide for teams adopting these processes, with phased adoption and common scenarios |

---

## Quick Navigation by Role

### If you are an Engineering Manager (EM), start here:

1. **[`00_process_handbook_overview.md`](00_process_handbook_overview.md)** — Read the "For Engineering Managers" section for your orientation path
2. **[`01_intent_strategic_alignment.md`](01_intent_strategic_alignment.md)** — You own the Intent Review Gate (P-004), strategic prioritization (P-005), and technology vision alignment (P-006)
3. **[`04_sprint_delivery_execution.md`](04_sprint_delivery_execution.md)** — You own sprint goal authoring (P-022), intent trace validation (P-023), sprint readiness gate (P-025), sprint review (P-027), and sprint retrospective (P-028)
4. **[`11_organizational_audit.md`](11_organizational_audit.md)** — You own audit layers 1-5 (P-062 to P-066) and the quarterly process health review (P-071)
5. **[`15_capacity_resource_management.md`](15_capacity_resource_management.md)** — You own quarterly capacity planning (P-082) and succession planning (P-084)
6. **[`17_onboarding_knowledge_transfer.md`](17_onboarding_knowledge_transfer.md)** — You own all onboarding processes (P-090 to P-092)

### If you are a Product Manager (PM), start here:

1. **[`00_process_handbook_overview.md`](00_process_handbook_overview.md)** — Read the "For Product Managers" section
2. **[`01_intent_strategic_alignment.md`](01_intent_strategic_alignment.md)** — You own intent articulation (P-001), OKR alignment (P-002), and boundary definition (P-003)
3. **[`02_scope_contract_management.md`](02_scope_contract_management.md)** — You own the entire Scope Contract lifecycle: deliverables (P-007), DoD (P-008), metrics (P-009), assumptions (P-010), exclusions (P-011), scope lock gate (P-013), and change control (P-014)
4. **[`04_sprint_delivery_execution.md`](04_sprint_delivery_execution.md)** — You own story writing (P-024), daily standup (P-026), and backlog refinement (P-029)
5. **[`12_post_delivery_retrospective.md`](12_post_delivery_retrospective.md)** — You own project post-mortem (P-070), OKR retrospective (P-072), and post-launch outcome measurement (P-073)

### If you are a Technical Program Manager (TPM), start here:

1. **[`00_process_handbook_overview.md`](00_process_handbook_overview.md)** — Read the "For Technical Program Managers" section
2. **[`03_dependency_coordination.md`](03_dependency_coordination.md)** — You own the entire dependency lifecycle: registration (P-015), critical path (P-016), resource conflicts (P-017), communication protocol (P-018), dependency gate (P-019), standups (P-020), and escalation (P-021)
3. **[`07_infrastructure_platform.md`](07_infrastructure_platform.md)** — You own production release management (P-048)
4. **[`13_risk_change_management.md`](13_risk_change_management.md)** — You own RAID log maintenance (P-074) and pre-launch risk review/CAB (P-076)
5. **[`15_capacity_resource_management.md`](15_capacity_resource_management.md)** — You own shared resource allocation (P-083)

### If you are a Tech Lead or Staff/Principal Engineer, start here:

1. **[`00_process_handbook_overview.md`](00_process_handbook_overview.md)** — Read the "For Tech Leads and Staff Engineers" section
2. **[`04_sprint_delivery_execution.md`](04_sprint_delivery_execution.md)** — You own feature development (P-031)
3. **[`10_documentation_knowledge.md`](10_documentation_knowledge.md)** — You own ADR publication (P-060)
4. **[`11_organizational_audit.md`](11_organizational_audit.md)** — You own the Tech Lead/Staff audit layer (P-067) and IC audit layer (P-068)
5. **[`16_technical_excellence_standards.md`](16_technical_excellence_standards.md)** — Staff/Principal Engineers own RFC process (P-085), tech debt tracking (P-086), language tier policy (P-087), and guild standards communication (P-080)

### If you are a Security Engineer, start here:

1. **[`02_scope_contract_management.md`](02_scope_contract_management.md)** — You own AppSec scope review (P-012)
2. **[`06_security_compliance.md`](06_security_compliance.md)** — You own threat modeling (P-038), SAST/DAST (P-039), CVE triage (P-040), security exceptions (P-041), compliance review (P-042), and security champions training (P-043)

### If you are a QA Engineer, start here:

1. **[`05_quality_assurance_testing.md`](05_quality_assurance_testing.md)** — You own test architecture design (P-032), automated test framework (P-033), DoD enforcement (P-034), performance testing (P-035), and contract testing (P-037)

### If you are an SRE, start here:

1. **[`09_sre_operations.md`](09_sre_operations.md)** — You own SLO definition (P-054), incident response (P-055), post-mortem (P-056), and on-call rotation (P-057)
2. **[`10_documentation_knowledge.md`](10_documentation_knowledge.md)** — You own runbook authoring (P-059)

### If you are a Platform or Cloud Engineer, start here:

1. **[`07_infrastructure_platform.md`](07_infrastructure_platform.md)** — Platform engineers own golden path adoption (P-044), environment self-service (P-046); Cloud engineers own infrastructure provisioning (P-045), CARB (P-047), and architecture pattern change (P-088)
2. **[`16_technical_excellence_standards.md`](16_technical_excellence_standards.md)** — Platform engineers own developer experience survey (P-089)

### If you are a Data or ML Engineer, start here:

1. **[`08_data_ml_operations.md`](08_data_ml_operations.md)** — Data engineers own pipeline QA (P-049) and schema migration (P-050); ML engineers own experiment logging (P-051), canary deployment (P-052), and drift monitoring (P-053)

### If you are a Technical Writer, start here:

1. **[`10_documentation_knowledge.md`](10_documentation_knowledge.md)** — You own API documentation (P-058) and release notes (P-061)

---

## Quick Navigation by Project Phase

### Starting a new project?

Follow the core delivery pipeline in order:

1. **Category 1** ([`01_intent_strategic_alignment.md`](01_intent_strategic_alignment.md)) — Articulate intent, align to OKRs, define boundaries, pass Intent Review Gate
2. **Category 2** ([`02_scope_contract_management.md`](02_scope_contract_management.md)) — Decompose deliverables, define DoD and metrics, register assumptions/risks, pass Scope Lock Gate
3. **Category 3** ([`03_dependency_coordination.md`](03_dependency_coordination.md)) — Map dependencies, analyze critical path, resolve resource conflicts, pass Dependency Acceptance Gate
4. **Category 4** ([`04_sprint_delivery_execution.md`](04_sprint_delivery_execution.md)) — Author sprint goals, write stories, pass Sprint Readiness Gate, begin execution

Also engage early:
- **Category 6** ([`06_security_compliance.md`](06_security_compliance.md)) — AppSec scope review at Stage 2; threat modeling in Sprint 1
- **Category 13** ([`13_risk_change_management.md`](13_risk_change_management.md)) — Risk register at Scope Lock (P-075); RAID log from Stage 2 onward

### In active development?

During sprints, these categories are continuously active:

- **Category 4** ([`04_sprint_delivery_execution.md`](04_sprint_delivery_execution.md)) — Daily standups, feature development, sprint review/retro, backlog refinement
- **Category 5** ([`05_quality_assurance_testing.md`](05_quality_assurance_testing.md)) — DoD enforcement per story, acceptance verification, contract testing per PR
- **Category 6** ([`06_security_compliance.md`](06_security_compliance.md)) — SAST/DAST on every PR, CVE triage on dependency updates
- **Category 10** ([`10_documentation_knowledge.md`](10_documentation_knowledge.md)) — API docs per API-changing story, ADRs per significant technical decision

### Preparing for release?

- **Category 5** ([`05_quality_assurance_testing.md`](05_quality_assurance_testing.md)) — Performance testing (P-035) pre-release
- **Category 7** ([`07_infrastructure_platform.md`](07_infrastructure_platform.md)) — Production release management (P-048), golden path and infrastructure provisioning
- **Category 10** ([`10_documentation_knowledge.md`](10_documentation_knowledge.md)) — Runbooks (P-059) required before production release; release notes (P-061) triggered by release
- **Category 13** ([`13_risk_change_management.md`](13_risk_change_management.md)) — Pre-launch CAB review (P-076) for HIGH-risk changes

### After launch?

- **Category 9** ([`09_sre_operations.md`](09_sre_operations.md)) — SLOs active, incident response begins, on-call rotation
- **Category 12** ([`12_post_delivery_retrospective.md`](12_post_delivery_retrospective.md)) — Post-launch outcome measurement at 30/60/90 days (P-073), project post-mortem (P-070), OKR retrospective (P-072)

### Running the organization (continuous)?

- **Category 11** ([`11_organizational_audit.md`](11_organizational_audit.md)) — Audit processes at each organizational layer, per their cadence
- **Category 14** ([`14_communication_alignment.md`](14_communication_alignment.md)) — OKR cascade, stakeholder updates, guild standards, DORA metrics
- **Category 15** ([`15_capacity_resource_management.md`](15_capacity_resource_management.md)) — Quarterly capacity planning, shared resource allocation, succession planning
- **Category 16** ([`16_technical_excellence_standards.md`](16_technical_excellence_standards.md)) — RFCs, tech debt tracking, language tier policy, architecture patterns, developer experience surveys
- **Category 17** ([`17_onboarding_knowledge_transfer.md`](17_onboarding_knowledge_transfer.md)) — New engineer and project onboarding, knowledge transfer
