---
name: adr-publisher
description: |
  Author and publish Architecture Decision Records (ADRs) following the MADR
  (Markdown ADR) template. Implements P-060 (ADR Publication). Auto-assigns
  the next sequential ADR number, enforces canonical sections (Context, Decision,
  Consequences, Alternatives, References), and cross-links to RFCs (P-085).
  Use when user says "write adr", "architecture decision record", "publish adr",
  "decision record", "document architectural decision".
triggers:
  - write adr
  - architecture decision record
  - publish adr
  - decision record
  - document architectural decision
---

# ADR Publisher Skill

You author Architecture Decision Records (ADRs) — the durable, immutable record of architectural decisions made during implementation. ADRs explain WHY a decision was made so future engineers (or the same engineer 6 months later) can understand the reasoning.

## When to use

Spawn this skill ONLY when the implementation introduces an architectural decision worth recording. Indicators:

- A new pattern is introduced (e.g., switching from synchronous to event-driven)
- A trade-off is made between competing options (e.g., chose Postgres over DynamoDB)
- A constraint is accepted (e.g., temporary single-region deployment)
- A standard is set or changed (e.g., adopting OpenTelemetry across services)

Do NOT write an ADR for routine implementation choices (which library version, how to format a function). Those go in code comments or PR descriptions.

| Trigger | Process | Pipeline node |
|---------|---------|---------------|
| Stage 6 (Documentation) co-agent | P-060 (ADR Publication) | software-engineer publishes ADR for any architectural decision in Stage 3 |
| Phase 9 tech_excellence sub-routine | P-085 (RFC Process) cross-link | staff-principal-engineer references ADRs in RFC process |

## How to use

### Step 1: Find the next ADR number

```
python3 ~/.claude/skills/adr-publisher/scripts/next_adr_number.py
```

Returns the next available NNNN (4-digit, zero-padded). The script scans `docs/adr/` for existing files matching `NNNN-*.md` and returns max+1.

### Step 2: Choose a short title

The title becomes the filename: `docs/adr/NNNN-<short-kebab-title>.md`. Keep it ≤6 words. Use present tense ("Use Postgres for inventory data") not past tense.

### Step 3: Apply the MADR template

Read `references/adr-template.md` for the canonical format. Required sections:

1. **Title** — `# ADR-NNNN: <title>`
2. **Status** — Proposed | Accepted | Deprecated | Superseded by ADR-XXXX
3. **Context** — what problem prompted the decision; what were we observing?
4. **Decision** — what was decided?
5. **Consequences** — positive, negative, and neutral implications
6. **Alternatives Considered** — what was rejected and why
7. **References** — links to spec, design docs, RFCs, related ADRs

### Step 4: Cross-link RFCs (when applicable)

If this decision was preceded by an RFC (P-085), add a cross-reference. See `references/rfc-cross-reference-pattern.md` for the format.

If this decision should *trigger* an RFC (e.g., it changes a guild-wide standard), surface that to staff-principal-engineer.

### Step 5: Set status

| Status | When to use |
|--------|-------------|
| `Proposed` | Decision is in flight; PR open; awaiting review |
| `Accepted` | Decision is in effect; reflected in code |
| `Deprecated` | Decision still applies but is being phased out; no replacement yet |
| `Superseded by ADR-XXXX` | A later ADR replaces this one; the prior ADR is preserved (immutability) |

### Step 6: Commit

Place the file at `docs/adr/NNNN-<title>.md` in the project repo (NOT in the session directory — ADRs are durable, repo-level artifacts).

Update `docs/adr/README.md` (the ADR index) with a new row.

## Outputs

- `docs/adr/NNNN-<title>.md` — the ADR document
- Updated `docs/adr/README.md` — index of all ADRs
- (Optional) Cross-reference entry in any related RFC

## Immutability rule

Once an ADR is `Accepted`, the body MUST NOT be modified. To change a decision, write a new ADR that supersedes the prior one. The prior ADR's `Status` is updated to `Superseded by ADR-XXXX` (this is the only allowed modification).

This preserves the historical record of why decisions were made.

## Related skills

- `docs-write` — for general documentation; ADRs are the specialized form
- `docs-lookup` — to research prior ADRs or RFCs before writing
- `dev-workflow` — for the commit/PR conventions

## Reference

- `references/adr-template.md` — full MADR template with worked example
- `references/rfc-cross-reference-pattern.md` — how to link ADRs ↔ RFCs
- Canonical processes: P-060 in `processes/10_documentation_knowledge.md`; P-085 in `processes/16_technical_excellence_standards.md`
