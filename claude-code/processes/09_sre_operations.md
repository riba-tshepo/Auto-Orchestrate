# Technical Specification: Site Reliability & Operations Processes (P-054 to P-057)

**Category**: 9 — Site Reliability & Operations | **Stage**: 2 (Specification) | **Date**: 2026-04-05
**Session**: auto-orc-20260405-procderive | **Author**: spec-creator agent
**Inputs**: Process Architecture (Stage 1), clarity_of_intent.md, Engineering_Team_Structure_Guide.md

---

## Overview

This specification defines four processes that govern how the organization establishes, monitors, and defends production reliability. Together they form a closed loop: SLOs define what reliable means (P-054), incident response activates when reliability is breached (P-055), post-mortems extract learning from failures (P-056), and on-call rotation management ensures the human system sustaining reliability is itself sustainable (P-057).

The primary owner across all four processes is the **sre** agent (Site Reliability Engineer, L4-L6, and SRE Lead). The SRE team sits under VP of Platform Engineering > Platform Engineering Director > SRE Lead, as defined in the Engineering Team Structure Guide.

### Process Summary Table

| Process ID | Process Name | Primary Owner | Risk Level | Cadence |
|------------|-------------|---------------|------------|---------|
| P-054 | SLO Definition and Review | sre | HIGH | Per-service + quarterly review |
| P-055 | Incident Response | sre | HIGH | Event-driven (production incidents) |
| P-056 | Post-Mortem | sre | HIGH | Event-driven (SEV-1/SEV-2 resolution) |
| P-057 | On-Call Rotation Management | sre (SRE Lead) | HIGH | Weekly review + quarterly rotation review |

### Cross-Process Dependencies

```
P-009 (Success Metrics) ──► P-054 (SLO Definition)
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
               P-055        P-057       P-059
          (Incident      (On-Call    (Runbook
           Response)     Rotation)   Authoring)
                    │
                    ▼
               P-056
          (Post-Mortem)
                    │
                    ▼
               P-074
          (RAID Log)
```

---

## P-054: SLO Definition and Review Process

### 1. Identity

| Field | Value |
|-------|-------|
| **Process ID** | P-054 |
| **Process Name** | SLO Definition and Review Process |
| **Purpose** | SRE negotiates Service Level Objectives with product teams for every production service. Error budget calculated from SLOs. Error budget burn reviewed quarterly; reliability investments adjusted accordingly. |
| **Derived From** | Stage 0 research Category 9; SRE role responsibilities; reliability engineering principles |

### 2. Ownership

| Role | Responsibility |
|------|---------------|
| **Primary Owner Agent** | sre |
| **Supporting Agents** | product-manager (PM agrees to SLO targets); engineering-manager (EM understands reliability obligations) |
| **Organizational Reporting** | SRE Lead reports to Platform Engineering Director, under VP of Platform Engineering |

### 3. Stages and Steps

| Stage | Step | Actor | Description | Duration |
|-------|------|-------|-------------|----------|
| 1 | Service Assessment | sre + software-engineer (Tech Lead) | Inventory the service: architecture, user-facing endpoints, data flows, blast radius. Assess business criticality tier (Tier-1 revenue-critical, Tier-2 business-important, Tier-3 internal/low-impact). | 1-2 days |
| 2 | SLO Negotiation | sre + product-manager + engineering-manager | Define SLO indicators for each service: availability (uptime percentage), latency (P50/P95/P99 targets), error rate (percentage of 5xx responses). PM validates that targets align with user expectations and business requirements. EM confirms team can sustain the reliability investment. | 1-2 days |
| 3 | SLO Documentation | sre | Produce SLO document per service containing: target percentages, measurement window (rolling 30-day default), error budget calculation formula, escalation thresholds. | 0.5 days |
| 4 | Monitoring Configuration | sre | Configure monitoring and alerting to track SLO compliance in real-time. Dashboards created in observability platform (Grafana/Datadog). Alert thresholds set: warning at 50% error budget consumed, critical at 80% consumed. | 1-2 days |
| 5 | Quarterly Error Budget Review | sre + product-manager + engineering-manager | Review error budget burn for each service. If error budget exhausted: reliability sprint triggered and feature work paused until budget replenished. If error budget healthy (>50% remaining): consider relaxing SLO or reducing reliability investment. | Quarterly, 60-minute meeting |

### 4. Inputs

