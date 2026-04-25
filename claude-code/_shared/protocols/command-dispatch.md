# Command Dispatch Protocol

**Version**: 1.0
**Date**: 2026-04-14
**Status**: Active

---

## Purpose

The Command Dispatcher provides a formal mechanism for the Big Three autonomous loops (auto-orchestrate, auto-audit, auto-debug) to invoke phase commands, domain guides, and utility commands based on pipeline conditions. Without this protocol, the Big Three operate in isolation — they can escalate to each other but cannot access security review, QA strategy, infrastructure guidance, risk management, or lifecycle transitions even when pipeline state warrants it.

---

## Constraints

| ID | Rule |
|----|------|
| DISPATCH-001 | **Trigger-based invocation** — The Big Three may invoke any phase command, domain guide, or utility command via the Command Dispatcher. Invocation is trigger-based (not manual). Trigger conditions are defined per-command and evaluated at every stage transition. |
| DISPATCH-002 | **Domain guide activation threshold** — Domain guides are activated when a process in their range is flagged as HIGH or CRITICAL risk during execution. Example: P-038 flagged → `/security` activated for that stage. |
| DISPATCH-003 | **Receipt protocol** — Phase commands and domain guides invoked via dispatch produce receipts consumed by the Big Three. Receipt format defined in the Dispatch Receipt Schema section below. |
| DISPATCH-NOCIRCLE-001 | **No circular dispatch** — Domain guides and phase commands invoked via the dispatcher MUST NOT trigger further dispatch evaluations. Only the Big Three loop controllers evaluate dispatch triggers. A dispatched Skill reads its context, produces output, and returns — it never evaluates the trigger table itself. |
| DISPATCH-GUARD-001 | **Skills, not agents** — Dispatch invocations use the `Skill()` tool, NOT the `Agent()` tool. This preserves gateway constraints (AUTO-001, AUD-LOOP-001, DBG-LOOP-001) which restrict Agent spawns to specific types. Skills are inline capabilities that cannot spawn subagents — they are fundamentally different from autonomous agent spawns. |

---

## Three-Tier Invocation Model

R-010 states "Display only — NEVER auto-invoke" for cross-command lifecycle transitions. The dispatcher reconciles R-010 with DISPATCH-001 by classifying commands into three tiers:

| Tier | Behavior | Commands | Rationale |
|------|----------|----------|-----------|
| **1 — Suggest** | Display `[DISPATCH-SUGGEST]` message. User runs manually. Never auto-invoke. | `/new-project`, `/release-prep`, `/post-launch`, `/sprint-ceremony`, `/gate-review` | Lifecycle boundaries require human intent. R-010 is preserved. These commands start entirely new workflows or represent project milestone transitions. |
| **2 — Auto-invoke** | Invoke via `Skill(skill: "<name>")`. Produce dispatch receipt. Inject findings into pipeline context. | `/security`, `/qa`, `/infra`, `/risk`, `/data-ml-ops`, `/org-ops` | Domain guides are inline capabilities (like spec-creator, validator), not lifecycle transitions. They provide expert analysis that enriches the current pipeline stage. Skills ≠ Agent spawns, so gateway constraints are preserved. |
| **3 — Utility** | Always available for inline use. No dispatch receipt. No trigger conditions required. | `/assign-agent`, `/process-lookup`, `/workflow-dash` | Informational tools with no pipeline impact. The Big Three may use these at any time for routing decisions, process lookup, or status display. |

**Why Tier 2 does NOT violate R-010**: R-010 applies to the `return_path.next_command` pattern — cross-command lifecycle transitions where one command's completion triggers the start of an entirely new command workflow. Domain guide invocations are fundamentally different: they are inline consultations within the current pipeline execution, analogous to reading a protocol file or invoking a skill like `spec-creator`. The domain guide returns findings; the loop controller continues its own execution with enriched context.

**Why Tier 2 does NOT violate gateway constraints**: AUTO-001 says "Spawn ONLY `subagent_type: 'orchestrator'`" — this constrains Agent spawns. `Skill()` invocations are not Agent spawns. The Component Taxonomy (auto-orchestrate.md, line 79) explicitly distinguishes: "Skill — Reusable capability... Cannot spawn subagents." The Execution Guard prohibits the loop controller from doing analysis/implementation work itself — invoking a domain guide Skill delegates that work to the Skill, consistent with the delegation principle.

