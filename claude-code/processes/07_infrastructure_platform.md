# Technical Specification: Infrastructure & Platform Processes (P-044 to P-048)

**Task ID**: Category 7 | **Stage**: 2 (Specification) | **Date**: 2026-04-05
**Session**: auto-orc-20260405-procderive | **Author**: spec-creator agent
**Inputs**: Stage 1 Process Architecture (Category 7), Clarity of Intent, Engineering_Team_Structure_Guide.md, 13 Agent Definitions

---

## Overview

This specification defines five processes that govern how infrastructure is provisioned, platform capabilities are delivered, cloud architecture decisions are governed, and production releases are managed. These processes collectively ensure that all infrastructure is code-managed, environments are self-service, cloud decisions are reviewed, and releases follow structured gates.

### Process Summary Table

| Process ID | Name | Primary Owner Agent | Risk Level |
|------------|------|---------------------|------------|
| P-044 | Golden Path Adoption Process | infra-engineer | MEDIUM |
| P-045 | Infrastructure Provisioning Process | infra-engineer | HIGH |
| P-046 | Environment Self-Service Process | infra-engineer | MEDIUM |
| P-047 | Cloud Architecture Review Board (CARB) Process | infra-engineer | MEDIUM |
| P-048 | Production Release Management Process | technical-program-manager | HIGH |

---

## P-044: Golden Path Adoption Process

### 1. Process Identity

- **Process ID**: P-044
- **Name**: Golden Path Adoption Process
- **Purpose**: Create and maintain CI/CD templates as the default path for new services. The golden path must be the easiest option -- not the only option. Adoption is measured quarterly via developer NPS.
- **Derived From**: Stage 0 research Category 7; Platform Engineer role; Internal Developer Platform (IDP) design; Engineering_Team_Structure_Guide Section 7 (DevOps and Platform Engineering Structure)
- **Risk Level**: MEDIUM -- low adoption means teams build inconsistent pipelines

### 2. Ownership

- **Primary Owner Agent**: `infra-engineer` (Platform Engineer L4-L6, DX Engineer)
- **Supporting Agents**:
  - `infra-engineer` -- provides infrastructure templates (IaC modules) that underpin golden path resources
  - `engineering-manager` -- Platform EM tracks adoption metrics and drives organizational adoption
  - `technical-writer` -- authors and maintains golden path documentation, onboarding guides, and developer portal content

### 3. Stages/Steps

| Step | Action | Owner | Duration |
|------|--------|-------|----------|
| 1 | **Identify friction points**: Platform Engineer audits current onboarding steps for new services, identifying the highest-cognitive-load tasks (environment setup, CI/CD configuration, dependency management, containerization) | infra-engineer | 2-3 days |
| 2 | **Create CI/CD templates**: Build golden path templates covering containerization (Dockerfile), pipeline stages (lint, test, SAST, build, deploy), environment configuration, and standard tooling | infra-engineer | 5-8 days |
| 3 | **Publish to developer portal**: Integrate templates into Backstage/Port developer portal with self-service scaffolding, so developers can instantiate a new service in a single action | infra-engineer | 2-3 days |
| 4 | **Document golden path**: Technical Writer produces onboarding documentation, decision records for template choices, and migration guides for teams with existing non-standard setups | technical-writer | 2-3 days |
| 5 | **Measure adoption**: Run quarterly developer NPS survey targeting template usability; collect monthly adoption rate metrics (percentage of new services using golden path) | engineering-manager | Ongoing (quarterly) |
| 6 | **Iterate on feedback**: Incorporate NPS feedback and adoption data into next template iteration; prioritize top friction items reported by developers | infra-engineer | Ongoing (quarterly) |

### 4. Inputs

- Developer onboarding pain point analysis (interviews, support ticket analysis)
- CI/CD tool inventory (current tools in use across all squads)
- Developer NPS survey results (quarterly)
- IaC module library (from infra-engineer)
- Engineering_Team_Structure_Guide -- Platform as a Product principle

### 5. Outputs/Artifacts

| Artifact | Format | Storage | Owner |
|----------|--------|---------|-------|
| CI/CD golden path templates | Code (YAML, Dockerfile, Makefile, pipeline configs) | Git repository (platform-templates repo) | infra-engineer |
| Developer portal catalog entries | Backstage/Port entity definitions | Developer portal | infra-engineer |
| Golden path documentation | Markdown/Docs site | Developer portal docs section | technical-writer |
| Adoption rate dashboard | Metrics dashboard | Observability platform | engineering-manager |
| Developer NPS results | Survey report | Team wiki | engineering-manager |

### 6. Gate/Checkpoint

