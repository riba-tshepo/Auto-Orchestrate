# Internal Phase Invocation Protocol

**Version**: 2.0
**Date**: 2026-04-25
**Status**: Active

---

## Purpose

`/auto-orchestrate` is the single user-facing command in this framework. It walks through the canonical end-to-end process (P-001 through P-093) as a sequence of internal phases. This protocol defines how the loop controller invokes its own internal phases — there are no sibling commands to dispatch to.

The previous version of this protocol (1.0, "Command Dispatch Protocol") mediated between three separate autonomous loops (`/auto-orchestrate`, `/auto-audit`, `/auto-debug`) and several lifecycle/domain commands. Those commands have been merged into `/auto-orchestrate` as internal phases. This protocol is the renamed, simplified successor.

---

## Constraints

| ID | Rule |
|----|------|
| PHASE-LOOP-001 | **Internal phase transitions only** — All phases (planning gates, domain phases, audit, debug, release, post-launch, governance) run inline within `/auto-orchestrate`. No `Skill()` invocation to a separate command; no `Agent()` spawn outside the AUTO-001 phase mapping. |
| PHASE-LOOP-002 | **Phase receipt protocol** — Each internal phase MUST write a phase receipt to `.orchestrate/<session>/phase-receipts/phase-{name}-{YYYYMMDD}-{HHMMSS}.json` with: `phase`, `started_at`, `completed_at`, `verdict`, `artifacts`, `next_phase`. The auto-orchestrate loop controller consumes these receipts the same way the previous protocol consumed dispatch receipts. |
| PHASE-LOOP-003 | **Phase agents do not transition** — Domain phase agents (qa-engineer, security-engineer, infra-engineer, data-engineer, ml-engineer, sre, auditor, debugger, etc.) read their phase context, produce findings, and return. The loop controller decides the next phase. Phase agents MUST NOT spawn other phase agents themselves. |
| PHASE-LOOP-004 | **Auto-evaluation + file-polled human gates at 8 boundaries** — All gate verdicts are first auto-evaluated (deterministic checklists + agent-evaluator verdict) to produce a `recommended_verdict`. The loop controller then writes `gate-pending-{gate_id}.json` and polls `gate-approval-{gate_id}.json` every `gate_poll_interval_seconds` for the user's final decision. Gates: (1) Intent Review, (2) Scope Lock, (3) Dependency Acceptance, (4) Sprint Readiness, (5) Stage 5 → Phase 5e Debug Entry, (6) Phase 5v Compliance Verdict, (7) CAB Review (Phase 7 prelude, when release_flag AND HIGH-risk), (8) Phase 7 Release Readiness. (See HUMAN-GATE-001 in `commands/auto-orchestrate.md`.) |
| HANDOVER-001 | **Explicit handover receipt at every agent boundary** — When agent A finishes work that agent B will consume (next-phase lead, same-phase co-agent peer, or downstream stage agent), A MUST write a handover receipt to `.orchestrate/<session>/handovers/handover-{from_agent}-to-{to_agent}-{YYYYMMDD}-{HHMMSS}.json` per the Handover Receipt schema below. The orchestrator passes the receipt path in B's spawn prompt. |
| HANDOVER-002 | **Acknowledgment on consumption** — When agent B begins work that consumes a handover receipt, B MUST write an acknowledgment receipt to the same `handovers/` directory per the Acknowledgment Schema below. The ack records what B received and any clarification questions. |
| HANDOVER-003 | **Clarification feedback loop with cap** — If B sets `request_clarification: true` in its ack, the orchestrator re-spawns A with B's questions. A produces a Clarification Response receipt; B reads it before proceeding. **Cap: 2 clarification rounds per handover.** After round 2, the orchestrator logs `[HANDOVER-WARN] Max clarification rounds reached for {handover_id}` and B proceeds with available information. |
| MEETING-001 | **Meeting handler types** — Every canonical meeting maps to one of three handlers: (a) **Human-Gated** (HUMAN-GATE-001 file-polled gate), (b) **Multi-Agent Sync** (parallel co-agent spawns + facilitator synthesis + meeting receipt; autonomous, no pause), (c) **Async Single-Agent** (one agent produces meeting outcome doc). See Meeting Catalog section. |
| MEETING-002 | **Meeting receipt protocol** — Multi-Agent Sync and Async Single-Agent meetings MUST write a meeting receipt to `.orchestrate/<session>/meetings/meeting-{meeting_id}-{YYYYMMDD}-{HHMMSS}.json` per the Meeting Receipt Schema below. Human-Gated meetings produce a gate-state.json entry (the existing gate protocol covers them). |
| AUTO-001 | **Phase-determined agent gateway** — See `commands/auto-orchestrate.md` Core Constraints. The loop controller spawns the agent type appropriate for the active phase. |
| SKILL-FRONTMATTER-001 | **Frontmatter-only routing for skill discovery** — When `checkpoint.optimizations.skill_frontmatter_routing == true` (default for new sessions), skill **discovery** loads only the YAML frontmatter from each candidate `SKILL.md` (~300 tok per skill) using `layer1.read_frontmatter` or `layer1.list_skills_with_triggers`. The full SKILL.md body is loaded ONLY at the moment the skill is invoked. Frontmatter is authoritative for routing — `name`, `description`, and `triggers` fields suffice for trigger matching. Behavioral equivalence: routing decisions MUST be identical to verbose mode; if a skill is selected via frontmatter and the body proves unloadable, fail loudly with `[SKILL-FRONTMATTER-001 FAIL] body unloadable for "<skill>" — falling back to verbose discovery`. Token saving: ~80% per skill considered. Audit log: `[OPT-3] Loaded N skill frontmatters (≈M tok); body load on invoke only`. |
| MANIFEST-DIGEST-001 | **Slim manifest digest for non-orchestrator spawns** — When `checkpoint.optimizations.manifest_digest == true` (default for new sessions), the spawn-prompt builder MUST inject a slim digest of `manifest.json` (~2.6k tok) instead of the full manifest (~19k tok) for any subagent that does not require chaining metadata or activation rules. The digest contains agent names + dispatch_triggers + skill names + triggers — sufficient for routing. The full manifest is injected for: (a) `agent_name == "orchestrator"`, (b) `agent_name == "session-manager"` (boot-time validation), (c) tasks with `needs_full_manifest: true`. Use `layer1.build_digest` and `layer1.needs_full_manifest`. If a subagent fails for lack of manifest fields, log `[MANIFEST-DIGEST-001 FAIL] subagent "<agent>" needs full manifest — re-spawning with full` and re-spawn once with `needs_full_manifest: true`. Token saving: ~17k tokens per non-orchestrator spawn (~86% compression). |
| TEMPLATE-EXTRACT-001 | **Per-stage orchestrator template extraction** — When `checkpoint.optimizations.per_stage_templates == true` (default for new sessions), the spawn-prompt builder MUST inject only the orchestrator CORE (~8k tok: constraints + boot + execution loop + skill selection + error recovery) plus the active stage / phase / meeting template (~300-2k tok), instead of the full ~33k `agents/orchestrator.md`. Use `layer1.build_spawn_prompt_body(orchestrator_md_path, stage=<n>|phase=<id>|meeting_kind=<kind>, enabled=True)`. The single source-of-truth file (`orchestrator.md`) is preserved; sections are carved at runtime. Safe fallback: if the requested template section can't be found, the helper returns the full file (behaviorally identical to flag-off). Token saving: ~25k tokens per orchestrator spawn (~75% compression). |
| STAGE-RECEIPT-DIET-001 | **Slim stage-receipt schema (v2.0.0)** — When `checkpoint.optimizations.stage_receipt_diet == true` (default for fresh installs), stage producers write the slim v2.0.0 format defined in `_shared/protocols/output-standard.md` §4.1: only `session_id`, `stage`, `agent`, `status`, `completed_at`, `key_findings`, `artifacts`, and `errors`. Consumer agents (Phase 5e debugger, Phase 5v auditor, internal phase trigger evaluator) MUST be tolerant — read both v1 and v2 shapes per §4.3. If a consumer needs a dropped field, it sets `needs_full_receipt: true` on its spawn and the producer re-emits a v1 receipt. Token saving: ~40k tokens per session (smaller per-receipt cost × multiple reads × ~8 receipts). |
| HANDOVER-COMPRESS-001 | **Slim handover schema (v2.0.0)** — When `checkpoint.optimizations.handover_compress == true` (default for fresh installs), `from_agent` writes the slim v2.0.0 handover-receipt format (this protocol §"Slim v2.0.0"): drops `context_carry`, `confidence`, and `consumed`/`consumed_at`. Consumers MUST read both v1 and v2 shapes via the tolerant reader pattern; the reader re-derives `context_carry` from `checkpoint` when callers expect v1 keys. If a consumer determines it needs a dropped field, the orchestrator re-spawns the producer with `needs_full_handover: true`. Token saving: ~20k tokens per session. |