| Input | Source | Required/Optional |
|-------|--------|-------------------|
| Service architecture documentation | software-engineer (Tech Lead) | Required |
| User expectations and business criticality | product-manager | Required |
| Historical reliability data (uptime, latency, error rates) | Observability platform | Required |
| Success Metrics from Scope Contract | P-009 (Success Metrics Definition Process) | Required for new services |
| Previous quarter's error budget burn data | SLO monitoring dashboards | Required for quarterly reviews |

### 5. Outputs and Artifacts

| Output | Format | Storage | Consumers |
|--------|--------|---------|-----------|
| SLO Document (per service) | Markdown document with structured tables | Team wiki, linked from service registry | sre, software-engineer, product-manager, engineering-manager |
| Error Budget Calculation | Formula embedded in SLO document + dashboard widget | Observability platform dashboard | sre, engineering-manager |
| Monitoring Dashboards | Grafana/Datadog dashboards | Observability platform | sre, software-engineer (on-call) |
| Alert Configuration | Alert rules in monitoring-as-code | Infrastructure repository | sre |
| Quarterly Burn Review Report | Meeting notes with action items | Team wiki; action items entered in RAID Log (P-074) | engineering-manager (Director), product-manager |

### 6. Gates and Checkpoints

| Gate | Trigger | Pass Criteria | Failure Action |
|------|---------|---------------|----------------|
| **New Service Launch Gate** | Any service approaching production deployment | SLO document exists, approved by PM and EM; monitoring configured; dashboards live; alert thresholds set | Production deployment blocked until SLO is defined |
| **Quarterly Error Budget Review Gate** | End of each quarter | All production services reviewed; services with exhausted budget have documented reliability sprint plan; action items assigned | VP of Platform Engineering escalation; affected services enter reliability-only mode |

### 7. Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| SLO coverage | Percentage of production services with a documented SLO | 100% |
| SLO agreement | SLO targets agreed by both SRE and the service owning team | Every SLO document has PM and EM sign-off |
| Quarterly review completion | Error budget burn reviewed quarterly with documented action items | 100% of services reviewed; action items tracked to closure |
| Error budget response time | Time from error budget exhaustion to reliability sprint kickoff | Within 1 sprint (2 weeks) |

### 8. Dependencies

| Dependency | Process | Direction | Description |
|------------|---------|-----------|-------------|
| P-009 | Success Metrics Definition | Upstream | Latency and availability targets from Success Metrics inform SLO thresholds |
| P-055 | Incident Response | Downstream | SLO definitions determine SEV-1 thresholds (SLO breach = potential SEV-1) |
| P-057 | On-Call Rotation Management | Downstream | SLOs define alert thresholds that drive on-call alert volume |
| P-059 | Runbook Authoring | Downstream | SLO-derived alerts reference runbooks for operational response |
| P-035 | Performance Testing | Downstream | SLO targets provide performance budgets for pre-launch load testing |
| P-045 | Infrastructure Provisioning | Lateral | Infrastructure capacity must support SLO targets |

### 9. Traceability

| Trace Point | Reference |
|-------------|-----------|
| Clarity of Intent | Stage 2 Scope Contract, Section 5 — Success Metrics define latency/availability targets that feed into SLOs |
| Engineering Team Structure Guide | Section 3.5 — SRE role: "Owns SLOs and error budgets for defined services" |
| Engineering Team Structure Guide | Section 7 — VP/Director of Platform Engineering: "defines SLO frameworks for all services" |
| Process Architecture | Category 9, Stage 0 research; SRE role responsibilities; reliability engineering principles |

---

## P-055: Incident Response Process

### 1. Identity

| Field | Value |
|-------|-------|
| **Process ID** | P-055 |
| **Process Name** | Incident Response Process |
| **Purpose** | Defined severity-tiered response to production incidents. SEV-1: immediate page, SRE + EM + Director. SEV-2: <15-minute response. SEV-3: <1-hour response. SEV-4: next business day. Post-mortem required for SEV-1 and SEV-2. |
| **Derived From** | Stage 0 research Category 9; SRE role; Engineering_Team_Structure_Guide incident management |

### 2. Ownership

| Role | Responsibility |
|------|---------------|
| **Primary Owner Agent** | sre |
| **Supporting Agents** | engineering-manager (EM paged for SEV-1/2); software-engineer (on-call engineer); security-engineer (if security-related incident) |
| **Organizational Reporting** | SRE Lead reports to Platform Engineering Director; Director escalation path to VP of Platform Engineering |

### 3. Severity Definitions

