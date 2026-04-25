# Complete Pipeline System — Optimization & Improvement Report
# Covers: 3 autonomous loops, 8 phase commands, 6 domain guides,
#         9 utility/workflow commands, 13 agents, 30+ skills, 93 processes

===============================================================================
TABLE OF CONTENTS
===============================================================================

  PART A: SYSTEM-LEVEL FLAWS (cross-cutting issues)
    A1. Command Invocation Architecture
    A2. Agent Utilization Imbalance
    A3. Process Coverage Gaps in Autonomous Loops
    A4. Skill Duplication & Missing Reuse
    A5. State Propagation Across All 20 Commands

  PART B: AUTONOMOUS LOOP IMPROVEMENTS (Big Three)
    B1.  Triage Gate (new pre-planning classifier)
    B2.  Planning Phase Backtrack
    B3.  Fast Path for Trivial Work
    B4.  Per-Task Parallelism
    B5.  Shared Knowledge Store
    B6.  Weighted Compliance Scoring
    B7.  Thrashing Detection
    B8.  Bidirectional Escalation
    B9.  Human Checkpoint Gates
    B10. Runtime Audit Mode
    B11. Normalized Taxonomy
    B12. Intra-Task Stage Regression

  PART C: PHASE & DOMAIN COMMAND IMPROVEMENTS
    C1. Phase Command Integration with Big Three
    C2. Domain Guide Activation from Autonomous Loops
    C3. Workflow Command State Synchronization

  PART D: AGENT OPTIMIZATION
    D1. Agent Consolidation Opportunities
    D2. Agent Capability Gaps
    D3. Agent Routing Improvements

  PART E: PROCESS OPTIMIZATION
    E1. Process Injection Coverage Analysis
    E2. Process Enforcement Model
    E3. Process Deduplication

  PART F: FULL OPTIMIZED ARCHITECTURE
    F1. Complete System Flow (ASCII)
    F2. Complete Constraint Registry
    F3. Implementation Roadmap


===============================================================================
PART A: SYSTEM-LEVEL FLAWS
===============================================================================

-----------------------------------------------------------------------
A1. COMMAND INVOCATION ARCHITECTURE — WHO CAN CALL WHAT
-----------------------------------------------------------------------

PROBLEM: The document states the 3 autonomous loops are "primary commands"
and "all other commands can be called by the 3 primary commands." But
the current architecture has no formal dispatch mechanism for this.

The Big Three only know about each other for escalation. They don't
have defined trigger points for invoking phase commands (/new-project,
/sprint-ceremony, etc.) or domain guides (/security, /qa, etc.).

CURRENT STATE (disconnected):

```
    ┌─────────────────────────────────────────────────────────────┐
    │             AUTONOMOUS LOOPS (The Big Three)                │
    │                                                             │
    │  /auto-orchestrate    /auto-audit     /auto-debug           │
    │        │                   │               │                │
    │        └───────────────────┼───────────────┘                │
    │          (escalation only) │                                │
    └────────────────────────────┼────────────────────────────────┘
                                 │
                          NO FORMAL PATHS
                                 │
    ┌────────────────────────────┼────────────────────────────────┐
    │          PHASE COMMANDS    │    (isolated)                  │
    │                            │                                │
    │  /new-project  /gate-review  /sprint-ceremony  /active-dev  │
    │  /release-prep  /post-launch                                │
    └────────────────────────────┼────────────────────────────────┘
                                 │
    ┌────────────────────────────┼────────────────────────────────┐
    │          DOMAIN GUIDES     │    (isolated)                  │
    │                            │                                │
    │  /security  /qa  /infra  /data-ml-ops  /risk  /org-ops      │
    └────────────────────────────┼────────────────────────────────┘
                                 │
    ┌────────────────────────────┼────────────────────────────────┐
    │          WORKFLOW/UTILITY  │    (isolated)                  │
    │                            │                                │
    │  /workflow  /workflow-start  /workflow-next  /workflow-end   │
    │  /workflow-dash  /workflow-focus  /workflow-plan             │
    │  /assign-agent  /process-lookup                             │
    └─────────────────────────────────────────────────────────────┘
```

IMPROVED STATE (formal dispatch):

```
    ┌─────────────────────────────────────────────────────────────┐
    │             AUTONOMOUS LOOPS (The Big Three)                │
    │                                                             │
    │  /auto-orchestrate    /auto-audit     /auto-debug           │
    │        │                   │               │                │
    │        ├── escalation ─────┼───────────────┤                │
    │        │                   │               │                │
    │   ┌────┴───────────────────┴───────────────┴────┐           │
    │   │         COMMAND DISPATCHER (new)             │           │
    │   │                                              │           │
    │   │  Trigger rules:                              │           │
    │   │   Stage 0 research  ──► /security (if P-038  │           │
    │   │                         flags threats)       │           │
    │   │   Stage 3 impl      ──► /qa (test strategy)  │           │
    │   │   Stage 5 validation──► /infra (if deploy    │           │
    │   │                         issues found)        │           │
    │   │   Pre-P1            ──► /new-project (if no  │           │
    │   │                         handoff receipt)     │           │
    │   │   Post-Stage 6      ──► /release-prep (if    │           │
    │   │                         release flag set)    │           │
    │   │   Post-release      ──► /post-launch         │           │
    │   │   Any stage         ──► /risk (if RAID log   │           │
    │   │                         has CRITICAL items)  │           │
    │   │   Sprint boundary   ──► /sprint-ceremony     │           │
    │   │                                              │           │
    │   │  Utility hooks (always available):            │           │
    │   │   /assign-agent  — agent routing decisions    │           │
    │   │   /process-lookup — find applicable process   │           │
    │   │   /workflow-dash  — status at any checkpoint  │           │
    │   └──────────────────────────────────────────────┘           │
    └─────────────────────────────────────────────────────────────┘
              │                │                │
              ▼                ▼                ▼
    PHASE COMMANDS      DOMAIN GUIDES    WORKFLOW/UTILITY
    (triggered by       (triggered by    (available as
     lifecycle stage)    process flags)   inline tools)
```

NEW CONSTRAINT:

```
DISPATCH-001: The Big Three may invoke any phase command, domain guide,
              or utility command via the command dispatcher. Invocation
              is trigger-based (not manual). Trigger conditions are
              defined per-command and evaluated at every stage transition.

DISPATCH-002: Domain guides are activated when a process in their range
              is flagged as HIGH or CRITICAL risk during execution.
              e.g., P-038 flagged ──► /security activated for that stage.

DISPATCH-003: Phase commands produce receipts consumed by the Big Three.
              Receipt format: { command, result, artifacts[], next_action }
```


-----------------------------------------------------------------------
A2. AGENT UTILIZATION IMBALANCE
-----------------------------------------------------------------------

PROBLEM: Of 13 agent types, only 8 are used by the Big Three. Five agents
(qa-engineer, security-engineer, sre, platform-engineer, cloud-engineer,
data-engineer, ml-engineer) are confined to phase/domain commands that
are never formally invoked by the autonomous loops.

