---
name: data-ml-ops
description: Guide the user through Data & ML Operations processes (P-049 to P-053).
---

# /data-ml-ops — Data & ML Operations

Guides execution of Data & ML Operations processes using data-engineer and ml-engineer agents.

## Processes Covered

| Process ID | Name | Owner | Description |
|------------|------|-------|-------------|
| P-049 | Data Pipeline Quality Assurance | data-engineer | Every data pipeline includes freshness checks, schema validation, row count validation, and null checks. These checks are automated and alert the Data Engineer when they fail. |
| P-050 | Data Schema Migration | data-engineer | All schema changes go through versioned migration scripts. Destructive changes (drops, renames, type changes) require a manual review flag and explicit approval before execution. |
| P-051 | ML Experiment Logging | ml-engineer | Every ML training run is logged in an experiment tracking system (MLflow/W&B) with hyperparameters, metrics, data version, and artifacts before a model can be considered for production. |
| P-052 | Model Canary Deployment | ml-engineer | Route a small percentage of production traffic to a new model version, validate performance metrics against the baseline, then progressively promote. Never deploy a new model to 100% of traffic directly. |
| P-053 | Data Drift Monitoring | data-engineer/ml-engineer | Automated alerting when input data distribution or model performance metrics drift beyond defined thresholds. Prevents silent model degradation in production. |

## Agents

- **data-engineer**: Owns data pipeline, ingestion, transformation, and storage processes
- **ml-engineer**: Owns model training, evaluation, deployment, and monitoring processes

## When to Use

Use /data-ml-ops when:
- Setting up or modifying data pipelines
- Training, evaluating, or deploying ML models
- Managing feature stores or model registries
- Handling data quality or drift issues

## How to Use

1. Select the process you need from the table above
2. The command will route to the appropriate agent (data-engineer or ml-engineer)
3. Follow the process steps defined in `claude-code/processes/08_data_ml_operations.md`

## Dispatch Mode

When invoked via the Command Dispatcher (a dispatch context file exists at the invoking session's `dispatch-receipts/dispatch-context-TRIG-*.json`), operate in dispatch mode:

1. **Skip interactive guidance** — Do not present process menus or ask for user selection
2. **Read dispatch context** — Parse the dispatch context file for `trigger_id`, `stage`, `condition_summary`, and `relevant_artifacts`
3. **Focused analysis** — Analyze only the processes relevant to the trigger (typically P-049 Data Pipeline QA or P-050 Schema Migration for TRIG-012 flagged processes)
4. **Structured output** — Produce findings in this format:

```
## Dispatch Findings

**Trigger**: <trigger_id> (<process_ids>)
**Severity**: <max severity across findings>
**Findings Count**: <N>

### Finding <N>: <title>
- **Process**: <process_id> (<process_name>)
- **Severity**: HIGH | CRITICAL
- **Location**: <pipeline, schema, model, or data source>
- **Recommendation**: <actionable data/ML fix>
- **Stage Impact**: Stage <N> (<what must change>)

## Recommended Next Action
- **Type**: inject_into_stage | create_task
- **Target Stage**: <N>
- **Instruction**: <what the target stage must address>
```

5. **Return immediately** — Do not wait for user input. The loop controller creates the dispatch receipt from this output.

See `_shared/protocols/command-dispatch.md` for the full dispatch protocol.

## Receipt Writing (STATE-001)

After completing analysis (standalone or dispatch mode), write a receipt:

1. `mkdir -p .pipeline-state/command-receipts .pipeline-state/process-log`
2. Write `.pipeline-state/command-receipts/data-ml-ops-<YYYYMMDD>-<HHMMSS>.json`:

```json
{
  "command": "data-ml-ops",
  "receipt_id": "data-ml-ops-<YYYYMMDD>-<HHMMSS>",
  "timestamp": "<ISO-8601>",
  "session_context": {
    "session_id": "<dispatch session_id or null>",
    "pipeline": "<auto-orchestrate|auto-audit|auto-debug|standalone>"
  },
  "inputs": {
    "mode": "<standalone|dispatch>",
    "process_ids": ["P-049", "P-050"]
  },
  "outputs": {
    "findings": [{"process": "P-049", "severity": "HIGH", "title": "..."}],
    "severity_max": "HIGH"
  },
  "artifacts": [],
  "processes_executed": ["P-049", "P-050"],
  "next_recommended_action": null,
  "dispatch_context": {
    "trigger_id": "<TRIG-XXX or null>",
    "invoked_by": "<session_id or null>"
  }
}
```

3. For each process executed, append to `.pipeline-state/process-log/<process-id>.jsonl` (STATE-003).

If write fails, log warning and continue — receipt writing MUST NOT block command execution. See `_shared/protocols/cross-pipeline-state.md` for the full receipt schema.

## Related Commands

- `/active-dev` — Sprint execution (may invoke data/ML processes)
- `/release-prep` — Pre-release quality checks (includes data validation)
- `/post-launch` — Post-launch monitoring (includes ML model monitoring)

## Process Reference

Full process definitions: `claude-code/processes/08_data_ml_operations.md`
