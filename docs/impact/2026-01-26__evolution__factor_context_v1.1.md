# Documentation Impact Declaration (DID)

**ID**: DID-2026-01-26-004
**Date**: 2026-01-26
**Topic**: Factor Context Extension v1.1
**Author**: Principal Market Factor Architecture Engineer

## Context
Following successful v1 integration, we are extending the Factor Context to v1.1 to provide richer observational resolution (acceleration, persistence, trend) without altering strategy logic.

## Changes
1.  **Schema Extension**: Updated `docs/evolution/context/factor_context_schema.md` to v1.1.0.
    *   Added `momentum.acceleration`, `momentum.persistence`.
    *   Added `value.trend`, `quality.stability`.
    *   Added `volatility.dispersion`.
2.  **Execution Binding**: Updated `src/evolution/factor_context_builder.py`.
    *   Generates v1.1 structure with mocked neutral states.
    *   Maintains v1 keys for strict backward compatibility.
3.  **DWBS**: Added Principle `PRIN-8` (Explanation not Coercion) and Invariant `EV-INV-004` (No gating on v1.1 fields).

## Impact Assessment
- **Epistemic**: Greatly enhanced explanatory power for rejections. "Why is momentum weak?" can now be answered (e.g., "Decelerating").
- **Backward Compatibility**: Verified. v1 consumers (e.g., existing strategies) can still access `strength` or `spread` as expected.
- **Safety**: No strategy logic modified. No risk of unintended trading behavior.

## Verification
- **Output**: `factor_context_builder.py` produces valid v1.1 JSON with v1 aliases.

## Sign-off
**System Architect**: [AUTOMATED_SIG_FACTOR_EXT]
**Date**: 2026-01-26
