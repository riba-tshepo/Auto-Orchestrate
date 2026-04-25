# Release Preparation

Guide the user through the release preparation checklist using the right agents and processes.

## Phase: Preparing for Release

### Quality Gates (Category 5)

**Primary agents**: `qa-engineer`, `sre`
**Reference**: `processes/05_quality_assurance_testing.md`

- **Performance Testing** (P-035) — Load, stress, and soak tests before release
  - QA engineer defines test scenarios
  - SRE validates against SLO thresholds
  - Results documented with pass/fail against defined benchmarks

### Infrastructure & Platform (Category 7)

**Primary agents**: `infra-engineer`, `sre`
**Reference**: `processes/07_infrastructure_platform.md`

- **Production Release Management** (P-048) — Release checklist, rollback plan, deployment strategy
  - Infrastructure engineer verifies CI/CD pipeline readiness and confirms infrastructure provisioned
  - Infrastructure engineer runs `cost-estimator` skill for release cost impact analysis
  - SRE runs `observability-setup` skill to configure monitoring, dashboards, and alerting
  - [ ] Cost estimate reviewed
  - [ ] Observability configured (dashboards, alerts, tracing)
  - SRE confirms monitoring, alerting, and runbooks in place
- **Golden Path Adoption** (P-044) — Verify service follows golden path templates
- **Infrastructure Provisioning** (P-045) — Production infrastructure ready
- **CARB** (P-047) — Change Advisory Review Board for infrastructure changes

### Documentation (Category 10)

**Primary agents**: `technical-writer`, `sre`
**Reference**: `processes/10_documentation_knowledge.md`

- **Runbooks** (P-059) — Required BEFORE production release
  - Incident response procedures
  - Escalation paths
  - Common failure modes and remediation
- **Release Notes** (P-061) — Triggered by release
  - User-facing changes
  - Breaking changes
  - Migration guides

### Risk & Change Management (Category 13)

**Primary agents**: `technical-program-manager`, `engineering-manager`
**Reference**: `processes/13_risk_change_management.md`

- **Pre-Launch CAB Review** (P-076) — Required for HIGH-risk changes
  - Risk assessment
  - Rollback strategy
  - Blast radius analysis
  - Go/no-go decision

## Release Checklist

```
Pre-Release:
[ ] Performance testing passed (P-035)
[ ] Production infrastructure provisioned (P-045)
[ ] CI/CD pipeline verified (P-048)
[ ] Monitoring and alerting configured
[ ] Runbooks written and reviewed (P-059)
[ ] Release notes drafted (P-061)
[ ] CAB review completed for HIGH-risk changes (P-076)
[ ] Rollback plan documented and tested
[ ] SLOs defined and dashboards ready (P-054)

Release:
[ ] Deploy via golden path pipeline (P-044)
[ ] Smoke tests pass in production
[ ] SLO metrics nominal
[ ] On-call team briefed

Post-Release:
[ ] Release notes published (P-061)
[ ] Monitoring verified for 24h
[ ] Stakeholders notified
```

## Receipt Writing (STATE-001)

After completing release preparation, write a receipt:

1. `mkdir -p .pipeline-state/command-receipts .pipeline-state/process-log`
2. Write `.pipeline-state/command-receipts/release-prep-<YYYYMMDD>-<HHMMSS>.json`:

```json
{
  "command": "release-prep",
  "receipt_id": "release-prep-<YYYYMMDD>-<HHMMSS>",
  "timestamp": "<ISO-8601>",
  "session_context": {
    "session_id": "<orchestrate session_id if available, else null>",
    "pipeline": "<auto-orchestrate|standalone>"
  },
  "inputs": {
    "release_name": "<user-provided>"
  },
  "outputs": {
    "checklist_status": {
      "performance_testing": "pass|fail|skipped",
      "infra_provisioned": "pass|fail|skipped",
      "cicd_verified": "pass|fail|skipped",
      "monitoring_configured": "pass|fail|skipped",
      "runbooks_written": "pass|fail|skipped",
      "release_notes_drafted": "pass|fail|skipped",
      "cab_review_completed": "pass|fail|skipped|n/a",
      "rollback_plan_documented": "pass|fail|skipped"
    },
    "blocking_items": ["CAB review not completed"]
  },
  "artifacts": [],
  "processes_executed": ["P-035", "P-044", "P-045", "P-048", "P-059", "P-061", "P-076"],
  "next_recommended_action": "post-launch",
  "dispatch_context": {
    "trigger_id": null,
    "invoked_by": null
  }
}
```

3. For each process executed, append to `.pipeline-state/process-log/<process-id>.jsonl` (STATE-003).

If write fails, log warning and continue. See `_shared/protocols/cross-pipeline-state.md` for the full receipt schema.

## Usage

What release are you preparing? I'll help you:
- Run through the release checklist with the right agents
- Identify missing runbooks or documentation
- Prepare the CAB review for high-risk changes
- Verify infrastructure and pipeline readiness
