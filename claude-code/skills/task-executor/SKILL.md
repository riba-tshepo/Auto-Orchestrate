---
name: task-executor
description: |
  Generic task execution agent for completing implementation work.
  Triggers: "execute task", "implement", "do the work", "complete this task",
  "carry out", "perform task", "build component", "create implementation",
  "execute plan", "finish task".
---

# Task Executor Skill

Complete assigned tasks by following instructions, producing deliverables, and verifying against acceptance criteria.

---

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `{{TASK_ID}}` | Yes | Current task identifier |
| `{{TASK_NAME}}` | Yes | Human-readable task name |
| `{{TASK_INSTRUCTIONS}}` | Yes | Specific execution instructions |
| `{{DELIVERABLES_LIST}}` | Yes | Expected outputs/artifacts |
| `{{ACCEPTANCE_CRITERIA}}` | Yes | Completion verification criteria |
| `{{SLUG}}` | Yes | URL-safe topic name for output |
| `{{DATE}}` | Yes | Current date (YYYY-MM-DD) |
| `{{TOPICS_JSON}}` | Yes | JSON array of categorization tags |
| `{{EPIC_ID}}` | No | Parent epic identifier |
| `{{SESSION_ID}}` | No | Session identifier |
| `{{DEPENDS_LIST}}` | No | Dependencies completed |
| `{{MANIFEST_SUMMARIES}}` | No | Context from previous agents |

---

## Execution Workflow

### 1. Prepare

- Validate task structure and required fields before execution:

```bash
scripts/task_validator.py {{TASK_ID}}
```

Fix any validation errors before proceeding.

- Read task via `{{TASK_SHOW}} {{TASK_ID}}` — understand full context.
- Review `{{MANIFEST_SUMMARIES}}` from upstream agents.
- Identify every item in `{{DELIVERABLES_LIST}}` and every criterion in `{{ACCEPTANCE_CRITERIA}}`.

### 2. Execute

- Follow `{{TASK_INSTRUCTIONS}}` step by step. Don't skip steps.
- Produce each deliverable. Document decisions as you go.
- If blocked, report immediately — don't fail silently.

### 3. Verify & Complete

- Check each acceptance criterion. Record PASS/FAIL with notes.
- Write output file to `{{OUTPUT_DIR}}/{{DATE}}_{{SLUG}}.md`.
- Append manifest entry to `{{MANIFEST_PATH}}`.
- Mark done via `{{TASK_COMPLETE}} {{TASK_ID}}`.
- Return summary message.

---

## Output File Template

Write to `{{OUTPUT_DIR}}/{{DATE}}_{{SLUG}}.md`:

```markdown
# {{TASK_NAME}}

## Summary

{{2-3 sentence overview of what was accomplished}}

## Deliverables

### {{Deliverable 1}}

{{What was created/modified}}

**Files affected:**
- {{file path}}

## Acceptance Criteria Verification

| Criterion | Status | Notes |
|-----------|--------|-------|
| {{Criterion 1}} | PASS/FAIL | {{Details}} |

## Implementation Notes

{{Technical details, decisions made, edge cases handled}}

## Linked Tasks

- Epic: {{EPIC_ID}}
- Task: {{TASK_ID}}
- Dependencies: {{DEPENDS_LIST}}
```

---

## Manifest Entry

Append to `{{MANIFEST_PATH}}` using the standard subagent manifest format.

| Field | Guideline |
|-------|-----------|
| `key_findings` | 3–7 items: deliverables completed, key decisions |
| `actionable` | `false` if complete; `true` if follow-up needed |
| `needs_followup` | Task IDs for dependent work identified during execution |
| `topics` | 2–5 categorization tags matching task labels |

---

## Skill Chaining

| Direction | Skill | Pattern |
|-----------|-------|---------|
| Consumes from | `spec-analyzer` | Phase plans and detailed requirements |
| Produces to | `validator` | Implementation artifacts + report for verification |

**Produces:** implementation artifacts (as specified per task) and a markdown implementation report summarizing changes and files affected.

**Consumes:** `phase-plan` and `requirements` from `spec-analyzer`.

---

## Quality Checklist

Before marking complete, confirm:

- [ ] All deliverables in `{{DELIVERABLES_LIST}}` are produced
- [ ] Every acceptance criterion verified with PASS/FAIL
- [ ] Output file written to `{{OUTPUT_DIR}}`
- [ ] Manifest entry appended
- [ ] Task marked complete
- [ ] No silent failures — blockers reported via manifest status

---

## Anti-Patterns to Avoid

- **Skipping acceptance checks** — verify every criterion before completing.
- **Partial deliverables without reporting** — complete all items or explicitly document what's missing and why.
- **Undocumented changes** — always write the output file; lost context breaks downstream agents.
- **Silent failures** — the orchestrator can't help if it doesn't know. Report via manifest.