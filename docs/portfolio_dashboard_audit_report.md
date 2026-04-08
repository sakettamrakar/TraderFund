# Portfolio Dashboard Audit Report

**Truth Epoch:** TRUTH_EPOCH_2026-03-06_01  
**Audit Date:** 2026-03-13  
**Data Mode:** REAL_ONLY  
**Governance:** INV-NO-EXECUTION · INV-NO-CAPITAL · INV-READ-ONLY-DASHBOARD

---

## 1. Holdings Weight Validation

**Status:** PASS — 0 discrepancies

All 30 INDIA holdings validated. Weight formula: `weight = market_value / total_portfolio_value * 100`.

| Holding | Market Value | Stored Weight | Computed Weight | Diff |
|---------|-------------|---------------|-----------------|------|
| LT | 30,968.55 | 19.23% | 19.23% | 0.0000 |
| HAL | 15,657.60 | 9.72% | 9.72% | 0.0000 |
| INDIGO | 12,473.10 | 7.74% | 7.74% | 0.0000 |
| IDFCFIRSTB | 9,385.50 | 5.83% | 5.83% | 0.0000 |
| JSWENERGY | 8,204.00 | 5.09% | 5.09% | 0.0000 |

Total portfolio value: ₹161,051.14 across 30 positions.

**Result:** HOLDING_WEIGHT_VALIDATION_RESULT = PASS

---

## 2. Top Holdings Panel Audit

**Status:** BUG FOUND AND FIXED

**Issue:** Analytics holdings were stored in alphabetical order by ticker. The dashboard's `holdings?.holdings?.slice(0, 8)` was taking the first 8 alphabetically (ADANIGREEN, APOLLO, BEL...) instead of the top 8 by weight (LT, HAL, INDIGO...).

**Root Cause:** `slice(0, 8)` without prior sort.

**Fix Applied:** Changed to:
```js
[...(holdings?.holdings || [])]
  .sort((a, b) => (b.weight_pct || 0) - (a.weight_pct || 0))
  .slice(0, 8)
```

**Verified:** After fix, top holdings correctly show LT (19.23%), HAL (9.72%), INDIGO (7.74%), etc.

---

## 3. Metric Explainability Layer

**Status:** IMPLEMENTED

Added tooltip definitions for all exposure and risk metrics displayed in dashboard. Each tooltip includes:
- **Label**: metric name
- **Short description**: what the metric measures
- **Interpretation guide**: how to read the value

Metrics with tooltips:
- Resilience Score (< 0.4 fragile / 0.4-0.7 adequate / > 0.7 strong)
- Concentration Score (lower = more concentrated)
- Macro Sensitivity (higher = more exposed to macro shocks)
- Regime Alignment (higher = better aligned)
- Diversification (HHI-based sector spread)
- Factor Balance (evenness of factor loadings)
- Composite Health (average of all scores)
- Correlated Risk Clusters (hidden concentration risk)
- Regime Vulnerability (positional risks)

Score cards now show color-coded status (green/orange/red) and text classification.

---

## 4. Data Provenance and Freshness

**Status:** ENHANCED

Dashboard now clearly displays:
- **Data Source**: MCP | API badge
- **Portfolio Last Refresh**: human-readable timestamp of latest portfolio snapshot
- **Market Data Timestamp**: data_as_of field from ingestion
- **Truth Epoch**: system knowledge baseline (TRUTH_EPOCH_2026-03-06_01)
- **Source Provenance**: broker connector trace
- **Broker Connectivity**: MCP/API status

Added explanatory note: "Truth epoch = system knowledge baseline. Refresh timestamp = latest portfolio snapshot."

---

## 5. Ingestion Update Verification

**Status:** VERIFIED

The ingestion pipeline (`service.py → ingest_snapshot()`) correctly:
1. Writes raw snapshot to `data/portfolio_intelligence/imports/`
2. Normalizes holdings with correct weight computation
3. Enriches with technicals and factor exposures
4. Runs analytics (including new exposure engine)
5. Persists to `data/portfolio_intelligence/analytics/`
6. Updates portfolio registry

Dashboard reads `latest.json` artifacts and returns current data. Exposure engine computes on-the-fly when analytics artifacts predate the exposure engine addition.

- INGESTION_PIPELINE_OK: ✓
- DASHBOARD_REFRESH_OK: ✓
- DATA_TIMESTAMP_UPDATED: ✓

---

## 6. Raw Data Traceability

**Status:** IMPLEMENTED

Added collapsible "Raw Data Traceability" panel showing:
- **Data Artifact Paths**: analytics, normalized, and raw import JSON paths
- **Ingestion Diagnostics**: engine version, data source, provenance, connector mode, ingestion timestamp
- **Broker Portfolio Summary**: raw broker summary fields (if available)

Users can expand the panel to inspect data lineage and verify ingestion correctness.

---

## 7. Dashboard UX Improvements

**Status:** IMPLEMENTED

- Metric tooltips with hover popups (ⓘ icon)
- Color-coded score values (green > 0.7, orange 0.4-0.7, red < 0.4)
- Text status classification on each score ("strong", "adequate", "fragile")
- Enhanced provenance card with clear field labels
- Collapsible raw data trace panel
- Vite HMR verified — all updates apply without build errors
