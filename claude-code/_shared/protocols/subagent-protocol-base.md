# Subagent Protocol Base Reference

This reference defines the RFC 2119 protocol for subagent output and handoff.
All subagents operating under an orchestrator MUST follow this protocol.

> **Canonical output rules**: See `_shared/protocols/output-standard.md` for the
> unified file naming, directory structure, manifest format, and stage receipt
> specification shared across all commands (auto-orchestrate, auto-debug, auto-audit).

---

## Output Requirements (RFC 2119)

### Mandatory Rules

| ID | Rule | Compliance |
|----|------|------------|
| OUT-001 | MUST write findings to `{{OUTPUT_DIR}}/{{DATE}}_{{SLUG}}.md` (see `output-standard.md` NAME-001) | Required |
| OUT-002 | MUST append ONE line to `{{MANIFEST_PATH}}` (session-level, see `output-standard.md` MANIFEST-SESSION) | Required |
| OUT-003 | MUST return ONLY: "Research complete. See MANIFEST.jsonl for summary." | Required |
| OUT-004 | MUST NOT return research content in response | Required |
| OUT-005 | MUST write `stage-receipt.json` to `{{OUTPUT_DIR}}/` on completion (see `output-standard.md` RECEIPT-001) | Required |

### Rationale

- **OUT-001**: Persistent storage for orchestrator and future agents
- **OUT-002**: Manifest enables O(1) lookup of key findings
- **OUT-003**: Minimal response preserves orchestrator context
- **OUT-004**: Full content would bloat orchestrator context window

---

## Output File Format

Write to `{{OUTPUT_DIR}}/{{DATE}}_{{SLUG}}.md`:

```markdown
# {{TITLE}}

## Summary

{{2-3 sentence overview}}

## Findings

### {{Category 1}}

{{Details}}

### {{Category 2}}

{{Details}}

## Recommendations

{{Action items}}

## Sources

{{Citations/references}}

## Linked Tasks

- Epic: {{EPIC_ID}}
- Task: {{TASK_ID}}
```

---

## Manifest Entry Format

Append ONE line (no pretty-printing) to `{{MANIFEST_PATH}}`:

```json
{"id":"{{SLUG}}-{{DATE}}","file":"{{DATE}}_{{SLUG}}.md","title":"{{TITLE}}","date":"{{DATE}}","status":"complete","topics":["topic1","topic2"],"key_findings":["Finding 1","Finding 2","Finding 3"],"actionable":true,"needs_followup":["{{NEXT_TASK_IDS}}"],"linked_tasks":["{{EPIC_ID}}","{{TASK_ID}}"]}
```

### Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier: `{topic-slug}-{date}` |
| `file` | string | Output filename |
| `title` | string | Human-readable title |
| `date` | string | ISO date (YYYY-MM-DD) |
| `status` | enum | `complete`, `partial`, `blocked` |
| `topics` | array | Categorization tags |
| `key_findings` | array | 3-7 one-sentence findings |
| `actionable` | boolean | Whether findings require action |
| `needs_followup` | array | Task IDs requiring attention |
| `linked_tasks` | array | Associated task IDs |

### Key Findings Guidelines

- **3-7 items maximum**
- **One sentence each**
- **Action-oriented language**
- **No implementation details** (those go in the output file)

---

## Task Lifecycle Integration

Reference: @_shared/protocols/task-system-integration.md

**IMPORTANT**: TaskCreate, TaskList, TaskUpdate, and TaskGet are NOT available to subagents. Task management is handled by the auto-orchestrate loop. Subagents receive task context in their spawn prompt and report results in their return value.

### Execution Sequence

```
1. Read task context from spawn prompt (TASK_ID, description, acceptance criteria)
2. Do work:      [skill-specific execution]
3. Write output: {{OUTPUT_DIR}}/{{DATE}}_{{SLUG}}.md
4. Append manifest: {{MANIFEST_PATH}}
5. Return:       "Research complete. See MANIFEST.jsonl for summary."
```

The auto-orchestrate loop handles task status updates (in_progress, completed) based on the subagent's return value.

---

## Completion Checklist

Before returning, verify:

- [ ] Output file written to `{{OUTPUT_DIR}}/`
- [ ] Manifest entry appended (single line, valid JSON)
- [ ] Response is ONLY the summary message
- [ ] Return value indicates completion status (complete, partial, or blocked)

---

## Token Reference

### Required Tokens (MUST be provided)

| Token | Description | Example |
|-------|-------------|---------|
| `{{TASK_ID}}` | Current task identifier | `1` |
| `{{DATE}}` | Current date | `2026-01-19` |
| `{{SLUG}}` | URL-safe topic name | `authentication-research` |

### Optional Tokens (defaults available)

