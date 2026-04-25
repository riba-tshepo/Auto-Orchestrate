---
name: threat-modeler
description: |
  STRIDE-based threat enumeration for security-critical changes. Implements P-038
  (Threat Modeling) and supports P-047 (Cloud Architecture Review Board / CARB).
  Produces a structured threat-model artifact (asset, threat type, severity, mitigation)
  that downstream agents (validator, cab-reviewer) consume to verify mitigations.
  Use when user says "threat model", "stride analysis", "security threat enumeration",
  "appsec scope review", "attack surface analysis".
triggers:
  - threat model
  - stride analysis
  - security threat enumeration
  - appsec scope review
  - attack surface analysis
---

# Threat Modeler Skill

You produce a structured threat model using the STRIDE framework. The output feeds three downstream consumers: the Scope Contract's risk section (P-010), the security-engineer's domain review at Phase 5s, and the CAB Decision Record at Phase 7 (when the change is HIGH-risk).

## When to use

| Trigger | Process | Pipeline node |
|---------|---------|---------------|
| Stage P2 (Scope Contract) | P-012 (AppSec Scope Review) co-agent — scope-level threat surface | security-engineer produces P2-appsec-scope-review.md |
| Phase 5s (Security Phase) | P-038 (Threat Modeling) — full implementation-level threat model | security-engineer produces phase-5s-security-findings.md |
| Phase 7 (CAB prelude) for HIGH-risk changes | P-047 (CARB) input | security-engineer feeds threat model into CAB review |

## STRIDE framework

For each asset (data store, service, API, user role, third-party integration), enumerate threats across six categories:

| Letter | Threat | Question to ask |
|--------|--------|-----------------|
| **S** | Spoofing | Could an attacker impersonate this asset/identity? |
| **T** | Tampering | Could data or code in this asset be modified maliciously? |
| **R** | Repudiation | Could a user deny an action they performed? |
| **I** | Info disclosure | Could confidential data leak from this asset? |
| **D** | DoS (Denial of Service) | Could this asset be made unavailable? |
| **E** | Elevation of privilege | Could a low-privilege actor gain higher privileges? |

Read `references/stride-template.md` for the full worksheet structure and `references/threat-model-output-schema.md` for the structured output format.

## How to use

### Step 1: Enumerate assets

From the Scope Contract (P2) or implementation diff (Stage 3+), list:
- **Data stores**: databases, file stores, caches, message queues
- **Services**: every microservice, function, or component
- **External integrations**: third-party APIs, vendor systems
- **User roles**: each role with distinct privilege levels
- **Trust boundaries**: where data crosses from one trust zone to another

### Step 2: Apply STRIDE per asset

For each asset, walk through the 6 STRIDE categories. For each category, answer:
- Is this threat applicable to this asset? (Y/N)
- If Y, what is the attack scenario?
- What is the severity? (CRITICAL / HIGH / MEDIUM / LOW)
- What is the recommended mitigation?

### Step 3: Build the data flow diagram

Draw (in markdown/ASCII) the data flow:
- External entities (users, third parties)
- Processes (your services)
- Data stores
- Data flows (with direction + auth/encryption status)
- Trust boundaries (dotted lines crossing flows)

### Step 4: Produce the structured output

Write the threat model artifact to:
- Stage P2: `.orchestrate/<session>/planning/P2-appsec-scope-review.md`
- Phase 5s: `.orchestrate/<session>/phase-receipts/phase-5s-security-findings.md`
- Phase 7 CAB: `.orchestrate/<session>/phase-7/cab/security-review.md`

Use the structure in `references/threat-model-output-schema.md`. The output MUST include:

```markdown
# Threat Model — [Scope/Component Name]

## Assets

| ID | Asset | Type | Trust Zone |
|----|-------|------|------------|
| A1 | ... | ... | ... |

## Data Flow Diagram

[ASCII diagram or reference to a separate .puml file]

## Threats (STRIDE per asset)

### A1: <Asset Name>

| Category | Applicable? | Attack Scenario | Severity | Mitigation |
|----------|-------------|-----------------|----------|------------|
| Spoofing | Y/N | ... | CRITICAL | ... |
| Tampering | ... | | | |
| Repudiation | ... | | | |
| Info Disclosure | ... | | | |
| DoS | ... | | | |
| Elevation | ... | | | |

[repeat per asset]

## Mitigations Summary

| Mitigation | Affects assets | Spec requirement | Implementation responsibility |
|------------|----------------|------------------|-------------------------------|
| Parameterized queries | A1, A2 | Stage 2 spec section X | software-engineer |
| Rate limiting at API gateway | A3 | Stage 2 spec section Y + IaC | infra-engineer |

## Critical findings (CRITICAL or HIGH severity)

[Must surface to RAID log via raid-logger. List each finding with proposed RAID entry.]

## Acceptance criteria for Stage 5 validation

- All CRITICAL mitigations implemented and verified
- HIGH mitigations implemented OR explicitly accepted with risk acknowledgment in RAID log
```

### Step 5: Cross-link to other skills

- For each CRITICAL/HIGH finding, instruct the orchestrator to append to RAID log via `raid-logger` skill
- For dependencies (e.g., new packages with CVEs), reference researcher's CVE check (RES-005)
- For Phase 7 CAB, your output becomes a section of `cab/security-review.md`

## Outputs

- Markdown threat model document (per the schema in references)
- Severity-ranked findings list (CRITICAL/HIGH/MEDIUM/LOW counts)
- List of mitigations cross-referenced to spec sections and assignees
- RAID log entries proposed for CRITICAL/HIGH items

## Related skills

- `raid-logger` — for registering CRITICAL/HIGH findings as Risks
- `security-auditor` — for code-level vulnerability scanning (complements threat model)
- `cab-reviewer` — consumes threat model for CAB Decision Record

## Reference

- `references/stride-template.md` — full STRIDE worksheet with worked examples
- `references/threat-model-output-schema.md` — structured output schema
- Canonical processes: P-038 in `processes/06_security_compliance.md`; P-047 in `processes/07_infrastructure_platform.md`
