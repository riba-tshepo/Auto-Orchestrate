---
name: auto-debug
description: |
  Autonomous debugging loop. Collects error context, spawns debugger agent
  repeatedly, cycles through triage-research-fix-verify until all errors resolved.
  Crash recovery via session checkpoints.
triggers:
  - auto-debug
  - auto debug
  - debug code
  - fix errors
  - debug docker
  - troubleshoot
  - diagnose errors
  - debug until fixed
arguments:
  - name: error_description
    type: string
    required: true
    description: The error, symptoms, or directive. Examples: paste an error message, "debug docker", "debug all", "fix failing tests". Pass "c" to continue the most recent in-progress debug session.
  - name: docker
    type: boolean
    required: false
    default: false
    description: Enable Docker-specific debugging (docker logs, container inspection, compose lifecycle). Auto-enabled if error_description mentions docker/container/compose.
  - name: max_iterations
    type: integer
    required: false
    default: 50
    description: Override the maximum number of debugger spawns.
  - name: stall_threshold
    type: integer
    required: false
    default: 3
    description: Override the number of consecutive no-progress iterations before failing.
  - name: fix_verify_cycles
    type: integer
    required: false
    default: 5
    description: Max fix-verify-retry cycles per unique error before escalating to user.
  - name: human_gates
    type: string
    required: false
    description: |
      Comma-separated list of debug stages where the loop pauses for human review.
      Values: "2" (pause after root cause analysis), "3" (pause after fix applied), "2,3" (both).
      Default: none (fully autonomous).
---

# Autonomous Debug Loop

## Core Constraints — IMMUTABLE

| ID | Rule |
|----|------|
| DBG-LOOP-001 | **Debugger-only gateway** — Spawn ONLY `subagent_type: "debugger"`. Never spawn software-engineer, researcher, orchestrator, etc. directly. The debugger agent handles internal delegation. If 2 consecutive retries return empty output, abort with `[DBG-LOOP-001]` message. |
| DBG-LOOP-002 | **Cycle-based termination** — Cannot declare `completed` unless the most recent verification passed with zero errors. Unlike auto-orchestrate (linear stages), auto-debug CYCLES through triage→research→fix→verify. |
| DBG-LOOP-003 | **Error context passthrough** — Every debugger spawn receives the FULL error context: original error, error history, previous fix attempts, and any new errors from failed verification. |
| DBG-LOOP-004 | **Checkpoint-before-spawn** — Write checkpoint to disk before every debugger spawn. |
| DBG-LOOP-005 | **No direct work** — Auto-debug is a loop controller. Never read project files, analyze errors, apply fixes, or run Docker commands. The debugger agent does all of this. |
| DBG-LOOP-006 | **Docker auto-detection** — If `error_description` contains "docker", "container", "compose", "dockerfile", or "port" (case-insensitive), auto-set `docker: true`. Log `[DBG-LOOP-006] Docker mode auto-enabled`. |
| DBG-LOOP-007 | **Error history immutability** — Only append to `error_history`; never modify existing entries. |
| DBG-LOOP-008 | **Fix-verify cycle tracking** — Track per-error fix-verify attempts. After `fix_verify_cycles` failures for the same error, escalate to user with full diagnostic context. |
| PROGRESS-001 | **Always-visible processing** — Output status lines before/after every tool call, spawn, and processing step. Never leave extended silence. See `commands/CONVENTIONS.md` for format. |
| MANIFEST-001 | **Manifest-driven pipeline** — The debugger MUST read `~/.claude/manifest.json` at boot and use it as the authoritative registry for skill discovery. Auto-debug passes the manifest path in every debugger spawn. |
| DBG-LOOP-009 | **Escalation return path** — When the debugger determines that an error is architectural (not a bug) — e.g., missing feature, design flaw, incorrect abstraction — auto-debug MUST offer to escalate back to auto-orchestrate instead of continuing fix attempts. The debugger signals this via `Escalation-Type: architectural` in its DONE block. Auto-debug then displays the return path option to the user. |
| ESCALATE-001 | **Cross-pipeline escalation hop limit** — Maximum 2 cross-pipeline escalation hops per error context. Before escalating to auto-orchestrate (DBG-LOOP-009), check hop count from `.pipeline-state/escalation-log.jsonl`. If `escalation_hop_count >= 2`, escalate to user instead of auto-orchestrate. Domain guide dispatches (`/infra`, `/security`) do NOT count toward the 2-hop limit. |
| ESCALATE-002 | **Escalation handoff documentation** — Every cross-pipeline escalation writes a handoff to `.pipeline-state/escalation-log.jsonl` with: `from_command`, `to_command`, `escalation_type`, `hop_count`, `timestamp`, `consumed: false`. |

### Component Taxonomy (TAXONOMY-001)

Auto-debug is a **META-CONTROLLER** — it spawns agents but never does work itself.

| Component | Type | Role in auto-debug |
|-----------|------|-------------------|
| auto-debug | meta-controller | This command (loop controller) |
| debugger | agent | All stages — triage, research, fix, verify |
| debug-diagnostics | skill | Invoked by debugger for error analysis |
| researcher | agent | Optional subagent spawned by debugger for LOW-confidence errors |

