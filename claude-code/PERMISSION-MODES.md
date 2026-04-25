# Permission Mode Compatibility Matrix (GAP-MED-002)

## Overview

Claude Code operates in different permission modes that affect tool availability and agent behavior. This document provides a compatibility matrix for all agents and skills across permission modes.

**Gap Status**: GAP-MED-002 MEDIUM
**Created**: 2026-02-11 (Iteration 2 remediation)
**Purpose**: Document agent/skill behavior across permission modes to enable fully autonomous operation

## Permission Modes

### Mode 1: Plan Mode

**Characteristics**:
- Interactive planning and approval workflow
- User reviews proposed actions before execution
- `EnterPlanMode` tool available
- Step-by-step execution with user confirmation

**Tool Behavior**:
- Read: Available
- Write/Edit: Requires approval for each operation
- Bash: Requires approval for each command
- Task: Availability depends on context

**Typical Use Cases**:
- Exploratory work with uncertain outcomes
- High-risk operations requiring oversight
- Learning new codebases
- User wants to review each change

### Mode 2: Auto-Accept Mode

**Characteristics**:
- Tools execute without per-action approval
- User grants blanket permission at session start
- Fast iteration on trusted operations
- Suitable for autonomous workflows

**Tool Behavior**:
- Read: Available, no approval needed
- Write/Edit: Available, no approval needed
- Bash: Available, no approval needed
- Task: Availability depends on spawn context

**Typical Use Cases**:
- `/auto-orchestrate` command
- Trusted refactoring operations
- Batch file updates
- CI/CD automation

### Mode 3: Manual Approval Mode

**Characteristics**:
- Default mode for most conversations
- Per-action approval for write operations
- Read operations allowed without approval
- Balance between control and efficiency

**Tool Behavior**:
- Read: Available, no approval needed
- Write/Edit: Requires user confirmation
- Bash: May require approval for destructive commands
- Task: Availability depends on context

**Typical Use Cases**:
- Interactive development sessions
- Code review with modifications
- Experimental changes
- Reviewing agent-generated plans

## Agent Compatibility Matrix

| Agent | Plan Mode | Auto-Accept | Manual Approval | Degradation Behavior |
|-------|-----------|-------------|-----------------|---------------------|
| **orchestrator** | Partial | YES (preferred) | Limited | Proposes work via PROPOSED_ACTIONS when Task unavailable (GAP-CRIT-001) — NEVER performs inline execution (MAIN-001, MAIN-002) |
| **product-manager** | Partial | YES | YES | Creates task plans as JSON files if TaskCreate unavailable |
| **software-engineer** | NO (conflicts with IMPL-002) | YES (required) | Partial | Requires Write/Edit access; will fail without auto-accept |
| **technical-writer** | Partial | YES | YES | Can operate with approval for each Write/Edit |
| **session-manager** | Partial | YES (preferred) | YES | Session file writes need approval in manual mode |
| **researcher** | YES | YES | YES | Read-only (WebSearch/WebFetch); fully compatible with all modes |
| **debugger** | NO (conflicts with DBG-002/DBG-004) | YES (required) | Partial | Requires Write/Edit to apply fixes; plan mode conflicts with "fix immediately" constraint |
| **auditor** | YES | YES | YES | Read-only — AUD-001 prohibits all writes; always compatible |

### orchestrator

**Preferred Mode**: Auto-Accept
**Constraints**: MAIN-002 requires Task tool for delegation

**Behavior by Mode**:
- **Plan Mode**: Cannot use EnterPlanMode (conflicts with autonomous operation). If Task available: delegates normally. If Task unavailable: proposes work via PROPOSED_ACTIONS — auto-orchestrate handles delegation on next iteration
- **Auto-Accept**: Full functionality IF Task tool available. Delegates to subagents without interruption
- **Manual Approval**: Limited — each subagent spawn would require approval, breaking autonomous flow

**Known Issues**:
- GAP-CRIT-001: Task tool may be unavailable regardless of permission mode
- Fallback: Proposes work via PROPOSED_ACTIONS for auto-orchestrate to delegate — orchestrator NEVER performs inline execution (MAIN-001, MAIN-002 are non-negotiable regardless of tool availability)

### product-manager