This means autonomous execution has NO inline access to QA strategy,
security review, SRE readiness, platform validation, or data pipeline
expertise — even though processes P-032 to P-057 require them.

CURRENT AGENT UTILIZATION:

```
AGENTS USED BY BIG THREE          AGENTS NEVER USED BY BIG THREE
(8 of 13)                         (5 of 13 — stranded)

┌─────────────────────────┐       ┌──────────────────────────────┐
│ orchestrator        [O] │       │ qa-engineer             [QA] │
│ researcher          [R] │       │ security-engineer       [SE] │
│ product-manager     [PM]│       │ sre                     [SR] │
│ tech-program-mgr    [TP]│       │ platform-engineer       [PL] │
│ engineering-manager [EM]│       │ cloud-engineer          [CL] │
│ software-engineer   [SW]│       │ data-engineer           [DA] │
│ technical-writer    [TW]│       │ ml-engineer             [ML] │
│ debugger            [DB]│       │                              │
│ auditor             [AU]│       │ These agents have expertise  │
│ staff-princ-eng     [SP]│       │ needed by stages 3-5 but     │
│                         │       │ are never spawned.           │
└─────────────────────────┘       └──────────────────────────────┘

Process coverage gap:

  P-032 to P-037 (QA)       ──► qa-engineer needed but not available
  P-038 to P-043 (Security) ──► security-engineer needed but not available
  P-044 to P-048 (Infra)    ──► platform-engineer, sre needed
  P-049 to P-053 (Data/ML)  ──► data-engineer, ml-engineer needed
  P-054 to P-057 (SRE Ops)  ──► sre needed
```

IMPROVEMENT: Conditional agent activation in execution stages.

```
┌──────────────────────────────────────────────────────────────────────┐
│                  CONDITIONAL AGENT ACTIVATION                        │
│                                                                      │
│  Stage 2 (Specification):                                            │
│    IF spec includes API contracts  ──► activate qa-engineer          │
│    IF spec includes auth/crypto    ──► activate security-engineer    │
│    IF spec includes infra/deploy   ──► activate platform-engineer    │
│    IF spec includes data pipelines ──► activate data-engineer        │
│                                                                      │
│  Stage 3 (Implementation):                                           │
│    IF security processes flagged   ──► security-engineer reviews     │
│    IF data schema changes          ──► data-engineer reviews         │
│                                                                      │
│  Stage 5 (Validation):                                               │
│    IF deployment validation needed ──► sre participates              │
│    IF ML model involved            ──► ml-engineer validates         │
│                                                                      │
│  Stage 6 (Documentation):                                            │
│    IF runbook needed               ──► sre co-authors                │
│    IF API docs needed              ──► qa-engineer reviews           │
│                                                                      │
│  Activation is optional — agents only spawn when their domain        │
│  processes are triggered. No overhead for tasks that don't need them.│
└──────────────────────────────────────────────────────────────────────┘
```

NEW CONSTRAINT:

```
AGENT-ACTIVATE-001: Orchestrator evaluates domain-activation rules at
                    each stage transition. If a domain agent's trigger
                    condition is met, that agent is spawned for the
                    current stage only. The agent produces a review
                    artifact and exits.

AGENT-ACTIVATE-002: Domain agents activated conditionally do NOT
                    persist across stages. They are single-stage
                    participants, not permanent pipeline members.
```


-----------------------------------------------------------------------
A3. PROCESS COVERAGE GAPS IN AUTONOMOUS LOOPS
-----------------------------------------------------------------------

PROBLEM: The system has 93 processes (P-001 to P-093), but the Big Three
only inject ~18 of them. 75 processes exist only in phase/domain commands
that the Big Three never invoke.

PROCESS COVERAGE ANALYSIS:

```
                    ┌─────────────────────────────────┐
                    │    93 TOTAL PROCESSES            │
                    │                                  │
                    │    ████████████████████░░░░░░░░  │
                    │    ▲                  ▲          │
                    │    │                  │          │
                    │  18 covered        75 orphaned   │
                    │  by Big Three     (unreachable   │
                    │                    autonomously) │
                    └─────────────────────────────────┘

By category:

  P-001 to P-006  Intent & Strategy       ░░░███  (3/6 covered)
  P-007 to P-014  Scope & Deliverables    ░░░████ (4/8 covered)
  P-015 to P-021  Dependencies            ░░█████ (2/7 covered)
  P-022 to P-031  Sprint Delivery         ░░░████ (2/10 covered)
  P-032 to P-037  QA & Testing            ░░░░░░░ (3/6 partial)
  P-038 to P-043  Security                ░██████ (1/6 covered)
  P-044 to P-048  Infrastructure          ░░░░░░░ (0/5 covered)
  P-049 to P-053  Data & ML               ░░░░░░░ (0/5 covered)
  P-054 to P-057  SRE Operations          ░░░░░░░ (0/4 covered)
  P-058 to P-061  Documentation           ░░░████ (3/4 covered)
  P-062 to P-069  7-Layer Org Audit       ░███████ (1/8 covered)
  P-070 to P-073  Post-Delivery Retro     ░░░░░░░ (0/4 covered)
  P-074 to P-077  Risk & Change           ░░░░░░░ (0/4 covered)
  P-078 to P-081  Communication           ░░░░░░░ (0/4 covered)
  P-082 to P-084  Capacity                ░░░░░░░ (0/3 covered)
  P-085 to P-089  Technical Excellence    ░░░░░░░ (0/5 covered)
  P-090 to P-093  Onboarding              ░░░░░░░ (0/4 covered)

  ░ = not covered     █ = covered by Big Three
```

IMPROVEMENT: Process delegation via command dispatcher (see A1).
When the Big Three encounter a process outside their range, they
invoke the appropriate phase/domain command to handle it.

```
PROCESS-DELEGATE-001: If a stage requires a process the autonomous
                      loop doesn't natively inject, the loop invokes
                      the owning command via the command dispatcher
                      and incorporates the result.

PROCESS-SCOPE-001:   Not all 93 processes apply to every task. The
                      triage gate (B1) determines which process
                      categories are relevant based on task scope.
                      TRIVIAL: P-001, P-007, P-033, P-034 only
                      MEDIUM:  + P-008-010, P-035-037, P-058
                      COMPLEX: full applicable set
```


-----------------------------------------------------------------------
A4. SKILL DUPLICATION & MISSING REUSE
-----------------------------------------------------------------------

PROBLEM: Several skills serve overlapping purposes across pipelines
but aren't shared. Meanwhile, some powerful skills are confined to
a single command when they'd benefit others.

```
DUPLICATION:
  docker-validator  ──► used by auto-debug AND auto-audit AND auto-orchestrate
                        (good — already shared)

  codebase-stats    ──► used by auto-audit (Phase A) AND auto-orchestrate (S4.5)
                        (good — already shared)

  spec-compliance   ──► used ONLY by auto-audit
                        SHOULD ALSO be used by auto-orchestrate Stage 5
                        (validator doesn't check spec compliance, only code quality)

MISSING REUSE:
  refactor-analyzer    ──► only used manually by software-engineer
                           SHOULD be invoked at Stage 4.5 alongside codebase-stats

  dependency-analyzer  ──► only used by staff-principal-engineer
                           SHOULD be invoked at P3 (dependency mapping)

  error-standardizer   ──► only used manually
                           SHOULD be invoked at Stage 3 (implementation)

  cicd-workflow        ──► only used by platform-engineer
                           SHOULD be invoked at Stage 5 if CI/CD is involved

UNDERUSED:
  production-code-workflow  ──► Stage 3 patterns, but not enforced
  dev-workflow              ──► commit conventions, but not enforced
```

