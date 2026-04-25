# Auto-Orchestrate

Multi-agent orchestration framework that extends Claude Code with autonomous software engineering workflows.

## Overview

Auto-Orchestrate is a Claude Code extension that adds autonomous multi-agent orchestration to your development workflow. It coordinates specialized AI agents through a structured pipeline — from research and planning through implementation, testing, validation, and documentation — so you can hand off complex engineering tasks and get production-ready results.

The system enforces strict quality gates, manages context budgets across agent handoffs, and supports session persistence with crash recovery, enabling fully autonomous software engineering pipelines.

## Features

- **11-stage hybrid pipeline** — Four planning stages (P1-P4: Intent, Scope, Dependencies, Sprint) followed by seven technical stages (0-6: research, planning, specification, implementation, testing, validation, documentation) with mandatory completion gates and a PRE-RESEARCH-GATE bridging the two phases
- **17 specialized agents** — 1 pipeline-core (orchestrator), 4 pipeline (researcher, debugger, auditor, session-manager), and 12 team agents covering the full engineering role hierarchy
- **48 task-specific skills** — Testing, security auditing, accessibility checking, documentation, DevOps, Docker validation, refactoring, CI/CD, dependency analysis, debugging diagnostics, spec compliance, cost estimation, observability setup, RAID logging, story generation, threat modeling, ADR publication, release notes, SLO definition, CAB review, OKR retrospectives, dependency-matrix generation, sprint-goal linking, and more
- **Single user-facing command** — `/auto-orchestrate` is the only command. Audit (Phase 5v), Debug (Phase 5e), Domain analysis (5q/5s/5i/5d), Release (Phase 7), Post-Launch (Phase 8), and Continuous Governance (Phase 9) all run as internal phases of the single autonomous loop
- **Parallel Stage 3 implementation** — Up to 5 concurrent software-engineers (configurable to 7) when independent stories share no files; hybrid heuristic + explicit-override detection at Stage 1 (PARALLEL-001/002/003 + CHAIN-002 + SE-009)
- **Token-budget optimization suite** — 6 independently-flagged optimizations cut a typical session from ~2.0M to ~1.1M tokens (~45% reduction): manifest digest, per-stage orchestrator templates, skill frontmatter routing, slim receipts, slim handovers, fired-only process injection. All gated by `checkpoint.optimizations.*` flags; reversible without code change
- **8 file-polled human gates** — Intent Review, Scope Lock, Dependency Acceptance, Sprint Readiness, Debug Entry, Compliance Verdict, CAB Review (conditional), Release Readiness — each pauses via `gate-pending-<id>.json` and polls for `gate-approval-<id>.json`
- **Session management with crash recovery** — Checkpoint-based sessions (schema 1.9.0) persist across interruptions and can be resumed
- **Zero-error gates and mandatory validation** — Security audits, compliance checks, and technical debt measurement enforced before completion
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

- `agents/` — 17 agent definition files
- `skills/` — All 48 skill directories
- `commands/` — Single command (`/auto-orchestrate`)
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

### Internal phases (formerly separate commands)

Auto-Orchestrate is **one command**. The previously-separate `/auto-debug`, `/auto-audit`, `/new-project`, `/release-prep`, `/post-launch`, and various domain-guide commands are now **internal phases** of `/auto-orchestrate`. The loop controller activates them automatically based on stage outcomes, scope flags, and process triggers — you do not invoke them directly.

| Internal phase | Triggered when | Equivalent to (legacy) |
|---|---|---|
| Phase 5q (Quality) | Stage 3 completes; or P-032..P-037 flag HIGH/CRITICAL | (qa-engineer activation) |
| Phase 5s (Security) | Stage receipt mentions security threats; or P-038..P-043 flag HIGH/CRITICAL | (security-engineer activation) |
| Phase 5i (Infra/SRE) | Stage 5 fails with infra keywords; or scope flags `infra` | (infra-engineer + sre activation) |
| Phase 5d (Data/ML) | Scope flags `data_ml`; or P-049..P-053 flag HIGH/CRITICAL | (data-engineer + ml-engineer activation) |
| **Phase 5v (Audit)** | Stage 5 PASSES but compliance < threshold | `/auto-audit` |
| **Phase 5e (Debug sub-loop)** | Stage 5 FAILS after 3 fix iterations | `/auto-debug` |
| **Phase 7 (Release Prep)** | `release_flag == true` (set via `--release` or auto-detected) | `/release-prep` |
| **Phase 8 (Post-Launch)** | After Phase 7 OR `triage.mode == "post_launch"` | `/post-launch` |
| **Phase 9 (Continuous Governance)** | tech_debt > 30%, duplication > 15%, CRITICAL RAID items, or cadence boundary | (organizational governance) |

