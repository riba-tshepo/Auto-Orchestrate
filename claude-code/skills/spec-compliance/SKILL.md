---
name: spec-compliance
description: |
  Requirement-to-implementation mapping and compliance scoring. Parses spec
  documents, builds a requirements matrix, scans the codebase for implementation
  evidence, checks Docker services, and produces compliance reports with gap analysis.
triggers:
  - spec compliance
  - requirements mapping
  - compliance check
  - implementation coverage
  - spec vs code
  - requirement audit
  - compliance matrix
  - gap analysis
  - spec gap
---

# Spec Compliance Skill

Maps spec/requirements documents to actual codebase implementations. Produces a structured compliance matrix and gap report that drives the audit-remediate loop.

## Before You Begin

Read `references/compliance-patterns.md` — framework-specific patterns for matching requirements to code implementations.

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `SPEC_PATH` | Yes | Path to spec/requirements document | `docs/spec.md` |
| `PROJECT_ROOT` | Yes | Root of the project to audit | `.` |
| `DOCKER_MODE` | No | Enable Docker service compliance checking | `true` |
| `COMPOSE_PATH` | No | Path to docker-compose.yml (auto-detected if omitted) | `./docker-compose.yml` |
| `COMPLIANCE_THRESHOLD` | No | Minimum compliance % for PASS verdict (default 90) | `90` |
| `SESSION_ID` | Yes | Audit session identifier | `auto-aud-2026-03-25-specaudit` |
| `TASK_ID` | Yes | Current task identifier | `5` |
| `DATE` | Yes | Current date (YYYY-MM-DD) | `2026-03-25` |
| `SLUG` | Yes | URL-safe topic name | `spec-compliance` |
| `OUTPUT_DIR` | Injected | Output directory | `.audit/<SESSION_ID>/` |
| `MANIFEST_PATH` | Injected | Manifest file path | `.audit/<SESSION_ID>/MANIFEST.jsonl` |

---

## Execution Flow

1. Get task → set status `in_progress`
2. Run Phases 1–6
3. Write compliance report to `{{OUTPUT_DIR}}/{{DATE}}_{{SLUG}}.md`
4. Write gap report to `{{OUTPUT_DIR}}/gap-report.json`
5. Append manifest entry
6. Set status `completed` → return summary

---

## Phase 1: Parse Spec Document

Extract structured requirements from the spec file.

**Helper script** (recommended):
```bash
python3 ~/.claude/skills/spec-compliance/scripts/spec_parser.py --file "$SPEC_PATH"
```

Output: JSON with requirements array.

**If script unavailable**, manually parse:
1. Read the spec document
2. Identify requirements by:
   - Tables with ID/Priority/Description columns
   - Headings with "Requirements", "Features", "User Stories"
   - Imperative statements: "must", "shall", "should", "will"
   - Acceptance criteria blocks (Given/When/Then)
3. Assign REQ-IDs (REQ-001, REQ-002, ...) if spec lacks explicit IDs
4. Extract keywords from each requirement for codebase matching
5. Classify as: `functional`, `non-functional`, `service`, `security`

**Requirement structure**:
```json
{
  "id": "REQ-001",
  "source": "spec.md:L12",
  "type": "functional",
  "priority": "MUST",
  "description": "User authentication via JWT tokens",
  "acceptance_criteria": "Given valid credentials, When POST /api/auth/login, Then receive JWT token",
  "keywords": ["jwt", "auth", "login", "token", "authentication"]
}
```

---

## Phase 2: Build Requirements Matrix

Create a tracking matrix with all extracted requirements:

| REQ-ID | Source | Type | Priority | Description | Status | Evidence | Details |
|--------|--------|------|----------|-------------|--------|----------|---------|
| REQ-001 | spec.md:L12 | functional | MUST | JWT auth | pending | — | — |

Initialize all requirements with `status: "pending"`.

---

## Phase 3: Scan Codebase for Implementation Evidence

For each requirement, search the codebase for implementation evidence.

**Helper script** (recommended):
```bash
python3 ~/.claude/skills/spec-compliance/scripts/compliance_checker.py \
  --requirements requirements.json \
  --root "$PROJECT_ROOT"
```

**If script unavailable**, manually check each requirement:

### Evidence Collection Strategy

1. **Keyword search**: Grep the project for requirement keywords
   ```bash
   grep -rl "jwt\|auth\|login\|token" --include="*.py" --include="*.js" --include="*.ts" "$PROJECT_ROOT" | head -20
   ```

2. **File pattern matching**: Look for files matching requirement concepts
   ```bash
   find "$PROJECT_ROOT" -name "*auth*" -o -name "*login*" -o -name "*jwt*" | grep -v node_modules | grep -v __pycache__
   ```