IMPROVEMENT:

```
SKILL-REUSE-001: spec-compliance skill is added to Stage 5 validation
                 alongside validator. Auto-orchestrate validates BOTH
                 code quality AND spec compliance before passing.

SKILL-REUSE-002: refactor-analyzer is added to Stage 4.5 pipeline.
                 Runs alongside codebase-stats. Output feeds into
                 Stage 5 validation as a quality signal.

SKILL-REUSE-003: dependency-analyzer is added to P3 (dependency map)
                 stage of auto-orchestrate planning phase.

SKILL-REUSE-004: production-code-workflow and dev-workflow are made
                 MANDATORY reads for software-engineer at Stage 3.
                 Currently advisory; should be enforced.
```


-----------------------------------------------------------------------
A5. STATE PROPAGATION ACROSS ALL 20 COMMANDS
-----------------------------------------------------------------------

PROBLEM: The document mentions .pipeline-state/ for cross-pipeline
knowledge transfer, but only for the Big Three. The phase commands,
domain guides, and workflow commands have no defined state interface.

CURRENT STATE ARCHITECTURE:

```
.orchestrate/<session>/     ──► auto-orchestrate only
.audit/<session>/           ──► auto-audit only
.debug/<session>/           ──► auto-debug only
.gate-state.json            ──► gate-review only
handoff-receipt.json        ──► new-project ──► auto-orchestrate

No state for:
  /sprint-ceremony   (produces nothing persistent)
  /active-dev        (produces nothing persistent)
  /release-prep      (produces nothing persistent)
  /post-launch       (produces nothing persistent)
  /security          (produces nothing persistent)
  /qa                (produces nothing persistent)
  /infra             (produces nothing persistent)
  /data-ml-ops       (produces nothing persistent)
  /risk              (produces nothing persistent)
  /org-ops           (produces nothing persistent)
  /workflow-*        (separate state, not integrated)
```

IMPROVED STATE ARCHITECTURE:

```
.pipeline-state/                           <── Shared root
├── knowledge/                             <── Cross-pipeline intelligence
│   ├── fix-registry.jsonl
│   ├── codebase-analysis.jsonl
│   ├── research-cache/
│   └── dependency-map.json
│
├── sessions/                              <── All pipeline sessions
│   ├── <session-id>.json
│   └── ...
│
├── escalation/                            <── Handoff documents
│   └── <source>-to-<target>.json
│
├── command-receipts/                      <── NEW: phase/domain outputs
│   ├── new-project-<id>.json             <── Replaces handoff-receipt.json
│   ├── gate-review-<id>.json             <── Replaces .gate-state.json
│   ├── sprint-ceremony-<id>.json
│   ├── release-prep-<id>.json
│   ├── post-launch-<id>.json
│   ├── security-review-<id>.json         <── NEW: domain guide outputs
│   ├── qa-review-<id>.json
│   ├── infra-review-<id>.json
│   ├── risk-assessment-<id>.json
│   └── ...
│
├── process-log/                           <── NEW: process execution history
│   ├── P-001.jsonl                        <── When/where/result of each process
│   ├── P-002.jsonl
│   └── ...P-093.jsonl
│
└── workflow/                              <── NEW: workflow state integration
    ├── active-session.json
    ├── task-focus.json
    └── dashboard-cache.json

Every command writes a receipt. Every receipt is readable by any other
command. The Big Three consume receipts to make informed decisions.
```

NEW CONSTRAINT:

```
STATE-001: Every command invocation writes a receipt to
           .pipeline-state/command-receipts/. Receipt includes:
           command, timestamp, inputs, outputs, artifacts[],
           processes_executed[], next_recommended_action.

STATE-002: The Big Three read all relevant receipts at boot and
           at each stage transition. Receipts older than the
           current session are treated as context, not directives.

STATE-003: Process execution is logged to .pipeline-state/process-log/
           with: process_id, command_source, timestamp, result,
           artifacts_produced[]. This enables process coverage tracking.
```


===============================================================================
PART B: AUTONOMOUS LOOP IMPROVEMENTS (Big Three)
===============================================================================

These are the 12 improvements from the previous analysis, now updated
to account for the full system context. Summarized here; full details
in the earlier document.

-----------------------------------------------------------------------
B1. TRIAGE GATE
-----------------------------------------------------------------------

```
USER INPUT
    │
    ▼
┌─────────────────────────┐
│  TRIAGE GATE            │
│                         │
│  Classify:              │
│  ├─ T-shirt size        │
│  ├─ Files touched est.  │
│  ├─ Risk score          │
│  ├─ Cross-team impact   │
│  ├─ Domain flags:       │  <── NEW: determines which domain
│  │   security? infra?   │      guides and agents to activate
│  │   data? ml? qa?      │
│  └─ Process scope       │  <── NEW: which of 93 processes apply
└────────┬────────────────┘
         │
    ┌────┴─────────┬──────────────────┐
    ▼              ▼                  ▼
 TRIVIAL        MEDIUM            COMPLEX
    │              │                  │
  Skip P1-P4    P1 + P2 only      Full P1-P4
  S0,S3,S5      S0-S3,S5,S6      S0-S6 (full)
  3 processes   ~12 processes     ~30+ processes
  0 domain      1-2 domain        all applicable
   agents        agents            domain agents
```


-----------------------------------------------------------------------
B2. PLANNING PHASE BACKTRACK
-----------------------------------------------------------------------

```
P1 ──► P2 ──► P3 ──► P4
              │       │
              │  ┌────┘
              │  │ (capacity or dep conflict)
              ▼  ▼
         Revise P2 (max 2 loops)
```

Updated: P3 now also runs dependency-analyzer skill (A4 improvement).


-----------------------------------------------------------------------
B3. FAST PATH FOR TRIVIAL WORK
-----------------------------------------------------------------------

```
/auto-orchestrate
    │
    ├── COMPLEX/MEDIUM ──► orchestrator ──► agents
    │
    └── TRIVIAL ──► Direct: researcher ──► SWE ──► validator
                    (no orchestrator overhead)
```


-----------------------------------------------------------------------
B4. PER-TASK PARALLELISM
-----------------------------------------------------------------------

```
Independent tasks run concurrently (max 3):

  Task A: [S0]──[S1]──[S2]──[S3]──[S5]──[S6]
  Task B: [S0]──[S1]──[S2]──[S3]──[S5]──[S6]   (parallel)
  Task C:              [S0]──[S1]──[S2]──[S3]──[S5]──[S6]  (queued)

Dependency types: NONE, READ-AFTER-WRITE, WRITE-AFTER-WRITE, API-CONTRACT
```