---

## Phase Catalog

| Phase ID | Name | Owner Agent(s) | Process Range | Trigger |
|----------|------|----------------|---------------|---------|
| **P1** | Intent Frame | `product-manager` | P-001..P-006 | Session start unless `--skip-planning` or triage classifies trivial/medium |
| **P2** | Scope Contract | `product-manager` | P-007..P-014 | After P1 PASSED |
| **P3** | Dependency Map | `technical-program-manager` | P-015..P-021 | After P2 PASSED |
| **P4** | Sprint Bridge | `engineering-manager` | P-022..P-031 | After P3 PASSED |
| **0..6** | Execution Stages | `researcher`, `product-manager`, `software-engineer`, `test-writer-pytest`, `codebase-stats`, `validator`, `technical-writer` | inline | After all P1-P4 PASSED (or skipped) |
| **5q** | Quality Phase | `qa-engineer` | P-032..P-037 | Stage 3 completes; or P-032..P-037 flagged HIGH/CRITICAL |
| **5s** | Security Phase | `security-engineer` | P-038..P-043 | Stage 0/2/3 receipt mentions security threats; or P-038..P-043 flagged HIGH/CRITICAL |
| **5i** | Infra/SRE Phase | `infra-engineer`, `sre` | P-044..P-048, P-054..P-057 | Stage 5 fails with infra keywords; or scope flags `infra` |
| **5d** | Data/ML Phase | `data-engineer`, `ml-engineer` | P-049..P-053 | Scope flags `data_ml`; or P-049..P-053 flagged HIGH/CRITICAL |
| **5v** | Validation + Audit | `auditor` | — | Stage 5 PASSES but compliance < threshold |
| **5e** | Debug sub-loop | `debugger` | — | Stage 5 FAILS after 3 fix iterations |
| **7** | Release Prep | `orchestrator` (PHASE: RELEASE_PREP), `qa-engineer`, `infra-engineer`, `sre`, `technical-writer`, `technical-program-manager` | P-035, P-044-048, P-059, P-061, P-076 | `release_flag == true` |
| **8** | Post-Launch | `sre`, `product-manager`, `engineering-manager` | P-070..P-073, P-054..P-057 (ongoing) | After Phase 7 OR `triage.mode == "post_launch"` |
| **9** | Continuous Governance | `engineering-manager`, `technical-program-manager`, `staff-principal-engineer`, `product-manager`, `infra-engineer`, `technical-writer` | P-062..P-093 | tech_debt > 30%, duplication > 15%, CRITICAL RAID items, or cadence boundary |

