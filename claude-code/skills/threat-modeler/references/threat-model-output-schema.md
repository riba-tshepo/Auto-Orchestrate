# Threat Model Output Schema

The structured output the threat-modeler skill produces. Downstream consumers (validator, cab-reviewer, raid-logger) parse this format.

## Output file structure

```markdown
# Threat Model — <Component or Scope Name>

**Author**: security-engineer
**Created at**: <ISO-8601>
**Pipeline node**: <P2 | Phase 5s | Phase 7 CAB>
**Scope**: <description of what's in scope>

## Summary

- **Assets identified**: <N>
- **Threats enumerated**: <N>
- **Severity breakdown**: <X CRITICAL, Y HIGH, Z MEDIUM, W LOW>
- **Mitigations recommended**: <N>
- **Verdict**: <SAFE_TO_PROCEED | MITIGATIONS_REQUIRED | ESCALATE_TO_CAB>

## 1. Assets

| ID | Asset | Type | Trust Zone | Owner |
|----|-------|------|------------|-------|
| A1 | User Sessions Service | Service | Internal | platform-team |
| A2 | Session Token Database | Data Store | Internal-Secure | platform-team |
| A3 | Identity Provider (Auth0) | External | External | vendor |

**Type values**: Service / Data Store / External Integration / User Role / Trust Boundary

**Trust Zone values**: Public / Internal / Internal-Secure / External / Privileged

## 2. Data Flow Diagram

[ASCII diagram OR reference to .puml/.drawio file]

```
External User
     │ (1) HTTPS POST /login
     ▼
[API Gateway] ─ TLS, rate-limit ─→ [Auth Service A1]
                                          │
                                  (2) verify creds
                                          ▼
                                 [Identity Provider A3]
                                          │
                                  (3) JWT signed
                                          ▼
                                  [Token Store A2]
                                  (encrypted at rest)
```

Trust boundaries marked with dashed lines crossing flow arrows.

## 3. Threat Enumeration (STRIDE)

For EACH asset, repeat this block:

### A1: User Sessions Service

| Category | Applicable? | Attack Scenario | Severity | Mitigation | Mitigation Status |
|----------|-------------|-----------------|----------|------------|-------------------|
| Spoofing | YES | Token replay via leaked session | HIGH | Token TTL ≤15min; rotate on privilege change | RECOMMENDED |
| Tampering | YES | Token payload tampered to escalate role | HIGH | HMAC-SHA256 signature with key rotation | IMPLEMENTED |
| Repudiation | NO | (not applicable at this asset layer) | — | — | — |
| Info Disclosure | YES | Tokens logged in plain text | MEDIUM | Mask in access logs; 90-day retention | RECOMMENDED |
| DoS | YES | Token-validation endpoint flooded | MEDIUM | Rate limit + result caching | RECOMMENDED |
| Elevation | YES | Signing key leaked → attacker forges any token | CRITICAL | Rotate quarterly; store in KMS; access alarms | RECOMMENDED |

**Mitigation Status values**:
- `IMPLEMENTED` — already in code/config; cite location
- `RECOMMENDED` — proposed; needs Stage 2 spec or Stage 3 impl work
- `ACCEPTED` — risk accepted; documented in RAID log
- `BLOCKED` — cannot mitigate; CAB escalation required

[Repeat for A2, A3, ...]

## 4. Mitigations Summary

| Mitigation | Affected Assets | Spec Requirement | Implementation Owner | Status |
|------------|-----------------|------------------|----------------------|--------|
| Token TTL ≤15min + rotation | A1, A2 | Stage 2 spec §auth.token_lifecycle | software-engineer | RECOMMENDED |
| HMAC-SHA256 signing + KMS-backed keys | A1, A2 | Stage 2 spec §auth.token_signing | software-engineer + infra-engineer | RECOMMENDED |
| Rate limiting at gateway | A1 | Stage 2 spec §rate_limit_policy | infra-engineer | RECOMMENDED |
| Mask tokens in logs | A1, A2 | Stage 2 spec §logging.pii_masking | software-engineer | RECOMMENDED |

## 5. Critical Findings (CRITICAL + HIGH severity)

For each CRITICAL or HIGH finding, propose a RAID entry:

```json
{
  "type": "Risk",
  "description": "Signing key leak enables token forgery for any user (CRITICAL)",
  "severity": "CRITICAL",
  "owner": "security-engineer",
  "status": "open",
  "source_process": "P-038",
  "mitigation": "Rotate signing key quarterly; store in KMS; alert on access",
  "tags": ["security", "auth", "key-management"]
}
```

The orchestrator MUST append these via the `raid-logger` skill.

## 6. Acceptance Criteria for Stage 5 Validation

- [ ] All CRITICAL mitigations are IMPLEMENTED + verified by validator
- [ ] All HIGH mitigations are IMPLEMENTED, RECOMMENDED-with-Stage-3-task, or explicitly ACCEPTED with RAID log entry
- [ ] All MEDIUM mitigations are IMPLEMENTED or have a documented post-launch tracking item
- [ ] Threat model document committed to `.orchestrate/<session>/phase-receipts/`
- [ ] CAB escalation triggered if any CRITICAL is BLOCKED OR ≥3 HIGH are BLOCKED

## 7. Dependencies on Other Skills/Phases

- `raid-logger` — register CRITICAL/HIGH findings as RAID entries
- `security-auditor` — runs CVE checks on dependencies; flag any CVE that maps to a STRIDE category
- `validator` — at Stage 5, verifies acceptance criteria above
- `cab-reviewer` — at Phase 7, ingests threat model for CAB Decision Record

## Verdict values

| Verdict | Meaning | Next action |
|---------|---------|-------------|
| `SAFE_TO_PROCEED` | All findings ≤ MEDIUM with mitigations RECOMMENDED or IMPLEMENTED | Continue to Stage 3 implementation |
| `MITIGATIONS_REQUIRED` | HIGH findings present; mitigations must land in Stage 2 spec + Stage 3 impl | Add tasks; do NOT proceed to Phase 7 until verified |
| `ESCALATE_TO_CAB` | CRITICAL finding without mitigation OR multiple BLOCKED HIGH findings | Phase 7 CAB review fires automatically (CAB-GATE-001) |
