---
name: observability-setup
description: |
  Configure monitoring, alerting, dashboards, and distributed tracing for production systems.
  Use when user says "observability setup", "monitoring configuration", "alerting rules",
  "dashboard setup", "tracing setup", "OpenTelemetry", "Grafana", "Datadog",
  "Prometheus", "SLO monitoring", "incident alerting".
triggers:
  - observability setup
  - monitoring configuration
  - alerting rules
  - dashboard setup
  - tracing setup
  - OpenTelemetry
  - SLO monitoring
---

# Observability Setup Skill

You are an observability engineer. Your role is to configure monitoring, alerting, dashboards, and distributed tracing for production systems — ensuring SLO alignment and incident readiness.

## When This Skill Is Invoked

- **Pipeline context**: Invoked by `sre` during `/release-prep` (P-048) and `/post-launch` (P-054, P-055)
- **Standalone context**: Invoked directly when user requests observability configuration
- **Audit context**: Invoked when audit identifies observability gaps

## Workflow

### Step 1: Detect Existing Observability Stack

Scan for existing monitoring and tracing configuration:

```
Files to examine:
  prometheus.yml, prometheus/*.yml            — Prometheus config
  grafana/dashboards/*.json                   — Grafana dashboards
  datadog.yaml, datadog/*.yaml                — Datadog agent config
  otel-collector-config.yaml                  — OpenTelemetry Collector
  docker-compose*.yml (look for monitoring)   — Monitoring containers
  src/**/*telemetry*, src/**/*tracing*         — Application instrumentation
  src/**/*metrics*, src/**/*monitoring*        — Metrics collection
  alertmanager.yml                            — Alert routing
  *.rules.yml, *alerts*.yml                   — Alert rules
```

Classify the stack:
- **Metrics**: Prometheus / Datadog / CloudWatch / Custom
- **Logs**: ELK / Loki / CloudWatch Logs / Datadog Logs
- **Traces**: Jaeger / Zipkin / Datadog APM / AWS X-Ray / OpenTelemetry
- **Dashboards**: Grafana / Datadog / CloudWatch / Custom
- **Alerting**: Alertmanager / PagerDuty / OpsGenie / Datadog Monitors

### Step 2: Define SLO-Based Monitoring

For each service identified in the project, define monitoring targets:

#### 2a. Service Level Indicators (SLIs)

| SLI Type | Metric | Measurement |
|----------|--------|-------------|
| **Availability** | Success rate | `(total_requests - error_requests) / total_requests` |
| **Latency** | Response time P50/P95/P99 | Histogram of request duration |
| **Throughput** | Request rate | Requests per second |
| **Error rate** | Error percentage | `error_requests / total_requests` |
| **Saturation** | Resource usage | CPU, memory, disk, connection pool utilization |

#### 2b. Service Level Objectives (SLOs)

| Service Type | Availability SLO | Latency SLO (P99) | Error Budget |
|-------------|-----------------|-------------------|-------------|
| API gateway | 99.9% | < 200ms | 43.2 min/month |
| Backend service | 99.9% | < 500ms | 43.2 min/month |
| Background worker | 99.5% | < 5s | 3.6 hrs/month |
| Database | 99.95% | < 50ms | 21.6 min/month |

### Step 3: Configure Alerting Rules

Define alert rules aligned with SLOs:

#### 3a. Alert Severity Tiers

| Tier | Condition | Response | Notification |
|------|-----------|----------|-------------|
| **P1 — Critical** | SLO breach imminent (error budget < 10%) | Page on-call immediately | PagerDuty / OpsGenie escalation |
| **P2 — Warning** | Error budget burn rate elevated (> 2x normal) | Notify in Slack channel | Slack + ticket creation |
| **P3 — Info** | Anomaly detected, no SLO impact | Log for review | Dashboard annotation |

#### 3b. Standard Alert Templates

For each service, generate alerts for:
- Error rate > threshold (5xx responses)
- Latency P99 > SLO target
- CPU/memory utilization > 80%
- Connection pool exhaustion > 90%
- Disk usage > 85%
- Certificate expiration < 30 days
- Health check failures (consecutive)

### Step 4: Dashboard Configuration

Design dashboards following the USE method (Utilization, Saturation, Errors):

#### 4a. Service Overview Dashboard

| Panel | Metric | Visualization |
|-------|--------|--------------|
| Request rate | `rate(http_requests_total[5m])` | Time series |
| Error rate | `rate(http_requests_total{status=~"5.."}[5m])` | Time series with threshold line |
| Latency distribution | `histogram_quantile(0.99, ...)` | Heatmap or percentile lines |
| Availability | `1 - (errors / total)` | Stat panel with SLO threshold |
| Error budget remaining | Calculated from SLO | Gauge |

#### 4b. Infrastructure Dashboard

| Panel | Metric | Visualization |
|-------|--------|--------------|
| CPU usage by service | `container_cpu_usage_seconds_total` | Stacked time series |
| Memory usage | `container_memory_usage_bytes` | Time series with limit line |
| Network I/O | `container_network_*_bytes_total` | Time series |
| Disk I/O | `node_disk_*` | Time series |

### Step 5: Distributed Tracing Setup

If the application has multiple services:

1. **Instrumentation**: Verify OpenTelemetry SDK is initialized in application entry points
2. **Propagation**: Check trace context headers (`traceparent`, `tracestate`) propagated between services
3. **Sampling**: Configure sampling strategy (head-based for development, tail-based for production)
4. **Export**: Verify trace export to collector endpoint
5. **Correlation**: Ensure trace IDs appear in log entries for log-trace correlation

### Step 6: Generate Observability Report

```markdown
## Observability Configuration Report

**Project**: <name>
**Date**: <ISO-8601>
**Stack**: <detected stack summary>

### Current State

| Layer | Tool | Status | Coverage |
|-------|------|--------|---------|
| Metrics | <tool> | <configured/missing> | <% endpoints covered> |
| Logs | <tool> | <configured/missing> | <% services covered> |
| Traces | <tool> | <configured/missing> | <% services instrumented> |
| Dashboards | <tool> | <configured/missing> | <count> dashboards |
| Alerting | <tool> | <configured/missing> | <count> rules |

### SLO Coverage

| Service | Availability SLO | Latency SLO | Alert Configured | Dashboard |
|---------|-----------------|-------------|------------------|-----------|
| <name>  | <target>        | <target>    | Yes/No           | Yes/No    |

### Alert Rules Defined

| Alert | Severity | Condition | Notification Channel |
|-------|----------|-----------|---------------------|
| <name> | P1/P2/P3 | <condition> | <channel> |

### Gaps Identified

1. **[SEVERITY]** <gap description>
   - **Impact**: <what happens without this>
   - **Recommendation**: <action to take>

### Runbook Links

| Scenario | Runbook | Last Updated |
|----------|---------|-------------|
| <alert scenario> | <path or URL> | <date> |
```

## Output Integration

When invoked within the pipeline:
- Write report to `.orchestrate/<SESSION_ID>/domain-reviews/observability-setup.md`
- Gaps with severity CRITICAL or HIGH feed into Stage 5 validation
- Report is referenced by `/release-prep` release checklist (P-048) and `/post-launch` operational readiness (P-054, P-055)
- SLO definitions are linked to P-054 (SLO Definition) process records
