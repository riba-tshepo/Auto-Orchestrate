## Current Project Status

Shows live status of your current project's gate progression and pipeline state.

```bash
# Step 1: Find most recent auto-orchestrate session
MOST_RECENT_SESSION=$(python3 -c "
import json, os
idx = '.sessions/index.json'
if not os.path.exists(idx): print('NO_SESSION'); exit()
sessions = json.load(open(idx)).get('sessions', [])
orc = [s for s in sessions if s.get('command') == 'auto-orchestrate' and s.get('status') in ('in_progress', 'complete')]
orc.sort(key=lambda x: x.get('created_at',''), reverse=True)
print(orc[0]['session_id'] if orc else 'NO_SESSION')
" 2>/dev/null)

# Step 2: If session found, display gate statuses
if [ "$MOST_RECENT_SESSION" != "NO_SESSION" ]; then
  GATE_FILE=".orchestrate/$MOST_RECENT_SESSION/gate-state.json"
  python3 -c "
import json, sys
gs_path = sys.argv[1]
try:
    gs = json.load(open(gs_path))
    gates = gs.get('gates', {})
    print(f'Project: {gs.get(\"project_name\", \"Unknown\")} | Session: {gs.get(\"session_id\", \"Unknown\")}')
    print()
    STATUS_ICONS = {'pending': '○', 'in_review': '◷', 'passed': '✓', 'failed': '✗'}
    for gate_id, gate_name in [('gate_1_intent_review','Gate 1: Intent Review'), ('gate_2_scope_lock','Gate 2: Scope Lock'), ('gate_3_dependency_acceptance','Gate 3: Dependency Acceptance'), ('gate_4_sprint_readiness','Gate 4: Sprint Readiness')]:
        g = gates.get(gate_id, {})
        status = g.get('status', 'pending')
        icon = STATUS_ICONS.get(status, '?')
        suffix = ''
        if status == 'failed': suffix = f' — BLOCKED: {g.get(\"fail_reason\", \"see gate-review\")}'
        elif g.get('override'): suffix = ' [OVERRIDE ACTIVE]'
        print(f'  {icon} {gate_name}: {status}{suffix}')
except FileNotFoundError:
    print('  [GATE-WARN] Gate state not yet initialized. Run /new-project first.')
except Exception as e:
    print(f'  [GATE-WARN] Could not read gate state: {e}')
  " "$GATE_FILE"
else
  echo "  No active project session found."
  echo "  Run /new-project to start a new project."
fi
```

---


# Development Workflow

Show the complete development workflow mapping agents to project phases.

## The Clarity of Intent Pipeline

```
 STAGE 1              STAGE 2              STAGE 3              STAGE 4
 Intent Frame    -->  Scope Contract  -->  Dependency Map  -->  Sprint Bridge
 (1-3 days)           (3-5 days)           (3-5 days)           (1-2 days)
     |                    |                    |                    |
 Intent Review       Scope Lock         Dependency           Sprint Readiness
    Gate                Gate            Acceptance Gate           Gate
```

## Agent Engagement by Phase

### Phase 1: Starting a New Project (`/new-project`)

```
Stage 1: Intent Frame
  product-manager ............ Drafts Intent Brief, defines problem
  engineering-manager ........ Validates capacity, co-owns gate
  staff-principal-engineer ... Technology vision alignment

Stage 2: Scope Contract  
  product-manager ............ Decomposes deliverables, defines DoD
  software-engineer .......... Technical estimation, story breakdown
  qa-engineer ................ Test strategy, acceptance criteria
  security-engineer .......... AppSec scope review (P-012)

Stage 3: Dependency Map
  technical-program-manager .. Maps dependencies, critical path
  engineering-manager ........ Resource conflict resolution
  staff-principal-engineer ... Cross-team architecture alignment

Stage 4: Sprint Bridge
  engineering-manager ........ Sprint goal, capacity validation
  product-manager ............ Story prioritization
  software-engineer .......... Story decomposition, estimation
```

### Phase 2: Active Development (`/active-dev`)

```
Continuous:
  software-engineer .......... Feature implementation (P-030)
  qa-engineer ................ DoD enforcement (P-034), testing (P-032-P-037)
  security-engineer .......... SAST/DAST per PR (P-039), CVE triage (P-040)
  technical-writer ........... API docs per API change (P-058)

Sprint Cadence:
  engineering-manager ........ Standups (P-026), review (P-027), retro (P-028)
  product-manager ............ Backlog refinement (P-029)
```

### Phase 3: Release Preparation (`/release-prep`)

```
Pre-Release:
  qa-engineer ................ Performance testing (P-035)
  platform-engineer .......... CI/CD pipeline verification (P-048)
  cloud-engineer ............. Infrastructure provisioning (P-045)
  sre ....................... Monitoring, alerting, SLO dashboards (P-054)
  technical-writer ........... Runbooks (P-059), release notes (P-061)
  technical-program-manager .. CAB review for HIGH-risk (P-076)
```

### Phase 4: Post-Launch (`/post-launch`)

```
Ongoing:
  sre ....................... SLO monitoring (P-054), incidents (P-055), on-call (P-057)
  
Scheduled:
  product-manager ............ Outcome measurement at 30/60/90 days (P-073)
  engineering-manager ........ Project post-mortem (P-070), OKR retro (P-072)
  sre ....................... Post-mortems after incidents (P-056)
```

### Phase 5: Organizational Operations (`/org-ops`)

```
Continuous/Cadenced:
  engineering-manager ........ Audit hierarchy (P-062-P-069), DORA (P-081)
  staff-principal-engineer ... RFCs (P-085), architecture patterns (P-088)
  product-manager ............ OKR cascade (P-078)
  technical-program-manager .. Capacity planning (P-082)
  platform-engineer .......... Tech debt tracking (P-086), DX survey (P-089)
  technical-writer ........... Knowledge transfer (P-092)
```

## Available Commands

| Command | Phase | Description |
|---------|-------|-------------|
| `/new-project` | Starting | Walk through 4-stage delivery pipeline |
| `/gate-review` | Starting | Run gate review checklist |
| `/active-dev` | Development | Sprint execution guidance |
| `/sprint-ceremony` | Development | Facilitate sprint ceremonies |
| `/qa` | Development | QA & Testing process guide (P-032 to P-037) |
| `/security` | Development/Release | Security & Compliance process guide (P-038 to P-043) |
| `/infra` | Release/Operations | Infrastructure & Platform process guide (P-044 to P-048) |
| `/risk` | Any | Risk & Change Management process guide (P-074 to P-077) |
| `/data-ml-ops` | Development/Operations | Data & ML Operations process guide (P-049 to P-053) |
| `/release-prep` | Release | Release preparation checklist |
| `/post-launch` | Operations | Post-launch processes |
| `/org-ops` | Continuous | Organizational operations |
| `/auto-orchestrate` | Any | Autonomous implementation pipeline |
| `/auto-audit` | Any | Spec compliance audit-remediate loop |
| `/auto-debug` | Any | Autonomous error debugging loop |
| `/workflow` | Any | Development workflow map |
| `/assign-agent` | Any | Route task to correct agent |
| `/process-lookup` | Any | Find process for a situation |
| `/agent-capabilities` | Any | Show agent profiles |

## Quick Reference

Need to know which agent handles what? Use `/assign-agent <task description>`.
Need a specific process? Use `/process-lookup <situation>`.
Starting fresh? Use `/new-project`.
