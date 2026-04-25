# Epic Examples

Consolidated examples for different epic types.

---

## Feature Epic Example

### Scenario: User Authentication System

A greenfield feature epic implementing authentication with email/password login, JWT tokens, protected routes, and session handling.

### Program Structure

| Program | Tasks | Purpose |
|------|-------|---------|
| 0 | T1 (Schema & types) | Foundation with no dependencies |
| 1 | T2 (JWT), T3 (Password) | Parallel core implementation |
| 2 | T4 (API endpoints) | Convergence point |
| 3 | T5 (Middleware) | Route protection |
| 4 | T6 (Tests) | Integration testing |

### Dependency Graph

```
T1 (Schema)
|--> T2 (JWT)
|    |--> T4 (API)
|--> T3 (Password)
     |--> T4 (API)
          |--> T5 (Middleware)
               |--> T6 (Tests)
```

### Key Patterns

1. **Schema First**: Types defined before implementation
2. **Parallel Fork**: JWT and password modules are independent
3. **Convergence Point**: API endpoints wait for both modules
4. **Test Last**: Integration tests after all implementation

---

## Bug Epic Example

### Scenario: Session Data Corruption

Race condition causing session data corruption on concurrent requests.

**Severity**: High -> Priority: high

### Program Structure

| Program | Tasks | Purpose |
|------|-------|---------|
| 0 | T1 (Investigation) | Root cause analysis |
| 1 | T2 (Atomic updates), T3 (Versioning) | Parallel fixes |
| 2 | T4 (Regression tests), T5 (Docs) | Verification |

### Bug Severity Mapping

| Severity | Priority | Indicators |
|----------|----------|------------|
| Critical | critical | Data loss, security, system down |
| High | high | Core feature broken |
| Medium | medium | Feature degraded, workaround exists |
| Low | low | Cosmetic, edge case |

### Key Pattern

Bug epics ALWAYS start with investigation. Never fix without understanding root cause.

---

## Migration Epic Example

### Scenario: Multi-Tenant Schema Migration

Database schema migration from single-tenant to multi-tenant with zero downtime.

**Risk Level**: High (production data, requires rollback plan)

### Migration Phases

| Phase | Tasks | Rollback | Risk |
|-------|-------|----------|------|
| A: Schema | Add nullable columns | Drop columns | Low |
| B: Dual-Write | Write to both systems | Disable flag | Low |
| C: Backfill | Populate existing data | Restore backup | Medium |
| D: Queries | Update read queries | Revert code | Medium |
| E: Cleanup | Enforce NOT NULL | Complex | High |

### Safety Notes

1. Each phase has checkpoint - don't proceed until validation passes
2. Rollback tested before proceeding
3. Security audit before cleanup
4. Point of no return at NOT NULL constraint

---

## Refactor Epic Example

### Scenario: Modernize Authentication System

Brownfield refactoring: session-based auth -> JWT with bcrypt.

**Classification**: Brownfield refactor (existing codebase)

### Refactor Program Structure

| Program | Tasks | Rollback Point |
|------|-------|----------------|
| 0 | Impact analysis, regression baseline | N/A (no changes) |
| 1 | New JWT module, bcrypt utilities | Disable feature flag |
| 2 | Adapter layer, integration tests | Disable feature flag |
| 3 | Enable for new users, auto-upgrade | Rollback to Program 2 |
| 4 | Validation, legacy removal | Point of no return |

### Brownfield Safety Patterns

1. **Strangler Fig**: New code parallel to legacy
2. **Feature Flags**: Instant rollback capability
3. **Regression Baseline First**: Tests BEFORE changes
4. **Gradual Migration**: Never big-bang cutover

### Brownfield Checklist

- [ ] Impact analysis completed
- [ ] Regression baseline tests written
- [ ] Rollback procedure documented and tested
- [ ] Feature flags designed for gradual rollout
- [ ] Legacy code preserved until validation complete

---

## Research Epic Examples

### Pattern 1: Exploratory Research

**Scenario**: Understanding real-time collaboration options.

**Program Structure**: Scope Definition -> Parallel Investigation -> Synthesis

```
T1 (Scope) -+-> T2 (WebSocket)
            +-> T3 (CRDT)      --> T5 (Synthesis)
            +-> T4 (OT)
```

### Pattern 2: Decision Research

**Scenario**: Choosing between Drizzle and Prisma ORM.

**Program Structure**: Criteria -> Parallel Evaluation -> Decision Matrix

```
T1 (Criteria) -+-> T2 (Drizzle)
               +-> T3 (Prisma)  --> T4 (Decision)
```

### Pattern 3: Codebase Analysis

**Scenario**: Understanding existing auth architecture.

**Program Structure**: Architecture -> Parallel Deep Dives -> Recommendations

```
T1 (Map Architecture) -+-> T2 (Dependencies)
                       +-> T3 (Data flows)  --> T5 (Recommendations)
                       +-> T4 (Pain points)
```

### Research Task Atomicity

Each research task SHOULD address exactly ONE question:

| Good | Bad |
|------|-----|
| "What WebSocket libraries exist for Node?" | "Research real-time options" |
| "Compare Drizzle query performance" | "Evaluate ORMs" |
| "Map auth token data flow" | "Understand auth system" |

---

## Common Patterns Summary

| Epic Type | Program 0 | Parallel Opportunities | Final Program |
|-----------|--------|------------------------|------------|
| Feature | Foundation/schema | Independent modules | Tests |
| Bug | Investigation | Parallel fixes | Verification |
| Migration | Schema prep | Dual implementations | Cleanup |
| Refactor | Impact + baseline | New code + docs | Validation |
| Research | Scope definition | Parallel investigation | Synthesis |
