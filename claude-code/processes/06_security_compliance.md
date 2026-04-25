# Security & Compliance Processes — Technical Specification
## Processes P-038 through P-043

**Session**: auto-orc-20260405-procderive
**Date**: 2026-04-05
**Stage**: 2 — Process Specification
**Category**: 6 — Security & Compliance
**Source**: Stage 1 Process Architecture (2026-04-05_process-architecture.md)
**Derived From**: Clarity of Intent Framework; Engineering Team Structure Guide

---

## Linked Skills

The following Claude Code skills support processes in this category. Auto-orchestrate invokes them at the appropriate pipeline stages (see `processes/process_injection_map.md`); operators may also invoke them directly via the `Skill` tool.

| Skill | Purpose |
|-------|---------|
| `security-auditor` | Vulnerability scanning for shell scripts and source code — drives P-038 (Security by Design) and P-039 (SAST/DAST). |
| `spec-compliance` | Verifies security requirements are implemented and traceable — supports P-040 and P-041. |
| `validator` | Includes security scan results in zero-error gate — supports P-039 in CI. |
| `dependency-analyzer` | Detects circular imports and unauthorized cross-layer access that often correlate with security regressions — supports P-038. |

---

## Document Purpose

This specification fully defines the six Security & Compliance processes (P-038 through P-043) identified in the Stage 1 Process Architecture. Each process is specified with unambiguous ownership, stages, inputs/outputs, gates, success criteria, dependencies, and traceability back to the Clarity of Intent framework and organizational structure.

### Agents Referenced

All agent assignments map to the 13 agents defined in `.claude/agents/`:

| Agent File | Shorthand Used Here |
|---|---|
| `security-engineer.md` | security-engineer |
| `infra-engineer.md` | infra-engineer |
| `software-engineer.md` | software-engineer |
| `product-manager.md` | product-manager |
| `engineering-manager.md` | engineering-manager |
| `technical-program-manager.md` | technical-program-manager |
| `data-engineer.md` | data-engineer |
| `technical-writer.md` | technical-writer |

### Organizational Roles Referenced

| Role | Org Position | Reporting Line |
|---|---|---|
| CISO | C-Suite / VP equivalent | Reports to CEO |
| AppSec Lead / Security Architect | L6-L7 | Reports to Director of Security Engineering |
| AppSec Engineer | L4-L6 | Reports to AppSec Lead |
| Security Champion (Embedded) | L4-L5 software engineer | Solid-line: EM; Dotted-line: AppSec Lead |
| GRC Lead | L5-L6 | Reports to Director of Security Engineering |
| GRC Analyst / Compliance Engineer | L4-L5 | Reports to GRC Lead / Legal (matrix) |
| SOC Manager | M4-M5 | Reports to VP of Security Engineering |
| Platform Engineer | L4-L6 | Reports to Platform EM |

---

## P-038: Threat Modeling Process

### Overview

| Field | Value |
|---|---|
| **Process ID** | P-038 |
| **Process Name** | Threat Modeling Process |
| **Purpose** | Security Champion runs a STRIDE-based threat model for every new feature before development begins. AppSec reviews the output. No CRITICAL findings can be unresolved before feature development proceeds. |
| **Derived From** | Clarity of Intent — Stage 4 (Sprint Bridge), Sprint 1 story example: "Conduct threat model for tokenization flow"; Stage 0 research Category 6 |
| **Risk Level** | HIGH — unmodeled security threats become production vulnerabilities |

### Ownership

| Role | Agent | Responsibility |
|---|---|---|
| **Primary Owner** | `security-engineer` | Security Champion runs the threat model; AppSec reviews the output |
| **Supporting** | `software-engineer` | Tech Lead provides technical architecture context, data flow diagrams, and system boundaries |
| **Supporting** | `product-manager` | PM confirms business logic boundaries, identifies sensitive data flows and user-facing attack surfaces |

### Stages/Steps

| Step | Action | Responsible | SLA |
|---|---|---|---|
| 1 | **Feature Design Review** — Security Champion reviews the feature design with the squad, identifying components that handle user data, authentication, authorization, payments, or external integrations | Security Champion | Sprint 1, Day 1-2 |
| 2 | **STRIDE Analysis** — Systematic analysis conducted across all six STRIDE categories: Spoofing (authentication bypass), Tampering (data integrity), Repudiation (audit trail gaps), Information Disclosure (data leaks), Denial of Service (resource exhaustion), Elevation of Privilege (authorization bypass) | Security Champion + TL | Sprint 1, Day 2-4 |
| 3 | **Threat Model Document Production** — Document produced containing: (a) system architecture diagram with trust boundaries, (b) data flow diagrams showing sensitive data paths, (c) identified threats mapped to STRIDE categories, (d) proposed mitigations for each threat, (e) residual risk assessment | Security Champion | Sprint 1, Day 4-5 |
| 4 | **AppSec Review** — AppSec Engineer reviews the threat model for completeness, accuracy, and severity classification. AppSec may upgrade or downgrade severity classifications. | AppSec Engineer | Within 3 business days of submission |
| 5 | **CRITICAL Finding Resolution** — All CRITICAL findings must be resolved (mitigated, accepted via P-041, or designed out) before feature development begins. Resolution means the threat is either eliminated by design change or mitigated with a compensating control that AppSec confirms as adequate. | Security Champion + TL | Before feature development starts |
| 6 | **HIGH Finding Mitigation Planning** — All HIGH findings must have a named mitigation owner and a target sprint for resolution before development begins. HIGH findings may proceed into development with a plan but cannot ship unresolved. | Security Champion + EM | Before feature development starts |

### Inputs

| Input | Source | Format |
|---|---|---|
| Feature design documents | PM + TL (from Scope Contract, P-010) | Design doc or RFC |
| System architecture diagrams | TL / Staff Engineer | Architecture diagrams with trust boundaries |
| User data flow documentation | TL + Data Engineer | Data flow diagrams showing PII/sensitive data paths |
| Previous threat models for related features | Security backlog | Historical threat model documents |

