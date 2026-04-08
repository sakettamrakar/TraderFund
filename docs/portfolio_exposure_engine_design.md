# Portfolio Exposure Engine — Design Document

**Truth Epoch:** TRUTH_EPOCH_2026-03-06_01  
**Module:** `src/portfolio_intelligence/exposure_engine.py`  
**Version:** 1.0.0  
**Governance:** INV-NO-EXECUTION · INV-NO-CAPITAL · INV-READ-ONLY-DASHBOARD

---

## 1. Overview

The Portfolio Exposure Engine provides institutional-grade exposure analytics across five dimensions: sector, industry, geography, factor, and macro regime. It detects hidden concentration risks and generates advisory-only insights.

## 2. Exposure Dimensions

### 2.1 Sector Exposure (`compute_sector_exposure`)
- Weight allocation by GICS-style sector
- Value aggregation by sector
- Holding count by sector
- Dominant sector identification

### 2.2 Industry Exposure (`compute_industry_exposure`)
- Sub-classification weight distribution
- Industry count and dominant industry

### 2.3 Geography Exposure (`compute_geography_exposure`)
- Country/geography weight distribution
- Value by geography region

### 2.4 Factor Exposure (`compute_factor_exposure`)
Decomposes portfolio into five factor dimensions using weighted-average loadings:
- **Growth**: Revenue/earnings growth orientation
- **Value**: Valuation discount characteristics
- **Momentum**: Price trend strength
- **Quality**: Earnings quality, ROE, balance sheet strength
- **Volatility**: Macro sensitivity and price volatility

Outputs include:
- Per-factor weighted loading
- Dominant factor identification
- Factor balance score (0-1, measures evenness of factor distribution)

### 2.5 Macro Regime Exposure (`compute_macro_regime_exposure`)
Evaluates portfolio alignment against current macro conditions:
- **Growth regime sensitivity**: How exposed the portfolio is to growth cycle changes
- **Interest rate sensitivity**: Cyclical sector weight as rate proxy
- **Inflation sensitivity**: Commodity/staples weight as inflation proxy
- **Liquidity sensitivity**: Proportion of medium-liquidity holdings

Outputs:
- Regime hint (DEFENSIVE / BALANCED / RISK_ON)
- Risk appetite disclosure
- Macro alignment score (0-1)
- Regime vulnerability flags

## 3. Hidden Concentration Detection

`detect_hidden_concentrations` identifies non-obvious risks:

| Detection | Method | Threshold |
|-----------|--------|-----------|
| Correlated clusters | Same-sector grouping | ≥3 holdings in sector |
| Sector concentration | HHI computation | HHI > 2500 |
| Factor overexposure | Max factor loading | Any factor > 0.7 |

## 4. Composite Metrics

`compute_exposure_metrics` produces five health scores:

| Metric | Range | Computation |
|--------|-------|-------------|
| `diversification_score` | 0-1 | 1 - normalized HHI |
| `concentration_score` | 0-1 | 1 - top-3 position weight/100 |
| `factor_balance_score` | 0-1 | 1 - 2×stddev of factor loadings |
| `regime_alignment_score` | 0-1 | Regime-dependent tilt scoring |
| `composite_health` | 0-1 | Average of above four scores |

## 5. Insight Generation

`generate_exposure_insights` produces advisory insights when thresholds are breached:

| Insight Category | Trigger |
|-----------------|---------|
| `sector_overconcentration` | Dominant sector > 30% weight |
| `hidden_factor_exposure` | Any factor loading > 0.7 |
| `regime_misalignment` | Macro alignment score < 0.4 |
| `diversification_gap` | Diversification score < 0.5 |
| `correlated_risk_clusters` | ≥2 correlated holding clusters |
| `regime_vulnerability` | Any regime vulnerability flag active |

All insights are marked `advisory_only: true`.

## 6. API Contract

### Input
```python
engine.compute_full_exposure(
    holdings: List[Dict],           # Enriched holdings with factor_exposure
    macro_context: Dict = {},       # From evolution tick macro context
    factor_context: Dict = {},      # From evolution tick factor context
    portfolio_id: str = "",
    market: str = "",
    truth_epoch: str = "",
    data_as_of: str = "",
)
```

### Output Structure
```json
{
  "portfolio_id": "...",
  "market": "...",
  "truth_epoch": "...",
  "computed_at": "ISO8601",
  "sector_exposure": { ... },
  "industry_exposure": { ... },
  "geography_exposure": { ... },
  "factor_exposure": { ... },
  "macro_regime_exposure": { ... },
  "hidden_concentrations": { ... },
  "exposure_metrics": { ... },
  "exposure_insights": [ ... ],
  "trace": { "engine": "portfolio_intelligence.exposure_engine", "version": "1.0.0" }
}
```

## 7. Governance Compliance

- All functions are pure computations with no side effects
- No trade recommendations or execution signals
- No capital allocation actions
- All outputs include truth_epoch and provenance trace
- Regime gate state is explicit on every macro output
