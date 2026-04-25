# Active Development Phase

Guide the user through processes that are continuously active during sprint execution.

## Phase: In Active Development

These categories run concurrently during every sprint:

### Sprint Delivery Execution (Category 4)

**Processes**: P-022 through P-031
**Primary agents**: `software-engineer`, `engineering-manager`, `product-manager`
**Reference**: `processes/04_sprint_delivery_execution.md`

Active processes:
- **Daily Standup** (P-026) — EM facilitates, all ICs report blockers
- **Feature Development** (P-030) — Software engineers implement stories
- **Sprint Review** (P-027) — Demo completed work to stakeholders
- **Sprint Retrospective** (P-028) — Team identifies improvements
- **Backlog Refinement** (P-029) — PM + EM groom upcoming stories
- **Sprint Delivery** (P-031) — Track velocity, burndown, completion

### Quality Assurance & Testing (Category 5)

**Processes**: P-032 through P-037
**Primary agents**: `qa-engineer`, `software-engineer`
**Reference**: `processes/05_quality_assurance_testing.md`

Active processes:
- **DoD Enforcement** (P-034) — Every story checked against Definition of Done before close
- **Acceptance Verification** (P-036) — QA validates acceptance criteria per story
- **Contract Testing** (P-037) — Run on every PR that changes API contracts
- **Test Architecture** (P-032) — QA maintains test strategy and frameworks
- **Automated Testing Framework** (P-033) — CI runs unit/integration/e2e tests
> **For deeper guidance**: `/qa` — dedicated QA & Testing process guide (P-032 to P-037)

### Security & Compliance (Category 6)

**Processes**: P-038 through P-043
**Primary agents**: `security-engineer`, `software-engineer`
**Reference**: `processes/06_security_compliance.md`

Active processes:
- **SAST/DAST on Every PR** (P-039) — Security scans in CI pipeline
- **CVE Triage on Dependency Updates** (P-040) — Assess new vulnerabilities
- **Threat Modeling** (P-038) — Update threat model as architecture evolves
- **Security Exceptions** (P-041) — Process for accepted risks
> **For deeper guidance**: `/security` — dedicated Security & Compliance process guide (P-038 to P-043)

### Documentation & Knowledge (Category 10)

**Processes**: P-058 through P-061
**Primary agents**: `technical-writer`, `software-engineer`
**Reference**: `processes/10_documentation_knowledge.md`

Documentation processes are invoked at the **skill level**, not the command level. There is no `/docs` command by design — documentation is a continuous practice embedded in all development workflows.

**Relevant skills**:
- `docs-lookup` — Search existing documentation before creating new content
- `docs-write` — Create or update documentation following the style guide

**Processes covered by these skills**:
- P-058: Documentation Planning
- P-059: Content Creation
- P-060: Review & Publishing
- P-061: Knowledge Base Maintenance

**Why no /docs command**: Documentation is not a discrete workflow phase — it runs continuously. The skills are invoked by agents (especially technical-writer) throughout all pipeline stages.

Active processes:
- **API Documentation** (P-058) — Update per API-changing story
- **ADR Publication** (P-060) — Write ADR per significant technical decision


### Infrastructure, Risk & Data Operations

For specialized process guidance beyond sprint delivery:
- `/infra` — Infrastructure & Platform process guide (P-044 to P-048)
- `/risk` — Risk & Change Management process guide (P-074 to P-077)
- `/data-ml-ops` — Data & ML Operations process guide (P-049 to P-053)

## Agent Routing for Active Development

| Task Type | Primary Agent | Supporting Agents |
|-----------|---------------|-------------------|
| Feature implementation | `software-engineer` | `qa-engineer` |
| Bug fix | `software-engineer` | `sre` (if production) |
| API contract change | `software-engineer` | `qa-engineer`, `technical-writer` |
| Security finding | `security-engineer` | `software-engineer` |
| Test gap | `qa-engineer` | `software-engineer` |
| Architecture decision | `staff-principal-engineer` | `software-engineer` |
| Sprint ceremony | `engineering-manager` | `product-manager` |
| Dependency blocked | `technical-program-manager` | `engineering-manager` |

## Receipt Writing (STATE-001)

After completing an active development guidance session, write a receipt:

1. `mkdir -p .pipeline-state/command-receipts .pipeline-state/process-log`
2. Write `.pipeline-state/command-receipts/active-dev-<YYYYMMDD>-<HHMMSS>.json`:

```json
{
  "command": "active-dev",
  "receipt_id": "active-dev-<YYYYMMDD>-<HHMMSS>",
  "timestamp": "<ISO-8601>",
  "session_context": {
    "session_id": "<orchestrate session_id if available, else null>",
    "pipeline": "<auto-orchestrate|standalone>"
  },
  "inputs": {
    "activity_type": "<sprint-execution|quality|security|documentation>"
  },
  "outputs": {
    "processes_reviewed": ["P-030", "P-034"],
    "guidance_given": "<summary of guidance provided>"
  },
  "artifacts": [],
  "processes_executed": ["P-030", "P-034"],
  "next_recommended_action": null,
  "dispatch_context": {
    "trigger_id": null,
    "invoked_by": null
  }
}
```

3. For each process executed, append to `.pipeline-state/process-log/<process-id>.jsonl` (STATE-003).

If write fails, log warning and continue. See `_shared/protocols/cross-pipeline-state.md` for the full receipt schema.

## Usage

What sprint activity do you need help with? I can:
- Guide a feature through implementation with the right quality checks
- Run a DoD enforcement check on completed stories
- Help with sprint ceremony preparation (review, retro, refinement)
- Triage a security finding or CVE
- Update documentation for API changes
