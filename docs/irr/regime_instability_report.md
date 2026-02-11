# Integration Reality Run - Regime Instability Report

## Observed Regime States (2026-02-09)
| Market | Path | Regime | Confidence Signal | Evidence |
|---|---|---|---|---|
| US | Manual context build (no code patch) | `UNKNOWN` | Factor sufficiency `INSUFFICIENT` | `docs/irr/runtime/IRR-2026-02-09-001/regime_context_US_manual.json`, `docs/irr/runtime/IRR-2026-02-09-001/factor_context_US_manual.json` |
| INDIA | Canonical India pipeline | `BULLISH` | Momentum state `bullish`, vol `normal` | `docs/evolution/context/regime_context_INDIA.json`, `docs/evolution/context/factor_context_INDIA.json` |
| US + INDIA | EV-TICK path | `UNKNOWN` downstream policy market due schema mismatch | Policy resolved to `market=UNKNOWN` | `docs/irr/runtime/IRR-2026-02-09-001/us_decision_policy.json`, `docs/irr/runtime/IRR-2026-02-09-001/india_decision_policy_via_core_engine.json` |

## Instability Signals
| ID | Signal | Type | Evidence |
|---|---|---|---|
| `RST-001` | Same day produced two incompatible India policy states (`HALTED UNKNOWN` vs `ACTIVE BULLISH`) depending orchestration path. | Governance Leakage | `docs/irr/runtime/IRR-2026-02-09-001/india_decision_policy_via_core_engine.json`, `docs/intelligence/decision_policy_INDIA.json` |
| `RST-002` | US remained fail-closed (`UNKNOWN`) despite successful partial ingestion, indicating unresolved benchmark binding path. | Honest Stagnation | `docs/irr/runtime/IRR-2026-02-09-001/10_manual_us_context_build.log` |
| `RST-003` | Temporal lag remained high (`US +7d`, `INDIA +10d`), amplifying stale regime risk. | Temporal Drift | `docs/irr/runtime/IRR-2026-02-09-001/post_state.json` |

## Governance Impact
Regime-driven policy behavior is not stable across runtime paths, which invalidates consistent interpretation and blocks safe truth advancement.
