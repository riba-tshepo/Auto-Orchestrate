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

### Deprecated Agents (redirects)

| Agent | File | Redirect |
|-------|------|----------|
| ~~Platform Engineer~~ | `platform-engineer.md` | Consolidated into `infra-engineer` |
| ~~Cloud Engineer~~ | `cloud-engineer.md` | Consolidated into `infra-engineer` |

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

These agents are available as Claude Code custom agents via `.claude/agents/`. Use the following slash commands to engage them through workflows:

- `/workflow` — See the complete development workflow
- `/assign-agent <task>` — Route a task to the right agent
- `/agent-capabilities [agent-name]` — View agent profiles
- `/gate-review [gate-name]` — Run a gate review
- `/process-lookup <situation>` — Find the right process

## Process Ownership

See `processes/AGENT_PROCESS_MAP.md` for the complete agent-to-process responsibility matrix.
