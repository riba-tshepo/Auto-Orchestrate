# Agent Activation Protocol

**Version**: 1.0
**Date**: 2026-04-14
**Status**: Active

---

## Purpose

The Agent Activation Protocol enables the orchestrator to conditionally spawn domain-expert agents (qa-engineer, security-engineer, sre, infra-engineer, data-engineer, ml-engineer) for single-stage review participation during autonomous pipeline execution. Without this protocol, these 6 agents are confined to manual domain commands (`/qa`, `/security`, `/infra`, `/data-ml-ops`) and are never invoked by the Big Three autonomous loops — even when processes P-032 to P-057 require their expertise.

This protocol is **complementary** to the Command Dispatch Protocol. Command dispatch invokes domain guide **Skills** (Tier 2, inline text analysis) via the loop controller. Agent activation spawns domain **agents** (subagents with tool access) via the orchestrator. Dispatch provides high-level findings; activation provides detailed, code-level review.

```
auto-orchestrate loop controller
  ├── Command Dispatcher (Step 4.8c) → Skill() for domain guides  [DISPATCH-GUARD-001]
  └── Orchestrator spawn
        └── Agent Activation (this protocol) → Agent() for domain reviews  [AGENT-ACTIVATE-001]
```

---

## Constraints

| ID | Rule |
|----|------|
| AGENT-ACTIVATE-001 | **Stage-transition evaluation** — The orchestrator evaluates domain-activation rules at each stage transition. If a domain agent's trigger condition is met, that agent is spawned for the current stage only. The agent produces a review artifact and exits. |
| AGENT-ACTIVATE-002 | **Single-stage participation** — Domain agents activated conditionally do NOT persist across stages. They are single-stage participants, not permanent pipeline members. Each activation is scoped to one stage's artifacts. |
| AGENT-ACTIVATE-003 | **Budget-exempt spawns** — Domain agent spawns do NOT decrement `REMAINING_BUDGET`. They are exempt from budget accounting, following the same exemption pattern as Stages 5 and 6. This ensures domain reviews never crowd out core pipeline work. |
| AGENT-ACTIVATE-004 | **Review-only output** — Domain agents produce review artifacts (findings, recommendations, severity counts). They do NOT produce `proposed-tasks.json` entries, do NOT modify `PROPOSED_ACTIONS`, and do NOT create tasks. Their output is advisory input for subsequent stages. |
| AGENT-ACTIVATE-005 | **Activation cap** — Maximum 2 domain agent activations per orchestrator spawn. This prevents runaway activation when multiple conditions match simultaneously. If more than 2 rules match, prioritize by severity (CRITICAL > HIGH > MEDIUM) then by rule ID (lower first). |

---

## Activation Rules Table