Each internal phase writes a phase receipt to `.orchestrate/<session>/phase-receipts/phase-{name}-{YYYYMMDD}-{HHMMSS}.json` for audit and re-injection into subsequent stages. See `_shared/protocols/command-dispatch.md` "Phase Catalog" for the full catalog.

### Pipeline composition

A single `/auto-orchestrate` invocation walks the entire pipeline end-to-end:

**Typical greenfield project flow**:

```
# Single command — internal phases (P1 → P2 → P3 → P4 → Stage 0..6 → 5q/5s/5i/5d → 5v audit
# → 5e debug if needed → Phase 7 release → Phase 8 post-launch → Phase 9 governance)
# all run automatically based on triage + scope.
/auto-orchestrate S Build a patient records platform with HIPAA compliance --release
```

**Existing project iteration flow**:

```
# Add a feature; planning may be skipped if the project already has stable artefacts
/auto-orchestrate F Add dark-mode toggle with user preference persistence

# Hit an issue mid-pipeline? Resume with the shorthand
/auto-orchestrate c
```

**Fast-path for trivial fixes** (no planning, single-stage):

```
/auto-orchestrate --skip-planning --fast-path --research-depth=minimal \
    Bump axios from 1.6.0 to 1.7.2
```

**Cross-session state**: All sessions share `.pipeline-state/` (escalation log, research cache, codebase analysis, fix registry) and `.domain/` (research ledger, fix registry, pattern library, decision log, codebase analysis, user preferences). Findings from prior sessions feed back into new sessions; researcher checks the cache before issuing new WebSearch queries (SHARED-003).

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
├── SECURITY.md                  # Security policy and vulnerability reporting
├── CHANGELOG.md                 # Version history and changes
├── RELEASE-NOTES.md             # v1.0.0 release notes
├── SECURITY-AUDIT-v1.0.0.md     # Security audit report for v1.0.0
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
    ├── agents/                  # Agent definitions (17 agents)
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
    ├── skills/                  # Skill definitions (48 skills)
    │   ├── accessibility-check/
    │   ├── codebase-stats/
    │   ├── cicd-workflow/
    │   ├── cost-estimator/
    │   ├── dependency-analyzer/
    │   ├── docker-validator/
    │   ├── ... (48 skill directories total)
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

**Security:** The script enforces a minimum `gh` CLI version (>= 2.63.0) to mitigate CVE-2024-53858. All inputs are validated against strict patterns to prevent command injection. All API operations are idempotent. See [SECURITY.md](SECURITY.md) for the full security policy.

Run `./protect-branches.sh help` for complete usage details, examples, environment variables, and exit codes.

## Documentation

- **[README.md](README.md)** — Getting started guide (this file)
- **[PLAYBOOK.md](PLAYBOOK.md)** — Operational playbook: when to use what, scenario walkthroughs, flag cookbook, failure modes, troubleshooting
- **[ARCHITECTURE.md](claude-code/ARCHITECTURE.md)** — System architecture and constraint matrix
- **[INTEGRATION.md](claude-code/INTEGRATION.md)** — Integration patterns and workflows  
- **[PERMISSION-MODES.md](claude-code/PERMISSION-MODES.md)** — Permission model documentation
- **[SECURITY.md](SECURITY.md)** — Security policy and vulnerability reporting
- **[CHANGELOG.md](CHANGELOG.md)** — Version history and release changes
- **[RELEASE-NOTES.md](RELEASE-NOTES.md)** — Latest release notes (v1.0.0)
- **[SECURITY-AUDIT-v1.0.0.md](SECURITY-AUDIT-v1.0.0.md)** — Security audit report for v1.0.0

## Contributing

Contributions are welcome. See **[CONTRIBUTING.md](CONTRIBUTING.md)** for the full guide, including dev setup, skill creation, agent modification, testing, code style, and PR process.

Quick start:

1. Open an issue to discuss the change you'd like to make
2. Fork the repository and create a feature branch
3. Follow the setup steps in CONTRIBUTING.md
4. Submit a pull request with a clear description of the changes

## License

This project is licensed under the [MIT License](LICENSE).