- **Gate Name**: Golden Path Quarterly Review
- **Cadence**: Quarterly (aligned with OKR cycles)
- **Participants**: Platform EM, Platform Engineer(s), DX Engineer, representative squad TLs (consumer feedback)
- **Pass Criteria**:
  - New service setup using golden path completes in less than 2 hours
  - Quarterly developer NPS on golden path is net positive (score > 0)
  - Adoption rate is 60% or higher of new services within 2 sprints of template availability
  - All template changes have been tested end-to-end with a real service instantiation
- **Failure Action**: Identify top 3 adoption blockers; assign remediation owners with 2-week deadline

### 7. Success Criteria

- New service setup using golden path completes in less than 2 hours (measured by scaffolding-to-first-deployment time)
- Quarterly developer NPS on golden path is net positive
- Adoption rate of 60% or higher of new services within 2 sprints of template availability
- Zero golden path templates with unresolved critical issues for more than 1 sprint

### 8. Dependencies

| Dependency | Process/System | Type | Impact if Missing |
|------------|---------------|------|-------------------|
| P-089 | Developer Experience Survey | Process | Cannot measure NPS or gather structured feedback |
| Developer portal (Backstage/Port) | Infrastructure | System | No self-service scaffolding; templates require manual setup |
| IaC module library | infra-engineer output | Artifact | Infrastructure templates lack standardized cloud resource modules |

### 9. Traceability

- **Clarity of Intent alignment**: Supports Stage 4 Sprint Bridge -- golden path templates reduce setup time so sprints begin with working environments, not environment configuration tasks
- **Org Structure alignment**: Platform as a Product principle (Engineering_Team_Structure_Guide Section 1); Platform Engineer role (Section 3.5); DX Engineer role (Section 3.5)
- **Upstream processes**: None (foundational platform process)
- **Downstream processes**: P-046 (Environment Self-Service depends on golden path templates); all squad delivery processes benefit from reduced onboarding friction

---

## P-045: Infrastructure Provisioning Process

### 1. Process Identity

- **Process ID**: P-045
- **Name**: Infrastructure Provisioning Process
- **Purpose**: All cloud resources provisioned via Infrastructure as Code (IaC). Manual provisioning is a policy violation. All IaC changes reviewed by a Cloud Engineer before apply.
- **Derived From**: Stage 0 research Category 7; Cloud Engineer role (AWS/Azure/GCP specialists); FinOps practices; Engineering_Team_Structure_Guide Section 3.6 (Cloud Engineering)
- **Risk Level**: HIGH -- manually provisioned resources create shadow infrastructure, security gaps, and cost attribution failures

### 2. Ownership

- **Primary Owner Agent**: `infra-engineer` (Cloud Architect, AWS/Azure/GCP specialists, FinOps)
- **Supporting Agents**:
  - `infra-engineer` -- maintains IaC modules in the IDP; ensures provisioning integrates with golden path
  - `sre` -- performs reliability review of provisioned infrastructure (SLO alignment, redundancy, failover)

### 3. Stages/Steps

| Step | Action | Owner | Duration |
|------|--------|-------|----------|
| 1 | **Identify infrastructure need**: Engineer identifies a new cloud resource requirement; opens an IaC pull request using the approved module library | Requesting engineer (any agent) | 1-2 hours |
| 2 | **Cloud Engineer review**: Cloud Engineer reviews IaC PR for correct sizing, IAM least-privilege, cost estimate, tagging compliance, and architectural consistency | infra-engineer | 1-2 days SLA |
| 3 | **CARB threshold check**: If the change meets CARB threshold (new cloud service adoption, architecture pattern change, or cost commitment above threshold), trigger P-047 CARB review | infra-engineer | Conditional (up to 7 days if CARB required) |
| 4 | **Plan review and approval**: IaC plan output (terraform plan / CDK diff) reviewed and approved by Cloud Engineer; SRE reviews reliability implications for production resources | infra-engineer + sre | 0.5-1 day |
| 5 | **Automated apply**: Apply executed via CI/CD pipeline -- never manually from CLI; pipeline enforces all policy checks (OPA/Checkov) pass before apply | CI/CD pipeline (infra-engineer maintained) | Minutes |
| 6 | **Resource tagging**: All provisioned resources tagged with team, cost-center, environment, and project ID; tagging validated by automated policy | infra-engineer (FinOps) | Automated |
| 7 | **Drift detection**: Scheduled cloud drift scanning detects any manual changes; violations flagged and remediated | infra-engineer | Ongoing (daily scans) |

### 4. Inputs

- Infrastructure need description (from requesting team)
- IaC module library (approved, versioned Terraform/CDK/Pulumi modules)
- Cost attribution tags (team, cost-center, environment, project ID)
- IAM policy templates (least-privilege patterns per resource type)
- CARB thresholds document (defines when P-047 is triggered)

