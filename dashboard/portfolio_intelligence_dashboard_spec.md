# Portfolio Intelligence Dashboard Spec

## Module Objective

Provide a read-only dashboard surface for institutional-style portfolio diagnostics across India and US portfolios. The module must expose data provenance, truth epoch, and regime-gate state while never initiating broker refresh or trade execution from the browser.

## Implemented Entry Points

- Frontend panel: `src/dashboard/frontend/src/components/PortfolioIntelligencePanel.jsx`
- Frontend API client: `src/dashboard/frontend/src/services/portfolioApi.js`
- Backend loader: `src/dashboard/backend/loaders/portfolio.py`
- Backend routes: `src/dashboard/backend/app.py`

## Backend API Contract

- `GET /api/portfolio/overview/{market}`
- `GET /api/portfolio/holdings/{market}/{portfolio_id}`
- `GET /api/portfolio/diversification/{market}/{portfolio_id}`
- `GET /api/portfolio/risk/{market}/{portfolio_id}`
- `GET /api/portfolio/structure/{market}/{portfolio_id}`
- `GET /api/portfolio/performance/{market}/{portfolio_id}`
- `GET /api/portfolio/insights/{market}/{portfolio_id}`
- `GET /api/portfolio/resilience/{market}/{portfolio_id}`
- `GET /api/portfolio/combined`

All endpoints are GET-only and return dashboard-safe analytical data.

## Panel Layout

### Header

Displays:

- module name
- read-only analytics note
- truth epoch
- selected market

### Portfolio Overview

Displays:

- total value
- total PnL
- total positions
- resilience score and classification

### Portfolio Selector

One button per imported portfolio in the selected market. The frontend defaults to the first available portfolio.

### Top Holdings

Shows:

- symbol
- weight
- conviction
- active risk flags

### Diversification

Shows:

- sector allocation
- factor exposure

### Risk And Resilience

Shows:

- regime gate state
- concentration score
- macro sensitivity
- resilience score

### Insights

Shows advisory-only insights with severity styling.

### Combined Market Bar

Shows:

- aggregated US value
- aggregated India value
- combined USD value when FX is available
- FX source status

## Empty And Error States

The module must be explicit when no imported portfolios exist.

Current behavior:

- empty state tells the operator to run the read-only tracker refresh outside the dashboard
- API failures render an error banner
- combined USD view shows `BLOCKED` when the FX rate is unavailable

## Provenance And Governance

The dashboard must visibly surface:

- `truth_epoch`
- market scope
- regime gate state
- provenance attached by backend loaders

It must not hide degraded or blocked analytical states.

## Non-Goals

The current dashboard module does not:

- initiate broker authentication
- trigger portfolio refresh
- accept trade actions
- rebalance portfolios
- optimize allocations

Those operations remain outside the dashboard boundary.

## Future Enhancements

- structure and performance subpanels wired into the frontend
- cross-market factor aggregation
- portfolio history spark lines
- stale-data badges
- deeper holdings drilldowns
- US broker portfolio selector parity once live connectors are added
