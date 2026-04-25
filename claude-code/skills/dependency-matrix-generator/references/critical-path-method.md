# Critical Path Method (CPM) Walkthrough

The Critical Path Method identifies the longest dependency chain in a project — its duration sets the minimum project timeline.

## Concepts

- **Activity**: A unit of work (e.g., "Build session-token library v2.0")
- **Duration**: Time required for the activity (e.g., 14 days)
- **Predecessors**: Activities that must complete before this one starts
- **Successors**: Activities that depend on this one
- **Slack** (or float): How much an activity can be delayed without delaying the project
- **Critical path**: The chain of activities with zero slack — delaying any one delays the project

## Algorithm summary

1. Build a directed acyclic graph (DAG): nodes = activities, edges = "must complete before"
2. Compute earliest start (ES) and earliest finish (EF) for each node by walking forward
3. Compute latest start (LS) and latest finish (LF) for each node by walking backward
4. Slack = LS - ES (or equivalently LF - EF)
5. Critical path = activities with slack = 0

## Worked example

### The project

Six activities for "Multi-region inventory failover":

| ID | Activity | Duration (days) | Predecessors |
|----|----------|----------------|--------------|
| A | Identity v2.0 token library | 14 | (none) |
| B | Inventory adapter for v2 tokens | 7 | A |
| C | Data CDC stream (data-platform delivery) | 21 | (none) |
| D | Inventory dual-write infrastructure | 14 | B, C |
| E | Inventory cutover (3-week rollout) | 21 | D |
| F | Customer launch (announcement, monitoring) | 7 | E |

### Step 1: Build the DAG

```
A (14d) ────┐
              ├── B (7d) ──┐
                            ├── D (14d) ── E (21d) ── F (7d)
              C (21d) ───┘
```

### Step 2: Forward pass (earliest times)

For each node, ES = max(EF of all predecessors); EF = ES + duration.

| ID | Duration | Predecessors | ES | EF |
|----|----------|--------------|----|----|
| A | 14 | — | 0 | 14 |
| B | 7 | A | 14 | 21 |
| C | 21 | — | 0 | 21 |
| D | 14 | B (EF=21), C (EF=21) | max(21, 21) = 21 | 35 |
| E | 21 | D | 35 | 56 |
| F | 7 | E | 56 | 63 |

**Project duration** = EF of last activity = 63 days

### Step 3: Backward pass (latest times)

For each node, LF = min(LS of all successors); LS = LF - duration. Start from the last activity (F) with LF = its EF.

| ID | Duration | Successors | LF | LS |
|----|----------|------------|----|----|
| F | 7 | — (last) | 63 | 56 |
| E | 21 | F | 56 | 35 |
| D | 14 | E | 35 | 21 |
| B | 7 | D | 21 | 14 |
| C | 21 | D | 21 | 0 |
| A | 14 | B | 14 | 0 |

### Step 4: Compute slack

Slack = LS - ES (or LF - EF — same value)

| ID | ES | LS | Slack | On critical path? |
|----|----|----|-------|-------------------|
| A | 0 | 0 | 0 | YES |
| B | 14 | 14 | 0 | YES |
| C | 0 | 0 | 0 | YES |
| D | 21 | 21 | 0 | YES |
| E | 35 | 35 | 0 | YES |
| F | 56 | 56 | 0 | YES |

In this case, ALL activities are on the critical path because B and C both finish at day 21 (D's predecessor constraint).

### Step 5: Identify the path

Critical path: A → B → D → E → F (and C also critical with EF = 21, parallel to A→B).

### Insights from the analysis

- **Project duration is 63 days** (~9 weeks).
- **Both A→B and C are on critical path**: speeding up A→B alone won't help unless C is also accelerated. They're "parallel critical paths."
- **No activity has slack** in this example — meaning any delay anywhere extends the project.

### What if scenarios

#### What if Identity v2 (A) takes 21 days instead of 14?

Forward pass changes: EF(A) = 21. EF(B) = 28. ES(D) = max(28, 21) = 28. EF(D) = 42. EF(E) = 63. EF(F) = 70. → Project takes 70 days. Slipped by 7 days.

#### What if data CDC (C) takes 28 days instead of 21?

Forward pass changes: EF(C) = 28. ES(D) = max(21, 28) = 28. → Project takes 70 days. Same impact as A slipping.

#### What if mobile /v2 endpoint (a non-critical-path activity, not in the example) takes 14 days?

If its slack is 14+ days, no project impact.

## Cycle detection

A valid project graph is a DAG (Directed Acyclic Graph). If there's a cycle, CPM doesn't work — the project is unschedulable.

The `dep_graph.py` script uses Tarjan's algorithm to detect strongly connected components. SCCs of size > 1 indicate cycles.

### Common cycle patterns

| Pattern | Example | Resolution |
|---------|---------|------------|
| Mutual blocker | A waits on B; B waits on A | One side commits to a stub/mock to unblock |
| Three-way deadlock | A → B → C → A | Identify the dependency with most slack and replace with a stub |
| "Both teams say go first" | Team X waits on Team Y's review; Team Y waits on Team X's design | Set a deadline; whichever moves first wins |

## Critical chain modification

Critical Path Method assumes activities have fixed durations. **Critical Chain Method** (CCM) adjusts for resource constraints (e.g., the same engineer is needed for two parallel activities).

In CCM:
- Critical path is recomputed based on resource availability
- "Buffer time" is added at the end (project buffer) and at convergence points (feeding buffers)
- The critical chain may differ from the traditional critical path

Use CCM when shared resources are a major constraint (per Section 2 of the Dependency Charter).

## Optimization heuristics

To shorten the critical path:

1. **Crash the longest activity**: Add resources to compress the longest critical-path activity (often most cost-effective per day saved)
2. **Parallelize where possible**: Identify activities currently sequential that could run in parallel
3. **Fast-track**: Start a successor before the predecessor fully completes (with risk of rework)
4. **Reduce scope**: Negotiate with stakeholders to descope non-essential parts of critical-path activities

## Anti-patterns

| Anti-pattern | Why bad | Fix |
|--------------|---------|-----|
| Padding every activity duration | Hides true critical path | Use realistic durations + project buffer |
| Treating slack as license to delay | Slack is contingency, not free time | Track slack consumption; alert when slack drops |
| Optimizing non-critical-path activities | Doesn't change project duration | Focus optimization on critical path first |
| Static critical path (set once, never updated) | Reality changes weekly | Recompute at each Dependency Standup (P-020) |