### 5. Outputs/Artifacts

| Artifact | Format | Storage | Owner |
|----------|--------|---------|-------|
| IaC pull request with plan output | Git PR + plan file | Git repository | Requesting engineer |
| Cloud Engineer review record | PR review comments + approval | Git repository | infra-engineer |
| Provisioned infrastructure | Cloud resources | Cloud provider | infra-engineer |
| Cost attribution tags | Resource tags | Cloud provider | infra-engineer (FinOps) |
| Audit trail | PR merge record + pipeline logs | Git + CI/CD system | infra-engineer |
| Drift detection report | Automated scan results | Observability platform | infra-engineer |

### 6. Gate/Checkpoint

- **Gate Name**: Cloud Engineer Code Review Gate
- **Trigger**: Every IaC pull request, before any apply
- **Participants**: Cloud Engineer (reviewer), requesting engineer (author), SRE (for production resources)
- **Pass Criteria**:
  - IaC uses approved module library (no raw resource definitions for modules that exist)
  - IAM follows least-privilege principle
  - Cost estimate reviewed and within budget
  - All resources tagged with required attributes (team, cost-center, environment, project ID)
  - Policy-as-code checks (OPA/Checkov) pass
  - CARB review completed if threshold met (P-047)
- **Failure Action**: PR blocked; Cloud Engineer provides specific remediation feedback; requesting engineer revises

### 7. Success Criteria

- 100% of cloud resources have IaC source (no unmanaged resources)
- Zero manually provisioned resources (detected via cloud drift tooling)
- All resources tagged for cost attribution
- IaC PR review SLA of 2 business days met for 95% of requests
- Zero IAM policy violations in quarterly security audit

### 8. Dependencies

| Dependency | Process/System | Type | Impact if Missing |
|------------|---------------|------|-------------------|
| P-047 | CARB Process | Process | Large infrastructure changes lack architectural governance |
| IaC module library | Platform team artifact | Artifact | Engineers write ad-hoc IaC; inconsistency and security gaps |
| Policy-as-code tooling (OPA/Checkov) | Infrastructure | System | No automated policy enforcement; relies solely on human review |
| Cloud drift detection tooling | Infrastructure | System | Manual provisioning goes undetected |
| CI/CD pipeline for IaC apply | infra-engineer maintained | System | Risk of manual applies from CLI |

### 9. Traceability

- **Clarity of Intent alignment**: Supports Stage 3 Dependency Map -- infrastructure dependencies are provisioned via auditable IaC, making dependency tracking concrete and verifiable
- **Org Structure alignment**: Cloud Engineer roles (Section 3.6); Cloud Architect CARB chair; FinOps Engineer cost governance; Platform Engineer IaC modules
- **Upstream processes**: P-047 (CARB review for threshold changes)
- **Downstream processes**: P-046 (Environment Self-Service depends on IaC infrastructure); P-048 (Production Release Management depends on infrastructure being provisioned and tagged); P-035 (Load testing requires provisioned perf environments)

---

## P-046: Environment Self-Service Process

### 1. Process Identity

- **Process ID**: P-046
- **Name**: Environment Self-Service Process
- **Purpose**: Developers request and provision environments via the developer portal (Backstage/Port) without raising tickets to cloud or platform teams. Reduces cognitive load and eliminates ticket queue delays.
- **Derived From**: Stage 0 research Category 7; DX Engineer role; Developer Experience mandate; Engineering_Team_Structure_Guide -- Platform as a Product principle, Cognitive Load Management
- **Risk Level**: MEDIUM -- without self-service, environment waits become sprint blockers

### 2. Ownership

- **Primary Owner Agent**: `infra-engineer` (DX Engineer builds and maintains self-service catalog)
- **Supporting Agents**:
  - `infra-engineer` -- builds and maintains underlying cloud provisioning automation that the self-service portal invokes

### 3. Stages/Steps

| Step | Action | Owner | Duration |
|------|--------|-------|----------|
| 1 | **Build environment catalog**: DX Engineer defines environment types (dev, staging, performance, sandbox) with pre-approved configurations, resource limits, and cost profiles | infra-engineer | 3-5 days (initial); ongoing maintenance |
| 2 | **Integrate with developer portal**: Environment catalog published in Backstage/Port with clear descriptions, expected provisioning time, and auto-expiry policy for each type | infra-engineer | 2-3 days |
| 3 | **Developer selects environment**: Developer navigates to portal, selects environment type, provides project/team metadata, and triggers provisioning | Requesting developer (any agent) | Minutes |
| 4 | **Automated provisioning**: Portal triggers IaC automation (using P-045 approved modules) with pre-approved configuration; no Cloud Engineer review required for catalog items | Automated (infra-engineer maintained modules) | SLA: 30 minutes or less for standard environments |
| 5 | **Environment delivery**: Developer receives environment access details (endpoints, credentials, connection strings) via portal notification | Automated | Immediate upon provisioning |
| 6 | **Automatic expiry**: All self-service environments have a defined TTL (time-to-live); expiry warnings sent 24 hours before teardown; developers can request extension via portal | Automated + infra-engineer policy | Ongoing |
| 7 | **Usage tracking**: All self-service provisioning logged with cost attribution; monthly usage report generated for Platform EM and FinOps | infra-engineer | Monthly |