| Severity | Definition | Examples | Response Time | Notification |
|----------|-----------|----------|---------------|-------------|
| **SEV-1** | Complete service outage or data loss affecting users; revenue impact | Production database down; payment processing failure; data breach | Immediate page | SRE + EM + Director; stakeholder updates every 15 min |
| **SEV-2** | Significant performance degradation; partial feature unavailability | API latency 10x normal; 30% of requests failing; one availability zone down | <15 minutes | SRE + EM; stakeholder updates every 30 min |
| **SEV-3** | Minor feature unavailability; workaround available | Non-critical feature broken; batch job delayed; degraded search results | <1 hour | SRE + on-call engineer; EM informed |
| **SEV-4** | Non-critical issue; no user impact | Internal tool broken; non-blocking warning in logs; cosmetic issue | Next business day | Ticket created; assigned in next sprint planning |

### 4. Stages and Steps

| Stage | Step | Actor | Description | SLA |
|-------|------|-------|-------------|-----|
| 1 | Detection | Monitoring system or user report | Incident detected via monitoring alert (SLO breach, health check failure, anomaly detection) or user/support report. Alert routes to on-call SRE via PagerDuty/OpsGenie. | Automated detection: <1 min from threshold breach |
| 2 | Triage | On-call SRE | On-call SRE acknowledges alert, assesses blast radius, and assigns severity using the definitions above. Creates incident channel (Slack/Teams) with standardized naming: `#inc-YYYYMMDD-brief-description`. | SEV-1: <5 min from page; SEV-2: <15 min |
| 3 | Escalation | On-call SRE | SEV-1: pages SRE Lead + EM + Director immediately. Incident commander assigned (SRE Lead or designated senior SRE). SEV-2: pages backup SRE + EM. SEV-3/4: on-call SRE handles or delegates. Security-related incidents: security-engineer paged regardless of severity. | SEV-1: <5 min from triage |
| 4 | Incident Command | Incident Commander (SRE Lead) | Incident commander coordinates resolution. Assigns roles: communications lead (updates stakeholders), technical lead (drives fix), scribe (records timeline). Stakeholder updates posted at defined intervals. Runbooks (P-059) consulted for known failure modes. | Updates: SEV-1 every 15 min; SEV-2 every 30 min |
| 5 | Resolution | On-call SRE + software-engineer | Service restored to normal operation. Incident commander confirms SLO metrics have returned to acceptable range. Temporary mitigations documented if root cause not yet addressed. | MTTR target: SEV-1 <4 hours; SEV-2 <8 hours |
| 6 | Declaration | Incident Commander | Incident declared resolved. Resolution summary posted to incident channel. Incident record created with: timeline, root cause (preliminary), blast radius, duration, affected services. | Within 1 hour of service restoration |
| 7 | Post-Mortem Trigger | sre | For SEV-1 and SEV-2: post-mortem meeting scheduled within 5 business days (P-056). Incident record forwarded to post-mortem facilitator. | SEV-1/2: post-mortem scheduled within 24 hours of resolution |

### 5. Inputs

| Input | Source | Required/Optional |
|-------|--------|-------------------|
| Monitoring alerts | Observability platform (configured per P-054 SLO thresholds) | Required |
| User/support incident reports | Support team or user feedback channels | Optional trigger |
| Runbooks | P-059 (Runbook Authoring Process) | Required for known failure modes |
| SLO definitions | P-054 (SLO Document per service) | Required for severity classification |
| On-call schedule | P-057 (On-Call Rotation Management) | Required for routing pages |

### 6. Outputs and Artifacts

| Output | Format | Storage | Consumers |
|--------|--------|---------|-----------|
| Incident Channel Log | Chat transcript with timestamped entries | Slack/Teams archive | sre, post-mortem facilitator |
| Incident Record | Structured document: timeline, severity, blast radius, duration, preliminary root cause, resolution actions | Incident tracking system (PagerDuty/OpsGenie + wiki) | sre, engineering-manager, post-mortem process (P-056) |
| Stakeholder Updates | Formatted status messages at defined intervals | Incident channel + status page (for SEV-1) | engineering-manager, product-manager, Director, VP (SEV-1) |
| Post-Mortem Trigger | Scheduled post-mortem meeting with incident record attached | Calendar + P-056 process intake | sre (facilitator), all incident participants |

### 7. Gates and Checkpoints

