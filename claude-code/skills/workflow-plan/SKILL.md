---
name: workflow-plan
description: |
  Optimize prompts and manage plan mode with task tracking.
  Use when user says "plan", "create plan", "plan mode", "planning", "design approach".
triggers:
  - plan
  - create plan
  - plan mode
  - planning
  - design approach
  - make a plan
---

# Intelligent Plan Mode Manager

Optimize prompts and manage plan mode with automatic continuity detection and task tracking.

## Step 1: Analyze User Input

Examine the provided task description for:

| Aspect | Questions to Consider |
|--------|----------------------|
| **Clarity** | Is the objective clear and unambiguous? |
| **Scope** | Are boundaries and limitations defined? |
| **Deliverables** | What specific outputs are expected? |
| **Constraints** | Any technical, time, or resource limitations? |
| **Context** | What background information is relevant? |

If the input is vague (e.g., "add auth", "fix bug", "improve performance"), identify what clarifications are needed before proceeding.

## Step 2: Check Existing Plans

Ensure the plans directory exists and scan for recent plans:

```bash
mkdir -p ~/.claude/plans
```

List recent plans:

```bash
ls -lt ~/.claude/plans/*.md 2>/dev/null | head -5
```

If plans exist, read the most recent one to check for continuity.

## Step 3: Check Existing Tasks

Use `TaskList` to see if there are related tasks already tracked.

Look for:
- Tasks with similar subjects
- Tasks in `in_progress` status
- Tasks that might be related to the new plan

## Step 4: Determine Plan Action

Based on analysis, choose one of:

| Action | Condition | Response |
|--------|-----------|----------|
| **Continue** | New task relates to existing plan/task | Resume existing work |
| **New Plan** | Task is unrelated to existing work | Create fresh plan |
| **Merge** | Task extends existing scope | Update existing plan |

### Continuity Detection Criteria

The new task is a **continuation** if it:
- References the same feature/component as existing plan
- Uses terms like "finish", "continue", "next step", "remaining"
- Falls within the scope defined in existing plan

The new task is **new** if it:
- Targets a completely different area of the codebase
- Has no conceptual overlap with recent plans
- Explicitly requests a fresh start

## Step 5: Generate Enhanced Prompt

Transform the user's input into a structured prompt:

---

### Enhanced Prompt

**Objective**: [Clear, specific statement of what needs to be accomplished]

**Context**:
- Current state: [What exists now]
- Background: [Relevant history or constraints]

**Deliverables**:
1. [Specific, measurable output 1]
2. [Specific, measurable output 2]
3. [Additional deliverables as needed]

**Constraints**:
- [Technical constraint]
- [Scope limitation]
- [Compatibility requirement]

**Success Criteria**:
- [ ] [Verifiable criterion 1]
- [ ] [Verifiable criterion 2]
- [ ] [Verifiable criterion 3]

**Out of Scope**:
- [What this plan explicitly does NOT include]

---

## Step 6: Enter Plan Mode

If not already in plan mode, provide this guidance:

> Based on the enhanced prompt above, I recommend entering plan mode to properly design the implementation approach.
>
> **Action**: Use the `EnterPlanMode` tool to begin structured planning.
>
> Plan mode will allow you to:
> - Explore the codebase thoroughly
> - Design an implementation approach
> - Get user approval before coding
> - Avoid wasted effort from misalignment

## Step 7: Create Task Tracking

Link this planning work to the task system for traceability:

1. **Create a task** using `TaskCreate` with:
   - Subject: Brief description of what's being planned
   - Description: Include the enhanced prompt and plan file path
   - ActiveForm: "Planning [feature name]"

2. **Update task status** as planning progresses:
   - Set to `in_progress` when planning begins
   - Set to `completed` when plan is approved

3. **Link to plan file**: Include path `~/.claude/plans/<plan-name>.md` in task description

## Step 8: Delegate to Orchestrator for Implementation

After planning is complete, delegate implementation to the orchestrator agent.

Verify task has been created (from Step 7). If task has not been created yet, go back to Step 7 first.

### Orchestrator Delegation

When conditions are met, spawn the orchestrator:

1. **Use Task tool** with subagent_type: `orchestrator`

2. **Task invocation**:
   ```
   Task(
     description: "Orchestrate implementation of [plan subject]",
     prompt: "
       ## Implementation Context

       TASK_ID: [task ID from Step 7]
       PLAN_FILE: ~/.claude/plans/<plan-name>.md

       ## Instructions

       Execute the implementation plan by:
       1. Read the plan file for full context
       2. Decompose work into subagent tasks
       3. Spawn appropriate subagents per Task Routing table:
          - Research → researcher
          - Implementation → task-executor
          - Documentation → technical-writer
          - Tests → test-writer-pytest
       4. Coordinate sequentially, respecting dependencies
       5. Update task status upon completion

       ## Enhanced Prompt
       [Include the enhanced prompt from Step 5]

       ## Success Criteria
       [Include success criteria from the plan]
     ",
     subagent_type: "orchestrator"
   )
   ```

3. **Report delegation status** — After spawning, output a confirmation message:
   > "Orchestrator agent invoked for task [TASK_ID]: [plan subject]. The orchestrator will coordinate implementation subagents."

   This message MUST be displayed to the user so they can see the handoff occurred.

## Usage Examples

### Example 1: Vague Input Transformation

**Input**: `/workflow-plan add auth`

**Analysis**:
- Missing: Auth method (JWT, OAuth, session?), protected routes, user model
- Scope: Unclear if signup/login/both, password reset, MFA

**Enhanced Prompt**:
```
Objective: Implement user authentication system

Questions to Clarify:
1. What authentication method? (JWT tokens / session cookies / OAuth)
2. Which routes need protection?
3. Does a user model exist or needs creation?
4. Required features: login, signup, logout, password reset, MFA?
```

### Example 2: Continuation Detection

**Input**: `/workflow-plan finish the login feature`

**Detection**: Found existing task #3 "Implement user authentication" with status `in_progress`.

**Action**: Continue existing work, reference remaining items from that task.

### Example 3: Clear New Task

**Input**: `/workflow-plan create REST API endpoints for inventory management`

**Action**: No related existing tasks found. Create new plan with full breakdown.

## Plan File Format

When creating a new plan, save to `~/.claude/plans/<date>-<slug>.md`:

```markdown
# Plan: [Title]

**Created**: [Date]
**Status**: draft | in-progress | approved | completed
**Task ID**: [Link to TaskCreate task]

## Objective
[What this plan accomplishes]

## Background
[Context and current state]

## Approach
[High-level strategy]

## Implementation Steps
1. [ ] Step 1
2. [ ] Step 2
3. [ ] Step 3

## Files to Modify
- `path/to/file1.ts` - [changes]
- `path/to/file2.ts` - [changes]

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| Risk 1 | Mitigation 1 |
```

## Output

After completing all steps, provide:

1. **Enhanced prompt** ready for plan mode
2. **Continuity status** (new plan or continuation)
3. **Recommended action** (enter plan mode / continue existing / clarify first)
4. **Task tracking link** if task was created
5. **Implementation status**:
   - If plan approved: "Delegated to orchestrator for implementation"
   - If in plan mode: "Orchestrator will be spawned after plan approval"
