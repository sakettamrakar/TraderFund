# Validation System

## Purpose

TraderFund now includes a first-class self-healing validation subsystem under `traderfund/validation/`.

The subsystem exists to:

- validate ingestion, memory, research, evaluation, and dashboard phases continuously
- centralize validation knowledge and task registration
- diagnose failures into root-cause categories instead of surfacing raw check failures only
- propose or apply safe remediations without touching capital, execution, or raw source data
- reuse existing desk skills and LLM infrastructure where they add value

## Architecture

The subsystem is organized as:

```text
traderfund/validation/
    __init__.py
    validation_engine.py
    validation_registry.py
    diagnosis_engine.py
    remediation_engine.py
    validation_runner.py
```

### validation_engine

`validation_engine.py` owns the execution model.

- Defines the validation task contract.
- Defines structured `ValidationResult` outputs.
- Executes registered tasks against a phase-specific context.

Output shape is normalized as:

```json
{
  "phase": "ingestion",
  "task": "schema_validation",
  "status": "FAIL",
  "reason": "schema_drift_detected",
  "details": {
    "processed_missing": ["volume"]
  }
}
```

### validation_registry

`validation_registry.py` is the knowledge center.

- Maintains the repository component map.
- Registers validation tasks by phase.
- Encodes the concrete checks for ingestion, memory, research, evaluation, and dashboard.

Registered tasks currently include:

- Ingestion: `schema_validation`, `timestamp_validation`, `null_handling`, `data_lineage`
- Memory: `layer_routing`, `mutation_control`, `cross_layer_contamination`
- Research: `factor_determinism`, `regime_gating`, `reproducibility`
- Evaluation: `score_consistency`, `evolution_integrity`
- Dashboard: `traceability`, `freshness`, `read_only_guarantee`

### diagnosis_engine

`diagnosis_engine.py` maps failures to root causes.

Examples:

- schema drift -> `ingestion_parser_issue`
- timestamp failure -> `source_feed_time_error`
- factor determinism failure -> `factor_computation_inconsistency`
- missing regime halt -> `regime_gate_missing`
- dashboard provenance failure -> `dashboard_provenance_gap`

The engine optionally reuses TraderFund LLM APIs for terse failure explanations when one of these is configured:

- `VALIDATION_ENABLE_LLM=1`
- `LLM_MODEL_PATH`
- `MOCK_GEMINI=1`

If no LLM is available, diagnosis remains deterministic.

### remediation_engine

`remediation_engine.py` converts diagnoses into safe remediation actions.

It supports:

- desk-skill-based diagnostics through `bin/run-skill.py`
- safe command-based repair suggestions such as canonical recomputation
- optional auto-application of safe remediations

Hard safety rule:

- never modify capital
- never modify execution
- never modify raw source data

### validation_runner

`validation_runner.py` orchestrates validation loops.

It provides:

- `run_post_ingestion()`
- `run_post_research()`
- `run_post_evaluation()`
- `run_pre_dashboard_refresh()`
- `run_loop()` for periodic multi-phase validation

Every run persists the latest structured summary to:

- `logs/validation/{phase}_{hook}_latest.json`

## Self-Healing Loop

The runtime loop is:

1. Execute registered validations for the phase.
2. Collect structured results.
3. Diagnose failures into root-cause classes.
4. Propose safe remediations.
5. Optionally apply remediations that are explicitly marked safe.
6. Persist the run summary.

This keeps validation observable and explainable rather than burying failures inside ad hoc scripts.

## Operator Usage

The validation subsystem is intended to be used in two modes:

- automatic boundary validation triggered by ingestion, research, evaluation, and dashboard refresh hooks
- manual operator-driven validation when investigating drift, checking readiness, or stabilizing the system after a failure

### Run One Phase Manually

From the repository root:

```powershell
python -m traderfund.validation.validation_runner --phase ingestion --hook manual --market US
```

Valid phases are:

- `ingestion`
- `memory`
- `research`
- `evaluation`
- `dashboard`

Exit behavior:

- exit code `0`: no FAIL results for that phase
- exit code `1`: at least one task returned FAIL

### Run A Full Manual Sweep

PowerShell example:

```powershell
foreach ($phase in 'ingestion','memory','research','evaluation','dashboard') {
  python -m traderfund.validation.validation_runner --phase $phase --hook manual --market US
  if ($LASTEXITCODE -ne 0) { break }
}
```

This is the preferred operator entrypoint when you want a clean readiness check across the whole subsystem.

### Apply Safe Auto-Remediation

You can allow the remediation engine to apply explicitly safe actions for a single phase:

```powershell
python -m traderfund.validation.validation_runner --phase dashboard --hook manual --market US --auto-remediate
```

Operator guidance:

- use `--auto-remediate` only for the phase currently under investigation
- review the persisted summary after the run
- re-run the same phase without `--auto-remediate` to confirm the fix
- if the failed phase feeds downstream phases, re-run those downstream phases as well

### Read Results

Each run writes the latest structured summary to:

- `logs/validation/{phase}_{hook}_latest.json`

Important fields in each summary:

- `results`: task-level PASS / FAIL / SKIP details
- `diagnoses`: root-cause mappings for FAIL tasks
- `remediations`: proposed safe actions
- `applied_remediations`: actions actually executed when auto-remediation is enabled
- `has_failures`: overall phase failure flag

### Optional Daily Review On The Scheduler Path

If you want the daily scheduler to analyze the latest validation outputs automatically, enable the opt-in review task on the wrapper:

```powershell
python infra_hardening/scheduler/wrapper.py --mode daily --enable-validation-review
```

That task reads the latest phase summaries from `logs/validation/`, writes a daily aggregate report to `logs/validation/daily/`, and fails the daily run if it detects critical validation failures or missing phase summaries.

To make the Windows scheduled daily task include this review, register it with:

```powershell
python -m infra_hardening.scheduler.manage --register --daily --enable-validation-review
```

The review is intentionally not part of the default daily command so the capability stays attached to the canonical scheduler path but remains operator-controlled.

### Recommended Operator Sequence

Use this order when manually stabilizing the system:

1. Run the target phase manually.
2. If it FAILs, inspect `diagnoses` and `remediations` in the latest summary JSON.
3. If the proposed repair is safe and phase-local, rerun that phase with `--auto-remediate`.
4. Re-run the same phase without auto-remediation to confirm PASS.
5. Re-run any downstream dependent phases.

### Historical Replay Validation

The validation subsystem itself does not run the full historical replay pipeline automatically.

Use the evaluation pipeline plus manual semantic comparison when replay determinism must be verified:

```powershell
python src/evolution/pipeline_runner.py docs/evolution/evaluation_profiles/EV-HISTORICAL-ROLLING-V1.yaml
```

Then validate replay artifacts semantically rather than by raw hash, because evaluation outputs embed runtime timestamps.

## Reused Capabilities

### Desk Skills

The subsystem reuses the existing desk-skill surface under `.agent/skills/` through `bin/run-skill.py`.

Current integration targets include:

- `constraint-validator` for schema and contract drift diagnosis
- `cognitive-order-validator` for research/regime-order failures
- `decision-ledger-curator` for evaluation/evolution integrity checks
- `audit-log-viewer` for dashboard provenance/freshness issues

### LLM APIs

The subsystem reuses:

- `llm_integration/client.py`
- `automation/gemini_bridge.py`
- `automation/executors/gemini_fallback.py`

LLM usage is intentionally bounded to:

- failure explanation
- root-cause expansion
- remediation suggestion text

It is not used as the source of truth for pass/fail decisions.

## Integration Points

Validation now runs automatically at these boundaries:

- after Angel SmartAPI ingestion in `ingestion/api_ingestion/angel_smartapi/market_data_ingestor.py`
- after canonical intraday processing in `processing/intraday_candles_processor.py`
- after US proxy ingestion in `ingestion/us_market/ingest_daily.py`
- memory validation piggy-backs on the post-ingestion hook so layer routing and contamination checks run whenever ingestion completes
- after research orchestration in `research_modules/pipeline_controller/runner.py`
- after evaluation runs in `src/evolution/pipeline_runner.py`
- before dashboard refresh in `src/dashboard/backend/app.py`

The dashboard integration is throttled with a short TTL so validation remains continuous without running on every GET request.