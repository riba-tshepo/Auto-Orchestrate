# Technical Specification: Technical Excellence & Standards Processes

**Category**: 16 -- Technical Excellence & Standards
**Processes**: P-085 through P-089
**Date**: 2026-04-05
**Stage**: 2 (Specification)
**Source**: Process Architecture (Stage 1), Clarity of Intent, Engineering Team Structure Guide

---

## Table of Contents

1. [Overview](#1-overview)
2. [P-085: RFC (Request for Comments) Process](#2-p-085-rfc-request-for-comments-process)
3. [P-086: Technical Debt Tracking Process](#3-p-086-technical-debt-tracking-process)
4. [P-087: Language Tier Policy Change Process](#4-p-087-language-tier-policy-change-process)
5. [P-088: Architecture Pattern Change Process](#5-p-088-architecture-pattern-change-process)
6. [P-089: Developer Experience Survey Process](#6-p-089-developer-experience-survey-process)
7. [Cross-Process Dependencies](#7-cross-process-dependencies)
8. [Traceability Matrix](#8-traceability-matrix)

---

## 1. Overview

Category 16 governs the processes that maintain and improve the technical foundation of the engineering organization. These five processes address distinct but interconnected concerns:

- **Architectural decision-making** at the cross-organization level (P-085, P-088)
- **Technical health measurement and remediation** (P-086)
- **Language ecosystem governance** to prevent fragmentation (P-087)
- **Developer productivity measurement** as a leading indicator of organizational health (P-089)

Together they ensure that technical standards evolve deliberately, technical debt remains visible and manageable, and the developer experience is continuously measured and improved.

### Design Principles

These processes follow the Clarity of Intent methodology: each process produces a specific artifact, passes through a defined gate, and only advances when the gate criteria are met. No silent decisions. No undocumented exceptions. Every outcome is traceable to its origin.

---

## 2. P-085: RFC (Request for Comments) Process

### Process ID
P-085

### Process Name
RFC (Request for Comments) Process

### Purpose
Principal Engineers author RFCs for multi-year or cross-organization technical decisions. Structured review by Staff, Distinguished, and relevant Engineering Managers ensures that decisions affecting multiple engineering domains are made with full organizational awareness. RFC acceptance authorizes implementing the proposed direction.

### Derived From
- Stage 0 research Category 17 (Technical Excellence practices)
- Principal Engineer role responsibilities (Engineering Team Structure Guide: Principal Engineer owns cross-org strategy, reports to VP or Director)
- Clarity of Intent Stage 2 (Scope Contract pattern): the RFC serves as a "scope contract" for architectural direction

### Primary Owner Agent
`staff-principal-engineer` (Principal Engineer)

### Supporting Agents
- `engineering-manager` -- relevant EMs review for team capacity and delivery impact
- `software-engineer` -- Tech Leads review for team-level feasibility and implementation implications

### Stages/Steps

| Stage | Activity | Owner | Duration | Gate |
|-------|----------|-------|----------|------|
| 1. Trigger Identification | Principal Engineer identifies a decision requiring RFC. A decision requires an RFC when it: (a) affects more than 2 engineering domains, (b) has multi-year implications, or (c) contradicts existing org-wide architecture | Principal Engineer | -- | Trigger criteria met |
| 2. RFC Authoring | RFC document authored containing: problem statement, proposed solution, alternatives considered with trade-off analysis, migration path (if changing existing systems), success criteria, and estimated effort | Principal Engineer | 3-5 days | Draft complete |
| 3. Publication and Comment Period | RFC published to engineering-wide RFC repository. All Staff Engineers, Distinguished Engineers, and relevant EMs are notified. Comment period opens. | Principal Engineer | 2 weeks (fixed) | Comment period elapsed |
| 4. Comment Resolution | Principal Engineer addresses all comments. Major objections (those challenging the fundamental approach) must be resolved through direct discussion, not just acknowledged. Minor comments may be addressed with amendments to the RFC. | Principal Engineer + Reviewers | 3-5 days | All major objections resolved |
| 5. Decision | RFC is accepted (with or without amendments) or rejected with documented rationale. Decision is made by consensus of reviewing Staff/Distinguished Engineers. If no consensus, the Principal Engineer's VP makes the final call. | Principal Engineer + VP (if escalation needed) | 1-2 days | Decision recorded |
| 6. Communication | Accepted RFC becomes the authoritative architecture decision. Communicated to all affected engineering teams within 1 week. Added to the Architecture Decision Register. | Principal Engineer | 1 week | All affected teams notified |

### Inputs
| Input | Source | Format |
|-------|--------|--------|
| Cross-org technical problem statement | Engineering teams, Staff/Principal Engineers, or CARB escalation | Free-form identification |
| Alternatives analysis | Principal Engineer research | Structured comparison |
| Feasibility data | Tech Leads from affected teams | Technical assessment |
| Technology Vision | P-006 (Technology Vision Alignment Process) | Vision document |
| Existing Architecture Decision Register | Previous RFC decisions | Decision log |

### Outputs / Artifacts
| Output | Format | Audience | Retention |
|--------|--------|----------|-----------|
| RFC Document | Structured document (problem, proposal, alternatives, migration path, success criteria) | All engineering | Permanent -- Architecture Decision Register |
| Review Comments | Threaded comments on RFC | RFC author + reviewers | Permanent -- attached to RFC |
| Decision Record | Accept/Reject with rationale | All engineering | Permanent -- Architecture Decision Register |

### Gate / Checkpoint

**Gate Name**: RFC Decision Gate

**Gate Criteria**:
- RFC comment period of 2 weeks has elapsed
- All major objections addressed before acceptance (major = challenges the fundamental approach)
- Accepted RFCs communicated to all affected engineering teams within 1 week of decision
- Decision rationale documented regardless of accept/reject outcome
- RFC added to Architecture Decision Register with unique ID

**Gate Participants**: Principal Engineer (author), Staff Engineers (reviewers), Distinguished Engineers (reviewers), relevant EMs, VP of Engineering (escalation only)

### Success Criteria
- RFC review period completed within 2 weeks (measured from publication date)
- All major objections addressed before acceptance -- no unresolved dissent on fundamental approach
- Accepted RFCs communicated to all affected engineering teams within 1 week of decision
- Zero architectural decisions at RFC scope made outside the RFC process (measured by quarterly audit)

### Dependencies
| Dependency | Process | Direction | Nature |
|------------|---------|-----------|--------|
| Technology Vision provides architectural guardrails | P-006 | Inbound | RFCs must align with Technology Vision |
| CARB may escalate decisions to RFC | P-047 | Inbound | CARB identifies decisions exceeding its scope |
| Architecture Pattern Changes reference RFC decisions | P-088 | Outbound | CARB checks consistency with RFC decisions |
| Technical Debt remediation may trigger RFCs | P-086 | Inbound | Large-scale debt remediation may require RFC |

### Traceability
- **Org Structure**: Principal Engineer role (L7, cross-org strategy); Staff Engineer role (L6, cross-team technical influence); Distinguished Engineer role (L8, company-wide)
- **Clarity of Intent**: Mirrors the Scope Contract pattern -- a written document that becomes the single source of truth, versioned and referenced by downstream work
- **Engineering Team Structure Guide**: Section 3 (Complete Role Catalog) defines Principal Engineer as "cross-org strategy" owner

---

## 3. P-086: Technical Debt Tracking Process

### Process ID
P-086

### Process Name
Technical Debt Tracking Process

### Purpose
Staff Engineer uses codebase metrics to measure and track technical debt quarterly. A report is produced for the Director of Engineering. Remediation sprints are allocated in capacity planning. This process makes invisible debt visible and ensures it is addressed systematically rather than accumulating until it causes delivery failures.

### Derived From
- Stage 0 research Category 17 (sustainable engineering practices)
- Staff Engineer responsibilities (Engineering Team Structure Guide: Staff Engineer L6, cross-team technical influence)
- Quarterly Capacity Planning (P-082) integration for remediation allocation
- Clarity of Intent principle: measurable outcomes with defined timelines

### Primary Owner Agent
`staff-principal-engineer` (Staff Engineer)

### Supporting Agents
- `engineering-manager` -- EM and Director allocate remediation capacity; Director reviews and approves quarterly report
- `software-engineer` -- Tech Lead provides team-level debt context, identifies local debt items

### Stages/Steps

| Stage | Activity | Owner | Duration | Gate |
|-------|----------|-------|----------|------|
| 1. Quarterly Codebase Analysis | Staff Engineer runs automated and manual analysis across all repositories: test coverage percentage, cyclomatic complexity distribution, dependency age (outdated/vulnerable dependencies), documentation coverage, code duplication ratio | Staff Engineer | 3-5 days | Analysis data collected |
| 2. Team-Level Context Collection | Staff Engineer consults each squad's Tech Lead to identify team-specific debt items not captured by automated metrics (e.g., architectural shortcuts, missing abstractions, undocumented tribal knowledge) | Staff Engineer + Tech Leads | 2-3 days | All squads consulted |
| 3. Report Production | Technical debt report produced containing: top 10 debt items ranked by impact, estimated paydown effort per item (in engineer-days), risk assessment if not addressed (probability and impact), trend comparison to previous quarter | Staff Engineer | 2-3 days | Report complete |
| 4. Director Review | Director of Engineering reviews report. Discussion of priorities, alignment with upcoming quarter's delivery goals. Director determines remediation sprint capacity allocation. | Staff Engineer + Director | 1 meeting (60 min) | Capacity allocation decided |
| 5. Remediation Sprint Scheduling | Remediation sprints scheduled with specific debt items targeted. Items assigned to owning squads. Tracked as formal sprint work, not side-of-desk effort. | Director + EMs | Integrated into P-082 | Sprints on calendar |
| 6. Trend Tracking | Debt metrics tracked over time. Quarter-over-quarter trend reported: is debt trending up or down? Are remediation sprints having measurable impact? | Staff Engineer | Ongoing | Trend data updated |

### Cadence
- **Measurement and Reporting**: Quarterly (aligned with quarterly capacity planning cycle, P-082)
- **Remediation**: Integrated into quarterly capacity planning; remediation sprints scheduled within the quarter following debt identification

### Inputs
| Input | Source | Format |
|-------|--------|--------|
| Codebase metrics (automated) | CI/CD pipeline analysis tools, SAST tools, dependency scanners | Automated reports |
| Team-level debt context | Tech Leads from each squad | Structured interview / written input |
| Previous quarter's debt report | P-086 archive | Quarterly report |
| Quarterly capacity plan | P-082 (Quarterly Capacity Planning) | Capacity allocation document |

### Outputs / Artifacts
| Output | Format | Audience | Retention |
|--------|--------|----------|-----------|
| Quarterly Technical Debt Report | Structured report: top 10 items, effort estimates, risk scores, trends | Director, EMs, Staff Engineers | Permanent -- quarterly archive |
| Debt Item Backlog | Prioritized list of debt items with effort estimates | EMs, Tech Leads | Living document, updated quarterly |
| Trend Dashboard | Quarter-over-quarter metrics visualization | Director, VP of Engineering | Updated quarterly |

### Gate / Checkpoint

**Gate Name**: Quarterly Debt Review Gate

**Gate Criteria**:
- Quarterly debt report produced on schedule (within 2 weeks of quarter end)
- All squad Tech Leads contributed team-level context
- Top 10 debt items have effort estimates and risk assessments
- Trend data compared to previous quarter
- Director has reviewed and allocated remediation capacity for next quarter

**Gate Participants**: Staff Engineer (report author), Director of Engineering (approver), Engineering Managers (capacity impact)

### Success Criteria
- Quarterly debt report produced on schedule every quarter -- zero missed quarters
- Debt trending visible over time with quarter-over-quarter comparison
- Remediation sprints allocated in capacity planning within 1 quarter of debt identification
- Technical debt metric (composite score) trending downward or stable over 4 quarters

### Dependencies
| Dependency | Process | Direction | Nature |
|------------|---------|-----------|--------|
| Capacity planning provides remediation budget | P-082 | Bidirectional | Debt report informs capacity allocation; capacity plan constrains remediation scope |
| Large-scale debt remediation may trigger RFC | P-085 | Outbound | Debt items requiring cross-org architectural change need RFC |
| Developer Experience Survey surfaces debt-related friction | P-089 | Inbound | Survey results may highlight debt items not captured by metrics |

### Traceability
- **Org Structure**: Staff Engineer (L6) owns cross-team technical health; Director of Engineering owns delivery accountability; EM allocates sprint capacity
- **Clarity of Intent**: Follows the measurable outcomes principle -- debt is quantified, tracked, and has defined success metrics
- **Engineering Team Structure Guide**: Staff Engineers "lead by influence, not authority" -- the debt report is their instrument of influence

---

## 4. P-087: Language Tier Policy Change Process

### Process ID
P-087

### Process Name
Language Tier Policy Change Process

### Purpose
Guild Lead sign-off is required for any new Tier 2 language use in a project. Tier 3 languages are blocked for new projects without explicit Distinguished Engineer and Director approval. This process prevents language fragmentation while allowing intentional, governed expansion of the language ecosystem.

### Derived From
- Stage 0 research Category 15 (Language governance)
- Engineering Team Structure Guide, Section 4.4 (Language Tier Policy): Tier 1 (fully supported), Tier 2 (supported with justification), Tier 3 (legacy/sunset)
- Engineering Team Structure Guide, Section 4.3 (Language Guilds): Guild governance of language standards
- Anti-pattern prevention: "Language Fragmentation -- too many languages across teams makes it hard to hire, share code, and maintain tooling"

### Primary Owner Agent
`staff-principal-engineer` (Guild Lead)

### Supporting Agents
- `engineering-manager` -- Director approves Tier 3 exceptions; EM confirms team capacity for language adoption

### Language Tiers (Reference)

| Tier | Definition | New Project Permission | Hiring Profile | Training Budget |
|------|-----------|------------------------|----------------|-----------------|
| Tier 1 -- Fully Supported | Official language with dedicated guild, standardized toolchain, active hiring profile, full IDE/CI support | Yes, no justification needed | Standard job descriptions exist | Full budget |
| Tier 2 -- Supported with Justification | Approved for specific domains; requires guild lead sign-off before new project | Yes, with guild approval | Available on request | Partial budget |
| Tier 3 -- Legacy / Sunset | No new projects; existing projects maintained until migration | No (exceptional cases only) | Not hiring for this language | Migration budget only |

**Current Tier Assignments** (from Engineering Team Structure Guide):
- **Tier 1**: JavaScript, TypeScript, Python, Go, Java, Kotlin, Swift, SQL
- **Tier 2**: Rust, C#, Scala, C++, Ruby
- **Tier 3**: C (unless embedded/systems), PHP (unless existing CMS product), older JVM versions

### Stages/Steps

| Stage | Activity | Owner | Duration | Gate |
|-------|----------|-------|----------|------|
| 1. Proposal Submission | Team proposes using a non-Tier-1 language for a new project or new component. Proposal includes: language name, current tier, project context, justification (why Tier 1 alternatives are insufficient), team expertise assessment, maintenance plan, toolchain readiness (CI/CD, linting, testing, IDE support) | Proposing Team (Tech Lead or EM) | 1-2 days | Proposal document submitted |
| 2. Guild Lead Evaluation | Relevant Guild Lead evaluates the proposal against three criteria: (a) Is the use technically justified? (b) Does the team have sufficient expertise? (c) Is the maintenance plan sustainable? | Guild Lead | 3-5 days | Evaluation complete |
| 3a. Tier 2 Decision | For Tier 2 languages: Guild Lead approves or rejects with documented rationale. If approved, conditions may be attached (e.g., "approved for this project only" or "requires mentorship from Guild member with production experience") | Guild Lead | 1 day | Decision recorded |
| 3b. Tier 3 Escalation | For Tier 3 languages: Guild Lead forwards evaluation with recommendation to Distinguished Engineer and Director of Engineering. All three must approve. Each approval is independent and documented. | Guild Lead + Distinguished Engineer + Director | 5-7 days | Three-way approval or rejection |
| 4. Register Update | Approved uses tracked in the Language Diversity Register: language, project, approver(s), approval date, conditions, review date | Guild Lead | 1 day | Register updated |
| 5. Quarterly Review | Language Diversity Register reviewed quarterly by Guild Leads. Tier 2 uses assessed for promotion to Tier 1 or sunset. Tier 3 exceptions assessed for ongoing justification. | All Guild Leads | Quarterly | Review complete |

### Inputs
| Input | Source | Format |
|-------|--------|--------|
| Language use proposal | Proposing team (Tech Lead or EM) | Structured proposal document |
| Current Language Tier Policy | Engineering Team Structure Guide Section 4.4 | Policy document |
| Language Diversity Register | P-087 archive | Living register |
| Team expertise assessment | Proposing team | Self-assessment with evidence |

### Outputs / Artifacts
| Output | Format | Audience | Retention |
|--------|--------|----------|-----------|
| Language Use Decision | Approve/Reject with rationale and conditions | Proposing team, Guild Lead, Director (Tier 3) | Permanent -- Language Diversity Register |
| Language Diversity Register | Tabular register of all non-Tier-1 language uses | Guild Leads, Directors, VP of Engineering | Living document, reviewed quarterly |
| Quarterly Language Review Summary | Summary of register changes, promotions, sunsets | Engineering leadership | Quarterly archive |

### Gate / Checkpoint

**Gate Name**: Language Tier Approval Gate

**Gate Criteria**:
- **Tier 2**: Guild Lead has evaluated and recorded a decision with documented rationale
- **Tier 3**: Guild Lead, Distinguished Engineer, and Director have each independently approved with documented rationale
- Language Diversity Register updated with the decision
- Conditions of approval (if any) are documented and have a review date

**Gate Participants**:
- Tier 2: Guild Lead (decision maker), proposing team Tech Lead/EM (requester)
- Tier 3: Guild Lead + Distinguished Engineer + Director (three-way approval required)

### Success Criteria
- No new Tier 2 language use begins without Guild Lead approval -- zero unapproved uses
- No new Tier 3 language use begins without full three-way approval chain -- zero unapproved uses
- Language Diversity Register is current and reviewed quarterly
- Language diversity (count of distinct languages in production) is stable or decreasing over 4 quarters

### Dependencies
| Dependency | Process | Direction | Nature |
|------------|---------|-----------|--------|
| RFC may mandate language tier changes | P-085 | Inbound | An RFC could promote or demote a language tier |
| CARB reviews may surface language decisions | P-088 | Bidirectional | Architecture pattern changes may require or eliminate language choices |
| Technology Vision sets language strategy context | P-006 | Inbound | Vision document may set direction on language consolidation |

### Traceability
- **Org Structure**: Guild Lead (volunteer coordinator, cross-tribe); Distinguished Engineer (L8, company-wide authority); Director of Engineering (delivery accountability)
- **Clarity of Intent**: Explicit boundaries principle -- Tier 3 languages are explicitly "not for new projects" just as the Intent Brief states what a project is NOT
- **Engineering Team Structure Guide**: Section 4.3 (Guilds), Section 4.4 (Language Tier Policy), Anti-pattern "Language Fragmentation"

---

## 5. P-088: Architecture Pattern Change Process

### Process ID
P-088

### Process Name
Architecture Pattern Change Process

### Purpose
CARB approval is required for new cloud service adoptions or architecture pattern changes above defined scope thresholds. This process prevents architectural fragmentation from local optimization decisions by ensuring cross-cutting changes are reviewed for security, cost, reliability, and consistency impacts.

### Derived From
- Stage 0 research Category 15 (Architecture governance)
- Engineering Team Structure Guide, Section 5.3 (Cloud Architecture Review Board): CARB composition, cadence, scope, and decision types
- CARB governance process (P-047 provides the operational cadence; P-088 defines what triggers CARB review)
- Technology Vision (P-006) provides the architectural guardrails against which changes are evaluated

### Primary Owner Agent
`cloud-engineer` (Cloud Architect; CARB chair)

### Supporting Agents
- `staff-principal-engineer` -- Principal/Staff Engineers serve on CARB as reviewers
- `security-engineer` -- Security Architect serves on CARB; evaluates security implications of pattern changes

### CARB Composition (Reference)
From Engineering Team Structure Guide Section 5.3:
- Cloud Architect (chair)
- Principal or Staff Engineers from product teams
- Security Architect
- FinOps Engineer

### Thresholds That Require CARB Review

| Threshold | Examples |
|-----------|---------|
| Any new cloud service adoption | First use of a service not already in the approved service catalog (e.g., first use of AWS Step Functions, Azure Cosmos DB) |
| Architecture pattern changes affecting >2 squads | Switching from REST to gRPC across multiple services; adopting event sourcing for shared domain |
| Changes to the approved service catalog | Adding or removing a service from the catalog; changing the approved configuration of an existing service |
| Cost commitments above defined threshold | Reserved instance purchases; committed use discounts; new vendor contracts above cost ceiling |

### Stages/Steps

| Stage | Activity | Owner | Duration | Gate |
|-------|----------|-------|----------|------|
| 1. Threshold Identification | Team identifies that their proposed change meets one or more CARB thresholds. Tech Lead or EM is responsible for recognizing the threshold. | Proposing Team (Tech Lead or EM) | -- | Threshold recognized |
| 2. CARB Review Request | Structured request submitted containing: (a) proposed change description, (b) alternatives considered with trade-offs, (c) cost model (upfront and ongoing), (d) security implications assessment, (e) affected squads and systems, (f) migration/rollback plan | Proposing Team | 2-3 days | Request submitted |
| 3. CARB Review | CARB reviews the request in its weekly cycle (P-047). Cloud Architect chairs the review. Security Architect evaluates security implications. FinOps Engineer evaluates cost impact. Staff/Principal Engineers evaluate architectural consistency. | CARB members | Weekly cycle (P-047) | Review complete |
| 4. Decision | CARB issues one of four decisions: Approve, Approve with Conditions, Reject (with documented rationale and redesign guidance), or Defer (needs more information -- return with specified additional data) | CARB (Cloud Architect announces) | Same session or within 48 hours | Decision recorded |
| 5. Post-Decision Actions | **If Approved**: Change enters implementation queue; service catalog updated within 1 week. **If Approved with Conditions**: Conditions documented; proposing team confirms conditions met before implementation. **If Rejected**: Rationale documented; proposing team may resubmit after addressing concerns. **If Deferred**: Information gaps specified; deadline for resubmission set. | Proposing Team + CARB chair | 1 week (catalog update) | Catalog/register updated |

### Inputs
| Input | Source | Format |
|-------|--------|--------|
| Architecture change proposal | Proposing team | Structured CARB review request |
| Approved service catalog | CARB maintained | Service catalog document |
| Technology Vision | P-006 | Vision document |
| Existing RFC decisions | P-085 | Architecture Decision Register |
| Cost data | FinOps Engineer | Cost analysis |
| Security assessment | Security Architect or proposing team's Security Champion | Threat/risk assessment |

### Outputs / Artifacts
| Output | Format | Audience | Retention |
|--------|--------|----------|-----------|
| CARB Decision Record | Structured decision: Approve/Approve with Conditions/Reject/Defer with rationale | Proposing team, all engineering, CARB archive | Permanent -- CARB decision log |
| Updated Service Catalog | Tabular catalog of approved cloud services and patterns | All engineering teams | Living document, updated per CARB decision |
| Conditions Register (if applicable) | List of conditions with compliance deadlines | Proposing team, CARB chair | Tracked until conditions met |

### Gate / Checkpoint

**Gate Name**: CARB Decision Gate

**Gate Criteria**:
- All threshold-meeting changes reviewed by CARB before implementation begins -- zero pre-implementation bypasses
- CARB decisions are consistent with Technology Vision (P-006) and RFC decisions (P-085)
- Service catalog updated within 1 week of CARB approval
- Rejected changes receive documented rationale with actionable redesign guidance
- Deferred changes have a specified information gap and resubmission deadline

**Gate Participants**: Cloud Architect (CARB chair), Principal/Staff Engineers (reviewers), Security Architect (security review), FinOps Engineer (cost review)

### Success Criteria
- All threshold-meeting changes reviewed by CARB before implementation -- zero bypasses measured quarterly
- CARB decisions consistent with Technology Vision (P-006) and existing RFC decisions (P-085) -- zero contradictions
- Service catalog updated within 1 week of each CARB approval
- CARB review cycle time: decision issued within 1 weekly cycle of submission (no multi-week backlogs)

### Dependencies
| Dependency | Process | Direction | Nature |
|------------|---------|-----------|--------|
| CARB operates on weekly cycle | P-047 | Inbound | P-047 is the operational cadence; P-088 defines what triggers review |
| Technology Vision provides guardrails | P-006 | Inbound | CARB evaluates changes against the Technology Vision |
| RFC decisions provide architectural direction | P-085 | Inbound | CARB ensures changes are consistent with accepted RFCs |
| Language Tier changes may interact | P-087 | Bidirectional | Architecture pattern changes may require or affect language choices |

### Traceability
- **Org Structure**: Cloud Architect chairs CARB (Engineering Team Structure Guide Section 5.3); Principal/Staff Engineers provide cross-team perspective; Security Architect ensures security governance; FinOps Engineer ensures cost governance
- **Clarity of Intent**: Mirrors the Explicit Exclusions principle -- the approved service catalog defines what IS approved, and everything outside it requires review. CARB thresholds serve as explicit boundaries.
- **Engineering Team Structure Guide**: Section 5.3 (CARB composition, cadence, scope, decision types), Section 5.1 (CCoE model)

---

## 6. P-089: Developer Experience Survey Process

### Process ID
P-089

### Process Name
Developer Experience Survey Process

### Purpose
DX Engineers measure developer NPS quarterly via structured survey. Findings feed platform backlog prioritization. Developer experience is a leading indicator of productivity and retention -- unmeasured developer experience degrades silently.

### Derived From
- Stage 0 research Category 17 (Developer Experience measurement)
- DX Engineer role (Engineering Team Structure Guide Section 7: Platform Engineering, DX Engineer -- L4-L6, internal developer NPS tracking)
- Platform as a Product design principle (Engineering Team Structure Guide: "The platform team should be treated as an internal product org with developers as its customers")

### Primary Owner Agent
`platform-engineer` (DX Engineer)

### Supporting Agents
- `engineering-manager` -- Platform EM reviews findings and acts on platform backlog changes; all EMs distribute survey to their teams

### Stages/Steps

| Stage | Activity | Owner | Duration | Gate |
|-------|----------|-------|----------|------|
| 1. Survey Design | DX Engineer designs or updates the quarterly developer NPS survey. Survey covers four dimensions: (a) tool usability (CI/CD, IDE, dev portal), (b) environment reliability (staging, local dev, build times), (c) onboarding friction (new engineer and new project setup), (d) documentation quality (API docs, runbooks, architecture docs) | DX Engineer | 2-3 days (first time); 1 day (subsequent quarters -- update only) | Survey instrument ready |
| 2. Distribution | Survey distributed to all engineers across the organization. Survey is anonymous. Distribution via engineering-wide channel with EM reinforcement. Response window: 2 weeks. | DX Engineer + EMs | 2 weeks (response window) | Response window closed |
| 3. Analysis | Results analyzed: (a) NPS score calculated (promoters minus detractors as percentage), (b) dimension-level scores calculated, (c) free-text responses themed and categorized, (d) comparison to previous quarter's results | DX Engineer | 3-5 days | Analysis complete |
| 4. Friction Point Documentation | Top friction points documented with frequency score (how many engineers reported it) and impact score (severity of productivity loss). Ranked by combined frequency x impact. | DX Engineer | 2-3 days | Friction point register produced |
| 5. Platform Backlog Update | Highest-impact friction points promoted to top of platform team backlog. Platform EM reviews and confirms prioritization. Friction points that require non-platform team action are routed to the appropriate EM/Director. | DX Engineer + Platform EM | 1-2 days | Backlog updated |
| 6. Results Communication | Results shared with all engineers -- unfiltered. No executive filtering of negative feedback. Results include: NPS score, dimension scores, top friction points, actions planned, and comparison to previous quarter. | DX Engineer + Platform EM | 1 day | Results published |

### Cadence
- **Survey**: Quarterly
- **Analysis and Communication**: Within 3 weeks of survey close
- **Backlog Impact**: Immediate -- highest-impact items enter next sprint planning

### Inputs
| Input | Source | Format |
|-------|--------|--------|
| Survey instrument | DX Engineer (designed/updated quarterly) | Survey form (anonymous) |
| Previous quarter's results | P-089 archive | Analysis report |
| Platform backlog (current state) | Platform team | Backlog / board |
| Engineer population list | Engineering management | Distribution list (for response rate calculation) |

### Outputs / Artifacts
| Output | Format | Audience | Retention |
|--------|--------|----------|-----------|
| Developer NPS Score | Single number (quarterly) | All engineering, VP of Engineering, CTO | Quarterly archive -- trended over time |
| Dimension Scores | Four scores (tool usability, environment reliability, onboarding friction, documentation quality) | Platform team, engineering leadership | Quarterly archive |
| Friction Point Register | Ranked list with frequency and impact scores | Platform team, engineering leadership | Quarterly archive, carried forward |
| Results Communication | Summary document or presentation | All engineers | Published quarterly |
| Updated Platform Backlog | Prioritized backlog with survey-driven items tagged | Platform team | Living document |

### Gate / Checkpoint

**Gate Name**: Survey Results Review Gate

**Gate Criteria**:
- Survey response rate of 60% or higher (if below 60%, results are flagged as potentially unrepresentative and the distribution method is reviewed)
- Results shared unfiltered with all engineers and engineering leadership
- Top 3 friction points have assigned owners and target resolution timeline
- Platform backlog updated to reflect survey findings
- Quarter-over-quarter comparison produced

**Gate Participants**: DX Engineer (analysis owner), Platform EM (backlog owner), VP of Engineering (accountability for action on results)

### Success Criteria
- Survey response rate at or above 60% every quarter
- Results shared unfiltered with engineering leadership -- zero instances of filtered or suppressed findings
- Top 3 friction points addressed (resolved or materially improved) within 2 quarters of identification
- Developer NPS trending upward or stable over 4 quarters

### Dependencies
| Dependency | Process | Direction | Nature |
|------------|---------|-----------|--------|
| Survey findings may surface technical debt items | P-086 | Outbound | Friction points related to code quality feed into debt tracking |
| Onboarding friction feeds into onboarding process | P-090 | Outbound | Onboarding dimension results inform onboarding process improvements |
| Platform backlog prioritization affects capacity planning | P-082 | Outbound | High-impact friction items may require capacity allocation |

### Traceability
- **Org Structure**: DX Engineer (L4-L6, Platform team); Platform EM (reviews and acts on findings); VP of Engineering (accountability)
- **Clarity of Intent**: Follows the "How to Know the Process Is Working" pattern from Clarity of Intent -- developer NPS is a process health signal, not just a vanity metric
- **Engineering Team Structure Guide**: Section 7 (Platform Engineering), DX Engineer role definition ("internal developer NPS tracking"), Platform as a Product principle

---

## 7. Cross-Process Dependencies

### Internal Dependencies (Within Category 16)

```
P-085 (RFC) ←→ P-088 (Architecture Pattern Change)
  - CARB checks consistency with RFC decisions
  - CARB may escalate decisions to RFC when scope exceeds CARB authority

P-085 (RFC) ← P-086 (Technical Debt Tracking)
  - Large-scale debt remediation may require an RFC

P-087 (Language Tier) ←→ P-088 (Architecture Pattern Change)
  - Architecture changes may require or affect language choices
  - Language tier changes may imply architecture pattern changes

P-089 (Developer Experience Survey) → P-086 (Technical Debt Tracking)
  - Survey friction points may surface debt items not captured by metrics
```

### External Dependencies (Other Categories)

| Process | Depends On | Nature |
|---------|-----------|--------|
| P-085 (RFC) | P-006 (Technology Vision Alignment) | RFCs must align with Technology Vision |
| P-085 (RFC) | P-047 (CARB Process) | CARB may escalate to RFC |
| P-086 (Technical Debt) | P-082 (Quarterly Capacity Planning) | Remediation capacity allocated through capacity planning |
| P-088 (Architecture Pattern Change) | P-006 (Technology Vision Alignment) | CARB evaluates against Technology Vision |
| P-088 (Architecture Pattern Change) | P-047 (CARB Process) | CARB weekly cycle is the operational mechanism |
| P-089 (Developer Experience Survey) | P-082 (Quarterly Capacity Planning) | High-impact friction items may need capacity allocation |
| P-089 (Developer Experience Survey) | P-090 (New Engineer Onboarding) | Onboarding dimension results inform onboarding improvements |

### Dependency Flow Diagram

```
                    ┌─────────────┐
                    │   P-006     │
                    │ Technology  │
                    │   Vision    │
                    └──────┬──────┘
                           │ (guardrails)
              ┌────────────┼────────────┐
              ▼            ▼            │
        ┌──────────┐ ┌──────────┐      │
        │  P-085   │ │  P-088   │      │
        │   RFC    │◄┤ Arch Pat │      │
        │ Process  │ │  Change  │      │
        └────┬─────┘ └────┬─────┘      │
             │             │            │
             │        ┌────┘            │
             ▼        ▼                 │
        ┌──────────┐                   │
        │  P-047   │                   │
        │  CARB    │                   │
        │ (weekly) │                   │
        └──────────┘                   │
                                       │
  ┌──────────┐     ┌──────────┐  ┌─────┴────┐
  │  P-089   │────►│  P-086   │─►│  P-082   │
  │  DevEx   │     │  Tech    │  │ Capacity │
  │  Survey  │     │  Debt    │  │ Planning │
  └──────────┘     └──────────┘  └──────────┘
```

---

## 8. Traceability Matrix

### Process-to-Source Traceability

| Process | Clarity of Intent Principle | Engineering Team Structure Guide Section | Stage 0 Research Category |
|---------|---------------------------|----------------------------------------|--------------------------|
| P-085 RFC | Scope Contract pattern (single source of truth for decisions) | Section 3 (Principal Engineer role, Staff Engineer role) | Category 17 |
| P-086 Technical Debt | Measurable outcomes with timelines; Success Metrics pattern | Section 3 (Staff Engineer role); Section 2 (Director role) | Category 17 |
| P-087 Language Tier | Explicit Exclusions (Tier 3 = "not for new projects"); Boundaries | Section 4.3 (Guilds), Section 4.4 (Language Tier Policy) | Category 15 |
| P-088 Architecture Pattern | Scope Lock gate pattern; Explicit boundaries (approved catalog) | Section 5.3 (CARB), Section 5.1 (CCoE) | Category 15 |
| P-089 DevEx Survey | "How to Know the Process Is Working" signals | Section 7 (Platform Engineering, DX Engineer role) | Category 17 |

### Process-to-Agent Traceability

| Agent | Primary Owner Of | Supporting Role In |
|-------|-----------------|-------------------|
| `staff-principal-engineer` | P-085 (RFC), P-086 (Tech Debt), P-087 (Language Tier) | P-088 (CARB member) |
| `cloud-engineer` | P-088 (Architecture Pattern Change) | -- |
| `platform-engineer` | P-089 (Developer Experience Survey) | -- |
| `engineering-manager` | -- | P-085 (EM review), P-086 (capacity allocation), P-087 (Director approval for Tier 3), P-089 (survey distribution) |
| `software-engineer` | -- | P-085 (Tech Lead feasibility review), P-086 (Tech Lead debt context) |
| `security-engineer` | -- | P-088 (Security Architect on CARB) |

### Process-to-Org-Role Traceability

| Org Role | Processes Involved | Nature of Involvement |
|----------|-------------------|----------------------|
| Principal Engineer (L7) | P-085 | Authors RFCs; owns cross-org architectural decisions |
| Staff Engineer (L6) | P-085, P-086 | Reviews RFCs; owns quarterly debt analysis and reporting |
| Distinguished Engineer (L8) | P-085, P-087 | Reviews RFCs; approves Tier 3 language exceptions |
| Guild Lead | P-087 | Evaluates and decides Tier 2 language proposals; recommends on Tier 3 |
| Cloud Architect | P-088 | Chairs CARB; announces decisions |
| Security Architect | P-088 | CARB member; evaluates security implications |
| FinOps Engineer | P-088 | CARB member; evaluates cost implications |
| DX Engineer | P-089 | Designs survey; analyzes results; updates platform backlog |
| Director of Engineering | P-086, P-087 | Reviews debt report; allocates remediation capacity; approves Tier 3 exceptions |
| Platform EM | P-089 | Reviews survey findings; owns platform backlog prioritization |
| VP of Engineering | P-085 (escalation), P-089 | Breaks RFC consensus deadlocks; accountable for action on DevEx results |

---

*End of specification.*

---

## Cross-Category Dependencies

### Dependencies FROM Other Categories (Inputs)

| Source Process | Source Category | Consuming Process | Nature |
|---------------|----------------|-------------------|--------|
| P-047 (CARB) | Cat 7: Infrastructure | P-088 (Architecture Pattern Change) | CARB is the operational review process |
| P-006 (Technology Vision Alignment) | Cat 1: Intent & Strategic Alignment | P-088 (Architecture Pattern Change) | Technology vision guides pattern decisions |

### Dependencies TO Other Categories (Outputs)

| Providing Process | Consuming Process | Target Category | Nature |
|------------------|-------------------|-----------------|--------|
| P-085 (RFC) | P-088 (Architecture Pattern Change) | Cat 16 (self) | RFC decisions inform pattern standards |
| P-086 (Technical Debt Tracking) | P-082 (Quarterly Capacity Planning) | Cat 15: Capacity & Resource | Debt remediation allocated in capacity planning |
| P-089 (Developer Experience Survey) | P-044 (Golden Path Adoption) | Cat 7: Infrastructure | Developer NPS measures golden path satisfaction |
| P-089 (Developer Experience Survey) | P-090 (New Engineer Onboarding) | Cat 17: Onboarding | Onboarding experience feeds developer NPS |

## Agent Assignments Summary

| Process | Primary Owner | Supporting Agents |
|---------|--------------|-------------------|
| P-085: RFC (Request for Comments) | staff-principal-engineer (Principal Engineer) | engineering-manager, software-engineer (TL) |
| P-086: Technical Debt Tracking | staff-principal-engineer (Staff Engineer) | engineering-manager, software-engineer (TL) |
| P-087: Language Tier Policy Change | staff-principal-engineer (Guild Lead) | engineering-manager (Director) |
| P-088: Architecture Pattern Change | cloud-engineer (Cloud Architect) | staff-principal-engineer, security-engineer |
| P-089: Developer Experience Survey | platform-engineer (DX Engineer) | engineering-manager (Platform EM) |
