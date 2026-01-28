# Macro Layer Principles

**Version**: 1.0  
**Date**: 2026-01-29  
**Status**: CONSTITUTIONAL

---

## 1. Core Philosophy

The Macro Context Layer exists to **explain the weather**, not to tell the pilot how to fly.

It provides a high-level, slow-moving narrative backdrop for the entire system. It helps the human observer understand *why* the automated strategies are behaving the way they are (e.g., "Momentum is suppressed because Monetary Policy is restrictive").

### The "Why" vs. "What" Distinction
- **Factor Layer**: Tells us *what* is happening (e.g., "Momentum is weak").
- **Macro Layer**: Tells us *why* it is happening (e.g., "Liquidity is contracting").
- **Strategy Layer**: Decides *what to do* about it (e.g., "Stand aside").

---

## 2. Hard Constraints (Non-Negotiable)

To ensure this layer remains helpful without introducing fragility or hidden risks, the following constraints are binding:

| Constraint | Description | Reasoning |
| :--- | :--- | :--- |
| **❌ NO GATING** | Macro states must NEVER directly block or allow a strategy. | Strategy logic should be self-contained. Macro is for context only. |
| **❌ NO EXECUTION** | Macro states must NEVER trigger trades or orders. | Macro signals are too slow and broad for execution timing. |
| **❌ NO FEEDBACK** | Macro states effectively "flow down" only. | Prevents complex feedback loops where strategies influence macro perception. |
| **❌ NO OPTIMIZATION** | Macro parameters are fixed/frozen. | Prevents overfitting to historical macro regimes. |

---

## 3. Signal Characteristics

All signals in the Macro Layer must adhere to these qualities:

1.  **Slow-Moving**: States should persist for weeks or months, not flip daily.
2.  **Interpretable**: Use human-readable labels (`TIGHTENING`, `NEUTRAL`, `EASING`), not raw numbers.
3.  **Widely Understood**: Concepts should be standard economic ontology (e.g., Yield Curve, Credit Spreads), not obscure proprietary metrics.
4.  **Explanatory**: The primary utility is to explain the *absence* of opportunity as much as the presence of it.

---

## 4. Integration Contract

- **Input**: Consumes raw market data (SPY, VIX, TNX) via standard ingestion.
- **Output**: A daily JSON snapshot (`macro_context.json`).
- **Dashboard**: Displayed as a "Weather Report" panel.
- **Evolution**: Attached to analysis windows for attribution.