---

## Trigger Rules Table

| Trigger ID | Condition | Command | Tier | Applies To | Evaluation Point |
|------------|-----------|---------|------|------------|-----------------|
| TRIG-001 | Stage 0 completes AND stage-receipt `process_acknowledgments` contains P-038 with severity HIGH or CRITICAL, OR `key_findings` mention security threats/vulnerabilities | `/security` | 2 | auto-orchestrate | Step 4.8c |
| TRIG-002 | Stage 3 completes (implementation done, test strategy needed) | `/qa` | 2 | auto-orchestrate | Step 4.8c |
| TRIG-003 | Stage 5 fails AND validator stage-receipt `failure_type` or `key_findings` contain "deploy", "docker", "infrastructure", "environment", or "platform" | `/infra` | 2 | auto-orchestrate | Step 4.8c |
| TRIG-004 | Session starts AND no `handoff-receipt.json` found in `.orchestrate/<session-id>/` | `/new-project` | 1 | auto-orchestrate | Step 0g |
| TRIG-005 | Stage 6 completes AND `checkpoint.release_flag == true` | `/release-prep` | 1 | auto-orchestrate | Step 5 (post-termination) |
| TRIG-006 | Terminal state is `completed` AND a dispatch receipt for `/release-prep` exists (TRIG-005 was previously suggested and user ran it) | `/post-launch` | 1 | auto-orchestrate | Step 5 (post-termination) |
| TRIG-007 | Any stage completes AND `.pipeline-state/codebase-analysis.jsonl` contains entries with `severity: "critical"`, OR planning artifact (P2 Scope Contract section 6) has RAID items with severity CRITICAL | `/risk` | 2 | auto-orchestrate, auto-audit | Step 4.8c / Step 4.5a |
| TRIG-008 | Planning stage P4 completes (Sprint Readiness gate PASSED) | `/sprint-ceremony` | 1 | auto-orchestrate | Step 0h (planning loop) |
| TRIG-009 | Audit gap-report contains gaps for processes P-038 through P-043 with severity CRITICAL or HIGH | `/security` | 2 | auto-audit | Step 4.5a |
| TRIG-010 | Audit gap-report contains gaps for processes P-032 through P-037 with severity CRITICAL or HIGH | `/qa` | 2 | auto-audit | Step 4.5a |
| TRIG-011 | Debugger returns `Category` of "docker", "infrastructure", "deploy", or "platform" | `/infra` | 2 | auto-debug | Step 4.2b |
| TRIG-012 | Any stage produces a process acknowledgment or finding flagged HIGH or CRITICAL that maps to a domain guide's process range | Corresponding domain guide (see Domain Guide Process Ranges) | 2 | all three | Stage transition |
| TRIG-013 | Stage N completes AND `process_scope.tier >= medium` AND expanded injection map has processes for Stage N that are (a) not natively handled by the stage agent, (b) not already dispatched by TRIG-001-012, and (c) have a `domain_guide` field pointing to a Tier 2 command | Corresponding domain guide per injection map `domain_guide` field | 2 | auto-orchestrate | Step 4.8c (after TRIG-001-012) |
| PHASE-TRIG-001 | Planning gate P{N} passes (any of P1-P4) | `/gate-review` | 1 | auto-orchestrate | Step 0h (after each gate pass) |
| PHASE-TRIG-002 | Stage 3 completes AND `tshirt_size` IN [L, XL] AND P4 Sprint Kickoff Brief artifact exists (multi-sprint project) | `/active-dev` | 1 | auto-orchestrate | Step 4.8c |
| PHASE-TRIG-003 | Iteration count reaches sprint boundary interval AND `tshirt_size` IN [L, XL]. Interval: L = every 5 iterations, XL = every 3 iterations | `/sprint-ceremony` | 1 | auto-orchestrate | Step 4.8c |
| TRIG-ORG-001 | Stage 4.5 completes AND codebase-stats report shows `tech_debt_score > 30%` OR `duplication_ratio > 0.15` | `/org-ops` | 2 | auto-orchestrate, auto-audit | Step 4.8c / Step 4.5a |

