---
name: auto-audit
description: |
  Autonomous audit-remediate loop. Audits codebase against spec, identifies gaps,
  invokes orchestrator to implement missing features, re-audits until compliant.
  Crash recovery via session checkpoints.
triggers:
  - auto-audit
  - auto audit
  - audit against spec
  - spec compliance loop
  - audit until compliant
  - verify implementation
  - audit and fix
arguments:
  - name: spec_path
    type: string
    required: true
    description: Path to spec/requirements document to audit against. Pass "c" to continue the most recent in-progress audit session.
  - name: scope
    type: string
    required: false
    description: |
      Scope flag: "F"/"f" (Frontend), "B"/"b" (Backend), "S"/"s" (Full stack).
      Passed through to orchestrator during remediation phase.
  - name: max_audit_cycles
    type: integer
    required: false
    default: 5
    description: Maximum audit-remediate cycles before stopping.
  - name: max_orchestrate_iterations
    type: integer
    required: false
    default: 100
    description: Max orchestrator spawns per remediation phase.
  - name: docker
    type: boolean
    required: false
    default: false
    description: Enable Docker service auditing. Auto-enabled if spec mentions docker/container/compose.
  - name: compliance_threshold
    type: integer
    required: false
    default: 90
    description: Minimum overall compliance percentage to accept (100 = all requirements must fully pass). Used alongside severity-weighted scoring.
  - name: critical_must_pass
    type: boolean
    required: false
    default: true
    description: When true, ALL requirements with MUST/CRITICAL severity must individually pass regardless of overall score. A 95% overall score with a failing CRITICAL requirement is still FAIL.
  - name: resume
    type: boolean
    required: false
    default: false
    description: Explicitly resume the latest in-progress audit session.
  - name: human_gates
    type: string
    required: false
    description: |
      Comma-separated list of audit phases where the loop pauses for human review.
      Values: "A" (pause after audit phase), "B" (pause after remediation phase), "A,B" (both).
      Default: none (fully autonomous).
---

# Autonomous Audit-Remediate Loop

## Core Constraints — IMMUTABLE

| ID | Rule |
|----|------|
| AUD-LOOP-001 | **Dual-gateway** — Spawn ONLY `subagent_type: "auditor"` (Phase A) or `subagent_type: "orchestrator"` (Phase B). Never spawn software-engineer, researcher, debugger, etc. directly. If 2 consecutive retries return empty output, abort with `[AUD-LOOP-001]` message. |
| AUD-LOOP-002 | **Cycle-based termination** — Cannot declare `completed` unless the most recent audit returned verdict PASS or ACCEPTABLE (score ≥ threshold). |
| AUD-LOOP-003 | **Spec context passthrough** — Every auditor spawn receives the FULL spec path. Every orchestrator spawn receives the FULL gap report as enhanced prompt context. Never summarize. |
| AUD-LOOP-004 | **Checkpoint-before-spawn** — Write checkpoint to disk before every agent spawn. |
| AUD-LOOP-005 | **No direct work** — Auto-audit is a meta-loop controller. Never read spec files, scan codebase, run Docker commands, or implement fixes. The auditor and orchestrator agents do all work. |
| AUD-LOOP-006 | **Docker auto-detection** — If spec filename or user arguments contain "docker", "container", "compose", "deploy" (case-insensitive), auto-set `docker: true`. |
| AUD-LOOP-007 | **Cycle history immutability** — Only append to `cycle_history`; never modify existing entries. |
| AUD-LOOP-008 | **Remediation scope injection** — Gap findings from the auditor are injected VERBATIM into the orchestrator spawn prompt. Never summarize, filter, or reinterpret gaps. |
| AUD-LOOP-009 | **Phase ordering** — Phase A (audit) ALWAYS precedes Phase B (remediation) within a cycle. Never remediate without auditing first. |
| PROGRESS-001 | **Always-visible processing** — Output status lines before/after every tool call, spawn, and processing step. See `commands/CONVENTIONS.md` for format. |
| MANIFEST-001 | **Manifest-driven pipeline** — Read `~/.claude/manifest.json` at boot. Pass manifest path to all agent spawns. |
| ESCALATE-001 | **Cross-pipeline escalation hop limit** — Maximum 2 cross-pipeline escalation hops per error context. Before escalating (e.g., advisory hint to auto-debug), check hop count from `.pipeline-state/escalation-log.jsonl`. If ≥ 2, escalate to user instead. Domain guide dispatches (`/security`, `/qa`, `/risk`) do NOT count toward the 2-hop limit. |
| ESCALATE-002 | **Escalation handoff documentation** — Every cross-pipeline escalation writes a handoff to `.pipeline-state/escalation-log.jsonl` with: `from_command`, `to_command`, `escalation_type`, `hop_count`, `timestamp`, `consumed: false`. |
| AUD-RUNTIME-001 | **Runtime verification sandbox** — Runtime verification (Phase 3 of auditor) executes in a sandbox context. CAN: run existing tests, send GET requests to health endpoints, start containers in read-only mode. CANNOT: modify source code, modify config files, write to production data stores, execute POST/PUT/DELETE requests. |
| AUD-RUNTIME-002 | **Runtime finding tagging** — Runtime verification findings are tagged with `[RUNTIME]` prefix in the audit report. Requirements that pass static analysis but fail runtime verification are flagged as `runtime_regression` with severity elevated by one tier (e.g., MAY → SHOULD). |

### Component Taxonomy (TAXONOMY-001)

Auto-audit is a **META-CONTROLLER** — it spawns agents but never does work itself.

| Component | Type | Role in auto-audit |
|-----------|------|-------------------|
| auto-audit | meta-controller | This command (loop controller) |
| auditor | agent | Phase A — audit execution |
| orchestrator | agent | Phase B — remediation execution |
| spec-compliance | skill | Invoked by auditor during Phase A |
| spec-analyzer | skill | Invoked by auditor during Phase A |

> See auto-orchestrate `TAXONOMY-001` for the canonical classification table across all pipelines. Three types: META-CONTROLLER (3), AGENT (17+), SKILL (30+).

## Execution Guard — AUTO-AUDIT IS A META-LOOP CONTROLLER, NOT A WORKER

