# Workflow Patterns

This reference documents reusable patterns for multi-skill workflows. Use these patterns when orchestrating skill chains.

---

## Pattern Overview

| Pattern | Description | Use Case |
|---------|-------------|----------|
| **Analyzer-Executor** | Analysis skill identifies work; executor performs it | Refactoring, test generation |
| **Producer-Consumer** | One skill produces artifacts consumed by multiple skills | Research, metrics collection |
| **Sequential Pipeline** | Multi-step workflow with chained transformations | Spec->plan->implement->validate |
| **Quality Gate** | Validation skill gates progression to next phase | Documentation review, compliance |

---

## Pattern 1: Analyzer-Executor

An analysis skill identifies work to be done; an executor skill performs the actual work.

### Flow

```
┌─────────────────────┐
│     ANALYZER        │  Identifies what needs to be done
│  (refactor-analyzer)│
└─────────┬───────────┘
          │ produces: extraction-plan, function-groups
          v
┌─────────────────────┐
│     EXECUTOR        │  Performs the identified work
│ (refactor-executor) │
└─────────────────────┘
```

### Characteristics

| Aspect | Description |
|--------|-------------|
| **Separation** | Analysis is distinct from execution |
| **Handoff** | Analyzer produces structured plan; executor consumes it |
| **Approval** | Often includes user approval between phases |
| **Rollback** | Execution can be reverted without losing analysis |

### Skill Pairs

| Analyzer | Executor | Domain |
|----------|----------|--------|
| `refactor-analyzer` | `refactor-executor` | Code refactoring |
| `test-gap-analyzer` | `test-writer-pytest` | Test generation |
| `spec-analyzer` | `task-executor` | Specification implementation |
| `dependency-analyzer` | `hierarchy-unifier` | Architecture consolidation |

### Contract

**Analyzer produces:**
- Structured analysis report
- Actionable items with priorities
- Execution plan for downstream skill

**Executor expects:**
- Clear plan to execute
- Identified targets and actions
- Success criteria

---

## Pattern 2: Producer-Consumer

One skill produces artifacts that multiple downstream skills can consume.

### Flow

```
┌─────────────────────┐
│     PRODUCER        │  Generates reusable artifacts
│  (codebase-stats)   │
└─────────┬───────────┘
          │ produces: metrics, hotspots, debt-inventory
    ┌─────┴─────┬────────────┐
    v           v            v
┌───────┐  ┌────────┐  ┌─────────┐
│refactor│  │test-gap │  │security │
│analyzer│  │analyzer │  │auditor  │
└───────┘  └────────┘  └─────────┘
```

### Characteristics

| Aspect | Description |
|--------|-------------|
| **One-to-many** | Single producer, multiple consumers |
| **Reusability** | Producer output used without re-collection |
| **Independence** | Consumers operate independently |
| **Efficiency** | Avoids duplicate data gathering |

### Producer Skills

| Producer | Outputs | Consumers |
|----------|---------|-----------|
| `researcher` | findings, recommendations | docs-write, spec-creator |
| `codebase-stats` | metrics, hotspots, debt-inventory | refactor-analyzer, test-gap-analyzer, security-auditor |
| `security-auditor` | vulnerability-list, risk-assessment | error-standardizer, validator |

### Contract

**Producer provides:**
- Well-structured output artifacts
- Consistent format across invocations
- Key findings in manifest entry

**Consumers expect:**
- Artifacts in documented format
- Graceful handling when producer hasn't run
- Independence from other consumers

---

## Pattern 3: Sequential Pipeline

Multi-step workflow where each skill's output feeds the next.

### Flow

```
┌───────────┐    ┌─────────────┐    ┌─────────────┐    ┌───────────┐
│  CREATOR  │ ->  │  ANALYZER   │ ->  │  EXECUTOR   │ ->  │ VALIDATOR │
│(spec-     │    │(spec-       │    │(task-       │    │(validator)│
│ creator)  │    │ analyzer)   │    │ executor)   │    │           │
└───────────┘    └─────────────┘    └─────────────┘    └───────────┘
    creates          analyzes         implements        validates
  specification      phases             tasks           compliance
```