### Domain Guide Process Ranges (for TRIG-012, TRIG-013, and TRIG-ORG-001)

| Domain Guide | Process Range | Skill Name |
|-------------|---------------|------------|
| `/security` | P-038 to P-043 | `security` |
| `/qa` | P-032 to P-037 | `qa` |
| `/infra` | P-044 to P-048 | `infra` |
| `/data-ml-ops` | P-049 to P-053 | `data-ml-ops` |
| `/risk` | P-074 to P-077 | `risk` |
| `/org-ops` | P-062 to P-069 | `org-ops` |

---

## Proactive Process Sweep (PROCESS-DELEGATE-001)

TRIG-013 implements proactive process delegation. Unlike TRIG-001-012 which fire reactively when specific conditions are met, TRIG-013 proactively consults the expanded process injection map to ensure all scope-applicable processes with domain guide coverage are engaged.

**Why this is needed**: TRIG-012 fires only when a process is flagged HIGH or CRITICAL. Many processes should be engaged proactively based on the task's scope classification, even when no severity flag exists. For example, if a COMPLEX task with the `infra` domain flag reaches Stage 2, the `/infra` domain guide should be consulted for P-044 (Golden Path) and P-046 (Environment Self-Service) regardless of whether those processes were flagged.

**Constraint**: TRIG-013 caps at 2 proactive dispatches per stage transition. If more than 2 domain guides qualify, prioritize by: (1) number of applicable processes, (2) alphabetical order.

```
FUNCTION proactive_process_sweep(completed_stage, process_scope, already_dispatched):

  INPUT:
    completed_stage:     numeric stage just completed
    process_scope:       checkpoint.triage.process_scope object
    already_dispatched:  set of domain guide skill names already dispatched by TRIG-001-012

  IF process_scope.tier == "trivial":
    RETURN []  # No proactive sweep for trivial tasks

  # Step 1: Get all injection hooks for the completed stage
  stage_hooks = injection_map.get_hooks_for_stage(completed_stage)

  # Step 2: Filter to hooks that are active given the process scope
  active_hooks = [h for h in stage_hooks
                  if hook_is_active(h, process_scope)
                  AND h.domain_guide is not null
                  AND h.domain_guide NOT IN already_dispatched]

  # Step 3: Group by domain guide
  by_guide = group_by(active_hooks, key=lambda h: h.domain_guide)

  # Step 4: Build dispatch candidates
  candidates = []
  FOR EACH (guide, hooks) IN by_guide:
    IF guide_is_tier_2(guide):  # Only auto-invoke Tier 2 guides
      candidates.append({
        guide: guide,
        processes: [h.process_ids for h in hooks],
        process_count: sum(len(h.process_ids) for h in hooks)
      })

  # Step 5: Sort by process count (descending), cap at 2
  candidates.sort(key=lambda c: (-c.process_count, c.guide))
  candidates = candidates[:2]  # TRIG-013 cap

  # Step 6: Dispatch
  dispatches = []
  FOR EACH candidate IN candidates:
    write_dispatch_context(
      trigger_id=f"TRIG-013-{completed_stage}-{candidate.guide}",
      processes=candidate.processes,
      scope=f"Proactive process coverage for Stage {completed_stage}: {candidate.processes}"
    )
    result = Skill(skill: guide_to_skill(candidate.guide))
    receipt = create_dispatch_receipt(result, trigger_id="TRIG-013")
    dispatches.append(receipt)

    display f"[DISPATCH-INVOKE] TRIG-013: Proactive sweep invoked {candidate.guide} for {len(candidate.processes)} processes"

  RETURN dispatches
```

---

## Evaluation Function

The dispatch evaluation runs at designated hook points in each of the Big Three commands. It is NOT a separate tool or agent — it is inline logic the loop controller executes.

