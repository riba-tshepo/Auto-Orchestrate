---
name: raid-logger
description: |
  Append-only RAID log management for Risks, Assumptions, Issues, and Dependencies.
  Used to seed and maintain `.orchestrate/<session>/raid-log.json` per the RAID-001
  constraint (single shared log; never overwrite). Implements P-010 (Assumptions and
  Risks Registration), P-074 (RAID Log Maintenance), P-075 (Risk Register at Scope Lock).
  Use when user says "raid log", "register risk", "track assumption", "raid entry",
  "risk register", "log dependency", "scope-lock risks".
triggers:
  - raid log
  - register risk
  - track assumption
  - raid entry
  - risk register
  - log dependency
  - scope-lock risks
---

# RAID Logger Skill

You manage the RAID (Risks, Assumptions, Issues, Dependencies) log that runs across the entire pipeline session. The RAID log is the single source of truth for tracking uncertainty, risk, and cross-cutting concerns.

## When to use

| Trigger | Process | Pipeline node |
|---------|---------|---------------|
| Stage P2 (Scope Contract) | P-010 (Assumptions and Risks Registration) | product-manager seeds initial entries |
| Phase 9 risk sub-routine | P-074 (RAID Log Maintenance) | technical-program-manager appends updates |
| Pre-Phase 5 anytime | P-075 (Risk Register at Scope Lock) | product-manager finalizes scope-lock risks |
| Whenever a new risk surfaces | any | any agent — append, never modify |

## Constraints (RAID-001)

1. **Single log per session** at `.orchestrate/<session_id>/raid-log.json` — JSONL format (one entry per line).
2. **Append-only.** Never overwrite, never delete, never modify existing entries. Status changes are NEW entries with `update_of: <prior_id>`.
3. **Atomic writes.** Use the `append_raid.py` script — it implements file-locking + dedup to handle concurrent writes from co-agents.
4. **Schema enforced.** Every entry must conform to `references/raid-entry-schema.md`. The script rejects non-conforming entries with `EXIT_INVALID_INPUT`.

## Vocabulary

**Type**: `Risk` | `Assumption` | `Issue` | `Dependency`

**Severity** (for Risk and Issue): `CRITICAL` | `HIGH` | `MEDIUM` | `LOW`. Assumptions and Dependencies use `severity: null` unless they have a quantifiable risk dimension.

**Status**: `open` | `mitigating` | `resolved` | `accepted` | `escalated`

## How to use

### To register a new entry

1. Read `references/raid-entry-schema.md` to confirm field requirements.
2. Build the entry as a JSON object:
   ```json
   {
     "id": "raid-001",
     "type": "Risk",
     "description": "Third-party API rate limit may exceed sprint quota",
     "severity": "HIGH",
     "owner": "engineering-manager",
     "status": "open",
     "source_process": "P-010",
     "mitigation": "Negotiate higher quota with vendor; cache aggressively",
     "timestamp": "<ISO-8601>"
   }
   ```
3. Run the script:
   ```
   python3 ~/.claude/skills/raid-logger/scripts/append_raid.py \
     --session <session_id> \
     --entry-json '<entry-json>'
   ```
4. Script returns `EXIT_SUCCESS` (0) on append, `EXIT_DUPLICATE` (10) if `id` already exists, `EXIT_INVALID_INPUT` (2) on schema violation.

### To update an existing entry's status

Append a new entry referencing the prior one:

```json
{
  "id": "raid-001-update-1",
  "type": "Risk",
  "description": "Third-party API rate limit may exceed sprint quota",
  "severity": "HIGH",
  "owner": "engineering-manager",
  "status": "mitigating",
  "source_process": "P-074",
  "update_of": "raid-001",
  "mitigation": "Vendor approved 2x quota; caching layer deployed",
  "timestamp": "<ISO-8601>"
}
```

### To list current entries

```
python3 ~/.claude/skills/raid-logger/scripts/append_raid.py \
  --session <session_id> --list-current
```

This collapses update chains and shows the latest status per `id`.

## Outputs

- Single line appended to `.orchestrate/<session_id>/raid-log.json`
- Stdout: JSON acknowledgment with `id`, `appended_at`, `total_entries`
- Exit code per `_shared/python/layer0/exit_codes`

## Related skills

- `validator` — checks RAID log integrity at Stage 5 validation
- `cab-reviewer` — consumes CRITICAL/HIGH risks for the CAB Decision Record at Phase 7

## Reference

- `references/raid-entry-schema.md` — full JSON schema with required/optional fields
- Canonical processes: P-010, P-074, P-075 in `processes/02_scope_contract_management.md` and `processes/13_risk_change_management.md`
- Pipeline constraint: `RAID-001` in `commands/auto-orchestrate.md`
