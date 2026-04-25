---
name: debug-diagnostics
description: |
  Structured error diagnosis skill for parsing, categorizing, and collecting
  diagnostic data. Produces structured diagnostic reports and tracks error-fix
  history within debug sessions.
triggers:
  - diagnose
  - error analysis
  - classify error
  - collect diagnostics
  - parse logs
  - error triage
  - debug diagnostics
  - stack trace analysis
---

# Debug Diagnostics Skill

Structured error diagnosis for the debugger agent. Parses errors, categorizes them, collects relevant diagnostic data, and produces actionable reports.

## Helper Scripts

The following scripts in `scripts/` provide automated diagnostic capabilities:

| Script | Purpose | CLI Example |
|--------|---------|-------------|
| `error_classifier.py` | Classify error messages by category and severity | `echo "$ERROR" \| python3 scripts/error_classifier.py` |
| `log_parser.py` | Parse log files into structured JSON by severity | `python3 scripts/log_parser.py --file app.log --level ERROR,WARN` |
| `diagnostic_collector.py` | Collect category-specific diagnostic data with secret redaction | `python3 scripts/diagnostic_collector.py --category docker --root .` |

## Before You Begin

Read `references/error-categories.md` — full error taxonomy with language-specific patterns and decision tree.

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `ERROR_INPUT` | Yes | Raw error message, log output, or stack trace | `ConnectionRefusedError: [Errno 111]...` |
| `DOCKER_MODE` | No | Enable Docker-specific diagnostics | `true` |
| `SESSION_ID` | Yes | Debug session identifier | `auto-dbg-2026-03-24-portfix` |
| `TASK_ID` | Yes | Current task identifier | `5` |
| `DATE` | Yes | Current date (YYYY-MM-DD) | `2026-03-24` |
| `SLUG` | Yes | URL-safe topic name | `connection-refused` |
| `OUTPUT_DIR` | Injected | Output directory | `.debug/<SESSION_ID>/diagnostics/` |
| `MANIFEST_PATH` | Injected | Manifest file path | `.debug/<SESSION_ID>/MANIFEST.jsonl` |

---

## Execution Flow

1. Get task → set status `in_progress`
2. Run Phases 1–5
3. Write report to `{{OUTPUT_DIR}}/{{DATE}}_{{SLUG}}.md`
4. Append manifest entry
5. Set status `completed` → return summary

---

## Phase 1: Parse Error

Extract structured information from raw error input.

**Extract**:
- Error type/class (e.g., `ConnectionRefusedError`, `SyntaxError`, `ENOENT`)
- Error message (human-readable description)
- File path and line number (if present in stack trace)
- Full stack trace (preserve verbatim)
- Exit code (if available)
- Timestamp (if present in log line)

**Helper script** (optional):
```bash
echo "$ERROR_INPUT" | python3 ~/.claude/skills/debug-diagnostics/scripts/error_classifier.py
```

Output: JSON with `category`, `error_type`, `message`, `file`, `line`, `confidence`.

If the script is unavailable, classify manually using the taxonomy in Phase 2.

---

## Phase 2: Categorize

Map the parsed error to one of 8 categories using the error taxonomy.

| Category | Indicators | Priority |
|----------|-----------|----------|
| `syntax` | SyntaxError, parse error, unexpected token, IndentationError | HIGH — blocks execution |
| `runtime` | RuntimeError, TypeError, ValueError, AttributeError, segfault, panic | HIGH — crashes process |
| `configuration` | ConfigError, missing env var, invalid config value, KeyError on config | HIGH — blocks startup |
| `dependency` | ImportError, ModuleNotFoundError, version conflict, resolution failed | HIGH — blocks import |
| `docker` | Container exited, build failed, port conflict, healthcheck failing, OOMKilled | HIGH — blocks deployment |
| `network` | ConnectionRefused, timeout, DNS failure, ECONNRESET, SSL error | MEDIUM — may be transient |
| `database` | OperationalError, connection refused (DB), migration failed, deadlock | HIGH — data path broken |
| `permission` | PermissionError, EACCES, 403 Forbidden, sudo required | MEDIUM — access issue |

**Ambiguous errors**: If an error matches multiple categories, use the **most specific** category. E.g., "ConnectionRefused on port 5432" → `database` (not `network`), because 5432 is PostgreSQL.

**Unknown errors**: If no category matches, classify as `runtime` with `confidence: LOW` and flag for research escalation.

---

## Phase 3: Collect Diagnostics

Gather context relevant to the error category. **Only collect what is relevant** — do not dump everything.

### Universal Diagnostics (all categories)