╔══════════════════════════════════════════════════════════════════════════╗
║  AUTO-AUDIT MUST NEVER:                                                 ║
║                                                                         ║
║  1. Read spec files, project source code, or Docker state              ║
║  2. Analyze requirements, scan for implementations, or run tests       ║
║  3. Apply fixes, edit files, or modify any project state               ║
║  4. Run Docker commands, build processes, or endpoint tests            ║
║  5. Spawn ANY agent type other than auditor or orchestrator            ║
║                                                                         ║
║  AUTO-AUDIT ONLY:                                                       ║
║  - Collects audit parameters from user (Step 1)                        ║
║  - Creates session infrastructure (Step 2)                             ║
║  - Spawns auditor agent for compliance analysis (Step 3)               ║
║  - Processes audit results (Step 4)                                    ║
║  - If gaps found: spawns orchestrator for remediation (Step 5)         ║
║  - After remediation: loops back to Step 3 (re-audit)                  ║
║  - Evaluates termination (Step 6)                                      ║
║                                                                         ║
║  If you catch yourself reading specs, scanning code, running Docker     ║
║  commands, or applying fixes — STOP. You are violating this guard.     ║
╚══════════════════════════════════════════════════════════════════════════╝

## Audit-Remediate Pipeline — Meta-Loop

Auto-audit orchestrates TWO agent types in an outer loop:

```
    ┌──────────────────────────────────────────────────────────┐
    │                                                          │
    ▼                                                          │
Phase A: AUDIT (spawn auditor)                                 │
    │ Produces: compliance score + gap-report.json             │
    │                                                          │
    ├─ If PASS/ACCEPTABLE → DONE                               │
    │                                                          │
    ▼                                                          │
Phase B: REMEDIATE (spawn orchestrator)                        │
    │ Orchestrator runs full pipeline to fix gaps               │
    │ (research → architect → spec → implement → validate)     │
    │                                                          │
    └────────────── loop back to Phase A ──────────────────────┘
```

**Key distinction from auto-orchestrate**: Auto-orchestrate uses a single-gateway (only orchestrator). Auto-audit uses a **dual-gateway** (auditor for analysis, orchestrator for remediation).

**Key distinction from auto-debug**: Auto-debug cycles triage→fix→verify within a single agent type. Auto-audit alternates between TWO different agent types.

## Configuration Defaults

| Parameter | Default | Description |
|-----------|---------|-------------|
| `MAX_AUDIT_CYCLES` | 5 | Max audit-remediate-reaudit cycles |
| `MAX_ORCHESTRATE_ITERATIONS` | 100 | Max orchestrator spawns per remediation phase |
| `COMPLIANCE_THRESHOLD` | 90 | Minimum compliance % for ACCEPTABLE verdict |
| `STALL_THRESHOLD` | 3 | Consecutive no-improvement cycles before stall |
| `CHECKPOINT_DIR` | `.audit/<session-id>/` | Session checkpoint directory |

### Weighted Severity Model (AUD-SEV-001)

The compliance threshold applies to the **overall weighted score**, but individual severity tiers have independent pass criteria:

| Severity | Weight | Individual Gate | Description |
|----------|--------|----------------|-------------|
| MUST / CRITICAL | 3x | **All must pass** (when `critical_must_pass: true`) | Core requirements that define system correctness. A single CRITICAL failure = overall FAIL regardless of score. |
| SHOULD / HIGH | 2x | **Caps verdict at NEEDS_WORK** | Important requirements that significantly impact quality. Contribute double weight to the overall score. Any failing HIGH requirement caps the maximum verdict at NEEDS_WORK regardless of overall score. |
| MAY / MEDIUM | 1x | No individual gate | Nice-to-have requirements. Standard weight contribution. |
| OPTIONAL / LOW | 0.5x | Excluded from threshold | Informational findings. Reported but do not affect pass/fail. |

**Mapping to Three-Tier Process Enforcement Model (E2)**: When auditing process compliance, the enforcement tier from `process_injection_map.md` maps to audit severity:
- **GATE** processes → MUST / CRITICAL severity (3x weight, must pass)
- **ADVISORY** processes → SHOULD / HIGH severity (2x weight, caps verdict at NEEDS_WORK if failing)
- **INFORMATIONAL** processes → MAY / MEDIUM severity (1x weight, no individual gate)

This mapping ensures that triage-upgraded GATE processes (ENFORCE-UPGRADE-001) are treated as CRITICAL requirements in audit scoring.

**Weighted score calculation**:
```
weighted_score = (
    (MUST_pass_count * 3 + SHOULD_pass_count * 2 + MAY_pass_count * 1) /
    (MUST_total * 3 + SHOULD_total * 2 + MAY_total * 1)
) * 100

# PARTIAL requirements count as 0.5 of their weight
# OPTIONAL/LOW requirements excluded from denominator
```

**Verdict logic (replaces simple threshold check)**:
```
IF critical_must_pass AND any MUST/CRITICAL requirement has status != PASS:
    verdict = FAIL
    reason = "CRITICAL requirement(s) not met: <list>"
ELSE IF any SHOULD/HIGH requirement has status == FAIL:
    verdict = NEEDS_WORK
    reason = "HIGH requirement(s) failing: <list> — manual review required"
ELSE IF weighted_score >= 100:
    verdict = PASS
ELSE IF weighted_score >= compliance_threshold:
    verdict = ACCEPTABLE
ELSE:
    verdict = FAIL
```

**Display format** (extends the compliance board in Step 4.2):
```
 COMPLIANCE BOARD (Cycle <N>):
 ┌─ CRITICAL/MUST Requirements ────────────────
 │  PASS: 8/8 (100%) — ALL CRITICAL MET ✓
 ├─ HIGH/SHOULD Requirements ──────────────────
 │  PASS: 5/7 (71%) | PARTIAL: 1 | FAIL: 1
 ├─ MEDIUM/MAY Requirements ───────────────────
 │  PASS: 4/5 (80%) | MISSING: 1
 ├─ Runtime Verification (AUD-RUNTIME-001) ────
 │  Endpoints checked: 5 | Services healthy: 3/4
 │  Runtime regressions: 1 (static-pass, runtime-fail)
 ├─ Weighted Score ────────────────────────────
 │  87.3% [ACCEPTABLE — above 85% threshold]
 │  (unweighted: 81.0%)
 └─────────────────────────────────────────────
```

---

## Step 0: Autonomous Mode Declaration

### 0-pre. Continue Shorthand

If `spec_path` is `"c"` (case-insensitive): treat as `resume: true`, skip Steps 0a and 1, jump to Step 2b. If no in-progress audit session found, abort.

### 0a. Permission Grant

Display once:

> **Audit mode requested.** This will:
> - Read and analyze the spec at `<spec_path>`
> - Scan the codebase for implementation evidence
> - If Docker enabled: check Docker services and endpoints
> - If gaps found: invoke orchestrator to implement missing features
> - Re-audit until compliant or max cycles reached
> - Run up to {{MAX_AUDIT_CYCLES}} audit-remediate cycles
>
> **Proceed with audit?** (Y/n)

If declined, abort: `"Audit session cancelled."`

Record in checkpoint: `"permissions": { "autonomous_operation": true, "audit_access": true, "remediation_access": true, "docker_access": <bool>, "granted_at": "<ISO-8601>" }`

### 0b. Docker Auto-Detection (AUD-LOOP-006)

Scan `spec_path` filename for Docker keywords (case-insensitive):
```
docker, container, compose, deploy, infrastructure, service
```

If ANY keyword found AND `docker` argument not explicitly set:
- Set `docker: true`
- Output: `[AUD-LOOP-006] Docker mode auto-enabled based on spec path`

### 0c. Scope Resolution

| Flag | Resolved | Layers |
|------|----------|--------|
| `F`/`f` | `frontend` | `["frontend"]` |
| `B`/`b` | `backend` | `["backend"]` |
| `S`/`s` | `fullstack` | `["backend", "frontend"]` |
| *(omitted)* | `custom` | `[]` |

**Preprocessing**: Strip surrounding quotes recursively, then trim whitespace.

This scope is passed through to the orchestrator during remediation.

Record: `"scope": { "flag": "<letter>", "resolved": "<scope>", "layers": [...] }`

### 0d. Inline Processing Rule

Step 1 runs INLINE. Do NOT delegate to agents or use `EnterPlanMode`.

### 0e. Manifest Validation

Verify that `~/.claude/manifest.json` exists and contains the `auditor` agent definition:

```bash
test -f ~/.claude/manifest.json && grep -q '"auditor"' ~/.claude/manifest.json && echo "PASS" || echo "FAIL"
```

If FAIL: abort with `[AUD-GAP-002] Manifest missing or auditor agent not found at ~/.claude/manifest.json. Cannot proceed. Run install.sh to install.`

Also verify the `orchestrator` agent exists (needed for remediation phase):

```bash
grep -q '"orchestrator"' ~/.claude/manifest.json && echo "PASS" || echo "FAIL"
```

If FAIL: log `[AUD-WARN] Orchestrator agent not found in manifest — remediation phase will be unavailable` (do not abort; audit-only mode can still proceed).

### 0f. Domain Memory and Shared State Initialization

Ensure `.domain/` and `.pipeline-state/` exist: `mkdir -p .domain .pipeline-state .pipeline-state/command-receipts .pipeline-state/process-log`. Pass `DOMAIN_MEMORY_DIR=.domain` and `PIPELINE_STATE_DIR=.pipeline-state` in auditor and orchestrator spawn prompts.

**Domain memory integration for auditing:**
- **Before audit**: Query `codebase_analysis` for previously identified risks on the same files
- **Before remediation**: Query `fix_registry` for known fixes matching audit gaps
- **After audit**: Append file-level findings to `codebase_analysis`
- **After remediation**: Append successful fixes to `fix_registry`

**Shared state integration** (see `_shared/protocols/cross-pipeline-state.md`):
- **On startup (SHARED-001)**: Read `.pipeline-state/fix-registry.jsonl` for known fixes (SHARED-004), `.pipeline-state/codebase-analysis.jsonl` for prior risk findings, `.pipeline-state/research-cache.jsonl` for cached research (SHARED-003). Read `.pipeline-state/command-receipts/` (STATE-002) for `/security` and `/qa` receipts — recent security or QA reviews inform audit expectations (known issues can be matched against gap findings to avoid redundant reporting).
- **After audit**: Write file-level findings to `.pipeline-state/codebase-analysis.jsonl`
- **After remediation**: Write verified fixes to `.pipeline-state/fix-registry.jsonl`
- **On termination**: Update `.pipeline-state/pipeline-context.json` with audit state. Write receipt to `.pipeline-state/command-receipts/auto-audit-<YYYYMMDD>-<HHMMSS>.json` (STATE-001) with: `inputs: { "spec_path" }`, `outputs: { "verdict", "compliance_score", "cycles_run" }`, `next_recommended_action`: `"auto-orchestrate"` if FAIL (remediation needed), `"release-prep"` if PASS. Write process log entries for all processes assessed (STATE-003) to `.pipeline-state/process-log/<process-id>.jsonl`.

---

## Step 1: Collect Audit Context (Inline)

> **GUARD**: Do NOT read the spec file. Collection uses ONLY the user's arguments. All spec analysis is the auditor agent's job.

Parse arguments and create structured audit context:

```json
{
  "spec_path": "<path>",
  "docker_mode": false,
  "scope": { "flag": null, "resolved": "custom", "layers": [] },
  "compliance_threshold": 90,
  "max_audit_cycles": 5,
  "max_orchestrate_iterations": 100
}
```

Verify spec_path exists (file existence check only — do NOT read contents):
```bash
test -f "$SPEC_PATH" && echo "exists" || echo "not found"
```

If spec not found, abort: `"Spec file not found at <spec_path>. Please provide a valid path."`

---

## Step 2: Initialize Session Checkpoint

### 2a. Ensure directories

```bash
mkdir -p .audit/${SESSION_ID} .audit/${SESSION_ID}/dispatch-receipts
```

**Output structure** (per `_shared/protocols/output-standard.md`): Each audit cycle creates a `cycle-<N>/` subdirectory. On Step 3 (before auditor spawn), create the cycle directory:
```bash
mkdir -p .audit/${SESSION_ID}/cycle-${AUDIT_CYCLE}
```

### 2b. Check for existing audit sessions

```bash
# CROSS-003: Scope scan to current working directory only
find "$(pwd)"/.audit -name "checkpoint.json" -exec grep -l '"status": "in_progress"' {} \; 2>/dev/null
```

**CWD filter**: Only consider sessions under the current working directory.

For EVERY in-progress session: set `"status": "superseded"`, add `"superseded_at"` and `"superseded_by"`. Non-destructive — never delete. If superseded session's `spec_path` matches current: **resume** (skip to Step 3).

Also update `.sessions/index.json` at the project root: set the superseded session's status to `"superseded"` and add `"superseded_at"`. See `commands/SESSIONS-REGISTRY.md` for the registry format and write protocol.

### 2c. Create new session

**Session ID**: `auto-aud-<DATE>-<8-char-slug>` (slug from spec filename).