| Rule ID | Trigger Stage | Condition | Agent | Review Scope | Processes |
|---------|--------------|-----------|-------|-------------|-----------|
| ACT-001 | 2 | Stage 2 spec contains API contracts, endpoint definitions, REST/GraphQL interfaces, or contract testing references | qa-engineer | Review spec for testability, acceptance criteria completeness, contract testing gaps | P-032, P-037 |
| ACT-002 | 2 | Stage 2 spec contains auth, authentication, authorization, crypto, secrets, tokens, OR P-038 flagged in stage-receipt or dispatch receipt | security-engineer | Review spec for security requirements completeness, threat model coverage, OWASP alignment | P-038, P-039 |
| ACT-003 | 2 | Stage 2 spec contains infrastructure, deploy, Docker, Kubernetes, Terraform, CI/CD pipeline changes | infra-engineer | Review spec for platform feasibility, golden path alignment, environment provisioning, IaC design | P-044, P-045, P-046 |
| ACT-004 | 2 | Stage 2 spec contains data pipeline, ETL, schema migration, data warehouse, dbt, streaming | data-engineer | Review spec for data architecture, schema versioning, pipeline quality patterns | P-049, P-050 |
| ACT-005 | 3 | Stage-receipt `process_acknowledgments` contains P-038 through P-043 with severity HIGH or CRITICAL, OR a `/security` dispatch receipt exists for this session | security-engineer | Security review of Stage 3 implementation code — injection risks, auth flaws, secret handling | P-038, P-039, P-040 |
| ACT-006 | 3 | Task description or dispatch_hint contains schema, migration, data model, pipeline, ETL | data-engineer | Review data layer implementation for schema versioning, migration safety, data quality | P-049, P-050 |
| ACT-007 | 5 | Stage 5 validation involves Docker, Kubernetes, cloud deployment, or infrastructure components | sre | Validate operational readiness — SLO alignment, monitoring, alerting, runbook existence | P-054, P-055 |
| ACT-008 | 5 | Session artifacts contain ML model files, training scripts, inference endpoints, or model serving config | ml-engineer | Validate ML pipeline — training-serving skew, canary deployment, experiment logging, drift monitoring | P-051, P-052, P-053 |
| ACT-009 | 5 | Session created or modified Terraform, CDK, Pulumi, or cloud IaC files | infra-engineer | Review IaC for cost optimization, security groups, architecture compliance | P-045, P-047 |
| ACT-010 | 6 | P-061 (Runbook) flagged in process acknowledgments OR infrastructure/deployment components present in session | sre | Co-author runbook sections — incident response, scaling procedures, rollback steps | P-054, P-056, P-061 |
| ACT-011 | 6 | P-059 (API Docs) flagged in process acknowledgments OR API endpoints implemented in session | qa-engineer | Review API documentation for completeness, accuracy against implementation, example coverage | P-032, P-059 |
| ACT-012 | 5 | Session artifacts contain UI components, HTML templates, React/Vue/Svelte components, or front-end code with user-facing interfaces | qa-engineer | Accessibility compliance review — WCAG 2.1 AA/AAA, ARIA patterns, keyboard navigation, color contrast, screen reader compatibility | P-032, P-035 |

---

## Condition Detection Methods

The orchestrator evaluates activation conditions by reading stage artifacts with Glob/Grep (tools it already has). No new tools are required.

| Condition Type | Detection Method |
|---------------|-----------------|
| **Spec keyword match** (ACT-001 to ACT-004) | Grep Stage 2 spec output (`.orchestrate/<SESSION_ID>/stage-2/*.md`) for domain-specific keywords. Match against section headings and content body — not filenames alone. |
| **Process acknowledgment check** (ACT-002, ACT-005, ACT-010, ACT-011) | Read `stage-receipt.json` for the completed stage. Check `process_acknowledgments` array for matching process IDs with `severity` of HIGH or CRITICAL. |
| **Dispatch receipt check** (ACT-005) | Glob `.orchestrate/<SESSION_ID>/dispatch-receipts/dispatch-*-TRIG-001-*.json` for `/security` dispatch receipts. Presence of any receipt triggers the rule. |
| **Task context match** (ACT-006) | Check current task's `description` and `dispatch_hint` fields for domain keywords. |
| **Artifact presence check** (ACT-007 to ACT-009) | Glob session directory and project root for domain-specific files: `Dockerfile`, `*.tf`, `*.yaml` (k8s manifests), `*.ipynb`, model files, etc. |
| **Session history check** (ACT-009) | Check `checkpoint.stages_completed` and stage artifacts for IaC file creation/modification records. |
| **Frontend artifact check** (ACT-012) | Glob session directory and project root for UI component files: `*.jsx`, `*.tsx`, `*.vue`, `*.svelte`, `*.html`, React/Vue/Svelte component directories. Match component creation/modification in stage artifacts. |

**False positive mitigation**: Conditions should match keywords in **context-relevant sections** of artifacts, not in passing references. For example, a spec mentioning "Docker" in a "Deployment" section triggers ACT-003, but "Docker" in a "Background" section describing prior work does not. When in doubt, activate — a focused 10-turn review has minimal overhead and false negatives (missing a needed review) are worse than false positives.

---

## Evaluation Function

