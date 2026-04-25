# Release Notes: Auto-Orchestrate

**Repository**: https://github.com/ribatshepo/Auto-Orchestrate
**License**: MIT

---

## Unreleased (Post-v1.0.0)

**Changes since**: 2026-02-12 (v1.0.0)
**Last updated**: 2026-04-26

This section documents all changes made after v1.0.0 that are not yet tagged in a release. These changes represent significant improvements to pipeline reliability, session management, agent communication, security posture, parallel execution, and token-budget efficiency.

---

### New Features

#### Token-Budget Optimization Suite (~45% session reduction)

A 6-phase suite of independently-flagged optimizations cuts a typical `/auto-orchestrate` session from ~2.0M to ~1.1M input tokens. Each phase is gated by a `checkpoint.optimizations.<flag>` boolean — default `true` on fresh installs, `false` on resumed sessions to keep prior on-disk receipts compatible. All 6 phases are reversible without code change.

| Phase | Constraint ID | Saving | Mechanism |
|---|---|---|---|
| 0 | (instrumentation) | baseline | Per-spawn token counters in `iteration_history[].token_counts_by_spawn` and `checkpoint.session_token_total` |
| 1 | `SKILL-FRONTMATTER-001` | ~76k | Skill discovery loads SKILL.md frontmatter only (~300 tok); body loaded only at invocation |
| 2 | (`process_injection_slim`) | ~50k | Spawn-prompt builder injects only fired hooks instead of the full process injection map |
| 3 | `MANIFEST-DIGEST-001` | ~416k | Subagents receive a 2.6k digest (agents+triggers) instead of the full 19k manifest; orchestrator + session-manager + `needs_full_manifest:true` get full |
| 4 | `TEMPLATE-EXTRACT-001` | ~302k | Orchestrator spawns receive CORE (~8k) + active stage/phase/meeting template instead of full 33k `orchestrator.md` |
| 5 | `STAGE-RECEIPT-DIET-001` | ~40k | Slim v2.0.0 stage-receipt schema; consumers tolerant of both v1 and v2 |
| 6 | `HANDOVER-COMPRESS-001` | ~20k | Slim v2.0.0 handover-receipt schema; `context_carry` re-derived from checkpoint by tolerant readers |

**Schema bumps**: 1.6.0 → 1.7.0 (parallel scheduling fields), 1.7.0 → 1.8.0 (first 4 optimization flags + token counters), 1.8.0 → 1.9.0 (slim receipt flags). Each migration block defaults the new flags to `false` for resumed sessions; new sessions get `true`.

**New layer1 helpers** (`skills/_shared/python/layer1/`):

- `skill_frontmatter.py` — `read_frontmatter()`, `list_skills_with_triggers()`, `estimate_frontmatter_tokens()`
- `manifest_digest.py` — `build_digest()`, `needs_full_manifest()`, `estimate_digest_tokens()`
- `orchestrator_template.py` — `build_spawn_prompt_body()`, `extract_core()`, `extract_stage_template()`, `extract_phase_template()`, `extract_meeting_template()`

**Per-task overrides** (re-fattening insurance): `needs_full_manifest: true` (Phase 3), `needs_full_receipt: true` (Phase 5), `needs_full_handover: true` (Phase 6) — single-task escape hatches that re-emit the verbose payload for that one boundary if a downstream consumer needs a dropped field.

#### Parallel Stage 3 Implementation (PARALLEL-001/002/003 + CHAIN-002 + SE-009)

Stage 3 may now spawn up to **5 concurrent software-engineers** (configurable up to 7 via `checkpoint.parallel_cap`) when independence groups have multiple unblocked tasks. Hybrid detection at Stage 1:

- **Heuristic (default)**: tasks sharing a common path prefix of `files_touched` at directory depth ≤ 2 default to the same group; cross-cutting tasks fall into a single shared group (safe sequential).
- **Explicit override (always wins)**: spec/task fields `independence_groups: [[ids],...]`, `shares_state_with: [ids]`, `independent_of: [ids]`.

The product-manager (Stage 1) MUST emit `independence_groups` and `dependency_graph` in `proposed-tasks.json` per `PARALLEL-001`. The orchestrator's Stage 3 spawn template picks one task per distinct group per spawn cycle (FIFO within group), up to `parallel_cap`, and spawns N concurrent software-engineers in a single message. `SE-009` requires concurrent-safe execution: operate only on declared `files_touched`, no peer-task state assumptions, atomic commits.