Create parent tracking task via `TaskCreate` (if unavailable, log `[CROSS-001] TaskCreate unavailable — setting parent_task_id: null` and continue with `parent_task_id: null`), then write checkpoint **atomically** (write to `.audit/<session-id>/checkpoint.tmp.json`, then rename to `checkpoint.json`) to `.audit/<session-id>/checkpoint.json`:

```json
{
  "schema_version": "1.0.0",
  "session_id": "<session-id>",
  "type": "audit",
  "created_at": "<ISO-8601>",
  "updated_at": "<ISO-8601>",
  "status": "in_progress",
  "audit_cycle": 0,
  "max_audit_cycles": 5,
  "max_orchestrate_iterations": 100,
  "compliance_threshold": 90,
  "critical_must_pass": true,
  "stall_threshold": 3,
  "docker_mode": false,
  "spec_path": "<path>",
  "scope": { "flag": null, "resolved": "custom", "layers": [] },
  "permissions": {
    "autonomous_operation": true,
    "audit_access": true,
    "remediation_access": true,
    "docker_access": false,
    "granted_at": "<ISO-8601>"
  },
  "parent_task_id": "<TaskCreate ID>",
  "cycle_history": [],
  "current_phase": "audit",
  "last_compliance_score": null,
  "last_gap_count": null,
  "stall_counter": 0,
  "escalation_hop_count": 0,
  "terminal_state": null
}
```

---

## Step 3: Spawn Auditor — Phase A (Audit)

> **CRITICAL GUARD**: You should arrive here with ZERO knowledge of the spec or project internals. If you have read the spec, scanned the codebase, or run Docker commands — STOP. You are violating the Execution Guard.

**Before spawning** (AUD-LOOP-004): Increment `audit_cycle`, set `current_phase: "audit"`, update `updated_at`, write checkpoint.

### 3a. Display cycle banner

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 AUDIT CYCLE <N> of <max> | Session: <session_id>
 Phase: AUDIT | Docker: ON/OFF | Threshold: <N>%
 Previous Score: <N>% (or "First audit") | Previous Gaps: <N>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 3b. Pre-spawn self-check

Before spawning, verify:
- [ ] Spawning exactly ONE agent with `subagent_type: "auditor"`
- [ ] Have NOT read the spec file or any project files
- [ ] Have NOT run any Docker commands
- [ ] NOT about to "analyze the spec myself because it seems simple"

### 3c. Spawn auditor

Spawn EXACTLY ONE agent: `Agent(subagent_type: "auditor")` using the **Appendix A** template.

> **Note (CROSS-006)**: Single-spawn enforcement is prompt-level only. No API-level guard exists. Monitor for violations in iteration history.

---

## Step 4: Process Audit Results

After auditor returns:

### 4.1 Parse auditor DONE block

Extract:
- `Verdict`: PASS, ACCEPTABLE, or FAIL
- `Compliance-Score`: percentage
- `Requirements-Total`, `Requirements-PASS`, `Requirements-PARTIAL`, `Requirements-MISSING`, `Requirements-FAIL`
- `Services-Total`, `Services-Healthy`, `Services-Unhealthy` (or N/A)
- `Gap-Report`: path to gap-report.json
- `Audit-Report`: path to audit report
- `Remediation-Items`: count of items needing fixes

If DONE block is missing or unparseable, treat as Verdict=FAIL, Compliance-Score=0.

### 4.2 Display compliance board

```
 COMPLIANCE BOARD (Cycle <N>):
 ┌─ CRITICAL/MUST Requirements ────────────────
 │  PASS: 5/5 (100%) — ALL CRITICAL MET ✓
 ├─ HIGH/SHOULD Requirements ──────────────────
 │  PASS: 4/8 (50%) | PARTIAL: 2 | FAIL: 2
 ├─ MEDIUM/MAY Requirements ───────────────────
 │  PASS: 3/7 (43%) | MISSING: 4
 ├─ Services (Docker) ─────────────────────────
 │  Healthy:  3/4
 │  Unhealthy: 1/4 (redis)
 ├─ Weighted Score ────────────────────────────
 │  67.5% [FAIL — below 90% threshold]
 │  (CRITICAL gate: PASSED | Weighted: 67.5% | Unweighted: 60%)
 └─────────────────────────────────────────────
```

### 4.3 Record cycle history (AUD-LOOP-007)

```json
{
  "cycle": N,
  "phase": "audit",
  "verdict": "FAIL",
  "compliance_score": 67.5,
  "requirements": {
    "total": 20,
    "pass": 12,
    "partial": 3,
    "missing": 4,
    "fail": 1
  },
  "services": {
    "total": 4,
    "healthy": 3,
    "unhealthy": 1
  },
  "gap_report_path": ".audit/<session-id>/gap-report.json",
  "remediation_items": 8,
  "delta_from_previous": "+17.5%"
}
```

### 4.4 Save checkpoint

Update checkpoint with: `audit_cycle`, `last_compliance_score`, `last_gap_count`, cycle history, `updated_at`.

### 4.5 Evaluate termination (Step 6)

If terminated, exit. Otherwise continue.

### Auto-Debug Advisory Hint (GAP-CMD-003)

When the gap report contains gaps categorized as `implementation_error` or `runtime_failure`:
1. Display advisory message:
   ```
   [AUD-DEBUG-HINT] Detected <N> implementation errors / runtime failures in gap report.
   These may benefit from autonomous debugging.
   Consider running: /auto-debug
   ```
2. This is **advisory only** — the audit continues normally regardless.
3. **NEVER trigger auto-debug automatically** from auto-audit. The hint is displayed once per audit cycle, not per gap.
4. Log: `[AUD-DEBUG-HINT] Displayed for <N> error-type gaps`

### 4.5-gate Human Checkpoint Gates (HUMAN-GATE-001)

If `human_gates` is configured, check whether the current phase requires human review:

```
IF human_gates is set AND human_gates != "":
    human_gates_list = human_gates.split(",")  # e.g., ["A", "B"]
    
    IF current_phase == "audit" AND "A" IN human_gates_list:
        1. Display audit results summary:
           ╔══════════════════════════════════════════════════════════════╗
           ║  HUMAN REVIEW GATE — Phase A (Audit) completed              ║
           ║                                                              ║
           ║  Compliance Score: <score>%  |  Verdict: <verdict>          ║
           ║  Gaps found: <gap_count>                                     ║
           ║  Gap report: .audit/<session>/gap-report.json               ║
           ║                                                              ║
           ║  Review the audit results and respond:                      ║
           ║  - "continue" or "y" to proceed to remediation              ║
           ║  - "stop" to halt the audit loop                            ║
           ╚══════════════════════════════════════════════════════════════╝
        2. Wait for user input (synchronous)
        3. On "continue"/"y": proceed to Phase B (remediation)
        4. On "stop": set terminal_state to `user_stopped`, terminate
        5. Log: [HUMAN-GATE] Phase A — user response: <response>
    
    IF current_phase == "remediation" AND "B" IN human_gates_list:
        1. Display remediation summary (after orchestrator completes)
        2. Wait for user input
        3. On "continue": proceed to next audit cycle
        4. On "stop": terminate
        5. Log: [HUMAN-GATE] Phase B — user response: <response>
```

