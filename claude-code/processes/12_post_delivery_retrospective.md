# Technical Specification: Post-Delivery & Retrospective Processes (P-070 to P-073)

**Task ID**: Category 12 | **Stage**: 2 (Specification) | **Date**: 2026-04-05
**Session**: auto-orc-20260405-procderive | **Author**: spec-creator agent
**Inputs**: Stage 1 Process Architecture (Category 12), Clarity of Intent process, Engineering Team Structure Guide

---

## Overview

Category 12 contains four processes that close the delivery feedback loop. They measure whether delivered work achieved its intended outcome, extract lessons from project execution, review organizational process health, and score OKR performance. Without these processes, the organization ships software but never learns whether it worked or how to improve.

**Process inventory:**

| ID | Process Name | Cadence | Primary Owner |
|----|-------------|---------|---------------|
| P-070 | Project Post-Mortem Process | Per project completion | product-manager |
| P-071 | Quarterly Process Health Review | Quarterly | engineering-manager (Director/VP) |
| P-072 | OKR Retrospective Process | End of quarter | product-manager |
| P-073 | Post-Launch Outcome Measurement Process | 30/60/90 days post-launch | product-manager |

**Execution order**: P-073 runs first (begins 30 days post-launch), P-070 depends on P-073 data, P-072 consumes P-073 data at quarter end, and P-071 aggregates signals from all other processes quarterly.

---

## P-070: Project Post-Mortem Process

### Purpose

Conduct a blameless retrospective at project completion covering intent alignment, scope adherence, dependency management effectiveness, and sprint execution quality across all four Clarity of Intent stages. The post-mortem produces actionable improvements that feed into the quarterly process health review (P-071).

### Derived From

- Stage 0 research Category 11 (post-delivery learning practices)
- PM + EM + TPM collaborative responsibility model
- Industry post-mortem best practices (blameless retrospective methodology)
- Clarity of Intent process: "How to Know the Process Is Working" section

### Primary Owner Agent

**product-manager** -- The PM owns scheduling, facilitation, and the final post-mortem document. The PM is the natural owner because they hold the Scope Contract, success metrics, and the relationship with the Sponsor who defined the original intent.

### Supporting Agents

| Agent | Role in Process |
|-------|----------------|
| **engineering-manager** | Provides sprint execution data (sprint goal completion rates, velocity, team health signals); co-facilitates the retrospective session; owns action items related to delivery execution |
| **technical-program-manager** | Provides dependency management data (late discoveries, blocked dependencies, escalation frequency); owns action items related to cross-team coordination |

### Stages/Steps

#### Stage 1: Schedule and Announce (Days 1-3 post-completion)

**Owner**: product-manager

1. PM schedules post-mortem within 2 weeks of project completion (non-negotiable deadline)
2. PM sends calendar invite to all participants: PM, EM, TPM, Tech Leads from all involved squads, and the project Sponsor (optional attendee)
3. PM creates a shared pre-read document containing:
   - Link to original Intent Brief
   - Link to final Scope Contract (including all versioned changes)
   - Link to Dependency Charter
   - Summary of Scope Change Requests filed during the project
   - Post-launch outcome data from P-073 (30-day report minimum)

#### Stage 2: Data Preparation (Days 3-7 post-completion)

**Owners**: product-manager, engineering-manager, technical-program-manager (in parallel)

Each agent prepares their quantitative data:

| Agent | Data Prepared |
|-------|--------------|
| **product-manager** | Scope changes filed (count, severity, root cause); final success metric values from P-073; intent alignment assessment (did the delivered product match the Intent Brief outcome?) |
| **engineering-manager** | Sprint goal completion rate across all sprints; DORA metric deltas (deployment frequency, lead time, change failure rate, MTTR) comparing project period to baseline; team health signals from sprint retrospectives |
| **technical-program-manager** | Late dependencies discovered (count and impact); dependency resolution time (average and worst case); escalation frequency; critical path accuracy (predicted vs. actual) |

All data is added to the pre-read document at least 2 business days before the session.

#### Stage 3: Facilitated Post-Mortem Session (90 minutes)

**Facilitator**: product-manager (or a neutral facilitator if the PM is emotionally invested in the outcome)

**Agenda:**

| Time | Activity | Method |
|------|----------|--------|
| 0-10 min | Context setting: restate Intent Brief outcome and final delivery state | PM presents |
| 10-25 min | Quantitative data review | PM, EM, TPM present their data |
| 25-60 min | 4 L's analysis applied to the full project arc | Facilitated group discussion |
| 60-75 min | Intent alignment review: did the final product achieve the Intent Brief outcome? | PM-led discussion using P-073 data |
| 75-90 min | Action item generation and owner assignment | All participants |

**4 L's Analysis Framework:**

| L | Question | Scope |
|---|----------|-------|
| **Loved** | What went well that we should repeat? | Across all 4 Clarity of Intent stages |
| **Learned** | What did we discover that we did not know before? | Technical, process, and organizational learnings |
| **Lacked** | What was missing that would have helped? | Tools, information, capacity, skills |
| **Longed For** | What do we wish we had done differently? | Process changes, earlier decisions, different approaches |

**Ground Rules:**
- Blameless: focus on systems and processes, not individuals
- Evidence-based: every claim should reference data or a specific incident
- Forward-looking: every observation should lead to an actionable improvement

