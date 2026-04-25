# Technical Specification: Communication & Alignment Processes

**Category**: 14 — Communication & Alignment
**Processes**: P-078, P-079, P-080, P-081
**Date**: 2026-04-05
**Stage**: 2 — Detailed Process Specification
**Derived From**: Stage 1 Process Architecture (Category 14); Clarity of Intent; Engineering Team Structure Guide

---

## Table of Contents

1. [P-078: OKR Cascade Communication Process](#p-078-okr-cascade-communication-process)
2. [P-079: Stakeholder Update Cadence Process](#p-079-stakeholder-update-cadence-process)
3. [P-080: Guild Standards Communication Process](#p-080-guild-standards-communication-process)
4. [P-081: DORA Metrics Review and Sharing Process](#p-081-dora-metrics-review-and-sharing-process)

---

## P-078: OKR Cascade Communication Process

### Process Identity

| Field | Value |
|-------|-------|
| **Process ID** | P-078 |
| **Process Name** | OKR Cascade Communication Process |
| **Category** | 14 — Communication & Alignment |
| **Risk Level** | HIGH |

### Purpose

Ensure company OKRs cascade visibly and traceably from CEO through CTO, VP, Director, EM, and PM down to Sprint Goals. Every engineer must be able to trace their current sprint goal to a company OKR within three degrees of separation. The cascade is documented at each organizational level — never assumed or inferred.

### Derived From

- Stage 0 research Category 16: organizational communication patterns
- Engineering Team Structure Guide Section 11.4: OKR cascade design (Company OKRs → Engineering OKRs → Team/Squad OKRs → Sprint Goals → User Stories/Tasks)
- Engineering Team Structure Guide Section 8.7: PM's perspective on OKR cascade
- Clarity of Intent Stage 1 (Intent Frame): strategic context referencing real OKRs
- Clarity of Intent Stage 4 (Sprint Bridge): Intent Trace connecting sprint goal to project intent and scope deliverable

### Primary Owner Agent

**engineering-manager** — VPs and Directors own the engineering OKR cascade at their respective organizational levels. EMs own the squad-level cascade and sprint goal connection.

### Supporting Agents

| Agent | Responsibility |
|-------|---------------|
| **product-manager** | Translates squad OKRs into sprint goals; ensures sprint goal traces to Key Results; validates alignment in Sprint Kickoff Briefs |
| **technical-program-manager** | Maintains program-level OKR alignment across multiple squads and tribes; flags misalignment across programs |

### Stages/Steps

#### Stage 1: Company OKR Publication

- **Actor**: CEO / CPO / Leadership Team
- **Action**: Publish company OKRs for the quarter
- **Timing**: Quarter start (Q-day)
- **Output**: Company OKR document published to organization-wide channel
- **Constraint**: OKRs must be outcomes, not outputs (per Engineering Team Structure Guide: "Reduce P95 API latency from 800ms to 200ms" is a Key Result; "Refactor the API layer" is a task)

#### Stage 2: Engineering OKR Derivation

- **Actor**: CTO + VPs
- **Action**: Derive engineering OKRs from company OKRs; each engineering OKR explicitly references the company OKR it supports
- **Timing**: Within 2 working days of company OKR publication
- **Output**: Engineering OKR document with traceability column linking each engineering objective to its parent company OKR
- **Constraint**: 3-5 Key Results per Objective; scoring target of 0.7 at quarter end (stretch goals)

#### Stage 3: Domain OKR Derivation

- **Actor**: VPs
- **Action**: Derive domain-level OKRs from engineering OKRs
- **Timing**: Within 3 working days of engineering OKR publication
- **Output**: Domain OKR document per VP area with parent engineering OKR reference

#### Stage 4: Area OKR Derivation

- **Actor**: Directors
- **Action**: Derive area OKRs from domain OKRs
- **Timing**: Within 5 working days of company OKR publication
- **Output**: Area OKR document per Director with parent domain OKR reference

#### Stage 5: Squad OKR and Sprint Goal Derivation

- **Actor**: EMs + PMs
- **Action**: Derive squad OKRs from area OKRs; connect sprint goals to squad Key Results
- **Timing**: Within 7 working days of company OKR publication (before first sprint planning of the quarter)
- **Output**: Squad OKR document; sprint goal to OKR trace visible in Sprint Kickoff Briefs (per Clarity of Intent Stage 4 Intent Trace format)

#### Stage 6: Cascade Publication and Verification

- **Actor**: TPM (coordination); EMs (squad-level verification)
- **Action**: Full cascade document published; verification that every sprint goal traces to a company OKR within 3 degrees
- **Timing**: Within 1 week of company OKR publication
- **Output**: Engineering OKR cascade document per organizational layer; published to team wiki / project root

### Inputs

| Input | Source | Description |
|-------|--------|-------------|
| Company OKRs | CEO / Leadership | Quarterly company objectives and key results |
| Previous quarter OKR scores | P-072 (OKR Retrospective) | Learnings and scoring from previous quarter to inform next cascade |
| Strategic priorities | P-005 (Strategic Prioritization) | Prioritized initiative list feeding the OKR cascade |
| Organizational hierarchy | Engineering Team Structure Guide | CTO → VP → Director → EM → PM structure defining cascade levels |

### Outputs/Artifacts

| Artifact | Format | Owner | Location |
|----------|--------|-------|----------|
| Engineering OKR Cascade Document | Structured document with traceability columns at each level | VP (engineering-level); Director (area-level); EM (squad-level) | Team wiki / project root; one document per organizational layer |
| Sprint Goal to OKR Trace | Intent Trace in Sprint Kickoff Brief (3-line format: Company OKR → Squad OKR → Sprint Goal) | EM + PM | Sprint Kickoff Brief (per Clarity of Intent Stage 4, Section 2) |
| OKR Cascade Summary | Single-page roll-up showing full cascade path | TPM | Program dashboard |

### Gate/Checkpoint

**Gate: OKR Cascade Completeness Review**

- **Timing**: 1 week after company OKR publication
- **Participants**: CTO or VP delegate, Directors, TPMs
- **Format**: 30-minute review or async verification with 48-hour response window
- **Pass Criteria**:
  - Every organizational level has published its derived OKRs
  - Every squad OKR traces to a company OKR within 3 degrees
  - No orphan OKRs (squad OKRs with no parent linkage)
  - OKR cascade document published and accessible to all engineers
  - Sprint goals for the first sprint of the quarter reference squad Key Results

### Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Sprint goal traceability | Every sprint goal traces to a company OKR within 3 degrees | 100% of sprint goals traceable |
| Cascade timeliness | OKR cascade documented and published | Within 1 week of company OKR publication |
| Engineer alignment | Random engineer can explain how their sprint goal connects to a company OKR | Consistently pass (per Clarity of Intent "Intent alignment" signal) |
| OKR quality | Key Results are outcomes, not outputs | 100% compliance in cascade review |

### Dependencies

| Dependency | Process | Nature |
|------------|---------|--------|
| Strategic Prioritization | P-005 | Feeds the OKR cascade with prioritized initiatives |
| OKR Retrospective | P-072 | Provides input (previous quarter learnings) for next cascade |
| Sprint Readiness Gate | P-078 feeds into Sprint Bridge (Clarity of Intent Stage 4) | Sprint goal to OKR trace reviewed at every Sprint Readiness Gate |

### Traceability

- **Upstream**: Company OKRs → Engineering Team Structure Guide Section 11.4 OKR cascade
- **Downstream**: Sprint Kickoff Briefs (Clarity of Intent Stage 4); Sprint Readiness Gate pass criteria ("Intent trace is visible")
- **Cross-reference**: Clarity of Intent Stage 1 Intent Brief Question 3 (strategic context must reference a real OKR)

---

## P-079: Stakeholder Update Cadence Process

### Process Identity

| Field | Value |
|-------|-------|
| **Process ID** | P-079 |
| **Process Name** | Stakeholder Update Cadence Process |
| **Category** | 14 — Communication & Alignment |
| **Risk Level** | MEDIUM |

### Purpose

Ensure stakeholders receive regular, structured updates on delivery progress at every organizational level. PMs communicate sprint outcomes to squad stakeholders. TPMs communicate program milestones. Directors communicate delivery health to VPs. Stakeholders are never surprised by major delivery issues — escalations are communicated immediately, not held for the next scheduled update.

### Derived From

- Stage 0 research Category 16: PM, TPM, and Director communication responsibilities
- Engineering Team Structure Guide: PM role ("manages stakeholder expectations"), TPM role, Director role
- Clarity of Intent Stage 3 Dependency Charter Section 4 (Communication Protocol): structured communication cadences for cross-team projects
- Clarity of Intent "How to Know the Process Is Working" signals: stakeholder trust maintained through regular communication

### Primary Owner Agent

**product-manager** — Owns sprint-level stakeholder updates.
**technical-program-manager** — Owns program-level milestone updates.

### Supporting Agents

| Agent | Responsibility |
|-------|---------------|
| **engineering-manager** | Director-level delivery health summaries to VP; EM provides sprint metrics to PM for stakeholder updates |

### Stages/Steps

#### Stage 1: Sprint Review Summary Distribution

- **Actor**: Product Manager
- **Action**: Distribute sprint review summary to squad stakeholders
- **Timing**: Within 24 hours of sprint review ceremony
- **Content**:
  - Sprint goal: achieved / partially achieved / missed (with explanation)
  - Deliverables completed vs. planned
  - Key decisions made during the sprint
  - Risks or blockers surfaced
  - Next sprint goal preview
- **Channel**: Stakeholder email list or designated communication channel

#### Stage 2: Program Milestone Tracker Update

- **Actor**: Technical Program Manager
- **Action**: Send milestone tracker update to program stakeholders at each milestone
- **Timing**: Within 24 hours of milestone completion or status change
- **Content**:
  - Milestone status (on track / at risk / missed)
  - Cross-team dependency status (pulled from Dependency Charter if applicable)
  - Updated timeline if changed
  - RAID log summary (Risks, Assumptions, Issues, Dependencies)
- **Channel**: Program stakeholder distribution list; RAID log linked

#### Stage 3: Weekly Delivery Health Summary

- **Actor**: Director (engineering-manager agent at Director level)
- **Action**: Send weekly delivery health summary to VP
- **Timing**: Weekly, fixed day (e.g., Friday)
- **Content**:
  - Squad delivery status across the Director's area
  - Sprint goal completion rates
  - Escalations and blockers
  - Capacity concerns
  - Input to P-064 (VP-level delivery governance)
- **Channel**: VP delivery dashboard or structured email

#### Stage 4: Immediate Escalation Communication

- **Actor**: Any role (PM, EM, TPM, TL) who identifies a major delivery issue
- **Action**: Communicate escalation immediately — never hold for next scheduled cycle
- **Timing**: As soon as the issue is identified
- **Content**:
  - What happened
  - Impact on deliverables and timeline
  - Current mitigation plan
  - Decision needed (if any)
- **Escalation Path**: Per Dependency Charter escalation paths (EM → Director → VP); per-dependency escalation defined in Clarity of Intent Stage 3

### Inputs

| Input | Source | Description |
|-------|--------|-------------|
| Sprint review outcomes | Sprint Review ceremony | Completed/incomplete stories, sprint goal status |
| Milestone tracker | TPM project tracking | Program-level milestone status |
| RAID log | TPM (per Clarity of Intent Stage 3) | Risks, Assumptions, Issues, Dependencies |
| Delivery metrics | CI/CD and project management tools | Velocity, burndown, blocker count |
| Escalation triggers | Dependency Charter (Clarity of Intent Stage 3, Section 4) | Any dependency blocked > 48 hours with no resolution path |

### Outputs/Artifacts

| Artifact | Format | Owner | Cadence |
|----------|--------|-------|---------|
| Sprint Review Summary | Structured 1-page summary | PM | Per sprint (biweekly) |
| Milestone Tracker Update | Status report with RAG indicators | TPM | Per milestone |
| Weekly Delivery Health Summary | Dashboard or structured email | Director | Weekly |
| Escalation Communication | Structured escalation message | Initiating role | As needed (immediate) |

### Gate/Checkpoint

**Checkpoint: Stakeholder Communication Audit**

- **Timing**: Monthly (as part of TPM program health review)
- **Participants**: TPM, PM leads, Director
- **Format**: Async review of communication log
- **Pass Criteria**:
  - All sprint review summaries sent within 24-hour SLA
  - No stakeholder reports learning about a major issue from outside the team before receiving a team update
  - Weekly delivery health summaries consistently delivered
  - Escalations communicated per defined escalation paths

### Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Update timeliness | Sprint review summaries sent within 24 hours | 100% compliance |
| No stakeholder surprises | Stakeholder survey / retrospective feedback: "Did you learn about any major issue from outside the team first?" | Zero instances per quarter |
| Delivery health visibility | VP receives weekly delivery health summary | Every week without gaps |
| Escalation responsiveness | Escalations communicated within 4 hours of identification | 100% compliance |

### Dependencies

| Dependency | Process | Nature |
|------------|---------|--------|
| VP-level delivery governance | P-064 | Weekly delivery health summary is input to P-064 |
| Dependency tracking | Clarity of Intent Stage 3 (Dependency Charter) | Communication Protocol and escalation paths defined there |
| Sprint ceremonies | Standard Scrum process | Sprint review is the trigger for PM stakeholder update |

### Traceability

- **Upstream**: Clarity of Intent Stage 3 Communication Protocol (dependency standup, RAID log update, escalation trigger cadences)
- **Downstream**: VP governance decisions (P-064); stakeholder trust metrics in quarterly retrospectives
- **Cross-reference**: Clarity of Intent "How to Know the Process Is Working" — intent alignment signal depends on consistent communication

---

## P-080: Guild Standards Communication Process

### Process Identity

| Field | Value |
|-------|-------|
| **Process ID** | P-080 |
| **Process Name** | Guild Standards Communication Process |
| **Category** | 14 — Communication & Alignment |
| **Risk Level** | LOW |

### Purpose

Guilds publish and maintain living standards documents. Updates are communicated through guild channels. Adoption is tracked but not mandated — guilds are voluntary cross-tribe communities with no formal authority. Non-adopting squads may hold an exemption with documented rationale. This process ensures standards remain relevant and visible rather than becoming stale shelf-ware.

### Derived From

- Stage 0 research Category 16: guild communication patterns
- Engineering Team Structure Guide Section 4.3 (Guilds and Chapters): "Guilds are voluntary, cross-tribe communities with no formal authority. Membership is self-selected. Chapters, by contrast, are formal, within-tribe discipline groupings."
- Engineering Team Structure Guide Guild table: Frontend Guild, JVM Guild, Systems Guild, Mobile Guild, Python Guild, Go Guild, Cloud Guild, Security Guild
- Engineering Team Structure Guide anti-pattern: "Platform Mandate Without Adoption" — standards without developer buy-in cause shadow IT

### Primary Owner Agent

**staff-principal-engineer** — Acting as Guild Lead. Guild Leads are typically Staff or Principal Engineers who set technical direction across multiple teams.

### Supporting Agents

| Agent | Responsibility |
|-------|---------------|
| **technical-writer** | Maintains standards documentation; ensures documents are well-structured, accessible, and version-controlled |
| **engineering-manager** | Tracks adoption of guild standards within their squad; reports adoption status quarterly |

### Stages/Steps

#### Stage 1: Standards Authoring or Update

- **Actor**: Guild Lead (staff-principal-engineer)
- **Action**: Author new standards document or update existing one based on guild discussion, new technology decisions, or incident learnings
- **Trigger**: Guild meeting decision; technology evaluation outcome; incident post-mortem recommendation; quarterly standards review
- **Constraint**: Standards must be outcome-oriented (describe the "what" and "why", not just the "how"); include rationale for each standard to enable informed adoption decisions

#### Stage 2: Guild Review and Consensus

- **Actor**: Guild members
- **Action**: Review proposed standard via guild channel; provide feedback; reach consensus (not necessarily unanimity)
- **Timing**: 1-2 week review period per guild meeting cycle
- **Output**: Approved standards document with version number and effective date

#### Stage 3: Publication and Communication

- **Actor**: Guild Lead + Technical Writer
- **Action**: Publish approved standard to guild channel and team wikis; notify affected EMs
- **Timing**: Within 48 hours of guild consensus
- **Communication Content**:
  - What changed (diff summary for updates; full document for new standards)
  - Why it changed (rationale)
  - Impact on existing squads (what, if anything, needs to change)
  - Adoption expectation (recommended, not mandated)
  - Point of contact for questions
- **Channel**: Guild Slack/Teams channel; team wiki; EM notification

#### Stage 4: EM Notification and Squad Assessment

- **Actor**: Engineering Managers
- **Action**: Review standards updates for relevance to their squad; decide adoption plan or document exemption rationale
- **Timing**: Within 1 sprint of publication
- **Output**: Squad adoption decision (adopt / defer / exempt with rationale)

#### Stage 5: Quarterly Adoption Tracking

- **Actor**: Guild Lead + EMs
- **Action**: Track adoption rate across squads; review exemptions; assess whether non-adoption indicates a problem with the standard itself
- **Timing**: Quarterly
- **Output**: Adoption report per guild standard
- **Key Principle**: Low adoption is a signal to improve the standard, not a mandate to force compliance (per Engineering Team Structure Guide anti-pattern guidance)

### Inputs

| Input | Source | Description |
|-------|--------|-------------|
| Guild meeting discussions | Guild meetings (biweekly or monthly) | Technical discussions driving standards decisions |
| Technology evaluation outcomes | Architecture Review Board / guild evaluation | New technology or pattern decisions |
| Incident post-mortem recommendations | Incident management process | Standards gaps identified through incidents |
| Existing standards documents | Team wiki | Current versions of guild standards |
| Squad adoption data | EMs | Current adoption status per squad |

### Outputs/Artifacts

| Artifact | Format | Owner | Location |
|----------|--------|-------|----------|
| Guild Standards Document | Versioned markdown/wiki document | Guild Lead (staff-principal-engineer) | Team wiki; guild channel pinned |
| Standards Update Notification | Structured message (what changed, why, impact) | Guild Lead + Technical Writer | Guild channel; EM distribution |
| Adoption Report | Quarterly summary table (guild standard x squad → adopted/exempt/pending) | Guild Lead | Guild quarterly review; shared with Directors |
| Exemption Register | Table of squads with documented exemption rationale per standard | EMs | Team wiki; linked from Adoption Report |

### Gate/Checkpoint

**Checkpoint: Quarterly Guild Standards Health Review**

- **Timing**: Quarterly (aligned with OKR cycle)
- **Participants**: Guild Lead, attending EMs, Director (optional)
- **Format**: 30-minute review in guild meeting
- **Review Items**:
  - Are all standards documents current (reviewed within the quarter)?
  - What is the adoption rate per standard?
  - Are exemptions reasonable and documented?
  - Are any standards candidates for retirement?
  - Are any frequently requested standards missing?

### Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Standards currency | All guild standards reviewed at least quarterly | 100% reviewed within quarter |
| Adoption visibility | Adoption rate tracked and visible per standard | Adoption data available for every guild standard |
| Exemption documentation | Squads that deviate from a standard have documented rationale | 100% of deviations documented |
| Communication timeliness | Standards updates communicated within 48 hours of consensus | 100% compliance |
| Standard relevance | Standards with < 25% adoption reviewed for retirement or improvement | Reviewed quarterly; action taken |

### Dependencies

| Dependency | Process | Nature |
|------------|---------|--------|
| Architecture Review | Architecture review processes | Technology decisions may trigger standards updates |
| Incident Post-Mortems | Incident management processes | Post-mortem recommendations may trigger standards creation |
| OKR Cycle | P-078 | Quarterly adoption tracking aligned with OKR quarterly cycle |

### Traceability

- **Upstream**: Engineering Team Structure Guide Guild table (defines which guilds exist and what standards they own); Security Champions Guild (threat modeling templates, CVE triage process)
- **Downstream**: Squad technical practices; code review standards; architecture decisions
- **Cross-reference**: Engineering Team Structure Guide anti-pattern "Platform Mandate Without Adoption" — this process explicitly avoids mandating adoption, tracking it instead as a health signal

---

## P-081: DORA Metrics Review and Sharing Process

### Process Identity

| Field | Value |
|-------|-------|
| **Process ID** | P-081 |
| **Process Name** | DORA Metrics Review and Sharing Process |
| **Category** | 14 — Communication & Alignment |
| **Risk Level** | MEDIUM |

### Purpose

Engineering Managers share DORA metrics in team context monthly. Directors review cross-squad trends. VPs review cross-domain trends. DORA metrics are treated as team health signals — they are NEVER used for individual performance scoring or team ranking. Metrics without context create gaming behavior; metrics with context create improvement culture.

### Derived From

- Stage 0 research Category 16: DORA best practices
- Engineering Team Structure Guide Section 7.7 and Section 11.5: DORA metrics definitions, measurement methods, and elite benchmarks
- Engineering Team Structure Guide Section 7.7: "Platform Engineering owns DORA metric collection and dashboards. Engineering Managers use DORA trends as team health signals, not as individual performance scores."
- Engineering Team Structure Guide: "A team with high Deployment Frequency and high Change Failure Rate needs better test coverage, not fewer deploys. A team with low Deployment Frequency and low Lead Time has a deployment gate problem, not a development problem."

### Primary Owner Agent

**engineering-manager** — Owns the EM → Director → VP review cascade. EMs contextualize and share metrics with their teams; Directors aggregate cross-squad trends; VPs aggregate cross-domain trends.

### Supporting Agents

| Agent | Responsibility |
|-------|---------------|
| **infra-engineer** | Owns DORA metric collection toolchain and dashboards; provides Deployment Frequency and Lead Time for Changes data from CI/CD systems |
| **sre** | Provides MTTR and Change Failure Rate data from incident management and monitoring systems |

### DORA Metrics Definitions

Per Engineering Team Structure Guide Section 11.5:

| Metric | Definition | Measurement Method | Elite Benchmark |
|--------|-----------|-------------------|-----------------|
| **Deployment Frequency** | How often code deploys to production per day/week | Count production deploys over time; normalize to per-day | Multiple times per day (on-demand) |
| **Lead Time for Changes** | Time from code commit to running in production | P50 and P95 of commit-to-deploy duration | Less than 1 hour |
| **Change Failure Rate** | Percentage of deployments resulting in a production incident | (Failed deploys / total deploys) x 100 | Less than 5% |
| **MTTR** | Mean time to restore service after a production incident | Mean duration from incident opened to resolved | Less than 1 hour |

### Stages/Steps

#### Stage 1: Automated Metric Collection

- **Actor**: Platform Engineer (infra-engineer) + SRE (sre)
- **Action**: DORA metrics collected automatically from CI/CD pipelines and incident management systems
- **Timing**: Continuous collection; dashboards updated in near-real-time
- **Systems**: CI/CD toolchain (GitHub Actions, GitLab CI, etc.); incident management (PagerDuty, OpsGenie, etc.); observability platform (Datadog, Grafana, etc.)
- **Output**: DORA metrics dashboard per squad, per tribe, per domain
- **Constraint**: Metrics must include both P50 and P95 for Lead Time for Changes (per Engineering Team Structure Guide)

#### Stage 2: EM Monthly Team Review

- **Actor**: Engineering Manager
- **Action**: Review team's DORA metrics monthly; share with team in retrospective context
- **Timing**: Monthly (during or adjacent to team retrospective)
- **Content**:
  - Current month's metrics vs. previous month (trend)
  - Current metrics vs. team's own baseline (not vs. other teams)
  - Context for each metric: what happened this month that explains the numbers
  - Diagnosis using Engineering Team Structure Guide patterns (e.g., high Deployment Frequency + high Change Failure Rate = need better test coverage; low Deployment Frequency + low Lead Time = deployment gate problem)
  - Improvement actions identified by the team (not imposed top-down)
- **Output**: Team DORA review notes with context and identified actions
- **CRITICAL CONSTRAINT**: DORA metrics are NEVER used in individual performance reviews or team rankings. This is stated in the review and reinforced consistently.

#### Stage 3: Director Cross-Squad Trend Review

- **Actor**: Director (engineering-manager agent at Director level)
- **Action**: Review DORA trends across all squads in their area; flag squads with degrading metrics for support (not punishment)
- **Timing**: Monthly (1 week after EM reviews)
- **Content**:
  - Cross-squad trend summary (anonymized where appropriate)
  - Squads with improving trends: what are they doing that others can learn from?
  - Squads with degrading trends: what support do they need? (capacity, tooling, process)
  - Systemic patterns visible at the area level
- **Output**: Area DORA trend summary shared with VPs

#### Stage 4: VP Cross-Domain Trend Review

- **Actor**: VP
- **Action**: Review cross-domain DORA trends; escalate systemic degradation to CTO
- **Timing**: Monthly (1 week after Director reviews)
- **Content**:
  - Organization-wide DORA health summary
  - Systemic issues requiring CTO attention or cross-domain investment
  - Platform engineering investment recommendations based on DORA data
- **Output**: Org-level DORA summary; escalation to CTO if systemic degradation detected

#### Stage 5: Quarterly Deep Review

- **Actor**: EM + Director
- **Action**: Deep quarterly review of DORA trends aligned with OKR retrospective
- **Timing**: Quarterly (per Engineering Team Structure Guide: "Review DORA trends in quarterly retrospectives")
- **Content**:
  - Quarter-over-quarter trend analysis
  - Correlation with delivery outcomes (did DORA improvements correlate with better sprint goal completion?)
  - Baseline reset if team composition or architecture changed significantly
  - Investment recommendations for next quarter

### Inputs

| Input | Source | Description |
|-------|--------|-------------|
| CI/CD deployment data | Platform Engineering dashboards | Deployment Frequency, Lead Time for Changes |
| Incident management data | SRE / incident management system | MTTR, Change Failure Rate |
| Team context | EM knowledge | Sprint events, team changes, architecture changes that explain metric movement |
| Previous month metrics | DORA dashboard historical data | Trend baseline |

### Outputs/Artifacts

| Artifact | Format | Owner | Cadence |
|----------|--------|-------|---------|
| DORA Dashboard | Automated dashboard per squad/tribe/domain | Platform Engineer | Continuous |
| Team DORA Review Notes | Contextualized summary with improvement actions | EM | Monthly |
| Area DORA Trend Summary | Cross-squad trend report | Director | Monthly |
| Org DORA Health Summary | Cross-domain trend report with escalations | VP | Monthly |
| Quarterly DORA Deep Review | Quarter-over-quarter analysis with investment recommendations | EM + Director | Quarterly |

### Gate/Checkpoint

**Checkpoint: Monthly DORA Review Completeness**

- **Timing**: End of each month
- **Participants**: Director (verifies all EMs in their area completed reviews)
- **Format**: Async verification
- **Pass Criteria**:
  - All squads have current DORA data available in dashboards
  - All EMs have conducted monthly team review and shared notes
  - Context is provided with every metric (no naked numbers)
  - No evidence of DORA metrics used for individual performance assessment
  - Degrading trends have identified support actions (not punitive measures)

### Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Monthly review completeness | All squads reviewed monthly at each organizational level | 100% of squads reviewed monthly |
| No individual performance misuse | DORA metrics absent from individual performance review documentation | Zero instances of DORA in individual reviews |
| Context provision | Every DORA review includes narrative context explaining the numbers | 100% of reviews include context |
| Trend visibility | DORA trends reviewed in quarterly retrospectives | Every quarter |
| Improvement culture | Teams identify improvement actions based on DORA data (tracked in retrospective action items) | At least 1 action per team per quarter |

### Dependencies

| Dependency | Process | Nature |
|------------|---------|--------|
| CI/CD pipeline instrumentation | Platform Engineering processes | DORA data collection depends on CI/CD pipeline instrumentation |
| Incident management | Incident response processes | MTTR and Change Failure Rate data depends on incident tracking |
| OKR Retrospective | P-072 | Quarterly DORA deep review aligned with OKR retrospective |
| Stakeholder Updates | P-079 | DORA trends may feed into Director weekly delivery health summaries |

### Traceability

- **Upstream**: Engineering Team Structure Guide Sections 7.7 and 11.5 (DORA metric definitions and usage guidance); Platform Engineering mandate to own collection toolchain
- **Downstream**: Team improvement actions; platform investment decisions; quarterly capacity planning
- **Cross-reference**: Engineering Team Structure Guide Section 7.6: "Platform's success is measured by developer satisfaction, adoption rate, and DORA metric improvements"; Section 11.5: "Baseline your metrics before setting targets. DORA trends matter more than absolute numbers."
- **Anti-pattern guard**: Engineering Team Structure Guide explicitly warns against using DORA for individual scoring — this process codifies that protection

---

## Cross-Process Dependencies (Category 14 Internal)

| From | To | Relationship |
|------|-----|-------------|
| P-078 (OKR Cascade) | P-079 (Stakeholder Updates) | OKR alignment context informs what stakeholders care about in updates |
| P-078 (OKR Cascade) | P-080 (Guild Standards) | Quarterly adoption tracking aligned with OKR cycle |
| P-078 (OKR Cascade) | P-081 (DORA Review) | DORA quarterly deep review aligned with OKR retrospective |
| P-079 (Stakeholder Updates) | P-081 (DORA Review) | DORA trends feed into delivery health summaries |
| P-080 (Guild Standards) | P-081 (DORA Review) | Guild standard adoption (e.g., CI/CD standards) can impact DORA metrics |

## External Process Dependencies Summary

| External Process | Depended On By | Nature |
|-----------------|----------------|--------|
| P-005 (Strategic Prioritization) | P-078 | Feeds OKR cascade with prioritized initiatives |
| P-064 (VP Delivery Governance) | P-079 | Receives weekly delivery health summaries |
| P-072 (OKR Retrospective) | P-078, P-081 | Provides input for next OKR cascade; aligns with quarterly DORA deep review |
| Clarity of Intent (all stages) | P-078, P-079 | Sprint Kickoff Brief Intent Trace (P-078); Communication Protocol (P-079) |

---

## Appendix: Agent Role Summary for Category 14

| Agent | P-078 Role | P-079 Role | P-080 Role | P-081 Role |
|-------|-----------|-----------|-----------|-----------|
| **engineering-manager** | Primary Owner (cascade at VP/Director/EM levels) | Supporting (Director delivery health) | Supporting (tracks squad adoption) | Primary Owner (review cascade) |
| **product-manager** | Supporting (sprint goal to OKR trace) | Primary Owner (sprint-level updates) | — | — |
| **technical-program-manager** | Supporting (program-level alignment) | Primary Owner (program-level updates) | — | — |
| **staff-principal-engineer** | — | — | Primary Owner (Guild Lead) | — |
| **technical-writer** | — | — | Supporting (standards documentation) | — |
| **infra-engineer** | — | — | — | Supporting (CI/CD data collection) |
| **sre** | — | — | — | Supporting (MTTR/CFR data) |

---

## Cross-Category Dependencies

### Dependencies FROM Other Categories (Inputs)

| Source Process | Source Category | Consuming Process | Nature |
|---------------|----------------|-------------------|--------|
| P-005 (Strategic Prioritization) | Cat 1: Intent & Strategic Alignment | P-078 (OKR Cascade Communication) | Strategic priorities feed OKR cascade |
| P-072 (OKR Retrospective) | Cat 12: Post-Delivery | P-078 (OKR Cascade Communication) | Learnings feed next cascade |
| P-027 (Sprint Review) | Cat 4: Sprint & Delivery | P-079 (Stakeholder Update Cadence) | Sprint outcomes feed updates |

### Dependencies TO Other Categories (Outputs)

| Providing Process | Consuming Process | Target Category | Nature |
|------------------|-------------------|-----------------|--------|
| P-078 (OKR Cascade) | P-022 (Sprint Goal Authoring) | Cat 4: Sprint & Delivery | OKR cascade ensures sprint goals trace to company OKRs |
| P-080 (Guild Standards) | P-067 (TL/Staff Audit) | Cat 11: Organizational Audit | Standards compliance checked at Layer 6 |

## Agent Assignments Summary

| Process | Primary Owner | Supporting Agents |
|---------|--------------|-------------------|
| P-078: OKR Cascade Communication | engineering-manager (VPs/Directors) | product-manager, technical-program-manager |
| P-079: Stakeholder Update Cadence | product-manager + technical-program-manager | engineering-manager |
| P-080: Guild Standards Communication | staff-principal-engineer (Guild Lead) | technical-writer, engineering-manager |
| P-081: DORA Metrics Review and Sharing | engineering-manager (EM/Director/VP cascade) | infra-engineer, sre |