> See auto-orchestrate `TAXONOMY-001` for the canonical classification table across all pipelines. Three types: META-CONTROLLER (3), AGENT (17+), SKILL (30+).

## Execution Guard — AUTO-DEBUG IS A LOOP CONTROLLER, NOT A WORKER

╔══════════════════════════════════════════════════════════════════════════╗
║  AUTO-DEBUG MUST NEVER:                                                 ║
║                                                                         ║
║  1. Read project files, logs, Docker output, or source code            ║
║  2. Analyze errors, diagnose root causes, or research solutions        ║
║  3. Apply fixes, edit files, or modify any project state               ║
║  4. Run Docker commands, tests, or build processes                     ║
║  5. Spawn ANY agent type other than "debugger" (DBG-LOOP-001)          ║
║                                                                         ║
║  AUTO-DEBUG ONLY:                                                       ║
║  - Collects initial error context from user (Step 1)                   ║
║  - Creates session infrastructure (Step 2)                             ║
║  - Spawns debugger agents in a loop (Step 3)                           ║
║  - Processes debugger results and tracks error state (Step 4)          ║
║  - Evaluates termination (Step 5)                                      ║
║                                                                         ║
║  If you catch yourself reading logs, running docker commands,           ║
║  analyzing stack traces, or applying fixes — STOP. You are             ║
║  violating this guard.                                                  ║
╚══════════════════════════════════════════════════════════════════════════╝

## Debug Pipeline — Cyclic, Not Linear

Unlike auto-orchestrate's linear pipeline (Stage 0→1→2→3→4.5→5→6), auto-debug uses a **cyclic** pipeline:

```
    ┌──────────────────────────────────────────────────────────────┐
    │                                                              │
    ▼                                                              │
Stage 0 (Triage) → Stage 1 (Research) → Stage 2 (Root Cause)      │
    → Stage 3 (Fix) → Stage 4 (Verify) ──── FAIL ─────────────────┘
                            │
                          PASS
                            │
                            ▼
                    Stage 5 (Documentation)
```

| Stage | Purpose | Complete when |
|-------|---------|---------------|
| 0 | **Triage** — Gather error context, categorize, collect diagnostics | Error categorized with evidence |
| 1 | **Research** — Research the error, find known solutions | Root causes identified with sources |
| 2 | **Root Cause** — Confirm root cause from evidence | Root cause confirmed and documented |
| 3 | **Fix** — Apply targeted fix | Fix applied to codebase |
| 4 | **Verify** — Prove the fix works | Zero errors on re-test |
| 5 | **Documentation** — Document findings and fix | Debug report written |

**Critical**: Stages 0-4 repeat on verification failure. Stage 5 only runs when Stage 4 passes.

## Configuration Defaults

| Parameter | Default | Description |
|-----------|---------|-------------|
| `MAX_ITERATIONS` | 50 | Hard cap on debugger spawns |
| `STALL_THRESHOLD` | 3 | Consecutive no-progress iterations before fail |
| `FIX_VERIFY_CYCLES` | 5 | Max fix-verify attempts per unique error |
| `CHECKPOINT_DIR` | `.debug/<session-id>/` | Primary checkpoint directory |

---

## Step 0: Autonomous Mode Declaration

### 0-pre. Continue Shorthand

If `error_description` is `"c"` (case-insensitive): treat as resume, skip Steps 0a and 1, jump to Step 2b. If no in-progress debug session found, abort.

### 0a. Permission Grant

Display once:

> **Debug mode requested.** This will:
> - Create/update files in `.debug/<session-id>/`
> - Spawn debugger agents without further prompts
> - Read logs, error messages, and project files to diagnose issues
> - Apply fixes to source code
> - Run tests and Docker commands to verify fixes
> - Run up to {{MAX_ITERATIONS}} debug iterations
>
> **Proceed with debugging?** (Y/n)

If declined, abort: `"Debug session cancelled."`

Record in checkpoint: `"permissions": { "autonomous_operation": true, "debug_access": true, "file_modification": true, "docker_access": true, "granted_at": "<ISO-8601>" }`

### 0b. Docker Auto-Detection (DBG-LOOP-006)

Scan `error_description` for Docker keywords (case-insensitive):

```
docker, container, compose, dockerfile, port, image, volume, network, service, healthcheck
```

If ANY keyword found AND `docker` argument not explicitly set:
- Set `docker: true`
- Output: `[DBG-LOOP-006] Docker mode auto-enabled based on error description`

### 0c. Inline Processing Rule

Step 1 runs INLINE. Do NOT delegate to agents or use `EnterPlanMode`.

### 0d. Manifest Validation

Verify that `~/.claude/manifest.json` exists and contains the `debugger` agent definition:

```bash
test -f ~/.claude/manifest.json && grep -q '"debugger"' ~/.claude/manifest.json && echo "PASS" || echo "FAIL"
```

If FAIL: abort with `[DBG-GAP-002] Manifest missing or debugger agent not found at ~/.claude/manifest.json. Cannot proceed. Run install.sh to install.`

### 0e. Domain Memory and Shared State Initialization