#### Stage 4: Action Item Documentation (Within 24 hours of session)

**Owner**: product-manager

1. PM writes the project post-mortem document (template below)
2. Each action item gets: description, owner agent, due date, and priority
3. Action items entered into RAID Log with owners
4. Post-mortem document shared with Director and all participants
5. Key findings communicated to Director in next weekly EM sync

#### Stage 5: Action Item Tracking

**Owner**: engineering-manager

1. Action items tracked in RAID Log alongside other project risks and issues
2. EM reviews action item progress in weekly EM sync with Director
3. Completed action items marked as resolved with evidence of implementation
4. Outstanding action items at quarter end feed into P-071 (Quarterly Process Health Review)

### Inputs

| Input | Source | Required/Optional |
|-------|--------|-------------------|
| Project RAID Log history | TPM / project documentation | Required |
| Sprint goal completion records | EM / sprint tracking tool | Required |
| Scope Change Request log | PM / Scope Contract version history | Required |
| Post-launch outcome data (30-day minimum) | P-073 output | Required |
| Dependency Charter and resolution records | TPM / Dependency Charter | Required |
| Intent Brief (original) | PM / project documentation | Required |
| Final Scope Contract (latest version) | PM / project documentation | Required |
| DORA metrics for project period | EM / CI-CD pipeline metrics | Recommended |

### Outputs/Artifacts

| Output | Format | Consumer |
|--------|--------|----------|
| **Project post-mortem document** | Markdown document with structured sections (template below) | Director, VP, all project participants, P-071 |
| **Action items for process improvement** | RAID Log entries with owners and due dates | EM (tracking), Director (review) |
| **Retrospective contribution to P-071** | Summary findings and metrics aggregated into quarterly process health data | engineering-manager (Director level) |

**Post-Mortem Document Template:**

```
# Project Post-Mortem: [Project Name]
Date: [Date] | Facilitator: [PM Name]
Participants: [Names and roles]

## 1. Intent Recap
- Original Intent Brief outcome: [verbatim from Intent Brief]
- Strategic context: [from Intent Brief]

## 2. Delivery Summary
- Scope Contract version at completion: [v1.x]
- Scope changes filed: [count] ([major/minor breakdown])
- Sprint goal completion rate: [X%] across [N] sprints
- Total duration: [planned vs. actual]

## 3. Outcome Achievement
- Success metric results (from P-073 30-day report):
  | Metric | Baseline | Target | Actual | Status |
- Intent alignment assessment: [Achieved / Partially Achieved / Not Achieved]

## 4. Quantitative Data
- DORA deltas: [table]
- Late dependencies discovered: [count and impact]
- Escalation frequency: [count]

## 5. 4 L's Analysis
- Loved: [findings]
- Learned: [findings]
- Lacked: [findings]
- Longed For: [findings]

## 6. Action Items
| # | Action | Owner | Due Date | Priority |
```

### Gate/Checkpoint

**Gate**: Director reviews post-mortem action items in weekly EM sync

**Gate criteria:**
- Post-mortem document is complete (all sections populated)
- Action items are specific, measurable, and have named owners
- At least one action item addresses a systemic process improvement (not just a one-off fix)
- Director confirms action items are tracked in RAID Log

**Escalation**: If post-mortem is not held within 2 weeks of project completion, Director escalates to VP in the next leadership sync.

### Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Timeliness | Calendar days from project completion to post-mortem session | Within 14 calendar days |
| Data quality | Quantitative data used alongside qualitative discussion | All 3 data categories (PM, EM, TPM) represented |
| Actionability | Action items are specific and trackable | Each action item has owner, due date, and measurable completion criteria |
| Follow-through | Action items completed by due date | Greater than 80% completion rate |
| Participation | Key roles attend the session | PM, EM, TPM, and at least 1 TL present |

### Dependencies

| Dependency | Direction | Description |
|------------|-----------|-------------|
| P-073 | Inbound | Post-Launch Outcome Measurement provides 30-day data that P-070 consumes for intent alignment assessment |
| P-071 | Outbound | Post-mortem findings and action item completion rates feed into Quarterly Process Health Review |
| P-028 | Inbound | Sprint Retrospective action items and team health signals feed into the post-mortem data preparation |
| Project completion | Inbound | Trigger event: the project must be complete (all deliverables accepted per Scope Contract DoD) |

### Traceability

| Trace Point | Reference |
|-------------|-----------|
| Clarity of Intent Stage 1 | Intent Brief outcome statement is the benchmark for intent alignment assessment |
| Clarity of Intent Stage 2 | Scope Contract deliverables and Definition of Done are the benchmark for scope adherence |
| Clarity of Intent Stage 3 | Dependency Charter is the benchmark for dependency management effectiveness |
| Clarity of Intent Stage 4 | Sprint Kickoff Briefs and sprint goal records are the benchmark for execution quality |
| Clarity of Intent "How to Know the Process Is Working" | Five health signals (scope changes, late dependencies, sprint goal rate, intent alignment, time-to-first-sprint) are measured per-project here and aggregated in P-071 |

---

## P-071: Quarterly Process Health Review

### Purpose

Review the Clarity of Intent process health signals quarterly at Director/VP level. Compare metrics to prior quarters, identify degrading signals, perform root cause analysis, and make evidence-based process adjustments. This is the organization's formal drift-detection mechanism that prevents process entropy.

