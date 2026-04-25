# Agent Reconciliation Notes

**Session**: auto-orc-20260406-gapintg  
**Date Verified**: 2026-04-06  
**Produced by**: software-engineer (Task #5, SPEC T001/T002/T003)  
**Status**: COMPLETE — All three agents verified IDENTICAL

---

## Summary

| Agent | Runtime Path | Source Path | MD5 Status | Install Risk |
|-------|-------------|-------------|------------|--------------|
| researcher | `~/.claude/agents/researcher.md` | `claude-code/agents/researcher.md` | IDENTICAL | LOW |
| session-manager | `~/.claude/agents/session-manager.md` | `claude-code/agents/session-manager.md` | IDENTICAL | LOW |
| orchestrator | `~/.claude/agents/orchestrator.md` | `claude-code/agents/orchestrator.md` | IDENTICAL | LOW (escalates to CRITICAL on divergence) |

---

## Agent: researcher

**Runtime path**: `~/.claude/agents/researcher.md`  
**Source path**: `claude-code/agents/researcher.md`  
**Date verified**: 2026-04-06

### Checksum Table

| File | MD5 | Size (bytes) |
|------|-----|-------------|
| Runtime (`~/.claude/agents/researcher.md`) | `5dd21a71c86cf1111bb587eb287d7fff` | 11807 |
| Source (`claude-code/agents/researcher.md`) | `5dd21a71c86cf1111bb587eb287d7fff` | 11807 |
| **Status** | **IDENTICAL** | — |

### Differences

No differences found.

### Install Risk Assessment

**Risk level**: LOW

Both files are byte-for-byte identical as of 2026-04-06. Running `install.sh` will not introduce divergence because the source and runtime copies are the same. Risk remains LOW as long as both files are updated together whenever the researcher agent is modified.

### Canonical Definition

`claude-code/agents/researcher.md` is the authoritative source. The runtime copy at `~/.claude/agents/researcher.md` is installed from the source by `install.sh`.

### Capabilities Preserved

- WebSearch + WebFetch for internet research (RES-008 — at least 3 queries mandatory)
- Stage 0 mandatory research protocol (RES-001 through RES-013)
- CVE checking via NVD and GitHub Security Advisories (RES-005, RES-010)
- Web-verified version numbers with currency requirement (RES-002, RES-012)
- Software-engineer feedback re-research loop (RES-013)
- Evidence-based findings with source citations (RES-001)
- Actionable recommendations with Risks and Remedies section (RES-004, RES-009)
- Structured output to `.orchestrate/<SESSION_ID>/stage-0/YYYY-MM-DD_<slug>.md` (RES-006, RES-007)
- research_completeness_score sections (Executive Summary, Core Technical Research, Tooling/Library Analysis, Architecture/Design Patterns, Risks and Remedies, CVE/Security Assessment, Recommended Versions Table, References)
- Partial status reporting when WebSearch is unavailable (RES-008)

### Action Required

**NONE** — Verify on every `install.sh` run that checksums remain equal before overwriting the runtime copy.

---

## Agent: session-manager

**Runtime path**: `~/.claude/agents/session-manager.md`  
**Source path**: `claude-code/agents/session-manager.md`  
**Date verified**: 2026-04-06

### Checksum Table

| File | MD5 | Size (bytes) |
|------|-----|-------------|
| Runtime (`~/.claude/agents/session-manager.md`) | `5f89522b7ba48b8679452252aa2d9b1e` | 7800 |
| Source (`claude-code/agents/session-manager.md`) | `5f89522b7ba48b8679452252aa2d9b1e` | 7800 |
| **Status** | **IDENTICAL** | — |

### Differences

No differences found.

### Install Risk Assessment

**Risk level**: LOW

Both files are byte-for-byte identical as of 2026-04-06. The session-manager governs the orchestration session lifecycle state machine. Any divergence between runtime and source would silently break session recovery, workflow routing, or constraint enforcement across all pipeline runs.

### Canonical Definition

`claude-code/agents/session-manager.md` is the authoritative source. The runtime copy at `~/.claude/agents/session-manager.md` is installed from the source by `install.sh`.

### Capabilities Preserved

- Session lifecycle state machine: IDLE → ACTIVE → ENDED (with SUSPENDED intermediate)
- `workflow-*` skill routing table: workflow-start, workflow-dash, workflow-focus, workflow-next, workflow-plan, workflow-end
- MAIN-001 through MAIN-005 orchestration constraints (all preserved in both copies)
- Session recovery from checkpoint (`session_state: active` detection)
- Validation gates for state transition blocking (invalid transitions rejected)
- Session state persistence to `~/.claude/sessions/<session_id>/state.json`
- Manifest probe at session start (manifest.json registry validation)
- Multi-session concurrency guard (only one ACTIVE session per user)
- Session handoff to orchestrator on `workflow-start` invocation

### Action Required

**NONE** — Verify on every `install.sh` run that checksums remain equal before overwriting the runtime copy.

---

## Agent: orchestrator

**Runtime path**: `~/.claude/agents/orchestrator.md`  
**Source path**: `claude-code/agents/orchestrator.md`  
**Date verified**: 2026-04-06

### Checksum Table

| File | MD5 | Size (bytes) |
|------|-----|-------------|
| Runtime (`~/.claude/agents/orchestrator.md`) | `9cbd7a90fdffbb83828c64c6c85c8e16` | 32479 |
| Source (`claude-code/agents/orchestrator.md`) | `9cbd7a90fdffbb83828c64c6c85c8e16` | 32479 |
| **Status** | **IDENTICAL** | — |
| **Size sentinel** | 32479 bytes | (change = CRITICAL alert) |

### Differences

No differences found.

### Install Risk Assessment

**Risk level**: LOW (current) — escalates to **CRITICAL** if any future edit diverges the two files.

`orchestrator.md` IS the orchestrator system prompt. At 32,479 bytes, it is the largest and most complex agent file in the repository. Overwriting `~/.claude/agents/orchestrator.md` with a different source version would silently break the entire auto-orchestrate pipeline, PDCA meta-loop, OODA failure classification, all stage routing, and all MAIN-001 through MAIN-015 constraints.

### CRITICAL Risk Escalation Warning

Any future divergence between `~/.claude/agents/orchestrator.md` and `claude-code/agents/orchestrator.md` is a **CRITICAL incident**, not a routine update. The runtime file is the live orchestrator system prompt — it controls every decision in every pipeline run.

**Required response to any detected divergence**:
1. HALT any active orchestration session.
2. Run a full diff: `diff ~/.claude/agents/orchestrator.md claude-code/agents/orchestrator.md`
3. Review every differing line. Do not auto-merge.
4. Escalate to the repository owner before resolving.

### install.sh Recommendation

`install.sh` MUST verify `orchestrator.md` checksums **before** overwriting the runtime copy. The recommended guard:

```bash
# In install.sh — orchestrator.md installation guard
RUNTIME_ORC="$HOME/.claude/agents/orchestrator.md"
SOURCE_ORC="claude-code/agents/orchestrator.md"

if [ -f "$RUNTIME_ORC" ]; then
    RUNTIME_MD5=$(md5sum "$RUNTIME_ORC" | cut -d' ' -f1)
    SOURCE_MD5=$(md5sum "$SOURCE_ORC" | cut -d' ' -f1)
    if [ "$RUNTIME_MD5" != "$SOURCE_MD5" ]; then
        echo "WARNING: orchestrator.md checksums differ!"
        echo "  Runtime MD5:  $RUNTIME_MD5 ($RUNTIME_ORC)"
        echo "  Source MD5:   $SOURCE_MD5 ($SOURCE_ORC)"
        echo "  Run 'diff $RUNTIME_ORC $SOURCE_ORC' to review differences."
        echo "  Use --force-orchestrator to override this guard."
        if [ "$1" != "--force-orchestrator" ]; then
            echo "SKIPPING orchestrator.md overwrite. Existing runtime copy preserved."
            exit 0
        fi
    fi
fi
cp "$SOURCE_ORC" "$RUNTIME_ORC"
```

This guard is referenced in SPEC T003 and is required for T009 (bridge protocol) implementation.

### Canonical Definition

`claude-code/agents/orchestrator.md` is the authoritative source. The runtime copy at `~/.claude/agents/orchestrator.md` is installed from the source by `install.sh` — but ONLY after checksum verification passes.

### Capabilities Preserved — Full Inventory

#### Pipeline Stages (7 mandatory stages)

| Stage | Agent | Purpose | Mandatory |
|-------|-------|---------|-----------|
| Stage 0 | `researcher` | Research, CVEs, codebase context | YES |
| Stage 1 | `product-manager` | Task decomposition, deps, risk | YES |
| Stage 2 | `spec-creator` | Technical specifications | YES |
| Stage 3 | `software-engineer` / `library-implementer-python` | Production code | Per task |
| Stage 4 | `test-writer-pytest` | Tests | Per task |
| Stage 4.5 | `codebase-stats` | Technical debt measurement | YES (post-impl) |
| Stage 5 | `validator` (+ `docker-validator`) | Compliance/correctness | YES |
| Stage 6 | `technical-writer` | Documentation updates | YES |

#### Orchestration Constraints (MAIN-001 through MAIN-015)

| ID | Constraint |
|----|-----------|
| MAIN-001 | Stay high-level — no implementation details, no writing code |
| MAIN-002 | Delegate ALL work — use Task tool exclusively for execution |
| MAIN-003 | No full file reads — manifest summaries / key_findings only |
| MAIN-004 | Sequential spawning — one subagent at a time; loop until budget exhausted |
| MAIN-005 | Per-handoff <=10K tokens |
| MAIN-006 | Zero-error gate — do NOT exit until 0 errors AND 0 warnings |
| MAIN-007 | Session folder autonomy — full read access to `~/.claude/`; writes delegated to session-manager |
| MAIN-008 | Minimal user interruption — ask ONLY for ambiguous objectives or irreversible decisions |
| MAIN-009 | File scope discipline — never touch files outside task scope |
| MAIN-010 | No deletion without consent |
| MAIN-011 | `max_turns` on every spawn |
| MAIN-012 | Flow integrity — ALWAYS follow full pipeline; STAGE_CEILING is a hard structural limit |
| MAIN-013 | Decomposition gate — NEVER spawn software-engineer unless task has `dispatch_hint` |
| MAIN-014 | No auto-commit — NEVER git commit/push |
| MAIN-015 | Always-visible processing — output progress before/after every spawn |

#### CI Engine Integrations

- **PDCA meta-loop** (cross-run): Plan (improvement_targets.json injection) → Do (stages 0-6) → Check (RetrospectiveAnalyzer) → Act (ImprovementRecommender + BaselineManager)
- **OODA within-run loop**: Observe → Orient (failure classification) → Decide (continue/retry/fallback_to_spec/surface_to_user) → Act
- **Stage telemetry hooks**: 7 hooks (hook:stage:before, hook:stage:after:success, hook:stage:after:failure, hook:stage:retry, hook:stage:fallback, hook:stage:escalate, hook:run:complete)
- **research_completeness_score blocking gate**: Threshold 70/100; blocks Stage 1 if Stage 0 score < 70
- **Domain memory** (6 JSONL stores): research_ledger, decision_log, pattern_library, fix_registry, codebase_analysis, user_preferences
- **CI Engine modules**: OODAController, StageMetricsCollector, RetrospectiveAnalyzer, ImprovementRecommender, BaselineManager
- **Backward compatibility**: All CI sections guarded by `if HAS_CI_ENGINE:` — graceful degradation when modules absent

#### Boot Sequence

1. Step -1 (PRE-BOOT): Write proposed-tasks.json atomically
2. Step -0.5 (CI ENGINE PROBE): Module-level availability check for all 5 CI modules
3. Step -0.25 (DOMAIN MEMORY PROBE): Check/initialize `.domain/` directory
4. Step 0 (BOOT-INFRA): Spawn session-manager for `.orchestrate/<session_id>/` setup
5. Step 1 (MANIFEST-001): Read `~/.claude/manifest.json` — authoritative routing registry
6. Step 2: Read Current Task State and STAGE_CEILING from spawn prompt
7. Step 3: Determine current pipeline stage; verify STAGE_CEILING not exceeded
8. Step 4 (CONSTRAINT CHECK): Delegate-or-stop self-audit

### Action Required

**Add `install.sh` guard before overwriting `orchestrator.md`.** See install.sh Recommendation section above. This guard MUST be implemented before the next `install.sh` run that modifies agent files. Reference: SPEC T003 → T009 (bridge protocol).

---

## Verification Commands

Run these after every `install.sh` execution to confirm continued identity:

```bash
# Verify all three agents remain identical
echo "=== researcher ===" && md5sum ~/.claude/agents/researcher.md claude-code/agents/researcher.md
echo "=== session-manager ===" && md5sum ~/.claude/agents/session-manager.md claude-code/agents/session-manager.md
echo "=== orchestrator ===" && md5sum ~/.claude/agents/orchestrator.md claude-code/agents/orchestrator.md

# Verify orchestrator size sentinel (expected: 32479 bytes each)
wc -c ~/.claude/agents/orchestrator.md claude-code/agents/orchestrator.md

# Verify all three agents covered in this notes file
grep -c "^## Agent:" claude-code/agents/agent-reconciliation-notes.md
# Expected: 3
```

---

*Last verified: 2026-04-06 | Next required verification: on every install.sh run*

---

## Consolidation: 2026-04-14 (Session: auto-orc-20260414-rmdupes)

**Action**: Removed 3 duplicate agents and updated all references across 40+ files.

| Removed Agent | Replaced By | Pipeline Stage |
|---------------|------------|----------------|
| `epic-architect` | `product-manager` | Stage 1 |
| `implementer` | `software-engineer` | Stage 3 |
| `documentor` | `technical-writer` | Stage 6 |

**Agent count**: 21 → 18

**Rationale**: The removed agents were duplicates of existing team agents with identical capabilities and skill bindings. Consolidation eliminates routing ambiguity in `manifest.json` and reduces maintenance burden. The replacement agents retain all constraints (IMPL-001 through IMPL-015, SFI-001) and skill bindings from the removed agents.

**Files affected**: Agent definitions, manifest.json, orchestrator.md, auto-orchestrate.md, ARCHITECTURE.md, INTEGRATION.md, PERMISSION-MODES.md, and all process/reference files that referenced the old agent names.

**Verification**: Stage 5 validation confirmed zero remaining references to removed agents in active (non-historical) documentation.
