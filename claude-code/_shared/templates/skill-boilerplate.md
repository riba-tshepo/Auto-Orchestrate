# Skill Boilerplate Templates

This file contains reusable boilerplate sections for skills.
Reference specific sections using anchor links: `@_shared/templates/skill-boilerplate.md#section-name`

---

## Task Integration

### Task System Reference

@_shared/protocols/task-system-integration.md

### Standard Execution Sequence

1. Get task details via `TaskGet`
2. Set focus via `TaskUpdate` (status: in_progress) - skip if orchestrator already set
3. Execute skill-specific work
4. Write output to `{{OUTPUT_DIR}}/{{DATE}}_{{SLUG}}.md`
5. Append manifest entry to `{{MANIFEST_PATH}}`
6. Complete task via `TaskUpdate` (status: completed)
7. Return summary message only

---

## Subagent Protocol

### Protocol Reference

@_shared/protocols/subagent-protocol-base.md

### Output Rules (RFC 2119)

| ID | Rule | Compliance |
|----|------|------------|
| OUT-001 | MUST write output to `{{OUTPUT_DIR}}/{{DATE}}_{{SLUG}}.md` | Required |
| OUT-002 | MUST append ONE line to `{{MANIFEST_PATH}}` | Required |
| OUT-003 | MUST return ONLY the summary message | Required |
| OUT-004 | MUST NOT return full content in response | Required |

### Summary Message Templates

Use the appropriate message for your skill type:

| Skill Type | Summary Message |
|------------|-----------------|
| Research | "Research complete. See MANIFEST.jsonl for summary." |
| Implementation | "Implementation complete. See MANIFEST.jsonl for summary." |
| Specification | "Specification complete. See MANIFEST.jsonl for summary." |
| Validation | "Validation complete. See MANIFEST.jsonl for summary." |
| Testing | "Tests complete. See MANIFEST.jsonl for summary." |
| Security | "Security audit complete. See MANIFEST.jsonl for summary." |
| Task | "Task complete. See MANIFEST.jsonl for summary." |

---

## Manifest Entry

### Format

Append ONE line (no pretty-printing) to `{{MANIFEST_PATH}}`:

```json
{"id":"{{SLUG}}-{{DATE}}","file":"{{DATE}}_{{SLUG}}.md","title":"{{TITLE}}","date":"{{DATE}}","status":"complete","topics":["topic1","topic2"],"key_findings":["Finding 1","Finding 2","Finding 3"],"actionable":true,"needs_followup":["{{NEXT_TASK_IDS}}"],"linked_tasks":["{{EPIC_ID}}","{{TASK_ID}}"]}
```

### Field Guidelines

| Field | Type | Guideline |
|-------|------|-----------|
| `id` | string | Format: `{topic-slug}-{date}` |
| `file` | string | Output filename |
| `title` | string | Human-readable title |
| `date` | string | ISO date (YYYY-MM-DD) |
| `status` | enum | `complete`, `partial`, `blocked` |
| `topics` | array | 2-5 categorization tags |
| `key_findings` | array | 3-7 one-sentence, action-oriented findings |
| `actionable` | boolean | `true` if findings require implementation |
| `needs_followup` | array | Task IDs requiring attention |
| `linked_tasks` | array | Associated epic/task IDs |

---

## Completion Checklist

### Standard Checklist

- [ ] Task focus set via `TaskUpdate` (if not already set)
- [ ] Skill-specific work completed
- [ ] Output file written to `{{OUTPUT_DIR}}/`
- [ ] Manifest entry appended (single line, valid JSON)
- [ ] Task completed via `TaskUpdate` (status: completed)
- [ ] Response is ONLY the summary message

---

## Error Handling

### Partial Completion

When work cannot complete fully:

1. Write partial findings to output file
2. Set manifest `"status": "partial"`
3. Add blocking reason to `needs_followup`
4. Complete task (partial work is still progress)
5. Return: "[Skill type] partial. See MANIFEST.jsonl for details."

### Blocked Status

When work cannot proceed:

1. Document blocking reason in output file
2. Set manifest `"status": "blocked"`
3. Do NOT complete task
4. Return: "[Skill type] blocked. See MANIFEST.jsonl for blocker details."

---

## Token Reference

### Required Tokens

| Token | Description | Example |
|-------|-------------|---------|
| `{{TASK_ID}}` | Current task identifier | `1` |
| `{{DATE}}` | Current date | `2026-01-25` |
| `{{SLUG}}` | URL-safe topic name | `authentication-research` |

### Optional Tokens

| Token | Default | Description |
|-------|---------|-------------|
| `{{EPIC_ID}}` | `""` | Parent epic ID |
| `{{SESSION_ID}}` | `""` | Session identifier |
| `{{OUTPUT_DIR}}` | `claudedocs/research-outputs` | Output directory |
| `{{MANIFEST_PATH}}` | `{{OUTPUT_DIR}}/MANIFEST.jsonl` | Manifest location |

---

## Skill Chaining (Optional)

Include this section when your skill participates in documented workflow patterns.
See `@_shared/protocols/skill-chain-contracts.md` for requirements.

### Produces

List artifact types this skill outputs for downstream skills:

| Output | Format | Description |
|--------|--------|-------------|
| `{{OUTPUT_TYPE}}` | {{FORMAT}} | {{DESCRIPTION}} |

**Example:**
| Output | Format | Description |
|--------|--------|-------------|
| `analysis-report` | Markdown | Code structure analysis with recommendations |
| `extraction-plan` | JSON array | Ordered list of functions to extract |

### Consumes

List inputs this skill can consume from upstream skills:

| Input | From Skill | Description |
|-------|------------|-------------|
| `{{INPUT_TYPE}}` | `{{SOURCE_SKILL}}` | {{DESCRIPTION}} |

**Example:**
| Input | From Skill | Description |
|-------|------------|-------------|
| `metrics` | `codebase-stats` | File complexity and size metrics |
| `hotspots` | `codebase-stats` | High-change-frequency files |

### Chain Relationships

Document workflow pattern participation:

| Direction | Skills | Pattern |
|-----------|--------|---------|
| Chains from | `{{PRECEDING_SKILLS}}` | {{PATTERN_NAME}} |
| Chains to | `{{FOLLOWING_SKILLS}}` | {{PATTERN_NAME}} |

**Example:**
| Direction | Skills | Pattern |
|-----------|--------|---------|
| Chains from | `codebase-stats` | producer-consumer |
| Chains to | `refactor-executor` | analyzer-executor |

### Pattern Reference

See `@_shared/references/workflow-patterns.md` for pattern documentation:
- `analyzer-executor` - Analysis skill identifies work; executor performs it
- `producer-consumer` - One skill produces artifacts consumed by multiple skills
- `sequential-pipeline` - Multi-step workflow with chained transformations
- `quality-gate` - Validation skill gates progression to next phase