**Checkpoint addition**:
```json
{
  "human_gates": [],
  "human_gate_history": []
}
```

### 4.5a Dispatch Trigger Evaluation (DISPATCH-001)

After evaluating termination and before routing based on verdict, evaluate command dispatch triggers per `_shared/protocols/command-dispatch.md`:

1. **Scan gap report for domain guide process ranges**:
   ```
   IF gap_report exists AND verdict == "FAIL":
       FOR EACH gap IN gap_report.gaps:
           process_id = gap.process_id  # e.g., "P-038"
           severity = gap.severity      # e.g., "CRITICAL", "HIGH"
           
           IF severity IN ["CRITICAL", "HIGH"]:
               # Map process ID to domain guide range
               IF process_id IN P-032..P-037:  # QA range (TRIG-010)
                   mark /qa for dispatch
               IF process_id IN P-038..P-043:  # Security range (TRIG-009)
                   mark /security for dispatch
               IF process_id IN P-044..P-048:  # Infra range
                   mark /infra for dispatch
               IF process_id IN P-049..P-053:  # Data/ML range
                   mark /data-ml-ops for dispatch
               IF process_id IN P-062..P-069:  # Org-ops range (TRIG-ORG-001)
                   mark /org-ops for dispatch
               IF process_id IN P-074..P-077:  # Risk range (TRIG-007)
                   mark /risk for dispatch
   ```

2. **For each marked domain guide, invoke via Skill** (Tier 2):
   ```
   FOR EACH domain_guide marked for dispatch:
       a. Write dispatch context file:
          .audit/<session>/dispatch-receipts/dispatch-context-<trigger_id>.json
          Include: trigger_id, source_session, gap details, relevant artifacts
       b. Invoke: Skill(skill: "<domain_guide_skill_name>")
       c. Parse structured dispatch findings from output
       d. Write dispatch receipt:
          .audit/<session>/dispatch-receipts/dispatch-<YYYYMMDD>-<trigger_id>-<4hex>.json
       e. Inject receipt findings into remediation context:
          - Append findings summary to checkpoint.dispatch_context
          - These findings are included in the orchestrator spawn prompt (Step 5b)
       f. Log: [DISPATCH-INVOKE] <trigger_id>: Invoked <command> for <N> HIGH/CRITICAL gaps
   ```

3. **Log summary**: `[DISPATCH] Audit dispatch: <N> domain guides consulted for <M> HIGH/CRITICAL gaps`

> **DISPATCH-GUARD-001**: Skill invocations are NOT Agent spawns. This does NOT violate AUD-LOOP-001 (dual-gateway constraint).

> **DISPATCH-NOCIRCLE-001**: Domain guides invoked here do NOT evaluate dispatch triggers themselves.

**Checkpoint additions** (added to auto-audit checkpoint schema with safe defaults):
```json
{
  "dispatch_log": [],
  "dispatch_context": {},
  "dispatch_summary": null
}
```

### 4.6 Route based on verdict

- If Verdict = PASS or ACCEPTABLE → proceed to termination (Step 6)
- If Verdict = FAIL → proceed to Step 5 (Remediation)

---

## Step 5: Spawn Orchestrator — Phase B (Remediation)

> **AUD-LOOP-001 GUARD**: Only spawn `subagent_type: "orchestrator"` here. Never spawn software-engineer, researcher, or any other agent type.

### 5a. Read gap report

Read the gap report from `.audit/<session-id>/gap-report.json`.

### 5b. Build remediation prompt

Convert gap findings into an orchestrator task description (AUD-LOOP-008 — verbatim injection):

**Token budget check**: Before injection, estimate the gap report token count. If the gap report exceeds approximately 4,000 tokens (~3,000 words):
1. Sort gaps by severity (MUST > SHOULD > MAY) then by status (FAIL > MISSING > PARTIAL)
2. Inject the top-N gaps (enough to fit within 4K tokens) verbatim
3. Append: `[TRUNCATED] Full gap report: .audit/<session-id>/gap-report.json — <M> additional gaps not included. Orchestrator should read full report at this path.`
4. Log: `[AA-INEFF-001] Gap report truncated: <N> of <total> gaps injected (4K token budget)`

If within budget, inject verbatim per AUD-LOOP-008.

See **Appendix B** for the full remediation spawn template.

### 5b.1 Inject dispatch context into remediation prompt

If dispatch receipts were produced in Step 4.5a, append domain guide findings to the remediation prompt:

```
IF checkpoint.dispatch_context is non-empty:
    append to remediation prompt:
    
    ## Domain Guide Analysis (from Command Dispatcher)
    
    The following domain guides were consulted for HIGH/CRITICAL gaps.
    Their findings MUST be addressed during remediation:
    
    FOR EACH dispatch_receipt IN checkpoint.dispatch_context:
        ### [DISPATCH-{trigger_id}] {command} findings
        **Severity**: {receipt.result.severity_max}
        **Summary**: {receipt.result.summary}
        **Action required**: {receipt.next_action.instruction}
```

This enriches the orchestrator's remediation context with expert analysis from domain guides (security review, QA strategy, infrastructure recommendations, etc.).

### 5c. Display remediation banner

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 AUDIT CYCLE <N> | Phase: REMEDIATION
 Gaps to Fix: <count> | Max Orchestrator Iterations: <max>
 Scope: <resolved> | Docker: ON/OFF
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5d. Phase ordering gate (AUD-LOOP-009)

Before entering remediation, verify:
1. Phase A (audit) completed for this cycle — `current_phase` was `"audit"` and gap report exists
2. If Phase A did NOT complete: abort remediation with `[AUD-LOOP-009] Cannot remediate without completed audit. Re-run Step 3.`

### 5e. Set phase and checkpoint

Set `current_phase: "remediation"`, write checkpoint **atomically** (AUD-LOOP-004).

### 5f. blockedBy chain validation (CHAIN-001)