Ensure `.domain/` and `.pipeline-state/` exist: `mkdir -p .domain .pipeline-state .pipeline-state/command-receipts .pipeline-state/process-log`. Pass `DOMAIN_MEMORY_DIR=.domain` and `PIPELINE_STATE_DIR=.pipeline-state` in debugger spawn prompts.

**Domain memory integration for debugging:**
- **Before diagnosis**: Query `fix_registry` for the error fingerprint — if a known fix exists with `verification_result: "pass"`, suggest it immediately
- **After fix verified**: Append error→fix mapping to `fix_registry` so future sessions benefit
- **After diagnosis**: Append codebase findings to `codebase_analysis` for future reference

**Shared state integration** (see `_shared/protocols/cross-pipeline-state.md`):
- **On startup (SHARED-001)**: Read `.pipeline-state/fix-registry.jsonl` for known fixes matching current error fingerprint (SHARED-004 — check before diagnosing). Read `.pipeline-state/codebase-analysis.jsonl` for known risks that may inform diagnosis. Read `.pipeline-state/research-cache.jsonl` for cached research relevant to the error domain (SHARED-003). Read `.pipeline-state/command-receipts/` (STATE-002) for `/infra` receipts — infrastructure reviews may explain environment-related errors.
- **After fix verified**: Write error→fix mapping to `.pipeline-state/fix-registry.jsonl` (SHARED-004 — append-only, shared across all pipelines)
- **On escalation to auto-orchestrate**: Write to `.pipeline-state/escalation-log.jsonl`
- **On termination**: Update `.pipeline-state/pipeline-context.json` with debug state. Write receipt to `.pipeline-state/command-receipts/auto-debug-<YYYYMMDD>-<HHMMSS>.json` (STATE-001) with: `inputs: { "error_description" }`, `outputs: { "errors_resolved", "errors_remaining", "escalations" }`, `next_recommended_action`: `"auto-orchestrate"` if escalation, `null` if resolved.

### 0f. Human-Input Treatment

Command arguments are **human-authored input**: preserve error messages verbatim, don't reinterpret error codes, document assumptions when resolving ambiguity.

---

## Step 1: Collect Error Context (Inline)

> **GUARD**: Do NOT read project files, logs, or source code. Collection uses ONLY the user's input text. All analysis is the debugger agent's job.

Parse the raw error_description and create a structured error context:

```json
{
  "error_input": "<verbatim user error_description>",
  "docker_mode": true,
  "initial_context": {
    "error_type": "user-reported",
    "raw_description": "<verbatim>",
    "docker_keywords_detected": ["docker", "container"],
    "inferred_domain": "<docker|runtime|build|test|configuration|startup|unknown>",
    "has_stack_trace": true,
    "has_error_code": false
  }
}
```

**Domain inference rules** (from user text only — no file reading):

| User text contains | Inferred domain |
|-------------------|-----------------|
| "docker", "container", "compose" | `docker` |
| "test", "pytest", "jest", "spec" | `test` |
| "build", "compile", "webpack", "tsc" | `build` |
| "start", "boot", "startup", "launch" | `startup` |
| "config", "env", "settings", ".env" | `configuration` |
| error class name (TypeError, etc.) | `runtime` |
| none of the above | `unknown` |

---

## Step 2: Initialize Session Checkpoint

### 2a. Ensure directories

```bash
mkdir -p .debug/${SESSION_ID}
mkdir -p .debug/${SESSION_ID}/reports
mkdir -p .debug/${SESSION_ID}/diagnostics
mkdir -p .debug/${SESSION_ID}/logs
mkdir -p .debug/${SESSION_ID}/dispatch-receipts
```

**Output structure** (per `_shared/protocols/output-standard.md`):
- `checkpoint.json` — session state (atomic write)
- `MANIFEST.jsonl` — session-level manifest (append-only)
- `error-history.jsonl` — append-only error tracking (at session root)
- `reports/YYYY-MM-DD_<slug>.md` — per-error debug reports
- `diagnostics/YYYY-MM-DD_<slug>.md` — category-specific diagnostic data
- `logs/` — supplementary logs (optional)

All output files use `YYYY-MM-DD_<slug>.<ext>` naming. Each debug cycle writes a `stage-receipt.json` to the session root after completing triage → fix → verify.

### 2b. Check for existing debug sessions

```bash
# CROSS-003: Scope scan to current working directory only
find "$(pwd)"/.debug -name "checkpoint.json" -exec grep -l '"status": "in_progress"' {} \; 2>/dev/null
```

**CWD filter**: Only consider sessions under the current working directory.

For EVERY in-progress session: set `"status": "superseded"`, add `"superseded_at"` and `"superseded_by"`. Non-destructive — never delete. If superseded session's `original_error` matches current: **resume** (skip to Step 3).

Also update `.sessions/index.json` at the project root: set the superseded session's status to `"superseded"` and add `"superseded_at"`. See `commands/SESSIONS-REGISTRY.md` for the registry format and write protocol.

### 2c. Create new session

**Session ID**: `auto-dbg-<DATE>-<8-char-slug>` (slug from error description).