```
FUNCTION evaluate_agent_activation(completed_stage, stage_receipt, dispatch_receipts, task_context):

  INPUT:
    completed_stage:    numeric stage just completed (0, 1, 2, 3, 4, 4.5, 5)
    stage_receipt:      parsed stage-receipt.json for the completed stage (if exists)
    dispatch_receipts:  array of dispatch receipts from session dispatch-receipts/ directory
    task_context:       current task descriptions, dispatch_hints, and session scope

  activations = []
  activation_candidates = []

  # Step 1: Find rules whose trigger_stage matches the NEXT stage
  next_stage = completed_stage + 1  # simplified; handle 4 → 4.5 → 5 mapping
  
  FOR EACH rule IN ACTIVATION_RULES_TABLE:
    IF rule.trigger_stage != next_stage:
      SKIP

    # Step 2: Evaluate condition
    condition_met = evaluate_activation_condition(rule, stage_receipt, dispatch_receipts, task_context)

    IF condition_met:
      severity = determine_severity(rule, stage_receipt, dispatch_receipts)
      activation_candidates.append({rule, severity})

  # Step 3: Sort by severity (CRITICAL > HIGH > MEDIUM), then rule_id (lower first)
  activation_candidates.sort(key=lambda c: (severity_rank(c.severity), c.rule.rule_id))

  # Step 4: Cap at 2 activations (AGENT-ACTIVATE-005)
  activations = activation_candidates[:2]

  # Step 5: Deduplicate by agent — if two rules activate the same agent, keep highest severity
  seen_agents = set()
  deduplicated = []
  FOR EACH activation IN activations:
    IF activation.rule.agent NOT IN seen_agents:
      deduplicated.append(activation)
      seen_agents.add(activation.rule.agent)
  activations = deduplicated

  RETURN activations
```

---

## Review Artifact Schema

Domain agent review output is written to:
```
.orchestrate/<SESSION_ID>/domain-reviews/<agent-name>-stage-<N>.md
```

### Required Format

```markdown
## Domain Review: <agent-name>

**Stage**: <N>
**Activation Rule**: <ACT-NNN>
**Review Scope**: <scope from activation rule>
**Reviewed Artifacts**: <list of input artifact paths>
**Timestamp**: <ISO-8601>

### Findings

1. **[SEVERITY]** <finding title>
   - **Process**: <P-NNN> (<process name>)
   - **Evidence**: <specific code/spec reference>
   - **Recommendation**: <actionable recommendation for next stage>

2. **[SEVERITY]** <finding title>
   ...

### Summary

| Severity | Count |
|----------|-------|
| CRITICAL | <N> |
| HIGH | <N> |
| MEDIUM | <N> |
| LOW | <N> |

### Recommendations for Next Stage

- <actionable recommendation 1>
- <actionable recommendation 2>
- ...
```

### Severity Definitions (for domain reviews)

| Severity | Meaning | Stage Impact |
|----------|---------|-------------|
| CRITICAL | Must be addressed before proceeding to next stage | Blocks stage advancement if not addressed |
| HIGH | Should be addressed in current or next stage | Injected as requirements into next stage spawn prompt |
| MEDIUM | Recommended improvement | Logged as advisory in next stage context |
| LOW | Minor suggestion | Acknowledged only; no injection |

---

## Domain Review Spawn Templates

All domain agent spawns use the following common block, plus an agent-specific block:

### Common Review Block (include in ALL domain agent spawns)

```
REVIEW MODE: You are performing a focused domain review, not full implementation work.
SCOPE: <activation.review_scope>
INPUT ARTIFACTS: <paths to stage artifacts being reviewed>
OUTPUT: .orchestrate/<SESSION_ID>/domain-reviews/<agent>-stage-<N>.md

You MUST:
- Read and analyze the input artifacts from your domain expertise perspective
- Write a structured review following the Domain Review Artifact Schema
- Include specific evidence (file paths, line numbers, code snippets) for each finding
- Assign severity to each finding (CRITICAL, HIGH, MEDIUM, LOW)

You MUST NOT:
- Create tasks or modify PROPOSED_ACTIONS
- Modify any source files or project code
- Run git commit/push or any git write operation (MAIN-014)
- Spawn subagents
- Exceed the scope defined above

Max output: structured review artifact only. No conversational preamble.
```

### qa-engineer Review Template
```
You are qa-engineer performing a domain review.

DOMAIN FOCUS: Quality assurance, testability, acceptance criteria, contract testing, test architecture.
PROCESSES: P-032 (Test Architecture), P-037 (Contract Testing), P-059 (API Docs)
EVALUATE AGAINST:
- Test pyramid coverage gaps
- Missing acceptance criteria
- API contract testability
- Performance testing requirements (P50/P95/P99 SLO coverage)
```

