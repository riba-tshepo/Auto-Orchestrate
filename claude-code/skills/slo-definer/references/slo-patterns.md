# SLO Patterns by Service Type

Use this catalog to pick the right SLOs for each service in scope. Each pattern lists recommended SLIs, default targets, common pitfalls, and observability requirements.

## Synchronous API (user-facing)

**Examples**: REST/GraphQL endpoints, gRPC services, BFFs.

### Recommended SLOs

| SLO | SLI | Default target | Window |
|-----|-----|---------------|--------|
| Latency (p95) | `histogram_quantile(0.95, request_duration)` | ≤ 200ms | 28d rolling |
| Latency (p99) | `histogram_quantile(0.99, request_duration)` | ≤ 500ms | 28d rolling |
| Availability | `1 - (5xx_count / total_count)` | 99.9% | 28d rolling |
| Error rate | `(5xx + 4xx_caused_by_us) / total` | ≤ 0.1% | 28d rolling |

### Common pitfalls

- **Including 4xx in error rate**: A 404 from "user typed wrong URL" isn't your fault. Filter out 4xx unless they're caused by service bugs.
- **Including health-check traffic**: `/healthz` is high-volume and trivially fast — it skews latency low. Filter it out.
- **Excluding cold start latency**: Cold starts (post-deploy, scale-up) can balloon p99. Decide whether to include or exclude based on user impact.

### Observability requirements

- HTTP request duration histogram with `le` buckets (e.g., 10ms, 50ms, 100ms, 200ms, 500ms, 1s, 5s, 10s)
- Status code label
- Path label (cardinality-aware — group dynamic paths)

## Async pipeline (events, queues)

**Examples**: Kafka consumers, SQS workers, event processors, webhooks.

### Recommended SLOs

| SLO | SLI | Default target | Window |
|-----|-----|---------------|--------|
| End-to-end freshness | `time_now - max(event.ingested_at)` | ≤ 5 min p95 | 28d rolling |
| Processing success rate | `(processed - failed) / processed` | ≥ 99.5% | 28d rolling |
| Backlog depth | `messages_in_queue` | ≤ 10000 (or service-specific) | 5min rolling |
| Throughput floor | `messages_per_minute` | ≥ <baseline> | 28d rolling |

### Common pitfalls

- **Confusing in-flight delay vs queue lag**: Distinguish "message produced 1 hour ago, still in queue" (queue lag) from "message produced 1 hour ago, processed 1 minute ago" (processing latency).
- **Ignoring DLQ growth**: A growing dead-letter queue is silent failure. Alert on DLQ size growth rate.

### Observability requirements

- Per-message ingested_at + processed_at timestamps
- Queue depth gauge (per consumer group)
- DLQ depth + DLQ growth rate

## Batch job

**Examples**: Nightly reports, ETL pipelines, cron-driven jobs.

### Recommended SLOs

| SLO | SLI | Default target | Window |
|-----|-----|---------------|--------|
| Job success rate | `(successful_runs / total_runs)` | ≥ 99% (28-day) | 28d rolling |
| Job completion time | `job.duration` | ≤ <SLA-driven> | per-run |
| Data freshness | `now - latest_record.created_at` | ≤ <SLA-driven> | per-run |
| Schedule adherence | `runs_started / runs_scheduled` | ≥ 99.5% | 28d rolling |

### Common pitfalls

- **Ignoring partial failures**: A job that succeeds but processes only 50% of expected rows is silent data loss. Track row counts, not just exit codes.
- **No retention policy on job logs**: Past failures should be queryable for retro analysis.

## ML inference

**Examples**: Real-time prediction APIs, recommendation services, scoring endpoints.

### Recommended SLOs

| SLO | SLI | Default target | Window |
|-----|-----|---------------|--------|
| Inference latency p95 | `histogram_quantile(0.95, inference_duration)` | ≤ 100ms | 28d rolling |
| Inference success rate | `(successful_inferences / total)` | ≥ 99.9% | 28d rolling |
| Prediction quality | `model.accuracy` (vs ground truth, async) | ≥ <baseline - 5%> | 7d rolling |
| Drift detection latency | `time_to_detect_drift` | ≤ 24h | per-incident |

### Common pitfalls

- **Latency without batch context**: A 500ms latency for batch=1 is bad; for batch=100 is good. Track per-batch-size if applicable.
- **Quality drift as binary alert**: Drift is gradual. Alert on percentile changes (e.g., quality dropped >5% from 7d baseline).

## Data store

**Examples**: Postgres/MySQL primaries, Redis, DynamoDB, Elasticsearch.

### Recommended SLOs

| SLO | SLI | Default target | Window |
|-----|-----|---------------|--------|
| Query latency p95 | `histogram_quantile(0.95, query_duration)` | ≤ 50ms (single-row) | 28d rolling |
| Connection success rate | `successful_connects / total_connects` | ≥ 99.99% | 28d rolling |
| Replication lag p95 | `histogram_quantile(0.95, replica_lag_seconds)` | ≤ 5s | 28d rolling |
| Disk space available | `disk_free / disk_total` | ≥ 20% | continuous |

## Default error-budget targets by tier

When picking an availability target, use this tier guide:

| Tier | Target | Error budget (per 28d) | When to use |
|------|--------|------------------------|-------------|
| Best-effort | 99% | ~7h | Internal tools, dev environments |
| Standard | 99.9% | ~40min | Most user-facing services |
| Critical | 99.95% | ~20min | Payment, auth, core platform |
| Mission-critical | 99.99% | ~4min | Core infra (DNS, identity, network) |

**Don't pick 99.999%** unless you're prepared for the cost: that's 25 seconds per month. Most services don't need it; the cost-to-benefit ratio is rarely justifiable.

## SLO anti-patterns

| Anti-pattern | Fix |
|--------------|-----|
| "100% uptime" target | Replace with realistic tier (99.9% — 99.99%); 100% means no error budget for deploys/experiments |
| SLI that aggregates across users with very different needs | Split: per-tenant or per-tier SLOs |
| SLO without filter on healthcheck traffic | Always exclude `/healthz`, `/metrics`, internal probes |
| SLO with 1d window | Too noisy; use 7d or 28d rolling for trend stability |
| Latency SLO at average (mean) | Always use percentiles (p95/p99); average hides tail latency |
| Multi-region SLO without per-region breakdown | Track per-region; aggregate hides regional outages |
| SLO that doesn't tie to user pain | "What does broken look like to the user?" must answer the SLO definition |