```
FUNCTION evaluate_dispatch_triggers(event_context):

  INPUT:
    event_type:     "stage_completed" | "stage_failed" | "session_start" |
                    "session_end" | "audit_complete" | "debug_result"
    stage:          numeric stage (0-6) or planning stage ("P1"-"P4")
    stage_receipt:  parsed stage-receipt.json (if available)
    checkpoint:     current session checkpoint
    gap_report:     parsed gap-report.json (auto-audit only, null otherwise)
    debugger_done:  parsed debugger DONE block (auto-debug only, null otherwise)

  triggers_fired = []
  current_command = checkpoint.command  # "auto-orchestrate" | "auto-audit" | "auto-debug"

  FOR EACH rule IN TRIGGER_RULES_TABLE:
    IF rule.applies_to does NOT include current_command:
      SKIP

    condition_met = evaluate_condition(rule, event_context)

    IF condition_met:
      IF rule.tier == 1:
        # Display-only suggestion (R-010 preserved)
        display "[DISPATCH-SUGGEST] {rule.trigger_id}: Consider running {rule.command}."
        display "  Reason: {rule.condition_summary}"
        append to checkpoint.dispatch_log:
          { trigger_id, command, tier: 1, action: "suggested", timestamp }

      ELSE IF rule.tier == 2:
        # Auto-invoke via Skill tool
        display "[DISPATCH-INVOKE] {rule.trigger_id}: Invoking {rule.command} for domain analysis"

        # Write dispatch context file for the Skill to read
        write dispatch_context to session dispatch-receipts/ directory:
          { trigger_id, source_session, stage, condition_summary, pipeline_context }

        # Invoke the domain guide Skill
        result = Skill(skill: rule.skill_name)

        # Create dispatch receipt from result
        receipt = {
          schema_version: "1.0.0",
          dispatch_id: "dispatch-{YYYYMMDD}-{trigger_id}-{4hex}",
          trigger_id: rule.trigger_id,
          command: rule.command,
          invocation_tier: 2,
          invoked_by: current_command,
          source_session: checkpoint.session_id,
          trigger_context: {
            event_type: event_context.event_type,
            stage: event_context.stage,
            condition_summary: describe_condition(rule, event_context)
          },
          result: parse_skill_output(result),
          artifacts: extract_artifact_paths(result),
          next_action: determine_next_action(rule, result),
          created_at: now_iso8601(),
          consumed: false,
          consumed_at: null
        }

        write receipt to .{session_dir}/dispatch-receipts/{dispatch_id}.json
        append receipt to triggers_fired

        display "[DISPATCH-COMPLETE] {rule.trigger_id}: {rule.command} analysis complete. Receipt written."
        append to checkpoint.dispatch_log:
          { trigger_id, command, tier: 2, action: "invoked", dispatch_id, timestamp }

  RETURN triggers_fired
```

### Next Action Processing

After `evaluate_dispatch_triggers` returns, the loop controller processes `next_action` for each receipt:

| `next_action.type` | Behavior |
|---------------------|----------|
| `inject_into_stage` | Append receipt summary to `checkpoint.dispatch_context.<target_stage>`. When the orchestrator is spawned for that stage, include dispatch context in the spawn prompt (see Appendix C integration). |
| `create_task` | Create a new task via `TaskCreate` with `dispatch_hint` from the receipt. Set `blockedBy` appropriately for the target stage. |
| `gate_block` | Set `checkpoint.dispatch_gates.<stage> = dispatch_id`. The stage cannot proceed until the gate condition is cleared (finding addressed). |
| `informational` | Log receipt to `dispatch_log` only. No pipeline impact. |
| `suggest_manual` | Display suggestion for user action. Used by Tier 1 triggers. |

---

## Dispatch Receipt Schema (DISPATCH-003)

