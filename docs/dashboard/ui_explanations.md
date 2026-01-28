# Dashboard UI Explanations (Semantic Copy)

This document serves as the master copy for all semantic explanations used in the refactored Market Intelligence Dashboard.

## 1. Strategy Eligibility Indicators

| State | Semantic Meaning (Layman) | Why it matters |
| :--- | :--- | :--- |
| ✅ Eligible | **Safety Gates Open**: The system is authorized to trade if an opportunity appears. | All risk and regime prerequisites are met. |
| ❌ Blocked | **Gated for Safety**: The environment is either too volatile or lacks the required structure. | Trading now would violate safety protocols. |
| ⚠️ Low Confidence | **Weak Environment**: The logic is allowed to run, but the market signals are faint or inconsistent. | Results are less predictable in this regime. |

## 2. Factor Breakdown (Layman Definitions)

### Momentum Factors
*   **Expansion (Volatility/Breadth)**: Is the market "opening up" or "contracting"?
    *   *Why it matters*: Momentum needs room to move; contraction traps capital.
*   **Acceleration**: Is the trend getting faster or slowing down?
    *   *Why it matters*: We only want to join trends that are gaining power, not fading.
*   **Breadth**: Is everyone joining in, or just a few big stocks?
    *   *Why it matters*: Healthy trends are supported by the majority of the market.
*   **Persistence**: Does the signal last, or is it "flickering"?
    *   *Why it matters*: We avoid "one-hit wonders" to reduce trading costs and false starts.

### Value Factors
*   **Dispersion**: Are stock prices spread out from their usual values?
    *   *Why it matters*: Value investing needs "mispricing" to exist. High dispersion = many opportunities.
*   **Liquidity Pressure**: Is the market panicked or orderly?
    *   *Why it matters*: Buying in a "crash" requires defensive positioning to survive.

## 3. "What Would Change My Mind?" (Causal reasoning)

*   **Momentum**: "We are waiting for the market to wake up. When volatility expands and more stocks join the move, our safety gates will open."
*   **Value**: "We are looking for extreme price differences. If the market becomes more chaotic but liquid, we find more opportunities to buy at a discount."