### Outputs/Artifacts

| Output | Format | Stored In | Retention |
|---|---|---|---|
| Threat model document | Structured document using STRIDE template | Security documentation repository | Permanent; versioned per feature |
| CRITICAL/HIGH findings list | Table with: finding ID, STRIDE category, severity, description, mitigation, owner | Security backlog | Until closure verified |
| Security backlog items | Ticketed items for non-CRITICAL findings | Sprint backlog / security backlog | Until resolved |
| AppSec review sign-off | Approval record with reviewer name, date, conditions | Threat model document appendix | Permanent |

### Gate/Checkpoint

| Gate | Condition | Enforced By |
|---|---|---|
| **Sprint 1 Completion Gate** | Threat model must be AppSec-reviewed before the feature ships to production | AppSec Lead |
| **Development Start Gate** | No CRITICAL findings unresolved; all HIGH findings have mitigation owner and target sprint | Security Champion + AppSec |

**Gate Pass Criteria:**
- Threat model uses STRIDE methodology with all six categories assessed
- Every identified threat has a severity classification (CRITICAL / HIGH / MEDIUM / LOW)
- No CRITICAL findings are unresolved at the point of gate review
- All HIGH findings have a named owner and remediation target sprint
- All findings are logged in the security backlog with tracking IDs
- AppSec has reviewed and signed off on the threat model

**Gate Fail Action:** Feature development is blocked until CRITICAL findings are resolved. The Security Champion and TL revise the design to address findings. AppSec re-reviews within 2 business days of resubmission.

### Success Criteria

| Metric | Target | Measurement Method |
|---|---|---|
| STRIDE coverage | All 6 categories assessed for every feature | Threat model document audit |
| CRITICAL finding resolution rate | 100% resolved before feature launch | Security backlog tracking |
| Threat model completion rate | 100% of new features have a threat model before development | Sprint 1 completion records |
| AppSec review turnaround | Within 3 business days | Submission-to-review timestamp delta |
| Finding backlog health | All findings have owners; no orphaned findings | Quarterly security backlog review |

### Dependencies

| Dependency | Process | Nature |
|---|---|---|
| AppSec availability confirmed | P-012 (AppSec Scope Review) | AppSec Scope Review at Stage 2 confirms AppSec capacity for threat modeling in Sprint 1 |
| Sprint planning includes threat model story | P-025 (Sprint Planning) | Threat model must be a planned story in Sprint 1 |
| Feature design available | P-010 (Scope Contract) | Feature design from Scope Contract provides the input for threat modeling |

### Traceability

```
Clarity of Intent Stage 4 (Sprint Bridge)
  → Sprint Kickoff Brief, Section 3: Stories and Acceptance Criteria
    → Story: "Conduct threat model for tokenization flow"
      → Acceptance: "Threat model document complete using STRIDE methodology;
         reviewed by AppSec; no CRITICAL findings unresolved;
         findings logged in security backlog"
  → Sprint DoD: "SAST scan clean (no new critical or high findings)"
```

---

## P-039: SAST/DAST CI Integration Process

### Overview

| Field | Value |
|---|---|
| **Process ID** | P-039 |
| **Process Name** | SAST/DAST CI Integration Process |
| **Purpose** | Static Analysis Security Testing (SAST) and Dynamic Analysis Security Testing (DAST) scans integrated into the CI/CD pipeline. CRITICAL and HIGH findings block merge. |
| **Derived From** | Stage 0 research Category 6; Sprint Definition of Done checklist ("SAST scan clean — no new critical or high findings") |
| **Risk Level** | HIGH — missing SAST/DAST allows known vulnerability patterns to reach production |

### Ownership

| Role | Agent | Responsibility |
|---|---|---|
| **Primary Owner (CI/CD Integration)** | `infra-engineer` | Integrates SAST/DAST tools into CI pipeline; manages pipeline configuration, scan execution, and result publishing |
| **Primary Owner (Rule Configuration)** | `security-engineer` | Configures severity rules, false positive suppression policies, and security dashboard |
| **Supporting** | `software-engineer` | TL communicates findings to team; engineers remediate findings in their code |

### Stages/Steps

| Step | Action | Responsible | SLA |
|---|---|---|---|
| 1 | **SAST Tool Integration** — Platform Engineer integrates SAST tool (e.g., SonarQube, Semgrep, Checkmarx) into CI pipeline. SAST runs automatically on every pull request. No manual invocation required. | Platform Engineer | One-time setup; maintained continuously |
| 2 | **Severity Rule Configuration** — Security Engineer configures severity thresholds: CRITICAL and HIGH findings block PR merge. MEDIUM findings generate warnings. LOW/INFO findings logged to dashboard only. | Security Engineer | Reviewed quarterly |
| 3 | **DAST Tool Integration** — Platform Engineer integrates DAST tool (e.g., OWASP ZAP, Burp Suite) for API and web endpoint scanning. DAST runs against every staging deployment. | Platform Engineer | One-time setup; maintained continuously |
| 4 | **False Positive Suppression** — Security Champion reviews suspected false positives and submits suppression requests. AppSec must approve every suppression. Suppressed findings are logged with justification and reviewer name. | Security Champion (request) + AppSec (approval) | 48 hours for suppression review |
| 5 | **Security Dashboard Publishing** — All SAST/DAST results published to centralized security dashboard. Dashboard shows: finding counts by severity, trends over time, suppression rate, mean-time-to-remediation. | Platform Engineer (infra) + Security Engineer (content) | Real-time on scan completion |

### Inputs

| Input | Source | Format |
|---|---|---|
| CI/CD pipeline configuration | Platform Engineer (from P-033 CI/CD infrastructure) | Pipeline-as-code (YAML / Jenkinsfile / GitHub Actions) |
| Security tool licenses | CISO / Procurement | License keys / SaaS subscriptions |
| Codebase language inventory | TL / Platform Engineer | Language tier list from Engineering Team Structure Guide Section 4 |
| SAST/DAST rule configuration | Security Engineer | Tool-specific configuration files |

