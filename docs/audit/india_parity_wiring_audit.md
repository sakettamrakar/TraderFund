# India Parity Wiring Audit

## 1. Execution Summary
**Date**: 2026-01-30
**Event**: `INDIA_DATA_PARITY_WIRING`
**Status**: **PASSED (Honest Degradation)**

---

## 2. Loader Implementation
*   **File**: `src/ingestion/india_market_loader.py`
*   **Architecture**: Role-based proxy binding (not symbol-based).
*   **Deprecation**: `RELIANCE.NS` surrogate explicitly deprecated in code comments.

---

## 3. Parity Check Results

| Proxy Role | Status | Resolution Path |
| :--- | :--- | :--- |
| `equity_core` | **NOT_INGESTED** | Source NIFTY50 daily OHLCV |
| `sector_proxy` | **NOT_INGESTED** | Source BANKNIFTY daily OHLCV |
| `volatility_gauge` | **NOT_INGESTED** | Source India VIX |
| `rates_anchor` | **NOT_INGESTED** | Source IN10Y G-Sec yield from RBI |

**Overall Parity Status**: **DEGRADED** (4/4 gaps)

---

## 4. Factor Activation
All India factors are marked `NON-ACTIONABLE` because their source proxies are missing.
This is the correct behavior per `OBL-HONEST-STAGNATION`.

---

## 5. Policy Layer Impact
*   **Decision Policy (INDIA)**: Returns `OBSERVE_ONLY` (unchanged).
*   **Fragility Policy (INDIA)**: Returns `NOT_EVALUATED` (unchanged).

The wiring correctly enforces that India cannot escape its degraded state until all four canonical proxies are ingested and validated.

---

## 6. Conclusion
The India market is now governed by a **role-based canonical proxy contract**.
The RELIANCE surrogate is formally deprecated.
The system is in a state of **Honest Stagnation**, awaiting proper data ingestion.
