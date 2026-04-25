# Specification: Multi-Layer Organizational Audit Processes (P-062 to P-069)

**Spec ID**: SPEC-CAT11-ORG-AUDIT
**Version**: 1.0
**Date**: 2026-04-05
**Category**: 11 — Organizational Hierarchy Audit (MANDATORY)
**Status**: Draft
**Derived From**:
- Process Architecture: `stage-1/2026-04-05_process-architecture.md` — Category 11 (P-062 to P-069)
- Organizational Structure: `Engineering_Team_Structure_Guide.md` — Sections 2 (Organizational Hierarchy), 3 (Roles), 10 (Complete Reporting Lines)
- Process Framework: `clarity_of_intent.md` — Four-stage process, gates, and roles

---

## Table of Contents

1. [Overview](#1-overview)
2. [Organizational Layers Covered](#2-organizational-layers-covered)
3. [Process Specifications](#3-process-specifications)
   - [P-062: Board/CEO Audit Layer (Layer 1)](#p-062-boardceo-audit-layer-process-layer-1)
   - [P-063: CTO/CPO/CISO Executive Audit Layer (Layer 2)](#p-063-ctocpociso-executive-audit-layer-process-layer-2)
   - [P-064: VP Delivery Audit Layer (Layer 3)](#p-064-vp-delivery-audit-layer-process-layer-3)
   - [P-065: Director Engineering Audit Layer (Layer 4)](#p-065-director-engineering-audit-layer-process-layer-4)
   - [P-066: Engineering Manager Audit Layer (Layer 5)](#p-066-engineering-manager-audit-layer-process-layer-5)
   - [P-067: Tech Lead/Staff Engineer Audit Layer (Layer 6)](#p-067-tech-leadstaff-engineer-audit-layer-process-layer-6)
   - [P-068: IC/Squad Engineer Audit Layer (Layer 7)](#p-068-icsquad-engineer-audit-layer-process-layer-7)
   - [P-069: Audit Finding Flow Process](#p-069-audit-finding-flow-process)
4. [Audit Finding Flow Diagram](#4-audit-finding-flow-diagram)
5. [Cross-Layer Integration](#5-cross-layer-integration)
6. [Audit Maturity Model](#6-audit-maturity-model)
7. [Appendices](#7-appendices)

---

## 1. Overview

### 1.1 Purpose of This Specification

This document specifies eight processes (P-062 through P-069) that together form a mandatory multi-layer organizational audit system. The system ensures that every layer of the engineering reporting hierarchy — from Board/CEO governance down to individual contributor self-audit — has a structured, repeatable mechanism for inspecting delivery health, technical quality, and organizational effectiveness.

The audit system serves three functions:

1. **Upward transparency** — Findings at any layer propagate to the decision-maker with authority to act, within defined SLAs.
2. **Downward accountability** — Directives from leadership flow through every layer until they reach the team that must execute the remediation.
3. **Lateral coherence** — Cross-team and cross-domain issues surface at the layer where they can be resolved, rather than being discovered late in delivery.

### 1.2 Design Principles

- **Every layer audits; no layer is exempt.** The CTO is audited by the Board; the IC self-audits against acceptance criteria. The system has no gaps.
- **Findings flow in both directions.** Escalation moves upward; remediation directives move downward. Both directions have SLAs.
- **Cadence matches decision authority.** Layers with broader authority audit less frequently (quarterly) but with greater strategic scope. Layers close to delivery audit continuously (per-PR, per-story).
- **Audit artifacts are inputs to the next layer.** Layer N produces the data that Layer N-1 reviews. This creates a natural aggregation pipeline.

### 1.3 Reporting Hierarchy Reference

The seven audit layers map directly to the organizational reporting chain defined in the Engineering Team Structure Guide (Section 10.1):

```
Layer 1: Board / CEO
Layer 2: CTO / CPO / CISO
Layer 3: VP of Engineering
Layer 4: Director of Engineering
Layer 5: Engineering Manager (EM)
Layer 6: Tech Lead (TL) / Staff Engineer (L6+)
Layer 7: Individual Contributor (IC) / Squad Engineer
```

Primary reporting chain (management track):
```
IC (L3-L5) -> EM (M4/M5) -> Director -> VP -> CTO -> CEO / Board
```

IC track parallel:
```
Staff (L6) -> Principal (L7) -> Distinguished (L8) -> Fellow (L9) -> CTO -> CEO / Board
```

---

## 2. Organizational Layers Covered

| Layer | Org Level | Span of Control | Audit Cadence | Audit Scope |
|-------|-----------|-----------------|---------------|-------------|
| 1 | Board / CEO | Entire company | Quarterly | Technology strategy, security posture, financial risk |
| 2 | CTO / CPO / CISO | 4-8 VPs + C-level peers | Monthly + Quarterly | Cross-domain DORA, OKR scoring, architecture strategy |
| 3 | VP of Engineering | 3-6 Directors per VP | Weekly + Monthly | Director delivery execution, cross-Director dependencies |
| 4 | Director of Engineering | 3-6 EMs per Director | Weekly + Per-gate | Squad delivery health, Clarity of Intent gates |
| 5 | Engineering Manager | 6-10 ICs per EM | Daily + Weekly + Per-sprint | IC performance, sprint execution, on-call burden |
| 6 | Tech Lead / Staff Engineer | 3-8 peers (influence) | Per-PR + Per-feature + Per-sprint | Technical quality, code review, ADR compliance |
| 7 | IC / Squad Engineer | Own work | Per-story + Per-sprint | Self-audit against acceptance criteria and DoD |

---

## 3. Process Specifications

---

### P-062: Board/CEO Audit Layer Process (Layer 1)

#### 1. Process ID and Name

**ID**: P-062
**Name**: Board/CEO Audit Layer Process

#### 2. Purpose

Quarterly Technology Business Review where the CTO presents technology delivery health, security posture summary, and major architectural decisions to the Board/CEO. This is the highest governance checkpoint in the engineering organization. Without it, the Board/CEO lacks visibility into technology risk, which prevents effective corporate governance over technology investments and strategic direction.

#### 3. Organizational Layer

**Layer 1: Board / CEO** — the apex of the reporting hierarchy. The Board and CEO have fiduciary and strategic oversight responsibility for all technology decisions that affect company viability.

#### 4. Primary Owner Agent

**engineering-manager** (CTO scope) — The CTO, operating at the highest level of the engineering-manager agent archetype, authors and presents the technology delivery summary.

#### 5. Supporting Agents

- **security-engineer** (CISO scope) — CISO authors and presents the quarterly security risk report, including security posture, incident summary, and compliance status.
- **staff-principal-engineer** (Distinguished Engineer scope) — Distinguished Engineers provide technical context for major architectural decisions presented to the Board.

#### 6. Audit Focus

| Focus Area | What Is Examined |
|------------|-----------------|
| Technology strategy alignment | Are technology investments aligned with company strategy and OKRs? |
| Security risk | CISO quarterly report: incident count, severity distribution, compliance posture, unresolved vulnerabilities |
| Financial risk from technology | Engineering spend vs. budget; ROI on major technology initiatives |
| Major architectural decisions | Significant architecture choices made in the quarter; rationale and trade-offs |
| Engineering OKR performance | Aggregate OKR scoring (0.0-1.0) across all engineering domains |

#### 7. Audit Cadence

**Quarterly** — Aligned with corporate quarterly business review cycle.

#### 8. Inputs

| Input | Source | Format |
|-------|--------|--------|
| CTO quarterly technology delivery health summary | CTO, aggregated from VP reports (P-063) | Executive summary document (2-4 pages) |
| CISO quarterly security risk report | CISO / security-engineer agent | Security posture report with risk matrix |
| Major architectural decisions log | CARB (Cloud Architecture Review Board) outputs | Decision register with rationale |
| Engineering OKR scoring | All engineering domains, aggregated by CTO | OKR scorecard (0.0-1.0 per objective) |
| Financial summary | Engineering finance / EM agent | Budget vs. actual; headcount utilization |

#### 9. Outputs / Artifacts

| Output | Description | Consumer |
|--------|-------------|----------|
| Board/CEO acknowledgment or directive | Written record of Board response: acknowledged, questions raised, or strategic directives issued | CTO |
| CTO action items with deadlines | Specific actions the Board requires from the CTO | CTO, VP layer (via P-063) |
| Technology risk register update | Updated register reflecting Board-level risk decisions | CTO, CISO, VP layer |

#### 10. Gate / Checkpoint

**Pass Criteria**:
- Quarterly review held on schedule (no deferrals beyond 2 weeks)
- All material security risks and architectural decisions presented — no filtering or omission
- Board/CEO can ask specific questions and receive specific, data-backed answers
- OKR scores for all engineering domains are presented with variance explanations
- CISO report covers all SEV-1 and SEV-2 incidents from the quarter

**Fail Criteria**:
- Review not held within the quarter
- Material security incidents omitted from the report
- OKR scores presented without supporting data
- Board questions cannot be answered with specifics

#### 11. Escalation Triggers

| Trigger | Threshold | Action |
|---------|-----------|--------|
| Material security incident | Any SEV-1 with data exposure or business continuity impact | Immediate Board notification outside quarterly cycle |
| Technology decision affecting company viability | Strategic technology pivot or major vendor change | Emergency Board session |
| Persistent engineering underperformance | Engineering OKR scoring <0.4 for two consecutive quarters | Board intervention; CTO performance review |

#### 12. Downward Remediation

Board/CEO directives flow downward through the following path:
1. Board issues directive to CTO
2. CTO translates directive into technology strategy adjustments (P-006: Technology Vision Alignment)
3. CTO communicates adjusted strategy to VPs in the Layer 2 audit (P-063)
4. VPs cascade to Directors (P-064), who cascade to EMs (P-065), and so on

**SLA**: CTO must communicate Board directives to VPs within 1 business day of the Board meeting.

#### 13. Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Quarterly review held on time | Calendar compliance | 100% of quarters |
| Board satisfaction with technology transparency | Board feedback (qualitative) | No surprise findings between quarterly reviews |
| Directive completion rate | CTO action items closed by next quarter | >90% |
| Security posture visibility | Board can articulate top 3 technology risks | Yes, consistently |

#### 14. Dependencies

| Dependency | Process | Nature |
|------------|---------|--------|
| Layer 2 audit data | P-063 | Layer 2 provides aggregated VP-domain data that feeds the CTO quarterly summary |
| RAID Log | P-074 | RAID Log entries at HIGH/CRITICAL level surface in the Board report |
| OKR scoring | P-072 (OKR Review) | Quarterly OKR scores are a primary input |

#### 15. Traceability

| Source Document | Section |
|-----------------|---------|
| Process Architecture | Category 11, P-062: Board/CEO Audit Layer Process |
| Engineering Team Structure Guide | Section 3.1 — CTO role: "Reports to: CEO / Board of Directors" |
| Engineering Team Structure Guide | Section 2.1 — Organizational hierarchy: Board/CEO at apex |

---

### P-063: CTO/CPO/CISO Executive Audit Layer Process (Layer 2)

#### 1. Process ID and Name

**ID**: P-063
**Name**: CTO/CPO/CISO Executive Audit Layer Process

#### 2. Purpose

Monthly executive audit where VPs present domain-level OKR progress, DORA metrics, cross-domain dependency status, and security program effectiveness to CTO/CPO/CISO. This layer aggregates VP-level data into an executive view, identifies systemic cross-domain issues, and provides the data pipeline for the quarterly Board review (P-062).

#### 3. Organizational Layer

**Layer 2: CTO / CPO / CISO** — The C-level technology leadership team. CTO manages 4-8 VPs plus C-level peers (CISO, CPO). CISO reports to CEO (recommended) with dotted-line to CTO.

#### 4. Primary Owner Agent

**engineering-manager** (CTO/VP scope) — CTO chairs the executive audit; VPs present their domain reports.

#### 5. Supporting Agents

- **security-engineer** (CISO scope) — CISO presents security program effectiveness, vulnerability trends, and compliance status.
- **technical-program-manager** — TPM provides cross-domain dependency summary and program-level RAID log status.

#### 6. Audit Focus

| Focus Area | What Is Examined |
|------------|-----------------|
| Cross-domain technology standards compliance | Are all VP domains adhering to architectural standards and technology mandates? |
| Organization-wide DORA metrics | Deployment frequency, lead time, change failure rate, MTTR — aggregated across all VP domains |
| Architectural strategy alignment | CARB outputs; ADR compliance across domains |
| Security program effectiveness | Vulnerability remediation rates, security training completion, incident trends |
| Cross-domain dependency health | Dependencies between VP domains that are blocked or at risk |

#### 7. Audit Cadence

- **Monthly**: Delivery health review (DORA, dependency status, delivery risks)
- **Quarterly**: OKR scoring (0.0-1.0) and strategic alignment review

#### 8. Inputs

| Input | Source | Format |
|-------|--------|--------|
| VP-level delivery reports per domain | Each VP, from Director rollups (P-064) | Monthly delivery summary |
| CARB outputs and architectural decisions | CARB / staff-principal-engineer | Decision register |
| Quarterly OKR scoring | All engineering domains | OKR scorecard |
| DORA metrics aggregated by VP domain | Engineering metrics platform | Dashboard / report |
| Cross-domain RAID log summary | TPM (P-074) | RAID summary document |
| Security program report | CISO / security-engineer | Monthly security status |

#### 9. Outputs / Artifacts

| Output | Description | Consumer |
|--------|-------------|----------|
| CTO directives on standards compliance | Written directives addressing non-compliance | VPs, Directors (via P-064) |
| Budget and headcount approvals or deferrals | Decisions on resource allocation requests | VPs, HR |
| Cross-domain dependency resolution decisions | CTO-level resolution for VP-to-VP dependency conflicts | VPs, TPM |
| Architectural mandates | Mandated technology choices for specific problem areas | All engineering teams |
| Quarterly Board summary (input to P-062) | Aggregated executive summary for Board review | Board / CEO |

#### 10. Gate / Checkpoint

**Pass Criteria**:
- Monthly review held on schedule
- All VP domains represented with data-backed delivery reports
- DORA metrics presented with trend analysis (not just point-in-time)
- Cross-domain dependencies have named owners and resolution timelines
- Security program report covers vulnerability remediation SLA compliance

**Fail Criteria**:
- VP domain reports missing or based on anecdotal data
- DORA metrics unavailable or not aggregated at domain level
- Cross-domain dependency conflicts unresolved for >1 month without escalation plan

#### 11. Escalation Triggers

| Trigger | Threshold | Action |
|---------|-----------|--------|
| Systemic delivery failures | >2 VP domains with sprint completion <60% for 2 consecutive sprints | CTO intervention; Board notification via P-062 |
| Persistent architectural drift | Standards non-compliance persisting across domains for >2 months | Architectural mandate issued; Staff/Principal Engineers assigned |
| Critical security gaps | CISO identifies gaps affecting regulatory compliance or data integrity | Immediate escalation to Board if material; CTO action plan within 48 hours |

#### 12. Downward Remediation

1. CTO issues directives at the monthly executive audit
2. VPs receive directives and translate them into domain-specific actions
3. VPs communicate to Directors in the Layer 3 weekly audit (P-064)
4. Directors cascade to EMs in weekly syncs (P-065)

**SLA**: VP must communicate CTO directives to Directors within 1 business day.

#### 13. Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Monthly review cadence maintained | Calendar compliance | 12/12 months per year |
| Cross-domain issues resolved at this layer | Issues resolved without Board escalation | >85% |
| DORA metric trends improving | Quarter-over-quarter DORA improvement | Positive trend across all 4 metrics |
| Directive completion rate | CTO directives closed by next monthly review | >80% |

#### 14. Dependencies

| Dependency | Process | Nature |
|------------|---------|--------|
| VP delivery data | P-064 | Layer 3 weekly audits produce the data that Layer 2 aggregates monthly |
| RAID Log | P-074 | Cross-domain RAID items surface in the executive audit |
| CARB decisions | P-075 (Architecture Review) | Architectural decisions feed into standards compliance review |
| Security program data | P-043 (Security Champions Training), P-040 (CVE triage) | Security training and vulnerability data feed CISO report |

#### 15. Traceability

| Source Document | Section |
|-----------------|---------|
| Process Architecture | Category 11, P-063: CTO/CPO/CISO Executive Audit Layer Process |
| Engineering Team Structure Guide | Section 2.2 — CTO span: "4-8 VPs plus C-level peers" |
| Engineering Team Structure Guide | Section 3.1 — CTO role: "Sets cross-organization technology standards" |

---

### P-064: VP Delivery Audit Layer Process (Layer 3)

#### 1. Process ID and Name

**ID**: P-064
**Name**: VP Delivery Audit Layer Process

#### 2. Purpose

Weekly VP-level audit where Directors present RAID log summaries, sprint goal completion rates, and scope change decisions. The VP reviews cross-Director dependency resolution and headcount vs. delivery capacity. This is the primary mechanism for cross-Director issue resolution and the bridge between strategic (monthly/quarterly) governance and tactical (weekly/sprint) execution.

#### 3. Organizational Layer

**Layer 3: VP of Engineering** — Each VP manages 3-6 Directors of Engineering. The VP layer is the highest level with weekly operational cadence.

#### 4. Primary Owner Agent

**engineering-manager** (VP of Engineering scope)

#### 5. Supporting Agents

- **technical-program-manager** — TPM provides RAID log summaries and cross-Director program status.

#### 6. Audit Focus

| Focus Area | What Is Examined |
|------------|-----------------|
| Director-level delivery execution quality | Sprint goal completion rates across all Directors' areas |
| Cross-Director dependency resolution | Dependencies between Directors' domains that are blocked or at risk |
| Headcount and budget alignment | Actual capacity vs. planned capacity; hiring pipeline status |
| Engineering standards compliance | Adherence to VP-level technology mandates and process standards |
| Scope change governance | Scope changes approved at Director level — appropriateness and impact |

#### 7. Audit Cadence

- **Weekly**: Delivery sync (30-60 minutes) — sprint health, blockers, dependency status
- **Monthly**: Standards review — deeper dive into engineering standards compliance and DORA trends

#### 8. Inputs

| Input | Source | Format |
|-------|--------|--------|
| Director weekly delivery status | Each Director, from EM rollups (P-065) | Weekly status report |
| DORA metric dashboards per Director domain | Engineering metrics platform | Dashboard |
| RAID log summaries | TPM (P-074) | Weekly RAID summary |
| Scope change decisions made at Director level | Directors, via Scope Change Requests (P-014) | Scope change log |
| Headcount utilization data | HR / EM systems | Utilization report |

#### 9. Outputs / Artifacts

| Output | Description | Consumer |
|--------|-------------|----------|
| VP resolution decisions for cross-Director conflicts | Written decisions resolving Director-to-Director dependency disputes | Directors, TPM |
| Headcount allocation adjustments | Rebalancing decisions across Director domains | Directors, HR |
| Engineering standards directives | VP-level mandates on process or technology standards | Directors, EMs |
| Escalation decisions (VP to CTO) | Items requiring CTO authority, packaged with context | CTO (via P-063) |
| Monthly VP delivery report | Aggregated monthly report for CTO executive audit | CTO (input to P-063) |

#### 10. Gate / Checkpoint

**Pass Criteria**:
- Weekly sync held on schedule
- All Directors present with data-backed status (not anecdotal)
- Cross-Director dependencies have current status and resolution owners
- Scope changes reviewed and approved/rejected with documented rationale
- RAID log items at HIGH severity have active resolution plans

**Fail Criteria**:
- Directors present without sprint completion data
- Cross-Director dependencies unresolved for >2 consecutive weekly syncs
- Scope changes made without VP awareness

#### 11. Escalation Triggers

| Trigger | Threshold | Action |
|---------|-----------|--------|
| Persistent delivery failure | Sprint goal completion <60% for 2 consecutive sprints in any Director's area | VP intervention; coaching or staffing adjustment |
| Unresolved cross-Director dependencies | HIGH-priority dependency unresolved for >2 weeks | VP-mandated resolution with deadline |
| Budget overruns | >10% over budget in any Director domain | VP review; CTO notification |
| Team health signals | Attrition spikes (>2 departures in a quarter in a single Director area) or burnout indicators | VP + HR intervention |

#### 12. Downward Remediation

1. VP issues directives at the weekly delivery sync
2. Directors receive directives and translate them into EM-level actions
3. Directors communicate to EMs in the Layer 4 weekly EM sync (P-065)
4. EMs cascade to TLs and ICs

**SLA**: Director must communicate VP directives to EMs within 1 business day of the weekly sync.

#### 13. Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Weekly sync cadence maintained | Calendar compliance | >95% of weeks |
| Cross-Director conflicts resolved at this layer | Conflicts resolved without CTO escalation | >80% |
| Sprint goal completion across Director domains | Aggregate sprint goal completion | >75% |
| Headcount utilization | Actual utilization vs. plan | Within 10% variance |

#### 14. Dependencies

| Dependency | Process | Nature |
|------------|---------|--------|
| Director delivery data | P-065 | Layer 4 weekly EM syncs produce data that Layer 3 aggregates |
| RAID Log | P-074 | RAID items at Director+ level surface in VP review |
| Scope change process | P-014 | Scope changes requiring VP approval follow the change control process |

#### 15. Traceability

| Source Document | Section |
|-----------------|---------|
| Process Architecture | Category 11, P-064: VP Delivery Audit Layer Process |
| Engineering Team Structure Guide | Section 3.1 — VP of Engineering: "Manages 3-6 Directors" |
| Engineering Team Structure Guide | Section 2.2 — VP span of control |

---

### P-065: Director Engineering Audit Layer Process (Layer 4)

#### 1. Process ID and Name

**ID**: P-065
**Name**: Director Engineering Audit Layer Process

#### 2. Purpose

Per-gate project audit combined with weekly EM sync. The Director reviews and approves/rejects Intent Review, Scope Lock, and Dependency Acceptance gate decisions from the Clarity of Intent process. The weekly EM sync covers squad DORA trends, blocked items, and upcoming sprint risk. This is the primary quality gate for all Clarity of Intent stage gates and the key bridge between people management and delivery governance.

#### 3. Organizational Layer

**Layer 4: Director of Engineering** — Each Director manages 3-6 Engineering Managers. The Director layer has both weekly operational cadence and event-driven gate review responsibilities.

#### 4. Primary Owner Agent

**engineering-manager** (Director of Engineering scope)

#### 5. Supporting Agents

- **product-manager** — PM presents gate artifacts (Intent Brief, Scope Contract) for Director review.
- **technical-program-manager** — TPM presents program health and dependency status at weekly sync.

#### 6. Audit Focus

| Focus Area | What Is Examined |
|------------|-----------------|
| Squad-level delivery health | DORA metrics, sprint goal completion, and blocker resolution across 3-6 managed EMs |
| Clarity of Intent gate quality | Quality of Intent Brief (Stage 1), Scope Contract (Stage 2), Dependency Charter (Stage 3) |
| Cross-team technical dispute resolution | Conflicts between squads that EMs and TLs could not resolve |
| DORA trends per squad | Deployment frequency, lead time, change failure rate, MTTR per squad |
| Incident post-mortem action items | Completion of post-mortem actions; recurrence of similar incidents |

#### 7. Audit Cadence

- **Weekly**: EM sync (30-60 minutes) — each EM presents squad status
- **Per-gate**: Triggered by each Clarity of Intent gate (Intent Review, Scope Lock, Dependency Acceptance) — the Director is a mandatory reviewer

#### 8. Inputs

| Input | Source | Format |
|-------|--------|--------|
| EM weekly reports | Each EM (P-066) | Squad DORA metrics, blocked items, sprint risk |
| Scope Contract and Dependency Charter | PM + TL, for active projects | Gate artifacts per Clarity of Intent |
| Sprint goal completion history per squad | EM reports / metrics platform | Sprint-over-sprint trend data |
| Incident history and post-mortem action items | SRE / incident management system | Incident log and action tracker |
| Gate artifacts requiring Director approval | PM, TL | Intent Brief, Scope Contract, Dependency Charter |

#### 9. Outputs / Artifacts

| Output | Description | Consumer |
|--------|-------------|----------|
| Gate decisions | PASS or FAIL with documented criteria for each Clarity of Intent gate | PM, TL, EM, project team |
| EM coaching directives | Performance feedback and coaching actions for EMs | Individual EMs |
| Cross-team conflict resolutions | Director-level decisions on squad-to-squad disputes | EMs, TLs |
| Leveling and hiring approvals | Decisions on promotions, leveling, and headcount requests | EMs, HR |
| Escalation items for VP audit | Issues exceeding Director authority, packaged with context | VP (input to P-064) |

#### 10. Gate / Checkpoint

**Pass Criteria (Weekly Sync)**:
- All EMs present with data-backed squad status
- Blocked items have resolution plans with owners and deadlines
- DORA trends reviewed with action items for declining metrics
- Post-mortem action items tracked and progressing

**Pass Criteria (Clarity of Intent Gates)**:
- Intent Brief answers all five questions with specifics (Stage 1 — per `clarity_of_intent.md`)
- Scope Contract has deliverables with owners and Definitions of Done (Stage 2)
- Dependency Charter has all dependencies with owners and commitment dates (Stage 3)
- Gate artifact quality sufficient for downstream stages to proceed

**Fail Criteria**:
- Gate artifact missing required sections
- EMs present without sprint completion data
- Post-mortem actions overdue by >1 sprint without explanation

#### 11. Escalation Triggers

| Trigger | Threshold | Action |
|---------|-----------|--------|
| Persistent squad delivery failure | Sprint goal completion <70% for any squad for 2 consecutive sprints | EM coaching; Director intervention in squad process |
| Unresolved cross-team conflicts | Conflict unresolved after TL and Staff Engineer attempts | Director mandates resolution |
| Scope changes requiring Director approval | Scope change expanding boundary or affecting timeline by >1 sprint | Director decides per change control process (P-014) |
| Security exceptions | Exception to security standards requested | Director escalates to CISO |

#### 12. Downward Remediation

1. Director issues directives at the weekly EM sync or immediately for gate failures
2. EMs receive directives and translate them into squad-level actions
3. EMs communicate to TLs and ICs via sprint planning and daily standups

**SLA**: EM must communicate Director directives within 1 business day of weekly sync; immediately for gate failures.

#### 13. Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Weekly EM sync cadence | Calendar compliance | >95% of weeks |
| Clarity of Intent gate quality | Gate pass rate on first submission | >70% |
| Cross-team conflict resolution at this layer | Conflicts resolved without VP escalation | >85% |
| Squad DORA trends | Improving or stable DORA across managed squads | No squad declining on >2 DORA metrics for >2 sprints |

#### 14. Dependencies

| Dependency | Process | Nature |
|------------|---------|--------|
| EM sprint data | P-066 | Layer 5 per-sprint audits produce the data Layer 4 reviews weekly |
| Clarity of Intent gate artifacts | P-004 (Intent Review), P-013 (Scope Lock), P-019 (Dependency Acceptance) | Gate artifacts must be produced before Director review |
| RAID Log | P-074 | Director reviews RAID Log in weekly EM sync |

#### 15. Traceability

| Source Document | Section |
|-----------------|---------|
| Process Architecture | Category 11, P-065: Director Engineering Audit Layer Process |
| Engineering Team Structure Guide | Section 3.1 — Director: "Manages 3-6 Engineering Managers" |
| Clarity of Intent | Gate: Intent Review, Gate: Scope Lock, Gate: Dependency Acceptance — Director as mandatory reviewer |
| Clarity of Intent | Roles and Responsibilities Summary — Director row |

---

### P-066: Engineering Manager Audit Layer Process (Layer 5)

#### 1. Process ID and Name

**ID**: P-066
**Name**: Engineering Manager Audit Layer Process

#### 2. Purpose

Per-sprint EM audit covering sprint goal completion, Definition of Done (DoD) compliance per story, on-call burden, and retrospective action item closure. The EM validates the intent trace in Sprint Kickoff Briefs (ensuring every sprint connects to project intent) and escalates DoD failures. This is the closest organizational oversight to the actual delivery work and the primary people management audit layer.

#### 3. Organizational Layer

**Layer 5: Engineering Manager** — Each EM manages 6-10 ICs (never more than 10, per the two-pizza rule). The EM owns people management, delivery outcomes, and process compliance at the squad level.

#### 4. Primary Owner Agent

**engineering-manager**

#### 5. Supporting Agents

- **product-manager** — PM validates sprint goal and intent trace; confirms acceptance criteria are clear.
- **sre** — SRE provides on-call burden data (alert frequency, pages per shift, toil metrics).

#### 6. Audit Focus

| Focus Area | What Is Examined |
|------------|-----------------|
| Individual IC performance and growth | Career development progress, skill gaps, engagement signals (via 1:1s) |
| Sprint execution quality | Sprint goal completion rate, DoD compliance per story, blocker resolution time |
| Team DORA metrics | Deployment frequency, lead time, change failure rate, MTTR for the squad |
| On-call burden | Target <2 alerts/shift for SREs; toil ratio tracking |
| Retrospective action item completion | Are retro actions being completed, or accumulating without closure? |
| Intent trace validation | Does the Sprint Kickoff Brief connect the sprint goal to a Scope Contract deliverable and the project intent? |

#### 7. Audit Cadence

- **Daily**: Standup observation — blocker surfacing, at-risk work identification
- **Weekly**: 1:1s with each IC (30-60 minutes each) — career development, performance, wellbeing
- **Per-sprint**: Retrospective and sprint review outcomes; DoD compliance audit

#### 8. Inputs

| Input | Source | Format |
|-------|--------|--------|
| Daily standup signals | Squad daily standup | Verbal / chat blockers and at-risk items |
| 1:1 conversations | Individual ICs | Private notes (career, performance, wellbeing) |
| DORA dashboards | Engineering metrics platform | Squad-level DORA dashboard |
| Sprint review outcomes | Sprint review ceremony | Demo results, stakeholder feedback |
| Retrospective action item tracking | Retro tool / tracking board | Action item list with owners and deadlines |
| Incident data (on-call burden) | Incident management system / SRE | Alert frequency, MTTA, MTTR per shift |
| Sprint Kickoff Brief | EM + TL (P-025: Sprint Bridge) | 1-page brief per squad per sprint |

#### 9. Outputs / Artifacts

| Output | Description | Consumer |
|--------|-------------|----------|
| 1:1 notes and career development commitments | Private record of IC development plans | EM (private), IC |
| Sprint retrospective action items | Documented improvement actions with owners | Squad, Director |
| EM escalation items for Director sync | Issues requiring Director authority | Director (input to P-065) |
| Performance review inputs | Biannual performance data compiled from sprint observations and 1:1s | Director, HR |
| On-call burden reports | Alert frequency and toil data when thresholds exceeded | Director, SRE Lead |
| Sprint completion report | Sprint goal achieved/not achieved, DoD compliance summary | Director (input to P-065) |

#### 10. Gate / Checkpoint

**Pass Criteria (Per-Sprint)**:
- Sprint goal clearly stated and connected to Scope Contract deliverable (intent trace present)
- >80% of stories meet DoD criteria
- All blockers from standup resolved within 24 hours or escalated
- Retrospective held; action items from previous retro reviewed for completion
- 1:1s held with all ICs during the sprint

**Fail Criteria**:
- Sprint goal not stated or disconnected from project intent
- DoD compliance <60% for the sprint
- Retrospective action items accumulating without closure for >2 sprints
- 1:1s missed for >2 weeks for any IC

#### 11. Escalation Triggers

| Trigger | Threshold | Action |
|---------|-----------|--------|
| Repeated missed sprint goals | Same squad, 2 consecutive sprints | EM investigates root cause; Director informed in weekly sync |
| Engineer blocked >24 hours | Blocker not resolved within 1 working day | EM intervenes directly; escalates to TL or Director if technical |
| On-call burden excessive | >50% of SRE shift spent on alerts (toil) | Toil reduction sprint triggered (P-057) |
| Team health signals | Disengagement, interpersonal conflict, or burnout indicators | EM + HR consultation; Director informed |
| DoD failures | Repeated DoD non-compliance by same IC | EM coaching; performance discussion |

#### 12. Downward Remediation

1. EM communicates sprint priorities, capacity allocation, and process expectations to TL and ICs
2. EM provides direct feedback in 1:1s on individual performance and growth areas
3. EM ensures Sprint Kickoff Brief is understood by all squad members before sprint starts

**SLA**: Within same sprint; immediately for sprint-blocking directives.

#### 13. Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Sprint goal completion rate | Sprints where goal fully achieved / total sprints | >80% |
| DoD compliance rate | Stories meeting all DoD criteria / total stories | >90% |
| Blocker resolution time | Median time from blocker raised to resolved | <24 hours |
| 1:1 cadence | 1:1s held per IC per sprint | 100% |
| Retro action item closure rate | Actions closed within 2 sprints | >75% |
| On-call burden | Alerts per SRE shift | <2 per shift |

#### 14. Dependencies

| Dependency | Process | Nature |
|------------|---------|--------|
| TL/IC work products | P-067, P-068 | Layers 6 and 7 produce the work that Layer 5 audits for DoD compliance |
| Sprint Bridge | P-025 | Sprint Kickoff Brief is the primary artifact EM validates |
| On-call data | P-057 (Toil Reduction) | On-call burden data feeds EM audit; excessive toil triggers P-057 |
| RAID Log | P-074 | EM contributes squad-level RAID items |

#### 15. Traceability

| Source Document | Section |
|-----------------|---------|
| Process Architecture | Category 11, P-066: Engineering Manager Audit Layer Process |
| Engineering Team Structure Guide | Section 3.1 — EM: "Manages 6-10 ICs (never more than 10)" |
| Clarity of Intent | Stage 4: Sprint Bridge — EM owns Sprint Kickoff Brief |
| Clarity of Intent | Sprint Readiness gate — EM runs sprint planning |

---

### P-067: Tech Lead/Staff Engineer Audit Layer Process (Layer 6)

#### 1. Process ID and Name

**ID**: P-067
**Name**: Tech Lead/Staff Engineer Audit Layer Process

#### 2. Purpose

Per-PR and per-feature technical audit by the Tech Lead and Staff Engineer. The TL reviews every PR against code review standards and DoD technical criteria. The Staff Engineer reviews cross-team Architecture Decision Records (ADRs) for standards compliance. This is the technical quality gatekeeping layer — technical quality at the PR level determines the quality of everything above it in the audit hierarchy.

#### 3. Organizational Layer

**Layer 6: Tech Lead (IC5-IC6) / Staff Engineer (L6+)** — TLs influence 3-8 peers through technical leadership within a squad. Staff Engineers influence multiple teams through architecture and standards. Neither has direct reports; both lead by influence.

#### 4. Primary Owner Agent

- **software-engineer** (Tech Lead scope) — TL owns squad-level code review and technical direction.
- **staff-principal-engineer** (Staff/Principal scope) — Staff Engineer owns cross-team ADR review and architectural standards compliance.

#### 5. Supporting Agents

- **security-engineer** (Security Champion scope) — Security Champions embedded in squads perform security-specific PR review for sensitive code paths.

#### 6. Audit Focus

| Focus Area | What Is Examined |
|------------|-----------------|
| Technical quality of work products | Code correctness, design quality, test coverage, maintainability |
| Code review standards compliance | Adherence to team and org code review standards |
| Architecture decisions | ADR completeness and compliance with architectural principles |
| DoD technical criteria | SAST scan clean, automated tests passing, coverage thresholds met |
| Cross-team architectural consistency | Staff Engineer ensures decisions across teams align with org-wide standards |

#### 7. Audit Cadence

- **Per-PR**: Code review — every PR requires TL or senior IC review before merge
- **Per-feature**: Architecture review before implementation begins (design review)
- **Per-sprint**: Standards compliance check at end of sprint

#### 8. Inputs

| Input | Source | Format |
|-------|--------|--------|
| PR code diffs and CI gate outputs | Version control system (GitHub/GitLab) | PR diff, CI pipeline results |
| ADR documents | Engineers proposing significant technical decisions | ADR document (templated) |
| Dependency Charter technical items | TPM + TL (P-019) | Technical dependency list |
| Sprint DoD technical criteria | EM + TL defined per team | DoD checklist |
| SAST/DAST scan results | Security tooling pipeline | Automated scan reports |

#### 9. Outputs / Artifacts

| Output | Description | Consumer |
|--------|-------------|----------|
| PR approval or rejection with specific feedback | Written code review feedback on every PR | IC author |
| ADR review comments and approval | Documented review of architectural decisions | IC author, EM, Director |
| Architecture compliance report per sprint | Summary of architectural drift or compliance issues | EM, Director |
| Architectural drift escalation | Escalation when drift is detected (TL -> Staff -> Director) | Staff Engineer, Director |
| Technical blocker escalation to EM | Technical issues that prevent story completion | EM |

#### 10. Gate / Checkpoint

**Pass Criteria (Per-PR)**:
- Code meets review standards (readability, correctness, test coverage)
- SAST scan clean — no new critical or high findings
- Automated tests written and passing in CI
- ADR documented for significant technical decisions

**Pass Criteria (Per-Sprint)**:
- All merged PRs reviewed by TL or designated senior IC
- No architectural drift identified without an ADR
- Coverage thresholds maintained or improved

**Fail Criteria**:
- PR merged without review (bypass of review gate)
- ADR missing for a significant technical decision
- SAST critical findings merged into main branch

#### 11. Escalation Triggers

| Trigger | Threshold | Action |
|---------|-----------|--------|
| Missing ADR | Significant technical decision without documented ADR | TL requires ADR before merge |
| Architectural drift | Pattern of decisions diverging from established architecture | TL escalates to Staff Engineer; Staff escalates to Director |
| Security finding in code review | Vulnerability identified during review | Security Champion + AppSec notified immediately |
| Technical blocker | Blocker persisting >24 hours | Escalate to EM for resolution |
| Repeated quality issues | Same IC producing PRs below standards for >2 sprints | TL raises with EM for coaching conversation |

#### 12. Downward Remediation

1. TL provides specific, actionable code review feedback on every PR
2. TL provides architectural direction and design guidance to ICs
3. Staff Engineer provides cross-team standards guidance and mentorship
4. TL coaches ICs on code quality improvements based on recurring patterns

**SLA**: PR review feedback within 1 business day; architectural drift escalation within the same sprint.

#### 13. Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| PR review coverage | PRs reviewed before merge / total merged PRs | 100% |
| PR review turnaround | Median time from PR opened to first review | <4 hours during business hours |
| ADR compliance | Significant decisions with ADRs / total significant decisions | 100% |
| SAST clean merge rate | PRs merged with clean SAST / total merged PRs | >98% |
| Architectural drift incidents | Drift findings per sprint | Declining or zero |

#### 14. Dependencies

| Dependency | Process | Nature |
|------------|---------|--------|
| IC work products | P-068 | Layer 7 produces PRs that Layer 6 reviews |
| CI/CD pipeline | P-032-P-037 (QA processes) | CI gates provide automated quality signals that TL incorporates |
| Architecture standards | P-075 (CARB) | CARB decisions define the standards TL/Staff enforce |
| Security scanning | P-040 (CVE triage) | SAST/DAST results feed into PR review |

#### 15. Traceability

| Source Document | Section |
|-----------------|---------|
| Process Architecture | Category 11, P-067: Tech Lead/Staff Engineer Audit Layer Process |
| Engineering Team Structure Guide | Section 3.1 — TL: "Influences 3-8 peers through technical leadership" |
| Engineering Team Structure Guide | Section 3.2 — Staff Engineer (L6): "Cross-team technical initiatives" |
| Clarity of Intent | Stage 4: Sprint DoD — "Code reviewed by at least one peer; SAST scan clean" |

---

### P-068: IC/Squad Engineer Audit Layer Process (Layer 7)

#### 1. Process ID and Name

**ID**: P-068
**Name**: IC/Squad Engineer Audit Layer Process

#### 2. Purpose

Per-story self-audit by the individual contributor against acceptance criteria and the Definition of Done. Security Champions (ICs with a dual responsibility) audit dependency updates for CVEs. Engineers escalate blockers within the same day. This is the earliest quality check in the entire audit hierarchy — failures at this layer propagate to PR review (Layer 6) and beyond.

#### 3. Organizational Layer

**Layer 7: Individual Contributor (IC) / Squad Engineer** — L3 (Junior) through L5 (Senior) engineers who execute the delivery work. Each IC reports to an EM and receives technical guidance from the TL.

#### 4. Primary Owner Agent

**software-engineer** (Individual Contributor scope)

#### 5. Supporting Agents

- **security-engineer** (Security Champion scope) — Security Champions in the IC layer perform CVE triage on dependency PRs (per P-040).

#### 6. Audit Focus

| Focus Area | What Is Examined |
|------------|-----------------|
| Own work against acceptance criteria | Does the completed story meet the acceptance criteria from the Sprint Kickoff Brief? |
| DoD checklist self-verification | Has the IC verified all DoD items before requesting PR review? |
| Security Champion duties | CVE review of dependency PRs (for designated Security Champions) |
| Peer code review participation quality | Quality and timeliness of code reviews given to peers |

#### 7. Audit Cadence

- **Per-story**: DoD self-check before requesting PR review — this is the highest-frequency audit in the system
- **Per-sprint**: Retrospective contribution — IC reflects on what went well, what did not, and what to improve
- **Per-dependency-PR**: Security Champion CVE review (for Security Champions only)

#### 8. Inputs

| Input | Source | Format |
|-------|--------|--------|
| Story acceptance criteria | PM (via Sprint Kickoff Brief, P-025) | Acceptance criteria in "Given/When/Then" or checklist format |
| Sprint DoD checklist | EM + TL defined per team | Checklist (code reviewed, tests passing, SAST clean, docs updated, etc.) |
| PR review feedback from peers | Peer ICs and TL | Written code review comments |
| CVE advisories for dependency PRs | Security tooling / advisory feeds | CVE reports (for Security Champions) |

#### 9. Outputs / Artifacts

| Output | Description | Consumer |
|--------|-------------|----------|
| Self-verified DoD compliance per story | IC has checked all DoD items before requesting review | TL (via PR), EM |
| PR review feedback (given and received) | Quality feedback provided to peers; feedback received and acted on | Peers, TL |
| CVE triage decisions | Security Champion assessment of dependency CVEs (for Security Champions) | AppSec, EM |
| Escalation items to EM | Blockers, unclear acceptance criteria, unachievable DoD items | EM (same-day SLA) |

#### 10. Gate / Checkpoint

**Pass Criteria (Per-Story)**:
- All acceptance criteria verified by the IC before requesting PR review
- DoD checklist completed: code reviewed by peer, automated tests written and passing, SAST clean, documentation updated, acceptance criteria verified
- PR description references the story and links to acceptance criteria

**Fail Criteria**:
- PR submitted without DoD self-check
- Acceptance criteria not verified before marking story complete
- Blockers not escalated within the same day

#### 11. Escalation Triggers

| Trigger | Threshold | Action |
|---------|-----------|--------|
| Acceptance criteria unclear | IC cannot determine what "done" means | Escalate to PM same day |
| DoD criteria not achievable | Available tools, time, or knowledge insufficient for DoD | Escalate to EM same day |
| Security issue discovered during implementation | Vulnerability found while coding | Escalate to Security Champion + AppSec immediately |
| CVE found in dependency PR | HIGH or CRITICAL CVE in a dependency update | Security Champion escalates to AppSec immediately (P-040) |
| Blocker of any kind | IC cannot make progress | Escalate to EM via standup (P-026) or direct message; same-day SLA |

#### 12. Downward Remediation

This is the bottom layer — there is no "downward" flow. Instead, the IC receives:
- **Acceptance criteria** from PM (via Sprint Kickoff Brief)
- **Architectural direction** from TL (via design reviews and code review feedback)
- **DoD standards** from EM + TL (via sprint DoD checklist)
- **Process expectations** from EM (via 1:1s and sprint planning)

#### 13. Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| DoD self-check compliance | Stories with completed DoD checklist before PR / total stories | >95% |
| Acceptance criteria verification | Stories verified against criteria before marking done | 100% |
| Blocker escalation timeliness | Blockers escalated within same day | 100% |
| PR review participation | Code reviews completed within 4 hours of request | >80% |
| CVE triage timeliness (Security Champions) | HIGH/CRITICAL CVEs triaged within 24 hours | 100% |

#### 14. Dependencies

| Dependency | Process | Nature |
|------------|---------|--------|
| Clear acceptance criteria | P-025 (Sprint Bridge) | Sprint Kickoff Brief must have testable acceptance criteria for IC to self-audit against |
| DoD definition | P-025 (Sprint Bridge), team agreement | DoD must be documented and visible |
| CI/CD pipeline | P-032-P-037 (QA processes) | Automated tests and SAST must be available for IC to verify DoD |
| Security tooling | P-040 (CVE triage) | CVE advisory feeds must be available for Security Champions |

#### 15. Traceability

| Source Document | Section |
|-----------------|---------|
| Process Architecture | Category 11, P-068: IC/Squad Engineer Audit Layer Process |
| Engineering Team Structure Guide | Section 3.2 — IC ladder: L3 through L5 |
| Clarity of Intent | Stage 4: Sprint Bridge — Stories and Acceptance Criteria; Definition of Done |
| Clarity of Intent | Sprint Readiness gate — "Every engineer can answer: What am I building, why does it matter, and how will I know it's done?" |

---

### P-069: Audit Finding Flow Process

#### 1. Process ID and Name

**ID**: P-069
**Name**: Audit Finding Flow Process

#### 2. Purpose

Defines the structured mechanism by which audit findings from any layer propagate upward (escalation) and downward (remediation directives). This is the connective tissue of the entire audit system. Without it, findings at lower layers never reach the decision-maker with authority to act, and directives from upper layers never reach the team that must execute the remediation.

#### 3. Organizational Layer

**All layers** — This process spans the entire hierarchy. It is not owned by a single layer but operates across all seven layers.

#### 4. Primary Owner Agent

**technical-program-manager** — The TPM tracks all findings in the RAID Log (P-074) and monitors SLA compliance for both upward escalations and downward directives.

#### 5. Supporting Agents

**All agents** — Every layer participates in this flow. Each agent is responsible for:
- Generating findings at their layer
- Escalating findings upward per the defined SLAs
- Receiving and acting on directives from above per the defined SLAs
- Acknowledging receipt of directives

#### 6. Audit Focus

| Focus Area | What Is Examined |
|------------|-----------------|
| Upward escalation SLA compliance | Are findings reaching the right decision-maker within the defined time window? |
| Downward directive SLA compliance | Are directives reaching the executing team within the defined time window? |
| Finding acknowledgment | Has every finding been acknowledged by its recipient? |
| Finding resolution | Has every finding been resolved or assigned a resolution plan with deadline? |
| RAID Log accuracy | Does the RAID Log reflect the current state of all active findings? |

#### 7. Audit Cadence

- **Continuous**: Findings are generated and escalated at the cadence of their source layer
- **Weekly**: RAID Log reviewed by Director in weekly EM sync (P-065)
- **Quarterly**: Audit finding SLA compliance reviewed in quarterly process health review (P-071)

#### 8. Inputs

| Input | Source | Format |
|-------|--------|--------|
| Audit findings from Layers 1-7 | P-062 through P-068 | Finding records with severity, owner, and timestamp |
| RAID Log entries | P-074 (RAID Log Maintenance) | RAID Log |
| Escalation SLA definitions | This process specification (P-069) | SLA table (see below) |

#### 9. Outputs / Artifacts

| Output | Description | Consumer |
|--------|-------------|----------|
| Escalation records with timestamps | Documented record of every upward escalation, including finding, timestamp, and receiving layer | TPM, Director, VP, CTO |
| Directive records with acknowledgment | Documented record of every downward directive, including acknowledgment timestamp | TPM, EM, TL, IC |
| RAID Log updates | All findings reflected in RAID Log with owners, deadlines, and current status | All layers |
| SLA compliance report | Quarterly report on escalation and directive SLA adherence | Director, VP, CTO (via P-071) |

#### 10. Gate / Checkpoint

**Pass Criteria**:
- No finding sits unacknowledged beyond its SLA
- All upward escalations have a decision outcome recorded within the SLA
- RAID Log reflects all audit findings with owners and deadlines
- Quarterly SLA compliance >90%

**Fail Criteria**:
- Finding unacknowledged beyond SLA with no explanation
- Decision outcome missing for escalated finding
- RAID Log not updated for >1 week

#### 11. Escalation Triggers

This process IS the escalation mechanism. The triggers are the SLA breaches themselves:

| SLA Breach | Action |
|------------|--------|
| Finding unacknowledged beyond SLA | TPM flags to the next layer up |
| Directive not communicated within SLA | TPM flags to the directive issuer |
| RAID Log not updated | TPM flags to the responsible layer owner |
| Quarterly SLA compliance <80% | Process health review (P-071) triggers process improvement action |

#### 12. Downward Remediation

The finding flow process defines remediation SLAs for all downward directives:

**Upward Escalation SLAs**:

| From | To | SLA |
|------|----|-----|
| IC (Layer 7) | EM (Layer 5) | Same day for blockers; next working day for quality issues |
| EM (Layer 5) | Director (Layer 4) | Same day for gate failures or HIGH blocked dependencies; weekly for trend data |
| Director (Layer 4) | VP (Layer 3) | Same sprint for critical delivery issues; monthly for trend reporting |
| VP (Layer 3) | CTO (Layer 2) | Immediate for SEV-1 delivery or security incidents; quarterly for systematic issues |
| CTO (Layer 2) | Board (Layer 1) | Immediate for material technology risk; quarterly for systematic governance |

**Downward Directive SLAs**:

| From | To | SLA |
|------|----|-----|
| Board/CTO (Layer 1/2) | VP (Layer 3) | Within 1 business day of receiving directive |
| VP (Layer 3) | Director (Layer 4) | Within 1 business day of receiving directive |
| Director (Layer 4) | EM (Layer 5) | Within 1 business day of weekly sync; immediately for gate failures |
| EM (Layer 5) | TL/IC (Layer 6/7) | Within same sprint; immediately for sprint-blocking directives |

#### 13. Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Upward escalation SLA compliance | Escalations within SLA / total escalations | >90% |
| Downward directive SLA compliance | Directives communicated within SLA / total directives | >90% |
| Finding acknowledgment rate | Findings acknowledged within SLA / total findings | >95% |
| RAID Log currency | RAID Log updated within 1 week of finding | 100% |
| Finding resolution rate | Findings resolved within their defined deadline | >80% |

#### 14. Dependencies

| Dependency | Process | Nature |
|------------|---------|--------|
| All audit layers | P-062 through P-068 | Every audit layer generates findings that feed this process |
| RAID Log Maintenance | P-074 | RAID Log is the primary tracking mechanism for findings |
| Quarterly Process Health Review | P-071 | SLA compliance is reviewed quarterly as part of process health |

#### 15. Traceability

| Source Document | Section |
|-----------------|---------|
| Process Architecture | Category 11, P-069: Audit Finding Flow Process |
| Process Architecture | P-062 through P-068: "Finding Flow — Upward" and "Finding Flow — Downward" sections |
| Clarity of Intent | Change Control section — Scope Change Request flow as a specific type of finding flow |

---

## 4. Audit Finding Flow Diagram

### 4.1 Complete Upward Escalation and Downward Remediation Flow

```
                    UPWARD ESCALATION                          DOWNWARD REMEDIATION
                    (Findings rise)                            (Directives descend)

    ┌─────────────────────────────────────────────────────────────────────────────┐
    │                                                                             │
    │  LAYER 1: Board / CEO                                                       │
    │  ┌─────────────────────────────────────┐                                    │
    │  │ P-062: Quarterly Technology Review   │                                   │
    │  │ Receives: CTO summary, CISO report   │                                   │
    │  │ Issues: Strategic directives          │                                   │
    │  └──────────────┬──────────────────────┘                                    │
    │                 │                                                            │
    │     ▲ Immediate: material risk      │ Within 1 business day                 │
    │     │ Quarterly: systematic          ▼                                       │
    │                 │                                                            │
    │  LAYER 2: CTO / CPO / CISO                                                  │
    │  ┌─────────────────────────────────────┐                                    │
    │  │ P-063: Monthly Executive Audit       │                                   │
    │  │ Receives: VP domain reports, DORA    │                                   │
    │  │ Issues: Standards mandates, budgets   │                                   │
    │  └──────────────┬──────────────────────┘                                    │
    │                 │                                                            │
    │     ▲ Immediate: SEV-1             │ Within 1 business day                  │
    │     │ Quarterly: systematic         ▼                                        │
    │                 │                                                            │
    │  LAYER 3: VP of Engineering                                                  │
    │  ┌─────────────────────────────────────┐                                    │
    │  │ P-064: Weekly VP Delivery Audit      │                                   │
    │  │ Receives: Director RAID, sprint data │                                   │
    │  │ Issues: Cross-Director resolutions    │                                   │
    │  └──────────────┬──────────────────────┘                                    │
    │                 │                                                            │
    │     ▲ Same sprint: critical        │ Within 1 business day                  │
    │     │ Monthly: trends               ▼                                        │
    │                 │                                                            │
    │  LAYER 4: Director of Engineering                                            │
    │  ┌─────────────────────────────────────┐                                    │
    │  │ P-065: Weekly EM Sync + Gate Review  │                                   │
    │  │ Receives: EM reports, gate artifacts  │                                   │
    │  │ Issues: Gate decisions, coaching       │                                   │
    │  └──────────────┬──────────────────────┘                                    │
    │                 │                                                            │
    │     ▲ Same day: gate failures      │ Within 1 biz day / immediately         │
    │     │ Weekly: trends                ▼                                        │
    │                 │                                                            │
    │  LAYER 5: Engineering Manager                                                │
    │  ┌─────────────────────────────────────┐                                    │
    │  │ P-066: Per-Sprint EM Audit           │                                   │
    │  │ Receives: IC performance, DORA, DoD  │                                   │
    │  │ Issues: Sprint priorities, coaching    │                                   │
    │  └──────────────┬──────────────────────┘                                    │
    │                 │                                                            │
    │     ▲ Sprint completion <70%       │ Within same sprint / immediately        │
    │     │ Personnel issues              ▼                                        │
    │                 │                                                            │
    │  LAYER 6: Tech Lead / Staff Engineer                                         │
    │  ┌─────────────────────────────────────┐                                    │
    │  │ P-067: Per-PR / Per-Feature Audit    │                                   │
    │  │ Receives: PRs, ADRs, CI results      │                                   │
    │  │ Issues: Review feedback, arch direction│                                   │
    │  └──────────────┬──────────────────────┘                                    │
    │                 │                                                            │
    │     ▲ Same day: blockers           │ Per-PR feedback                         │
    │     │ Next day: quality issues       ▼                                       │
    │                 │                                                            │
    │  LAYER 7: IC / Squad Engineer                                                │
    │  ┌─────────────────────────────────────┐                                    │
    │  │ P-068: Per-Story Self-Audit          │                                   │
    │  │ Performs: DoD self-check, CVE triage  │                                   │
    │  │ Escalates: Blockers, unclear criteria │                                   │
    │  └─────────────────────────────────────┘                                    │
    │                                                                             │
    └─────────────────────────────────────────────────────────────────────────────┘

    P-069 (Audit Finding Flow Process) governs all arrows in this diagram.
    TPM tracks all findings in RAID Log (P-074).
```

### 4.2 Lateral (Cross-Team) Finding Flow

```
    Squad A (IC)                     Squad B (IC)
        │                                │
        ▼                                ▼
    TL A (Layer 6)  ──── conflict ──── TL B (Layer 6)
        │                                │
        ▼   (unresolved)                 ▼
    Staff Engineer ─────────────────── Staff Engineer
        │                                │
        ▼   (unresolved)                 ▼
    EM A (Layer 5)  ──── escalate ──── EM B (Layer 5)
        │                                │
        └──────────┬─────────────────────┘
                   ▼
           Director (Layer 4)
           Resolves cross-team conflicts
                   │
                   ▼  (if cross-Director)
           VP (Layer 3)
           Resolves cross-Director conflicts
```

---

## 5. Cross-Layer Integration

### 5.1 Data Aggregation Pipeline

Each audit layer produces data that the layer above consumes. This creates a natural aggregation pipeline where detailed operational data at the bottom is progressively summarized into strategic insights at the top.

| Layer | Produces | Consumed By | Aggregation |
|-------|----------|-------------|-------------|
| Layer 7 (IC) | DoD compliance per story, blocker reports | Layer 6 (TL) via PR review; Layer 5 (EM) via standup | Per-story detail |
| Layer 6 (TL) | PR review outcomes, ADR compliance, architecture reports | Layer 5 (EM) via sprint review | Per-PR / per-feature detail |
| Layer 5 (EM) | Sprint goal completion, DORA metrics, on-call burden | Layer 4 (Director) via weekly sync | Per-sprint aggregation per squad |
| Layer 4 (Director) | Gate decisions, cross-team status, DORA trends | Layer 3 (VP) via weekly sync | Weekly aggregation across 3-6 squads |
| Layer 3 (VP) | Delivery health, cross-Director dependency status | Layer 2 (CTO) via monthly review | Monthly aggregation across 3-6 Directors |
| Layer 2 (CTO) | Cross-domain health, OKR scores, security posture | Layer 1 (Board) via quarterly review | Quarterly aggregation across all domains |

### 5.2 Cadence Alignment

The cadences of all layers are designed to align so that each layer has fresh data when it conducts its audit.

```
Timeline (1 Quarter = ~6 Sprints)
───────────────────────────────────────────────────────────────────────

Layer 7 (IC):     ●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●  (continuous)
Layer 6 (TL):     ●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●  (per-PR)
Layer 5 (EM):     ■─────■─────■─────■─────■─────■─────■              (daily/weekly/per-sprint)
Layer 4 (Dir):    ▲─────▲─────▲─────▲─────▲─────▲─────▲──G──G──G    (weekly + per-gate)
Layer 3 (VP):     ▲─────▲─────▲─────▲─────▲─────▲─────▲     ◆       (weekly + monthly)
Layer 2 (CTO):                ◆                 ◆           ◆       (monthly)
Layer 1 (Board):                                            ★       (quarterly)

Legend: ● = continuous  ■ = per-sprint  ▲ = weekly  ◆ = monthly  ★ = quarterly  G = gate
```

### 5.3 Clarity of Intent Integration

The audit layers directly support the four-stage Clarity of Intent process:

| Clarity of Intent Stage | Gate | Gate Reviewer (Audit Layer) | Supporting Audit |
|------------------------|------|----------------------------|-----------------|
| Stage 1: Intent Frame | Intent Review | Director (Layer 4, P-065) | VP informed (Layer 3) |
| Stage 2: Scope Contract | Scope Lock | Director (Layer 4, P-065) | Staff Engineer reviews architecture (Layer 6, P-067) |
| Stage 3: Dependency Map | Dependency Acceptance | Director (Layer 4, P-065) | TPM coordinates (P-069 finding flow) |
| Stage 4: Sprint Bridge | Sprint Readiness | EM (Layer 5, P-066) | TL validates technical feasibility (Layer 6, P-067) |

### 5.4 Agent Coverage Matrix

Every agent in the `.claude/agents/` directory participates in at least one audit layer:

| Agent | Primary Layer | Supporting Layers | Role in Audit System |
|-------|--------------|-------------------|---------------------|
| engineering-manager | Layers 1-5 (CTO through EM) | All | Primary owner of organizational audit at every management layer |
| software-engineer | Layer 6 (TL), Layer 7 (IC) | — | Technical quality gatekeeping and self-audit |
| staff-principal-engineer | Layer 1, Layer 6 | Layer 2 | Cross-team architecture audit; Board-level technical context |
| security-engineer | Layer 1 (CISO), Layer 6, Layer 7 | Layer 2 | Security posture audit at all layers; Security Champion duties |
| product-manager | Layer 4 (gate artifacts), Layer 5 | — | Gate artifact quality; intent trace validation |
| technical-program-manager | P-069 (finding flow) | Layers 2-4 | RAID Log tracking; cross-domain dependency summary |
| sre | — | Layer 5 | On-call burden data for EM audit |
| qa-engineer | — | Layers 6-7 | Quality gate data feeds into TL and IC audits |
| cloud-engineer | — | Layer 6 | Cloud architecture compliance in PR review |
| data-engineer | — | Layer 6 | Data pipeline architecture compliance |
| ml-engineer | — | Layer 6 | ML system architecture compliance |
| platform-engineer | — | Layers 5-6 | CI/CD pipeline health; infrastructure audit data |
| technical-writer | — | Layer 5 | Documentation DoD compliance |

---

## 6. Audit Maturity Model

### 6.1 Overview

The audit maturity model defines five levels of process maturity for the multi-layer audit system. Organizations assess their current level and target the next level as a continuous improvement goal.

### 6.2 Maturity Levels

#### Level 1: Ad Hoc

**Characteristics**:
- Audits happen informally and inconsistently
- No defined cadences; reviews triggered only by crises
- Findings communicated verbally with no tracking
- No RAID Log or formal escalation mechanism
- Individual managers audit their teams differently with no standardization

**Indicators**:
- Surprise findings at Board level that should have been caught earlier
- Cross-team conflicts discovered during development, not during dependency mapping
- No data-backed delivery health reports at any layer
- "We did not know" is a common response to escalated issues

**Exit Criteria to Level 2**:
- Define audit cadences for all 7 layers
- Establish a RAID Log
- Document escalation paths

---

#### Level 2: Defined

**Characteristics**:
- Audit cadences defined for all 7 layers (P-062 through P-068)
- RAID Log established and maintained (P-074)
- Escalation paths documented with SLAs (P-069)
- Audit artifacts exist but quality is inconsistent
- Some layers skip audits during high-pressure periods

**Indicators**:
- Cadences exist on paper but compliance is 60-80%
- RAID Log exists but is not always current
- Escalation SLAs defined but sometimes breached without consequence
- Board quarterly review happens but with incomplete data

**Exit Criteria to Level 3**:
- Achieve >90% cadence compliance across all layers
- RAID Log updated within 1 week of every finding
- Escalation SLA compliance >80%

---

#### Level 3: Consistent

**Characteristics**:
- All audit layers operate at their defined cadence with >90% compliance
- RAID Log is current and accurate
- Escalation and directive SLAs consistently met (>90%)
- Audit artifacts are standardized and data-backed
- Findings consistently reach the right decision-maker within SLA

**Indicators**:
- Board quarterly review contains no surprises — all material issues already known
- Cross-team conflicts resolved at the appropriate layer without excessive escalation
- Sprint goal completion >75% across the organization
- DORA metrics visible and reviewed at every layer

**Exit Criteria to Level 4**:
- Quarterly process health review (P-071) operational
- Audit findings lead to measurable process improvements
- Leading indicators (not just lagging) used at Layers 3-5

---

#### Level 4: Measured

**Characteristics**:
- Quarterly process health review (P-071) measures audit system effectiveness
- Leading indicators supplement lagging indicators at all layers
- Audit findings systematically produce process improvements
- Cross-layer data flows are automated (dashboards, not manual reports)
- SLA compliance tracked with trend analysis

**Indicators**:
- Process health metrics (per `clarity_of_intent.md` "How to Know the Process Is Working") tracked quarterly
- Scope changes per project declining quarter-over-quarter
- Late dependency discovery <1 per project
- Sprint goal completion >80%
- Intent alignment: random engineer can explain project purpose

**Exit Criteria to Level 5**:
- Audit findings produce systemic improvements (not just local fixes)
- Predictive analytics on delivery risk
- Audit process itself continuously improves based on retrospective data

---

#### Level 5: Optimizing

**Characteristics**:
- Audit system is self-improving: each quarterly health review produces process adjustments
- Predictive analytics identify delivery risks before they materialize
- Audit overhead is minimal because quality is built in at every layer
- Cross-layer integration is seamless; data flows automatically from Layer 7 to Layer 1
- Organizational trust is high; audits are valued as enablers, not overhead

**Indicators**:
- Escalation rate declining (issues resolved at the lowest possible layer)
- Gate pass rate on first submission >85%
- DORA metrics in "Elite" category (per DORA research)
- Audit ceremonies are efficient (time-boxed, data-driven, action-oriented)
- New team members onboard into the audit system within their first sprint

---

### 6.3 Maturity Assessment Checklist

| Dimension | L1 | L2 | L3 | L4 | L5 |
|-----------|----|----|----|----|-----|
| Cadence compliance (all layers) | <50% | 60-80% | >90% | >95% | >98% |
| RAID Log currency | No RAID Log | Exists, inconsistent | Updated weekly | Updated in real-time | Automated |
| Escalation SLA compliance | No SLAs | Defined, 60-80% met | >90% met | >95% met, trended | >98%, predictive |
| Audit artifact quality | None | Inconsistent | Standardized | Data-backed, templated | Automated generation |
| Cross-layer data flow | Manual, ad hoc | Manual, structured | Semi-automated | Automated dashboards | Fully integrated |
| Process improvement loop | None | Reactive | Annual | Quarterly (P-071) | Continuous |
| Board/CEO confidence | Low | Moderate | Good | High | Full trust |

---

## 7. Appendices

### Appendix A: Process Summary Table

| Process ID | Name | Layer | Primary Agent | Cadence | Risk Level |
|------------|------|-------|--------------|---------|------------|
| P-062 | Board/CEO Audit Layer | 1 | engineering-manager (CTO) | Quarterly | HIGH |
| P-063 | CTO/CPO/CISO Executive Audit Layer | 2 | engineering-manager (CTO/VP) | Monthly + Quarterly | HIGH |
| P-064 | VP Delivery Audit Layer | 3 | engineering-manager (VP) | Weekly + Monthly | HIGH |
| P-065 | Director Engineering Audit Layer | 4 | engineering-manager (Director) | Weekly + Per-gate | HIGH |
| P-066 | Engineering Manager Audit Layer | 5 | engineering-manager | Daily + Weekly + Per-sprint | HIGH |
| P-067 | Tech Lead/Staff Engineer Audit Layer | 6 | software-engineer + staff-principal-engineer | Per-PR + Per-feature + Per-sprint | HIGH |
| P-068 | IC/Squad Engineer Audit Layer | 7 | software-engineer | Per-story + Per-sprint | MEDIUM |
| P-069 | Audit Finding Flow | All | technical-program-manager | Continuous | HIGH |

### Appendix B: Complete SLA Reference

**Upward Escalation SLAs**:

| From Layer | To Layer | Blocker/Critical SLA | Trend/Systematic SLA |
|------------|----------|---------------------|---------------------|
| 7 (IC) | 5 (EM) | Same day | Next working day |
| 5 (EM) | 4 (Director) | Same day | Weekly sync |
| 4 (Director) | 3 (VP) | Same sprint | Monthly report |
| 3 (VP) | 2 (CTO) | Immediate (SEV-1) | Quarterly |
| 2 (CTO) | 1 (Board) | Immediate (material risk) | Quarterly |

**Downward Directive SLAs**:

| From Layer | To Layer | Standard SLA | Urgent SLA |
|------------|----------|-------------|------------|
| 1 (Board) | 2 (CTO) | Within 1 business day | Immediate |
| 2 (CTO) | 3 (VP) | Within 1 business day | Immediate |
| 3 (VP) | 4 (Director) | Within 1 business day | Immediate |
| 4 (Director) | 5 (EM) | Within 1 business day | Immediately for gate failures |
| 5 (EM) | 6/7 (TL/IC) | Within same sprint | Immediately for sprint-blockers |

### Appendix C: Traceability Matrix

| Process | Process Architecture Section | Eng Team Structure Section | Clarity of Intent Section |
|---------|----------------------------|---------------------------|--------------------------|
| P-062 | Cat 11, P-062 | 2.1 (hierarchy), 3.1 (CTO role) | — |
| P-063 | Cat 11, P-063 | 2.2 (CTO span), 3.1 (CTO standards) | — |
| P-064 | Cat 11, P-064 | 3.1 (VP role), 2.2 (VP span) | — |
| P-065 | Cat 11, P-065 | 3.1 (Director role) | Gate reviews (Intent, Scope Lock, Dependency) |
| P-066 | Cat 11, P-066 | 3.1 (EM role, 6-10 ICs) | Stage 4: Sprint Bridge; Sprint Readiness gate |
| P-067 | Cat 11, P-067 | 3.1 (TL role), 3.2 (Staff L6) | Stage 4: DoD (code review, SAST) |
| P-068 | Cat 11, P-068 | 3.2 (IC ladder L3-L5) | Stage 4: Stories and Acceptance Criteria; DoD |
| P-069 | Cat 11, P-069 | 10.1 (reporting chain) | Change Control (finding flow as scope change) |

---

**End of Specification**

---

## Cross-Category Dependencies

### Dependencies FROM Other Categories (Inputs)

| Source Process | Source Category | Consuming Process | Nature |
|---------------|----------------|-------------------|--------|
| P-074 (RAID Log Maintenance) | Cat 13: Risk & Change | P-065 (Director Audit) | Director reviews RAID Log in weekly sync |
| P-074 (RAID Log Maintenance) | Cat 13: Risk & Change | P-069 (Audit Finding Flow) | Findings tracked in RAID Log |

### Dependencies TO Other Categories (Outputs)

| Providing Process | Consuming Process | Target Category | Nature |
|------------------|-------------------|-----------------|--------|
| P-062 (Board/CEO Audit) | P-006 (Technology Vision Alignment) | Cat 1: Intent & Strategic Alignment | Board directives adjust CTO technology vision |
| P-065 (Director Audit) | P-004 (Intent Review Gate) | Cat 1: Intent & Strategic Alignment | Director chairs all Clarity of Intent gates |
| P-065 (Director Audit) | P-013 (Scope Lock Gate) | Cat 2: Scope & Contract | Director reviews scope at gate |
| P-069 (Audit Finding Flow) | P-074 (RAID Log Maintenance) | Cat 13: Risk & Change | All audit findings tracked in RAID Log |

### Internal Dependency Graph

```
Layer 1 (P-062) <-- aggregates -- Layer 2 (P-063)
Layer 2 (P-063) <-- aggregates -- Layer 3 (P-064)
Layer 3 (P-064) <-- aggregates -- Layer 4 (P-065)
Layer 4 (P-065) <-- aggregates -- Layer 5 (P-066)
Layer 5 (P-066) <-- reviews ---- Layer 6 (P-067)
Layer 6 (P-067) <-- reviews ---- Layer 7 (P-068)

P-069 (Audit Finding Flow) <-- consumes findings from ALL layers (P-062 through P-068)
```

## Agent Assignments Summary

| Process | Primary Owner | Supporting Agents |
|---------|--------------|-------------------|
| P-062: Board/CEO Audit Layer (Layer 1) | engineering-manager (CTO) | security-engineer (CISO), staff-principal-engineer |
| P-063: CTO/CPO/CISO Executive Audit (Layer 2) | engineering-manager (CTO/VP) | security-engineer, technical-program-manager |
| P-064: VP Delivery Audit (Layer 3) | engineering-manager (VP) | technical-program-manager |
| P-065: Director Engineering Audit (Layer 4) | engineering-manager (Director) | product-manager, technical-program-manager |
| P-066: EM Audit Layer (Layer 5) | engineering-manager | product-manager, sre |
| P-067: TL/Staff Engineer Audit (Layer 6) | software-engineer (TL) + staff-principal-engineer | security-engineer |
| P-068: IC/Squad Engineer Audit (Layer 7) | software-engineer (ICs) | security-engineer (Security Champions) |
| P-069: Audit Finding Flow | technical-program-manager | All agents |
