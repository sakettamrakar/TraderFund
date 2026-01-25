# PHASE LOCK: Volatility & Market Context Module

## Current Status

| Property | Value |
|----------|-------|
| **Authority Level** | RESEARCH-ONLY |
| **Activation Phase** | Phase 7+ |
| **Current Phase** | Phase 5 |
| **Production Wiring** | ❌ FORBIDDEN |

---

## Activation Requirements

Before this module can influence live trading, ALL of the following must be true:

1. ✅ Project has reached **Phase 7**.
2. ⬜ 30 trading days of passive context logging completed.
3. ⬜ Correlation analysis between regimes and signal quality documented.
4. ⬜ Explicit sign-off recorded in `docs/governance/ACTIVATION_LOG.md`.
5. ⬜ Promotion PR tagged `[PROMOTION]` and approved by Senior Architect.
6. ⬜ 90%+ test coverage verified.

---

## What This Lock Prevents

- ❌ Using volatility labels to filter signals.
- ❌ Using ATR to size positions.
- ❌ Auto-attaching context snapshots to trade signals.
- ❌ Creating "skip trade" rules based on regime.
- ❌ Running without `--research-mode` CLI flag.

---

## Forbidden Actions (Even After Activation)

Even in Phase 7+, the following are NEVER allowed:

- Hard-coded thresholds (e.g., "skip if ATR > 2%")
- Automatic regime-based position sizing
- Direct integration with momentum engine
- Real-time regime changes triggering exits

---

## Override Procedure

There is NO override procedure. The phase lock is enforced at runtime.

To bypass for research:
1. Set `TRADERFUND_ACTIVE_PHASE=6` (or higher) in your environment.
2. Document this in the Activation Log.

---

## Governance Reference

- [RESEARCH_MODULE_GOVERNANCE.md](../../docs/governance/RESEARCH_MODULE_GOVERNANCE.md)
- [MODULE_AUTHORITY_MATRIX.md](../../docs/governance/MODULE_AUTHORITY_MATRIX.md)

---

## Signature

This module was locked on: **2026-01-03**

*Senior Trading Platform Architect*
*TraderFund Project*
