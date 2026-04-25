# OKR Scoring Rubric

Score each Key Result on a 0.0 to 1.0 scale based on Google's OKR convention.

## Score bands

| Score | Band | Meaning |
|-------|------|---------|
| 1.0 | Hit | Hit the target. Rare in well-set OKRs — if frequent, targets are too soft. |
| 0.7 | Stretch achieved | Most ambitious target reached; this is the desired outcome for a stretch OKR. |
| 0.6–0.69 | Solid | Strong achievement; on track for the larger ambition. |
| 0.4–0.59 | Partial | Significant progress; missed the target but moved the needle. |
| 0.2–0.39 | Started | Some progress; substantial gap to target. |
| 0.0–0.19 | No progress | Failed to materially advance the metric. |

## Calculation methods

### Method 1: Linear ratio (default)

For metrics where partial credit makes sense:

```
score = min(1.0, actual / target)
```

Examples:
- Target: reduce abandonment by 15%; Actual: reduced by 12% → 12/15 = 0.80
- Target: reach 1M MAU; Actual: 700K MAU → 700/1000 = 0.70
- Target: cut p95 latency to 200ms (from 500ms); Actual: 280ms → (500-280)/(500-200) = 220/300 = 0.73

### Method 2: Threshold (binary)

For metrics where partial credit doesn't make sense:

```
score = 1.0 if achieved else 0.0
```

Examples:
- "Achieve SOC2 Type II certification" → 1.0 if certified, 0.0 if not
- "Launch new feature in EU before regulatory deadline" → binary outcome

### Method 3: Weighted milestones

For multi-step KRs, weight by milestone:

```
score = (milestone_1_weight × milestone_1_achieved) + (milestone_2_weight × milestone_2_achieved) + ...
where weights sum to 1.0
```

Example: "Migrate 100% of inventory traffic to v2"
- Milestone 1 (50% traffic): weight 0.4 — achieved → 0.4
- Milestone 2 (90% traffic): weight 0.4 — achieved → 0.4
- Milestone 3 (100% traffic): weight 0.2 — not achieved → 0.0
- Total score: 0.4 + 0.4 + 0.0 = 0.8

### Method 4: Inverse direction

For "lower is better" metrics, invert:

```
score = min(1.0, target / actual)  # only when actual < target is desirable
```

Example: Target: reduce p95 latency to 200ms; Actual: 230ms → 200/230 = 0.87

## How to interpret aggregate OKR scores

If an Objective has 3 Key Results:

```
Aggregate = (KR1_score + KR2_score + KR3_score) / 3
```

Or weighted if some KRs matter more:
```
Aggregate = w1*KR1 + w2*KR2 + w3*KR3 (weights sum to 1.0)
```

| Aggregate | Verdict |
|-----------|---------|
| 0.7+ | Objective achieved at stretch level |
| 0.5–0.69 | Objective partially achieved; analyze which KRs missed |
| 0.3–0.49 | Objective off-track; consider re-scoping or retiring |
| 0.0–0.29 | Objective failed; explicit retire-or-pivot decision needed |

## Worked examples

### Example 1: Customer-facing performance improvement

**Objective**: Make checkout fast enough that abandonment drops measurably

| KR | Target | Actual | Method | Score |
|----|--------|--------|--------|-------|
| KR1: Reduce p95 checkout latency to 800ms | 800ms | 920ms (was 1500ms) | Inverse: (1500-920)/(1500-800) = 580/700 | **0.83** |
| KR2: Reduce abandonment rate by 15% | 15% drop | 11% drop | Linear: 11/15 | **0.73** |
| KR3: Increase mobile checkout completion by 10% | +10pp | +7pp | Linear: 7/10 | **0.70** |

**Aggregate**: (0.83 + 0.73 + 0.70) / 3 = **0.75 → Solid achievement, leaning to stretch**

### Example 2: Internal capability OKR

**Objective**: Establish reliable post-mortem culture

| KR | Target | Actual | Method | Score |
|----|--------|--------|--------|-------|
| KR1: Achieve SOC2 Type II | Achieved | Achieved | Threshold | **1.0** |
| KR2: 100% incidents have post-mortems within 5 days | 100% | 8/10 incidents | Linear: 8/10 | **0.80** |
| KR3: Run 4 game-day exercises | 4 | 2 | Linear: 2/4 | **0.50** |

**Aggregate**: (1.0 + 0.80 + 0.50) / 3 = **0.77 → Stretch achievement**

### Example 3: Failed Objective (illustrative)

**Objective**: Become the fastest payment provider in our market

| KR | Target | Actual | Method | Score |
|----|--------|--------|--------|-------|
| KR1: Reduce p99 latency by 50% | 50% reduction | 12% reduction | Linear: 12/50 | **0.24** |
| KR2: Win 3 enterprise customers based on speed | 3 | 0 | Linear: 0/3 | **0.0** |
| KR3: Publish quarterly speed benchmark | Yes | No | Threshold | **0.0** |

**Aggregate**: (0.24 + 0.0 + 0.0) / 3 = **0.08 → Failed; retire-or-pivot**

## When to call it "1.0" vs "0.7"

A common confusion: when does an OKR score 1.0 vs 0.7?

- **1.0** is reserved for hitting the *committed* target. Most teams set committed targets that they're confident they can hit.
- **0.7** is the *stretch* target — the ambitious version, set higher than the commit. Achieving 0.7 means you reached the stretch.

Best practice: set BOTH a committed (1.0) and a stretch (0.7) target. The KR clearly states both:

> "KR1: Reduce checkout abandonment by **8% (commit) / 15% (stretch)**"

Then:
- Achieved 8% → score 1.0 (hit commit)
- Achieved 15% → score 0.7+ (hit stretch — 0.7 if exactly 15%, ratio above if more)

## Anti-patterns in OKR scoring

| Anti-pattern | Why bad | Fix |
|--------------|---------|-----|
| Score 1.0 every quarter | Targets too soft; no aspirational benefit | Set stretch targets (0.7 should be ambitious) |
| Score before measurement window closes | Premature; outcomes still developing | Wait until Day 30 / 60 / 90 milestone |
| Cherry-pick which KRs to score | Loses signal | Score every KR honestly; missing data scores 0.0 |
| Round generously | Hides reality | Use the calculation methods exactly |
| Score 0.0 with no narrative | Action item lost | Always include "what blocked us" + action items |
| Repeat same OKRs without retrospective | Wastes cycles | Use retro to retire / revise / continue OKRs |
