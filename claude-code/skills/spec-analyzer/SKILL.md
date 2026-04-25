---
name: spec-analyzer
description: >
  Specification analysis, validation, and multi-phase implementation planning.
  Use when user says "specification", "spec analysis", "analyze spec", "validate spec",
  "implementation plan", "phase planning", "requirements extraction", "acceptance criteria",
  "break down into phases", "implementation roadmap".
triggers:
  - specification
  - spec analysis
  - analyze spec
  - validate spec
  - implementation plan
  - phase planning
  - requirements extraction
  - acceptance criteria
  - break down into phases
  - implementation roadmap
---

# Spec Analyzer Skill

Analyzes specifications for completeness, extracts structured requirements, validates implementability, and produces phased implementation plans.

> **Specifications must be complete, unambiguous, and testable before implementation begins.**

## Before You Begin — Load Reference Docs

Read all of the following reference files before proceeding with any workflow step:

- Read `references/spec-patterns.md` — Specification patterns and templates for structured requirements.
- Read `references/phase-patterns.md` — Multi-phase implementation planning patterns and decomposition strategies.
- Read `references/validation-checklist.md` — Validation criteria checklist for specification completeness and quality.

## Parameters

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| `TASK_ID` | Yes | Current task identifier |
| `DATE` | Yes | Current date (YYYY-MM-DD) |
| `SLUG` | Yes | URL-safe topic name |
| `SPEC_PATH` | Yes | Path to specification file |
| `VALIDATION_CRITERIA` | No | Custom validation criteria |
| `EPIC_ID` | No | Parent epic identifier |
| `SESSION_ID` | No | Session identifier |
| `OUTPUT_DIR` | Injected | Output directory |
| `MANIFEST_PATH` | Injected | Path to MANIFEST.jsonl |

---

## Execution Flow

1. Get task → set status `in_progress`
2. Execute spec workflow (analyze, validate, or plan)
3. Write report to `{{OUTPUT_DIR}}/{{DATE}}_{{SLUG}}.md`
4. Append manifest entry → set status `completed`

```
SPEC-ANALYZER ──> SPEC-VALIDATOR ──> IMPLEMENTATION PLANNER
     │                  │                     │
     ▼                  ▼                     ▼
 Extract from      Validate for          Create phased
 docs/specs/       completeness          implementation/
```

---

## Directory Structure

```
project/
├── docs/
│   ├── specs/                # Source specifications
│   └── implementation/       # Generated implementation plans
│       ├── README.md
│       ├── phase-1-foundation.md
│       ├── phase-2-enhancement.md
│       └── phase-3-integration.md
```

---

## Specification Patterns

### Required Sections

| Section | Purpose |
|---------|---------|
| Overview | What and why |
| Problem Statement | What problem this solves |
| Goals | What success looks like |
| Functional Requirements | What the system must do |
| Non-Functional Requirements | How well it must perform |
| Acceptance Criteria | How to verify completion |
| Dependencies | What this relies on |
| Out of Scope | What this does NOT include |

### Requirement Format

```markdown
### Functional Requirements

| ID | Priority | Description |
|----|----------|-------------|
| FR-01 | MUST | System shall allow users to register with email |
| FR-02 | SHOULD | System shall support social login |

### Non-Functional Requirements

| ID | Category | Description |
|----|----------|-------------|
| NFR-01 | Performance | Response time < 200ms p95 |
| NFR-02 | Availability | 99.9% uptime SLA |
```

### Acceptance Criteria Format

Use Given/When/Then:

```markdown
### AC-01: User Registration
**Given** a visitor on the registration page
**When** they submit valid email and password
**Then** account is created and confirmation email sent
```

---

## Phase Planning

Use **vertical slicing** — each phase delivers complete, end-to-end functionality:

```
Phase 1: Basic user registration (email only)
Phase 2: Add social login (Google, GitHub)
Phase 3: Add MFA support
```

### Phase Document Structure

Each phase document should include: overview (status, dates, prerequisites), requirements addressed (FR/NFR IDs), deliverables with acceptance criteria, technical approach (architecture, data model, API changes), ordered implementation tasks, testing strategy, and definition of done checklist.

---

## Validation Checklist

| Severity | Issues |
|----------|--------|
| **Blocking** | Missing acceptance criteria, contradicting requirements, unresolvable dependencies, impossible requirements |
| **Important** | Vague requirements ("fast", "secure"), missing error cases, incomplete data model, missing security requirements |
| **Minor** | Inconsistent terminology, missing diagrams, formatting issues |

---

## Output Format

Write to `{{OUTPUT_DIR}}/{{DATE}}_{{SLUG}}.md`:

1. **Summary** — Spec path, status (`READY`/`NEEDS_WORK`/`BLOCKED`), readiness score (0–100)
2. **Requirements Extracted** — Functional and non-functional tables with ID, priority/category, description
3. **Validation Results** — Table: category, issue count, severity
4. **Recommendations** — Numbered action items
5. **Phase Plan** (if generated) — Table: phase number, focus area, requirement IDs covered
6. **Linked Tasks** — Epic ID, Task ID

---

## Skill Chaining

| Direction | Skills | Pattern |
|-----------|--------|---------|
| Consumes from | `spec-creator`, `researcher` | Spec documents, research findings |
| Produces for | `task-executor` | Phase plans, requirements, validation reports |

Acts as both a sequential pipeline stage (spec-creator → spec-analyzer → task-executor) and a quality gate for spec completeness.

---

## Common Workflows

**Analyze new spec**: Read spec → validate spec structure → extract requirements → identify dependencies → check completeness → score readiness → define phases → create documents

Run spec validation before extracting requirements:

```bash
scripts/spec_validator.py {{SPEC_PATH}}
```

Fix any blocking or important issues reported by the validator before proceeding with analysis.

**Before implementation**: Verify spec exists in `docs/specs/` → validate readiness → create implementation plan if missing → begin Phase 1

**Update spec**: Re-run analysis → re-validate → update implementation plan → note changes in README

---

## Constraints

- Summary message: `"Specification workflow complete. See MANIFEST.jsonl for summary."`
- Partial: `"Specification workflow partial. See MANIFEST.jsonl for details."`
- Blocked: `"Specification workflow blocked. See MANIFEST.jsonl for blocker details."`