**Per-group stage tracking**: `checkpoint.independence_group_stages: {group_id: stage_n}` lets independent groups advance through stages at different rates without violating CHAIN-001 (relaxed cross-group per PARALLEL-002).

**Single-spawn rule clarified**: the "EXACTLY ONE agent" guard in auto-orchestrate's loop controller applies to its own turn (one orchestrator). The orchestrator itself MAY spawn N parallel implementation agents in its own turn — they belong to the same orchestrator response and report back together.

Token cost is roughly linear in concurrency (N parallel spawns ≈ N×35k input); wall-clock is roughly inverse (5x speedup for 5 concurrent stories). The win is latency, not cost.

#### Cross-Pipeline Shared State Constraints (SHARED-001–004)

The cross-pipeline state protocol (`_shared/protocols/cross-pipeline-state.md`) now codifies four named constraints for shared knowledge management:

- **SHARED-001**: All pipelines read shared knowledge stores at startup before first action
- **SHARED-002**: Escalation handoffs written to shared `.pipeline-state/escalation-log.jsonl`
- **SHARED-003**: Research cache checked before spawning researcher agents (avoids redundant lookups)
- **SHARED-004**: Fix-registry is append-only and shared — auto-debug checks for existing verified fixes before diagnosing

Cross-references added to `auto-orchestrate.md`, `auto-audit.md`, and `auto-debug.md` at their respective startup and operational sections.

#### Ten New Skills for Process Coverage (48 total, up from 38)

A second wave of skill creation added **10 high- and medium-value skills** to close gaps in process coverage (PROCESS_GAPS.md Section 14):

- **`raid-logger`** — Append-only RAID entries to per-session RAID log (P-010, P-074, P-075). Atomic append + dedup + severity validation. Used by product-manager + technical-program-manager.
- **`story-generator`** — Convert deliverables/epics into INVEST-compliant user stories with acceptance criteria (P-024, P-029). Includes `validate_story.py` INVEST validator.
- **`threat-modeler`** — STRIDE-based threat enumeration with mitigation matrix output (P-038, P-047). Template-driven; integrates with security-auditor.
- **`adr-publisher`** — Architecture Decision Record authoring with auto-numbering (P-060, P-085). Includes `next_adr_number.py`.
- **`release-notes-generator`** — Conventional-commits parser + categorized changelog generator (P-061, P-048). Includes `parse_git_log.py` and `render_release_notes.py`.
- **`slo-definer`** — SLO/SLI patterns + error-budget computation + MWMBR alert thresholds (P-054, P-055, P-056). Includes `calculate_error_budget.py`.
- **`cab-reviewer`** — CAB Decision Record template with risk classification rubric (P-076, P-048). Template-driven.
- **`okr-retrospective-tracker`** — OKR achievement scoring + 30/60/90-day post-launch retrospective (P-072, P-073). Includes `score_okr.py`.
- **`dependency-matrix-generator`** — Cross-team dependency register + critical path + cycle detection (P-015, P-016, P-017, P-030). Includes `dep_graph.py` and `resource_conflict_detector.py`.
- **`sprint-goal-linker`** — Sprint goal template + intent trace validator (Project Intent → Scope Deliverable → Sprint Goal) (P-022, P-023). Template-driven.

Each is registered in `manifest.json`, referenced by owning agent prompts, and wired into the relevant orchestrator spawn templates.

#### Three New Skills (38 total, up from 35)

- **`accessibility-check`** — WCAG 2.1 AA/AAA compliance checking for web interfaces and UI components. Invoked by qa-engineer at Stage 5 (ACT-012) when frontend artifacts are detected. Audits color contrast, keyboard navigation, ARIA patterns, form labels, focus management, and semantic HTML.

- **`cost-estimator`** — Cloud infrastructure cost estimation and FinOps analysis. Invoked by infra-engineer during `/release-prep` (P-048). Scans Terraform, Docker, CDK, Pulumi, and Kubernetes manifests to produce monthly cost projections with optimization recommendations.

- **`observability-setup`** — Monitoring, alerting, dashboard, and distributed tracing configuration. Invoked by sre during `/release-prep` and `/post-launch` (P-054, P-055). Defines SLO-based monitoring, alert severity tiers, USE-method dashboards, and OpenTelemetry instrumentation guidance.

#### Researcher Agent (6th Specialized Agent)

