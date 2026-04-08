# Data Provenance Visibility Report

**Truth Epoch:** TRUTH_EPOCH_2026-03-06_01  
**Audit Date:** 2026-03-13

---

## Dashboard Provenance Display (After Audit)

The portfolio intelligence dashboard now displays the following provenance fields:

### Header Bar
| Field | Source | Example |
|-------|--------|---------|
| Epoch | `overview.truth_epoch` | TRUTH_EPOCH_2026-03-06_01 |
| Scope | `market` prop | INDIA |
| Source | `portfolio_data_source` | MCP |

### Data Provenance and Freshness Card
| Field | Source | Description |
|-------|--------|-------------|
| Data Source | `portfolio_data_source` | MCP or API badge |
| Portfolio Last Refresh | `portfolio_refresh_timestamp` | Human-readable latest ingestion time |
| Market Data Timestamp | `data_as_of` | When market data was captured |
| Truth Epoch | `truth_epoch` | System knowledge baseline |
| Broker Status | `refresh_diagnostics.broker_connectivity` | Broker connection state |
| MCP Status | `refresh_diagnostics.mcp.portfolio_fetch_status` | MCP connector state |
| API Fallback | `refresh_diagnostics.api_fallback.status` | API fallback state |
| Source Provenance | `source_provenance` | Canonical broker connector ID |

### Explanatory Note
> Truth epoch = system knowledge baseline. Refresh timestamp = latest portfolio snapshot.

This clarifies that the truth epoch is a frozen reference point, while the refresh timestamp represents the actual latest data.

---

## Raw Data Traceability Panel

A collapsible panel allows inspection of:

| Section | Fields |
|---------|--------|
| Data Artifact Paths | analytics, normalized, and raw import JSON file paths |
| Ingestion Diagnostics | analytics engine, data source, provenance, connector mode, ingestion timestamp |
| Broker Portfolio Summary | raw broker-reported fields |

---

## Data Flow Provenance Chain

```
Broker (Zerodha Kite)
  ↓ MCP-first / API fallback
Raw Import Snapshot
  → data/portfolio_intelligence/imports/{market}/{portfolio_id}/latest.json
  ↓
Normalized Holdings
  → data/portfolio_intelligence/normalized/{market}/{portfolio_id}/latest.json
  ↓
Enriched Holdings (technicals + factor exposures)
  ↓
Analytics Output (+ exposure engine)
  → data/portfolio_intelligence/analytics/{market}/{portfolio_id}/latest.json
  ↓
Dashboard API → Frontend Display
```

Each artifact preserves:
- `truth_epoch`
- `data_as_of`
- `portfolio_refresh_timestamp`
- `portfolio_data_source`
- `source_provenance`
- `refresh_diagnostics`

---

## Freshness Indicators

| Indicator | Location | Meaning |
|-----------|----------|---------|
| Green timestamp | Portfolio Last Refresh | Data is from latest ingestion |
| MCP badge | Data Source | Portfolio fetched via Model Context Protocol |
| API badge | Data Source | Portfolio fetched via REST API fallback |
| UNAVAILABLE | Any field | Data not available for this field |

## Compliance

- OBL-DATA-PROVENANCE-VISIBLE: ✓ All provenance fields visible
- OBL-TRUTH-EPOCH-DISCLOSED: ✓ Shown in header and provenance card
- OBL-REGIME-GATE-EXPLICIT: ✓ Regime gate state shown in risk card
- OBL-HONEST-STAGNATION: ✓ Timestamps reflect actual data age
