# Look-through Exposure Integration

## Current Integration Points

The real look-through path is integrated into the existing portfolio intelligence pipeline instead of a parallel module.

### Existing infrastructure reused
- Portfolio ingestion: `src/portfolio_intelligence/service.py`
- Portfolio normalization: `src/portfolio_intelligence/normalization.py`
- Portfolio enrichment: `src/portfolio_intelligence/enrichment.py`
- Exposure computation: `src/portfolio_intelligence/exposure_engine.py`
- Analytics output: `src/portfolio_intelligence/analytics.py`
- Dashboard loaders: `src/dashboard/backend/loaders/portfolio.py`
- Dashboard panels: `src/dashboard/frontend/src/components/PortfolioExposurePanel.jsx`

### Real metadata sources currently integrated
- India security master: `data/input/daily/Equities/sec_list_*.csv`
- Cached fund disclosures: `data/portfolio_intelligence/fund_metadata/{market}/{ticker}.json`
- Cached benchmark compositions: `data/portfolio_intelligence/benchmark_metadata/{market}/{benchmark}.json`
- Optional provider-backed ETF holdings: Alpha Vantage `ETF_PROFILE` when `ALPHAVANTAGE_API_KEY` is configured

## Architecture mapping
1. Broker ingestion loads raw mutual fund holdings.
2. Normalization preserves benchmark and underlying metadata fields on mutual fund rows.
3. Enrichment resolves:
   - security type
   - fund family
   - benchmark reference
   - benchmark provider
   - underlying holdings
   - look-through provenance state
4. Exposure engine expands real underlying holdings first.
5. If real disclosures are unavailable, cached benchmark compositions are used.
6. If neither exists, the system surfaces `HEURISTIC_FALLBACK` or `REAL_LOOKTHROUGH_UNAVAILABLE` explicitly.

## Governance notes
- All look-through states are provenance-visible.
- Truth epoch remains disclosed through the existing portfolio artifact path.
- The dashboard remains read-only.
- No execution or capital allocation logic was added.
