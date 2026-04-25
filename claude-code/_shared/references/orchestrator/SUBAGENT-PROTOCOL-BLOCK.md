# Subagent Protocol Block

Reference the base protocol when spawning subagents via Task tool.

## Protocol Reference

@_shared/protocols/subagent-protocol-base.md

## Usage

When spawning a subagent via Task tool:

1. Reference the subagent protocol from the base file
2. Add task context (epic, dependencies, previous findings)
3. Define specific deliverables
4. Set clear completion criteria

## Example Subagent Prompt

```
You are the {ROLE} subagent. Your job is to complete task {TASK_ID}.

@_shared/protocols/subagent-protocol-base.md

## CONTEXT
- Epic: {EPIC_ID} ({EPIC_TITLE})
- Your Task: {TASK_ID} ({TASK_TITLE})
- Depends on: {DEPENDENCY_IDS}
- Turn limit: {MAX_TURNS} (prioritize core deliverable over quality gates)

## EARLY EXIT INSTRUCTIONS
If you cannot complete all phases within your turn budget:
1. Write partial results to the output file (EARLY-001)
2. Set manifest status to "partial" with remaining work in needs_followup (EARLY-002)
3. Priority order: (1) core deliverable, (2) self-review, (3) security audit, (4) quality pipeline (EARLY-003)
4. Return summary: "PARTIAL: completed X, remaining: Y"

## LARGE FILE HANDLING
For files exceeding 500 lines, do NOT read the entire file at once.
Use Grep to find relevant sections, then Read with offset/limit for targeted regions.
See READ-001 to READ-005 in the subagent protocol.

## REFERENCE FROM PREVIOUS RESEARCH (key_findings):
{PREVIOUS_KEY_FINDINGS}

## YOUR TASK
{DETAILED_INSTRUCTIONS}

BEGIN EXECUTION.
```

## See Also

- @_shared/protocols/subagent-protocol-base.md - Full protocol specification
- @_shared/protocols/task-system-integration.md - Task tool usage
- @_shared/templates/skill-boilerplate.md - Reusable skill patterns
