# Auto-Orchestrate

Multi-agent orchestration framework that extends Claude Code with autonomous software engineering workflows.

## Overview

Auto-Orchestrate is a Claude Code extension that adds autonomous multi-agent orchestration to your development workflow. It coordinates specialized AI agents through a structured pipeline — from research and planning through implementation, testing, validation, and documentation — so you can hand off complex engineering tasks and get production-ready results.

The system enforces strict quality gates, manages context budgets across agent handoffs, and supports session persistence with crash recovery, enabling fully autonomous software engineering pipelines.

## Features

- **11-stage hybrid pipeline** — Four planning stages (P1-P4: Intent, Scope, Dependencies, Sprint) followed by seven technical stages (0-6: research, planning, specification, implementation, testing, validation, documentation) with mandatory completion gates and a PRE-RESEARCH-GATE bridging the two phases
- **18 specialized agents** — 2 pipeline-core (orchestrator, researcher), 3 pipeline (debugger, auditor, session-manager), and 13 team agents covering the full engineering role hierarchy
- **2 autonomous subsystems** — `/auto-debug` for cyclic error-fix loops; `/auto-audit` for spec-compliance verification loops
- **38 task-specific skills** — Testing, security auditing, accessibility checking, documentation, DevOps, Docker validation, refactoring, CI/CD, dependency analysis, debugging diagnostics, spec compliance, cost estimation, observability setup, and more
- **Session management with crash recovery** — Checkpoint-based sessions that persist across interruptions and can be resumed
- **Task decomposition with parallel execution** — Product-manager decomposes work into dependency graphs for optimized scheduling (Program planning)
- **Zero-error gates and mandatory validation** — Security audits, compliance checks, and technical debt measurement enforced before completion
- **Context-efficient orchestration** — Under 10K tokens per agent handoff, keeping orchestration overhead minimal
- **No-auto-commit policy** — The dev-workflow skill generates conventional commit messages and displays copy-pasteable git commands without executing them automatically

## Prerequisites

