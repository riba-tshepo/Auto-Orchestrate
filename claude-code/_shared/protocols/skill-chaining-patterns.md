# Skill Chaining Patterns

This reference defines patterns for multi-level skill invocation and context propagation across agent boundaries.

---

## Related Protocols

- **@_shared/protocols/skill-chain-contracts.md** - RFC 2119 requirements for chain handoffs
- **@_shared/references/workflow-patterns.md** - Reusable workflow patterns (analyzer-executor, producer-consumer, etc.)

---

## Pattern Overview

| Pattern | Description | Use Case |
|---------|-------------|----------|
| Single-level | Orchestrator spawns one skill | Simple task delegation |
| Skill chaining | Skill invokes other skills | Workflow orchestration |
| Multi-level | Subagent becomes orchestrator | Complex nested workflows |

---

## Pattern 1: Single-Level Spawning

The orchestrator delegates work to a subagent via Task tool with skill injection.

### Flow

```
┌─────────────────┐
│   ORCHESTRATOR  │
│  (orchestrator)
└────────┬────────┘
         │ Task tool + skill template
         v
┌─────────────────┐
│    SUBAGENT     │
│ (researcher)
└─────────────────┘
```

### Implementation

```bash
# Orchestrator prepares context
source lib/token-inject.sh
export TI_TASK_ID="T1234"
export TI_DATE="$(date +%Y-%m-%d)"
export TI_SLUG="auth-research"
ti_set_defaults

# Load skill template with tokens
template=$(ti_load_template "skills/researcher/SKILL.md")

# Spawn via Task tool (includes subagent protocol block)
```

### Context Propagation

- **Input**: Task ID, skill template, previous manifest key_findings
- **Output**: Manifest entry with key_findings for next agent
- **Response**: "Research complete. See MANIFEST.jsonl for summary."

---

## Pattern 2: Skill Chaining

A skill invokes other skills to complete workflow phases. The loaded skill maintains context while delegating specialized work.

### Example: technical-writer

```
┌─────────────────────┐
│   technical-writer  │ <- Loaded by user request
│  (Documentation     │
│   Specialist)       │
└─────────┬───────────┘
          │
    ┌─────┴─────┬────────────┐
    v           v            v
┌───────┐  ┌────────┐  ┌─────────┐
│lookup │  │ write  │  │ review  │
│(Phase │  │(Phase  │  │(Phase   │
│   1)  │  │   3)   │  │   4)    │
└───────┘  └────────┘  └─────────┘
```

### Skill Invocation Methods

**Context matters**: The invocation method depends on WHERE the skill is being called from.

#### Main conversation (has Skill tool)
```markdown
# Via Skill tool (programmatic) — ONLY works in main conversation
Skill(skill="docs-lookup")

# Via slash command (user-facing) — ONLY works in main conversation
/docs-lookup
```

#### Subagent context (NO Skill tool available)
```markdown
# Read and follow inline — agent reads the SKILL.md and follows its instructions directly
# The agent MUST have the tools needed by the skill (Read, Glob, Grep, Edit, Write, etc.)
Read: skills/<skill-name>/SKILL.md → follow all steps using available tools

# Delegate via Task tool — spawn a subagent with the skill content as the prompt
Task(description: "Execute docs-lookup", prompt: "<SKILL.md content>", subagent_type: "general-purpose", max_turns: 15)
```

**IMPORTANT**: Agents spawned via the Task tool (technical-writer, session-manager, software-engineer, etc.) do NOT have access to the `Skill()` tool. They MUST use one of the subagent invocation methods above. Attempting `Skill(skill="...")` from a subagent will fail silently or produce no result.

### When to Use Skill Chaining

| Scenario | Pattern |
|----------|---------|
| Workflow has distinct phases | Chain skills for each phase |
| Skills share common context | Parent skill maintains state |
| Quality gates between phases | Invoke review skill before completion |
| Specialized expertise needed | Delegate to domain-specific skill |

### Canonical Pattern: Cross-Skill Script Invocation

When a skill needs to consume another skill's Python script output, invoke the script directly via relative path. This avoids spawning a subagent and keeps the output in the calling skill's context.

**Example: test-writer-pytest invoking hierarchy-unifier's function_discoverer**

```bash
# From within test-writer-pytest, invoke a sibling skill's script
python ../hierarchy-unifier/scripts/function_discoverer.py <target_directory>
```

**Expected output format:** JSON array of discovered functions with file paths, names, and signatures.

**How the consuming skill uses it:**
1. Capture the JSON output into a variable or pipe
2. Parse the structured output to inform test generation
3. Use function signatures to generate accurate test stubs

