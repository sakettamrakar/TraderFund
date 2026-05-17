# Data Source Governance & Mapping

## 1. Purpose
This document maps the abstract **Market Proxy Sets** (defined in `market_proxy_sets.md`) to specific, authorized **Data Sources** (files/APIs) within the system.

**Policy:**
*   Where a direct source exists, it MUST be used.
*   Where a source is missing, it is recorded in the `coverage_gap_register.md`.
*   **Surrogate Policy**: For the India market, until Index data is available, `NSE_RELIANCE` and `NSE_HDFCBANK` are authorized as *temporary structural proxies* for Nifty and BankNifty respectively, but MUST be labeled as "SURROGATE" in the UI.

---

## 2. United States (US) Source Mapping
*Root Path:* `data/regime/raw/`

| Ticker | Required Source File | Status | Authorized Fallback / Notes |
| :--- | :--- | :--- | :--- |
| **SPY** | `SPY.csv` | **AVAILABLE** | Primary Regime Source. |
| **QQQ** | `QQQ.csv` | **AVAILABLE** | Tech Factor Source. |
| **IWM** | `IWM.csv` | **MISSING** | Gap registered. |
| **DIA** | `DIA.csv` | **MISSING** | Gap registered. |
| **VIX** | `VIX.csv` | **AVAILABLE** | |
| **US02Y**| `^TNX.csv` (Approx?) | **PARTIAL** | `^TNX` is 10Y. Need 2Y source. |
| **US10Y**| `^TNX.csv` | **AVAILABLE** | Yahoo Finance symbol for 10Y Yield. |
| **DXY** | `DX-Y.NYB.csv` | **MISSING** | Gap registered. |
| **USOIL**| `CL=F.csv` | **MISSING** | Gap registered. |

*(Note: `HYG.csv` and `LQD.csv` exist in `data/regime/raw` but are not in the primary proxy definition list. They serve as Credit Factor inputs.)*

---

## 3. India (IN) Source Mapping
*Root Path:* `data/raw/api_based/angel/historical/`

| Symbol | Required Source File | Status | Authorized Surrogate |
| :--- | :--- | :--- | :--- |
| **NIFTY** | `NSE_NIFTY_1d.jsonl` | **MISSING** | **NSE_RELIANCE_1d.jsonl** (Heavyweight Proxy) |
| **BANKNIFTY**| `NSE_BANKNIFTY_1d.jsonl` | **MISSING** | **NSE_HDFCBANK_1d.jsonl** (Sector Proxy) |
| **CNXIT** | `NSE_CNXIT_1d.jsonl` | **MISSING** | **NSE_INFY_1d.jsonl** (Sector Proxy) |
| **NIFTYSML** | `NSE_NIFTYSML_1d.jsonl`| **MISSING** | None. |
| **INDIAVIX** | `NSE_INDIAVIX_1d.jsonl`| **MISSING** | None. |
| **IN10Y** | `IN10Y.csv` | **MISSING** | None. |
| **USDINR** | `USDINR.csv` | **MISSING** | None. |
| **UKOIL** | `BRENT.csv` | **MISSING** | None. |

**Governance Note**: The "MISSING" status for India indices is a critical gap. The system currently pretends `RELIANCE` is the Market for regime purposes. This is an accepted risk for Phase 10 but must be remediated in Phase 12 (Data Expansion).
