# Market Proxy Sets & Regime Definitions

## 1. Governance & Purpose
This document defines the canonical "Proxy Sets" used to evaluate Market Regimes, Capital Readiness, and Factor Conditions for the TraderFund strategies. 
**Strict adherence to these sets prevents "cherry-picking" of data.**

---

## 2. United States (US) Market Proxy Set
**Strategic Focus:** Tech dominance, Global liquidity (Dollar), and Consumer strength.

| Category | Ticker | Description | Semantic Role |
| :--- | :--- | :--- | :--- |
| **Equity** | **SPY** | S&P 500 ETF | **Benchmark**. The detailed truth of the broad market. |
| **Equity** | **QQQ** | Nasdaq 100 ETF | **Growth/Tech**. Leading indicator for risk-on appetite. |
| **Equity** | **IWM** | Russell 2000 ETF | **Small-Cap**. Breadth & domestic economic health. |
| **Equity** | **DIA** | Dow Jones ETF | **Blue Chip**. Industrial/Cyclical robustness. |
| **Volatility** | **VIX** | CBOE Volatility Index | **Fear Gauge**. Direct measure of option-implied volatility. |
| **Rates** | **US02Y** | 2-Year Treasury Yield | **Fed Policy**. Highly sensitive to rate hike/cut expectations. |
| **Rates** | **US10Y** | 10-Year Treasury Yield | **Valuation Anchor**. Mortgage rates & equity risk premium. |
| **Macro** | **DXY** | US Dollar Index | **Liquidity**. Global capital flows (Strong DXY = Tighter Conditions). |
| **Macro** | **USOIL** | WTI Crude Oil | **Inflation**. Key input for energy costs and CPI. |

---

## 3. India (IN) Market Proxy Set
**Strategic Focus:** Banking dominance, Oil dependence, and Foreign flows (FIIs).

| Category | Symbol | Description | Semantic Role |
| :--- | :--- | :--- | :--- |
| **Equity** | **NIFTY** | Nifty 50 Index | **Benchmark**. The detailed truth of the Indian market. |
| **Equity** | **BANKNIFTY** | Nifty Bank Index | **Financials**. Vital pulse (Banks = ~35% of Nifty). |
| **Equity** | **CNXIT** | Nifty IT Index | **Tech/Export**. Rupee sensitivity and global correlation. |
| **Equity** | **NIFTYSMLCAP100** | Nifty Smallcap 100 | **Sentiment**. Local retail risk appetite gauge. |
| **Volatility** | **INDIAVIX**| India VIX | **Fear Gauge**. Local option-implied volatility. |
| **Rates** | **IN10Y** | 10-Year Govt Bond | **Valuation**. Risk-free rate reference for India. |
| **Macro** | **USDINR** | US Dollar / Rupee | **FII Flows**. Currency stability (Weak Rupee = Foreign Outflows). |
| **Macro** | **UKOIL** | Brent Crude Oil | **Import Bill**. India imports ~85% of oil; High Oil = Macro Drag. |
| **Pre-Market**| **GIFTNIFTY**| GIFT Nifty Futures | **Gap Indicator**. Early signal for market open sentiment. |

---

## 4. Regime determination Logic (Draft)
*   **Bullish**: Benchmark > SMA200 + Breadth expanding + VIX falling.
*   **Bearish**: Benchmark < SMA200 + VIX elevated.
*   **Neutral/Choppy**: Mixed signals (e.g., Benchmark up, but Breadth weak).