### Derived From

- Stage 0 research Category 11 (process governance and continuous improvement)
- Clarity of Intent "How to Know the Process Is Working" section (five health signals)
- Director/VP governance responsibility as defined in org structure

### Primary Owner Agent

**engineering-manager** (Director and VP level) -- Directors aggregate metrics across their squads; VPs review cross-Director trends. The EM hierarchy owns this because process health is a delivery accountability that rolls up through the engineering management chain.

### Supporting Agents

| Agent | Role in Process |
|-------|----------------|
| **product-manager** | Contributes scope change metrics, OKR scoring data, and intent alignment observations across projects |
| **technical-program-manager** | Contributes dependency discovery metrics, cross-team coordination effectiveness data, and RAID Log trends |

### Stages/Steps

#### Stage 1: Metric Aggregation (Week 1 of quarter review period)

**Owner**: engineering-manager (each Director for their squads)

Each Director aggregates the following metrics across all projects completed in the quarter:

| Metric | Source | Target |
|--------|--------|--------|
| Scope changes per project | Scope Change Request logs from PM | Less than 2 major changes per project; declining quarter-over-quarter |
| Late dependency discovery | Dependency Charter vs. actual dependency records from TPM | Less than 1 per project |
| Sprint goal completion rate | Sprint tracking records from EM | Greater than 80% |
| Intent alignment | Random engineer survey: "Can you explain your project's purpose in one sentence?" | Consistently yes |
| Time-to-first-sprint | Calendar days from project kickoff to first sprint start | 8-12 days; stable, not growing |
| Audit finding SLA compliance rate | Security and compliance tracking from AppSec | Greater than 95% within SLA |

**Data collection method**: Directors pull data from RAID Logs, sprint tracking tools, Scope Contract version histories, and P-070 post-mortem documents. Each Director produces a one-page metrics summary for their org.

#### Stage 2: Cross-Director Trend Analysis (Week 1-2)

**Owner**: engineering-manager (VP level)

1. VP collects Director-level metrics summaries
2. VP compares current quarter metrics to prior quarter (trending analysis)
3. VP identifies signals that are: improving, stable, or degrading
4. VP produces a trend summary document highlighting:
   - Metrics that improved (and what drove the improvement)
   - Metrics that degraded (flagged for root cause analysis)
   - Metrics that remained stable (confirm they are within target range)

#### Stage 3: Root Cause Analysis for Degrading Signals (Week 2)

**Owner**: engineering-manager (VP), with support from PM and TPM

For each degrading signal:

1. Identify the specific projects or squads driving the degradation
2. Review P-070 post-mortem documents for those projects
3. Interview the PM, EM, and TPM from affected projects (15-minute focused conversations)
4. Determine whether the root cause is:
   - **Process gap**: The Clarity of Intent process does not address this scenario
   - **Process non-compliance**: The process exists but was not followed
   - **Capacity constraint**: The process was followed but insufficient resources caused the issue
   - **External factor**: Something outside the team's control caused the issue

#### Stage 4: Process Adjustment Decisions (Week 2-3)

**Owner**: engineering-manager (VP + Directors)

1. VP and Directors meet (60 minutes) to review findings
2. For each degrading signal with an identified root cause, decide on one of:
   - **Adjust process**: Modify a specific Clarity of Intent stage or gate criteria
   - **Add enforcement**: Introduce a new checkpoint or automated check
   - **Train**: Address non-compliance through targeted coaching
   - **Accept**: Document the risk and accept current state (with justification)
3. Each adjustment decision is documented with: what changed, why, effective date, and owner

#### Stage 5: Communication and Implementation (Week 3)

**Owner**: engineering-manager (Directors)

1. Process adjustments documented in a Quarterly Process Health Report
2. Report shared with all EMs, PMs, and TPMs
3. Directors communicate changes in their weekly EM syncs
4. Updated process documentation produced within 2 weeks of decision
5. Next quarter's review checks whether adjustments had the intended effect

### Inputs

| Input | Source | Required/Optional |
|-------|--------|-------------------|
| P-070 post-mortem documents from the quarter | product-manager | Required |
| Scope Change Request logs (all projects) | product-manager | Required |
| Dependency discovery records (all projects) | technical-program-manager | Required |
| Sprint goal completion records (all squads) | engineering-manager | Required |
| Audit finding SLA compliance data | security-engineer / AppSec | Required |
| Prior quarter's Process Health Report | engineering-manager (VP) | Required (except first quarter) |
| P-072 OKR Retrospective outputs | product-manager | Recommended |

### Outputs/Artifacts

| Output | Format | Consumer |
|--------|--------|----------|
| **Quarterly Process Health Report** | Markdown document with metrics, trends, root cause analysis, and decisions | VP, Directors, all EMs, PMs, TPMs |
| **Process adjustment decisions** | Documented changes with owner, effective date, and rationale | All process participants |
| **Updated process documentation** | Revised Clarity of Intent process docs (if applicable) | All engineering teams |

**Quarterly Process Health Report Template:**