Create parent tracking task via `TaskCreate` (if unavailable, log `[CROSS-001] TaskCreate unavailable — setting parent_task_id: null` and continue with `parent_task_id: null`), then write checkpoint **atomically** (write to `.debug/<session-id>/checkpoint.tmp.json`, then rename to `checkpoint.json`) to `.debug/<session-id>/checkpoint.json`:

```json
{
  "schema_version": "1.0.0",
  "session_id": "<session-id>",
  "type": "debug",
  "created_at": "<ISO-8601>",
  "updated_at": "<ISO-8601>",
  "status": "in_progress",
  "iteration": 0,
  "max_iterations": 50,
  "stall_threshold": 3,
  "fix_verify_cycles": 5,
  "docker_mode": false,
  "original_error": "<raw error_description>",
  "error_context": {
    "error_input": "...",
    "docker_mode": false,
    "initial_context": { "..." }
  },
  "permissions": {
    "autonomous_operation": true,
    "debug_access": true,
    "file_modification": true,
    "docker_access": true,
    "granted_at": "<ISO-8601>"
  },
  "parent_task_id": "<TaskCreate ID>",
  "iteration_history": [],
  "error_history": [],
  "errors_active": [],
  "errors_resolved": [],
  "fix_verify_attempts": {},
  "current_debug_cycle": 0,
  "terminal_state": null,
  "stall_counter": 0,
  "last_error_snapshot": null,
  "thrash_counter": 0,
  "state_hash_window": [],
  "escalation_hop_count": 0
}
```

---

## Step 3: Spawn Debugger (Loop Entry)

> **CRITICAL GUARD**: You should arrive here with EXACTLY ONE task (the parent tracking task from Step 2c) and ZERO knowledge of the project's internals. If you have read project files, analyzed errors, or run Docker commands — STOP. You are violating the Execution Guard.

**Before spawning** (DBG-LOOP-004): Increment `iteration`, update `updated_at`, write checkpoint.

### 3a. Display iteration banner

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DEBUG ITERATION <N> of <max> | Session: <session_id>
 Docker Mode: <ON/OFF> | Debug Cycle: <M>
 Active Errors: <count> | Resolved: <count>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 3b. Display error board

```
 ERROR BOARD:
 ┌─ Active Errors ─────────────────────────────────
 │  ▶ E-001  ConnectionRefusedError on port 5432   [cycle 2/5]
 │  ○ E-002  ImportError: no module named 'xyz'    [new]
 ├─ Resolved ──────────────────────────────────────
 │  ✓ E-000  Docker build failed: COPY not found   [fixed iter 3]
 └─────────────────────────────────────────────────
 Legend: ✓ resolved  ▶ fixing  ○ new  ✗ escalated
```

### 3c. Pre-spawn self-check

Before spawning, verify:
- [ ] Spawning exactly ONE agent with `subagent_type: "debugger"`
- [ ] Have NOT read any project files, logs, or configs
- [ ] Have NOT analyzed any errors or run any Docker commands
- [ ] Error context is fully assembled from Steps 1-2 and previous iteration results
- [ ] NOT about to "fix it myself because it looks simple"

### 3d. Spawn debugger

Spawn EXACTLY ONE agent: `Agent(subagent_type: "debugger")` using the **Appendix A** template. Never spawn multiple debuggers in parallel. Never spawn non-debugger agents from this loop.

> **Note (CROSS-006)**: Single-spawn enforcement is prompt-level only. No API-level guard exists. Monitor for violations in iteration history.

---

## Step 4: Process Results and Loop

> **DBG-LOOP-001 GUARD**: NEVER spawn a non-debugger agent regardless of debugger output.

After debugger returns, execute these sub-steps with visible progress:

### 4.1 Parse debugger output

Extract from the DONE block:

| Field | Required | Description |
|-------|----------|-------------|
| `Error` | Yes | Original error summary |
| `Category` | Yes | Error category (syntax, runtime, docker, etc.) |
| `Root-Cause` | Yes | Identified root cause |
| `Fix` | Yes | What was changed |
| `Files-Modified` | Yes | List of modified files |
| `Verification` | Yes | PASS or FAIL |
| `Fix-Verify-Cycles` | Yes | Number of internal cycles |
| `New-Errors` | Yes | New errors found, or "none" |
| `Research-Escalated` | No | YES or NO |
| `Researcher-Status` | No | FULL (all queries succeeded), PARTIAL (some queries failed, e.g. WebSearch unavailable), or NONE (no researcher spawned). When PARTIAL: log `[AD-BREAK-002] Researcher returned partial results — debug quality may be degraded` |
| `Docker-Mode` | No | YES or NO |
| `Git-Commit-Message` | No | Suggested commit message |
| `Debug-Report` | No | Path to debug report |

If DONE block is missing or unparseable, treat as FAIL with `New-Errors: "Debugger did not produce structured output"`.

### 4.2 Update error tracking

**If Verification = PASS**:
- Move the error to `errors_resolved` with fix details
- Reset `fix_verify_attempts` for that error
- Check `New-Errors`: if "none", proceed to termination check. If new errors listed, add to `errors_active`.

