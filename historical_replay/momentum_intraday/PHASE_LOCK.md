# PHASE_LOCK.md — Historical Intraday Momentum Replay

---

## ⚠️ CRITICAL GOVERNANCE NOTICE

This module is **DIAGNOSTIC ONLY**.

---

## Restrictions

### 1. MUST NOT Influence Live Trading

The outputs of this module **MUST NEVER** be used to make live trading decisions. This includes:

- Entry/exit decisions
- Position sizing
- Risk parameters
- Trade timing

### 2. MUST NOT Be Used for Optimization

You **MUST NOT** use replay results to tune or optimize:

- Momentum engine parameters (VWAP thresholds, volume multipliers, etc.)
- Signal filtering rules
- Confidence calculations

Optimization requires formal backtesting infrastructure with proper out-of-sample testing, walk-forward analysis, and statistical validation. This module is NOT that.

### 3. MUST NOT Compare P&L

This module does **NOT** calculate profits or losses. Any mental P&L calculation based on replay data is invalid because:

- Execution slippage is not modeled
- Bid-ask spreads are not modeled
- Order book impact is not modeled
- Position management is not modeled

### 4. MUST NOT Replace Live Observation

Historical replay is a **supplement** to live observation (Phase-4), not a replacement. You must continue running live observation to gather real-world signal data.

---

## Permitted Uses

### ✅ Allowed

- Understanding signal formation patterns
- Analyzing timing of signals relative to price action
- Comparing signal quality across different market conditions
- Training intuition for the momentum strategy
- Debugging unexpected signal behavior
- Verifying that the momentum engine is working correctly

### ❌ Forbidden

- Parameter optimization
- P&L estimation
- Trading decisions
- Curve-fitting
- Any form of "what-if" scenario testing with parameter changes

---

## Review Requirements

Before making ANY changes to the momentum engine based on replay observations:

1. Document the observation in the EOD review
2. Discuss with the team (or self-review with a cool-down period)
3. Validate the hypothesis with live observation data
4. Only then consider parameter changes through proper change control

---

## Audit Trail

All replay runs are logged to `observations/historical_replay/`. These logs should be retained for audit purposes. The `mode=HISTORICAL_REPLAY` label ensures all outputs are clearly identified.

---

## Last Review

- **Date**: 2026-01-05
- **Reviewer**: System-generated during module creation
- **Status**: LOCKED — No changes without governance review

---

## Contact

For questions about this governance policy, consult the project lead or the RESEARCH_MODULE_GOVERNANCE.md document.
