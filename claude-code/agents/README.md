# Engineering Team Agents Reference

## Overview

12 specialized agent types (17 total including pipeline-specific agents) mapping to organizational roles from Individual Contributor (L3) through C-suite (L9). Each agent has a defined scope, model assignment, tool access, and process ownership.

## Agent Index

### Implementation Agents (Opus - deep work)

| Agent | File | Primary Scope |
|-------|------|---------------|
| [Software Engineer](software-engineer.md) | `software-engineer.md` | Production code, debugging, unit tests, code reviews (L3-L5) |
| [Infrastructure Engineer](infra-engineer.md) | `infra-engineer.md` | CI/CD pipelines, golden paths, IaC, Terraform, cloud provisioning, IAM, FinOps (BUILDS + PROVISIONS) |
| [Security Engineer](security-engineer.md) | `security-engineer.md` | Security reviews, SAST/DAST, threat modeling, CVEs (read-only) |
| [Data Engineer](data-engineer.md) | `data-engineer.md` | ETL/ELT pipelines, data warehouse, dbt models, streaming |
| [ML Engineer](ml-engineer.md) | `ml-engineer.md` | ML pipelines, feature stores, model serving, experiments |

### Coordination & Advisory Agents (Sonnet - breadth)

| Agent | File | Primary Scope |
|-------|------|---------------|
| [Staff/Principal Engineer](staff-principal-engineer.md) | `staff-principal-engineer.md` | Architecture, RFCs, ADRs, cross-team design (L6-L9) |
| [Engineering Manager](engineering-manager.md) | `engineering-manager.md` | Sprint planning, DORA, capacity, OKRs (EM through VP) |
| [Product Manager](product-manager.md) | `product-manager.md` | User stories, backlog, acceptance criteria, roadmaps |
| [Technical Program Manager](technical-program-manager.md) | `technical-program-manager.md` | Cross-team dependencies, RAID, milestones, PI planning |
| [SRE](sre.md) | `sre.md` | SLOs, incident response, post-mortems, on-call (OPERATES) |
| [QA Engineer](qa-engineer.md) | `qa-engineer.md` | Test architecture, automated frameworks, DoD enforcement |
| [Technical Writer](technical-writer.md) | `technical-writer.md` | API docs, developer guides, runbooks, release notes |

### Removed Agents (historical record)

| Agent | Status | Successor |
|-------|--------|-----------|
| ~~Platform Engineer~~ | Removed 2026-04-25 (was: `platform-engineer.md`) | `infra-engineer` |
| ~~Cloud Engineer~~ | Removed 2026-04-25 (was: `cloud-engineer.md`) | `infra-engineer` |

## Infrastructure Pair

These two agents have explicitly non-overlapping scopes:

```
infra-engineer      BUILDS + PROVISIONS   CI/CD, golden paths, IDP, Terraform, cloud resources, IAM, FinOps
sre                 OPERATES              SLOs, incidents, monitoring, on-call
```

## Agent Engagement by Project Phase

### Starting a New Project
`product-manager` -> `engineering-manager` -> `staff-principal-engineer` -> `software-engineer` -> `security-engineer`

### Active Development
`software-engineer` + `qa-engineer` + `security-engineer` + `technical-writer`

### Release Preparation
`qa-engineer` + `infra-engineer` + `sre` + `technical-writer` + `technical-program-manager`

### Post-Launch
`sre` + `product-manager` + `engineering-manager`

### Organizational Operations
`engineering-manager` + `staff-principal-engineer` + `product-manager` + `technical-program-manager`

## Usage with Claude Code

These agents are available as Claude Code custom agents via `.claude/agents/`. They are spawned by `/auto-orchestrate` at the appropriate internal phase per AUTO-001 (phase-determined agent gateway):

- **Phases 1–4 (Planning)** spawn `product-manager`, `technical-program-manager`, `engineering-manager`
- **Stages 0–6 (Execution)** spawn `researcher`, `product-manager`, `software-engineer`, `test-writer-pytest`, `technical-writer`
- **Phases 5q/5s/5i/5d (Domain)** spawn `qa-engineer`, `security-engineer`, `infra-engineer`, `data-engineer`/`ml-engineer`
- **Phase 5v (Audit)** spawns `auditor`
- **Phase 5e (Debug)** spawns `debugger`
- **Phase 7 (Release)** spawns `orchestrator` with `PHASE: RELEASE_PREP`
- **Phase 8 (Post-Launch)** spawns `sre`, `product-manager`, `engineering-manager`
- **Phase 9 (Governance)** spawns `engineering-manager`, `technical-program-manager`, `staff-principal-engineer`, `product-manager`, `infra-engineer`, `technical-writer` per sub-routine

**Parallel Stage 3 spawning** — When the product-manager (Stage 1) emits independence groups in `proposed-tasks.json` per PARALLEL-001, the orchestrator may spawn up to 5 concurrent `software-engineer` instances (one per distinct independence group) at Stage 3. Each carries `SE-009 (concurrent-safe execution)`: operate only on the task's declared `files_touched`; commit atomically. Configurable to 7 via `checkpoint.parallel_cap`.

**Token-budget optimizations** — Subagents (except `orchestrator` and `session-manager`) receive a 2.6k manifest digest instead of the 19k full manifest by default (MANIFEST-DIGEST-001). The orchestrator itself receives only the active stage/phase/meeting template plus core constraints from `orchestrator.md` (TEMPLATE-EXTRACT-001) instead of the full 33k file. Set `needs_full_manifest: true` on a task spawn if an agent needs full chaining metadata.

Run the framework with `/auto-orchestrate "<task description>"`. There are no other commands — domain guides, lifecycle commands, and utilities all run as internal phases.

## Process Ownership

See `processes/AGENT_PROCESS_MAP.md` for the complete agent-to-process responsibility matrix.