### 4. Inputs

- Developer portal (Backstage/Port) with self-service plugin
- Pre-approved environment configurations (per environment type)
- Cloud account with provisioning permissions scoped to self-service automation
- IaC modules from P-045 module library
- Golden path templates from P-044

### 5. Outputs/Artifacts

| Artifact | Format | Storage | Owner |
|----------|--------|---------|-------|
| Self-service environment catalog | Portal catalog entries | Developer portal (Backstage/Port) | infra-engineer |
| Provisioned environment | Cloud resources with access details | Cloud provider | Requesting developer (temporary owner) |
| Expiry schedule | Automated TTL configuration | Platform automation system | infra-engineer |
| Cost attribution record | Tagged resources + usage logs | Cloud cost management tool | infra-engineer (FinOps) |
| Monthly usage report | Dashboard/report | Observability platform | infra-engineer |

### 6. Gate/Checkpoint

- **Gate Name**: Environment Catalog Review
- **Cadence**: Quarterly (aligned with golden path review cycle)
- **Participants**: DX Engineer, Platform EM, Cloud Engineer, representative developers (consumers)
- **Pass Criteria**:
  - Standard environment provisioned in 30 minutes or less without a ticket
  - Developer portal catalog covers 90% or more of common environment requests (measured by remaining manual ticket volume)
  - All self-service environments have automatic expiry configured
  - Zero orphaned environments (environments past expiry still running)
  - Cost per self-service environment within defined budget guardrails
- **Failure Action**: Expand catalog to cover uncovered environment types; fix provisioning failures; enforce expiry automation

### 7. Success Criteria

- Standard environment provisioned in 30 minutes or less without a ticket
- Developer portal catalog covers 90% or more of common environment requests
- All self-service environments have automatic expiry
- Environment-related support tickets reduced by 80% or more compared to pre-self-service baseline
- Zero orphaned environments running past expiry

### 8. Dependencies

| Dependency | Process/System | Type | Impact if Missing |
|------------|---------------|------|-------------------|
| P-045 | Infrastructure Provisioning (IaC) | Process | Self-service has no standardized provisioning modules to invoke |
| P-044 | Golden Path Adoption | Process | Environments lack standard templates; each provisioning is ad-hoc |
| Developer portal (Backstage/Port) | Infrastructure | System | No self-service UI; developers must raise tickets |
| Cloud automation permissions | Security | Configuration | Portal cannot provision without scoped IAM roles |

### 9. Traceability

- **Clarity of Intent alignment**: Directly supports Stage 3 Dependency Map, Section 2 (Shared Resource Conflicts) -- self-service environments eliminate the "staging environment contention" problem explicitly called out in the Clarity of Intent Dependency Charter example
- **Org Structure alignment**: DX Engineer role (Section 3.5); Platform as a Product principle (Section 2.4 -- Cognitive Load Management); developer satisfaction as platform success metric
- **Upstream processes**: P-044 (Golden Path provides templates); P-045 (IaC provides provisioning modules)
- **Downstream processes**: All delivery processes benefit -- sprint blockers from environment waits are eliminated

---

## P-047: Cloud Architecture Review Board (CARB) Process

### 1. Process Identity

- **Process ID**: P-047
- **Name**: Cloud Architecture Review Board (CARB) Process
- **Purpose**: Weekly review of new cloud service adoptions, architecture pattern changes, and cost commitments above defined thresholds. Prevents ungoverned cloud sprawl, vendor lock-in, security gaps, and cost overruns.
- **Derived From**: Stage 0 research Category 7; Cloud Architect role; Engineering_Team_Structure_Guide CARB reference (Section 3.6 -- Cloud Architect chairs CARB)
- **Risk Level**: MEDIUM -- ungoverned cloud service adoption creates lock-in, security gaps, and cost sprawl

### 2. Ownership

- **Primary Owner Agent**: `infra-engineer` (Cloud Architect chairs CARB)
- **Supporting Agents**:
  - `staff-principal-engineer` -- Principal/Staff Engineers provide cross-org architectural review and consistency evaluation
  - `security-engineer` -- Security Architect reviews security implications of proposed cloud services and patterns
  - `engineering-manager` -- FinOps Engineer participates in cost model review and budget impact assessment

