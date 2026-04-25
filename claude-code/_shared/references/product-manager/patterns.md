# Epic Patterns Reference

Detailed patterns for specialized epic types.

---

## Research Epic Pattern

When the work type is classified as research:

### Research Program Structure

| Program | Task Type | Purpose |
|------|-----------|---------|
| Program 0 | Scope Definition | Define research questions, boundaries, success criteria |
| Program 1+ | Investigation (parallel) | Multiple parallel investigation tasks for sources/aspects |
| Final Program | Synthesis | Aggregate findings, create recommendations, link to future work |

### Research Epic Types

| Type | When | Structure |
|------|------|-----------|
| Exploratory | Investigating unknowns | Questions -> Literature + Alternatives + Feasibility -> Synthesis -> Recommendations |
| Decision | Comparing options | Criteria -> Option A + B + C (parallel) -> Matrix -> Recommendation |
| Codebase Analysis | Understanding existing code | Architecture -> Dependencies + Data Flows -> Pain Points -> Improvements |

### Research-Specific Commands

```bash
# Initialize research outputs directory
{{TASK_RESEARCH_INIT}}

# Create research epic with research-specific labels
{{TASK_ADD}} "Research: {{TOPIC}}" \
  --type epic \
  --size medium \
  --labels "research,{{TYPE}},{{DOMAIN}}" \
  --phase core \
  --description "Research questions: ..." \
  --acceptance "Findings documented in research outputs; Recommendations actionable"

# Query prior research before starting
{{TASK_RESEARCH_LIST}} --status complete --topic {{DOMAIN}}
{{TASK_RESEARCH_SHOW}} {{ID}}              # Key findings only
{{TASK_RESEARCH_PENDING}}                  # Incomplete work

# Link research to task after completion
{{TASK_LINK}} {{TASK_ID}} {{RESEARCH_ID}}
```

### Research Task Atomicity

Each research task SHOULD address exactly ONE research question:
- **Good**: "What authentication options exist for SvelteKit?"
- **Bad**: "Research authentication and authorization"

### Research Output Integration

- Subagents write findings to `{{OUTPUT_DIR}}/`
- Subagents append entry to `{{MANIFEST_PATH}}` with `linked_tasks: ["{{TASK_ID}}"]`
- Orchestrator reads only manifest summaries (key_findings) for context efficiency
- Use `{{TASK_RESEARCH_INJECT}}` to get subagent protocol block

### Synthesis vs Investigation Tasks

| Type | Parallel? | Dependencies | Output |
|------|-----------|--------------|--------|
| Investigation | Yes | Scope definition only | Raw findings |
| Synthesis | No | All investigation tasks | Conclusions, recommendations |

---

## Bug Epic Pattern

When work is classified as bug fix:

### Bug Severity to Priority Mapping

| Severity | Priority | Indicators |
|----------|----------|------------|
| Critical | critical | Data loss, security, system down |
| High | high | Core feature broken, workaround difficult |
| Medium | medium | Feature degraded, workaround exists |
| Low | low | Cosmetic, edge case |

### Bug Program Structure

| Program | Task Type | Purpose |
|------|-----------|---------|
| Program 0 | Investigation | Root cause analysis |
| Program 1 | Fix | Implement solution |
| Program 2 | Regression Test | Verify fix, add test coverage |

### Bug-Specific Labels

```bash
{{TASK_ADD}} "Fix: {{BUG_DESCRIPTION}}" \
  --type epic \
  --labels "bug,severity:{{LEVEL}},{{DOMAIN}}" \
  --priority {{MAPPED_PRIORITY}}
```

---

## Brownfield Epic Pattern

When working in existing codebases (refactoring, modernization, migrations):

### Brownfield vs Greenfield Classification

| Indicator | Greenfield | Brownfield |
|-----------|------------|------------|
| Code exists | No | Yes |
| Tests exist | No | May exist |
| Users exist | No | Yes (production impact) |
| Rollback needed | No | Yes (critical) |
| Dependencies | None | Many (existing systems) |

