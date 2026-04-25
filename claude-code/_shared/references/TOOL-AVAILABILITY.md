# Tool Availability Constraints for Claude Code Agents

## Overview

Tool availability in Claude Code is determined by the **built-in agent type definitions**, NOT by manifest.json declarations. The manifest documents intended tool usage but does not grant tool access at runtime.

**Critical distinction**: The `Task` tool (spawns subagents) is a DIFFERENT tool from `TaskCreate`/`TaskList`/`TaskUpdate`/`TaskGet` (task management). These are separate tools with separate availability.

## The Gap (GAP-CRIT-001) — OPEN

**Problem**: Subagents spawned via `Task(subagent_type: "...")` receive a LIMITED set of tools defined by Claude Code's built-in agent type registry. Critically:

1. **Task tool**: Listed in agent type definitions but **NOT reliably available at runtime** when spawned by auto-orchestrate. The orchestrator has confirmed it cannot spawn subagents.
2. **TaskCreate/TaskList/TaskUpdate/TaskGet**: These task management tools are **NEVER available** to any subagent. They are only available to the main Claude Code instance (the auto-orchestrate loop).

**Root Cause**: Claude Code's built-in agent type definitions declare tools that may not be provisioned at runtime depending on the spawn context, permission mode, and conversation state. The manifest.json mirrors these declarations but neither document controls actual runtime availability.

**Status**: OPEN — Workaround implemented via file-based task proposal protocol.

## Tool Availability Matrix (Actual Runtime)

| Agent | Actually Available | NOT Available | Spawned By |
|-------|-------------------|---------------|------------|
| orchestrator | Read, Glob, Grep, Bash | Task*, TaskCreate/List/Update/Get | auto-orchestrate, auto-audit |
| product-manager | Read, Glob, Grep, Bash | Task*, TaskCreate/List/Update/Get | orchestrator |
| researcher | Read, Glob, Grep, Bash, WebSearch, WebFetch | Task*, TaskCreate/List/Update/Get | orchestrator |
| software-engineer | Read, Write, Edit, Bash, Glob, Grep | Task*, TaskCreate/List/Update/Get | orchestrator |
| technical-writer | Read, Glob, Grep, Edit, Write | Task*, TaskCreate/List/Update/Get | orchestrator |
| debugger | Read, Write, Edit, Bash, Glob, Grep | Task*, TaskCreate/List/Update/Get | auto-debug |
| auditor | Read, Glob, Grep, Bash | Task*, TaskCreate/List/Update/Get | auto-audit |
| session-manager | Read, Glob, Grep, Bash | Task*, TaskCreate/List/Update/Get | orchestrator |

\* Task tool availability is unreliable — declared but not consistently provisioned at runtime when spawned via auto-orchestrate.

**Key Findings**:
- TaskCreate, TaskList, TaskUpdate, and TaskGet are **NEVER** available to any subagent. Only the loop controllers (auto-orchestrate, auto-debug, auto-audit) have these tools.
- The **researcher** agent uniquely has WebSearch and WebFetch for internet research.
- The **auditor** agent is read-only — it has no Write or Edit tools.
- The **debugger** agent has the same write tools as the software-engineer (it fixes code).

## Workaround: File-Based Task Proposal Protocol

> **CONSTRAINT**: The file-based protocol is a communication channel, NOT permission for the orchestrator to perform implementation work. Writing `.orchestrate/<session-id>/proposed-tasks.json` is only permitted when explicitly directed by the spawn prompt. The orchestrator MUST NOT write any other files to disk — EVEN IF the files are plans, analyses, specifications, or documentation. See Orchestrator constraints above.

Since subagents cannot create or manage tasks directly, the system uses a file-based protocol:

### Task Proposals (Subagent → Auto-Orchestrate)

Subagents write task proposals to `.orchestrate/<session-id>/proposed-tasks.json`:

```json
{
  "tasks": [
    {
      "subject": "Task title",
      "description": "Detailed description. dispatch_hint: software-engineer",
      "activeForm": "Working on X",
      "blockedBy": [],
      "dispatch_hint": "software-engineer",
      "risk": "medium",
      "acceptance_criteria": ["Criterion 1", "Criterion 2"]
    }
  ]
}
```

The auto-orchestrate loop reads this file after each orchestrator iteration and creates tasks via TaskCreate.

### Task State (Auto-Orchestrate → Orchestrator)

The auto-orchestrate loop passes current task state in the orchestrator's spawn prompt under a `## Current Task State` section. The orchestrator reads task state from this context instead of calling TaskList.

### Task Updates (Orchestrator → Auto-Orchestrate)

The orchestrator returns proposed task updates in its response using a `PROPOSED_ACTIONS` JSON block. The auto-orchestrate loop parses this and executes TaskUpdate calls.

## What the Manifest.json Does (and Doesn't Do)

The manifest.json serves three purposes:
1. **Documentation** — declares intended tool usage patterns
2. **Discovery** — helps agents understand capabilities of other agents
3. **Validation** — CI checks for consistency

It does NOT:
- Grant tool permissions at runtime
- Control runtime tool availability
- Override Claude Code's built-in agent type tool access