```
# Quarterly Process Health Report: Q[N] [Year]
Prepared by: [VP Name] | Review date: [Date]

## 1. Metric Summary
| Metric | Q[N-1] Value | Q[N] Value | Trend | Target | Status |

## 2. Improving Signals
- [Metric]: improved from [X] to [Y] because [root cause]

## 3. Degrading Signals
- [Metric]: degraded from [X] to [Y]
  - Root cause: [analysis]
  - Decision: [adjust/enforce/train/accept]
  - Action: [specific change]
  - Owner: [name/role]
  - Effective: [date]

## 4. Stable Signals
- [Metric]: stable at [X] (within target range)

## 5. Process Adjustments This Quarter
| # | Change | Rationale | Owner | Effective Date |

## 6. Follow-Up from Prior Quarter Adjustments
| # | Prior Adjustment | Expected Effect | Actual Effect | Status |
```

### Gate/Checkpoint

**Gate**: VP confirms Quarterly Process Health Report is complete and process adjustments are communicated

**Gate criteria:**
- All six metrics are measured and trended (not spot-checked)
- Prior quarter comparison is included
- Degrading signals have root cause analysis and a decision
- At least 1 process adjustment per quarter is evidence-based (not zero adjustments and not arbitrary changes)
- Report is shared with all EMs, PMs, and TPMs within 3 weeks of quarter end

### Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Timeliness | Review held on schedule | Within first 3 weeks of new quarter |
| Completeness | All 6 metrics measured and trended | 100% coverage |
| Evidence-based adjustment | At least 1 process adjustment per quarter based on data | Minimum 1 per quarter |
| Follow-through | Prior quarter adjustments assessed for effectiveness | 100% of prior adjustments reviewed |
| Communication | Report distributed to all process participants | All EMs, PMs, TPMs receive report |

### Dependencies

| Dependency | Direction | Description |
|------------|-----------|-------------|
| P-070 | Inbound | Project post-mortem documents provide per-project process health data |
| P-072 | Inbound | OKR Retrospective provides OKR scoring data that informs process effectiveness |
| P-073 | Inbound | Post-Launch Outcome Measurement provides success metric data used in intent alignment assessment |
| P-028 | Inbound | Sprint Retrospective action item completion rates contribute to sprint execution quality metrics |
| All Clarity of Intent stages (P-004 through P-022) | Inbound | Process health metrics are derived from how well these stages execute |

### Traceability

| Trace Point | Reference |
|-------------|-----------|
| Clarity of Intent "How to Know the Process Is Working" | The five health signals (scope changes, late dependencies, sprint goal rate, intent alignment, time-to-first-sprint) are directly adopted as the core metrics for this review |
| Engineering Team Structure: Director role | Directors own delivery accountability for their domain, making them the natural aggregation point for process health metrics |
| Engineering Team Structure: VP role | VPs own cross-org engineering standards, making them the natural decision point for process adjustments |
| P-074 (RAID Log Maintenance) | Audit finding SLA compliance metric is sourced from RAID Log data reviewed in quarterly process health review |

---

## P-072: OKR Retrospective Process

### Purpose

Score all OKR Key Results at quarter end on a 0.0-1.0 scale, conduct an honest retrospective on why each KR scored as it did, publish scores and learnings transparently, and feed insights into next quarter's OKR setting. This process ensures the organization does not operate on false confidence from unscored or privately scored OKRs.

### Derived From

- Stage 0 research Category 11 (OKR lifecycle and quarterly review practices)
- PM role responsibility: "tracks OKR key results" (Engineering Team Structure Guide)
- Quarterly OKR cycle as defined in organizational delivery methodology
- P-005 (Strategic Prioritization) which feeds the OKR cascade

### Primary Owner Agent

**product-manager** -- The PM owns OKR key results tracking throughout the quarter and is the natural owner of scoring and retrospective. The PM has the closest relationship to the success metrics and delivery data needed to score accurately.

### Supporting Agents

| Agent | Role in Process |
|-------|----------------|
| **engineering-manager** | Provides delivery execution context (what was shipped, what was delayed, capacity constraints); co-retrospects on KRs related to engineering execution quality |

### Stages/Steps

#### Stage 1: KR Scoring (Last week of quarter)

**Owner**: product-manager

For each Key Result defined at the start of the quarter:

1. PM retrieves the current metric value from the measurement source defined in the KR
2. PM scores the KR on a 0.0-1.0 scale using the standard OKR scoring rubric:

| Score Range | Meaning |
|-------------|---------|
| 0.0-0.3 | Failed to make meaningful progress |
| 0.4-0.6 | Made progress but fell significantly short of target |
| 0.7-0.9 | Near target or at target (ideal "stretch" range) |
| 1.0 | Fully achieved or exceeded (may indicate target was not ambitious enough) |

3. PM documents the raw data, measurement method, and any caveats for each score
4. **Rule**: No KR may be scored as "in progress" at quarter end. Every KR gets a numeric score.

#### Stage 2: PM + EM Retrospective Session (60 minutes)

**Owner**: product-manager (facilitates), engineering-manager (co-participant)

For each KR, PM and EM discuss:

1. **What drove the score?** Identify the primary factors (positive or negative)
2. **Root cause for under-performing KRs**: Was the issue:
   - **Target wrong**: The target was unrealistic given constraints known at quarter start
   - **Approach wrong**: The solution strategy did not achieve the intended effect
   - **Capacity wrong**: Insufficient engineering capacity was allocated
   - **External factor**: Something outside the team's control intervened
3. **Learnings**: What would the team do differently if attempting this KR again?
4. **Carry-forward decision**: Should this KR (or a refined version) carry into next quarter?