### 3. Participants

Cloud Architect (chair) + Principal/Staff Engineers + Security Architect + FinOps Engineer. Requesting team's TL presents.

### 4. Stages/Steps

| Step | Action | Owner | Duration |
|------|--------|-------|----------|
| 1 | **Submit CARB review request**: Team submits proposal document including architecture description, cost model, security assessment, alternative analysis, and vendor lock-in evaluation | Requesting team TL | 1-3 days (preparation) |
| 2 | **Schedule review**: Cloud Architect schedules proposal within weekly CARB cadence; urgent reviews can use async track (48-hour SLA) | infra-engineer (Cloud Architect) | Within 1 weekly cycle |
| 3 | **CARB review session**: Board reviews security implications, cost model (FinOps), vendor lock-in risk, architectural consistency with existing patterns, and operational readiness | All CARB participants | 30-60 minutes per proposal |
| 4 | **Decision**: CARB records decision: Approve / Approve with conditions / Reject / Defer | infra-engineer (Cloud Architect) | Same session |
| 5 | **Communication**: Approved proposals enter IaC backlog for implementation; rejected proposals receive documented rationale communicated to requesting team within 24 hours | infra-engineer | 24 hours max |
| 6 | **Conditions tracking**: For "Approve with conditions" decisions, conditions are tracked as action items with owners and deadlines; implementation cannot proceed until conditions are met | infra-engineer + requesting team | Varies per condition |

### 5. CARB Trigger Thresholds

The following changes require CARB review before implementation:

| Trigger | Example |
|---------|---------|
| New cloud service adoption | Team wants to use a managed service not currently in the approved services list |
| Architecture pattern change | Moving from synchronous API calls to event-driven messaging for a domain |
| Cost commitment above threshold | Reserved instances, committed use discounts, or new service estimated to exceed defined monthly spend threshold |
| Multi-region or multi-cloud expansion | Deploying workloads to a new region or cloud provider |
| Vendor contract or SLA dependency | Introducing a third-party managed service with SLA dependencies |

### 6. Inputs

- Architecture proposal document (from requesting team)
- Cost model with 12-month projection
- Security assessment (from security-engineer or Security Champion)
- Alternative analysis (at least 2 alternatives evaluated)
- Current approved services list (maintained by Cloud Architect)

### 7. Outputs/Artifacts

| Artifact | Format | Storage | Owner |
|----------|--------|---------|-------|
| CARB decision record | Structured document (Approve/Reject/Defer + rationale) | Architecture decision record (ADR) repository | infra-engineer |
| Conditions document (if applicable) | Action items with owners and deadlines | ADR repository + project tracker | infra-engineer |
| Updated approved services list (if new service approved) | List/registry | Developer portal or wiki | infra-engineer |
| Rejection rationale (if rejected) | Written communication | ADR repository + requesting team notification | infra-engineer |

### 8. Gate/Checkpoint

- **Gate Name**: CARB Decision Gate
- **Cadence**: Weekly standing meeting; async 48-hour SLA for urgent reviews
- **Participants**: Cloud Architect (chair), Principal/Staff Engineers, Security Architect, FinOps Engineer, requesting team TL (presenter)
- **Pass Criteria**:
  - Proposal includes cost model, security assessment, and alternative analysis
  - Security implications reviewed and acceptable (or conditions defined)
  - Cost model within budget or escalation path defined
  - Architectural consistency with existing patterns (or justified divergence documented)
  - No unresolved CRITICAL security findings
- **Failure Action**: Reject or Defer with documented rationale; requesting team revises and resubmits in next weekly cycle

### 9. Success Criteria

- All CARB decisions made within one weekly cycle (no proposal waits more than 7 days)
- Rejected proposals receive documented rationale within 24 hours
- Zero new cloud services adopted without CARB review (detected via cloud inventory scanning)
- All "Approve with conditions" items tracked to completion

### 10. Dependencies

| Dependency | Process/System | Type | Impact if Missing |
|------------|---------------|------|-------------------|
| P-006 | Technology Vision | Process | CARB lacks architectural guardrails to evaluate proposals against |
| Approved services list | Cloud Architect artifact | Artifact | No baseline to compare new service proposals against |
| Cloud inventory scanning | Infrastructure | System | Unapproved service adoption goes undetected |

### 11. Traceability

- **Clarity of Intent alignment**: Supports Stage 2 Scope Contract, Section 6 (Assumptions and Risks) -- CARB ensures cloud architecture decisions are explicitly reviewed, preventing the "we assumed this service was available" class of risks
- **Org Structure alignment**: Cloud Architect role (Section 3.6 -- chairs CARB); Principal/Staff Engineer cross-org influence (Section 2.3); FinOps Engineer cost governance (Section 3.6); Security Architect (Section 3.7)
- **Upstream processes**: P-006 (Technology Vision provides guardrails)
- **Downstream processes**: P-045 (Infrastructure Provisioning -- CARB approval required before large IaC changes proceed)

