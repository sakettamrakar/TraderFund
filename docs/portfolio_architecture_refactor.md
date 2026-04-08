# Portfolio Architecture Refactor — Design Document

**Truth Epoch:** TRUTH_EPOCH_2026-03-06_01  
**Governance:** INV-NO-EXECUTION · INV-NO-CAPITAL · INV-READ-ONLY-DASHBOARD  
**Data Mode:** REAL_ONLY

---

## 1. Pre-Existing Architecture

The portfolio intelligence subsystem (`src/portfolio_intelligence/`) was already well-structured with clean separation of concerns:

```
BrokerConnector → Normalization → Enrichment → Analytics → Storage
```

### Module Inventory (Before)

| Module | Purpose | Lines |
|--------|---------|-------|
| `config.py` | Central configuration, credential sets | 116 |
| `service.py` | Orchestration (ingest, refresh, load) | ~200 |
| `normalization.py` | Canonicalize broker holdings | ~200 |
| `enrichment.py` | Attach technicals, factor exposures, macro context | ~197 |
| `analytics.py` | Portfolio-level analytical output | ~200 |
| `storage.py` | JSON artifact persistence | 84 |
| `validation.py` | System diagnostics | 118 |
| `connectors/zerodha.py` | Kite Connect API connector | ~200 |
| `broker_mcp_connectors/kite_mcp.py` | MCP-first connector | ~200 |

### Identified Gaps

1. **Exposure analytics were embedded** within `analytics.py` (sector_allocation, factor_distribution) — not modular or extensible
2. **No hidden concentration detection** beyond basic HHI
3. **No macro regime alignment scoring** independent of per-holding regime compatibility
4. **No institutional-grade exposure decomposition** (industry, geography dimensions)

---

## 2. Architecture Enhancement

### New Module: `exposure_engine.py`

The Portfolio Exposure Engine was added as a dedicated analytical module that plugs into the existing pipeline without disrupting it.

```
Enrichment → Analytics ──→ ExposureEngine → exposure_analysis payload
                    └──→ existing analytics payload
```

### Design Principles

- **Composable Functions**: Each exposure category (sector, industry, geography, factor, macro) is a standalone pure function
- **Engine Class**: `PortfolioExposureEngine` orchestrates all computations and produces a unified output
- **Non-Breaking Integration**: Analytics.py calls the engine and includes `exposure_analysis` as an additional output key
- **Read-Only**: No state mutation, no trade recommendations, no capital actions

### Integration Points

| Layer | File | Change |
|-------|------|--------|
| Analytics | `analytics.py` | Import engine, call `compute_full_exposure()`, add `exposure_analysis` to output |
| Backend Loader | `loaders/portfolio.py` | New `load_portfolio_exposure()`, `load_portfolio_macro_alignment()` |
| Backend Routes | `app.py` | New GET `/api/portfolio/exposure/{market}/{portfolio_id}`, `/api/portfolio/macro-alignment/{market}/{portfolio_id}` |
| Frontend API | `portfolioApi.js` | New `getPortfolioExposure()`, `getPortfolioMacroAlignment()` |
| Frontend Panel | `PortfolioExposurePanel.jsx` | New component with sector bars, factor bars, macro sensitivity, clusters |
| Main Panel | `PortfolioIntelligencePanel.jsx` | Integrated `<PortfolioExposurePanel>` component |

---

## 3. Post-Refactor Architecture

```
src/portfolio_intelligence/
├── config.py              # Configuration (unchanged)
├── service.py             # Orchestration (unchanged)
├── normalization.py       # Canonicalization (unchanged)
├── enrichment.py          # Enrichment (unchanged)
├── analytics.py           # Analytics + exposure engine integration
├── exposure_engine.py     # NEW — institutional-grade exposure computation
├── storage.py             # Persistence (unchanged)
├── validation.py          # System validation (unchanged)
├── connectors/            # Broker connectors (unchanged)
└── broker_mcp_connectors/ # MCP connectors (unchanged)
```

The refactor adds one new module and makes minimal modifications to existing code (3 lines added to `analytics.py`), maintaining full backward compatibility.
