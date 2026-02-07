# Decision Policy Contract

## 1. Overview
The Decision Policy Layer acts as the governance gate between **Market Truth** (Epistemic) and **System Action** (Executive).
It does not decide *what* to buy, but *whether* the system is allowed to consider buying anything at all.

---

## 2. Market Scope & Independence
*   **Principle**: Decisions are market-specific. A `BULLISH` US market does not authorize action in `INDIA`.
*   **Evaluation**: The policy engine runs independently for each configured market (`US`, `INDIA`).

---

## 3. Allowed Action Space (Abstract)
The output of the policy is a set of **Permissions**, not commands.

| Action Permission | Description |
| :--- | :--- |
| `ALLOW_LONG_ENTRY` | Strategies may scan for and exert long entries. |
| `ALLOW_SHORT_ENTRY` | Strategies may scan for and exert short entries. |
| `ALLOW_POSITION_HOLD` | Existing positions may be maintained. |
| `FORCE_LIQUIDATION` | Existing positions must be closed (Emergency/Risk). |
| `ALLOW_REBALANCING` | Portfolio weights may be adjusted (no new net exposure). |
| `OBSERVE_ONLY` | No transactional actions allowed. Logging/Analysis only. |

---

## 4. Input State Requirements
The Policy Engine MUST consume the canonical Context objects:
1.  **Regime Context**: `State`, `Confidence`, `ProxyStatus`.
2.  **Factor Context**: `Liquidity`, `Breadth`, `Volatility`.
3.  **Fragility Context**: (Future) `ShockState`, `Correlation`.

---

## 5. Decision Logic (Constraint-First)

### 5.1. The "Golden Rule" of Degradation
**IF** `ProxyStatus == DEGRADED`:
*   **Output**: `OBSERVE_ONLY`.
*   **Reason**: "Epistemic Foundation Insufficient".
*   **Override**: None. (Phase 10 Policy).

### 5.2. Liquidity Constraints
**IF** `Liquidity.State == TIGHT` OR `Liquidity.State == CRISIS`:
*   **Block**: `ALLOW_LONG_ENTRY` (Margin/Lev cost risk).
*   **Block**: `ALLOW_SHORT_ENTRY` (Squeeze risk).
*   **Permit**: `ALLOW_POSITION_HOLD` (with tighter stops).

### 5.3. Regime Constraints
*   **BULLISH**: `ALLOW_LONG_ENTRY`.
*   **BEARISH**: `ALLOW_SHORT_ENTRY` (if verified) OR `OBSERVE_ONLY`.
*   **NEUTRAL**: `ALLOW_LONG_ENTRY` (Selective) OR `ALLOW_REBALANCING`.
*   **UNCERTAIN**: `OBSERVE_ONLY`.

### 5.4. Breadth Constraints
**IF** `Breadth.State == DIVERGENT` (e.g. Price Up, Breadth Down):
*   **Restrict**: `ALLOW_LONG_ENTRY` -> `HIGH_QUALITY_ONLY` (Implementation Detail for Strategy).
*   **Policy Output**: `ALLOW_LONG_ENTRY` (Conditional).

---

## 6. Output Contract
The Policy Engine emits a `decision_policy_{market}.json`:
```json
{
  "market": "US",
  "computed_at": "ISO8601",
  "action_state": "RESTRICTED",
  "permissions": ["ALLOW_POSITION_HOLD", "ALLOW_REBALANCING"],
  "blocked": ["ALLOW_LONG_ENTRY", "ALLOW_SHORT_ENTRY"],
  "reason": "Regime is BEARISH with NEUTRAL Liquidity. Defensive posture.",
  "epistemic_check": {
    "proxy_status": "CANONICAL",
    "regime_confidence": 0.8
  }
}
```
