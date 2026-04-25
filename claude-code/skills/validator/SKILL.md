---
name: validator
description: |
  Compliance validation agent for verifying systems, documents, and code against
  requirements, schemas, or standards. Triggers: "validate", "verify",
  "check compliance", "audit", "compliance check", "validation report".
---

# Validator Skill

Verify that systems, documents, or code comply with specified requirements, schemas, or standards. Produce a PASS / PARTIAL / FAIL report with remediation guidance.

---

## Parameters

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| `{{VALIDATION_TARGET}}` | Yes | What is being validated | `Schema v2.6.0` |
| `{{TARGET_FILES_OR_SYSTEMS}}` | Yes | Files/paths to check | `schemas/*.json` |
| `{{VALIDATION_CRITERIA}}` | Yes | Checklist of requirements | RFC 2119 compliance items |
| `{{VALIDATION_COMMANDS}}` | No | Specific commands to run | `ajv validate --spec=draft7` |
| `{{SLUG}}` | Yes | URL-safe topic name | `schema-validation` |
| `{{DATE}}` | Yes | Current date (YYYY-MM-DD) | |
| `{{OUTPUT_DIR}}` | Yes | Where to write the report | |

---

## Helper Scripts

| Script | Purpose | Example |
|--------|---------|---------|
| `scripts/schema_validator.py` | Validate JSON/YAML against schemas | `python scripts/schema_validator.py --schema schema.json data.json` |
| `scripts/compliance_checker.py` | Check project conventions | `python scripts/compliance_checker.py --strict .` |

---

## Execution Workflow

1. **Define scope** — identify `{{VALIDATION_TARGET}}` and `{{TARGET_FILES_OR_SYSTEMS}}`.
2. **Identify criteria** — load `{{VALIDATION_CRITERIA}}` and any applicable schemas/standards.
3. **Execute checks** — run automated scripts and manual inspections against every criterion.
4. **Run Docker validation** if applicable (see below).
5. **Document findings** — record each check as PASS/FAIL with details.
6. **Calculate compliance** — compute percentage and assign overall status.
7. **Write report** to `{{OUTPUT_DIR}}/{{DATE}}_{{SLUG}}.md`.
8. **Append manifest** to `{{MANIFEST_PATH}}`.

---

## Status Definitions

| Status | Meaning | Criteria |
|--------|---------|----------|
| **PASS** | Fully compliant | All checks pass, 0 critical issues |
| **PARTIAL** | Mostly compliant | >70% pass, no critical issues |
| **FAIL** | Non-compliant | <70% pass OR any critical issue |

---

## Validation Types

### Schema Validation

Verify data structures against JSON Schema. Check: required fields present, types correct, enum values valid, constraints satisfied.

```python
from lib.layer2.validation import validate_schema, validate_task, validate_config

result = validate_schema(data, schema_path="schemas/todo.schema.json")
is_valid = validate_task(task_dict)
errors = validate_config(config_dict)
```

### Code Compliance

Check: style guide conformance, naming conventions, documentation requirements, security patterns.

### Document Validation

Check: required sections present, frontmatter complete, links valid, format consistent.

### Protocol Compliance

Check: RFC 2119 keywords used correctly, required behaviors implemented, constraints enforced, error handling present.

### Docker Validation

When Docker is available (`docker version` exits 0), invoke `docker-validator` as a **mandatory** sub-step. If Docker is unavailable, skip with a note.

**Delegated phases** (executed by docker-validator): Environment Check → State Audit → Checkpoint → Build & Deploy → UX Testing (unauth + auth) → HTTP Validation → State Restoration.

**Gate rule:** Non-zero errors from docker-validator FAIL the overall validation. Incorporate its error/warning counts into your totals.

**Forward these parameters:** `SESSION_ID`, `TASK_ID`, `DATE`, `SLUG`, `COMPOSE_PATH`, `HEALTHCHECK_ENDPOINT`, `AUTH_ENDPOINT`, `AUTH_CREDENTIALS` (last three from task description if available).

### User Journey Testing

Test complete end-to-end user flows to verify the application works correctly from the end-user perspective. This is **MANDATORY** for Stage 5 validation.

**Test Categories:**

