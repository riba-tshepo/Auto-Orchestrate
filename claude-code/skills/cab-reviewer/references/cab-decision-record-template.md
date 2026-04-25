# CAB Decision Record Template

Output filename: `.orchestrate/<session>/phase-7/cab-decision-record.md`

## Template

```markdown
# CAB Decision Record — <Change Title>

**Session**: <session_id>
**CAB Date**: <ISO-8601>
**Chair**: technical-program-manager
**Status**: Recommended | Approved | Approved with Conditions | Rejected | Deferred

## 1. Change Summary

**What is being deployed**: <one-paragraph description>

**Components affected**: <services, infrastructure, data stores>

**User impact**:
- Visible to users: yes/no — <description if yes>
- Performance impact expected: <none | minor | significant>
- Downtime expected: <none | minor (<5 min) | significant>

**Linked artifacts**:
- Sprint Kickoff Brief: `.orchestrate/<session>/planning/P4-sprint-kickoff-brief.md`
- Spec: `.orchestrate/<session>/stage-2/<spec>.md`
- Validation Report: `.orchestrate/<session>/stage-5/validation-report.md`
- Threat Model (if applicable): `.orchestrate/<session>/phase-receipts/phase-5s-security-findings.md`
- Release Notes (draft): `.orchestrate/<session>/phase-7/release-notes-draft.md`

## 2. Risk Classification

**Final tier**: HIGH | CRITICAL

**Rubric scoring** (per `references/risk-classification-rubric.md`):

| Dimension | Score (1–5) | Justification |
|-----------|-------------|---------------|
| Blast radius | 4 | Affects ~80% of API traffic; cross-region |
| Reversibility | 2 | Rollback requires 30+ minutes (database migration) |
| Compliance/security | 5 | Touches PII; SOC2 control IM-3 |
| Novelty | 3 | Similar pattern deployed once before in Q2 |
| Detection time | 3 | SLO breach alerts within 5 min; user reports within 30 min |

**Total score**: 17/25 → **HIGH** (15+ score = HIGH; 20+ = CRITICAL)

## 3. Participant Reviews

### technical-program-manager (chair)

[verbatim section from `cab/tpm-decision-draft.md`]

### security-engineer (security review)

[verbatim section from `cab/security-review.md`]

**Severity**: <CRITICAL | HIGH | MEDIUM | LOW | NONE>
**Top concerns**:
- ...
- ...

### sre (operational review)

[verbatim section from `cab/sre-review.md`]

**SLO impact**: <breach risk | within budget | improvement>
**Rollback feasibility**: <feasible in N minutes | feasible with caveats | not feasible>
**On-call readiness**: <ready | needs additional preparation>

### product-manager (business review)

[verbatim section from `cab/pm-review.md`]

**Customer impact**: <description>
**Communication plan**: <email | in-app banner | none required>

### engineering-manager (capacity review)

[verbatim section from `cab/em-review.md`]

**Rollback capacity**: <on-call has time | will need backup>
**Team readiness for incident response**: <ready | gaps identified>

## 4. Recommended Verdict

**Recommendation**: Approve | Approve with Conditions | Reject | Defer

**Rationale**: <2–4 sentences explaining the recommendation>

## 5. Conditions (if Approve with Conditions)

For each condition, the deploy is BLOCKED until the condition is satisfied. The release-readiness gate enforces these.

| # | Condition | Owner | Verification method | Due before |
|---|-----------|-------|---------------------|------------|
| C-1 | Confirm PagerDuty rotation includes new service "inventory-v2" | sre | Screenshot of PD config + on-call sign-off | Deploy day |
| C-2 | Rollback procedure rehearsed in staging within 24h prior to deploy | sre + software-engineer | Rehearsal artifact at .orchestrate/<session>/phase-7/rollback-rehearsal.md | Deploy - 24h |
| C-3 | Customer support team briefed on potential issues + escalation flow | product-manager | Brief sent + acknowledgment from CS lead | Deploy day |
| C-4 | Feature-flag canary at 5% for first 2 hours; 25% next 4 hours; 100% after 24h | infra-engineer | Canary config in feature-flag service | Deploy plan |

Conditions cascade to the release-readiness gate as blocking findings. The orchestrator records each as a RAID entry via the `raid-logger` skill.

## 6. Rollback Plan

**Trigger conditions** (any one is sufficient to roll back):
- SLO breach (latency p95 > 300ms or error rate > 1%) sustained for 5 minutes
- Customer support reports >5 affected customers within 30 minutes
- On-call engineer's discretion

**Rollback procedure** (exact steps):
1. Set feature flag `inventory_v2_enabled` to `false` (effects in <10 seconds)
2. Drain v2 service traffic via load balancer (3-5 minutes)
3. If database migration in flight: pause migration via `inventory-migration-controller`
4. Verify SLOs return to baseline within 10 minutes
5. Open incident ticket with rollback context

**Rollback time estimate**: 5–15 minutes (feature-flag); 30–45 minutes (full rollback including migration reversal)

**Rollback decision authority**: on-call SRE + on-call software-engineer (jointly) OR engineering-manager (unilaterally)

## 7. Decision Trail

| Reviewer | Role | Reviewed at | Recommendation |
|----------|------|-------------|----------------|
| <name> | technical-program-manager (chair) | <ISO-8601> | Approve with Conditions |
| <name> | security-engineer | <ISO-8601> | Approve |
| <name> | sre | <ISO-8601> | Approve with Conditions (C-1, C-2) |
| <name> | product-manager | <ISO-8601> | Approve |
| <name> | engineering-manager | <ISO-8601> | Approve |

**Final disposition**: <Approve with Conditions | Reject | etc.>

**Final decision authority** (who clicks "approved" on the cab-review gate): <user identifier from gate-approval-cab-review.json>

**Disposition timestamp**: <ISO-8601 from gate-approval>

---

## Footer

This Decision Record is immutable once the cab-review gate is approved. Subsequent changes require a new CAB review (re-fire CAB-GATE-001 with updated context).
```

## Worked example summary block

For brevity, when generating the auto-eval summary for `gate-pending-cab-review.json`:

```
"summary": "CAB Decision Record produced. Risk: HIGH (17/25 rubric score). Recommended: Approve with Conditions (4 conditions). 5/5 reviewers approve. Rollback: 5-15 min (feature flag) / 30-45 min (full). Top concerns: PII in scope, 30-min rollback for migration, cross-region change. See full record at phase-7/cab-decision-record.md."
```

## Authoring guidance

- **Be specific**: "Some risk to performance" is useless. "p95 latency may regress 30-50ms based on synthetic load test" is actionable.
- **Conditions must be measurable**: each Condition needs a Verification method. "Confirmed by team" isn't enough; specify the artifact.
- **Rollback time matters more than rollback existence**: a 4-hour rollback at 2am is theoretical; favor approaches that allow <15min rollback for HIGH/CRITICAL changes.
- **Don't approve under uncertainty**: if a reviewer flags a concern that can't be answered before the gate, recommend Defer or add it as a Condition.
