---
name: dependency-matrix-generator
description: |
  Build cross-team dependency registers, identify critical paths, detect cycles,
  and resolve resource conflicts. Implements P-015 (Cross-Team Dependency
  Registration), P-016 (Critical Path Analysis), P-017 (Shared Resource Conflict
  Resolution), P-030 (Sprint-Level Dependency Tracking). Provides graph-based
  topological sort, cycle detection, and resource-conflict identification.
  Use when user says "dependency matrix", "critical path", "cross-team
  dependency", "sprint dependency", "dependency cycle", "resource conflict".
triggers:
  - dependency matrix
  - critical path
  - cross-team dependency
  - sprint dependency
  - dependency cycle
  - resource conflict
---

# Dependency Matrix Generator Skill

You build the dependency artifacts that feed Phase 3 (Dependency Map) and the iteration-boundary Dependency Standup. Output includes a dependency register, critical path analysis, cycle detection, and resource conflict identification.

## When to use

| Trigger | Process | Pipeline node |
|---------|---------|---------------|
| Stage P3 (Dependency Map) lead | P-015 (Cross-Team Dependency Registration), P-016 (Critical Path), P-018 (Communication Protocol) | technical-program-manager produces P3-dependency-charter.md |
| Stage P4 (Sprint Bridge) co-agent | P-030 (Sprint-Level Dependency Tracking) | technical-program-manager produces P4-sprint-deps.md |
| PHASE: DEPENDENCY_STANDUP (iteration boundary) | P-020 (Dependency Standup) | technical-program-manager facilitates + updates RAID via raid-logger |

## How to use

### Step 1: Gather inputs

For Stage P3:
- Scope Contract at `.orchestrate/<session>/planning/P2-scope-contract.md` (Deliverables, Success Metrics)
- Stakeholder list (from Intent Brief)
- Project timeline / desired launch date

For DEPENDENCY_STANDUP (iteration boundary):
- Latest Dependency Charter at `.orchestrate/<session>/planning/P3-dependency-charter.md`
- Recent Daily Standup blockers at `.orchestrate/<session>/meetings/meeting-p-026-daily-standup-iter-*.json`
- Current task-board state

### Step 2: Identify dependencies

For each deliverable in scope, ask:
- What teams or systems must provide something for this to land?
- What systems consume this deliverable's output?
- What shared resources (CI capacity, infra, vendor APIs) does this contend for?

Document each as a dependency entry:

```json
{
  "id": "dep-001",
  "from_team": "inventory-team",
  "to_team": "identity-team",
  "what_is_needed": "Session-token library v2.0 with org-scope claim",
  "by_when": "2026-05-15",
  "status": "committed | at-risk | blocked | unknown",
  "owner_from_side": "inventory-team-tech-lead",
  "owner_to_side": "identity-team-em",
  "escalation_path": "Identity team EM → Director Platform → VP Engineering",
  "blocking_for": ["dep-005", "dep-007"]
}
```

### Step 3: Run the dependency graph script

```
python3 ~/.claude/skills/dependency-matrix-generator/scripts/dep_graph.py \
  --input dependencies.json \
  --output graph-analysis.json
```

The script:
- Builds a directed graph from the dependency register
- Performs topological sort (returns linear order)
- Detects cycles (returns SCCs if any)
- Identifies the critical path (longest path through the DAG)
- Returns nodes by depth (parallelizable work groups)

If cycles are detected, the script exits with code 50 (EXIT_CYCLE_DETECTED) and lists the cycles. **Cycles must be resolved before P3 gate passes.**

### Step 4: Detect resource conflicts

```
python3 ~/.claude/skills/dependency-matrix-generator/scripts/resource_conflict_detector.py \
  --input dependencies.json \
  --output conflicts.json
```

The script identifies shared resources (named in the `shared_resources` field of dependencies) where multiple deliverables compete in overlapping windows. Output is a list of conflict pairs with overlap windows and recommended resolutions.

### Step 5: Build the Dependency Charter

Use the structure in `references/dependency-charter-format.md`. Sections:

```markdown
# Dependency Charter — <Project Name>

## 1. Dependency Register

| ID | From → To | What | By When | Status | Owners | Escalation |
|----|-----------|------|---------|--------|--------|------------|
| dep-001 | inventory → identity | Session-token v2.0 | 2026-05-15 | committed | TL/EM | Director |
| ... | ... | ... | ... | ... | ... | ... |

## 2. Shared Resource Conflicts

| Resource | Competing Demands | Window Overlap | Resolution |
|----------|-------------------|----------------|------------|
| CI build capacity | Inv migration + Auth refactor both heavy compile | Week of 2026-05-08 | Inv team uses spare runner pool; document in raid log |

## 3. Critical Path

[ASCII diagram showing dependency chain that determines minimum timeline]

```
[Identity v2.0] → [Inventory adapter] → [Inventory cutover] → [Customer-facing launch]
   (~2 weeks)        (~1 week)              (~3 weeks)             (~1 week)
   = 7 weeks total minimum timeline
```

## 4. Communication Protocol

| Mechanism | Cadence | Participants | Purpose |
|-----------|---------|--------------|---------|
| Cross-team dependency standup | Twice weekly | TPMs + TLs | Status updates, blocker triage |
| Async update in #project-channel | Daily | All affected | Visibility |
| Escalation path | When blocked | Director → VP | Unblock |
```

### Step 6: For DEPENDENCY_STANDUP (iteration boundary)

Walk through the Dependency Register filtered to dependencies due in the current sprint window. For each:
- Status changed since last check?
- Any new blockers?
- Trigger escalation?

Append RAID entries via `raid-logger` for any newly-blocked dependencies (severity HIGH if it threatens critical path).

## Outputs

- Dependency register JSON at `.orchestrate/<session>/planning/dependencies.json`
- Graph analysis JSON at `.orchestrate/<session>/planning/dep-graph-analysis.json`
- Conflict report JSON at `.orchestrate/<session>/planning/dep-conflicts.json`
- Markdown Dependency Charter at `.orchestrate/<session>/planning/P3-dependency-charter.md`
- (At standup) Meeting receipt with new blockers + RAID updates

## Critical path semantics

The critical path is the LONGEST dependency chain — its length determines the minimum project timeline. Optimization work should target critical-path items first; non-critical dependencies have slack.

A change in critical-path item duration → entire timeline shifts. Non-critical-path changes don't affect timeline (within the slack budget).

## Cycle handling

Cycles in dependency graphs indicate process failure — Team A waiting on Team B which is waiting on Team A. The script will:
1. Identify all cycles via SCC (strongly connected components)
2. List nodes in each cycle
3. Suggest cycle-break candidates (typically the dependency with the most slack or the most reversibility)

Cycles MUST be resolved before P3 gate passes. The chair (TPM) negotiates with the involved teams.

## Related skills

- `raid-logger` — register blocked / at-risk dependencies as RAID entries
- `dependency-analyzer` — for code-level dependency analysis (different from this skill which is project/team level)
- `cab-reviewer` — at Phase 7, reviews if any in-progress dependencies threaten release

## Reference

- `references/dependency-charter-format.md` — full P3 Dependency Charter format
- `references/critical-path-method.md` — CPM walkthrough with worked example
- Canonical processes: P-015, P-016, P-017, P-018, P-020 in `processes/03_dependency_coordination.md`; P-030 in `processes/04_sprint_delivery_execution.md`
