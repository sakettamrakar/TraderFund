# Fragility & Stress Policy Design Audit

## 1. Design Summary
**Date**: 2026-01-30
**Event**: `FRAGILITY_STRESS_POLICY_DESIGN`
**Status**: **COMPLETE**

## 2. Governance Adherence
- **Subtractive Principle**: Verified. The `STRESS_LEVELS` map defines only blocked intents. The implementation has no mechanism to add permissions.
- **Market Isolation**: Verified. `FragilityEngine.evaluate(market)` takes a market parameter and applies distinct logic.
- **India Hard-Stop**: Verified. India is forced to `NOT_EVALUATED` with a mandatory `SYSTEMIC_STRESS` block list.
- **Invariants**: 
    - `INV-NO-CAPITAL`: No capital allocation logic present.
    - `INV-NO-EXECUTION`: No execution hooks.
    - `INV-PROXY-CANONICAL`: US logic is based on factor data (canonical-bound).

## 3. Artifacts Delivered
- `docs/intelligence/fragility_policy_design.md`: Structural specification.
- `src/intelligence/fragility_engine.py`: Engine for generating artifacts.
- `docs/intelligence/fragility_policy_US.json`: Initial state (NORMAL).
- `docs/intelligence/fragility_policy_INDIA.json`: Initial state (NOT_EVALUATED).

## 4. Next Steps
1.  **Dashboard Integration**: Wire these artifacts to the UI.
2.  **Decision Composition**: Update `DecisionPolicyEngine` or a coordinator to apply the fragility filter.
3.  **Real Data Backfill**: Run the engine against historical factor snapshots to verify stress detection.