---

## P-048: Production Release Management Process

### 1. Process Identity

- **Process ID**: P-048
- **Name**: Production Release Management Process
- **Purpose**: Structured release process ensuring all quality, security, and reliability gates pass before production deployment. Release Manager owns the go/no-go decision. No release proceeds without explicit authorization.
- **Derived From**: Release Manager role responsibilities; CAB process; Engineering_Team_Structure_Guide (Section 3.5 -- Release Manager, Section 13 -- Operational Framework)
- **Risk Level**: HIGH -- uncontrolled production releases are the primary source of incidents

### 2. Ownership

- **Primary Owner Agent**: `technical-program-manager` (Release Manager owns go/no-go decision)
- **Supporting Agents**:
  - `sre` -- performs reliability check (SLO status, error budgets, monitoring readiness)
  - `security-engineer` -- provides security clearance (SAST/DAST results, threat model status)
  - `qa-engineer` -- provides final QA sign-off (acceptance criteria verified, regression suite passed)
  - `infra-engineer` -- executes deployment via CI/CD pipeline; manages rollback procedures

### 3. Stages/Steps

| Step | Action | Owner | Duration |
|------|--------|-------|----------|
| 1 | **Schedule release window**: Release Manager selects deployment window based on change risk, traffic patterns, and team availability for monitoring | technical-program-manager | 1-2 days before release |
| 2 | **Pre-release checklist execution**: Verify all items: (a) all stories in DoD-complete state, (b) SAST/DAST scans clean, (c) performance tests passed, (d) runbooks updated, (e) rollback procedure documented and tested, (f) SLO monitoring dashboards confirmed active | technical-program-manager + all supporting agents | 0.5-1 day |
| 3 | **CAB review (if HIGH-risk)**: If the release is classified as HIGH-risk (per P-076 criteria), trigger Change Advisory Board review for additional approval | technical-program-manager | Conditional (per P-076 cadence) |
| 4 | **Go/no-go decision**: Release Manager confirms all pre-release checklist items pass; issues formal go/no-go declaration; any single failing item blocks the release | technical-program-manager | 30 minutes |
| 5 | **Staged rollout**: Deployment follows canary (1-5% traffic) then gradual expansion (25%, 50%, 100%) pattern; each stage monitored for error rate, latency, and SLO compliance | infra-engineer + sre | 1-4 hours (depends on rollout stages) |
| 6 | **Post-deployment smoke tests**: Automated smoke test suite runs against production; results reviewed within 30 minutes of deployment | qa-engineer + infra-engineer | 30 minutes |
| 7 | **Rollback readiness**: If smoke tests fail or SLO breach detected, rollback procedure executed immediately; incident process triggered if customer impact detected | sre + infra-engineer | Minutes (automated rollback) |
| 8 | **Release record**: Release Manager documents final release record: version, components deployed, checklist results, rollout timeline, any issues encountered | technical-program-manager | 1 hour post-deployment |

### 4. Pre-Release Checklist (Detailed)

All items must be verified before go/no-go decision:

| # | Checklist Item | Verifier | Evidence Required |
|---|---------------|----------|-------------------|
| 1 | All stories in DoD-complete state (P-034) | qa-engineer | Story tracker shows all stories DONE with DoD verification |
| 2 | SAST scan clean -- no new critical or high findings (P-039) | security-engineer | SAST report with zero new critical/high findings |
| 3 | DAST scan clean -- no new critical findings (P-039) | security-engineer | DAST report attached to release record |
| 4 | Performance tests passed -- no regression beyond thresholds (P-035) | qa-engineer | Performance test report with comparison to baseline |
| 5 | Runbooks updated for new/changed components (P-054) | sre | Runbook review approval in PR |
| 6 | Rollback procedure documented and tested | infra-engineer | Rollback test execution record |
| 7 | SLO monitoring dashboards active and alerting configured | sre | Dashboard URLs confirmed; alert test fired |
| 8 | Feature flags configured for gradual rollout | infra-engineer | Feature flag configuration in management tool |
| 9 | Database migrations tested and reversible (if applicable) | software-engineer (via qa-engineer verification) | Migration test results |
| 10 | External dependency health confirmed | sre | Dependency health check results |

### 5. Inputs

- DoD-complete stories (from squad delivery processes)
- SAST/DAST scan results (from P-039)
- Performance test results (from P-035)
- Updated runbooks (from P-054)
- SLO monitoring configuration (from SRE)
- Rollback procedure documentation
- CAB approval (if HIGH-risk, from P-076)

