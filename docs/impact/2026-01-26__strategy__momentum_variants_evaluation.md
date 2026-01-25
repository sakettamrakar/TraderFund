# Documentation Impact Declaration (DID)

**ID**: DID-2026-01-26-005
**Date**: 2026-01-26
**Topic**: Momentum Strategy Evolution (Variants)
**Author**: Principal Strategy Evolution Architect

## Context
Following the successful binding of Factor Context v1.1 (Level, Acceleration, Persistence), we are evolving the monolithic `STRATEGY_MOMENTUM_V1` into specialized variants. This allows the system to capture distinct market behaviors without compromising the safety of the baseline.

## Changes
1.  **Strategy Registry**: Created `src/strategy/registry.py` with declarative definitions:
    *   `STRATEGY_MOMENTUM_STRICT_V1`: Baseline (Strong + Accelerating).
    *   `STRATEGY_MOMENTUM_ACCELERATING_V1`: Early Entry (Accelerating).
    *   `STRATEGY_MOMENTUM_PERSISTENT_V1`: Trend Following (Persistent).
2.  **Execution Logic**: Updated `bulk_evaluator.py` and `rejection_analysis.py` to behave dynamically based on the Registry.
3.  **Analysis**: Rejection analysis now checks specific factor requirements (Level, Acceleration, Persistence) against the Context.

## Impact Assessment
- **Safety**: High. Baseline constraints are preserved or strengthened (`STRICT`).
- **Observability**: Rejection reasons will now differ by strategy (e.g., `FACTOR_REQ_MOMENTUM_ACCEL_FLAT` vs `FACTOR_REQ_MOMENTUM_LEVEL_NEUTRAL`), proving the specialized intent.
- **Backward Compatibility**: `STRATEGY_MOMENTUM_V1` key retained in registry for reference.

## Verification
- **EV-RUN**: Will execute all variants across 105 windows.
- **Success Criteria**: Variants must exhibit differentiated rejection patterns consistent with their intent.

## Sign-off
**System Architect**: [AUTOMATED_SIG_STRAT_EVO]
**Date**: 2026-01-26
