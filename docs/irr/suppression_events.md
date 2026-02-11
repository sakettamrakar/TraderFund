# Integration Reality Run - Suppression Events

## Scope
Suppression observations from policy and fragility outputs generated during IRR runtime.

## US (Manual Context Path)
- Context: `regime=UNKNOWN`, factor sufficiency `INSUFFICIENT`
- Decision output: `OBSERVE_ONLY`
- Fragility output: `OBSERVE_ONLY` retained, no additional revocations

| Permission Family | Status | Suppression Source | Evidence |
|---|---|---|---|
| Entry intents (`ALLOW_LONG_ENTRY`, `ALLOW_SHORT_ENTRY`, `ALLOW_LONG_ENTRY_SPECIAL`) | Suppressed | Decision policy fail-closed on unknown regime | `docs/irr/runtime/IRR-2026-02-09-001/us_decision_policy_manual.json` |
| Rebalancing intent (`ALLOW_REBALANCING`) | Suppressed | Not granted by decision policy | `docs/irr/runtime/IRR-2026-02-09-001/us_decision_policy_manual.json` |
| Observation intent (`OBSERVE_ONLY`) | Allowed | Decision policy | `docs/irr/runtime/IRR-2026-02-09-001/us_fragility_policy_manual.json` |

## INDIA (Canonical India Policy Pipeline)
- Context: `regime=BULLISH`
- Decision output: `ALLOW_LONG_ENTRY`, `ALLOW_POSITION_HOLD`
- Fragility output: no revocations

| Permission Family | Status | Suppression Source | Evidence |
|---|---|---|---|
| Long entry | Allowed | Decision policy | `docs/intelligence/decision_policy_INDIA.json` |
| Short entry | Suppressed | Regime gate (BULLISH path does not grant short) | `docs/intelligence/decision_policy_INDIA.json` |
| Hold | Allowed | Decision + fragility | `docs/intelligence/fragility_context_INDIA.json` |
| Rebalancing | Suppressed | Not granted in current regime path | `docs/intelligence/decision_policy_INDIA.json` |

## Schema-Leakage Policy Path (Tick Contexts)
Both US and INDIA policy runs against tick-generated contexts resolved to `market=UNKNOWN`, yielding full operational suppression.

| Market | Policy State | Final Authorized Intents | Evidence |
|---|---|---|---|
| US | HALTED | none | `docs/irr/runtime/IRR-2026-02-09-001/us_decision_policy.json` |
| INDIA | HALTED | none | `docs/irr/runtime/IRR-2026-02-09-001/india_decision_policy_via_core_engine.json` |

## Suppression Integrity Note
Suppression remained monotonic in all observed paths: downstream fragility did not restore any upstream-denied intent.
