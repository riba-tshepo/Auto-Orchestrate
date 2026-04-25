# Specification Validation Checklist

## Structural Completeness

### Required Sections

| Section | Present | Quality |
|---------|---------|---------|
| Title/Overview | [ ] | [ ] |
| Problem Statement | [ ] | [ ] |
| Goals/Objectives | [ ] | [ ] |
| Functional Requirements | [ ] | [ ] |
| Non-Functional Requirements | [ ] | [ ] |
| Acceptance Criteria | [ ] | [ ] |
| Dependencies | [ ] | [ ] |
| Out of Scope | [ ] | [ ] |

### Conditional Sections

| Section | Needed | Present |
|---------|--------|---------|
| Data Model | [ ] | [ ] |
| API Specification | [ ] | [ ] |
| UI/UX Requirements | [ ] | [ ] |
| Security Requirements | [ ] | [ ] |
| Migration Strategy | [ ] | [ ] |
| Rollback Plan | [ ] | [ ] |

## Requirement Quality

### SMART Criteria

For each requirement, verify:

| Criterion | Description | Check |
|-----------|-------------|-------|
| **S**pecific | Clear, unambiguous language | [ ] |
| **M**easurable | Quantifiable success criteria | [ ] |
| **A**chievable | Technically feasible | [ ] |
| **R**elevant | Aligned with goals | [ ] |
| **T**estable | Can write tests for it | [ ] |

### Red Flags in Requirements

| Flag | Example | Better |
|------|---------|--------|
| Vague adjectives | "System should be fast" | "Response time < 200ms p95" |
| Open-ended lists | "Support formats like PDF, etc." | "Support PDF, DOCX, PNG" |
| Compound requirements | "Must do X and Y and Z" | Split into FR-01, FR-02, FR-03 |
| Implementation details | "Use Redis for caching" | "Cache frequently accessed data" |
| Missing actor | "Data should be validated" | "System validates user input" |
| Ambiguous scope | "Handle all edge cases" | List specific edge cases |

### Completeness Checks

- [ ] All user types identified
- [ ] Happy path defined
- [ ] Error cases defined
- [ ] Edge cases defined
- [ ] Boundary conditions specified
- [ ] Null/empty handling specified

## Acceptance Criteria Quality

### Coverage

| Requirement | Has AC | AC Testable |
|-------------|--------|-------------|
| FR-01 | [ ] | [ ] |
| FR-02 | [ ] | [ ] |
| ... | [ ] | [ ] |

**Target: 100% of MUST requirements have AC**

### AC Quality Checks

- [ ] Written in Given/When/Then or clear checklist
- [ ] Objectively verifiable (no "should feel fast")
- [ ] Covers success scenarios
- [ ] Covers failure scenarios
- [ ] Covers edge cases
- [ ] Includes specific values where applicable
- [ ] No implementation details

### Common AC Issues

| Issue | Example | Fix |
|-------|---------|-----|
| Vague outcome | "appropriate message shown" | "Error message 'Invalid email' displayed" |
| Missing precondition | "When user submits form" | "Given user on registration page, When..." |
| Untestable | "User experience is good" | Define specific UX metrics |
| Too broad | "System handles all errors" | List specific error scenarios |

## Consistency Validation

### Terminology

- [ ] Key terms defined (glossary if needed)
- [ ] Consistent naming throughout
- [ ] Matches existing system terminology
- [ ] Acronyms expanded on first use

### Cross-Reference

- [ ] No contradicting requirements
- [ ] No duplicate requirements
- [ ] Referenced specs exist
- [ ] Referenced features exist
- [ ] Version numbers consistent

### Common Inconsistencies

| Type | Example | Fix |
|------|---------|-----|
| Naming | "User" vs "Customer" vs "Account" | Pick one, use consistently |
| State | "Draft" vs "Pending" vs "New" | Define state machine |
| Flow | Different paths in different sections | Create single flow diagram |
| Metrics | "Fast" in one place, "< 1s" in another | Use same metric everywhere |

## Technical Feasibility

### Architecture Fit

- [ ] Aligns with existing architecture
- [ ] No impossible requirements
- [ ] Required technology available
- [ ] Team has required skills
- [ ] Infrastructure can support

### Performance Feasibility

| Requirement | Feasible | Notes |
|-------------|----------|-------|
| NFR-01: < 10ms response | [ ] | May need caching |
| NFR-02: 1M concurrent | [ ] | Needs load testing |

### Integration Feasibility

- [ ] External APIs available and documented
- [ ] API rate limits acceptable
- [ ] Authentication methods compatible
- [ ] Data formats compatible

## Dependency Validation

### Internal Dependencies

| Dependency | Exists | Status | Blocking |
|------------|--------|--------|----------|
| Auth Service | [ ] | _____ | [ ] |
| User Service | [ ] | _____ | [ ] |

### External Dependencies

| Dependency | Available | Version OK | Fallback |
|------------|-----------|------------|----------|
| Stripe API | [ ] | [ ] | [ ] |
| SendGrid | [ ] | [ ] | [ ] |

### Circular Dependency Check

```
A -> B -> C -> A  [ERROR] Circular!
A -> B -> C       [OK]
```

## Security Validation

### Authentication & Authorization

- [ ] Auth method specified
- [ ] User roles defined
- [ ] Permissions matrix documented
- [ ] Session handling specified

### Data Security

- [ ] Sensitive data identified
- [ ] Encryption requirements specified
- [ ] Data retention policy defined
- [ ] PII handling documented

### Compliance

| Requirement | Applicable | Addressed |
|-------------|------------|-----------|
| GDPR | [ ] | [ ] |
| SOC2 | [ ] | [ ] |
| HIPAA | [ ] | [ ] |
| PCI-DSS | [ ] | [ ] |

## Scoring Guide

### Category Scores (0-10)

| Category | Score | Weight |
|----------|-------|--------|
| Structure | /10 | 15% |
| Requirements | /10 | 25% |
| Acceptance Criteria | /10 | 20% |
| Consistency | /10 | 15% |
| Dependencies | /10 | 10% |
| Technical | /10 | 15% |

### Score Interpretation

| Score | Rating | Action |
|-------|--------|--------|
| 90-100% | READY | Proceed to implementation |
| 75-89% | MINOR ISSUES | Fix issues, can start planning |
| 50-74% | NEEDS WORK | Significant revision needed |
| < 50% | NOT READY | Major revision required |

### Blocking Issue Categories

**Must fix before implementation:**
- Missing acceptance criteria for MUST requirements
- Contradicting requirements
- Unresolvable dependencies
- Technically impossible requirements
- Critical security gaps

**Should fix but won't block:**
- Missing non-functional requirements
- Incomplete edge cases
- Minor inconsistencies
- Missing nice-to-have sections

## Quick Validation Checklist

### 5-Minute Check

- [ ] Has clear problem statement
- [ ] Has measurable requirements
- [ ] Has acceptance criteria
- [ ] Dependencies identified
- [ ] Out of scope defined

### 15-Minute Check

- [ ] All MUST requirements SMART
- [ ] AC covers happy + error paths
- [ ] No obvious contradictions
- [ ] Dependencies exist and accessible
- [ ] Security basics covered

### Full Validation

Complete all sections above, score, and produce validation report.
