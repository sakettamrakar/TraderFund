# PHASE LOCK: Backtesting Engine

## Current Status

| Property | Value |
|----------|-------|
| **Authority Level** | RESEARCH-ONLY |
| **Activation Phase** | Phase 6+ |
| **Current Phase** | Phase 5 |
| **Production Wiring** | ❌ FORBIDDEN |

---

## Activation Requirements

Before this module can be wired to production systems, ALL of the following must be true:

1. ✅ Project has reached **Phase 6**.
2. ⬜ 30 trading days of error-free research usage completed.
3. ⬜ 100 simulated trades validated against paper trading results.
4. ⬜ Explicit sign-off recorded in `docs/governance/ACTIVATION_LOG.md`.
5. ⬜ Promotion PR tagged `[PROMOTION]` and approved by Senior Architect.
6. ⬜ 90%+ test coverage verified.

---

## What This Lock Prevents

- ❌ Importing this module from `core_modules/`.
- ❌ Running without `--research-mode` CLI flag.
- ❌ Initializing `BacktestEngine` when `ACTIVE_PHASE < 6`.
- ❌ Writing results to production log directories.

---

## Override Procedure

There is NO override procedure for this phase lock. The lock is enforced at runtime via environment variable checks. To bypass the lock:

1. Set `TRADERFUND_ACTIVE_PHASE=6` (or higher) in your environment.
2. This is considered an **intentional architectural decision**.
3. Any bypass MUST be documented in the Activation Log.

---

## Governance Reference

This phase lock implements the policies defined in:

- [RESEARCH_MODULE_GOVERNANCE.md](../../docs/governance/RESEARCH_MODULE_GOVERNANCE.md)
- [MODULE_AUTHORITY_MATRIX.md](../../docs/governance/MODULE_AUTHORITY_MATRIX.md)

---

## Signature

This module was locked on: **2026-01-03**

*Senior Trading Platform Architect*
*TraderFund Project*