### 6. Outputs/Artifacts

| Artifact | Format | Storage | Owner |
|----------|--------|---------|-------|
| Pre-release checklist (completed) | Checklist document with evidence links | Release management system | technical-program-manager |
| Go/no-go decision record | Formal declaration with timestamp | Release management system | technical-program-manager |
| Production deployment | Deployed software | Production environment | infra-engineer |
| Release record | Structured document (version, components, timeline, issues) | Release management system | technical-program-manager |
| Smoke test results | Automated test report | CI/CD system | qa-engineer |
| Rollback readiness confirmation | Documented procedure + test evidence | Release management system | infra-engineer |

### 7. Gate/Checkpoint

- **Gate Name**: Release Go/No-Go Gate
- **Trigger**: Every production release
- **Participants**: Release Manager (technical-program-manager), SRE, Security Engineer, QA Engineer, Platform Engineer, squad TL(s)
- **Pass Criteria**:
  - All 10 pre-release checklist items verified with evidence
  - No unresolved CRITICAL or HIGH severity issues in release scope
  - CAB approval obtained (if HIGH-risk change per P-076)
  - Rollback procedure tested within the last 30 days
  - At least one SRE available for monitoring during rollout window
- **Failure Action**: Release blocked; Release Manager documents blocking items; release rescheduled when items are resolved

### 8. Success Criteria

- No release proceeds without Release Manager go/no-go declaration
- All pre-release checklist items confirmed before deployment
- Post-deployment smoke tests pass within 30 minutes of deployment
- Staged rollout followed for all releases (canary before full deployment)
- Rollback executed within 15 minutes when triggered
- Zero releases with missing security clearance (SAST/DAST)

### 9. Dependencies

| Dependency | Process/System | Type | Impact if Missing |
|------------|---------------|------|-------------------|
| P-034 | DoD Enforcement | Process | Cannot verify stories are truly complete |
| P-035 | Performance Testing | Process | No performance regression data for go/no-go |
| P-039 | SAST/DAST Security Scanning | Process | No security clearance for release |
| P-076 | CAB (Change Advisory Board) | Process | HIGH-risk changes lack additional governance |
| P-054 | SLO/Runbook Management | Process | Runbooks not updated; SLO monitoring not configured |
| CI/CD deployment pipeline | infra-engineer maintained | System | No automated staged rollout capability |
| Feature flag management system | Infrastructure | System | No gradual rollout or kill switch capability |

### 10. Traceability

- **Clarity of Intent alignment**: Supports Stage 4 Sprint Bridge, Section 5 (Definition of Done -- Sprint Level) -- the release process enforces the DoD items listed in Clarity of Intent: "Code reviewed", "Automated tests passing", "SAST scan clean", "Deployed to staging and smoke-tested"
- **Org Structure alignment**: Release Manager role (Section 3.5 -- owns go/no-go, chairs CAB); SRE Lead (Section 3.5 -- reliability gates); Platform Engineer (Section 3.5 -- deployment execution); TPM cross-team coordination (Section 2.1 -- Cross-Cutting Roles)
- **Upstream processes**: P-034, P-035, P-039, P-054, P-076 (all feed into pre-release checklist)
- **Downstream processes**: P-054 (runbook is a pre-release requirement -- bidirectional); incident management processes (triggered if post-deployment issues detected)

---

## Cross-Process Dependency Map

```
P-006 (Technology Vision)
  └──> P-047 (CARB) ──> P-045 (Infrastructure Provisioning)
                              │
P-044 (Golden Path) ──────────┼──> P-046 (Environment Self-Service)
                              │
                              └──> P-048 (Production Release Management)
                                        │
                         P-034 (DoD) ───┤
                         P-035 (Perf) ──┤
                         P-039 (SAST) ──┤
                         P-054 (SLO) ───┤
                         P-076 (CAB) ───┘
```

### Dependency Flow Summary

1. **P-047 (CARB)** depends on P-006 (Technology Vision) for architectural guardrails
2. **P-045 (Infrastructure Provisioning)** depends on P-047 (CARB) for large change approval
3. **P-044 (Golden Path)** is foundational -- no upstream process dependencies within this category
4. **P-046 (Environment Self-Service)** depends on both P-044 (templates) and P-045 (IaC modules)
5. **P-048 (Production Release Management)** depends on P-034, P-035, P-039, P-054, P-076 from other categories; uses infrastructure from P-045

---

## Agent Responsibility Matrix (RACI)

