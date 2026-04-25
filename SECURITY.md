# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of Auto-Orchestrate seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Where to Report

**Please DO NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via:

1. **GitHub Security Advisories** (preferred):  
   Navigate to the [Security tab](https://github.com/ribatshepo/Auto-Orchestrate/security/advisories) and click "Report a vulnerability"

2. **Email** (alternative):  
   Contact the maintainer directly through the GitHub profile email

### What to Include

Please include the following information in your report:

- Type of vulnerability (e.g., code execution, privilege escalation, information disclosure)
- Full paths of source file(s) related to the manifestation of the vulnerability
- Location of the affected source code (tag/branch/commit)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if available)
- Impact assessment (what an attacker could do)

### Response Timeline

- **Initial Response**: Within 48 hours of receipt
- **Status Update**: Within 7 days of initial response
- **Fix Timeline**: Depends on severity (critical: 7 days, high: 14 days, medium/low: 30 days)

### Disclosure Policy

- We follow a **coordinated disclosure** process
- Vulnerabilities will not be publicly disclosed until:
  1. A fix is available, OR
  2. 90 days have passed since the initial report (whichever comes first)
- We will credit reporters in release notes unless anonymity is requested

## Security Considerations

### Install Script (`install.sh`)

The install script performs file operations in the user's home directory (`~/.claude/`). Key security properties:

- **Backup Creation**: Automatically backs up existing `~/.claude/` configuration before making changes
- **Permissions**: Preserves file ownership and sets appropriate permissions (644 for files, 755 for directories)
- **Path Safety**: Uses absolute paths resolved from HOME environment variable
- **No Network Access**: Script does not download or execute remote code
- **Idempotent**: Safe to run multiple times

**User Responsibilities**:
- Review the install script before execution
- Ensure `~/.claude/` directory permissions are correct (typically 700 or 755)
- Verify the repository source before cloning

### Python Shared Library (`claude-code/skills/_shared/python/`)

The shared Python library provides utilities for skills. Security properties:

- **Zero External Dependencies**: No pip packages required — uses only Python 3 standard library
- **Layered Architecture**: Strict import hierarchy prevents circular dependencies and minimizes attack surface
- **File Operations**: Uses atomic writes and proper error handling
- **No Network Access**: Library code does not perform network operations
- **Input Validation**: Validation layer (layer2/validation.py) provides input sanitization

**User Responsibilities**:
- Skills execute with the permissions of the Claude Code process
- Ensure Python scripts in `skills/*/scripts/` are reviewed before use
- Do not modify system paths or environment variables in skill scripts

### CI Engine and Domain Memory (`claude-code/lib/`)

The CI engine and domain memory libraries provide continuous improvement analysis and cross-session knowledge persistence. Security properties:

- **Zero External Dependencies**: Uses only Python 3 standard library (OpenTelemetry and Prometheus are optional)
- **Atomic Writes**: All persistent data uses atomic tmp-then-rename with fsync
- **Concurrent Access**: File-level locking via `fcntl.flock()` for safe concurrent writes
- **Schema Validation**: JSON schemas defined for all data files (`lib/ci_engine/schemas/`)
- **No Network Access**: Both systems are local-only (Prometheus export is opt-in)
- **Append-Only Stores**: Domain memory uses JSONL append-only format — no data overwrite or deletion
- **Input Sanitization**: Error fingerprints are normalized (paths/numbers stripped) before storage

### Agent Execution Context

Agents spawned by the orchestrator operate with the same permissions as the Claude Code CLI process. Security boundaries:

- **File Access**: Agents can read/write files the user can access
- **Subprocess Execution**: Agents can spawn subprocesses (e.g., bash, git, pytest)
- **Session Isolation**: Sessions are isolated via checkpoint files scoped by session ID
- **No Privilege Escalation**: Agents do not attempt to escalate privileges

**User Responsibilities**:
- Run Claude Code with appropriate user-level permissions (do not run as root)
- Review auto-orchestrate objectives before granting autonomous mode permission
- Monitor file changes in working directories during autonomous orchestration

