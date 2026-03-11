# Portfolio Intelligence System Validation Report

- Generated at: `2026-03-11T14:39:19.871208+00:00`
- Truth epoch: `TRUTH_EPOCH_2026-03-06_01`
- Execution mode: `REAL_RUN`

## Core Status

- Connectivity: `CONNECTIVITY_OK`
- Ingestion: `INGESTION_ERROR`
- Analytics: `ANALYTICS_ERROR`
- Dashboard: `DASHBOARD_OK`

## MCP First Validation

- MCP connectivity: `MCP_CONNECTIVITY_OK`
- MCP fetch: `MCP_PORTFOLIO_FETCH_ERROR`
- MCP schema: `MCP_SCHEMA_INVALID`
- API fallback: `API_FALLBACK_AUTH_REQUIRED`

## Broker Diagnostics

- MCP authentication: `False`
- MCP auth message: Kite MCP login required for read-only portfolio ingestion.
- MCP login URL available: `True`
- MCP validation: `data_complete=False, positions_detected=False, schema_valid=False`
- API fallback authenticated: `False`
- API fallback message: Missing Zerodha credentials for read-only portfolio ingestion.
- API fallback missing credentials: `KITE_ACCESS_TOKEN or KITE_REQUEST_TOKEN`

## Notes

- Kite MCP is reachable but requires interactive broker login before holdings and positions can be pulled.
- Kite Connect API fallback remains blocked until the remaining authentication material is supplied.
- No imported analytical artifacts were available at validation time, so dashboard metrics remain in an empty state.