```bash
# Language/runtime versions
python3 --version 2>&1 || true
node --version 2>&1 || true
go version 2>&1 || true

# Project dependency manifests
cat requirements.txt 2>/dev/null || cat Pipfile 2>/dev/null || true
cat package.json 2>/dev/null | head -30 || true
cat go.mod 2>/dev/null | head -20 || true
```

### Category-Specific Diagnostics

**`syntax`**:
```bash
# Show file content around error line (±5 lines context)
sed -n '$((LINE-5)),$((LINE+5))p' "$ERROR_FILE"
# Check language version compatibility
```

**`runtime`**:
```bash
# Full stack trace (already in ERROR_INPUT)
# Check for core dumps
ls -la /tmp/core* 2>/dev/null || true
# Memory state
free -h 2>/dev/null || true
```

**`configuration`**:
```bash
# Env vars (REDACT secrets — replace values containing key/secret/password/token with "***REDACTED***")
env | grep -iE '(DATABASE|REDIS|API|APP|PORT|HOST|SECRET|KEY|TOKEN|URL)' | sed -E 's/(SECRET|KEY|TOKEN|PASSWORD|PASS)=.*/\1=***REDACTED***/I'
# Config files
find . -maxdepth 2 -name "*.env*" -o -name "*.conf" -o -name "*.cfg" -o -name "*.ini" -o -name "*.toml" -o -name "*.yaml" -o -name "*.yml" | head -20
```

**`dependency`**:
```bash
# Installed packages
pip list 2>/dev/null || npm ls --depth=0 2>/dev/null || true
# Lock file status
ls -la *lock* 2>/dev/null || true
# Virtual environment check
echo "VIRTUAL_ENV=$VIRTUAL_ENV"
```

**`docker`** (requires `DOCKER_MODE: true`):
```bash
# Container state
docker compose ps --format json 2>&1
# Recent logs (last 50 lines per service)
docker compose logs --tail=50 2>&1
# Container inspection (state + networking)
docker compose ps -q | xargs -I{} docker inspect {} --format '{{json .State}}' 2>&1
docker compose ps -q | xargs -I{} docker inspect {} --format '{{json .NetworkSettings.Ports}}' 2>&1
# Health checks
docker compose ps -q | xargs -I{} docker inspect {} --format '{{.Name}}: {{json .State.Health}}' 2>&1
# Resource usage
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.PIDs}}" 2>&1
# Dockerfile and compose file
cat docker-compose.yml 2>/dev/null || cat docker-compose.yaml 2>/dev/null || true
# Port conflicts
ss -tlnp 2>/dev/null | grep -E ':(80|443|3000|5000|5432|6379|8080|8443|27017)' || true
```

**`network`**:
```bash
# DNS resolution
nslookup "$TARGET_HOST" 2>&1 || true
# Port check
timeout 3 bash -c "echo > /dev/tcp/$TARGET_HOST/$TARGET_PORT" 2>&1 && echo "Port open" || echo "Port closed"
# Listening ports
ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null || true
```

**`database`**:
```bash
# DB connection string (REDACTED)
env | grep -iE '(DATABASE_URL|DB_HOST|DB_PORT|DB_NAME|POSTGRES|MYSQL|MONGO|REDIS)' | sed -E 's/(PASSWORD|PASS)=[^&;]*/\1=***REDACTED***/gI'
# Migration status
python3 manage.py showmigrations 2>/dev/null || npx prisma migrate status 2>/dev/null || alembic current 2>/dev/null || true
# DB process check
pg_isready 2>/dev/null || mysqladmin ping 2>/dev/null || true
```

**`permission`**:
```bash
# File permissions on error path
ls -la "$ERROR_FILE" 2>/dev/null || true
stat "$ERROR_FILE" 2>/dev/null || true
# Current user
id
# Process user
ps aux | grep -i "$PROCESS_NAME" | head -5 || true
```

### Log Parsing (all categories)

```bash
# Parse recent logs for errors
python3 ~/.claude/skills/debug-diagnostics/scripts/log_parser.py --file "$LOG_FILE" --level ERROR,WARN,CRITICAL 2>/dev/null || true
```

**IMPORTANT**: Always redact sensitive data before writing to diagnostic reports. Use the patterns:
- Replace values after `PASSWORD=`, `SECRET=`, `TOKEN=`, `KEY=`, `API_KEY=` with `***REDACTED***`
- Replace connection strings containing passwords with redacted versions
- Never log credentials, API keys, or tokens in plain text

---

## Phase 4: Generate Report

Write a structured diagnostic report.

### Report Template