```json
{
  "schema_version": "1.0.0",
  "dispatch_id": "dispatch-20260414-TRIG-001-a3f2",
  "trigger_id": "TRIG-001",
  "command": "/security",
  "skill_name": "security",
  "invocation_tier": 2,
  "invoked_by": "auto-orchestrate",
  "source_session": "auto-orc-20260414-myapp",
  "trigger_context": {
    "event_type": "stage_completed",
    "stage": 0,
    "condition_summary": "P-038 flagged HIGH in stage-0 receipt: threat model identified SQL injection risk"
  },
  "result": {
    "status": "completed",
    "findings_count": 3,
    "severity_max": "HIGH",
    "summary": "Threat model identified 3 risks: SQL injection in /api/users endpoint, missing CORS policy on API gateway, weak session token generation using Math.random()"
  },
  "artifacts": [
    ".orchestrate/auto-orc-20260414-myapp/dispatch-receipts/TRIG-001-security-findings.md"
  ],
  "next_action": {
    "type": "inject_into_stage",
    "target_stage": 2,
    "instruction": "Specification MUST address: (1) parameterized queries for /api/users, (2) CORS policy definition, (3) cryptographically secure session tokens"
  },
  "created_at": "2026-04-14T10:30:00Z",
  "consumed": false,
  "consumed_at": null
}
```

### Receipt Lifecycle

1. **Created**: Dispatch evaluation writes receipt with `consumed: false`
2. **Injected**: Loop controller processes `next_action`, injects context into checkpoint
3. **Consumed**: When the target stage completes successfully addressing the findings, mark `consumed: true` and set `consumed_at` timestamp
4. **Unconsumed receipts**: At session termination, any unconsumed receipts are listed in `dispatch_summary` as unresolved findings

---

## Dispatch Mode Protocol for Domain Guides

When a domain guide is invoked via the Command Dispatcher (Tier 2), it operates in **dispatch mode** rather than interactive mode. The invoking loop controller passes context by writing a dispatch context file before invoking the Skill.

### Dispatch Context File

Written by the loop controller to `.{session_dir}/dispatch-receipts/dispatch-context-{trigger_id}.json` before `Skill()` invocation:

```json
{
  "dispatch_mode": true,
  "trigger_id": "TRIG-001",
  "source_command": "auto-orchestrate",
  "source_session": "auto-orc-20260414-myapp",
  "stage": 0,
  "event_type": "stage_completed",
  "condition_summary": "P-038 flagged HIGH in stage-0 receipt",
  "relevant_artifacts": [
    ".orchestrate/auto-orc-20260414-myapp/stage-0/2026-04-14_research.md"
  ],
  "scope": "Analyze security findings from Stage 0 research and produce actionable recommendations for Stage 2 specification"
}
```

### Dispatch Mode Behavior

When a domain guide detects dispatch mode (dispatch context file present):

1. **Skip interactive guidance** — Do not present process menus or ask for user selection
2. **Read dispatch context** — Parse the dispatch context file for scope and relevant artifacts
3. **Focused analysis** — Analyze only the processes relevant to the trigger condition
4. **Structured output** — Produce findings as structured text that the loop controller can parse:

```
## Dispatch Findings

**Trigger**: TRIG-001 (P-038 Security)
**Severity**: HIGH
**Findings Count**: 3

### Finding 1: SQL Injection Risk
- **Process**: P-038 (Threat Modeling)
- **Severity**: HIGH
- **Location**: /api/users endpoint
- **Recommendation**: Use parameterized queries; add input validation layer
- **Stage Impact**: Stage 2 (spec must include security requirements)

### Finding 2: Missing CORS Policy
...

## Recommended Next Action
- **Type**: inject_into_stage
- **Target Stage**: 2
- **Instruction**: Specification MUST address the 3 findings above
```

5. **Return to loop controller** — The Skill completes and returns. The loop controller parses the output and creates the dispatch receipt.

---

## Checkpoint Schema Additions

All three commands add these fields to their checkpoint schema. All fields have safe defaults for backward compatibility with existing sessions.

```json
{
  "dispatch_log": [],
  "dispatch_context": {
    "0": [], "1": [], "2": [], "3": [], "4": [], "4.5": [], "5": [], "6": []
  },
  "dispatch_gates": {},
  "dispatch_summary": null,
  "release_flag": false
}
```