### Brownfield Program 0: Impact Analysis (MANDATORY)

**Every brownfield epic MUST start with impact analysis:**

```bash
# T1: Impact analysis task (Program 0)
{{TASK_ADD}} "Analyze impact and dependencies" \
  --type task \
  --size medium \
  --priority critical \
  --parent {{EPIC_ID}} \
  --phase setup \
  --labels "brownfield,analysis,Program-0" \
  --description "Document all files, functions, and integration points affected. Create dependency graph. Identify external systems." \
  --acceptance "Dependency map documented" \
  --acceptance "All integration points identified" \
  --acceptance "Risk areas flagged"
```

### Brownfield Program 0: Regression Baseline (MANDATORY)

**Create tests BEFORE any modifications:**

```bash
# T2: Regression baseline task (Program 0)
{{TASK_ADD}} "Create regression test baseline" \
  --type task \
  --size medium \
  --priority high \
  --parent {{EPIC_ID}} \
  --phase setup \
  --labels "brownfield,testing,Program-0,regression-risk" \
  --description "Write tests for ALL current behaviors BEFORE changes. These verify no regressions during work." \
  --acceptance "Current behavior fully tested" \
  --acceptance "Edge cases covered" \
  --acceptance "Tests pass against current code"
```

### Brownfield Safety Patterns

| Pattern | Purpose | Implementation |
|---------|---------|----------------|
| **Strangler Fig** | Gradual replacement | New code parallel to legacy, shift traffic gradually |
| **Feature Flags** | Rollback capability | Gate new behavior, instant rollback |
| **Dual-Write** | Data migration safety | Write to both old/new, verify consistency |
| **Shadow Mode** | Risk-free testing | New code runs but doesn't affect users |

### Brownfield-Specific Labels

```bash
--labels "brownfield,refactor,regression-risk"
--labels "brownfield,migration,rollback-checkpoint"
--labels "brownfield,cleanup,tech-debt"
```

### Rollback Checkpoints

Every brownfield epic MUST document rollback at each Program:

```bash
# Rollback documentation task (parallel with implementation)
{{TASK_ADD}} "Document Program N rollback procedure" \
  --type task \
  --size small \
  --priority high \
  --parent {{EPIC_ID}} \
  --labels "brownfield,rollback" \
  --description "Document and test rollback procedure for this Program. Must be tested in staging." \
  --acceptance "Rollback procedure documented" \
  --acceptance "Tested in staging environment"
```

### Brownfield Verification Gates

After brownfield task completion:

```bash
# Regression tests still pass
{{TASK_VERIFY}} {{TASK_ID}} --gate testsPassed

# Cleanup/tech debt addressed
{{TASK_VERIFY}} {{TASK_ID}} --gate cleanupDone

# Security review for auth/data changes
{{TASK_VERIFY}} {{TASK_ID}} --gate securityPassed
```

### Brownfield Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| **Big-bang cutover** | High risk, no rollback | Gradual migration with feature flags |
| **No regression tests** | Can't verify no breakage | Baseline tests before any changes |
| **Undocumented rollback** | Stuck if issues arise | Document rollback at each phase |
| **Modifying and testing together** | Tests may pass broken code | Tests first, then modifications |

