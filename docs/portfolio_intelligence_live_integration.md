# Portfolio Intelligence Live Integration

## Governance Envelope

- Truth epoch: `TRUTH_EPOCH_2026-03-06_01`
- Data mode: `REAL_ONLY`
- Execution mode: `REAL_RUN`
- Markets: `US`, `INDIA`
- Invariants: `INV-NO-EXECUTION`, `INV-NO-CAPITAL`, `INV-NO-SELF-ACTIVATION`, `INV-PROXY-CANONICAL`, `INV-READ-ONLY-DASHBOARD`
- Obligations: `OBL-DATA-PROVENANCE-VISIBLE`, `OBL-TRUTH-EPOCH-DISCLOSED`, `OBL-REGIME-GATE-EXPLICIT`, `OBL-MARKET-PARITY`, `OBL-HONEST-STAGNATION`

## Deployment State As Of March 11, 2026

The Portfolio Intelligence subsystem is deployed as a read-only analytics stack. The live ingestion path is implemented for Zerodha, the portfolio analytics engine is wired into the backend and frontend dashboard, and the validation CLI is operational.

The environment is not yet credential-complete for a live broker pull. `docs/system_validation_report.md` currently shows:

- `CONNECTIVITY_ERROR`
- `INGESTION_ERROR`
- `ANALYTICS_ERROR`
- `DASHBOARD_OK`

This is an honest deployment state, not a partial success disguised as completion. The code is live in the repository; live broker authentication is blocked only by missing Zerodha authentication material.

## Implemented Components

- Broker connectors: `src/portfolio_intelligence/connectors/`
- Normalization engine: `src/portfolio_intelligence/normalization.py`
- Enrichment engine: `src/portfolio_intelligence/enrichment.py`
- Portfolio analytics engine: `src/portfolio_intelligence/analytics.py`
- Artifact store and registry: `src/portfolio_intelligence/storage.py`
- Orchestration services: `src/portfolio_intelligence/service.py`
- Validation runner: `src/portfolio_intelligence/validation.py`
- Refresh CLI: `scripts/portfolio_tracker_refresh.py`
- Dashboard backend loader: `src/dashboard/backend/loaders/portfolio.py`
- Dashboard frontend client: `src/dashboard/frontend/src/services/portfolioApi.js`
- Dashboard frontend module: `src/dashboard/frontend/src/components/PortfolioIntelligencePanel.jsx`

## Runtime Flow

1. Broker connector authenticates in read-only mode.
2. Holdings, positions, orders, and instrument metadata are fetched from the broker API.
3. Raw snapshots are written to `data/portfolio_intelligence/imports/<MARKET>/<PORTFOLIO_ID>/`.
4. Canonical holdings are normalized into market, sector, geography, weight, PnL, and metadata fields.
5. Local enrichment adds price-history technicals, India PE coverage, and latest macro and factor context from canonical evolution outputs.
6. The analytics engine computes holding cards, diversification, concentration, factor distribution, resilience, and advisory insights.
7. Final artifacts are written to `data/portfolio_intelligence/analytics/<MARKET>/<PORTFOLIO_ID>/latest.json`.
8. The dashboard consumes GET-only backend endpoints and renders the portfolio module without any trade or broker-side write action.

## Live Zerodha Activation Path

The implemented connector supports two compliant auth paths:

- Direct session use with `KITE_API_KEY` plus `KITE_ACCESS_TOKEN`
- Token exchange with `KITE_API_KEY`, `KITE_REQUEST_TOKEN`, and `KITE_API_SECRET`

Optional:

- `KITE_REDIRECT_URL`
- `PORTFOLIO_BROKER_RPS`
- `PORTFOLIO_REQUEST_TIMEOUT_SECONDS`
- `PORTFOLIO_TRACKER_REFRESH_SECONDS`
- `PORTFOLIO_USDINR_RATE`

The refresh command is:

```powershell
python scripts\portfolio_tracker_refresh.py --broker zerodha --market INDIA --portfolio-id zerodha_primary --account-name "Zerodha Primary"
```

Validation-only mode is:

```powershell
python scripts\portfolio_tracker_refresh.py --validate-only
```

Credential values are read from environment variables through `PortfolioIntelligenceConfig`. The validator reports only presence and missing-field names; it does not print secrets.

## Dashboard Integration

The backend exposes read-only portfolio endpoints:

- `GET /api/portfolio/overview/{market}`
- `GET /api/portfolio/holdings/{market}/{portfolio_id}`
- `GET /api/portfolio/diversification/{market}/{portfolio_id}`
- `GET /api/portfolio/risk/{market}/{portfolio_id}`
- `GET /api/portfolio/structure/{market}/{portfolio_id}`
- `GET /api/portfolio/performance/{market}/{portfolio_id}`
- `GET /api/portfolio/insights/{market}/{portfolio_id}`
- `GET /api/portfolio/resilience/{market}/{portfolio_id}`
- `GET /api/portfolio/combined`

The frontend module renders:

- overview metrics
- holdings diagnostics
- diversification and factor exposure
- risk and resilience
- advisory insights
- combined US and India exposure

No browser action triggers broker refresh. Ingestion remains an operator-side CLI concern.

## Known Gaps

- Live Zerodha validation is blocked until credentials are supplied at runtime.
- US broker connectivity is not implemented yet; the architecture is ready for it.
- Combined USD normalization for India holdings requires `PORTFOLIO_USDINR_RATE`.
- Fundamental and sentiment coverage are intentionally partial until canonical data sources are integrated for both markets.

## Next Activation Steps

1. Provide Zerodha credentials through environment variables or secret injection.
2. Run a live refresh for the India portfolio.
3. Confirm `CONNECTIVITY_OK`, `INGESTION_OK`, and `ANALYTICS_OK` in `docs/system_validation_report.md`.
4. Register additional broker connectors behind the same `BrokerConnector` interface for US portfolios.