### Field Definitions

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `dispatch_log` | array | `[]` | Append-only log of all dispatch evaluations. Each entry: `{ trigger_id, command, tier, action, dispatch_id?, timestamp }` |
| `dispatch_context` | object | `{}` (empty per stage) | Per-stage array of dispatch receipt summaries to include in orchestrator spawn prompts. Keyed by stage number. |
| `dispatch_gates` | object | `{}` | Active dispatch gates blocking stage advancement. Keyed by stage number, value is `dispatch_id`. Cleared when finding is addressed. |
| `dispatch_summary` | object/null | `null` | Written at termination. Contains: `{ total_dispatches, receipts_consumed, receipts_unconsumed, suggestions_made }` |
| `release_flag` | boolean | `false` | Set to `true` when task description contains release/deploy keywords or user passes `--release` flag. Triggers TRIG-005 at termination. |

---

## Session Directory Addition

Each command's session directory gains a `dispatch-receipts/` subdirectory:

```
.orchestrate/<session-id>/dispatch-receipts/
.audit/<session-id>/dispatch-receipts/
.debug/<session-id>/dispatch-receipts/
```

Contents:
- `dispatch-context-TRIG-NNN.json` — Context file written before Skill invocation
- `dispatch-YYYYMMDD-TRIG-NNN-XXXX.json` — Dispatch receipt written after Skill returns
- `TRIG-NNN-<domain>-findings.md` — Artifact files produced by domain guide analysis

---

## Integration Reference

### auto-orchestrate Integration Points

| Step | Hook | Triggers Evaluated |
|------|------|--------------------|
| Step 0g | Pre-session dispatch check | TRIG-004 (no handoff → suggest /new-project) |
| Step 0h | Planning loop (per gate) | PHASE-TRIG-001 (gate passes → suggest /gate-review) |
| Step 0h | Planning loop (all gates) | TRIG-008 (P4 complete → suggest /sprint-ceremony) |
| Step 4.8c | Post-stage dispatch evaluation | TRIG-001, TRIG-002, TRIG-003, TRIG-007, TRIG-012, TRIG-013, TRIG-ORG-001, PHASE-TRIG-002, PHASE-TRIG-003 |
| Step 4.8e | Workflow state synchronization | WORKFLOW-SYNC-001 (task-board.json + focus-stack.json write) |
| Step 5 | Post-termination dispatch | TRIG-005 (release-prep), TRIG-006 (post-launch) |
| Appendix C | Spawn prompt injection | Include `dispatch_context.<current_stage>` in orchestrator prompt |

### auto-audit Integration Points

| Step | Hook | Triggers Evaluated |
|------|------|--------------------|
| Step 4.5a | Post-audit dispatch evaluation | TRIG-007, TRIG-009, TRIG-010, TRIG-012, TRIG-ORG-001 |

### auto-debug Integration Points

| Step | Hook | Triggers Evaluated |
|------|------|--------------------|
| Step 4.2b | Post-debug dispatch evaluation | TRIG-011, TRIG-012 |

---

## Relationship to Existing Protocols

### Process Injection Map (`process_injection_map.md`)

The Command Dispatcher complements the Process Injection Map. The injection map defines which organizational processes apply at each stage and whether they are advisory or enforced. The Command Dispatcher goes further: when a process is flagged, it invokes the corresponding domain guide for expert analysis and injects findings back into the pipeline.

| Concern | Process Injection Map | Command Dispatcher |
|---------|----------------------|--------------------|
| Scope | Maps processes to stages | Invokes domain guides when processes flag issues |
| Mechanism | Hook format (notify/gate/link) | Skill invocation with receipt |
| Output | Process acknowledgment in stage-receipt | Dispatch receipt with next_action |
| Enforcement | Per-hook `enforced` flag | Per-trigger tier (suggest vs auto-invoke) |

### Cross-Pipeline State (`cross-pipeline-state.md`)

Dispatch receipts are session-local (stored in `.{session_dir}/dispatch-receipts/`). However, dispatch findings that produce `codebase-analysis` entries are written to `.pipeline-state/codebase-analysis.jsonl` per the existing cross-pipeline protocol, making them available to future sessions.

### Escalation Protocol

The Command Dispatcher handles domain guide invocations (horizontal expertise). Escalation handles command-to-command transitions (vertical lifecycle). They are complementary:
- **Dispatch**: auto-orchestrate invokes `/security` for Stage 0 threat analysis → findings injected into Stage 2
- **Escalation**: auto-debug escalates to auto-orchestrate when error is architectural → new orchestration session
