# Start a New Project

Guide the user through the core delivery pipeline for starting a new project.

## Phase: Project Initiation

Follow these categories in order, engaging the right agents at each stage:

### Stage 1: Intent & Strategic Alignment (Category 1)

**Processes**: P-001 through P-006
**Primary agents**: `product-manager`, `engineering-manager`, `staff-principal-engineer`
**Reference**: `processes/01_intent_strategic_alignment.md`

Steps:
1. **Articulate Intent** (P-001) — PM drafts the Intent Brief answering: Why are we doing this? What problem does it solve? Who benefits?
2. **Align to OKRs** (P-002) — Map deliverables to team/org OKRs
3. **Define Boundaries** (P-003) — Explicit in-scope / out-of-scope / deferred lists
4. **Intent Review Gate** (P-004) — PM + EM present to stakeholders. Pass criteria: clear problem statement, OKR alignment, boundary agreement
5. **Strategic Prioritization** (P-005) — Stack rank against competing initiatives
6. **Technology Vision Alignment** (P-006) — Staff/Principal validates tech direction fits architecture vision

**Gate**: Intent Review Gate (P-004) must PASS before proceeding.

### Stage 2: Scope Contract Management (Category 2)

**Processes**: P-007 through P-014
**Primary agents**: `product-manager`, `software-engineer`, `qa-engineer`, `security-engineer`
**Reference**: `processes/02_scope_contract_management.md`

Steps:
1. **Decompose Deliverables** (P-007) — Break intent into concrete deliverables with acceptance criteria
2. **Define Definition of Done** (P-008) — Per-story and per-epic DoD
3. **Define Success Metrics** (P-009) — Measurable outcomes tied to OKRs
4. **Register Assumptions & Risks** (P-010) — Initial RAID log entries
5. **Document Exclusions** (P-011) — Explicit "we are NOT building" list
6. **AppSec Scope Review** (P-012) — Security engineer reviews scope for security implications
7. **Scope Lock Gate** (P-013) — PM owns. All deliverables, DoD, metrics, risks documented
8. **Change Control** (P-014) — Process for handling scope changes post-lock

**Gate**: Scope Lock Gate (P-013) must PASS before proceeding.

**Also engage early**:
- **Security** (Category 6, P-038) — Threat modeling should begin during scope definition
- **Risk Management** (Category 13, P-075) — Risk register at Scope Lock

### Stage 3: Dependency Coordination (Category 3)

**Processes**: P-015 through P-021
**Primary agents**: `technical-program-manager`, `engineering-manager`, `staff-principal-engineer`
**Reference**: `processes/03_dependency_coordination.md`

Steps:
1. **Register Cross-Team Dependencies** (P-015) — Map all external team dependencies
2. **Analyze Critical Path** (P-016) — Identify blocking dependencies
3. **Resolve Resource Conflicts** (P-017) — Negotiate shared resource allocation
4. **Communication Plan** (P-018) — Establish sync cadences with dependent teams
5. **Dependency Acceptance Gate** (P-019) — All dependent teams acknowledge and commit
6. **Dependency Standups** (P-020) — Recurring sync for active dependencies
7. **Escalation Protocol** (P-021) — When and how to escalate blocked dependencies

**Gate**: Dependency Acceptance Gate (P-019) must PASS before proceeding.

### Stage 4: Sprint Bridge (Category 4)

**Processes**: P-022 through P-031
**Primary agents**: `engineering-manager`, `software-engineer`, `product-manager`
**Reference**: `processes/04_sprint_delivery_execution.md`

Steps:
1. **Author Sprint Goals** (P-022) — Clear, measurable sprint objectives
2. **Intent Trace** (P-023) — Every story traces back to intent brief
3. **Write Stories** (P-024) — Detailed user stories with acceptance criteria
4. **Sprint Readiness Gate** (P-025) — Stories refined, dependencies cleared, team committed

**Gate**: Sprint Readiness Gate (P-025) must PASS before sprint execution begins.

## Usage

To start a new project, I will:
1. Read the relevant process files for the current stage
2. Identify which agents should be involved
3. Guide you through each gate's pass criteria
4. Track progress through the 4-stage pipeline

What is the project you'd like to start? I'll begin with Stage 1 (Intent & Strategic Alignment).

## Receipt Writing (STATE-001)

After completing any stage of project initiation, write a receipt:

1. `mkdir -p .pipeline-state/command-receipts .pipeline-state/process-log`
2. Write `.pipeline-state/command-receipts/new-project-<YYYYMMDD>-<HHMMSS>.json`:

```json
{
  "command": "new-project",
  "receipt_id": "new-project-<YYYYMMDD>-<HHMMSS>",
  "timestamp": "<ISO-8601>",
  "session_context": {
    "session_id": "<generated session_id>",
    "pipeline": "standalone"
  },
  "inputs": {
    "project_name": "<from user>",
    "trigger_gate": "gate2|gate4"
  },
  "outputs": {
    "handoff_receipt_path": ".orchestrate/<session>/handoff-receipt.json",
    "session_id": "<generated>"
  },
  "artifacts": [".orchestrate/<session>/handoff-receipt.json"],
  "processes_executed": ["P-001", "P-002", "P-003", "P-004", "P-007"],
  "next_recommended_action": "auto-orchestrate",
  "dispatch_context": {
    "trigger_id": null,
    "invoked_by": null
  }
}
```

