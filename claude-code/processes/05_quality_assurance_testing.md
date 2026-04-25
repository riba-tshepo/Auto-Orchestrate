# Quality Assurance & Testing Processes Specification

**Category**: 5 — Quality Assurance & Testing
**Processes**: P-032 through P-037
**Date**: 2026-04-05
**Stage**: 2 — Detailed Specification
**Source**: Process Architecture (Stage 1), Clarity of Intent, Engineering Team Structure Guide

---

## Linked Skills

The following Claude Code skills support processes in this category. Auto-orchestrate invokes them at the appropriate pipeline stages (see `processes/process_injection_map.md`); operators may also invoke them directly via the `Skill` tool.

| Skill | Purpose |
|-------|---------|
| `test-gap-analyzer` | Identify untested code paths, generate missing test cases, and produce coverage reports — drives P-032 and P-037. |
| `test-writer-pytest` | Generate pytest-based tests including unit, integration, and contract tests — drives P-033 and P-037. |
| `validator` | Zero-error validation gate covering build, lint, type, and test outcomes — enforces P-034 (Definition of Done). |
| `accessibility-check` | WCAG 2.1 AA/AAA compliance checks for UI components — supports P-036 (Acceptance Criteria Verification) for any UX work. |
| `spec-compliance` | Map test coverage to specification requirements; produces compliance matrix and gap report — supports P-036. |

---

## Table of Contents

