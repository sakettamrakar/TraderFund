# Risk Envelopes

This document defines the **read-only** constraints that bound the system's theoretical risk taking.

## 1. Strategy-Level Constraints

*   **Max Exposure Per Strategy**: 5% of Total Paper Capital.
*   **Leverage**: **Strictly 1.0x** (No leverage permitted).
*   **Concentration**: No single instrument > 20% of a strategy's allocation.

## 2. Regime-Level Constraints

*   **Bear / Crash Regimes**:
    *   Momentum Ceiling -> Reduced to 10%.
    *   Carry -> **FORBIDDEN**.
    *   Volatility -> Ceiling increased to 40% (if structurally eligible).
*   **High Volatility (Expansion)**:
    *   Mean Reversion -> **FORBIDDEN**.

## 3. Portfolio-Level Constraints

*   **Gross Exposure Cap**: 100% (No Leverage).
*   **Net Exposure Floor**: 0% (No Net Shorting of the aggregated portfolio).
*   **Family Overlap**: Max 2 families active in the same instrument directionally.