After the orchestrator returns task proposals, validate dependency chains:
- Every task for Stage N (N > 0) must include `blockedBy` referencing at least one Stage N-1 task
- Auto-fix missing chains: `[CHAIN-FIX] Added blockedBy to "<subject>"`
- Log any orphaned task IDs (blockedBy pointing to non-existent tasks)

### 5g. Spawn orchestrator

Spawn EXACTLY ONE agent: `Agent(subagent_type: "orchestrator")` using the **Appendix B** template.

The orchestrator runs its full internal pipeline (research → architecture → spec → implementation → validation → documentation). Auto-audit does NOT manage the orchestrator's internal stages — it only receives the final result.

### 5h. Process orchestrator result

Record remediation in cycle_history:
```json
{
  "cycle": N,
  "phase": "remediation",
  "orchestrator_summary": "<first 1000 chars of orchestrator output>",
  "orchestrate_session_dir": ".orchestrate/<orchestrator-session-id>/",
  "tasks_completed": [],
  "tasks_pending": [],
  "files_modified": [],
  "stages_reached": []
}
```

### 5i. Save checkpoint

### 5j. Loop back to Step 3 (re-audit)

Return to Step 3 to re-audit the codebase after remediation.

---

## Step 6: Termination Conditions

Evaluate in order:

| # | Condition | Status |
|---|-----------|--------|
| 1 | Verdict = PASS (100% weighted compliance AND all CRITICAL pass) | `fully_compliant` |
| 2 | Verdict = ACCEPTABLE (weighted score ≥ threshold AND all CRITICAL pass when `critical_must_pass: true`) | `acceptable_compliance` |
| 2a | Weighted score ≥ threshold BUT CRITICAL requirement(s) failing | `critical_blocked` — cannot accept until CRITICAL requirements pass |
| 2b | Verdict = NEEDS_WORK (HIGH/SHOULD requirement(s) failing, regardless of overall score) | `needs_work` — cannot achieve PASS/ACCEPTABLE until HIGH requirements pass |
| 3 | `audit_cycle >= MAX_AUDIT_CYCLES` | `max_cycles_reached` |
| 4 | `stall_counter >= STALL_THRESHOLD` | `stalled` |
| 5 | User requests stop | `user_stopped` |

**Stall detection**: Compare compliance_score with previous cycle:
- Same or worse score → increment `stall_counter`
- Improvement < 1.0% (absolute) → increment `stall_counter` (epsilon improvement does not count as progress). Log: `[AA-BREAK-002] Compliance improved by only <delta>% (< 1% minimum) — counting as stall`
- Improvement >= 1.0% (absolute) → reset `stall_counter` to 0

**Thrashing detection (THRASH-001)**: Track a rolling window of state hashes (last 4 cycles). State hash = `SHA-256(round(compliance_score) + ":" + gap_count)`. If the current hash matches any previous hash in the window, the audit loop is thrashing — oscillating between the same compliance states without net improvement.
- Log: `[THRASH-001] Compliance state hash collision — cycle <N> matches cycle <M>. Audit loop is thrashing.`
- Increment `thrash_counter`
- If `thrash_counter >= 2`: set terminal_state to `thrashing` and terminate

**Diminishing returns detection (DIMINISH-001)**: Track compliance score improvement per cycle. If improvement < 0.5% (absolute) for 3 consecutive cycles AND `audit_cycle > 2`, fire the diminishing returns signal:
- Log: `[DIMINISH-001] Compliance improvement below 0.5% for 3 consecutive cycles — diminishing returns detected`
- Set `diminishing_returns_triggered: true`

**Cost ceiling detection (COST-CEIL-001)**: If `audit_cycle > 0.7 * MAX_AUDIT_CYCLES`, fire the cost ceiling signal:
- Log: `[COST-CEIL-001] Consumed <audit_cycle>/<MAX_AUDIT_CYCLES> cycles (>70%) — approaching cost ceiling`
- Set `cost_ceiling_triggered: true`

**Multi-signal termination evaluation**: Count active signals (STALL, THRASH, DIMINISH, COST_CEILING):
- 2+ signals → `auto_terminated`. Log: `[MULTI-SIGNAL] 2+ signals active: <signals>. Auto-terminating.`
- 1 signal → warn but continue. Log: `[SIGNAL-WARN] 1 signal active: <signal>. Continuing with caution.`

**Checkpoint additions for 4-signal model**:
```json
{
  "thrash_counter": 0,
  "state_hash_window": [],
  "diminishing_returns_triggered": false,
  "score_improvement_window": [],
  "cost_ceiling_triggered": false
}
```

### Terminal State Reference

| Value | Meaning |
|-------|---------|
| `fully_compliant` | 100% compliance score |
| `acceptable_compliance` | Score >= compliance threshold |
| `max_cycles_reached` | Hit MAX_AUDIT_CYCLES limit |
| `stalled` | No meaningful progress for STALL_THRESHOLD cycles |
| `user_stopped` | User manually cancelled |
| `critical_blocked` | Overall score acceptable but CRITICAL requirements failing |
| `needs_work` | HIGH/SHOULD requirements failing — manual review required |
| `thrashing` | Compliance state oscillating without net improvement |
| `auto_terminated` | 2+ termination signals active simultaneously |

### On Termination

Set `terminal_state` and `status` in checkpoint, update parent task, display:

```
## Auto-Audit Complete

**Session**: <session_id> | **Status**: <terminal_state> | **Cycles**: N/max
**Spec**: <spec_path> | **Final Score**: N% | **Threshold**: N%
**Docker Mode**: ON/OFF | **Scope**: <resolved>

### Compliance Summary
| Status | Count | % |
|--------|-------|---|
| PASS | 15 | 75% |
| PARTIAL | 3 | 15% |
| MISSING | 1 | 5% |
| FAIL | 1 | 5% |

### Docker Services (if applicable)
| Service | Status | Details |
|---------|--------|---------|
| postgres | PASS | Running, healthy, port 5432 |
| redis | FAIL | Unhealthy, ECONNREFUSED |

### Cycle Timeline
| # | Phase | Score | Gaps | Delta | Action |
|---|-------|-------|------|-------|--------|
| 1 | Audit | 67.5% | 8 | — | Initial audit |
| 1 | Remediate | — | — | — | Orchestrator ran 12 iterations |
| 2 | Audit | 85% | 3 | +17.5% | Improvement after remediation |
| 2 | Remediate | — | — | — | Orchestrator ran 8 iterations |
| 3 | Audit | 95% | 1 | +10% | Acceptable (≥90%) |

### Remaining Gaps (if any)
- [PARTIAL] REQ-015: Full-text search — basic works, advanced filters missing
  Evidence: src/search/basic.py exists, no advanced_search module

### Git Commit Instructions
> Auto-audit NEVER commits automatically. Review and commit manually.
**Suggested commits**: [collected from orchestrator DONE blocks]

### Reports (per `_shared/protocols/output-standard.md`)
- Audit report: `.audit/<session-id>/cycle-<N>/YYYY-MM-DD_audit-report.md`
- Gap report: `.audit/<session-id>/cycle-<N>/gap-report.json`
- Stage receipt: `.audit/<session-id>/cycle-<N>/stage-receipt.json`
- Session manifest: `.audit/<session-id>/MANIFEST.jsonl`

### Iteration Timeline (Remediation Details)
| Cycle | Orchestrator Iterations | Tasks Completed | Tasks Pending |
|-------|------------------------|-----------------|---------------|
| 1 | 12 | 5 | 0 |
| 2 | 8 | 3 | 0 |
```