| Activity | infra-engineer (platform) | infra-engineer (cloud) | technical-program-manager | sre | security-engineer | qa-engineer | engineering-manager | staff-principal-engineer | technical-writer |
|----------|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| P-044: Golden path template creation | **R/A** | C | - | - | - | - | I | - | C |
| P-044: Developer NPS measurement | C | - | - | - | - | - | **R/A** | - | - |
| P-045: IaC PR review | C | **R/A** | - | C | - | - | - | - | - |
| P-045: Drift detection | - | **R/A** | - | C | - | - | - | - | - |
| P-046: Self-service catalog build | **R/A** | C | - | - | - | - | I | - | - |
| P-047: CARB chair/decision | - | **R/A** | - | - | C | - | C | C | - |
| P-048: Go/no-go decision | C | - | **R/A** | C | C | C | I | - | - |
| P-048: Deployment execution | **R** | - | **A** | C | - | - | I | - | - |
| P-048: Post-deploy smoke tests | C | - | I | C | - | **R** | - | - | - |

**Legend**: R = Responsible, A = Accountable, C = Consulted, I = Informed

---

## Appendix: Glossary of Terms

| Term | Definition |
|------|-----------|
| **Golden Path** | The opinionated, supported, default way to build and deploy a service; the path of least resistance that also meets all organizational standards |
| **IaC (Infrastructure as Code)** | Managing infrastructure through version-controlled code (Terraform, CDK, Pulumi) rather than manual configuration |
| **IDP (Internal Developer Platform)** | The set of tools, templates, and self-service capabilities that reduce cognitive load for product development teams |
| **CARB** | Cloud Architecture Review Board -- governance body for cloud architecture decisions |
| **CAB** | Change Advisory Board -- governance body for high-risk production changes (P-076) |
| **NPS** | Net Promoter Score -- survey metric measuring developer satisfaction with platform tools |
| **Drift Detection** | Automated scanning that identifies differences between declared IaC state and actual cloud resource state |
| **Staged Rollout** | Deploying to progressively larger portions of traffic (canary -> gradual -> full) to limit blast radius |
| **TTL** | Time-to-live -- automatic expiry period for temporary resources |

---

## Cross-Category Dependencies

### Dependencies FROM Other Categories (Inputs)

| Source Process | Source Category | Consuming Process | Nature |
|---------------|----------------|-------------------|--------|
| P-006 (Technology Vision Alignment) | Cat 1: Intent & Strategic Alignment | P-047 (CARB) | Technology vision provides architectural guardrails |
| P-034 (DoD Enforcement) | Cat 5: Quality Assurance | P-048 (Production Release Mgmt) | DoD verification before release |
| P-035 (Performance Testing) | Cat 5: Quality Assurance | P-048 (Production Release Mgmt) | Performance tests passed |
| P-039 (SAST/DAST) | Cat 6: Security | P-048 (Production Release Mgmt) | Security scans clean |
| P-076 (CAB) | Cat 13: Risk & Change | P-048 (Production Release Mgmt) | CAB approval for HIGH-risk changes |
| P-089 (Developer Experience Survey) | Cat 16: Technical Excellence | P-044 (Golden Path Adoption) | Developer NPS measures satisfaction |

### Dependencies TO Other Categories (Outputs)

| Providing Process | Consuming Process | Target Category | Nature |
|------------------|-------------------|-----------------|--------|
| P-045 (Infrastructure Provisioning) | P-035 (Performance Testing) | Cat 5: Quality Assurance | Load test environments |
| P-045 (Infrastructure Provisioning) | P-046 (Environment Self-Service) | Cat 7 (self) | IaC enables self-service |
| P-048 (Production Release Mgmt) | P-059 (Runbook Authoring) | Cat 10: Documentation | Runbooks required before release |
| P-048 (Production Release Mgmt) | P-061 (Release Notes) | Cat 10: Documentation | Release triggers release notes |
| P-048 (Production Release Mgmt) | P-073 (Post-Launch Outcome Measurement) | Cat 12: Post-Delivery | Release enables 30/60/90-day measurement |
| P-044 (Golden Path Adoption) | P-090 (New Engineer Onboarding) | Cat 17: Onboarding | Golden path for environment setup |

## Agent Assignments Summary

| Process | Primary Owner | Supporting Agents |
|---------|--------------|-------------------|
| P-044: Golden Path Adoption | infra-engineer | infra-engineer, engineering-manager, technical-writer |
| P-045: Infrastructure Provisioning | infra-engineer | infra-engineer, sre |
| P-046: Environment Self-Service | infra-engineer (DX Engineer) | infra-engineer |
| P-047: Cloud Architecture Review Board (CARB) | infra-engineer (Cloud Architect) | staff-principal-engineer, security-engineer, engineering-manager |
| P-048: Production Release Management | technical-program-manager (Release Manager) | sre, security-engineer, qa-engineer, infra-engineer |