-----------------------------------------------------------------------
B5. SHARED KNOWLEDGE STORE
-----------------------------------------------------------------------

Now expanded to cover ALL 20 commands, not just Big Three (see A5).


-----------------------------------------------------------------------
B6. WEIGHTED COMPLIANCE SCORING (auto-audit)
-----------------------------------------------------------------------

```
Severity tiers: CRITICAL (10x) > HIGH (5x) > MEDIUM (2x) > LOW (1x)
CRITICAL fail = overall FAIL regardless of score
HIGH fail = max verdict NEEDS_WORK
```

Updated: spec-compliance skill now runs at Stage 5 too (A4 improvement).


-----------------------------------------------------------------------
B7. THRASHING DETECTION
-----------------------------------------------------------------------

```
4 signals: Stall + Thrash + Diminishing Returns + Cost Ceiling
1 signal  ──► pause + notify
2 signals ──► auto-terminate
```


-----------------------------------------------------------------------
B8. BIDIRECTIONAL ESCALATION
-----------------------------------------------------------------------

```
auto-orchestrate ◄──► auto-audit ◄──► auto-debug
                          │
                          ├──► /security (domain escalation)    <── NEW
                          ├──► /infra (deployment issues)       <── NEW
                          └──► /risk (CRITICAL RAID items)      <── NEW

Max 2 cross-pipeline hops, then ──► user
Domain escalations don't count toward the 2-hop limit.
```


-----------------------------------------------------------------------
B9. HUMAN CHECKPOINT GATES
-----------------------------------------------------------------------

```
Configurable per stage. Triage-linked defaults:
  TRIVIAL  ──► no human gates
  MEDIUM   ──► spec-review only
  COMPLEX  ──► spec-review + validation-review
```


-----------------------------------------------------------------------
B10. RUNTIME AUDIT MODE (auto-audit)
-----------------------------------------------------------------------

```
Phase 4 (new): Runtime verification
  CAN: run tests, hit endpoints, start in test mode
  CANNOT: modify source, modify config, write prod data
```


-----------------------------------------------------------------------
B11. NORMALIZED TAXONOMY
-----------------------------------------------------------------------

```
3 types:
  META-CONTROLLER (3): auto-orchestrate, auto-audit, auto-debug
  AGENT (13):          orchestrator, researcher, product-manager, TPM, EM,
                       software-engineer, technical-writer, debugger, auditor,
                       qa-engineer, security-engineer, sre, platform-engineer,
                       cloud-engineer, data-engineer, ml-engineer,
                       staff-principal-engineer
  SKILL (30+):         All skills (deterministic input ──► output tools)
```


-----------------------------------------------------------------------
B12. INTRA-TASK STAGE REGRESSION
-----------------------------------------------------------------------

```
Stage 5 fail ──► regress to Stage 3 (same spawn, max 2x)
3rd fail     ──► escalate to auto-debug
```


===============================================================================
PART C: PHASE & DOMAIN COMMAND IMPROVEMENTS
===============================================================================

-----------------------------------------------------------------------
C1. PHASE COMMAND INTEGRATION WITH BIG THREE
-----------------------------------------------------------------------

PROBLEM: Phase commands operate independently. /new-project creates a
handoff receipt, but there's no formal trigger for the Big Three to
invoke /sprint-ceremony, /release-prep, or /post-launch.

IMPROVED PHASE COMMAND TRIGGERS:

```
┌──────────────────────────────────────────────────────────────────┐
│             PHASE COMMAND TRIGGER MAP                             │
│                                                                  │
│  Trigger Point          Phase Command         Condition          │
│  ─────────────────────────────────────────────────────────────── │
│                                                                  │
│  Before P1              /new-project           No handoff        │
│  (auto-orchestrate)                            receipt exists    │
│                                                                  │
│  P1/P2/P3/P4 gates     /gate-review            Gate reached      │
│  (auto-orchestrate)                                              │
│                                                                  │
│  After P4 passes        /sprint-ceremony       Sprint boundary   │
│  (auto-orchestrate)     (planning ceremony)    detected          │
│                                                                  │
│  During Stage 3         /active-dev            Multi-sprint      │
│  (auto-orchestrate)     (status sync)          project           │
│                                                                  │
│  After Stage 6          /release-prep          Release flag      │
│  (auto-orchestrate)                            set in scope      │
│                                                                  │
│  After release          /post-launch           Deployment        │
│  (auto-orchestrate)                            confirmed         │
│                                                                  │
│  Sprint boundaries      /sprint-ceremony       Sprint timer      │
│  (auto-orchestrate)     (standup/retro)        triggers          │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

PHASE COMMAND LIFECYCLE:

```
/new-project
    │
    ├──► handoff-receipt ──► /auto-orchestrate
    │                             │
    │                    ┌────────┴────────────────────┐
    │                    │  PLANNING (P1-P4)           │
    │                    │    /gate-review at each gate│
    │                    │    /sprint-ceremony after P4│
    │                    └────────┬────────────────────┘
    │                             │
    │                    ┌────────┴────────────────────┐
    │                    │  EXECUTION (S0-S6)          │
    │                    │    /active-dev (status sync)│
    │                    │    /security (if flagged)   │
    │                    │    /qa (test strategy)      │
    │                    │    /risk (RAID items)       │
    │                    └────────┬────────────────────┘
    │                             │
    │                    ┌────────┴────────────────────┐
    │                    │  RELEASE                    │
    │                    │    /release-prep             │
    │                    └────────┬────────────────────┘
    │                             │
    │                    ┌────────┴────────────────────┐
    │                    │  OPERATIONS                 │
    │                    │    /post-launch              │
    │                    │    /sprint-ceremony (retro)  │
    │                    └────────────────────────────-─┘
    │
    └──► /auto-audit (compliance check) ──► /auto-debug (if needed)
```


-----------------------------------------------------------------------
C2. DOMAIN GUIDE ACTIVATION FROM AUTONOMOUS LOOPS
-----------------------------------------------------------------------

```
┌──────────────────────────────────────────────────────────────────┐
│             DOMAIN GUIDE ACTIVATION MAP                           │
│                                                                  │
│  Domain Guide    Trigger Process    Activation Stage              │
│  ─────────────────────────────────────────────────────────────── │
│                                                                  │
│  /security       P-038 (Threat      Stage 0 (research) or       │
│                  Modeling) flagged   Stage 2 (spec) or           │
│                  as applicable       Stage 3 (implementation)    │
│                                                                  │
│  /qa             P-032 (Test Arch)   Stage 2 (spec) or           │
│                  or P-035 (Perf      Stage 4 (tests) or          │
│                  Testing) flagged    Stage 5 (validation)        │
│                                                                  │
│  /infra          P-044 (Golden       Stage 3 (if infra changes)  │
│                  Path) or P-048      or Stage 5 (deploy          │
│                  (Prod Release)      validation)                 │
│                                                                  │
│  /data-ml-ops    P-049 (Data         Stage 2 (if data pipeline)  │
│                  Pipeline QA) or     or Stage 3 (implementation) │
│                  P-051 (ML           or Stage 5 (validation)     │
│                  Experiment)                                      │
│                                                                  │
│  /risk           P-074 (RAID Log)    Any stage (if CRITICAL      │
│                  has CRITICAL items   risk identified)            │
│                                                                  │
│  /org-ops        P-062 (Tech Debt    Stage 4.5 (code stats)     │
│                  Audit) threshold     or post-completion          │
│                  exceeded                                         │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

