# Quick-Start Guide: Adopting the Engineering Process Framework

**Version**: 1.0 | **Date**: 2026-04-05

This guide helps teams adopt the Engineering Processes Handbook incrementally. You do not need to implement all 93 processes at once. Start with the core delivery pipeline, then expand as your team matures.

---

## Prerequisites

Before adopting these processes, ensure your team has:

1. **Read the [Clarity of Intent Framework](../clarity_of_intent.md)**. The entire process handbook is built on its four stages (Intent Frame, Scope Contract, Dependency Map, Sprint Bridge). Understanding the "why" behind the four gates is essential before you engage with the process specifications.

2. **Understood the organizational structure**. The 12 agent roles (product-manager, engineering-manager, technical-program-manager, software-engineer, staff-principal-engineer, security-engineer, qa-engineer, infra-engineer, sre, data-engineer, ml-engineer, technical-writer) each have specific process ownership. See the [Agent Process Map](AGENT_PROCESS_MAP.md) for the full breakdown.

3. **Identified who fills each role on your team**. In smaller teams, one person may cover multiple agent roles. That is fine — the processes still apply, but the same person wears multiple hats during different ceremonies.

4. **Have a project tracking tool** (Jira, Linear, or equivalent) and a documentation platform (Confluence, Notion, or equivalent) where artifacts will live.

---

## Minimum Viable Process Adoption

For a team running its first project under this framework, adopt these 12 processes. They represent the critical path from intent to delivered software:

### The Core 12

| # | Process ID | Process Name | Why It Is Essential |
|---|-----------|-------------|---------------------|
| 1 | P-001 | Intent Articulation | Without a clear Intent Brief, every downstream decision lacks a reference point |
| 2 | P-004 | Intent Review Gate | The gate ensures the team agrees on "why" before investing in "what" |
| 3 | P-007 | Deliverable Decomposition | Turns intent into concrete, ownable deliverables |
| 4 | P-008 | Definition of Done Authoring | Eliminates "what does done mean?" disputes during sprints |
| 5 | P-013 | Scope Lock Gate | Freezes scope so teams can commit to delivery timelines |
| 6 | P-015 | Cross-Team Dependency Registration | Makes invisible blockers visible before they delay sprints |
| 7 | P-019 | Dependency Acceptance Gate | Gets explicit commitments from dependency owners |
| 8 | P-022 | Sprint Goal Authoring | Connects each sprint to the project's purpose |
| 9 | P-024 | Story Writing | Engineers need clear stories with acceptance criteria |
| 10 | P-025 | Sprint Readiness Gate | The final check that the team is ready to execute |
| 11 | P-031 | Feature Development | The IC-level implementation workflow with CI gates |
| 12 | P-034 | Definition of Done Enforcement | Ensures quality standards are met per story, not retroactively |

These 12 processes cover the four Clarity of Intent gates and the minimum execution workflow. Everything else in the handbook extends, supports, or governs these core processes.

---

## Phased Adoption Guide

### Phase 1: Core Four Gates (Weeks 1-4)

**Goal:** Establish the Clarity of Intent pipeline for your next project.

**Adopt these processes:**

| Category | Processes | What You Get |
|----------|-----------|-------------|
| 1. Intent & Strategic Alignment | P-001, P-002, P-003, P-004 | A clear Intent Brief that passes review |
| 2. Scope & Contract Management | P-007, P-008, P-009, P-010, P-011, P-013 | A locked Scope Contract with deliverables, DoD, metrics, and exclusions |
| 3. Dependency & Coordination | P-015, P-016, P-019 | A Dependency Charter with critical path and committed owners |
| 4. Sprint & Delivery Execution | P-022, P-023, P-024, P-025, P-031 | Sprint goals connected to intent; stories with criteria; readiness gate |

**Success signal:** Your first project passes all four gates in 8-12 working days. Engineers can answer "What am I building, why does it matter, and how will I know it's done?"

**Process count:** 18 processes

### Phase 2: Add Quality, Security, and Risk (Weeks 5-12)

**Goal:** Layer in quality assurance, security hygiene, and risk management.

**Add these processes:**

| Category | Processes | What You Get |
|----------|-----------|-------------|
| 5. Quality Assurance & Testing | P-032, P-033, P-034, P-035, P-036 | Test architecture, automated framework, DoD enforcement, performance testing, acceptance verification |
| 6. Security & Compliance | P-012, P-038, P-039, P-040 | AppSec scope review at Stage 2, threat modeling in Sprint 1, SAST/DAST on every PR, CVE triage |
| 13. Risk & Change Management | P-074, P-075, P-076 | RAID log from Stage 2 onward, risk register at Scope Lock, pre-launch CAB review |
| 2. Scope & Contract Management | P-014 | Scope change control for post-lock changes |
| 3. Dependency & Coordination | P-017, P-018, P-020, P-021 | Resource conflict resolution, communication protocols, dependency standups, escalation |
| 4. Sprint & Delivery Execution | P-026, P-027, P-028, P-029, P-030 | Daily standups, sprint review/retro, backlog refinement, dependency tracking |

