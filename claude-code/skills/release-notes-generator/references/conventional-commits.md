# Conventional Commits Cheat-Sheet

Reference: https://www.conventionalcommits.org

Format: `<type>(<optional-scope>)!: <description>`

## Types — included in release notes

| Type | Section in release notes | Description |
|------|--------------------------|-------------|
| `feat` | 🚀 Features | A new feature or user-facing capability |
| `fix` | 🐛 Fixes | A bug fix |
| `perf` | ⚡ Performance | A performance improvement (cite before/after if possible) |
| `security` | 🔒 Security | A security fix (also use `fix(sec):` style) |

## Types — excluded by default

These types are typically internal and excluded from release notes:

| Type | Description | Why excluded |
|------|-------------|--------------|
| `chore` | Build process, tooling, dependencies (non-user-facing) | Not user-impacting |
| `refactor` | Code restructuring with no behavior change | Not user-impacting |
| `test` | Adding/modifying tests | Not user-impacting |
| `style` | Formatting, whitespace, semicolons | Not user-impacting |
| `docs` | Documentation only | Excluded UNLESS user-facing API docs |
| `ci` | CI/CD config | Not user-impacting |
| `build` | Build system | Not user-impacting |

Override: include any of these by adding `--include-types <type>` to the parser.

## Breaking changes

Mark breaking changes in EITHER way:

### Option 1: Bang notation
```
feat!: remove deprecated /v1/inventory/stock endpoint
```

### Option 2: BREAKING CHANGE footer
```
feat: rewrite stock-levels API for multi-region support

BREAKING CHANGE: /v1/inventory/stock removed. Migrate to /v2/inventory/stock-levels.
See docs/api-migration-v1-to-v2.md for field mapping.
```

Either form triggers the parser to put the commit in the `⚠️ Breaking Changes` section.

## Scopes

Optional scope in parentheses scopes the change to a subsystem:

```
feat(inventory): add multi-region stock query
fix(checkout): resolve race in cart totalization
perf(api): reduce checkout latency by 40% via N+1 elimination
```

Scopes are extracted into the parser's `scope` field per commit, useful for filtering or grouping in custom rendering.

## Issue / PR references

Reference issues and PRs in the commit body OR description:

```
fix: resolve cart race condition (#1255)

Closes #1240, #1242
```

The parser extracts `#NNNN` references and links them to the configured base URL (e.g., `https://github.com/example/repo/issues/NNNN`).

## Author / Co-author

Use standard `Co-authored-by:` trailers:

```
feat: multi-region failover

Co-authored-by: Bob <bob@example.com>
```

The parser collects unique authors (including co-authors) into the `Contributors` list.

## Examples — full commit messages

### Feature with breaking change

```
feat(api)!: rewrite stock-levels endpoint for multi-region

The legacy /v1/inventory/stock returned a flat list with no region
support and 30s+ response times at scale. New /v2/inventory/stock-levels
returns paginated, per-region results.

BREAKING CHANGE: /v1/inventory/stock removed. Migration guide:
docs/api-migration-v1-to-v2.md.

Closes #1180

Co-authored-by: Alice <alice@example.com>
```

→ Categorized as: `feat`, scope `api`, breaking, author `Alice`, references `#1180`

### Performance fix with metrics

```
perf(checkout): eliminate N+1 in cart totalization

Before: 380ms p95
After: 230ms p95

Achieved by batching the per-line-item tax lookups. See ADR-0019
for the architecture decision.

Refs #1244
```

→ Categorized as: `perf`, scope `checkout`, references `#1244`

### Security fix

```
fix(sec): bump requests to 2.32.0 for CVE-2026-1234

The CVE allows... [details].

Severity: HIGH per CVSS 8.1.

Closes #1250
```

→ Categorized as: `security`, references `#1250`, severity tag extracted

## Anti-patterns

| Anti-pattern | Fix |
|--------------|-----|
| `feat: stuff` | Be specific about what feature |
| `update README` | Use `docs:` prefix; consider whether it belongs in release notes |
| `WIP` or `tmp` commits | Squash before merging |
| Multiple types in one commit (`feat+fix:`) | Split into separate commits |
| Missing prefix entirely | The parser will categorize as `unknown` and skip from release notes |