DOMAIN GUIDE OUTPUT FORMAT:

```
{
  "command": "/security",
  "trigger": "P-038",
  "stage": "Stage 2",
  "findings": [...],
  "severity": "HIGH",
  "recommendations": [...],
  "blocking": true|false,
  "processes_executed": ["P-038", "P-039", "P-040"],
  "artifacts": ["threat-model.md", "security-review.json"]
}
```


-----------------------------------------------------------------------
C3. WORKFLOW COMMAND STATE SYNCHRONIZATION
-----------------------------------------------------------------------

PROBLEM: /workflow-* commands maintain separate state from the Big Three.
A user running /workflow-dash sees different data than auto-orchestrate's
internal task board.

IMPROVEMENT:

```
┌──────────────────────────────────────────────────────────────────┐
│         UNIFIED WORKFLOW STATE                                    │
│                                                                  │
│  .pipeline-state/workflow/                                        │
│  ├── active-session.json      <── shared with Big Three          │
│  ├── task-board.json          <── single source of truth         │
│  ├── focus-stack.json         <── /workflow-focus reads/writes    │
│  └── dashboard-cache.json     <── /workflow-dash reads            │
│                                                                  │
│  Sync rules:                                                     │
│   - auto-orchestrate WRITES task-board.json at each iteration    │
│   - /workflow-dash READS task-board.json (never writes)          │
│   - /workflow-next READS task-board.json + dependency graph       │
│   - /workflow-focus READS/WRITES focus-stack.json                 │
│   - /workflow-start creates active-session.json                  │
│   - /workflow-end archives active-session.json                   │
│                                                                  │
│  If auto-orchestrate is running:                                 │
│   - /workflow-* commands are READ-ONLY (cannot modify tasks)     │
│   - /workflow-dash shows live pipeline progress                  │
│   - /workflow-focus shows current auto-orchestrate focus          │
│                                                                  │
│  If auto-orchestrate is NOT running:                             │
│   - /workflow-* commands have full read/write access             │
│   - /workflow-next suggests tasks from last checkpoint            │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```


===============================================================================
PART D: AGENT OPTIMIZATION
===============================================================================

-----------------------------------------------------------------------
D1. AGENT CONSOLIDATION OPPORTUNITIES
-----------------------------------------------------------------------

```
┌──────────────────────────────────────────────────────────────────┐
│  CURRENT: 13 agents (+ 5 domain agents = 18 total)              │
│                                                                  │
│  CONSOLIDATION CANDIDATES:                                       │
│                                                                  │
│  cloud-engineer + platform-engineer ──► infra-engineer           │
│    Rationale: Cloud and platform are converging domains.         │
│    Both handle P-044 to P-048. Merge into single agent with     │
│    cloud + platform capabilities.                                │
│    Savings: 1 agent type, simpler routing.                       │
│                                                                  │
│  data-engineer + ml-engineer ──► data-ml-engineer                │
│    Rationale: In practice, data pipeline and ML ops are          │
│    tightly coupled. Both handle P-049 to P-053.                  │
│    Savings: 1 agent type, but ONLY if tasks don't need both     │
│    simultaneously. If they do, keep separate.                    │
│                                                                  │
│  NOT consolidation candidates:                                   │
│   - qa-engineer / security-engineer: distinct domains            │
│   - sre / platform-engineer: ops vs build, different phases     │
│   - product-manager / engineering-manager: strategy vs execution │
│                                                                  │
│  RECOMMENDED: Merge cloud+platform. Keep data+ml separate.       │
│  New count: 12 agent types (from 13, or 17 from 18)             │
└──────────────────────────────────────────────────────────────────┘
```


-----------------------------------------------------------------------
D2. AGENT CAPABILITY GAPS
-----------------------------------------------------------------------

```
┌───────────────────┬────────────────────────────────────────────────┐
│ Gap               │ Recommendation                                 │
├───────────────────┼────────────────────────────────────────────────┤
│ No dedicated      │ Add performance-review capability to           │
│ performance agent │ qa-engineer. Not a new agent — extend          │
│                   │ existing qa-engineer with P-035.               │
├───────────────────┼────────────────────────────────────────────────┤
│ No accessibility  │ Add accessibility-check skill (not agent).     │
│ specialist        │ Invoked by qa-engineer at Stage 5.             │
├───────────────────┼────────────────────────────────────────────────┤
│ No cost/billing   │ Add cost-estimator skill. Invoked by           │
│ awareness         │ platform-engineer at /release-prep.            │
├───────────────────┼────────────────────────────────────────────────┤
│ Debugger can't    │ FIXED by B8 (bidirectional escalation).        │
│ handle arch.      │ Debugger escalates to auto-orchestrate.        │
│ issues            │                                                │
├───────────────────┼────────────────────────────────────────────────┤
│ No observability  │ Add observability-setup skill. Invoked by      │
│ setup             │ sre at /release-prep or /post-launch.          │
└───────────────────┴────────────────────────────────────────────────┘
```


-----------------------------------------------------------------------
D3. AGENT ROUTING IMPROVEMENTS
-----------------------------------------------------------------------

/assign-agent currently uses a decision tree. Improve with a
scoring model:

```
┌──────────────────────────────────────────────────────────────────┐
│         AGENT ROUTING SCORE MODEL                                │
│                                                                  │
│  For each candidate agent, compute:                              │
│                                                                  │
│  score = (domain_match × 3)                                      │
│        + (process_coverage × 2)                                  │
│        + (skill_availability × 1)                                │
│        - (current_load × 1)                                      │
│                                                                  │
│  domain_match:     How well agent's domain matches the task      │
│  process_coverage: How many required processes agent can execute  │
│  skill_availability: How many needed skills agent has access to   │
│  current_load:     How many active tasks agent is handling        │
│                                                                  │
│  Highest score wins. Ties broken by domain_match.                │
│                                                                  │
│  Example:                                                        │
│    Task: "Fix authentication token validation"                   │
│                                                                  │
│    software-engineer:  (2×3) + (2×2) + (3×1) - (1×1) = 12       │
│    security-engineer:  (3×3) + (3×2) + (2×1) - (0×1) = 17  ◄── │
│    qa-engineer:        (1×3) + (1×2) + (1×1) - (0×1) =  6       │
│                                                                  │
│    Winner: security-engineer (domain expertise matches best)     │
└──────────────────────────────────────────────────────────────────┘
```


===============================================================================
PART E: PROCESS OPTIMIZATION
===============================================================================

-----------------------------------------------------------------------
E1. PROCESS INJECTION COVERAGE BY COMMAND
-----------------------------------------------------------------------

