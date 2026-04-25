# Auto-Orchestrate Pipeline Playbook

Operational guide for running the Big Three pipelines (`/auto-orchestrate`, `/auto-audit`, `/auto-debug`) end-to-end. For concepts and architecture see [README.md](README.md); for constraint details see [`claude-code/commands/`](claude-code/commands/).

## Table of contents

1. [When to use what](#1-when-to-use-what) — decision guide
2. [Pre-flight](#2-pre-flight) — first-time and per-session setup
3. [Scenario walkthroughs](#3-scenario-walkthroughs) — 6 end-to-end flows
4. [Flag cookbook](#4-flag-cookbook) — recipes for common combinations
5. [Reading pipeline output](#5-reading-pipeline-output) — logs, checkpoints, receipts
6. [Failure modes and recovery](#6-failure-modes-and-recovery) — terminal states and what to do
7. [Cross-pipeline handoffs](#7-cross-pipeline-handoffs) — escalation patterns
8. [Troubleshooting](#8-troubleshooting) — common issues and fixes

---

## 1. When to use what

### Decision table

| You want to... | Run | Why |
|---------------|-----|-----|
| Start a new project with formal planning artifacts | `/new-project` → `/auto-orchestrate` | P1-P4 planning artifacts inform execution |
| Ship a feature or complete scope on an existing codebase | `/auto-orchestrate` | Full 0-6 pipeline with triage-driven depth |
| Fix a typo, bump a dep, or other trivial single-file change | `/auto-orchestrate --skip-planning --fast-path` | Bypass orchestrator overhead |
| Verify a codebase matches its spec document | `/auto-audit <spec.md>` | Audit-remediate loop |
| Debug a specific error or failing test | `/auto-debug <error text>` | Triage-research-fix-verify cycle |
| Debug containers / compose issues | `/auto-debug debug docker` | Docker-aware lifecycle analysis |
| Resume the most recent in-progress session (any Big Three) | `/<command> c` | Continues from last checkpoint |
| Inspect task state while a pipeline runs | `/workflow-dash` | Read-only view of current task board |
| Formal org-gate review (Intent / Scope Lock / Dependency / Sprint) | `/gate-review <gate>` | Runs between P-series stages if your org uses gates |
| Conduct sprint ceremony (standup, retro) | `/sprint-ceremony` | Mid-sprint coordination for L/XL projects |

### Decision tree (common entry points)

```
Is there a spec/requirements doc you want to verify code against?
├─ Yes → /auto-audit <spec>
└─ No:
    Is the task a known error / failing test?
    ├─ Yes → /auto-debug <error>
    └─ No:
        Is this a trivial fix (< 20 words, "fix"/"bump"/"typo")?
        ├─ Yes → /auto-orchestrate --skip-planning --fast-path <task>
        └─ No:
            Is this a brand-new project?
            ├─ Yes → /new-project <goals> → /auto-orchestrate
            └─ No → /auto-orchestrate <scope-flag> <task>
```

### Which scope flag?

| Flag | Use when | Triage bumps to |
|------|----------|-----------------|
| *(none)* | Custom objective, no stack-wide constraints | `trivial`/`medium` based on signals |
| `B` | Backend-only work (models, APIs, services, migrations) | `medium` default |
| `F` | Frontend-only work (pages, forms, UI) | `medium` default |
| `S` | Fullstack production-ready build | `complex` (forces planning P1-P4) |

---

## 2. Pre-flight

### First-time setup (once per machine)

```bash
# Verify the Claude Code manifest exists and lists the orchestrator
test -f ~/.claude/manifest.json && grep -q '"orchestrator"' ~/.claude/manifest.json \
    && echo "OK" || echo "MISSING — install auto-orchestrate components"

# Verify researcher and depth_check script are in place (RESEARCH-DEPTH-001)
test -f ~/.claude/agents/researcher.md && echo "researcher OK"
test -f ~/.claude/skills/researcher/scripts/depth_check.py \
    && python3 ~/.claude/skills/researcher/scripts/depth_check.py --selftest \
    && echo "depth_check OK"
```

### Per-session checks (before running any Big Three command)

| Check | Command | What "good" looks like |
|-------|---------|------------------------|
| Clean working tree | `git status` | No uncommitted changes that might conflict with pipeline writes |
| On a feature branch (not main) | `git branch --show-current` | `feature/<descriptor>` or similar — **never run on `main`** |
| No stale in-progress session | `ls -la .orchestrate/*/checkpoint.json 2>/dev/null` | Either empty or all have `"status": "completed"` or `"superseded"` |
| Node/Python toolchain present if needed | `node --version`, `python3 --version` | Whatever your project requires |
| Network access for WebSearch | `curl -s https://pypi.org > /dev/null && echo ok` | Required for researcher at `normal`/`deep`/`exhaustive` tiers |

### Session directories the pipeline creates

```
.orchestrate/<session-id>/     # Per-session checkpoint + stage outputs
  ├── checkpoint.json          # State of truth (read this to inspect progress)
  ├── MANIFEST.jsonl           # Append-only session manifest
  ├── proposed-tasks.json      # Latest task proposals from orchestrator
  ├── planning/                # P1-P4 artifacts (if planning ran)
  └── stage-{0..6}/            # Per-stage outputs + stage-receipt.json

.pipeline-state/               # Cross-pipeline shared state
  ├── research-cache.jsonl     # Cached research (feeds future Stage 0)
  ├── fix-registry.jsonl       # Known fix patterns (feeds auto-debug)
  ├── escalation-log.jsonl     # Cross-command handoffs
  ├── codebase-analysis.jsonl  # Architecture insights
  └── workflow/                # /workflow-* consumers

.domain/                       # Append-only domain memory (persists across sessions)
```

---

## 3. Scenario walkthroughs

### Scenario A: Greenfield project with formal planning

**Context**: New repo, no code, need to build from zero. Team uses organizational gates.

```bash
# Step 1: Frame the project — creates planning artifacts + handoff receipt
/new-project Build a patient records platform with HIPAA compliance, role-based access, and audit logging

# (Inspect the handoff receipt before proceeding)
cat .orchestrate/auto-orc-<YYYYMMDD>-patient-records/handoff-receipt.json

# Step 2: Run the full pipeline — consumes the handoff receipt automatically
/auto-orchestrate S

# (Triage auto-detects security+risk domain flags → bumps research to exhaustive)
# (Planning P1-P4 skipped — handoff receipt has planning_complete: true)
# (Pipeline runs Stage 0 → 6, human_gates default to [2, 5] due to complex triage)

# Step 3: When auto-orchestrate pauses at human gate Stage 2 (specs)
# — review .orchestrate/<session>/stage-2/ artifacts, respond "continue" or "revise"

# Step 4: After pipeline completes, verify against scope contract
/auto-audit .orchestrate/<session>/planning/P2-scope-contract.md scope=S --docker

# Step 5: If audit surfaces gaps, auto-audit invokes orchestrator remediation automatically
#         If Stage 5 validator exhausts fix cycles, it prompts for /auto-debug escalation
/auto-debug c    # only if prompted by the prior command
```

**Expected terminal states**:
- `/new-project` → handoff receipt written with `status: "pending"`
- `/auto-orchestrate` → `completed`, all 6 stages + planning ✓
- `/auto-audit` → `completed` with compliance ≥ 90% (default threshold)
- `/auto-debug` → `completed` if validation errors resolved

### Scenario B: Feature on an existing codebase

**Context**: Established repo, add a dark-mode toggle with user preference persistence.

```bash
# Single command — no planning needed (medium complexity, --skip-planning default)
/auto-orchestrate F Add dark-mode toggle with user preference persistence, respect prefers-color-scheme, cover via E2E tests

# Triage: "add" keyword + single scope flag + 1-2 deliverables → medium complexity
# Research depth: normal (auto-resolved, 3+ WebSearch queries)
# Human gates: [2] default (spec review only)
```

**If it stalls mid-implementation**:

```bash
# Resume — auto-orchestrate picks up where it left off
/auto-orchestrate c
```

**After completion**:

```bash
# Quick verification (no spec needed — check mandatory stages completed)
cat .orchestrate/<session>/checkpoint.json | grep -E '"terminal_state"|"stages_completed"'
```

### Scenario C: Trivial fix via fast-path

**Context**: Bump a dependency version, fix a typo, update a config.

```bash
# Fast-path bypasses orchestrator entirely — 3 spawns total (researcher → engineer → validator)
/auto-orchestrate --skip-planning --fast-path --research-depth=minimal \
    Bump axios from 1.6.0 to 1.7.2

# (Researcher cache-checks → single CVE lookup → 1-page output)
# (Engineer edits package.json/lockfile → runs install)
# (Validator runs test suite; if passes → completed)
```

**Fast-path auto-fallback**: If the researcher discovers the bump is actually a breaking change (major version), `[FAST-PATH-ABORT]` fires and the full pipeline resumes at Stage 0. No manual intervention needed.

### Scenario D: Debug a failing test or error

**Context**: Tests were green, now red. Need to find and fix.

```bash
# Paste the error or describe symptoms
/auto-debug TypeError: Cannot read property 'foo' of undefined at src/users.ts:42

# (Debugger triages → researches if unknown → applies fix → re-runs tests)
# (Default: 5 fix-verify cycles per error)
```

**For Docker / compose issues**:

```bash
/auto-debug debug docker
# (Auto-detects failing containers, reads compose logs, analyzes lifecycle)
```

**For flaky / intermittent bugs** (loosen limits):

```bash
/auto-debug --fix_verify_cycles=10 --stall_threshold=5 \
    Race condition in websocket handler — fails ~1/10 runs
```

### Scenario E: Spec compliance audit

**Context**: You have a spec document and want to verify the codebase matches.

```bash
# Basic audit
/auto-audit docs/api-spec.md

# Scope-targeted: only audit backend against backend sections
/auto-audit docs/api-spec.md scope=B

# With container compliance (docker-compose services match spec)
/auto-audit docs/deployment-spec.md --docker

# Strict compliance threshold (default 90%)
/auto-audit --compliance_threshold=95 docs/strict-spec.md
```

**What happens**: The auditor reads the spec, extracts requirements, greps/reads the codebase for evidence, builds a compliance matrix, identifies gaps, and if gaps exist → invokes `/auto-orchestrate` to remediate. Loops until threshold met or `max_audit_cycles` reached (default 5).

### Scenario F: Release preparation

**Context**: Ready to ship. Want to bundle validation + audit + operational readiness.

```bash
# Flag the session as release-targeted
/auto-orchestrate --release S Final hardening pass for v2.0 launch

# On completion, auto-orchestrate emits [DISPATCH-SUGGEST] TRIG-005
# recommending /release-prep

# Run release prep (org-specific — loads release checklist)
/release-prep

# After actual release, run post-launch hygiene
/post-launch
```

---

## 4. Flag cookbook

Recipes for common situations. Copy-paste and adapt.

### Cost control

```bash
# Trivial task, minimize token spend
/auto-orchestrate --skip-planning --fast-path --research-depth=minimal <task>

# Medium task, but you've already seen the research elsewhere — skip deep research
/auto-orchestrate --research-depth=normal <task>

# Stop after a short budget to inspect progress
/auto-orchestrate --max_iterations=20 <task>
```

### Human-in-the-loop (more oversight)

```bash
# Pause at every stage for human review
/auto-orchestrate --human-gates=all <task>

# Pause only before implementation starts
/auto-orchestrate --human-gates=2 <task>

# Pause at spec review AND validation review (complex-tier default)
/auto-orchestrate --human-gates="2,5" <task>
```

### Rigorous research for risky work

```bash
# Security-sensitive change — force exhaustive tier
/auto-orchestrate --research-depth=exhaustive <task>

# Unfamiliar stack — force deep tier with cross-reference requirement
/auto-orchestrate --research-depth=deep <task>
```

### Recovering a stuck session

```bash
# Resume where you left off
/auto-orchestrate c

# If the session is truly stuck, force a fresh session with the same input
# (the old session is superseded, not deleted)
/auto-orchestrate <original task description>

# If you want to wipe and restart from a specific stage, edit the checkpoint directly:
# .orchestrate/<session>/checkpoint.json → modify stages_completed array, then resume
```

### Debugging with escalating aggressiveness

```bash
# First pass — standard cycles
/auto-debug <error>

# If stalls — more cycles per error
/auto-debug --fix_verify_cycles=10 --stall_threshold=5 <error>

# If still stuck — raise iteration ceiling
/auto-debug --max_iterations=100 --fix_verify_cycles=10 <error>
```

### Audit with remediation tuning

```bash
# Quick audit-only (no remediation)
/auto-audit --max_audit_cycles=1 --max_orchestrate_iterations=0 <spec>

# Full audit-remediate (default behavior)
/auto-audit <spec>

# Strict: high threshold, aggressive remediation
/auto-audit --compliance_threshold=95 --max_audit_cycles=10 <spec>
```

---

## 5. Reading pipeline output

### Log prefix reference

While a pipeline runs, bracketed prefixes in output indicate what's happening. The important ones:

| Prefix | Meaning | Action |
|--------|---------|--------|
| `[STAGE N]` / `[P1:PLANNING]` | Stage boundary | Informational |
| `[GATE]` | Gate passed/failed | If FAILED, agent retries once |
| `[TRIAGE]` | Complexity classification + T-shirt size | Informational; shapes depth/gates |
| `[RESEARCH-DEPTH]` | Resolved tier + source | Informational; confirms tier selection |
| `[CHAIN-FIX]` | Auto-fixed missing `blockedBy` | Informational; no action needed |
| `[DISPATCH-SUGGEST]` | Tier-1 trigger — user may run a followup command | Manual decision |
| `[DISPATCH]` TRIG-N | Tier-2 trigger fired — domain guide invoked | Findings injected into stage context |
| `[HUMAN-GATE]` | Pipeline paused for human review | Respond `continue`/`revise`/`stop` |
| `[THRASH-001]` | State hash collision — system alternating | Pipeline will inject diagnostic task |
| `[AO-INEFF-001]` | Task stuck in_progress ≥ 5 iterations | Marked failed; stall counter doesn't reset |
| `[DIMINISH-001]` | Progress delta < 2% for 5 iterations | Warning; approaching auto-termination |
| `[COST-CEIL-001]` | Consumed > 70% of max_iterations | Warning; approaching cost ceiling |
| `[MULTI-SIGNAL]` | 2+ termination signals active | Pipeline auto-terminating with `auto_terminated` |
| `[ESCALATE]` | Pipeline handing off to another Big Three | Prompt asks for user confirmation |
| `[COMPLETE]` | Pipeline finished successfully | Check terminal state + artifacts |

### Key files to inspect

**Mid-session (pipeline still running)**:

```bash
# Current task state (as auto-orchestrate sees it)
cat .pipeline-state/workflow/task-board.json | jq '.'

# Orchestrator-proposed tasks for latest iteration
cat .orchestrate/<session>/proposed-tasks.json | jq '.tasks[] | {subject, stage, status}'

# Checkpoint snapshot (most authoritative)
cat .orchestrate/<session>/checkpoint.json | jq '{iteration, stages_completed, terminal_state, triage: .triage.complexity}'
```

**Post-session**:

```bash
# Session summary
cat .pipeline-state/command-receipts/auto-orchestrate-<YYYYMMDD>-*.json | jq '.'

# Per-stage work
ls .orchestrate/<session>/stage-3/      # Implementation artifacts
cat .orchestrate/<session>/stage-5/compliance-report.md   # Validator output
cat .orchestrate/<session>/stage-6/     # Documentation produced
```

### Checkpoint schema at a glance

| Field | Indicates |
|-------|-----------|
| `iteration` / `max_iterations` | Budget consumed |
| `stages_completed` | High-water mark: `[0, 1, 2, 3, 4.5, 5, 6]` = fully done |
| `terminal_state` | `null` = running; see §6 for value meanings |
| `triage.complexity` | `trivial` \| `medium` \| `complex` (drives defaults) |
| `triage.tshirt_size` | `XS`-`XL` (drives sprint boundaries) |
| `research_depth.tier` | `minimal`/`normal`/`deep`/`exhaustive` |
| `research_depth.source` | `explicit` \| `handoff` \| `triage-default` \| `escalated` \| `fallback` |
| `thrash_counter` | Non-zero = system has cycled at least once |
| `diminishing_returns_triggered` | `true` = progress has stalled |
| `cost_ceiling_triggered` | `true` = > 70% budget consumed |
| `human_gates` / `human_gate_history` | Configured + consumed human gates |
| `dispatch_log` | Every `[DISPATCH-SUGGEST]` and `[DISPATCH]` fired |

---

## 6. Failure modes and recovery

### Terminal state reference (auto-orchestrate)

| `terminal_state` | Meaning | Recovery |
|-------------------|---------|----------|
| `completed` | All mandatory stages ✓, all tasks ✓ | Nothing to do. Review Stage 6 docs and commit. |
| `completed_stages_incomplete` | Tasks done but stages 0/1/2/4.5/5/6 missing after one retry | Re-run: `/auto-orchestrate c` — mandatory stages will re-inject |
| `max_iterations_reached` | Hit MAX_ITERATIONS cap | Raise: `/auto-orchestrate --max_iterations=200 c` or investigate why progress was slow |
| `stalled` | `STALL_THRESHOLD` iterations with zero progress | Inspect checkpoint. Probably blocked by external dependency. Consider `/auto-debug c` if validation-related |
| `all_blocked` | Every task has unmet `blockedBy` | Dependency deadlock. Inspect task graph, manually unblock a task, resume |
| `user_stopped` | You responded "stop" at a human gate | Fresh run, or edit checkpoint and resume |
| `thrashing` | System alternating between states without net progress | **Don't resume blindly.** Read `thrash_history` — something in the task graph is oscillating. Often a spec/validator disagreement |
| `escalated_to_debug` | Stage 5 validator escalated | Run `/auto-debug c` to pick up the handoff |
| `auto_terminated` | 2+ termination signals fired simultaneously | Same as thrashing — diagnose before resuming. Check `dispatch_log` for recent findings |

### Common patterns

**"I keep hitting max_iterations"** — Either your task is too big (break it up) or orchestrator is ping-ponging between stages. Check `thrash_counter` in checkpoint.

**"Auto-debug keeps proposing the same fix that doesn't work"** — The fix-registry is suggesting a known-bad pattern. Edit `.pipeline-state/fix-registry.jsonl` to remove the stale entry, then resume.

**"Stage 5 validator fails indefinitely"** — After 3 fix iterations the pipeline escalates. If you decline the `/auto-debug` escalation, it ends as `stalled`. To force more validator iterations, re-run and let it try again; to fix manually, inspect `.orchestrate/<session>/stage-5/compliance-report.md`.

**"Researcher keeps saying partial"** — Either WebSearch is unavailable or the tier contract isn't being met. Check the stage-0 output against the depth tier — it may need `--research-depth=normal` if you forced minimal on a non-trivial task.

---

## 7. Cross-pipeline handoffs

### How the three commands chain

```
/auto-orchestrate (Stage 5 validation fails 3x)
    └──[ESCALATE]──► /auto-debug c
                         └──[FIX]──► (optional) /auto-orchestrate c (remediation)

/auto-audit (compliance < threshold)
    └──[REMEDIATE]──► /auto-orchestrate (spawned internally)
                         └──[COMPLETE]──► back to /auto-audit for re-audit

/new-project
    └──[HANDOFF]──► /auto-orchestrate (reads handoff-receipt.json)
```

### Escalation hop limit (ESCALATE-001)

Maximum **2 cross-pipeline escalation hops per error context**. Tracked in `.pipeline-state/escalation-log.jsonl`. Each hop writes a handoff entry with `from_command`, `to_command`, `error_context`. After 2 hops the next target escalates to user instead.

**Domain guide dispatches DO NOT count** — `/security`, `/infra`, `/qa`, `/risk`, `/data-ml-ops`, `/org-ops` are advisory, not pipeline transfers.

### Reading the escalation log

```bash
# See pending handoffs (consumed: false)
jq 'select(.consumed == false)' .pipeline-state/escalation-log.jsonl

# See escalation chain for the current error
jq 'select(.error_context | contains("your-error-string"))' .pipeline-state/escalation-log.jsonl
```

### Manually reset escalation state

If you want to unblock a pipeline that's claiming "2-hop limit reached":

```bash
# Mark all prior handoffs consumed
jq 'if .consumed == false then .consumed = true | .consumed_at = "<now>" else . end' \
    .pipeline-state/escalation-log.jsonl > /tmp/escl.jsonl && mv /tmp/escl.jsonl .pipeline-state/escalation-log.jsonl
```

---

## 8. Troubleshooting

### Pipeline won't start

| Symptom | Cause | Fix |
|---------|-------|-----|
| `[AO-GAP-002] Manifest missing` | `~/.claude/manifest.json` not present | Re-install or copy from repo |
| `[MANIFEST-001] Mandatory X not found` | Pipeline component missing in manifest | Add it or install the missing agent/skill |
| `[BRIDGE-BLOCK] source_gate_status expected PASSED` | Handoff receipt gates not passed | Run `/gate-review <gate>` to pass the required gate |
| `[PLAN-GATE-00N]` on a greenfield project | Planning stage N not completed | Pipeline will execute it automatically; wait for it |

### Pipeline starts but doesn't progress

| Symptom | Cause | Fix |
|---------|-------|-----|
| Task stuck `in_progress` for many iterations | Subagent spawning but failing silently | After 5 iterations, `[AO-INEFF-001]` marks it failed. Wait for auto-cleanup or edit checkpoint |
| `[CHAIN-WARN]` every iteration | Orphaned `blockedBy` references | Orchestrator will self-correct; if persistent, edit proposed-tasks.json |
| `[THRASH-001]` collisions | Validator/implementation loop | Inspect last 3 iterations' stage-receipts to find the disagreement |

### Research-specific issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Researcher emits `status: "partial"` with `depth_shortfall` | Tier contract not met (below query floor, missing section) | Check tier vs task complexity; if mismatch, re-run with `--research-depth=<right-tier>` |
| `[RESEARCH-DEPTH-WARN] Invalid tier` | Typo in flag value | Valid tiers: `minimal`, `normal`, `deep`, `exhaustive`. Case-insensitive |
| All research output identical across sessions | Cache serving stale entries | Edit `.pipeline-state/research-cache.jsonl` to bump `ttl_hours` or remove entries |
| Researcher never uses WebSearch | RES-008 violation — codebase-only mode | Verify WebSearch is available; if not, expect `status: "partial"` |

### `/auto-debug` specific

| Symptom | Cause | Fix |
|---------|-------|-----|
| Proposes wildly different fixes each iteration | Insufficient context | Provide a more specific error description; paste actual stack trace |
| "Docker mode" not auto-detected | No docker keywords in error | Pass `--docker` explicitly |
| Exhausts fix-verify cycles immediately | Error is really an error in test setup, not production code | Narrow the error description to the specific failing symptom |

### `/auto-audit` specific

| Symptom | Cause | Fix |
|---------|-------|-----|
| Compliance always < threshold, never improves | Spec requirements don't match code conventions | Review the compliance matrix output; some requirements may be mis-classified. Consider `--compliance_threshold=80` for incremental progress |
| Audit loops with no progress | Gaps found → remediation spawned → same gaps after | Inspect the gap report; the orchestrator may be unable to satisfy a requirement. Manual intervention needed |
| Docker compliance fails but code looks correct | `docker-compose.yml` service names don't match spec vocabulary | Normalize naming or update spec |

---

## Appendix: Quick command reference

```bash
# Big Three
/auto-orchestrate <task>                     # Full pipeline (with auto-triage)
/auto-orchestrate <scope> <task>             # Scoped: B/F/S
/auto-orchestrate c                          # Resume most recent

/auto-audit <spec.md>                        # Audit + remediate
/auto-audit <spec.md> scope=<B|F|S>          # Scoped audit
/auto-audit c                                # Resume most recent

/auto-debug <error>                          # Debug loop
/auto-debug debug docker                     # Docker-specific
/auto-debug c                                # Resume most recent

# Advanced flags (auto-orchestrate)
--skip-planning                              # Bypass P1-P4
--fast-path                                  # 3-stage bypass (requires --skip-planning)
--research-depth=<minimal|normal|deep|exhaustive>
--human-gates=<"2"|"2,5"|"all">
--release                                    # Mark for release-prep followup
--max_iterations=<N>
--stall_threshold=<N>
--max_tasks=<N>

# Advanced flags (auto-debug)
--docker
--fix_verify_cycles=<N>
--max_iterations=<N>
--stall_threshold=<N>

# Advanced flags (auto-audit)
--docker
--max_audit_cycles=<N>
--max_orchestrate_iterations=<N>
--compliance_threshold=<0-100>

# Phase commands (user-invoked, suggested by Tier-1 triggers)
/new-project <goals>                         # Create planning artifacts
/gate-review <gate>                          # Org gate review
/sprint-ceremony                             # Standup / retro
/active-dev                                  # Sprint status sync (L/XL)
/release-prep                                # Pre-release hygiene
/post-launch                                 # Post-release operations

# Workflow inspection (read-only while Big Three active)
/workflow-dash                               # Current task dashboard
/workflow-next                               # Next suggested task
/workflow-focus                              # Focus stack
```

---

*For constraint details (AUTO-001 through RESEARCH-DEPTH-001), see `claude-code/commands/auto-orchestrate.md`. For architecture, see [README.md](README.md). For changes, see [CHANGELOG.md](CHANGELOG.md).*