### qa-engineer Accessibility Review Template (ACT-012)
```
You are qa-engineer performing an accessibility domain review.

DOMAIN FOCUS: Accessibility compliance, WCAG 2.1 AA/AAA, ARIA patterns, keyboard navigation, color contrast, screen reader compatibility.
PROCESSES: P-032 (Test Architecture), P-035 (Performance Testing — accessibility performance)
EVALUATE AGAINST:
- WCAG 2.1 Level AA compliance for all interactive elements
- ARIA roles, states, and properties on custom widgets
- Keyboard navigation (all interactive elements reachable and operable)
- Color contrast ratios (4.5:1 for normal text, 3:1 for large text)
- Focus management (visible focus indicators, logical tab order)
- Screen reader compatibility (meaningful alt text, live regions)
- Form labels and error messages (programmatically associated)
```

### security-engineer Review Template
```
You are security-engineer performing a domain review.

DOMAIN FOCUS: Application security, threat modeling, OWASP Top 10, auth/crypto, secrets management.
PROCESSES: P-038 (Threat Modeling), P-039 (SAST/DAST), P-040 (CVE Triage)
EVALUATE AGAINST:
- STRIDE threat model coverage
- Injection vulnerabilities (SQL, XSS, command)
- Authentication/authorization flaws
- Secret exposure risks
- Dependency vulnerabilities
READ-ONLY: You have no Write tool. Evidence-based findings only.
```

### infra-engineer Review Template
```
You are infra-engineer performing a domain review.

DOMAIN FOCUS: CI/CD, golden path templates, container orchestration, environment provisioning, cloud infrastructure, IaC, cost optimization, IAM, architecture compliance.
PROCESSES: P-044 (Golden Path), P-045 (Infrastructure Provisioning), P-046 (Environment Self-Service), P-047 (Cloud Architecture Review)
EVALUATE AGAINST:
- Golden path alignment (easiest path, not only path)
- CI/CD pipeline feasibility
- Container configuration correctness
- Environment provisioning patterns
- IaC completeness (no manual provisioning)
- Cost optimization opportunities
- Security group / IAM policy correctness
- Multi-region / availability design
```

### data-engineer Review Template
```
You are data-engineer performing a domain review.

DOMAIN FOCUS: Data pipelines, schema migrations, data quality, streaming, warehouse design.
PROCESSES: P-049 (Pipeline Quality), P-050 (Schema Migration)
EVALUATE AGAINST:
- Schema versioning (destructive changes require manual review)
- Data quality gates (freshness, null checks, row counts)
- Pipeline idempotency
- Migration rollback safety
```

### ml-engineer Review Template
```
You are ml-engineer performing a domain review.

DOMAIN FOCUS: ML pipelines, model serving, experiment tracking, drift monitoring, canary deployment.
PROCESSES: P-051 (Experiment Logging), P-052 (Model Canary), P-053 (Drift Monitoring)
EVALUATE AGAINST:
- Training-serving skew prevention
- Experiment logging completeness (hyperparams, metrics, data version)
- Canary deployment requirement (never 100% direct)
- Drift monitoring configuration
```

### sre Review Template
```
You are sre performing a domain review.

DOMAIN FOCUS: SLO definition, incident response, operational readiness, runbooks, monitoring.
PROCESSES: P-054 (SLO Definition), P-055 (Incident Response), P-056 (Post-Mortem), P-061 (Runbook)
EVALUATE AGAINST:
- SLO coverage for new/modified services
- Error budget impact assessment
- Monitoring and alerting configuration
- Runbook completeness (rollback, scaling, incident steps)
- On-call impact
```

---

## Integration with Orchestrator Execution Loop

The orchestrator integrates agent activation at two points in its execution loop:

### Point 1: Post-Stage Activation Evaluation

After all tasks for a stage complete and before processing the next stage's tasks:

```
# After line ~317 in orchestrator.md (after task completion loop, before Post-Loop Mandatory Gates)

completed_stage = get_highest_completed_stage(all_tasks)

IF stage_just_completed(completed_stage):  # First time seeing this stage fully done
    # Read activation rules from manifest (MANIFEST-001)
    activation_rules = manifest.agents[*].activation_rules WHERE trigger_stage == completed_stage + 1
    
    stage_receipt = read(".orchestrate/<SESSION_ID>/stage-<completed_stage>/stage-receipt.json")
    dispatch_receipts = glob(".orchestrate/<SESSION_ID>/dispatch-receipts/dispatch-*.json")
    
    activations = evaluate_agent_activation(completed_stage, stage_receipt, dispatch_receipts, task_context)
    
    domain_agents_spawned = 0
    FOR EACH activation IN activations:
        IF domain_agents_spawned >= 2: BREAK  # AGENT-ACTIVATE-005
        
        output(f"[DOMAIN-REVIEW] {activation.rule_id}: Spawning {activation.agent} for Stage {completed_stage + 1} review")
        
        spawn_subagent(
            activation.agent,
            review_task={
                subject: f"Domain review: {activation.review_scope}",
                description: activation.review_scope,
                stage: completed_stage + 1,
                output_path: f".orchestrate/{SESSION_ID}/domain-reviews/{activation.agent}-stage-{completed_stage + 1}.md"
            },
            extra_prompt = COMMON_REVIEW_BLOCK + AGENT_SPECIFIC_TEMPLATE,
            max_turns = 10
        )
        # NOTE: Does NOT decrement REMAINING_BUDGET (AGENT-ACTIVATE-003)
        
        output(f"[DOMAIN-REVIEW] {activation.agent} review complete. Artifact: {output_path}")
        domain_agents_spawned += 1
```

### Point 2: Review Context Injection into Stage Spawns

Before spawning agents for the next stage's tasks, inject domain review findings:

```
# Before spawn_subagent() call in execution loop (~line 302 in orchestrator.md)

domain_reviews = glob(".orchestrate/<SESSION_ID>/domain-reviews/*-stage-{task.stage}.md")
IF domain_reviews:
    review_summary = compile_reviews(domain_reviews)
    extra_prompt += f"""

## Domain Expert Review Findings

The following domain experts reviewed artifacts relevant to this stage. Address their findings:

{review_summary}

CRITICAL findings MUST be addressed in your implementation.
HIGH findings SHOULD be addressed in your implementation.
MEDIUM/LOW findings: acknowledge in your output but no action required.
"""
```

---

## Relationship to Other Protocols

| Protocol | Relationship |
|----------|-------------|
| **Command Dispatch** (`command-dispatch.md`) | Complementary. Dispatch invokes Skills for high-level analysis; activation spawns agents for code-level review. A dispatch receipt can trigger an activation rule (ACT-005). |
| **Process Injection Map** (`process_injection_map.md`) | Additive. Process injection maps processes to stages (advisory/gate). Activation adds expert review when those processes flag issues. |
| **Cross-Pipeline State** (`cross-pipeline-state.md`) | Domain review artifacts are session-local. Findings that warrant cross-pipeline persistence should be written to `.pipeline-state/codebase-analysis.jsonl` by the orchestrator. |
| **Escalation Protocol** | Orthogonal. Escalation handles command-to-command transitions (auto-debug → auto-orchestrate). Activation handles within-orchestrator domain reviews. |

---

## Checkpoint Schema Additions

The auto-orchestrate checkpoint gains these fields (added in schema 1.3.0):

```json
{
  "domain_activations": [],
  "domain_reviews": {
    "0": [], "1": [], "2": [], "3": [], "4": [], "4.5": [], "5": [], "6": []
  }
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `domain_activations` | array | `[]` | Append-only log of all domain agent activations. Each entry: `{ rule_id, agent, stage, timestamp, artifact_path, findings_count, severity_max }` |
| `domain_reviews` | object | `{}` per stage | Per-stage array of agent names that produced reviews. Used to inject review context into spawn prompts. |

---

*Implements Improvement A2 (Agent Utilization Imbalance) | References: AGENT-ACTIVATE-001/002 (Improvements.md), MANIFEST-001 (orchestrator.md), DISPATCH-GUARD-001 (command-dispatch.md)*