**See [examples.md#refactor-epic-example](examples.md#refactor-epic-example) for complete brownfield refactoring example.**

---

## Refactor Epic Pattern

For code modernization, architectural improvements, and tech debt reduction:

### Refactor Program Structure

| Program | Task Type | Purpose |
|------|-----------|---------|
| Program 0 | Impact Analysis + Regression Baseline | Understand scope, create safety net |
| Program 1 | New Implementation (parallel) | Build new code alongside legacy |
| Program 2 | Adapter/Integration | Create bridge between old and new |
| Program 3 | Gradual Migration | Shift traffic/users incrementally |
| Program 4 | Validation + Cleanup | Verify migration, remove legacy |

### Refactor Safety Rules

1. **Never modify existing code in Program 0** - Analysis only
2. **New code is ADDITIVE in Program 1** - Don't touch legacy yet
3. **Feature flags control all behavior changes** - Instant rollback
4. **Test rollback at every phase** - Before production deployment
5. **Remove legacy code LAST** - Only after validation complete

### Refactor-Specific Commands

```bash
# Create refactor epic with lifecycle tracking
{{TASK_ADD}} "EPIC: Refactor {{COMPONENT}}" \
  --type epic \
  --size large \
  --priority high \
  --epic-lifecycle planning \
  --labels "refactor,brownfield,{{DOMAIN}}" \
  --description "Modernize {{COMPONENT}}. Strangler fig pattern with feature flags." \
  --acceptance "New implementation complete" \
  --acceptance "All users migrated" \
  --acceptance "Legacy code removed" \
  --acceptance "Rollback tested at each phase"
```

**See [examples.md#refactor-epic-example](examples.md#refactor-epic-example) for complete example.**

---

## Task Naming Conventions

### Pattern: "{Verb} {Object} {Qualifier}"

**Good:**
- "Create user authentication schema"
- "Implement JWT validation middleware"
- "Write integration tests for auth flow"
- "Add error handling to API endpoints"

**Bad:**
- "Auth stuff"
- "Part 1"
- "Fix things"
- "TODO"

### Numbered Sequences

For clearly sequential work:
- "1. Define data model"
- "2. Create API endpoints"
- "3. Build UI components"
- "4. Add integration tests"

---

## Orchestrator Integration

### When to Invoke product-manager

| Trigger | Example Request |
|---------|-----------------|
| Epic creation | "Create an epic for user authentication" |
| Task decomposition | "Break down this project into tasks" |
| Program analysis | "What can run in parallel?" |
| Sprint planning | "Plan the sprint backlog" |

### How to Invoke

```
# Via Skill tool
Skill(skill="product-manager")

# Via slash command
/product-manager
```

### Subagent Skill Specification

Skills are session-scoped - subagents don't automatically get parent skills.

| Scenario | Should Have Skill? | Rationale |
|----------|-------------------|-----------|
| Coder implementing a task | No | Coders execute, not plan |
| Researcher gathering info | No | Researchers investigate, not plan |
| Nested orchestrator | Yes | Needs planning capability |

### Output Protocol

When product-manager creates an epic:

1. Write output file: `{{OUTPUT_DIR}}/{{DATE}}_epic-{{FEATURE_SLUG}}.md`
2. Append manifest entry to `{{MANIFEST_PATH}}`
3. Return summary only: "Epic created. See MANIFEST.jsonl for summary."

---

## Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Giving all subagents product-manager | Context bloat | Only nested orchestrators need it |
| Returning full epic details | Bloats orchestrator context | Return manifest summary only |
| Skipping research check | Duplicate work | Query existing research first |
| Parallel epic creation | Task conflicts | Create epics sequentially |

---

## Categorized Decomposition Pattern

When decomposing an epic, group tasks by concern area rather than listing them flat.

### When to Apply

Every epic with 5+ tasks SHOULD use categorized decomposition. Smaller epics MAY use it for clarity.

### Category Selection

Choose categories based on the epic's domain. Common groupings:

| Domain | Typical Categories |
|--------|--------------------|
| Feature | Foundation, Core Features, Integration, Testing |
| Infrastructure | Setup, Configuration, Hardening, Deployment |
| Migration | Analysis, Data Migration, Cutover, Validation |
| Bug fix | Investigation, Fix, Regression Testing |

### Category Block Structure

Each category contains:
1. Category name and purpose (one-line summary)
2. Summary table of tasks in the category
3. Detailed spec for each task (description, acceptance criteria, files, risk, dispatch_hint)

### Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| One task per category | No grouping benefit | Merge into adjacent category |
| Overlapping categories | Confusing ownership | Each task belongs to exactly one category |
| Category without purpose | Adds noise | Every category needs a one-line justification |

---

## Risk Classification Pattern

Assign a risk level to every task during decomposition.

### Risk Levels

| Level | Criteria | Action |
|-------|----------|--------|
| **high** | Touches auth, data, external APIs, shared state; scope unclear | Add mitigation to bottleneck analysis; consider splitting |
| **medium** | Moderate coupling, existing test coverage gaps | Note in task spec; flag for review |
| **low** | Isolated change, good test coverage, well-understood | Standard execution |

### Risk Indicators

| Indicator | Suggests |
|-----------|----------|
| Multiple system boundaries crossed | high |
| No existing test coverage | medium-high |
| Affects user-facing behavior | medium |
| Isolated internal change | low |
| Well-documented existing code | low |

---

## Bottleneck Identification Pattern

Identify tasks that block the most downstream work and document mitigations.

### Detection

A task is a bottleneck when:
- It appears in `blockedBy` of 3+ other tasks
- It is on the critical path AND has no parallel alternative
- It requires external input or review

### Documentation

For each bottleneck, record:

| Field | Content |
|-------|---------|
| Task ID | The blocking task |
| Blocks | List of downstream tasks |
| Impact | What happens if delayed |
| Mitigation | How to reduce risk (split, parallelize, pre-work) |

### Mitigation Strategies

| Strategy | When |
|----------|------|
| Split the bottleneck task | Task is too broad |
| Pre-work in earlier Program | Some subtasks can start sooner |
| Provide stub/interface first | Downstream only needs contract, not implementation |
| Assign to dedicated agent | Prioritize throughput on bottleneck |

---

## Pre-Creation Validation Pattern

Before creating any TaskCreate calls, validate the full plan.

### Validation Steps

1. **Dependency check**: No circular references; every `blockedBy` target exists
2. **Program 0 check**: At least one task has no dependencies
3. **Context budget check**: Every task ≤ 3 files, ~600 lines (software-engineer: 1 file)
4. **dispatch_hint check**: Every task has a `dispatch_hint` set
5. **Acceptance criteria check**: Every task has measurable acceptance criteria
6. **Risk check**: Every task has a risk level assigned
7. **Cap check**: Total tasks ≤ 20; system-wide LIMIT-001/LIMIT-002 respected
8. **Bottleneck check**: All tasks blocking 3+ others are documented

### On Failure

| Failure | Recovery |
|---------|----------|
| Circular dependency | Break cycle with intermediate task |
| No Program 0 tasks | Re-examine deps; at least one task must be unblocked |
| Task too large | Split per Context-Safe Task Sizing rules |
| Missing dispatch_hint | Assign based on Skill Routing table |
| Over task cap | Consolidate remaining work into fewer tasks |

---

## Dispatch Hint Pattern

Every task MUST include a `dispatch_hint` field indicating which skill should execute it.

### Required Format

```
dispatch_hint: "{{skill_name}}"
```

### Routing Table

| Task Type | dispatch_hint | When |
|-----------|---------------|------|
| Implementation | `task-executor` | Build, create, implement code |
| Research | `researcher` | Investigate, explore, gather info |
| Specifications | `spec-creator` | Write specs, define protocols |
| Python tests | `test-writer-pytest` | Write pytest test suites |
| Python libraries | `library-implementer-python` | Create Python modules |
| Validation | `validator` | Verify, audit, check compliance |
| Documentation | `docs-write` | Write or update documentation |
| Security audit | `security-auditor` | Security vulnerability scanning |

### Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Missing dispatch_hint | Orchestrator guesses wrong skill | Always set explicitly |
| Generic "software-engineer" for everything | Misses specialized skills | Match task type to skill |
| dispatch_hint on epic | Epics aren't dispatched | Only set on leaf tasks |

---

## See Also

- @_shared/references/product-manager/examples.md - Detailed epic examples
- @_shared/protocols/subagent-protocol-base.md - Output protocol
- @_shared/protocols/task-system-integration.md - Task tools
