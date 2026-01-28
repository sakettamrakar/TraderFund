# Macro Signal Catalog

**Version**: 1.0  
**Date**: 2026-01-29  
**Status**: FROZEN

This catalog defines the **complete and exhaustive** set of macro dimensions tracked by the system.

---

## A. Monetary & Rates
*The price and availability of money.*

| Signal | Source Proxy | States | Definition |
| :--- | :--- | :--- | :--- |
| **Policy Stance** | 2Y Yield vs Fed Funds (Proxy) | `TIGHTENING` / `NEUTRAL` / `EASING` | Direction of short-term rate expectations. |
| **Rate Level** | 10Y Yield (`^TNX`) | `HIGH` / `MID` / `LOW` | Absolute cost of long-term capital (Regime relative). |
| **Curve Shape** | 10Y - 2Y Spread | `INVERTED` / `FLAT` / `NORMAL` / `STEEP` | Yield curve slope indicating cycle stage. |
| **Real Rates** | TIPS Yield (or Nom - Breakeven) | `POSITIVE` / `NEUTRAL` / `NEGATIVE` | Cost of capital adjusted for inflation. |

---

## B. Liquidity & Credit
*The flow of capital and health of intermediaries.*

| Signal | Source Proxy | States | Definition |
| :--- | :--- | :--- | :--- |
| **Liquidity Impulse** | Fed Balance Sheet (Proxy) | `EXPANDING` / `STABLE` / `CONTRACTING` | Rate of change in central bank liquidity support. |
| **Credit Spreads** | HYG vs IEF | `TIGHT` / `NORMAL` / `WIDE` | Risk premium demanded for corporate credit. |
| **Funding Stress** | FRA-OIS (or Proxy) | `LOW` / `ELEVATED` / `CRISIS` | Interbank lending stress. |

---

## C. Growth & Inflation
*The economic engine.*

| Signal | Source Proxy | States | Definition |
| :--- | :--- | :--- | :--- |
| **Growth Trend** | Copper/Gold, Cyclicals/Defensives | `ACCELERATING` / `STABLE` / `DECELERATING` | Market-implied growth expectations. |
| **Inflation Regime** | Breakeven Rates, Commodities | `DEFLATION` / `DISINFLATION` / `STABLE` / `INFLATION` | Price level trajectory. |
| **Policy-Growth** | Rate vs Growth Proxy | `SUPPORTIVE` / `NEUTRAL` / `RESTRICTIVE` | Is policy tailwind or headwind to growth? |

---

## D. Risk Sentiment
*The market's willingness to take risk.*

| Signal | Source Proxy | States | Definition |
| :--- | :--- | :--- | :--- |
| **Risk Appetite** | SPY vs Low Vol | `RISK-ON` / `MIXED` / `RISK-OFF` | Preference for aggressive vs defensive assets. |
| **Volatility Regime** | VIX Level | `SUPPRESSED` / `NORMAL` / `ELEVATED` / `EXTREME` | Cost of optionality / fear gauge. |
| **Correlation** | Avg Pairwise Correlation | `LOW` / `NORMAL` / `HIGH` | Diversification potential. |

---

## E. State Determination Logic (Simplified)

For the **Macro Context Builder**, we use simplified, robust proxies for these complex concepts to maintain structural integrity without needing external macro data feeds.

**Example Logic:**
- **Curve Shape**: `10Y - 2Y < 0` → `INVERTED`.
- **Volatility**: `VIX < 15` → `SUPPRESSED`, `15-25` → `NORMAL`, `>25` → `ELEVATED`.
- **Trend**: `Smooth(Price) > Smooth(Price, lag)` → `ACCELERATING`.

*Note: All logic is structurally frozen and read-only.*
