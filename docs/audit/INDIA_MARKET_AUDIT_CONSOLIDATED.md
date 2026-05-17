# India Market Audit — Consolidated

> Consolidated from 7 individual India audit files. Originals moved to `_delete/audit/`.
> Timeline: Jan 30, 2026 (initial wiring) → Feb 9, 2026 (delta ingestion remediation)

---

## 1. Initial Parity Wiring (Jan 30)

**Event**: `INDIA_DATA_PARITY_WIRING` | **Status**: PASSED (Honest Degradation)

- Loader: `src/ingestion/india_market_loader.py` — role-based proxy binding
- `RELIANCE.NS` surrogate explicitly deprecated

| Proxy Role | Status | Resolution Path |
| :--- | :--- | :--- |
| `equity_core` | NOT_INGESTED | Source NIFTY50 daily OHLCV |
| `sector_proxy` | NOT_INGESTED | Source BANKNIFTY daily OHLCV |
| `volatility_gauge` | NOT_INGESTED | Source India VIX |
| `rates_anchor` | NOT_INGESTED | Source IN10Y G-Sec yield from RBI |

**Parity**: DEGRADED (4/4 gaps). All factors `NON-ACTIONABLE`. Policy: `OBSERVE_ONLY`.

---

## 2. Data Ingestion — Multi-Proxy Acquisition (Jan 30)

**Event**: `INDIA_DATA_INGESTION` | **Status**: SUCCESS — PARITY ACHIEVED

| Proxy Role | Ticker | Source | Rows | Status |
| :--- | :--- | :--- | :--- | :--- |
| `equity_core` | NIFTY50 (`^NSEI`) | Yahoo Finance | 496 | ACTIVE |
| `sector_proxy` | BANKNIFTY (`^NSEBANK`) | Yahoo Finance | 492 | ACTIVE |
| `volatility_gauge` | INDIAVIX (`^INDIAVIX`) | Yahoo Finance | 492 | ACTIVE |
| `rates_anchor` | IN10Y | Synthetic (Placeholder) | 200 | ACTIVE (SYNTHETIC) |

Parity: DEGRADED → CANONICAL (0 gaps). **Warning**: IN10Y was synthetic placeholder data.

---

## 3. Parity Correction — REAL_ONLY Invariant Violation (Jan 30)

**Event**: `INDIA_PARITY_STATE_CORRECTION` | **Trigger**: `truth.data_mode: REAL_ONLY` violated

- `rates_anchor` (IN10Y) was synthetic random noise, not real market data
- Correction: `CANONICAL` → `DEGRADED`, `canonical_ready: true` → `false`
- IN10Y status: `ACTIVE` → `UNSATISFIED_REAL_DATA`
- Policy impact: Decision & Fragility evaluation BLOCKED

**Epistemic lesson**: The system does not mask synthetic data as real. Honest stagnation enforced.

---

## 4. IN10Y Real Data Ingestion via FRED (Jan 30)

**Event**: `INDIA_IN10Y_FRED_INGESTION` | **Status**: SUCCESS — PARITY WITH REAL DATA

| Field | Value |
| :--- | :--- |
| Source | FRED (Federal Reserve Bank of St. Louis) |
| Series ID | `INDIRLTLT01STM` |
| Original Source | IMF |
| Frequency | Monthly |
| Observations | 72 (2020-01 to 2025-12) |
| Latest Yield | 6.63% |
| Provenance | **REAL** |

- API key from `FRED_API_KEY` env var, never logged (`OBL-SECRET-NON-DISCLOSURE`)
- Synthetic placeholder deleted, replaced with authentic IMF-sourced data
- History threshold adjusted to 60 observations (5 years monthly) for liquidity regime analysis

**Final parity**: All 4 proxies REAL. True Canonical Status achieved.

---

## 5. Policy & Fragility Evaluation (Jan 30)

**Event**: `INDIA_POLICY_FRAGILITY_EVALUATION` | **Status**: SUCCESS — FULL EVALUATION

### Factor Context
| Factor | State | Value | Assessment |
| :--- | :--- | :--- | :--- |
| Momentum | `neutral` | -- | Range-bound market |
| Volatility | `normal` | VIX = 13.37 | Low fear |
| Liquidity | `loose` | Yield = 6.63% | Easy conditions |
| Breadth | `bank_lead` | Banks +1.3% vs NIFTY -2.7% | Financials outperforming |

**Regime**: NEUTRAL (Range-Bound / Mixed)

### Decision Policy
- State: `ACTIVE` | Permissions: `ALLOW_POSITION_HOLD`, `ALLOW_REBALANCING`
- Epistemic Health: `CANONICAL`

### Fragility Policy
- Stress State: `NORMAL` | Constraints: None
- Permission integrity: PASSED (no permissions added by Fragility layer)

### Market Isolation: PASSED — only India data used, no US cross-pollination

**Transition**: DEGRADED/OBSERVE_ONLY → CANONICAL/ACTIVE

---

## 6. Delta Ingestion Refactor (Feb 8)

**Audit ID**: AUD-CODE-2026-02-08-01

Refactored `scripts/india_data_acquisition.py` from Full Overwrite to Delta-Merge:
1. **Load existing history** — abort if load fails (failsafe)
2. **Incremental fetch** — from last recorded date only
3. **Merge & deduplicate** — by `Date`, keeping latest observation
4. **Explicit logging** — pre-fetch count, fetch date, rows fetched, post-merge count, delta

**Justification**: Aligns with US `ingest_daily.py` logic. Preserves historical stability, efficiency, and audit trail.

**Risks mitigated**: Gap risk (unlikely >2yr gap), schema drift (column normalization), duplicate handling (keep `last`).

---

## 7. Delta Ingestion Remediation Verification (Feb 9)

**Date**: 2026-02-09 | **Status**: SUCCESS

| Ticker | Canonical Rows | Fetched | Post-Merge | Delta | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| NIFTY50 | 496 | 2 | 497 | +1 | SUCCESS |
| BANKNIFTY | 492 | 2 | 493 | +1 | SUCCESS |
| INDIAVIX | 492 | 2 | 493 | +1 | SUCCESS |

**Compliance**:
- [x] `INV-HISTORICAL-CONTINUITY`: No historical rows dropped
- [x] `OBL-DELTA-AUDITABILITY`: Logs show Before/Fetched/After/Overlap
- [x] Safety abort if canonical file cannot be read

**Artifacts**: `scripts/india_data_acquisition.py`, `logs/india_delta_ingestion.log`