### Outputs/Artifacts

| Output | Format | Stored In | Retention |
|---|---|---|---|
| Integrated SAST CI gate | Pipeline configuration with SAST step | CI/CD repository | Permanent; version-controlled |
| Integrated DAST CI gate | Pipeline configuration with DAST step | CI/CD repository | Permanent; version-controlled |
| Merge block configuration | Severity-based merge blocking rules | CI/CD platform settings | Active configuration |
| Security finding dashboard | Web dashboard with charts and finding detail | Security dashboard platform | 12 months rolling |
| False positive suppression log | Suppression records with justification and approver | Security dashboard / repository | Permanent |

### Gate/Checkpoint

| Gate | Condition | Enforced By |
|---|---|---|
| **Continuous — Every PR** | SAST scan passes (no new CRITICAL/HIGH findings) before merge is permitted | CI/CD pipeline (automated) |
| **Continuous — Every Staging Deploy** | DAST scan completes and results published to dashboard | CI/CD pipeline (automated) |
| **Suppression Approval** | No finding suppressed without AppSec written approval | Security Champion + AppSec |

**Gate Pass Criteria:**
- SAST runs on every PR automatically without manual invocation
- CRITICAL and HIGH findings cannot be merged without Security Champion review and AppSec approval
- DAST runs against every staging deployment
- All suppressed findings have documented justification and AppSec approval
- Security dashboard is accessible to all engineering teams

**Gate Fail Action:** PR is blocked from merging. The engineer fixes the finding or the Security Champion initiates a false positive review. If the finding is a true positive that cannot be immediately fixed, P-041 (Security Exception Process) is invoked.

### Success Criteria

| Metric | Target | Measurement Method |
|---|---|---|
| SAST coverage | 100% of PRs scanned | CI/CD pipeline metrics |
| DAST coverage | 100% of staging deployments scanned | CI/CD pipeline metrics |
| Merge block enforcement | 0 CRITICAL/HIGH findings merged without review | Security dashboard audit |
| False positive rate | < 20% of total findings are suppressed | Suppression log analysis |
| Mean time to remediation (CRITICAL) | < 24 hours | Finding open-to-close timestamps |
| Mean time to remediation (HIGH) | < 5 business days | Finding open-to-close timestamps |

### Dependencies

| Dependency | Process | Nature |
|---|---|---|
| CI/CD infrastructure exists | P-033 (Automated Test Framework / CI Infrastructure) | SAST/DAST integration requires an operational CI/CD pipeline |
| Golden path templates | P-044 (Golden Path Adoption) | SAST/DAST steps should be included in golden path CI templates |
| Security Champion program | P-043 (Security Champions Training) | Champions must be trained on SAST/DAST tools to review findings |

### Traceability

```
Clarity of Intent Stage 4 (Sprint Bridge)
  → Sprint DoD, Section 5: "SAST scan clean (no new critical or high findings)"
  → Every PR must pass SAST before merge
  → Every staging deployment must pass DAST before production promotion

Clarity of Intent Stage 2 (Scope Contract)
  → Section 3, Definition of Done: "[deliverable] passes AppSec threat model review"
  → SAST/DAST CI gates are the automated enforcement of this criterion
```

---

## P-040: CVE Triage Process

### Overview

| Field | Value |
|---|---|
| **Process ID** | P-040 |
| **Process Name** | CVE Triage Process |
| **Purpose** | Security Champion reviews dependency update PRs for CVEs before approving. HIGH and CRITICAL CVEs escalate to AppSec immediately. Dependency update PRs cannot be merged with unreviewed HIGH/CRITICAL CVEs. |
| **Derived From** | Stage 0 research Category 6; Security Champions role (Engineering Team Structure Guide Section 3.7); Supply chain security best practices |
| **Risk Level** | HIGH — unreviewed CVEs in dependencies are the most common production vulnerability vector |

### Ownership

| Role | Agent | Responsibility |
|---|---|---|
| **Primary Owner** | `security-engineer` | Security Champion performs CVE triage; AppSec provides escalation review for HIGH/CRITICAL |
| **Supporting** | `software-engineer` | Engineer who opens or is assigned the dependency PR; provides codebase context on affected code paths |

### Stages/Steps

| Step | Action | Responsible | SLA |
|---|---|---|---|
| 1 | **Automated Dependency PR** — Automated tooling (Dependabot, Renovate, or equivalent) opens a dependency update PR listing changed packages and versions | Automated tooling | Continuous |
| 2 | **Security Champion CVE Review** — Security Champion reviews the CVE advisory for each updated dependency. Checks: (a) Is there a CVE associated? (b) What is the CVSS score? (c) Is the vulnerability exploitable in the context of this codebase? | Security Champion | Within 24 hours of PR open |
| 3 | **Severity Assessment and Escalation** — CVSS score assessed: CRITICAL (9.0+) or HIGH (7.0-8.9) triggers immediate AppSec escalation. MEDIUM (4.0-6.9) reviewed by Security Champion alone. LOW (0.1-3.9) logged and merged. | Security Champion | Immediate for CRITICAL/HIGH |
| 4 | **AppSec Escalation Review** — For HIGH/CRITICAL CVEs, AppSec confirms: (a) Is a public exploit available? (b) Is the affected code path in use in the codebase? (c) Are compensating controls in place? (d) What is the recommended action? | AppSec Engineer | Within 4 hours of escalation for CRITICAL; within 24 hours for HIGH |
| 5 | **Triage Decision** — Decision made from three options: (a) Merge immediately — no CVE or LOW severity only; (b) Merge after mitigation — MEDIUM severity, mitigation applied in same PR or follow-up; (c) Block until patched — HIGH/CRITICAL with exploitable path and no compensating control | Security Champion (MEDIUM/LOW) or AppSec (HIGH/CRITICAL) | Same day as review |
| 6 | **Finding Logging** — All CVE findings logged in security tracking system with: CVE ID, CVSS score, affected package, affected code paths, triage decision, reviewer name, date | Security Champion | Same day as decision |