A new dedicated `researcher` agent (`agents/researcher.md`, 312 lines) joins the system as the mandatory Stage 0 agent. The researcher uses `WebSearch` and `WebFetch` for internet-enabled investigation and enforces RES-001 through RES-007 constraints:

- **RES-001**: Evidence-based findings — every claim cites a source
- **RES-002**: Currency — prefers sources within 3 months–1 year
- **RES-003**: Relevance — directly addresses the research question
- **RES-004**: Actionable — every finding maps to an implementation decision
- **RES-005**: Security-first — CVE lookup for packages and Docker images
- **RES-006**: Structured output — standard output format with all required sections
- **RES-007**: Manifest entry — writes key_findings (3–7 sentences) to manifest
- **RES-008**: Mandatory internet research — WebSearch/WebFetch must be called in every session

Capabilities: CVE lookup, package analysis, Docker image security research, best-practices investigation, and technology evaluation.

#### Docker Validator Skill (Stage 5 Sub-Step)

New `docker-validator` skill (`skills/docker-validator/SKILL.md`, 449 lines) added as a mandatory Stage 5 sub-step when Docker Engine is available. Executes 8 validation phases:

1. Environment check — Docker Engine >= 27.1.1, Compose, daemon
2. State audit — snapshot containers, images, volumes, networks
3. Checkpoint creation — persists snapshot to `.orchestrate/<SESSION_ID>/logs/docker-checkpoint.json`
4. Build and deploy — `docker compose build` + `docker compose up -d --wait`
5. UX testing (unauthenticated) — public endpoints expect 200/302
6. UX testing (authenticated) — protected endpoints expect 200 (GET) / 201 (POST/PUT)
7. HTTP validation summary — aggregate results, flags 4xx/5xx
8. State restoration — `docker compose down --volumes --remove-orphans`, verifies delta

Registered in `manifest.json`, enforced in `orchestrator.md`, and wired into the auto-orchestrate pipeline.

#### File-Based Task Proposal Protocol

Subagents now communicate task proposals via `.orchestrate/<session-id>/proposed-tasks.json` files and `PROPOSED_ACTIONS` JSON blocks in return values. This enables reliable task management without requiring direct TaskCreate/TaskUpdate tool access from subagents.

- Orchestrator proposes tasks in its return value using `PROPOSED_ACTIONS` JSON block
- Auto-orchestrate reads the return value and executes TaskCreate on behalf of the orchestrator
- GAP-CRIT-001 status: workaround implemented (was previously unworkarounded)

#### `dispatch_hint` Routing Field

Epic-architect now assigns a `dispatch_hint` field to every decomposed task, providing explicit routing keys for the orchestrator to route tasks to the correct subagent. This eliminates routing guesswork and enforces MAIN-013 (decomposition gate).

#### `.orchestrate/` Session Folder Structure

Each auto-orchestrate session creates a per-session directory at `.orchestrate/<session-id>/` with stage-based subdirectories:

```
.orchestrate/
└── <session-id>/
    ├── checkpoint.json    # Session checkpoint (task state, iteration history)
    ├── proposed-tasks.json
    ├── stage-0/           # Researcher output (Stage 0)
    ├── stage-1/           # Epic-architect plans (Stage 1)
    ├── stage-2/           # Spec-creator output (Stage 2)
    ├── stage-3/           # Implementer output (Stage 3)
    ├── stage-4/           # Test writer output (Stage 4)
    ├── stage-4.5/         # Codebase stats output (Stage 4.5)
    ├── stage-5/           # Validator output (Stage 5)
    └── stage-6/           # Documentor output (Stage 6)
```

All session artifacts are co-located with the project, eliminating the need for global `~/.claude/` writes.

#### No-Auto-Commit Policy

`dev-workflow` phases G3 and G4 now generate conventional commit messages and display copy-pasteable `git add`/`git commit`/`git push` commands **without executing them**. The user reviews and runs commands manually. This eliminates surprise commits during autonomous orchestration sessions.

---

#### Autonomous Debug Subsystem (7th Specialized Agent + Command)

A new `debugger` agent (`agents/debugger.md`, model: opus) and `/auto-debug` command (`commands/auto-debug.md`) provide a cyclic autonomous debugging pipeline:

**Pipeline**: triage → research → root cause + fix → verify → report (cycles until zero errors or iteration limit reached)

**Usage**:
```
/auto-debug <error description or "debug all" or paste stack trace>
/auto-debug debug docker           # Docker-specific debugging
/auto-debug c                      # Resume most recent debug session
```