**When to use this pattern:**
- The consuming skill needs structured data from another skill's script
- The script is stateless (no side effects, deterministic output)
- Spawning a full subagent would be overhead for a single script call

**When NOT to use:**
- The script requires the full skill context (read references, apply workflow)
- The script modifies files (use skill chaining instead)

### Context Management

**Within skill chain (same agent)**:
- Skills share the agent's context window
- State persists between skill invocations
- No manifest needed for internal handoffs

**Across agent boundaries**:
- Use manifest for key_findings only
- Write detailed output to files
- Return minimal response to preserve parent context

---

## Pattern 3: Multi-Level Orchestration

A subagent can itself become an orchestrator, spawning further subagents for complex nested workflows.

### Flow

```
┌─────────────────────┐
│    ORCHESTRATOR     │  Level 0: Main workflow
│   (orchestrator)    │
└─────────┬───────────┘
          │ Task tool
          v
┌─────────────────────┐
│ SUB-ORCHESTRATOR    │  Level 1: Epic decomposition
│ (product-manager)   │
└─────────┬───────────┘
          │ Task tool
          v
┌─────────────────────┐
│    WORKER AGENT     │  Level 2: Task execution
│ (task-executor)     │
└─────────────────────┘
```

### Guidelines for Multi-Level

1. **Depth limit**: SHOULD NOT exceed 3 levels (diminishing returns)
2. **Context budget**: Each level MUST stay under 10K tokens
3. **Manifest propagation**: Each level writes to shared manifest
4. **Response contract**: Each level returns only summary message

### When Multi-Level is Appropriate

| Use Case | Levels | Structure |
|----------|--------|-----------|
| Simple research | 1 | Orchestrator -> Researcher |
| Epic planning | 2 | Orchestrator -> Architect -> Executor |
| Complex pipeline | 3 | Orchestrator -> Coordinator -> Workers |

---

## Context Boundary Rules

For detailed protocol rules, see: @_shared/protocols/subagent-protocol-base.md

**Key principles:**
1. **Manifest for handoffs** - Parent reads only key_findings, not full files
2. **Minimal response** - Return summary message only, not content
3. **File-based details** - Full analysis to output files, summary to manifest
4. **Token injection** - Use `lib/token-inject.sh` for dynamic replacement
5. **Chunked reading** - For files >500 lines, use READ-001 to READ-005 (probe, chunk, target, consolidate)

---

## Anti-Patterns

@_shared/templates/anti-patterns.md#output-anti-patterns

Additional chaining-specific anti-patterns:

| Pattern | Problem | Solution |
|---------|---------|----------|
| Parallel subagent spawning | Race conditions | Sequential spawning only |
| Deep nesting (4+ levels) | Coordination overhead | Flatten to 3 levels max |
| Reading full files at parent | Context explosion | Use manifest key_findings |

---

## Implementation Checklist

@_shared/templates/skill-boilerplate.md#completion-checklist

Additional steps for skill chaining:

Before chaining to another skill:
- [ ] Determine if skill shares context (same agent) or needs delegation
- [ ] For main conversation: Use `Skill(skill="name")` or `/skill-name`
- [ ] For subagent (inline): Read SKILL.md and follow instructions with available tools
- [ ] For subagent (delegated): Use Task tool with SKILL.md content as prompt

---

## Reference Skills

| Skill | Demonstrates |
|-------|--------------|
| `orchestrator` | Single-level spawning via Task tool |
| `technical-writer` | Skill chaining (lookup -> write -> review) |
| `product-manager` | Potential multi-level orchestration |

---

## Skill Chain Contracts

Skills participating in chains MUST follow the contracts defined in `@_shared/protocols/skill-chain-contracts.md`:

| Contract | Description |
|----------|-------------|
| CHAIN-001 to CHAIN-004 | Producer requirements (declare outputs, populate key_findings) |
| CHAIN-005 to CHAIN-008 | Consumer requirements (declare inputs, graceful degradation) |
| CHAIN-009 to CHAIN-011 | Chain relationship requirements (no circular dependencies) |

Skills declare chaining metadata in `manifest.json`:

```json
{
  "chaining": {
    "produces": ["analysis-report", "extraction-plan"],
    "consumes_from": ["codebase-stats"],
    "chains_to": ["refactor-executor"],
    "chains_from": ["codebase-stats"],
    "patterns": ["analyzer-executor"]
  }
}
```

---

## See Also

- @_shared/protocols/skill-chain-contracts.md - Chain contract requirements
- @_shared/references/workflow-patterns.md - Workflow pattern documentation
- @_shared/protocols/subagent-protocol-base.md - Base subagent protocol
- @_shared/protocols/task-system-integration.md - Task system integration
