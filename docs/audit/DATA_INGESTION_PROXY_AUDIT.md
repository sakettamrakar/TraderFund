# Data Ingestion & Proxy Audit — Consolidated

> Consolidated from 6 ingestion/proxy audit files. Originals moved to `_delete/audit/`.
> Timeline: Jan 30, 2026 (ignition & expansion) → Feb 8, 2026 (delta load audit)

---

## 1. Load Semantics

| Component | Load Pattern | Detail |
| :--- | :--- | :--- |
| US Ingestor (`ingest_daily.py`) | **Delta Merge** | Loads existing CSV, appends 100-bar `compact` API response, deduplicates by `timestamp` |
| India Ingestor (`india_data_acquisition.py`) | **Full Overwrite** (pre-remediation) | Downloads 2-year history from Yahoo Finance, overwrites target files |
| EV-TICK Raw (`ev_tick.py`) | **Snapshot Delta** | Saves raw JSON into new daily directories `data/raw/us/YYYY-MM-DD` |

**Evidence**: US `SPY_daily.csv` = 116 rows (delta accumulation of ~115 trading days); India NIFTY50 = full 2yr history (overwrite pattern).

**Risks**:
- US gap risk: 100-bar compact limit → silent gap if inactive >100 trading days
- India post-hoc adjustment: Yahoo corporate action adjustments silently update old records, degrading auditability
- Schema fragility: no explicit validation before merge in either pipeline

---

## 2. System Ignition — Proxy Wiring (Jan 30)

**US Market**:
- Primary: SPY (S&P 500 ETF) — ACTIVE, CSV headers normalized
- Secondary: QQQ — queued for next iteration
- Volatility: VIX — ACTIVE
- Data: `MarketLoader` ingests and normalizes

**India Market**:
- Surrogate: `NSE_RELIANCE` — DEGRADED (acknowledged), JSONL parsing active

**Factor Recomputation**: `FactorContextBuilder` v2.0.0-IGNITION
- Decoupled from regime labels (direct price calculation)
- Momentum: SMA20/SMA50 crossover | Volatility: VIX (US) / Realized Vol (India)

---

## 3. Proxy Compliance — Contract vs Implementation

### Mismatch Findings

| Component | Claimed Input | Actual Input | Verdict |
| :--- | :--- | :--- | :--- |
| US `regime.py` | SPY + QQQ + IWM + VIX | SPY only | MISMATCH |
| US Factor Engine | Multi-Factor | Single-File | MISMATCH |
| India Dashboard | "Nifty 50" | RELIANCE | MISMATCH (UI lies about source) |
| India `regime.py` | RELIANCE | RELIANCE.jsonl | ALIGNED (degraded) |

### Integrity Findings
- **[P-INT-001]** US Benchmark: contract requires SPY(60%)+QQQ(30%) weighted composite; implementation loads SPY only (MEDIUM severity)
- **[P-INT-002]** Rates Anchor: contract requires `^TNX`; no `load_rates` method exists (HIGH severity)
- **[P-INT-003]** India Surrogate: correctly bound to `NSE_RELIANCE` (COMPLIANT)

### Dependency Compliance Matrix

| Layer | Requirement | Actual | Compliance |
| :--- | :--- | :--- | :--- |
| Regime | Benchmark + Vol Gauge | SPY + VIX (US), RELIANCE + CalcVol (IN) | PASS |
| Factor (Momentum) | Bench + Growth | SPY only | PARTIAL |
| Factor (Liquidity) | Rates | None | FAIL |
| Factor (Breadth) | Sector | None | FAIL |
| Dashboard | Provenance visible | `inputs_used` populated | PASS |

---

## 4. US Data Expansion & Recompute (Jan 30)

### Ingestion
- `^TNX` (rates anchor): ACTIVE — synthetic Base-100 index (~99.41), thresholds calibrated (102=Tight, 98=Loose)
- `QQQ` (growth proxy): ACTIVE — used for relative strength vs SPY

### Factor Re-computation Results
| Factor | New State | Change from Pre-Expansion |
| :--- | :--- | :--- |
| Liquidity | NEUTRAL (rates ~99.41) | Was UNKNOWN/TIGHT |
| Breadth | TECH_LEAD (QQQ > SPY +2%) | Was UNKNOWN |
| Value.Liquidity | NEUTRAL | Was UNKNOWN |

**Blindness removed**: System now sees rates and sector rotation.

---

## 5. Governance Assessment

- **Factor Continuity**: High for US (persistent delta history), Moderate for India (full reload drift)
- **Auditability**: Secure for US (local append only), Weak for India pre-remediation (no per-day diff tracking)
- **Structurally compliant**: Code uses `ProxyAdapter` and `MarketLoader` abstraction
- **Content deficient**: Breadth of ingestion narrower than contract definition (pre-expansion)

**Post-expansion status**: US proxy set COMPLETE. India remediated to delta-merge in Feb 2026.