### Characteristics

| Aspect | Description |
|--------|-------------|
| **Linear** | Clear start-to-end progression |
| **Transformative** | Each step transforms the artifact |
| **Dependent** | Each step requires previous step's output |
| **Traceable** | Clear lineage from input to output |

### Example Pipelines

**Specification Pipeline:**
1. `spec-creator` -> creates specification document
2. `spec-analyzer` -> extracts phases and requirements
3. `task-executor` -> implements each phase
4. `validator` -> validates compliance

**Documentation Pipeline:**
1. `researcher` -> gathers information
2. `docs-write` -> creates documentation
3. `docs-review` -> reviews for style compliance

### Contract

**Each step provides:**
- Transformed/enhanced artifact
- Clear output format for next step
- Status in manifest for tracking

**Each step expects:**
- Previous step's output in expected format
- Clear transformation requirements
- Defined completion criteria

---

## Pattern 4: Quality Gate

A validation skill gates progression to the next phase.

### Flow

```
┌─────────────────────┐
│    WORK SKILL       │  Produces deliverable
│    (docs-write)     │
└─────────┬───────────┘
          │ produces: documentation-file
          v
┌─────────────────────┐
│    GATE SKILL       │  Validates deliverable
│   (docs-review)     │
├─────────────────────┤
│ PASS: Continue      │
│ FAIL: Return to     │
│       work skill    │
└─────────────────────┘
```

### Characteristics

| Aspect | Description |
|--------|-------------|
| **Blocking** | Gate must pass before progression |
| **Binary** | Pass/fail outcome |
| **Feedback** | Failure provides improvement guidance |
| **Iterative** | May cycle through work->gate multiple times |

### Quality Gates

| Work Skill | Gate Skill | Pass Condition |
|------------|------------|----------------|
| `docs-write` | `docs-review` | No style violations |
| Any `-executor` skill | `validator` | Compliance check passes |
| `spec-creator` | `spec-analyzer` | Requirements complete |
| `refactor-executor` | `validator` | Tests pass, no regressions |

### Contract

**Work skill provides:**
- Deliverable meeting documented requirements
- Artifacts in format gate can evaluate

**Gate skill provides:**
- Clear pass/fail determination
- Specific feedback on failures
- Validation report for tracking

---

## Pattern Selection Guide

| Scenario | Recommended Pattern |
|----------|---------------------|
| Need to analyze before acting | Analyzer-Executor |
| One source, many uses | Producer-Consumer |
| Multi-step transformation | Sequential Pipeline |
| Quality checkpoint needed | Quality Gate |
| Complex workflow | Combine patterns |

---

## Combining Patterns

Real workflows often combine multiple patterns:

```
┌───────────────────────────────────────────────────────────────┐
│                    COMBINED WORKFLOW                          │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐                                              │
│  │ codebase-   │ ─────────────────┐                           │
│  │ stats       │                  │                           │
│  └─────────────┘                  │ (Producer-Consumer)       │
│         │                         │                           │
│         v                         v                           │
│  ┌─────────────┐           ┌─────────────┐                    │
│  │ refactor-   │           │ test-gap-   │                    │
│  │ analyzer    │           │ analyzer    │                    │
│  └──────┬──────┘           └──────┬──────┘                    │
│         │ (Analyzer-Executor)     │                           │
│         v                         v                           │
│  ┌─────────────┐           ┌─────────────┐                    │
│  │ refactor-   │           │ test-writer │                    │
│  │ executor    │           │ pytest      │                    │
│  └──────┬──────┘           └──────┬──────┘                    │
│         │                         │                           │
│         └──────────┬──────────────┘                           │
│                    v (Quality Gate)                           │
│             ┌─────────────┐                                   │
│             │  validator  │                                   │
│             └─────────────┘                                   │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## See Also

- @_shared/protocols/skill-chain-contracts.md - Chain contract requirements
- @_shared/protocols/skill-chaining-patterns.md - Execution patterns
- @manifest.json - Skill chaining metadata