| Gate | Trigger | Pass Criteria | Failure Action |
|------|---------|---------------|----------------|
| **Severity Classification Gate** | Incident detected | Severity assigned within SLA; incident channel created; correct personnel paged | SRE Lead reviews missed classifications weekly; patterns addressed in on-call retrospective |
| **Resolution Confirmation Gate** | Service restored | SLO metrics within acceptable range for >15 minutes; no cascading failures; temporary mitigations documented | Incident remains open; incident commander continues coordination |
| **Post-Mortem Scheduling Gate** | SEV-1/SEV-2 resolved | Post-mortem meeting scheduled within 24 hours; all participants confirmed | SRE Lead escalates to Director; post-mortem is mandatory, not optional |

### 8. Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Mean Time to Resolution (MTTR) | Duration from incident detection to resolution | SEV-1: <4 hours; SEV-2: <8 hours |
| Post-mortem coverage | Percentage of SEV-1/2 incidents with completed post-mortem | 100% within 5 business days |
| On-call response time | Time from page to acknowledgment | SEV-1: <5 minutes |
| Stakeholder update cadence | Compliance with update intervals during active incidents | SEV-1: update every 15 min; SEV-2: every 30 min |
| Severity accuracy | Percentage of incidents correctly classified at triage (reviewed retrospectively) | >90% correct classification |

### 9. Dependencies

| Dependency | Process | Direction | Description |
|------------|---------|-----------|-------------|
| P-054 | SLO Definition and Review | Upstream | SLO definitions determine what constitutes an SLO breach and informs SEV-1 thresholds |
| P-056 | Post-Mortem | Downstream | SEV-1 and SEV-2 incidents trigger the post-mortem process |
| P-057 | On-Call Rotation Management | Upstream | On-call schedule determines who receives pages |
| P-059 | Runbook Authoring | Upstream | Runbooks provide step-by-step resolution guidance during incidents |

### 10. Traceability

| Trace Point | Reference |
|-------------|-----------|
| Engineering Team Structure Guide | Section 3.5 — SRE role: "leads incident response and post-mortems" |
| Engineering Team Structure Guide | Section 2.1 — VP of Engineering: "Escalation path for engineering-wide incidents and decisions" |
| Engineering Team Structure Guide | Section 13 — Operational Framework: incident management practices |
| Process Architecture | Category 9; SRE role; Engineering_Team_Structure_Guide incident management |

---

## P-056: Post-Mortem Process

### 1. Identity

| Field | Value |
|-------|-------|
| **Process ID** | P-056 |
| **Process Name** | Post-Mortem Process |
| **Purpose** | Blameless post-mortem for all SEV-1 and SEV-2 incidents within 5 business days of resolution. Produces action items with owners and deadlines. Action items tracked in RAID Log and reviewed in EM syncs. |
| **Derived From** | Stage 0 research Category 9; SRE role; post-mortem best practices |

### 2. Ownership

| Role | Responsibility |
|------|---------------|
| **Primary Owner Agent** | sre |
| **Supporting Agents** | engineering-manager (EM participates; Director informed for SEV-1); software-engineer (on-call engineers participate); technical-program-manager (tracks action items in RAID Log) |
| **Organizational Reporting** | SRE Lead facilitates; Director of Engineering informed for all SEV-1 post-mortems |

### 3. Blameless Post-Mortem Principles

The post-mortem process is explicitly **blameless**. The following principles are non-negotiable:

| Principle | Description |
|-----------|-------------|
| **No blame, no shame** | Focus on systems and processes, never on individual fault. Language like "Person X caused..." is prohibited. |
| **Systems thinking** | Every incident has multiple contributing factors. The goal is to identify systemic weaknesses, not a single root cause. |
| **Psychological safety** | Participants must feel safe to share what they observed without fear of punishment. The facilitator enforces this actively. |
| **Action-oriented** | Every contributing factor must produce at least one actionable item. Post-mortems without action items are incomplete. |
| **Transparency** | Post-mortem documents are published to the team wiki, visible to all engineering staff. Hiding incidents prevents organizational learning. |

### 4. Stages and Steps