---

## Human-in-the-Loop Gate Protocol

The loop controller pauses for human approval at 7 formal gate boundaries via file-polled async approval. **Each gate writes a pending file and polls for an approval file.** This lets the user approve from any terminal, IDE, or CI tool that can write to the session's `gates/` directory.

### Gate Boundaries (7)

| # | Gate ID | When | Recommended verdict produced by |
|---|---------|------|----------------------------------|
| 1 | `intent-review` | After Phase 1 (Intent Frame) auto-eval | product-manager + engineering-manager evaluator |
| 2 | `scope-lock` | After Phase 2 (Scope Contract) auto-eval | product-manager (with security-engineer for P-012) |
| 3 | `dependency-acceptance` | After Phase 3 (Dependency Map) auto-eval | technical-program-manager (with engineering-manager for P-019) |
| 4 | `sprint-readiness` | After Phase 4 (Sprint Bridge) auto-eval | engineering-manager |
| 5 | `debug-entry` | When Stage 5 fix-loop exhausts (3 iterations), before Phase 5e begins | validator (failure summary) |
| 6 | `compliance-verdict` | After Phase 5v (Audit) compliance score is computed, before remediation | auditor |
| 7 | `release-readiness` | After Phase 7 (Release Prep) artifacts produced, before deployment-affecting actions | orchestrator (PHASE: RELEASE_PREP) |

### gate-pending-{gate_id}.json Schema

