# Portfolio Refresh Pipeline Update

## Updated Refresh Service

The refresh path is now split into two layers:

- `PortfolioIntelligenceService`
- `PortfolioRefreshService`

`PortfolioIntelligenceService` owns canonical ingestion and artifact persistence.

`PortfolioRefreshService` owns source routing:

- probe MCP
- validate MCP payload
- fall back to API if needed
- return explicit diagnostics

## New Refresh Flow

1. Start refresh for Zerodha portfolio
2. Probe Kite MCP connectivity and authentication
3. If MCP is authenticated, fetch holdings and positions
4. Validate MCP response
5. If valid, ingest snapshot through the shared normalization and analytics pipeline
6. If invalid, authenticate Kite Connect API
7. If API auth succeeds, ingest through the same shared pipeline
8. Persist diagnostics and chosen `portfolio_data_source`

## Shared Ingest Step

To avoid duplicating logic between MCP and API, the service now uses `ingest_snapshot(...)`.

This single ingest step:

- writes raw import artifacts
- normalizes holdings
- enriches portfolio intelligence
- computes analytics
- writes analytics artifacts
- updates the portfolio registry

## Stored Metadata Additions

The pipeline now persists:

- `portfolio_data_source`
- `source_provenance`
- `refresh_diagnostics`
- `portfolio_refresh_timestamp`
- `portfolio_summary`

These fields are available in:

- raw import snapshots
- normalized portfolio payloads
- analytics outputs
- dashboard overview responses
- holdings payloads consumed by the frontend

## Tracker Behavior

`PortfolioTrackerService.refresh_all()` now calls the MCP-first path automatically for Zerodha registrations. No operator change is required beyond supplying the necessary broker authentication material.

## CLI Behavior

`scripts/portfolio_tracker_refresh.py` now:

- uses MCP-first refresh for Zerodha
- prints the resulting `data_source`
- writes the validation report after every run

## Failure Semantics

The refresh path fails closed.

If neither MCP nor API can authenticate, the system:

- does not invent placeholder portfolio data
- does not write misleading analytics
- emits explicit diagnostics showing which source failed and why