## Implications for Agent Design

### Orchestrator
- Cannot call TaskList → receives task state in spawn prompt
- Cannot call TaskCreate → proposes tasks via files or return values
- Cannot call TaskUpdate → proposes updates via return values
- Cannot reliably call Task → reports back via PROPOSED_ACTIONS; auto-orchestrate retries or handles delegation.

  **UNCONDITIONAL PROHIBITION**: The orchestrator MUST NOT perform implementation work directly — REGARDLESS OF whether the Task tool is available, REGARDLESS OF whether the work seems urgent, and REGARDLESS OF whether the orchestrator believes the action is "analysis" rather than "implementation." MAIN-001 (stay high-level) and MAIN-002 (delegate ALL work) are non-negotiable.

  **No exceptions, including when**:
  - The Task tool is unavailable or fails
  - The work seems time-sensitive or urgent
  - The orchestrator has already analyzed the problem and the solution seems obvious
  - The orchestrator believes it is "only writing a planning document" rather than "implementing"
  - The proposed output is a markdown file, an analysis document, a specification, or any other non-code artifact
  - The orchestrator rationalizes a "more practical approach" due to tool limitations
  - The orchestrator claims direct work is "more efficient for [task type] anyway"
  - The orchestrator wants to "do the research phase directly by reading the codebase"
  - The orchestrator proposes to "create the tasks myself and spawn software-engineer agents"

  **Observed violation patterns** (from production incidents):
  1. "Given the orchestrator approach has tool limitations that prevent effective task creation from subagents, let me take a more practical approach. I'll do the research phase directly (Stage 0) by reading the codebase, then create the tasks myself and spawn software-engineer agents for the actual fixes." — This is a MAIN-001/MAIN-002/MAIN-012 violation disguised as pragmatism.
  2. "The subagent tools can't write files reliably. Let me do the research directly - this is more efficient for an audit task anyway. I'll read the key files across all services systematically." — This is a MAIN-001/MAIN-002 violation disguised as efficiency.

  The ONLY permitted actions when Task tool is unavailable: read existing files (Read/Glob/Grep) ONLY to compose PROPOSED_ACTIONS task descriptions, then return PROPOSED_ACTIONS.

### Product-Manager
- Cannot call TaskCreate → writes task proposals to `.orchestrate/<session-id>/proposed-tasks.json`
- Cannot call TaskList → receives relevant task context in spawn prompt
- Task proposals follow the JSON format above

### Researcher
- Cannot call TaskCreate → findings written to `stage-0/YYYY-MM-DD_<slug>.md`
- HAS WebSearch and WebFetch (only agent with internet access)
- Writes `stage-receipt.json` on completion (per output-standard.md RECEIPT-001)

### Software-Engineer
- Cannot call TaskUpdate → reports completion status in return value (DONE block)
- Can read/write/edit files (its core function works correctly)
- Writes `stage-receipt.json` + `changes.md` to stage directory

### Debugger
- Cannot call TaskCreate → error fixes tracked via `.debug/<session-id>/error-history.jsonl`
- Can read/write/edit files (fixes code directly)
- Queries `.domain/fix_registry.jsonl` for known fixes before diagnosing
- Writes fixes to `.domain/fix_registry.jsonl` after verification

### Auditor
- Cannot call TaskCreate → writes gap-report.json to `.audit/<session-id>/cycle-<N>/`
- Read-only: has NO Write or Edit tools — never modifies project files
- Writes `stage-receipt.json` per audit cycle

### Session-Manager
- Cannot call TaskCreate → coordinates via workflow-* skill state machine
- Sets up `.orchestrate/<session-id>/` directory structure at boot

### Loop Controllers (auto-orchestrate, auto-debug, auto-audit)
- HAVE TaskCreate, TaskList, TaskUpdate, TaskGet (sole gateways for task management)
- Read task proposals from file-based protocols
- Pass task state to agents in spawn prompts
- Execute task updates based on agent return values
- Are the ONLY entities that can create, list, update, or get tasks
- Initialize `.domain/` directory for domain memory

## See Also

- `agents/orchestrator.md` — Orchestrator with fallback protocol
- `agents/product-manager.md` — File-based task proposal output
- `agents/debugger.md` — Debug agent with fix_registry integration
- `agents/auditor.md` — Read-only audit agent
- `commands/auto-orchestrate.md` — Single user-facing command. Internally proxies task management for orchestration, audit (Phase 5v), and debug (Phase 5e) sub-loops.
- `_shared/protocols/output-standard.md` — Unified output file naming and stage receipts
- `ARCHITECTURE.md` — System architecture

## Status

- **Discovered**: 2026-02-11 (Iteration 1 gap analysis)
- **Documented**: 2026-02-11 (Iteration 2 remediation)
- **False Resolution**: 2026-02-14 (Documentation incorrectly claimed RESOLVED)
- **Reopened**: 2026-02-15 (Confirmed Task tool NOT available at runtime; TaskCreate/TaskList never available to subagents)
- **Workaround**: 2026-02-15 (File-based task proposal protocol implemented)
