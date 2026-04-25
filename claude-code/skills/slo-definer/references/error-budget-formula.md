# Error Budget Formula

## The fundamental math

```
Error Budget (allowed failures) = Total Events × (1 - SLO target)
```

For availability SLOs measured in time:

```
Error Budget (minutes) = Window (minutes) × (1 - SLO target)
```

## Worked examples

### 99.9% availability over 28 days

```
Window = 28 days × 24 hours × 60 minutes = 40,320 minutes
SLO target = 0.999
Error budget = 40,320 × (1 - 0.999) = 40,320 × 0.001 = 40.32 minutes

Human-readable: ~40 minutes per 28 days
```

### 99.95% availability over 28 days

```
Window = 40,320 minutes
SLO target = 0.9995
Error budget = 40,320 × 0.0005 = 20.16 minutes

Human-readable: ~20 minutes per 28 days
```

### 99% availability over 28 days

```
Window = 40,320 minutes
SLO target = 0.99
Error budget = 40,320 × 0.01 = 403.2 minutes

Human-readable: ~6h 43min per 28 days
```

### 99.99% availability over 90 days (quarterly)

```
Window = 90 × 24 × 60 = 129,600 minutes
SLO target = 0.9999
Error budget = 129,600 × 0.0001 = 12.96 minutes

Human-readable: ~13 minutes per quarter
```

## Request-based error budget (for high-volume APIs)

For services with consistent traffic, request-based error budgets are easier to reason about than time-based ones.

```
Error Budget (failed requests) = Total Requests × (1 - SLO target)
```

### Example: 99.9% availability, 1M requests/day, 28-day window

```
Total requests = 1,000,000 × 28 = 28,000,000
SLO target = 0.999
Error budget = 28,000,000 × 0.001 = 28,000 failed requests

Per day: 28,000 / 28 = 1,000 failed requests/day on average
```

## Burn rate alerting

The "burn rate" tells you how fast the error budget is being consumed. If the budget is exhausted in less than the window, you have a problem.

```
Burn rate = (current error rate) / (allowed error rate per SLO)
```

### Burn rate examples

For a 99.9% SLO (allowed error rate = 0.1%):

| Current error rate | Burn rate | Time to exhaust 28d budget |
|--------------------|-----------|----------------------------|
| 0.1% | 1x | 28 days (on track) |
| 0.2% | 2x | 14 days |
| 1.0% | 10x | 2.8 days |
| 10% | 100x | 6.7 hours |

### Recommended burn-rate alert thresholds

Per Google SRE workbook:

| Severity | Burn rate | Lookback window | Meaning |
|----------|-----------|-----------------|---------|
| **PAGE** | 14.4x over 1h | 1h | Will exhaust 28d budget in 2 days. Wake someone up. |
| **PAGE** | 6x over 6h | 6h | Will exhaust 28d budget in 5 days. Wake someone up. |
| **TICKET** | 3x over 1d | 1d | Concerning trend; investigate during business hours. |
| **TICKET** | 1x over 3d | 3d | On track to exhaust budget; investigate. |

## Multi-window multi-burn-rate (MWMBR) — recommended

Combining short-window (page-fast) and long-window (page-on-trend) gives you both signal strength AND reduced noise:

```
ALERT_PAGE = (1h burn rate >= 14.4) AND (5min burn rate >= 14.4)
ALERT_TICKET = (6h burn rate >= 6) AND (30min burn rate >= 6)
```

The "AND" reduces false positives from one-off spikes.

## When to use MWMBR vs simple thresholds

- **Simple**: Services with <100 requests/min. Burn rate measurements are too noisy at low volumes.
- **MWMBR**: Services with >1000 requests/min where statistical signal is strong.

For low-volume services, prefer absolute thresholds (e.g., "page if any 4xx beyond known clients") plus periodic uptime probes.

## Error budget policy template

When error budget is exhausted, here's the recommended policy (customize per service):

```markdown
## Error Budget Policy — <service-name>

### When budget is exhausted

1. **Freeze risky deploys** for the remainder of the window:
   - No infrastructure changes
   - No experimental features (turn off feature flags for new rollouts)
   - Critical fixes still allowed (with extra review)

2. **Prioritize reliability work**:
   - Top of next sprint: known reliability tickets
   - Engineering manager + SRE Tech Lead align on top 3 reliability investments
   - At least 30% of next-sprint capacity goes to reliability

3. **Post-mortem the budget exhaustion** within 5 business days:
   - What incidents consumed the budget?
   - Was the SLO target right?
   - Are there systemic issues to address?
   - Action items go into the RAID log via raid-logger

4. **Reset on next window** (28d rolling) automatically.

### Exception process

If a critical business need requires deploy during freeze:
- Escalate to engineering-manager + sre + product-manager
- Document the exception in raid-log.json
- Increased monitoring during deploy
- Rollback plan rehearsed beforehand
```

## Common mistakes in error budget reasoning

| Mistake | Why it's wrong | Fix |
|---------|----------------|-----|
| Treating 100% as the target | Leaves no budget for any change | Pick a realistic tier (99.9% — 99.99%) |
| Resetting budget at calendar boundaries (e.g., monthly) | Sudden cliff: budget can be wasted in 1 day, then plenty for 30 | Use 28-day rolling window |
| Same target for all endpoints | Hides tail behavior; overspends on cheap requests | Per-endpoint SLOs for hot paths; aggregate for the rest |
| Page on every threshold | Alert fatigue | Use MWMBR; tune thresholds per service |
| Ignoring "good enough" reliability | Over-investing in reliability the user doesn't notice | Tie SLO to user impact; confirm with product |