- **Claude Code CLI** — [Anthropic's official CLI for Claude](https://docs.anthropic.com/en/docs/claude-code)
- **Python 3** — Required for skill scripts (no pip dependencies needed)
- **Docker Engine >= 27.1.1** — Required for docker-validator skill (Stage 5a); includes Docker Compose

## Installation

Clone the repository and run the install script:

```bash
git clone https://github.com/ribatshepo/Auto-Orchestrate.git
cd Auto-Orchestrate
chmod +x install.sh
./install.sh
```

The install script copies the following into `~/.claude/`:

- `agents/` — Agent definition files
- `skills/` — All 38 skill directories
- `commands/` — Command definitions (auto-orchestrate, auto-debug, auto-audit)
- `_shared/` — Protocols, templates, references, and style guides
- `manifest.json` — Component registry used for agent routing
- `settings.json` — Permission and configuration settings

> **Note:** The installer automatically backs up your existing `~/.claude/` configuration to `~/.claude/backup-<timestamp>/` before making changes.

## Quick Start

### Autonomous orchestration

Launch a fully autonomous pipeline with a single command:

```
/auto-orchestrate Build a REST API for user management with authentication, tests, and documentation
```

**Scope flags** target the pipeline at a specific stack layer with pre-built quality specifications:

```
/auto-orchestrate B                          # Backend scope (default objective)
/auto-orchestrate F build the dashboard      # Frontend scope with custom objective
/auto-orchestrate S implement all features   # Fullstack scope
```

| Flag | Scope | Description |
|------|-------|-------------|
| `B`/`b` | Backend | Models, migrations, services, controllers, routes, auth, persistence |
| `F`/`f` | Frontend | Pages, forms, API integrations, child-friendly usability |
| `S`/`s` | Fullstack | Both backend and frontend, production-ready end-to-end |
| *(omitted)* | Custom | No scope injection — follows user input as-is |

**Advanced flags** tune pipeline behavior beyond scope:

| Flag | Values | Description |
|------|--------|-------------|
| `--research-depth` | `minimal` \| `normal` \| `deep` \| `exhaustive` | Override auto-resolved research tier. Controls WebSearch query budget, cache-first behavior, source count per HIGH finding, and output shape. Auto-resolves from triage complexity when omitted (trivial→minimal, medium→normal, complex→deep) with a one-tier bump for security/risk domain flags. See `RESEARCH-DEPTH-001` in `commands/auto-orchestrate.md` Step 0h-pre. |
| `--skip-planning` | *(boolean)* | Bypass P1-P4 planning stages. Use when planning artifacts already exist or for tasks that do not require formal planning. |
| `--fast-path` | *(boolean)* | Enable 3-stage bypass (researcher → software-engineer → validator) for trivial tasks. Requires `--skip-planning` and trivial triage; auto-disables on complexity upgrade. |
| `--human-gates` | `"2,5"` \| `"all"` | Comma-separated stage numbers where pipeline pauses for human review. Empty default applies triage-linked gates (medium→"2", complex→"2,5"). |
| `--release` | *(boolean)* | Mark session as release-targeted. Triggers `/release-prep` dispatch suggestion at successful completion. |

### Research depth examples

The `--research-depth` flag controls how much investigative work the Stage 0 researcher (and P1/P2 planning research) performs. Depth auto-resolves from task complexity when omitted; pass the flag only when you want to override the default.

**Auto-resolved (no flag)** — triage picks the tier for you:

```
/auto-orchestrate Fix typo in login button label
# → trivial complexity → minimal research (cache-first, single CVE check)

/auto-orchestrate Add pagination to the users list
# → medium complexity → normal research (≥3 WebSearch queries, full RES-* contract)

/auto-orchestrate B build a multi-tenant analytics platform with real-time dashboards
# → complex + fullstack signals → deep research (≥10 queries, 2+ sources per HIGH finding)

/auto-orchestrate Implement OAuth2 authentication with audit logging for compliance
# → complex + security/risk domain flags → exhaustive research (auto-bump one tier)
```

**Explicit override** — force a specific tier:

```
# minimal — cheapest, fastest, cache-preferred
/auto-orchestrate --research-depth=minimal Bump Django from 5.0 to 5.0.1

# normal — current default behavior
/auto-orchestrate --research-depth=normal Add Redis caching to the product catalog

# deep — 10+ queries clustered by sub-topic, production-incident patterns
/auto-orchestrate --research-depth=deep B Migrate session store from in-memory to Postgres

# exhaustive — domain-partitioned research (security / performance / operational / UX)
/auto-orchestrate --research-depth=exhaustive S Build HIPAA-compliant patient portal
```

**Combined with other flags**:

```
# Scope + depth override
/auto-orchestrate F --research-depth=deep redesign the admin console with accessibility focus

# Skip planning + minimal depth for a documented trivial fix
/auto-orchestrate --skip-planning --research-depth=minimal Fix broken link in footer

# Release-ready with exhaustive research, human gates at spec and validation
/auto-orchestrate --research-depth=exhaustive --human-gates="2,5" --release \
    S Ship v2.0 with new billing integration
```

**Tier characteristics** (authoritative per `agents/researcher.md` RES-014):

| Tier | WebSearch queries | Sources per HIGH finding | Output shape | Best for |
|------|-------------------|-------------------------|--------------|----------|
| `minimal` | 0-1 (cache-first) | 1 | 1-page summary, CVE-only | Trivial fixes, fast-path |
| `normal` | ≥3 | 1 | Full template (CVEs, Risks & Remedies, Versions) | Most medium tasks |
| `deep` | ≥10 clustered | ≥2 independent | Full template + Production Incident Patterns | Complex tasks, unfamiliar stacks |
| `exhaustive` | ≥30 across domains | ≥3 independent | Domain-partitioned (security / perf / ops / UX) + synthesis | Regulated work, high-risk changes |

The tier propagates through the orchestrator into the researcher's spawn prompt as `RESEARCH_DEPTH`. The researcher self-checks output against the tier contract via `~/.claude/skills/researcher/scripts/depth_check.py` before finalizing the manifest entry. Shortfalls emit `status: "partial"` with a `depth_shortfall` array rather than silently shipping below-contract output.

The system will:

**Planning phase (P1-P4):**
- P1. Frame product intent (Intent Brief)
- P2. Define scope and acceptance criteria (Scope Contract)
- P3. Map dependencies (Dependency Charter)
- P4. Bridge to sprint execution (Sprint Kickoff Brief)

**Technical phase (0-6):**
0. Detect project type (greenfield, existing, or continuation) and verify 9 pipeline components
1. Research requirements and unknowns
2. Decompose the task into an execution plan
3. Write technical specifications (with gate enforcement if organizational gates are active)
4. Implement production code
5. Generate tests
6. Run validation and security gates (with enforced process hooks for code review and testing)
7. Produce documentation (with enforced process hook for documentation completeness)

### Session management

Start, monitor, and manage work sessions:

```
/workflow-start    # Initialize a new work session
/workflow-dash     # View project task dashboard
/workflow-next     # Get the next suggested task
/workflow-focus    # Set focus on a specific task
/workflow-plan     # Enter interactive planning mode
/workflow-end      # Wrap up the current session
```

### Resuming sessions

Sessions are checkpointed automatically in `.orchestrate/<session-id>/checkpoint.json` (project-local). If a session is interrupted, restarting `/auto-orchestrate` with the same task description will detect and resume from the last checkpoint. Legacy sessions from `~/.claude/sessions/` are also detected as a backward-compatible fallback.

You can also use the shorthand `/auto-orchestrate c` to quickly resume the most recent in-progress session.

### Autonomous debugging

Debug errors autonomously with a cyclic triage-research-fix-verify loop. The debugger collects error context, classifies the error, researches the fix if unknown, applies it, verifies, and escalates to the user if iterations are exhausted.

**Basic invocations**:

```
/auto-debug TypeError: Cannot read property 'foo' of undefined at src/users.ts:42
/auto-debug Tests failing after upgrade — jest reports 14 failures in api/handlers
/auto-debug build broken with "Cannot find module '@prisma/client'"
```

**Docker-specific debugging** (container/compose lifecycle, logs, exec):

```
/auto-debug debug docker                       # Auto-detect failing containers
/auto-debug docker-compose up exits code 125
/auto-debug --docker postgres container stuck restarting
```

**Batch/scope debugging** — fix multiple issues in one session:

```
/auto-debug debug all                          # Fix every currently-failing check
/auto-debug fix failing tests                  # Target only test failures
/auto-debug troubleshoot CI pipeline           # Target CI-specific issues
```

**Tuning flags** — override iteration limits for thorny bugs:

```
# More fix-verify cycles per error (default 5) for flaky/intermittent bugs
/auto-debug --fix_verify_cycles=10 Race condition in websocket handler

# Higher iteration ceiling for multi-error cascades
/auto-debug --max_iterations=100 Migration failures after schema change

# Loosen stall threshold (default 3) for environments with slow feedback
/auto-debug --stall_threshold=5 Intermittent network test failures
```

**Resume an in-progress debug session**:

```
/auto-debug c                                  # Resume most recent
```

### Autonomous audit

Verify a codebase against a specification document, then automatically remediate gaps via orchestrator handoff until the codebase complies. The loop runs audit → identify gaps → spawn orchestrator → re-audit.

**Basic invocations**:

```
/auto-audit docs/spec.md                       # Audit against a spec file
/auto-audit requirements.md                    # Any markdown requirements doc
/auto-audit .orchestrate/auto-orc-2026-04-19-billing/stage-2/2026-04-19_billing-spec.md
```

**Scope-targeted audits** — limit remediation to one stack layer:

```
/auto-audit docs/spec.md scope=B               # Backend only
/auto-audit docs/spec.md scope=F               # Frontend only
/auto-audit docs/spec.md scope=S               # Full-stack (default for most specs)
```

**Docker-aware audits** — include container services in compliance check:

```
/auto-audit docs/spec.md --docker              # Check docker-compose services
/auto-audit spec.md --docker scope=B           # Backend + container compliance
```

**Tuning flags** — control remediation aggressiveness:

```
# More audit-remediate cycles (default 5) for large specs
/auto-audit --max_audit_cycles=10 docs/large-spec.md

# Cap remediation orchestrator spawns per cycle (default 100)
/auto-audit --max_orchestrate_iterations=50 docs/spec.md

# Threshold-based pass (default 90% compliance)
/auto-audit --compliance_threshold=95 docs/strict-spec.md
```

**Resume an in-progress audit session**:

```
/auto-audit c                                  # Resume most recent
```

### Pipeline composition

The three Big Three commands compose into a full build-verify-fix workflow. Each writes checkpoints and receipts so the next command can consume prior context.

**Typical greenfield project flow**:

```
# 1. Create planning artifacts (Intent Brief, Scope Contract, Dependency Charter, Sprint Kickoff Brief)
/new-project Build a patient records platform with HIPAA compliance

# 2. Build it — consumes the handoff receipt from /new-project
/auto-orchestrate S  # Fullstack, auto-resolves to deep/exhaustive research via triage

# 3. Verify against the scope contract once build completes
/auto-audit .orchestrate/<session-id>/planning/P2-scope-contract.md scope=S

# 4. Debug any validation failures that surfaced (optional — auto-orchestrate escalates here automatically)
/auto-debug c  # Resume into the prior debug session if auto-orchestrate escalated
```

**Existing project iteration flow**:

```
# Add a feature to an existing codebase
/auto-orchestrate F Add dark-mode toggle with user preference persistence

# Hit an issue mid-pipeline? Resume with the shorthand
/auto-orchestrate c

# After success, audit the shipped work against a spec for regression
/auto-audit docs/dark-mode-spec.md
```

**Fast-path for trivial fixes** (no planning, single-stage):

```
/auto-orchestrate --skip-planning --fast-path --research-depth=minimal \
    Bump axios from 1.6.0 to 1.7.2
```

**Cross-pipeline state**: All three commands share `.pipeline-state/` (escalation log, research cache, codebase analysis, fix registry). This means `/auto-debug` findings feed back into the next `/auto-orchestrate` session, and `/auto-audit` consumes prior research without re-running WebSearch.

## Architecture Overview

```
User Input
    |
    v
/auto-orchestrate  (command)
    |
    v
orchestrator  (agent) ──> session-manager
    |                          |
    |── product-manager ───> P1 Intent Brief, P2 Scope Contract
    |── tech-program-mgr ──> P3 Dependency Charter
    |── engineering-mgr ───> P4 Sprint Kickoff Brief
    |       |
    |   [PRE-RESEARCH-GATE]
    |       |
    |── researcher ──────────> Research (Stage 0, mandatory)
    |── product-manager ───> Task decomposition
    |── software-engineer ─> Code + self-review + security gate
    |── technical-writer ──> Docs (maintain-don't-duplicate)
    |
    v
Completion (all mandatory gates passed)

/auto-debug  (command)
    |
    v
debugger  (agent) ──> debug-diagnostics
    |── researcher (optional: unfamiliar errors)
    v
Fix verified ──> Debug report in .debug/<session-id>/

/auto-audit  (command)
    |
    v
auditor  (agent) ──> spec-compliance
    |
    v
Compliance report ──> Gap found? ──> orchestrator (remediation) ──> Re-audit
```


### Pipeline Stages

The pipeline is an 11-stage hybrid: P1 -> P2 -> P3 -> P4 -> 0 -> 1 -> 2 -> 3 -> 4.5 -> 5 -> 6.

**Planning stages (P-series):**

| Stage | Component | Purpose | Required |
|-------|-----------|---------|----------|
| P1 | product-manager | Frame product intent (Intent Brief) | **Yes** |
| P2 | product-manager | Define scope contract (Scope Contract) | **Yes** |
| P3 | technical-program-manager | Map dependencies (Dependency Charter) | **Yes** |
| P4 | engineering-manager | Bridge to sprint execution (Sprint Kickoff Brief) | **Yes** |

The PRE-RESEARCH-GATE blocks Stage 0 until all P-series stages are complete.

**Technical stages (0-6):**

| Stage | Component | Purpose | Required |
|-------|-----------|---------|----------|
| 0 | researcher | Gather unknowns and context | **Yes** |
| 1 | product-manager | Decompose into tasks with dependencies | **Yes** |
| 2 | spec-creator | Write technical specifications | **Yes** |
| 3 | software-engineer | Produce production-ready code | No |
| 4 | test-writer-pytest | Generate tests | No |
| 4.5 | codebase-stats | Measure technical debt impact | **Yes** |
| 5 | validator | Validate compliance and correctness | **Yes** |
| 5a | docker-validator | Docker environment validation, UX testing, state checkpointing | **Yes** (sub-step of 5) |
| 6 | technical-writer | Write/update documentation | **Yes** |

All P-series stages and Stages 0, 1, 2, 4.5, 5, and 6 are mandatory — the pipeline will not terminate until they complete successfully (AUTO-002).

### Constraint System

The framework enforces three constraint sets to maintain quality and predictability:

- **MAIN-001 to MAIN-015** — Orchestrator constraints (delegation-only, context budgets, zero-error gates, file scope discipline, no auto-commit, always-visible processing)
- **IMPL-001 to IMPL-013** — Implementer constraints (no placeholders, one-pass quality, security gates, anti-pattern detection)
- **AUTO-001 to AUTO-007** — Auto-orchestrate constraints (stage monotonicity, mandatory completion, checkpoint integrity)
- **CEILING-001, CHAIN-001** — Pipeline enforcement (stage ceiling limits orchestrator to next incomplete stage, mandatory blockedBy chains between stages)
- **PROGRESS-001, DISPLAY-001** — Visibility constraints (always-visible processing, task board at every iteration)
- **SCOPE-001, SCOPE-002** — Scope constraints (verbatim spec passthrough, template integrity)

See `claude-code/ARCHITECTURE.md` for the full constraint matrix.

## Available Components

### Agents

| Agent | Mandatory Skills | Description |
|-------|-----------------|-------------|
| orchestrator | *(delegates to agents)* | Coordinates workflows by delegating to subagents; enforces MAIN constraints |
| product-manager | spec-analyzer, dependency-analyzer | Decomposes work into task graphs with dependency analysis (4-phase pipeline) |
| software-engineer | production-code-workflow, security-auditor, codebase-stats, refactor-analyzer, refactor-executor | Single-pass implementation with self-review, quality pipeline, and security gate |
| technical-writer | docs-lookup, docs-write, docs-review | Documentation specialist; chains skills for full docs workflow |
| session-manager | workflow-start/end/dash/focus/next/plan | Manages session lifecycle, checkpoints, and crash recovery |
| researcher | researcher (skill), docs-lookup | Internet-enabled research for best practices, CVEs, package analysis |
| debugger | debug-diagnostics | Autonomous debugger: triage, research, fix, verify with minimal blast radius; supports Docker debugging mode |
| auditor | spec-compliance | Read-only spec compliance auditor; produces compliance report + gap-report.json; never modifies code |

### Skills (by domain)

**Quality and Validation**
validator, docker-validator, test-writer-pytest, test-gap-analyzer, security-auditor, codebase-stats

**Debugging and Auditing**
debug-diagnostics, spec-compliance

**Code Implementation**
task-executor, library-implementer-python, production-code-workflow

**Analysis and Planning**
researcher, spec-creator, spec-analyzer, dependency-analyzer

**Documentation**
docs-lookup, docs-write, docs-review

**Refactoring and Infrastructure**
refactor-analyzer, refactor-executor, schema-migrator, error-standardizer, hierarchy-unifier, docker-workflow, cicd-workflow

**Workflow and Session Management**
workflow-start, workflow-dash, workflow-focus, workflow-next, workflow-plan, workflow-end

**Utility and Discovery**
skill-lookup, skill-creator, dev-workflow, python-venv-manager

## Project Structure

```
Auto-Orchestrate/
├── README.md                    # This file
├── LICENSE                      # MIT License
├── CHANGELOG.md                 # Version history and changes
├── protect-branches.sh          # GitHub branch protection manager
├── install.sh     # Installer script
├── uninstall.sh   # Uninstaller script
│
├── .orchestrate/                # Per-session orchestration output (gitignored)
│
└── claude-code/                 # Main system directory
    ├── ARCHITECTURE.md          # System architecture documentation
    ├── INTEGRATION.md           # Integration guide
    ├── PERMISSION-MODES.md      # Permission mode documentation
    ├── manifest.json            # Component registry (agent/skill routing)
    ├── settings.json            # Configuration and permissions
    │
    ├── agents/                  # Agent definitions (18 agents)
    │   ├── orchestrator.md
    │   ├── product-manager.md
    │   ├── software-engineer.md
    │   ├── technical-writer.md
    │   ├── researcher.md
    │   ├── session-manager.md
    │   ├── debugger.md
    │   └── auditor.md
    │
    ├── commands/                # Command definitions
    │   ├── auto-orchestrate.md  # Autonomous orchestration loop
    │   ├── auto-debug.md        # Autonomous debug loop
    │   └── auto-audit.md        # Autonomous audit loop
    │
    ├── lib/                     # Python libraries (CI engine + domain memory)
    │   ├── ci_engine/           # Continuous improvement engine
    │   │   ├── ooda_controller.py        # Within-run OODA feedback loop
    │   │   ├── stage_metrics_collector.py # Telemetry (12 DMAIC KPIs)
    │   │   ├── root_cause_classifier.py  # 8-category failure classification
    │   │   ├── retrospective_analyzer.py # Post-run analysis (PDCA Check)
    │   │   ├── improvement_recommender.py # Cross-run targets (PDCA Act)
    │   │   ├── baseline_manager.py       # Rolling 10-run baselines
    │   │   ├── knowledge_store_writer.py # Persistent knowledge store
    │   │   ├── run_summary.py            # Run summary dataclass
    │   │   ├── prometheus_exporter.py    # Optional Prometheus metrics
    │   │   ├── schemas/                  # JSON schemas for all data files
    │   │   └── tests/                    # Unit + integration tests
    │   └── domain_memory/       # Cross-session domain knowledge
    │       ├── store.py         # JSONL append/query engine
    │       ├── schemas.py       # Entry dataclasses (6 stores)
    │       ├── indexer.py       # SQLite WAL-mode index
    │       ├── hooks.py         # Pipeline integration hooks
    │       └── tests/           # Tests
    │
    ├── skills/                  # Skill definitions (38 skills)
    │   ├── accessibility-check/
    │   ├── codebase-stats/
    │   ├── cicd-workflow/
    │   ├── cost-estimator/
    │   ├── dependency-analyzer/
    │   ├── docker-validator/
    │   ├── ... (38 skill directories total)
    │   └── _shared/             # Shared Python libraries (layer0-3)
    │
    └── _shared/                 # Shared resources
        ├── protocols/           # Agent communication protocols
        │   ├── subagent-protocol-base.md  # RFC 2119 output rules
        │   ├── output-standard.md         # Unified file naming/structure
        │   ├── output-schemas.md          # Inter-skill JSON schemas
        │   ├── skill-chain-contracts.md   # Skill chaining rules
        │   └── skill-chaining-patterns.md # Invocation patterns
        ├── references/          # Agent-specific reference docs
        ├── schemas/             # JSON schemas (manifest.schema.json)
        ├── templates/           # Skill boilerplate and anti-patterns
        ├── style-guides/        # Documentation style guide
        └── tokens/              # Placeholder token definitions
```

### Session Output Directories

Three runtime directories are created automatically by the autonomous commands. All are **gitignored** and safe to delete between sessions.

```
.orchestrate/<session-id>/       # Created by /auto-orchestrate
├── checkpoint.json              # Session state (atomic write, schema 1.1.0)
├── MANIFEST.jsonl               # Session-level manifest
├── proposed-tasks.json          # Task proposals from orchestrator
├── planning/                    # Planning phase artifacts (P1-P4)
│   ├── p1-intent-brief.md
│   ├── p2-scope-contract.md
│   ├── p3-dependency-charter.md
│   └── p4-sprint-kickoff.md
├── stage-0/                     # Research (YYYY-MM-DD_<slug>.md + stage-receipt.json)
├── stage-1/                     # Architecture (proposed-tasks.json + stage-receipt.json)
├── stage-2/                     # Specs (YYYY-MM-DD_<slug>.md + stage-receipt.json)
├── stage-3/                     # Implementation (stage-receipt.json + changes.md)
├── stage-4/                     # Tests (stage-receipt.json + changes.md)
├── stage-4.5/                   # Codebase metrics (YYYY-MM-DD_<slug>.md)
├── stage-5/                     # Validation (YYYY-MM-DD_<slug>.md)
└── stage-6/                     # Documentation (stage-receipt.json + changes.md)

.debug/<session-id>/             # Created by /auto-debug
├── checkpoint.json
├── MANIFEST.jsonl
├── error-history.jsonl          # Append-only error tracking
├── reports/                     # Debug reports (YYYY-MM-DD_<slug>.md)
├── diagnostics/                 # Diagnostic data
└── logs/                        # Supplementary logs (optional)

.audit/<session-id>/             # Created by /auto-audit
├── checkpoint.json
├── MANIFEST.jsonl
├── cycle-1/                     # Per-cycle subdirectory
│   ├── YYYY-MM-DD_audit-report.md
│   ├── gap-report.json
│   └── stage-receipt.json
└── cycle-N/

.domain/                         # Cross-session domain knowledge
├── research_ledger.jsonl        # Research findings (queryable)
├── decision_log.jsonl           # Architecture decisions
├── pattern_library.jsonl        # Success patterns and anti-patterns
├── fix_registry.jsonl           # Error → fix mappings
├── codebase_analysis.jsonl      # Per-file risk and analysis
├── user_preferences.jsonl       # User corrections
└── domain_index.db              # SQLite index (derived)
```

All output files follow `YYYY-MM-DD_<slug>.<ext>` naming (per `_shared/protocols/output-standard.md`). Each stage writes a `stage-receipt.json` on completion — the standard bridge to domain memory. The `.domain/` directory persists across all sessions and commands, enabling cross-run learning.

## Utilities

### Branch Protection (`protect-branches.sh`)

Manages GitHub branch protection rules and rulesets via the `gh` CLI. Use it to enforce PR-based workflows, restrict who can push to protected branches, and prevent accidental branch deletion.

**Prerequisites:** `gh` CLI >= 2.63.0, `jq`, authenticated via `gh auth login`

**Quick start:**

```bash
# Protect the main branch (require PRs, enforce for admins)
./protect-branches.sh setup-main

# Protect a contributor branch
./protect-branches.sh protect-branch feature/my-feature

# Protect a branch and allow specific users to push (org repos only)
./protect-branches.sh protect-branch feature/my-feature --users alice,bob
```

**Commands:**

| Command | Description |
|---------|-------------|
| `setup-main` | Protect main branch (PR required, admin enforced) |
| `protect-branch <branch> [--users u1,u2]` | Protect a contributor branch, optionally grant push access |
| `grant-access <branch> <user>` | Grant push access to a protected branch (org repos only) |
| `revoke-access <branch> <user>` | Revoke push access from a protected branch (org repos only) |
| `status [branch]` | Show protection status for a branch or the whole repo |
| `help` | Show full usage details |

**Org vs user repos:** Push restrictions (`--users`, `grant-access`, `revoke-access`) are only available for organization-owned repositories. For user-owned repos, the script falls back to PR-only enforcement. The script auto-detects the repo type.

**Repository detection:** The script auto-detects the repository from the current git remote. Override with `REPO=owner/repo`.

**Security:** The script enforces a minimum `gh` CLI version (>= 2.63.0) to mitigate CVE-2024-53858. All inputs are validated against strict patterns to prevent command injection. All API operations are idempotent.

Run `./protect-branches.sh help` for complete usage details, examples, environment variables, and exit codes.

## Documentation

- **[README.md](README.md)** — Getting started guide (this file)
- **[PLAYBOOK.md](PLAYBOOK.md)** — Operational playbook: when to use what, scenario walkthroughs, flag cookbook, failure modes, troubleshooting
- **[ARCHITECTURE.md](claude-code/ARCHITECTURE.md)** — System architecture and constraint matrix
- **[INTEGRATION.md](claude-code/INTEGRATION.md)** — Integration patterns and workflows  
- **[PERMISSION-MODES.md](claude-code/PERMISSION-MODES.md)** — Permission model documentation
- **[CHANGELOG.md](CHANGELOG.md)** — Version history and release changes

## Contributing

Contributions are welcome. See **[CONTRIBUTING.md](CONTRIBUTING.md)** for the full guide, including dev setup, skill creation, agent modification, testing, code style, and PR process.

Quick start:

1. Open an issue to discuss the change you'd like to make
2. Fork the repository and create a feature branch
3. Follow the setup steps in CONTRIBUTING.md
4. Submit a pull request with a clear description of the changes

## License

This project is licensed under the [MIT License](LICENSE).