| Category | Description | Example Flows |
|----------|-------------|---------------|
| CRUD Operations | Create, Read, Update, Delete for every entity | Create user → view user → edit user → delete user |
| Authentication | Login, logout, session management, token flows | Register → login → access protected resource → logout |
| Navigation | Page flows, routing, breadcrumbs, back navigation | Home → list → detail → edit → save → back to list |
| Error Handling | Invalid input, missing data, permission denied | Submit empty form → see validation error → fix → submit |
| Edge Cases | Boundary values, concurrent operations, empty states | View empty list → create first item → verify empty state gone |

**Execution:**
- If Docker available: use docker-validator HTTP endpoint testing (Phases 5-6)
- If Docker unavailable: test via API-level calls (curl, scripts) or code-level verification
- Each journey MUST be reported as PASS/FAIL with the specific flow tested
- Advancement is blocked if ANY user journey fails

**Report format:**

```markdown
## User Journey Results

| # | Journey | Flow | Status | Details |
|---|---------|------|--------|---------|
| 1 | User CRUD | Create → Read → Update → Delete | PASS | All operations returned expected status codes |
| 2 | Authentication | Login → Access → Logout | FAIL | Login returns 500 on valid credentials |

Totals: N tested, N passed, N failed
```

### Feature Functionality Testing

Verify that every feature implemented in the current session works correctly. This is **MANDATORY** for Stage 5 validation.

**Process:**
1. Identify all features implemented in the current session (from software-engineer DONE blocks)
2. For each feature, define expected behavior from the end-user perspective
3. Test each feature against its expected behavior
4. Report PASS/FAIL per feature with details

**Report format:**

```markdown
## Feature Functionality Results

| # | Feature | Expected Behavior | Status | Details |
|---|---------|-------------------|--------|---------|
| 1 | User registration | POST /api/users creates user, returns 201 | PASS | |
| 2 | Password reset | POST /api/reset sends email, returns 200 | FAIL | Returns 404 |

Totals: N tested, N passed, N failed
```

**Gate rule:** ALL features must PASS before Stage 5 is marked complete. Failed features trigger the fix-loop protocol (validate→report→fix→revalidate, max 3 iterations per IMPL-009).

---

## Output File Template

Write to `{{OUTPUT_DIR}}/{{DATE}}_{{SLUG}}.md`:

```markdown
# Validation Report: {{VALIDATION_TARGET}}

## Summary

- **Status**: PASS | PARTIAL | FAIL
- **Compliance**: {X}%
- **Critical Issues**: {N}

## Checklist Results

| Check | Status | Details |
|-------|--------|---------|
| {Check} | PASS/FAIL | {Details} |

## Issues Found

### Critical
{List or "None"}

### Warnings
{List or "None"}

### Suggestions
{List or "None"}

## Remediation

{Required fixes if FAIL/PARTIAL, or "No remediation required" if PASS}
```

---

## Manifest Entry

| Field | Guideline |
|-------|-----------|
| `key_findings` | Overall status + %, critical issue count, main findings summary |
| `actionable` | `true` if any issues found |
| `needs_followup` | Remediation task IDs |
| `topics` | `["validation", "compliance", "{{TOPIC}}"]` |

---

## Skill Chaining

The validator is a **terminal quality-gate skill** — it receives work from executor skills and provides the final pass/fail determination.

| Direction | Skills | What flows |
|-----------|--------|------------|
| Consumes from | `task-executor`, `refactor-executor`, `test-writer-pytest`, `hierarchy-unifier`, `error-standardizer`, `security-auditor`, `docker-validator` | Deliverables and artifacts to validate |
| Produces | — (terminal) | Validation report (Markdown) and structured compliance status (JSON) |

---

## Completion Checklist

- [ ] All validation checks executed
- [ ] Each result documented with PASS/FAIL
- [ ] Compliance percentage calculated
- [ ] Critical issues flagged
- [ ] Docker validation run (if Docker available)
- [ ] User journey testing completed (all journeys passed)
- [ ] Feature functionality testing completed (all features passed)
- [ ] Fix-loop iterations recorded (if any)
- [ ] Remediation steps provided (if FAIL/PARTIAL)
- [ ] Report written to `{{OUTPUT_DIR}}`
- [ ] Manifest entry appended