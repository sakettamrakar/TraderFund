# Dashboard Loader → Artifact Mapping

**Created:** 2026-05-17
**Purpose:** Maps every dashboard backend loader to its producing pipeline stage and canonical artifact.

---

## Loader Inventory

| API Endpoint | Loader Function | Source Artifact | Producer Stage | Missing-Data Behavior |
| :--- | :--- | :--- | :--- | :--- |
| `/api/system/status` | `load_system_status` | `docs/intelligence/execution_gate_status.json` | `intelligence.engine` | Returns `UNKNOWN` status with `epoch_bounded: false` |
| `/api/layers/health` | `load_layer_health` | `docs/intelligence/system_layer_health.json` | `intelligence.engine` | Returns all layers as `UNKNOWN` with error message |
| `/api/market/snapshot` | `load_market_snapshot` | `docs/evolution/ticks/{tick_id}/{market}/regime_context.json` | `evolution.pipeline_runner` | Returns empty dict |
| `/api/watchers/timeline` | `load_watcher_timeline` | Tick history dirs | `evolution.pipeline_runner` | Returns empty list |
| `/api/strategies/eligibility` | `load_strategy_eligibility` | Strategy registry files | `research_modules` | Returns empty eligibility |
| `/api/meta/summary` | `load_meta_summary` | `docs/meta/` files | Various | Returns empty summary |
| `/api/system/narrative` | `load_system_narrative` | `docs/intelligence/` narrative files | `intelligence.engine` | Returns empty narrative |
| `/api/system/blockers` | `load_system_blockers` | `docs/intelligence/` blocker files | `intelligence.engine` | Returns empty blockers |
| `/api/intelligence/suppression/{market}` | `load_suppression_status` | `docs/intelligence/suppression_state_{market}.json` | `intelligence.engine` | Returns empty suppression state |
| `/api/capital/readiness` | `load_capital_readiness` | Capital assessment files | `capital.assessment` | Returns not-ready state |
| `/api/capital/history` | `load_capital_history` | Capital history files | `capital.assessment` | Returns empty history |
| `/api/macro/context` | `load_macro_context` | Macro context files | `research_modules` | Returns empty context |
| `/api/intelligence/gate` | `load_execution_gate` | `docs/intelligence/execution_gate_status.json` | `intelligence.engine` | Returns gate as `UNKNOWN` |
| `/api/intelligence/parity/{market}` | `load_market_parity` | `docs/intelligence/market_parity_{market}.json` | `intelligence.engine` | Returns empty parity |
| `/api/meta/evaluation/scope` | `load_evaluation_scope` | `docs/intelligence/` scope files | `intelligence.engine` | Returns empty scope |
| `/api/intelligence/stress_posture` | `load_stress_posture` | `docs/intelligence/stress_posture.json` | `intelligence.engine` | Returns empty posture |
| `/api/intelligence/constraint_posture` | `load_constraint_posture` | `docs/intelligence/constraint_posture.json` | `intelligence.engine` | Returns empty constraints |
| `/api/intelligence/snapshot` | `load_intelligence_snapshot` | `docs/intelligence/intelligence_snapshot_{market}.json` | `intelligence.engine` | Returns empty snapshot |
| `/api/intelligence/policy/{market}` | `load_decision_policy` | `docs/intelligence/decision_policy_{market}.json` | `intelligence.engine` | Returns empty policy |
| `/api/intelligence/fragility/{market}` | `load_fragility_context` | `docs/intelligence/fragility_context_{market}.json` | `intelligence.engine` | Returns empty context |
| `/api/data_anchor` | `load_data_anchor` | `docs/epistemic/truth_epoch.json` | `epistemic.truth_epoch` | Returns `UNKNOWN` epoch |
| `/api/inspection/stress_scenarios` | `load_stress_scenarios` | Static audit report | `inspection` (read-only) | Returns empty scenarios |
| `/api/intelligence/temporal/status` | `load_temporal_status` | `docs/intelligence/temporal/temporal_state_{market}.json` | `intelligence.engine` | Returns `TEMPORAL_STATE_MISSING` error |
| `/api/portfolio/*` | `load_portfolio_*` | Broker API + cached portfolio files | `portfolio.refresh` | Returns empty / not-found |

---

## Provenance Contract

Every loader response includes provenance fields via `attach_provenance()`:

| Field | Type | Description |
| :--- | :--- | :--- |
| `source_artifact` | `string` | Canonical path of the artifact that produced this data |
| `trace_id` | `string` | `{source_artifact}::{truth_epoch}` |
| `epoch_bounded` | `bool` | Whether the data is tied to a known truth epoch |
| `truth_epoch` | `string` | The truth epoch ID or `UNKNOWN` |

---

## Manifest Integration

When the pipeline manifest is available at `logs/validation/pipeline_manifest.json`, dashboard loaders
can resolve artifacts from it. See `src/dashboard/backend/loaders/manifest_loader.py` for the helper.