Written by the loop controller when a gate is reached. Contains the auto-eval recommended verdict plus context for human decision-making.

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
    "deterministic_criteria": { "...": "per-gate fields" },
    "agent_evaluator": {
      "agent": "product-manager",
      "verdict": "PASS",
      "rationale": "..."
    }
  },
  "artifact_path": ".orchestrate/auto-orc-20260425-myapp/planning/P1-intent-brief.md",
  "summary": "Human-readable summary for the reviewer",
  "blocking_findings": [],
  "approval_options": [
    { "decision": "approved", "effect": "Proceed to next phase" },
    { "decision": "approved_with_edits", "effect": "Proceed using artifact_edit_path from approval file" },
    { "decision": "rejected", "effect": "Re-spawn owner agent with feedback" },
    { "decision": "stop", "effect": "Terminate session with terminal_state: 'gate_rejected'" }
  ],
  "instructions_for_user": "Review the artifact at artifact_path. Then write .orchestrate/<session-id>/gates/gate-approval-<gate_id>.json with your decision."
}
```

### gate-approval-{gate_id}.json Schema

Written by the user (or any tool acting on their behalf). The loop controller polls for this file every `gate_poll_interval_seconds` (default 30).

```json
{
  "schema_version": "1.0.0",
  "gate_id": "intent-review",
  "decision": "approved",
  "decided_at": "2026-04-25T10:42:00Z",
  "decided_by": "<user identifier — free-form: name, email, CI bot, etc.>",
  "feedback": "Optional free-form feedback. Required on 'rejected'. Logged to gate-history on 'approved'.",
  "artifact_edit_path": ".orchestrate/auto-orc-20260425-myapp/planning/P1-intent-brief.md"
}
```

**Required fields**: `gate_id`, `decision`, `decided_at`. All others optional. `decision` MUST be one of: `approved`, `approved_with_edits`, `rejected`, `stop`.

### Gate History

The loop controller appends every gate transition to `.orchestrate/<session>/gates/gate-history.jsonl` for audit. Each line is a JSON object: `{ gate_id, recommended_verdict, decision, decided_by, decided_at, feedback }`. This file is the immutable audit trail for human decisions across the session.

### Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `gate_poll_interval_seconds` | 30 | How often the loop controller checks for the approval file |
| `gate_timeout_seconds` | 86400 (24h) | Max wait per gate before terminating with `terminal_state: "gate_timeout"` |
| `skip_human_gates` | false | If true, recommended verdict is treated as approved automatically. Audit-trail evaluator becomes `"auto-skip"`. |

### Resume Behavior

When the loop controller is interrupted while polling, the session resumes by reading the latest `gate-pending-*.json`. If a matching `gate-approval-*.json` was written during the interruption, it is consumed on resume. Otherwise polling continues from `created_at + (now - last_poll)` and the gate timeout is re-checked.

---

## Meeting Catalog (MEETING-001)

The canonical end-to-end process specifies live ceremonies. The pipeline implements them via three handler types — there is no real-time multi-party meeting; each meeting type is realized through agent spawns + artifact production. The user's autonomy preference (8 human gates only) governs which meetings pause vs run autonomously.

### Three Handler Types

| Type | Mechanism | Pauses pipeline? |
|------|-----------|-------------------|
| **Human-Gated** | `gate-pending-{gate_id}.json` written; loop controller polls for `gate-approval-{gate_id}.json` (HUMAN-GATE-001) | YES — until user approves |
| **Multi-Agent Sync** | Orchestrator spawns facilitator + attendee co-agents in parallel; facilitator synthesizes minutes; meeting receipt written | NO — runs inline |
| **Async Single-Agent** | One agent produces structured meeting outcome doc; meeting receipt written | NO — runs inline |

### Canonical Meeting → Handler Map

| P-XXX | Meeting | Handler | Facilitator | Cadence | PHASE: value |
|-------|---------|---------|-------------|---------|--------------|
| P-004 | Intent Review | Human-Gated | engineering-manager (evaluator) | Per project | n/a (gate `intent-review`) |
| P-013 | Scope Lock | Human-Gated | product-manager (evaluator) | Per project | n/a (gate `scope-lock`) |
| P-019 | Dependency Acceptance | Human-Gated | technical-program-manager (evaluator) | Per project | n/a (gate `dependency-acceptance`) |
| P-025 | Sprint Readiness | Human-Gated | engineering-manager (evaluator) | Per sprint | n/a (gate `sprint-readiness`) |
| (Phase 4) | Sprint Kickoff | Multi-Agent Sync | engineering-manager | Per sprint | `SPRINT_CEREMONY` |
| P-026 | Daily Standup | Multi-Agent Sync | product-manager (Scrum Master) | L = every 5 iters; XL = every 3; else none | `DAILY_STANDUP` |
| P-020 | Dependency Standup | Multi-Agent Sync | technical-program-manager | Same as P-026 + only if `cross_team_impact` non-empty | `DEPENDENCY_STANDUP` |
| P-029 | Backlog Refinement | Async Single-Agent | product-manager | Same as P-026 + only when backlog has unrefined items | `BACKLOG_REFINEMENT` |
| P-027 | Sprint Review | Multi-Agent Sync | engineering-manager (chair) | After Stage 6 | `SPRINT_REVIEW` |
| P-028 | Sprint Retrospective | Multi-Agent Sync | engineering-manager (facilitator) | After Sprint Review | `SPRINT_RETRO` |
| P-076 | Pre-Launch Risk Review (CAB) | Human-Gated | technical-program-manager | Phase 7 prelude when `release_flag` AND HIGH-risk | n/a (gate `cab-review`) |
| P-077 | Quarterly Risk Review | Async Single-Agent | engineering-manager | Phase 9 risk sub-routine | (Phase 9 sub-routine) |
| P-082 | Quarterly Capacity Planning | Hybrid (Async + final gate) | engineering-manager | Phase 9 capacity sub-routine | (Phase 9 sub-routine) |

## Meeting Receipt Schema (MEETING-002)

Multi-Agent Sync and Async Single-Agent meetings write to `.orchestrate/<session>/meetings/meeting-{meeting_id}-{YYYYMMDD}-{HHMMSS}.json`:

```json
{
  "schema_version": "1.0.0",
  "meeting_id": "p-026-daily-standup-iter-15",
  "process_id": "P-026",
  "meeting_type": "daily_standup | dependency_standup | sprint_kickoff | sprint_review | sprint_retro | backlog_refinement | quarterly_risk_review | quarterly_capacity_planning",
  "handler": "multi_agent_sync | async_single_agent",
  "facilitator_agent": "product-manager",
  "attendees": ["product-manager", "engineering-manager", "software-engineer"],
  "started_at": "2026-04-25T10:30:00Z",
  "completed_at": "2026-04-25T10:45:00Z",
  "iteration": 15,
  "inputs_consumed": [
    ".orchestrate/<session>/.../prior-artifact.md"
  ],
  "minutes": {
    "agenda_items": [
      {"item": "Yesterday/Today/Blockers", "discussion": "...", "outcome": "..."}
    ],
    "decisions": ["..."],
    "action_items": [
      {"description": "Resolve env access blocker", "owner_agent": "engineering-manager", "due": "next iteration"}
    ],
    "blockers_surfaced": ["..."],
    "follow_ups": ["..."]
  },
  "triggers_handover_to": ["technical-program-manager"],
  "next_meeting_at_iteration": 20
}
```

For Async Single-Agent meetings, `attendees` is a single-element list and `agenda_items` is replaced with the structured output (e.g., refined backlog table for P-029).

## Agent-to-Agent Handover Protocol (HANDOVER-001/002/003)

Handover between agents within and across phases uses an explicit receipt + acknowledgment + optional clarification protocol mediated by the orchestrator (loop controller). Agents do NOT communicate directly; the orchestrator is the broker.

### Handover Receipt Schema (HANDOVER-001 — written by from_agent)

#### Slim v2.0.0 (PRIMARY — HANDOVER-COMPRESS-001)

When `checkpoint.optimizations.handover_compress == true` (default for fresh installs), producers write the slim format. Consumers MUST read both v1 and v2 (see "Tolerant Consumer Reads" below).

```json
{
  "schema_version": "2.0.0",
  "format": "slim",
  "handover_id": "ho-product-manager-to-technical-program-manager-20260425-104500",
  "from_agent": "product-manager",
  "to_agent": "technical-program-manager",
  "from_phase": "P2",
  "to_phase": "P3",
  "produced_at": "2026-04-25T10:45:00Z",
  "primary_artifact": ".orchestrate/<session>/planning/P2-scope-contract.md",
  "supplementary_artifacts": [
    ".orchestrate/<session>/planning/P2-appsec-scope-review.md",
    ".orchestrate/<session>/planning/P2-dod-review.md"
  ],
  "key_decisions": [
    "Scope is bounded to backend services only; frontend deferred to next quarter"
  ],
  "open_questions": [
    "Should P-076 CAB review fire for the database migration?"
  ],
  "blockers": []
}
```

**Dropped from v1** (re-derivable from checkpoint):
- `context_carry` — `session_id` is in the handover_id; `scope`, `active_processes`, `active_phases` are all on `checkpoint.scope` and `checkpoint.phase_transitions`
- `confidence` — subjective and rarely consumed; if a consumer needs it, set `needs_full_handover: true`
- `consumed` / `consumed_at` — tracked separately by the orchestrator's handover registry, not in the receipt itself

Token saving: ~150 tok per handover × ~10 handovers per session × ~2 reads each ≈ ~3k *direct* + ~17k indirect (handover blobs are pasted into multiple downstream spawn prompts as "prior decisions" context). Total realized saving (per the plan) ≈ 20k tokens.

#### Verbose v1.0.0 (LEGACY / FALLBACK)

Produced when the flag is `false`. Consumers MUST be tolerant of this shape:

```json
{
  "schema_version": "1.0.0",
  "handover_id": "ho-product-manager-to-technical-program-manager-20260425-104500",
  "from_agent": "product-manager",
  "to_agent": "technical-program-manager",
  "from_phase": "P2",
  "to_phase": "P3",
  "produced_at": "2026-04-25T10:45:00Z",
  "primary_artifact": ".orchestrate/<session>/planning/P2-scope-contract.md",
  "supplementary_artifacts": [
    ".orchestrate/<session>/planning/P2-appsec-scope-review.md",
    ".orchestrate/<session>/planning/P2-dod-review.md"
  ],
  "key_decisions": [
    "Scope is bounded to backend services only; frontend deferred to next quarter"
  ],
  "open_questions": [
    "Should P-076 CAB review fire for the database migration?"
  ],
  "blockers": [],
  "context_carry": {
    "session_id": "auto-orc-20260425-myapp",
    "scope": "backend",
    "active_processes": ["P-007", "P-008", "P-013"],
    "active_phases": ["5s", "5q"]
  },
  "confidence": "high",
  "consumed": false,
  "consumed_at": null
}
```

#### Tolerant Consumer Reads

Every consumer of `handover-*.json` MUST handle both shapes:

```python
def read_handover(path: str, checkpoint: dict) -> dict:
    raw = json.load(open(path))
    sv = raw.get("schema_version", "1.0.0")
    if sv.startswith("2.") or raw.get("format") == "slim":
        # Re-derive context_carry from checkpoint when v1 callers expect it
        raw.setdefault("context_carry", {
            "session_id": checkpoint["session_id"],
            "scope": checkpoint.get("scope", {}).get("resolved", "custom"),
            "active_processes": checkpoint.get("triage", {})
                                        .get("process_scope", {})
                                        .get("applicable_processes", []),
            "active_phases": [t["to_phase"] for t in checkpoint.get("phase_transitions", [])],
        })
        raw.setdefault("confidence", None)
        raw.setdefault("consumed", False)
        raw.setdefault("consumed_at", None)
    return raw