| Stage | Step | Actor | Description | Duration/SLA |
|-------|------|-------|-------------|-------------|
| 1 | Scheduling | sre (facilitator) | Post-mortem meeting scheduled within 24 hours of incident resolution. All incident participants invited. EM and Director invited for SEV-1. Meeting held within 5 business days of resolution. | Schedule within 24 hours; hold within 5 business days |
| 2 | Pre-Work: Timeline Reconstruction | sre (facilitator) | Facilitator reconstructs the incident timeline from: monitoring data, incident channel logs, system logs, deployment history. Pre-populated timeline shared with participants 24 hours before the meeting. | 1-2 hours of facilitator prep |
| 3 | Post-Mortem Meeting | sre (facilitator) + all participants | Meeting structure (90 minutes max): (a) Review timeline — corrections and additions from participants (20 min). (b) Identify contributing factors — what systemic conditions allowed this to happen? (15 min). (c) What went well — detection speed, response coordination, communication (10 min). (d) What could improve — gaps in monitoring, runbooks, escalation, tooling (15 min). (e) Generate action items — specific, owned, time-bound (20 min). (f) Summary and next steps (10 min). | 90 minutes max |
| 4 | Document Production | sre (facilitator) | Post-mortem document written using standardized template (see Section 5 below). Document reviewed by EM before publication. | Within 2 business days of meeting |
| 5 | Publication | sre (facilitator) | Post-mortem document published to team wiki. Link shared in engineering-wide channel. | Same day as document completion |
| 6 | Action Item Tracking | technical-program-manager | Action items entered in RAID Log (P-074). Each action item has: description, owner, deadline, priority. TPM tracks status. EM reviews in weekly Director sync (P-065). | Entered within 1 business day of publication |
| 7 | Action Item Escalation | engineering-manager (Director) | Action items not completed within 2 sprints (4 weeks) escalate to VP of Platform Engineering. VP determines whether to extend deadline or reprioritize. | Escalation trigger: 2 sprints past deadline |

### 5. Post-Mortem Document Template

The post-mortem document MUST contain these sections:

| Section | Content |
|---------|---------|
| **Header** | Incident ID, severity, date/time, duration, affected services, incident commander |
| **Executive Summary** | 2-3 sentences: what happened, what was the impact, how was it resolved |
| **Timeline** | Timestamped sequence of events from detection through resolution |
| **Impact** | User impact (number of affected users, revenue impact if applicable), service impact (which SLOs breached, for how long) |
| **Contributing Factors** | Systemic conditions that allowed this incident (NOT "root cause" singular — multiple factors) |
| **What Went Well** | Aspects of detection, response, and communication that worked effectively |
| **What Could Improve** | Gaps identified in monitoring, runbooks, processes, tooling, or communication |
| **Action Items** | Table: ID, Description, Owner, Priority, Deadline, Status |
| **Lessons Learned** | Key takeaways that apply beyond this specific incident |

### 6. Inputs

| Input | Source | Required/Optional |
|-------|--------|-------------------|
| Incident record | P-055 (Incident Response Process) | Required |
| Monitoring data and system logs | Observability platform | Required |
| Incident channel transcript | Slack/Teams archive | Required |
| Deployment history | CI/CD pipeline logs | Required if deployment-related |
| SLO breach data | P-054 (SLO dashboards) | Required |

### 7. Outputs and Artifacts

| Output | Format | Storage | Consumers |
|--------|--------|---------|-----------|
| Post-Mortem Document | Markdown using standardized template | Team wiki, indexed by incident ID | All engineering staff (published openly) |
| Action Items | Structured entries with owner, deadline, priority | RAID Log (P-074) | engineering-manager, technical-program-manager, action item owners |
| RAID Log Entries | Per P-074 format | RAID Log system | Director (weekly review), VP (escalation) |

### 8. Gates and Checkpoints

| Gate | Trigger | Pass Criteria | Failure Action |
|------|---------|---------------|----------------|
| **Post-Mortem Timeliness Gate** | 5 business days after SEV-1/2 resolution | Post-mortem meeting held; document drafted | SRE Lead escalates to Director; this is a mandatory process |
| **Document Quality Gate** | Post-mortem document submitted | All template sections completed; contributing factors identified (not just "root cause"); at least 1 action item per contributing factor; every action item has owner and deadline | Facilitator revises document; EM reviews before publication |
| **Action Item Completion Gate** | 2 sprints (4 weeks) after action item creation | Action item completed or explicitly deferred with VP approval | Escalation to VP of Platform Engineering |

### 9. Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Post-mortem timeliness | Percentage of SEV-1/2 incidents with post-mortem published within 5 business days | 100% |
| Action item ownership | Percentage of action items with a named owner and deadline | 100% |
| Action item completion | Percentage of action items completed within their deadline | >80% |
| Recurrence prevention | Percentage of post-mortem action items that prevent recurrence of the same failure mode | No identical incident recurs after action items are completed |
| Blamelessness adherence | Post-mortem documents reviewed for blame language (spot-checked quarterly) | Zero instances of blame language |

### 10. Dependencies