**Key parameters**: `docker` (boolean), `max_iterations` (default 50), `stall_threshold` (default 3), `fix_verify_cycles` (default 5)

**Debugger constraints** (DBG-001 to DBG-012):
- DBG-001: Evidence-first — every diagnosis cites specific log lines or traces
- DBG-002: Minimal blast radius — fix ONLY what is broken; no opportunistic cleanup
- DBG-003: Verify before declaring fixed — re-run test/check after every fix
- DBG-004: Fix immediately when root cause is found
- DBG-005: No auto-commit
- DBG-006: Uses debug-diagnostics skill for structured error categorization
- DBG-007: Docker awareness — collect `docker compose logs` and container health first
- DBG-008: Researcher escalation for unfamiliar errors (spawns researcher subagent)
- DBG-009: Max 3 internal fix-verify iterations per error before escalating
- DBG-010: Writes structured debug report to `.debug/<session-id>/reports/`
- DBG-011: Single error focus — one error at a time, starting with root error
- DBG-012: Preserve evidence — never delete diagnostic data

**Session directory**: `.debug/<session-id>/reports/` (project-local, parallel to `.orchestrate/`)

Supported by the new `debug-diagnostics` skill for structured error categorization.

---

#### Autonomous Audit Subsystem (8th Specialized Agent + Command)

A new `auditor` agent (`agents/auditor.md`, model: opus) and `/auto-audit` command (`commands/auto-audit.md`) provide an audit-remediate loop that verifies a codebase against a specification document:

**Pipeline**: audit → gap analysis → remediate (via orchestrator) → re-audit (cycles until compliance threshold met or cycle limit reached)

**Usage**:
```
/auto-audit path/to/spec.md                # Audit against spec
/auto-audit path/to/spec.md scope=B       # Backend scope
/auto-audit c                              # Resume most recent audit session
```

**Key parameters**: `scope` (F/B/S), `max_audit_cycles` (default 5), `max_orchestrate_iterations` (default 100), `docker` (boolean), `compliance_threshold` (default 90%)

**Auditor constraints** (AUD-001 to AUD-008):
- AUD-001: Read-only operation — NEVER modifies project files or Docker state
- AUD-002: Spec-first — reads spec document before scanning codebase
- AUD-003: Evidence-based verdicts — every PASS/PARTIAL/MISSING/FAIL cites file paths or command output
- AUD-004: Uses spec-compliance skill for structured compliance checking
- AUD-005: Dual output — human-readable audit-report-<cycle>.md AND machine-readable gap-report.json
- AUD-006: No auto-commit
- AUD-007: Complete coverage — every requirement in the spec gets a verdict
- AUD-008: Docker conditional — Docker auditing only when DOCKER_MODE is true

**Session directory**: `.audit/<session-id>/` (project-local)

Supported by the new `spec-compliance` skill for requirements extraction and compliance scoring.

---

### Bug Fixes

#### Session Management

- **Checkpoint path isolation** — Session checkpoints are now written to project-local `.orchestrate/<session-id>/checkpoint.json` instead of `~/.claude/sessions/<id>.json`. Prevents cross-project interference and keeps all session artifacts co-located with the project.

- **Cross-terminal supersession interference** — Supersession scan now scoped to `.orchestrate/*/checkpoint.json` (current project only) instead of `~/.claude/sessions/auto-orc-*.json` (global). Eliminates false-positive supersessions when multiple projects run auto-orchestrate concurrently.

- **Crash recovery legacy support** — Crash recovery protocol reads `.orchestrate/` (primary) then falls back to `~/.claude/sessions/` (read-only legacy), so sessions started before the path change can still be recovered.

- **Session supersession gap** — `auto-orchestrate.md` Step 2b now loops over ALL in-progress sessions (not just the first match) when a new session starts, adding `superseded_at` and `superseded_by` metadata to each, and creating `.stale` marker files in corresponding `.orchestrate/<session-id>/` directories.

- **Crash recovery task state loss** — Checkpoint schema now includes a `task_snapshot` field (written every iteration in Step 4.7) containing full task state (id, subject, status, blockedBy, dispatch_hint). Crash Recovery Protocol reads `task_snapshot.tasks` and restores tasks via TaskCreate when the task system is empty after a crash.

#### Pipeline Reliability

- **PRE-IMPL-GATE** — Orchestrator now blocks implementer spawns if Stage 0 (researcher), Stage 1 (epic-architect), or Stage 2 (spec-creator) have not completed. Re-routes to the first missing stage automatically.