```

**Re-fattening insurance**: If a downstream consumer determines it needs a dropped field, the orchestrator re-spawns the producer with `needs_full_handover: true` and logs `[HANDOVER-COMPRESS-001 FALLBACK]`.

### Acknowledgment Schema (HANDOVER-002 — written by to_agent on spawn)

```json
{
  "schema_version": "1.0.0",
  "ack_for": "ho-product-manager-to-technical-program-manager-20260425-104500",
  "received_at": "2026-04-25T10:46:00Z",
  "acknowledged_by": "technical-program-manager",
  "questions_for_handoff": [
    "Open question 1 from your handover: 'Should P-076 fire?' — yes/no/conditional?"
  ],
  "request_clarification": false,
  "proceed_anyway": true
}
```

### Clarification Response Schema (HANDOVER-003 — written by from_agent on re-spawn)

```json
{
  "schema_version": "1.0.0",
  "clarification_for": "ho-product-manager-to-technical-program-manager-20260425-104500",
  "responder_agent": "product-manager",
  "responded_at": "2026-04-25T10:48:00Z",
  "responses": [
    {"question": "Should P-076 CAB fire for the database migration?", "answer": "Yes — schema migration is HIGH-risk per P-050"}
  ],
  "updated_artifacts": [".orchestrate/<session>/planning/P2-scope-contract.md"],
  "round": 1
}
```

### Handover Flow

```
Agent A finishes work
     │
     ▼
