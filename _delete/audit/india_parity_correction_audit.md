# India Parity State Correction Audit

## 1. Correction Summary
**Date**: 2026-01-30
**Event**: `INDIA_PARITY_STATE_CORRECTION`
**Trigger**: Violation of `REAL_ONLY` invariant detected.

---

## 2. Violation Details
*   **Proxy Role**: `rates_anchor` (IN10Y)
*   **Issue**: Data was generated synthetically using random noise, not sourced from a real data provider.
*   **Invariant Violated**: `truth.data_mode: REAL_ONLY` requires all proxy data to be authentic market data.

---

## 3. Correction Applied

| Before | After |
| :--- | :--- |
| `parity_status: CANONICAL` | `parity_status: DEGRADED` |
| `canonical_ready: true` | `canonical_ready: false` |
| `IN10Y.status: ACTIVE` | `IN10Y.status: UNSATISFIED_REAL_DATA` |

---

## 4. Current State

| Proxy Role | Status | Provenance |
| :--- | :--- | :--- |
| `equity_core` (NIFTY50) | **ACTIVE** | REAL (Yahoo Finance) |
| `sector_proxy` (BANKNIFTY) | **ACTIVE** | REAL (Yahoo Finance) |
| `volatility_gauge` (INDIAVIX) | **ACTIVE** | REAL (Yahoo Finance) |
| `rates_anchor` (IN10Y) | **UNSATISFIED** | SYNTHETIC (Placeholder) |

---

## 5. Policy Impact
*   **Decision Policy (INDIA)**: Evaluation **BLOCKED**. Returns `OBSERVE_ONLY`.
*   **Fragility Policy (INDIA)**: Evaluation **BLOCKED**. Returns `NOT_EVALUATED`.

---

## 6. Resolution Path
To lift India from `DEGRADED`:
1.  Delete `data/india/IN10Y.csv` (synthetic).
2.  Source real IN10Y yield data from RBI, CCIL, or authorized financial data provider.
3.  Place the real data file at the expected path.
4.  Re-run `IndiaMarketLoader` to verify parity.

---

## 7. Epistemic Lesson
This correction demonstrates the system's commitment to **Honest Stagnation**.
We do not mask synthetic data as real. We do not claim readiness we do not possess.
The system is **stronger** for refusing to lie to itself.
