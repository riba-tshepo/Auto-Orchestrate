# Skill Anti-Patterns

Common anti-patterns to avoid when implementing skills.
Reference this file: `@_shared/templates/anti-patterns.md`

---

## Output Anti-Patterns

| Pattern | Problem | Solution |
|---------|---------|----------|
| Returning full content | Bloats orchestrator context | Write to file, return summary only |
| Skipping manifest | Orchestrator can't find findings | Always append manifest entry |
| Multi-line manifest | Invalid JSON | Single line, no pretty-print |
| Forgetting task lifecycle | Task not tracked | Always complete via TaskUpdate |

---

## Research Anti-Patterns

| Pattern | Problem | Solution |
|---------|---------|----------|
| No sources cited | Findings unverifiable | Always cite sources |
| Outdated sources | Stale recommendations | Prefer sources <2 years old |
| Single source | Narrow perspective | Cross-reference multiple sources |
| No recommendations | Findings not actionable | Always include next steps |

---

## Implementation Anti-Patterns

| Pattern | Problem | Solution |
|---------|---------|----------|
| Missing validation | Invalid input crashes | Always validate inputs |
| No error handling | Silent failures | Return proper exit codes |
| Missing docs | Usage unclear | Document function signatures |
| No syntax check | Broken code shipped | Verify syntax before completing |

---

## Testing Anti-Patterns

| Pattern | Problem | Solution |
|---------|---------|----------|
| Non-idempotent tests | Tests affect each other | Always use temp directories |
| Missing teardown | Artifacts left behind | Always clean up in teardown |
| Hardcoded paths | Tests fail elsewhere | Use `$TEST_DIR` and relative paths |
| Order-dependent tests | Tests fail in isolation | Each test must be independent |
| Missing error cases | Only happy path covered | Test all error conditions |
| Vague test names | Unclear what's being tested | Use descriptive behavior names |
| Testing implementation | Fragile tests | Test behavior, not internals |

---

## Validation Anti-Patterns

| Pattern | Problem | Solution |
|---------|---------|----------|
| Skipping failing checks | Incomplete report | Run all checks, report all failures |
| Vague findings | Unclear remediation | Specific issue + file/line + fix |
| Missing severity | Can't prioritize | Always classify: critical/warning/suggestion |
| No remediation | Findings not actionable | Always provide fix for FAIL/PARTIAL |

---

## Security Anti-Patterns

| Pattern | Problem | Solution |
|---------|---------|----------|
| False positives | Too many alerts | Whitelist known-safe patterns |
| Ignoring medium | Accumulating debt | Fix with related changes |
| No remediation | Findings not actionable | Always provide fix guidance |
| Scan once | New vulns introduced | Add to CI/CD pipeline |
