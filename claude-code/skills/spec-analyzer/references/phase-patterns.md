# Phase Planning Patterns Reference

## Phasing Strategies

### 1. Vertical Slicing (Recommended)

Each phase delivers complete, end-to-end functionality.

```
┌─────────────────────────────────────────────────────────┐
│                    Full Feature                          │
├─────────────────────────────────────────────────────────┤
│  Phase 1   │   Phase 2   │   Phase 3   │   Phase 4     │
│  ┌─────┐   │   ┌─────┐   │   ┌─────┐   │   ┌─────┐     │
│  │ UI  │   │   │ UI  │   │   │ UI  │   │   │ UI  │     │
│  ├─────┤   │   ├─────┤   │   ├─────┤   │   ├─────┤     │
│  │ API │   │   │ API │   │   │ API │   │   │ API │     │
│  ├─────┤   │   ├─────┤   │   ├─────┤   │   ├─────┤     │
│  │ DB  │   │   │ DB  │   │   │ DB  │   │   │ DB  │     │
│  └─────┘   │   └─────┘   │   └─────┘   │   └─────┘     │
│  Basic     │   Social    │   MFA       │   SSO         │
│  Auth      │   Login     │   Support   │   Integration │
└─────────────────────────────────────────────────────────┘
```

**When to use:**
- Feature can be incrementally released
- Want to demonstrate value early
- Need feedback between phases
- Agile/iterative development

**Benefits:**
- Each phase is deployable
- Early value demonstration
- Risk distributed across phases
- Can stop after any phase
- Easier to test end-to-end

**Example:**
```
Phase 1: Basic user registration (email/password)
Phase 2: Add Google OAuth login
Phase 3: Add GitHub OAuth login
Phase 4: Add MFA (TOTP)
Phase 5: Add SSO (SAML/OIDC)
```

### 2. Horizontal Layering

Build infrastructure/platform first, then features.

```
┌─────────────────────────────────────────────────────────┐
│                                                          │
│  Phase 4:  │     UI Layer      │  Features, Polish      │
│            ├───────────────────┤                        │
│  Phase 3:  │    API Layer      │  Business Logic        │
│            ├───────────────────┤                        │
│  Phase 2:  │   Data Layer      │  Models, Storage       │
│            ├───────────────────┤                        │
│  Phase 1:  │  Infrastructure   │  DB, Cache, Queue      │
│            └───────────────────┘                        │
└─────────────────────────────────────────────────────────┘
```

**When to use:**
- New system/platform build
- Heavy infrastructure requirements
- Multiple features share foundation
- Team specialization (frontend/backend)

**Benefits:**
- Solid foundation
- Shared infrastructure
- Clear team boundaries

**Drawbacks:**
- [ ] Value delivered late
- [ ] Higher risk of building wrong thing
- [ ] Harder to get feedback

### 3. Risk-First

Tackle highest-risk items first to de-risk project.

```
┌─────────────────────────────────────────────────────────┐
│                                                          │
│  Phase 1:  High Risk      │  Integration with legacy    │
│            v              │  Performance critical path  │
│  Phase 2:  Medium Risk    │  New technology components  │
│            v              │  Complex business logic     │
│  Phase 3:  Low Risk       │  Standard CRUD operations   │
│            v              │  UI polish                  │
│  Phase 4:  No Risk        │  Documentation, cleanup     │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**When to use:**
- High uncertainty in project
- Critical dependencies on external systems
- New/unfamiliar technology
- Tight deadlines

**Benefits:**
- Early identification of blockers
- More accurate estimation after Phase 1
- Can pivot early if needed

### 4. Dependency-Ordered

Order phases by technical dependencies.

```
         ┌──────────┐
         │  Auth    │  Phase 1: No dependencies
         │ Service  │
         └────┬─────┘
              │
    ┌─────────┼─────────┐
    │         │         │
┌───v───┐ ┌───v───┐ ┌───v───┐
│ User  │ │ Order │ │ Notif │  Phase 2: Depend on Auth
│Service│ │Service│ │Service│
└───┬───┘ └───┬───┘ └───────┘
    │         │
    └────┬────┘
         │
    ┌────v────┐
    │Dashboard│  Phase 3: Depends on User, Order
    │ Service │
    └─────────┘