3. **Route/endpoint discovery**: Check for API endpoints matching requirements
   ```bash
   grep -rn "route\|router\|@app\.\|@api\.\|path(" --include="*.py" --include="*.js" --include="*.ts" "$PROJECT_ROOT" | head -30
   ```

4. **Test evidence**: Check for tests covering the requirement
   ```bash
   grep -rl "test.*auth\|auth.*test\|login.*test\|test.*login" "$PROJECT_ROOT/tests" 2>/dev/null | head -10
   ```

5. **Model/schema evidence**: Check for data models
   ```bash
   grep -rn "class.*Model\|class.*Schema\|CREATE TABLE\|model\." --include="*.py" --include="*.js" --include="*.sql" "$PROJECT_ROOT" | head -20
   ```

### Status Assignment Rules

| Status | Criteria |
|--------|----------|
| **PASS** | Implementation files found AND functional (imports resolve, routes exist) AND tests found |
| **PARTIAL** | Some implementation found but incomplete — e.g., model exists but no controller/route, or code exists but no tests |
| **MISSING** | Zero implementation evidence — no files, functions, or routes match requirement keywords |
| **FAIL** | Implementation exists but is broken — import errors, syntax issues, placeholder/TODO code, or Docker service unhealthy |
| **SKIPPED** | Requirement explicitly excluded from current scope (e.g., frontend req when scope=backend) |

### Evidence Documentation

For each requirement, record:
- **Files found**: list of file paths with relevant code
- **Functions/classes**: specific functions or classes implementing the requirement
- **Routes/endpoints**: API routes matching the requirement
- **Tests**: test files covering the requirement
- **Issues**: any problems found (TODOs, placeholders, broken imports)

---

## Phase 4: Docker Service Discovery (DOCKER_MODE only)

Skip this phase entirely if `DOCKER_MODE` is not `true`.

**Helper script** (recommended):
```bash
python3 ~/.claude/skills/spec-compliance/scripts/service_discovery.py \
  --compose "$COMPOSE_PATH" \
  --root "$PROJECT_ROOT"
```

**If script unavailable**, manually check:

1. **Parse compose file**:
   ```bash
   cat docker-compose.yml 2>/dev/null || cat docker-compose.yaml 2>/dev/null || cat compose.yml 2>/dev/null
   ```

2. **Extract services**: name, image, ports, healthcheck, depends_on

3. **Check running containers**:
   ```bash
   docker compose ps --format json 2>&1
   ```

4. **Check health**:
   ```bash
   docker compose ps -q | xargs -I{} docker inspect {} --format '{{.Name}}: {{json .State.Health}}' 2>&1
   ```

5. **Test port connectivity**:
   ```bash
   # For each exposed port
   timeout 3 bash -c "echo > /dev/tcp/localhost/$PORT" 2>&1 && echo "Port $PORT: open" || echo "Port $PORT: closed"
   ```

6. **HTTP health checks** (for web services on ports 80, 443, 3000-9999):
   ```bash
   curl -sf -o /dev/null -w "%{http_code}" "http://localhost:$PORT/health" 2>/dev/null || echo "no-response"
   ```

**Service status assignment**:
- **PASS**: Container running, healthy (if healthcheck defined), port accessible
- **PARTIAL**: Container running but unhealthy, or port not responding
- **FAIL**: Container exited, not running, or not defined in compose
- **MISSING**: Spec requires service but no compose definition found

Add service findings as SVC-NNN entries to the compliance matrix.

---

## Phase 5: Score Compliance

Calculate overall compliance score:

```
compliance_score = (PASS_count + PARTIAL_count * 0.5) / total_requirements * 100
```

Determine verdict:

| Score | Verdict |
|-------|---------|
| 100% | `PASS` — all requirements fully implemented |
| ≥ threshold | `ACCEPTABLE` — meets minimum compliance |
| < threshold | `FAIL` — below minimum compliance |

---

## Phase 6: Write Reports

### Compliance Report (`{{OUTPUT_DIR}}/{{DATE}}_{{SLUG}}.md`)

```markdown
# Compliance Report: {{SLUG}}

**Session**: {{SESSION_ID}} | **Date**: {{DATE}} | **Spec**: {{SPEC_PATH}}
**Compliance Score**: {{SCORE}}% | **Verdict**: {{VERDICT}}

## Summary

| Status | Count | % |
|--------|-------|---|
| PASS | {{N}} | {{%}} |
| PARTIAL | {{N}} | {{%}} |
| MISSING | {{N}} | {{%}} |
| FAIL | {{N}} | {{%}} |
| SKIPPED | {{N}} | {{%}} |

## Requirements Matrix

| REQ-ID | Priority | Description | Status | Evidence |
|--------|----------|-------------|--------|----------|
| REQ-001 | MUST | JWT authentication | PASS | src/auth/jwt.py, tests/test_auth.py |
| REQ-002 | MUST | Rate limiting | MISSING | No implementation found |

## Docker Services (if applicable)

| SVC-ID | Service | Status | Health | Port | Details |
|--------|---------|--------|--------|------|---------|
| SVC-001 | postgres | PASS | healthy | 5432 | Running, responsive |
| SVC-002 | redis | FAIL | unhealthy | 6379 | ECONNREFUSED |

## Gaps Requiring Remediation

### MISSING Requirements
{{For each MISSING requirement: full description, spec source, what needs to be built}}

### PARTIAL Requirements
{{For each PARTIAL requirement: what exists, what's missing, specific gaps}}

### FAIL Requirements
{{For each FAIL requirement: what's broken, error details, what needs fixing}}

### Unhealthy Services
{{For each unhealthy service: current state, error details, remediation needed}}
```