A writes handover-receipt.json → handovers/
     │
     ▼
Orchestrator spawns Agent B with handover receipt path in spawn prompt
     │
     ▼
B reads handover receipt, writes acknowledgment.json → handovers/
     │
     ├── request_clarification == false → B proceeds with its work
     │
     └── request_clarification == true (round ≤ 2)
              │
              ▼
        Orchestrator re-spawns A with B's questions
              │
              ▼
        A writes clarification-response.json → handovers/
              │
              ▼
        Orchestrator re-spawns B with response (re-ack); B writes new ack
              │
              ├── still has questions AND round < 2 → loop
              │
              └── round == 2 OR no further questions → B proceeds
                  (orchestrator logs [HANDOVER-WARN] if round 2 still has questions)
```

### Handover Mediator

The orchestrator (loop controller) is the only entity that:
- Spawns from_agent (creates the handover prerequisite)
- Spawns to_agent with handover receipt path
- Re-spawns from_agent on clarification request
- Counts clarification rounds and applies the cap

Phase agents and stage agents do NOT spawn each other for handovers.

## Phase Receipt Schema

```json
{
  "schema_version": "1.0.0",
  "phase_id": "5s",
  "phase_name": "Security",
  "session_id": "auto-orc-20260425-myapp",
  "trigger_context": {
    "trigger_type": "process_flagged",
    "stage": 0,
    "condition_summary": "P-038 flagged HIGH in stage-0 receipt: threat model identified SQL injection risk"
  },
  "agent": "security-engineer",
  "started_at": "2026-04-25T10:30:00Z",
  "completed_at": "2026-04-25T10:34:12Z",
  "verdict": {
    "status": "completed",
    "findings_count": 3,
    "severity_max": "HIGH",
    "summary": "Threat model identified 3 risks: SQL injection in /api/users endpoint, missing CORS policy, weak session token generation"
  },
  "artifacts": [
    ".orchestrate/auto-orc-20260425-myapp/phase-receipts/phase-5s-security-findings.md"
  ],
  "next_action": {
    "type": "inject_into_stage",
    "target_stage": 2,
    "instruction": "Specification MUST address: (1) parameterized queries for /api/users, (2) CORS policy definition, (3) cryptographically secure session tokens"
  },
  "consumed": false,
  "consumed_at": null
}
```

### Receipt Lifecycle

1. **Created**: Loop controller writes receipt with `consumed: false` after the phase agent returns.
2. **Injected**: Loop controller processes `next_action`, injects context into `checkpoint.phase_findings.<target_stage>`.
3. **Consumed**: When the target stage completes successfully addressing the findings, mark `consumed: true` and set `consumed_at`.
4. **Unconsumed receipts**: At session termination, any unconsumed receipts are listed in `phase_summary` as unresolved findings.

---

## Phase Context File

Before invoking a phase agent, the loop controller writes `.orchestrate/<session>/phase-receipts/phase-context-{phase_id}.json`:

```json
{
  "phase_id": "5s",
  "trigger_id": "Stage 0 P-038 HIGH",
  "source_phase": "Stage 0",
  "session_id": "auto-orc-20260425-myapp",
  "stage": 0,
  "condition_summary": "P-038 flagged HIGH in stage-0 receipt",
  "relevant_artifacts": [
    ".orchestrate/auto-orc-20260425-myapp/stage-0/2026-04-25_research.md"
  ],
  "scope": "Analyze security findings from Stage 0 research and produce actionable recommendations for Stage 2 specification"
}
```

---

## Trigger Phrase Conflict Resolution (TRIGGER-TIE-001)

The phrase-based agent routing logic preserved from the prior protocol. Used when scope/dispatch_hint resolution faces ambiguity.

### General rule (TRIGGER-TIE-001a) — Agent wins over its own skills

When a phrase matches **both an agent and a skill**, and the agent invokes that skill internally (i.e., the skill appears in the agent's `skills_orchestrated` list, the agent's prompt references the skill, or the skill's `chaining.consumes_from` lists the agent), **route to the agent**. The agent will invoke the skill itself.

Worked examples:

| Phrase | Agent | Skill | Resolution |
|--------|-------|-------|------------|
| `code review`, `production code`, `write code`, `implement feature` | `software-engineer` | `production-code-workflow` | route to `software-engineer` |
| `test coverage` | `qa-engineer` | `test-writer-pytest` | route to `qa-engineer` |
| `error triage` | `debugger` | `debug-diagnostics` | route to `debugger` |
| `security audit` | `security-engineer` | `security-auditor` | route to `security-engineer` |
| `schema migration` | `data-engineer` | `schema-migrator` | route to `data-engineer` |
| `acceptance criteria` | `product-manager` | `spec-analyzer` | route to `product-manager` |
| `OpenTelemetry` | `sre` | `observability-setup` | route to `sre` |
| `FinOps` | `infra-engineer` | `cost-estimator` | route to `infra-engineer` |
| `audit`, `gap analysis` | `auditor` | `validator` / `spec-compliance` | route to `auditor` |
| `research`, `investigate`, `analyze topic`, `look up`, `gather information`, `explore options` | `researcher` | `researcher` | route to the `researcher` agent (it owns the workflow) |

### Same-tier ambiguities (TRIGGER-TIE-001b) — explicit per-phrase resolutions

When a phrase matches **two skills** (no governing agent) or **two agents** (no shared workflow), the general rule does not apply. The following per-phrase resolutions are authoritative:

| Phrase | Owners | Resolution | Rationale |
|--------|--------|------------|-----------|
| `compliance check` | skill `validator`, skill `spec-compliance` | If task context contains "spec", "requirements", "traceability", "audit", or "compliance matrix" → route to `spec-compliance`. Otherwise (CI / build / zero-error context) → route to `validator`. | `spec-compliance` is requirement-to-implementation traceability; `validator` is the zero-error gate. Different scopes, same phrase. |
| `implement` | skill `production-code-workflow`, skill `task-executor` | If task context contains "code", "feature", "endpoint", "service", "module", "file", or any language name → route to `production-code-workflow`. Otherwise (generic task execution) → route to `task-executor`. | `production-code-workflow` enforces no-placeholder/no-stub patterns specific to source code; `task-executor` is generic. |
| `performance review` | agent `engineering-manager`, agent `qa-engineer` | If task context contains "team", "person", "promo", "OKR", "1:1", "performance management", or any individual's name → route to `engineering-manager`. Otherwise (system, latency, throughput, load testing) → route to `qa-engineer`. | These are two unrelated concepts (HR vs system performance) sharing a phrase. |

The receipt's `verdict.routing_rationale` field SHOULD cite the relevant rule (`TRIGGER-TIE-001a` or `TRIGGER-TIE-001b`) when a conflict was resolved.

---

## Checkpoint Schema Additions

The auto-orchestrate checkpoint includes these phase-tracking fields:

```json
{
  "phase_transitions": [],
  "phase_receipts": [],
  "phase_findings": {
    "0": [], "1": [], "2": [], "3": [], "4": [], "4.5": [], "5": [], "6": []
  },
  "phase_gates": {},
  "phase_summary": null,
  "release_flag": false
}
```

### Field Definitions

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `phase_transitions` | array | `[]` | Append-only log of phase transitions: `{ from_phase, to_phase, reason, timestamp }` |
| `phase_receipts` | array | `[]` | Paths to phase receipts written under `.orchestrate/<session>/phase-receipts/` |
| `phase_findings` | object | `{}` (empty per stage) | Per-stage array of phase receipt summaries to include in spawn prompts. Keyed by stage number. |
| `phase_gates` | object | `{}` | Active phase gates blocking stage advancement. Keyed by stage number, value is phase_receipt_id. Cleared when finding is addressed. |
| `phase_summary` | object/null | `null` | Written at termination. `{ total_phases_invoked, phases_completed, phase_receipts }` |
| `release_flag` | boolean | `false` | Set to `true` when task description contains release/deploy keywords or user passes `--release`. Triggers Phase 7 at session end. |

---

## Session Directory Layout

```
.orchestrate/<session-id>/
├── checkpoint.json
├── gate-state.json                    # Auto-evaluated gate verdicts + human approvals (8 gates)
├── raid-log.json                      # Shared RAID log (Phase 2 + Phase 9)
├── planning/                          # Planning artifacts (P1-P4)
├── stage-{0,1,2,3,4,4.5,5,6}/         # Per-stage outputs
├── phase-receipts/                    # Phase context + receipts
│   ├── phase-context-5s.json          # Context written before phase agent spawn
│   ├── phase-5s-security-<TS>.json    # Phase receipt written after agent returns
│   └── phase-5s-security-findings.md  # Optional artifact produced by phase agent
├── meetings/                          # Meeting receipts (Multi-Agent Sync + Async Single-Agent)
│   ├── meeting-p-026-daily-standup-iter-15-<TS>.json
│   ├── meeting-p-027-sprint-review-<TS>.json
│   ├── meeting-p-028-sprint-retro-<TS>.json
│   └── meeting-p-029-backlog-refinement-<TS>.json
├── gates/                             # Human gate pending/approval files
│   ├── gate-pending-<gate_id>.json
│   └── gate-approval-<gate_id>.json
└── handovers/                         # Agent-to-agent handover protocol
    ├── handover-<from>-to-<to>-<TS>.json     # Written by from_agent (HANDOVER-001)
    ├── ack-<handover_id>.json                 # Written by to_agent (HANDOVER-002)
    └── clarification-<handover_id>-r<N>.json  # Written on re-spawn (HANDOVER-003)
