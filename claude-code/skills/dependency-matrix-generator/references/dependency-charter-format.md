# Dependency Charter Format (P-015 through P-018)

The P3 Dependency Charter is the canonical artifact for Stage P3. Save to `.orchestrate/<session>/planning/P3-dependency-charter.md`.

## Required sections (4)

### Section 1: Dependency Register (P-015)

Every cross-team dependency. Format as a table:

```markdown
## 1. Dependency Register

| ID | Dependent (from) | Provider (to) | What is Needed | By When | Status | Owner (from) | Owner (to) | Escalation Path | Blocking |
|----|------------------|---------------|----------------|---------|--------|--------------|------------|-----------------|----------|
| dep-001 | inventory-team | identity-team | Session-token library v2.0 with org-scope claim | 2026-05-15 | committed | inventory-tech-lead | identity-em | identity-em → Director Platform → VP Eng | dep-005, dep-007 |
| dep-002 | inventory-team | data-platform-team | Customer order history CDC stream | 2026-05-22 | at-risk | inventory-tech-lead | dataplat-em | dataplat-em → Director Data → VP Data | (none — terminal) |
| dep-003 | mobile-team | inventory-team | New /v2/inventory/stock endpoint | 2026-06-01 | unknown | mobile-tech-lead | inventory-tech-lead | inventory-em → Director Eng | (terminal) |
```

**Status values**:
- `committed`: Provider has agreed and is on track
- `at-risk`: Slipping; needs attention but not yet blocked
- `blocked`: Cannot proceed; escalation likely needed
- `unknown`: New dependency; not yet confirmed by provider

**Blocking values**: comma-separated list of dependency IDs that wait on this one. Empty for terminal nodes (downstream of nothing).

### Section 2: Shared Resource Conflicts (P-017)

Resources that multiple teams compete for during overlapping time windows.

```markdown
## 2. Shared Resource Conflicts

| Resource | Competing Demands | Demand Window Overlap | Severity | Resolution | Owner |
|----------|-------------------|----------------------|----------|------------|-------|
| CI build capacity (large-runner pool) | Inventory migration (week of 5/8) + Auth refactor (weeks of 5/1-5/15) | 2026-05-08 to 2026-05-15 | HIGH | Spin up 2 additional self-hosted runners; cost $X/month for 2 months; sunset after | infra-engineer |
| Production database failover window | Inventory cutover (req. 2h) + Identity v2 deploy (req. 1h) | 2026-05-22 night | CRITICAL | Stagger: identity 8pm-9pm, inventory 10pm-12am; coordinated war room | technical-program-manager |
| ML inference GPU cluster | Recommendation A/B (continuous) + new fraud model training (3-day burst) | 2026-05-10 to 2026-05-13 | MEDIUM | Pause A/B for 3 days OR train on cheaper instance type | ml-engineer |
```

If no conflicts identified, state explicitly: "No shared resource conflicts identified."

### Section 3: Critical Path (P-016)

The longest chain of dependencies — sets the minimum project timeline. Include both the diagram and a written narrative.

```markdown
## 3. Critical Path

### Diagram

```
[Identity v2.0]
   2 weeks
      │
      ▼
[Inventory adapter for v2 tokens]
   1 week
      │
      ▼
[Inventory cutover (dual-write + backfill + verification)]
   3 weeks
      │
      ▼
[Customer-facing launch (feature flag + comms)]
   1 week
      │
      ▼
[Day-30 measurement]
   N/A (calendar)
```

**Total critical path**: 7 weeks (Identity v2.0 → customer launch)

### Narrative

The critical path begins with **Identity team's session-token library v2.0** (2 weeks). Until v2.0 ships, our inventory team cannot build the adapter (week 3). The cutover process (weeks 4-6) is the longest single phase because of the 8-week dual-write rollout pattern — but we can compress to 3 weeks by cutting backfill verification short with acceptable risk. Customer-facing launch (week 7) gates on cutover completion.

**Slack inventory**:
- The CDC stream from data-platform (dep-002) is on the critical path's tail (needed by week 5); it has 3 weeks of slack.
- The mobile /v2 endpoint (dep-003) has 4+ weeks slack; can ship in week 8 without affecting timeline.
- The fraud model training has slack outside the critical path entirely.

### Risk-adjusted timeline

If Identity v2.0 slips by 1 week, the entire timeline slips by 1 week (no slack on critical path).
If non-critical-path items slip by 2 weeks, no impact (within slack budget).
```

### Section 4: Communication Protocol (P-018)

How the teams stay synchronized.

```markdown
## 4. Communication Protocol

| Mechanism | Cadence | Participants | Purpose | Channel / Tool |
|-----------|---------|--------------|---------|-----------------|
| Cross-team dependency standup | Twice weekly (Mon/Thu, 15min) | TPMs + Tech Leads of all involved teams | Status updates per Dependency Register; blocker triage; escalation triggers | Zoom / shared doc |
| Async update | Daily by 10am | All affected team channels | Visibility into progress; surface blockers early | #cross-team-inventory-launch (Slack) |
| Escalation path | When blocked | Provider EM → Director (provider org) → VP Engineering | Unblock dependencies that have missed promised dates by >1 week | Email + meeting request |
| Post-launch retrospective | Within 5 days of launch | All involved team leads + EMs | Cross-team retro on coordination effectiveness | In-person preferred |

### Standup format

Each standup follows P-020 (Dependency Standup) structure:
1. **Open** (1 min): Chair (TPM) opens with a 15-min reminder
2. **Round** (10 min): Each TL gives status on their incoming + outgoing dependencies (focus on blockers, not progress)
3. **Triage** (3 min): Chair classifies new blockers by severity; assigns escalation owners
4. **Close** (1 min): Confirm next standup; capture action items

### Async update format

Daily by 10am, each affected TL posts in the shared channel:
- Yesterday: <what we did on shared dependencies>
- Today: <what we'll do on shared dependencies>
- Blockers: <any new or changed blockers>

Blockers MUST be flagged with `@channel` if they involve another team's commitment.
```

## Optional extension sections

### Vendor / external dependencies

If the project has third-party dependencies (vendor APIs, customer integrations), add:

```markdown
## 5. External Dependencies

| Dependency | Vendor / External Party | Contract Status | SLA / Commitment | Risk |
|------------|------------------------|-----------------|-------------------|------|
| Identity SSO provider | Okta | Active enterprise contract | 99.99% uptime SLA | LOW — well-tested |
| Vendor inventory feed | AcmeFeeds | Trial extension to 2026-05-30 | No SLA on trial; best-effort | MEDIUM — at-risk if not converted to paid |
```

### Dependencies to be retired

If the project changes existing dependencies:

```markdown
## 6. Retired Dependencies

| Dependency | Was Provider | Replaced By | Migration Plan |
|------------|--------------|-------------|----------------|
| Legacy /v1/inventory endpoint | inventory-team | New /v2/inventory in this project | 8-week dual-write + cutover; deprecation announced 2025-Q4 |
```

## Checklist for the chair (TPM)

Before submitting the Dependency Charter to the P3 gate:

- [ ] Every dependency has an `id`, owners (both sides), `by_when`, status
- [ ] No dependency has `unknown` status (escalate to confirm or remove)
- [ ] Shared resource conflicts documented with resolution + owner
- [ ] Critical path diagram is accurate (run dep_graph.py to verify)
- [ ] No cycles in dependency graph (script will fail if so)
- [ ] Communication protocol mechanism is concrete (channel, time, format)
- [ ] Escalation paths name actual roles (not "leadership")
- [ ] Charter is reviewed by the engineering-manager (P3 gate co-evaluator)
