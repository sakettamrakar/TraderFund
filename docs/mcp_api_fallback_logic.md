# MCP API Fallback Logic

## Priority Chain

TraderFund now routes Zerodha portfolio refresh through this order:

`MCP -> API -> error state`

The change is implemented in `src/portfolio_intelligence/service.py` through `PortfolioRefreshService`.

## Decision Sequence

1. Build `KiteMCPConnector`
2. Check MCP connectivity with `initialize`
3. Authenticate MCP session through `get_profile`
4. Fetch holdings and positions through MCP
5. Validate MCP payload shape
6. If valid, ingest via the shared pipeline and mark `portfolio_data_source = MCP`
7. If invalid or unauthenticated, build the Kite Connect API connector
8. If API auth succeeds, ingest via API and mark `portfolio_data_source = API`
9. If API auth also fails, raise a controlled read-only error state with diagnostics

## MCP Failure Cases That Trigger Fallback

- MCP server unreachable
- MCP login required
- MCP authentication failure
- MCP holdings fetch failure
- MCP positions fetch failure
- MCP response schema invalid

## API Fallback Statuses

The refresh diagnostics and validator now emit:

- `API_FALLBACK_READY`
- `API_FALLBACK_STANDBY`
- `API_FALLBACK_IN_USE`
- `API_FALLBACK_AUTH_REQUIRED`
- `API_FALLBACK_ERROR`

## Current Observed State On March 11, 2026

From the live validation run:

- MCP is reachable
- MCP requires interactive login
- API fallback is implemented but not authenticated because `KITE_ACCESS_TOKEN` and `KITE_REQUEST_TOKEN` are absent

That yields:

- `MCP_CONNECTIVITY_OK`
- `MCP_PORTFOLIO_FETCH_ERROR`
- `MCP_SCHEMA_INVALID`
- `API_FALLBACK_AUTH_REQUIRED`

## Why This Design Is Safer

- MCP is attempted first for read-only extraction
- API is used only when MCP does not satisfy the validation gate
- write-capable MCP and API methods are not part of the TraderFund connector flow
- the dashboard remains read-only and never triggers refresh from the browser
- the data source used for every imported portfolio is visible in stored artifacts and UI diagnostics
