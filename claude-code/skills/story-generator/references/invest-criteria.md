# INVEST Criteria

User stories should satisfy all six INVEST criteria. The story-generator validator checks each.

## I — Independent

**Definition**: The story can be developed and delivered independently of other stories in the same sprint. No story should be blocked by another story committed to the same sprint.

**Pass example**: "As a customer, I want to view my order history" — implementable on its own.

**Fail example**: "As a customer, I want to filter order history by date" when there's no order history view yet — depends on another in-sprint story.

**Fix**: Either include the prerequisite in this story, or move it to a later sprint.

## N — Negotiable

**Definition**: Stories capture *outcomes*, not *implementation details*. The "how" is negotiated between PM and engineers; the "what" and "why" are fixed.

**Pass example**: "As a customer, I want to receive an email when my order ships" — silent on which email service or template engine.

**Fail example**: "As a customer, I want to receive a SendGrid email via the dynamic-template API when shipped" — over-prescribed.

**Fix**: Strip implementation details. Move them to the spec produced at Stage 2.

## V — Valuable

**Definition**: The story delivers user, business, or technical value. The "so that" clause must articulate it concretely.

**Pass example**: "...so that I know when to expect my package and can plan delivery acceptance."

**Fail example**: "...so that the system has email functionality." — meta-value, not user value.

**Fix**: Trace the value to the original Intent Brief outcome.

## E — Estimable

**Definition**: An engineer can produce a credible point estimate within a refinement session. Vague stories are inestimable.

**Pass example**: "Add a 'forgot password' link to the login page that triggers a password reset email" — clear scope, clear estimate.

**Fail example**: "Improve the login experience" — too vague to size.

**Fix**: Add concrete acceptance criteria. If still inestimable, mark NOT-READY and refine in P-029 Backlog Refinement.

## S — Small

**Definition**: The story fits within a sprint. Typically ≤8 Fibonacci points.

**Pass example**: 3-point story for "Add forgot-password link + reset email flow"

**Fail example**: 13+ point story for "Complete authentication system overhaul"

**Fix**: Split into multiple smaller stories along these axes (in priority order):
1. **By user role** — split if multiple roles need it
2. **By workflow step** — happy path first; edge cases as separate stories
3. **By data shape** — text-only first; rich content as separate story
4. **By acceptance criterion** — each AC could be its own story
5. **By non-functional dimension** — function first; performance/scale as separate stories

## T — Testable

**Definition**: Acceptance criteria are verifiable by automated or manual tests. "Done" is unambiguous.

**Pass example**: "Given a logged-in user clicks 'Forgot password', When they enter their email and click submit, Then they receive a reset email within 60 seconds."

**Fail example**: "The login flow should be fast and reliable." — not testable.

**Fix**: Convert each AC to Given/When/Then format. Specify thresholds (latency, success rate).

## INVEST Checklist (validator script enforces)

For each story:
- [ ] Independent — no in-sprint blockers
- [ ] Negotiable — outcome-only language
- [ ] Valuable — `so that` clause traces to Intent Brief
- [ ] Estimable — has Fibonacci point estimate
- [ ] Small — ≤8 points (split if larger)
- [ ] Testable — ≥2 acceptance criteria in Given/When/Then format

A story passes only if ALL six are checked. Failed stories block the gate or get marked NOT-READY for next refinement cycle.