- **BUDGET-RESERVATION** — Orchestrator reserves 3 budget slots for mandatory post-implementation stages (4.5, 5, 6). If only 3 slots remain and the next task is an implementer spawn, it is deferred so mandatory stages are never skipped due to budget exhaustion.

- **Budget exemption for Stages 5 and 6** — Stage 5 (validator) and Stage 6 (documentor) spawns are EXEMPT from budget limits. Budget exhaustion is NEVER a valid reason to skip Stages 5 or 6.

- **Proactive missing-stage injection** — After each iteration, `auto-orchestrate` checks if any mandatory stage (0, 1, 2, 4.5, 5, 6) is absent AND no task for that stage is pending or in-progress. Missing stages are immediately injected as new tasks before proceeding to the next orchestrator spawn.

- **Termination condition 1a** — When all tasks appear complete but `stages_completed` is missing any mandatory stage, auto-orchestrate forces missing-stage task injection and one more iteration before declaring completion.

#### Agent Communication

- **spec-creator output path conflict** — Resolved conflict between `docs/specs/` (SKILL.md default) and `.orchestrate/<SESSION_ID>/specs/` (orchestrator directive). The orchestrator now passes an explicit `OUTPUT_DIR` parameter in the Stage 2 spawn template. The spec-creator SKILL.md supports `OUTPUT_DIR` override with `docs/specs/` fallback for standalone use.

- **Epic-architect ↔ orchestrator task handoff** — Clarified that `dispatch_hint` is the routing key and that `PROPOSED_ACTIONS` in the orchestrator return value drives task creation. Documented in TOOL-AVAILABILITY.md.

#### Security and Constraint Hardening

- **AUTO-001 delegated-spawn rationalization bypass** — Strengthened the AUTO-001 GUARD in `auto-orchestrate.md` Step 4 to explicitly block the rationalization pattern where auto-orchestrate spawns a non-orchestrator agent because "the orchestrator delegated the routing decision". The GUARD now enumerates five concrete prohibited justifications:
  1. "The orchestrator delegated this spawn to me"
  2. "The orchestrator explicitly routed this to researcher/implementer/etc"
  3. "Since the orchestrator's Task tool is unavailable for N iterations I will execute the spawn directly"
  4. "The stall threshold is exceeded so I will bypass the orchestrator"
  5. "The orchestrator has made its routing decision so I will carry it out"

  A corresponding anti-pattern row was added to the Anti-Patterns table.

- **HARD SELF-AUDIT GATE** — Orchestrator now includes a mandatory self-audit gate (replaces advisory checklist) that BLOCKS return unless all mandatory stages have been executed. If any mandatory stage was skipped, the orchestrator must go back and spawn the missing agent before returning.

---

### Changed

| Component | Change |
|-----------|--------|
| Stage 0 | Now MANDATORY — researcher must run before epic-architect; previously optional |
| Agent count | 5 → 8 (added researcher, debugger, auditor) |
| dev-workflow G3/G4 | Message-generation-only — no longer auto-commits or auto-pushes |
| Orchestrator communication | Receives task state via spawn prompt; proposes updates via PROPOSED_ACTIONS (not direct TaskCreate/TaskUpdate) |
| Epic-architect task caps | Enforces LIMIT-001/LIMIT-002 (50-task ceiling); generates broader consolidated tasks |
| TOOL-AVAILABILITY.md | Major overhaul clarifying tool availability for all subagents |
| GAP-CRIT-001 | Status changed: workaround fully implemented via file-based proposal protocol |
| ARCHITECTURE.md | Updated to reflect 6 agents, new skills, and revised session management |
| README.md | Agent count corrected from 5 to 6; directory tree updated; manifest schema path fixed |

---

### Security

- **Removed `Bash(rm *)` from `settings.json` allow list** — The `Bash(rm *)` permission was temporarily added for cleanup operations and has been removed to reduce the attack surface. `rm` is no longer an explicitly allowed permission in the default configuration.

---

### Documentation Updates

- **ARCHITECTURE.md** — Updated to reflect 6 agents, added researcher agent documentation, revised session management section, updated mandatory stage descriptions
- **README.md** — Agent count corrected (5 → 6), directory tree updated with `researcher.md`, manifest schema path fixed to `_shared/schemas/manifest.schema.json`
- **agents/TOOL-AVAILABILITY.md** — Redirect notice added pointing to canonical `_shared/references/TOOL-AVAILABILITY.md`
- **install.sh** — Now copies documentation files (`ARCHITECTURE.md`, `INTEGRATION.md`, `PERMISSION-MODES.md`) to `~/.claude/` during installation