### Inputs

| Input | Source | Format |
|---|---|---|
| Dependency update PR | Dependabot / Renovate (automated) | Pull request with dependency diff |
| CVE advisory databases | NVD (National Vulnerability Database), GHSA (GitHub Security Advisories) | Advisory records |
| SBOM (Software Bill of Materials) inventory | Platform tooling | SBOM document (CycloneDX / SPDX format) |
| Codebase dependency usage analysis | Security Champion + TL | Code path analysis showing which dependency functions are called |

### Outputs/Artifacts

| Output | Format | Stored In | Retention |
|---|---|---|---|
| CVE triage decision record | Structured record: CVE ID, severity, decision, rationale, reviewer | Security tracking system | Permanent |
| Security backlog items | Tickets for deferred remediation of MEDIUM findings | Security backlog | Until resolved |
| Escalation records | AppSec review records for HIGH/CRITICAL CVEs | Security tracking system | Permanent |
| Updated SBOM | Refreshed SBOM reflecting merged dependency changes | SBOM repository | Current version + history |

### Gate/Checkpoint

| Gate | Condition | Enforced By |
|---|---|---|
| **Per-PR Gate** | No dependency PR merged with unreviewed HIGH/CRITICAL CVEs | Security Champion review required before merge |
| **Escalation Gate** | CRITICAL (9.0+) and HIGH (7.0-8.9) CVEs must have AppSec sign-off before merge | AppSec Engineer |

**Gate Pass Criteria:**
- All HIGH/CRITICAL CVEs reviewed within 24 hours of PR open
- No unreviewed HIGH/CRITICAL CVE reaches the main branch
- AppSec has reviewed and signed off on all HIGH/CRITICAL escalations
- All findings logged in the security tracking system

**Gate Fail Action:** Dependency PR remains open and unmerged. If the CVE is CRITICAL with an active exploit and no patch is available, the Security Champion and AppSec collaborate on a compensating control (e.g., WAF rule, code-level workaround). If no mitigation is possible, P-041 (Security Exception) may be invoked with CISO approval.

### Success Criteria

| Metric | Target | Measurement Method |
|---|---|---|
| HIGH/CRITICAL CVE review SLA | 100% reviewed within 24 hours | PR open-to-review timestamp delta |
| Unreviewed CVE escape rate | 0 HIGH/CRITICAL CVEs reach main branch unreviewed | Git log audit + security tracking cross-reference |
| Triage decision documentation rate | 100% of CVE decisions logged | Security tracking system audit |
| CRITICAL CVE remediation time | < 48 hours from disclosure to merged fix | CVE disclosure date to merge date |
| SBOM currency | SBOM updated within 24 hours of dependency change | SBOM repository timestamp |

### Dependencies

| Dependency | Process | Nature |
|---|---|---|
| SAST/DAST CI catches some CVEs | P-039 (SAST/DAST CI Integration) | Automated scanning catches known patterns; manual CVE triage fills gaps for supply chain vulnerabilities not caught by SAST |
| Dependency update automation | Infrastructure prerequisite | Dependabot/Renovate must be configured for all repositories |
| Security Champions trained | P-043 (Security Champions Training) | Champions must be trained on CVE advisory interpretation and CVSS scoring |

### Traceability

```
Engineering Team Structure Guide, Section 3.7
  → Security Champion (Embedded): "CVE review for dependency updates"
  → AppSec Engineer: "dependency vulnerability management"

Clarity of Intent Stage 4 (Sprint Bridge)
  → Sprint DoD: "Code reviewed by at least one peer" (Security Champion is the
     designated peer reviewer for dependency PRs)

Process Architecture, Audit Layer
  → IC-Level Audit (P-062): "Security Champion duties: CVE review of
     dependency PRs (P-040)"
```

---

## P-041: Security Exception Process

### Overview

| Field | Value |
|---|---|
| **Process ID** | P-041 |
| **Process Name** | Security Exception Process |
| **Purpose** | Formal review and approval path for any deviation from security standards. AppSec reviews, CISO approves, Engineering Director is informed. Time-bounded exceptions only. |
| **Derived From** | Stage 0 research Category 6; CISO and AppSec Lead role responsibilities (Engineering Team Structure Guide Section 3.7) |
| **Risk Level** | HIGH — ungoverned exceptions accumulate into systemic security debt |

### Ownership

| Role | Agent | Responsibility |
|---|---|---|
| **Primary Owner** | `security-engineer` | AppSec reviews the exception request and compensating controls; CISO is the approval authority |
| **Supporting** | `engineering-manager` | Engineering Director is formally notified of all approved exceptions; tracks exception impact on team risk posture |
| **Supporting** | `product-manager` | PM documents the business justification and risk acceptance rationale |

### Stages/Steps

| Step | Action | Responsible | SLA |
|---|---|---|---|
| 1 | **Deviation Identification** — Team identifies a security standard that cannot be met immediately (e.g., SAST finding that cannot be fixed before release deadline, third-party dependency with known vulnerability and no patch, legacy system that cannot support required encryption). Team documents the specific standard being deviated from. | Any team member | Identified as soon as the deviation is discovered |
| 2 | **Business Justification** — PM documents: (a) the specific security standard being deviated from, (b) business reason the standard cannot be met on the current timeline, (c) impact of not shipping (cost of delay), (d) proposed compensating controls, (e) proposed exception duration | PM | Within 2 business days of identification |
| 3 | **AppSec Risk Review** — AppSec reviews the exception request: (a) Is the risk acceptable given compensating controls? (b) Are the compensating controls adequate? (c) Is the proposed exception duration reasonable? (d) What is the residual risk? AppSec produces a risk assessment with a recommendation (approve/reject/modify). | AppSec Engineer / AppSec Lead | Within 3 business days of submission |
| 4 | **CISO Decision** — CISO reviews the exception request and AppSec risk assessment. Approves or rejects the exception. If approved, sets a time bound (maximum: end of next quarter). CISO may impose additional compensating controls. | CISO | Within 2 business days of AppSec recommendation |
| 5 | **Engineering Director Notification** — Engineering Director for the affected area is formally notified of the approved exception. Notification includes: exception scope, compensating controls, expiry date, and remediation owner. | Security Engineer (notification) + Engineering Director (acknowledgment) | Within 1 business day of CISO decision |
| 6 | **Exception Registry Entry** — Exception recorded in the security exception registry with: exception ID, requestor, standard deviated from, justification, compensating controls, AppSec risk assessment, CISO decision, expiry date, remediation owner, remediation target date. | Security Engineer | Same day as CISO decision |
| 7 | **Quarterly Review** — All active exceptions reviewed quarterly by AppSec and CISO. Expired exceptions that have not been remediated are escalated to Engineering Director and VP of Engineering. | AppSec Lead + CISO | Quarterly cadence |