#### Stage 3: Documentation (Within 2 business days of session)

**Owner**: product-manager

PM produces the OKR Scoring Document:

```
# OKR Retrospective: Q[N] [Year] - [Squad/Team Name]
Date: [Date] | PM: [Name] | EM: [Name]

## Objective: [Objective statement]

### KR 1: [Key Result statement]
- Score: [0.0-1.0]
- Data: [raw metric value, measurement source]
- Root cause: [target/approach/capacity/external]
- Learning: [specific, honest assessment]
- Carry forward: [Yes/No/Modified - with rationale]

### KR 2: [Key Result statement]
[same structure]

## Summary
- Average score: [X.X]
- Top learning: [one-sentence summary]
- Recommendation for next quarter: [specific input for OKR setting]
```

#### Stage 4: Publication (Within 3 business days of session)

**Owner**: product-manager

1. OKR scores and learnings published to the team (all squad members see the scores)
2. OKR scores and learnings shared with Director
3. Director aggregates squad-level OKR scores for VP review
4. Publication channel: team wiki / shared document repository (not buried in email)

#### Stage 5: Feed into Next Quarter OKR Setting

**Owner**: product-manager

1. Learnings from under-performing KRs explicitly referenced during next quarter's OKR planning
2. Carry-forward KRs included in the initial OKR draft for next quarter
3. Target calibration: if KRs consistently score 1.0, targets are being set too conservatively; if consistently below 0.4, targets are unrealistic or the approach needs fundamental change

### Inputs

| Input | Source | Required/Optional |
|-------|--------|-------------------|
| OKR definitions (Objectives and Key Results for the quarter) | PM / OKR tracking tool | Required |
| Delivery data (what was shipped and when) | EM / sprint tracking tool | Required |
| Success metric data from P-073 | product-manager / analytics | Required (for KRs with post-launch metrics) |
| P-005 Strategic Prioritization context | PM / strategic planning documents | Recommended |

### Outputs/Artifacts

| Output | Format | Consumer |
|--------|--------|----------|
| **OKR Scoring Document** (0.0-1.0 per KR) | Markdown document per squad/team | Team members, Director, VP |
| **Public learning summary** | Aggregated learnings across squads (Director produces) | All engineering teams, P-071 |
| **Next quarter OKR input** | Carry-forward KRs and target calibration recommendations | PM (for next quarter OKR planning), P-005 |

### Gate/Checkpoint

**Gate**: Director confirms all squads have published OKR scores and learnings

**Gate criteria:**
- All KRs scored on 0.0-1.0 scale (no "in progress" or "TBD" scores)
- Learnings are specific and honest (not generic platitudes)
- Scores and learnings are published publicly (not kept private between PM and EM)
- Under-performing KRs (below 0.4) have documented root cause analysis
- Director has aggregated view across all squads

### Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Completeness | All KRs scored with numeric value | 100% scored, 0% "in progress" |
| Honesty | Learnings reference specific causes, not vague statements | Every under-performing KR has one of: target/approach/capacity/external root cause |
| Transparency | Scores published to team and Director | 100% published within 1 week of quarter end |
| Timeliness | Retrospective session held and document produced | Within last week of quarter + 3 business days |
| Feed-forward | Learnings referenced in next quarter OKR planning | Carry-forward decisions documented for every KR below 0.7 |

### Dependencies

| Dependency | Direction | Description |
|------------|-----------|-------------|
| P-073 | Inbound | Post-Launch Outcome Measurement provides success metric data used to score delivery-related KRs |
| P-005 | Bidirectional | Strategic Prioritization feeds OKR cascade; OKR Retrospective provides input for next cascade |
| P-071 | Outbound | OKR scoring data and learnings feed into Quarterly Process Health Review |
| Quarter end | Inbound | Trigger event: the quarter must end for scoring to occur |

### Traceability

| Trace Point | Reference |
|-------------|-----------|
| Clarity of Intent Stage 2, Section 5 | Scope Contract success metrics directly correspond to KR measurement data |
| Engineering Team Structure: PM role | "Tracks OKR key results" is an explicit PM responsibility |
| Engineering Team Structure: EM role | "Delivery outcomes" accountability means the EM must co-own the retrospective |
| Clarity of Intent "How to Know the Process Is Working" | Intent alignment signal (can a random engineer explain the project purpose?) validates whether OKR communication was effective |

---

## P-073: Post-Launch Outcome Measurement Process

### Purpose

Measure the success metrics defined in the Scope Contract at 30, 60, and 90 days post-launch and report to the Sponsor and Director. This is the organization's proof mechanism: it closes the loop between intent (Stage 1) and outcome (post-delivery). Without P-073, teams ship software but never verify whether it achieved the business outcome that justified building it.

### Derived From

- Clarity of Intent Stage 2, Section 5 (Success Metrics): the Scope Contract defines the metrics, baselines, targets, measurement methods, and timelines that P-073 measures
- Post-delivery accountability mechanism: organizational commitment to outcome verification
- PM role responsibility for stakeholder reporting and outcome tracking

### Primary Owner Agent

**product-manager** -- The PM defined the success metrics in the Scope Contract, owns the relationship with the Sponsor, and has access to the analytics and business data needed for measurement. The PM is accountable for proving the project achieved its intended outcome.