---

## v1.0.0 — 2026-02-12

**Release Date**: 2026-02-12
**License**: MIT
**Repository**: https://github.com/ribatshepo/Auto-Orchestrate

---

### Overview

Auto-Orchestrate v1.0.0 is the first public release of a multi-agent orchestration framework that extends Claude Code with autonomous software engineering workflows. This release provides a complete system for handing off complex engineering tasks to AI agents and getting production-ready results through a structured 7-stage pipeline.

The system coordinates specialized agents — from research and planning through implementation, testing, validation, and documentation — with strict quality gates, context budget management, and session persistence with crash recovery.

---

### Key Features

#### Autonomous Multi-Agent Orchestration

Launch a fully autonomous pipeline with a single command:

```
/auto-orchestrate Build a REST API for user management with authentication, tests, and documentation
```

The system will:
1. Research requirements and unknowns (Stage 0)
2. Decompose the task into an execution plan with dependency graphs (Stage 1)
3. Write technical specifications (Stage 2)
4. Implement production code with self-review and security gates (Stage 3)
5. Generate tests (Stage 4)
6. Measure technical debt impact (Stage 4.5 — mandatory)
7. Run validation and compliance checks (Stage 5 — mandatory)
8. Produce documentation (Stage 6 — mandatory)

**Key innovations**:
- **Checkpoint-based session persistence** — sessions resume automatically after interruptions
- **Zero-error gates** — implementation must reach 0 errors and 0 warnings before advancing
- **Mandatory validation** — stages 4.5, 5, and 6 must complete before termination
- **Context-efficient handoffs** — under 10K tokens per agent delegation via manifest summaries
- **Single-file implementer pattern** — each implementer invocation targets exactly one file to prevent context exhaustion

#### 5 Specialized Agents

| Agent | Role | Key Features |
|-------|------|--------------|
| **orchestrator** | Coordinates workflows | Enforces MAIN-001 to MAIN-013 constraints; delegates via Task tool |
| **epic-architect** | Decomposes work | 4-phase pipeline (scope → tasks → dependencies → Programs) with parallel execution planning |
| **implementer** | Writes code | One-pass quality (implement → self-review → fix → security gate); opus model; production-ready only (IMPL-001 to IMPL-012) |
| **documentor** | Creates docs | Maintain-don't-duplicate principle; 3-phase chain (lookup → write → review) |
| **session-manager** | Manages sessions | Checkpoint persistence; crash recovery; workflow command orchestration |

#### 32 Task-Specific Skills

**Quality and Validation**:
- validator — compliance validation
- test-writer-pytest — pytest test generation
- test-gap-analyzer — coverage gap detection
- security-auditor — shell script vulnerability scanning
- codebase-stats — technical debt measurement (mandatory Stage 4.5)

**Implementation**:
- task-executor — generic task execution
- library-implementer-python — Python library modules
- production-code-workflow — production code patterns and placeholder detection

**Analysis and Planning**:
- researcher — multi-source investigation
- spec-creator — RFC 2119 specifications
- spec-analyzer — specification analysis and phase planning
- dependency-analyzer — circular dependency detection and layer validation

**Documentation**:
- docs-lookup — library documentation via Context7
- docs-write — create/edit with style guide compliance
- docs-review — style guide validation

**Refactoring and Infrastructure**:
- refactor-analyzer — code structure analysis
- refactor-executor — script splitting and modularization
- schema-migrator — JSON schema version upgrades
- error-standardizer — convert to emit_error() pattern
- hierarchy-unifier — consolidate scattered operations
- docker-workflow — Docker containerization patterns
- cicd-workflow — CI/CD pipeline configuration (GitHub Actions, GitLab CI)

**Workflow and Session Management**:
- workflow-start — initialize session
- workflow-dash — project dashboard
- workflow-focus — task focus management
- workflow-next — intelligent next task suggestion
- workflow-plan — planning mode
- workflow-end — session wrap-up

**Utility**:
- skill-lookup — search prompts.chat marketplace
- skill-creator — create new skills
- dev-workflow — atomic commits and release management
- python-venv-manager — virtual environment management

#### Constraint System

The framework enforces three constraint sets to maintain quality and predictability:

