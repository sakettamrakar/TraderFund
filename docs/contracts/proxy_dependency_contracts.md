# Proxy Dependency Contracts

## 1. Overview
This document enforces **Dependency Binding**: every reasoning layer in the TraderFund system must explicitly declare which Proxy Roles it consumes.
**Rule**: No layer may access raw data (e.g., `SPY.csv`) directly. It must request a Role (e.g., `get_proxy(market, 'benchmark_equity')`).

---

## 2. Regime Layer Contract
**Responsibilities**: Determine Market State (Bullish/Bearish/Neutral).

| Input Role | US Binding | INDIA Binding | Criticality |
| :--- | :--- | :--- | :--- |
| **Benchmark Equity** | `composite(SPY, QQQ)` | `surrogate(RELIANCE)` | **BLOCKING** |
| **Volatility Gauge** | `VIX` | `realized_vol(RELIANCE)` | **BLOCKING** |
| **Rates Anchor** | `US10Y` | `IN10Y` (Missing) | Warning |
| **Logic** | Multi-Factor Gate | Single-Factor Gate | |

**Constraint**: If `Benchmark Equity` or `Volatility Gauge` is missing, Regime State = **UNKNOWN** (Fail Closed).

---

## 3. Factor Engine Contract
**Responsibilities**: Calculate Momentum, Value, Volatility, Liquidity factors.

| Factor | Required Proxy Role | Fallback Policy |
| :--- | :--- | :--- |
| **Momentum** | `Benchmark Equity` + `Growth Proxy` | Use Benchmark Only if Growth missing. |
| **Volatility** | `Volatility Gauge` | Computed StdDev if Gauge missing. |
| **Liquidity** | `Rates Anchor` + `Liquidity Proxy` | `UNAVAILABLE` if missing. |
| **Breadth** | `Benchmark` vs `Sector Proxies` | `UNAVAILABLE` if missing. |

---

## 4. Macro Layer Contract
**Responsibilities**: Contextualize market moves (inflation, global flows).

| Signal | Required Proxy Role |
| :--- | :--- |
| **Risk Appetite** | `Rates Anchor` (Yield Curve) |
| **Global Flows** | `Currency Proxy` (DXY / USDINR) |
| **Inflation** | `Commodity Proxy` (Oil) |

---

## 5. UI / Dashboard Contract
**Responsibilities**: Display provenance and honesty.

*   **OBL-DATA-PROVENANCE-VISIBLE**: The UI must display the *exact* tickers used in the `Benchmark Equity` role for the selected market.
*   **OBL-HONEST-STAGNATION**: If a proxy is stale, the corresponding UI component must grey out.

---

## 6. Audit & Verification
*   **Check**: Does `regime.py` import `SPY` hardcoded? -> **VIOLATION**.
*   **Check**: Does `regime.py` access `ProxySet.get('benchmark_equity')`? -> **COMPLIANT**.
