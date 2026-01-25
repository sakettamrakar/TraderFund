# PHASE LOCK: Risk Modeling & Position Sizing Module

## Current Status

| Property | Value |
|----------|-------|
| **Authority Level** | RESEARCH-ONLY |
| **Activation Phase** | Phase 8+ |
| **Current Phase** | Phase 5 |
| **Live Capital Influence** | ❌ FORBIDDEN |

---

## Activation Requirements

Before this module can influence live position sizing, ALL of the following must be true:

1. ✅ Project has reached **Phase 8**.
2. ⬜ 50 simulated trades compared to actual outcome (if manual sizing was used).
3. ⬜ Risk model selection documented and justified.
4. ⬜ Explicit sign-off recorded in `docs/governance/ACTIVATION_LOG.md`.
5. ⬜ Promotion PR tagged `[PROMOTION]` and approved by Senior Architect.
6. ⬜ 90%+ test coverage verified.

---

## What This Lock Prevents

- ❌ Live position sizing based on model outputs.
- ❌ Automatic stop placement.
- ❌ Capital allocation to live trades.
- ❌ Running without `--research-mode` CLI flag.

---

## Forbidden Actions (Even After Activation)

The following are NEVER allowed:

- Auto-adjusting risk based on recent P&L
- Kelly Criterion applied without human review
- Dynamic daily loss limits
- Direct integration with order execution

---

## Governance Reference

- [RESEARCH_MODULE_GOVERNANCE.md](../../docs/governance/RESEARCH_MODULE_GOVERNANCE.md)
- [MODULE_AUTHORITY_MATRIX.md](../../docs/governance/MODULE_AUTHORITY_MATRIX.md)

---

## Signature

This module was locked on: **2026-01-03**

*Senior Trading Platform Architect*
*TraderFund Project*