**MAIN-001 to MAIN-013** (Orchestrator):
- Delegation-only (no direct implementation)
- Context budgets (under 10K tokens per handoff)
- Zero-error gates (0 errors/warnings before advancing)
- File scope discipline (no out-of-scope modifications)
- Flow integrity (never skip pipeline stages)
- Decomposition gate (verify dispatch_hint before routing)

**IMPL-001 to IMPL-012** (Implementer):
- No placeholders (production-ready code only)
- One-pass quality (implement → review → fix in single pass)
- Security gate (0 security issues before completion)
- Anti-pattern detection (code must not match anti-patterns table)
- Context budget discipline (turn tracking, checkpoints, hard-exit)
- Single-file scope (targets exactly ONE file per invocation)

**AUTO-001 to AUTO-007** (Auto-Orchestrate):
- Stage monotonicity (pipeline stages only increase)
- Mandatory completion (stages 4.5, 5, 6 required before termination)
- Checkpoint integrity (write checkpoint before every spawn)
- Iteration history immutability (append-only)

---

### Architecture

#### Pipeline Stages

| Stage | Component | Purpose | Mandatory |
|-------|-----------|---------|-----------|
| 0 | researcher | Gather unknowns and context | No |
| 1 | epic-architect | Decompose into tasks with dependencies | No |
| 2 | spec-creator | Write technical specifications | No |
| 3 | implementer | Produce production-ready code | No |
| 4 | test-writer-pytest | Generate tests | No |
| 4.5 | codebase-stats | Measure technical debt impact | **Yes** |
| 5 | validator | Validate compliance and correctness | **Yes** |
| 6 | documentor | Write/update documentation | **Yes** |

#### Layered Python Library

The `claude-code/skills/_shared/python/` directory provides a zero-dependency Python library with strict layered architecture:

- **Layer 0** (Foundation): exit_codes, colors, constants — no dependencies
- **Layer 1** (Basic Helpers): logging, error_json, config, file_ops, output_format — imports layer0 only
- **Layer 2** (Business Logic): validation, task_ops — imports layer0-1
- **Layer 3** (Orchestration): migrate, backup, doctor, hierarchy_unified — imports layer0-2

**Key property**: Zero external dependencies — uses only Python 3 standard library.

#### Subagent Protocol

All subagents follow RFC 2119 output requirements (OUT-001 to OUT-004):

- Write findings to `{{OUTPUT_DIR}}/{{DATE}}_{{SLUG}}.md`
- Append one-line JSONL entry to manifest with `key_findings` (3-7 sentence summary)
- Return only: "Research complete. See MANIFEST.jsonl for summary."
- Never return full content in response (preserves orchestrator context)

---

### Getting Started

#### Prerequisites

