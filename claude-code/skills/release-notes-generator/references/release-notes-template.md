# Release Notes Template

Output filename: `CHANGELOG.md` (prepend) or `release-notes-draft.md` (per-release).

## Template

```markdown
## [<version>] — <YYYY-MM-DD>

> **Highlights**: <one-paragraph summary of the 3–5 most user-impactful changes>

### 🚀 Features

- **<title>** ([#123](pr-link)) — <one-line description>. By @<author>.
- ...

### 🐛 Fixes

- **<title>** ([#124](pr-link)) — <description>. By @<author>.
- ...

### ⚡ Performance

- **<title>** ([#125](pr-link)) — <description with before/after metrics>. By @<author>.
- ...

### 🔒 Security

- **<title>** ([CVE-YYYY-NNNN](cve-link)) — <description>. Severity: <CRITICAL|HIGH|MEDIUM|LOW>. By @<author>.
- ...

### ⚠️ Breaking Changes

> Read this section before upgrading.

#### <Breaking change title>

**What changed**: <description>

**Why**: <reason for the breaking change>

**Migration**: <step-by-step migration guide>

```diff
- old_api.deprecated_method()
+ new_api.replacement_method()
```

**Affected users**: <who needs to act — all consumers, only those using X feature, etc.>

[repeat per breaking change]

### 📦 Dependencies

- Bumped `<package>` from `<old-version>` to `<new-version>` ([changelog](link)). Reason: <CVE fix | feature | maintenance>.
- ...

### 👥 Contributors

Thanks to everyone who contributed to this release:

@author1, @author2, @author3 — and <N> first-time contributors!

---
```

## Worked example

```markdown
## [2.4.0] — 2026-04-25

> **Highlights**: Multi-region failover for the inventory service, 40% latency reduction in checkout API, and a new admin export feature for compliance audits. Note: this release includes a breaking change to the deprecated `/v1/inventory/stock` endpoint — see Breaking Changes.

### 🚀 Features

- **Multi-region failover for inventory service** ([#1247](https://github.com/example/repo/pull/1247)) — Inventory now replicates synchronously across us-east-1 and eu-west-1. Reads automatically failover within 5 seconds of a regional outage. By @alice.
- **Admin compliance export** ([#1252](https://github.com/example/repo/pull/1252)) — Admins can now export an audit-ready CSV of all inventory mutations from the admin panel. Supports SOC2 control IM-3. By @bob.
- **Configurable rate limits per API key** ([#1238](https://github.com/example/repo/pull/1238)) — API rate limits are now configurable per-key with sane defaults. Default unchanged at 1000 req/min. By @carol.

### 🐛 Fixes

- **Stock counter race condition under concurrent reservations** ([#1255](https://github.com/example/repo/pull/1255)) — Resolved a race that could allow oversells when ≥3 customers reserved the same SKU within ~50ms. Fixed via row-level locking in the reservation flow. By @dave.
- **Order webhook delivery retries respect Retry-After header** ([#1248](https://github.com/example/repo/pull/1248)) — Previously ignored the header. Now backoff respects vendor guidance. By @alice.

### ⚡ Performance

- **Checkout API latency reduced 40% (p95)** ([#1244](https://github.com/example/repo/pull/1244)) — Eliminated N+1 queries in cart-totalization. Before: 380ms p95. After: 230ms p95. By @bob.
- **Inventory query cache hit rate increased to 92%** ([#1241](https://github.com/example/repo/pull/1241)) — Tuned cache key strategy and TTL based on access patterns. By @carol.

### 🔒 Security

- **CVE-2026-1234 in `requests` 2.31.0 patched** ([#1250](https://github.com/example/repo/pull/1250)) — Bumped to 2.32.0. Severity: HIGH. No known exploits in our deployment surface. By @security-team.
- **Hardened admin session token TTL from 24h to 4h** ([#1253](https://github.com/example/repo/pull/1253)) — Reduces window for stolen-token replay attacks. Severity: MEDIUM. By @alice.

### ⚠️ Breaking Changes

> Read this section before upgrading.

#### `/v1/inventory/stock` endpoint removed

**What changed**: The deprecated `/v1/inventory/stock` endpoint (which returned a flat list) has been removed. All clients must use `/v2/inventory/stock-levels` (which returns paginated, region-aware results).

**Why**: `/v1` couldn't return per-region stock and lacked pagination, causing 30s+ response times at scale. Deprecation was announced in 2025-Q4 release.

**Migration**:

```diff
- GET /v1/inventory/stock
+ GET /v2/inventory/stock-levels?region=us-east-1&page=1&per_page=100
```

The response shape is similar but adds `region` and `page_token`. See `docs/api-migration-v1-to-v2.md` for the field-by-field mapping.

**Affected users**: All API clients still using `/v1/inventory/stock`. Use `grep` on your codebase for the old path.

### 📦 Dependencies

- Bumped `requests` from `2.31.0` to `2.32.0` ([CVE-2026-1234 patch](https://nvd.nist.gov/vuln/detail/CVE-2026-1234)).
- Bumped `psycopg2` from `2.9.5` to `2.9.9` (maintenance release).
- Bumped `redis-py` from `4.6.0` to `5.0.1` (new connection pool API; backward-compatible).

### 👥 Contributors

Thanks to everyone who contributed to this release:

@alice, @bob, @carol, @dave, @security-team — and 2 first-time contributors: @newbie1, @newbie2!

---
```

## Authoring tips

### Writing for users, not engineers

- "Stock counter race condition under concurrent reservations" ✓ (describes the user impact)
- "Refactored ReservationManager to use SELECT FOR UPDATE" ✗ (implementation detail; belongs in PR description)

### Highlights section curation

- Pick 3–5 changes with the highest user impact
- Lead with the most positive (e.g., new features) but don't bury breaking changes
- Mention performance with concrete before/after numbers
- Keep each item to 1 sentence

### Breaking changes are non-negotiable

- ALWAYS include a section if there are any
- ALWAYS provide migration guidance with code examples
- ALWAYS list affected users so they can self-identify

### Hyperlinks

- Link issues/PRs (use the auto-extracted IDs from `parse_git_log.py`)
- Link CVEs to NVD or vendor advisory
- Link migration guides if longer than the inline section

### Don't include in release notes

- Internal refactors with no user-facing change
- Test additions (unless they revealed a bug worth mentioning)
- Documentation-only commits (unless the docs are user-facing API docs)
- Build system changes
- Style/lint fixes