| Token | Default | Description |
|-------|---------|-------------|
| `{{EPIC_ID}}` | `""` | Parent epic ID |
| `{{SESSION_ID}}` | `""` | Session identifier |
| `{{OUTPUT_DIR}}` | `claudedocs/research-outputs` | Output directory |
| `{{MANIFEST_PATH}}` | `{{OUTPUT_DIR}}/MANIFEST.jsonl` | Manifest location |

### Task Tools (Claude Code Native)

**NOTE**: TaskCreate, TaskList, TaskUpdate, and TaskGet are ONLY available to the auto-orchestrate loop (main Claude Code instance). Subagents do NOT have access to these tools. See `claude-code/_shared/references/TOOL-AVAILABILITY.md` for details.

| Action | How Subagents Handle It |
|--------|------------------------|
| Get task context | Provided in spawn prompt by auto-orchestrate |
| Report progress | Include status in return value |
| Propose new tasks | Write to `.orchestrate/<session-id>/proposed-tasks.json` |
| Report completion | Return summary; auto-orchestrate updates status |

---

## Error Handling

### Partial Completion

If work cannot complete fully:

1. Write partial findings to output file
2. Set manifest `"status": "partial"`
3. Add blocking reason to `needs_followup`
4. Complete task (partial work is still progress)
5. Return: "Research partial. See MANIFEST.jsonl for details."

### Blocked Status

If work cannot proceed:

1. Document blocking reason in output file
2. Set manifest `"status": "blocked"`
3. Do NOT complete task
4. Return: "Research blocked. See MANIFEST.jsonl for blocker details."

---

## Early Exit Protocol (Context Budget Safety)

When a subagent approaches its turn limit or context budget, it MUST exit gracefully rather than crash. These rules ensure partial work is preserved and continuable.

### Mandatory Rules

| ID | Rule | Compliance |
|----|------|------------|
| EARLY-001 | **Progress checkpointing** — MUST write partial results to output file after each major phase so work survives termination | Required |
| EARLY-002 | **Graceful completion on turn limit** — when approaching limit, write partial results, set manifest status to `"partial"`, return summary with "PARTIAL: completed X, remaining: Y" | Required |
| EARLY-003 | **Priority ordering under pressure** — when budget is tight, execute in this order: (1) core deliverable, (2) self-review, (3) security audit, (4) quality pipeline. Skip lower-priority items and note them as skipped in output | Required |

### Rationale

- **EARLY-001**: Prevents total loss of work when context or turn limits are hit mid-execution
- **EARLY-002**: Enables the orchestrator to detect partial completions and create continuation tasks for remaining work
- **EARLY-003**: Ensures the most valuable output (working code, primary findings) is always delivered, even if quality gates are skipped

### Partial Result Output Format

When exiting early, the output file MUST include a `## Remaining Work` section:

```markdown
## Remaining Work

- [ ] Item not completed 1
- [ ] Item not completed 2

**Status**: PARTIAL — completed phases 1-3, skipped phases 4-5 (turn limit)
```

### Partial Manifest Entry

When writing a partial manifest entry, use `"status": "partial"` and include remaining work in `needs_followup`:

```json
{"id":"{{SLUG}}-{{DATE}}","file":"{{DATE}}_{{SLUG}}.md","title":"{{TITLE}}","date":"{{DATE}}","status":"partial","topics":["topic1"],"key_findings":["Finding 1"],"actionable":true,"needs_followup":["remaining-task-description"],"linked_tasks":["{{TASK_ID}}"]}
```

### Implementation-Specific Partial Results (Software-Engineer Agent)

When the software-engineer exits early due to context/turn budget exhaustion, the partial result MUST include enough context for a continuation task to resume seamlessly:

**`needs_followup` format for code tasks**:
```json
{
  "needs_followup": [
    "Continue implementation from REMAINING_WORK.md in <working-directory>",
    "Files completed: file1.py, file2.py",
    "Files remaining: file3.py (controller), file4.py (tests)",
    "Partial files: file5.py (50% complete — auth middleware started, permission checks remaining)"
  ]
}
```

**Key requirements**:
- List ALL files already written to disk (the continuation task must not overwrite them)
- List remaining files with brief scope descriptions
- Flag any partially-written files and describe what's done vs. remaining
- Reference `REMAINING_WORK.md` if created by the software-engineer

The orchestrator will pass this information to product-manager, which creates a scoped continuation task. The continuation software-engineer then reads existing files from disk and resumes from where the previous software-engineer stopped.

---

## Large File Reading Protocol (Context Budget Safety)

When a subagent needs to read source files, it MUST follow these rules to avoid exhausting its context window. Naive full reads of large files are the most common cause of context budget blowout.

### Mandatory Rules