3. For each process executed, append to `.pipeline-state/process-log/<process-id>.jsonl` (STATE-003).

Note: The existing `handoff-receipt.json` is NOT replaced. It continues to serve as the direct auto-orchestrate handoff artifact. The command receipt is the cross-pipeline visibility layer.

If write fails, log warning and continue. See `_shared/protocols/cross-pipeline-state.md` for the full receipt schema.

## Phase 5: Bridge Protocol Handoff (Auto-Orchestrate Launch)

After completing the 4-stage project initiation pipeline, you can hand off to /auto-orchestrate for autonomous implementation.

### Trigger Conditions

Phase 5 activates when:
- **After Gate 2 (Scope Lock) passes**: Early handoff with Scope Contract only
- **After Gate 4 (Sprint Readiness) passes**: Full handoff with all dependency context (RECOMMENDED)
- **User explicit trigger**: User can trigger Phase 5 at any point after Gate 2

### handoff-receipt.json Schema

```json
{
  "schema_version": "1.0",
  "session_id": "auto-orc-{YYYYMMDD}-{project_slug}",
  "created_at": "ISO-8601 timestamp",
  "source_command": "/new-project",
  "trigger_gate": "gate2|gate4",
  "project": {
    "project_name": "string — from Scope Contract field 1",
    "problem_statement": "string — from Scope Contract field 2",
    "deliverables": ["array of strings — from Scope Contract field 3"],
    "definition_of_done": "string — from Scope Contract field 4",
    "exclusions": ["array of strings — from Scope Contract field 5"],
    "constraints": ["array of strings — from Scope Contract field 6"]
  },
  "task_description": "string — concatenated summary for /auto-orchestrate input",
  "scope": "F|B|S|null — full/backend/service scope flag",
  "status": "pending"
}
```

### Extraction Mapping

Map Scope Contract fields to handoff-receipt.json:

| Scope Contract Field | handoff-receipt.json Field | Description |
|---------------------|--------------------------|-------------|
| Project Name | project.project_name | Top-level project identifier |
| Problem Statement | project.problem_statement | What problem this solves |
| Deliverables (MoSCoW) | project.deliverables | Must-have deliverables only |
| Definition of Done | project.definition_of_done | Success criteria |
| Explicit Exclusions | project.exclusions | What is NOT in scope |
| Constraints | project.constraints | Technical/org constraints |

### task_description Construction

Build the task_description from extracted fields:

```
"task_description": "Build {project_name}. Problem: {problem_statement}. Deliverables: {deliverables joined with '; '}. DoD: {definition_of_done}. Constraints: {constraints joined with '; '}."
```

### Phase 5 Steps

1. Confirm Gate 4 (or Gate 2) has passed
2. Derive session_id: `auto-orc-{YYYYMMDD}-{slugify(project_name)}`
3. Create `.orchestrate/{session_id}/` directory
4. Write `handoff-receipt.json` with all 6 extracted fields + task_description
5. Present task_description to user for review/edit
6. Ask: "Launch /auto-orchestrate with this task? (yes/no/edit)"
7. If yes: Output `/auto-orchestrate "{task_description}" --scope {F|B|S}` instruction
8. If no: Save receipt for future use; inform user they can run /auto-orchestrate manually

### File Path

`{working_dir}/.orchestrate/{session_id}/handoff-receipt.json`

### Interface Contract

- **Input**: Completed Scope Contract artifact (from Phase 2) or Sprint Kickoff Brief (from Phase 4)
- **Output**: `.orchestrate/{session_id}/handoff-receipt.json` written to disk
- **Error**: If required Scope Contract fields are missing, ask user to provide them before proceeding

### Gate State Check at Each Stage Transition

Before Stage 2 (Scope Contract) begins:
- Check: `gate_1_intent_review.status == "passed"`
- If not: `[GATE-BLOCK] Gate 1 (Intent Review) has not passed. Cannot advance to Scope Contract. Run /gate-review intent-review to complete gate review.`

Before Stage 3 (Dependency Coordination) begins:
- Check: `gate_2_scope_lock.status == "passed"`
- If not: `[GATE-BLOCK] Gate 2 (Scope Lock) has not passed. Cannot advance to Dependency Coordination. Run /gate-review scope-lock to complete gate review.`

Before Stage 4 (Sprint Bridge) begins:
- Check: `gate_3_dependency_acceptance.status == "passed"`
- If not: `[GATE-BLOCK] Gate 3 (Dependency Acceptance) has not passed. Cannot advance to Sprint Bridge. Run /gate-review dependency-acceptance to complete gate review.`

Before /sprint-ceremony (execution):
- Check: `gate_4_sprint_readiness.status == "passed"`
- If not: `[GATE-BLOCK] Gate 4 (Sprint Readiness) has not passed. Cannot begin sprint execution. Run /gate-review sprint-readiness to complete gate review.`

Override: If `gate_N.override` is non-null with a valid `authorized_by` field, enforcement is waived for that gate only.