```
PROCESS RANGES vs COMMANDS THAT EXECUTE THEM:

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
                          │          │           │          │          │
Legend:                   │ Phase/   │ Phase/    │Autonomous│Autonomous│
                          │ Domain   │ Domain    │Loop      │Loop      │
                          │(direct)  │(direct)   │(direct)  │(direct)  │

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
                          │          │           │          │          │
  ◄── = accessible via command dispatcher from Big Three
```


-----------------------------------------------------------------------
E2. PROCESS ENFORCEMENT MODEL
-----------------------------------------------------------------------

```
┌──────────────────────────────────────────────────────────────────┐
│         THREE-TIER PROCESS ENFORCEMENT                           │
│                                                                  │
│  GATE (blocking):                                                │
│    Process MUST pass before pipeline advances.                   │
│    Failure = pipeline stops + notification.                      │
│    Examples: P-034 (Code Review) at Stage 5                      │
│              P-037 (Automated Testing) at Stage 5                │
│              P-058 (Technical Docs) at Stage 6                   │
│              P-038 (Security by Design) at Stage 2               │
│                                                                  │
│  ADVISORY (non-blocking, tracked):                               │
│    Process runs and results are recorded, but pipeline           │
│    continues regardless of result. Failures appear in            │
│    final report as tech debt.                                    │
│    Examples: P-035 (Testing) at Stage 4                          │
│              P-040 (Dependency Scanning) at Stage 3              │
│              P-062 (Technical Debt Audit) at Stage 4.5           │
│                                                                  │
│  INFORMATIONAL (non-blocking, not tracked):                      │
│    Process provides context but has no pass/fail state.          │
│    Used for research, planning, and analysis processes.          │
│    Examples: P-001 (Intent Articulation) at Stage 0              │
│              P-016 (Critical Path Analysis) at P3                │
│                                                                  │
│  NEW: Process enforcement level can be UPGRADED by triage:       │
│    TRIVIAL task: all processes ADVISORY or INFORMATIONAL         │
│    MEDIUM task:  security + code review processes are GATE       │
│    COMPLEX task: security + code review + testing are GATE       │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```


-----------------------------------------------------------------------
E3. PROCESS DEDUPLICATION
-----------------------------------------------------------------------

Some process numbers appear to cover overlapping concerns across
different commands. Potential duplicates:

```
┌────────────────┬──────────────────────┬──────────────────────────┐
│ Potential Dup  │ Process A            │ Process B                │
├────────────────┼──────────────────────┼──────────────────────────┤
│ Testing        │ P-033 (Automated     │ P-037 (Contract Testing) │
│                │ Test Framework)      │ in /qa                   │
│                │ in auto-orchestrate  │                          │
│ Resolution: Keep both. P-033 = framework setup, P-037 = API     │
│ contract testing. Different scopes.                              │
├────────────────┼──────────────────────┼──────────────────────────┤
│ Code Review    │ P-034 at Stage 3     │ P-034 at Stage 5         │
│                │ (advisory)           │ (gate)                   │
│ Resolution: Same process, different enforcement. Correct as-is.  │
├────────────────┼──────────────────────┼──────────────────────────┤
│ Security       │ P-038 (AppSec)       │ P-039 (SAST/DAST)       │
│                │ at Stage 0/2         │ in /security only        │
│ Resolution: P-039 should also be injected at Stage 3 or Stage 5.│
│ Currently only available via /security domain guide.             │
├────────────────┼──────────────────────┼──────────────────────────┤
│ Risk           │ P-010 (RAID Log)     │ P-074 (RAID Log)         │
│                │ at Stage 1           │ in /risk                 │
│ Resolution: These are the SAME process invoked at different      │
│ lifecycle points. Should share the same RAID data store.         │
│ Add constraint: RAID-001: Single RAID log, append-only,          │
│ accessible by P-010 and P-074.                                   │
└────────────────┴──────────────────────┴──────────────────────────┘
```


===============================================================================
PART F: FULL OPTIMIZED ARCHITECTURE
===============================================================================

-----------------------------------------------------------------------
F1. COMPLETE SYSTEM FLOW
-----------------------------------------------------------------------

