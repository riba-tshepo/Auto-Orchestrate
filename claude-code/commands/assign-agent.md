# Assign Agent

Route a task to the correct agent based on a multi-dimensional scoring model.

## Instructions

Analyze the user's task description: $ARGUMENTS

Then determine the correct agent using the scoring model below.

### Scoring Model

For each of the 12 candidate agents, compute:

```
score = (domain_match × 3) + (process_coverage × 2) + (skill_availability × 1) - (current_load × 1)
```

**Highest score wins. Ties broken by domain_match (highest wins).**

### Scoring Dimensions

**domain_match (0-3)**: How well the agent's domain matches the task description.
- **3** = Exact domain match (task keywords are the agent's primary domain)
- **2** = Strong overlap (task touches the agent's domain significantly)
- **1** = Tangential (task has minor relevance to agent's domain)
- **0** = No match

**process_coverage (0-3)**: How many of the task's required processes (P-xxx) the agent owns or supports.
- **3** = Agent owns 3+ matching processes
- **2** = Agent owns 1-2 matching processes or supports 3+
- **1** = Agent supports 1-2 matching processes
- **0** = No process coverage

**skill_availability (0-3)**: How many skills relevant to the task the agent has in its mandatory skills list.
- **3** = 3+ relevant skills available
- **2** = 2 relevant skills
- **1** = 1 relevant skill
- **0** = No relevant skills

**current_load (0-2)**: How many active tasks the agent is currently handling (from session state).
- **0** = No active tasks (or session state unavailable — default to 0)
- **1** = 1-2 active tasks
- **2** = 3+ active tasks

### Domain Affinity Table

| Agent | domain_match = 3 keywords | Key Processes |
|-------|--------------------------|---------------|
| `software-engineer` | code, implement, debug, unit test, refactor, feature, bug fix | P-030, P-024, P-034 |
| `staff-principal-engineer` | architecture, RFC, ADR, cross-team design, technical strategy | P-006, P-085, P-088 |
| `engineering-manager` | sprint, DORA, capacity, OKR, team health, performance review | P-022, P-025, P-026, P-027, P-028 |
| `product-manager` | user story, backlog, acceptance criteria, roadmap, prioritization | P-001, P-007, P-009, P-013 |
| `technical-program-manager` | dependency, RAID, milestone, PI planning, cross-team coordination | P-015, P-016, P-019, P-074 |
| `infra-engineer` | CI/CD, golden path, Terraform, cloud, IAM, FinOps, IaC, platform, Docker, Kubernetes | P-039, P-044, P-045, P-046, P-047 |
| `sre` | SLO, error budget, incident, post-mortem, observability, on-call, alerting | P-054, P-055, P-056, P-057 |
| `security-engineer` | security, threat model, SAST, DAST, CVE, vulnerability, auth | P-012, P-038, P-039, P-040 |
| `qa-engineer` | test, QA, DoD, performance testing, accessibility, contract testing | P-032, P-033, P-034, P-035, P-036, P-037 |
| `data-engineer` | ETL, ELT, data pipeline, dbt, warehouse, schema migration, streaming | P-049, P-050 |
| `ml-engineer` | ML pipeline, model serving, experiment tracking, feature store, drift | P-051, P-052, P-053 |
| `technical-writer` | documentation, API docs, runbook, release notes, developer guide | P-058, P-059, P-060, P-061 |

### Worked Example

Task: "Fix authentication token validation"

| Agent | domain_match | process_coverage | skill_availability | current_load | Score |
|-------|-------------|-----------------|-------------------|-------------|-------|
| software-engineer | 2 (code fix, strong overlap) | 2 (P-034 code review) | 3 (production-code-workflow, dev-workflow, debug-diagnostics) | 1 | (2×3)+(2×2)+(3×1)-(1×1) = **12** |
| security-engineer | 3 (auth is security domain) | 3 (P-038, P-039, P-040) | 2 (security audit skills) | 0 | (3×3)+(3×2)+(2×1)-(0×1) = **17** |
| qa-engineer | 1 (tangential — testing aspect) | 1 (P-037 contract testing) | 1 (test-writer-pytest) | 0 | (1×3)+(1×2)+(1×1)-(0×1) = **6** |

**Winner: security-engineer** (score 17 — domain expertise matches best for auth token validation)

### Multi-Agent Tasks

Some tasks require multiple agents in sequence:

| Scenario | Agent Sequence |
|----------|---------------|
| New API endpoint | `software-engineer` -> `qa-engineer` -> `technical-writer` |
| Infrastructure change | `infra-engineer` -> `sre` |
| Security remediation | `security-engineer` (assess) -> `software-engineer` (fix) -> `qa-engineer` (verify) |
| Architecture change | `staff-principal-engineer` (RFC) -> `software-engineer` (implement) |
| Production incident | `sre` (respond) -> `software-engineer` (fix) -> `sre` (post-mortem) |
| Data pipeline | `data-engineer` (build) -> `qa-engineer` (test) -> `sre` (monitor) |
| ML feature | `ml-engineer` (model) -> `software-engineer` (integrate) -> `sre` (serve) |

## Output

For the given task, provide:
1. **Scoring breakdown** — show domain_match, process_coverage, skill_availability, current_load for the top 3 candidates
2. **Primary agent** — highest score, and why
3. **Supporting agents** if multi-agent coordination needed
4. **Relevant processes** (P-xxx) that apply
5. **Relevant phase** (new-project / active-dev / release-prep / post-launch / org-ops)