### Supporting Agents

| Agent | Role in Process |
|-------|----------------|
| **data-engineer** | Provides measurement data from analytics dashboards, data pipelines, and backend logs; validates data quality and measurement methodology; builds or maintains the queries/dashboards needed for measurement |
| **sre** | Provides reliability and performance data (latency, error rates, availability) relevant to success metrics that include performance targets; validates that measurement infrastructure is collecting data correctly |

### Stages/Steps

#### Stage 0: Measurement Planning (At Scope Lock, before launch)

**Owner**: product-manager

**This stage happens during Scope Lock (P-013), not after launch.** This is critical: measurement dates and methods must be defined before the project ships, not retrofitted afterward.

1. PM extracts success metrics from Scope Contract Section 5
2. PM schedules 30/60/90-day measurement dates in calendar (anchored to planned launch date)
3. PM confirms with data-engineer that measurement infrastructure exists:
   - Analytics events are instrumented and collecting data
   - Dashboard or query for each metric is built or planned
   - Baseline values are recorded and validated
4. PM confirms with SRE that performance-related metrics have monitoring in place
5. PM documents the measurement plan:

| Metric | Baseline | Target | Measurement Source | Dashboard/Query | 30-Day Date | 60-Day Date | 90-Day Date |
|--------|----------|--------|--------------------|-----------------|-------------|-------------|-------------|

#### Stage 1: 30-Day Measurement

**Owner**: product-manager, supported by data-engineer

1. PM retrieves metric data from the defined measurement source
2. Data-engineer validates data quality: confirms events are firing correctly, no data gaps, sample size is sufficient
3. PM compares current metric value to:
   - Baseline (from Scope Contract)
   - Target (from Scope Contract)
   - Expected trajectory (is the metric moving in the right direction?)
4. PM writes the 30-Day Outcome Report:

```
# 30-Day Outcome Report: [Project Name]
Date: [Date] | PM: [Name] | Launch Date: [Date]

## Metrics
| Metric | Baseline | Target | 30-Day Actual | Direction | Confidence |

## Assessment
- On track / Needs attention / Off track
- [Narrative explanation for each metric]

## Data Quality Notes
- [Any caveats about measurement reliability]

## Next Measurement
- 60-day measurement scheduled for: [Date]
```

5. PM presents 30-Day report to Director

#### Stage 2: 60-Day Measurement

**Owner**: product-manager, supported by data-engineer and sre

1. Same measurement process as 30-day
2. **Critical trigger**: If any metric is significantly off-track at 60 days (below 50% of the way to target), PM and EM jointly investigate the root cause:
   - Is the feature being used as expected? (Check adoption/usage data)
   - Is there a technical issue affecting performance? (SRE provides data)
   - Was the target realistic given what we now know? (Re-examine assumptions)
   - Is there an external factor (market change, competitor action, seasonal effect)?
3. Investigation findings documented in the 60-Day report
4. If off-track: PM and EM propose corrective actions (feature iteration, performance optimization, additional instrumentation) or recommend adjusting the target with justification

#### Stage 3: 90-Day Measurement (Final)

**Owner**: product-manager, supported by data-engineer

1. Same measurement process as 30-day and 60-day
2. PM writes the final 90-Day Outcome Report with a definitive assessment:
   - **Achieved**: Metric met or exceeded target
   - **Partially achieved**: Metric improved significantly from baseline but did not reach target
   - **Not achieved**: Metric did not improve meaningfully or moved in wrong direction
3. PM presents 90-Day report to Sponsor and Director
4. Report becomes a formal input to P-070 (Project Post-Mortem) and P-072 (OKR Retrospective)

**90-Day Outcome Report Template:**

```
# 90-Day Outcome Report: [Project Name]
Date: [Date] | PM: [Name] | Launch Date: [Date]

## Final Metrics
| Metric | Baseline | Target | 30-Day | 60-Day | 90-Day | Verdict |

## Intent Alignment
- Original Intent Brief outcome: [verbatim]
- Assessment: [Achieved / Partially Achieved / Not Achieved]
- Evidence: [data-backed justification]

## Trajectory
[Chart or table showing metric progression over 30/60/90 days]

## Learnings
- [What we learned about the problem space]
- [What we learned about our measurement approach]
- [What we would do differently]

## Recommendations
- [Continue monitoring / Iterate on feature / Accept current state / Investigate further]
```

### Inputs

| Input | Source | Required/Optional |
|-------|--------|-------------------|
| Scope Contract Section 5 (Success Metrics) | PM / Scope Contract | Required |
| Analytics event data | Data pipelines / analytics dashboards | Required |
| SRE performance data (latency, error rates, availability) | SRE / monitoring tools | Required (for metrics with performance targets) |
| Baseline metric values (recorded at Scope Lock) | PM / Scope Contract | Required |
| Feature usage/adoption data | Analytics / product analytics tools | Recommended |

### Outputs/Artifacts

| Output | Format | Consumer |
|--------|--------|----------|
| **30-Day Outcome Report** | Markdown document | Director |
| **60-Day Outcome Report** | Markdown document (includes investigation findings if off-track) | Director, EM (if investigation triggered) |
| **90-Day Outcome Report** (final) | Markdown document with definitive assessment | Sponsor, Director, P-070, P-072 |
| **Target vs. actuals comparison** | Data within each report | All stakeholders |
| **Escalation** (if significantly off-track) | Documented investigation with corrective action proposal | Director, PM, EM |

