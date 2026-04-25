# Post-Launch Operations

Guide the user through post-launch processes and operational readiness.

## Phase: After Launch

### SRE Operations (Category 9)

**Primary agents**: `sre`, `software-engineer`
**Reference**: `processes/09_sre_operations.md`

Active processes:
- **SLO Definition & Monitoring** (P-054) — SLOs active, error budgets tracked
  - SRE owns SLO definitions and dashboard maintenance
  - Engineering manager reviews error budget burn rate weekly
- **Incident Response** (P-055) — Incident management process active
  - SRE leads incident response
  - Software engineer provides subject matter expertise
  - On-call rotation established
- **Post-Mortem** (P-056) — Blameless post-mortems after incidents
  - SRE facilitates
  - Action items tracked to completion
  - Learnings shared across teams
- **On-Call Rotation** (P-057) — Rotation schedule active
  - SRE manages rotation
  - Escalation paths documented in runbooks

### Post-Delivery Retrospective (Category 12)

**Primary agents**: `engineering-manager`, `product-manager`, `staff-principal-engineer`
**Reference**: `processes/12_post_delivery_retrospective.md`

Scheduled processes:
- **Post-Launch Outcome Measurement** (P-073) — Measure at 30/60/90 days
  - Product manager tracks success metrics defined in scope contract
  - Engineering manager tracks technical health metrics
  - Compare actual outcomes to predicted OKR impact
- **Project Post-Mortem** (P-070) — Full project retrospective
  - What went well, what didn't, what to change
  - Process effectiveness review
  - Team health assessment
- **OKR Retrospective** (P-072) — Did we move the OKRs we said we would?
  - Quantitative assessment against targets
  - Learnings for next planning cycle
- **Quarterly Process Health Review** (P-071) — Process effectiveness audit
  - Are gates adding value or creating theater?
  - Process adoption metrics

## Post-Launch Timeline

```
Week 1:    Incident response active, monitoring stabilization
Day 30:    First outcome measurement (P-073)
Day 60:    Second outcome measurement, project post-mortem (P-070)
Day 90:    Final outcome measurement, OKR retrospective (P-072)
Quarterly: Process health review (P-071)
```

## Agent Routing for Post-Launch

| Situation | Primary Agent | Supporting |
|-----------|---------------|------------|
| Production incident | `sre` | `software-engineer` |
| Performance degradation | `sre` | `infra-engineer` |
| Security incident | `security-engineer` | `sre` |
| Outcome measurement | `product-manager` | `engineering-manager` |
| Project retrospective | `engineering-manager` | all participants |
| Architecture drift | `staff-principal-engineer` | `sre` |

## Receipt Writing (STATE-001)

After completing a post-launch activity, write a receipt:

1. `mkdir -p .pipeline-state/command-receipts .pipeline-state/process-log`
2. Write `.pipeline-state/command-receipts/post-launch-<YYYYMMDD>-<HHMMSS>.json`:

```json
{
  "command": "post-launch",
  "receipt_id": "post-launch-<YYYYMMDD>-<HHMMSS>",
  "timestamp": "<ISO-8601>",
  "session_context": {
    "session_id": "<orchestrate session_id if available, else null>",
    "pipeline": "<auto-orchestrate|standalone>"
  },
  "inputs": {
    "activity_type": "<incident-response|post-mortem|outcome-measurement|slo-review|retro>"
  },
  "outputs": {
    "metrics_reviewed": ["SLO compliance", "error budget burn"],
    "action_items": ["..."]
  },
  "artifacts": [],
  "processes_executed": ["P-054", "P-055"],
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

What post-launch activity do you need help with? I can:
- Set up SLO definitions and monitoring dashboards
- Facilitate a post-mortem or retrospective
- Run outcome measurement against success metrics
- Review on-call rotation and incident response readiness
