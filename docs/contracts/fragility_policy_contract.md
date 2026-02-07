# Fragility & Stress Policy Contract

## 1. Overview
The **Fragility Policy Layer** is a "Systemic Circuit Breaker".
It operates **downstream** of the Decision Policy. While the Decision Policy asks "Is the setup good?", the Fragility Policy asks "Is the environment safe?".
It possesses solely **subtractive power**: it can revoke permissions granted by the Decision Policy, but it can never grant new ones.

---

## 2. Signal Definitions (Conceptual)

### 2.1. Liquidity Stress
*   **Definition**: Rapid tightening of financial conditions.
*   **Signals**: Rate spikes (`^TNX` ROC), Credit Spread widening (implied), Volume evaporation.
*   **Risk**: Leverage decay, slippage, inability to exit.

### 2.2. Regime Transition (Whipsaw)
*   **Definition**: Recent flip in Regime State (e.g., Bull -> Bear within 5 days).
*   **Signals**: `regime_change_count`, `proximity_to_gate`.
*   **Risk**: False breakouts, trap moves.

### 2.3. Volatility Shock
*   **Definition**: Explusion of volatility from a low base.
*   **Signals**: `VIX` spike, `VVIX` (Vol of Vol) expansion.
*   **Risk**: Gap moves, stop runs.

### 2.4. Correlation Spike (Contagion)
*   **Definition**: Asset classes moving in lockstep (Beta -> 1.0).
*   **Signals**: `Corr(SPY, TLT)`, `Corr(Sector, Benchmark)`.
*   **Risk**: Loss of diversification benefit.

---

## 3. Stress State Classification

1.  **`NORMAL`**: Standard operating environment.
    *   *Action*: No constraints applied.
2.  **`EVALUATING`**: Insufficient data to determine stress (e.g. startup).
    *   *Action*: `BLOCK_NEW_ENTRY`.
3.  **`ELEVATED_STRESS`**: One or more signals showing warning signs.
    *   *Action*: `BLOCK_MARGIN_USE` (Implied), `RESTRICT_SIZE` (Implementation detail).
4.  **`SYSTEMIC_STRESS`**: Multiple signals firing or critical liquidity shock.
    *   *Action*: `BLOCK_ALL_ENTRIES`, `FORCE_DEFENSIVE_HOLD`.
5.  **`TRANSITION_UNCERTAIN`**: Recent regime flip.
    *   *Action*: `BLOCK_ALL_ENTRIES` (Wait for confirmation).

---

## 4. Permission Subtraction Rules
The Final Permission Set is calculated as:
`Final = DecisionPolicy.Permissions - FragilityPolicy.Revocations`

| Stress State | Revoked Permissions | Rationale |
| :--- | :--- | :--- |
| `NORMAL` | None | System healthy. |
| `ELEVATED` | `ALLOW_LEVERAGE` (Concept), `ALLOW_AGGRESSIVE_ENTRY` | De-risk margin. |
| `SYSTEMIC` | `ALLOW_LONG_ENTRY`, `ALLOW_SHORT_ENTRY`, `ALLOW_REBALANCING` | Capital preservation. Only `HOLD` or `LIQUIDATE` allowed. |
| `TRANSITION` | `ALLOW_LONG_ENTRY`, `ALLOW_SHORT_ENTRY` | Avoid chipsaw. |

---

## 5. Market Scope
*   **US**: Full Fragility Evaluation enabled.
*   **India**: Hard-coded `NOT_EVALUATED` (Reason: `DEGRADED_PROXY`).
    *   Because India is already handled by `DEGRADED_STATE` logic in Decision Policy, Fragility Layer is redundant but must remain consistent.

---

## 6. Output Artifact
`fragility_context_{market}.json`:
```json
{
  "market": "US",
  "computed_at": "ISO8601",
  "stress_state": "ELEVATED",
  "signals": {
    "liquidity_shock": false,
    "volatility_spike": true
  },
  "constraints": ["BLOCK_LEVERAGE"],
  "reason": "VIX spike detected (>30). Defensive posture."
}
```