```markdown
# Diagnostic Report: {{SLUG}}

**Session**: {{SESSION_ID}} | **Date**: {{DATE}} | **Iteration**: {{ITERATION}}

## Error Summary

| Field | Value |
|-------|-------|
| **Category** | {{CATEGORY}} |
| **Error Type** | {{ERROR_TYPE}} |
| **Message** | {{ERROR_MESSAGE}} |
| **Location** | {{FILE}}:{{LINE}} |
| **Confidence** | HIGH / MEDIUM / LOW |
| **Docker Mode** | {{DOCKER_MODE}} |

## Raw Error

```
{{ERROR_INPUT verbatim}}
```

## Evidence Collected

### Stack Trace
```
{{STACK_TRACE or "N/A"}}
```

### System State
{{Relevant output from Phase 3 diagnostics}}

### Docker State (if applicable)
{{Container status, logs, health checks}}

### Configuration State
{{Relevant env vars (redacted), config files}}

## Preliminary Analysis

- **Likely root cause**: {{analysis based on evidence}}
- **Confidence**: HIGH / MEDIUM / LOW
- **Related errors**: {{any cascading or related errors found in logs}}

## Recommended Actions

1. {{Most likely fix with specific file/line references}}
2. {{Alternative fix if #1 doesn't work}}
3. {{Research needed if root cause unclear — specific questions to investigate}}

## Research Escalation

{{If confidence is LOW or error is unfamiliar}}
- **Escalate to researcher**: YES / NO
- **Research questions**:
  1. {{specific question about the error}}
  2. {{version compatibility question}}
  3. {{known issue / CVE question}}
```

Output: `{{OUTPUT_DIR}}/{{DATE}}_{{SLUG}}.md`

---

## Phase 5: Track History

Append to the session's error-fix tracking file at `.debug/<SESSION_ID>/error-history.jsonl`:

```json
{
  "timestamp": "<ISO-8601>",
  "iteration": N,
  "error_id": "E-NNN",
  "category": "docker",
  "error_type": "ContainerExited",
  "message": "Container exited with code 1",
  "file": "Dockerfile",
  "line": 15,
  "confidence": "HIGH",
  "status": "diagnosed",
  "diagnostic_report": ".debug/<SESSION_ID>/diagnostics/<DATE>_<SLUG>.md",
  "research_escalation": false
}
```

Update existing entries (by `error_id`) when errors are re-diagnosed after failed fix attempts. Append new entries for new errors discovered during diagnostics.

---

## Manifest Entry

Append to `{{MANIFEST_PATH}}`:

```json
{
  "task_id": "{{TASK_ID}}",
  "skill": "debug-diagnostics",
  "date": "{{DATE}}",
  "slug": "{{SLUG}}",
  "output_file": "{{OUTPUT_DIR}}/{{DATE}}_{{SLUG}}.md",
  "key_findings": [
    "Error categorized as {{CATEGORY}} with {{CONFIDENCE}} confidence",
    "Root cause likely: {{brief root cause}}",
    "{{N}} related errors found in logs",
    "Research escalation: YES/NO"
  ],
  "error_count": N,
  "category": "{{CATEGORY}}",
  "docker_mode": false
}
```

---

## Skill Chaining

| Direction | Skills |
|-----------|--------|
| **Produces** | diagnostic-report, error-classification |
| **Consumes from** | _(first in debug pipeline — no upstream skill)_ |
| **Chains to** | researcher (for research escalation), validator (for verification), docker-validator (for Docker verification) |
| **Chains from** | _(entry point)_ |

---

## Anti-Patterns

| Pattern | Why It's Wrong | Do This Instead |
|---------|---------------|-----------------|
| Guessing root cause without evidence | Wastes fix-verify cycles | Always cite specific log lines or stack trace frames |
| Collecting all diagnostics regardless of category | Noise drowns signal | Only collect category-relevant data |
| Logging secrets in diagnostic reports | Security violation | Always redact PASSWORD, SECRET, TOKEN, KEY values |
| Classifying as "unknown" without attempting classification | Skips useful categorization | Use decision tree, classify as best-fit with LOW confidence |
| Ignoring cascading errors | Fixes symptom not cause | Check logs for earlier errors that triggered the reported one |
| Running Docker commands when `DOCKER_MODE: false` | Unnecessary overhead, may error | Only run Docker diagnostics when explicitly enabled |

---

## Constraints

| ID | Rule |
|----|------|
| DIAG-001 | **Evidence-based** — every finding cites a specific log line, stack frame, or command output |
| DIAG-002 | **Redact secrets** — never write passwords, tokens, API keys, or credentials in plain text to reports |
| DIAG-003 | **Category-focused** — collect only diagnostics relevant to the classified error category |
| DIAG-004 | **Preserve raw input** — include the verbatim error input in every report |
| DIAG-005 | **Track history** — always append to error-history.jsonl, never overwrite |
| DIAG-006 | **Docker gating** — only run Docker commands when `DOCKER_MODE: true` |
