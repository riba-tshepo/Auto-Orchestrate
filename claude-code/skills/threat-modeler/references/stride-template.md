# STRIDE Worksheet Template

## How to use

1. List every asset in your scope (data stores, services, integrations, user roles).
2. For each asset, walk through all 6 STRIDE categories. Mark Applicable Y/N. If Y, fill in the attack scenario, severity, and mitigation.
3. Critical findings are surfaced to the RAID log via the `raid-logger` skill.

## The 6 STRIDE categories in detail

### S — Spoofing identity

**What**: An attacker pretends to be someone or something they're not.

**Common scenarios**:
- Stolen session tokens used to impersonate a user
- DNS hijack redirects users to attacker-controlled service
- Unverified webhook callers sending malicious payloads
- Insider re-uses another employee's credentials

**Common mitigations**:
- Strong authentication (multi-factor where possible)
- Token rotation + short TTL
- Mutual TLS for service-to-service
- Webhook signature verification (HMAC)
- Audit logging of authentication events

### T — Tampering with data

**What**: Data is modified by an attacker — in transit or at rest.

**Common scenarios**:
- API request body tampered with at a proxy
- Database row modified by attacker with SQL injection
- Configuration file replaced via supply chain attack
- Message queue payload tampered between producer and consumer

**Common mitigations**:
- TLS for all data in transit
- Encryption at rest for sensitive data
- Input validation + parameterized queries
- Cryptographic signatures on critical data (e.g., signed JWTs, signed packages)
- Immutable audit logs

### R — Repudiation

**What**: A user denies performing an action; the system cannot prove they did.

**Common scenarios**:
- User claims they didn't authorize a payment
- Admin denies making a destructive config change
- API client denies sending a malicious request

**Common mitigations**:
- Comprehensive audit logging (who, what, when, IP, user-agent)
- Cryptographic non-repudiation (signed transactions)
- Immutable log storage (e.g., write-once, append-only)
- Time synchronization (NTP) for accurate timestamps

### I — Information disclosure

**What**: Confidential data is exposed to unauthorized parties.

**Common scenarios**:
- Database backup leaks via misconfigured S3 bucket
- Error messages reveal internal stack traces, schema, or secrets
- Log files contain PII/credentials
- Side-channel: timing attack reveals existence of valid usernames

**Common mitigations**:
- Encryption at rest + in transit
- Principle of least privilege (RBAC + per-resource ACLs)
- Sanitize error messages (generic public errors; detail only in internal logs)
- Mask/redact sensitive fields in logs
- Constant-time comparisons for security-critical checks

### D — Denial of Service

**What**: System is rendered unavailable.

**Common scenarios**:
- API flooded with high-volume requests
- Resource exhaustion via large file uploads
- Algorithmic DoS via malformed input that triggers exponential parsing
- Dependency outage cascades into ours

**Common mitigations**:
- Rate limiting at API gateway (per-user, per-IP, per-endpoint)
- Request size limits
- Input parsing limits (max depth, max length)
- Circuit breakers for downstream dependencies
- Capacity planning + auto-scaling
- DDoS protection at edge (CloudFlare, AWS Shield, etc.)

### E — Elevation of privilege

**What**: A low-privilege actor gains higher privileges.

**Common scenarios**:
- IDOR (Insecure Direct Object Reference): user accesses another user's data by changing an ID in URL
- Buffer overflow → arbitrary code execution
- Privilege escalation via insecure deserialization
- Container escape via kernel vulnerability

**Common mitigations**:
- Authorization checks at every endpoint (don't trust the client)
- RBAC with explicit role definitions
- Least-privilege defaults (deny by default)
- Memory-safe languages where possible
- Avoid deserializing untrusted data
- Container isolation hardening (gVisor, kata, etc.)

## Worked example — Asset: User Sessions Service

| Category | Applicable? | Attack Scenario | Severity | Mitigation |
|----------|-------------|-----------------|----------|------------|
| **S** Spoofing | YES | Session token leaked from logs is replayed by attacker to impersonate user | HIGH | Short token TTL (15min); rotate on privilege change; bind tokens to IP+user-agent |
| **T** Tampering | YES | Token payload modified to escalate privileges | HIGH | Sign tokens with HMAC-SHA256; verify signature on every request |
| **R** Repudiation | NO (not applicable to session service itself) | n/a | n/a | Handled at app layer with audit logs |
| **I** Info Disclosure | YES | Tokens written to access logs end up in cold storage indefinitely | MEDIUM | Mask token in access logs; rotate logging keys; 90-day log retention |
| **D** DoS | YES | Token validation endpoint flooded with requests, exhausting CPU | MEDIUM | Rate limit per IP at API gateway; cache validated token results for TTL window |
| **E** Elevation | YES | If signing key leaked, attacker forges any user's token (root access) | CRITICAL | Rotate signing keys quarterly; store in HSM/KMS; alert on key access anomalies |

## Severity rubric

| Severity | Definition |
|----------|------------|
| **CRITICAL** | System-wide compromise possible; immediate user/data harm; regulatory exposure |
| **HIGH** | Limited compromise of multiple users/components; significant harm; requires mitigation before launch |
| **MEDIUM** | Limited to single user/component; mitigatable post-launch with monitoring |
| **LOW** | Theoretical or low-impact; acceptable risk with documented acknowledgment |

## When to escalate to CAB (P-076)

Escalate to the Pre-Launch Risk Review (CAB) gate if:
- Any CRITICAL finding without confirmed mitigation, OR
- ≥3 HIGH findings without confirmed mitigation, OR
- Any finding affecting customer PII / payment data / compliance scope (PCI/HIPAA/SOC2/GDPR), OR
- Any finding requiring infrastructure changes that span teams