**Success signal:** Quality gates catch defects before release. Security reviews happen early (at Scope Lock, not post-launch). Risks are tracked systematically. Sprint ceremonies are running smoothly.

**Process count:** +22 processes (40 total)

### Phase 3: Full Framework (Weeks 13-26)

**Goal:** Adopt all remaining processes for complete organizational coverage.

**Add these processes:**

| Category | Processes | What You Get |
|----------|-----------|-------------|
| 1. Intent & Strategic Alignment | P-005, P-006 | Strategic prioritization, technology vision alignment |
| 5. Quality Assurance & Testing | P-037 | Contract testing for API boundaries |
| 6. Security & Compliance | P-041, P-042, P-043 | Security exceptions, compliance reviews, security champions training |
| 7. Infrastructure & Platform | P-044, P-045, P-046, P-047, P-048 | Golden path, IaC, environment self-service, CARB, production release management |
| 8. Data & ML Operations | P-049, P-050, P-051, P-052, P-053 | Data pipeline QA, schema migration, ML experiment logging, canary deployment, drift monitoring |
| 9. SRE & Operations | P-054, P-055, P-056, P-057 | SLO definition, incident response, post-mortem, on-call management |
| 10. Documentation & Knowledge | P-058, P-059, P-060, P-061 | API docs, runbooks, ADRs, release notes |
| 11. Organizational Audit | P-062 to P-069 | Full 7-layer audit hierarchy with finding flow |
| 12. Post-Delivery & Retrospective | P-070, P-071, P-072, P-073 | Project post-mortem, process health, OKR retro, outcome measurement |
| 13. Risk & Change Management | P-077 | Quarterly risk review |
| 14. Communication & Alignment | P-078, P-079, P-080, P-081 | OKR cascade, stakeholder updates, guild standards, DORA metrics |
| 15. Capacity & Resource Management | P-082, P-083, P-084 | Capacity planning, resource allocation, succession planning |
| 16. Technical Excellence | P-085, P-086, P-087, P-088, P-089 | RFCs, tech debt tracking, language tiers, architecture patterns, DX surveys |
| 17. Onboarding & Knowledge Transfer | P-090, P-091, P-092, P-093 | Engineer onboarding, project onboarding, knowledge transfer, cross-team dependency onboarding |

**Success signal:** All 93 processes are active at their defined cadences. Quarterly Process Health Review (P-071) shows improving metrics. The organization has full traceability from strategic OKRs through delivery to post-launch measurement.

**Process count:** +53 processes (93 total)

> **Mature-stage execution: parallel sprint implementation**: Once your sprint backlog routinely contains mutually-independent stories (different services, non-overlapping files, no shared schema changes), enable parallel Stage 3 execution. The product-manager (Stage 1) emits `independence_groups` in `proposed-tasks.json` per the hybrid detection algorithm (heuristic by file path + explicit `shares_state_with` / `independent_of` overrides). The orchestrator spawns up to 5 concurrent software-engineers (configurable to 7 via `checkpoint.parallel_cap`) — wall-clock for the sprint shrinks roughly by the concurrency factor. See `agents/product-manager.md` "Stage 1 Decomposition Output" and `commands/auto-orchestrate.md` PARALLEL-001/002/003.

---

## Common Scenarios

### Scenario: Single-squad project with no cross-team dependencies

**Use:** Phase 1 processes, but compress Stages 1 and 2 into a single document and a single gate review. Skip Category 3 dependency processes (P-015 to P-021) entirely. Stage 4 remains the same.

**Minimum processes:** P-001, P-004, P-007, P-008, P-013, P-022, P-024, P-025, P-031, P-034

### Scenario: Cross-team project involving 3+ squads

**Use:** Full Phase 1 + Phase 2 processes. Category 3 (Dependency & Coordination) is critical. Ensure a TPM is assigned to own the Dependency Charter and run dependency standups (P-020) twice weekly.

**Key processes to prioritize:** P-015, P-016, P-017, P-019, P-020, P-021, P-030, P-083

### Scenario: Project with significant security or compliance requirements

**Use:** Phase 1 + Phase 2 security processes immediately. Do not defer P-012 (AppSec Scope Review) or P-038 (Threat Modeling) to later phases.

**Key processes to prioritize:** P-012 (at Stage 2), P-038 (Sprint 1), P-039 (every PR), P-041, P-042

### Scenario: New team or organization adopting the framework for the first time

**Use:** Phase 1 only for your first project. Run a retrospective (P-028) after the first sprint to assess how the gates felt. Add Phase 2 processes one category at a time in subsequent projects.

**Tip:** Assign one person as the "process champion" who reads the full handbook and can guide the team through gate ceremonies.