### Inputs

| Input | Source | Format |
|---|---|---|
| Security exception request | Requesting team (any team member may initiate) | Structured request form |
| Business justification | PM | Written justification with cost-of-delay analysis |
| Compensating control documentation | TL / Security Champion | Technical description of alternative controls |
| AppSec risk assessment | AppSec Engineer / Lead | Risk assessment document with recommendation |
| Triggering finding | P-039 (SAST/DAST finding) or P-038 (threat model finding) or P-040 (CVE triage) | Finding reference ID |

### Outputs/Artifacts

| Output | Format | Stored In | Retention |
|---|---|---|---|
| Security exception record (approved/rejected) | Structured record with all fields from Step 6 | Security exception registry | Permanent |
| Engineering Director notification | Formal notification with exception details | Email / notification system + exception registry | Permanent |
| AppSec risk assessment | Risk assessment document | Attached to exception record | Permanent |
| Exception registry entry with expiry | Registry row with expiry date and remediation tracking | Security exception registry | Until remediation verified |

### Gate/Checkpoint

| Gate | Condition | Enforced By |
|---|---|---|
| **CISO Approval Gate** | No security exception is valid without explicit CISO sign-off | CISO (sole approval authority) |
| **Time Bound Gate** | Every exception must have an expiry date no later than end of next quarter | CISO (sets during approval) |
| **Quarterly Expiry Review** | All expired exceptions reviewed; unremediated exceptions escalated | AppSec Lead + CISO |

**Gate Pass Criteria:**
- No exception granted without CISO approval
- All exceptions have a defined time limit and expiry date
- Compensating controls are documented and verified by AppSec
- Engineering Director has acknowledged notification
- Exception registry is updated same-day

**Gate Fail Action:** Exception request is rejected. The team must either: (a) meet the security standard before shipping, (b) revise the request with stronger compensating controls and resubmit, or (c) delay the release until the standard can be met.

### Success Criteria

| Metric | Target | Measurement Method |
|---|---|---|
| Unauthorized exceptions | 0 — no security deviations without CISO approval | Quarterly audit of exceptions vs. known deviations |
| Time-bounded exceptions | 100% of exceptions have expiry dates | Exception registry audit |
| Quarterly review completion | 100% of quarters have exception reviews completed | Review completion records |
| Exception remediation rate | > 90% of exceptions remediated before expiry | Exception registry tracking |
| Exception accumulation | Declining quarter-over-quarter | Exception registry trend analysis |

### Dependencies

| Dependency | Process | Nature |
|---|---|---|
| SAST/DAST findings trigger exceptions | P-039 (SAST/DAST CI Integration) | A SAST/DAST finding that cannot be immediately fixed is the most common trigger for an exception request |
| Threat model findings trigger exceptions | P-038 (Threat Modeling) | A CRITICAL/HIGH threat model finding with no immediate fix may require an exception |
| CVE triage triggers exceptions | P-040 (CVE Triage) | A HIGH/CRITICAL CVE with no available patch may require an exception |

### Traceability

```
Engineering Team Structure Guide, Section 3.7
  → CISO: "Security strategy and risk ownership; compliance program oversight"
  → AppSec Lead: "Secure SDLC design" (exception process is part of secure SDLC)

Clarity of Intent Stage 2 (Scope Contract)
  → Section 6, Assumptions and Risks:
    "PCI compliance review takes longer than 2 weeks" → Risk → MEDIUM
    → If PCI review reveals a standard deviation, P-041 is the formal path

Process Architecture, Bottlenecks
  → "AppSec (P-012, P-038, P-041, P-076): Single-team resource"
  → Mitigation: Security Champions distribute load; AppSec is reviewer/approver
```

---

## P-042: Compliance Review Process

### Overview

| Field | Value |
|---|---|
| **Process ID** | P-042 |
| **Process Name** | Compliance Review Process |
| **Purpose** | GRC team runs SOC 2 / ISO 27001 / GDPR compliance reviews on defined schedules and against new data-handling features. Findings tracked to closure with named owners and deadlines. |
| **Derived From** | Stage 0 research Category 6; GRC team responsibilities (Engineering Team Structure Guide Section 3.7); Regulatory requirements |
| **Risk Level** | HIGH — unaddressed compliance gaps create regulatory and contractual risk |

### Ownership

| Role | Agent | Responsibility |
|---|---|---|
| **Primary Owner** | `security-engineer` | GRC Lead owns compliance review scheduling, execution, and finding closure verification |
| **Supporting** | `engineering-manager` | Engineering Director informed of findings; ensures team capacity for remediation |
| **Supporting** | `data-engineer` | Data Engineer provides data handling context for PII/GDPR compliance assessment |
| **Supporting** | `technical-program-manager` | TPM tracks finding remediation in RAID Log (P-074) |

### Stages/Steps

