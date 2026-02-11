# Fragility & Stress Policy Layer Design

## 1. Overview
The Fragility & Stress Policy is a secondary governance layer that operates as a **filter** on the Decision Policy. Its purpose is to detect systemic conditions where standard decision logic (e.g., "Market is Bullish, so Buy") becomes dangerous due to structural instability.

## 2. Policy Invariants
- **SUBTRACTIVE ONLY**: The Fragility layer can only remove permissions; it can never grant new ones.
- **DETERMINISTIC**: Evaluation must be based on observable systemic signals.
- **MARKET-SPECIFIC**: Stress in one market does not automatically imply stress in another (though correlations are tracked).

## 3. Fragility Signals
| Signal | Source Indicators | Description |
| :--- | :--- | :--- |
| **Liquidity Stress** | Repo rates, Fed Funding, TED Spread | Funding tightness that forces deleveraging. |
| **Regime Transition** | Trend-line breaks, Moving Average crossovers | Periods of high whipsaw risk during trend change. |
| **Correlation Spike** | Multi-asset correlation matrix | Diversification collapse where all assets move together. |
| **Volatility Shock** | VIX Expansion, ATR expansion | Sudden increase in price variance or gap risk. |

## 4. Stress State Classification
| State | Description | Primary Constraint |
| :--- | :--- | :--- |
| **NORMAL** | Signal noise within bounds. | No impact on Decision Policy. |
| **ELEVATED_STRESS** | Signals show moderate divergence from norm. | Block high-convexity/high-risk entries (e.g., Shorts, Special Longs). |
| **SYSTEMIC_STRESS** | Major signal failure or outlier event. | Block ALL entries. Force defensive posture. |
| **TRANSITION_UNCERTAIN** | Market is mid-regime change. | Block all entries. Allow Rebalancing/Holding only. |

## 5. Permission Subtraction Rules
The layer computes a `blocked_by_fragility` list. 
`Final Permissions = Decision Permissions EXCEPT IF IN blocked_by_fragility`.

| Stress State | Blocked Intents |
| :--- | :--- |
| **NORMAL** | `[]` |
| **ELEVATED_STRESS** | `["ALLOW_SHORT_ENTRY", "ALLOW_LONG_ENTRY_SPECIAL"]` |
| **SYSTEMIC_STRESS** | `["ALLOW_LONG_ENTRY", "ALLOW_SHORT_ENTRY", "ALLOW_REBALANCING", "ALLOW_LONG_ENTRY_SPECIAL"]` |
| **TRANSITION_UNCERTAIN** | `["ALLOW_LONG_ENTRY", "ALLOW_SHORT_ENTRY", "ALLOW_LONG_ENTRY_SPECIAL"]` |

## 6. Market Scope (Governance)
### US Market
- Full evaluation using canonical proxy sets (Equities, Bonds, Credit).
- Epistemic Grade: `CANONICAL`.

### INDIA Market
- **Hard Restriction**: Due to `DEGRADED_PROXY_STATE`, fragility cannot be reliably evaluated.
- **Default State**: `NOT_EVALUATED`.
- **Constraint**: Permissions are ALWAYS restricted to `OBSERVE_ONLY`.

## 7. Artifact Schema (`fragility_policy_{market}.json`)
```json
{
  "fragility_policy": {
    "market": "US",
    "stress_state": "NORMAL",
    "signals": {
      "liquidity": "STABLE",
      "volatility": "MODERATE",
      "correlation": "LOW"
    },
    "blocked_intents": [],
    "reason": "Systemic signals within normal ranges.",
    "evaluation_timestamp": "2026-01-30T...",
    "epoch_id": "TE-2026-01-30"
  }
}
```