---

## Step 7: Write Audit Receipt

After displaying the termination summary (Step 6), write the audit receipt:

### 7a. Determine next_steps array based on verdict

| Verdict | next_steps |
|---------|-----------|
| `fully_compliant` | `["/sprint-ceremony — implementation fully compliant with spec"]` |
| `acceptable_compliance` | `["/sprint-ceremony — compliance above threshold", "Optional: /auto-audit for remaining gaps"]` |
| `max_cycles_reached` | `["Review remaining gaps manually", "Re-run /auto-audit with targeted scope if needed"]` |
| `stalled` | `["Review audit gap report manually", "Consider /auto-debug for implementation errors", "Re-run /auto-audit after manual fixes"]` |
| `user_stopped` | `["Session manually stopped — resume with /auto-audit c or start new session"]` |

### 7b. Write audit-receipt.json

Write `.audit/{session_id}/audit-receipt.json` atomically:
- Write to `.audit/{session_id}/audit-receipt.tmp.json`
- Validate JSON (python3 -m json.tool)
- Rename to `audit-receipt.json`

Schema (see `~/.claude/processes/schemas/audit-receipt-schema.json` for JSON Schema):
```json
{
  "schema_version": "1.0",
  "session_id": "{session_id}",
  "type": "audit",
  "verdict": "{fully_compliant|acceptable_compliance|needs_work|max_cycles_reached|stalled|user_stopped}",
  "final_compliance_score": {last_compliance_score},
  "compliance_threshold": {compliance_threshold},
  "timestamp": "{ISO-8601 completed_at}",
  "cycle_count": {audit_cycle},
  "gap_count": {last_gap_count},
  "next_steps": [{next_steps_array}],
  "related_orchestrate_session": "{session_id_of_most_recent_orchestrate_session_if_any}"
}
```

### 7c. Update .sessions/index.json

Add or update the audit session entry in `.sessions/index.json`:
- Find existing entry for this session_id (if any)
- Update status to `"complete"` and set `completed_at`
- Add field: `"audit_receipt_path": ".audit/{session_id}/audit-receipt.json"`
- Atomic write: write to `.sessions/index.tmp.json`, validate, rename

### 7d. Display completion hint

After writing the receipt:
```
[AUDIT-COMPLETE] Audit receipt written: .audit/{session_id}/audit-receipt.json
Verdict: {verdict} | Score: {final_compliance_score}%

Next steps:
{for each next_step in next_steps}: - {next_step}
```

---

## Crash Recovery Protocol

Runs at the START of every invocation:

1. Ensure `.audit/` exists
2. Scan for `"status": "in_progress"` checkpoints in `.audit/*/checkpoint.json`
3. If found: same/no spec_path → **Resume**; different spec_path → supersede, start fresh
4. If not found → proceed normally
5. Cross-command awareness: read `.sessions/index.json` (if present) to detect active sessions from other commands. Log any `in_progress` cross-command sessions found. See `commands/SESSIONS-REGISTRY.md`.

### Resume

1. Read checkpoint: restore `audit_cycle`, `cycle_history`, `last_compliance_score`, `stall_counter`, `current_phase`
2. If `current_phase` was "remediation": the orchestrator may have been interrupted — skip to re-audit (Step 3)
3. If `current_phase` was "audit": the auditor may have been interrupted — re-run audit (Step 3)
4. Display recovery summary
5. Resume from current cycle, skip Step 1

---

## Appendix A: Auditor Spawn Prompt Template

Use `Agent(subagent_type: "auditor", max_turns: 15)` with this prompt:

```
## Audit Session Context

SESSION_ID: <session_id>
AUDIT_CYCLE: <N> of <max_audit_cycles>
DOCKER_MODE: <true/false>
COMPLIANCE_THRESHOLD: <percentage>
MANIFEST_PATH: ~/.claude/manifest.json

## Spec to Audit Against
SPEC_PATH: <spec_path>

## Previous Audit Results (if cycle > 1)
Previous compliance score: <N>%
Previous gaps: <N> remediation items
Changes since last audit: Orchestrator ran <N> iterations implementing fixes

<Previous gap summary — which items were flagged for remediation>

## Autonomous Mode Permissions (pre-granted)
Operate without confirmations. Read any project file. Run read-only Bash commands.
NEVER modify any file. NEVER git commit/push. NEVER run docker compose up/down.

## MANDATORY: Skill Loading
╔══════════════════════════════════════════════════════════════╗
║  You MUST read ~/.claude/skills/spec-compliance/SKILL.md     ║
║  BEFORE starting Phase 1.                                    ║
║  Follow its execution flow for requirements extraction       ║
║  and compliance mapping.                                     ║
║                                                              ║
║  ALSO read and use:                                          ║
║  ~/.claude/skills/spec-analyzer/SKILL.md (spec validation)   ║
║  ~/.claude/skills/codebase-stats/SKILL.md (code metrics)     ║
║  ~/.claude/skills/test-gap-analyzer/SKILL.md (test evidence) ║
║  ~/.claude/skills/security-auditor/SKILL.md (security scan)  ║
║                                                              ║
║  When DOCKER_MODE=true, ALSO read:                           ║
║  ~/.claude/skills/docker-validator/SKILL.md                  ║
╚══════════════════════════════════════════════════════════════╝

## Instructions

1. **Phase 1 (Spec Ingestion)**: Read spec at SPEC_PATH. Validate structure
   with spec-analyzer. Parse requirements with spec-compliance/spec_parser.py.

2. **Phase 2 (Codebase Scanning)**: Run spec-compliance/compliance_checker.py.
   Supplement with codebase-stats and test-gap-analyzer for evidence.

3. **Phase 3 (Runtime Verification)**: Supplement static analysis with runtime evidence:
   - Run existing test suites in dry-run/collection mode to verify test coverage
   - If DOCKER_MODE: start containers read-only, hit health endpoints (GET only), verify service connectivity
   - Query database schemas (read-only) to verify migration state
   - Check API endpoint availability (GET /health, GET /api/docs, etc.)
   - Record all runtime evidence in audit report with `[RUNTIME]` prefix
   - **Constraint**: No POST/PUT/DELETE requests, no file modifications, no destructive commands
   - If runtime verification fails (containers won't start, tests error): log `[RUNTIME-SKIP] <reason>` and proceed with static-only analysis

4. **Phase 4 (Docker Audit)**: If DOCKER_MODE, run
   spec-compliance/service_discovery.py. Cross-reference with spec requirements
   AND runtime verification results from Phase 3.

5. **Phase 5 (Report)**: Run security-auditor. Aggregate all findings (static + runtime).
   Write audit report and gap-report.json. Determine verdict using weighted severity model.
   Flag any requirements that passed static analysis but failed runtime verification.

6. **Return DONE block** with all required fields.

## Constraints
- AUD-001: Source-read-only — NEVER modify source files, configuration, or Docker state. MAY execute read-only runtime verification: run existing test suites (`pytest --co`, `npm test -- --dry-run`), hit health/status endpoints, query database schemas (read-only), and check service availability. Runtime verification results supplement static analysis.
- AUD-001a: Runtime audit mode — When DOCKER_MODE=true, the auditor MAY start containers in read-only mode (`docker compose up -d` for health checks), query API endpoints (GET only), and inspect container state. The auditor MUST NOT modify container state, push images, or run destructive commands. After verification, the auditor MUST leave containers in their original state.
- AUD-002: Spec-first — read spec before scanning code
- AUD-003: Evidence-based — cite file paths and line numbers
- AUD-005: Structured output — both report and gap-report.json
- AUD-007: Complete coverage — audit ALL requirements
- AUD-008: Docker only when DOCKER_MODE=true

## Session Isolation
SESSION_ID: <session_id>. All output to .audit/<session_id>/.
```

---

## Appendix B: Orchestrator Remediation Spawn Prompt Template

Use `Agent(subagent_type: "orchestrator", max_turns: 30)` with this prompt:

```
## MANDATORY FIRST ACTION (before boot)
Write `.orchestrate/<SESSION_ID>/proposed-tasks.json` with task proposals for implementing the gaps identified below.

## Remediation Context (from Audit Cycle <N>)

PARENT_TASK_ID: <parent_task_id>
SESSION_ID: <session_id>
AUDIT_CYCLE: <N>
SCOPE: <resolved scope>
SCOPE_LAYERS: <layers array>
STAGE_CEILING: 6
MANIFEST_PATH: ~/.claude/manifest.json

## STAGE_CEILING — HARD STRUCTURAL LIMIT
╔══════════════════════════════════════════════════════════════╗
║  STAGE_CEILING = 6 (full pipeline available)                 ║
║  Follow the standard pipeline:                               ║
║  Stage 0 (Research) → 1 (Architecture) → 2 (Specs) →        ║
║  3 (Implementation) → 4.5 (Stats) → 5 (Validation) →        ║
║  6 (Documentation)                                           ║
╚══════════════════════════════════════════════════════════════╝

## Gap Findings (VERBATIM from auditor — AUD-LOOP-008)

<For each gap from gap-report.json, include full detail:>

### MISSING Requirements
<REQ-ID>: <description>
  Source: <spec source location>
  Priority: <MUST/SHOULD/MAY>
  Evidence: <what was searched, what was NOT found>
  Remediation: <what needs to be built>

### PARTIAL Requirements
<REQ-ID>: <description>
  Source: <spec source location>
  Priority: <MUST/SHOULD/MAY>
  What exists: <evidence of partial implementation>
  What's missing: <specific gaps to fill>

### FAIL Requirements
<REQ-ID>: <description>
  Source: <spec source location>
  Priority: <MUST/SHOULD/MAY>
  What's broken: <specific error/issue>
  Fix needed: <what to fix>

### Unhealthy Services (if Docker)
<SVC-ID>: <service name>
  Status: <FAIL/PARTIAL>
  Current state: <details>
  Fix needed: <what to fix>

## Spec Reference
SPEC_PATH: <spec_path>
The auditor has already analyzed this spec. Focus on implementing the gaps above.

## Domain Agent Activation Protocol

Read and follow `~/.claude/_shared/protocols/agent-activation.md`.
At each stage transition during remediation, evaluate activation rules from `manifest.agents[*].activation_rules`. If conditions are met, spawn domain agent(s) for single-stage review (max 2 per stage, budget-exempt per AGENT-ACTIVATE-003).
Domain review artifacts: `.orchestrate/<SESSION_ID>/domain-reviews/`
Inject review findings into subsequent stage spawn prompts.

## Autonomous Mode Permissions (pre-granted)
Operate without confirmations. Access ~/.claude/ freely. Make assumptions.
Do NOT call EnterPlanMode. NEVER git commit/push.

## Delegation Guard — YOU ARE A COORDINATOR, NOT A WORKER
╔══════════════════════════════════════════════════════════════╗
║  Delegate ALL work to subagents. NEVER implement yourself.   ║
║  Spawn researcher, product-manager, spec-creator, software-engineer ║
║  as needed following the standard pipeline.                  ║
╚══════════════════════════════════════════════════════════════╝

## Instructions
1. Focus ONLY on the gaps identified above. Do not re-implement working features.
2. Follow the standard pipeline: research → architect → spec → implement → validate → doc.
3a. When delegating to orchestrator, include directive: "Researcher MUST verify LATEST stable versions via WebSearch (RES-011, RES-012). Implementer MUST use researcher's Recommended Versions table (IMPL-015). Feedback loop enabled (RES-013)."
3. Propose tasks via .orchestrate/<SESSION_ID>/proposed-tasks.json.
4. Spawn subagents to do ALL work. Never implement yourself.
5. NO AUTO-COMMIT: Never git commit/push.
6. Return PROPOSED_ACTIONS JSON block at end.

{{#if scope != "custom"}}
## Scope
Only work on layers in SCOPE_LAYERS: <layers>
{{/if}}
```
