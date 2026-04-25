# Process Injection Map: Auto-Orchestrate ↔ Organizational Processes

**Version**: 2.0  
**Date**: 2026-04-14  
**Produced by**: software-engineer (Task #8, SPEC T018; expanded A3)  
**Status**: Active — Scope-conditional injection (PROCESS-SCOPE-001)

---

## Executive Summary

The auto-orchestrate pipeline (Stages 0-6) and the organizational process framework (P-001 through P-093) run in parallel. This document defines the **process injection map**: a cross-reference table identifying which organizational processes apply at each auto-orchestrate stage, the injection event that triggers process engagement, whether the hook blocks pipeline advancement, and the **scope condition** that determines when the hook is active.

V1 mapped 18 processes to pipeline stages. V2 expands coverage to all 93 processes via scope-conditional injection (PROCESS-SCOPE-001). Not all processes apply to every task — the triage gate classifies process scope as TRIVIAL, MEDIUM, or COMPLEX, and injection hooks only fire when their scope condition is met.

---

## Process Coverage by Command — with Dispatch (E1)

This section shows which commands execute which process ranges, and how the Command Dispatcher (DISPATCH-001) extends coverage from the Big Three autonomous loops.

```
BEFORE DISPATCH-001 (direct execution only):

P-001───006  Intent       │ new-proj │ auto-orch │          │          │
P-007───014  Scope        │ new-proj │ auto-orch │          │          │
P-015───021  Dependencies │ new-proj │ auto-orch │          │          │
P-022───031  Sprint       │ sprint   │ active    │ auto-orch│          │
P-032───037  QA           │ qa       │ active    │ auto-orch│          │
P-038───043  Security     │ security │ active    │ auto-orch│ audit    │
P-044───048  Infra        │ infra    │ release   │          │          │
P-049───053  Data/ML      │ data-ml  │           │          │          │
P-054───057  SRE          │ post-lnch│           │          │          │
P-058───061  Docs         │ auto-orch│ active    │          │          │
P-062───069  Org Audit    │ org-ops  │           │ auto-orch│ audit    │
P-070───073  Retro        │ post-lnch│           │          │          │
P-074───077  Risk         │ risk     │ release   │          │          │
P-078───081  Comms        │ org-ops  │           │          │          │
P-082───084  Capacity     │ org-ops  │           │          │          │
P-085───089  Tech Excl    │ org-ops  │           │          │          │
P-090───093  Onboarding   │ org-ops  │           │          │          │
                          │ Phase/   │ Phase/    │Autonomous│Autonomous│
                          │ Domain   │ Domain    │Loop      │Loop      │

AFTER DISPATCH-001 (all accessible via Big Three):

P-001───006  Intent       │ new-proj │ auto-orch │          │          │
P-007───014  Scope        │ new-proj │ auto-orch │          │          │
P-015───021  Dependencies │ new-proj │ auto-orch │          │          │
P-022───031  Sprint       │ sprint ◄─┤ active ◄──┤ auto-orch│          │
P-032───037  QA           │ qa ◄─────┤ active ◄──┤ auto-orch│          │
P-038───043  Security     │ security◄┤ active ◄──┤ auto-orch│ audit    │
P-044───048  Infra        │ infra ◄──┤ release◄──┤ auto-orch│          │
P-049───053  Data/ML      │ data-ml◄─┤           │ auto-orch│          │
P-054───057  SRE          │ post-l ◄─┤           │ auto-orch│          │
P-058───061  Docs         │          │           │ auto-orch│          │
P-062───069  Org Audit    │ org-ops◄─┤           │ auto-orch│ audit    │
P-070───073  Retro        │ post-l ◄─┤           │ auto-orch│          │
P-074───077  Risk         │ risk ◄───┤ release◄──┤ auto-orch│          │
P-078───081  Comms        │ org-ops◄─┤           │          │          │
P-082───084  Capacity     │ org-ops◄─┤           │          │          │
P-085───089  Tech Excl    │ org-ops◄─┤           │          │          │
P-090───093  Onboarding   │ org-ops◄─┤           │          │          │

  ◄── = accessible via command dispatcher from Big Three
```

**Key insight**: After DISPATCH-001, auto-orchestrate can reach ALL 93 processes — either directly (injection hooks), via domain guide dispatch (Tier 2), or via Tier 1 suggestions for phase commands. This makes auto-orchestrate the universal process coverage gateway.

---

## Injection Table: Auto-Orchestrate Stage → Organizational Process

### Core Injection Hooks (All Scope Tiers)

These hooks fire for ALL tasks regardless of triage complexity. They represent the minimum process coverage.

| AO Stage | Stage Name | Agent | Primary Org Processes | Injection Event | Action | Enforced |
|----------|-----------|-------|----------------------|----------------|--------|----------|
| Stage 0 | Research | researcher | P-001 (Intent Articulation), P-038 (Threat Modeling) | Before Stage 0: Verify P-001 Intent Brief exists in handoff receipt; researcher notes P-038 threat-model concerns | notify | false |
| Stage 1 | Product Management | product-manager | P-007 (Deliverable Decomposition), P-008 (Definition of Done Authoring), P-009 (Success Metrics Definition), P-010 (Assumptions and Risks Registration) | During Stage 1: Link task decomposition to P-007; DoD per epic = P-008; metrics per P-009; RAID seed per P-010 | link | false |
| Stage 2 | Specification | spec-creator | P-033 (Automated Test Framework), P-038 (Threat Modeling) | During Stage 2: Spec must reference P-033 automated test framework requirements; P-038 threat-model security requirements embedded | gate | **true** (P-038 only) |
| Stage 3 | Implementation | software-engineer | P-031 (Feature Development), P-034 (Definition of Done Enforcement), P-036 (Acceptance Criteria Verification), P-040 (CVE Triage) | After Stage 3: Present P-034 DoD checklist; P-036 acceptance criteria verified; P-040 CVE triage for new dependencies | notify | false |
| Stage 4 | Test Writing | test-writer-pytest | P-035 (Performance Testing), P-037 (Contract Testing) | During Stage 4: Tests must cover P-035 performance test requirements; P-037 contract tests for service boundaries | link | false |
| Stage 4.5 | Codebase Stats | codebase-stats | P-086 (Technical Debt Tracking) | After Stage 4.5: Tech debt report written; new debt items logged per P-086 | link | false |
| Stage 5 | Validation | validator | P-034 (Definition of Done Enforcement), P-036 (Acceptance Criteria Verification), P-037 (Contract Testing) | Before Stage 5 exit: Confirm P-034 + P-036 + P-037 pass criteria met in validation report | gate | **true** (P-034, P-037) |
| Stage 6 | Documentation | technical-writer | P-058 (API Documentation), P-059 (Runbook Authoring), P-061 (Release Notes) | After Stage 6: Link Stage 6 docs to P-058 + P-059 + P-061 process records; P-058 acknowledgment required | gate | **true** (P-058) |

### MEDIUM Scope Injection Hooks (scope_condition: medium+)

These hooks fire only when triage classifies the task as MEDIUM or COMPLEX complexity.

| AO Stage | Stage Name | Org Processes | Injection Event | Action | Enforced | Internal Phase |
|----------|-----------|---------------|----------------|--------|----------|-------------|
| Stage 1 | Product Mgmt | P-011 (Exclusion Documentation), P-013 (Scope Lock), P-014 (Change Control) | During Stage 1: Link scope deliverables to P-011 exclusions and P-013 lock criteria | link | false | — |
| Stage 2 | Specification | P-032 (Test Architecture Design) | During Stage 2: Spec includes testability section aligned with P-032 | link | false | Phase 5q |
| Stage 3 | Implementation | P-039 (SAST/DAST CI Integration) | After Stage 3: Verify P-039 SAST/DAST scans run against new code; log scan results | link | false (upgradeable to GATE via ENFORCE-UPGRADE-001) | Phase 5s |
| Stage 5 | Validation | P-039 (SAST/DAST CI Verification) | During Stage 5: Validator checks P-039 scan results; CRITICAL/HIGH findings must be addressed | gate | false (upgradeable to GATE via ENFORCE-UPGRADE-001) | Phase 5s |
| Stage 6 | Documentation | P-060 (ADR Publication) | After Stage 6: If architecture decisions made, publish ADR per P-060 | link | false | — |

### COMPLEX Scope Injection Hooks (scope_condition: complex)

These hooks fire only when triage classifies the task as COMPLEX.

| AO Stage | Stage Name | Org Processes | Injection Event | Action | Enforced | Internal Phase |
|----------|-----------|---------------|----------------|--------|----------|-------------|
| Stage 0 | Research | P-002 (OKR Alignment), P-003 (Boundary Definition) | Before Stage 0: Link research scope to P-002 OKR alignment and P-003 boundaries | link | false | — |
| Stage 0 | Research | P-005 (Strategic Prioritization), P-006 (Technical Vision) | Before Stage 0: Note P-005/P-006 as reference for research framing | informational | false | — |
| Stage 0 | Research | P-074 (RAID Log), P-075 (Risk Register at Scope Lock) | During Stage 0: Researcher notes risks for P-074 RAID log seeding | link | false | Phase 9 |
| Stage 1 | Product Mgmt | P-012 (AppSec Scope Review) | During Stage 1: Link security scope to P-012 review | link | false | — |
| Stage 1 | Product Mgmt | P-022 (Sprint Goals), P-023 (Intent Trace), P-024 (Story Writing) | During Stage 1: Product-manager aligns task decomposition with P-022-024 sprint patterns | notify | false | — |
| Stage 2 | Specification | P-085 (RFC Process) | During Stage 2: If architectural decision required, reference P-085 RFC template | informational | false | — |
| Stage 3 | Implementation | P-086 (Technical Debt Tracking) | After Stage 3: Log new tech debt items per P-086 | link | false | — |
| Stage 3 | Implementation | P-060 (ADR Publication) | During Stage 3: If architecture decisions made during impl, draft ADR per P-060 | notify | false | — |
| Stage 5 | Validation | P-076 (Pre-Launch Risk Review) | Before Stage 5: If release_flag is true, reference P-076 pre-launch checklist | notify | false | Phase 9 |
| Stage 6 | Documentation | P-088 (Architecture Pattern Change) | After Stage 6: If new architecture patterns established, register per P-088 | informational | false | — |

### Domain-Conditional Injection Hooks (scope_condition: complex + domain flag)

These hooks fire only when triage classifies the task as COMPLEX AND the corresponding domain flag is active.

| AO Stage | Domain Flag | Org Processes | Injection Event | Action | Enforced | Internal Phase |
|----------|-----------|---------------|----------------|--------|----------|-------------|
| Stage 0 | `infra` | P-015 (Register Dependencies), P-016 (Critical Path) | During Stage 0: Researcher identifies cross-team infra dependencies | notify | false | — |
| Stage 2 | `infra` | P-044 (Golden Path Adoption), P-046 (Environment Self-Service) | During Stage 2: Spec references P-044 golden path for deployment | link | false | Phase 5i |
| Stage 2 | `data_ml` | P-049 (Pipeline Quality), P-050 (Schema Migration) | During Stage 2: Spec includes data quality and migration requirements | link | false | Phase 5d |
| Stage 3 | `infra` | P-045 (Infrastructure Provisioning) | During Stage 3: IaC must follow P-045 (no manual provisioning) | notify | false | Phase 5i |
| Stage 3 | `data_ml` | P-051 (ML Experiment Logging) | During Stage 3: ML code must include experiment logging per P-051 | notify | false | Phase 5d |
| Stage 5 | `infra` | P-047 (Cloud Architecture Review), P-048 (Production Release Management) | Before Stage 5: Validate against P-047 CARB checklist; P-048 release gates | notify | false | Phase 5i |
| Stage 5 | `data_ml` | P-052 (Model Canary Deployment), P-053 (Data Drift Monitoring) | During Stage 5: Validate canary deployment config and drift monitoring setup | notify | false | Phase 5d |
| Stage 5 | `sre` | P-054 (SLO Definition), P-055 (Incident Response Readiness) | During Stage 5: Validate SLO coverage and incident response runbook | notify | false | — |
| Stage 6 | `sre` | P-056 (Post-Mortem Template), P-057 (On-Call Rotation) | After Stage 6: Reference P-056/P-057 in operational documentation | informational | false | — |

### Post-Pipeline Injection Hooks (Internal Phase Auto-Invocation)

These processes apply after the execution pipeline completes. They are auto-invoked as internal phases by the auto-orchestrate loop controller per AUTO-EVAL-001 — no human pause, no separate command.

| Timing | Org Processes | Condition | Internal Phase | Action |
|--------|---------------|-----------|----------------|--------|
| Post-Stage 6 | P-070 (Post-Mortem), P-071 (Process Health Review) | COMPLEX + terminal_state == completed | Phase 8 (Post-Launch) | auto-invoke |
| Post-Stage 6 | P-073 (Outcome Measurement) | COMPLEX + terminal_state == completed | Phase 8 (Post-Launch) | auto-invoke |
| Post-Stage 6 | P-090 (New Engineer Onboarding), P-091 (New Project Onboarding), P-092 (Knowledge Transfer), P-093 (Technical Onboarding for Cross-Team Dependencies) | COMPLEX + terminal_state == completed | Phase 9 (Continuous Governance — onboarding sub-routine) | auto-invoke |
| Post-P4 | P-025 (Sprint Readiness), P-026 (Daily Standup cadence), P-027 (Sprint Review), P-028 (Retrospective) | COMPLEX + planning completed | Phase 4 inline (Sprint Kickoff Ceremony) | auto-invoke |

### Organizational-Only Processes (Informational Reference)

These processes are genuinely organizational — they involve human coordination, team dynamics, or cadences that cannot be automated. They are logged as `[PROCESS-INFO]` in process receipts but never dispatched.

| Category | Processes | Rationale |
|----------|-----------|-----------|
| Communication & Alignment (Cat 14) | P-078 (OKR Cascade Communication), P-079 (Stakeholder Update Cadence), P-080 (Guild Standards Communication), P-081 (DORA Metrics Review and Sharing) | Require org-level human coordination and cadences |
| Capacity & Resource Management (Cat 15) | P-082 (Quarterly Capacity Planning), P-083 (Shared Resource Allocation), P-084 (Succession Planning) | Human management decisions; quarterly planning cycles |
| Technical Excellence (partial) | P-087 (Language Tier Policy Change), P-089 (Developer Experience Survey) | Org-wide policies and surveys; not task-scoped |
| Sprint Delivery (partial) | P-029 (Backlog Refinement — handled at iteration boundaries via meeting), P-030 (Sprint-Level Dependency Tracking — handled in P4 + Dependency Standup) | These appear in the pipeline (P-029 as PHASE: BACKLOG_REFINEMENT, P-030 as P4 co-agent) but are listed here for cross-reference; not "organizational-only" |
| Dependency Coordination (partial) | P-017 (Resource Conflicts), P-018 (Communication Plan), P-019 (Dependency Acceptance Gate), P-020 (Dependency Standups), P-021 (Escalation Protocol) | Require cross-team human coordination |

---

## Process Coverage Summary (PROCESS-SCOPE-001)

V2 of the injection map provides coverage for all 93 processes across four tiers:

| Coverage Tier | Process Count | Mechanism |
|--------------|--------------|-----------|
| **Core** (all tasks) | 18 processes | Direct injection hooks — fire for every task |
| **MEDIUM+** | +9 processes (27 total) | Scope-conditional hooks — fire when triage ≥ MEDIUM |
| **COMPLEX** | +15 processes (42 total) | Scope-conditional hooks — fire when triage = COMPLEX |
| **Domain-conditional** | +14 processes (56 total) | Scope + domain flag hooks — fire when COMPLEX + domain flag active |
| **Post-pipeline** | +8 processes (64 total) | Tier 1 suggest — surfaced after pipeline completion |
| **Organizational-only** | 16 processes (80 total) | Informational reference — logged but not dispatched |
| **Implicitly covered** | 13 processes (93 total) | Covered by parent process or stage agent natively |

### Meetings Coverage (MEETING-001)

The canonical end-to-end process specifies meetings/ceremonies that the pipeline implements via three handler types. See `_shared/protocols/command-dispatch.md` "Meeting Catalog" for the canonical mapping. Every canonical meeting is implemented:

| P-XXX | Meeting | Handler Type | Pipeline Implementation |
|-------|---------|--------------|-------------------------|
| P-004 | Intent Review | Human-Gated | Gate `intent-review` (Phase 1 end) |
| P-013 | Scope Lock | Human-Gated | Gate `scope-lock` (Phase 2 end) |
| P-019 | Dependency Acceptance | Human-Gated | Gate `dependency-acceptance` (Phase 3 end) |
| P-025 | Sprint Readiness | Human-Gated | Gate `sprint-readiness` (Phase 4 end) |
| (Phase 4) | Sprint Kickoff | Multi-Agent Sync | `PHASE: SPRINT_CEREMONY` (Phase 4 inline) |
| P-026 | Daily Standup | Multi-Agent Sync | `PHASE: DAILY_STANDUP` (iteration boundary) |
| P-020 | Dependency Standup | Multi-Agent Sync | `PHASE: DEPENDENCY_STANDUP` (iteration boundary, conditional) |
| P-029 | Backlog Refinement | Async Single-Agent | `PHASE: BACKLOG_REFINEMENT` (iteration boundary or post-retro) |
| P-027 | Sprint Review | Multi-Agent Sync | `PHASE: SPRINT_REVIEW` (post-Stage 6) |
| P-028 | Sprint Retrospective | Multi-Agent Sync | `PHASE: SPRINT_RETRO` (post-Sprint Review) |
| P-076 | Pre-Launch Risk Review (CAB) | Human-Gated | Gate `cab-review` (Phase 7 prelude, when HIGH-risk) |
| P-077 | Quarterly Risk Review | Async Single-Agent | Phase 9 risk sub-routine |
| P-082 | Quarterly Capacity Planning | Hybrid (Async + final gate) | Phase 9 capacity sub-routine |

**Total**: 8 human-gated meetings + 5 multi-agent sync meetings + 2 async single-agent meetings + 1 hybrid (Phase 9 sub-routine) = **16 canonical meetings**, all implemented.

### Previously Stubbed Processes — Integration Status

| Stub | Processes | V1 Status | V2 Status | Integration |
|------|-----------|-----------|-----------|-------------|
| Sprint Planning | P-022, P-023, P-024 | STUB | **INTEGRATED-ADVISORY** | Injected at Stage 1 (COMPLEX scope) as notify hooks |
| Dependency Coordination | P-015, P-016 | STUB (partial) | **INTEGRATED-ADVISORY** | P-015/P-016 injected at Stage 0 (COMPLEX + infra flag); P-017-021 remain organizational-only |
| Onboarding | P-090, P-091, P-092, P-093 | STUB | **POST-PIPELINE** | Surfaced as informational at pipeline completion (COMPLEX scope) |

---

## Hook Format Specification

Each injection hook is defined with the following fields. Hooks are stored in process receipts and logged to the orchestrator output.

```yaml
hook:
  ao_stage: 3
  ao_agent: software-engineer
  event: "after_stage_complete"
  process_ids: ["P-034", "P-036"]
  action: "notify"
  enforcement_tier: "ADVISORY"
  action_detail: >
    After Stage 3 (software-engineer) completes: present P-034 Code Review
    checklist to user. Gate optional — user may proceed without P-034
    in auto mode but must acknowledge the skip.
  output_artifact: null
  enforced: false
  scope_condition: "all"
  domain_flag: null
```

**Field definitions**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ao_stage` | integer or string | YES | The AO pipeline stage number (0, 1, 2, 3, 4, 4.5, 5, 6) or `"post"` for post-pipeline |
| `ao_agent` | string | YES | The agent name that triggers this hook (e.g., "software-engineer", "validator") |
| `event` | string | YES | When the hook fires: `"before_stage_start"`, `"during_stage"`, `"after_stage_complete"` |
| `process_ids` | string[] | YES | List of organizational process IDs this hook engages (e.g., ["P-034", "P-036"]) |
| `action` | string | YES | One of: `"notify"`, `"gate"`, `"link"`, `"informational"`, `"suggest"` |
| `enforcement_tier` | string | YES | One of: `"GATE"`, `"ADVISORY"`, `"INFORMATIONAL"`. See Three-Tier Enforcement Model. Default derived from `action`: gate→GATE, notify/link→ADVISORY, informational/suggest→INFORMATIONAL. Can be upgraded by ENFORCE-UPGRADE-001 based on triage complexity. |
| `action_detail` | string | YES | Human-readable description of what happens when this hook fires |
| `output_artifact` | string or null | NO | Path to a file written by this hook, if any. Null if the hook only logs. |
| `enforced` | boolean | YES | `true` = blocks AO pipeline advancement until acknowledged; `false` = advisory only |
| `scope_condition` | string | YES | Minimum triage tier for this hook to fire: `"all"`, `"medium"`, `"complex"`. Default: `"all"`. |
| `domain_flag` | string or null | NO | Required domain flag for this hook to fire: `"infra"`, `"data_ml"`, `"sre"`, `"risk"`, or `null` (no domain restriction). Only evaluated when `scope_condition` is `"complex"`. |
| `phase` | string or null | NO | If this hook's process is handled by an internal phase, the phase ID (e.g., `"5s"` for Security, `"5q"` for Quality, `"5i"` for Infra/SRE, `"5d"` for Data/ML, `"9"` for Continuous Governance). Used by the auto-orchestrate loop controller to route findings to the right phase agent. |

**Action type definitions**:

- `notify` — Log a message to orchestrator output at the injection event. Does not block pipeline. Format: `[PROCESS-INJECT] Stage {N} ({event}): {process_ids} — {action_detail}`
- `gate` — Block pipeline advancement until the process requirement is explicitly acknowledged by the user or by a passing validation check. Used only when `enforced: true`.
- `link` — Write a cross-reference entry to `.orchestrate/{session_id}/process_receipts.json` mapping the AO stage output to the organizational process record. Does not block pipeline.
- `informational` — Log `[PROCESS-INFO] {process_ids} noted as applicable. Reference: {process_file}.` No pipeline impact. Used for organizational-only processes.
- `auto-invoke` — Auto-invoke the corresponding internal phase. Logs `[PROCESS-INVOKE] Phase {phase_id} for {process_ids}.` No human pause per AUTO-EVAL-001.

**Scope condition evaluation**:

```
FUNCTION hook_is_active(hook, process_scope):
  IF hook.scope_condition == "all":
    RETURN true
  IF hook.scope_condition == "medium" AND process_scope.tier IN ["medium", "complex"]:
    RETURN true
  IF hook.scope_condition == "complex" AND process_scope.tier == "complex":
    IF hook.domain_flag is null:
      RETURN true
    IF hook.domain_flag IN process_scope.domain_flags:
      RETURN true
  RETURN false
```

---

## Three-Tier Process Enforcement Model (E2)

Every injection hook is classified into one of three enforcement tiers:

```
┌──────────────────────────────────────────────────────────────────┐
│  GATE (blocking):                                                │
│    Process MUST pass before pipeline advances.                   │
│    Failure = pipeline stops + notification.                      │
│    Maps to: action="gate", enforced=true                         │
│    Examples: P-034 (DoD Enforcement) at Stage 5                  │
│              P-037 (Contract Testing) at Stage 5                 │
│              P-058 (API Documentation) at Stage 6                │
│              P-038 (Threat Modeling) at Stage 2                  │
│                                                                  │
│  ADVISORY (non-blocking, tracked):                               │
│    Process runs and results are recorded, but pipeline           │
│    continues regardless of result. Failures appear in            │
│    final report as tech debt.                                    │
│    Maps to: action="notify" or "link", enforced=false            │
│    Examples: P-035 (Performance Testing) at Stage 4              │
│              P-040 (CVE Triage) at Stage 3                       │
│              P-086 (Technical Debt Tracking) at Stage 4.5        │
│                                                                  │
│  INFORMATIONAL (non-blocking, not tracked):                      │
│    Process provides context but has no pass/fail state.          │
│    Used for research, planning, and analysis processes.          │
│    Maps to: action="informational" or "suggest"                  │
│    Examples: P-001 (Intent Articulation) at Stage 0              │
│              P-016 (Critical Path Analysis) at P3                │
└──────────────────────────────────────────────────────────────────┘
```

### Triage-Based Enforcement Upgrading (ENFORCE-UPGRADE-001)

The enforcement tier of a hook can be **upgraded** (never downgraded) based on the triage complexity classification. This ensures that higher-complexity tasks receive stricter process enforcement.

| Triage Complexity | Enforcement Behavior |
|-------------------|---------------------|
| **TRIVIAL** | All hooks use their default tier. No GATE processes enforced (all ADVISORY or INFORMATIONAL). |
| **MEDIUM** | Security + DoD + acceptance processes are upgraded to GATE: P-034 (DoD Enforcement), P-036 (Acceptance Criteria Verification), P-038 (Threat Modeling), P-039 (SAST/DAST CI Integration) |
| **COMPLEX** | All MEDIUM gates PLUS testing processes upgraded: P-035 (Performance Testing), P-037 (Contract Testing) |

**Upgrade logic** (evaluated during triage at Step 0h-pre, stored in `checkpoint.triage.enforcement_overrides`):

```
FUNCTION compute_enforcement_overrides(complexity):
  IF complexity == "trivial":
    RETURN {}  # all hooks use default enforcement_tier
  
  overrides = {}
  
  IF complexity IN ["medium", "complex"]:
    # Security + code review → GATE
    overrides["P-034"] = "GATE"  # Code Review
    overrides["P-036"] = "GATE"  # Security Review
    overrides["P-038"] = "GATE"  # Security by Design
    overrides["P-039"] = "GATE"  # SAST/DAST
  
  IF complexity == "complex":
    # Testing → GATE
    overrides["P-035"] = "GATE"  # Performance Testing
    overrides["P-037"] = "GATE"  # Automated Testing
  
  RETURN overrides
```

**Runtime enforcement**: When evaluating an injection hook, the effective tier is:
```
effective_tier = enforcement_overrides.get(process_id, hook.enforcement_tier)
```

### Static Enforcement (always GATE regardless of triage)

These processes are always GATE — they cannot be downgraded by any triage result:

| Process | Stage | Enforcement Rationale |
|---------|-------|----------------------|
| P-038 (Threat Modeling) | Stage 2 | Threat-model security requirements cannot be skipped at specification time |
| P-034 (Definition of Done Enforcement) | Stage 5 exit | DoD enforcement is a quality gate; validation without DoD verification is incomplete |
| P-037 (Contract Testing) | Stage 5 exit | Contract test criteria must be verified against implementation |
| P-058 (API Documentation) | Stage 6 exit | API documentation is a mandatory pipeline stage |

---

## Process Deduplication Resolutions (E3)

Four potential process overlaps were identified. Resolutions:

| Overlap | Process A | Process B | Resolution |
|---------|-----------|-----------|------------|
| Testing | P-033 (Automated Test Framework) in main pipeline | P-037 (Contract Testing) in Phase 5q | **Keep both.** P-033 = framework setup, P-037 = API contract testing. Different scopes. |
| Code Review | P-034 at Stage 3 (ADVISORY) | P-034 at Stage 5 (GATE) | **Correct as-is.** Same process, different enforcement tiers at different lifecycle points. |
| Security | P-038 (AppSec) at Stage 0/2 | P-039 (SAST/DAST) via Phase 5s | **P-039 now injected at Stage 3 and Stage 5** (MEDIUM scope hooks). Previously only accessible via the deleted `/security` command; now an internal phase. |
| RAID Log | P-010 (RAID Log) at Stage 1 | P-074 (RAID Log) in Phase 9 | **Shared data store.** Both processes read/write the same RAID log file. See RAID-001 constraint below. |

### RAID-001: Single RAID Log Constraint

| ID | Rule |
|----|------|
| RAID-001 | **Single RAID log, append-only** — P-010 (Stage 1 seeding) and P-074 (risk management updates) share a single RAID log at `.orchestrate/{session_id}/raid-log.json`. Both processes append entries; neither overwrites. The product-manager (Stage 1) seeds initial RAID items from the Scope Contract. Phase 9 (Continuous Governance) appends risk updates during execution via its risk sub-routine. Format: JSONL, one entry per line, fields: `{ "id", "type": "Risk|Assumption|Issue|Dependency", "description", "severity", "owner", "status", "source_process", "timestamp" }`. |

---

## Process Stubs Directory

`claude-code/processes/process_stubs/` contains minimal process documents for organizational processes that have no home in either pipeline. Each stub:

1. **Identifies** the process gap (which processes are missing)
2. **Defines the scope** of the missing processes
3. **Provides a minimal process description** that agents can reference
4. **Specifies the trigger condition** for when these processes should be engaged
5. **Notes the integration path** for future pipeline integration

Stubs are NOT full process implementations — they are placeholders that prevent processes from being silently ignored. When a stub process is triggered, the orchestrator logs: `[PROCESS-STUB] {process_ids} — No full implementation. Reference: {stub_file}. Manual engagement required.`

---

## Integration with gate-state.json

Injection hooks that produce pass/fail outcomes (action: `"gate"`) MAY write their result to `.orchestrate/{session_id}/gate-state.json` (defined in SPEC T014 / `claude-code/processes/gate_state_schema.json`). The integration path:

1. Hook fires at its `event` trigger point
2. If `enforced: true` and `action: "gate"`: the hook presents the process checklist
3. If the user confirms all items pass: hook writes `gate_N.status: "passed"` and `checklist_items_passed` to gate-state.json
4. Pipeline advances
5. If any item fails: hook writes `gate_N.status: "failed"` and `fail_reason`; pipeline is blocked

This integration requires the gate enforcement mechanism from SPEC T014 to be operational. Until T015/T016 implement the enforcement in the commands, this integration is advisory.

---

## Implementation Notes for T019: Orchestrator Injection Points

The following locations in `claude-code/agents/orchestrator.md` (and `~/.claude/agents/orchestrator.md`) are the exact insertion points for process injection hooks. **T019 MUST NOT modify the orchestrator without the install.sh guard from SPEC T003 being in place.**

| Injection Point | Location in orchestrator.md | Hook IDs |
|-----------------|------------------------------|----------|
| Stage 0 pre-spawn | Stage 0 researcher spawn template — add after standard instructions | P-001 check, P-038 scope notify |
| Stage 2 post-completion | OODA `continue` branch after Stage 2 — add process gate for P-038 | P-038 gate (enforced) |
| Stage 3 post-impl | Post-impl fix loop completion — after `validation.errors == 0` | P-034 notify, P-036 notify, P-040 link |
| Stage 4.5 completion | After codebase-stats agent completes | P-062 link |
| Stage 5 pre-exit | Zero-error gate check — add process confirmation | P-034 notify, P-036 notify, P-037 notify |
| Stage 6 completion | After technical-writer completes — before PDCA Check phase | P-058 link, P-059 link, P-061 link |
| Run completion hook | `hook:run:complete` emission — add process receipts finalization | All linked processes |

**Exact file**: `claude-code/agents/orchestrator.md` (source) and `~/.claude/agents/orchestrator.md` (runtime).  
**Constraint**: Verify checksums equal before modifying (see `claude-code/agents/agent-reconciliation-notes.md`).  
**Verify post-modification**: `md5sum claude-code/agents/orchestrator.md ~/.claude/agents/orchestrator.md` — they must match after T019 modifies both.

---

## Organizational Process Reference Lookup

For full process definitions, see the following process handbook files:

| Process Range | Category | File | Internal Phase |
|--------------|----------|------|-------------|
| P-001 to P-006 | 1. Intent & Strategic Alignment | `claude-code/processes/01_intent_strategic_alignment.md` | — |
| P-007 to P-014 | 2. Scope & Contract Management | `claude-code/processes/02_scope_contract_management.md` | — |
| P-015 to P-021 | 3. Dependency & Coordination | `claude-code/processes/03_dependency_coordination.md` | — |
| P-022 to P-031 | 4. Sprint & Delivery Execution | `claude-code/processes/04_sprint_delivery_execution.md` | — |
| P-032 to P-037 | 5. Quality Assurance & Testing | `claude-code/processes/05_quality_assurance_testing.md` | Phase 5q |
| P-038 to P-043 | 6. Security & Compliance | `claude-code/processes/06_security_compliance.md` | Phase 5s |
| P-044 to P-048 | 7. Infrastructure & Platform | `claude-code/processes/07_infrastructure_platform.md` | Phase 5i |
| P-049 to P-053 | 8. Data & ML Operations | `claude-code/processes/08_data_ml_operations.md` | Phase 5d |
| P-054 to P-057 | 9. SRE & Operations | `claude-code/processes/09_sre_operations.md` | Phase 5i (sub-routine), Phase 8 (ongoing) |
| P-058 to P-061 | 10. Documentation & Knowledge | `claude-code/processes/10_documentation_knowledge.md` | Stage 6 |
| P-062 to P-069 | 11. Organizational Audit | `claude-code/processes/11_organizational_audit.md` | Phase 9 (audit sub-routine) |
| P-070 to P-073 | 12. Post-Delivery Retrospective | `claude-code/processes/12_post_delivery_retrospective.md` | Phase 8 |
| P-074 to P-077 | 13. Risk & Change Management | `claude-code/processes/13_risk_change_management.md` | Phase 9 (risk sub-routine) |
| P-078 to P-081 | 14. Communication & Alignment | `claude-code/processes/14_communication_alignment.md` | Phase 9 (cadence sub-routine) |
| P-082 to P-084 | 15. Capacity & Resource Mgmt | `claude-code/processes/15_capacity_resource_management.md` | Phase 9 (capacity sub-routine) |
| P-085 to P-089 | 16. Technical Excellence | `claude-code/processes/16_technical_excellence_standards.md` | Phase 9 (tech excellence sub-routine) |
| P-090 to P-093 | 17. Onboarding & Knowledge Transfer | `claude-code/processes/17_onboarding_knowledge_transfer.md` | Phase 9 (onboarding sub-routine) |

---

*Implements SPEC T018, Improvement A3 (PROCESS-SCOPE-001, PROCESS-DELEGATE-001) | References: T009 (bridge protocol), T014 (gate state schema), command-dispatch.md (TRIG-013)*