- **Claude Code CLI** — [Anthropic's official CLI for Claude](https://docs.anthropic.com/en/docs/claude-code)
- **Python 3** — Required for skill scripts (no pip dependencies needed)

#### Installation

```bash
# Clone the repository
git clone https://github.com/ribatshepo/Auto-Orchestrate.git
cd Auto-Orchestrate

# Run the install script (auto-backs up existing ~/.claude/ config)
chmod +x install.sh
./install.sh
```

The install script copies:
- `agents/` → `~/.claude/agents/` (5 agent definitions)
- `skills/` → `~/.claude/skills/` (32 skill directories)
- `commands/` → `~/.claude/commands/` (auto-orchestrate command)
- `_shared/` → `~/.claude/_shared/` (protocols, templates, references)
- `manifest.json` → `~/.claude/manifest.json` (component registry)
- `settings.json` → `~/.claude/settings.json` (configuration)

#### Quick Start: Autonomous Orchestration

```
/auto-orchestrate Implement user authentication with JWT tokens, tests, and documentation
```

The system will:
1. Enhance your prompt into structured objectives with success criteria
2. Spawn the orchestrator repeatedly (default: max 15 iterations)
3. Loop until all tasks complete or a termination condition is met (success, stall, or max iterations)
4. Create session checkpoint in `.orchestrate/auto-orc-<date>-<slug>/checkpoint.json`

#### Quick Start: Session Management

```
/workflow-start    # Initialize session, display task overview
/workflow-dash     # View project dashboard (tasks by status)
/workflow-next     # Get intelligent next task suggestion
/workflow-focus 3  # Set focus on task ID 3
# ... do work ...
/workflow-end      # Wrap up session with progress summary
```

#### Resuming Sessions

Sessions are checkpointed automatically. If interrupted:

```
/auto-orchestrate c
```

This resumes the most recent in-progress session from the last checkpoint.

---

### Known Limitations

#### GAP-CRIT-001: Task Tool Availability

The orchestrator agent may not have access to the Task tool in all permission modes. When this occurs:

- Simple work (documentation, file edits) proceeds inline via emergency fallback
- Complex work requiring subagent delegation is documented for manual completion
- The orchestrator logs `[GAP-CRIT-001] Task tool unavailable` in its output

**Workaround**: The file-based task proposal protocol (`PROPOSED_ACTIONS` + `.orchestrate/<session-id>/proposed-tasks.json`) now provides a fully implemented workaround. See CHANGELOG.md Unreleased section for details.

**Status**: Architectural constraint under investigation. See `claude-code/agents/TOOL-AVAILABILITY.md` for details.

#### No Sandboxing

Skills and agents execute with the same permissions as the Claude Code process. There is no sandboxing or containerization. Users should:

- Review auto-orchestrate objectives before granting autonomous mode permission
- Run Claude Code with appropriate user-level permissions (do not run as root)
- Monitor file changes in working directories during autonomous orchestration

#### Permission Mode Compatibility

Auto-orchestrate has undergone limited testing across all Claude Code permission modes. Compatibility may vary. If you encounter issues, try different permission modes or invoke agents directly.

---

### Security Considerations

#### Secure by Default

- **Zero external dependencies** — Python library uses only Python 3 standard library
- **Automatic backups** — install script backs up existing `~/.claude/` to `~/.claude/backup-<timestamp>/`
- **Atomic file operations** — shared library uses atomic writes with proper error handling
- **Input validation** — validation layer (layer2/validation.py) provides input sanitization
- **Audit trail** — manifest entries provide full history of agent actions

#### User Responsibilities

- Review the install script before execution
- Review generated code before running it, especially for security-sensitive tasks
- Use specific, well-defined objectives for `/auto-orchestrate` (avoid vague requests)
- Verify agents only modify files within the expected task scope
- Maintain independent backups of critical codebases

For detailed security information, see [SECURITY.md](SECURITY.md).

---

### Documentation

- **README.md** — Quick start, architecture overview, component catalog
- **ARCHITECTURE.md** — Full system architecture (1,569 lines) with agent decision flows, skill catalog, cross-reference matrix
- **INTEGRATION.md** — Step-by-step installation and verification guide
- **PERMISSION-MODES.md** — Claude Code permission mode compatibility
- **SECURITY.md** — Security policy, vulnerability reporting, security considerations
- **CHANGELOG.md** — Keep a Changelog format with full v1.0.0 changes
- **LICENSE** — MIT License

Agent definitions: `claude-code/agents/*.md` (5 files)
Skill definitions: `claude-code/skills/*/SKILL.md` (32 files)
Protocols: `claude-code/_shared/protocols/*.md` (4 files)

---

### Contributing

Contributions are welcome. To get started:

1. Open an issue to discuss the change you would like to make
2. Fork the repository and create a feature branch
3. Submit a pull request with a clear description of the changes

Please keep changes focused and include relevant context in your PR description.

---

### Roadmap (Post-v1.0.0)

Future releases may include:

- **Runtime tool detection** — graceful degradation when Task tool is unavailable
- **Alternative delegation mechanisms** — bash-based subagent invocation for simple tasks
- **Permission mode testing** — comprehensive compatibility matrix across all modes
- **Expanded skill catalog** — additional DevOps, testing, and analysis skills
- **Multi-language support** — TypeScript, Go, Rust implementer agents
- **CI/CD integration** — GitHub Actions workflows for automated testing and deployment

---

### Acknowledgments

Built with Claude Opus 4.6 and Claude Code.

Special thanks to the open-source community for inspiration from:
- Keep a Changelog (changelog format)
- Semantic Versioning (version scheme)
- RFC 2119 (constraint language)
- Prompts.chat (skill discovery concept)

---

### License

This project is licensed under the [MIT License](LICENSE).

---

### Links

- **Repository**: https://github.com/ribatshepo/Auto-Orchestrate
- **Issues**: https://github.com/ribatshepo/Auto-Orchestrate/issues
- **Security**: https://github.com/ribatshepo/Auto-Orchestrate/security/advisories
- **Claude Code**: https://docs.anthropic.com/en/docs/claude-code

---

**Release v1.0.0** — First public release. Autonomous multi-agent orchestration for Claude Code.
