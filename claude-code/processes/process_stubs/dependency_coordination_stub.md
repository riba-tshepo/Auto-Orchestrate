---
status: PARTIAL-INTEGRATED
related_process: claude-code/processes/03_dependency_coordination.md
category: category-03-dependency
last_reviewed: 2026-04-14
---

> **STATUS: PARTIAL-INTEGRATED** — P-015 and P-016 are now injected at Stage 0 (COMPLEX + infra flag) as advisory notify hooks per the expanded process injection map (V2). P-017 through P-021 remain organizational-only (require cross-team human coordination). For full process definitions see `03_dependency_coordination.md`.

# Process Stub: Dependency Coordination (P-015 through P-021)

**Type**: Process stub — partially integrated (P-015, P-016 advisory; P-017-021 organizational-only)  
**Status**: PARTIAL-INTEGRATED — P-015/P-016 injected at Stage 0 for COMPLEX tasks with infra flag  
**Date**: 2026-04-14 (updated from 2026-04-06)  
**Produced by**: software-engineer (Task #8, SPEC T018; updated A3)

---

## Gap Description

Dependency coordination processes P-015 through P-021 run **parallel to organizational Stages 1-3** (Intent → Scope → Dependencies) and have no equivalent in the auto-orchestrate pipeline. Auto-orchestrate Stages 0-2 (Research → Epic → Spec) proceed without ever triggering cross-team dependency registration, critical path analysis, or escalation protocols. If the project has external dependencies (shared APIs, platform infrastructure, third-party integrations), they can become blockers during Stage 3 implementation with no prior coordination.

The `/new-project` command guides dependency coordination in Stage 3, but when a project jumps directly to `/auto-orchestrate` (bypassing the organizational pipeline), these six processes are never engaged.

---

## Processes Covered

### P-015: Register Cross-Team Dependencies

**Owner**: Technical Program Manager  
**When**: During or before Stage 0 (Research) — the researcher should identify external dependencies  
**Purpose**: Map all external team dependencies before implementation begins

**Minimum required actions**:
1. Review Stage 0 research output for any mentioned external systems, APIs, or teams
2. Register each dependency: team name, what is needed, by when, blocking or non-blocking
3. Create a dependency register entry in `.orchestrate/{session_id}/dependency-register.json`

**In auto-orchestrate mode**: The Stage 0 researcher (RES-009, Risks and Remedies) identifies external dependencies as risks. The TPM should review the research output and register any mentioned dependencies before Stage 3 begins.

### P-016: Critical Path Analysis

**Owner**: Technical Program Manager + Staff/Principal Engineer  
**When**: After Stage 1 (Product Management), before Stage 3 (Implementation)  
**Purpose**: Identify which dependencies block implementation

**Minimum required actions**:
1. Review Stage 1 task decomposition for tasks with external prerequisites
2. Mark blocking dependencies (without resolution, Stage 3 cannot proceed for those tasks)
3. Mark non-blocking dependencies (implementation can proceed; integration tested later)

**In auto-orchestrate mode**: Stage 1 product-manager produces a dependency graph for internal tasks. External dependency blocking is not modeled. TPM must overlay external blocking analysis before Stage 3.

### P-017: Resource Conflict Resolution

**Owner**: Engineering Manager  
**When**: Before Stage 3  
**Purpose**: Negotiate shared resource allocation with dependent teams

**In auto-orchestrate mode**: Not applicable unless shared infrastructure (clusters, databases, test environments) is involved. If Stage 3 requires shared resources, EM must coordinate before software-engineers begin.

### P-018: Communication Plan

**Owner**: TPM  
**When**: Before Stage 3  
**Purpose**: Establish sync cadences with dependent teams

**In auto-orchestrate mode**: Advisory. If implementation generates questions for dependent teams, the TPM's communication plan defines who to contact and at what cadence.

### P-020: Dependency Standups

**Owner**: TPM  
**When**: During Stage 3 (Implementation)  
**Purpose**: Recurring sync for active dependencies

**In auto-orchestrate mode**: If Stage 3 runs for multiple sessions (long implementation), TPM should conduct dependency standups between sessions.

### P-021: Escalation Protocol

**Owner**: Engineering Manager + TPM  
**When**: Any time a dependency becomes blocking during implementation  
**Purpose**: Define when and how to escalate blocked dependencies

**Minimum required actions**:
1. Define escalation trigger: dependency blocked for more than N days (recommended: 2 business days)
2. Define escalation path: TPM → EM → VP Engineering
3. Document in the project's RAID log

**In auto-orchestrate mode**: If Stage 3 is blocked by an external dependency, the escalation protocol from P-021 should be invoked. The orchestrator will surface blocked tasks after 3 fix iterations (IMPL-009); if the block is external, P-021 escalation applies.

---

## Integration Path (Partially Implemented — A3 / PROCESS-SCOPE-001)

**Integrated processes** (P-015, P-016):
- **Injection point**: Stage 0 (Research), scope_condition: `complex`, domain_flag: `infra`
- **Action**: `notify` — log `[PROCESS-INJECT] Stage 0: P-015/P-016 — Researcher identifies cross-team infrastructure dependencies`
- **Enforced**: `false` (advisory)
- **Mechanism**: When triage classifies a task as COMPLEX with the `infra` domain flag, the researcher at Stage 0 is notified to identify cross-team infrastructure dependencies and critical path items.

**Organizational-only processes** (P-017 through P-021):
- P-017 (Resource Conflicts), P-018 (Communication Plan), P-019 (Dependency Acceptance Gate), P-020 (Dependency Standups), P-021 (Escalation Protocol) remain organizational-only
- These require cross-team human coordination that cannot be automated
- They are logged as `[PROCESS-INFO]` in process receipts when a COMPLEX task is active
- The `/new-project` command (Tier 1) handles these in its Stage 3 guidance

---

*Stub for: P-015 (Register Cross-Team Dependencies), P-016 (Critical Path), P-017 (Resource Conflicts), P-018 (Communication Plan), P-020 (Dependency Standups), P-021 (Escalation Protocol)*  
*Full process: `claude-code/processes/03_dependency_coordination.md`*  
*Integration: `claude-code/processes/process_injection_map.md` (Domain-Conditional Injection Hooks)*