| ID | Rule | Compliance |
|----|------|------------|
| READ-001 | **Size-before-read** — before reading any file, use `Read` with `limit: 50` to check total line count from the line-number prefix. If the file exceeds 500 lines, switch to chunked or targeted reading | Required |
| READ-002 | **Chunked reading** — for files >500 lines, read in chunks of 300 lines using `offset` and `limit` parameters. Process each chunk before reading the next | Required |
| READ-003 | **Targeted reading** — when searching for specific content in a large file, use `Grep` first to find line numbers, then `Read` with `offset`/`limit` to read only the relevant region (±30 lines around the match) | Required |
| READ-004 | **Consolidation** — when a task requires understanding a full large file, build a working summary after each chunk rather than holding all chunks in context. Write intermediate summaries to the output file if needed | Required |
| READ-005 | **Multi-file budget** — when a task involves multiple files, estimate total size first. If combined size exceeds 1,500 lines, prioritize files by relevance to the task and apply READ-003 (targeted reading) to lower-priority files | Required |

### Rationale

- **READ-001**: Prevents blind reads that flood the context window with thousands of lines
- **READ-002**: Keeps each read within a manageable size while still covering the full file when needed
- **READ-003**: Most tasks only need specific sections — targeted reads avoid loading irrelevant code
- **READ-004**: Summarizing as you go prevents the accumulation of raw content that defeats the purpose of chunking
- **READ-005**: Multiple large files compound context pressure — budgeting across files prevents cumulative blowout

### Chunked Reading Pseudocode

```
chunked_read(file_path):
  # Step 1: Probe file size
  probe = Read(file_path, limit=50)
  total_lines = extract_last_line_number(probe)

  if total_lines <= 500:
    return Read(file_path)  # normal read

  # Step 2: Read in chunks, consolidate
  summary = ""
  for offset in range(1, total_lines, 300):
    chunk = Read(file_path, offset=offset, limit=300)
    summary = update_summary(summary, chunk)

  return summary
```

### Targeted Reading Pseudocode

```
targeted_read(file_path, search_terms):
  # Step 1: Find relevant line numbers
  matches = Grep(pattern=search_terms, path=file_path, output_mode="content", -n=true)

  # Step 2: Read regions around matches (±30 lines)
  for match in matches:
    line_num = extract_line_number(match)
    region = Read(file_path, offset=max(1, line_num - 30), limit=60)
    process(region)
```

---

## Manifest Size Management (Context Budget Safety)

When the JSONL manifest grows large, reading it in full exhausts the agent's context window. These rules cap manifest reads and trigger rotation.

### Mandatory Rules

| ID | Rule | Compliance |
|----|------|------------|
| MAN-001 | Before reading manifest for `key_findings`, agents MUST read only the **last 50 entries** (use `Read` with `offset` set to skip earlier lines). If manifest exceeds 200 entries, log `[MAN-001] Manifest rotation recommended (>200 entries)` | Required |
| MAN-002 | When orchestrator detects manifest >200 entries at boot, MUST rotate: rename current manifest to `MANIFEST-<DATE>-archived.jsonl`, create a new manifest containing only entries linked to non-completed tasks | Required |

### Rationale

- **MAN-001**: Prevents blind reads of 200+ JSONL lines that flood the context window — most recent entries are the most relevant
- **MAN-002**: Keeps the active manifest small for fast O(1)-style lookups while preserving history in archives

### Manifest Read Pseudocode

```
read_manifest(manifest_path, task_status_map):
  # Step 1: Probe manifest size
  probe = Read(manifest_path, limit=5)
  total_lines = extract_last_line_number(probe)

  if total_lines <= 50:
    return Read(manifest_path)  # normal read

  # Step 2: Read only last 50 entries (MAN-001)
  offset = max(1, total_lines - 50)
  recent = Read(manifest_path, offset=offset, limit=50)

  if total_lines > 200:
    log("[MAN-001] Manifest rotation recommended (>200 entries)")

  return recent
```

### Default Constants

| Constant | Default | Description |
|----------|---------|-------------|
| `MANIFEST_READ_LIMIT` | 50 | Max entries to read from manifest |
| `MANIFEST_ROTATION_THRESHOLD` | 200 | Entry count triggering rotation |

---

## Anti-Patterns

| Pattern | Problem | Solution |
|---------|---------|----------|
| Returning full research | Bloats orchestrator context | Write to file, return summary only |
| Skipping manifest | Orchestrator can't find findings | Always append manifest entry |
| Multi-line manifest | Invalid JSON | Single line, no pretty-print |
| Calling TaskCreate/TaskList/TaskUpdate | These tools are NOT available to subagents | Report status in return value; propose tasks via files |
| Reading entire large file at once | Context window exhaustion | Use READ-001 to detect, READ-002/003 to read in parts |
| Reading multiple large files fully | Compounds context bloat | Use READ-005 multi-file budget, READ-003 targeted reads |
| Holding all chunks in context | Defeats the purpose of chunking | Use READ-004 consolidation — summarize as you go |
| Reading entire oversized manifest | Context exhaustion from 200+ entries | Use MAN-001: read last 50 entries only |
