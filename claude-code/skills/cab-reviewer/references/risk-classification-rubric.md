# Risk Classification Rubric

Score the change across 5 dimensions; sum determines the risk tier.

## The 5 dimensions

### 1. Blast radius

How many users, services, or data stores would be affected if this change fails catastrophically?

| Score | Description |
|-------|-------------|
| 1 | Internal/dev tools only; no external impact |
| 2 | Single team's services; <100 internal users; no customer impact |
| 3 | Single product area; <10% of traffic; affects subset of customers |
| 4 | Cross-product; >10% of traffic; affects most customers |
| 5 | Platform-wide; all customers affected; data-corruption risk |

### 2. Reversibility

How fast and how reliably can we roll back if something goes wrong?

| Score | Description |
|-------|-------------|
| 1 | Feature flag; instant rollback (<10 seconds) |
| 2 | Code rollback via redeploy; <5 minutes |
| 3 | Code rollback + minor data cleanup; <30 minutes |
| 4 | Database migration partial rollback; 30+ minutes; some data may be lost |
| 5 | Irreversible: schema changes that can't be undone, deleted data, third-party API state |

### 3. Compliance / Security

Does this change touch regulated data, security-critical paths, or compliance scope?

| Score | Description |
|-------|-------------|
| 1 | No PII / no security relevance |
| 2 | Internal data only; no customer data |
| 3 | Customer data but not regulated (e.g., usernames, preferences) |
| 4 | PII / payment data / SOC2 control changes |
| 5 | HIPAA / financial transactions / authentication / regulatory submission |

### 4. Novelty

How well-understood is this type of change?

| Score | Description |
|-------|-------------|
| 1 | Routine deploy of well-tested service; pattern used 100+ times |
| 2 | Familiar pattern with minor variations |
| 3 | Pattern used a few times in this org; some learning required |
| 4 | First time for this team; pattern documented elsewhere |
| 5 | Novel architecture; first-of-its-kind in this org |

### 5. Detection time

How long until we'd notice a problem after deploy?

| Score | Description |
|-------|-------------|
| 1 | Synthetic monitor catches in <1 min; auto-alert |
| 2 | SLO alert within 5–15 min |
| 3 | SLO alert within 30 min OR detected via dashboards in 30 min |
| 4 | Detected via customer complaints in 1–4 hours |
| 5 | Silent failure; could take days to detect (e.g., gradual data corruption) |

## Tier determination

Sum the 5 scores (range: 5–25):

| Total score | Tier | CAB required? |
|-------------|------|---------------|
| 5–9 | LOW | No |
| 10–14 | MEDIUM | No |
| 15–19 | **HIGH** | **YES** |
| 20–25 | **CRITICAL** | **YES (mandatory; cannot skip)** |

### Auto-escalation rules

A change is automatically classified at the higher tier (regardless of score) if ANY of:

- **Auto-CRITICAL**: any single dimension scores 5
  - Score-5 reversibility (irreversible) → CRITICAL automatically
  - Score-5 compliance (HIPAA / financial / regulatory) → CRITICAL automatically
  - Score-5 detection (silent failure mode) → CRITICAL automatically

- **Auto-HIGH**: any single dimension scores 4
  - Score-4 blast radius (cross-product / >10% traffic) → at minimum HIGH
  - Score-4 reversibility (long rollback with data loss) → at minimum HIGH
  - Score-4 compliance (PII / SOC2 / payment) → at minimum HIGH

## Worked example

**Change**: Migrate inventory database from DynamoDB to Postgres (8-week dual-write + cutover)

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Blast radius | 4 | Inventory affects 80%+ of customer-facing traffic |
| Reversibility | 4 | 30+ min to revert during cutover; some recent writes may be lost |
| Compliance/security | 4 | Customer order history is PII (SOC2 IM-3) |
| Novelty | 3 | Similar pattern done once before for sessions DB |
| Detection time | 2 | SLO breaches surface in 5-10 min via Datadog |

**Total**: 17/25 → **HIGH** tier

(Auto-rules: blast radius 4 + reversibility 4 + compliance 4 → HIGH minimum confirmed)

→ CAB review required (CAB-GATE-001 fires)

## Edge cases

### Change has multiple sub-changes

Score by the highest-risk sub-change. A release that includes both a feature flag toggle (LOW) and a schema migration (HIGH) gets the HIGH score.

### Change is reversible but has externalities

A change that's technically reversible (e.g., revoking sent emails) but has irreversible side effects (recipients have already read the emails) — score reversibility on the externality, not just the technical action.

### Change adds rather than modifies

New endpoint with no traffic until announced is LOW blast radius even if novel. The blast radius materializes after announcement.

### Compliance scope is unclear

If unsure whether PII / regulated data is in scope, route to security-engineer for a quick read BEFORE classifying. Default to higher score under uncertainty.

## Don't game the rubric

The rubric is a tool, not a rule to evade. If a change feels HIGH-risk but the score comes out at 14, the chair (TPM) can override upward. The chair cannot override downward.

If you find yourself deflating scores to avoid CAB, that's a signal something is wrong — consult the engineering-manager.