```
USER INPUT
    │
    ▼
╔═══════════════════════════════════════════════════════════════════╗
║  TRIAGE GATE                                                     ║
║                                                                  ║
║  Classify: TRIVIAL / MEDIUM / COMPLEX                            ║
║  Determine: planning depth, stages, agents, processes, domains   ║
╚═══════════╤════════════════╤═════════════════╤═══════════════════╝
            │                │                 │
       TRIVIAL           MEDIUM            COMPLEX
            │                │                 │
            │          ┌─────┴──────┐    ┌─────┴──────────────────┐
            │          │ P1 + P2    │    │ /new-project (if no    │
            │          │ only       │    │  handoff receipt)      │
            │          └─────┬──────┘    │ P1-R ──► P1 ──► Gate  │
            │                │           │ P2-R ──► P2 ◄─► P3    │
            │                │           │ P3 ──► Gate            │
            │                │           │ P4 ──► Gate            │
            │                │           │ /gate-review at each   │
            │                │           │ /sprint-ceremony after │
            │                │           └─────┬──────────────────┘
            │                │                 │
       ┌────┴────────────────┴─────────────────┘
       │
       ▼
╔═══════════════════════════════════════════════════════════════════╗
║  EXECUTION PHASE                                                 ║
║                                                                  ║
║  COMMAND DISPATCHER active — invokes phase/domain commands as    ║
║  needed at each stage transition.                                ║
║                                                                  ║
║  ┌─────────────────────────────────────────────────────────────┐ ║
║  │ Stage 0: Research                                           │ ║
║  │   Agents: researcher                                        │ ║
║  │   IF security scope ──► /security (threat model)            │ ║
║  │   Processes: P-001, P-038                                   │ ║
║  ├─────────────────────────────────────────────────────────────┤ ║
║  │ Stage 1: Task Decomposition                                 │ ║
║  │   Agents: product-manager                                   │ ║
║  │   Computes: task dependency graph (PARALLEL-001)            │ ║
║  │   Processes: P-007, P-008, P-009, P-010                     │ ║
║  ├─────────────────────────────────────────────────────────────┤ ║
║  │ Stage 2: Specification                                      │ ║
║  │   Skills: spec-creator                                      │ ║
║  │   IF security ──► security-engineer reviews                 │ ║
║  │   IF data/ml  ──► data-engineer reviews                     │ ║
║  │   IF QA       ──► /qa (test architecture)                   │ ║
║  │   Processes: P-033, P-038 (gate)                            │ ║
║  │   [HUMAN-GATE: spec-review] (MEDIUM+COMPLEX)               │ ║
║  ├─────────────────────────────────────────────────────────────┤ ║
║  │ Stage 3: Implementation (parallel tasks up to 3)            │ ║
║  │   Agents: software-engineer                                 │ ║
║  │   IF security ──► security-engineer reviews                 │ ║
║  │   IF infra    ──► platform-engineer assists                 │ ║
║  │   Skills: production-code-workflow (enforced), dev-workflow  │ ║
║  │   Processes: P-034, P-036, P-040                            │ ║
║  ├─────────────────────────────────────────────────────────────┤ ║
║  │ Stage 4: Tests (optional for TRIVIAL)                       │ ║
║  │   Skills: test-writer-pytest                                │ ║
║  │   IF QA scope ──► /qa (test strategy)                       │ ║
║  │   Processes: P-035, P-037                                   │ ║
║  ├─────────────────────────────────────────────────────────────┤ ║
║  │ Stage 4.5: Code Stats                                       │ ║
║  │   Skills: codebase-stats + refactor-analyzer (new)          │ ║
║  │   IF tech debt > threshold ──► /org-ops (P-062)             │ ║
║  │   Processes: P-062                                          │ ║
║  ├─────────────────────────────────────────────────────────────┤ ║
║  │ Stage 5: Validation                                         │ ║
║  │   Skills: validator + spec-compliance (new) + docker-valid. │ ║
║  │   IF deploy ──► sre validates                               │ ║
║  │   IF infra  ──► /infra (production release check)           │ ║
║  │   Processes: P-034 (gate), P-037 (gate), P-039 (new)       │ ║
║  │   [HUMAN-GATE: validation-review] (COMPLEX only)            │ ║
║  │   Failure: regress to S3 (max 2x), then ──► /auto-debug    │ ║
║  ├─────────────────────────────────────────────────────────────┤ ║
║  │ Stage 6: Documentation                                      │ ║
║  │   Agents: technical-writer                                  │ ║
║  │   IF API docs ──► qa-engineer reviews                       │ ║
║  │   IF runbook  ──► sre co-authors                            │ ║
║  │   Skills: docs-lookup, docs-write, docs-review              │ ║
║  │   Processes: P-058 (gate), P-059, P-061                     │ ║
║  └─────────────────────────────────────────────────────────────┘ ║
╚══════════════════════════╤════════════════════════════════════════╝
                           │
                           ▼
╔═══════════════════════════════════════════════════════════════════╗
║  POST-EXECUTION                                                  ║
║                                                                  ║
║  /release-prep (if release flag set)                             ║
║    Agents: qa-engineer, sre, platform-engineer                   ║
║    Processes: P-035, P-044, P-045, P-047, P-048, P-059, P-061   ║
║                                                                  ║
║  /post-launch (after deployment)                                 ║
║    Agents: sre, engineering-manager, product-manager             ║
║    Processes: P-054 to P-057, P-070 to P-073                    ║
║                                                                  ║
║  /auto-audit (optional compliance check)                         ║
║    Agents: auditor, orchestrator (remediation)                   ║
║    Processes: all applicable from audit scope                    ║
║                                                                  ║
║  /sprint-ceremony (retrospective)                                ║
║    Agents: engineering-manager, full team                        ║
║    Processes: P-027, P-028, P-029                                ║
║                                                                  ║
╚═══════════════════════════════════════════════════════════════════╝
                           │
                           ▼
╔═══════════════════════════════════════════════════════════════════╗
║  PROGRESS MONITORING (active throughout)                         ║
║                                                                  ║
║  Signals: Stall | Thrash | Diminishing Returns | Cost Ceiling    ║
║  1 signal ──► pause + notify                                     ║
║  2 signals ──► auto-terminate with report                        ║
║                                                                  ║
║  /workflow-dash available as read-only view during execution     ║
║  /risk activated if RAID log has CRITICAL items                  ║
╚═══════════════════════════════════════════════════════════════════╝
                           │
                           ▼
╔═══════════════════════════════════════════════════════════════════╗
║  CROSS-PIPELINE INTEGRATION                                     ║
║                                                                  ║
║  .pipeline-state/                                                ║
║  ├── knowledge/        (shared intelligence)                     ║
║  ├── sessions/         (all session records)                     ║
║  ├── escalation/       (handoff documents)                       ║
║  ├── command-receipts/ (phase/domain outputs)                    ║
║  ├── process-log/      (P-001 to P-093 execution history)       ║
║  └── workflow/         (unified workflow state)                   ║
║                                                                  ║
║  Escalation: orchestrate ◄──► audit ◄──► debug                  ║
║  Domain:     orchestrate ──► /security, /qa, /infra, /risk       ║
║  Max 2 cross-pipeline hops, then ──► user                        ║
║  Domain escalations don't count toward 2-hop limit.              ║
╚═══════════════════════════════════════════════════════════════════╝
```


-----------------------------------------------------------------------
F2. COMPLETE CONSTRAINT REGISTRY (ALL NEW + MODIFIED)
-----------------------------------------------------------------------

```
┌──────────────────────┬────────┬───────────────────────────────────────────┐
│ ID                   │ Status │ Rule                                      │
├──────────────────────┼────────┼───────────────────────────────────────────┤
│                      │        │                                           │
│  SYSTEM-LEVEL (A-series)                                                  │
│                      │        │                                           │
│ DISPATCH-001         │ NEW    │ Big Three invoke phase/domain commands    │
│                      │        │ via command dispatcher at stage triggers   │
│ DISPATCH-002         │ NEW    │ Domain guides activate on process flags   │
│ DISPATCH-003         │ NEW    │ All commands produce receipts             │
│ AGENT-ACTIVATE-001   │ NEW    │ Conditional domain agent activation      │
│ AGENT-ACTIVATE-002   │ NEW    │ Domain agents are single-stage only      │
│ PROCESS-DELEGATE-001 │ NEW    │ Unknown processes delegated via dispatch  │
│ PROCESS-SCOPE-001    │ NEW    │ Triage determines process scope          │
│ SKILL-REUSE-001      │ NEW    │ spec-compliance added to Stage 5         │
│ SKILL-REUSE-002      │ NEW    │ refactor-analyzer added to Stage 4.5     │
│ SKILL-REUSE-003      │ NEW    │ dependency-analyzer added to P3          │
│ SKILL-REUSE-004      │ NEW    │ production-code-workflow enforced at S3   │
│ STATE-001            │ NEW    │ All commands write receipts               │
│ STATE-002            │ NEW    │ Big Three read receipts at boot + stages  │
│ STATE-003            │ NEW    │ Process execution logged to process-log/  │
│ RAID-001             │ NEW    │ Single RAID log shared by P-010 and P-074│
│                      │        │                                           │
│  AUTONOMOUS LOOP (B-series)                                               │
│                      │        │                                           │
│ TRIAGE-001           │ NEW    │ All tasks classified before execution    │
│ BACKTRACK-001        │ NEW    │ P3 can revise P2 (max 2 loops)           │
│ BACKTRACK-002        │ NEW    │ P4 can revise P2 for capacity            │
│ BACKTRACK-003        │ NEW    │ Backtrack events logged append-only      │
│ FAST-001             │ NEW    │ Trivial tasks bypass orchestrator        │
│ PARALLEL-001         │ NEW    │ Dependency graph computed at Stage 1     │
│ PARALLEL-002         │ NEW    │ CHAIN-001 relaxed for independent tasks  │
│ PARALLEL-003         │ NEW    │ Max 3 concurrent tasks                   │
│ SHARED-001           │ NEW    │ All pipelines read shared knowledge      │
│ SHARED-002           │ NEW    │ Escalation handoffs to shared store      │
│ SHARED-003           │ NEW    │ Research cache checked before researcher │
│ SHARED-004           │ NEW    │ Fix-registry append-only, shared         │
│ ESCALATE-001         │ NEW    │ Max 2 cross-pipeline escalations         │
│ ESCALATE-002         │ NEW    │ Every escalation writes handoff doc      │
│ REGRESS-001          │ NEW    │ Intra-task regression S5 ──► S3 only     │
│ REGRESS-002          │ NEW    │ Max 2 regressions per task per spawn     │
│ REGRESS-003          │ NEW    │ Regressions logged in task record        │
│ AUD-RUNTIME-001      │ NEW    │ Runtime verification in sandbox          │
│ AUD-RUNTIME-002      │ NEW    │ Runtime findings tagged separately       │
│ AUTO-003             │ MODIFY │ Intra-task regression allowed S5──►S3    │
│ AUTO-001             │ MODIFY │ Trivial tasks exempt (FAST-001)          │
│ CHAIN-001            │ MODIFY │ Cross-task deps from dependency graph    │
│ AUD-001              │ MODIFY │ May execute tests (not modify code)      │
│                      │        │                                           │
│  WORKFLOW (C-series)                                                      │
│                      │        │                                           │
│ WORKFLOW-SYNC-001    │ NEW    │ task-board.json is single source of truth│
│ WORKFLOW-SYNC-002    │ NEW    │ /workflow-* read-only when Big Three run  │
│                      │        │                                           │
└──────────────────────┴────────┴───────────────────────────────────────────┘

TOTALS:
  New constraints:      37
  Modified constraints:  4
  Total:                41
```


