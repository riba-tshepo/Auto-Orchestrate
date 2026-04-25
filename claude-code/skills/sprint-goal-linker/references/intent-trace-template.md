# Intent Trace Template (P-023)

The Intent Trace is the 3-line bridge that proves the Sprint Goal serves the Project Intent. P-023 (Intent Trace Validation) requires every sprint to have a complete, valid trace.

## Format

```
Project Intent: <verbatim from Intent Brief outcome>

         ↓ (advances)

Scope Deliverable <ID>: <name + description from Scope Contract>

         ↓ (advances)

Sprint Goal: <single sentence outcome statement for this sprint>
```

## Worked examples

### Example 1: Multi-region inventory failover (Sprint 2 of 4)

```
Project Intent: Reduce regional-inconsistency oversells by 80% within Q3 to
recover from CS escalation #4521 and improve customer NPS for inventory
accuracy by 10pp.

         ↓ (advances)

Scope Deliverable D-2: Multi-region inventory adapter with sub-second
read consistency across us-east-1 and eu-west-1.
(Definition of Done: adapter routes ≥99% of cross-region reads correctly;
p95 latency ≤ 230ms.)

         ↓ (advances)

Sprint Goal: By sprint end, the inventory service routes 25% of
us-east-1 read traffic through the new multi-region adapter without
measurable latency regression (p95 ≤ 230ms vs current 220ms).
```

✓ Continuity: Sprint Goal (25% routed) advances Deliverable D-2 (full multi-region adapter)
✓ Specificity: Project Intent is broadest (Q3 OKR); Sprint Goal is most concrete (this sprint, 25%)
✓ OKR alignment: Project Intent cites recovery from CS escalation + NPS goal (OKR-tied)
✓ Testability: Sprint Goal verifiable at sprint review (% routed + latency measurement)

### Example 2: Performance hardening sprint

```
Project Intent: Improve checkout reliability and speed in Q3 to reduce
abandonment by 15% and reach the OKR-3.2 target of 99.9% checkout availability.

         ↓ (advances)

Scope Deliverable D-1: Sub-200ms p95 checkout API latency under
production-equivalent load.
(Definition of Done: load test at 1.5x peak passes with p95 ≤ 200ms;
SLO defined for /checkout endpoint at 99.9%.)

         ↓ (advances)

Sprint Goal: By sprint end, /checkout API p95 latency is ≤ 200ms under
production-equivalent synthetic load (current: 380ms; target reduction
of 47%).
```

✓ Continuity: Sprint Goal (200ms latency) advances Deliverable D-1 (sub-200ms target)
✓ Specificity: Sprint Goal narrows to one endpoint, one threshold, one load condition
✓ OKR alignment: cites OKR-3.2 in Project Intent
✓ Testability: load test result is definitive

### Example 3: Compliance / regulated work

```
Project Intent: Achieve SOC2 Type II certification by 2026-09-30 to unblock
enterprise sales pipeline ($X ARR potential gated on certification).

         ↓ (advances)

Scope Deliverable D-3: All audit logs meet SOC2 IM-3 control requirements
(immutable, queryable, retained 1 year).
(Definition of Done: audit logging implemented for all production services;
verified by external auditor during pre-audit walkthrough.)

         ↓ (advances)

Sprint Goal: By sprint end, the 5 highest-priority production services
(payment, auth, inventory, orders, sessions) emit immutable audit logs
queryable via the central audit dashboard with 100% of customer-data-access
events captured.
```

✓ Continuity: Sprint Goal advances D-3 (5 of N services done)
✓ Specificity: names the 5 services, the dashboard, the event type
✓ OKR alignment: SOC2 cert is the OKR-aligned outcome
✓ Testability: dashboard query confirms coverage

## Failed Intent Trace patterns

### Continuity break

```
Project Intent: Reduce checkout abandonment by 15% in Q3.

         ↓ (advances)

Scope Deliverable D-2: Multi-region inventory failover.

         ↓ (advances)

Sprint Goal: By sprint end, multi-region inventory routes 25% of traffic.
```

❌ **Failure**: Multi-region inventory doesn't directly advance "reduce checkout abandonment by 15%." There's a missing causal link. Either:

- The Project Intent is about availability (not abandonment) — fix Intent Brief
- D-2 is the wrong deliverable for this Project Intent — choose a different one
- Add a causal link: "Multi-region failover prevents the regional outages that contribute 4pp of the 12pp abandonment we see during incidents — closing this gap is part of the 15% target"

### Specificity violation

```
Project Intent: Build a great inventory system.

         ↓ (advances)

Scope Deliverable D-1: Inventory service.

         ↓ (advances)

Sprint Goal: Make the inventory service better.
```

❌ **Failure**: All three levels are equally vague. Specificity should increase as you go down. Fix:

- Project Intent: cite a specific outcome (latency, accuracy, abandonment, etc.)
- Deliverable: name what's being delivered concretely
- Sprint Goal: numeric outcome verifiable at sprint review

### OKR reference missing

```
Project Intent: Improve checkout.

         ↓ (advances)

Scope Deliverable D-1: Sub-200ms p95 checkout latency.

         ↓ (advances)

Sprint Goal: By sprint end, /checkout p95 ≤ 200ms.
```

❌ **Failure**: Project Intent doesn't cite an OKR. Either:

- Intent Brief was authored without strategic context — add OKR alignment in P-002
- OR explicitly mark this as "tactical project, no OKR mapping" with engineering-manager sign-off

### Testability fail

```
Project Intent: Make customers happier.

         ↓ (advances)

Scope Deliverable D-1: Improve UX.

         ↓ (advances)

Sprint Goal: By sprint end, the checkout flow feels better.
```

❌ **Failure**: "Feels better" cannot be verified at sprint review. Fix:

- Define "happier": NPS, abandonment, complaint rate, time-to-purchase
- Define "feels better": specific UX metric (e.g., task completion time, error rate, click count)

## Mandatory verification at the P4 gate

The P4 gate (Sprint Readiness Gate, P-025) requires that every sprint in the Sprint Kickoff Brief has a complete, valid Intent Trace. The validator checks:

- [ ] All 3 lines present and non-empty
- [ ] Project Intent matches the Intent Brief outcome verbatim
- [ ] Scope Deliverable references an actual ID/name from Scope Contract Section 2
- [ ] Sprint Goal is one sentence, ≤30 words, with measurable outcome
- [ ] Each ↓ arrow has a continuity rationale (advances/serves/contributes-to)
- [ ] OKR reference exists in Project Intent (or explicit "tactical project" marker)

If any check fails, the P4 gate's recommended_verdict is `rejected` with the specific failure cited.
