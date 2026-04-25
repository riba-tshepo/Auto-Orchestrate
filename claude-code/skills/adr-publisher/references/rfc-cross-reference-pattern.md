# ADR ↔ RFC Cross-Reference Pattern

ADRs (P-060) record decisions; RFCs (P-085) propose architectural changes for guild-wide review. They cross-reference in three ways:

## 1. ADR triggered by an RFC

A guild-wide change (e.g., "All services must export OpenTelemetry traces") is debated as an RFC. Once accepted, each affected team writes an ADR documenting their team's adoption decision.

**RFC** (`docs/rfcs/2026-04-otel-adoption.md`):
- Status: Accepted
- Audience: Engineering org
- Decision: Adopt OpenTelemetry as the standard observability instrumentation across all services

**ADR per affected service** (`docs/adr/0021-otel-adoption-inventory-service.md`):
- Status: Accepted
- References → RFC-2026-04
- Decision: Inventory service adopts OpenTelemetry via the spring-otel autoconfigure starter

The ADR reference: `Related RFC: docs/rfcs/2026-04-otel-adoption.md (RFC-2026-04, Accepted 2026-04-15)`

## 2. ADR proposes a change that warrants an RFC

A team-level decision turns out to have guild-wide implications. The ADR is written, but its `Consequences` section flags the need for an RFC, and a follow-up RFC is started.

**ADR** (`docs/adr/0028-async-event-bus-for-inventory.md`):
- Status: Accepted
- Decision: Use Kafka as our event bus for inventory state changes
- Consequences (Positive): "Decouples inventory from downstream consumers"
- Consequences (Negative): "**Other teams may want similar event-bus access; recommend an RFC to standardize event-bus governance.**"

**Follow-up RFC** (created by staff-principal-engineer):
- Title: RFC-2026-05: Event-bus governance for product teams
- References: ADR-0028 (the trigger)

## 3. ADR supersedes a prior ADR

Decisions evolve. When a new ADR replaces an older one, both ADRs link to each other.

**Prior ADR** (`docs/adr/0009-dynamodb-for-inventory.md`):
- Status: ~~Accepted~~ → **Superseded by ADR-0014**
- Original decision body remains UNMODIFIED (immutability rule)
- Status line updates to: `Status: Superseded by [ADR-0014](0014-postgres-for-inventory.md)`

**New ADR** (`docs/adr/0014-postgres-for-inventory.md`):
- Status: Accepted
- References: ADR-0009 (predecessor)
- Context section explains why the prior decision was revisited

## Cross-reference syntax

In ADRs, use these reference forms:

```markdown
## References
- Related RFC: [RFC-2026-04 (OTel adoption)](../rfcs/2026-04-otel-adoption.md)
- Predecessor: [ADR-0009 (DynamoDB selection)](0009-dynamodb-for-inventory.md)
- Triggered RFC: [RFC-2026-05 (Event-bus governance)](../rfcs/2026-05-event-bus-governance.md) — pending
```

In RFCs, mirror the cross-reference:

```markdown
## Related Decisions
- ADRs that triggered this RFC: ADR-0028
- ADRs that adopt this RFC's outcome: ADR-0021, ADR-0023, ADR-0027 (per-service adoption)
```

## When to escalate ADR → RFC

The adr-publisher skill should flag for staff-principal-engineer review when an ADR's Consequences section meets ANY of these criteria:

- Decision affects ≥2 other teams
- Decision changes a documented standard or pattern (P-088 Architecture Pattern Change)
- Decision introduces a new technology to the org's tech stack (P-087 Language Tier Policy)
- Decision has compliance / security / privacy implications

For these cases, the orchestrator should spawn staff-principal-engineer with `PHASE: GOVERNANCE` sub-routine `tech_excellence` to consider whether an RFC is needed (P-085).

## Index files

- `docs/adr/README.md` — chronological ADR index with title, status, date
- `docs/rfcs/README.md` — chronological RFC index with title, status, date

Both files are updated by the adr-publisher (for ADRs) and the staff-principal-engineer agent (for RFCs).
