# Broker Data Source Panel

## Purpose

Expose which broker access path produced the portfolio now visible in the Portfolio Intelligence dashboard.

This panel is implemented inside `src/dashboard/frontend/src/components/PortfolioIntelligencePanel.jsx`.

## Display Fields

- `Portfolio Data Source`
- `Broker Connectivity`
- `MCP Status`
- `API Fallback`
- `Refresh Timestamp`

## Data Contract

The panel reads from the imported holdings payload and portfolio overview payload:

- `portfolio_data_source`
- `portfolio_refresh_timestamp`
- `refresh_diagnostics.broker_connectivity`
- `refresh_diagnostics.mcp.connectivity_status`
- `refresh_diagnostics.mcp.portfolio_fetch_status`
- `refresh_diagnostics.api_fallback.status`

## Visual Rules

- `MCP` is shown as a green badge
- `API` is shown as a blue badge
- `UNAVAILABLE` is shown as a muted badge

## Behavioral Rules

- The panel is read-only
- It must not expose login buttons or refresh actions
- It must show degraded states directly instead of suppressing them
- It must continue rendering even when no imported portfolios exist

## Current Empty-State Behavior

If no imported portfolio exists for the chosen market, the dashboard tells the operator to run the tracker refresh outside the browser. This preserves the invariant that the dashboard remains observational only.