### Gap Report (`{{OUTPUT_DIR}}/gap-report.json`)

```json
{
  "session_id": "{{SESSION_ID}}",
  "date": "{{DATE}}",
  "spec_path": "{{SPEC_PATH}}",
  "compliance_score": 67.5,
  "verdict": "FAIL",
  "threshold": 90,
  "total_requirements": 20,
  "summary": {
    "pass": 12,
    "partial": 3,
    "missing": 4,
    "fail": 1,
    "skipped": 0
  },
  "gaps": [
    {
      "id": "REQ-002",
      "source": "spec.md:L25",
      "type": "functional",
      "priority": "MUST",
      "status": "MISSING",
      "description": "Rate limiting on all API endpoints",
      "evidence": "No files matching rate_limit, throttle, or rate patterns found",
      "remediation": "Implement rate limiting middleware for all API routes"
    },
    {
      "id": "SVC-002",
      "source": "docker-compose.yml",
      "type": "service",
      "priority": "MUST",
      "status": "FAIL",
      "description": "Redis service",
      "evidence": "Container running but port 6379 refuses connections",
      "remediation": "Fix Redis configuration — check bind address and protected-mode settings"
    }
  ],
  "services": {
    "total": 4,
    "healthy": 3,
    "unhealthy": 1,
    "details": []
  }
}
```

---

## Manifest Entry

Append to `{{MANIFEST_PATH}}`:

```json
{
  "task_id": "{{TASK_ID}}",
  "skill": "spec-compliance",
  "date": "{{DATE}}",
  "slug": "{{SLUG}}",
  "output_file": "{{OUTPUT_DIR}}/{{DATE}}_{{SLUG}}.md",
  "key_findings": [
    "Compliance score: {{SCORE}}% ({{VERDICT}})",
    "{{PASS_count}}/{{TOTAL}} requirements fully implemented",
    "{{GAP_count}} gaps requiring remediation",
    "Docker services: {{HEALTHY}}/{{TOTAL_SVC}} healthy"
  ],
  "compliance_score": 67.5,
  "verdict": "FAIL",
  "gap_count": 5,
  "docker_mode": true
}
```

---

## Skill Chaining

| Direction | Skills |
|-----------|--------|
| **Produces** | compliance-matrix, gap-report |
| **Consumes from** | `spec-analyzer` (validated specs), `spec-creator` (spec documents) |
| **Chains to** | `auditor` agent (compliance decisions), `orchestrator` (remediation via gap report) |
| **Chains from** | `spec-analyzer` (upstream validation) |

---

## Anti-Patterns

| Pattern | Why It's Wrong | Do This Instead |
|---------|---------------|-----------------|
| Marking requirements as PASS without evidence | False compliance, undetected gaps | Always cite specific files, functions, or test paths |
| Running Docker commands when DOCKER_MODE=false | Unnecessary overhead, may error | Gate ALL Docker operations on DOCKER_MODE flag |
| Summarizing or filtering the gap report | Downstream agents need complete info | Write ALL gaps verbatim to gap-report.json |
| Searching only file names, not content | Misses implementations in generically named files | Search both file names AND file content for keywords |
| Ignoring test evidence | Partial implementations look complete without test coverage check | Always check for tests alongside implementation |
| Marking TODO/placeholder code as PASS | Inflates compliance score | Code with TODO/FIXME/HACK/placeholder = PARTIAL at best |

---

## Constraints

| ID | Rule |
|----|------|
| SPEC-COMP-001 | **Evidence-based** — every status assignment cites specific file paths, line numbers, or command outputs |
| SPEC-COMP-002 | **Spec-first** — always parse the spec before scanning the codebase. Requirements drive the audit. |
| SPEC-COMP-003 | **Complete coverage** — every requirement in the spec gets a status. No requirement is silently skipped. |
| SPEC-COMP-004 | **Secret redaction** — never include passwords, tokens, API keys, or credentials in reports |
| SPEC-COMP-005 | **Docker gating** — only run Docker commands when `DOCKER_MODE: true` |
| SPEC-COMP-006 | **Structured output** — always produce both human-readable report AND machine-readable gap-report.json |