### Gate/Checkpoint

**Gate 1**: Director review of 30-Day report
- Report is complete with all metrics measured
- Data quality is validated by data-engineer
- Direction assessment (on track / needs attention / off track) is provided for each metric

**Gate 2**: Sponsor review of 90-Day report
- All metrics have final values with 30/60/90-day trajectory
- Intent alignment assessment is explicit (Achieved / Partially Achieved / Not Achieved)
- Learnings and recommendations are documented
- Sponsor confirms the assessment aligns with their understanding of the outcome

### Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Measurement timeliness | Reports produced on scheduled dates | All 3 reports within 5 business days of scheduled date |
| Measurement completeness | All Scope Contract success metrics measured | 100% of defined metrics have values in each report |
| Data validation | Data-engineer confirms measurement quality | Data quality sign-off on every report |
| Stakeholder reporting | Reports presented to Director (30-day) and Sponsor (90-day) | 100% of reports presented to designated stakeholder |
| Off-track investigation | Significantly off-track metrics at 60 days trigger investigation | 100% of off-track metrics investigated within 1 week |
| Feed-forward | 90-day report consumed by P-070 and P-072 | Report referenced in post-mortem and OKR retrospective |

### Dependencies

| Dependency | Direction | Description |
|------------|-----------|-------------|
| P-013 (Scope Lock Gate) | Inbound | Scope Contract defines the success metrics, baselines, targets, and measurement methods that P-073 measures. Without a locked Scope Contract, there is nothing to measure against. |
| P-048 (Production Release Management) | Inbound | Production release triggers the 30/60/90-day measurement clock. The launch date anchors all measurement dates. |
| P-070 | Outbound | 30-day data (minimum) feeds into Project Post-Mortem for intent alignment assessment |
| P-072 | Outbound | Success metric data feeds into OKR Retrospective for KR scoring |
| P-071 | Outbound | Outcome measurement results contribute to quarterly process health assessment |
| Data pipeline availability | Inbound | Analytics infrastructure must be collecting the relevant events before launch |

### Traceability

| Trace Point | Reference |
|-------------|-----------|
| Clarity of Intent Stage 1 (Intent Brief) | The outcome statement in the Intent Brief is the ultimate benchmark: did we achieve the intended business outcome? |
| Clarity of Intent Stage 2, Section 5 (Success Metrics) | Every metric measured in P-073 traces directly to the Success Metrics table in the Scope Contract. The baseline, target, measurement method, and timeline are all defined there. |
| Clarity of Intent Stage 2, Section 1 (Outcome Restatement) | The Scope Contract's outcome restatement ensures P-073 measures against the same outcome the Sponsor approved |
| Engineering Team Structure: PM role | "Tracks OKR key results; manages stakeholder expectations" -- P-073 is the operational mechanism for this responsibility |
| Engineering Team Structure: Data Engineer role | "Data pipeline design and maintenance; data quality monitoring" -- Data Engineer's role in P-073 is a direct application of their core responsibilities |
| Engineering Team Structure: SRE role | "Owns SLOs and error budgets for defined services" -- SRE provides performance data for metrics that include reliability or latency targets |

---

## Cross-Process Dependency Map

```
                    ┌─────────────────────────┐
                    │  P-013: Scope Lock Gate  │
                    │  (defines metrics)       │
                    └──────────┬──────────────┘
                               │
                    ┌──────────▼──────────────┐
                    │  P-048: Production       │
                    │  Release (launch)        │
                    └──────────┬──────────────┘
                               │
                    ┌──────────▼──────────────┐
              ┌─────│  P-073: Post-Launch      │─────┐
              │     │  Outcome Measurement     │     │
              │     │  (30/60/90 days)         │     │
              │     └──────────────────────────┘     │
              │                                       │
    ┌─────────▼────────────┐           ┌─────────────▼──────────┐
    │  P-070: Project      │           │  P-072: OKR            │
    │  Post-Mortem         │           │  Retrospective         │
    │  (per project)       │           │  (end of quarter)      │
    └─────────┬────────────┘           └─────────────┬──────────┘
              │                                       │
              └──────────────┬────────────────────────┘
                             │
                  ┌──────────▼──────────────┐
                  │  P-071: Quarterly       │
                  │  Process Health Review  │
                  │  (quarterly)            │
                  └─────────┬──────────────┘
                            │
                  ┌─────────▼──────────────┐
                  │  Process Adjustments   │
                  │  → Next quarter        │
                  └────────────────────────┘
```

---

## Agent Responsibility Matrix (RACI)

