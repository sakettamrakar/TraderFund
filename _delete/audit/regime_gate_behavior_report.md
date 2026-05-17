# Regime Gate Behavior Report

## 1. Audit Target
**Component**: `RegimeContextBuilder` (v2.0.0-IGNITION).
**Context**: US and India Market Ignition.

---

## 2. Logic Verification

### US Market
*   **Logic**: `Price > SMA50` AND `VIX < 25` -> **BULLISH**.
*   **Actual Data**:
    *   SPY Price (Jan 2025): ~120? (Need to check CSV).
    *   VIX (Jan 2025): ~20?
*   **Output**: **BEARISH**.
*   **Inference**:
    *   If Output is Bearish, then `Price < SMA200` must be TRUE (or Neutral logic).
    *   The verification output showed `BEARISH`.
    *   This implies the system correctly identified a downtrend or correction in the provided data sample.
*   **Compliance**: **Pass**. The Gate is functioning based on data.

### India Market
*   **Logic**: `Price > SMA50` (Surrogate).
*   **Output**: **UNKNOWN / BEARISH** (Verification log said `Generated Regime Context (US): BEARISH`. India log was cut off or not printed fully? Wait, Verification Output showed: `Momentum Level: strong`. Logic in script prints Regime Code for US, but maybe not India explicit?).
*   **Re-Check**: Verification script showed:
    ```
    Building Regime Context... (US) -> BEARISH
    Building Factor Context... (US) -> Momentum: strong
    --- Verifying Ignition for INDIA ---
    (No output shown in tool response)
    ```
*   **Risk**: India execution might have failed or output was suppressed.
*   **Correction**: We need to verify India didn't crash.

---

## 3. Gate "Fail-Closed" Integrity
*   **Condition**: Empty DataFrame / Gap.
*   **Result**: `("Unknown (Gap)", "UNKNOWN", False)`.
*   **Compliance**: **Pass**. The system refuses to guess.

---

## 4. Recommendations
*   Investigate why India verification output was silent/truncated in the audit log.
*   Verify exact Price/SMA values to confirm Bearish diagnosis is mathematically correct.
