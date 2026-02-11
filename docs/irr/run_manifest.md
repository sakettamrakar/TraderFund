# Integration Reality Run - Manifest

## Run Identity
- Run ID: `IRR-2026-02-09-001`
- Date: `2026-02-09`
- Start (IST): `2026-02-09T19:11:36+05:30`
- End (IST): `2026-02-09T19:15:10+05:30`
- Duration: `~3m 34s`
- Follow-on Run: `SHADOW-2026-02-09-001`

## Scope
- Markets: `US`, `INDIA`
- Objective: Governance stress test under frozen temporal truth and disabled execution
- Runtime paths exercised:
  - Real ingestion (`ingestion/us_market/ingest_daily.py`, `scripts/india_data_acquisition.py`)
  - Temporal canonicalization (`scripts/temporal_orchestrator.py`)
  - Regime/factor generation (`src/evolution/orchestration/ev_tick.py`, manual context build for US)
  - Policy and fragility (`src/intelligence/decision_policy_engine.py`, `src/intelligence/fragility_policy_engine.py`, `scripts/india_policy_evaluation.py`)
  - Narrative reality check (`scripts/run_real_market_stories.py`)
  - UI epistemic check (`scripts/verify_inspection_backend.py`)

## Governance Invariants Enforced
- Truth Epoch was not advanced.
- Execution gate remained `CLOSED`.
- No broker or capital execution path was enabled.
- No asset ranking or optimization routine was introduced.

## Invariant Verification
- `docs/epistemic/truth_epoch.json` SHA256 unchanged:
  - Before: `0949CFC2EDA48572A6E3216E11DEA52DD106C9EA39D784F9917A70048E83E96E`
  - After: `0949CFC2EDA48572A6E3216E11DEA52DD106C9EA39D784F9917A70048E83E96E`
- `docs/intelligence/execution_gate_status.json` SHA256 unchanged:
  - Before: `4047E00B24CFA6F7EE4D4BA5E2AF6BB82F9594CB4631598E1BE81521714014E1`
  - After: `4047E00B24CFA6F7EE4D4BA5E2AF6BB82F9594CB4631598E1BE81521714014E1`

## Command Ledger (IRR)
| Step | Command | Exit | Evidence |
|---|---|---:|---|
| 01 | `python ingestion/us_market/ingest_daily.py` | 0 | `docs/irr/runtime/IRR-2026-02-09-001/01_us_ingestion.log` |
| 02 | `python scripts/india_data_acquisition.py` | 0 | `docs/irr/runtime/IRR-2026-02-09-001/02_india_ingestion.log` |
| 03 | `python scripts/temporal_orchestrator.py` | 0 | `docs/irr/runtime/IRR-2026-02-09-001/03_temporal_orchestrator.log` |
| 04 | `python scripts/ignition_verification.py` | 1 | `docs/irr/runtime/IRR-2026-02-09-001/04_ignition_verification.log` |
| 05 | `python src/evolution/orchestration/ev_tick.py` | 0 | `docs/irr/runtime/IRR-2026-02-09-001/08_ev_tick.log` |
| 06 | Policy evaluation from tick contexts | 0 | `docs/irr/runtime/IRR-2026-02-09-001/09_policy_eval_from_tick.log` |
| 07 | Manual US context build (no code patch) | 0 | `docs/irr/runtime/IRR-2026-02-09-001/10_manual_us_context_build.log` |
| 08 | US policy + fragility on manual context | 0 | `docs/irr/runtime/IRR-2026-02-09-001/11_us_policy_from_manual_context.log` |
| 09 | `python scripts/run_real_market_stories.py` | 0 | `docs/irr/runtime/IRR-2026-02-09-001/12_real_market_stories.log` |
| 10 | `python scripts/verify_inspection_backend.py` | 0 | `docs/irr/runtime/IRR-2026-02-09-001/13_ui_backend_verify.log` |

## Runtime Evidence Directory
- `docs/irr/runtime/IRR-2026-02-09-001/`
- `docs/irr/runtime/SHADOW-2026-02-09-001/`