**Preferred Mode**: Auto-Accept or Manual Approval
**Constraints**: None (creates tasks, doesn't write code)

**Behavior by Mode**:
- **Plan Mode**: Can create decomposition plans as markdown files for review
- **Auto-Accept**: Full functionality — creates tasks via TaskCreate, writes plan docs
- **Manual Approval**: Works well — user reviews each task before creation

**Known Issues**: None

### software-engineer

**Preferred Mode**: Auto-Accept (REQUIRED)
**Constraints**: IMPL-002 (Don't ask — make decisions autonomously)

**Behavior by Mode**:
- **Plan Mode**: INCOMPATIBLE — software-engineer makes autonomous decisions (IMPL-002), plan mode requires approval
- **Auto-Accept**: Full functionality — implements, reviews, fixes in one pass
- **Manual Approval**: DEGRADED — approval requests conflict with IMPL-002 constraint. Partial compatibility: user must approve each file write

**Known Issues**:
- Plan mode fundamentally conflicts with software-engineer's "don't ask" constraint
- Recommend: Use `/auto-orchestrate` or manually grant auto-accept when invoking software-engineer

### technical-writer

**Preferred Mode**: Auto-Accept or Manual Approval
**Constraints**: None (documentation updates are low-risk)

**Behavior by Mode**:
- **Plan Mode**: Can search docs (docs-lookup) and propose updates for review
- **Auto-Accept**: Full functionality — updates docs autonomously via docs-write
- **Manual Approval**: Works well — user reviews each doc change via Write/Edit approvals

**Known Issues**: None

### session-manager

**Preferred Mode**: Auto-Accept
**Constraints**: Needs write access to `.orchestrate/<session-id>/` (project-local primary path) and `~/.claude/manifest.json`. Legacy `~/.claude/sessions/` is a read-only fallback for crash recovery of pre-migration sessions only.

**Behavior by Mode**:
- **Plan Mode**: Session management doesn't fit plan-review workflow
- **Auto-Accept**: Full functionality — writes checkpoints, rotates manifest
- **Manual Approval**: Partial — user must approve each session file write (interrupts boot sequence)

**Known Issues**: Boot infrastructure (Step 0) may stall in manual mode awaiting session file write approval

### researcher

**Preferred Mode**: Any (fully compatible with all modes)
**Constraints**: Read-only — uses WebSearch and WebFetch; no file writes

**Behavior by Mode**:
- **Plan Mode**: Full functionality — research is read-only
- **Auto-Accept**: Full functionality
- **Manual Approval**: Full functionality — no write operations to approve

**Known Issues**: None

### debugger

**Preferred Mode**: Auto-Accept (REQUIRED)
**Constraints**: DBG-002 (minimal blast radius), DBG-004 (fix immediately) require Write/Edit access

**Behavior by Mode**:
- **Plan Mode**: INCOMPATIBLE — debugger applies targeted fixes immediately (DBG-004); plan mode approval conflicts with fix-immediately constraint
- **Auto-Accept**: Full functionality — diagnoses errors, applies fixes, verifies, writes debug reports
- **Manual Approval**: DEGRADED — each fix requires Write/Edit approval, breaking the fix-verify loop. Partial compatibility if user approves promptly.

**Known Issues**:
- Plan mode fundamentally conflicts with debugger's "fix immediately" constraint (DBG-004)
- Recommend: Use `/auto-debug` which operates in auto-accept mode

### auditor

**Preferred Mode**: Any (fully compatible with all modes)
**Constraints**: AUD-001 (read-only) — auditor NEVER writes to project files

**Behavior by Mode**:
- **Plan Mode**: Full functionality — audit is entirely read-only (Glob/Grep/Read only)
- **Auto-Accept**: Full functionality
- **Manual Approval**: Full functionality — no write operations to approve

**Known Issues**: None. Note that if auto-audit enters the remediation phase (spawning orchestrator to fix gaps), that phase requires Auto-Accept for software-engineer subagents.

## Skill Compatibility Matrix

| Skill | Plan Mode | Auto-Accept | Manual Approval | Notes |
|-------|-----------|-------------|-----------------|-------|
| researcher | YES | YES | YES | Read-only, always compatible |
| spec-creator | YES | YES | YES | Writes specs, approval OK |
| spec-analyzer | YES | YES | YES | Analysis-focused, approval OK |
| validator | YES | YES | YES | Read-only validation |
| test-writer-pytest | Partial | YES | YES | Writes test files |
| library-implementer-python | NO | YES (required) | Partial | Same constraints as software-engineer |
| task-executor | Partial | YES | YES | Generic execution, context-dependent |
| codebase-stats | YES | YES | YES | Read-only analysis |
| docs-lookup | YES | YES | YES | Read-only search |
| docs-write | YES | YES | YES | Documentation updates |
| docs-review | YES | YES | YES | Read-only review |
| refactor-analyzer | YES | YES | YES | Analysis phase only |
| refactor-executor | Partial | YES | Partial | File writes need approval/auto-accept |
| security-auditor | YES | YES | YES | Read-only scanning |
| spec-compliance | YES | YES | YES | Read-only analysis; always compatible |
| test-gap-analyzer | YES | YES | YES | Analysis + generates test stubs |
| error-standardizer | Partial | YES | Partial | Modifies code files |
| dependency-analyzer | YES | YES | YES | Read-only analysis |
| debug-diagnostics | NO | YES (required) | Partial | Used by debugger; requires Write for fix application |
| cicd-workflow | Partial | YES | YES | Creates CI files |
| docker-workflow | Partial | YES | YES | Creates Dockerfiles |
| dev-workflow | Partial | YES (preferred) | Partial | Commits need auto-accept |
| schema-migrator | NO | YES (required) | NO | Data migrations are high-risk |
| hierarchy-unifier | Partial | YES | Partial | Modifies task hierarchy |
| production-code-workflow | NO | YES (required) | NO | Production code = auto-accept only |
| workflow-* (5 skills) | YES | YES | YES | Session management, low-risk |

## Tool Availability by Permission Mode

| Tool | Plan Mode | Auto-Accept | Manual Approval | Notes |
|------|-----------|-------------|-----------------|-------|
| Read | ✅ Always | ✅ Always | ✅ Always | No restrictions |
| Glob | ✅ Always | ✅ Always | ✅ Always | No restrictions |
| Grep | ✅ Always | ✅ Always | ✅ Always | No restrictions |
| Write | ⚠️ Review | ✅ Auto | ⚠️ Approval | Context-dependent |
| Edit | ⚠️ Review | ✅ Auto | ⚠️ Approval | Context-dependent |
| Bash | ⚠️ Review | ✅ Auto | ⚠️ Approval (destructive) | Safe commands may auto-execute |
| Task | ⚠️ Context | ⚠️ Context | ⚠️ Context | **GAP-CRIT-001**: Availability not guaranteed by mode |

**Critical Finding**: Task tool availability is NOT determined by permission mode alone. It depends on spawn mechanism and conversation context (see GAP-CRIT-001 in `claude-code/_shared/references/TOOL-AVAILABILITY.md`).

## Autonomous Operation Recommendations

### For `/auto-orchestrate` Command

**Recommended Setup**:
1. Use Auto-Accept mode (permission granted in Step 0a)
2. Grant session folder access (`.orchestrate/`, `~/.claude/sessions/` legacy fallback, `~/.claude/plans/`)
3. Accept "no clarifying questions" policy (command makes assumptions)

**Expected Behavior**:
- orchestrator spawned in Auto-Accept mode
- Subagents inherit Auto-Accept permissions
- No approval prompts during execution loop
- Full autonomous operation

**Known Limitation**: Task tool may still be unavailable (GAP-CRIT-001), but Write/Edit/Bash work without approval prompts.

### For `/auto-debug` Command

**Recommended Setup**:
1. Use Auto-Accept mode (requires Write/Edit/Bash for applying fixes)
2. Ensure Docker daemon access if debugging Docker services
3. Grant project directory write access (debugger applies targeted fixes)

**Expected Behavior**:
- debugger spawned in Auto-Accept mode
- Applies minimal-blast-radius fixes to specific files
- Spawns researcher subagent for unfamiliar errors (WebSearch/WebFetch)
- Never commits or pushes — outputs suggested commit message only

**Known Limitation**: Task tool may still be unavailable (GAP-CRIT-001).

### For `/auto-audit` Command

**Recommended Setup**:
1. Auto-Accept mode is NOT required — auditor is read-only (AUD-001)
2. Manual Approval mode works; each audit step is non-destructive
3. If compliance gaps are found, auto-audit will spawn orchestrator for remediation — that phase requires Auto-Accept for software-engineer subagents

**Expected Behavior**:
- auditor runs in any permission mode (read-only)
- Produces `YYYY-MM-DD_audit-report.md` and `gap-report.json` (per cycle subdirectory)
- On gaps found: auto-audit spawns orchestrator in remediation phase
- compliance_threshold (default 90%) governs when loop exits

**Known Limitation**: Remediation phase inherits auto-orchestrate limitations (GAP-CRIT-001).

### For Manual Agent Invocation

**For software-engineer**:
```markdown
⚠️ Auto-Accept Required

The software-engineer agent operates under IMPL-002 (Don't ask — make decisions).
This conflicts with approval-based workflows.

**Action**: Grant auto-accept for this conversation or use `/auto-orchestrate`
```

**For technical-writer**:
- Manual approval OK for doc reviews
- Auto-accept preferred for batch doc updates

**For product-manager**:
- Any mode works
- Manual approval allows reviewing tasks before creation

## Fallback Behaviors

### When Task Tool Unavailable (All Modes)

orchestrator MUST NOT perform any work itself (MAIN-001, MAIN-002 are non-negotiable). Instead:
1. **Propose work via PROPOSED_ACTIONS** — auto-orchestrate reads proposals and delegates to the correct subagent on the next iteration
2. **Write task proposals** to `.orchestrate/<session-id>/proposed-tasks.json` for auto-orchestrate to process
3. **Report failure** — include in return value that Task tool was unavailable so auto-orchestrate can retry spawning
4. **Use Read/Glob/Grep for analysis only** — research and planning are allowed; writing, editing, or implementing code is NEVER allowed

See: `claude-code/_shared/references/TOOL-AVAILABILITY.md` (GAP-CRIT-001)

### When Write/Edit Unavailable (Plan/Manual Modes)

Agents that require Write/Edit will:
1. **Request approval** for each file operation
2. **Batch operations** when possible (single approval for multiple files)
3. **Escalate** if approval is denied

### When Bash Unavailable (Restricted Modes)

Skills that rely on Bash commands will:
1. **Use Read-only alternatives** (Grep instead of shell grep)
2. **Defer** to user for command execution
3. **Document** required commands for manual execution

## Testing Permission Mode Compatibility

### Test Checklist

To verify agent behavior across modes:

- [ ] **orchestrator**: Test in auto-accept with and without Task tool
- [ ] **software-engineer**: Verify failure in plan mode, success in auto-accept
- [ ] **technical-writer**: Test docs-write in all three modes
- [ ] **product-manager**: Test task creation in manual approval mode
- [ ] **session-manager**: Test boot sequence (Step 0) in manual mode

### Test Procedure

1. Create test session in each permission mode
2. Invoke agent with known task
3. Observe tool access patterns
4. Document approval prompts vs auto-execution
5. Check for degraded functionality vs complete failure

## Remediation Checklist

- [x] Document permission modes and characteristics
- [x] Create agent compatibility matrix
- [x] Create skill compatibility matrix
- [x] Document tool availability by mode
- [x] Provide autonomous operation recommendations
- [x] Document fallback behaviors
- [ ] Test orchestrator in all three modes (requires live testing)
- [ ] Test software-engineer in plan mode (expect failure per IMPL-002)
- [ ] Verify auto-orchestrate permission grant flow (Step 0a)
- [ ] Update agent docs with mode-specific guidance

## See Also

- `claude-code/_shared/references/TOOL-AVAILABILITY.md` — GAP-CRIT-001 (Task tool availability)
- `claude-code/agents/orchestrator.md` — MAIN-002 (delegate ALL work)
- `claude-code/agents/software-engineer.md` — IMPL-002 (don't ask)
- `claude-code/commands/auto-orchestrate.md` — Step 0a (permission grant flow)
- Iteration 1 gap analysis: `~/.claude/sessions/auto-orc-2026-0211-impl-gap/gap-analysis-findings.md`

---

**Last Updated**: 2026-03-25 (added researcher, debugger, auditor agents; auto-debug and auto-audit command sections; debug-diagnostics and spec-compliance skills)
**Related Gaps**: GAP-MED-002, GAP-CRIT-001
**Status**: Documented (live testing required for verification)