**If Verification = FAIL**:
- Increment `fix_verify_attempts[error_id]`
- Update error context with new error details from `New-Errors`
- If `fix_verify_attempts[error_id] >= fix_verify_cycles`:
  - Mark error as `escalated`
  - Display to user with full diagnostic context:
    ```
    ⚠ ERROR ESCALATED: E-001 — ConnectionRefusedError on port 5432
    Fix-verify cycles exhausted (5/5). Previous attempts:
    1. Changed DB_PORT in .env → still refused
    2. Restarted postgres container → connection reset
    3. Rebuilt postgres image → same error
    4. Checked pg_hba.conf → no change
    5. Verified network bridge → still failing

    Full diagnostics: .debug/<session-id>/diagnostics/...
    Debug report: .debug/<session-id>/reports/...

    Options:
    - Provide additional context or hints
    - Type "skip" to move to next error
    - Type "stop" to end debug session
    ```
  - Wait for user input (timeout: 60 seconds). If no response within timeout, apply default action:
    - Default: `skip` (move to next error, log `[AD-INEFF-003] Escalation timeout — skipping error E-<id>`)
    - Configurable via `escalation_default` parameter: `skip` | `abort` | `continue`


### 4.2a Error Fingerprinting (AD-GAP-002)

Error identity is determined by fingerprint, NOT by error ID assignment order. Two errors are the **same error** if they share the same fingerprint.

**Fingerprint fields** (all required for identity):
- `exception_type`: The exception class or error code (e.g., `ConnectionRefusedError`, `HTTP 500`)
- `normalized_message`: Error message with variable parts stripped (file paths, ports, timestamps → `<path>`, `<port>`, `<timestamp>`)
- `source_file`: The file where the error originates (from stack trace top frame)

**Excluded from identity** (changes to these do NOT create a new error):
- Line number (may shift after edits)
- Stack trace depth
- Timestamp
- Container ID or process ID

**Fingerprint hash**: `SHA-256(exception_type + ":" + normalized_message + ":" + source_file)` truncated to 16 hex chars.

When a new error appears, compute its fingerprint. If the fingerprint matches an existing error in `error_history`, reuse that error's ID and increment its cycle count. If no match, assign a new error ID.

### 4.2b Dispatch Trigger Evaluation (DISPATCH-001)

After updating error tracking and fingerprinting, evaluate command dispatch triggers per `_shared/protocols/command-dispatch.md`:

1. **Check debugger Category for domain guide triggers**:
   ```
   category = parsed_done_block.Category  # from Step 4.1
   root_cause = parsed_done_block.Root-Cause

   # TRIG-011: Infrastructure/deploy issues
   IF category IN ["docker", "infrastructure", "deploy", "platform", "environment"]:
       dispatch_target = "/infra"
       trigger_id = "TRIG-011"
       condition_summary = "Debugger categorized error as {category}: {root_cause}"

   # TRIG-012: Security-related errors
   ELSE IF category == "security" OR root_cause matches CVE/injection/auth/XSS patterns:
       dispatch_target = "/security"
       trigger_id = "TRIG-012"
       condition_summary = "Debugger identified security-related root cause: {root_cause}"

   ELSE:
       # No dispatch needed for this iteration
       SKIP to Step 4.3
   ```

2. **Invoke domain guide via Skill** (Tier 2):
   ```
   a. Write dispatch context file:
      .debug/<session>/dispatch-receipts/dispatch-context-<trigger_id>.json
      Include: trigger_id, error context, category, root_cause, files_investigated
   b. Invoke: Skill(skill: "<domain_guide_skill_name>")
   c. Parse structured dispatch findings
   d. Write dispatch receipt:
      .debug/<session>/dispatch-receipts/dispatch-<YYYYMMDD>-<trigger_id>-<4hex>.json
   e. Inject receipt context into next debugger spawn prompt:
      Append to debugger spawn context: "Domain guide ({command}) analysis: {summary}"
   f. Log: [DISPATCH-INVOKE] <trigger_id>: Invoked <command> — {findings_count} findings
   ```

3. **Log summary**: `[DISPATCH] Debug dispatch: <N> domain guides consulted`

> **DISPATCH-GUARD-001**: Skill invocations are NOT Agent spawns. This does NOT violate DBG-LOOP-001 (debugger-only gateway).

> **DISPATCH-NOCIRCLE-001**: Domain guides invoked here do NOT evaluate dispatch triggers themselves.

**Checkpoint additions** (added to auto-debug checkpoint schema with safe defaults):
```json
{
  "dispatch_log": [],
  "dispatch_context": {},
  "dispatch_summary": null
}
```

### 4.3 Display updated error board

Same format as Step 3b, reflecting state changes.

### 4.4 Record iteration history (DBG-LOOP-007)

```json
{
  "iteration": N,
  "debug_cycle": M,
  "verification_result": "PASS",
  "errors_active": ["E-002"],
  "errors_resolved": ["E-000", "E-001"],
  "errors_escalated": [],
  "fix_verify_attempt": 1,
  "files_modified": ["src/db.py"],
  "category": "database",
  "root_cause": "Wrong port in DATABASE_URL",
  "summary": "<first 500 chars of debugger output>"
}
```