### Branch Protection Script (`protect-branches.sh`)

The branch protection script manages GitHub branch protection rules via the `gh` CLI and REST API. Security properties:

- **Minimum gh CLI Version**: Enforces `gh` >= 2.63.0 to mitigate credential leak vulnerability CVE-2024-53858
- **Input Validation**: All branch names, usernames, and repository identifiers are validated against strict regex patterns to prevent command injection
- **No Shell Expansion**: API payloads are constructed via `jq` (not string interpolation), preventing JSON injection
- **Idempotent Operations**: All API calls use upsert semantics (PUT) or check-before-modify patterns, making repeated execution safe
- **Authentication Required**: The script verifies `gh auth status` before making any API calls

**User Responsibilities**:
- Ensure `gh` CLI tokens have appropriate repository admin scopes
- Review branch protection settings after applying them via `./protect-branches.sh status`
- Push restrictions are only available for organization-owned repositories; user-owned repos rely on PR enforcement only

### Known Limitations

1. **GAP-CRIT-001** (Task Tool Availability):  
   The orchestrator agent may not have access to the Task tool in all contexts. When this occurs, the orchestrator uses the PROPOSED_ACTIONS file-based protocol to propose tasks and updates, which the auto-orchestrate loop then executes. The orchestrator does NOT fall back to direct execution — it remains a coordinator only. This is a runtime constraint, not a security vulnerability, but users should be aware that the delegation model uses a file-based fallback in certain permission modes.

2. **No Sandboxing**:  
   Skills and agents execute in the same environment as the Claude Code process. There is no sandboxing or containerization. Malicious skills could potentially perform arbitrary file operations or subprocess execution.

### Debugger Agent (`debugger`)

The debugger agent has Write, Edit, and Bash access and is explicitly designed to modify project files. Additional security considerations:

- **Minimal blast radius (DBG-002)**: Debugger is constrained to fix ONLY the identified broken component — it must not refactor or clean up unrelated code
- **Evidence-first (DBG-001)**: All changes must be traceable to a specific error log, stack trace, or test failure cited in the debug report
- **No auto-commit (DBG-005)**: Debugger outputs suggested commit messages but never executes git commit or git push
- **Audit trail**: All debug reports written to `.debug/<session-id>/reports/` provide a per-change evidence trail

**User Responsibilities**:
- Review `.debug/<session-id>/reports/` after each debug session
- Verify that fix scope matches the error description before accepting changes
- Use `/auto-debug` with specific error descriptions, not vague "fix everything" objectives, to constrain blast radius

## Best Practices

When using Auto-Orchestrate:

1. **Review Code Before Execution**: Always review generated code before running it, especially for security-sensitive tasks
2. **Limit Autonomous Mode Scope**: Use specific, well-defined objectives for `/auto-orchestrate` rather than vague requests
3. **Session Checkpoints**: Regularly review session checkpoint files in `.orchestrate/<session-id>/checkpoint.json` (project-local) to ensure expected behavior. The `~/.claude/sessions/` path is a legacy read-only fallback for sessions started before the path migration; new sessions no longer write there.
4. **File Scope Discipline**: The orchestrator enforces file scope discipline (MAIN-009) — verify that agents only modify files within the task scope
5. **Backup Critical Data**: While the system includes backup mechanisms, maintain independent backups of critical codebases

## Audit Trail

All agent actions are recorded per-session in `.orchestrate/<session-id>/` directories within the project root. The `~/.claude/manifest.json` file serves as the static component registry. Per-session output files include research findings, architecture plans, and execution logs. This provides an audit trail for:

- Agent spawn events
- File modifications
- Task state changes
- Errors and warnings

Review the `.orchestrate/` session directories regularly to monitor autonomous orchestration behavior. Debug session artifacts are stored in `.debug/<session-id>/` and audit artifacts in `.audit/<session-id>/`. The `~/.claude/sessions/` path is a legacy read-only fallback only.

## Contact

For non-security issues, please open a GitHub issue.

For general questions, see the project README and documentation.

**Last Updated**: 2026-03-25