| Step | Action | Responsible | SLA |
|---|---|---|---|
| 1 | **Annual Review Scheduling** — GRC Lead schedules annual compliance review cycles: SOC 2 Type II (annual), ISO 27001 surveillance/recertification (annual), GDPR assessment (annual). Review dates published to engineering leadership at start of fiscal year. | GRC Lead | Fiscal year Q1 |
| 2 | **Feature-Triggered Review** — New features touching user data, payments, PII, or data subject rights trigger a targeted compliance review. PM flags these features during Scope Contract (P-010); AppSec Scope Review (P-012) confirms compliance relevance. | GRC Lead (triggered by PM / AppSec) | Before feature reaches production |
| 3 | **Compliance Assessment Execution** — Controls mapped to compliance requirements. For each applicable requirement: (a) control exists? (b) control is effective? (c) evidence available? Assessment produces a control-to-requirement mapping matrix. | GRC Analyst / Compliance Engineer | Per review schedule |
| 4 | **Gap Identification and Assignment** — Each gap assigned: (a) named owner (specific person, not a team), (b) severity (CRITICAL / HIGH / MEDIUM / LOW), (c) remediation deadline. CRITICAL gaps: 7 days. HIGH gaps: 30 days. MEDIUM gaps: 60 days. LOW gaps: next quarterly review. | GRC Lead | Within 5 business days of assessment completion |
| 5 | **Remediation Tracking** — TPM tracks all compliance findings in the RAID Log (P-074). Status updated weekly. Findings approaching deadline trigger escalation to Engineering Director. | TPM | Weekly updates |
| 6 | **Closure Verification** — GRC Lead verifies that remediation is effective: the control now meets the compliance requirement, and evidence is collected. Only GRC Lead can close a compliance finding. | GRC Lead | Within 5 business days of remediation claimed |

### Inputs

| Input | Source | Format |
|---|---|---|
| Current control inventory | GRC team | Control-to-requirement mapping spreadsheet/tool |
| Audit scope definition | GRC Lead + External auditor (if applicable) | Scoping document |
| New feature descriptions | PM (from Scope Contract, P-010) | Scope Contract deliverables |
| Previous audit findings | GRC team | Prior audit reports and finding records |
| Data handling documentation | Data Engineer | Data flow diagrams, data classification records |

### Outputs/Artifacts

| Output | Format | Stored In | Retention |
|---|---|---|---|
| Compliance assessment report | Structured report with control-to-requirement matrix | GRC documentation repository | Permanent; required for external audit evidence |
| Finding list with owners and deadlines | Table: finding ID, requirement, gap description, owner, severity, deadline | RAID Log (P-074) + GRC tracking | Until closure verified |
| Remediation tracking records | Weekly status updates per finding | RAID Log | Permanent |
| Closure verification records | GRC sign-off per finding | GRC tracking system | Permanent; required for external audit evidence |
| External audit evidence package | Compiled evidence for SOC 2 / ISO 27001 auditors | GRC documentation repository | Per regulatory retention requirements |

### Gate/Checkpoint

| Gate | Condition | Enforced By |
|---|---|---|
| **Production Deployment Gate (Feature-Triggered)** | New features touching PII/payments require compliance clearance before production | GRC Lead |
| **Annual Review Completion Gate** | Annual compliance reviews (SOC 2, ISO 27001, GDPR) completed on schedule | GRC Lead + CISO |
| **Finding Remediation Gate** | HIGH compliance findings remediated within 30 days | TPM tracking + GRC Lead verification |

**Gate Pass Criteria:**
- Annual compliance review completed on schedule for all applicable frameworks
- All HIGH compliance findings remediated within 30 days
- No production deployment of PII-handling features without compliance clearance
- All findings have named owners and deadlines
- GRC Lead has verified closure of remediated findings

**Gate Fail Action:** For feature-triggered reviews: feature deployment to production is blocked until compliance clearance is obtained. For annual reviews: overdue reviews escalated to CISO and VP of Engineering. For unremediated findings: escalated to Engineering Director per RAID Log escalation path.

### Success Criteria

| Metric | Target | Measurement Method |
|---|---|---|
| Annual review completion | 100% on schedule | GRC calendar vs. actual completion dates |
| HIGH finding remediation SLA | 100% within 30 days | Finding open-to-close timestamps |
| CRITICAL finding remediation SLA | 100% within 7 days | Finding open-to-close timestamps |
| Feature compliance clearance | 100% of PII/payment features cleared before production | Deployment records cross-referenced with compliance clearance |
| External audit outcomes | 0 material findings in SOC 2 / ISO 27001 external audits | External audit reports |
| Finding closure verification rate | 100% of claimed remediations verified by GRC | GRC closure records |

### Dependencies

| Dependency | Process | Nature |
|---|---|---|
| AppSec Scope Review identifies compliance-relevant features | P-012 (AppSec Scope Review) | P-012 flags features that require compliance review during Scope Lock |
| RAID Log for tracking | P-074 (RAID Log Management) | Compliance findings tracked alongside other project risks and issues |
| Data handling documentation | Data engineering processes | Data flow documentation needed for GDPR and PII compliance assessment |
| Threat model findings | P-038 (Threat Modeling) | Threat model may identify compliance-relevant risks (e.g., data exposure paths) |

### Traceability

```
Clarity of Intent Stage 2 (Scope Contract)
  → Section 6, Assumptions and Risks:
    "PCI compliance review takes longer than 2 weeks" → Risk → MEDIUM
    → Mitigation: "Start review in parallel with development, not after"
  → Section 3, Definition of Done:
    "Payment tokenization: PCI compliance review passed"

Engineering Team Structure Guide, Section 3.7
  → GRC Analyst / Compliance Engineer:
    "SOC 2, ISO 27001, GDPR, HIPAA compliance program management;
     vendor security assessments; policy documentation;
     audit evidence collection; privacy program support"
```

---

## P-043: Security Champions Training Process

### Overview

| Field | Value |
|---|---|
| **Process ID** | P-043 |
| **Process Name** | Security Champions Training Process |
| **Purpose** | AppSec Lead runs quarterly training for all Security Champions covering the current threat landscape, OWASP Top 10 updates, tool usage, and recent CVE patterns relevant to the codebase. |
| **Derived From** | Stage 0 research Category 17 (Knowledge & Training); Security Champions program design (Engineering Team Structure Guide Section 3.7) |
| **Risk Level** | MEDIUM — untrained Security Champions provide false security coverage |

