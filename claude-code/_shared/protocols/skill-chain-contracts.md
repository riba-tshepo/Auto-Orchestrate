# Skill Chain Contracts Protocol

This protocol defines RFC 2119 requirements for skill chaining handoffs, enabling intelligent skill composition and documented workflow patterns.

---

## Overview

Skills have natural functional relationships (analyzer->executor, producer->consumer) that require explicit contracts for:
- Discovering which skills chain together
- Understanding input/output contracts between skills
- Reusing documented workflow patterns

---

## Producer Requirements

| ID | Rule | Description |
|----|------|-------------|
| CHAIN-001 | Producer MUST declare outputs in manifest `chaining.produces` | List of output artifact types the skill generates |
| CHAIN-002 | Producer MUST populate `key_findings` with consumer-actionable items | Manifest entries must include findings usable by downstream skills |
| CHAIN-003 | Producer SHOULD set `needs_followup` with next skill's task ID | Explicit linkage to suggested next skill |
| CHAIN-004 | Producer SHOULD document output format in skill's chaining section | Enable consumers to parse producer artifacts |

---

## Consumer Requirements

| ID | Rule | Description |
|----|------|-------------|
| CHAIN-005 | Consumer MUST declare inputs in manifest `chaining.consumes_from` | List of skills whose outputs this skill can consume |
| CHAIN-006 | Consumer SHOULD check manifest for producer's `key_findings` first | Read manifest before re-analyzing from scratch |
| CHAIN-007 | Consumer SHOULD validate producer output format | Handle schema mismatches gracefully |
| CHAIN-008 | Consumer MUST NOT assume producer has run (graceful degradation) | Operate independently when no producer output exists |

---

## Chain Relationship Requirements

| ID | Rule | Description |
|----|------|-------------|
| CHAIN-009 | Skills MUST declare `chains_to`/`chains_from` in manifest | Explicit forward/backward chain relationships |
| CHAIN-010 | Skills SHOULD declare `patterns` for recognized workflow patterns | Reference patterns from workflow-patterns.md |
| CHAIN-011 | Skills MUST NOT create circular chain dependencies | Prevent infinite loops (A->B->A prohibited) |

---

## Manifest Chaining Schema

Skills declare chaining metadata in `manifest.json`:

```json
{
  "name": "skill-name",
  "chaining": {
    "produces": ["artifact-type-1", "artifact-type-2"],
    "consumes_from": ["upstream-skill-1", "upstream-skill-2"],
    "chains_to": ["downstream-skill-1"],
    "chains_from": ["upstream-skill-1"],
    "patterns": ["analyzer-executor", "producer-consumer"]
  }
}
```

### Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| `produces` | array | Artifact types this skill outputs (e.g., "analysis-report", "test-stubs") |
| `consumes_from` | array | Skills whose outputs this skill can consume |
| `chains_to` | array | Skills that typically follow this one |
| `chains_from` | array | Skills that typically precede this one |
| `patterns` | array | Workflow patterns this skill participates in |

---

## Artifact Types

Standard artifact types for `produces` declarations:

| Artifact Type | Description | Example Skills |
|---------------|-------------|----------------|
| `analysis-report` | Code/system analysis findings | refactor-analyzer, dependency-analyzer |
| `extraction-plan` | Plan for code modifications | refactor-analyzer, refactor-executor |
| `gaps-list` | Identified coverage or quality gaps | test-gap-analyzer |
| `test-stubs` | Generated test file skeletons | test-gap-analyzer, test-writer-pytest |
| `phase-plan` | Multi-phase implementation plan | spec-analyzer |
| `requirements` | Extracted requirements list | spec-analyzer, spec-creator |
| `coupling-analysis` | Module dependency analysis | dependency-analyzer |
| `layer-violations` | Architecture constraint violations | dependency-analyzer |
| `vulnerability-list` | Security vulnerability findings | security-auditor |
| `risk-assessment` | Prioritized risk analysis | security-auditor |
| `findings` | Research findings and recommendations | researcher |
| `metrics` | Codebase statistics and metrics | codebase-stats |
| `debt-inventory` | Technical debt inventory | codebase-stats |
| `validation-report` | Compliance validation results | validator |

---

## Pattern References

See `@_shared/references/workflow-patterns.md` for detailed pattern documentation:

| Pattern | Description |
|---------|-------------|
| `analyzer-executor` | Analysis skill identifies work; executor performs it |
| `producer-consumer` | One skill produces artifacts consumed by multiple skills |
| `sequential-pipeline` | Multi-step workflow with chained transformations |
| `quality-gate` | Validation skill gates progression to next phase |

---

## Compliance Checklist

When implementing skill chaining:

- [ ] Producer declares `produces` array in manifest
- [ ] Producer populates `key_findings` in manifest entry
- [ ] Consumer declares `consumes_from` in manifest
- [ ] Consumer handles missing producer output gracefully
- [ ] Chain relationships declared bidirectionally (`chains_to`/`chains_from`)
- [ ] No circular dependencies in chain declarations
- [ ] Patterns array references valid workflow patterns

---

## See Also

- @_shared/protocols/skill-chaining-patterns.md - Chaining execution patterns
- @_shared/references/workflow-patterns.md - Reusable workflow patterns
- @_shared/protocols/subagent-protocol-base.md - Base subagent protocol
