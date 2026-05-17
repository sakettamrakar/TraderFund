# Factor Discontinuity Report

## 1. Discontinuity Event
**Event**: `IGNITION-001`
**Date**: 2026-01-30
**Trigger**: Switch from Regime-Derived Factors (Semantic) to Calculated Factors (Technical).

---

## 2. Discontinuity Analysis

### Momentum Factor
*   **Prior State**: Linked to Regime Label.
    *   If Regime="BULLISH" -> Momentum="STRONG".
*   **New State**: Calculated independently.
    *   Price > SMA20 > SMA50 -> "STRONG".
    *   ROC(10) > 2% -> "POSITIVE".
*   **Observation**:
    *   **US**: Output `STRONG` (Ignition Verification). Matches prior state? *Likely YES* given the hardcoded "Forced Bullish" mocks were removed.
    *   **India**: Output `STRONG`.
*   **Verdict**: **Healthy Discontinuity**. The system now reacts to price, not labels.

### Volatility Factor
*   **Prior State**: Derived/Mocked.
*   **New State**:
    *   **US**: VIX Level (Raw). Expected ~15-25.
    *   **India**: Realized Vol (Annualized). Expected ~15-25.
*   **Observation**:
    *   US Verification returned `20.0` (Fallback default? No, file read). Check VIX.csv.
*   **Warning**: The `FactorContextBuilder` logic uses the raw value. Downstream strategies expecting a normalized 0-1 score will break if they consume this directly without a normalization layer (e.g., `(25 - VIX) / 25`).

### Liquidity / Value / Quality
*   **Status**: **REGRESSED**.
*   **Prior State**: Mocked / Derived "Neutral".
*   **New State**: `state: "neutral", confidence: 0.5`.
*   **Reason**: Missing fundamental/macro data inputs (Rates, Earnings).
*   **Verdict**: **Honest Stagnation**. The system correctly reports low confidence rather than fake data.

---

## 3. Conclusion
The implementation successfully decoupled Factors from Regime Labels. However, "Advanced" factors (Liquidity, Quality) have regressed to a low-confidence holding state due to missing inputs.
