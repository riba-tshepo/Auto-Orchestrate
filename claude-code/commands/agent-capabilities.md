# Agent Capabilities

Show the capabilities, scope, and process ownership for a specific agent or all agents.

## Instructions

If a specific agent is named in: $ARGUMENTS
Then read that agent's definition from `agents/<agent-name>.md` and show its full profile.

If no agent specified, show the summary matrix.

### Agent Summary Matrix

| Agent | Model | Scope | Key Processes |
|-------|-------|-------|---------------|
| `software-engineer` | opus | Production code, debugging, tests (L3-L5) | P-030, P-024, P-034 |
| `staff-principal-engineer` | sonnet | Architecture, RFCs, ADRs (L6-L9) | P-006, P-085, P-088 |
| `engineering-manager` | sonnet | Sprints, DORA, capacity, OKRs (EM-VP) | P-022, P-025, P-026, P-027, P-028, P-066, P-081, P-082 |
| `product-manager` | sonnet | Stories, backlog, acceptance, roadmaps | P-001, P-007, P-009, P-013, P-029 |
| `technical-program-manager` | sonnet | Dependencies, RAID, milestones | P-015, P-016, P-019, P-074, P-076 |
| `infra-engineer` | opus | CI/CD, golden paths, IDP, Terraform, multi-cloud, IAM, FinOps (BUILDS + PROVISIONS) | P-039, P-044, P-045, P-046, P-047, P-088, P-089 |
| `sre` | sonnet | SLOs, incidents, post-mortems (OPERATES) | P-054, P-055, P-056, P-057 |
| `security-engineer` | opus | Security reviews, threat modeling (read-only) | P-012, P-038, P-039, P-040 |
| `qa-engineer` | sonnet | Test architecture, DoD, performance, accessibility | P-032, P-033, P-034, P-035, P-036, P-037 |
| `data-engineer` | opus | ETL/ELT, warehousing, dbt, streaming | P-049, P-050 |
| `ml-engineer` | opus | ML pipelines, model serving, experiments | P-051, P-052, P-053 |
| `technical-writer` | sonnet | API docs, runbooks, release notes | P-058, P-059, P-060, P-061 |

### Infrastructure Pair (Non-Overlapping)

```
infra-engineer     ──  BUILDS the Internal Developer Platform +
                       PROVISIONS cloud infrastructure
                       CI/CD, golden paths, IaC, Terraform, IAM, FinOps
                       
sre                ──  OPERATES production systems
                       SLOs, incidents, monitoring, on-call
```

> **Consolidation note**: `platform-engineer` and `cloud-engineer` have been merged into `infra-engineer`. The former agents are deprecated stubs.

### Routing Score Reference (D3)

The `/assign-agent` command uses a scoring model to route tasks. Each agent has high-affinity domain keywords:

| Agent | High-Affinity Keywords (domain_match = 3) |
|-------|-------------------------------------------|
| `software-engineer` | code, implement, debug, unit test, refactor, feature, bug fix |
| `staff-principal-engineer` | architecture, RFC, ADR, cross-team design, technical strategy |
| `engineering-manager` | sprint, DORA, capacity, OKR, team health, performance review |
| `product-manager` | user story, backlog, acceptance criteria, roadmap, prioritization |
| `technical-program-manager` | dependency, RAID, milestone, PI planning, cross-team coordination |
| `infra-engineer` | CI/CD, golden path, Terraform, cloud, IAM, FinOps, IaC, platform, Docker, Kubernetes |
| `sre` | SLO, error budget, incident, post-mortem, observability, on-call, alerting |
| `security-engineer` | security, threat model, SAST, DAST, CVE, vulnerability, authentication, authorization |
| `qa-engineer` | test, QA, DoD, performance testing, accessibility, contract testing, coverage |
| `data-engineer` | ETL, ELT, data pipeline, dbt, warehouse, schema migration, streaming, Kafka |
| `ml-engineer` | ML pipeline, model serving, experiment tracking, feature store, model drift |
| `technical-writer` | documentation, API docs, runbook, release notes, developer guide |

## Output

For the requested agent(s):
1. Read the agent definition from `agents/<name>.md`
2. Show: name, model, tools, description, scope boundaries
3. List owned processes with brief descriptions
4. Show which project phases the agent is most active in
5. Note any explicit scope exclusions or boundaries
