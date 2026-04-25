---
name: auto-orchestrate
description: |
  Autonomous orchestration loop. Enhances user input, spawns orchestrator
  repeatedly, loops until all tasks complete. Crash recovery via session checkpoints.
triggers:
  - auto-orchestrate
  - auto orchestrate
  - autonomous orchestration
  - orchestrate until done
  - run to completion
  - continue orchestration
arguments:
  - name: task_description
    type: string
    required: true
    description: The task or objective to orchestrate. Pass "c" to continue the most recent in-progress session. Not required when resuming an existing session.
  - name: session_id
    type: string
    required: false
    description: Resume a specific session by ID (e.g. "auto-orc-2026-01-29-inventory").
  - name: max_iterations
    type: integer
    required: false
    default: 100
    description: Override the maximum number of orchestrator spawns.
  - name: stall_threshold
    type: integer
    required: false
    default: 2
    description: Override the number of consecutive no-progress iterations before failing.
  - name: max_tasks
    type: integer
    required: false
    default: 50
    description: Override maximum total tasks allowed (LIMIT-001). Cap 100.
  - name: scope
    type: string
    required: false
    description: |
      Scope flag: "F"/"f" (Frontend), "B"/"b" (Backend), "S"/"s" (Full stack).
      When set, injects scope-specific audit/implementation specs into the enhanced prompt.
      If omitted, task_description is used as-is.
  - name: resume
    type: boolean
    required: false
    default: false
    description: Explicitly resume the latest in-progress session, ignoring task_description.
  - name: skip_planning
    type: boolean
    required: false
    default: false
    description: Skip P-series planning stages (P1-P4). Use when planning artifacts already exist or for tasks that do not require formal planning.
  - name: fast_path
    type: boolean
    required: false
    default: false
    description: Enable fast-path mode for trivial single-stage tasks. Bypasses full pipeline when the orchestrator determines only one agent is needed. Requires --skip-planning.
  - name: research_depth
    type: string
    required: false
    description: |
      Explicit override for research tier (RESEARCH-DEPTH-001). One of:
      "minimal", "normal", "deep", "exhaustive".
      If omitted, depth is auto-resolved from triage complexity + domain flags
      (see Step 0h-pre). This flag wins over all other precedence sources.
      Invalid values fall back to the triage default and log a warning.
---

# Autonomous Orchestration Loop

## Pre-flight Component Verification

Before spawning Stage 0 (researcher), verify ALL 9 pipeline-critical components exist in manifest:

### Component Taxonomy

Throughout the pipeline system, components are classified as follows:

| Classification | Definition | Examples | Invocation |
|---------------|-----------|----------|------------|
| **Meta-Controller** | Autonomous loop controller that spawns agents but never does work itself. Invoked by user as a slash command. | auto-orchestrate, auto-audit, auto-debug | `/command-name` (user invokes) |
| **Agent** | Autonomous role with its own `.md` definition in `agents/`, model assignment, and tool access. Can spawn subagents. | orchestrator, researcher, software-engineer, product-manager | `Agent(subagent_type: "<name>")` |
| **Skill** | Reusable capability with a `SKILL.md` in `skills/`, invoked inline by an agent or via the Skill tool. Cannot spawn subagents. | spec-creator, validator, codebase-stats, test-writer-pytest | Read and follow `SKILL.md` inline |

**Canonical classification** (authoritative across all pipelines):

| Component | Type | Used In |
|-----------|------|---------|
| orchestrator | agent | auto-orchestrate, auto-audit (remediation) |
| researcher | agent | auto-orchestrate (Stage 0), auto-debug (optional) |
| product-manager | agent | auto-orchestrate (P1-P2, Stage 1) |
| technical-program-manager | agent | auto-orchestrate (P3) |
| engineering-manager | agent | auto-orchestrate (P4) |
| software-engineer | agent | auto-orchestrate (Stage 3) |
| technical-writer | agent | auto-orchestrate (Stage 6) |
| auditor | agent | auto-audit (Phase A) |
| debugger | agent | auto-debug |
| spec-creator | **skill** | auto-orchestrate (Stage 2) |
| validator | **skill** | auto-orchestrate (Stage 5) |
| codebase-stats | **skill** | auto-orchestrate (Stage 4.5) |
| test-writer-pytest | **skill** | auto-orchestrate (Stage 4, optional) |
| docs-lookup | **skill** | auto-orchestrate (Stage 6, via technical-writer) |
| docs-write | **skill** | auto-orchestrate (Stage 6, via technical-writer) |
| docs-review | **skill** | auto-orchestrate (Stage 6, via technical-writer) |
| spec-compliance | **skill** | auto-orchestrate (Stage 5, via validator) |
| refactor-analyzer | **skill** | auto-orchestrate (Stage 4.5, via codebase-stats) |
| dependency-analyzer | **skill** | auto-orchestrate (P3, via technical-program-manager) |
| production-code-workflow | **skill** | auto-orchestrate (Stage 3, via software-engineer) |
| dev-workflow | **skill** | auto-orchestrate (Stage 3, via software-engineer) |

> **TAXONOMY-001**: Three component types exist: **META-CONTROLLER** (3: auto-orchestrate, auto-audit, auto-debug), **AGENT** (17+: orchestrator, researcher, product-manager, etc.), **SKILL** (30+: spec-creator, validator, codebase-stats, etc.). Meta-controllers spawn agents; agents invoke skills; skills produce output. `spec-creator`, `validator`, `spec-compliance`, `refactor-analyzer`, `dependency-analyzer`, `production-code-workflow`, `dev-workflow`, and `codebase-stats` are ALWAYS skills, never agents. They are invoked inline by the orchestrator's subagents. Any document that classifies them as agents is in error — this table is authoritative.

### Pipeline Component Matrix

| Stage | Component Name | Type | Mandatory | Manifest Location |
|-------|---------------|------|-----------|-------------------|
| P1-P2 | product-manager | agent | YES | `agents[]` where `name == "product-manager"` |
| P3 | technical-program-manager | agent | YES | `agents[]` where `name == "technical-program-manager"` |
| P3 | dependency-analyzer | skill | YES | `skills[]` where `name == "dependency-analyzer"` |
| P4 | engineering-manager | agent | YES | `agents[]` where `name == "engineering-manager"` |
| 0 | researcher | agent | YES | `agents[]` where `name == "researcher"` |
| 1 | product-manager | agent | YES | `agents[]` where `name == "product-manager"` |
| 2 | spec-creator | skill | YES | `skills[]` where `name == "spec-creator"` |
| 3 | software-engineer | agent | YES (one of) | `agents[]` where `name == "software-engineer"` |
| 3 | production-code-workflow | skill | YES | `skills[]` where `name == "production-code-workflow"` |
| 3 | dev-workflow | skill | YES | `skills[]` where `name == "dev-workflow"` |
| 3 | library-implementer-python | skill | NO (alternative) | `skills[]` where `name == "library-implementer-python"` |
| 4 | test-writer-pytest | skill | NO (Stage 4 optional) | `skills[]` where `name == "test-writer-pytest"` |
| 4.5 | codebase-stats | skill | YES | `skills[]` where `name == "codebase-stats"` |
| 4.5 | refactor-analyzer | skill | YES | `skills[]` where `name == "refactor-analyzer"` |
| 5 | validator | skill | YES | `skills[]` where `name == "validator"` |
| 5 | spec-compliance | skill | YES | `skills[]` where `name == "spec-compliance"` |
| 6 | technical-writer | agent | YES | `agents[]` where `name == "technical-writer"` |

### Verification Steps

1. Read `~/.claude/manifest.json`
2. Verify orchestrator agent exists at `~/.claude/agents/orchestrator.md`
3. For each component in the matrix:
   a. Check if component exists in the appropriate manifest array (`agents[]` or `skills[]`)
   b. For agents, also verify the `.md` file exists at `~/.claude/agents/<name>.md`
   c. Record result in `manifest_validation` object

4. Classify results:
   - **MANDATORY MISSING**: researcher, product-manager, technical-program-manager, engineering-manager, spec-creator, software-engineer, production-code-workflow, dev-workflow, codebase-stats, refactor-analyzer, validator, spec-compliance, dependency-analyzer, technical-writer
     - Abort with: `[MANIFEST-001] Mandatory {type} "{name}" not found in manifest. Stage {N} will fail. Aborting.`
   - **OPTIONAL MISSING**: library-implementer-python, test-writer-pytest
     - Warn: `[MANIFEST-WARN] Optional {type} "{name}" not found. Stage {N} may use alternatives.`
   - **ALL MANDATORY PRESENT**: proceed

5. Display pre-flight verification summary:
```
Pre-flight Manifest Check:
  ✓ product-manager (Stage P1-P2 + Stage 1, agent)
  ✓ technical-program-manager (Stage P3, agent)
  ✓ dependency-analyzer (Stage P3, skill)
  ✓ engineering-manager (Stage P4, agent)
  ✓ researcher (Stage 0, agent)
  ✓ spec-creator (Stage 2, skill)
  ✓ software-engineer (Stage 3, agent)
  ✓ production-code-workflow (Stage 3, skill)
  ✓ dev-workflow (Stage 3, skill)
  ? library-implementer-python (Stage 3, optional skill)
  ? test-writer-pytest (Stage 4, optional skill)
  ✓ codebase-stats (Stage 4.5, skill)
  ✓ refactor-analyzer (Stage 4.5, skill)
  ✓ validator (Stage 5, skill)
  ✓ spec-compliance (Stage 5, skill)
  ✓ technical-writer (Stage 6, agent)
  Result: 15/15 mandatory present, 2 optional (0 missing)
```

6. Log: `[MANIFEST] Verified {checked_count}/{total_count} pipeline components. Missing: {missing_list or "none"}`

### Checkpoint Schema Addition

Record verification result in checkpoint:
```json
{
  "manifest_validation": {
    "checked_at": "<ISO-8601>",
    "total_checked": 17,
    "mandatory_present": 15,
    "mandatory_missing": [],
    "optional_present": ["library-implementer-python", "test-writer-pytest"],
    "optional_missing": [],
    "warnings": [],
    "components": [
      { "name": "product-manager", "type": "agent", "stage": "P1-P2", "mandatory": true, "found": true },
      { "name": "technical-program-manager", "type": "agent", "stage": "P3", "mandatory": true, "found": true },
      { "name": "dependency-analyzer", "type": "skill", "stage": "P3", "mandatory": true, "found": true },
      { "name": "engineering-manager", "type": "agent", "stage": "P4", "mandatory": true, "found": true },
      { "name": "researcher", "type": "agent", "stage": 0, "mandatory": true, "found": true },
      { "name": "product-manager", "type": "agent", "stage": 1, "mandatory": true, "found": true },
      { "name": "spec-creator", "type": "skill", "stage": 2, "mandatory": true, "found": true },
      { "name": "software-engineer", "type": "agent", "stage": 3, "mandatory": true, "found": true },
      { "name": "production-code-workflow", "type": "skill", "stage": 3, "mandatory": true, "found": true },
      { "name": "dev-workflow", "type": "skill", "stage": 3, "mandatory": true, "found": true },
      { "name": "library-implementer-python", "type": "skill", "stage": 3, "mandatory": false, "found": true },
      { "name": "test-writer-pytest", "type": "skill", "stage": 4, "mandatory": false, "found": true },
      { "name": "codebase-stats", "type": "skill", "stage": 4.5, "mandatory": true, "found": true },
      { "name": "refactor-analyzer", "type": "skill", "stage": 4.5, "mandatory": true, "found": true },
      { "name": "validator", "type": "skill", "stage": 5, "mandatory": true, "found": true },
      { "name": "spec-compliance", "type": "skill", "stage": 5, "mandatory": true, "found": true },
      { "name": "technical-writer", "type": "agent", "stage": 6, "mandatory": true, "found": true }
    ]
  }
}
```

## Session Resume from Handoff

When /auto-orchestrate starts, check for an existing handoff receipt from a prior auto-orchestrate session:

### Fresh Start
If no prior session exists, start normally with the provided task_description.

### Handoff Resume
If starting from a prior session handoff:
1. Look for `.orchestrate/{session_id}/handoff-receipt.json`
2. If found and `status == "pending"`:
   a. Load all 6 project fields from the receipt
   b. Use `task_description` from the receipt as the orchestration objective
   c. Update `status` to `"active"` in the receipt
   d. Log: `[HANDOFF] Resuming from prior session handoff (last phase: {last_phase})`
3. If found but `status != "pending"`: Treat as normal session (may already be in progress)
4. If not found: Treat as fresh start

### Handoff Validation (Enhanced)
If resuming from handoff, perform additional validation after loading:

5. **Validate `source_gate_status`** — If present, check that required gate was passed:
   - If `source_gate_status == "PASSED"`: proceed
   - If `source_gate_status != "PASSED"`: emit `[BRIDGE-BLOCK] Handoff receipt source_gate_status is "{status}", expected "PASSED". Bridge protocol requires gate passage before auto-orchestration.` Abort. Set checkpoint status to `"bridge_blocked"`.
6. **Check `scope_contract_path`** — If present, verify the file exists:
   - If file exists: log `[BRIDGE] Scope contract found at {path}`
   - If file missing: log `[BRIDGE-WARN] Scope contract path "{path}" not found. File may have been moved. Proceeding with task_description from receipt.`
7. **Extract `scope_flag`** — If present, use for scope resolution in Step 0d:
   - Store extracted flag for use in scope resolution
   - If `scope_flag` in receipt conflicts with `--scope` argument: argument takes precedence, log `[HANDOFF-OVERRIDE] --scope argument overrides handoff scope_flag`
8. Log validation result: `[HANDOFF-VALID] Gate: {gate}, Scope: {flag}, Contract: {path}`

### Handoff Receipt Path

`{working_dir}/.orchestrate/{session_id}/handoff-receipt.json`

The session_id follows the format: `auto-orc-{YYYYMMDD}-{project_slug}`

## Core Constraints — IMMUTABLE

| ID | Rule |
|----|------|
| AUTO-001 | **Phase-determined agent gateway** — Auto-orchestrate spawns the agent type appropriate for the active phase. Default phases spawn `orchestrator`. Phase 5v (Validation + Audit) spawns `auditor`. Phase 5e (Debug sub-loop) spawns `debugger`. Phases 5q/5s/5i/5d may spawn `qa-engineer`/`security-engineer`/`infra-engineer`/`data-engineer` directly when the active scope flags their domain. The loop controller never does work itself; it only spawns and observes. If 2 consecutive retries return empty output for any phase spawn, abort with `[AUTO-001]` message. |
| AUTO-002 | **Mandatory stage completion** — Cannot declare `completed` unless `stages_completed` includes 0, 1, 2, 4.5, 5, and 6. Stage 4 (test-writer-pytest) is optional — included only when the product-manager (Stage 1) produces test tasks. If no Stage 4 tasks exist, Stage 4 is considered implicitly complete. |
| AUTO-003 | **Stage monotonicity with validation regression** — `current_pipeline_stage` only increases or holds, EXCEPT: when Stage 5 (Validation) fails AND the validator identifies implementation defects (not spec or architecture issues), the pipeline MAY regress to Stage 3 (Implementation) for targeted fixes. Regression rules: (1) Only Stage 5 → Stage 3 regression is permitted (REGRESS-001); (2) Maximum 2 regression cycles per session — tracked in `validation_regression_count` (REGRESS-002); (3) Each regression creates a new Stage 3 task with `blockedBy` referencing the failed Stage 5 task and `regression: true` flag, logged in the task record (REGRESS-003); (4) After 2 regressions, the pipeline must proceed to termination or escalate to auto-debug; (5) Log `[REGRESS] Stage 5 → 3 regression {N}/2 — <reason>`. The high-water mark `stages_completed` is NOT modified on regression — Stage 3 remains "completed" but new fix tasks are injected. |
| AUTO-004 | **Post-implementation stage gate** — If Stage 3 done but 4.5/5/6 missing for 1+ iterations, set `mandatory_stage_enforcement: true` and inject missing-stage tasks. |
| AUTO-005 | **Checkpoint-before-spawn** — Write checkpoint to disk before every orchestrator spawn. |
| AUTO-006 | **No direct agent routing** — Never tell the orchestrator which agent to use; routing is its decision. |
| AUTO-008 | **Orchestrator delegation mandate** — The orchestrator MUST spawn subagents for ALL stage work. It must NEVER do research, analysis, implementation, testing, or documentation itself. Reading project files to "understand" the codebase is researcher work, not orchestrator work. |
| AUTO-009 | **Fast-path bypass** — When `fast_path: true` AND triage classifies the task as `trivial`, auto-orchestrate bypasses the orchestrator entirely via Step 2a (FAST-001). The loop controller spawns researcher → software-engineer → validator directly. Fast-path tasks still write stage-receipts per stage. Fast-path is NEVER available when scope is `frontend`, `backend`, or `fullstack` (scoped work always requires the full pipeline). See Step 2a for full implementation. |
| FAST-001 | **Fast-path orchestrator bypass** — Trivial tasks with `fast_path: true` bypass the orchestrator gateway (exception to AUTO-001). Auto-orchestrate spawns researcher (Stage 0), software-engineer (Stage 3), and validator (Stage 5) directly. Fast-path auto-disables if: scope flag is set (F/B/S), researcher reveals complexity > trivial, or Stage 5 validation fails — falling back to the full pipeline at current progress. |
| AUTO-007 | **Iteration history immutability** — Only append to `iteration_history`; never modify existing entries. |
| CEILING-001 | **Stage ceiling enforcement** — Calculate `STAGE_CEILING` from `stages_completed` before every spawn (Step 3a). Orchestrator MUST NOT work above STAGE_CEILING. Auto-fix missing `blockedBy` chains. |
| CHAIN-001 | **Mandatory blockedBy chains with independence exceptions** — Every proposed task for Stage N (N > 0) must include `blockedBy` referencing at least one Stage N-1 task. Auto-orchestrate validates and auto-fixes in Step 4.2. **Independence exception (CHAIN-002)**: When the product-manager (Stage 1) marks tasks as `independent: true` (no shared files, no data dependencies), independent task groups MAY progress through stages concurrently. Task A at Stage 3 and Task B at Stage 0 can execute in parallel if they are in different independence groups. Independence groups are declared in Stage 1 output and validated by the orchestrator. Tasks within the same independence group follow strict sequential staging. The orchestrator MUST NOT run two tasks from the same group at different stages simultaneously. |
| PARALLEL-001 | **Dependency graph at Stage 1 (hybrid detection)** — The product-manager (Stage 1) MUST compute and emit a task dependency graph with edges `{from_task, to_task, dependency_type}` where `dependency_type` ∈ {`NONE`, `READ-AFTER-WRITE`, `WRITE-AFTER-WRITE`, `API-CONTRACT`}, plus `independence_groups` (list of `[task_id, ...]` arrays) in `proposed-tasks.json`. Detection is **hybrid**: (a) heuristic — group tasks sharing a common path prefix (depth ≤ 2) of declared `files_touched`; tasks with no/empty `files_touched` default to a single shared group; (b) explicit override — spec/task fields `independence_groups: [[ids],...]`, `shares_state_with: [ids]`, `independent_of: [ids]` ALWAYS supersede the heuristic. Stage 1 auto-eval (Step 4.8b) FAILs and re-spawns product-manager when these fields are missing. |
| PARALLEL-002 | **Cross-group stage relaxation** — For tasks in different independence groups (CHAIN-002), the CHAIN-001 `blockedBy` requirement is relaxed per PARALLEL-001's dependency graph. Tasks in separate groups may execute at different pipeline stages concurrently, provided no `READ-AFTER-WRITE` or `WRITE-AFTER-WRITE` edge exists between them. |
| PARALLEL-003 | **Concurrency cap** — Maximum **5 tasks** may execute concurrently across independence groups by default (configurable up to **7** via `checkpoint.parallel_cap`, range `[1, 7]`). The orchestrator picks tasks FIFO within each group, one task per distinct group per spawn cycle, until the cap is reached. If only one group has unblocked tasks, the orchestrator falls back to a single-task spawn (no parallelism). Per-group stage tracking lives in `checkpoint.independence_group_stages`. |
| PHASE-LOOP-001 | **Internal phase transitions only** — Audit (Phase 5v) and Debug (Phase 5e) are internal sub-loops of auto-orchestrate, not separate commands. When validation fails or compliance falls below threshold, the loop controller transitions to the corresponding internal phase. There is no cross-command escalation; no escalation log is written. |
| PHASE-LOOP-002 | **Internal phase receipt** — Each internal phase (5v, 5e, 5q, 5s, 5i, 5d, 7, 8, 9) MUST write a phase receipt to `.orchestrate/<session>/phase-receipts/phase-{name}-{YYYYMMDD}-{HHMMSS}.json` with: `phase`, `started_at`, `completed_at`, `verdict`, `artifacts`, `next_phase`. Phase receipts replace the deleted dispatch-receipts protocol. |
| PROGRESS-001 | **Always-visible processing** — Output status lines before/after every tool call, spawn, and processing step. Never leave extended silence. See `commands/CONVENTIONS.md` for format. |
| PROGRESS-002 | **In-progress blocks completion** — Tasks with status `in_progress` mean background agents are still working. NEVER evaluate termination, declare completion, or mark stages done while `in_progress > 0`. Display running task count prominently. |
| DISPLAY-001 | **Task board at every iteration** — Show full task board with individual tasks grouped by stage at iteration start (Step 3) and post-iteration (Step 4.3). |
| SCOPE-001 | **Scope specification passthrough** — When scope is not `custom`, pass FULL scope spec (Appendix A/B) VERBATIM through every layer. Never summarize. |
| SCOPE-002 | **Scope template integrity** — A narrow user objective does not reduce the spec — all design principles, steps, and constraints still apply in full. |
| MANIFEST-001 | **Manifest-driven pipeline** — The orchestrator MUST read `~/.claude/manifest.json` at boot and use it as the authoritative registry for agent routing, skill discovery, and capability validation. Auto-orchestrate passes the manifest path in every orchestrator spawn. Agents MUST verify their mandatory skills exist in the manifest before invoking them. |
| PRE-RESEARCH-GATE | **Planning phase prerequisite** — Stage 0 (researcher) MUST NOT begin unless `planning_stages_completed` contains all four values `["P1", "P2", "P3", "P4"]` AND all four entries in `planning_gate_statuses` have value `"PASSED"`. Skip conditions: (1) `--skip-planning` flag is passed, or (2) checkpoint field `planning_skipped` is `true` (set when resuming a session that already has planning artifacts from a prior session). Error codes: `[PLAN-GATE-001]` through `[PLAN-GATE-004]` for each incomplete stage. |
| WORKFLOW-SYNC-001 | **Task board single source of truth** — When auto-orchestrate is running, `.pipeline-state/workflow/task-board.json` is the single source of truth for task state. auto-orchestrate WRITES this file at every iteration (Step 4.8e). `/workflow-dash`, `/workflow-next`, and `/workflow-focus` READ this file. No other command writes to it while auto-orchestrate is active. **Concurrent task states**: When parallel scheduling is active (PARALLEL-002/003), `task-board.json` MAY carry multiple `in_progress` entries simultaneously — one per parallel software-engineer spawn. Each parallel agent updates its own task atomically (last-writer-wins on the `tasks[].status` field per task ID); the orchestrator reconciles after the parallel spawn cycle returns. Per-group state lives in `checkpoint.independence_group_stages`. |
| WORKFLOW-SYNC-002 | **Read-only workflow commands during orchestration** — When `pipeline-context.json` shows `active_command` as any Big Three AND `last_updated` is within 5 minutes, `/workflow-*` commands operate in read-only mode. They may read `task-board.json`, `focus-stack.json`, and `dashboard-cache.json` but MUST NOT modify task state. Full read/write access resumes when no Big Three session is active. |
| ENFORCE-UPGRADE-001 | **Triage-based enforcement upgrading** — Process injection hooks have a default `enforcement_tier` (GATE, ADVISORY, INFORMATIONAL). Triage complexity can UPGRADE (never downgrade) hooks: TRIVIAL = all defaults; MEDIUM = security + code review processes become GATE (P-034, P-036, P-038, P-039); COMPLEX = MEDIUM gates + testing processes become GATE (P-035, P-037). Overrides stored in `checkpoint.triage.enforcement_overrides`. See `processes/process_injection_map.md` for the full Three-Tier Enforcement Model. |
| RAID-001 | **Single RAID log** — P-010 (Stage 1 seeding) and P-074 (risk management) share a single RAID log at `.orchestrate/{session_id}/raid-log.json`. Append-only JSONL. Product-manager seeds at Phase 2 (Scope Contract); Phase 9 (Continuous Governance) appends risk-domain entries. Neither phase overwrites existing entries. |
| AUTO-EVAL-001 | **Auto-evaluation produces a recommended verdict; human approval finalizes it** — At every formal gate (Intent Review, Scope Lock, Dependency Acceptance, Sprint Readiness, Phase 5v Compliance Verdict, Stage 5 → Phase 5e Debug Entry, Phase 7 Release Readiness), the orchestrator first runs the deterministic checklists + agent-evaluator pattern to produce a `recommended_verdict` (PASS/FAIL/INDETERMINATE). The loop controller then writes a **gate-pending file** with the recommended verdict + summary and **polls for a gate-approval file** (HUMAN-GATE-001). The pipeline does not advance past the gate until the user writes an approval file with `decision: "approved"` (or `"rejected"`/`"stop"`). Both the auto-eval verdict and the human decision are recorded in `gate-state.json` for audit traceability. |
| HUMAN-GATE-001 | **File-polled human gates at 8 boundaries** — The pipeline pauses for human approval at: (1) Intent Review, (2) Scope Lock, (3) Dependency Acceptance, (4) Sprint Readiness, (5) Stage 5 → Phase 5e Debug Entry, (6) Phase 5v Compliance Verdict, (7) CAB Review (Phase 7 prelude — fires only when `release_flag == true` AND change classified HIGH-risk per CAB-GATE-001), (8) Phase 7 Release Readiness. At each gate, the loop controller writes `.orchestrate/<session>/gates/gate-pending-<gate_id>.json` and polls `.orchestrate/<session>/gates/gate-approval-<gate_id>.json` every `gate_poll_interval_seconds` (default 30) up to `gate_timeout_seconds` (default 86400, i.e. 24h). On timeout, terminate with `terminal_state: "gate_timeout"`. Schema and behavior in section "Human-in-the-Loop Gates" below. |
| CAB-GATE-001 | **CAB Review fires conditionally** — Gate 7 (`cab-review`) fires before Gate 8 (`release-readiness`) only when (a) `release_flag == true` AND (b) the CAB co-agent (technical-program-manager) classifies the change as `HIGH` or `CRITICAL` risk. The CAB co-agent runs first as part of Phase 7's RELEASE_PREP coordination and writes a CAB Decision Record. If risk classification is LOW or MEDIUM, the cab-review gate is skipped (logged as `[CAB-SKIP] risk_classification: <level>`) and Phase 7 proceeds to the release-readiness gate. |
| HANDOVER-001 | **Explicit handover receipt at every agent boundary** — When a spawned agent finishes work that another agent will consume, it MUST write a handover receipt to `.orchestrate/<session>/handovers/handover-{from_agent}-to-{to_agent}-{YYYYMMDD}-{HHMMSS}.json`. The orchestrator passes the receipt path in the next agent's spawn prompt. Schema in `_shared/protocols/command-dispatch.md` "Agent-to-Agent Handover Protocol" section. |
| HANDOVER-002 | **Acknowledgment on consumption** — Receiving agents MUST write an acknowledgment receipt before doing work. The ack records what was received and any questions. |
| HANDOVER-003 | **Clarification feedback loop with cap** — If the receiving agent flags `request_clarification: true`, the orchestrator re-spawns the producing agent with the questions. Cap: 2 clarification rounds per handover. After round 2, log `[HANDOVER-WARN]` and proceed. |
| MEETING-001 | **Three meeting handler types** — Every canonical meeting maps to one of three handlers: (a) Human-Gated (file-polled gate per HUMAN-GATE-001), (b) Multi-Agent Sync (parallel co-agent spawns + facilitator synthesis + meeting receipt; autonomous), (c) Async Single-Agent (one agent produces meeting outcome doc; autonomous). Multi-Agent Sync and Async Single-Agent meetings produce a meeting receipt to `.orchestrate/<session>/meetings/`. See "Meetings & Ceremonies" section. |

## Execution Guard — AUTO-ORCHESTRATE IS A LOOP CONTROLLER, NOT A WORKER

