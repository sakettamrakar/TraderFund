# Validation Integration Report

## Summary

TraderFund now has an integrated validation subsystem under `traderfund/validation/` and phase hooks at ingestion, research, evaluation, and dashboard refresh boundaries.

The implementation is registry-driven, diagnosis-aware, and remediation-capable.

## Component Map

### Ingestion

- `ingestion/api_ingestion/alpha_vantage/`
- `ingestion/api_ingestion/angel_smartapi/`
- `ingestion/historical_backfill/`
- `ingestion/incremental_update/`
- `ingestion/universe_expansion/`
- `processing/intraday_candles_processor.py`
- `src/ingestion/`

### Memory Layer (V3)

- `docs/memory/`
- `docs/contracts/layer_interaction_contract.md`
- `docs/verification_runs/RUN_002_MEMORY.md`
- `src/layers/`
- `docs/intelligence/`

### Research And Factor Computation

- `research_modules/pipeline_controller/`
- `research_modules/universe_hygiene/`
- `research_modules/structural_capability/`
- `research_modules/energy_setup/`
- `research_modules/participation_trigger/`
- `research_modules/momentum_confirmation/`
- `research_modules/sustainability_risk/`
- `src/layers/factor_live.py`
- `src/intelligence/`

### Evaluation / Evolution

- `src/evolution/pipeline_runner.py`
- `src/evolution/factor_context_builder.py`
- `src/evolution/bulk_evaluator.py`
- `src/evolution/decision_replay.py`
- `src/evolution/paper_pnl.py`
- `src/evolution/rejection_analysis.py`
- `src/evolution/compile_bundle.py`
- `docs/evolution/evaluation_profiles/`

### Dashboard

- `src/dashboard/backend/app.py`
- `src/dashboard/backend/loaders/`
- `src/dashboard/frontend/src/`
- `docs/dashboard/`

### Desk Skills

- `.agent/skills/`
- `bin/run-skill.py`

### LLM Development APIs

- `llm_integration/client.py`
- `llm_integration/engine/explainer.py`
- `automation/gemini_bridge.py`
- `automation/executors/gemini_fallback.py`
- `automation/agents/validation_agent.py`

## New Modules

- `traderfund/validation/__init__.py`
- `traderfund/validation/validation_engine.py`
- `traderfund/validation/validation_registry.py`
- `traderfund/validation/diagnosis_engine.py`
- `traderfund/validation/remediation_engine.py`
- `traderfund/validation/validation_runner.py`

## Validation Tasks Registered

### Ingestion

- `schema_validation`
- `timestamp_validation`
- `null_handling`
- `data_lineage`

### Memory

- `layer_routing`
- `mutation_control`
- `cross_layer_contamination`

### Research

- `factor_determinism`
- `regime_gating`
- `reproducibility`

### Evaluation

- `score_consistency`
- `evolution_integrity`

### Dashboard

- `traceability`
- `freshness`
- `read_only_guarantee`

## Reused Modules

### Desk Skills Reused

- `constraint-validator`
- `cognitive-order-validator`
- `decision-ledger-curator`
- `audit-log-viewer`

These are integrated as remediation or diagnostic actions through `bin/run-skill.py`.

### LLM APIs Reused

- Local LLM access through `llm_integration/client.py`
- Gemini fallback through `automation/gemini_bridge.py`

These are used only for explanatory diagnostics and remediation suggestions.

## Integration Points Added

### Post-Ingestion

- `ingestion/api_ingestion/angel_smartapi/market_data_ingestor.py`
- `processing/intraday_candles_processor.py`
- `ingestion/us_market/ingest_daily.py`

The post-ingestion hook runs both the `ingestion` and `memory` validation phases so canonical routing and contamination checks remain attached to live data movement.

### Post-Research

- `research_modules/pipeline_controller/runner.py`

### Post-Evaluation

- `src/evolution/pipeline_runner.py`

### Pre-Dashboard Refresh

- `src/dashboard/backend/app.py`

The dashboard hook runs through HTTP middleware with a 60-second throttle window so validation is continuous but not wasteful.

## Operational Notes

- Latest validation summaries are persisted to `logs/validation/`.
- Validation decisions are deterministic even when LLM assistance is unavailable.
- Remediation auto-application is restricted to actions marked safe.
- The subsystem explicitly blocks remediation actions that target capital, execution, or raw source data.