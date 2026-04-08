# Portfolio Intelligence System Validation Report

- Generated at: `2026-03-13T14:06:51.349402+00:00`
- Truth epoch: `TRUTH_EPOCH_2026-03-06_01`
- Execution mode: `REAL_RUN`

## Core Status

- Connectivity: `CONNECTIVITY_OK`
- Ingestion: `INGESTION_OK`
- Analytics: `ANALYTICS_OK`
- Dashboard: `DASHBOARD_OK`

## MCP First Validation

- MCP connectivity: `MCP_CONNECTIVITY_OK`
- MCP fetch: `MCP_PORTFOLIO_FETCH_OK`
- MCP schema: `MCP_SCHEMA_VALID`
- API fallback: `API_FALLBACK_STANDBY`

## Broker Diagnostics

- MCP authentication: `True`
- MCP auth message: Authenticated against Kite MCP in read-only mode.
- MCP login URL available: `False`
- MCP validation: `data_complete=True, positions_detected=True, schema_valid=True`
- API fallback authenticated: `True`
- API fallback message: Authenticated against Zerodha in read-only mode.
- API fallback missing credentials: `NONE`

## Notes

- Kite Connect API fallback is available if MCP is unavailable or invalid.