-----------------------------------------------------------------------
F3. IMPLEMENTATION ROADMAP
-----------------------------------------------------------------------

```
╔═══════════════════════════════════════════════════════════════════╗
║  PHASE 1: FOUNDATION (Week 1-2)                                  ║
║  Highest ROI, unblocks everything else                           ║
║                                                                  ║
║  ├── B1.  Triage Gate                                            ║
║  ├── B3.  Fast Path for Trivial Work                             ║
║  ├── B12. Intra-Task Stage Regression                            ║
║  └── A5.  Shared State Architecture (.pipeline-state/)           ║
║                                                                  ║
║  Impact: 40-60% reduction in overhead for small tasks.           ║
║          Foundation for all cross-pipeline features.             ║
╠═══════════════════════════════════════════════════════════════════╣
║  PHASE 2: INTELLIGENCE (Week 3-4)                                ║
║  Make the system smarter                                         ║
║                                                                  ║
║  ├── B5.  Shared Knowledge Store                                 ║
║  ├── B6.  Weighted Compliance Scoring                            ║
║  ├── B7.  Thrashing Detection                                    ║
║  ├── A4.  Skill Reuse (spec-compliance at S5, etc.)              ║
║  └── E2.  Three-Tier Process Enforcement                         ║
║                                                                  ║
║  Impact: Better audit verdicts. Fewer wasted iterations.         ║
║          Skills used where they're most needed.                  ║
╠═══════════════════════════════════════════════════════════════════╣
║  PHASE 3: INTEGRATION (Week 5-6)                                 ║
║  Connect the full system                                         ║
║                                                                  ║
║  ├── A1.  Command Dispatcher                                     ║
║  ├── C1.  Phase Command Integration                              ║
║  ├── C2.  Domain Guide Activation                                ║
║  ├── A2.  Conditional Agent Activation                           ║
║  └── C3.  Workflow State Synchronization                         ║
║                                                                  ║
║  Impact: All 93 processes reachable. All 13 agents usable.       ║
║          Phase/domain commands integrated into autonomous loops. ║
╠═══════════════════════════════════════════════════════════════════╣
║  PHASE 4: ARCHITECTURE (Week 7-8)                                ║
║  Structural improvements                                         ║
║                                                                  ║
║  ├── B2.  Planning Phase Backtrack                               ║
║  ├── B4.  Per-Task Parallelism                                   ║
║  ├── B8.  Bidirectional Escalation                               ║
║  └── D3.  Agent Routing Score Model                              ║
║                                                                  ║
║  Impact: Faster execution. Smarter routing. No dead-end          ║
║          escalations.                                            ║
╠═══════════════════════════════════════════════════════════════════╣
║  PHASE 5: POLISH (Week 9-10)                                     ║
║  Quality of life                                                 ║
║                                                                  ║
║  ├── B9.  Human Checkpoint Gates                                 ║
║  ├── B10. Runtime Audit Mode                                     ║
║  ├── B11. Normalized Taxonomy                                    ║
║  ├── D1.  Agent Consolidation (cloud+platform)                   ║
║  ├── D2.  New Skills (accessibility, cost-estimator, etc.)       ║
║  └── E3.  Process Deduplication (RAID-001, P-039 injection)      ║
║                                                                  ║
║  Impact: Human oversight when needed. Runtime verification.      ║
║          Cleaner taxonomy. Fewer redundant components.           ║
╚═══════════════════════════════════════════════════════════════════╝
```


-----------------------------------------------------------------------
F4. SUMMARY METRICS
-----------------------------------------------------------------------

```
┌─────────────────────────────┬─────────────┬──────────────┐
│ Metric                      │ Before      │ After        │
├─────────────────────────────┼─────────────┼──────────────┤
│ Agents usable by Big Three  │ 8 of 13     │ 13 of 13     │
│ (+ domain agents)           │ (61%)       │ (100%)       │
├─────────────────────────────┼─────────────┼──────────────┤
│ Processes reachable by      │ 18 of 93    │ 93 of 93     │
│ autonomous loops             │ (19%)       │ (100%)       │
├─────────────────────────────┼─────────────┼──────────────┤
│ Cross-pipeline escalation   │ One-way     │ Bidirectional│
│ paths                       │ (3 paths)   │ (6+ paths)   │
├─────────────────────────────┼─────────────┼──────────────┤
│ Commands integrated with    │ 3 of 20     │ 20 of 20     │
│ autonomous loops             │ (15%)       │ (100%)       │
├─────────────────────────────┼─────────────┼──────────────┤
│ Stall detection signals     │ 1           │ 4            │
├─────────────────────────────┼─────────────┼──────────────┤
│ Overhead for trivial tasks  │ Full P1-P4  │ Zero planning│
│                             │ + S0-S6     │ + S0,S3,S5   │
├─────────────────────────────┼─────────────┼──────────────┤
│ Max concurrent tasks        │ 1           │ 3            │
├─────────────────────────────┼─────────────┼──────────────┤
│ Compliance scoring          │ Flat 90%    │ Weighted     │
│                             │ threshold   │ w/ severity  │
├─────────────────────────────┼─────────────┼──────────────┤
│ Shared state across         │ Partial     │ Full         │
│ commands                    │ (3 of 20)   │ (20 of 20)   │
├─────────────────────────────┼─────────────┼──────────────┤
│ New constraints             │ --          │ 37 new +     │
│                             │             │ 4 modified   │
└─────────────────────────────┴─────────────┴──────────────┘
```