╔══════════════════════════════════════════════════════════════════════════╗
║  AUTO-ORCHESTRATE MUST NEVER:                                           ║
║                                                                         ║
║  1. Read project files to understand the codebase or task domain        ║
║     (that is the researcher/orchestrator's job)                         ║
║  2. Create implementation/work tasks directly — ONLY create ONE         ║
║     parent tracking task (Step 2c), then let the orchestrator           ║
║     propose all work tasks via proposed-tasks.json                      ║
║  3. Spawn an agent type that is not appropriate for the active phase    ║
║     (AUTO-001). Default = orchestrator. Phase 5v = auditor. Phase 5e =  ║
║     debugger. Phases 5q/5s/5i/5d/Stage 6/Phase 7-9 spawn the matching   ║
║     lead and co-agents per the Pipeline Stage Reference table.          ║
║  4. Do analysis, planning, or implementation work itself                ║
║  5. "Identify services", "read documentation", "understand the          ║
║     architecture" — these are Stage 0 (researcher) activities           ║
║  6. Skip a human gate (HUMAN-GATE-001). The loop controller MUST write  ║
║     gate-pending and poll for gate-approval at all 7 gate boundaries:   ║
║     Intent Review, Scope Lock, Dependency Acceptance, Sprint Readiness, ║
║     Stage 5 → Phase 5e Debug Entry, Phase 5v Compliance Verdict, and    ║
║     Phase 7 Release Readiness. Auto-evaluation produces a recommended   ║
║     verdict; the human decision finalizes it.                           ║
║                                                                         ║
║  AUTO-ORCHESTRATE ONLY:                                                 ║
║  - Enhances the user prompt (Step 1)                                    ║
║  - Creates session infrastructure (Step 2, including gates/ directory)  ║
║  - Spawns the phase-appropriate agent in a loop (Step 3)                ║
║  - Processes spawn results and manages tasks (Step 4)                   ║
║  - Writes gate-pending files and polls for gate-approval at all 7       ║
║    formal gate boundaries (HUMAN-GATE-001)                              ║
║  - Transitions between internal phases (5v audit, 5e debug, 5q/5s/5i/5d ║
║    domain, 7 release, 8 post-launch, 9 governance)                      ║
║  - Evaluates termination (Step 5)                                       ║
║                                                                         ║
║  If you catch yourself reading project docs, identifying services,      ║
║  creating more than 1 task before the first orchestrator spawn,         ║
║  or skipping a human gate — STOP. You are violating this guard.         ║
╚══════════════════════════════════════════════════════════════════════════╝

## Planning Phase Stages (P-Series)

The P-series stages implement the Clarity of Intent methodology (see `clarity_of_intent.md`). They execute sequentially before Stage 0 (Research) and produce planning artifacts that inform the AI execution pipeline. All four stages are MANDATORY for new projects. Each stage has one owner agent, one output artifact, one gate, and one or more triggered processes.

### P1: Intent Frame

| Field | Value |
|-------|-------|
| **Stage ID** | P1 |
| **Name** | Intent Frame |
| **Owner Agent** | `product-manager` |
| **Phase Mode** | `HUMAN_PLANNING` |
| **Input** | User's raw task description + project context |
| **Output Artifact** | Intent Brief (`.orchestrate/<session>/planning/P1-intent-brief.md`) |
| **Gate** | Intent Review |
| **Gate Pass Criteria** | Clear objective stated; stakeholders identified; measurable success criteria defined; explicit boundaries (what this is NOT); strategic context references a real OKR or priority |
| **Processes Triggered** | P-001 (Intent Articulation) |
| **max_turns** | 20 |

**Intent Brief Template** (agent MUST produce all 5 sections):

1. **Outcome** -- measurable end-state, not a feature description
2. **Beneficiaries** -- named user segment with before/after description
3. **Strategic Context** -- OKR or quarterly theme connection
4. **Boundaries** -- explicit exclusions (what this project is NOT)
5. **Cost of Inaction** -- what happens if we do not do this

**Intent Review Gate Logic**:

```
GATE_PASS = (
    artifact_exists(".orchestrate/<session>/planning/P1-intent-brief.md")
    AND section_count >= 5
    AND each_section_has_content(min_chars=50)
    AND outcome_is_measurable(section_1)  # contains a metric, percentage, or timeline
    AND boundaries_stated(section_4)       # at least one "NOT" exclusion
)

IF GATE_PASS:
    planning_gate_statuses.P1 = "PASSED"
    planning_stages_completed.append("P1")
    emit "[GATE] Intent Review: PASSED -- Intent Brief produced"
ELSE:
    planning_gate_statuses.P1 = "FAILED"
    emit "[GATE] Intent Review: FAILED -- <missing_sections>"
    # Retry: re-spawn product-manager with failure feedback
```

**Output format**: `[P1:PLANNING] Intent Frame -- product-manager -- P-001`

### P2: Scope Contract

| Field | Value |
|-------|-------|
| **Stage ID** | P2 |
| **Name** | Scope Contract |
| **Owner Agent** | `product-manager` |
| **Phase Mode** | `HUMAN_PLANNING` |
| **Input** | P1 Intent Brief (`.orchestrate/<session>/planning/P1-intent-brief.md`) |
| **Output Artifact** | Scope Contract (`.orchestrate/<session>/planning/P2-scope-contract.md`) |
| **Gate** | Scope Lock |
| **Gate Pass Criteria** | Every deliverable has named owner + Definition of Done; exclusions explicit; success metrics trace to Intent Brief outcome; assumptions with HIGH severity have validation plan |
| **Processes Triggered** | P-007 (Deliverable Decomposition), P-013 (Scope Lock Gate) |
| **max_turns** | 20 |

**Scope Contract Template** (agent MUST produce all 6 sections):

1. **Outcome Restatement** -- verbatim copy from Intent Brief Section 1
2. **Deliverables** -- table with columns: #, Deliverable, Description, Owner
3. **Definition of Done** -- table with columns: Deliverable, Done When (testable criteria)
4. **Explicit Exclusions** -- table with columns: Exclusion, Reason, Future Home
5. **Success Metrics** -- table with columns: Metric, Baseline, Target, Measurement Method, Timeline
6. **Assumptions and Risks** -- table with columns: Item, Type, Severity, Mitigation, Owner

**Scope Lock Gate Logic**:

```
GATE_PASS = (
    artifact_exists(".orchestrate/<session>/planning/P2-scope-contract.md")
    AND section_count >= 6
    AND deliverables_have_owners(section_2)      # every row has non-empty Owner
    AND deliverables_have_dod(section_3)          # every deliverable in section_2 has a DoD in section_3
    AND exclusions_present(section_4)             # at least one exclusion row
    AND metrics_trace_to_intent(section_5)        # at least one metric references Intent Brief outcome
    AND high_severity_items_have_plan(section_6)  # HIGH items have non-empty Mitigation
)

IF GATE_PASS:
    planning_gate_statuses.P2 = "PASSED"
    planning_stages_completed.append("P2")
    emit "[GATE] Scope Lock: PASSED -- Scope Contract produced"
ELSE:
    planning_gate_statuses.P2 = "FAILED"
    emit "[GATE] Scope Lock: FAILED -- <validation_failures>"
```

**Output format**: `[P2:PLANNING] Scope Contract -- product-manager -- P-007, P-013`

### P3: Dependency Map

| Field | Value |
|-------|-------|
| **Stage ID** | P3 |
| **Name** | Dependency Map |
| **Owner Agent** | `technical-program-manager` |
| **Phase Mode** | `HUMAN_PLANNING` |
| **Input** | P2 Scope Contract (`.orchestrate/<session>/planning/P2-scope-contract.md`) |
| **Output Artifact** | Dependency Charter (`.orchestrate/<session>/planning/P3-dependency-charter.md`) |
| **Gate** | Dependency Acceptance |
| **Gate Pass Criteria** | Every dependency has named owner + "needed by" date; critical path documented; escalation paths defined for all blocked dependencies |
| **Processes Triggered** | P-015 (Cross-Team Dependency Registration), P-016 (Critical Path Analysis) |
| **Skills Invoked** | `dependency-analyzer` — Read `~/.claude/skills/dependency-analyzer/SKILL.md` and run dependency analysis to inform the Dependency Register and Critical Path |
| **max_turns** | 20 |

**Dependency Charter Template** (agent MUST produce all 4 sections):

1. **Dependency Register** -- table with columns: ID, Dependent Team, Depends On, What Is Needed, By When, Status, Owner, Escalation Path
2. **Shared Resource Conflicts** -- table with columns: Resource, Competing Demands, Resolution
3. **Critical Path** -- sequential dependency chain showing minimum timeline
4. **Communication Protocol** -- table with columns: Mechanism, Cadence, Participants, Purpose

**Dependency Analysis Skill Integration**:
Before producing the Dependency Charter, the technical-program-manager MUST:
1. Read `~/.claude/skills/dependency-analyzer/SKILL.md`
2. Run dependency analysis on the project to extract source-level dependencies, detect circular imports, and validate architecture layers
3. Use the cycle detection and layer validation outputs to populate the Dependency Register (section 1) and Critical Path (section 3)
4. Flag any circular dependencies discovered as blockers in the Escalation Path column

**Dependency Acceptance Gate Logic**:

```
GATE_PASS = (
    artifact_exists(".orchestrate/<session>/planning/P3-dependency-charter.md")
    AND section_count >= 4
    AND dependencies_have_owners(section_1)        # every row has non-empty Owner
    AND dependencies_have_dates(section_1)          # every row has non-empty By When
    AND critical_path_present(section_3)            # section_3 has at least one dependency chain
    AND escalation_paths_defined(section_1)         # blocked items have Escalation Path
)

IF GATE_PASS:
    planning_gate_statuses.P3 = "PASSED"
    planning_stages_completed.append("P3")
    emit "[GATE] Dependency Acceptance: PASSED -- Dependency Charter produced"
ELSE:
    planning_gate_statuses.P3 = "FAILED"
    emit "[GATE] Dependency Acceptance: FAILED -- <validation_failures>"
```

**Output format**: `[P3:PLANNING] Dependency Map -- technical-program-manager -- P-015, P-016`

### P4: Sprint Bridge

| Field | Value |
|-------|-------|
| **Stage ID** | P4 |
| **Name** | Sprint Bridge |
| **Owner Agent** | `engineering-manager` |
| **Phase Mode** | `HUMAN_PLANNING` |
| **Input** | P3 Dependency Charter + P2 Scope Contract |
| **Output Artifact** | Sprint Kickoff Brief (`.orchestrate/<session>/planning/P4-sprint-kickoff-brief.md`) |
| **Gate** | Sprint Readiness |
| **Gate Pass Criteria** | Sprint goal stated and connects to Scope Contract deliverable; intent trace visible (project intent -> deliverable -> sprint goal); all stories have acceptance criteria; dependencies due this sprint have status + contingency |
| **Processes Triggered** | P-022 (Sprint Goal Authoring), P-023 (Intent Trace Validation) |
| **max_turns** | 20 |

**Sprint Kickoff Brief Template** (agent MUST produce all 5 sections):

1. **Sprint Goal** -- one sentence stating what will be true at sprint end
2. **Intent Trace** -- three-line trace: Project Intent -> Scope Deliverable -> Sprint Goal
3. **Stories and Acceptance Criteria** -- table with columns: Story, Acceptance Criteria, Points, Assignee
4. **Dependencies Due This Sprint** -- table with columns: Dependency, Needed By, Current Status, Contingency if Late
5. **Definition of Done (Sprint Level)** -- bulleted checklist of completion criteria

**Sprint Readiness Gate Logic**:

```
GATE_PASS = (
    artifact_exists(".orchestrate/<session>/planning/P4-sprint-kickoff-brief.md")
    AND section_count >= 5
    AND sprint_goal_present(section_1)               # non-empty, one sentence
    AND intent_trace_complete(section_2)              # all three lines present
    AND stories_have_ac(section_3)                    # every story row has Acceptance Criteria
    AND dependencies_have_contingency(section_4)      # every dependency has Contingency if Late
)

IF GATE_PASS:
    planning_gate_statuses.P4 = "PASSED"
    planning_stages_completed.append("P4")
    emit "[GATE] Sprint Readiness: PASSED -- Sprint Kickoff Brief produced"
ELSE:
    planning_gate_statuses.P4 = "FAILED"
    emit "[GATE] Sprint Readiness: FAILED -- <validation_failures>"
```

**Output format**: `[P4:PLANNING] Sprint Bridge -- engineering-manager -- P-022, P-023`

### Planning Artifact Flow

```
User Input (task_description + project context)
  |
  v
P1-Research (researcher) --> P1 Intent Frame (product-manager) --> Intent Review Gate
  |                                    |
  |    answers "Why?" and "What outcome?"
  |    consumed by: P2 (Scope Contract)
  |                                    |
  v                                    v
P2-Research (researcher) --> P2 Scope Contract (product-manager) --> Scope Lock Gate
                                       |
       answers "What exactly?" and "What does done look like?"
       consumed by: P3 (Dependency Charter), Stage 0 (researcher)
                                       |
                                       v
                            P3 Dependency Map (TPM) --> Dependency Acceptance Gate
                                       |
              answers "Who else?" and "What is the critical path?"
              consumed by: P4 (Sprint Kickoff Brief), Stage 1 (product-manager)
                                       |
                                       v
                            P4 Sprint Bridge (EM) --> Sprint Readiness Gate
                                       |
              answers "What in the first sprint?"
              consumed by: Stage 1 (product-manager task decomposition)
                                       |
                                       v PRE-RESEARCH-GATE
                                       |
                            Stage 0 Research (researcher) --> ...

Stage 0: researcher reads P2 (Scope Contract) for research focus
Stage 1: product-manager reads all P1-P4 artifacts for task decomposition
Stages 2-6: unchanged (consume Stage 0/1 outputs as before)
```

### Planning Revision Protocol (PLAN-REV)

The planning flow supports **conditional backward edges** when a later stage discovers that an earlier stage's assumptions are invalid.

| ID | Rule |
|----|------|
| PLAN-REV-001 | **Revision trigger** — If P3 (Dependency Map) or P4 (Sprint Bridge) discovers that a dependency, resource conflict, or timeline constraint makes the P2 Scope Contract infeasible, the agent MUST emit a `[PLAN-REVISION]` signal in its output. |
| PLAN-REV-002 | **Revision scope** — A revision can target P2 (scope change) or P1 (intent change). It CANNOT skip — revising P1 requires re-running P2, P3, and P4. Revising P2 requires re-running P3 and P4. |
| PLAN-REV-003 | **Revision budget** — Maximum 2 revision cycles per planning phase. After 2 revisions, the pipeline proceeds with the current artifacts and logs `[PLAN-REV-CAP] Revision budget exhausted — proceeding with current planning artifacts`. |
| PLAN-REV-004 | **Revision artifact** — The revising agent writes a `P{N}-revision-rationale.md` explaining what changed and why before the target stage re-executes. |

> **Constraint aliases**: BACKTRACK-001 ≡ PLAN-REV-001 (revision trigger), BACKTRACK-002 ≡ PLAN-REV-003 (revision budget), BACKTRACK-003 ≡ PLAN-REV-004 (artifact logging). These aliases are used in the constraint registry (Improvements.md §F2).

**Revision signal format**:
```
[PLAN-REVISION] Target: P2 | Reason: <one-line reason>
Invalidating finding: <specific dependency/conflict that makes current scope infeasible>
Recommended change: <what should change in the target artifact>
```

**P3 dependency analysis prerequisite (SKILL-REUSE-003)**: The technical-program-manager at P3 MUST invoke the `dependency-analyzer` skill before evaluating whether to trigger a PLAN-REVISION. This ensures the backtrack decision is informed by formal dependency analysis rather than ad-hoc assessment.

**Revision flow**:
```
P1 → P2 → P3 (dependency-analyzer) ──[PLAN-REVISION Target:P2]──→ P2' → P3' → P4
                                                                          │
P1 → P2 → P3 → P4 ──[PLAN-REVISION Target:P1]──→ P1' → P2' → P3' → P4'
```

**Gate handling on revision**: When a revision is triggered:
1. The triggering stage's gate status remains `"FAILED"` (it did not complete successfully)
2. The target stage's gate status is reset to `null`
3. All stages between target and trigger (inclusive) are removed from `planning_stages_completed`
4. `planning_revision_count` is incremented in checkpoint
5. Log: `[PLAN-REV] Revision {N}/2 — reverting to P{target} due to: <reason>`

**Checkpoint addition**:
```json
{
  "planning_revision_count": 0,
  "planning_revision_history": []
}
```

## Meetings & Ceremonies (MEETING-001)

The canonical end-to-end process specifies live ceremonies (P-020 Dependency Standup, P-026 Daily Standup, P-027 Sprint Review, P-028 Sprint Retrospective, P-029 Backlog Refinement, P-076 CAB, P-082 Quarterly Capacity Planning). The pipeline implements them via three handler types — each ceremony is a sequence of agent spawns + artifact production, not a real-time multi-party event.

### Three Handler Types

| Type | Mechanism | Pauses pipeline? |
|------|-----------|-------------------|
| **Human-Gated** | `gate-pending-{gate_id}.json` + poll for `gate-approval-{gate_id}.json` (HUMAN-GATE-001) | YES — until user approves |
| **Multi-Agent Sync** | Orchestrator spawns facilitator + attendee co-agents in parallel; facilitator synthesizes minutes; meeting receipt written | NO — runs inline |
| **Async Single-Agent** | One agent produces structured meeting outcome doc; meeting receipt written | NO — runs inline |

### Meeting Catalog

| P-XXX | Meeting | Handler | Facilitator | Cadence | PHASE: value |
|-------|---------|---------|-------------|---------|--------------|
| P-004 | Intent Review | Human-Gated | engineering-manager (evaluator) | Per project | Gate `intent-review` |
| P-013 | Scope Lock | Human-Gated | product-manager (evaluator) | Per project | Gate `scope-lock` |
| P-019 | Dependency Acceptance | Human-Gated | technical-program-manager (evaluator) | Per project | Gate `dependency-acceptance` |
| P-025 | Sprint Readiness | Human-Gated | engineering-manager (evaluator) | Per sprint | Gate `sprint-readiness` |
| (Phase 4 close) | Sprint Kickoff | Multi-Agent Sync | engineering-manager | Per sprint | `SPRINT_CEREMONY` |
| P-026 | Daily Standup | Multi-Agent Sync | product-manager (Scrum Master) | L = every 5 iters; XL = every 3; M and below = none | `DAILY_STANDUP` |
| P-020 | Dependency Standup | Multi-Agent Sync | technical-program-manager | Same as P-026 + only if `cross_team_impact` non-empty | `DEPENDENCY_STANDUP` |
| P-029 | Backlog Refinement | Async Single-Agent | product-manager | Same as P-026 + only when backlog has unrefined items | `BACKLOG_REFINEMENT` |
| P-027 | Sprint Review | Multi-Agent Sync | engineering-manager (chair) | After Stage 6 completes | `SPRINT_REVIEW` |
| P-028 | Sprint Retrospective | Multi-Agent Sync | engineering-manager (facilitator) | After Sprint Review | `SPRINT_RETRO` |
| P-076 | Pre-Launch Risk Review (CAB) | Human-Gated | technical-program-manager | Phase 7 prelude when `release_flag` AND HIGH-risk (CAB-GATE-001) | Gate `cab-review` |
| P-077 | Quarterly Risk Review | Async Single-Agent | engineering-manager | Phase 9 risk sub-routine | (Phase 9) |
| P-082 | Quarterly Capacity Planning | Hybrid (Async + final gate) | engineering-manager | Phase 9 capacity sub-routine | (Phase 9) |

### Sprint Closure Phase Sequence (post-Stage 6, pre-Phase 7)

```
Stage 6 (Documentation) completes
     │
     ▼
PHASE: SPRINT_REVIEW                  ← engineering-manager chair, product-manager + software-engineer attendees
     │  meetings/meeting-p-027-sprint-review-<TS>.json
     │  Handover → engineering-manager (Sprint Retro)
     ▼
PHASE: SPRINT_RETRO                   ← engineering-manager facilitator (4 L's framework)
     │  meetings/meeting-p-028-sprint-retro-<TS>.json
     │  Handover → product-manager (Backlog Refinement)
     ▼
PHASE: BACKLOG_REFINEMENT             ← product-manager (incorporates retro action items)
     │  meetings/meeting-p-029-backlog-refinement-<TS>.json
     │  Handover → orchestrator (Phase 7 entry, if release_flag)
     ▼
Phase 7 Release Prep (if release_flag) OR session termination
```

### Iteration-Boundary Meetings During Execution

During Stages 0-5 execution, the loop controller fires standup meetings on a t-shirt-size cadence. The check runs at the end of every iteration in Step 4 (after task processing, before termination evaluation):

```
IF checkpoint.triage.tshirt_size IN ["L", "XL"]:
    interval = 5 IF tshirt_size == "L" ELSE 3
    IF checkpoint.iteration > 0 AND checkpoint.iteration % interval == 0:

        # P-026 Daily Standup — always fires at boundary
        spawn PHASE: DAILY_STANDUP

        # P-020 Dependency Standup — only if cross-team impact
        IF len(checkpoint.triage.cross_team_impact) > 0:
            spawn PHASE: DEPENDENCY_STANDUP

        # P-029 Backlog Refinement — only if unrefined backlog items exist
        IF backlog has unrefined items:
            spawn PHASE: BACKLOG_REFINEMENT
```

For trivial / S / M tasks (`tshirt_size` not in {L, XL}), no standup meetings fire — the cadence is suppressed. The orchestrator still produces handover receipts at every stage transition per HANDOVER-001.

---

## Pipeline Stage Reference

Agent assignments below match the canonical role-to-process ownership in `processes/AGENT_PROCESS_MAP.md`. Each row lists the **lead** agent (in bold or first) and any **co-agents** that own processes in the same phase. The orchestrator spawns the lead agent first; co-agents are spawned for processes they own when those processes activate.

| Stage | Name | Lead agent | Co-agents (process-owned) | Mandatory | Artifact | Gate | Complete when |
|-------|------|------------|---------------------------|-----------|----------|------|---------------|
| P1 | Intent Frame | `product-manager` (P-001..P-003) | `engineering-manager` (P-004 Intent Review Gate, P-005 Strategic Prioritization, P-006 Tech Vision); `staff-principal-engineer` (P-006 support) | **YES** | Intent Brief | **Intent Review (HUMAN GATE)** | Intent Brief produced; Intent Review gate APPROVED by user |
| P2 | Scope Contract | `product-manager` (P-007..P-011, P-013, P-014) | `security-engineer` (P-012 AppSec Scope Review); `qa-engineer` (P-008 DoD support); `sre` + `data-engineer` (P-009 Success Metrics support) | **YES** | Scope Contract | **Scope Lock (HUMAN GATE)** | Scope Contract produced; Scope Lock gate APPROVED by user |
| P3 | Dependency Map | `technical-program-manager` (P-015..P-021) | `engineering-manager` (P-017 conflict resolution, P-019 gate co-owner, P-021 escalation); `infra-engineer` (P-017 platform conflicts); `staff-principal-engineer` (P-016 critical path support) | **YES** | Dependency Charter | **Dependency Acceptance (HUMAN GATE)** | Dependency Charter produced; Dependency Acceptance gate APPROVED by user |
| P4 | Sprint Bridge | `engineering-manager` (P-022, P-023, P-025, P-027, P-028) | `product-manager` (P-024 Story Writing, P-026 Standup, P-029 Backlog); `technical-program-manager` (P-030 Sprint Dependency Tracking); `software-engineer` (P-031 Feature Development) | **YES** | Sprint Kickoff Brief | **Sprint Readiness (HUMAN GATE)** | Sprint Kickoff Brief produced; Sprint Readiness gate APPROVED by user |
| 0 | Research | `researcher` | — | **YES** | Research Document | -- | researcher task completed |
| 1 | Task Decomposition | `product-manager` | — | **YES** | Epic Decomposition | -- | product-manager task completed |
| 2 | Specification | `spec-creator` (skill) | — | **YES** | Technical Spec | -- | spec-creator task completed |
| 3 | Implementation | `software-engineer` / `library-implementer-python` (skill) | — | Per task | Production Code | -- | software-engineer task completed |
| 4 | Tests | `test-writer-pytest` (skill) | — | Per task | Test Suite | -- | test-writer-pytest task completed |
| 4.5 | Code Stats | `codebase-stats` (skill) | — | **YES** (post-impl) | Metrics Report | -- | codebase-stats task completed |
| 5 | Validation | `validator` (skill) | `spec-compliance` (skill) | **YES** | Validation Report | -- | validator task completed |
| 5q | Quality Phase | `qa-engineer` (P-032..P-035, P-037) | `product-manager` (P-036 Acceptance Criteria Verification) | When scope flags qa | QA review (P-032..P-037) | -- | findings produced; phase receipt written |
| 5s | Security Phase | `security-engineer` (P-038..P-043) | — | When scope flags security or P-038..P-043 flagged HIGH/CRITICAL | Security review (P-038..P-043) | -- | findings produced; phase receipt written |
| 5i | Infra/SRE Phase | `infra-engineer` (P-044..P-047, P-088, P-089), `sre` (P-054..P-057, P-059) | `technical-program-manager` (P-048 Production Release Management); `security-engineer` (P-039 SAST/DAST CI co-ownership) | When scope flags infra or Stage 5 fails with infra keywords | Infra review (P-044..P-048, P-054..P-057) | -- | findings produced; phase receipt written |
| 5d | Data/ML Phase | `data-engineer` (P-049, P-050), `ml-engineer` (P-051..P-053) | — | When scope flags data_ml or P-049..P-053 flagged HIGH/CRITICAL | Data/ML review (P-049..P-053) | -- | findings produced; phase receipt written |
| 5v | Validation+Audit | `auditor` | — | When Stage 5 PASSES but compliance < threshold | Compliance Report (weighted MUST/SHOULD/MAY) | **Compliance Verdict (HUMAN GATE)** | verdict APPROVED by user; max audit cycles enforced |
| 5e | Debug sub-loop | `debugger` | — | When Stage 5 FAILS after 3 fix iterations | Debug report (triage-research-fix-verify) | **Debug Entry (HUMAN GATE)** before sub-loop runs | all errors resolved or max debug iterations reached |
| 6 | Documentation | `technical-writer` (P-058 API Docs, P-061 Release Notes) | `sre` (P-059 Runbook Authoring); `software-engineer` (P-060 ADR Publication) | **YES** | Documentation | -- | technical-writer task completed |
| 7 | Release Prep | `orchestrator` (PHASE: RELEASE_PREP) | `qa-engineer` (P-035 Performance Testing); `infra-engineer` (P-044..P-047); `technical-program-manager` (P-048 Production Release Management, P-076 Pre-Launch Risk Review/CAB); `sre` (P-054, P-059); `technical-writer` (P-061 Release Notes) | When `release_flag == true` | Release readiness artifact | **Release Readiness (HUMAN GATE)** | release artifact produced; release gate APPROVED by user |
| 8 | Post-Launch | `sre` (P-054..P-057) | `product-manager` (P-070 Project Post-Mortem, P-072 OKR Retro, P-073 Outcome Measurement); `engineering-manager` (P-071 Quarterly Process Health Review) | After Phase 7 OR `triage.mode == "post_launch"` | Post-launch artifacts (P-070..P-073, P-054..P-057) | -- | post-launch processes acknowledged |
| 9 | Continuous Governance | (per sub-routine) | `engineering-manager` (P-062..P-066, P-077, P-078, P-081, P-082, P-084, P-090..P-092); `software-engineer` (P-067, P-068); `technical-program-manager` (P-069, P-074, P-076, P-083, P-093); `product-manager` (P-075, P-079); `staff-principal-engineer` (P-080, P-085..P-087); `infra-engineer` (P-088, P-089); `technical-writer` (P-080 support, P-092 support) | When tech_debt > 30%, duplication > 15%, or CRITICAL RAID items present | Governance artifacts (P-062..P-093) | -- | governance processes acknowledged |

Unknown/no dispatch_hint → "Uncategorized".

## Human-in-the-Loop Gates (HUMAN-GATE-001)

The pipeline pauses for human approval at 7 formal gate boundaries. The mechanism is **file-polled** — async — so the user can approve from any terminal, IDE, or CI tool that can write to the session's gates directory.

### Gate Boundaries

| # | Gate ID | When | Recommended verdict produced by |
|---|---------|------|----------------------------------|
| 1 | `intent-review` | After Phase 1 (Intent Frame) auto-eval | product-manager (with engineering-manager evaluator for P-004) |
| 2 | `scope-lock` | After Phase 2 (Scope Contract) auto-eval | product-manager (with security-engineer for P-012) |
| 3 | `dependency-acceptance` | After Phase 3 (Dependency Map) auto-eval | technical-program-manager (with engineering-manager for P-019) |
| 4 | `sprint-readiness` | After Phase 4 (Sprint Bridge) auto-eval | engineering-manager |
| 5 | `debug-entry` | When Stage 5 fix-loop exhausts (3 iterations) and before Phase 5e begins | validator (failure summary) |
| 6 | `compliance-verdict` | After Phase 5v (Audit) compliance score is computed, before remediation | auditor |
| 7 | `release-readiness` | After Phase 7 (Release Prep) artifacts are produced, before deployment-affecting actions | orchestrator (PHASE: RELEASE_PREP) |

### Gate Directory

```
.orchestrate/<session-id>/gates/
├── gate-pending-intent-review.json         # Written by loop controller
├── gate-approval-intent-review.json        # Written by USER
├── gate-pending-scope-lock.json
├── gate-approval-scope-lock.json
├── gate-pending-dependency-acceptance.json
├── ...
└── gate-history.jsonl                       # Append-only log of all gate transitions
```

### gate-pending-{gate_id}.json Schema

Written by the loop controller when a gate is reached. Contains the recommended verdict from auto-eval plus the context needed for a human to make a decision.

```json
{
  "schema_version": "1.0.0",
  "gate_id": "intent-review",
  "phase": "Phase 1: Intent Frame",
  "session_id": "auto-orc-20260425-myapp",
  "session_path": ".orchestrate/auto-orc-20260425-myapp",
  "iteration": 1,
  "created_at": "2026-04-25T10:30:00Z",
  "expires_at": "2026-04-26T10:30:00Z",
  "recommended_verdict": "approved",
  "recommended_by": "auto-eval",
  "evaluator_breakdown": {
    "deterministic_criteria": {
      "artifact_exists": true,
      "section_count_meets_min": true,
      "outcome_is_measurable": true,
      "boundaries_stated": true
    },
    "agent_evaluator": {
      "agent": "product-manager",
      "verdict": "PASS",
      "rationale": "Intent Brief is internally consistent and answers all 5 template questions substantively"
    }
  },
  "artifact_path": ".orchestrate/auto-orc-20260425-myapp/planning/P1-intent-brief.md",
  "summary": "Intent Brief produced. Outcome: 'reduce checkout abandonment by 15% within Q3'. Beneficiaries: returning customers. 3 boundaries stated. Strategic context references Q3 OKR-2.",
  "blocking_findings": [],
  "approval_options": [
    { "decision": "approved", "effect": "Proceed to next phase" },
    { "decision": "approved_with_edits", "effect": "Proceed using the artifact_edit_path provided in approval file" },
    { "decision": "rejected", "effect": "Re-spawn owner agent with feedback in approval file" },
    { "decision": "stop", "effect": "Terminate session with terminal_state: 'gate_rejected'" }
  ],
  "instructions_for_user": "Review the artifact at artifact_path. Then write .orchestrate/<session-id>/gates/gate-approval-intent-review.json with your decision. If you approve_with_edits, edit the artifact in place and reference its path in the approval file."
}
```

### gate-approval-{gate_id}.json Schema

Written by the user (or any tool acting on their behalf) to approve, reject, or stop. The loop controller polls for this file every `gate_poll_interval_seconds` (default 30).

```json
{
  "schema_version": "1.0.0",
  "gate_id": "intent-review",
  "decision": "approved",
  "decided_at": "2026-04-25T10:42:00Z",
  "decided_by": "<user identifier — free-form: name, email, CI bot, etc.>",
  "feedback": "Outcome target tightened from 15% to 12% — see edited artifact",
  "artifact_edit_path": ".orchestrate/auto-orc-20260425-myapp/planning/P1-intent-brief.md"
}
```

**Required fields**: `gate_id`, `decision`, `decided_at`. All others optional. `feedback` is consumed by the orchestrator on `rejected` to inform the retry; on `approved` it is logged to gate-history.

### Gate Flow Logic

```
FUNCTION run_gate(gate_id, recommended_verdict, evaluator_breakdown, artifact_path, summary):

  pending_path = ".orchestrate/<session>/gates/gate-pending-{gate_id}.json"
  approval_path = ".orchestrate/<session>/gates/gate-approval-{gate_id}.json"

  # Step 1: Write gate-pending file
  write atomically to pending_path:
    { gate_id, phase, recommended_verdict, evaluator_breakdown,
      artifact_path, summary, blocking_findings,
      created_at: now_iso8601(),
      expires_at: now_iso8601() + gate_timeout_seconds,
      approval_options, instructions_for_user }

  Display:
    [HUMAN-GATE] {phase} — awaiting approval at {pending_path}
    Recommended verdict: {recommended_verdict}
    Approve by writing: {approval_path}

  # Step 2: Poll for approval file
  start_time = now()
  WHILE not exists(approval_path):
    IF (now() - start_time) > gate_timeout_seconds:
      Log: "[HUMAN-GATE] Gate {gate_id} timed out after {gate_timeout_seconds}s"
      Set checkpoint.terminal_state = "gate_timeout"
      Append to gates/gate-history.jsonl:
        { gate_id, decision: "timeout", timestamp: now_iso8601() }
      RETURN "TIMEOUT"
    sleep(gate_poll_interval_seconds)

  # Step 3: Read and validate approval
  approval = read_json(approval_path)
  validate approval has required fields {gate_id, decision, decided_at}
  validate approval.gate_id matches expected gate_id
  validate approval.decision IN {approved, approved_with_edits, rejected, stop}

  # Step 4: Append to gate-state.json + gate-history.jsonl
  Append to gate-state.json:
    { gate: gate_id, status: <decision>, evaluated_at: now_iso8601(),
      evaluator: "human", recommended_verdict: recommended_verdict,
      decided_by: approval.decided_by, feedback: approval.feedback }
  Append to gates/gate-history.jsonl: same content

  # Step 5: Act on decision
  IF approval.decision IN ["approved", "approved_with_edits"]:
    IF approval.artifact_edit_path is not null:
      Use approval.artifact_edit_path as the canonical artifact for downstream phases.
    Log: "[HUMAN-GATE] {gate_id} APPROVED by {approval.decided_by}"
    RETURN "APPROVED"

  IF approval.decision == "rejected":
    Log: "[HUMAN-GATE] {gate_id} REJECTED by {approval.decided_by}: {approval.feedback}"
    # Loop controller re-spawns the owner agent with approval.feedback as additional context
    RETURN "REJECTED"

  IF approval.decision == "stop":
    Log: "[HUMAN-GATE] {gate_id} STOP requested by {approval.decided_by}"
    Set checkpoint.terminal_state = "gate_rejected"
    RETURN "STOP"
```

### Configuration

These knobs are exposed as command arguments and checkpoint fields:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `gate_poll_interval_seconds` | 30 | How often the loop controller checks for the approval file |
| `gate_timeout_seconds` | 86400 (24h) | Max wait time before terminating with `gate_timeout` |
| `skip_human_gates` | false | If true, the recommended_verdict from auto-eval is treated as approved automatically. Use only for CI/automation contexts where humans cannot intervene. **Sets gate-state.json `evaluator` to `"auto-skip"` for audit trail.** |

### Resume After Approval

When the loop controller is interrupted while polling, resuming the session reads the latest `gate-pending-*.json`. If a matching `gate-approval-*.json` was written during the interruption, the approval is consumed on resume. Otherwise polling continues from `created_at + (now - last_poll)`.

---

## Phase 5v — Validation + Audit (absorbed from former /auto-audit)

Phase 5v is the internal compliance audit sub-loop. It activates after Stage 5 (Validation) PASSES but compliance falls below threshold (default 90%).

| Field | Value |
|-------|-------|
| **Phase ID** | 5v |
| **Owner Agent** | `auditor` |
| **Trigger** | Stage 5 verdict = PASS but `spec-compliance` weighted score < `compliance_threshold` (default 90%) |
| **Cap** | `max_audit_cycles` (default 5) |
| **Output** | `.orchestrate/<session>/phase-receipts/phase-5v-audit-cycle-{N}-{timestamp}.json` + per-cycle audit report |

### Phase 5v Loop

```
audit_cycle = 0
WHILE audit_cycle < max_audit_cycles:
    audit_cycle += 1
    Log: "[PHASE 5v] Audit cycle {audit_cycle}/{max_audit_cycles} starting"

    # Phase A: Auditor analyzes
    Spawn auditor agent with PHASE: AUDIT, scope=current session artifacts.
    Auditor runs spec-compliance with weighted scoring:
      - MUST findings: weight 3
      - SHOULD findings: weight 2
      - MAY findings: weight 1
    Output: .orchestrate/<session>/cycle-{N}/gap-report.json + audit-report.md

    score = compute_weighted_compliance_score(gap_report)

    # HUMAN GATE — compliance verdict (HUMAN-GATE-001 #6)
    # Required at every audit cycle so the human can: accept current state, request
    # remediation, or stop the session.
    IF score >= compliance_threshold:
        recommended_verdict = "approved"  # auto-eval recommends PASS
    ELSE IF NO new gaps in this cycle that weren't in the previous (state hash collision):
        recommended_verdict = "approved_with_edits"  # auto-eval recommends ACCEPTABLE_THRASH
    ELSE:
        recommended_verdict = "rejected"  # auto-eval recommends REMEDIATE

    gate_result = run_gate(
      gate_id = "compliance-verdict",
      recommended_verdict = recommended_verdict,
      evaluator_breakdown = {
        compliance_score: score,
        threshold: compliance_threshold,
        cycle: audit_cycle,
        gap_count: gap_report.gap_count,
        critical_gap_count: count_severity(gap_report, "CRITICAL"),
        thrashing_detected: <bool>
      },
      artifact_path = ".orchestrate/<session>/cycle-{audit_cycle}/audit-report.md",
      summary = "Compliance score: {score}% (threshold: {compliance_threshold}%). {gap_count} gaps ({critical_gap_count} CRITICAL). Cycle {audit_cycle}/{max_audit_cycles}."
    )

    IF gate_result == "APPROVED":
        # User accepts compliance state — exit audit loop with PASS or ACCEPTABLE
        verdict = "PASS" IF score >= compliance_threshold ELSE "ACCEPTABLE_HUMAN"
        Log: "[PHASE 5v] Compliance verdict APPROVED by user at cycle {audit_cycle} (score: {score}%)"
        BREAK

    IF gate_result == "STOP":
        verdict = "STOPPED_BY_USER"
        Set checkpoint.terminal_state = "gate_rejected"
        Log: "[PHASE 5v] User requested stop; halting audit"
        BREAK

    IF gate_result == "TIMEOUT":
        verdict = "GATE_TIMEOUT"
        Set checkpoint.terminal_state = "gate_timeout"
        Log: "[PHASE 5v] Compliance verdict gate timed out"
        BREAK

    # gate_result == "REJECTED" → user requests remediation. Phase B runs.

    # Phase B: Orchestrator remediates
    Log: "[PHASE 5v] User requested remediation; remediating gaps (score {score}%)"
    Spawn orchestrator with PHASE: REMEDIATE, gap-report.json verbatim, plus user feedback from approval.
    Orchestrator creates Stage 3 fix tasks (regression: true, blockedBy: gap_id),
    re-enters Stage 3 → Stage 4.5 → Stage 5 inline, then returns to Phase 5v.

IF audit_cycle >= max_audit_cycles AND verdict NOT IN ["PASS", "ACCEPTABLE_HUMAN", "STOPPED_BY_USER", "GATE_TIMEOUT"]:
    verdict = "FAIL_AUDIT_EXHAUSTED"
    Log: "[PHASE 5v] Max audit cycles reached; final score {score}%"

Write phase receipt with verdict, score, audit_cycle count.
```

## Phase 5e — Debug sub-loop (absorbed from former /auto-debug)

Phase 5e is the internal error-debug sub-loop. It activates when Stage 5 (Validation) FAILS after the validator's own 3 fix iterations are exhausted.

| Field | Value |
|-------|-------|
| **Phase ID** | 5e |
| **Owner Agent** | `debugger` |
| **Trigger** | Stage 5 fix-loop exhausted; remaining errors > 0 |
| **Cap** | `max_debug_iterations` (default 50); `max_phase_5e_entries_per_session` (default 2, matches REGRESS-002) |
| **Output** | `.orchestrate/<session>/phase-receipts/phase-5e-debug-{timestamp}.json` + per-error debug reports |

### Phase 5e Loop

```
errors_active = parse_validator_errors(.orchestrate/<session>/stage-5/validation-report.md)

# HUMAN GATE — debug entry (HUMAN-GATE-001 #5)
# Required before the debugger runs, so the human can redirect rather than auto-debug.
gate_result = run_gate(
  gate_id = "debug-entry",
  recommended_verdict = "approved",  # auto-eval recommends entering debug
  evaluator_breakdown = {
    stage_5_fix_iterations_exhausted: 3,
    remaining_error_count: len(errors_active),
    error_categories_seen: <distinct categories from errors_active>,
    phase_5e_entries_so_far: checkpoint.phase_5e_entry_count,
    max_phase_5e_entries: max_phase_5e_entries_per_session
  },
  artifact_path = ".orchestrate/<session>/stage-5/validation-report.md",
  summary = "Stage 5 validation failed after 3 fix iterations. {len(errors_active)} errors remain. Recommended: enter Phase 5e debug sub-loop. Approval options: approve to debug, reject to redirect (e.g. ask researcher), stop to terminate."
)

IF gate_result == "REJECTED":
    Log: "[PHASE 5e] User REJECTED debug entry; feedback: {approval.feedback}"
    # User rejected — re-enter Stage 3 with their feedback as guidance instead of debug
    Append to checkpoint.phase_transitions:
      { from_phase: "Stage 5", to_phase: "Stage 3", reason: "user_rejected_debug_entry" }
    Re-spawn software-engineer with feedback as failure context. Skip debug sub-loop.
    RETURN

IF gate_result == "STOP":
    Log: "[PHASE 5e] User requested stop at debug entry"
    Set checkpoint.terminal_state = "gate_rejected"
    RETURN

IF gate_result == "TIMEOUT":
    Set checkpoint.terminal_state = "gate_timeout"
    RETURN

# gate_result == "APPROVED" → run debug sub-loop
debug_iteration = 0
checkpoint.phase_5e_entry_count += 1

WHILE errors_active is non-empty AND debug_iteration < max_debug_iterations:
    debug_iteration += 1
    Log: "[PHASE 5e] Debug iteration {debug_iteration}/{max_debug_iterations}"

    # Spawn debugger with current error context
    Spawn debugger agent with PHASE: DEBUG, errors=errors_active.
    Debugger runs triage-research-fix-verify cycle:
      1. Triage: classify error (docker, infra, code, dependency, etc.)
      2. Research: identify root cause; consult researcher findings if architectural
      3. Fix: apply minimal fix
      4. Verify: re-run validator on the affected scope

    Compute error fingerprints (exception_type + normalized_message + source_file).
    Update errors_active: remove fingerprints that verified clean.

    # Thrashing detection
    IF state_hash_window detects oscillation:
        Log: "[PHASE 5e] Thrashing detected; halting debug sub-loop"
        BREAK

    # Diminishing returns
    IF errors_resolved_per_iteration < 1 for 3 consecutive iterations:
        Log: "[PHASE 5e] Diminishing returns; halting debug sub-loop"
        BREAK

    # Architectural escalation as internal phase jump (no cross-command escalation)
    IF debugger.category IN ["missing_feature", "design_flaw", "spec_mismatch", "dependency_issue"]:
        Log: "[PHASE 5e] Architectural error — internal phase jump to Phase 2 (Scope) for re-spec"
        Append to checkpoint.phase_transitions: { from_phase: "Phase 5e", to_phase: "Phase 2", reason: "architectural_error" }
        Re-enter Phase 2 inline; on return, re-validate.

IF errors_active is empty:
    verdict = "RESOLVED"
    Re-enter Stage 5 with applied fixes; if Stage 5 passes, advance to Stage 6.
ELSE IF debug_iteration >= max_debug_iterations:
    verdict = "EXHAUSTED"
    Set terminal_state = "debug_loop_exhausted" (see Step 5).

Write phase receipt with verdict, debug_iteration, errors_active.
```

## Phase 5q — Quality (absorbed from former /qa)

| Field | Value |
|-------|-------|
| **Phase ID** | 5q |
| **Owner Agent** | `qa-engineer` |
| **Trigger** | Stage 3 completes (test strategy needed); or P-032..P-037 flagged HIGH/CRITICAL |
| **Output** | `.orchestrate/<session>/phase-receipts/phase-5q-quality-{timestamp}.json` |
| **Process Range** | P-032..P-037 (Quality Assurance & Testing) |

The qa-engineer agent reviews implementation artifacts against P-032..P-037 (test architecture, automated frameworks, regression coverage, performance testing, DoD enforcement). Findings inject into Stage 4 (test) and Stage 5 (validation) work via `phase_findings`.

## Phase 5s — Security (absorbed from former /security)

| Field | Value |
|-------|-------|
| **Phase ID** | 5s |
| **Owner Agent** | `security-engineer` |
| **Trigger** | Stage 0/2/3 receipt mentions security threats; or P-038..P-043 flagged HIGH/CRITICAL |
| **Output** | `.orchestrate/<session>/phase-receipts/phase-5s-security-{timestamp}.json` |
| **Process Range** | P-038..P-043 (Security & Compliance) |

The security-engineer agent runs threat modeling (P-038), SAST/DAST review (P-039), CVE triage (P-040), AppSec scope review (P-012/P-041), compliance assessment (P-042), and incident analysis (P-043). Findings inject into Stage 2 (specs MUST address security requirements), Stage 3 (implementation MUST honor constraints), and Stage 5 (validation MUST verify security acceptance criteria).

## Phase 5i — Infra/SRE (absorbed from former /infra)

| Field | Value |
|-------|-------|
| **Phase ID** | 5i |
| **Owner Agent** | `infra-engineer`, `sre` (depending on sub-process) |
| **Trigger** | Stage 5 fails with deploy/infra keywords; or scope flags `infra`; or P-044..P-048 / P-054..P-057 flagged HIGH/CRITICAL |
| **Output** | `.orchestrate/<session>/phase-receipts/phase-5i-infra-{timestamp}.json` |
| **Process Range** | P-044..P-048 (Infrastructure & Platform), P-054..P-057 (SRE & Operations) |

The infra-engineer agent covers golden path adoption (P-044), cloud infrastructure provisioning (P-045), environment self-service (P-046), CARB review (P-047), CI/CD pipelines (P-048). The sre agent (invoked when `triage.mode == "post_launch"` or for SRE sub-processes) covers SLO monitoring (P-054), incident response (P-055), post-mortems (P-056), on-call (P-057). Findings inject into Stage 3 (infra requirements), Phase 7 (release prep), and Phase 8 (post-launch).

## Phase 5d — Data/ML (absorbed from former /data-ml-ops)

| Field | Value |
|-------|-------|
| **Phase ID** | 5d |
| **Owner Agent** | `data-engineer`, `ml-engineer` (depending on sub-process) |
| **Trigger** | Scope flags `data_ml`; or P-049..P-053 flagged HIGH/CRITICAL |
| **Output** | `.orchestrate/<session>/phase-receipts/phase-5d-data-ml-{timestamp}.json` |
| **Process Range** | P-049..P-053 (Data & ML Operations) |

The data-engineer agent covers data pipeline construction (P-049), schema migration (P-050). The ml-engineer agent covers experiment logging (P-051), model training & deployment (P-052), canary deployment (P-053). Findings inject into Stage 2 (data/ML specs), Stage 3 (pipeline implementation), and Stage 5 (validation).

## Phase 9 — Continuous Governance (absorbed from former /org-ops and /risk)

| Field | Value |
|-------|-------|
| **Phase ID** | 9 |
| **Owner Agents** | `engineering-manager`, `technical-program-manager`, `staff-principal-engineer`, `product-manager`, `infra-engineer`, `technical-writer` (per sub-process) |
| **Trigger** | (1) `tech_debt_score > 30%` OR `duplication_ratio > 0.15` from Stage 4.5 codebase-stats; OR (2) CRITICAL RAID items present in `raid-log.json` or `codebase-analysis.jsonl`; OR (3) iteration boundary reached for L/XL t-shirt-sized projects (cadenced governance) |
| **Output** | `.orchestrate/<session>/phase-receipts/phase-9-governance-{subprocess}-{timestamp}.json` |
| **Process Range** | P-062..P-069 (Organizational Hierarchy Audit), P-074..P-077 (Risk & Change Management), P-078..P-081 (Communication & Alignment), P-082..P-084 (Capacity & Resource Mgmt), P-085..P-089 (Technical Excellence & Standards), P-090..P-093 (Onboarding & Knowledge Transfer) |

Phase 9 sub-routines are invoked based on the trigger condition:

| Sub-routine | Triggered by | Owner |
|-------------|--------------|-------|
| **Audit hierarchy** (P-062..P-069) | tech_debt > 30% OR duplication > 15% | `engineering-manager` |
| **Risk management** (P-074..P-077) | CRITICAL RAID items present | `technical-program-manager` (CAB review for HIGH-risk changes) |
| **Communication & Alignment** (P-078..P-081) | OKR cadence boundary | `product-manager` (OKR cascade), `engineering-manager` (DORA metrics) |
| **Capacity & Resource Mgmt** (P-082..P-084) | Sprint cadence boundary | `technical-program-manager` (capacity planning) |
| **Technical Excellence** (P-085..P-089) | RFC/architecture review needed; tech-debt ≥ threshold | `staff-principal-engineer` (RFCs P-085, architecture patterns P-088), `infra-engineer` (tech debt P-086, DX survey P-089) |
| **Onboarding & Knowledge Transfer** (P-090..P-093) | New team member or significant artifact change | `technical-writer` (knowledge transfer P-092) |

All Phase 9 sub-routines append to the shared `raid-log.json` per RAID-001 — they never overwrite.

## Configuration Defaults

| Parameter | Default | Description |
|-----------|---------|-------------|
| `MAX_ITERATIONS` | 100 | Hard cap on orchestrator spawns |
| `STALL_THRESHOLD` | 2 | Consecutive no-progress iterations before fail |
| `CHECKPOINT_DIR` | `.orchestrate/<session-id>/` | Primary checkpoint directory (project-local) |
| `SESSION_DIR` | `~/.claude/sessions` | Legacy fallback (read-only) |
| `SCOPE` | `custom` | Stack scope: `frontend`, `backend`, `fullstack`, or `custom` |
| `gate_poll_interval_seconds` | 30 | HUMAN-GATE-001 polling cadence — how often the loop controller checks for `gate-approval-*.json` files |
| `gate_timeout_seconds` | 86400 (24h) | HUMAN-GATE-001 timeout — max wait at any single gate before terminating with `gate_timeout` |
| `skip_human_gates` | false | If true, the auto-eval `recommended_verdict` is treated as approved automatically. **Use only for CI/automation contexts.** Sets `gate-state.json` `evaluator: "auto-skip"` for audit trail. |
| `compliance_threshold` | 90 | Phase 5v compliance score (weighted MUST/SHOULD/MAY) at or above which the audit recommends APPROVED |
| `max_audit_cycles` | 5 | Phase 5v cap on audit-remediate cycles per session |
| `max_debug_iterations` | 50 | Phase 5e cap on debug iterations per session |
| `max_phase_5e_entries_per_session` | 2 | Phase 5e cap on debug-loop entries (matches REGRESS-002) |

## Cross-Platform Output Format

All pipeline output (progress lines, task boards, gate statuses, stage summaries) MUST adhere to these format rules to ensure consistent rendering across Terminal, Claude Desktop, and VS Code extension.

### OUTPUT-001: Primary Format

Plain Markdown tables are the PRIMARY format for task boards, stage progress, and gate status displays. Markdown renders correctly in all three platforms.

### OUTPUT-002: Banner Format

ASCII bracket-prefix format for banners and progress lines. Use these prefixes:
- `[PLANNING]` -- P-series stage progress
- `[GATE]` -- Gate check results
- `[STAGE P1]` through `[STAGE P4]` -- Planning stage identification
- `[STAGE 0]` through `[STAGE 6]` -- Execution stage identification (existing)
- `[PRE-RESEARCH-GATE]` -- Planning-to-execution transition
- `[PLAN-GATE-NNN]` -- Planning gate error codes
- `[PLAN-SKIP]` -- Planning phase skipped
- `[PLAN-REUSE]` -- Planning artifacts reused from prior session

### OUTPUT-003: No ANSI in Artifacts

ANSI escape codes MUST NOT appear in stored artifacts (any file under `.orchestrate/` or `.domain/`). ANSI coloring is permitted ONLY for live TTY output. Always provide a plain-text fallback. Rationale: Claude Desktop and VS Code extension render Markdown but not ANSI escape codes.

### OUTPUT-004: Unicode Policy

Unicode box-drawing characters (e.g., the task board in Step 3c) are acceptable in live terminal output and documentation. They MUST NOT appear in structured output fields (JSON values in checkpoint, stage-receipt, or proposed-tasks files).

### OUTPUT-005: Progress Line Format

P-series progress lines follow this exact format:

**Stage start**:
```
[P1:PLANNING] Intent Frame -- product-manager -- P-001
```
Format: `[<stage>:PLANNING] <name> -- <agent> -- <process_ids>`

**Stage completion**:
```
[P1:PASSED] Intent Review gate passed -- Intent Brief produced
```
Format: `[<stage>:PASSED] <gate_name> gate passed -- <artifact_name> produced`

**Stage failure**:
```
[P1:FAILED] Intent Review gate failed -- missing: Boundaries, Cost of Inaction
```
Format: `[<stage>:FAILED] <gate_name> gate failed -- missing: <sections>`

### Planning Phase Task Board

During the planning phase, the task board (DISPLAY-001) shows planning stages instead of execution stages:

```
 PLANNING PHASE TASK BOARD:
 +----- P1 (Intent Frame) ---------------------------------
 |  [done] Intent Brief produced -- product-manager
 |  [done] Intent Review: PASSED
 +----- P2 (Scope Contract) --------------------------------
 |  >> Scope Contract in progress -- product-manager
 |  .. Scope Lock: PENDING
 +----- P3 (Dependency Map) --------------------------------
 |  [blocked] Dependency Charter -- technical-program-manager  [blocked by P2]
 |  .. Dependency Acceptance: PENDING
 +----- P4 (Sprint Bridge) ---------------------------------
 |  [blocked] Sprint Kickoff Brief -- engineering-manager      [blocked by P3]
 |  .. Sprint Readiness: PENDING
 +----------------------------------------------------------
 Legend: [done] passed  >> in progress  [blocked] blocked  .. pending
```

### Markdown Table Format for Gate Status

At each iteration, the planning phase status is shown as a Markdown table when relevant:

| Stage | Gate | Status | Artifact |
|-------|------|--------|----------|
| P1: Intent Frame | Intent Review | PASSED | P1-intent-brief.md |
| P2: Scope Contract | Scope Lock | PASSED | P2-scope-contract.md |
| P3: Dependency Map | Dependency Acceptance | PASSED | P3-dependency-charter.md |
| P4: Sprint Bridge | Sprint Readiness | PASSED | P4-sprint-kickoff-brief.md |

---

## Step 0: Autonomous Mode Declaration

### 0-pre. Continue Shorthand

If `task_description` is `"c"` (case-insensitive): treat as `resume: true`, skip Steps 0a and 1, jump to Step 2b. If no in-progress session found, abort.

### 0a. Permission Grant

Display once:

> **Autonomous mode requested.** This will:
> - Create/update files in `.orchestrate/<session-id>/` and `~/.claude/plans/`
> - Spawn orchestrator and subagents without further prompts
> - Make reasonable assumptions instead of asking clarifying questions
> - Run up to {{MAX_ITERATIONS}} orchestrator iterations
>
> **Proceed autonomously?** (Y/n)

If declined, abort: `"Auto-orchestration cancelled. Use /workflow-plan for interactive planning."`

Record in checkpoint: `"permissions": { "autonomous_operation": true, "session_folder_access": true, "no_clarifying_questions": true, "granted_at": "<ISO-8601>" }`

### 0b. Inline Processing Rule

Step 1 runs INLINE. Do NOT delegate to `workflow-plan` or use `EnterPlanMode`.

### 0c. Human-Input Treatment

Command arguments are **human-authored input**: preserve context, don't reinterpret meaning, document assumptions when resolving ambiguity.

### 0d. Scope Resolution

| Flag | Resolved | Layers |
|------|----------|--------|
| `F`/`f` | `frontend` | `["frontend"]` |
| `B`/`b` | `backend` | `["backend"]` |
| `S`/`s` | `fullstack` | `["backend", "frontend"]` |
| *(omitted)* | `custom` | `[]` |

**Preprocessing**: Strip surrounding quotes recursively, then trim whitespace.

**Inline flag extraction** (when `scope` not provided separately): If the first non-whitespace token is **exactly one character** matching `F/f/B/b/S/s` followed by space or end-of-string, extract as scope flag. Multi-character tokens (e.g., "fix") are NEVER flags.

**Default objectives** (when only a flag is provided):

| Scope | Default |
|-------|---------|
| `backend` | Build or complete all backend features to production-ready state, then audit and fully integrate — real implementations, proper persistence, zero placeholders |
| `frontend` | Build or complete all frontend features to production-ready state, then audit and fully integrate — every UI page, form, and API integration with child-friendly usability |
| `fullstack` | Build or complete all features across backend and frontend to production-ready state — full stack, zero placeholders, production-ready end-to-end |

Record: `"scope": { "flag": "<letter>", "resolved": "<scope>", "layers": [...] }`

### 0d-bis. Research Depth Flag Extraction (RESEARCH-DEPTH-001 explicit path)

Extract and validate the `--research-depth` argument BEFORE Step 0h-pre resolution, so the resolution block can consume it via its `explicit` precedence path.

**Extraction**:
```
raw = command_args.get("research_depth") OR None

# Also accept --research-depth=<value> inline in task_description for convenience:
IF raw is None:
    match = regex_match(r"--research-depth(?:=|\s+)(\w+)", task_description)
    IF match:
        raw = match.group(1)
        task_description = task_description_with_flag_stripped  # remove from objective
        Log: "[RESEARCH-DEPTH-FLAG] Extracted --research-depth from task_description"
```

**Validation**:
```
VALID_TIERS = {"minimal", "normal", "deep", "exhaustive"}

IF raw is None:
    # No explicit override — resolution falls through to triage default in Step 0h-pre
    explicit_research_depth = None
    Log: "[RESEARCH-DEPTH] No explicit override; will resolve from triage."

ELSE IF raw.lower() in VALID_TIERS:
    explicit_research_depth = raw.lower()
    Log: "[RESEARCH-DEPTH] Explicit override: {explicit_research_depth}"

ELSE:
    explicit_research_depth = None
    Log: "[RESEARCH-DEPTH-WARN] Invalid tier '{raw}' — expected one of {VALID_TIERS}. Falling back to triage default."
```

**Store for Step 0h-pre consumption**: Write `command_args.research_depth = explicit_research_depth`. The RESEARCH-DEPTH-001 resolution block (Step 0h-pre) reads this as its highest-priority source:
```
IF command_args.research_depth is not None:
    research_depth.tier = command_args.research_depth
    research_depth.source = "explicit"
```

**Case-insensitive**: Accept any case (`DEEP`, `Deep`, `deep` all map to `deep`). Invalid values do NOT abort the session — they just log a warning and fall through to triage default, preserving the user's ability to run the pipeline even with a typo.

### 0e. Manifest Validation

Verify that `~/.claude/manifest.json` exists and contains the `orchestrator` agent definition:

```bash
test -f ~/.claude/manifest.json && grep -q '"orchestrator"' ~/.claude/manifest.json && echo "PASS" || echo "FAIL"
```

If FAIL: abort with `[AO-GAP-002] Manifest missing or orchestrator agent not found at ~/.claude/manifest.json. Cannot proceed.`

### 0f. Domain Memory and Shared State Initialization

Ensure the `.domain/` and `.pipeline-state/` directories exist at the project root:

```bash
mkdir -p .domain
mkdir -p .pipeline-state .pipeline-state/command-receipts .pipeline-state/process-log .pipeline-state/workflow
```

**`.domain/`** persists **cross-session, cross-command** domain knowledge (research findings, error→fix mappings, patterns, architecture decisions, codebase analysis, user preferences). All stores are append-only JSONL with file locking for concurrency safety. Pass `DOMAIN_MEMORY_DIR=.domain` in the orchestrator spawn prompt.

**`.pipeline-state/`** enables **cross-pipeline knowledge transfer** between auto-orchestrate, auto-audit, and auto-debug. See `_shared/protocols/cross-pipeline-state.md` for the full protocol.

**On startup**, read shared state (SHARED-001):
1. Read `.pipeline-state/escalation-log.jsonl` — consume unconsumed escalations from auto-debug (mark as `consumed: true`)
2. Read `.pipeline-state/research-cache.jsonl` — cache entries for SHARED-003 lookup before Stage 0 researcher spawn
3. Read `.pipeline-state/codebase-analysis.jsonl` — pass high-severity insights to researcher prompt
4. Read `.pipeline-state/fix-registry.jsonl` — available as context for debugging regressions during validation
5. Read `.pipeline-state/pipeline-context.json` — log if another pipeline was recently active
6. Pass `PIPELINE_STATE_DIR=.pipeline-state` in the orchestrator spawn prompt
7. Read `.pipeline-state/command-receipts/` (STATE-002) — scan for receipts from prior auto-orchestrate sessions. Receipts predating this session's `created_at` are **context** (logged, not acted upon). Receipts from within the current session or with `phase_context.invoked_by` matching this session are **actionable** (injected into relevant phase context).
8. Read `.pipeline-state/workflow/active-session.json` — if a workflow session is active, log task state summary for awareness
7. Write `.pipeline-state/workflow/active-session.json` with `session_state: "active"`, `source: "auto-orchestrate"`, `session_id: <session_id>`, `started_at: <now>`. This signals WORKFLOW-SYNC-002 (read-only mode for workflow-* commands).
8. Initialize `.pipeline-state/workflow/task-board.json` with empty task list: `{ "schema_version": "1.0.0", "source": "auto-orchestrate", "session_id": <session_id>, "last_updated": <now>, "iteration": 0, "pipeline_stage": null, "tasks": [], "stages_completed": [], "terminal_state": null }`
7. Store `last_receipt_scan` timestamp in checkpoint for incremental scanning at stage transitions

**At each stage transition (Step 4.8c)**: Before evaluating phase transitions, re-scan `.pipeline-state/command-receipts/` for receipts written since `last_receipt_scan` (STATE-002). This catches receipts from prior auto-orchestrate sessions in the same project. Update `last_receipt_scan`. For each new actionable receipt: if it has findings with severity HIGH or CRITICAL, treat as equivalent to a domain phase transition condition (e.g., security findings → Phase 5s).

**On termination**:
- Update `.pipeline-state/pipeline-context.json` with final session state
- Write receipt to `.pipeline-state/command-receipts/auto-orchestrate-<YYYYMMDD>-<HHMMSS>.json` (STATE-001) with: `inputs: { "task_description", "scope" }`, `outputs: { "terminal_state", "stages_completed": [], "tasks_total", "tasks_completed" }`, `processes_executed` aggregated from all stage receipts, `next_recommended_action`: `"release-prep"` if completed, `"auto-debug"` if failed with errors, `null` otherwise
- Write process log entries for all processes executed across stages (STATE-003) to `.pipeline-state/process-log/<process-id>.jsonl`
- Update `.pipeline-state/workflow/active-session.json` with `session_state: "ended"`, `ended_at: <now>`, final `tasks_completed` and `task_count` tallies
- Write final `.pipeline-state/workflow/task-board.json` with `terminal_state` set and all task statuses finalized (WORKFLOW-SYNC-001). This releases the read-only lock for workflow-* commands.

> **Process coverage reference**: Auto-orchestrate covers ALL 93 organizational processes via internal phases — Phases 1-4 cover P-001..P-031, Phases 5q/5s/5i/5d cover P-032..P-053, Phase 6 covers P-058..P-061, Phase 7 covers release processes (P-035, P-044-048, P-059, P-061, P-076), Phase 8 covers P-070..P-073 (and P-054..P-057 ongoing), Phase 9 covers P-062..P-093. See `processes/process_injection_map.md` for the per-stage process injection table.

### 0g. Project Type Detection

Classify the target project as `greenfield`, `existing`, or `continuation` to adapt pipeline behavior. Detection uses metadata operations only (git history, file counts, file existence) — no source file reading (preserves Execution Guard).

**Detection Signals**:

```bash
# SIGNAL 1: Git History Depth
COMMIT_COUNT=$(git rev-list HEAD --count 2>/dev/null || echo "0")

# SIGNAL 2: Source File Count
SOURCE_FILE_COUNT=$(find . -maxdepth 3 -type f \( -name "*.py" -o -name "*.ts" -o -name "*.js" -o -name "*.go" -o -name "*.rs" -o -name "*.java" -o -name "*.rb" \) | wc -l)

# SIGNAL 3: Handoff Receipt Presence
HANDOFF_PRESENT=$(test -f .orchestrate/${SESSION_ID}/handoff-receipt.json && echo "present" || echo "absent")

# SIGNAL 4: Prior Orchestration History
PRIOR_SESSION_COUNT=$(ls -d .orchestrate/auto-orc-*/checkpoint.json 2>/dev/null | wc -l)
```

**Classification Logic**:

```
IF PRIOR_SESSION_COUNT > 0 AND any prior session has status "in_progress" or "superseded":
  project_type = "continuation"
ELSE IF COMMIT_COUNT < 5 AND SOURCE_FILE_COUNT < 10:
  project_type = "greenfield"
ELSE:
  project_type = "existing"
```

**Store in checkpoint**:

```json
{
  "project_type": "greenfield|existing|continuation",
  "project_detection": {
    "commit_count": 0,
    "source_file_count": 0,
    "handoff_present": false,
    "prior_session_count": 0,
    "detected_at": "<ISO-8601>"
  }
}
```

**Pass to orchestrator spawn prompt**: Add `PROJECT_TYPE: <type>` in the spawn prompt context.

**Inject into enhanced prompt**:

| Project Type | Context Injected |
|-------------|------------------|
| `greenfield` | `**Project Type**: Greenfield. This is a new project requiring scaffolding, architecture decisions, dependency selection, and initial project structure. The researcher (Stage 0) should prioritize: technology selection, project scaffolding patterns, dependency evaluation. The product-manager (Stage 1) should include scaffolding tasks.` |
| `existing` | `**Project Type**: Existing codebase. This project has established patterns, existing dependencies, and production code. The researcher (Stage 0) should prioritize: codebase analysis, change impact assessment, existing pattern identification. The product-manager (Stage 1) should include regression risk analysis.` |
| `continuation` | `**Project Type**: Continuation of prior orchestration session. Previous session context is available in .orchestrate/. The researcher (Stage 0) should check prior research output and build incrementally.` |

**Detection MUST NOT read project source files** — only metadata (git log, file counts, file existence). Source file reading is the researcher's job (Stage 0).

Log: `[DETECT] Project type: <classification> (commits: <N>, source files: <N>, prior sessions: <N>)`

### 0h-pre. Complexity Triage Gate (TRIAGE-001)

Before entering the planning phase, classify the task complexity to determine whether full P1-P4 planning is warranted.

**Triage signals** (from user input text only — no file reading):

| Signal | Trivial | Medium | Complex |
|--------|---------|--------|---------|
| Word count of task_description | < 20 words | 20-100 words | > 100 words |
| Explicit scope flag | No flag (custom) | Single flag (F/B) | Fullstack (S) |
| Keywords: "fix", "typo", "config", "bump" | Present | — | — |
| Keywords: "build", "implement", "create", "redesign" | — | — | Present |
| Keywords: "refactor", "update", "add", "improve" | — | Present | — |
| Multiple deliverables mentioned | No | 1-2 | 3+ |
| `project_type` (from Step 0g) | Any | existing | greenfield |

**Classification logic**:
```
trivial_signals = count of Trivial column matches
complex_signals = count of Complex column matches

IF trivial_signals >= 3 AND complex_signals == 0:
    complexity = "trivial"
ELSE IF complex_signals >= 2 OR scope == "fullstack":
    complexity = "complex"
ELSE:
    complexity = "medium"
```

**Triage routing**:

| Complexity | Planning | Pipeline |
|-----------|----------|----------|
| `trivial` | **SKIP** P1-P4 (auto-set `planning_skipped: true`) | Full pipeline (Stage 0-6) unless `fast_path: true` |
| `medium` | **SKIP** P1-P4 (auto-set `planning_skipped: true`) | Full pipeline (Stage 0-6) |
| `complex` | **REQUIRE** P1-P4 (proceed to Step 0h) | Full pipeline (Stage 0-6) |

**Override**: The `--skip-planning` flag always wins. The triage gate only applies when `skip_planning` is not explicitly set.

**Process scope classification (PROCESS-SCOPE-001)**:

After determining complexity, classify the process scope. This determines which injection hooks from the expanded process injection map (`processes/process_injection_map.md`) are active for this session.

**Domain flag detection** (from user input text only — same constraint as triage signals):

| Domain Flag | Detection Keywords |
|-------------|-------------------|
| `infra` | "deploy", "infrastructure", "kubernetes", "k8s", "docker", "CI/CD", "pipeline", "terraform", "cloud" |
| `data_ml` | "data pipeline", "ETL", "ML", "model", "training", "dataset", "schema migration", "dbt", "streaming" |
| `sre` | "SLO", "incident", "monitoring", "on-call", "reliability", "observability", "alerting" |
| `risk` | "risk", "compliance", "regulatory", "audit", "RAID" |

```
domain_flags = []
FOR EACH (flag, keywords) IN DOMAIN_FLAG_TABLE:
    IF any keyword IN lowercase(task_description + scope_specification):
        domain_flags.append(flag)

# Process scope tier follows complexity tier
process_scope_tier = complexity  # trivial, medium, or complex

# Active processes determined by tier
IF process_scope_tier == "trivial":
    active_processes = ["P-001", "P-007", "P-033", "P-034"]
    active_categories = [1, 2, 5]
    active_phases = []
ELSE IF process_scope_tier == "medium":
    active_processes = CORE_PROCESSES + MEDIUM_PROCESSES  # ~27 processes
    active_categories = [1, 2, 5, 6, 10]
    active_phases = ["5s", "5q"]
ELSE:  # complex
    active_processes = CORE + MEDIUM + COMPLEX_PROCESSES  # base ~42
    active_categories = [1, 2, 3, 5, 6, 10, 12, 13, 16]
    active_phases = ["5s", "5q", "9"]
    # Add domain-conditional categories
    IF "infra" IN domain_flags:
        active_categories += [7]
        active_phases += ["5i"]
        active_processes += INFRA_PROCESSES  # P-044-048
    IF "data_ml" IN domain_flags:
        active_categories += [8]
        active_phases += ["5d"]
        active_processes += DATA_ML_PROCESSES  # P-049-053
    IF "sre" IN domain_flags:
        active_categories += [9]
        active_processes += SRE_PROCESSES  # P-054-057
    IF "risk" IN domain_flags:
        active_processes += RISK_PROCESSES  # P-074-077 (already in domain_guides)
```

**Enforcement override computation (ENFORCE-UPGRADE-001)**:

After computing process scope, determine which process hooks should be upgraded to GATE enforcement based on triage complexity:

```
IF complexity == "trivial":
    enforcement_overrides = {}  # all hooks use default enforcement_tier

ELSE IF complexity == "medium":
    enforcement_overrides = {
        "P-034": "GATE",  # Code Review
        "P-036": "GATE",  # Security Review
        "P-038": "GATE",  # Security by Design
        "P-039": "GATE"   # SAST/DAST
    }

ELSE IF complexity == "complex":
    enforcement_overrides = {
        "P-034": "GATE",  # Code Review
        "P-035": "GATE",  # Performance Testing
        "P-036": "GATE",  # Security Review
        "P-037": "GATE",  # Automated Testing
        "P-038": "GATE",  # Security by Design
        "P-039": "GATE"   # SAST/DAST
    }
```

Store in `checkpoint.triage.enforcement_overrides`. At runtime, effective enforcement tier = `enforcement_overrides.get(process_id, hook.default_tier)`.

Log: `[ENFORCE-UPGRADE] Complexity: <complexity>. GATE-enforced processes: <list of overridden process IDs>.`

**Checkpoint addition**:
```json
{
  "triage": {
    "complexity": "trivial|medium|complex",
    "signals": { "trivial": 0, "medium": 0, "complex": 0 },
    "planning_skipped_by_triage": false,
    "classified_at": "<ISO-8601>",
    "tshirt_size": "XS|S|M|L|XL",
    "files_touched_estimate": 0,
    "risk_score": 1,
    "cross_team_impact": [],
    "process_scope": {
      "tier": "trivial|medium|complex",
      "domain_flags": [],
      "active_categories": [],
      "domain_guides_enabled": [],
      "total_active": 0
    },
    "enforcement_overrides": {}
  }
}
```

**Derived triage fields** (computed after classification):

```
tshirt_size:
  trivial + signals.trivial >= 3  → "XS"
  trivial + signals.trivial < 3   → "S"
  medium                          → "M"
  complex + signals.complex < 5   → "L"
  complex + signals.complex >= 5  → "XL"

files_touched_estimate:
  IF scope == "frontend" OR "backend": word_count / 20 (capped at 30)
  IF scope == "fullstack": word_count / 15 (capped at 50)
  IF scope == "custom" OR none: word_count / 25 (capped at 20)
  Minimum: 1

risk_score (1-5):
  base = 1
  + complexity_ordinal (trivial=0, medium=1, complex=2)
  + 1 IF domain_flags contains "security" OR "risk"
  + 1 IF length(domain_flags) > 2
  Capped at 5

cross_team_impact:
  Copy of active domain_flags keys (e.g., ["security", "infra", "qa"])
```

Log: `[TRIAGE] Complexity: <classification> | T-shirt: <tshirt_size> | Risk: <risk_score>/5 (trivial: <N>, medium: <N>, complex: <N> signals). Planning: <SKIP|REQUIRE>.`
Log: `[PROCESS-SCOPE] Tier: <tier>. Domain flags: <flags>. Active categories: <N>. Domain guides: <guides>. Total processes: <count>.`

**Research Depth Resolution (RESEARCH-DEPTH-001)**:

After triage classification and process scope are computed, resolve the research depth tier for Stage 0 (and planning P1/P2 research). Depth controls the researcher agent's query budget, synthesis breadth, and output contract.

**Tier definitions** (authoritative):

| Tier | Intent | Typical use |
|------|--------|-------------|
| `minimal` | Cache-first, CVE check only, single-page output | Trivial tasks, fast-path |
| `normal` | Current default — 3+ WebSearch queries, full RES-* contract | Medium tasks |
| `deep` | 10+ queries, multi-topic, cross-reference 2+ sources per HIGH finding | Complex tasks |
| `exhaustive` | Domain-partitioned sub-research (security/perf/ops/UX), parallel findings | Regulated/high-risk work, opt-in only |

**Precedence order** (first match wins):

```
# 1. Explicit CLI flag (highest precedence)
# Populated by Step 0d-bis after validation (invalid values already fell through to None there)
IF command_args.research_depth is not None:
    research_depth.tier = command_args.research_depth
    research_depth.source = "explicit"

# 2. Handoff receipt pre-configuration
ELSE IF handoff_receipt is present AND handoff_receipt.research_depth is non-empty:
    research_depth.tier = handoff_receipt.research_depth
    research_depth.source = "handoff"

# 3. Triage-derived default
ELSE IF checkpoint.triage is not null:
    IF checkpoint.triage.complexity == "trivial":
        base_tier = "minimal"
    ELSE IF checkpoint.triage.complexity == "medium":
        base_tier = "normal"
    ELSE IF checkpoint.triage.complexity == "complex":
        base_tier = "deep"

    # 3a. Domain escalation — bump up one tier for security/risk/regulated work
    escalated_by = []
    IF "security" in checkpoint.triage.process_scope.domain_flags OR "risk" in checkpoint.triage.process_scope.domain_flags:
        base_tier = bump_up(base_tier)    # minimal→normal, normal→deep, deep→exhaustive, exhaustive→exhaustive (capped)
        escalated_by = [flag for flag in ("security", "risk") if flag in checkpoint.triage.process_scope.domain_flags]

    research_depth.tier = base_tier
    research_depth.source = "escalated" IF escalated_by else "triage-default"
    research_depth.escalated_by = escalated_by

# 4. Fallback — preserves pre-RESEARCH-DEPTH-001 behavior
ELSE:
    research_depth.tier = "normal"
    research_depth.source = "fallback"

research_depth.resolved_at = now_iso8601()
```

**Bump-up table** (domain escalation):

| Base tier | After escalation |
|-----------|------------------|
| `minimal` | `normal` |
| `normal` | `deep` |
| `deep` | `exhaustive` |
| `exhaustive` | `exhaustive` (capped — no higher tier exists) |

**Validation** (when source is `explicit` or `handoff`):
- Tier MUST be one of `minimal`, `normal`, `deep`, `exhaustive`
- If invalid: fall through to triage default and log `[RESEARCH-DEPTH-WARN] Invalid depth "<value>" from <source> — falling back to triage default`

**Store in checkpoint**:
```json
{
  "research_depth": {
    "tier": "minimal|normal|deep|exhaustive",
    "source": "explicit|handoff|triage-default|escalated|fallback",
    "escalated_by": [],
    "resolved_at": "<ISO-8601>"
  }
}
```

Log (exactly once at resolution): `[RESEARCH-DEPTH] Depth: <tier> | Source: <source> | Triage: <complexity> | Domain flags: <flags> | Escalated by: <escalated_by or "none">`

> **Scope unification**: The resolved `research_depth.tier` is the SAME tier used for P1/P2 planning research (Step 0h) AND Stage 0 execution research. A complex greenfield project thus gets `deep` research consistently across planning and execution. See Step 0h "P1 and P2 Research Sub-Step" for the planning consumer and Appendix C for the Stage 0 consumer.

> **Fast-path interaction**: When `fast_path: true` AND tier resolves to `minimal`, the Stage 0 researcher in Step 2a MAY satisfy RES-008 via cache hit alone (SHARED-003). For all other tiers, RES-008 binds normally — WebSearch is mandatory.

### 0h. Planning Phase Gate (PRE-RESEARCH-GATE)

Before proceeding to Step 1 (Enhance User Input) and the execution pipeline, verify that all four planning stages have been completed.

**Skip conditions** (check FIRST):

1. `--skip-planning` flag was passed as a command argument
   - Set `planning_skipped: true` in checkpoint
   - Log: `[PLAN-SKIP] --skip-planning flag set. Bypassing planning phase.`
   - Proceed directly to Step 1

2. Complexity triage (Step 0h-pre) classified task as `trivial` or `medium`:
   - Set `planning_skipped: true` and `planning_skipped_by_triage: true` in checkpoint
   - Log: `[PLAN-SKIP] Triage classified task as <complexity>. Bypassing planning phase.`
   - Proceed directly to Step 1

3. Planning artifacts already exist from a prior session or manual creation:
   - Check for existence of ALL four files:
     - `.orchestrate/<session>/planning/P1-intent-brief.md`
     - `.orchestrate/<session>/planning/P2-scope-contract.md`
     - `.orchestrate/<session>/planning/P3-dependency-charter.md`
     - `.orchestrate/<session>/planning/P4-sprint-kickoff-brief.md`
   - If ALL four exist:
     - Set `planning_skipped: true` and `planning_stages_completed: ["P1","P2","P3","P4"]`
     - Set all `planning_gate_statuses` to `"PASSED"`
     - Log: `[PLAN-REUSE] Planning artifacts found from prior session. Skipping planning phase.`
     - Proceed directly to Step 1

4. Handoff receipt from a prior auto-orchestrate session has `planning_complete: true`:
   - Set checkpoint fields as in condition 3
   - Log: `[PLAN-HANDOFF] Planning completed in prior session handoff. Skipping planning phase.`
   - Proceed directly to Step 1

**Gate enforcement** (if no skip condition met):

```
planning_complete = (
    "P1" in planning_stages_completed
    AND "P2" in planning_stages_completed
    AND "P3" in planning_stages_completed
    AND "P4" in planning_stages_completed
    AND planning_gate_statuses.P1 == "PASSED"
    AND planning_gate_statuses.P2 == "PASSED"
    AND planning_gate_statuses.P3 == "PASSED"
    AND planning_gate_statuses.P4 == "PASSED"
)

IF planning_complete:
    Log: "[PRE-RESEARCH-GATE] All planning stages complete. Proceeding to execution pipeline."
    Proceed to Step 1.

ELSE:
    # Determine which stages are incomplete and report error codes
    IF "P1" not in planning_stages_completed OR planning_gate_statuses.P1 != "PASSED":
        emit "[PLAN-GATE-001] P1 Intent Frame incomplete. Intent Brief missing or Intent Review gate not passed."
    IF "P2" not in planning_stages_completed OR planning_gate_statuses.P2 != "PASSED":
        emit "[PLAN-GATE-002] P2 Scope Contract incomplete. Scope Contract missing or Scope Lock gate not passed."
    IF "P3" not in planning_stages_completed OR planning_gate_statuses.P3 != "PASSED":
        emit "[PLAN-GATE-003] P3 Dependency Map incomplete. Dependency Charter missing or Dependency Acceptance gate not passed."
    IF "P4" not in planning_stages_completed OR planning_gate_statuses.P4 != "PASSED":
        emit "[PLAN-GATE-004] P4 Sprint Bridge incomplete. Sprint Kickoff Brief missing or Sprint Readiness gate not passed."

    # Determine next planning stage to execute
    next_planning_stage = first stage in [P1, P2, P3, P4] where status != "PASSED"
    Set current_planning_stage = next_planning_stage
    Log: "[PRE-RESEARCH-GATE] Planning incomplete. Next: Stage {next_planning_stage}."

    # Execute planning loop
    FOR each stage in [P1, P2, P3, P4] where gate_status != "PASSED":

        Log: "[P{N}:START] Executing {stage_name} -- Agent: {agent}"

        ## P1 and P2 Research Sub-Step
        IF stage is P1 OR stage is P2:
            Log: "[P{N}:RESEARCH] Spawning researcher for planning research (depth: {checkpoint.research_depth.tier})"
            # RESEARCH-DEPTH-001 unification: planning research uses the SAME resolved tier
            # as Stage 0 execution research. Planning only runs when complexity == "complex"
            # (per Step 0h-pre triage routing), so the tier will typically be `deep` or
            # `exhaustive` (if domain-escalated). Legacy sessions with null tier use `normal`.
            planning_depth = checkpoint.research_depth.tier OR "normal"
            Spawn researcher agent with prompt (pass RESEARCH_DEPTH: planning_depth):
              - P1 research: Investigate the project domain, existing codebase structure,
                stakeholder needs, competitive landscape, and technical constraints.
                Query budget and output contract are set by RESEARCH_DEPTH (see Appendix C
                researcher depth directives). Output findings that will inform the
                Intent Brief.
              - P2 research: Investigate technical feasibility, effort estimation patterns,
                dependency risks, and scope precedents. Query budget and output contract
                are set by RESEARCH_DEPTH. Output findings that will inform the Scope Contract.
            Output: .orchestrate/<session>/planning/P{N}-research.md
            Log: "[P{N}:RESEARCH-DONE] Research complete (depth: {planning_depth}) -- feeding into {stage_name}"

        ## Agent Spawn
        Spawn the stage's designated agent (via orchestrator with PHASE: HUMAN_PLANNING):
          - P1: product-manager -> produces Intent Brief
                 (receives P1-research.md as additional input)
          - P2: product-manager -> produces Scope Contract
                 (receives P1 Intent Brief + P2-research.md as input)
          - P3: technical-program-manager -> produces Dependency Charter
                 (receives P2 Scope Contract as input)
          - P4: engineering-manager -> produces Sprint Kickoff Brief
                 (receives P3 Dependency Charter + P2 Scope Contract as input)

        ## Gate Validation (auto-eval + HUMAN GATE per AUTO-EVAL-001 / HUMAN-GATE-001)
        Step A — Auto-evaluation (produces recommended_verdict):
          1. Verify the stage artifact was produced at the expected path.
          2. Run the deterministic gate criteria for this stage (see "Auto-Evaluated Gate
             Criteria" section below).
          3. Where judgment is required, spawn the gate's evaluator agent (product-manager
             for P1/P2, technical-program-manager for P3, engineering-manager for P4) with
             PHASE: GATE_EVAL to produce a PASS/FAIL verdict.
          4. Compute recommended_verdict:
             - "approved" if deterministic_criteria_pass AND evaluator_verdict == "PASS"
             - "rejected" otherwise (with structured failure reasons)

        Step B — Run human gate (HUMAN-GATE-001):
          gate_id_map = { P1: "intent-review", P2: "scope-lock",
                          P3: "dependency-acceptance", P4: "sprint-readiness" }

          gate_result = run_gate(
            gate_id = gate_id_map[stage],
            recommended_verdict = recommended_verdict,
            evaluator_breakdown = { deterministic_criteria, agent_evaluator },
            artifact_path = ".orchestrate/<session>/planning/{artifact_filename}",
            summary = <human-readable summary of artifact>
          )
          # See "Human-in-the-Loop Gates" section above for run_gate() semantics.

        Step C — Act on combined verdict:
          IF gate_result == "APPROVED":
            Set planning_gate_statuses.{gate} = "PASSED"
            Append stage to planning_stages_completed
            Set planning_artifacts.{artifact_key} = approval.artifact_edit_path OR original path
            Log: "[P{N}:PASSED] {gate_name} gate APPROVED by user (auto-eval recommended: {recommended_verdict})"
            Append to gate-state.json:
              { gate: gate_name, status: "PASSED", evaluated_at: now_iso8601(),
                evaluator: "human", recommended_verdict: recommended_verdict,
                criteria_fired: [list_of_criteria_passed],
                evaluator_verdict_source: agent_name_or_null,
                decided_by: <approval.decided_by>, feedback: <approval.feedback> }

          ELSE IF gate_result == "REJECTED":
            Log: "[P{N}:FAILED] {gate_name} gate REJECTED by user — feedback: <approval.feedback>"
            Append to gate-state.json:
              { gate: gate_name, status: "FAILED", evaluated_at: now_iso8601(),
                evaluator: "human", recommended_verdict: recommended_verdict,
                fail_reason: approval.feedback,
                decided_by: <approval.decided_by> }
            Retry up to 2 times by re-spawning the stage's owner agent with approval.feedback.
            If still rejected after 2 retries, log error and continue to next iteration.

          ELSE IF gate_result == "STOP":
            Log: "[P{N}:STOP] {gate_name} gate STOP requested by user"
            Set checkpoint.terminal_state = "gate_rejected"
            Exit the planning loop and proceed to Step 5 (termination).

          ELSE IF gate_result == "TIMEOUT":
            Log: "[P{N}:TIMEOUT] {gate_name} gate TIMED OUT after gate_timeout_seconds"
            Set checkpoint.terminal_state = "gate_timeout"
            Exit the planning loop and proceed to Step 5 (termination).

        ## Progress Display
        Display planning progress:
        ```
        [PLANNING] P1 V -> P2 V -> P3 > -> P4 o
        ```

        Write checkpoint after each planning stage completion.

    # All planning stages complete
    Log: "[PRE-RESEARCH-GATE] All planning stages complete. Proceeding to execution pipeline."

    ## Sprint Kickoff Ceremony (Phase 4 inline — absorbed from former /sprint-ceremony)
    # Auto-conducted by engineering-manager. No human pause.
    Spawn engineering-manager with PHASE: SPRINT_CEREMONY:
      - Read P4 Sprint Kickoff Brief
      - Produce kickoff-receipt.json with: sprint_goal, story_count, capacity_check,
        team_commitment_recorded
      - Output: .orchestrate/<session>/planning/sprint-kickoff-receipt.json
    Append to gate-state.json:
      { gate: "Sprint Ceremony", status: "COMPLETED", evaluated_at: now_iso8601(),
        evaluator: "auto", artifact: "sprint-kickoff-receipt.json" }

    Proceed to Step 1.
```

### Auto-Evaluated Gate Criteria

Each planning gate is evaluated by combining deterministic checks (artifact existence, schema, RAID severity counts) with an agent-evaluator verdict where judgment is required. The combined verdict becomes the **recommended_verdict** written to `gate-pending-{gate_id}.json`. Final approval comes from the user via `gate-approval-{gate_id}.json` per HUMAN-GATE-001.

| Gate | Deterministic checks | Evaluator agent | Evaluator verdict criteria |
|------|----------------------|-----------------|----------------------------|
| **Intent Review (P1)** | (1) `P1-intent-brief.md` exists; (2) ≥5 sections; (3) each section ≥50 chars; (4) Outcome contains a metric/percentage/timeline; (5) Boundaries section contains ≥1 explicit "NOT" exclusion | `product-manager` (PHASE: GATE_EVAL) | Returns `PASS` if Intent Brief is internally consistent and answers all 5 template questions substantively; `FAIL` with explicit feedback otherwise |
| **Scope Lock (P2)** | (1) `P2-scope-contract.md` exists; (2) Acceptance Criteria section non-empty; (3) Definition of Done section non-empty; (4) Success Metrics section contains ≥1 measurable metric; (5) RAID log seeded at `raid-log.json`; (6) AppSec scope review section present (P-012 acknowledgment) | `product-manager` (PHASE: GATE_EVAL) | Returns `PASS` if scope is testable, bounded, and the change-control approach is stated; `FAIL` otherwise |
| **Dependency Acceptance (P3)** | (1) `P3-dependency-charter.md` exists; (2) Cross-team dependencies enumerated; (3) Critical path identified; (4) Communication plan section present; (5) Resource conflicts section present (may be empty if none); (6) Escalation protocol stated | `technical-program-manager` (PHASE: GATE_EVAL) | Returns `PASS` if no unresolved CRITICAL dependency conflicts and critical path is realistic; `FAIL` otherwise |
| **Sprint Readiness (P4)** | (1) `P4-sprint-kickoff-brief.md` exists; (2) Sprint goal stated as a single sentence; (3) Stories enumerated with acceptance criteria; (4) Story estimates sum to within team capacity (estimate vs capacity ratio ≤ 1.0); (5) Team commitment block present | `engineering-manager` (PHASE: GATE_EVAL) | Returns `PASS` if estimates are realistic and stories are independently demoable; `FAIL` otherwise |

When the evaluator returns `FAIL`, its feedback is fed back into the next retry of the stage's owner agent (up to 2 retries). On the third failure, the gate is marked FAILED in `gate-state.json` and the session continues to the next iteration — the next iteration will re-attempt the failing stage with the latest feedback.

**Planning loop is SELF-CONTAINED** -- it does NOT reuse Step 3. It runs inline at Step 0h before the main orchestration loop begins. Each planning stage is executed sequentially by spawning the orchestrator with `PHASE: HUMAN_PLANNING` context, which routes to the correct agent per the Planning Phase Routing in orchestrator.md.

**Error Code Reference**:

| Error Code | Stage | Meaning | Recovery Action |
|------------|-------|-------P3--|-----------------|
| `[PLAN-GATE-001]` | P1 | Intent Brief missing or Intent Review gate failed | Spawn product-manager in HUMAN_PLANNING mode for P1 |
| `[PLAN-GATE-002]` | P2 | Scope Contract missing or Scope Lock gate failed | Spawn product-manager in HUMAN_PLANNING mode for P2 (requires P1 PASSED) |
| `[PLAN-GATE-003]` | P3 | Dependency Charter missing or Dependency Acceptance gate failed | Spawn technical-program-manager for P3 (requires P2 PASSED) |
| `[PLAN-GATE-004]` | P4 | Sprint Kickoff Brief missing or Sprint Readiness gate failed | Spawn engineering-manager for P4 (requires P3 PASSED) |

---

## Step 0g: Pre-Session Phase Initialization

Initialize phase tracking and resume any incomplete prior phases.

### 0g.1 Resume incomplete phase from prior session

```
IF exists(".orchestrate/<session-id>/checkpoint.json")
   AND checkpoint.phase_transitions has entries
   AND checkpoint.terminal_state is null:
    last_phase = checkpoint.phase_transitions[-1].to_phase
    Log: "[PHASE-RESUME] Resuming phase {last_phase} from prior session"
    set current_phase = last_phase
ELSE:
    set current_phase = "Phase 1: Intent Frame" (or skip per 0h skip conditions)
```

### 0g.2 Detect release flag

```
IF task_description contains "release", "deploy to production", "ship", "go live"
   OR user passed --release flag:
    checkpoint.release_flag = true
    Log: "[PHASE] Release flag detected — Phase 7 (Release Prep) will run at end of pipeline"
```

### 0g.3 Initialize phase checkpoint fields

```json
{
  "phase_transitions": [],
  "phase_receipts": [],
  "domain_activations": [],
  "domain_reviews": { "0": [], "1": [], "2": [], "3": [], "4": [], "4.5": [], "5": [], "6": [] },
  "release_flag": false
}
```

These fields track internal phase progression. `phase_transitions` is append-only with `{from_phase, to_phase, reason, timestamp}` entries. `phase_receipts` lists paths to phase receipts written under `.orchestrate/<session>/phase-receipts/`. Domain activation fields track which domain agents reviewed which stages per `_shared/protocols/agent-activation.md`.

---

## Step 1: Enhance User Input (Inline)

> **GUARD**: Do NOT delegate to `workflow-plan` or call `EnterPlanMode`.
> **GUARD**: Do NOT read project files, docs, or source code. Enhancement uses ONLY the user's input text. Project analysis is the researcher's job (Stage 0). If the task mentions "docs folder" or specific files, reference them in the enhanced prompt for the orchestrator — do NOT read them yourself.

Analyze raw input for clarity, scope, deliverables, constraints, and context. Transform into a structured prompt.

### Custom Scope Template (when scope is `custom`)

```
**Objective**: [Clear statement]
**Context**: [Current state, background]
**Deliverables**: [Specific outputs]
**Constraints**: [Limitations]
**Success Criteria**: [Verifiable criteria]
**Out of Scope**: [Exclusions]
**Assumptions** (autonomous mode): [Documented assumptions]
```

### Scope-Templated Enhanced Prompt (when scope is NOT `custom`)

The scope specification IS the enhanced prompt template. The user's `task_description` provides the **Objective**; the scope spec defines everything else.

**Rules**:
- User input may ADD requirements but MUST NOT cause any scope spec content to be omitted (SCOPE-002)
- Store the full verbatim scope spec in `enhanced_prompt.scope_specification`

Format:
```
**Objective**: [User's task_description]
**Additional User Context**: [Extra requirements beyond scope spec, if any]
**Assumptions** (autonomous mode): [Assumptions]
**Out of Scope**: [Exclusions]

## Full Scope Specification (VERBATIM)
[Entire text from Appendix A and/or B — word-for-word, nothing omitted]
```

---

## Step 2: Initialize Session Checkpoint

### 2a. Ensure directories

```bash
mkdir -p .orchestrate/${SESSION_ID}
mkdir -p ~/.claude/sessions  # legacy fallback
```

### 2b. Supersede existing in-progress sessions

```bash
# CROSS-003: Scope scan to current working directory only
grep -rl '"status": "in_progress"' "$(pwd)"/.orchestrate/*/checkpoint.json 2>/dev/null
grep -rl '"status": "in_progress"' ~/.claude/sessions/auto-orc-*.json 2>/dev/null
```

**CWD filter**: Only consider sessions whose checkpoint file is under the current working directory. Sessions from other projects are ignored. Log: `[CROSS-003] Filtered session scan to CWD: $(pwd)`

For EVERY in-progress session: set `"status": "superseded"`, add `"superseded_at"` and `"superseded_by"`. Non-destructive — never delete. If superseded session's `original_input` matches current: **resume** (skip to Step 3).

**Stale in_progress task cleanup on resume**: When resuming a session, scan for tasks marked `in_progress`. For each, check the `in_progress_iterations` counter in the checkpoint. If a task has been `in_progress` for >= 5 iterations: mark as `failed`, log `[RESUME] Task #<id> "<subject>" stuck in_progress for <N> iterations — marking failed`. This prevents resume from hanging on zombie tasks.

Also update `.sessions/index.json` at the project root: set the superseded session's status to `"superseded"` and add `"superseded_at"`. See `commands/SESSIONS-REGISTRY.md` for the registry format and write protocol.

### 2c. Create new session

**Session ID**: `auto-orc-<DATE>-<8-char-slug>` (slug from user input).

Create parent tracking task via `TaskCreate` (if available; if TaskCreate fails, log `[CROSS-001] TaskCreate unavailable — setting parent_task_id: null` and continue with `parent_task_id: null`), then:

```bash
mkdir -p .orchestrate/<session-id>/{planning,stage-0,stage-1,stage-2,stage-3,stage-4,stage-4.5,stage-5,stage-6,phase-receipts,gates,meetings,handovers}
```

**Output structure** (per `_shared/protocols/output-standard.md`):
- `checkpoint.json` — session state (atomic write)
- `MANIFEST.jsonl` — session-level manifest (one per session, not per-stage)
- `proposed-tasks.json` — task proposals from orchestrator
- `stage-N/` — per-stage outputs with `YYYY-MM-DD_<slug>.md` files + `stage-receipt.json`
- **Stage-3, stage-4, stage-6** write code/tests/docs to the **project directory**; their `stage-receipt.json` + `changes.md` track what was modified
- Every stage completion writes a `stage-receipt.json` — the standard bridge to domain memory

Write checkpoint **atomically** (write to `checkpoint.tmp.json`, then rename to `checkpoint.json`) to `.orchestrate/<session-id>/checkpoint.json` (primary) and `~/.claude/sessions/<session-id>.json` (legacy):

**Checkpoint schema migration**: On resume (Step 2b), check the `schema_version` field of the loaded checkpoint. If the version is older than the current format (e.g., "1.0.0" vs "1.1.0"), attempt graceful migration: add any missing fields with defaults, log `[MIGRATE] Checkpoint migrated from <old> to <new>`. If migration fails, abort with `[MIGRATE-FAIL] Cannot migrate checkpoint from schema_version <version>. Start a new session.`

**Planning fields migration (1.0.0 → 1.1.0)**: When resuming a session with `schema_version: "1.0.0"` (pre-planning), add planning fields with default values:

```json
{
  "planning_stages_completed": [],
  "planning_artifacts": {
    "P1_intent_brief": null,
    "P2_scope_contract": null,
    "P3_dependency_charter": null,
    "P4_sprint_kickoff_brief": null
  },
  "planning_gate_statuses": {
    "P1": null,
    "P2": null,
    "P3": null,
    "P4": null
  },
  "current_planning_stage": null,
  "planning_skipped": false,
  "triage": null,
  "fast_path_used": false,
  "planning_revision_count": 0,
  "planning_revision_history": [],
  "validation_regression_count": 0,
  "thrash_counter": 0,
  "state_hash_window": [],
  "auto_eval_history": [],
  "phase_transitions": []
}
```

Log: `[MIGRATE] Added planning fields to checkpoint (1.0.0 → 1.1.0)`

Update `schema_version` to `"1.1.0"` after migration.

### 2d. Gate State Check

If `.orchestrate/<session>/gate-state.json` exists from a prior session in the same project root (written by an earlier auto-orchestrate run):

1. Read and parse the gate state file
2. Extract `current_gate`, `gate_status`, and `gates_passed` array (derive from gates with `status: "passed"`)
3. Map organizational gates to pipeline stages:
   - Gate 1 (Intent Review / `gate_1_intent_review`) → prerequisite for Stage 0
   - Gate 2 (Scope Lock / `gate_2_scope_lock`) → prerequisite for Stage 2
   - Gate 3 (Dependency Acceptance / `gate_3_dependency_acceptance`) → prerequisite for Stage 3
   - Gate 4 (Sprint Readiness / `gate_4_sprint_readiness`) → prerequisite for Stage 5
4. Store in checkpoint:
   ```json
   "gate_state": {
     "source": ".gate-state.json",
     "current_gate": 2,
     "gates_passed": ["gate_1_intent_review", "gate_2_scope_lock"],
     "loaded_at": "<ISO-8601>"
   }
   ```

**Backward compatibility**: If `.gate-state.json` does not exist, log `[GATE-SKIP] No gate state found — organizational gates not enforced` and proceed normally. Set `gate_state: null` in checkpoint.

```json
{
  "schema_version": "1.9.0",
  "session_id": "<session-id>",
  "created_at": "<ISO-8601>",
  "updated_at": "<ISO-8601>",
  "status": "in_progress",
  "iteration": 0,
  "max_iterations": 100,
  "original_input": "<raw user input>",
  "scope": { "flag": null, "resolved": "custom", "layers": [] },
  "permissions": { "autonomous_operation": true, "session_folder_access": true, "no_clarifying_questions": true, "granted_at": "<ISO-8601>" },
  "enhanced_prompt": {
    "objective": "...", "context": "...",
    "deliverables": ["..."], "constraints": ["..."], "success_criteria": ["..."],
    "out_of_scope": ["..."], "assumptions": ["..."],
    "scope_specification": "<VERBATIM scope spec or empty for custom>"
  },
  "task_ids": [],
  "parent_task_id": "<TaskCreate ID>",
  "iteration_history": [],
  "terminal_state": null,
  "current_pipeline_stage": 0,
  "stages_completed": [],
  "mandatory_stage_enforcement": false,
  "stage_3_completed_at_iteration": null,
  "task_limits": { "max_tasks": 50, "max_active_tasks": 30, "max_continuation_depth": 3 },
  "task_snapshot": { "written_at": null, "iteration": null, "tasks": [] },
  "gate_state": null,
  "gate_override": false,
  "project_type": null,
  "planning_stages_completed": [],
  "planning_artifacts": {
    "P1_intent_brief": null,
    "P2_scope_contract": null,
    "P3_dependency_charter": null,
    "P4_sprint_kickoff_brief": null
  },
  "planning_gate_statuses": {
    "P1": null,
    "P2": null,
    "P3": null,
    "P4": null
  },
  "current_planning_stage": null,
  "planning_skipped": false,
  "phase_transitions": [],
  "phase_receipts": [],
  "phase_findings": { "0": [], "1": [], "2": [], "3": [], "4": [], "4.5": [], "5": [], "6": [] },
  "phase_gates": {},
  "phase_summary": null,
  "release_flag": false,
  "domain_activations": [],
  "domain_reviews": { "0": [], "1": [], "2": [], "3": [], "4": [], "4.5": [], "5": [], "6": [] },
  "research_depth": {
    "tier": null,
    "source": null,
    "escalated_by": [],
    "resolved_at": null
  },
  "parallel_cap": 5,
  "independence_groups": [],
  "independence_group_stages": {},
  "dependency_graph": { "edges": [] },
  "optimizations": {
    "skill_frontmatter_routing": true,
    "process_injection_slim": true,
    "manifest_digest": true,
    "per_stage_templates": true,
    "stage_receipt_diet": true,
    "handover_compress": true
  },
  "session_token_total": { "input": 0, "output": 0 }
}
```

**Phase fields migration (1.1.0 → 2.0.0)**: When resuming a session without phase fields (legacy dispatch fields are dropped), add the new phase fields with defaults:
```json
{
  "phase_transitions": [],
  "phase_receipts": [],
  "phase_findings": { "0": [], "1": [], "2": [], "3": [], "4": [], "4.5": [], "5": [], "6": [] },
  "phase_gates": {},
  "phase_summary": null,
  "release_flag": false
}
```
Log: `[MIGRATE] Migrated dispatch fields to phase fields (1.1.0 → 2.0.0)`

**Domain activation fields migration (1.2.0 → 1.3.0)**: When resuming a session without domain activation fields, add them with defaults:
```json
{
  "domain_activations": [],
  "domain_reviews": { "0": [], "1": [], "2": [], "3": [], "4": [], "4.5": [], "5": [], "6": [] }
}
```
Log: `[MIGRATE] Added domain activation fields to checkpoint (1.2.0 → 1.3.0)`

Update `schema_version` to `"1.3.0"` after migration.

**Process scope fields migration (1.3.0 → 1.4.0)**: When resuming a session where `triage` exists but lacks `process_scope`, add it with a safe default:
```json
{
  "triage": {
    "process_scope": {
      "tier": "complex",
      "domain_flags": [],
      "active_categories": [1, 2, 3, 5, 6, 7, 8, 9, 10, 12, 13, 16],
      "active_phases": ["5s", "5q", "5i", "5d", "9"],
      "total_active": 56
    }
  }
}
```
Log: `[MIGRATE] Added process_scope to triage (1.3.0 → 1.4.0). Defaulting to complex (all processes active).`

**Note**: Default is `complex` (all processes active) so existing sessions do not lose coverage. New sessions compute the actual scope via Step 0h-pre.

Update `schema_version` to `"1.4.0"` after migration.

**Triage fields migration (1.4.0 → 1.5.0)**: When resuming a session where `triage` exists but lacks `tshirt_size`, add derived fields with safe defaults:
```json
{
  "triage": {
    "tshirt_size": "M",
    "files_touched_estimate": 10,
    "risk_score": 3,
    "cross_team_impact": []
  }
}
```
Log: `[MIGRATE] Added tshirt_size/risk_score/files_touched_estimate/cross_team_impact to triage (1.4.0 → 1.5.0). Defaulting to medium estimates.`

Update `schema_version` to `"1.5.0"` after migration.

**Research depth migration (1.5.0 → 1.6.0)**: When resuming a session that lacks `research_depth`, add the field with safe defaults. The tier remains `null` until the next Step 0h-pre pass re-resolves it via RESEARCH-DEPTH-001:
```json
{
  "research_depth": {
    "tier": null,
    "source": null,
    "escalated_by": [],
    "resolved_at": null
  }
}
```
Log: `[MIGRATE] Added research_depth field to checkpoint (1.5.0 → 1.6.0). Tier will be resolved on next Step 0h-pre pass.`

**Resolution behavior on resume**: If `research_depth.tier` is `null` when the orchestrator spawn prompt is built (Step 3/Appendix C), fall back to `"normal"` for that spawn and log `[RESEARCH-DEPTH-RESUME] research_depth.tier was null on resume — using "normal" fallback`. This preserves pre-RESEARCH-DEPTH-001 behavior for legacy sessions.

Update `schema_version` to `"1.6.0"` after migration.

**Parallel scheduling fields migration (1.6.0 → 1.7.0)**: When resuming a session that lacks PARALLEL-001/002/003 fields, add them with safe defaults. Sessions resumed at this version run sequentially (single-task spawn) until Stage 1 re-emits `independence_groups` and `dependency_graph`:

```json
{
  "parallel_cap": 5,
  "independence_groups": [],
  "independence_group_stages": {},
  "dependency_graph": { "edges": [] }
}
```

Log: `[MIGRATE] Added parallel scheduling fields to checkpoint (1.6.0 → 1.7.0). Default parallel_cap=5; sequential spawning until Stage 1 re-emits independence_groups.`

Update `schema_version` to `"1.7.0"` after migration.

**Field semantics**:
- `parallel_cap` — Maximum concurrent Stage 3 spawns. Range `[1, 7]`. Default 5. Used by orchestrator's Stage 3 parallel scheduling algorithm (see `agents/orchestrator.md` Stage 3 Parallel Implementation Pattern).
- `independence_groups` — Array of arrays of task IDs, emitted by Stage 1 product-manager (PARALLEL-001). Empty array means no parallelism (single shared group).
- `independence_group_stages` — Map `{ group_id: stage_n }` tracking each group's furthest-reached stage. Updated when a task in that group completes. Allows groups to advance independently (PARALLEL-002).
- `dependency_graph.edges` — Edges of `{from_task, to_task, dependency_type}`; `dependency_type` ∈ `{NONE, READ-AFTER-WRITE, WRITE-AFTER-WRITE, API-CONTRACT}`. Used to gate cross-group concurrency.

**Token-budget optimization fields migration (1.7.0 → 1.8.0)**: When resuming a session that lacks token-budget optimization fields, add them with defaults. Resumed sessions default ALL optimization flags to `false` (verbose mode) until the next iteration explicitly opts in. New sessions default to `true`:

```json
{
  "optimizations": {
    "skill_frontmatter_routing": false,
    "process_injection_slim": false,
    "manifest_digest": false,
    "per_stage_templates": false
  },
  "session_token_total": { "input": 0, "output": 0 }
}
```

Log: `[MIGRATE] Added token-budget optimization fields (1.7.0 → 1.8.0). Optimizations default OFF for resumed sessions; flip true to enable.`

Update `schema_version` to `"1.8.0"` after migration.

**Receipt-diet optimization fields migration (1.8.0 → 1.9.0)**: When resuming a session that lacks the receipt-diet optimization fields, add them. Resumed sessions default these to `false` (legacy verbose receipts) so prior receipts on disk remain valid against their existing readers. New sessions default to `true`:

```json
{
  "optimizations": {
    "stage_receipt_diet": false,
    "handover_compress": false
  }
}
```

Log: `[MIGRATE] Added stage_receipt_diet + handover_compress (1.8.0 → 1.9.0). Receipt slim mode defaults OFF on resume; flip true to write v2 receipts.`

Update `schema_version` to `"1.9.0"` after migration.

**Optimization flag semantics**:
- `skill_frontmatter_routing` — When true, skill discovery loads SKILL.md YAML frontmatter only (~300 tok); full body loads only at invocation. See SKILL-FRONTMATTER-001 in `_shared/protocols/command-dispatch.md`.
- `process_injection_slim` — When true, spawn-prompt builder injects only fired hooks (filtered) instead of the full process injection map. See `[INJECT-AUDIT]` log entries in Step 3.
- `manifest_digest` — When true, subagents receive a 2k digest (`agents[].name + dispatch_triggers` + `skills[].name + triggers`); only the orchestrator and tasks with `needs_full_manifest: true` get the full 19k manifest.
- `per_stage_templates` — When true, orchestrator spawn prompts load `agents/orchestrator.md` core + only the active stage/phase template from `agents/orchestrator/templates/`. When false, builder concatenates all templates back to the legacy verbose format.
- `stage_receipt_diet` — When true, stage producers write the slim v2.0.0 stage-receipt format (`_shared/protocols/output-standard.md` §4.1). Consumer agents must read both v1 and v2 per §4.3. See STAGE-RECEIPT-DIET-001.
- `handover_compress` — When true, handover-receipt producers write the slim v2.0.0 format (`_shared/protocols/command-dispatch.md`). Consumers re-derive `context_carry` from checkpoint when v1 callers expect it. See HANDOVER-COMPRESS-001.

**Token estimation method (Step 4.6)**: Token counts are estimates, not meters. Use:
- `input_estimate = (chars_in_spawn_prompt + chars_in_agent_md + sum(chars_in_loaded_skill_mds)) // 4`
- `output_estimate = chars_in_returned_text // 4`

Estimates are sufficient to see trend deltas across optimization phases (target ~48% reduction). Logs: `[TOKEN] spawn=<id> agent=<name> input≈<N> output≈<M>`.

---

## Step 2a: Fast-Path Evaluation (FAST-001)

After session setup (Step 2) and before entering the orchestrator loop (Step 3), evaluate whether this task qualifies for the fast path — a streamlined 3-stage execution that bypasses the orchestrator entirely.

**Entry condition**:
```
IF checkpoint.triage.classification == "trivial"
   AND fast_path == true
   AND scope NOT IN ["frontend", "backend", "fullstack"]
   AND checkpoint.fast_path_used != true  # not already attempted
THEN:
    Enter fast-path execution
ELSE:
    Skip to Step 3 (normal orchestrator loop)
```

**Fast-path execution** (exception to AUTO-001 per FAST-001):

```
┌─────────────────────────────────────────────────────────────────────┐
│  FAST PATH: TRIVIAL TASK BYPASS                                     │
│                                                                     │
│  TRIVIAL + fast_path ──► researcher (S0)                            │
│                              │                                      │
│                              ├── checkpoint + stage-receipt          │
│                              │                                      │
│                              ▼                                      │
│                          software-engineer (S3)                     │
│                              │                                      │
│                              ├── checkpoint + stage-receipt          │
│                              │                                      │
│                              ▼                                      │
│                          validator skill inline (S5)                │
│                              │                                      │
│                              ├── checkpoint + stage-receipt          │
│                              │                                      │
│                              ▼                                      │
│                          DONE (stages_completed: [0, 3, 5])        │
│                                                                     │
│  Total: 3 spawns maximum instead of N orchestrator iterations       │
└─────────────────────────────────────────────────────────────────────┘
```

**Stage 0 — Researcher**:
1. **Research cache check (SHARED-003)**: Before spawning, check `.pipeline-state/research-cache.jsonl` for non-stale entries matching the task keywords. If cached results exist with `ttl_hours` not expired, include them in the researcher prompt as `[CACHED-RESEARCH]` context to avoid redundant lookups.
2. Spawn `Agent(subagent_type: "researcher")` with the enhanced prompt from Step 1
3. Write checkpoint before spawn (AUTO-005 applies)
4. On completion: write stage-receipt to `.orchestrate/<session>/stage-0/`
4. **Complexity upgrade check**: If researcher output contains any of: multiple services/components discovered, architectural concerns, dependency conflicts, or security flags → log `[FAST-PATH-ABORT] Researcher revealed complexity > trivial — falling back to full pipeline` and proceed to Step 3 with `stages_completed: [0]`, `fast_path_used: false`

**Stage 3 — Software Engineer**:
1. Spawn `Agent(subagent_type: "software-engineer")` with researcher findings + enhanced prompt
2. Write checkpoint before spawn
3. On completion: write stage-receipt to `.orchestrate/<session>/stage-3/`

**Stage 5 — Validator**:
1. Read and follow the `validator` skill's `SKILL.md` inline (this is a skill, not an agent)
2. On completion: write stage-receipt to `.orchestrate/<session>/stage-5/`
3. **Validation failure fallback**: If validator returns FAIL → log `[FAST-PATH-ABORT] Validation failed — falling back to full pipeline at Stage 3` and proceed to Step 3 with `stages_completed: [0, 3]`, `fast_path_used: false`

**Fast-path completion**:
```json
{
  "stages_completed": [0, 3, 5],
  "fast_path_used": true,
  "terminal_state": "completed"
}
```
Log: `[FAST-PATH] Trivial task completed via fast path — 3 stages, no orchestrator overhead.`

Proceed directly to Step 6 (Termination) with `terminal_state: "completed"`.

---

## Step 3: Spawn Orchestrator (Loop Entry)

> **CRITICAL TRANSITION GUARD**: You should arrive here with EXACTLY ONE task (the parent tracking task from Step 2c) and ZERO knowledge of the project's internals. If you have read project files, identified components/services, or created multiple tasks — you have violated the Execution Guard. STOP and restart from this step. The orchestrator and its subagents will do ALL project analysis and task creation.

**Before spawning** (AUTO-005): Increment `iteration`, update `updated_at`, write checkpoint.

### 3a. Calculate STAGE_CEILING

#### Planning Gate Check (PRE-RESEARCH-GATE)

Before calculating the numeric STAGE_CEILING, check planning completion:

```
IF planning_skipped == false AND planning_stages_completed != ["P1","P2","P3","P4"]:
    STAGE_CEILING = "PLANNING"  # Cannot proceed to numeric stages
    # The orchestrator operates in HUMAN_PLANNING mode
    # See Step 0h for planning loop details
ELSE:
    # Proceed to numeric STAGE_CEILING calculation below
```

When `STAGE_CEILING = "PLANNING"`, the orchestrator receives:
- `PHASE: HUMAN_PLANNING` in spawn prompt
- `CURRENT_PLANNING_STAGE: <P1|P2|P3|P4>` indicating the next incomplete stage

#### Numeric STAGE_CEILING Calculation

STAGE_CEILING = the maximum pipeline stage the orchestrator may work on. Calculated from `stages_completed`:

| Condition | STAGE_CEILING |
|-----------|---------------|
| 0 not completed | 0 (research only) |
| 0 done, 1 not | 1 |
| {0,1} done, 2 not | 2 |
| {0,1,2} done, 3 not | 3 |
| {0,1,2,3} done, 4/4.5 not | 4.5 (Stage 4 optional — see AUTO-002) |
| {0,1,2,4.5} done, 5 not | 5 |
| {0,1,2,4.5,5} done, 6 not | 6 |
| All done | 6 |

**STAGE_CEILING is a HARD LIMIT** — the orchestrator MUST NOT spawn agents or do work above this stage.

#### Gate Enforcement at Stage Transitions

Before allowing work at a pipeline stage, check if the mapped organizational gate has been passed (from Step 2d gate_state):

| Pipeline Stage | Required Gate | Gate Name |
|----------------|---------------|-----------|
| Stage 0 | Gate 1 | `gate_1_intent_review` |
| Stage 2 | Gate 2 | `gate_2_scope_lock` |
| Stage 3 | Gate 3 | `gate_3_dependency_acceptance` |
| Stage 5 | Gate 4 | `gate_4_sprint_readiness` |

**Enforcement logic**:

1. **Gate NOT passed AND `gate_override` NOT set**:
   - Log: `[GATE-BLOCK] Stage <N> requires Gate <G> — re-run the corresponding planning phase (Phase 1-4) to produce a passing gate verdict`
   - Reduce STAGE_CEILING to block that stage
   - Example: If Stage 2 requires Gate 2 but Gate 2 not passed → cap STAGE_CEILING at 1

2. **Gate NOT passed BUT `gate_override: true` in checkpoint**:
   - Log: `[GATE-OVERRIDE] Proceeding past Gate <G> with override`
   - Allow progression past the gate
   - Record override usage in iteration_history for audit

3. **`.gate-state.json` does not exist**:
   - Log: `[GATE-SKIP] No gate state found — organizational gates not enforced`
   - Proceed normally (backward compatible)
   - This is the default state for projects not using the organizational workflow

**Gate ceiling calculation** (applied AFTER stages_completed ceiling):
```
gate_ceiling = 6  # Default: no gate restriction

if gate_state is not null:
    if "gate_1_intent_review" not in gates_passed and not gate_override:
        gate_ceiling = min(gate_ceiling, -1)  # Block Stage 0
    if "gate_2_scope_lock" not in gates_passed and not gate_override:
        gate_ceiling = min(gate_ceiling, 1)   # Block Stage 2+
    if "gate_3_dependency_acceptance" not in gates_passed and not gate_override:
        gate_ceiling = min(gate_ceiling, 2)   # Block Stage 3+
    if "gate_4_sprint_readiness" not in gates_passed and not gate_override:
        gate_ceiling = min(gate_ceiling, 4.5) # Block Stage 5+

STAGE_CEILING = min(STAGE_CEILING_from_stages, gate_ceiling)
```

### 3b. Display iteration banner

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ITERATION <N> of <max> | Session: <session_id>
 PLANNING: P1 <✓/✗> P2 <✓/✗> P3 <✓/✗> P4 <✓/✗> | EXECUTION: Stage 0 <✓/✗> → ... → Stage 6 <✓/✗>
 STAGE_CEILING: <ceiling> | Tasks: <completed> done, <in_progress> running, <pending> pending, <blocked> blocked
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Planning status indicators**:
- `✓` — Planning stage gate PASSED
- `✗` — Planning stage gate not passed or FAILED
- If `planning_skipped: true`, display: `PLANNING: [SKIPPED]`

> **IMPORTANT**: If `in_progress > 0`, append to the banner: `⚠ <N> task(s) still running — pipeline NOT complete`

### 3c. Display task board (DISPLAY-001)

Query `TaskList`, group by `dispatch_hint` using the Pipeline Stage Reference table. Display:

```
 TASK BOARD:
 ┌─ Stage 0 (Research) ─────────────────────────────
 │  ✓ #2  Research pipeline audit best practices
 ├─ Stage 1 (Product Management) ────────────────────
 │  ◷ #3  Decompose audit into epic tasks          [blocked by #2]
 ├─ Stage 2 (Specifications) ───────────────────────
 │  ◷ #4  Create technical specifications          [blocked by #3]
 └──────────────────────────────────────────────────
 Legend: ✓ completed  ▶ in_progress  ○ pending  ◷ blocked
```

Each task shows: status icon, task ID, subject (truncated to 45 chars), `[blocked by #N]` if blocked.

### 3d. Pre-spawn self-check

Before spawning, verify ALL of these conditions. If ANY fails, you are off-track:
- [ ] You are about to spawn exactly ONE agent with `subagent_type: "orchestrator"` — NOT 5 parallel agents, NOT software-engineer/researcher/technical-writer agents
- [ ] You have NOT read any project source files, docs, or configs (beyond what Step 1 needed for prompt enhancement)
- [ ] The only task that exists (besides the parent) was proposed by a previous orchestrator iteration (or this is iteration 1 with no work tasks yet)
- [ ] The iteration banner (Step 3b) includes `STAGE_CEILING` — if it doesn't, you skipped Step 3a
- [ ] You are NOT about to "do the work yourself" because it "seems simple enough"

### 3d-bis. Manifest digest selection (MANIFEST-DIGEST-001)

Before building the spawn prompt body, decide which manifest representation to inject:

```python
# Pseudocode — actual implementation uses layer1.needs_full_manifest
from layer1 import build_digest, needs_full_manifest

if checkpoint["optimizations"]["manifest_digest"] is False:
    # Verbose / legacy mode: full manifest for all spawns
    manifest_payload = read_file(manifest_path)
    manifest_injection_kind = "full"
elif needs_full_manifest(target_agent_name, task=task_being_spawned):
    # orchestrator, session-manager, or task with needs_full_manifest=true
    manifest_payload = read_file(manifest_path)
    manifest_injection_kind = "full"
else:
    # All other subagents — slim digest
    manifest_payload = build_digest(manifest_path)  # ~2.6k tok vs ~19k
    manifest_injection_kind = "digest"

log(f"[OPT-2-DIGEST] target={target_agent_name} kind={manifest_injection_kind} "
    f"tokens≈{len(manifest_payload)//4}")
```

Set `MANIFEST_INJECTION: <kind>` in the spawn prompt context block (line shown in Auto-Orchestration Context).

**Re-spawn-on-failure**: If a subagent's return text contains `[MANIFEST-FIELD-MISSING]` (the agent looked for a field not in the digest), the loop controller re-spawns that agent ONCE with `needs_full_manifest: true` and logs `[MANIFEST-DIGEST-001 FAIL] subagent "<agent>" needs full manifest — re-spawning with full`. If the second spawn also fails, abort the task with `[MANIFEST-DIGEST-FATAL]`.

### 3d-ter. Orchestrator template extraction (TEMPLATE-EXTRACT-001)

Build the orchestrator's spawn prompt body via the section-extraction helper to avoid shipping the full ~33k `orchestrator.md` when only one stage/phase template is active:

```python
# Pseudocode — actual implementation uses layer1.build_spawn_prompt_body
from layer1 import build_spawn_prompt_body

flag_on = checkpoint["optimizations"]["per_stage_templates"]
orch_md = "~/.claude/agents/orchestrator.md"

if active_phase:           # e.g. "5q", "5s", "7", "9"
    body = build_spawn_prompt_body(orch_md, phase=active_phase, enabled=flag_on)
elif active_meeting:       # e.g. "daily-standup", "sprint-review"
    body = build_spawn_prompt_body(orch_md, meeting_kind=active_meeting, enabled=flag_on)
else:                      # Numeric stage spawn
    body = build_spawn_prompt_body(orch_md, stage=STAGE_CEILING, enabled=flag_on)

log(f"[OPT-1-TEMPLATE] flag={'on' if flag_on else 'off'} "
    f"injected_tokens≈{len(body)//4} "
    f"target={'core+stage-' + str(STAGE_CEILING) if flag_on else 'full'}")
```

**Safe fallback**: When `flag_on=True` and the requested section can't be located, the helper returns the full file. This makes it impossible for a missing section to silently strip the orchestrator's instructions.

**Behavioral equivalence**: With flag off, the helper returns byte-equivalent content to today (the unaltered full file). With flag on, only ~8k of CORE + ~300-2k of active template are sent, but every subsection actually needed at the spawn boundary remains present.

### 3e. Spawn orchestrator

Spawn EXACTLY ONE agent: `Agent(subagent_type: "orchestrator")` using the **Appendix C** template. Never spawn multiple orchestrators in parallel. Never spawn non-orchestrator agents from this loop.

> **Note (CROSS-006)**: Single-spawn enforcement is prompt-level only. No API-level guard exists. Monitor for violations in iteration history.

---

## Step 4: Process Results and Loop

> **AUTO-001 GUARD**: NEVER spawn a non-orchestrator agent regardless of orchestrator output.

After orchestrator returns, execute these sub-steps with visible progress at each (PROGRESS-001):

**4.1 Display summary**: Stages covered, tasks completed/in_progress/pending, pipeline status. If ANY tasks are `in_progress`, display prominently: `⚠ <N> task(s) still running — waiting for completion before evaluating pipeline`. Tasks with status `in_progress` mean background agents are still working — the pipeline is NOT idle and NOT complete.

**4.2 Process task proposals** `[STEP 4.2]`:
- Read `.orchestrate/<session-id>/proposed-tasks.json` and parse `PROPOSED_ACTIONS` from return text
- **Precedence rule**: If BOTH sources contain tasks, the file (`proposed-tasks.json`) takes precedence. `PROPOSED_ACTIONS` from return text is used ONLY as fallback when the file is missing, empty, or contains `"tasks": []`. Log: `[STEP 4.2] Source: file` or `[STEP 4.2] Source: return-text (file empty/missing)`
- **Deduplication**: If both sources are present, merge by `subject` field — file version wins on conflict. Log duplicates: `[STEP 4.2] Deduplicated <N> tasks (file wins)`
- **blockedBy chain validation (CHAIN-001)**: Every task for Stage N (N > 0) must reference Stage N-1. Auto-fix missing chains: `[CHAIN-FIX] Added blockedBy to "<subject>"`. Validate that referenced blockedBy task IDs actually exist — log orphaned references: `[CHAIN-WARN] Task "<subject>" blockedBy references non-existent task`
- **dispatch_hint validation (HINT-001)**: For each task, check that `dispatch_hint` matches a known agent name from `manifest.json` agents list OR a known skill name. If invalid: log `[HINT-WARN] Invalid dispatch_hint "<hint>" on task "<subject>" — routing may fail`. Do NOT block task creation; just warn.
- Create via `TaskCreate`, set `blockedBy` via `TaskUpdate`
- Write `proposed-tasks-processed-<iteration>.json` with enriched content (skip if empty)
- Output: `Created <N> tasks, updated <M> (chain-fixed: <K>)`

**4.2b PARALLEL-001 emission validation** `[STEP 4.2b]`:
- When Stage 1 has just completed, validate that `proposed-tasks.json` includes both `independence_groups` (array of arrays of task IDs) and `dependency_graph.edges` (array; may be empty). Required by PARALLEL-001.
- If either field is missing or malformed: log `[PARALLEL-001 FAIL] Missing independence_groups or dependency_graph — re-spawning product-manager` and re-spawn the product-manager once with feedback. After 2 failed re-spawns, abort with `[PARALLEL-001-FATAL]`.
- On success: persist both fields into `checkpoint.independence_groups` and `checkpoint.dependency_graph`. Log `[PARALLEL-001] Persisted N groups, M edges to checkpoint`.

**4.2c Per-group stage tracking (PARALLEL-002/003)** `[STEP 4.2c]`:
- After processing task proposals and stage transitions, advance per-group stage pointers in `checkpoint.independence_group_stages`:
  ```
  FOR EACH group_id IN checkpoint.independence_groups (one per group):
      group_tasks = tasks where task.id in group_id
      group_stage = MAX(task.stage for task in group_tasks where task.status == "completed")
      checkpoint.independence_group_stages[group_id] = group_stage
  ```
- These pointers let independent groups progress through stages at different rates without violating CHAIN-001 (which is relaxed cross-group per PARALLEL-002).
- The orchestrator's Stage 3 Parallel Implementation Pattern (see `agents/orchestrator.md`) reads `checkpoint.parallel_cap` (default 5, range `[1, 7]`) plus this map to decide concurrent spawn count.
- Note: `task-board.json` MAY carry multiple `in_progress` entries simultaneously when parallel scheduling is active (WORKFLOW-SYNC-001 reconciliation: each parallel agent updates its own task atomically; orchestrator reconciles after the spawn cycle returns).

**4.3 Query and display tasks** `[STEP 4.3]`:
- Query `TaskList`, categorize: `completed`, `pending`, `in_progress`, `blocked_or_failed`, `partial`
- Display task board (same format as Step 3c) showing status changes

**4.4 Verify partial tasks**: Ensure `"status": "partial"` tasks have continuation tasks.

**4.5 Task ceiling check**: If total tasks >= `max_tasks`: `task_cap_reached: true`. Output: `[LIMIT-001]`

**4.6 Record iteration history**:
```json
{
  "iteration": N,
  "tasks_completed": [{"id": "1", "subject": "..."}],
  "tasks_pending": [{"id": "3", "subject": "..."}],
  "tasks_in_progress": [],
  "tasks_blocked": [{"id": "4", "subject": "...", "blocked_by": ["3"]}],
  "tasks_partial_continued": [],
  "task_cap_reached": false,
  "stages_completed_snapshot": [0, 1],
  "stage_regression": false,
  "mandatory_stage_enforcement": false,
  "summary": "<first 500 chars of orchestrator output>",
  "token_counts_by_spawn": [
    {
      "spawn_id": "<UUID-or-counter>",
      "agent": "orchestrator",
      "stage": 3,
      "phase": null,
      "input_estimate": 41200,
      "output_estimate": 6800,
      "skills_loaded": ["production-code-workflow"],
      "optimizations_active": ["manifest_digest", "skill_frontmatter_routing"]
    }
  ]
}
```

**Token estimation logic** (per-spawn, Step 4.6):
1. `input_estimate = (chars_spawn_prompt + chars_agent_md + sum(chars_skill_mds_loaded)) // 4` — per `Token estimation method` in Step 2.
2. `output_estimate = chars_returned_text // 4`.
3. Append entry to `iteration_history[N].token_counts_by_spawn`.
4. After all spawns complete this iteration, accumulate to checkpoint root:
   - `checkpoint.session_token_total.input += sum(input_estimate for spawn in iteration)`
   - `checkpoint.session_token_total.output += sum(output_estimate for spawn in iteration)`
5. Log: `[TOKEN] iter=N input≈<sum_in> output≈<sum_out> session_total≈<input+output>`.

**Optimization tracking**: Each spawn records which `optimizations.*` flags were active at the time of the spawn. This lets retro analysis attribute savings to specific phases (Phase 0 baseline → Phase 4 fully optimized).

**4.7 Save checkpoint + task snapshot**: Write `task_snapshot` with ALL tasks (complete replacement each iteration):
```json
"task_snapshot": {
  "written_at": "<ISO-8601>", "iteration": N,
  "tasks": [{ "id": "...", "subject": "...", "status": "...", "blockedBy": [], "dispatch_hint": "..." }]
}
```

**4.8 Evaluate pipeline progress**: Use Pipeline Stage Reference to determine completion. A stage is complete ONLY when ALL tasks for that stage are `completed` AND ZERO tasks for that stage are `in_progress`. Tasks still `in_progress` (background agents running) block stage completion — do NOT mark a stage done while any of its tasks are still running. Apply AUTO-003 (monotonicity). Track `stage_3_completed_at_iteration`.

**4.8a Process Hook Verification** (V2 enforcement):

For each completed stage with enforced process hooks, verify process acknowledgments:

```
ENFORCED_HOOKS = {
  5: ["P-034", "P-037"],  # Code Review + UAT at Stage 5 (Validator) exit
  6: ["P-058"]            # Technical Documentation at Stage 6 exit
}

For each stage in stages_completed:
  If stage in ENFORCED_HOOKS:
    1. Read .orchestrate/<session-id>/stage-<N>/stage-receipt.json
    2. Check for process_acknowledgments array containing required process IDs
    3. If required process acknowledgment is missing:
       - Track iteration count in checkpoint.process_gates.stage_<N>.<P-NNN>_iterations
       - Iteration 1: Log [PROC-WARN] Stage <N> missing P-<NNN> acknowledgment — will enforce next iteration
       - Iteration 2: Log [PROC-ENFORCE] Stage <N> P-<NNN> not acknowledged — creating remediation task
         Create remediation task: "Stage <N> Process Gate: Acknowledge P-<NNN> in stage output"
       - Iteration 3+: Log [PROC-ESCALATE] Stage <N> P-<NNN> still unacknowledged — flagging for review
         Set checkpoint.process_gates.stage_<N>.escalated = true
    4. If acknowledgment found:
       - Set checkpoint.process_gates.stage_<N>.<P-NNN>_acknowledged = true
       - Log [PROC-PASS] Stage <N> P-<NNN> acknowledged

Acknowledgment detection patterns (grep stage output or stage-receipt.json):
  - P-034: "[P-034]" or "code review: PASS" or "review checklist"
  - P-037: "[P-037]" or "test results:" or "tests passed:"
  - P-058: "[P-058]" or "documentation: COMPLETE" or "docs written:"
```

**Checkpoint schema addition** for process gates:
```json
{
  "process_gates": {
    "stage_5": {
      "P-034_acknowledged": false,
      "P-034_iterations": 0,
      "P-037_acknowledged": false,
      "P-037_iterations": 0,
      "escalated": false
    },
    "stage_6": {
      "P-058_acknowledged": false,
      "P-058_iterations": 0,
      "escalated": false
    }
  }
}
```

**4.8b Auto-Evaluated Stage Verdicts (AUTO-EVAL-001)**:

After a stage completes, the orchestrator auto-evaluates the stage output and either advances to the next stage or transitions to an internal sub-loop. **No human pause occurs.** The evaluation logic is per-stage:

| Completed Stage | Auto-evaluation | Outcome |
|-----------------|-----------------|---------|
| Stage 0 (Research) | Researcher produced findings doc; verify ≥1 finding | PASS → Stage 1; FAIL → re-spawn researcher (max 2 retries) |
| Stage 1 (Decomposition) | `proposed-tasks.json` parses; CHAIN-001 chains valid; PARALLEL-001 graph present | PASS → Stage 2; FAIL → re-spawn product-manager |
| Stage 2 (Specification) | Spec artifact present per task; spec-creator skill verdict | PASS → Stage 3; FAIL → re-spawn |
| Stage 3 (Implementation) | Code changes committed per task | PASS → Stage 4 or 4.5; FAIL → re-spawn software-engineer |
| Stage 4.5 (Code Health) | codebase-stats output present; refactor-analyzer suggestions logged | always PASS (advisory) |
| Stage 5 (Validation) | validator + spec-compliance verdicts | PASS → Stage 6; FAIL → transition to **Phase 5e (Debug sub-loop)** then re-enter Stage 5; if persistent → **Phase 5v (Validation+Audit)** for compliance scoring |
| Stage 6 (Documentation) | docs-write artifacts present; docs-review verdict | PASS → Phase 7 (Release Prep); FAIL → re-spawn technical-writer |

Domain phases (5q/5s/5i/5d) are inline-invoked when the active scope flags their domain — see "Domain Phase Activation" section below. They run between Stage 5 and Stage 6 and produce findings that gate Phase 7 entry.

**Checkpoint addition**:
```json
{
  "auto_eval_history": [],
  "phase_transitions": []
}
```

`auto_eval_history` records every per-stage verdict with timestamp, criteria fired, and decision. `phase_transitions` records every transition between internal phases (Stage→5v, 5v→5e, 5e→Stage 3, etc.) for retro analysis.

**Internal Phase Architecture**:

The single auto-orchestrate command walks through the canonical end-to-end process as a sequence of internal phases. There are no sibling commands.

```
/auto-orchestrate <task>
    │
    ├─► Phase 1: Intent Frame (P-001..P-006)
    │      └─► Auto-evaluated Intent Review gate
    │
    ├─► Phase 2: Scope Contract (P-007..P-014)
    │      └─► Auto-evaluated Scope Lock gate
    │
    ├─► Phase 3: Dependency Map (P-015..P-021)
    │      └─► Auto-evaluated Dependency Acceptance gate
    │
    ├─► Phase 4: Sprint Bridge + Kickoff Ceremony (P-022..P-031)
    │      └─► Auto-evaluated Sprint Readiness gate
    │
    ├─► Phase 5: Execution (Stages 0..4.5)
    │      ├─► Phase 5q: Quality (P-032..P-037) — when scope flags qa
    │      ├─► Phase 5s: Security (P-038..P-043) — when scope flags security
    │      ├─► Phase 5i: Infra/SRE (P-044..P-048, P-054..P-057) — when scope flags infra
    │      ├─► Phase 5d: Data/ML (P-049..P-053) — when scope flags data_ml
    │      ├─► Phase 5v: Validation + Audit (Stage 5 + compliance scoring)
    │      │      └─► Phase 5e: Debug sub-loop (when validation fails)
    │      └─► Stage 6: Documentation (P-058..P-061)
    │
    ├─► Phase 7: Release Prep (release_flag=true)
    │      └─► Auto-evaluated Release Readiness gate
    │
    ├─► Phase 8: Post-Launch (P-070..P-073, P-054..P-057)
    │
    └─► Phase 9: Continuous Governance (P-062..P-069, P-074..P-093)
           └─► Inline-cadenced; runs on iteration boundaries when scope warrants
```

**Domain Phase Activation**:

Phases 5q, 5s, 5i, 5d are inline-invoked when the active scope flags their domain or when stage findings raise HIGH/CRITICAL severity in the corresponding process range. They do NOT run as separate commands.

| Phase | Process Range | Activates when |
|-------|---------------|----------------|
| **5q (Quality)** | P-032..P-037 | Stage 3 completes; or stage findings flag P-032..P-037 HIGH/CRITICAL |
| **5s (Security)** | P-038..P-043 | Stage 0/2/3 receipt mentions security threats; or P-038..P-043 flagged HIGH/CRITICAL |
| **5i (Infra/SRE)** | P-044..P-048, P-054..P-057 | Stage 5 fails with deploy/infrastructure keywords; or scope flags infra |
| **5d (Data/ML)** | P-049..P-053 | Stage 2/3/5 flags P-049..P-053 HIGH/CRITICAL; or scope flags data_ml |
| **9 (Governance)** | P-062..P-093 | Codebase-stats reports `tech_debt_score > 30%` OR `duplication_ratio > 0.15`; or CRITICAL RAID items present |

**4.8c Internal Phase Transition Evaluation (PHASE-LOOP-001)**:

After evaluating pipeline progress (4.8) and process hooks (4.8a), evaluate internal phase transitions. Each completed stage may trigger a transition to a domain phase before continuing the main pipeline. **There are no command dispatches; all phases run inline within auto-orchestrate.**

1. **Build event context** for each newly completed stage this iteration:
   ```
   completed_stages_this_iteration = stages_completed - stages_completed_previous_iteration

   FOR EACH newly_completed_stage IN completed_stages_this_iteration:
       event_context = {
         event_type: "stage_completed",
         stage: newly_completed_stage,
         stage_receipt: read ".orchestrate/<session>/stage-<N>/stage-receipt.json" (if exists),
         checkpoint: current checkpoint
       }
   ```

2. **Evaluate phase transitions** based on stage outcomes and active scope:

   | Condition | Transition |
   |-----------|------------|
   | Stage 0 completes AND stage-receipt flags P-038 HIGH/CRITICAL | → Phase 5s (Security) inline before Stage 1 spec influences |
   | Stage 3 completes | → Phase 5q (Quality) inline for test strategy review |
   | Stage 5 fails with deploy/infra keywords | → Phase 5i (Infra) inline for resolution |
   | Stage 4.5 completes AND tech_debt > 30% OR duplication > 15% | → Phase 9 (Governance) inline for tech-debt action |
   | Any stage flags P-049..P-053 HIGH/CRITICAL | → Phase 5d (Data/ML) inline |
   | Any stage receipt has CRITICAL RAID items | → Phase 9 (Governance — risk subroutine) inline |
   | Stage 5 verdict = FAIL after Phase 5e debug | → re-enter Phase 5e (max 2 cycles per regression budget) |
   | Stage 5 verdict = PASS but compliance < threshold | → Phase 5v audit sub-loop (max 5 audit cycles) |

3. **For each transition that fires**:
   ```
   a. Append to checkpoint.phase_transitions:
      { from_phase: <current>, to_phase: <target>, reason: <condition>, timestamp: now_iso8601() }
   b. Spawn the phase's appropriate agent (per AUTO-001 phase mapping):
      - Phase 5q → qa-engineer
      - Phase 5s → security-engineer
      - Phase 5i → infra-engineer
      - Phase 5d → data-engineer or ml-engineer
      - Phase 5v → auditor
      - Phase 5e → debugger
      - Phase 7 → orchestrator (with PHASE: RELEASE_PREP)
      - Phase 8 → sre, product-manager (PHASE: POST_LAUNCH)
      - Phase 9 → engineering-manager, technical-program-manager, staff-principal-engineer (PHASE: GOVERNANCE)
   c. Phase agent reads its dispatch-context (now phase-context) and produces structured findings.
   d. Write phase receipt to .orchestrate/<session>/phase-receipts/phase-<name>-<YYYYMMDD>-<HHMMSS>.json:
      { phase, started_at, completed_at, verdict, artifacts, next_phase }
   e. Process verdict.next_action:
      - "inject_into_stage": append phase findings to checkpoint.phase_findings.<target_stage>
      - "create_task": TaskCreate with appropriate dispatch_hint and blockedBy
      - "phase_block": set checkpoint.phase_gates.<stage> = phase_receipt_id
      - "informational": log only
   f. Append phase_receipt path to checkpoint.phase_receipts
   ```

4. **Proactive phase coverage**:

   After evaluating reactive transitions, run the proactive coverage sweep if `checkpoint.triage.process_scope.tier >= "medium"`. This ensures domain phases for scope-applicable processes get coverage even without explicit severity flags.

   ```
   IF checkpoint.triage.process_scope.tier != "trivial":
       FOR EACH applicable_phase in checkpoint.triage.process_scope.applicable_domains:
           IF applicable_phase NOT IN already_invoked_this_stage_transition:
               invoke_phase(applicable_phase)
               # Cap: maximum 2 proactive phase invocations per stage transition
   ```

5. **Phase gate enforcement**: Before proceeding to the next stage, check if any `phase_gates` block it:
   ```
   IF checkpoint.phase_gates contains key for next pending stage:
       display "[PHASE-GATE] Stage <N> blocked by phase {phase_receipt_id}"
       display "  Findings from {phase_name} must be addressed before proceeding"
       # Stage remains blocked until phase finding is addressed in a subsequent iteration
   ```

> **PHASE-LOOP-001**: All phase invocations are internal to auto-orchestrate. There is no Skill() dispatch to a separate command — phase agents are spawned per AUTO-001's phase mapping.

> **PHASE-LOOP-002**: Phase agents do NOT evaluate phase transitions themselves. They produce findings and return; the loop controller decides next phase.

**4.8d Domain Activation Review (AGENT-ACTIVATE-001)**:

After dispatch evaluation, check if the orchestrator reported domain agent activations in this iteration. Domain agent activation is handled BY the orchestrator (not the loop controller) per `_shared/protocols/agent-activation.md`. The loop controller's role here is to log and track activations in the checkpoint.

1. **Scan for new domain review artifacts**:
   ```
   new_reviews = glob(".orchestrate/<session>/domain-reviews/*-stage-*.md")
   known_reviews = flatten(checkpoint.domain_reviews.values())
   new_this_iteration = new_reviews - known_reviews
   ```

2. **Log activations**:
   ```
   IF new_this_iteration is non-empty:
       display "[DOMAIN-REVIEW] {len(new_this_iteration)} domain review(s) produced this iteration:"
       FOR EACH review IN new_this_iteration:
           agent_name = extract_agent_name(review.filename)  # e.g., "security-engineer" from "security-engineer-stage-2.md"
           stage = extract_stage(review.filename)
           display "  - {agent_name} reviewed Stage {stage} artifacts"
   ```

3. **Update checkpoint**:
   ```
   FOR EACH review IN new_this_iteration:
       agent_name = extract_agent_name(review.filename)
       stage = extract_stage(review.filename)
       
       checkpoint.domain_activations.append({
           "agent": agent_name,
           "stage": stage,
           "artifact_path": review.path,
           "timestamp": now_iso8601(),
           "iteration": checkpoint.iteration
       })
       
       IF agent_name NOT IN checkpoint.domain_reviews[stage]:
           checkpoint.domain_reviews[stage].append(agent_name)
   ```

4. **Inject domain review context for next orchestrator spawn**: If domain reviews exist for stages with pending tasks, include review summaries in the next orchestrator spawn prompt via the Domain Review Context section in Appendix C.

> **AGENT-ACTIVATE-001 boundary**: Domain agents are spawned BY the orchestrator during its execution, not by the loop controller. The loop controller only observes and logs the results. This preserves AUTO-001 (loop controller spawns only orchestrators).

**4.8e Workflow State Synchronization (WORKFLOW-SYNC-001)**:

After updating the checkpoint and domain review tracking, synchronize workflow state to `.pipeline-state/workflow/` for consumption by `/workflow-*` commands:

1. **Write task-board.json** (atomic write — write to `.tmp`, rename):
   ```json
   {
     "schema_version": "1.0.0",
     "source": "auto-orchestrate",
     "session_id": "<checkpoint.session_id>",
     "last_updated": "<now_iso8601()>",
     "iteration": "<checkpoint.iteration>",
     "pipeline_stage": "<current STAGE_CEILING>",
     "tasks": [
       // FOR EACH task IN TaskList():
       {
         "id": "<task.id>",
         "subject": "<task.subject>",
         "status": "<task.status>",
         "dispatch_hint": "<task.dispatch_hint>",
         "blockedBy": ["<task.blockedBy>"],
         "stage": "<infer_stage(task.dispatch_hint)>",
         "updated_at": "<task.updated_at>"
       }
     ],
     "stages_completed": "<checkpoint.stages_completed>",
     "terminal_state": "<checkpoint.terminal_state>"
   }
   ```

2. **Write focus-stack.json** (atomic write):
   ```json
   {
     "source": "auto-orchestrate",
     "session_id": "<checkpoint.session_id>",
     "focused_task_id": "<current in_progress task id, or null>",
     "focused_task_subject": "<current in_progress task subject, or null>",
     "focused_at": "<now_iso8601()>",
     "stack": ["<task_id for each in_progress task>"],
     "last_updated": "<now_iso8601()>"
   }
   ```

3. **Log**: `[WORKFLOW-SYNC] task-board.json updated (iteration {iteration}, {tasks_count} tasks, stage ceiling {STAGE_CEILING})`

> **WORKFLOW-SYNC-001**: This write is the single source of truth for task state while auto-orchestrate is active. `/workflow-dash` reads this file; `/workflow-focus` reads `focus-stack.json`. Both are read-only per WORKFLOW-SYNC-002.

**4.9 Mandatory stage gates**:
- **AUTO-004**: If Stage 3 done but 4.5/5/6 missing for 1+ iterations → `mandatory_stage_enforcement: true`, inject missing tasks.
- **Proactive injection**: For any mandatory stage at or below `STAGE_CEILING` absent from `stages_completed` with no pending/in-progress task, create it immediately with proper `blockedBy` chain:
  - Stage 0: `researcher`, no blockedBy
  - Stage 1: `product-manager`, blockedBy Stage 0
  - Stage 2: `spec-creator`, blockedBy Stage 1
  - Stage 4: `test-writer-pytest`, blockedBy Stage 3 (**optional** — inject only if product-manager produced test tasks)
  - Stage 4.5: `codebase-stats` + `refactor-analyzer`, blockedBy Stage 3
  - Stage 5: `validator` + `spec-compliance` (SPEC_PATH=`.orchestrate/<SESSION_ID>/stage-2/`), blockedBy Stage 4.5
  - Stage 6: `technical-writer`, blockedBy Stage 5

**4.9b Cadenced Meeting Triggers (MEETING-001)**:

For L/XL t-shirt-sized projects, fire iteration-boundary meetings autonomously. Cadence is taken from the Meetings & Ceremonies section above (L = every 5 iterations, XL = every 3, M and below = none).

```
IF checkpoint.triage.tshirt_size IN ["L", "XL"] AND checkpoint.iteration > 0:
    interval = 5 IF checkpoint.triage.tshirt_size == "L" ELSE 3

    IF checkpoint.iteration % interval == 0:
        # P-026 Daily Standup — always fires at boundary
        Log: "[MEETING] Iteration boundary at {iteration} — firing P-026 Daily Standup"
        Spawn orchestrator with PHASE: DAILY_STANDUP, ITERATION={iteration}
        # Receipt: meetings/meeting-p-026-daily-standup-iter-{iteration}-<TS>.json

        # P-020 Dependency Standup — only if cross-team impact present
        IF len(checkpoint.triage.cross_team_impact) > 0:
            Log: "[MEETING] cross_team_impact present — firing P-020 Dependency Standup"
            Spawn orchestrator with PHASE: DEPENDENCY_STANDUP, ITERATION={iteration}
            # Receipt: meetings/meeting-p-020-dependency-standup-iter-{iteration}-<TS>.json

        # P-029 Backlog Refinement — only if backlog has unrefined items
        unrefined_count = count tasks in task-board.json where (
          status == "pending" AND (acceptance_criteria is missing OR estimate is missing OR owner is missing)
        )
        IF unrefined_count > 0:
            Log: "[MEETING] {unrefined_count} unrefined backlog items — firing P-029 Backlog Refinement"
            Spawn product-manager with PHASE: BACKLOG_REFINEMENT, ITERATION={iteration}
            # Receipt: meetings/meeting-p-029-backlog-refinement-iter-{iteration}-<TS>.json

ELSE IF checkpoint.triage.tshirt_size NOT IN ["L", "XL"]:
    # Trivial / S / M tasks: no cadenced standups (cadence suppressed)
    pass
```

These meetings produce meeting receipts to `meetings/` and handover receipts to `handovers/` per MEETING-002 and HANDOVER-001. They run autonomously — no human gate.

**4.9c Phase 9 Trigger Evaluation (Continuous Governance)**:

Every iteration, evaluate Phase 9 sub-routine triggers and fire matching sub-routines autonomously. Phase 9 runs in parallel to the main flow — it does not block stage progression.

```
# Read latest codebase-stats output (if present from Stage 4.5)
codebase_stats_path = ".orchestrate/<session>/stage-4.5/codebase-stats.json"
tech_debt_score = read_field(codebase_stats_path, "tech_debt_score") OR 0
duplication_ratio = read_field(codebase_stats_path, "duplication_ratio") OR 0

# Count CRITICAL items in RAID log (P-074)
raid_log_path = ".orchestrate/<session>/raid-log.json"
critical_raid_count = count_lines_where(raid_log_path, severity == "CRITICAL")

# Cadence checks for L/XL projects
is_cadence_boundary = (
    checkpoint.triage.tshirt_size IN ["L", "XL"]
    AND checkpoint.iteration > 0
    AND checkpoint.iteration % (5 IF tshirt_size == "L" ELSE 3) == 0
)

phase_9_subroutines_to_fire = []

# Audit sub-routine — tech debt threshold OR duplication threshold
IF tech_debt_score > 30 OR duplication_ratio > 0.15:
    phase_9_subroutines_to_fire.append({
        "sub_routine": "audit",
        "reason": f"tech_debt={tech_debt_score}%, duplication={duplication_ratio}",
        "scope": "P-062..P-066 (audit hierarchy layers 1-5) + P-067, P-068 (IC/Squad layers) + P-069 (audit finding flow)"
    })

# Risk sub-routine — CRITICAL RAID items present
IF critical_raid_count > 0:
    phase_9_subroutines_to_fire.append({
        "sub_routine": "risk",
        "reason": f"{critical_raid_count} CRITICAL RAID items",
        "scope": "P-074 (RAID Log Maintenance), P-075 (Risk Register), P-076 (Pre-Launch CAB), P-077 (Quarterly Risk Review)"
    })

# Cadenced governance — fires on iteration boundary for L/XL projects
IF is_cadence_boundary:
    # Comms sub-routine — every cadence boundary
    phase_9_subroutines_to_fire.append({
        "sub_routine": "comms",
        "reason": f"cadence boundary at iteration {checkpoint.iteration}",
        "scope": "P-078 (OKR Cascade), P-079 (Stakeholder Updates), P-080 (Guild Standards), P-081 (DORA Metrics)"
    })

    # Capacity sub-routine — every other cadence boundary (less frequent)
    IF checkpoint.iteration % (2 * interval) == 0:
        phase_9_subroutines_to_fire.append({
            "sub_routine": "capacity",
            "reason": "cadenced capacity review",
            "scope": "P-082 (Quarterly Capacity Planning), P-083 (Shared Resource Allocation), P-084 (Succession Planning)"
        })

# Tech excellence sub-routine — fires when significant arch changes detected
IF checkpoint.iteration_history contains entries with `architectural_change: true`:
    phase_9_subroutines_to_fire.append({
        "sub_routine": "tech_excellence",
        "reason": "architectural change detected in iteration history",
        "scope": "P-085 (RFC), P-086 (Tech Debt Tracking), P-087 (Language Tier Policy), P-088 (Architecture Pattern Change), P-089 (Developer Experience Survey)"
    })

# Onboarding sub-routine — fires on session completion only (deferred to Phase 8 area)
# Skipped here; handled at Post-Termination per Phase 8 / Phase 9 onboarding integration.

# Fire all matching sub-routines
FOR EACH sub_routine_spec IN phase_9_subroutines_to_fire:
    Log: "[PHASE 9 TRIGGER] sub_routine={sub_routine_spec.sub_routine} fired — reason: {sub_routine_spec.reason}"
    Spawn orchestrator with PHASE: GOVERNANCE, SUB_ROUTINE={sub_routine_spec.sub_routine}, scope={sub_routine_spec.scope}
    # Receipt: phase-receipts/phase-9-governance-{sub_routine}-<TS>.json
    Append to checkpoint.phase_transitions:
      { from_phase: f"Stage iteration-{iteration}", to_phase: f"Phase 9 ({sub_routine_spec.sub_routine})",
        reason: sub_routine_spec.reason, timestamp: now_iso8601() }

# Cap: max 2 Phase 9 sub-routines per iteration boundary to avoid runaway governance noise
IF len(phase_9_subroutines_to_fire) > 2:
    Log: "[PHASE 9 CAP] {N} sub-routines triggered; firing top 2 by severity, deferring rest to next iteration"
    # Priority order: risk > audit > tech_excellence > capacity > comms > onboarding
```

Phase 9 sub-routines write phase receipts and handover receipts per MEETING-002 / HANDOVER-001 conventions. They run inline (autonomous) and do not block the main pipeline flow.

**4.10 Evaluate termination** (see Step 5).

**4.11 If NOT terminated** → return to Step 3.

---

## Step 5: Termination Conditions

**Pre-check — in_progress tasks block termination**: If ANY tasks have status `in_progress`, skip ALL termination checks and return to Step 3 (next iteration). Background agents are still working — the pipeline is neither complete, stalled, nor blocked. Display: `⚠ <N> task(s) still in_progress — skipping termination check, continuing loop`.

**Planning completion pre-condition**: Before evaluating execution pipeline termination, verify planning is complete:

```
planning_complete = (
    planning_skipped == true
    OR planning_stages_completed == ["P1", "P2", "P3", "P4"]
)

IF NOT planning_complete:
    # Cannot terminate — planning phase still active
    # Return to Step 3 to continue planning loop
    Display: "[PRE-RESEARCH-GATE] Planning incomplete — cannot evaluate termination"
    Return to Step 3
```

Evaluate in order (ONLY when zero tasks are `in_progress` AND planning is complete):

| # | Condition | Status |
|---|-----------|--------|
| 1 | All tasks completed AND `stages_completed` includes 0,1,2,4.5,5,6 (Stage 4 optional — see AUTO-002) AND (planning_stages_completed includes P1,P2,P3,P4 OR planning_skipped == true) | `completed` |
| 1a | All tasks completed BUT mandatory stages missing | Inject tasks, retry once. If still missing: `completed_stages_incomplete` |
| 2 | `iteration >= MAX_ITERATIONS` | `max_iterations_reached` |
| 3 | No progress for `STALL_THRESHOLD` consecutive iterations | `stalled` |
| 4 | All remaining tasks blocked AND zero `in_progress` | `all_blocked` |

**Stall detection**: Same pending+completed counts for 2 consecutive iterations = stall. However, `in_progress` tasks reset the stall counter (work is actively happening). `tasks_partial_continued` also resets counter.

**Thrashing detection (THRASH-001)**: Track a rolling window of state hashes (last 6 iterations). The state hash is computed from: `SHA-256(sorted task IDs + ":" + sorted task statuses + ":" + sorted stages_completed)`. If the current state hash matches ANY previous hash in the rolling window, the system is **thrashing** — alternating between states without making net progress. Thrashing is detected even when individual iteration counts change (which would evade the stall counter).

When thrashing is detected:
1. Log: `[THRASH-001] State hash collision detected — iteration <N> matches iteration <M>. System is thrashing.`
2. Increment `thrash_counter` in checkpoint
3. If `thrash_counter >= 2`: set terminal_state to `thrashing` and terminate
4. If `thrash_counter == 1`: log `[THRASH-WARN] First thrashing occurrence — attempting recovery` and inject a diagnostic task: "Analyze pipeline thrashing — identify conflicting changes between iterations <M> and <N>"

**Checkpoint additions**:
```json
{
  "thrash_counter": 0,
  "state_hash_window": [],
  "thrash_history": []
}
```

Add `thrashing` to the Terminal State Reference table as:
```
| `thrashing` | System alternating between states without net progress |
```

**In-progress ceiling (AO-INEFF-001)**: Track per-task `in_progress_iterations` count. If any task remains `in_progress` for 5 consecutive iterations without completing, treat it as failed: set status to `failed`, log `[AO-INEFF-001] Task #<id> "<subject>" stuck in_progress for 5 iterations — marking failed`, and do NOT let it reset the stall counter.

**Diminishing returns detection (DIMINISH-001)**: After each iteration, compute `progress_delta = tasks_completed_this_iteration / total_tasks`. Append to `progress_delta_window` (rolling window, last 5 entries). If ALL 5 entries are below 0.02 (2%) AND `iteration > 10`, fire the diminishing returns signal:
- Log: `[DIMINISH-001] Progress delta below 2% for 5 consecutive iterations — diminishing returns detected`
- Set `diminishing_returns_triggered: true` in checkpoint

**Cost ceiling detection (COST-CEIL-001)**: After each iteration, check: if `iteration > 0.7 * max_iterations`, fire the cost ceiling signal:
- Log: `[COST-CEIL-001] Consumed <iteration>/<max_iterations> iterations (>70%) — approaching cost ceiling`
- Set `cost_ceiling_triggered: true` in checkpoint

**Multi-signal termination evaluation**: After evaluating all individual signals (stall, thrash, diminishing returns, cost ceiling), count active signals:
```
active_signals = []
IF stall_counter >= STALL_THRESHOLD: active_signals.append("STALL")
IF thrash_counter >= 1: active_signals.append("THRASH")
IF diminishing_returns_triggered: active_signals.append("DIMINISH")
IF cost_ceiling_triggered: active_signals.append("COST_CEILING")

IF len(active_signals) >= 2:
    terminal_state = "auto_terminated"
    Log: [MULTI-SIGNAL] 2+ signals active: {active_signals}. Auto-terminating.
ELSE IF len(active_signals) == 1:
    Log: [SIGNAL-WARN] 1 signal active: {active_signals[0]}. Injecting diagnostic task.
    # Inject diagnostic task but do NOT terminate yet
```

**Checkpoint additions for 4-signal model**:
```json
{
  "diminishing_returns_triggered": false,
  "progress_delta_window": [],
  "cost_ceiling_triggered": false
}
```

Add `auto_terminated` to the Terminal State Reference table:
```
| `auto_terminated` | 2+ termination signals active simultaneously |
```

### Post-Termination Sprint Closure → Phase 7 / Phase 8 (Release + Post-Launch)

After `terminal_state == "completed"` is determined, run the Sprint Closure sequence (P-027 Sprint Review → P-028 Sprint Retrospective → P-029 Backlog Refinement) inline, **then** Phase 7 (Release Prep — human-gated) and Phase 8 (Post-Launch). The sprint closure meetings run autonomously per MEETING-001 (Multi-Agent Sync); Phase 7 pauses for the release-readiness human gate (and the cab-review gate when CAB-GATE-001 conditions are met).

```
IF terminal_state == "completed":

    # Sprint Closure Sequence — runs unconditionally after Stage 6 success
    # (autonomous per MEETING-001; no human pause)

    # P-027 Sprint Review (Multi-Agent Sync)
    Log: "[MEETING] P-027 Sprint Review starting"
    Spawn orchestrator with PHASE: SPRINT_REVIEW (the orchestrator coordinates
      engineering-manager + product-manager + software-engineer per the SPRINT_REVIEW
      template in agents/orchestrator.md).
    Output: meetings/meeting-p-027-sprint-review-<TS>.json
    Append to checkpoint.phase_transitions: { from_phase: "Stage 6", to_phase: "Sprint Review" }

    # P-028 Sprint Retrospective (Multi-Agent Sync)
    Log: "[MEETING] P-028 Sprint Retrospective starting"
    Spawn orchestrator with PHASE: SPRINT_RETRO (incoming handover from Sprint Review).
    Output: meetings/meeting-p-028-sprint-retro-<TS>.json
    Append to checkpoint.phase_transitions: { from_phase: "Sprint Review", to_phase: "Sprint Retro" }

    # P-029 Backlog Refinement (Async Single-Agent)
    Log: "[MEETING] P-029 Backlog Refinement starting"
    Spawn product-manager with PHASE: BACKLOG_REFINEMENT (incoming handover from Sprint Retro).
    Output: meetings/meeting-p-029-backlog-refinement-<TS>.json
    Append to checkpoint.phase_transitions: { from_phase: "Sprint Retro", to_phase: "Backlog Refinement" }
    # Phase 7: Release Prep — runs when release_flag is set
    IF checkpoint.release_flag == true:
        Log: "[PHASE 7] Release flag set — running Release Prep inline"

        # CAB Review prelude (P-076) — only fires for HIGH/CRITICAL risk changes (CAB-GATE-001)
        # CAB co-agent (TPM) classifies risk; if HIGH or CRITICAL, run cab-review human gate.
        Spawn orchestrator with PHASE: CAB_REVIEW (the orchestrator coordinates TPM as chair
          plus security-engineer, sre, product-manager, engineering-manager — produces
          CAB Decision Record at .orchestrate/<session>/phase-7/cab-decision-record.md
          with risk_classification and recommended_verdict).

        risk_classification = read_field(.orchestrate/<session>/phase-7/cab-decision-record.md, "risk_classification")
        IF risk_classification IN ["HIGH", "CRITICAL"]:
            Log: "[CAB-GATE] Risk classified {risk_classification} — firing cab-review human gate"

            # HUMAN GATE — cab-review (HUMAN-GATE-001 #7)
            gate_result = run_gate(
              gate_id = "cab-review",
              recommended_verdict = read_field(cab-decision-record.md, "recommended_verdict"),
              evaluator_breakdown = {
                risk_classification: risk_classification,
                cab_chair: "technical-program-manager",
                participants: ["technical-program-manager", "security-engineer", "sre",
                               "product-manager", "engineering-manager"],
                cab_decision: read_field(cab-decision-record.md, "decision"),
                conditions: read_field(cab-decision-record.md, "conditions")
              },
              artifact_path = ".orchestrate/<session>/phase-7/cab-decision-record.md",
              summary = "CAB Decision: {decision}. Risk: {risk_classification}. Conditions: {N}. Approval options: approve to proceed to release-readiness, reject to remediate, stop to terminate."
            )

            IF gate_result == "REJECTED":
                Log: "[CAB-GATE] CAB REJECTED by user — feedback: {approval.feedback}"
                Append to checkpoint.phase_transitions: { from_phase: "Phase 7", to_phase: "Stage 5", reason: "cab_rejected" }
                Skip release-readiness gate; re-enter Stage 5 with feedback.
                CONTINUE outer loop

            IF gate_result IN ["STOP", "TIMEOUT"]:
                Set checkpoint.terminal_state = "gate_rejected" OR "gate_timeout"
                Skip Phase 8.
                BREAK

            # gate_result == "APPROVED" → conditions (if any) become blocking findings on
            # the release-readiness gate; loop controller carries them forward
            checkpoint.cab_conditions = read_field(cab-decision-record.md, "conditions")
        ELSE:
            Log: "[CAB-SKIP] Risk classified {risk_classification} — cab-review gate not required"

        # Phase 7 main RELEASE_PREP coordination (always runs after CAB resolution)
        Spawn orchestrator with PHASE: RELEASE_PREP. The orchestrator coordinates:
          - qa-engineer: performance testing (P-035)
          - infra-engineer: CI/CD verification + provisioning (P-044..P-047)
          - technical-program-manager: production release management (P-048)
          - sre: monitoring, alerting, SLO dashboards (P-054), runbooks (P-059)
          - technical-writer: release notes (P-061)
        Phase 7 produces: release-readiness-artifact.md (checklist of all P-035, P-044..P-048,
        P-059, P-061 items with acknowledgment status; cab_conditions from above are blocking
        findings if present).

        Auto-evaluate Release Readiness:
          recommended_verdict = "approved" IF all gate-critical items acknowledged ELSE "rejected"
          evaluator_breakdown = {
            performance_testing_complete: <bool>,
            cicd_verified: <bool>,
            slo_dashboards_present: <bool>,
            runbooks_published: <bool>,
            release_notes_drafted: <bool>,
            cab_review_status: <"approved" | "pending" | "n/a">,
            critical_security_findings_resolved: <bool>
          }

        # HUMAN GATE — release readiness (HUMAN-GATE-001 #7)
        # Required before any deployment-affecting action proceeds.
        gate_result = run_gate(
          gate_id = "release-readiness",
          recommended_verdict = recommended_verdict,
          evaluator_breakdown = evaluator_breakdown,
          artifact_path = ".orchestrate/<session>/phase-7/release-readiness-artifact.md",
          summary = "Release readiness checklist complete. Recommended: {recommended_verdict}. Approval options: approve to proceed to Phase 8, reject to remediate (returns to Stage 5 for fixes), stop to terminate."
        )

        IF gate_result == "APPROVED":
            Write phase receipt: .orchestrate/<session>/phase-receipts/phase-7-release-<timestamp>.json with verdict="APPROVED"
            Append to checkpoint.phase_transitions: { from_phase: "Stage 6", to_phase: "Phase 7" }
            Log: "[PHASE 7] Release Readiness APPROVED by user; proceeding to Phase 8"

        ELSE IF gate_result == "REJECTED":
            Log: "[PHASE 7] Release Readiness REJECTED — feedback: {approval.feedback}"
            # Re-enter Stage 5 with feedback as failure context to remediate
            Append to checkpoint.phase_transitions: { from_phase: "Phase 7", to_phase: "Stage 5", reason: "release_rejected" }
            Skip Phase 8; the loop controller will re-evaluate after remediation.

        ELSE IF gate_result IN ["STOP", "TIMEOUT"]:
            Set checkpoint.terminal_state = "gate_rejected" OR "gate_timeout"
            Skip Phase 8.

    # Phase 8: Post-Launch — runs only if Phase 7 was approved OR session ran in operations mode
    IF (Phase 7 completed AND gate_result == "APPROVED") OR checkpoint.triage.mode == "post_launch":
        Log: "[PHASE 8] Running Post-Launch processes inline"
        Spawn orchestrator with PHASE: POST_LAUNCH. The orchestrator coordinates:
          - sre: SLO monitoring (P-054), incidents (P-055), on-call (P-057)
          - product-manager: project post-mortem (P-070), OKR retrospective (P-072),
            outcome measurement at 30/60/90 days (P-073)
          - engineering-manager: quarterly process health review (P-071)
        Write phase receipt: .orchestrate/<session>/phase-receipts/phase-8-post-launch-<timestamp>.json
        Append to checkpoint.phase_transitions: { from_phase: "Phase 7", to_phase: "Phase 8" }

# Write phase summary
checkpoint.phase_summary = {
    total_phases_invoked: len(checkpoint.phase_transitions),
    phases_completed: list(set(t.to_phase for t in checkpoint.phase_transitions)),
    phase_receipts: list(checkpoint.phase_receipts)
}
```

### On Termination

Set `terminal_state` and `status`, update parent task, display:

```
## Auto-Orchestration Complete
**Session**: <session_id> | **Scope**: <resolved> | **Status**: <terminal_state> | **Iterations**: N/max

### Planning Phase
P1 <✓/✗> → P2 <✓/✗> → P3 <✓/✗> → P4 <✓/✗> (or [SKIPPED] if planning_skipped)

### Execution Pipeline
Stage 0 <✓/✗> → Stage 1 <✓/✗> → ... → Stage 6 <✓/✗>

### Completed Tasks
- ✓ [#id] <subject> (<agent>, Stage N)

### Remaining Tasks (if any)
- ○ [#id] <subject> (<agent>, Stage N) — blocked by #id

### Mandatory Stages
| Stage | Status | Task |
|-------|--------|------|
| 0 (researcher) | ✓/✗ | #<id> <subject> |
| 1 (product-manager) | ✓/✗ | #<id> <subject> |
| 2 (spec-creator) | ✓/✗ | #<id> <subject> |
| 4.5 (codebase-stats) | ✓/✗ | #<id> <subject> |
| 5 (validator) | ✓/✗ | #<id> <subject> |
| 6 (technical-writer) | ✓/✗ | #<id> <subject> |

### Terminal State Reference

| Value | Meaning |
|-------|---------|
| `completed` | All tasks done, all mandatory stages covered |
| `completed_stages_incomplete` | All tasks done but mandatory stages missing after retry |
| `max_iterations_reached` | Hit MAX_ITERATIONS limit |
| `stalled` | No progress for STALL_THRESHOLD consecutive iterations |
| `gate_rejected` | A human gate received `decision: "stop"` from the user |
| `gate_timeout` | A human gate exceeded `gate_timeout_seconds` without an approval file |
| `all_blocked` | All remaining tasks blocked, zero in_progress |
| `user_stopped` | User manually cancelled |
| `thrashing` | System alternating between states without net progress |
| `debug_loop_exhausted` | Phase 5e debug sub-loop hit max_iterations without resolving all errors |
| `auto_terminated` | 2+ termination signals active simultaneously (MULTI-SIGNAL) |

### Git Commit Instructions
> Auto-orchestrate NEVER commits automatically. Review and commit manually.
**Files modified**: [from software-engineer DONE blocks]
**Suggested commits**: [Git-Commit-Message values]

### Phase Invocation Summary
| Metric | Count |
|--------|-------|
| Internal phases invoked | <phase_summary.total_phases_invoked> |
| Phase receipts written | <len(phase_summary.phase_receipts)> |
| Phases completed | <len(phase_summary.phases_completed)> |

### Domain Agent Activation Summary
| Metric | Value |
|--------|-------|
| Total activations | <len(checkpoint.domain_activations)> |
| Agents activated | <unique agents from checkpoint.domain_activations> |
| Stages with reviews | <stages with non-empty checkpoint.domain_reviews> |

{{#if checkpoint.domain_activations is non-empty}}
| Stage | Agent | Rule | Artifact |
|-------|-------|------|----------|
{{#for each activation in checkpoint.domain_activations}}
| {{activation.stage}} | {{activation.agent}} | {{activation.rule_id}} | {{activation.artifact_path}} |
{{/for each}}
{{/if}}

### Iteration Timeline
| # | Completed | Running | Pending | Tasks Worked On |
|---|-----------|---------|---------|-----------------|
| 1 | 0 | 0 | 7 | Proposed all pipeline tasks |
| 2 | 0 | 1 | 6 | ▶ #2 Research (Stage 0) |
| 3 | 1 | 0 | 6 | ✓ #2 Research (Stage 0) |
```

### Pipeline Chain Completion (GAP-PIPE-004)

On successful termination (`completed` status), check for handoff receipt and update the session index for traceability across multiple auto-orchestrate runs in the same project:

1. Check if `.orchestrate/<session-id>/handoff-receipt.json` exists
2. If found and the receipt records a continuation chain (e.g., a follow-up auto-orchestrate session was registered):
   - Read `.sessions/index.json`
   - Add or update `pipeline_chains` array entry:
     ```json
     {
       "chain_id": "chain-<YYYYMMDD>-<slug>",
       "from_session": "<current-session-id>",
       "to_session": "<next-session-id-if-known>",
       "trigger": "completion",
       "status": "pending",
       "created_at": "<ISO-8601>"
     }
     ```
   - Atomic write to `.sessions/index.tmp.json`, then rename
   - Display: `[CHAIN] Continuation registered for next auto-orchestrate session`
3. If no handoff receipt or no continuation registered: skip silently (standalone session)

### Return Path Completion (GAP-PIPE-005)

After displaying the termination summary, update the handoff receipt for traceability:

1. Check if `.orchestrate/<session-id>/handoff-receipt.json` exists
2. If found:
   - Update `auto_orchestrate_status` to `"completed"` (or `"failed"` on non-successful termination)
   - Update `completed_timestamp` to current ISO-8601 timestamp
   - Set `return_path.stage6_artifacts_path` to `".orchestrate/<session-id>/stage-6/"`
   - Set `return_status` to `terminal_state` value (e.g., `"completed"`, `"stalled"`, `"max_iterations_reached"`)
   - Set `return_at` to current ISO-8601 timestamp
   - Set `return_summary` to the termination summary (first 500 characters of the summary text)
   - Atomic write (write to `.tmp` then rename)
3. If no handoff receipt: skip silently (standalone session — no chain to update)

**Updated handoff receipt fields on termination**:
```json
{
  "auto_orchestrate_status": "completed",
  "completed_timestamp": "<ISO-8601>",
  "return_path": {
    "stage6_artifacts_path": ".orchestrate/<session-id>/stage-6/"
  },
  "return_status": "<terminal_state>",
  "return_at": "<ISO-8601>",
  "return_summary": "<first 500 chars of termination summary>"
}
```

---

## Crash Recovery Protocol

Runs at the START of every invocation:

1. Ensure `.orchestrate/` and `~/.claude/sessions/` exist
2. Scan for `"status": "in_progress"` checkpoints
3. If found: same/no input → **Resume**; different input → supersede, start fresh
4. If not found → proceed normally
5. Cross-command awareness: read `.sessions/index.json` (if present) to detect active sessions from other commands. Log any `in_progress` cross-command sessions found. See `commands/SESSIONS-REGISTRY.md`.

### Resume

1. Read `task_snapshot` (skip if absent for backward compat)
2. If `TaskList` populated: use live state. If empty AND snapshot non-empty: restore tasks (create completed as completed, pending as pending, set up `blockedBy`; log `[WARN]` on failures)
3. Display recovery summary with restored task board (same format as Step 3c)
4. Resume from `iteration + 1`, skip Step 1

---

## Known Limitations

### GAP-CRIT-001: Task Tool Availability

Subagents lack TaskCreate/TaskList/TaskUpdate/TaskGet. **Workaround**: Auto-orchestrate acts as task management proxy — subagents write to `proposed-tasks.json`, auto-orchestrate creates tasks (Step 4.2), current state passed in spawn prompt, orchestrators return `PROPOSED_ACTIONS`.

### .orchestrate/ Folder Structure

```
.orchestrate/<session-id>/
├── planning/                      # P-series planning artifacts
│   ├── P1-intent-brief.md
│   ├── P2-scope-contract.md
│   ├── P3-dependency-charter.md
│   ├── P4-sprint-kickoff-brief.md
│   └── planning-receipt.json      # Combined receipt for all planning stages
├── stage-{0,1,2,3,4,4.5,5,6}/     # Per-stage output
└── proposed-tasks.json            # Task proposals (written by orchestrator FIRST)
```

---

## Appendix A: Backend Scope Specification

> Included in enhanced prompt when `layers` contains `"backend"`.

### Task
Implement all backend features to production-ready state, then audit and fully integrate. Applies to both **greenfield** (build from scratch) and **existing** (complete and fix) codebases.

- **Greenfield**: Design and build the full backend — models, migrations, services, controllers, routes, authentication, authorization, seed data, and configuration. Every feature must be fully implemented with real persistence and real integrations.
- **Existing**: Complete all partial features, replace all simulations/placeholders/in-memory workarounds, fix every gap and integration issue.

No in-memory workarounds, no simulations, no fake data, no placeholder logic. Everything uses real implementations with proper persistence.

### Implementation Quality Criteria (for Stage 3 — NOT a pipeline sequence)

> **IMPORTANT**: These are quality requirements for the software-engineer (Stage 3) and validator (Stage 5).
> They are NOT pipeline stages. The pipeline sequence is always: Stage 0 (Research) -> 1 (Product Management) -> 2 (Specifications) -> 3 (Implementation) -> 4.5 (Codebase Stats) -> 5 (Validation) -> 6 (Documentation).

- **Branch** — Create a feature branch.

- **Implement All Features** — Build or complete every backend feature:
   - **Greenfield**: Create all models, migrations, services, controllers, routes, auth, middleware, seed data, config from scratch.
   - **Existing**: Walk through every module and complete partial/stubbed features.
   - Write real business logic — no placeholders, no TODOs.
   - Create all API endpoints, services, models, migrations.
   - Implement error handling, input validation, response formatting.
   - Wire all dependencies, database connections, service integrations.
   - Every feature must have a complete data path from API request -> persistent storage -> response.
   - Build missing controllers/routes for defined models. Implement real logic for mock-returning routes. Complete missing CRUD operations.

- **Full Codebase Audit** — After implementation, assess every module:
   - Fully implemented and functional end-to-end?
   - Missing validations, broken logic, incomplete integrations?
   - All API endpoints exposed, documented, working?
   - Any in-memory storage, simulated data, mock services, placeholder logic?
   - Any remaining TODO/FIXME/HACK/PLACEHOLDER comments?

- **Eliminate All Simulations** — Replace every instance of:
   - In-memory stores -> real persistent storage
   - Simulated/mocked service calls -> real integrations
   - Hardcoded/fake/sample data -> real data flows
   - Placeholder/stub logic -> full implementations
   - Every data path must survive restarts.

- **Fix All Gaps** — Address every remaining issue:
   - Broken configs, missing env vars, incomplete integrations
   - Validation gaps, bugs, logic errors
   - Database migrations — up to date and clean
   - Scripts (seed, setup, utility) must all work
   - Complete any still-partial features
   - Default users, roles, groups, permissions — functional seed data
   - Startup integrity — no errors on restart/cold boot
   - Service accounts and inter-service credentials working

- **Clean Build** — All build processes complete with zero errors, zero warnings.

- **Verify End-to-End** — Entire backend running, all features operational, data persists across restarts.

### Backend Constraints
- Implement-then-audit: build/complete all features first, then audit and fix.
- **Greenfield**: Build every module — don't skip because "nothing to audit."
- **Existing**: Scope covers every module and feature.
- Zero tolerance for in-memory storage, simulations, mock data, placeholders.
- All API responses use consistent formats (status codes, error shapes, pagination).

---

## Appendix B: Frontend Scope Specification

> Included in enhanced prompt when `layers` contains `"frontend"`.

### Task
Implement all frontend features to production-ready state, then audit and fully integrate. Applies to both **greenfield** and **existing** frontends.

- **Greenfield**: Build the complete frontend — app shell, navigation, routing, auth flows, every page/form/view to consume all backend APIs. Set up project structure, component library, state management, API client from scratch.
- **Existing**: Complete all partial pages/components, replace mock data/placeholder screens with real API integrations, fix all gaps.

The frontend must consume all backend API endpoints. No fake data, no mock APIs, no placeholder screens. **Primary design goal**: a 10-year-old child could use this system without supervision or training.

### Core Design Principles

#### 1. Minimum Typing, Maximum Selection
- **Dropdowns/Select boxes** for every field with known values — load from backend API.
- **Checkboxes** for booleans, toggles, multi-select.
- **Radio buttons** for small mutually exclusive choices.
- **Date/Time pickers** for all date/datetime/time fields — never manual typing.
- **Toggle switches** for enable/disable, active/inactive states.
- **Auto-complete/searchable dropdowns** for large lists.
- **Sliders** for numeric ranges. **Colour pickers** for colour fields. **File upload drag-and-drop** for attachments.
- **Text boxes only when unavoidable** (descriptions, names, notes, search). If a value exists in the system, it must be selected, not typed.

#### 2. Bulk Operations
Every list and table must support:
- **Multiple delete** with confirmation dialog.
- **Multiple create** / batch creation where applicable.
- **Select All / Deselect All** checkbox on headers.
- **Bulk status change**, **bulk assign**, **bulk export** (CSV, PDF, etc.).
- **Bulk actions toolbar** — floating/sticky when items selected.

#### 3. Tabs for Logical Grouping
- Use tabbed layouts when a page has multiple logical sections (Details, Related Items, History, Settings).
- Each tab loads data independently with loading indicator.
- Active tab reflected in URL for bookmarking/sharing.

#### 4. Pre-load Everything from the Backend
- Fetch all dropdown options, reference data, lookups on page load.
- Show loading states (spinners, skeletons, shimmer).
- Cache reference data within session. Display human-readable labels everywhere — not IDs/UUIDs.
- Dropdown options show relevant context (e.g., "John Smith — Admin").

#### 5. Child-Friendly Usability
- **Clear, simple labels** — no jargon, abbreviations, or technical terms.
- **Tooltips/help icons (?)** on every field with plain-language explanations.
- **Inline validation** with friendly messages (e.g., "Please pick a role" not "ValidationError: role_id null").
- **Confirmation dialogs** before destructive/irreversible actions.
- **Success/failure toast notifications** for every action.
- **Undo** where feasible (brief "Undo" option after delete).
- **Consistent layout** — same patterns everywhere (list -> detail -> edit -> back).
- **Breadcrumbs** on every page.
- **Large, clearly labelled buttons** — primary prominent, secondary subdued, destructive red.
- **Empty states** with friendly message and "Create Your First [Item]" button.
- **Search and filter bars** on every list (prefer dropdown filters over free-text).
- **Pagination** with sensible defaults and page size options.
- **Responsive design** (desktop, tablet, mobile).
- **Keyboard navigation** for all interactive elements.
- **Consistent iconography** alongside text labels (trash + "Delete", pencil + "Edit").
- **No dead ends** — every page has a clear next action or navigation.
- **Wizard/stepper flows** for complex multi-step creation with progress indicators.

#### 6. User Context in the Frontend
- Show/hide features based on logged-in user's **roles and permissions** from backend.
- Pre-fill current user info where relevant.
- Display user name, role, avatar in header.
- Filter data views by access level.
- **Disable or hide** actions the user lacks permission for — never show buttons that return 403.
- Personalised dashboard by role.
- Handle token expiry, session timeout, re-auth gracefully.

### Frontend Implementation Quality Criteria (for Stage 3 — NOT a pipeline sequence)

> **IMPORTANT**: These are quality requirements for the software-engineer (Stage 3) and validator (Stage 5).
> They are NOT pipeline stages. The pipeline sequence is always: Stage 0 (Research) -> 1 (Product Management) -> 2 (Specifications) -> 3 (Implementation) -> 4.5 (Codebase Stats) -> 5 (Validation) -> 6 (Documentation).

- **Map Every Feature to UI** — For every backend endpoint/module, identify every screen, form, list, detail view, and interaction needed.

- **Build All Pages** — For each feature:
   - **List/Table view**: search bar, dropdown filters, column sorting, bulk checkboxes, bulk toolbar, pagination, empty state.
   - **Create form**: dropdowns, checkboxes, date pickers, toggles, auto-complete. Text inputs only where unavoidable. Inline validation, help tooltips.
   - **Edit form**: same as create, pre-populated from API.
   - **Detail/View page**: read-only with tabs for logical sections, related data, activity history, metadata.
   - **Delete**: single with confirmation, bulk via checkbox selection.

- **Connect to Backend APIs** — Every page calls real endpoints, handles loading/error/empty/forbidden states, submits real data. No fake data, no mocked calls, no hardcoded values.

- **Navigation and Layout** — Complete application shell:
   - Sidebar/top nav grouped logically. Menu visibility by roles/permissions. Breadcrumbs everywhere.
   - Global search if applicable. User profile menu with logout, settings, profile.

- **Test End-to-End** — Every user flow works through to backend persistence. Every CRUD, bulk action, filter, and search works against the real backend.

### Frontend Constraints
- Every feature/endpoint gets a complete, fully functional UI.
- **Greenfield**: Build entire frontend from scratch — don't skip features.
- **Existing**: Complete and fix every page and component.
- Zero fake data, mock APIs, placeholder screens.
- Every dropdown/list/selection loads from backend API.
- Minimise text inputs — if a value can be selected, use a selection component.
- Bulk operations on every list view.
- Tabs wherever a page has multiple logical sections.
- Usable by a child. Plain language only. Visual feedback for every action.
- Permission-gated UI — never show what the user cannot use.

---

## Appendix C: Orchestrator Spawn Prompt Template

Use `Agent(subagent_type: "orchestrator", max_turns: 30)` with this prompt:

```
## MANDATORY FIRST ACTION (before boot)
Write `.orchestrate/<SESSION_ID>/proposed-tasks.json` atomically: write to `.orchestrate/<SESSION_ID>/proposed-tasks.tmp.json` first, then rename to `proposed-tasks.json`. This prevents partial reads if auto-orchestrate reads during write. If no new tasks: write `{"session_id": "<SESSION_ID>", "iteration": <N>, "tasks": []}`.

Format:
```json
{
  "session_id": "<SESSION_ID>",
  "iteration": <N>,
  "tasks": [
    {"subject": "...", "description": "...", "activeForm": "...", "stage": 0, "dispatch_hint": "researcher", "blockedBy": []},
    {"subject": "...", "description": "...", "activeForm": "...", "stage": 1, "dispatch_hint": "product-manager", "blockedBy": ["<stage-0-task-subject>"]},
    {"subject": "...", "description": "...", "activeForm": "...", "stage": 2, "dispatch_hint": "spec-creator", "blockedBy": ["<stage-1-task-subject>"]}
  ]
}
```
**CRITICAL**: Every task for Stage N (N > 0) MUST include `blockedBy` referencing Stage N-1 task(s). Tasks without chains will be auto-fixed or rejected.

All output files: `YYYY-MM-DD_<descriptor>.<ext>`.

## Auto-Orchestration Context

PARENT_TASK_ID: <parent_task_id>
SESSION_ID: <session_id>
ITERATION: <N> of <max_iterations>
SCOPE: <resolved scope>
SCOPE_LAYERS: <layers array>
STAGE_CEILING: <calculated ceiling>
MANIFEST_PATH: ~/.claude/manifest.json
MANIFEST_INJECTION: <"full" | "digest"> (per MANIFEST-DIGEST-001)
GATE_STATE: <current gate state or "not_enforced">
PROJECT_TYPE: <greenfield|existing|continuation>
PROCESS_SCOPE_TIER: <trivial|medium|complex>
PROCESS_DOMAIN_FLAGS: <domain flags array>
PROCESS_ACTIVE_CATEGORIES: <active category numbers>
PROCESS_DOMAIN_GUIDES: <enabled domain guide commands>
RESEARCH_DEPTH: <minimal|normal|deep|exhaustive>
RESEARCH_DEPTH_SOURCE: <explicit|handoff|triage-default|escalated|fallback>
RESEARCH_DEPTH_ESCALATED_BY: <list or "none">

**RESEARCH_DEPTH values** (resolved via RESEARCH-DEPTH-001, Step 0h-pre):
- `"minimal"` — Cache-first; single CVE query; 1-page summary. Fast-path trivial only.
- `"normal"` — 3+ WebSearch queries; full RES-* contract (CVEs, Versions, Risks & Remedies). Current default.
- `"deep"` — 10+ queries clustered by sub-topic; 2+ independent sources per HIGH finding; production incident patterns.
- `"exhaustive"` — Domain-partitioned research (security / perf / ops / UX); opt-in for regulated/high-risk work.

If `RESEARCH_DEPTH` is `null` (legacy session on resume), substitute `"normal"` and log `[RESEARCH-DEPTH-RESUME]`.

**GATE_STATE values**:
- `"not_enforced"` — No `.gate-state.json` found; organizational gates not active
- `"gate_1_passed"` — Gate 1 (Intent Review) passed; Stage 0 unlocked
- `"gate_2_passed"` — Gates 1-2 passed; Stages 0-2 unlocked
- `"gate_3_passed"` — Gates 1-3 passed; Stages 0-3 unlocked
- `"gate_4_passed"` — All gates passed; full pipeline unlocked
- `"gate_N_blocked"` — Stage blocked due to missing gate; see STAGE_CEILING

**PROJECT_TYPE values**:
- `"greenfield"` — New project (< 5 commits AND < 10 source files)
- `"existing"` — Existing project with established codebase
- `"continuation"` — Continuation of a prior orchestration session

## STAGE_CEILING — HARD STRUCTURAL LIMIT
╔══════════════════════════════════════════════════════════════╗
║  STAGE_CEILING = <ceiling>                                   ║
║                                                              ║
║  MUST NOT: Spawn agents above ceiling, do work above         ║
║  ceiling, propose tasks without blockedBy chains,            ║
║  rationalize skipping ahead.                                 ║
║                                                              ║
║  MAY: Propose future-stage tasks WITH blockedBy chains,      ║
║  spawn agents at/below ceiling, advance current stage.       ║
║                                                              ║
║  0=research only, 1=+architect, 2=+specs, 3=+impl,          ║
║  4.5=+stats, 5=+validation, 6=+docs.                        ║
║  Stages above ceiling are STRUCTURALLY BLOCKED.              ║
╚══════════════════════════════════════════════════════════════╝

## Scope Context
{{#if scope != "custom"}}
Only work on layers in SCOPE_LAYERS.
- backend: Backend modules, services, APIs, migrations. Do NOT modify frontend.
- frontend: Frontend pages, components, forms, API integrations. Do NOT modify backend (except reading API contracts).
- fullstack: Both in scope. Backend generally precedes frontend.
Follow scope specifications in Enhanced Prompt precisely.
{{else}}
No scope restriction — follow the enhanced prompt as written.
{{/if}}

## Process Scope (PROCESS-SCOPE-001)

Process scope tier: **{{PROCESS_SCOPE_TIER}}**
Domain flags: {{PROCESS_DOMAIN_FLAGS}}
Active categories: {{PROCESS_ACTIVE_CATEGORIES}}
Domain guides enabled: {{PROCESS_DOMAIN_GUIDES}}

When evaluating process injection hooks from `processes/process_injection_map.md`, only fire hooks whose `scope_condition` is met by the current process scope tier. Hooks with `domain_flag` requirements only fire if that flag is in PROCESS_DOMAIN_FLAGS.

At each stage transition, consult the expanded injection map for applicable processes:
- **Core hooks** (scope_condition: "all"): Always fire
- **MEDIUM hooks**: Fire only if PROCESS_SCOPE_TIER is "medium" or "complex"
- **COMPLEX hooks**: Fire only if PROCESS_SCOPE_TIER is "complex"
- **Domain-conditional hooks**: Fire only if PROCESS_SCOPE_TIER is "complex" AND the required domain_flag is active

Log applicable processes as `[PROCESS-INJECT]` or `[PROCESS-INFO]` per the injection map's action types.

### Slim Injection (`optimizations.process_injection_slim`)

When `checkpoint.optimizations.process_injection_slim == true` (default for new sessions), the spawn-prompt builder MUST inject only the *fired* hooks for the current stage/scope, not the full injection map. Algorithm:

```
all_hooks = parse_injection_map("processes/process_injection_map.md")
eligible = [h for h in all_hooks if h.scope_condition matches PROCESS_SCOPE_TIER
                                    and (not h.domain_flag or h.domain_flag in PROCESS_DOMAIN_FLAGS)
                                    and (not h.stage or h.stage == current_stage)]
fired = [h for h in eligible if h.action != "skip"]
inject_into_spawn_prompt(fired)  # ~200 tok per hook × ~5 hooks = ~1k tok vs full ~3k

log(f"[INJECT-AUDIT] eligible={len(eligible)} fired={len(fired)} injected={len(fired)} "
    f"stage={current_stage} scope_tier={PROCESS_SCOPE_TIER}")
```

**Safety guard**: If `len(eligible) > 0` AND `len(fired) == 0`, log `[INJECT-AUDIT-WARN] eligible hooks but none fired — possible silent under-injection bug, scope=<tier> stage=<N>`. This surfaces a regression where the filter accidentally drops every hook.

**Behavior with flag off**: builder injects the full process injection map (~3k tok) regardless of fired status — legacy verbose mode for compatibility.

**Token saving**: ~2k tokens saved per stage spawn × ~25 spawns per session ≈ ~50k saved.

## Phase Findings (from internal phase invocations)

{{#if phase_findings[STAGE_CEILING] is non-empty}}
Internal phases have produced findings relevant to the current stage. Address these in your work:

{{#for each entry in phase_findings[STAGE_CEILING]}}
### [PHASE-{{entry.phase}}] {{entry.phase_name}} findings
**Severity**: {{entry.severity_max}}
**Summary**: {{entry.result_summary}}
**Action required**: {{entry.next_action_instruction}}
**Artifacts**: {{entry.artifacts}}
{{/for each}}

These findings were produced by internal domain phases (5q/5s/5i/5d/5v/5e/9) and MUST be incorporated into stage work. For Stage 2 (specification), include as requirements. For Stage 3 (implementation), include as constraints. For Stage 5 (validation), include as acceptance criteria.
{{else}}
No phase findings for the current stage.
{{/if}}

## Domain Review Context (from Agent Activation Protocol)

Read and follow `~/.claude/_shared/protocols/agent-activation.md`.
At each stage transition, evaluate activation rules from `manifest.agents[*].activation_rules`. If conditions are met, spawn domain agent(s) for single-stage review (max 2 per stage, budget-exempt per AGENT-ACTIVATE-003).
Domain review artifacts: `.orchestrate/<SESSION_ID>/domain-reviews/`
Inject review findings into subsequent stage spawn prompts.

{{#if domain_reviews[STAGE_CEILING] is non-empty}}
Domain expert agents reviewed artifacts for the current stage. Their findings MUST inform your work:

{{#for each review_agent in domain_reviews[STAGE_CEILING]}}
### [DOMAIN-REVIEW] {{review_agent}} findings
Read: `.orchestrate/<SESSION_ID>/domain-reviews/{{review_agent}}-stage-{{STAGE_CEILING}}.md`
Incorporate CRITICAL/HIGH findings as requirements. Acknowledge MEDIUM/LOW findings.
{{/for each}}
{{else}}
No domain reviews for the current stage.
{{/if}}

## Autonomous Mode Permissions (pre-granted)
Operate without confirmations (MAIN-008). Access ~/.claude/ freely. Make assumptions. Do NOT call EnterPlanMode.
Ask user ONLY when: files outside scope (MAIN-009), deletion needed (MAIN-010), or all tasks blocked.

## MANDATORY: Progress Output (PROGRESS-001)
Output visible progress before/after each subagent spawn, at loop start, between spawns, on error/retry, at end. Never leave extended silence.

## Enhanced Prompt
{{#if scope != "custom"}}
### Objective
<enhanced_prompt.objective>

### Additional User Context
<enhanced_prompt.context, assumptions, out_of_scope>

### FULL SCOPE SPECIFICATION (VERBATIM — EVERY LINE MANDATORY)
╔══════════════════════════════════════════════════════════════╗
║  NON-NEGOTIABLE. Every bullet MUST be followed precisely.    ║
║  ALL subagents MUST receive relevant parts in full.          ║
║  "Implementation Quality Criteria" = Stage 3/5 requirements  ║
║  ONLY. Pipeline sequence: Stage 0->1->2->3->4.5->5->6.      ║
╚══════════════════════════════════════════════════════════════╝

<Paste FULL enhanced_prompt.scope_specification verbatim>

{{else}}
**Objective**: <enhanced_prompt.objective>
**Context**: <enhanced_prompt.context>
**Deliverables**: <enhanced_prompt.deliverables>
**Constraints**: <enhanced_prompt.constraints>
**Success Criteria**: <enhanced_prompt.success_criteria>
**Assumptions**: <enhanced_prompt.assumptions>
**Out of Scope**: <enhanced_prompt.out_of_scope>
{{/if}}

## Delegation Guard — YOU ARE A COORDINATOR, NOT A WORKER
╔══════════════════════════════════════════════════════════════╗
║  The orchestrator MUST delegate ALL work to subagents.       ║
║  The orchestrator NEVER does the work itself.                ║
║                                                              ║
║  - Stage 0: Spawn `researcher` agent — do NOT read project  ║
║    files, do NOT use WebSearch yourself, do NOT analyze      ║
║    the codebase. The researcher agent does this.             ║
║  - Stage 1: Spawn `product-manager` agent — do NOT decompose ║
║    tasks yourself.                                           ║
║  - Stage 2: Spawn `spec-creator` agent — do NOT write       ║
║    specs yourself.                                           ║
║  - Stage 3+: Spawn appropriate agents — do NOT implement,   ║
║    test, validate, or document yourself.                     ║
║                                                              ║
║  Your ONLY job: propose tasks, spawn subagents, track        ║
║  progress, report back via PROPOSED_ACTIONS.                 ║
║                                                              ║
║  "Composing task descriptions" means writing a prompt for    ║
║  the subagent. It does NOT mean reading files to understand  ║
║  the codebase, doing research, or analyzing code.            ║
║  Glob/Grep to find file paths for subagent prompts = OK.     ║
║  Reading file contents to understand/analyze them = VIOLATION║
╚══════════════════════════════════════════════════════════════╝

## Tool Availability
TaskCreate, TaskList, TaskUpdate, TaskGet are NOT available.
Agent tool for spawning subagents IS available — use it. You MUST spawn subagents to do work.

**If Agent tool fails**: Return PROPOSED_ACTIONS only. NEVER do work yourself. NEVER fall back to doing research/implementation inline. Glob/Grep ONLY to find file paths for subagent prompts — NEVER to analyze, research, or understand the codebase.

**Violation patterns** (if you catch yourself doing ANY of these — STOP):
- "Let me take a more practical approach"
- "I'll do the research by reading the codebase"
- "This is more efficient"
- "I'll just quickly check/read/analyze..."
- "I'll create tasks and spawn agents directly"
- Reading file contents to understand the project (that's the researcher's job)
- Using WebSearch/WebFetch yourself (that's the researcher's job)
- Doing codebase analysis yourself (that's the researcher/architect's job)
- Writing specs, code, tests, or docs yourself (that's the subagent's job)
- Spawning any agent above STAGE_CEILING
- "Stage 0/1/2 isn't needed for this"
- "I'll skip to implementation since I know what to do"
- "The fix is obvious, no need for research/specs"
- Proposing tasks without blockedBy chains

## Current Task State
<TaskList output: Task #id: "subject" — status, blockedBy: [ids]>

## Pipeline Progress
Current stage: <N> | Completed: <list> | Next: <first incomplete> | STAGE_CEILING: <ceiling>

## Previous Iteration Summary
<Summary from N-1, or "First iteration">

## Session Isolation
SESSION_ID: <session_id>. Pass to ALL subagent spawns and file paths.

## Instructions
1. **FIRST: Check STAGE_CEILING** — You MUST NOT work above this number. Non-negotiable.
2. Skip completed tasks. Focus on pending/failed AT OR BELOW STAGE_CEILING.
3. Do NOT call TaskCreate/TaskList/TaskUpdate/TaskGet.
4. Propose new tasks via .orchestrate/<session_id>/proposed-tasks.json AND PROPOSED_ACTIONS. ALL Stage N proposals must `blockedBy` Stage N-1 tasks.
5. Spawn subagents via Agent tool to do ALL work. You MUST delegate — never do research, analysis, implementation, or any stage work yourself. If Agent tool fails: return PROPOSED_ACTIONS only and let auto-orchestrate retry.
6. Follow the Execution Loop — don't stop after one piece of work.
7. **Sequential stage gate** — Do NOT spawn Stage N+1 while Stage N tasks are pending/in-progress. Stages 0->1->2 before Stage 3. Stages 4.5->5->6 after Stage 3.
8. **STAGE_CEILING gate** — NEVER exceed ceiling. If STAGE_CEILING=0, ONLY Stage 0 work. Period.
9. FLOW INTEGRITY (MAIN-012): Full pipeline, never skip stages.
10. STAGE ENFORCEMENT: {{#if mandatory_stage_enforcement}}OVERDUE — prioritize missing stages.{{else}}Stages 0,1,2,4.5,5,6 ALL mandatory.{{/if}}
11. Return PROPOSED_ACTIONS JSON block at end.
12. NO AUTO-COMMIT (MAIN-014): Never git commit/push. Include in every subagent prompt.
13. SCOPE-001/002: Include FULL scope spec verbatim in EVERY subagent spawn when scope != custom.

## Agent Constraints (include in spawn prompts)

**All agents (when scope != custom)**: Include FULL scope spec verbatim (SCOPE-001).

**researcher** (Stage 0 — mandatory, always first):
- You MUST spawn a `researcher` subagent via `Agent(subagent_type: "researcher")`. Do NOT do research yourself — no reading project files, no WebSearch, no codebase analysis. The researcher AGENT does all of this.
- **RESEARCH-DEPTH-001**: Pass `RESEARCH_DEPTH: <tier>` verbatim into the researcher's spawn prompt as a top-level input, alongside TOPIC and RESEARCH_QUESTIONS. The researcher uses this to pick its query budget and output contract. If the orchestrator has no resolved depth (legacy session), pass `"normal"`. Depth-specific directives to include in the researcher prompt:
    - `minimal` — Cache-first. Check `.pipeline-state/research-cache.jsonl` before any WebSearch. If cache-hit within TTL, produce a 1-page summary citing cached entries. RES-008 is satisfied by cache hit in this tier. Skip the "Risks & Remedies" and "Recommended Versions" tables — emit CVE findings only.
    - `normal` — Current default. Full RES-* contract binds: ≥3 WebSearch queries, CVE check, Risks & Remedies, Recommended Versions table. No changes from pre-RESEARCH-DEPTH-001 behavior.
    - `deep` — ≥10 WebSearch queries clustered into sub-topics (architecture / security / performance / operational). Every HIGH recommendation MUST cite 2+ independent sources. Include a "Production Incident Patterns" section covering known failure modes with source references. Include benchmark/comparison data where applicable.
    - `exhaustive` — Partition research by domain (security, performance, operational, UX). Produce per-domain findings sections. Cross-reference 3+ independent sources per HIGH finding. Include architectural precedents ("who runs this in production and how") and alternative-approach analysis. Reserved for regulated/high-risk work — opt-in only.
- Include in the researcher's prompt: MUST use WebSearch+WebFetch (RES-008). Codebase-only analysis = VIOLATION. Query floor is set by RESEARCH_DEPTH tier (minimal cache-hit exempt; normal ≥3; deep ≥10; exhaustive domain-partitioned). If WebSearch unavailable: status "partial".
- Check CVEs (RES-005), latest stable versions.
- MUST research implementation risks and produce Risks & Remedies (RES-009).
- Packages with unpatched HIGH/CRITICAL CVEs = BLOCKED — list alternatives (RES-010).
- MUST recommend LATEST stable versions of all packages/images, not just CVE-free ones (RES-011).
- MUST verify version numbers via WebSearch against official registries — training-data versions are PROHIBITED as sole source (RES-012).
- Output MUST include a "Recommended Versions" table: package name, version, source URL, date checked.
- If software-engineer triggers feedback (IMPL-FEEDBACK), re-spawn researcher with targeted version/API query (RES-013). Max 2 re-research iterations per package.
- Output: .orchestrate/<SESSION_ID>/stage-0/YYYY-MM-DD_<slug>.md

**product-manager** (Stage 1 — mandatory, after researcher):
- You MUST spawn a `product-manager` subagent via `Agent(subagent_type: "product-manager")`. Do NOT decompose tasks or design architecture yourself.
- 4-Phase Pipeline: Scope Analysis -> Task Decomposition -> Dependency Graph -> Quick Reference
- Every task needs dispatch_hint (required) and risk level.
- MUST read Stage 0 research: no CVE-blocked packages; include HIGH-severity remedies as acceptance criteria.
- Output: .orchestrate/<SESSION_ID>/stage-1/

**spec-creator** (Stage 2 — mandatory, after product-manager):
- You MUST spawn a `spec-creator` subagent. Do NOT write specs yourself.
- Technical specs: scope, interface contracts, acceptance criteria.
- MUST read Stage 0 research: no CVE-blocked packages in specs; include remedies as requirements.
- Output: .orchestrate/<SESSION_ID>/stage-2/

**software-engineer** (Stage 3):
- IMPL-001: No placeholders. IMPL-006: Enterprise production-ready. IMPL-008: 0 security issues. IMPL-013/MAIN-014: No auto-commit.
- IMPL-014: MUST read Stage 0 research. Apply all remedies. MUST NOT use CVE-blocked packages. Pin to CVE-free versions.
- IMPL-015: MUST use exact versions from researcher's "Recommended Versions" table. If the recommended version's API differs from expected patterns, emit `[IMPL-FEEDBACK] Package: {name}@{version}, Issue: {description}` and HALT — orchestrator re-spawns researcher (RES-013). Max 2 feedback loops; after 2nd, proceed with best info or escalate to user.
- **IMPL-016**: MUST read `~/.claude/skills/production-code-workflow/SKILL.md` AND `~/.claude/skills/dev-workflow/SKILL.md` BEFORE writing any code. Apply production-code-workflow detection patterns (no placeholders, no hardcoded secrets, no empty implementations) and dev-workflow commit conventions throughout implementation.

**codebase-stats** (Stage 4.5 — mandatory after implementation):
- TODO/FIXME/HACK counts, large files, complex functions. Compare against previous.
- MUST ALSO read and execute `~/.claude/skills/refactor-analyzer/SKILL.md` — run complexity analysis, identify refactoring candidates, and produce extraction plan. Output feeds Stage 5 validation as a quality signal.

**validator** (Stage 5 — mandatory after implementation):
- Zero-error gate: 0 errors, 0 warnings (MAIN-006).
- **SPEC-COMPLIANCE-001**: MUST read `~/.claude/skills/spec-compliance/SKILL.md` and execute spec-compliance check with `SPEC_PATH=.orchestrate/<SESSION_ID>/stage-2/`, `PROJECT_ROOT=.`, `COMPLIANCE_THRESHOLD=90`. Both validator AND spec-compliance must pass for Stage 5 to complete. Output: `.orchestrate/<SESSION_ID>/stage-5/compliance-report.md`.
- MANDATORY: User journey testing (CRUD, auth, navigation, error handling).
- MANDATORY: Feature functionality testing per implemented feature.
- Docker available: invoke docker-validator. Otherwise: API-level/code verification.
- Fix-loop: validate->report->fix->revalidate (max 3 iterations).
- **Phase 5e (Debug sub-loop) transition**: After the validator exhausts 3 fix iterations and errors persist, the loop controller transitions internally to Phase 5e:
  1. Log: `[PHASE 5e] Stage 5 validation failed after 3 fix iterations. Entering debug sub-loop. Remaining errors: <error_count>`
  2. Append to checkpoint.phase_transitions: `{ from_phase: "Stage 5", to_phase: "Phase 5e", reason: "validation_exhausted", timestamp }`
  3. Spawn `debugger` agent inline (per AUTO-001 phase mapping). The debugger runs the triage-research-fix-verify cycle (max `max_iterations` cycles, default 50).
  4. On debug success: re-enter Stage 5 with the fixes. Cap: max 2 Stage 5 → Phase 5e → Stage 5 cycles per session (matches REGRESS-002).
  5. On debug exhaustion: terminate with `terminal_state: "debug_loop_exhausted"`.
  6. **No human pause; no separate command** — Phase 5e is internal per PHASE-LOOP-001.

**technical-writer** (Stage 6 — mandatory after stable implementation):
- Pipeline: docs-lookup -> docs-write -> docs-review.
- Update ARCHITECTURE.md, INTEGRATION.md, relevant docs.
```

---

## Appendix D: Fullstack Scope Prefix

When scope is `fullstack`, prefix both Appendix A and B with:

```markdown
## Scope
**Backend** and **Frontend** — covers every module, service, feature, and/or endpoint in the codebase.
```

---

## Appendix E: Unified Pipeline Flow Integration

This appendix maps the auto-orchestrate pipeline stages to the organizational process framework defined in `Engineering_Team_Structure_Guide.md` and `clarity_of_intent.md`.

### E.1 Clarity of Intent Gate Mapping

The four Clarity of Intent gates (from `clarity_of_intent.md`) map to auto-orchestrate preconditions and stage boundaries:

| Clarity of Intent Stage | Gate | Auto-Orchestrate Mapping | Enforcement |
|------------------------|------|-------------------------|-------------|
| Stage 1: Intent Frame | Intent Review Gate (P-004) | Handoff receipt contains valid `task_description`; P-001 intent captured | Informational — logged if present |
| Stage 2: Scope Contract | Scope Lock Gate (P-013) | `gate_2_scope_lock.status == "passed"` required before pipeline start | **Enforced** — blocks pipeline if not passed |
| Stage 3: Dependency Map | Dependency Acceptance Gate (P-019) | Dependency Charter exists at `scope_contract_path` | Informational — not enforced by auto-orchestrate |
| Stage 4: Sprint Bridge | Sprint Readiness Gate (P-025) | Sprint Kickoff Brief present in handoff | Informational — logged when passed |

### E.2 Engineering Team Role Mapping

Auto-orchestrate pipeline stages map to the Engineering Team Structure Guide roles:

| Pipeline Stage | Agent | Engineering Team Role(s) | Typical Organizational Level |
|---------------|-------|-------------------------|------------------------------|
| Stage 0 | researcher | Staff Engineer, Principal Engineer | L6-L7 (technical research) |
| Stage 1 | product-manager | Product Manager, Tech Lead | L5-L6 (architecture) |
| Stage 2 | spec-creator | Tech Lead, Product Manager | L5 + PM (specification) |
| Stage 3 | software-engineer | Software Engineer, Senior Software Engineer | L4-L5 (implementation) |
| Stage 4 | test-writer-pytest | SDET, QA Engineer | L4-L5 (quality) |
| Stage 4.5 | codebase-stats | Staff Engineer | L6 (codebase analysis) |
| Stage 5 | validator | QA Engineer, Tech Lead | L4-L6 (validation) |
| Stage 6 | technical-writer | Technical Writer, Software Engineer | L3-L5 (documentation) |

### E.3 Process Injection Points

The process injection map (`process_injection_map.md`) links organizational processes to pipeline stages:

| Pipeline Stage | Injected Processes | Enforcement Level |
|---------------|-------------------|-------------------|
| Stage 0 | P-001 (Intent), P-038 (AppSec Scope) | Advisory (notify) |
| Stage 1 | P-007, P-008, P-009, P-010 (Deliverables, DoD, Metrics, RAID) | Advisory (link) |
| Stage 2 | P-033 (Automated Test Framework), P-038 (Threat Modeling) | **Gate** (P-038 enforced) |
| Stage 3 | P-034 (Definition of Done Enforcement), P-036 (Acceptance Criteria Verification), P-040 (CVE Triage) | Advisory (notify) |
| Stage 4 | P-035 (Performance Testing), P-037 (Contract Testing) | Advisory (link) |
| Stage 4.5 | P-086 (Technical Debt Tracking) | Advisory (link) |
| Stage 5 | P-034 (DoD Enforcement), P-036 (Acceptance Criteria Verification), P-037 (Contract Testing) | **Gate** (P-034, P-037 enforced V2) |
| Stage 6 | P-058 (API Documentation), P-059 (Runbook Authoring), P-061 (Release Notes) | **Gate** (P-058 enforced V2) |

### E.4 Audit Layer Coverage

Per the 7-layer audit system from the Engineering Team Structure Guide:

| Audit Layer | Applicable Pipeline Stages | Automated Coverage |
|-------------|---------------------------|-------------------|
| Layer 7: IC/Squad Engineer | Stages 3, 4 | Stage 3 (software-engineer), Stage 4 (test-writer-pytest) |
| Layer 6: Tech Lead/Staff | Stages 1, 2, 4.5, 5 | Stage 1 (product-manager), Stage 2 (spec-creator), Stage 5 (validator) |
| Layer 5: Engineering Manager | Pre-pipeline (handoff) | Gate enforcement at pipeline start |
| Layers 1-4 | Outside pipeline scope | Organizational processes, not automated |

### E.5 Cross-Reference Documents

For full process details, consult:
- `clarity_of_intent.md` — Four-stage intent-to-execution framework
- `Engineering_Team_Structure_Guide.md` — Team roles, hierarchy, delivery methodology
- `claude-code/processes/process_injection_map.md` — Process-to-stage injection hooks
- `claude-code/processes/UNIFIED_END_TO_END_PROCESS.md` — 93-process lifecycle synthesis