| Dependency | Process | Direction | Description |
|------------|---------|-----------|-------------|
| P-055 | Incident Response | Upstream | Incident must be resolved before post-mortem begins; incident record is primary input |
| P-074 | RAID Log Maintenance | Downstream | Action items tracked in RAID Log; TPM maintains status |
| P-065 | Director Weekly EM Sync | Downstream | Action items reviewed by Director in weekly sync |

### 11. Traceability

| Trace Point | Reference |
|-------------|-----------|
| Engineering Team Structure Guide | Section 3.5 — SRE role: "leads incident response and post-mortems" |
| Engineering Team Structure Guide | Section 13 — Operational Framework references post-mortem practices |
| Clarity of Intent | Stage 4 Sprint Bridge, Section 5 — Definition of Done includes "documentation updated" which covers post-mortem publication |
| Process Architecture | Category 9; SRE role; post-mortem best practices |

---

## P-057: On-Call Rotation Management Process

### 1. Identity

| Field | Value |
|-------|-------|
| **Process ID** | P-057 |
| **Process Name** | On-Call Rotation Management Process |
| **Purpose** | SRE Lead maintains a fair, sustainable on-call rotation. Target: <2 interrupt alerts per shift. >5 alerts per week per engineer triggers a toil reduction sprint. |
| **Derived From** | Stage 0 research Category 9; SRE Lead role responsibilities |

### 2. Ownership

| Role | Responsibility |
|------|---------------|
| **Primary Owner Agent** | sre (SRE Lead) |
| **Supporting Agents** | engineering-manager (EM informed of on-call burden exceeding threshold) |
| **Organizational Reporting** | SRE Lead reports to Platform Engineering Director; burden escalation path to Director then VP |

### 3. On-Call Policy

| Policy | Specification |
|--------|--------------|
| **Minimum rotation size** | 5 engineers per rotation. Fewer than 5 creates unsustainable burden. |
| **Rotation cadence** | Weekly rotation (7-day shifts). No engineer on primary on-call more than once per rotation cycle. |
| **Shift structure** | Primary on-call + secondary (backup) on-call per shift. Primary handles all pages; secondary steps in if primary is unreachable after 10 minutes. |
| **Compensation** | On-call compensation follows company policy. Shifts during weekends/holidays receive additional compensation per HR policy. |
| **Override scheduling** | Engineers can swap shifts with mutual agreement. All swaps recorded in PagerDuty/OpsGenie. SRE Lead approves swaps that would leave gaps. |
| **Alert volume target** | <2 interrupt alerts per on-call shift. This is a sustainability threshold, not a performance target. |
| **Toil trigger** | >5 alerts per week per engineer triggers a toil reduction sprint. This is non-negotiable. |
| **Burden ceiling** | >50% of sprint time spent on on-call duties triggers EM notification and Director escalation. |

### 4. Stages and Steps

| Stage | Step | Actor | Description | Cadence |
|-------|------|-------|-------------|---------|
| 1 | Schedule Maintenance | SRE Lead | Maintain on-call schedule in PagerDuty/OpsGenie. Ensure minimum 5-person rotation at all times. Account for PTO, holidays, and team changes. Schedule published at least 4 weeks in advance. | Ongoing; schedule published monthly |
| 2 | Weekly Alert Volume Review | SRE Lead | Review alert volume per engineer from the past week. Metrics collected: total alerts, interrupt alerts (requiring action), noise alerts (auto-resolved or non-actionable), MTTA (mean time to acknowledge). | Weekly |
| 3 | Noise Reduction | sre | For alerts identified as noise (auto-resolved, non-actionable, or duplicate): tune thresholds, suppress known-noisy alerts, or fix underlying flaky checks. Goal: every alert that pages should require human action. | Ongoing; tracked weekly |
| 4 | Toil Reduction Sprint Trigger | SRE Lead + engineering-manager | If >5 alerts/week per engineer: SRE Lead files a toil reduction sprint request. EM acknowledges and allocates sprint capacity. Toil reduction sprint focuses exclusively on: automating manual responses, fixing recurring alert causes, improving runbooks, tuning alert thresholds. | Triggered within 1 sprint of threshold breach |
| 5 | Burden Escalation | SRE Lead + engineering-manager | If >50% of sprint time spent on on-call: SRE Lead notifies EM immediately. EM escalates to Director. Director determines response: additional SRE headcount, service ownership transfer, or architectural investment to reduce operational burden. | Event-driven |
| 6 | Quarterly Rotation Review | SRE Lead + engineering-manager | Review rotation for fairness: are shifts evenly distributed? Are certain engineers bearing disproportionate burden? Review on-call satisfaction (informal pulse check with on-call engineers). Adjust rotation structure if needed. | Quarterly |

