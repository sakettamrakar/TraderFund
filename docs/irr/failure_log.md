# Integration Reality Run - Failure Log

## Classification Standard (Mandatory Taxonomy)
- `Temporal Drift`
- `Governance Leakage`
- `Narrative Violations`
- `UI Epistemic Failures`
- `Honest Stagnation`

## Failure Register
| ID | Taxonomy | Severity | Observation | Evidence | Status |
|---|---|---|---|---|---|
| `TDR-001` | Temporal Drift | HIGH | US temporal state remained `CTT 2026-02-06` vs frozen `TE 2026-01-30` (`+7 days`). | `docs/irr/runtime/IRR-2026-02-09-001/post_state.json` | Logged |
| `TDR-002` | Temporal Drift | HIGH | INDIA temporal state remained `CTT 2026-02-09` vs frozen `TE 2026-01-30` (`+10 days`). | `docs/irr/runtime/IRR-2026-02-09-001/post_state.json` | Logged |
| `TDR-003` | Temporal Drift | MEDIUM | Temporal orchestrator could not determine US RDT from configured source. | `docs/irr/runtime/IRR-2026-02-09-001/03_temporal_orchestrator.log` | Logged |
| `GLK-001` | Governance Leakage | CRITICAL | Truth epoch source divergence: `truth_epoch.json` indicates `TRUTH_EPOCH_2026-02-07_01` while temporal and execution docs enforce `TE-2026-01-30`. | `docs/epistemic/truth_epoch.json`, `docs/intelligence/temporal/temporal_state_US.json`, `docs/intelligence/execution_gate_status.json` | Logged |
| `GLK-002` | Governance Leakage | HIGH | INDIA ingestion run injected `IN10Y` as `SYNTHETIC` during a reality run. | `docs/irr/runtime/IRR-2026-02-09-001/02_india_ingestion.log` | Logged |
| `GLK-003` | Governance Leakage | HIGH | EV-TICK factor build for INDIA reported `No benchmark binding for US`, indicating market context leakage. | `docs/irr/runtime/IRR-2026-02-09-001/08_ev_tick.log` | Logged |
| `GLK-004` | Governance Leakage | HIGH | Core policy engine consumed tick contexts and produced `market=UNKNOWN`/`HALTED` due schema mismatch (`regime` vs expected `regime_code` fields). | `docs/irr/runtime/IRR-2026-02-09-001/us_decision_policy.json`, `docs/irr/runtime/IRR-2026-02-09-001/india_decision_policy_via_core_engine.json` | Logged |
| `NV-001` | Narrative Violations | HIGH | Real narrative endpoint returned 404; zero stories and zero narratives were produced. | `docs/irr/runtime/IRR-2026-02-09-001/12_real_market_stories.log` | Logged |
| `UIE-001` | UI Epistemic Failures | MEDIUM | UI backend API passed, but temporal truth source inconsistency means dashboard can expose conflicting epoch narratives depending endpoint source. | `docs/irr/runtime/IRR-2026-02-09-001/13_ui_backend_verify.log`, `docs/epistemic/truth_epoch.json` | Logged |
| `HS-001` | Honest Stagnation | MEDIUM | Ignition verifier pathing is non-operational without manual import surgery; integration step did not self-heal. | `docs/irr/runtime/IRR-2026-02-09-001/04_ignition_verification.log` | Logged |
| `HS-002` | Honest Stagnation | LOW | EV-TICK ingestion produced partial API empties for QQQ/IWM/VIX (`Information` payload), reducing live completeness without hidden fallback. | `docs/irr/runtime/IRR-2026-02-09-001/08_ev_tick.log` | Logged |
| `HS-003` | Honest Stagnation | LOW | US factor context correctly fail-closed to `INSUFFICIENT` and `UNKNOWN` instead of fabricating confidence. | `docs/irr/runtime/IRR-2026-02-09-001/factor_context_US_manual.json` | Logged |

## Handling Rule Applied
All failures were observed and classified only. No patching, no suppression, and no outcome improvement were performed during this run.