### Scenario: Production service requiring high reliability

**Use:** Prioritize Category 9 (SRE & Operations) alongside the core pipeline. SLO definition (P-054) should happen before production deployment. Incident response (P-055), runbooks (P-059), and on-call rotation (P-057) are non-negotiable for production services.

**Key processes to prioritize:** P-054, P-055, P-056, P-057, P-059, P-035

### Scenario: Data or ML project

**Use:** Core pipeline plus Category 8 (Data & ML Operations). Data pipeline QA (P-049) and schema migration (P-050) for data engineering work. ML experiment logging (P-051), canary deployment (P-052), and drift monitoring (P-053) for ML model delivery.

**Key processes to prioritize:** P-049, P-050, P-051, P-052, P-053, P-054

### Scenario: Scope change requested mid-project

**Use:** P-014 (Scope Change Control). The person identifying the change writes a Scope Change Request. PM decides for changes within scope boundary; Engineering Director decides for changes that expand scope or affect timeline by more than one sprint. The Scope Contract is versioned.

---

## Anti-Patterns to Avoid

### 1. Skipping gates to "move faster"

**The temptation:** "We already know what we're building, let's skip straight to Sprint Bridge."

**Why it fails:** The gates exist to surface misalignment early. Skipping the Intent Review Gate (P-004) means scope disputes emerge during Sprint 2 instead of before Sprint 1. Skipping Scope Lock (P-013) means the definition of "done" is negotiated during code review. The 8-12 days invested in the four gates saves 2-4 sprints of rework.

### 2. Treating gates as rubber stamps

**The temptation:** "Everyone is busy. Let's just sign off on the gate async without actually reading the artifact."

**Why it fails:** A gate that passes without scrutiny is worse than no gate at all — it creates a false sense of alignment. If reviewers cannot explain the project's purpose after the Intent Review Gate, the gate has not done its job. Insist on the pass criteria being genuinely met.

### 3. Writing artifacts after the work is done

**The temptation:** "We'll document the Intent Brief and Scope Contract retroactively."

**Why it fails:** These artifacts are not documentation — they are decision-forcing functions. An Intent Brief written after Sprint 1 describes what was built, not what should have been built. The value is in the thinking the artifact forces, not the document itself.

### 4. One person writes everything

**The temptation:** "The PM can write the Intent Brief, Scope Contract, and Dependency Charter alone."

**Why it fails:** The artifacts require different perspectives. The Intent Brief needs the sponsor's strategic context. The Scope Contract needs the Tech Lead's technical judgment on feasibility and DoD. The Dependency Charter needs the TPM's cross-team visibility. Single-author artifacts miss the blind spots these different viewpoints reveal.

### 5. Adopting all 93 processes on day one

**The temptation:** "We need to be rigorous. Let's implement everything at once."

**Why it fails:** Process overload causes process rejection. Teams that try to adopt everything simultaneously execute nothing well. Follow the phased adoption guide above. Master the four gates first, then expand. It is better to run 18 processes well than 93 processes poorly.

### 6. Ignoring the Dependency Charter for "internal" dependencies

**The temptation:** "We only need the Dependency Charter for external teams. Our internal dependencies are obvious."

**Why it fails:** Internal dependencies are the most commonly underestimated source of sprint failure. "The API team will have it ready by Sprint 2" is not a commitment until the API team's TL has verbally confirmed it in the Dependency Acceptance Gate (P-019). Register all dependencies, internal and external.

### 7. Silent scope changes

**The temptation:** "It's a small change, not worth the paperwork."

**Why it fails:** Small, undocumented scope changes accumulate. By Sprint 4, the team is building something materially different from the Scope Contract, and nobody can point to where the drift started. Use P-014 (Scope Change Control) for every change. The overhead is a single form with four fields — it takes 10 minutes.

### 8. Measuring process adoption by artifact count instead of outcome

**The temptation:** "We produced all four artifacts, so the process is working."

**Why it matters:** The process is working when sprint goal completion rates exceed 80%, scope changes per project are declining, late dependency discoveries are below 1 per project, and engineers can explain why they are building what they are building. Track the signals described in the Clarity of Intent framework's "How to Know the Process Is Working" section.

---

## Where to Go Next

- **[README.md](README.md)** — Full file index and role-based navigation
- **[AGENT_PROCESS_MAP.md](AGENT_PROCESS_MAP.md)** — See all processes your agent role owns and supports
- **[00_process_handbook_overview.md](00_process_handbook_overview.md)** — Master overview with lifecycle diagram, agent responsibility matrix, and dependency graph
- **[18_cross_reference_index.md](18_cross_reference_index.md)** — Detailed cross-references: process-to-agent, process-to-stage, process-to-layer mappings
- **[../clarity_of_intent.md](../clarity_of_intent.md)** — The foundational framework that this handbook operationalizes
