# Sprint Goal Pattern (Outcome-Not-Output Framing)

A Sprint Goal is a **single sentence** that defines what will be **true** at sprint end — not what will be **done** at sprint end.

## The pattern

> By sprint end, **<who>** can / will **<outcome>** **<measurable threshold>** so that **<value>**.

OR more directly:

> By sprint end, **<measurable outcome statement>**.

## Worked examples

### Example 1: Customer-facing capability

❌ Output framing: "Build the multi-region adapter and deploy it"

✓ Outcome framing: "By sprint end, **the inventory service routes 25% of US-East-1 read traffic through the new multi-region adapter** without measurable latency regression (p95 ≤ 230ms)."

Why outcome works:
- Defines what's true (traffic routed) not what's done (adapter built)
- Measurable: 25% routing + 230ms p95 — both verifiable
- Tied to user value: latency regression matters to customers

### Example 2: Performance improvement

❌ Output: "Reduce p95 checkout latency"

✓ Outcome: "By sprint end, **/checkout API p95 latency is ≤ 200ms** under production-equivalent load (current: 380ms)."

Why outcome works:
- Specific threshold (200ms) instead of "reduce"
- Specific endpoint and load condition
- Baseline reference (380ms) to confirm the delta

### Example 3: Internal capability

❌ Output: "Roll out OpenTelemetry tracing"

✓ Outcome: "By sprint end, **all inventory service production requests emit OTel-formatted traces** queryable in the Datadog tracing dashboard, with ≥95% trace completeness."

Why outcome works:
- Verifiable (look at dashboard)
- Specific scope (inventory service, production)
- Quality threshold (95% completeness)

### Example 4: Defensive / hardening sprint

❌ Output: "Fix all P1 bugs"

✓ Outcome: "By sprint end, **the Q2-aged P1 bug count is ≤ 3** (current: 11), with the 8 highest-frequency bugs fixed and verified in production."

Why outcome works:
- Numeric goal (≤ 3)
- Defines "highest-frequency" so prioritization is explicit
- Verified in production (not just merged)

### Example 5: Discovery / research sprint

❌ Output: "Investigate caching options"

✓ Outcome: "By sprint end, **the team has a recommended caching strategy** documented as a written ADR with ≥2 alternatives evaluated and a prototype validating the recommended approach end-to-end on the staging cart endpoint."

Why outcome works:
- Concrete deliverable (ADR)
- Quality bar (≥2 alternatives + prototype)
- Specific scope (staging cart endpoint)

## What makes a good Sprint Goal

### Singular

ONE sentence. ONE goal. If you find yourself saying "and" or "also," split into multiple sprints OR pick the priority.

❌ "Improve performance AND reduce errors AND add the new admin feature"

✓ Pick one. The other two go in the backlog with their own sprints.

### Outcome-focused

Describes a state (what will be true) not an action (what will be done).

❌ "Refactor the inventory service" — what does done look like?

✓ "By sprint end, the inventory service has zero P1 bugs and runs with 30% lower CPU usage" — done is measurable.

### Tied to a deliverable

Trace back to the Scope Contract. If you can't, the Sprint Goal isn't earning the project sprint slot.

### Achievable in the sprint window

If the Sprint Goal requires 3 weeks of work, you'll fail to meet it. Either:
- Compress scope: "By sprint end, route 10% of traffic" instead of "100%"
- Defer to a multi-sprint goal split across sprints: "Sprint 1: 25%, Sprint 2: 50%, Sprint 3: 100%"

### Verifiable at sprint review

P-027 (Sprint Review) asks: "Did we meet the Sprint Goal?" The answer should be definitive (yes/no/partially), not subjective.

## Multi-sprint goals

For longer initiatives that span sprints, structure the Sprint Goal as a milestone:

| Sprint | Sprint Goal |
|--------|-------------|
| Sprint 1 | "By sprint end, the multi-region adapter passes integration tests on staging." |
| Sprint 2 | "By sprint end, the multi-region adapter routes 10% of US-East-1 prod read traffic without latency regression." |
| Sprint 3 | "By sprint end, the multi-region adapter routes 50% of US-East-1 prod read traffic and 25% of EU-West-1." |
| Sprint 4 | "By sprint end, multi-region routing is at 100% in both regions and the adapter is owned by SRE on-call rotation." |

Each sprint's goal is independently verifiable while the project arc moves forward.

## Sprint Goal vs OKR

| Concept | Scope | Cadence |
|---------|-------|---------|
| OKR | Quarterly outcome (multi-team) | Quarterly |
| Project Intent (Intent Brief outcome) | Project outcome (single team / cross-team) | Project duration (weeks–months) |
| Scope Deliverable | One named output of the project | Multiple per project |
| Sprint Goal | One outcome per sprint | Sprint (1–2 weeks typically) |

The Intent Trace (P-023) is what connects these levels. Sprint Goal must trace up through Scope Deliverable → Project Intent → OKR.

## Anti-patterns to avoid

| Anti-pattern | Why bad |
|--------------|---------|
| Sprint Goal = list of stories | Stories are tactics; goals are outcomes |
| Vague goal ("improve X") | Not verifiable |
| Goal that doesn't tie to current Scope Deliverable | Sprint isn't earning its time on the project |
| Goal that requires post-sprint deploys to verify | Sprint Review (end of sprint) can't verify |
| "Stretch" goals that are aspirational only | Either commit (it's the goal) or don't (move to next sprint) |
| Same Sprint Goal across multiple sprints | Indicates the goal is too big or work isn't progressing |
