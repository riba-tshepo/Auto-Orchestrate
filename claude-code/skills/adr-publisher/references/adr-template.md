# ADR Template (MADR-flavored)

Save as `docs/adr/NNNN-<short-kebab-title>.md` in the project repo.

## Template (copy and fill)

```markdown
# ADR-NNNN: <Concise title in present tense>

**Status**: Proposed | Accepted | Deprecated | Superseded by ADR-XXXX
**Date**: YYYY-MM-DD
**Authors**: <agent role(s) — e.g., software-engineer, staff-principal-engineer>
**Stakeholders**: <who is affected by this decision>

## Context

<What is the problem we're trying to solve? What forces are at play —
business, technical, organizational? What are we observing?>

<Cite specifics: which user pain point, which performance number, which
operational incident, which regulatory requirement.>

## Decision

<What is the architecture decision? State it in 1–3 sentences. Use
present tense and active voice.>

> **We will <X> in order to <Y>.**

<Provide the rationale in the next paragraph. Why is this the right
trade-off given the context?>

## Consequences

### Positive

- <What gets better as a result of this decision?>
- <What new capability is enabled?>
- <What complexity is removed?>

### Negative

- <What gets harder?>
- <What new complexity is introduced?>
- <What technical debt is taken on?>

### Neutral

- <What changes but is neither clearly better nor worse?>
- <What requires team learning or process adjustment?>

## Alternatives Considered

### Alternative 1: <Name>

**Description**: <one paragraph>

**Pros**: <bullet list>

**Cons**: <bullet list>

**Why rejected**: <key reason this didn't win>

### Alternative 2: <Name>

[same structure]

[≥2 alternatives required; if fewer were considered, document why]

## References

- Spec: `.orchestrate/<session>/stage-2/<spec-file>.md` (if applicable)
- Related RFC: `<RFC link>` (if applicable, P-085)
- Related ADRs: ADR-XXXX (predecessor or related decision)
- External references: <RFC, blog post, vendor doc>

## Implementation notes

<Optional: practical guidance for implementing the decision. Anti-patterns to avoid.
Migration steps if replacing prior pattern.>
```

## Worked example

```markdown
# ADR-0014: Use Postgres for inventory data

**Status**: Accepted
**Date**: 2026-04-25
**Authors**: software-engineer, staff-principal-engineer
**Stakeholders**: inventory-team, platform-team, data-engineering

## Context

The inventory service needs a primary data store for SKU records (~50M rows),
stock levels (updated 100/sec at peak), and supplier metadata. We've been
running on DynamoDB for 18 months. We're observing:

- **Query inflexibility**: 60% of new product asks require a secondary index;
  we've added 11 GSIs and the cost has tripled in 12 months.
- **Cross-region replication lag**: stock levels can be 30+ seconds stale
  in non-primary regions, causing oversells.
- **Aggregation pain**: nightly inventory reports run for 4+ hours via Athena;
  ad-hoc analytics requires data export.

We're scaling to 200M rows and 500/sec writes by Q3 and need to lock the
data store choice before Stage 3 implementation.

## Decision

> **We will migrate inventory data from DynamoDB to Postgres (RDS Aurora)
> in order to gain query flexibility, support synchronous cross-region
> reads, and enable in-database analytics without a separate ETL pipeline.**

The migration runs over 8 weeks via dual-write + backfill. Read traffic
cuts over after backfill completes and verification passes.

## Consequences

### Positive

- Ad-hoc queries land in <1s instead of requiring a new GSI
- Cross-region read consistency tightens from 30s to <1s (Aurora Global)
- Nightly reports run in 20 minutes (in-database) vs. 4 hours (Athena)
- Single source of truth simplifies the data model

### Negative

- Aurora is more operationally complex than DynamoDB (failover, version upgrades, parameter tuning)
- Higher baseline cost ($X/month vs $Y/month for DynamoDB at current scale)
- Team needs to upskill on Postgres operational practices

### Neutral

- Schema migrations now block deployments (mitigated by online schema change tooling)
- Connection pooling becomes a concern at high concurrency (PgBouncer required)

## Alternatives Considered

### Alternative 1: Continue with DynamoDB + add ElasticSearch for queries

**Description**: Keep DynamoDB as primary store; sync data to ES for queries that don't fit DynamoDB's access patterns.

**Pros**: No migration; preserves existing operational maturity.
**Cons**: Two systems to manage; sync lag introduces consistency issues; ES is itself operationally complex.
**Why rejected**: Doesn't solve the cross-region consistency problem; doubles the ops burden.

### Alternative 2: CockroachDB (distributed SQL)

**Description**: Switch to CockroachDB for SQL access and built-in cross-region consistency.

**Pros**: Best cross-region consistency story; Postgres-compatible SQL.
**Cons**: Smaller community; higher per-node cost; team has zero operational experience.
**Why rejected**: Operational risk too high for a data store that's currently functional. Revisit in 12 months when team has Postgres experience.

### Alternative 3: Stay on DynamoDB, accept the constraints

**Description**: No change. Live with query inflexibility and cross-region lag.

**Pros**: Zero migration cost.
**Cons**: Doesn't address the cross-region oversell problem (which is causing customer complaints).
**Why rejected**: The customer impact (oversells) is no longer acceptable per CS team escalation.

## References

- Spec: `.orchestrate/auto-orc-20260420-inventory/stage-2/inventory-spec.md`
- Related RFC: RFC-2026-03 (Cross-region consistency strategy) — `docs/rfcs/2026-03-cross-region-consistency.md`
- Related ADRs: ADR-0009 (Original DynamoDB selection) — superseded by this ADR
- External: Postgres at scale postmortem (vendor), Aurora Global Database docs

## Implementation notes

- Phase 1 (weeks 1–2): Dual-write via outbox pattern; reads still from DynamoDB
- Phase 2 (weeks 3–6): Backfill historical data; reconciliation job verifies parity
- Phase 3 (weeks 7–8): Cut over reads region by region; remove DynamoDB writes after 1 week of stability
- Rollback: Outbox pattern allows reverting writes-direction at any phase
```

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Writing the ADR after the fact, glossing over alternatives | Capture alternatives at decision time, not retroactively |
| One-paragraph "Context" with no specifics | Cite incident reports, metrics, customer feedback |
| Decision phrased as "we discussed X and chose Y" | State the decision in active present tense: "We will use Y because..." |
| Consequences only positive | Negative + neutral are equally important; future readers need the full picture |
| Skipping References | At minimum, link the spec and any prior ADR |
| Modifying an Accepted ADR | NEVER. Write a new ADR that supersedes; mark prior as Superseded |