1. [P-032: Test Architecture Design Process](#p-032-test-architecture-design-process)
2. [P-033: Automated Test Framework Process](#p-033-automated-test-framework-process)
3. [P-034: Definition of Done Enforcement Process](#p-034-definition-of-done-enforcement-process)
4. [P-035: Performance Testing Process](#p-035-performance-testing-process)
5. [P-036: Acceptance Criteria Verification Process](#p-036-acceptance-criteria-verification-process)
6. [P-037: Contract Testing Process](#p-037-contract-testing-process)
7. [Cross-Process Dependency Map](#cross-process-dependency-map)
8. [Category-Level Traceability Matrix](#category-level-traceability-matrix)

---

## P-032: Test Architecture Design Process

### Identification

| Field | Value |
|-------|-------|
| **Process ID** | P-032 |
| **Process Name** | Test Architecture Design Process |
| **Category** | 5 — Quality Assurance & Testing |
| **Risk Level** | HIGH |

### Purpose

Design the test coverage strategy for a project — unit, integration, contract, performance — aligned to the deliverable Definition of Done established at Stage 2 (Scope Contract). The test architecture document must be authored and approved before the first sprint begins. It serves as the blueprint that P-033 (Automated Test Framework), P-035 (Performance Testing), and P-037 (Contract Testing) implement against.

### Derived From

- **Clarity of Intent**: Stage 2, Scope Contract — Section 3 (Definition of Done) defines the testable acceptance criteria per deliverable. Stage 4, Sprint Kickoff Brief — Section 5 (Definition of Done, Sprint Level) specifies "Automated tests written and passing in CI" and "Acceptance criteria verified by PM or QA."
- **Process Architecture**: Stage 0 research Category 5; QA Lead role responsibilities; Scope Contract DoD section.
- **Engineering Team Structure Guide**: QA Lead/Quality Architect (L6) role — "Test strategy, tool standards, DoD definition."

### Ownership

| Role | Agent | Responsibility |
|------|-------|---------------|
| **Primary Owner** | `qa-engineer` (QA Lead / Quality Architect, L6) | Authors test architecture document; defines coverage strategy, test pyramid proportions, and tooling stack |
| **Supporting** | `software-engineer` (Tech Lead) | Provides technical context on system architecture, identifies components with highest defect risk, reviews test architecture for feasibility |
| **Supporting** | `sre` | Provides SLO definitions and performance budgets; aligns performance test strategy to production SLOs |

### Stages/Steps

```
Stage 2 Scope Lock
       │
       ▼
┌──────────────────────────────┐
│ Step 1: Scope Contract Review│  QA Lead reviews all deliverables
│                              │  and their DoD criteria from P-013
└──────────┬───────────────────┘
           ▼
┌──────────────────────────────┐
│ Step 2: Risk-Based Analysis  │  Classify each deliverable by
│                              │  defect risk (HIGH/MEDIUM/LOW)
└──────────┬───────────────────┘
           ▼
┌──────────────────────────────┐
│ Step 3: Coverage Strategy    │  Define test types per deliverable:
│ Design                       │  unit, integration, contract, E2E,
│                              │  performance, accessibility
└──────────┬───────────────────┘
           ▼
┌──────────────────────────────┐
│ Step 4: Test Pyramid &       │  Set proportions:
│ Targets                      │  Unit >70%, Integration 15-20%,
│                              │  Contract/E2E 5-10%, Perf as needed
└──────────┬───────────────────┘
           ▼
┌──────────────────────────────┐
│ Step 5: Tooling Selection    │  Select test frameworks, assertion
│                              │  libraries, CI runners, coverage
│                              │  tools aligned to team's stack
└──────────┬───────────────────┘
           ▼
┌──────────────────────────────┐
│ Step 6: Performance Budget   │  Align perf budgets to SLOs from
│ Alignment                    │  SRE (P-054); define P50/P95/P99
│                              │  targets per deliverable
└──────────┬───────────────────┘
           ▼
┌──────────────────────────────┐
│ Step 7: Document & Publish   │  Test Architecture document
│                              │  published before Sprint 1
└──────────┬───────────────────┘
           ▼
┌──────────────────────────────┐
│ Step 8: Review & Approval    │  TL + SRE review; QA Lead
│                              │  incorporates feedback; final
│                              │  version baselined
└──────────────────────────────┘
```

**Step 1 — Scope Contract Review**: QA Lead reads the Scope Contract (output of P-013) and extracts every deliverable and its Definition of Done criteria. Each DoD criterion is classified as automatable (can be verified by CI) or manual (requires human verification).

**Step 2 — Risk-Based Analysis**: Each deliverable is assessed for defect risk based on: complexity, number of integration points, user-facing surface area, and whether it touches financial or security-sensitive data. HIGH-risk deliverables receive deeper test coverage.

**Step 3 — Coverage Strategy Design**: For each deliverable, QA Lead defines which test types apply. Not every deliverable needs every test type. A backend API needs unit + integration + contract tests. A UI component needs unit + E2E + accessibility tests. A performance-sensitive service needs all of the above plus load tests.

**Step 4 — Test Pyramid and Targets**: The test pyramid proportions are defined at the project level with per-deliverable overrides where justified. Default targets: unit tests >70% line coverage, integration tests covering all critical paths, contract tests covering all inter-service APIs, E2E tests covering primary user journeys only (kept minimal to avoid brittleness).

**Step 5 — Tooling Selection**: Frameworks and tools are selected from the organization's approved tooling list. If a new tool is needed, it must be justified and approved by the TL. Tooling must integrate with the existing CI/CD pipeline (coordinated with `infra-engineer`).

**Step 6 — Performance Budget Alignment**: QA Lead works with SRE to translate SLO targets into concrete performance test assertions. For example, if the SLO is "99.9% of requests complete in <200ms," the performance test must validate P99 latency <200ms under expected load.

**Step 7 — Document and Publish**: The Test Architecture document is written and stored in the project's documentation root. It is published before Sprint 1 begins.

**Step 8 — Review and Approval**: The TL reviews for technical feasibility. The SRE reviews performance budget alignment. QA Lead incorporates feedback and baselines the final version.

### Inputs

| Input | Source Process | Description |
|-------|---------------|-------------|
| Scope Contract (deliverables + DoD) | P-013 (Scope Lock) | List of all deliverables with testable acceptance criteria |
| SLO definitions | P-054 (SLO Definition) | Performance targets that test architecture must validate against |
| Existing test infrastructure | Current state | Available test frameworks, CI runners, coverage tooling |
| System architecture diagrams | Technical design docs | Service boundaries, integration points, data flows |

### Outputs/Artifacts

| Output | Format | Consumers |
|--------|--------|-----------|
| **Test Architecture Document** | Markdown/Confluence document | SDET (P-033), Performance Engineer (P-035), all squad engineers |

The Test Architecture Document contains:

1. **Deliverable-to-Test-Type Matrix** — which test types apply to each deliverable
2. **Coverage Targets** — numeric targets per deliverable (e.g., "Payments API: unit 80%, integration 100% critical paths, contract 100% endpoints")
3. **Test Pyramid Definition** — proportions and rationale for deviations from default
4. **Tooling Stack** — selected frameworks, libraries, and CI integration approach
5. **Performance Budget Table** — P50/P95/P99 latency targets per deliverable, mapped to SLOs
6. **Risk Classification** — HIGH/MEDIUM/LOW per deliverable with justification

### Gate/Checkpoint

**Gate Name**: Test Architecture Review

**Timing**: After Scope Lock (P-013), before Sprint 1 begins.

**Participants**: QA Lead, Tech Lead, SRE, Engineering Manager.

**Format**: 30-minute review meeting or async review with 48-hour response window.

**Pass Criteria**:
- Every Scope Contract deliverable has a test coverage strategy
- Coverage targets are numeric and measurable (not "good coverage" or "adequate testing")
- Test tooling is compatible with the team's CI/CD stack
- Performance budgets are aligned to SLO definitions from SRE
- At least one test type is identified for every DoD criterion that states "tests pass" or "verified"
- The TL confirms the strategy is technically feasible within the sprint timeline

### Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Deliverable coverage | % of deliverables with a test strategy | 100% |
| Measurable targets | All coverage targets are numeric | Yes/No — must be Yes |
| Tooling alignment | Test tools integrate with CI/CD without new infrastructure | Verified by infra-engineer |
| Performance alignment | Performance budgets trace to SLO definitions | 100% of perf-sensitive deliverables |

### Dependencies

| Dependency | Process | Direction | Nature |
|------------|---------|-----------|--------|
| Scope Contract locked | P-013 | Upstream (blocks P-032) | Deliverables and DoD must be defined before test architecture can be designed |
| SLO definitions | P-054 | Upstream (informs P-032) | Performance budgets derived from SLOs |
| Automated Test Framework | P-033 | Downstream (P-032 feeds P-033) | SDET implements frameworks per this architecture |
| Performance Testing | P-035 | Downstream (P-032 feeds P-035) | Performance tests follow budgets defined here |
| Contract Testing | P-037 | Downstream (P-032 feeds P-037) | Contract tests follow coverage defined here |

### Traceability

| Trace Point | Reference |
|-------------|-----------|
| Clarity of Intent — Stage 2 | Scope Contract, Section 3 (Definition of Done): "If a deliverable does not have a Definition of Done, it is not in scope" |
| Clarity of Intent — Stage 4 | Sprint DoD: "Automated tests written and passing in CI" |
| Eng Team Structure | QA Lead/Quality Architect (L6): "Test strategy, tool standards, DoD definition" |
| Process Architecture | Category 5, P-032; execution Program 4 (Scope Detailing) |

---

## P-033: Automated Test Framework Process

### Identification

| Field | Value |
|-------|-------|
| **Process ID** | P-033 |
| **Process Name** | Automated Test Framework Process |
| **Category** | 5 — Quality Assurance & Testing |
| **Risk Level** | HIGH |

### Purpose

SDET implements automated test suites integrated into the CI/CD pipeline so that all automated tests run on every pull request. Test failures block merge. This process translates the test architecture (P-032) into executable, CI-integrated test infrastructure that every engineer uses daily. Without this process, testing remains manual, inconsistent, and a delivery bottleneck.

### Derived From

- **Clarity of Intent**: Stage 4, Sprint DoD — "Automated tests written and passing in CI," "SAST scan clean," "Deployed to staging and smoke-tested."
- **Process Architecture**: Stage 0 research Category 5; Sprint DoD checklist; SDET role responsibilities.
- **Engineering Team Structure Guide**: SDET (L4-L6) role — "Automated test frameworks, CI integration, contract testing."

### Ownership

| Role | Agent | Responsibility |
|------|-------|---------------|
| **Primary Owner** | `qa-engineer` (SDET, L4-L6) | Implements test frameworks, configures CI integration, sets up coverage gates |
| **Supporting** | `infra-engineer` | CI/CD pipeline integration; configures PR check rules and coverage reporting in CI |
| **Supporting** | `software-engineer` (Tech Lead) | Reviews framework design for alignment with codebase patterns; approves tooling choices |

### Stages/Steps

**Step 1 — Framework Implementation**: SDET selects and implements test frameworks per the Test Architecture Document (P-032). This includes assertion libraries, test runners, mocking/stubbing frameworks, and fixture management.

**Step 2 — Local Dev Integration**: Unit test framework is integrated into the local development environment. Engineers must be able to run unit tests locally before pushing. The SDET provides a documented "how to run tests" guide and verifies it works on all team members' dev setups.

**Step 3 — CI Pipeline Integration**: Integration tests and contract tests are integrated into the CI pipeline. The SDET works with `infra-engineer` to configure test stages in the pipeline. Tests run in isolated environments (containers or ephemeral namespaces).

**Step 4 — PR Gate Configuration**: PR check rules are configured so that:
- All unit tests must pass before merge
- All integration tests must pass before merge
- Coverage thresholds (from P-032) are enforced as a gate
- No bypass is permitted without EM approval (logged and auditable)

**Step 5 — Coverage Reporting**: Coverage reporting is integrated into CI. Coverage reports are generated on every PR and posted as a PR comment or linked artifact. Coverage trends are tracked over time. A coverage gate is configured: PRs that decrease coverage below the threshold are blocked.

### Inputs

| Input | Source Process | Description |
|-------|---------------|-------------|
| Test Architecture Document | P-032 | Framework choices, coverage targets, test types per deliverable |
| CI/CD pipeline configuration | Platform team | Existing pipeline stages, runner configuration, artifact storage |
| Test tooling stack | P-032 | Approved frameworks and libraries |
| Codebase | Current state | Existing code structure, language, build system |

### Outputs/Artifacts

| Output | Format | Consumers |
|--------|--------|-----------|
| **Automated test suites** | Test code in repository alongside production code | All squad engineers |
| **CI test configuration** | Pipeline config files (e.g., `.github/workflows/`, `Jenkinsfile`, `.gitlab-ci.yml`) | Platform team, all engineers |
| **Coverage reports** | HTML/JSON reports in CI artifacts | QA Lead, TL, EM |
| **PR gate configuration** | Branch protection rules, CI check requirements | All engineers (enforced automatically) |
| **Test runner documentation** | Markdown in repo | All engineers |

### Gate/Checkpoint

**Gate Name**: Test Framework Operational Review

**Timing**: End of Sprint 1 (or the sprint in which framework setup is completed).

**Participants**: SDET, QA Lead, TL, Platform Engineer.

**Format**: 30-minute demonstration and review.

**Pass Criteria**:
- Automated tests execute on every PR without manual intervention
- Test failures block merge (demonstrated with a deliberate failing test)
- Coverage reports are generated and visible to the team on every PR
- Coverage gate is active: a PR dropping coverage below threshold is blocked (demonstrated)
- At least one engineer outside the QA team has successfully run tests locally using the documented instructions
- No EM bypass has been needed for non-exceptional reasons

### Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| PR test execution | % of PRs that trigger automated tests | 100% |
| Merge blocking | Test failures block merge without exception | Enforced (no bypass without EM approval) |
| Coverage visibility | Coverage reports available on every PR | 100% of PRs |
| Local test parity | Engineers can run tests locally | All squad engineers verified |

### Dependencies

| Dependency | Process | Direction | Nature |
|------------|---------|-----------|--------|
| Test Architecture Design | P-032 | Upstream (blocks P-033) | Framework choices and targets must be defined first |
| CI/CD pipeline | Platform team | Upstream (required infrastructure) | Pipeline must exist for test integration |
| DoD Enforcement | P-034 | Downstream (P-033 feeds P-034) | Automated CI gates are the foundation of DoD enforcement |
| Contract Testing | P-037 | Downstream (P-033 feeds P-037) | Contract test infrastructure depends on this framework |
| SAST/DAST Integration | P-039 | Downstream (P-033 feeds P-039) | Security scans integrate into the same CI pipeline |

### Traceability

| Trace Point | Reference |
|-------------|-----------|
| Clarity of Intent — Stage 4 | Sprint DoD: "Automated tests written and passing in CI" |
| Clarity of Intent — Stage 4 | Sprint DoD: "SAST scan clean (no new critical or high findings)" |
| Eng Team Structure | SDET (L4-L6): "Automated test frameworks, CI integration, contract testing" |
| Process Architecture | Category 5, P-033; execution Program 6 (parallel to dependency mapping) |

---

## P-034: Definition of Done Enforcement Process

### Identification

| Field | Value |
|-------|-------|
| **Process ID** | P-034 |
| **Process Name** | Definition of Done Enforcement Process |
| **Category** | 5 — Quality Assurance & Testing |
| **Risk Level** | HIGH |

### Purpose

Verify all Definition of Done criteria before a story is counted as complete. CI gates enforce all automatable criteria. Human verification is required for criteria that cannot be automated. This is the enforcement mechanism that prevents "almost done" from being counted as "done" — the single most common source of hidden defect backlog in sprint-based delivery.

### Derived From

- **Clarity of Intent**: Stage 4, Sprint Kickoff Brief — Section 5 (Definition of Done, Sprint Level). The six DoD criteria are: (1) code reviewed by at least one peer, (2) automated tests written and passing in CI, (3) SAST scan clean, (4) documentation updated, (5) acceptance criteria verified by PM or QA, (6) deployed to staging and smoke-tested.
- **Process Architecture**: Clarity of Intent — Stage 4 sprint DoD section; Stage 0 research Category 5.
- **Engineering Team Structure Guide**: QA Lead role — "DoD definition" and enforcement.

### Ownership

| Role | Agent | Responsibility |
|------|-------|---------------|
| **Primary Owner** | `qa-engineer` | Verifies non-automated DoD criteria; maintains DoD checklist; flags non-compliant story closures |
| **Supporting** | `product-manager` | Verifies business acceptance criteria (DoD item 5) |
| **Supporting** | `software-engineer` | Self-verifies automated criteria before requesting QA verification; ensures code review (DoD item 1) |

### Stages/Steps

**Step 1 — Engineer Self-Check**: The implementing engineer completes development and runs a DoD self-check against all six criteria. This is a mandatory pre-verification step before requesting formal QA review.

Self-check items:
- [ ] Code reviewed by at least one peer (PR approved)
- [ ] Automated tests written and passing in CI
- [ ] SAST scan clean (no new critical or high findings)
- [ ] Documentation updated (API docs, runbook, README as applicable)
- [ ] Acceptance criteria verified locally
- [ ] Deployed to staging and smoke-tested

**Step 2 — CI Gate Verification**: CI automatically verifies the automatable criteria:
- All automated tests pass (P-033 infrastructure)
- SAST scan clean (P-039 infrastructure)
- Coverage thresholds met (P-033 coverage gate)
- Code review approved (branch protection rule)

If any CI gate fails, the story cannot proceed to human verification. The engineer must fix the failure first.

**Step 3 — QA Manual Verification**: QA engineer manually verifies criteria that cannot be automated:
- Acceptance criteria met through exploratory testing
- Edge cases and error paths behave correctly
- UI/UX matches design specifications (if applicable)
- Accessibility requirements met (if applicable)

**Step 4 — PM Business Acceptance**: PM or designated product representative verifies that the story delivers the intended business value:
- Acceptance criteria met from a product perspective
- User experience aligns with the Scope Contract deliverable intent
- No unintended side effects on related features

**Step 5 — Story Completion**: Only when ALL criteria are confirmed — automated CI gates PASS, QA manual verification PASS, PM acceptance PASS — is the story marked complete. The verification is recorded as a completion record attached to the story.

### Inputs

| Input | Source Process | Description |
|-------|---------------|-------------|
| Sprint story with acceptance criteria | P-024 (Story Creation) | Story must have written acceptance criteria |
| DoD checklist | Clarity of Intent Stage 4 | The six standard DoD items |
| CI gate output | P-033 (Automated Test Framework) | Automated test results, SAST results, coverage report |
| Staging deployment | Sprint execution | Story must be deployed to staging for verification |

### Outputs/Artifacts

| Output | Format | Consumers |
|--------|--------|-----------|
| **Story completion verification record** | Structured record per story (checklist with PASS/FAIL per criterion, verifier name, timestamp) | EM (sprint metrics), PM (sprint review), auditors |
| **DoD compliance report** | Aggregated per-sprint summary of DoD compliance | EM, QA Lead, Director |

The verification record contains:
- Story ID and title
- Each DoD criterion with PASS/FAIL status
- CI gate results (linked)
- QA verifier name and timestamp
- PM verifier name and timestamp (if applicable)
- Any exceptions or deferred items with justification

### Gate/Checkpoint

**Gate Name**: Per-Story Completion Gate

**Timing**: Applied to every story before it moves to the "Done" column.

**Participants**: Implementing engineer, QA engineer, PM (for business-critical stories).

**Format**: Continuous — not a scheduled meeting. Each story passes through this gate individually.

**Pass Criteria**:
- All six DoD criteria are marked PASS
- No CI gate failures remain unresolved
- QA manual verification is recorded
- PM acceptance is recorded (for stories with business acceptance criteria)
- If any criterion has a justified exception, it is documented and approved by the EM

### Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| DoD documentation rate | % of stories with a complete verification record before closure | 100% |
| Zero unverified closures | Stories closed without DoD verification | 0 per sprint |
| CI gate enforcement | % of stories that pass CI gates before manual verification begins | 100% |
| Defect escape rate | Defects found in production that would have been caught by DoD enforcement | Declining quarter-over-quarter |

### Dependencies

| Dependency | Process | Direction | Nature |
|------------|---------|-----------|--------|
| Automated Test Framework | P-033 | Upstream (blocks P-034) | CI gates must exist before DoD can be enforced automatically |
| Story acceptance criteria | P-024 | Upstream (blocks P-034) | Stories must have written criteria to verify against |
| Acceptance Criteria Verification | P-036 | Downstream (P-034 triggers P-036) | DoD enforcement includes acceptance verification as one criterion |
| Feature development complete | P-031 | Upstream (blocks P-034) | Story must be implemented before verification |
| Sprint Review | P-027 | Downstream (P-034 feeds P-027) | Only DoD-verified stories are demonstrated at sprint review |

### Traceability

| Trace Point | Reference |
|-------------|-----------|
| Clarity of Intent — Stage 4 | Sprint Kickoff Brief, Section 5: all six DoD items listed verbatim |
| Clarity of Intent — Stage 2 | Scope Contract, Section 3: "If a deliverable does not have a Definition of Done, it is not in scope" |
| Eng Team Structure | QA Lead role: "DoD definition"; Sprint DoD is a team-level standard |
| Process Architecture | Category 5, P-034; execution Program 13 (Quality Gates, blockedBy P-031) |

---

## P-035: Performance Testing Process

### Identification

| Field | Value |
|-------|-------|
| **Process ID** | P-035 |
| **Process Name** | Performance Testing Process |
| **Category** | 5 — Quality Assurance & Testing |
| **Risk Level** | HIGH |

### Purpose

Establish performance baselines before optimization and validate P50/P95/P99 latency against SLOs before release. Performance testing is part of the Definition of Done for performance-sensitive deliverables. This process prevents performance regressions from reaching production, where they manifest as SLO violations and incidents.

### Derived From

- **Clarity of Intent**: Stage 2, Scope Contract — Section 5 (Success Metrics) defines measurable performance targets. Section 6 (Assumptions and Risks) captures performance risks. Stage 4, Sprint DoD — "Deployed to staging and smoke-tested" implies staging validation including performance.
- **Process Architecture**: Stage 0 research Category 5; Performance Engineer role; SRE SLO responsibilities.
- **Engineering Team Structure Guide**: Performance Engineer (L5-L6) — "Load testing, capacity planning, SLA validation."

### Ownership

| Role | Agent | Responsibility |
|------|-------|---------------|
| **Primary Owner** | `qa-engineer` (Performance Engineer, L5-L6) | Writes performance test scripts, runs load tests, produces performance reports |
| **Supporting** | `sre` | Provides SLO definitions, infrastructure capacity information, and production traffic patterns for realistic load modeling |
| **Supporting** | `software-engineer` (Tech Lead) | Reviews performance budgets for technical feasibility; assists with performance optimization when SLO violations are found |

### Stages/Steps

**Step 1 — Performance Budget Definition**: Performance budgets are defined per deliverable during Stage 2 (Scope Contract success metrics). The Performance Engineer extracts these and creates a Performance Budget Table mapping each deliverable to its P50/P95/P99 latency targets, throughput targets, and error rate thresholds.

**Step 2 — Test Script Authoring**: Performance Engineer writes load test scripts using the organization's approved performance testing tooling (e.g., k6, Gatling, Locust, JMeter). Scripts simulate realistic user behavior patterns based on production traffic data provided by SRE.

**Step 3 — Baseline Establishment**: Before any code changes are deployed, the Performance Engineer runs the test scripts against the current system to establish a baseline. This baseline is the reference point for detecting regressions. Baseline results are documented and versioned.

**Step 4 — Load Test Execution**: After development is complete and the feature is deployed to the staging environment, the Performance Engineer runs the full load test suite. The test simulates expected production load (and optionally 2x-3x expected load for headroom validation).

**Step 5 — Results Analysis**: P50/P95/P99 latency results are compared against:
- SLO targets (from P-054 via SRE)
- Performance budgets (from Scope Contract)
- Baseline measurements (from Step 3)

Any metric that exceeds the target is flagged as a performance violation.

**Step 6 — Violation Remediation or Release Block**: If any SLO violations are detected:
- The violation is documented with specific metrics and the delta from target
- The release is blocked until the violation is resolved
- The TL and EM are notified immediately
- A remediation plan is created (optimization task or architecture change)
- The load test is re-run after remediation to confirm the fix

### Inputs

| Input | Source Process | Description |
|-------|---------------|-------------|
| SLO definitions | P-054 (SLO Definition) | Latency, throughput, and error rate targets |
| Performance budgets | P-032 (Test Architecture) / Scope Contract | Per-deliverable performance targets |
| Staging environment | P-045 (Infrastructure) | Environment capable of running load tests |
| Production traffic patterns | SRE | Realistic user behavior data for load modeling |

### Outputs/Artifacts

| Output | Format | Consumers |
|--------|--------|-----------|
| **Performance test scripts** | Code in repository (e.g., k6 scripts, Gatling simulations) | Performance Engineer, SRE |
| **Baseline performance report** | Markdown/HTML report with P50/P95/P99 metrics | TL, EM, SRE |
| **Load test results report** | Markdown/HTML report with P50/P95/P99 metrics, comparison to baseline and SLOs | TL, EM, SRE, PM, Release Manager |
| **SLO compliance declaration** | PASS/FAIL per SLO with supporting data | Release gate (P-048), CAB (P-076) |
| **Blocking defect list** | List of SLO violations with remediation plan (if any) | TL, EM |

### Gate/Checkpoint

**Gate Name**: Pre-Launch Performance Gate

**Timing**: After feature development is complete (P-031), before production deployment (P-048).

**Participants**: Performance Engineer, TL, SRE, EM.

**Format**: Asynchronous report review with escalation meeting if violations are found.

**Pass Criteria**:
- P95 latency is within SLO bounds under expected production load
- No performance regression from baseline (or regression is within acceptable tolerance, defined as <5% degradation)
- Load test simulates realistic production traffic patterns (validated by SRE)
- Error rate under load does not exceed SLO error budget
- Results are reproducible (at least two consecutive test runs produce consistent results)

### Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| SLO compliance | % of deliverables meeting P95 latency SLO at release | 100% |
| Baseline coverage | % of performance-sensitive deliverables with documented baselines | 100% |
| Realistic load modeling | SRE validates load test traffic patterns | Validated per release |
| Regression prevention | Performance regressions caught before production | 0 regressions escaping to production |

### Dependencies

| Dependency | Process | Direction | Nature |
|------------|---------|-----------|--------|
| SLO definitions | P-054 | Upstream (informs P-035) | Cannot define performance budgets without SLOs |
| Test Architecture Design | P-032 | Upstream (informs P-035) | Performance test strategy defined in test architecture |
| Infrastructure for load testing | P-045 | Upstream (required infrastructure) | Staging environment must support load testing |
| Feature development complete | P-031 | Upstream (blocks P-035 execution) | Code must be deployed to staging before load testing |
| Production Release | P-048 | Downstream (P-035 gates P-048) | Performance results must pass before release |
| CAB Review | P-076 | Downstream (P-035 informs P-076) | Performance compliance is a CAB input for HIGH-risk changes |

### Traceability

| Trace Point | Reference |
|-------------|-----------|
| Clarity of Intent — Stage 2 | Scope Contract, Section 5 (Success Metrics): performance targets with baselines and timelines |
| Clarity of Intent — Stage 2 | Scope Contract, Section 6 (Risks): "Tokenization adds latency to checkout flow" — performance risk example |
| Eng Team Structure | Performance Engineer (L5-L6): "Load testing, capacity planning, SLA validation" |
| Process Architecture | Category 5, P-035; execution Program 13 (Quality Gates, pre-release) |

---

## P-036: Acceptance Criteria Verification Process

### Identification

| Field | Value |
|-------|-------|
| **Process ID** | P-036 |
| **Process Name** | Acceptance Criteria Verification Process |
| **Category** | 5 — Quality Assurance & Testing |
| **Risk Level** | HIGH |

### Purpose

PM or QA formally verifies each story against its acceptance criteria before story closure. This is the final human gate before a story enters the "done" column. It ensures that the story delivers the intended behavior from a product perspective, not just that the code passes technical checks. Self-verified acceptance criteria are unreliable — this process mandates independent verification.

### Derived From

- **Clarity of Intent**: Stage 4, Sprint DoD — "Acceptance criteria verified by PM or QA." Stage 2, Scope Contract — Section 3 (Definition of Done) uses "It is done when..." format with testable conditions. Stage 4, Sprint Kickoff Brief — Section 3 (Stories and Acceptance Criteria) in "Given/When/Then" format.
- **Process Architecture**: Clarity of Intent — Stage 4 sprint DoD checklist.
- **Engineering Team Structure Guide**: PM role — validates acceptance criteria; QA role — alternate verifier.

### Ownership

| Role | Agent | Responsibility |
|------|-------|---------------|
| **Primary Owner** | `product-manager` | Verifies stories against business acceptance criteria; records PASS/FAIL per criterion |
| **Supporting** | `qa-engineer` | Alternate verifier when PM is unavailable; performs deeper exploratory testing alongside acceptance verification |

### Stages/Steps

**Step 1 — Engineer Signals Readiness**: The implementing engineer confirms the story is ready for acceptance verification. Pre-conditions that must be true before signaling readiness:
- All CI gates pass (P-034 Step 2)
- Code is deployed to staging
- The engineer has self-verified acceptance criteria locally

**Step 2 — Acceptance Testing**: The PM (or QA as alternate) tests the story against each acceptance criterion. Each criterion is individually evaluated:
- **Given/When/Then** criteria: the verifier executes the scenario exactly as written
- **Checklist criteria**: each item is verified independently
- Edge cases and error paths are tested if they are part of the acceptance criteria

**Step 3 — Criterion-Level PASS/FAIL**: Each acceptance criterion is marked individually as PASS or FAIL. A story can have a mix of passing and failing criteria.

**Step 4 — FAIL Handling**: If any criterion FAILS:
- The story is reverted to "In Progress" status
- Specific, actionable feedback is provided to the engineer (what failed, expected vs. actual behavior, steps to reproduce)
- The engineer addresses the failure and re-signals readiness
- The failed criteria are re-verified (passing criteria do not need re-verification unless the fix could have affected them)

**Step 5 — PASS and Completion**: When ALL criteria PASS:
- The PM/QA records the verification (verifier name, timestamp, criterion-level results)
- The story is eligible to be marked complete (subject to remaining DoD items in P-034)

### Inputs

| Input | Source Process | Description |
|-------|---------------|-------------|
| Sprint story with acceptance criteria | P-024 (Story Creation) | Stories must have written, testable acceptance criteria |
| Staging deployment | Sprint execution | Feature must be deployed and accessible for verification |
| CI gate results | P-034 (DoD Enforcement) | All automated CI gates must pass before acceptance testing |

### Outputs/Artifacts

| Output | Format | Consumers |
|--------|--------|-----------|
| **Acceptance verification record** | Per-story record: PASS/FAIL per criterion, verifier identity, timestamp, feedback (if FAIL) | EM (sprint metrics), DoD enforcement (P-034), sprint review (P-027) |

### Gate/Checkpoint

**Gate Name**: Per-Story Acceptance Gate

**Timing**: After CI gates pass (P-034 Step 2), before story is marked "Done."

**Participants**: PM or QA (verifier), implementing engineer (available for questions).

**Format**: Continuous — each story passes through this gate individually. Not a scheduled meeting.

**Pass Criteria**:
- Every acceptance criterion has a recorded PASS/FAIL result
- Verification was performed by someone other than the implementing engineer
- All criteria PASS (or exceptions are documented and approved by EM)
- Verification was performed against staging deployment, not local environment

### Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Verification coverage | % of stories with recorded acceptance verification | 100% |
| Independent verification | % of verifications performed by non-software-engineer | 100% |
| Cycle time | Median time from "ready for acceptance" to verification complete | < 4 hours (business hours) |
| Rejection quality | Rejected stories include specific, actionable feedback | 100% of rejections |

### Dependencies

| Dependency | Process | Direction | Nature |
|------------|---------|-----------|--------|
| DoD Enforcement (CI gates) | P-034 | Upstream (blocks P-036) | CI gates must pass before human acceptance testing |
| Story acceptance criteria | P-024 | Upstream (blocks P-036) | Stories must have written criteria to verify against |
| Feature development | P-031 | Upstream (blocks P-036) | Story must be implemented and deployed to staging |
| Sprint Review | P-027 | Downstream (P-036 feeds P-027) | Only accepted stories are demonstrated at sprint review |

### Traceability

| Trace Point | Reference |
|-------------|-----------|
| Clarity of Intent — Stage 4 | Sprint DoD: "Acceptance criteria verified by PM or QA" |
| Clarity of Intent — Stage 4 | Sprint Kickoff Brief, Section 3: Stories written with acceptance criteria in "Given/When/Then" format |
| Clarity of Intent — Stage 2 | Scope Contract, Section 3: "It is done when..." testable conditions per deliverable |
| Eng Team Structure | PM role: backlog ownership, acceptance criteria definition and verification |
| Process Architecture | Category 5, P-036; execution Program 13 (Quality Gates, blockedBy P-031 and P-034) |

---

## P-037: Contract Testing Process

### Identification

| Field | Value |
|-------|-------|
| **Process ID** | P-037 |
| **Process Name** | Contract Testing Process |
| **Category** | 5 — Quality Assurance & Testing |
| **Risk Level** | MEDIUM |

### Purpose

Validate API contracts between services on every PR that touches API definitions. Prevent consumer services from breaking when provider APIs change. In a microservice architecture, API contract breakage is a primary source of cross-team incidents. Consumer-driven contract testing shifts this detection to the PR level, before breaking changes can be merged.

### Derived From

- **Clarity of Intent**: Stage 2, Scope Contract — deliverables include API endpoints with OpenAPI specs. Stage 3, Dependency Charter — Section 1 (Dependency Register) identifies API dependencies between teams. Stage 4, Sprint DoD — "Automated tests written and passing in CI" includes contract tests.
- **Process Architecture**: Stage 0 research Category 5; SDET role; microservice architecture patterns.
- **Engineering Team Structure Guide**: SDET (L4-L6) — "Automated test frameworks, CI integration, contract testing."

### Ownership

| Role | Agent | Responsibility |
|------|-------|---------------|
| **Primary Owner** | `qa-engineer` (SDET, L4-L6) | Authors consumer-driven contract tests, configures CI contract gate, maintains contract version history |
| **Supporting** | `software-engineer` (Tech Lead) | Ensures consumer-driven contracts are authored for all inter-service APIs; reviews contract test design |
| **Supporting** | `infra-engineer` | CI pipeline integration for contract test execution on API-touching PRs |

### Stages/Steps

**Step 1 — API Contract Inventory**: SDET works with the TL to identify all service-to-service API contracts in the project scope. Each contract is documented with:
- Provider service name
- Consumer service name(s)
- API endpoint(s) covered
- OpenAPI specification location
- Contract test responsibility (which team writes/maintains)

**Step 2 — Consumer-Driven Contract Authoring**: For every API consumer, the SDET (working with the consumer team) authors contract tests that define the consumer's expectations of the provider API. These tests specify:
- Expected request/response schemas
- Required fields and their types
- Error response formats
- Pagination contracts
- Authentication/authorization requirements

Consumer-driven contracts ensure that the provider does not break consumers. The provider can add new fields or endpoints, but cannot remove or change what consumers depend on.

**Step 3 — CI Integration**: Contract tests are integrated into the CI pipeline. Configuration rules:
- Contract tests run on every PR that touches API definitions (OpenAPI specs, protobuf files, GraphQL schemas, or code in API controller/handler directories)
- Contract test execution is triggered by file-path filters in CI
- Tests run against a contract broker or mock provider (not against live services)

**Step 4 — Merge Gate Enforcement**: Contract violations block merge. When a provider PR breaks a consumer contract:
- The PR is blocked with a clear error message identifying which consumer contract was broken
- The provider team must either: (a) update their change to maintain backward compatibility, or (b) coordinate with the consumer team to update the contract (versioned API change)
- No bypass without EM approval from both provider and consumer teams

**Step 5 — Contract Version History**: Contract versions are maintained in source control alongside the API code. Version history provides:
- Traceability of contract changes over time
- Rollback capability if a contract change causes issues
- Audit trail for API compatibility decisions

### Inputs

| Input | Source Process | Description |
|-------|---------------|-------------|
| OpenAPI specifications | API development | Current API specs for all inter-service contracts |
| Consumer test scenarios | Consumer teams | What each consumer depends on from the provider API |
| CI pipeline configuration | P-033 (Automated Test Framework) | Pipeline infrastructure for running contract tests |
| Dependency Charter | P-015 (Dependency Registration) | Identifies which teams depend on which APIs |

### Outputs/Artifacts

| Output | Format | Consumers |
|--------|--------|-----------|
| **Contract test suite** | Test code in repository (e.g., Pact tests, Spring Cloud Contract, custom contract tests) | Provider and consumer teams |
| **CI contract gate** | Pipeline configuration with file-path triggers | All engineers working on API code |
| **API compatibility reports** | Per-PR report showing contract verification results | TL, EM, consumer teams |
| **Contract version history** | Versioned contract files in source control | All teams, auditors |

### Gate/Checkpoint

**Gate Name**: Per-PR Contract Gate

**Timing**: On every PR that modifies API definitions or API-handling code.

**Participants**: Automated (CI pipeline). Escalation to TL/EM for contract disputes.

**Format**: Automated CI check. No manual intervention for passing contracts.

**Pass Criteria**:
- All consumer-driven contract tests pass against the proposed API change
- No existing consumer contract is broken by the change
- If a new API endpoint is introduced, at least one consumer contract test exists before merge
- Contract version is incremented if the contract semantics change

### Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Contract coverage | % of service-to-service APIs covered by contract tests | 100% |
| Break prevention | API-breaking changes blocked at PR level | 0 breaking changes merged without contract test failure |
| CI integration | Contract tests run automatically on API-touching PRs | 100% of relevant PRs |
| Version tracking | Contract changes tracked in source control | 100% of contract modifications versioned |

### Dependencies

| Dependency | Process | Direction | Nature |
|------------|---------|-----------|--------|
| Automated Test Framework | P-033 | Upstream (blocks P-037) | CI infrastructure must exist for contract test execution |
| Test Architecture Design | P-032 | Upstream (informs P-037) | Contract test coverage is defined in the test architecture |
| API Documentation | P-058 | Bidirectional | Contract tests validate against OpenAPI specs; contract test results inform API documentation accuracy |
| Dependency Registration | P-015 | Upstream (informs P-037) | API dependencies between teams identify which contracts need tests |

### Traceability

| Trace Point | Reference |
|-------------|-----------|
| Clarity of Intent — Stage 3 | Dependency Charter, Section 1: API dependencies between teams (e.g., "Mobile Squad depends on Payments Squad for Saved Payment Method API") |
| Clarity of Intent — Stage 4 | Sprint DoD: "Automated tests written and passing in CI" — includes contract tests |
| Clarity of Intent — Stage 2 | Scope Contract, Section 2 (Deliverables): API deliverables with OpenAPI specs |
| Eng Team Structure | SDET (L4-L6): "contract testing" listed as key output |
| Process Architecture | Category 5, P-037; execution Program 13 (Quality Gates, per-PR) |

---

## Cross-Process Dependency Map

The six QA processes form a layered dependency chain. P-032 (design) feeds P-033 (implementation), which enables P-034 (enforcement), P-035 (performance), P-036 (acceptance), and P-037 (contracts).

```
External Inputs
│
├── P-013 (Scope Lock) ──────────────────────────────────────┐
├── P-054 (SLO Definition) ───────────────────────┐          │
├── P-024 (Story Criteria) ────────────────┐      │          │
└── P-031 (Feature Development) ────┐      │      │          │
                                    │      │      │          │
                                    │      │      │          ▼
                                    │      │      │   ┌─────────────┐
                                    │      │      │   │   P-032     │
                                    │      │      │   │ Test Arch   │
                                    │      │      │   │ Design      │
                                    │      │      │   └──────┬──────┘
                                    │      │      │          │
                                    │      │      │          ▼
                                    │      │      │   ┌─────────────┐
                                    │      │      │   │   P-033     │
                                    │      │      │   │ Automated   │
                                    │      │      │   │ Test Frmwk  │
                                    │      │      │   └──┬───┬───┬──┘
                                    │      │      │      │   │   │
                              ┌─────┘      │      │      │   │   │
                              │            │      │      │   │   │
                              ▼            ▼      ▼      ▼   │   │
                       ┌─────────────────────────────────┐   │   │
                       │          P-034                   │   │   │
                       │  Definition of Done Enforcement  │   │   │
                       └──────────────┬──────────────────┘   │   │
                                      │                      │   │
                              ┌───────┘                      │   │
                              ▼                              ▼   │
                       ┌─────────────┐              ┌────────────┴──┐
                       │   P-036     │              │    P-035      │
                       │ Acceptance  │              │ Performance   │
                       │ Criteria    │              │ Testing       │
                       │ Verify      │              │               │
                       └─────────────┘              └───────────────┘
                                                            │
                       ┌─────────────┐                      │
                       │   P-037     │                      │
                       │ Contract    │──────────────────────┘
                       │ Testing     │    (both gate P-048)
                       └─────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ P-048 Production  │
                    │ Release Mgmt     │
                    │ (via P-076 CAB)  │
                    └───────────────────┘
```

### Execution Sequence

Per the Process Architecture execution programs:

| Program | Processes | Timing |
|---------|-----------|--------|
| Program 4 (Scope Detailing) | P-032 — Test Architecture Design | After Scope Lock, before Sprint 1 |
| Program 6 (Dependency Mapping, parallel) | P-033 — Automated Test Framework | After P-032, parallel to dependency mapping |
| Program 13 (Quality Gates) | P-034, P-035, P-036, P-037 | After feature development (P-031); P-037 runs per-PR during development |

### Critical Path Involvement

P-034 (DoD Enforcement) is on the project critical path:

```
... → P-031 (Feature Dev) → P-034 (DoD Enforcement) → P-036 (Acceptance) → P-027 (Sprint Review) → ...
```

P-035 and P-037 are pre-release gates that can run in parallel with P-034/P-036 but must complete before P-048 (Production Release).

---

## Category-Level Traceability Matrix

| Process | Clarity of Intent Stage | Clarity of Intent Artifact | Specific Section | Eng Team Structure Role |
|---------|------------------------|---------------------------|-----------------|------------------------|
| P-032 | Stage 2 | Scope Contract | Section 3 (DoD), Section 5 (Success Metrics) | QA Lead/Quality Architect (L6) |
| P-033 | Stage 4 | Sprint Kickoff Brief | Section 5 (Sprint-level DoD): "Automated tests written and passing in CI" | SDET (L4-L6) |
| P-034 | Stage 4 | Sprint Kickoff Brief | Section 5 (Sprint-level DoD): all six criteria | QA Lead + QA Engineer |
| P-035 | Stage 2 | Scope Contract | Section 5 (Success Metrics), Section 6 (Risks) | Performance Engineer (L5-L6) |
| P-036 | Stage 4 | Sprint Kickoff Brief | Section 3 (Stories + Acceptance Criteria), Section 5 (DoD item 5) | PM (primary), QA (alternate) |
| P-037 | Stage 3 | Dependency Charter | Section 1 (Dependency Register — API dependencies) | SDET (L4-L6) |

### Agent Responsibility Summary

| Agent | Primary Owner | Supporting Role |
|-------|--------------|-----------------|
| `qa-engineer` | P-032, P-033, P-034, P-035, P-037 | P-036 (alternate verifier) |
| `product-manager` | P-036 | P-034 (business acceptance) |
| `software-engineer` | — | P-032 (technical context), P-033 (framework review), P-034 (self-check), P-037 (consumer contracts) |
| `infra-engineer` | — | P-033 (CI/CD integration), P-037 (CI integration) |
| `sre` | — | P-032 (SLO alignment), P-035 (SLO definitions, traffic patterns) |

---

*End of specification. Six processes (P-032 through P-037) fully specified with stages, inputs, outputs, gates, success criteria, dependencies, and traceability.*

---

## Cross-Category Dependencies

### Dependencies FROM Other Categories (Inputs)

| Source Process | Source Category | Consuming Process | Nature |
|---------------|----------------|-------------------|--------|
| P-013 (Scope Lock Gate) | Cat 2: Scope & Contract | P-032 (Test Architecture Design) | Deliverables and DoD define test targets |
| P-054 (SLO Definition) | Cat 9: SRE & Operations | P-035 (Performance Testing) | SLOs define performance test thresholds |
| P-045 (Infrastructure Provisioning) | Cat 7: Infrastructure | P-035 (Performance Testing) | Infrastructure for load test environments |
| P-031 (Feature Development) | Cat 4: Sprint & Delivery | P-034 (DoD Enforcement) | Story completion triggers DoD verification |
| P-024 (Story Writing) | Cat 4: Sprint & Delivery | P-034 (DoD Enforcement) | Stories must have criteria |

### Dependencies TO Other Categories (Outputs)

| Providing Process | Consuming Process | Target Category | Nature |
|------------------|-------------------|-----------------|--------|
| P-032 (Test Architecture Design) | P-033 (Automated Test Framework) | Cat 5 (self) | Test architecture drives framework |
| P-033 (Automated Test Framework) | P-039 (SAST/DAST CI Integration) | Cat 6: Security | CI/CD infrastructure required |
| P-034 (DoD Enforcement) | P-048 (Production Release Mgmt) | Cat 7: Infrastructure | DoD verification before release |
| P-035 (Performance Testing) | P-048 (Production Release Mgmt) | Cat 7: Infrastructure | Performance tests passed before release |
| P-035 (Performance Testing) | P-076 (Pre-Launch Risk Review) | Cat 13: Risk & Change | Performance results for CAB |
| P-037 (Contract Testing) | P-058 (API Documentation) | Cat 10: Documentation | Contract tests validate against spec |

## Agent Assignments Summary

| Process | Primary Owner | Supporting Agents |
|---------|--------------|-------------------|
| P-032: Test Architecture Design | qa-engineer (QA Lead) | software-engineer (TL), sre |
| P-033: Automated Test Framework | qa-engineer (SDET) | infra-engineer, software-engineer (TL) |
| P-034: Definition of Done Enforcement | qa-engineer | product-manager, software-engineer |
| P-035: Performance Testing | qa-engineer (Performance Engineer) | sre, software-engineer (TL) |
| P-036: Acceptance Criteria Verification | product-manager | qa-engineer |
| P-037: Contract Testing | qa-engineer (SDET) | software-engineer (TL), infra-engineer |
