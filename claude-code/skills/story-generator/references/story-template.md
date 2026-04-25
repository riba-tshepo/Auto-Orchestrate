# User Story Template

## Format (mandatory)

```markdown
### Story <ID>: <Concise title (≤8 words)>

**As a** <persona/role — be specific>
**I want** <capability/action — outcome-focused>
**so that** <benefit/outcome — trace to Intent Brief>

**Priority**: P0 | P1 | P2
**Estimate**: <Fibonacci point: 1, 2, 3, 5, 8>
**Assignee**: <agent role>

**Acceptance Criteria**:
1. Given <preconditions>, When <action>, Then <verifiable outcome>
2. Given <preconditions>, When <action>, Then <verifiable outcome>
[≥2 criteria mandatory; ≥3 recommended for complex stories]

**Dependencies** (if any): <story IDs in earlier sprints OR external blockers>
**Out of scope** (if applicable): <explicit exclusions to prevent scope creep>
**INVEST verdict**: PASS | FAIL (<failed criterion>)
```

## Worked example

```markdown
### Story PR-12: Forgot password reset flow

**As a** logged-out user who has forgotten their password
**I want** to request a password reset link via email
**so that** I can regain account access without contacting support

**Priority**: P0
**Estimate**: 3 points
**Assignee**: software-engineer

**Acceptance Criteria**:
1. Given I am on the login page, When I click "Forgot password?", Then I am taken to a password-reset form.
2. Given I am on the password-reset form, When I enter a registered email and click Submit, Then a reset email is sent within 60 seconds.
3. Given I receive a reset email, When I click the reset link within 24 hours, Then I am taken to a "set new password" form.
4. Given the reset link is older than 24 hours, When I click it, Then I see an "expired link" message and an option to request a new one.

**Dependencies**: Story AU-3 (registered email field validation) — already in done column
**Out of scope**: Multi-factor authentication for the reset flow (see Story PR-15)
**INVEST verdict**: PASS
```

## Common splits (for stories that fail S — Small)

When a story is >8 points, split along one of these axes:

### Split by user role
```
[Original 13-pt] As a user, I want to manage my profile (admin/customer/staff)
↓ split into:
[5-pt] As a customer, I want to edit my profile
[5-pt] As an admin, I want to view any user's profile
[3-pt] As staff, I want to flag profile fields for review
```

### Split by workflow step
```
[Original 13-pt] As a buyer, I want to complete a purchase
↓ split into:
[5-pt] As a buyer, I want to add items to my cart (happy path)
[3-pt] As a buyer, I want to enter shipping information
[5-pt] As a buyer, I want to enter payment and submit order
[Deferred to next sprint] Edge cases: invalid card, address validation failure
```

### Split by acceptance criterion
```
[Original 8-pt with 6 ACs] As a user, I want a comprehensive notifications dashboard
↓ split into:
[3-pt with 3 ACs] As a user, I want to see unread notifications
[2-pt with 2 ACs] As a user, I want to mark notifications as read
[3-pt with 1 AC] As a user, I want to filter notifications by type
```

## Anti-patterns (the validator will flag these)

| Anti-pattern | Example | Fix |
|--------------|---------|-----|
| Implementation in story | "...via SendGrid" | Move to spec |
| Vague benefit | "...so that the system works better" | Tie to Intent Brief outcome |
| Missing AC | (no Acceptance Criteria section) | Add ≥2 in G/W/T format |
| Unsized | (no Estimate field) | Force a Fibonacci point or mark NOT-READY |
| Tech-task masquerading as story | "As a developer, I want to refactor the auth module" | Reframe with user value, OR move to spec/ADR |
| Multi-role in one story | "As an admin and customer..." | Split by role |