```

**When to use:**
- Clear technical dependencies
- Multiple services/components
- Microservices architecture

## Phase Sizing

### T-Shirt Sizing Guide

| Size | Duration | Team | Scope |
|------|----------|------|-------|
| XS | 1-2 days | 1 person | Single feature/fix |
| S | 3-5 days | 1-2 people | Small feature |
| M | 1-2 weeks | 2-3 people | Medium feature |
| L | 2-4 weeks | 3-5 people | Large feature |
| XL | 1-2 months | 5+ people | Major feature/epic |

### Ideal Phase Size

**Target: 1-2 weeks per phase (Size M)**

- Long enough to deliver value
- Short enough to maintain momentum
- Easy to estimate accurately
- Natural review/feedback points

### Split Large Phases

If a phase is > 2 weeks:

1. Find natural break points
2. Identify shippable increments
3. Split by feature subset
4. Split by user type
5. Split by data scope (subset of data)

## Phase Document Structure

### Phase Overview

```markdown
# Phase N: [Name]

## Quick Info
| Field | Value |
|-------|-------|
| Status | [ ] Not Started / [~] In Progress / [x] Complete |
| Start Date | [date] |
| Target End | [date] |
| Prerequisites | Phase N-1 / None |
| Assignees | [names] |

## Goal
[One sentence describing what this phase achieves]

## Success Criteria
- [ ] [Measurable criterion 1]
- [ ] [Measurable criterion 2]
```

### Requirements Section

```markdown
## Requirements

### Functional Requirements
| ID | Description | Priority |
|----|-------------|----------|
| FR-01 | ... | MUST |
| FR-02 | ... | SHOULD |

### Non-Functional Requirements
| ID | Description |
|----|-------------|
| NFR-01 | ... |
```

### Deliverables Section

```markdown
## Deliverables

### 1. [Deliverable Name]

**Description:** What this is

**Files:**
- `src/services/UserService.ts`
- `src/models/User.ts`
- `src/api/routes/users.ts`

**Acceptance Criteria:**
- [ ] [AC 1]
- [ ] [AC 2]

**Tests:**
- [ ] Unit tests for UserService
- [ ] API integration tests
```

### Technical Section

```markdown
## Technical Approach

### Architecture
[Describe approach, include diagram if helpful]

### Data Model
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### API Changes
| Method | Path | Description |
|--------|------|-------------|
| POST | /api/users | Create user |
| GET | /api/users/:id | Get user |
```

### Tasks Section

```markdown
## Implementation Tasks

| # | Task | Estimate | Status |
|---|------|----------|--------|
| 1 | Set up data model | 2h | [ ] |
| 2 | Implement repository | 4h | [ ] |
| 3 | Implement service | 4h | [ ] |
| 4 | Add API endpoints | 4h | [ ] |
| 5 | Write unit tests | 4h | [ ] |
| 6 | Write integration tests | 2h | [ ] |
| 7 | Documentation | 2h | [ ] |
| **Total** | | **22h** | |
```

### Definition of Done

```markdown
## Definition of Done

### Code Complete
- [ ] All tasks implemented
- [ ] Code follows coding standards
- [ ] No placeholders or TODOs

### Testing Complete
- [ ] Unit tests written and passing
- [ ] Integration tests passing
- [ ] Manual testing completed

### Review Complete
- [ ] Code review approved
- [ ] Documentation reviewed

### Deployment
- [ ] Deployed to staging
- [ ] Smoke tests passing
- [ ] Ready for production
```

## Phase Transitions

### Phase Completion Checklist

Before marking phase complete:

- [ ] All deliverables complete
- [ ] All acceptance criteria met
- [ ] All tests passing
- [ ] Code review approved
- [ ] Documentation updated
- [ ] Deployed to target environment
- [ ] Stakeholder sign-off (if required)

### Phase Handoff

```markdown
## Phase N Completion Summary

**Completed:** [date]
**Duration:** [actual time]

### What Was Delivered
- [Deliverable 1]
- [Deliverable 2]

### What Changed from Plan
- [Any deviations and why]

### Known Issues
- [Issue 1] - [workaround/plan]

### Ready for Phase N+1
- [Any setup needed]
- [Any information for next phase]
```

## Common Phase Patterns

### MVP -> Enhancement -> Scale

```
Phase 1: MVP
- Core functionality only
- Manual processes OK
- Limited error handling
- Basic UI

Phase 2: Enhancement
- Additional features
- Better UX
- Error handling
- Automation

Phase 3: Scale
- Performance optimization
- Monitoring/alerting
- Documentation
- Edge cases
```

### Build -> Integrate -> Harden

```
Phase 1: Build
- Core implementation
- Happy path working
- Basic tests

Phase 2: Integrate
- External system integration
- Error handling
- Retry logic

Phase 3: Harden
- Security hardening
- Performance tuning
- Comprehensive testing
- Documentation
```

### Feature Flags Approach

```
Phase 1: Behind flag (internal only)
- Implement feature
- Deploy to production (disabled)
- Internal testing

Phase 2: Beta rollout
- Enable for beta users
- Collect feedback
- Fix issues

Phase 3: General availability
- Enable for all users
- Remove feature flag
- Full documentation
```