### 4.5 Save checkpoint (DBG-LOOP-004)

Update checkpoint with current state: `iteration`, `errors_active`, `errors_resolved`, `fix_verify_attempts`, `iteration_history`, `updated_at`.

### 4.6 Stall detection

Compare current vs previous iteration:
- Same `errors_active` count AND same `errors_resolved` count AND same `fix_verify_attempts` values = increment `stall_counter`
- Any change (error resolved, new error found, different error being worked, `fix_verify_attempts` incremented for any error) = reset `stall_counter` to 0

**Stall signals** include: error counts, resolved counts, AND `fix_verify_attempts` per error. A fix attempt that fails verification is still progress (the debugger tried something new).

### 4.6a Thrashing detection (THRASH-001)

Track a rolling window of error state hashes (last 6 iterations). The state hash is computed from: `SHA-256(sorted error_fingerprints + ":" + sorted error_statuses + ":" + sorted files_modified)`.

If the current state hash matches ANY previous hash in the rolling window, the system is **thrashing** — fix A breaks B, fix B breaks A, oscillating without net progress. Thrashing evades the stall detector because counts change every iteration.

When thrashing is detected:
1. Log: `[THRASH-001] Error state hash collision — iteration <N> matches iteration <M>. Debug loop is thrashing.`
2. Increment `thrash_counter` in checkpoint
3. If `thrash_counter >= 2`: set terminal_state to `thrashing` and terminate
4. If `thrash_counter == 1`: log `[THRASH-WARN] First thrashing — providing full oscillation context to debugger` and include both iteration snapshots in the next debugger spawn prompt so it can see the oscillation pattern

**Checkpoint additions**:
```json
{
  "thrash_counter": 0,
  "state_hash_window": []
}
```

**Diminishing returns detection (DIMINISH-001)**: Track `errors_resolved_per_iteration` for the last 3 iterations. If the count is strictly decreasing for 3 consecutive iterations (e.g., 3→2→1 or 2→1→0) AND `iteration > 5`, fire the diminishing returns signal:
- Log: `[DIMINISH-001] Errors resolved per iteration decreasing for 3 consecutive iterations — diminishing returns detected`
- Set `diminishing_returns_triggered: true`

**Cost ceiling detection (COST-CEIL-001)**: If `iteration > 0.7 * max_iterations`, fire the cost ceiling signal:
- Log: `[COST-CEIL-001] Consumed <iteration>/<max_iterations> iterations (>70%) — approaching cost ceiling`
- Set `cost_ceiling_triggered: true`

**Multi-signal termination evaluation**: Count active signals (STALL, THRASH, DIMINISH, COST_CEILING):
- 2+ signals → `auto_terminated`. Log: `[MULTI-SIGNAL] 2+ signals active: <signals>. Auto-terminating.`
- 1 signal → warn but continue. Log: `[SIGNAL-WARN] 1 signal active: <signal>. Continuing with caution.`

**Additional checkpoint fields for 4-signal model**:
```json
{
  "diminishing_returns_triggered": false,
  "errors_resolved_window": [],
  "cost_ceiling_triggered": false
}
```

### 4.7-gate Human Checkpoint Gates (HUMAN-GATE-001)

If `human_gates` is configured, check whether the current debug stage requires human review:

```
IF human_gates is set AND human_gates != "":
    human_gates_list = human_gates.split(",")  # e.g., ["2", "3"]
    
    IF current_debug_stage == "root_cause_identified" AND "2" IN human_gates_list:
        1. Display root cause analysis:
           ╔══════════════════════════════════════════════════════════════╗
           ║  HUMAN REVIEW GATE — Root Cause Analysis completed          ║
           ║                                                              ║
           ║  Error: <error summary>                                     ║
           ║  Root cause: <debugger's diagnosis>                         ║
           ║  Proposed fix: <debugger's recommendation>                  ║
           ║                                                              ║
           ║  Review and respond:                                        ║
           ║  - "continue" or "y" → apply the fix                       ║
           ║  - "reject" → re-run root cause analysis                   ║
           ║  - "stop" → halt debug session                             ║
           ╚══════════════════════════════════════════════════════════════╝
        2. Wait for user input (synchronous)
        3. On "reject": re-run debugger with feedback, log [HUMAN-GATE] Stage 2 — rejected by user
        4. On "stop": terminal_state = user_stopped
    
    IF current_debug_stage == "fix_applied" AND "3" IN human_gates_list:
        1. Display fix summary (files modified, changes made)
        2. Wait for user input
        3. On "continue": proceed to verification
        4. On "revert": mark fix as failed, re-enter debug cycle
        5. On "stop": terminate
        6. Log: [HUMAN-GATE] Stage 3 — user response: <response>
```

**Checkpoint addition**:
```json
{
  "human_gates": [],
  "human_gate_history": []
}
```

### 4.7 Evaluate termination (see Step 5)

### 4.8 If NOT terminated

Update error context with:
- New errors from failed verification
- Updated fix-verify attempt counts
- Previous fix attempts summary (for debugger to avoid repeating)

Return to Step 3.

---

## Step 5: Termination Conditions