### Ownership

| Role | Agent | Responsibility |
|---|---|---|
| **Primary Owner** | `security-engineer` | AppSec Lead prepares and delivers quarterly training; certifies Champion proficiency |
| **Supporting** | `engineering-manager` | EMs ensure their squad's Security Champion attends; notified of non-attendees |

### Stages/Steps

| Step | Action | Responsible | SLA |
|---|---|---|---|
| 1 | **Training Content Preparation** — AppSec Lead prepares quarterly training covering: (a) current threat landscape updates, (b) OWASP Top 10 changes and relevance to the codebase, (c) recent CVE patterns affecting dependencies in use, (d) SAST/DAST tool updates and new features, (e) lessons learned from recent threat models and security incidents | AppSec Lead | 2 weeks before scheduled training |
| 2 | **Training Delivery** — All Security Champions required to attend. Training format: 2-hour session combining lecture (45 min), hands-on exercise (45 min), Q&A and discussion (30 min). Remote attendance acceptable with active participation. | AppSec Lead (delivery) + All Security Champions (attendance) | Quarterly — scheduled at start of each quarter |
| 3 | **Hands-On Exercise** — Champions review a real finding from the last quarter and trace the fix from discovery through triage, remediation, and verification. Exercise validates the Champion can use the full triage workflow (P-038, P-039, P-040). | AppSec Lead (facilitation) + Security Champions (execution) | During training session |
| 4 | **Tool Certification** — Security Champions demonstrate proficiency with current SAST/DAST tools: (a) can interpret SAST scan results, (b) can initiate and read DAST reports, (c) can submit and justify false positive suppressions, (d) can navigate CVE advisory databases (NVD, GHSA). | AppSec Lead (assessment) + Security Champions (demonstration) | During training session |
| 5 | **Completion Recording and Non-Attendee Notification** — Training completion recorded per Champion. EMs notified of any non-attendees. Non-attendees must complete a makeup session within 2 weeks or their Security Champion designation is suspended until training is completed. | AppSec Lead (recording) + EMs (follow-up) | Within 1 business day of training |

### Cadence

**Quarterly** — standing process. Training scheduled at the start of each quarter. This is a recurring governance process and does not depend on any project-specific trigger.

### Inputs

| Input | Source | Format |
|---|---|---|
| Threat intelligence feeds | Security operations / industry sources | Threat briefings, advisories |
| OWASP Top 10 updates | OWASP Foundation | OWASP publication |
| Quarterly CVE summary | AppSec team (from P-040 triage records) | Summary report of CVEs triaged in the quarter |
| SAST/DAST tool updates | Tool vendors / Platform Engineer | Release notes, new feature documentation |
| Recent threat model findings | Security Champions (from P-038) | Threat model documents from the quarter |
| Security incident lessons learned | SOC / Incident Response (if applicable) | Post-mortem summaries |

### Outputs/Artifacts

| Output | Format | Stored In | Retention |
|---|---|---|---|
| Trained Security Champion cohort | Attendance and certification records | Security Champions program records | Permanent |
| Training completion records | Per-Champion: attended (Y/N), tool certification (pass/fail), date | Security Champions program records | Permanent |
| Training materials | Slide deck, exercise materials, tool guides | Security knowledge base | Updated quarterly; all versions retained |
| Non-attendee notification | EM notification with makeup deadline | Email / notification system | Until makeup completed |

### Gate/Checkpoint

| Gate | Condition | Enforced By |
|---|---|---|
| **Quarterly Training Completion** | Training delivered on schedule with adequate attendance | AppSec Lead |
| **Attendance Threshold** | >= 80% Security Champion attendance per quarter | AppSec Lead + EMs |
| **Tool Certification** | All attending Champions pass tool proficiency check | AppSec Lead |
| **Makeup Compliance** | Non-attendees complete makeup within 2 weeks or designation suspended | AppSec Lead + EM |

**Gate Pass Criteria:**
- >= 80% Security Champion attendance per quarter
- All Security Champions proficient in current SAST/DAST tooling (certification passed)
- Training content covers all five areas (threat landscape, OWASP, CVEs, tools, lessons learned)
- All non-attendees have a scheduled makeup session within 2 weeks

**Gate Fail Action:** If attendance falls below 80%, AppSec Lead escalates to Engineering Directors. If a Champion fails tool certification, they receive 1:1 remedial training from AppSec within 1 week. If a Champion misses training and makeup deadline, their Security Champion designation is suspended and their squad operates without a Champion until training is completed — this is escalated to the EM and Director as a security coverage gap.

### Success Criteria

| Metric | Target | Measurement Method |
|---|---|---|
| Quarterly attendance rate | >= 80% of Security Champions | Attendance records |
| Tool certification pass rate | 100% of attendees | Certification records |
| Training delivery on schedule | 100% of quarters | Training calendar vs. actual delivery dates |
| Makeup session compliance | 100% of non-attendees complete makeup within 2 weeks | Makeup tracking records |
| Champion retention rate | >= 90% of Champions continue quarter-over-quarter | Champion roster comparison |

### Dependencies

| Dependency | Process | Nature |
|---|---|---|
| None | — | Quarterly standing process with no upstream process dependencies |

**Note:** P-043 is a foundational enablement process. While it has no upstream dependencies, it is a downstream dependency for P-038 (Threat Modeling), P-039 (SAST/DAST CI Integration), and P-040 (CVE Triage) — all of which rely on trained Security Champions for execution.

### Traceability

```
Engineering Team Structure Guide, Section 3.7
  → Security Champion (Embedded):
    "Threat modeling for new squad features; CVE review for dependency updates;
     security issue escalation to AppSec team; Security Champions Guild
     participation; security awareness in sprint ceremonies"
  → AppSec Lead: "developer security training programs;
     Security Champions program ownership"

Process Architecture, Implementation Sequence
  → "P-043: Security Champions Training — trigger: quarterly"
  → Listed under "Recurring Governance Processes (start immediately)"
```