```

---

## Integration Points (within `/auto-orchestrate`)

| Step | Hook | Phase Transitions Evaluated |
|------|------|------------------------------|
| Step 0g | Pre-session phase initialization | Resume incomplete prior phase if any |
| Step 0h | Planning loop | P1 → P2 → P3 → P4 with auto-evaluated gates |
| Step 4.8c | Post-stage transition evaluation | Stage transitions to 5q / 5s / 5i / 5d / 5v / 5e / 9 based on stage-receipt + scope |
| Step 5 | Post-termination | Phase 7 (Release Prep) when release_flag; Phase 8 (Post-Launch) after Phase 7 |

---

## Relationship to Existing Protocols

### Process Injection Map (`process_injection_map.md`)

The injection map defines which processes apply at each stage and whether they are advisory or enforced. With the consolidation, the `domain_guide` field is replaced by `phase` — pointing to an internal phase rather than a separate command.

| Concern | Process Injection Map | Internal Phase Invocation |
|---------|----------------------|----------------------------|
| Scope | Maps processes to stages | Invokes domain phases when processes flag issues |
| Mechanism | Hook format (notify/gate/link) | Phase agent spawn with phase-context |
| Output | Process acknowledgment in stage-receipt | Phase receipt with next_action |
| Enforcement | Per-hook `enforced` flag | Per-phase gate at planning + release |

### Cross-Pipeline State (`cross-pipeline-state.md`)

With one command, the cross-pipeline state simplifies. `task-board.json`, `focus-stack.json`, `active-session.json` are still produced for `/workflow-*` skill consumers (those are skills, not commands). `escalation-log.jsonl` is no longer produced — there is no cross-pipeline escalation.
