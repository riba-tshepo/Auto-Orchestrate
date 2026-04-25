---
name: slo-definer
description: |
  Define Service Level Objectives (SLOs) and compute error budgets for new and
  modified services. Implements P-054 (SLO Definition and Review) and supports
  P-055 (Incident Response Readiness) and P-056 (Post-Mortem). Provides SLO
  pattern templates by service type, SLI selection guidance, and a deterministic
  error-budget calculator.
  Use when user says "define slo", "slo definition", "error budget",
  "service level objective", "sli selection".
triggers:
  - define slo
  - slo definition
  - error budget
  - service level objective
  - sli selection
---

# SLO Definer Skill

You define Service Level Objectives (SLOs) for services in the pipeline's scope. SLOs are user-facing reliability targets; SLIs are the underlying measurable metrics; error budgets quantify acceptable failure tolerance.

## When to use

| Trigger | Process | Pipeline node |
|---------|---------|---------------|
| Stage P2 (Scope Contract) co-agent (sre + data-engineer) | P-009 (Success Metrics Definition) — translate outcome targets to SLOs | sre + data-engineer produce P2-metrics-review.md |
| Phase 5i (Infra/SRE) | P-054 (SLO Definition and Review) — finalize SLOs against implementation | sre produces phase-5i-infra-findings.md |
| Phase 8 (Post-Launch) | P-054 ongoing — monitor SLO health post-launch | sre tracks SLO breach + error budget burn |

## How to use

### Step 1: Identify the service and its users

For each service in scope:
- What does it do?
- Who calls it (synchronous user / async client / batch)?
- What does "broken" look like to its users?

### Step 2: Pick the right SLO pattern by service type

Read `references/slo-patterns.md` for catalog. Common patterns:

| Service type | Recommended SLOs |
|--------------|------------------|
| Synchronous API (user-facing) | Latency p95 + p99; Availability; Error rate |
| Async pipeline (events, queues) | End-to-end freshness; Processing success rate; Backlog depth |
| Batch job | Job success rate; Job completion time; Data freshness |
| ML inference | Latency p95; Inference success rate; Prediction quality drift |
| Data store | Query latency p95; Connection success rate; Replication lag |

### Step 3: Define each SLO with all 5 fields

Every SLO MUST have:

| Field | Description | Example |
|-------|-------------|---------|
| **SLI** | The measurement (metric + query) | `histogram_quantile(0.95, http_request_duration_seconds_bucket)` |
| **Target** | The threshold | `≤ 200ms p95` |
| **Window** | Measurement window | `28-day rolling` |
| **Filter** | What's in scope | `path != /healthz, status != 5xx` |
| **Owner** | On-call team | `platform-team` |

### Step 4: Compute the error budget

```
python3 ~/.claude/skills/slo-definer/scripts/calculate_error_budget.py \
  --target 99.9 --window-days 28
```

Returns:
```json
{
  "availability_target_percent": 99.9,
  "window_days": 28,
  "total_minutes": 40320,
  "error_budget_minutes": 40.32,
  "error_budget_human": "~40 minutes per 28-day window"
}
```

The error budget is the time/requests you can fail before breaching the SLO. It's the "permission to take risk" — deploys, experiments, etc. — that engineering gets in exchange for reliability work.

### Step 5: Write SLO definitions

Format per service:

```markdown
## SLOs for <service-name>

### Latency SLO
- **SLI**: `histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))`
- **Target**: ≤ 200ms
- **Window**: 28-day rolling
- **Filter**: `path != "/healthz", path != "/metrics"`
- **Owner**: platform-team
- **Error budget**: 5% of requests slower than 200ms (per 28d window)

### Availability SLO
- **SLI**: `1 - (sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])))`
- **Target**: 99.9%
- **Window**: 28-day rolling
- **Filter**: `path != "/healthz"`
- **Owner**: platform-team
- **Error budget**: 40 minutes per 28-day window
```

### Step 6: Connect to incident response (P-055)

For each SLO, define the alert thresholds:
- **Burn-rate alert**: page when error budget burning at >2x normal rate (early warning)
- **Breach alert**: page when SLO is in breach (incident declared)

These tie to runbooks (P-059) and incident response (P-055).

## Error budget policy

When the error budget is exhausted within a window:
1. Freeze risky deploys (feature flags off, no infra changes)
2. Prioritize reliability work (bug fixes, capacity, monitoring)
3. Reset on next window OR via post-mortem action items

Document this policy per service. The orchestrator's RAID log entry tracks budget exhaustion as a CRITICAL Risk.

## Integration with other skills

- `observability-setup` — instruments the service so SLIs are measurable
- `raid-logger` — registers error-budget-exhausted as a CRITICAL Risk
- `release-notes-generator` — release notes mention any SLO changes (target tightening or relaxation)
- `cab-reviewer` — Phase 7 CAB reviews release readiness against current SLO health

## Outputs

- Markdown SLO document at `.orchestrate/<session>/phase-receipts/phase-5i-slo-definition.md`
- Error-budget calculation JSON (machine-readable for downstream alerting setup)
- (At Phase 8) SLO health snapshot in `phase-receipts/phase-8-post-launch-receipt.md`

## Related skills

- `observability-setup` — for instrumenting the SLIs
- `cost-estimator` — high SLO targets may increase infrastructure cost; cost-estimator quantifies
- `raid-logger` — for tracking SLO-related risks
- `validator` — at Stage 5, verifies SLO instrumentation is in place

## Reference

- `references/slo-patterns.md` — SLO catalog by service type
- `references/error-budget-formula.md` — math + worked examples
- Canonical processes: P-054 in `processes/09_sre_operations.md`
