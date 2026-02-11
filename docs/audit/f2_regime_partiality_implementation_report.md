# F2 Regime Partiality Implementation Report

## Scope
Implementation executed for F2 remediation using the `DEGRADE-ON-PARTIAL` pattern.

- Execution mode: `REAL_RUN`
- Truth Epoch: `TE-2026-01-30` (frozen)
- Markets: `US`, `INDIA`
- Invariants preserved: `INV-NO-EXECUTION`, `INV-NO-CAPITAL`, `INV-HONEST-STAGNATION`, `INV-TRUTH-EPOCH-EXPLICIT`, `INV-NO-TEMPORAL-INFERENCE`, `INV-PROXY-CANONICAL`

## 1. Canonical Partiality Detection
Implemented market-scoped canonical partiality detection in:
- `src/governance/canonical_partiality.py`

Implemented states:
- `CANONICAL_COMPLETE`
- `CANONICAL_PARTIAL`
- `CANONICAL_MIXED`

Detection signals per market:
- Required role presence
- Role status from parity diagnostics
- Role freshness alignment relative to `CTT`
- Freshness skew across required roles

Persisted artifacts:
- `docs/intelligence/canonical_partiality_state_US.json`
- `docs/intelligence/canonical_partiality_state_INDIA.json`

## 2. Regime Degradation Logic
Implemented explicit regime degradation when canonical state is not complete:
- If `canonical_state != CANONICAL_COMPLETE` then:
  - `regime_state/regime_code = UNKNOWN`
  - `regime_confidence = DEGRADED`
  - `regime_reason = Partial canonical inputs`

Implemented in:
- `src/evolution/regime_context_builder.py`
- `src/evolution/orchestration/ev_tick.py`
- `scripts/india_policy_evaluation.py`

Observed runtime result:
- `US` degraded to `UNKNOWN (PARTIAL DATA)` due missing/stale `rates_anchor` role.
- `INDIA` remained `CANONICAL_COMPLETE` and retained evaluated regime.

## 3. Downstream Propagation
Policy layer now consumes canonical partiality and fail-closes:
- `src/intelligence/decision_policy_engine.py`

Behavior:
- If `canonical_state != CANONICAL_COMPLETE`:
  - `policy_state = HALTED`
  - `permissions = [OBSERVE_ONLY]`
  - no regime inference path is executed

Resulting policy artifact example:
- `docs/intelligence/decision_policy_US.json` now carries degraded regime metadata and `OBSERVE_ONLY` enforcement.

Fragility layer was not expanded and remains subtractive-only.

## 4. Dashboard Disclosure
Updated dashboard market snapshot path to disclose partiality and degraded regime semantics:
- `src/dashboard/backend/loaders/market_snapshot.py`
- `src/dashboard/backend/api.py`
- `src/dashboard/frontend/src/components/MarketSnapshot.jsx`
- `src/dashboard/frontend/src/components/MarketSnapshot.css`

Displayed fields now include:
- `REGIME: UNKNOWN (PARTIAL DATA)` when degraded
- `CanonicalState`
- missing/stale role lists
- concise degradation reason

## 5. Cross-Market Isolation
Partiality is computed and persisted independently per market.

Validation evidence:
- `US`: `CANONICAL_PARTIAL` (rates role issue)
- `INDIA`: `CANONICAL_COMPLETE`
- No cross-market state override path introduced.

## 6. Audit Logging
Persisted under:
- `docs/audit/f2_regime_partiality/partiality_detections.jsonl`
- `docs/audit/f2_regime_partiality/regime_degradations.jsonl`

Logged events:
- canonical partiality detections
- regime degradations with market, reason, and source

## Validation Executed
Commands executed:
- `python -m py_compile src/governance/canonical_partiality.py`
- `python -m py_compile src/intelligence/decision_policy_engine.py scripts/india_policy_evaluation.py src/evolution/regime_context_builder.py src/evolution/orchestration/ev_tick.py src/dashboard/backend/loaders/market_snapshot.py src/dashboard/backend/api.py`
- `python scripts/india_policy_evaluation.py`
- `python src/evolution/orchestration/ev_tick.py`
- runtime loader validation for market snapshot payloads (`US`, `INDIA`)

Observed runtime outcomes:
- `US` snapshot now returns `Regime = UNKNOWN (PARTIAL DATA)`, `CanonicalState = CANONICAL_PARTIAL`, with explicit missing/stale role disclosure.
- `INDIA` snapshot returns canonical-complete regime with no degradation.

## Non-Goals Compliance
Confirmed not implemented:
- No Truth Epoch advancement.
- No automatic regime or evaluation trigger.
- No factor computation changes.
- No ingestion cadence modification.
- No data backfilling.
- No execution or capital enablement.
- No implementation of role-weighted or market-scoped regime logic variants.