### Escalation Return Path (DBG-LOOP-009)

When the debugger identifies an issue as **architectural** (not a targeted bug), auto-debug offers escalation back to auto-orchestrate:

**Detection**: The debugger's DONE block contains `Escalation-Type: architectural` with one of these categories:
- `missing_feature` — The "bug" is actually a feature that was never implemented
- `design_flaw` — The fix requires changing the architecture, not patching code
- `spec_mismatch` — The implementation doesn't match the spec; needs re-spec, not debug
- `dependency_issue` — A dependency needs to be replaced, not patched

**Escalation flow** (subject to ESCALATE-001 hop limit):
```
0. Check escalation_hop_count from checkpoint (initialized from .pipeline-state/escalation-log.jsonl on startup).
   IF escalation_hop_count >= 2:
       Log: [ESCALATE-001] Hop limit reached (2/2). Cannot escalate to auto-orchestrate — escalating to user.
       Display architectural issue to user with full context.
       Skip steps 1-3 below.
1. Debugger returns: Escalation-Type: architectural, Category: <category>
2. Auto-debug displays:
   ```
   [ESCALATE-RETURN] Debugger identified architectural issue (not a bug):
   Category: <category>
   Details: <from debugger DONE block>
   
   This issue requires broader work than debugging can address.
   Options:
   - "escalate" → Create handoff receipt for /auto-orchestrate
   - "continue" → Continue debugging anyway (may not resolve)
   - "stop" → End debug session
   ```
3. If user chooses "escalate":
   a. Write `.debug/<session-id>/escalation-receipt.json`:
      ```json
      {
        "schema_version": "1.0",
        "source_command": "auto-debug",
        "source_session": "<session-id>",
        "escalation_type": "architectural",
        "category": "<category>",
        "error_context": "<original error + debugger findings>",
        "files_investigated": ["<list from debugger>"],
        "suggested_scope": "<debugger recommendation>",
        "created_at": "<ISO-8601>"
      }
      ```
   b. Set terminal_state to `escalated_to_orchestrate`
   c. Display:
      ```
      [ESCALATE-RETURN] Escalation receipt written.
      To continue with broader work, run: /auto-orchestrate <suggested task description>
      Context from this debug session will be available in .debug/<session-id>/
      ```
```

**Escalation receipt consumption**: When `/auto-orchestrate` starts, check for escalation receipts from auto-debug:
1. Scan `.debug/*/escalation-receipt.json` for receipts with no `consumed_at` field
2. If found: inject the escalation context into the enhanced prompt (Step 1)
3. Mark receipt as `consumed_at: <ISO-8601>`
4. Log: `[ESCALATE-RESUME] Consuming escalation from auto-debug session <id>`

Evaluate in order:

| # | Condition | Status |
|---|-----------|--------|
| 1 | `errors_active` is empty AND last verification was PASS | `resolved` |
| 2 | `iteration >= MAX_ITERATIONS` | `max_iterations_reached` |
| 3 | `stall_counter >= STALL_THRESHOLD` | `stalled` |
| 4 | All active errors are `escalated` AND user said "stop" | `escalated` |
| 5 | User explicitly requests stop | `user_stopped` |

### Terminal State Reference

| Value | Meaning |
|-------|---------|
| `resolved` | All errors fixed, verification passed |
| `max_iterations_reached` | Hit MAX_ITERATIONS limit |
| `stalled` | No progress for STALL_THRESHOLD iterations |
| `thrashing` | System alternating between states without net progress |
| `escalated` | All active errors escalated to user, user stopped |
| `escalated_to_orchestrate` | Architectural issue identified, escalated back to /auto-orchestrate |
| `user_stopped` | User manually cancelled |
| `auto_terminated` | 2+ termination signals active simultaneously |

### On Termination

Set `terminal_state` and `status` in checkpoint, update parent task, display:

```
## Debug Session Complete

**Session**: <session_id> | **Status**: <terminal_state> | **Iterations**: N/max
**Docker Mode**: ON/OFF | **Debug Cycles**: M

### Errors Resolved
- ✓ E-000: Docker build failed — COPY path incorrect (fixed iter 3)
  Root cause: Dockerfile referenced ./app but source was in ./src
  Fix: Changed COPY ./app to COPY ./src in Dockerfile line 15
  Files: Dockerfile

- ✓ E-001: ConnectionRefusedError on port 5432 (fixed iter 7)
  Root cause: DATABASE_URL used port 5433 instead of 5432
  Fix: Corrected port in .env
  Files: .env

### Errors Unresolved (if any)
- ✗ E-002: Intermittent timeout on /api/health (escalated after 5 cycles)
  Last known state: Timeout occurs under load, possibly resource-related
  Diagnostics: .debug/<session-id>/diagnostics/2026-03-24_health-timeout.md

### Files Modified (all iterations)
- Dockerfile (line 15: fixed COPY path)
- .env (line 3: corrected DB port)

### Git Commit Instructions
> Auto-debug NEVER commits automatically. Review and commit manually.
**Suggested commits**:
- fix: correct COPY source path in Dockerfile
- fix: use correct PostgreSQL port in DATABASE_URL

### Debug Reports
- .debug/<session-id>/reports/2026-03-24_docker-build.md
- .debug/<session-id>/reports/2026-03-24_connection-refused.md

### Iteration Timeline
| # | Cycle | Error Worked On | Result | Files Changed |
|---|-------|-----------------|--------|---------------|
| 1 | 1 | E-000: Docker build | PASS | Dockerfile |
| 2 | 1 | E-001: Connection refused | FAIL | .env |
| 3 | 2 | E-001: Connection refused | PASS | .env |
| 4 | 1 | E-002: Health timeout | FAIL | — |
| 5 | 2 | E-002: Health timeout | FAIL | — |
```

