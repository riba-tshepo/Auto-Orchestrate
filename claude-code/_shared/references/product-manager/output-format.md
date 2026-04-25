# Epic Output Format — Multi-Phase Planning Pipeline

The product-manager produces output in **4 mandatory phases**. Each phase builds on the previous one. All phases are written to a single output file.

---

## Output File Location

Write to `{{OUTPUT_DIR}}/{{DATE}}_epic-{{FEATURE_SLUG}}.md`

---

## Phase 1: Scope Analysis

Assess what exists, what's missing, and what risks apply before decomposing.

```markdown
# Epic: {{EPIC_TITLE}}

## Scope Analysis

### Current State
- What exists today (code, infrastructure, docs, tests)
- Key files and systems involved

### Target State
- What the completed epic delivers
- Success criteria (measurable outcomes)

### Gap Assessment

| Area | Current | Target | Gap |
|------|---------|--------|-----|
| {{AREA_1}} | {{CURRENT}} | {{TARGET}} | {{GAP}} |
| {{AREA_2}} | {{CURRENT}} | {{TARGET}} | {{GAP}} |

### Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| {{RISK_1}} | high/medium/low | {{MITIGATION}} |
| {{RISK_2}} | high/medium/low | {{MITIGATION}} |

### Out of Scope
- Explicitly excluded items
```

---

## Phase 2: Categorized Task Decomposition

Group tasks by concern area. Each category contains related tasks with full specs.

```markdown
## Task Decomposition

### Overview

| Field | Value |
|-------|-------|
| Epic ID | {{EPIC_ID}} |
| Parent | {{PARENT_ID or "None (root)"}} |
| Priority | {{PRIORITY}} |
| Total Tasks | {{N}} |
| Categories | {{CATEGORY_COUNT}} |

### Category: {{CATEGORY_NAME}}

> {{CATEGORY_PURPOSE}}

| ID | Title | Size | Risk | Depends | dispatch_hint |
|----|-------|------|------|---------|---------------|
| {{T_ID}} | {{TITLE}} | small/medium | low/medium/high | {{DEPS or "-"}} | {{SKILL_NAME}} |

**{{T_ID}}: {{TITLE}}**
- **Description**: {{WHAT_AND_WHY}}
- **Acceptance Criteria**: {{MEASURABLE_OUTCOMES}}
- **Files**: {{AFFECTED_FILES}} (max 3; max 1 for software-engineer)
- **Risk**: {{RISK_LEVEL}} — {{RISK_REASON}}
- **dispatch_hint**: `{{SKILL_NAME}}`

(Repeat for each task in category. Repeat category block for each concern area.)
```

### Standard Category Names

Use generic category names appropriate to the epic:

| Category | When to Use |
|----------|-------------|
| Foundation | Schema, config, infrastructure setup |
| Core Features | Primary functionality implementation |
| Integration | Connecting systems, APIs, adapters |
| Hardening | Security, validation, error handling |
| Testing | Test suites, coverage, regression |
| Deployment | CI/CD, environments, rollout |
| Documentation | Docs, guides, API references |
| Migration | Data migration, cutover, cleanup |

---

## Phase 3: Dependency Graph with Programs

Map all dependencies, assign Programs, identify bottlenecks and parallelization.

```markdown
## Dependency Graph

### Program Table

| Program | Tasks | Depends On | Parallel? |
|---------|-------|------------|-----------|
| 0 | {{T1_ID}} | — | — |
| 1 | {{T2_ID}}, {{T3_ID}} | Program 0 | Yes |
| 2 | {{T4_ID}} | Program 1 | No (convergence) |
| 3 | {{T5_ID}} | Program 2 | No |

### Visual Graph

```
{{T1_ID}}
├── {{T2_ID}}
│   └── {{T4_ID}}
└── {{T3_ID}}
    └── {{T4_ID}}
        └── {{T5_ID}}
```

### Critical Path

{{T1_ID}} → {{T2_ID}} → {{T4_ID}} → {{T5_ID}}

### Bottleneck Analysis

| Bottleneck | Blocks | Impact | Mitigation |
|------------|--------|--------|------------|
| {{TASK_ID}} | {{BLOCKED_TASKS}} | {{DESCRIPTION}} | {{ACTION}} |

### Parallel Opportunities

Tasks within the same Program that touch different files/systems can execute concurrently:
- Program 1: {{T2_ID}} and {{T3_ID}} are independent
```

---

## Phase 4: Quick Reference for Execution

TaskCreate-ready specifications and creation order for the orchestrator.

```markdown
## Quick Reference

### Creation Order

Tasks MUST be created in this order (respects dependency registration):

1. {{T1_ID}}: {{TITLE}} — `dispatch_hint: "{{SKILL}}"` — Program 0
2. {{T2_ID}}: {{TITLE}} — `dispatch_hint: "{{SKILL}}"` — Program 1, blockedBy: [{{T1_ID}}]
3. {{T3_ID}}: {{TITLE}} — `dispatch_hint: "{{SKILL}}"` — Program 1, blockedBy: [{{T1_ID}}]
4. {{T4_ID}}: {{TITLE}} — `dispatch_hint: "{{SKILL}}"` — Program 2, blockedBy: [{{T2_ID}}, {{T3_ID}}]
5. {{T5_ID}}: {{TITLE}} — `dispatch_hint: "{{SKILL}}"` — Program 3, blockedBy: [{{T4_ID}}]

### Ready Tasks (Program 0)

These tasks have no dependencies and can start immediately:
- {{T1_ID}}: {{TITLE}}

### Validation Checklist

- [ ] All tasks have `dispatch_hint` set
- [ ] All tasks have acceptance criteria
- [ ] All tasks fit context budget (≤3 files, ~600 lines; software-engineer: 1 file)
- [ ] No circular dependencies
- [ ] At least one Program 0 task exists
- [ ] Critical path identified
- [ ] Bottlenecks documented with mitigations
- [ ] Risk levels assigned to all tasks
- [ ] Total tasks ≤ 20 per epic
- [ ] LIMIT-001/LIMIT-002 checked before creation

### Session

- Session ID: {{SESSION_ID}}
- Scope: `epic:{{EPIC_ID}}`
- First Ready Task: {{T1_ID}}
```

---

## Manifest Entry Format

Append ONE line (no pretty-printing) to `{{MANIFEST_PATH}}`:

```json
{"id":"epic-{{FEATURE_SLUG}}-{{DATE}}","file":"{{DATE}}_epic-{{FEATURE_SLUG}}.md","title":"Epic Created: {{FEATURE_NAME}}","date":"{{DATE}}","status":"complete","topics":["epic","planning","{{DOMAIN}}"],"key_findings":["Created Epic {{EPIC_ID}} with {{N}} child tasks","Dependency chain: {{T1}} -> {{T2}}/{{T3}} -> {{T4}} -> {{T5}}","Program 0 (parallel start): [{{T1_ID}}]","Program 1 (parallel): [{{T2_ID}}, {{T3_ID}}]","Critical path: {{T1}} -> {{T2}} -> {{T4}} -> {{T5}}","Session started: {{SESSION_ID}}"],"actionable":true,"needs_followup":["{{FIRST_READY_TASK_ID}}"],"linked_tasks":["{{EPIC_ID}}","{{ALL_TASK_IDS}}"]}
```
