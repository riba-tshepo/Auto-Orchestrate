# RAID Entry Schema

Every entry in `.orchestrate/<session>/raid-log.json` (JSONL format) must conform to this schema.

## Required fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique entry identifier. Pattern: `raid-NNN` for original, `raid-NNN-update-N` for status updates. Lowercase, hyphenated. |
| `type` | enum | One of: `Risk`, `Assumption`, `Issue`, `Dependency` |
| `description` | string | One-sentence description of the item. ≥10 chars, ≤500 chars. |
| `owner` | string | Agent name from manifest.agents that owns this item (e.g., `engineering-manager`, `technical-program-manager`). |
| `status` | enum | One of: `open`, `mitigating`, `resolved`, `accepted`, `escalated` |
| `source_process` | string | Canonical P-XXX that created this entry (e.g., `P-010` for initial seeding, `P-074` for RAID Log Maintenance, `P-075` for Risk Register at Scope Lock). |
| `timestamp` | string | ISO-8601 timestamp of when the entry was created |

## Conditionally required

| Field | Type | Required when | Description |
|-------|------|---------------|-------------|
| `severity` | enum or null | `type` == `Risk` or `Issue` | One of: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`. Null for `Assumption` and `Dependency` (unless a meaningful severity applies). |
| `update_of` | string | This entry replaces a prior one's status | The `id` of the prior entry being updated. Required for status changes. |
| `mitigation` | string | `severity` is `CRITICAL` or `HIGH` | Mitigation plan or current mitigation status. |

## Optional fields

| Field | Type | Description |
|-------|------|-------------|
| `tags` | array of strings | Free-form tags for filtering (e.g., `["security", "performance", "vendor-risk"]`) |
| `due_by` | string (ISO-8601) | When this needs to be resolved by — common for Dependencies and time-bound Risks |
| `resolution` | string | Set when `status` is `resolved` — describes how it was resolved |
| `escalation_path` | string | For `Dependency` type — escalation owner if blocked |

## Example entries

### Original Risk
```json
{
  "id": "raid-001",
  "type": "Risk",
  "description": "Third-party API rate limit may exceed sprint quota during launch week",
  "severity": "HIGH",
  "owner": "engineering-manager",
  "status": "open",
  "source_process": "P-010",
  "mitigation": "Negotiate higher quota with vendor; deploy caching layer with 5min TTL",
  "tags": ["vendor-risk", "performance"],
  "timestamp": "2026-04-25T10:30:00Z"
}
```

### Status update (mitigating)
```json
{
  "id": "raid-001-update-1",
  "type": "Risk",
  "description": "Third-party API rate limit may exceed sprint quota during launch week",
  "severity": "HIGH",
  "owner": "engineering-manager",
  "status": "mitigating",
  "source_process": "P-074",
  "update_of": "raid-001",
  "mitigation": "Vendor approved 2x quota (effective 2026-05-01); caching layer deployed in canary",
  "timestamp": "2026-04-26T14:15:00Z"
}
```

### Final resolution
```json
{
  "id": "raid-001-update-2",
  "type": "Risk",
  "description": "Third-party API rate limit may exceed sprint quota during launch week",
  "severity": "HIGH",
  "owner": "engineering-manager",
  "status": "resolved",
  "source_process": "P-074",
  "update_of": "raid-001-update-1",
  "resolution": "Quota increase confirmed; load test at 1.5x peak passed without 429s",
  "timestamp": "2026-04-29T09:00:00Z"
}
```

### Assumption
```json
{
  "id": "raid-002",
  "type": "Assumption",
  "description": "Customer base will adopt new auth flow within 30 days of release",
  "severity": null,
  "owner": "product-manager",
  "status": "open",
  "source_process": "P-010",
  "timestamp": "2026-04-25T10:35:00Z"
}
```

### Dependency
```json
{
  "id": "raid-003",
  "type": "Dependency",
  "description": "Identity team's session-token library must reach v2.0 before our auth refactor lands",
  "severity": null,
  "owner": "technical-program-manager",
  "status": "open",
  "source_process": "P-015",
  "due_by": "2026-05-15",
  "escalation_path": "Identity team EM → Director of Platform → VP Engineering",
  "tags": ["cross-team"],
  "timestamp": "2026-04-25T11:00:00Z"
}
```

### Issue (after work has started)
```json
{
  "id": "raid-004",
  "type": "Issue",
  "description": "Stage 3 implementation revealed schema migration is destructive — backfill needed",
  "severity": "MEDIUM",
  "owner": "data-engineer",
  "status": "mitigating",
  "source_process": "P-074",
  "mitigation": "Pivot to non-destructive migration with dual-write; backfill in batch job",
  "tags": ["data-migration"],
  "timestamp": "2026-04-27T16:20:00Z"
}
```

## Validation rules

The `append_raid.py` script enforces:

1. `id` is unique within the log (unless `update_of` is set, in which case the prior `id` must exist)
2. `type` is one of the 4 enum values
3. `severity` is one of the 4 enum values (or `null` for non-Risk/Issue types)
4. `status` is one of the 5 enum values
5. `description` is 10–500 chars
6. `owner` is a known agent name (validated against `manifest.json` agents list)
7. `source_process` matches pattern `P-\d{3}`
8. `timestamp` is valid ISO-8601
9. CRITICAL/HIGH severity Risks/Issues MUST have a `mitigation` field
10. `update_of` references an existing entry's `id`
