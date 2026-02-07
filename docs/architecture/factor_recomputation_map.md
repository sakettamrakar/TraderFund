# Factor Re-computation Map

## 1. Impact Analysis
Switching inputs from single-instrument to multi-proxy baskets significantly alters the semantic meaning of "Momentum", "Value", and "Volatility". This document maps the transformation rules.

---

## 2. Factor: MOMENTUM
**Definition**: The persistence and strength of the market trend.

| Market | Old Formula | New Formula | Rationale |
| :--- | :--- | :--- | :--- |
| **US** | `SMA_Cross(SPY)` | `Weighted_Score(SPY_Score * 0.7 + QQQ_Score * 0.3)` | Tech (QQQ) leads turns. SPY alone lags. Blending gives earlier signal. |
| **INDIA**| `SMA_Cross(RELIANCE)` | `SMA_Cross(RELIANCE)` | **No Change** (Surrogate constraint). Note: Bias towards Energy sector. |

**Discontinuity Risk**: Medium. Adding QQQ may flip "Neutral" to "Bullish" faster.

---

## 3. Factor: VOLATILITY
**Definition**: The cost of protection / fear level.

| Market | Old Formula | New Formula | Rationale |
| :--- | :--- | :--- | :--- |
| **US** | `StdDev(SPY)` | `Level(VIX)` | Implied Volatility (VIX) is a forward-looking fear gauge. Realized Vol (StdDev) is backward-looking. |
| **INDIA**| `StdDev(RELIANCE)` | `StdDev(RELIANCE)` | **No Change** (Missing INDIAVIX). |

**Discontinuity Risk**: **HIGH**. VIX levels (12-30+) are numerically different from Daily Returns StdDev (0.01-0.03). Normalization required (e.g., VIX/100/sqrt(252)).

---

## 4. Factor: BREADTH (New)
**Definition**: Participation rate (Are all stocks moving?).

| Market | Old Formula | New Formula | Rationale |
| :--- | :--- | :--- | :--- |
| **US** | N/A | `Correlation(SPY, QQQ)` | Proxy for breadth. correlation -> 1.0 means unified move. Divergence warns of top. |
| **INDIA**| N/A | N/A | Cannot compute breadth from single surrogate. |

---

## 5. Factor: LIQUIDITY / MACRO
**Definition**: Availability of capital.

| Market | Old Formula | New Formula | Rationale |
| :--- | :--- | :--- | :--- |
| **US** | N/A | `inv(US10Y)` | Higher yields = Tighter liquidity. Simple inverse relationship for now. |
| **INDIA**| N/A | N/A | Missing Bond/Currency data. |

---

## 6. Migration Strategy
1.  **Parallel Calculation**: Compute `Momentum_v1` (Old) and `Momentum_v2` (New) side-by-side for 1 epoch.
2.  **Normalization Check**: Ensure `Momentum_v2` output range is roughly [-1.0, 1.0] like `Momentum_v1`.
3.  **Cutover**: Update `factor_context_builder.py` to use v2 logic only after validation.