### 5. Inputs

| Input | Source | Required/Optional |
|-------|--------|-------------------|
| PagerDuty/OpsGenie on-call records | On-call management platform | Required |
| Alert volume data (per engineer, per shift) | Observability platform + PagerDuty/OpsGenie analytics | Required |
| Engineer availability (PTO, holidays, team changes) | HR system / team calendar | Required |
| SLO definitions and alert thresholds | P-054 (SLO Definition and Review) | Required |
| Incident volume and patterns | P-055 (Incident Response Process) | Required for identifying toil sources |

### 6. Outputs and Artifacts

| Output | Format | Storage | Consumers |
|--------|--------|---------|-----------|
| On-Call Schedule | PagerDuty/OpsGenie schedule | On-call management platform | sre, software-engineer (on-call), engineering-manager |
| Weekly Alert Volume Report | Dashboard + weekly summary | Observability platform; summary posted in SRE team channel | SRE Lead, engineering-manager |
| Toil Reduction Sprint Trigger | Formal request with: alert data, threshold breach evidence, proposed sprint scope | Sprint planning backlog | engineering-manager, sre team |
| Quarterly Rotation Review Report | Summary: shift distribution, alert burden per engineer, satisfaction pulse, recommendations | Team wiki | SRE Lead, engineering-manager, Director |

### 7. Gates and Checkpoints

| Gate | Trigger | Pass Criteria | Failure Action |
|------|---------|---------------|----------------|
| **Rotation Coverage Gate** | Schedule publication (monthly) | Minimum 5 engineers in rotation; no uncovered shifts in next 4 weeks; primary + secondary assigned for every shift | SRE Lead recruits additional engineers or escalates staffing gap to Director |
| **Alert Volume Gate** | Weekly review | Average <2 interrupt alerts per shift; no engineer exceeding 5 alerts/week | Toil reduction sprint triggered within 1 sprint |
| **Burden Gate** | Continuous monitoring | No engineer spending >50% of sprint time on on-call | EM informed; Director escalated; structural remediation planned |
| **Fairness Gate** | Quarterly review | No engineer on call more than once per rotation cycle; shift burden evenly distributed (no engineer >120% of average burden) | Rotation restructured; SRE Lead adjusts schedule |

### 8. Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Alert volume per shift | Average interrupt alerts per on-call shift | <2 per shift |
| Rotation fairness | Maximum deviation from average on-call burden per engineer | No engineer exceeds 1 shift per 5-person rotation cycle |
| Toil reduction response time | Time from threshold breach to toil reduction sprint kickoff | Within 1 sprint (2 weeks) |
| Alert noise ratio | Percentage of alerts that are non-actionable (noise) | <20% of total alerts |
| On-call satisfaction | Quarterly pulse check (1-5 scale) | Average >= 3.5/5 |
| Burden ceiling compliance | Percentage of sprints where no engineer exceeds 50% on-call time | 100% |

### 9. Dependencies

| Dependency | Process | Direction | Description |
|------------|---------|-----------|-------------|
| P-054 | SLO Definition and Review | Upstream | SLOs define alert thresholds that drive on-call alert volume |
| P-055 | Incident Response | Upstream | Incident response generates on-call demand; incident patterns inform toil sources |
| P-059 | Runbook Authoring | Lateral | Well-maintained runbooks reduce time-to-resolve and on-call burden |

### 10. Traceability

| Trace Point | Reference |
|-------------|-----------|
| Engineering Team Structure Guide | Section 3.5 — SRE role: "runs on-call rotations" and "drives toil reduction" |
| Engineering Team Structure Guide | Section 2.1 — SRE Lead reports to Platform Engineering Director |
| Engineering Team Structure Guide | Section 2.4 — Cognitive Load Management: "When cognitive load exceeds capacity, quality drops, incidents rise, and engineers burn out" — directly motivating the burden ceiling policy |
| Process Architecture | Category 9; SRE Lead role responsibilities |

---

## Appendix A: Process Interaction Matrix

This matrix shows how the four SRE & Operations processes interact with each other and with key external processes.

