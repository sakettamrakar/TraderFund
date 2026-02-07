# India Parity Gap Register

## 1. Purpose
This register tracks the data gaps preventing India from achieving CANONICAL proxy status.

---

## 2. Gap Inventory

| Gap ID | Proxy Role | Required Ticker | Current Status | Blocking Factor | Resolution Path |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `IND-GAP-001` | Benchmark Equity | `NIFTY50` / `^NSEI` | **NOT_INGESTED** | Momentum, Regime | Source NIFTY50 daily OHLCV from Yahoo Finance or NSE. |
| `IND-GAP-002` | Sector Proxy | `BANKNIFTY` / `^NSEBANK` | **NOT_INGESTED** | Breadth (Sector Rotation) | Source BANKNIFTY daily OHLCV. |
| `IND-GAP-003` | Volatility Gauge | `INDIAVIX` / `^INDIAVIX` | **NOT_INGESTED** | Volatility, Fragility | Source India VIX from NSE. |
| `IND-GAP-004` | Rates Anchor | `IN10Y` | **NOT_INGESTED** | Liquidity | Source 10Y G-Sec yield from RBI or CCIL. May require manual CSV. |

---

## 3. Factor Coverage Matrix (Post-Parity)

| Factor | Source Proxy | Current State | Post-Parity State |
| :--- | :--- | :--- | :--- |
| **Momentum** | NIFTY50 | `UNKNOWN` (Surrogate) | `CALCULATED` |
| **Volatility** | INDIAVIX | `UNKNOWN` | `CALCULATED` |
| **Liquidity** | IN10Y | `UNKNOWN` | `CALCULATED` |
| **Breadth** | BANKNIFTY vs NIFTY50 | `UNKNOWN` | `CALCULATED` |

---

## 4. Honest Stagnation Declaration
Until all gaps (`IND-GAP-001` through `IND-GAP-004`) are resolved:
*   India remains in **`DEGRADED_PROXY_STATE`**.
*   Decision Policy output is locked to **`OBSERVE_ONLY`**.
*   Fragility Policy returns **`NOT_EVALUATED`**.

This is the correct, governed behavior. There is no shortcut.
