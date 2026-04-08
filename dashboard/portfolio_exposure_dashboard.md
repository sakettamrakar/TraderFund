# Portfolio Exposure Dashboard — Panel Specification

**Truth Epoch:** TRUTH_EPOCH_2026-03-06_01  
**Component:** `PortfolioExposurePanel.jsx`

---

## Overview

The Portfolio Exposure Dashboard panel is embedded within the existing `PortfolioIntelligencePanel` and renders after the insights card. It visualizes exposure data from two new API endpoints:

- `GET /api/portfolio/exposure/{market}/{portfolio_id}`
- `GET /api/portfolio/macro-alignment/{market}/{portfolio_id}`

## Panel Sections

### 1. Composite Metrics Grid
Five score cards displayed in a responsive grid:

| Metric | Description |
|--------|-------------|
| Diversification | Portfolio diversification score (0-1) |
| Concentration | Inverse of top-3 position weight concentration |
| Factor Balance | Evenness of factor exposure distribution |
| Regime Alignment | Alignment with current macro regime |
| Composite Health | Average of all four scores |

### 2. Sector Allocation Bars
Horizontal bar chart showing sector weight distribution, sorted by descending weight. Each bar is proportional to the largest sector weight.

### 3. Factor Exposure Bars
Five horizontal bars for factor loadings (Growth, Value, Momentum, Quality, Volatility), each scaled 0-1. Dominant factor label displayed below.

### 4. Geography Exposure Bars
Horizontal bars showing country/geography weight distribution.

### 5. Macro Regime Sensitivity
Four sensitivity bars:
- Growth Regime Sensitivity
- Interest Rate Sensitivity
- Inflation Sensitivity
- Liquidity Sensitivity

Below bars: regime hint, risk appetite, and alignment score.

Regime vulnerability flags (if any) are shown as warning tags.

### 6. Correlated Holdings Clusters
Displayed only when clusters are detected (≥1). Shows sector name, holding count, and ticker list for each correlated cluster. Sector concentration HHI and factor overexposure warnings shown when triggered.

### 7. Exposure Insights Feed
Advisory-only insights displayed as severity-colored cards (HIGH=red, MEDIUM=orange, LOW=green). Each shows category and explanation.

## Data Flow

```
User selects portfolio
  → getPortfolioExposure(market, portfolioId)
  → getPortfolioMacroAlignment(market, portfolioId)
  → PortfolioExposurePanel receives { exposure, macroAlignment } props
  → Renders all sections from response data
```

## API Response Structure (Exposure Endpoint)

```json
{
  "portfolio_id": "...",
  "market": "...",
  "truth_epoch": "...",
  "regime_gate_state": "...",
  "sector_exposure": { "allocation_pct": {}, "dominant_sector": "..." },
  "industry_exposure": { "weight_distribution": {} },
  "geography_exposure": { "country_exposure_pct": {} },
  "factor_exposure": { "growth_factor": 0.6, "value_factor": 0.4, ... },
  "hidden_concentrations": { "correlated_holdings_clusters": {}, ... },
  "exposure_metrics": { "diversification_score": 0.7, "composite_health": 0.65, ... },
  "exposure_insights": [{ "category": "...", "severity": "...", "explanation": "..." }]
}
```

## Styling

CSS variables inherit from the existing dashboard theme (`--bg-secondary`, `--accent`, `--text-primary`). The panel uses the same `portfolio-card` styling conventions. Bar fills use `--accent` (teal by default). Warning tags use orange.

## Governance

- Read-only: no interactive controls that trigger mutations
- All insights marked `advisory_only: true`
- No trade recommendations or execution buttons