| | P-054 (SLO) | P-055 (Incident) | P-056 (Post-Mortem) | P-057 (On-Call) |
|---|---|---|---|---|
| **P-054 (SLO)** | -- | Defines SEV-1 thresholds | Error budget data informs post-mortem priority | Defines alert thresholds |
| **P-055 (Incident)** | SLO breach triggers detection | -- | Triggers post-mortem for SEV-1/2 | Generates on-call demand |
| **P-056 (Post-Mortem)** | May recommend SLO adjustment | Incident record is input | -- | Action items may include alert tuning |
| **P-057 (On-Call)** | Alert volume informed by SLOs | Provides responder routing | Toil patterns inform post-mortem themes | -- |

### External Process Dependencies

| External Process | Interaction |
|-----------------|-------------|
| P-009 (Success Metrics) | Upstream to P-054: business metrics inform SLO targets |
| P-045 (Infrastructure Provisioning) | Lateral to P-054: infrastructure capacity supports SLO targets |
| P-059 (Runbook Authoring) | Upstream to P-055: runbooks used during incident response |
| P-065 (Director Weekly EM Sync) | Downstream from P-056: action items reviewed in Director sync |
| P-074 (RAID Log Maintenance) | Downstream from P-056: action items tracked in RAID Log |

---

## Appendix B: Escalation Path Summary

| Trigger | First Escalation | Second Escalation | Third Escalation |
|---------|-----------------|-------------------|------------------|
| SEV-1 incident | SRE Lead + EM + Director (immediate) | VP of Platform Engineering (if unresolved >2 hours) | CTO (if unresolved >4 hours) |
| SEV-2 incident | SRE + EM (within 15 min) | Director (if unresolved >4 hours) | VP (if unresolved >8 hours) |
| Error budget exhausted | SRE Lead notifies EM | Director reviews in weekly sync | VP approves reliability sprint |
| Post-mortem action items overdue (>2 sprints) | EM reviews with action item owner | Director intervenes | VP decides extend or reprioritize |
| On-call burden >50% of sprint | SRE Lead notifies EM | Director escalated | VP determines structural remediation |
| Alert volume >5/week/engineer | SRE Lead triggers toil sprint | EM allocates capacity | Director reviews if toil sprint insufficient |

---

## Appendix C: DORA Metrics Alignment

The SRE & Operations processes directly support two of the four DORA metrics tracked in P-081 (DORA Metrics Review):

| DORA Metric | SRE Process Alignment |
|-------------|----------------------|
| **Change Failure Rate** | P-054 SLO tracking measures service reliability; P-056 post-mortems reduce failure recurrence |
| **Mean Time to Recovery (MTTR)** | P-055 incident response directly drives MTTR; P-059 runbooks (downstream) improve resolution speed; P-057 on-call ensures responder availability |

The remaining two DORA metrics (Deployment Frequency and Lead Time for Changes) are primarily driven by CI/CD processes (Category 6) but are indirectly supported by SRE processes — well-defined SLOs and efficient incident response give teams confidence to deploy more frequently.

---

## Cross-Category Dependencies

### Dependencies FROM Other Categories (Inputs)

| Source Process | Source Category | Consuming Process | Nature |
|---------------|----------------|-------------------|--------|
| P-009 (Success Metrics Definition) | Cat 2: Scope & Contract | P-054 (SLO Definition) | Success metrics inform SLO targets |
| P-059 (Runbook Authoring) | Cat 10: Documentation | P-055 (Incident Response) | Runbooks used during incidents |

### Dependencies TO Other Categories (Outputs)

| Providing Process | Consuming Process | Target Category | Nature |
|------------------|-------------------|-----------------|--------|
| P-054 (SLO Definition) | P-035 (Performance Testing) | Cat 5: Quality Assurance | SLOs define performance thresholds |
| P-054 (SLO Definition) | P-049 (Data Pipeline QA) | Cat 8: Data & ML | SLOs define data freshness targets |
| P-054 (SLO Definition) | P-052 (Model Canary Deployment) | Cat 8: Data & ML | SLOs define promotion thresholds |
| P-054 (SLO Definition) | P-057 (On-Call Rotation) | Cat 9 (self) | SLOs define alert thresholds |
| P-055 (Incident Response) | P-056 (Post-Mortem) | Cat 9 (self) | Incident must be resolved first |

## Agent Assignments Summary

| Process | Primary Owner | Supporting Agents |
|---------|--------------|-------------------|
| P-054: SLO Definition and Review | sre | product-manager, engineering-manager |
| P-055: Incident Response | sre | engineering-manager, software-engineer, security-engineer |
| P-056: Post-Mortem | sre | engineering-manager, software-engineer, technical-program-manager |
| P-057: On-Call Rotation Management | sre (SRE Lead) | engineering-manager |