| Activity | product-manager | engineering-manager | technical-program-manager | data-engineer | sre |
|----------|:-:|:-:|:-:|:-:|:-:|
| **P-070: Schedule post-mortem** | R/A | I | I | - | - |
| **P-070: Prepare quantitative data** | R | R | R | - | - |
| **P-070: Facilitate session** | R/A | C | C | - | - |
| **P-070: Write post-mortem doc** | R/A | C | C | - | - |
| **P-070: Track action items** | I | R/A | C | - | - |
| **P-071: Aggregate metrics** | C | R/A | C | - | - |
| **P-071: Cross-Director trend analysis** | C | R/A (VP) | C | - | - |
| **P-071: Root cause analysis** | C | R/A | C | - | - |
| **P-071: Process adjustment decisions** | C | R/A | C | - | - |
| **P-072: Score KRs** | R/A | C | - | - | - |
| **P-072: Retrospective session** | R/A | R | - | - | - |
| **P-072: Publish scores** | R/A | I | - | - | - |
| **P-073: Plan measurements (at Scope Lock)** | R/A | - | - | C | C |
| **P-073: 30-day measurement** | R/A | - | - | R | C |
| **P-073: 60-day measurement + investigation** | R/A | R (if off-track) | - | R | R |
| **P-073: 90-day measurement (final)** | R/A | - | - | R | C |
| **P-073: Present to Sponsor** | R/A | I | - | - | - |

R = Responsible, A = Accountable, C = Consulted, I = Informed

---

## Risk Analysis

| Risk | Severity | Affected Process | Mitigation |
|------|----------|-----------------|------------|
| Post-mortems not held within 2-week window | MEDIUM | P-070 | Director tracks post-mortem scheduling in weekly EM sync; escalates if overdue |
| Quantitative data unavailable for post-mortem | MEDIUM | P-070 | Data preparation stage starts immediately after project completion; PM confirms data sources exist before scheduling |
| Process health review becomes a checkbox exercise | MEDIUM | P-071 | VP enforces evidence-based adjustments; at least 1 adjustment per quarter required |
| OKR scores inflated to avoid accountability | LOW | P-072 | Scores must reference raw data; Director reviews for consistency; public publication creates social accountability |
| Analytics instrumentation missing or broken at launch | HIGH | P-073 | Measurement planning happens at Scope Lock (Stage 0), not after launch; data-engineer validates instrumentation before launch |
| 30/60/90-day measurements skipped due to new project priorities | HIGH | P-073 | Measurement dates scheduled at Scope Lock and visible in team calendar; Director review of 30-day report creates accountability checkpoint |
| Off-track metrics at 60 days not investigated | MEDIUM | P-073 | Investigation is a mandatory step, not optional; Director review of 60-day report checks for investigation when metrics are off-track |
| Post-mortem action items never completed | MEDIUM | P-070 | EM tracks action items in RAID Log; Director reviews in weekly sync; completion rate is a P-071 metric |

---

## Implementation Notes

### Tooling Requirements

| Process | Tooling Need |
|---------|-------------|
| P-070 | Shared document template for post-mortem; RAID Log integration for action items |
| P-071 | Metrics dashboard or spreadsheet for quarterly trending; report template |
| P-072 | OKR tracking tool with 0.0-1.0 scoring capability; publication channel (wiki or shared docs) |
| P-073 | Analytics dashboards for success metrics; calendar integration for measurement reminders; report template |

### Cadence Summary

| Process | Trigger | Frequency |
|---------|---------|-----------|
| P-070 | Project completion | Per project (within 2 weeks of completion) |
| P-071 | Quarter boundary | Quarterly (first 3 weeks of new quarter) |
| P-072 | Quarter boundary | Quarterly (last week of quarter + 3 business days) |
| P-073 | Production launch | Per project (30/60/90 days post-launch) |

### Sequencing Constraints

1. P-073 must begin measurement planning at Scope Lock (P-013), before the project launches
2. P-073 30-day data must be available before P-070 post-mortem is held
3. P-072 occurs at quarter end; P-073 data feeds into KR scoring
4. P-071 occurs at the start of the new quarter and aggregates data from P-070, P-072, and P-073
5. P-071 process adjustments are communicated before the new quarter's projects enter Scope Lock

---

*End of specification.*

---

## Cross-Category Dependencies

### Dependencies FROM Other Categories (Inputs)

| Source Process | Source Category | Consuming Process | Nature |
|---------------|----------------|-------------------|--------|
| P-013 (Scope Lock Gate) | Cat 2: Scope & Contract | P-073 (Post-Launch Outcome Measurement) | Scope Contract defines success metrics to measure |
| P-048 (Production Release Mgmt) | Cat 7: Infrastructure | P-073 (Post-Launch Outcome Measurement) | Release enables measurement |

### Dependencies TO Other Categories (Outputs)

| Providing Process | Consuming Process | Target Category | Nature |
|------------------|-------------------|-----------------|--------|
| P-072 (OKR Retrospective) | P-078 (OKR Cascade Communication) | Cat 14: Communication | Learnings feed next OKR cascade |
| P-071 (Quarterly Process Health Review) | All categories | All | Process adjustments affect all processes |

### Internal Dependency Graph

```
P-073 (Post-Launch Outcome Measurement) -- 30-day data --> P-070 (Project Post-Mortem)
P-073 (Post-Launch Outcome Measurement) -- metric data --> P-072 (OKR Retrospective)
P-070 (Project Post-Mortem) -- action items --> P-071 (Quarterly Process Health Review)
```

## Agent Assignments Summary

| Process | Primary Owner | Supporting Agents |
|---------|--------------|-------------------|
| P-070: Project Post-Mortem | product-manager | engineering-manager, technical-program-manager |
| P-071: Quarterly Process Health Review | engineering-manager (Director + VP) | product-manager, technical-program-manager |
| P-072: OKR Retrospective | product-manager | engineering-manager |
| P-073: Post-Launch Outcome Measurement | product-manager | data-engineer, sre |