---

## Crash Recovery Protocol

Runs at the START of every invocation:

1. Ensure `.debug/` exists
2. Scan for `"status": "in_progress"` checkpoints in `.debug/*/checkpoint.json`
3. If found: same/no input → **Resume**; different input → supersede, start fresh
4. If not found → proceed normally
5. Cross-command awareness: read `.sessions/index.json` (if present) to detect active sessions from other commands. Log any `in_progress` cross-command sessions found. See `commands/SESSIONS-REGISTRY.md`.

### Resume

1. Read checkpoint: restore `errors_active`, `errors_resolved`, `error_history`, `fix_verify_attempts`
2. Display recovery summary with error board
3. Resume from `iteration + 1`, skip Step 1

---

## Appendix A: Debugger Spawn Prompt Template

Use `Agent(subagent_type: "debugger", max_turns: 30)` with this prompt:

```
## Debug Session Context

SESSION_ID: <session_id>
ITERATION: <N> of <max_iterations>
DEBUG_CYCLE: <M>
DOCKER_MODE: <true/false>
MANIFEST_PATH: ~/.claude/manifest.json

## Error Context

### Current Error to Debug
<Verbatim error description — original user input or new error from failed verification>

### Error Category (if known from previous triage)
<Category from previous iteration, or "unknown" for first iteration>

### Previous Fix Attempts (if any)
<List of what was tried and what happened — prevents repeating failed approaches>

Attempt 1: <description> → Result: <PASS/FAIL, new error if any>
Attempt 2: <description> → Result: <PASS/FAIL, new error if any>
...

### Error History
<Full error history from checkpoint — all errors seen this session>

| ID | Error | Status | Fixed In | Cycles |
|----|-------|--------|----------|--------|
| E-000 | Docker build failed | resolved | iter 3 | 1 |
| E-001 | ConnectionRefused:5432 | active | — | 2/5 |

## Autonomous Mode Permissions (pre-granted)
Operate without confirmations. Read any project file, log, or config. Apply fixes directly.
NEVER git commit/push. Make reasonable assumptions.

## MANDATORY: Skill Loading
╔══════════════════════════════════════════════════════════════╗
║  You MUST read ~/.claude/skills/debug-diagnostics/SKILL.md   ║
║  BEFORE starting Phase 1 (Triage).                           ║
║  Follow its execution flow for error categorization.         ║
║                                                              ║
║  When DOCKER_MODE=true, ALSO read:                           ║
║  ~/.claude/skills/docker-workflow/references/troubleshooting.md║
║  ~/.claude/skills/docker-validator/SKILL.md                  ║
║                                                              ║
║  For unfamiliar errors (confidence LOW), spawn a             ║
║  researcher subagent — do NOT guess.                         ║
╚══════════════════════════════════════════════════════════════╝

## Instructions

1. **Phase 1 (Triage)**: Read error context. Invoke debug-diagnostics skill to categorize and collect diagnostics. If DOCKER_MODE: collect container state first.

2. **Phase 2 (Research)**: For HIGH confidence errors, skip to Phase 3. For LOW confidence, spawn `researcher` subagent with specific questions. For Docker errors, read docker-workflow troubleshooting reference.

3. **Phase 3 (Fix)**: Identify root cause from evidence. Apply minimal, targeted fix. Do NOT refactor unrelated code. Do NOT introduce unnecessary dependencies.

4. **Phase 4 (Verify)**: Re-run the failing command/test. If DOCKER_MODE: rebuild and restart containers, check health. If FAIL and internal cycle < 3: loop back to Phase 1 with new error. If FAIL and cycle >= 3: return with FAIL status.

5. **Phase 5 (Report)**: Write debug report to .debug/<SESSION_ID>/reports/. Update error-history.jsonl.

6. **Return DONE block** with all required fields (see debugger agent spec).

## Constraints
- DBG-001: Evidence-first — cite specific log lines, not guesses
- DBG-002: Minimal blast radius — fix only what's broken
- DBG-003: Verify before declaring fixed
- DBG-004: Fix immediately when root cause found
- DBG-005: NEVER git commit/push
- DBG-009: Max 3 internal fix-verify cycles, then return FAIL
- DBG-011: One error at a time
- DBG-012: Preserve all diagnostic data
- DBG-013: When spawning researcher for package/dependency errors, include directive: "Verify LATEST stable version via WebSearch (RES-011, RES-012). Do NOT rely on training data for version numbers."

## Session Isolation
SESSION_ID: <session_id>. All output files go to .debug/<session_id>/.
```