---

## Cross-Process Dependency Map

The six Security & Compliance processes form an interconnected system. The following map shows how they relate to each other and to processes in other categories.

```
                    ┌─────────────────────────────┐
                    │  P-043: Security Champions   │
                    │  Training (Quarterly)         │
                    │  Enables all other processes  │
                    └──────┬──────┬──────┬─────────┘
                           │      │      │
              ┌────────────┘      │      └────────────┐
              ▼                   ▼                    ▼
   ┌──────────────────┐ ┌─────────────────┐ ┌─────────────────┐
   │  P-038: Threat   │ │ P-039: SAST/DAST│ │  P-040: CVE     │
   │  Modeling         │ │ CI Integration   │ │  Triage          │
   │  (Per Feature)    │ │ (Continuous)     │ │  (Per PR)        │
   └────────┬─────────┘ └───────┬─────────┘ └────────┬────────┘
            │                   │                     │
            │    Findings may   │   Findings may      │ CVEs may
            │    trigger ──────►│◄── trigger ─────────┘ trigger
            │                   │                        │
            ▼                   ▼                        ▼
   ┌────────────────────────────────────────────────────────────┐
   │              P-041: Security Exception Process              │
   │              (Triggered by any unresolvable finding)        │
   └────────────────────────────────────────────────────────────┘
                              │
                              │ Exceptions touching compliance
                              │ standards feed into
                              ▼
   ┌────────────────────────────────────────────────────────────┐
   │              P-042: Compliance Review Process               │
   │              (Annual + Feature-Triggered)                   │
   └────────────────────────────────────────────────────────────┘
```

### External Process Dependencies

| Security Process | Depends On | Category |
|---|---|---|
| P-038 | P-012 (AppSec Scope Review) | Category 2: Scope & Contract Management |
| P-038 | P-025 (Sprint Planning) | Category 4: Sprint & Delivery Execution |
| P-039 | P-033 (Automated Test Framework / CI Infrastructure) | Category 5: Quality Assurance & Testing |
| P-039 | P-044 (Golden Path Adoption) | Category 7: Infrastructure & Platform |
| P-042 | P-012 (AppSec Scope Review) | Category 2: Scope & Contract Management |
| P-042 | P-074 (RAID Log Management) | Category 12: Risk & Governance |

### Processes That Depend on Security & Compliance

| Downstream Process | Depends On | Nature |
|---|---|---|
| P-034 (Definition of Done Enforcement) | P-039 | DoD includes "SAST scan clean" |
| P-048 (Production Release Management) | P-039 | SAST/DAST must be clean before release |
| P-076 (Pre-Launch Risk Review / CAB) | P-039 | SAST/DAST clean is a CAB prerequisite |
| P-062 (IC-Level Audit) | P-040 | Audits IC compliance with CVE review duties |

---

## AppSec Bottleneck Mitigation

The Process Architecture identifies AppSec as a bottleneck resource (referenced across P-012, P-038, P-041, P-076). The Security & Compliance processes are designed to mitigate this through the Security Champions model:

| Activity | Primary Executor | AppSec Role |
|---|---|---|
| Threat modeling (P-038) | Security Champion | Reviewer (3-day SLA) |
| SAST/DAST finding review (P-039) | Security Champion | Approver for suppressions only |
| CVE triage (P-040) | Security Champion | Escalation reviewer for HIGH/CRITICAL only |
| Security exceptions (P-041) | PM (justification) + AppSec (review) | Risk assessor; CISO is approver |
| Compliance reviews (P-042) | GRC team | Not directly involved (separate team) |
| Champion training (P-043) | AppSec Lead | Trainer (quarterly time investment) |

This design ensures AppSec is an advisor and approver — not a gatekeeper or sole executor — consistent with the Engineering Team Structure Guide principle: "Security belongs in every squad through the Security Champions program, not just behind a central AppSec gate."

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-04-05 | spec-creator (Stage 2) | Initial specification of P-038 through P-043 |

---

## Cross-Category Dependencies

### Dependencies FROM Other Categories (Inputs)

| Source Process | Source Category | Consuming Process | Nature |
|---------------|----------------|-------------------|--------|
| P-012 (AppSec Scope Review) | Cat 2: Scope & Contract | P-038 (Threat Modeling) | AppSec availability confirmed |
| P-033 (Automated Test Framework) | Cat 5: Quality Assurance | P-039 (SAST/DAST CI Integration) | CI/CD infrastructure required |

### Dependencies TO Other Categories (Outputs)

| Providing Process | Consuming Process | Target Category | Nature |
|------------------|-------------------|-----------------|--------|
| P-039 (SAST/DAST CI Integration) | P-048 (Production Release Mgmt) | Cat 7: Infrastructure | SAST/DAST clean before release |
| P-039 (SAST/DAST CI Integration) | P-076 (Pre-Launch Risk Review) | Cat 13: Risk & Change | Security scan results for CAB |
| P-042 (Compliance Review) | P-074 (RAID Log Maintenance) | Cat 13: Risk & Change | Remediation tracked in RAID Log |

## Agent Assignments Summary

| Process | Primary Owner | Supporting Agents |
|---------|--------------|-------------------|
| P-038: Threat Modeling | security-engineer (Security Champion + AppSec) | software-engineer (TL), product-manager |
| P-039: SAST/DAST CI Integration | infra-engineer + security-engineer | software-engineer (TL) |
| P-040: CVE Triage | security-engineer (Security Champion) | software-engineer |
| P-041: Security Exception | security-engineer (AppSec + CISO) | engineering-manager, product-manager |
| P-042: Compliance Review | security-engineer (GRC Lead) | engineering-manager, data-engineer, technical-program-manager |
| P-043: Security Champions Training | security-engineer (AppSec Lead) | engineering-manager |
