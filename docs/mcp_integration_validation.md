# MCP Integration Validation

## Validation Scope

The validator now checks both the historical portfolio subsystem state and the new broker-routing state.

Implementation: `src/portfolio_intelligence/validation.py`

## Reported Status Fields

Core subsystem fields:

- `CONNECTIVITY_OK|CONNECTIVITY_ERROR`
- `INGESTION_OK|INGESTION_ERROR`
- `ANALYTICS_OK|ANALYTICS_ERROR`
- `DASHBOARD_OK|DASHBOARD_ERROR`

MCP-first routing fields:

- `MCP_CONNECTIVITY_OK|MCP_CONNECTIVITY_ERROR`
- `MCP_PORTFOLIO_FETCH_OK|MCP_PORTFOLIO_FETCH_ERROR`
- `MCP_SCHEMA_VALID|MCP_SCHEMA_INVALID`
- `API_FALLBACK_READY|API_FALLBACK_STANDBY|API_FALLBACK_IN_USE|API_FALLBACK_AUTH_REQUIRED|API_FALLBACK_ERROR`

## Live Validation Result As Of March 11, 2026

Current report from `docs/system_validation_report.md`:

- `CONNECTIVITY_OK`
- `INGESTION_ERROR`
- `ANALYTICS_ERROR`
- `DASHBOARD_OK`
- `MCP_CONNECTIVITY_OK`
- `MCP_PORTFOLIO_FETCH_ERROR`
- `MCP_SCHEMA_INVALID`
- `API_FALLBACK_AUTH_REQUIRED`

## Interpretation

- The Zerodha MCP server is reachable from the current environment.
- MCP authentication is not complete because the connector requires interactive login.
- The API fallback code path is present, but the remaining API auth material is not available yet.
- Dashboard integration is operational, but no imported portfolio artifacts exist yet, so portfolio analytics remain empty.

## Diagnostic Fields

The validator exposes:

- MCP auth result
- API auth result
- MCP validation booleans
- credential presence summary
- India overview payload
- combined portfolio payload

This makes stagnation visible instead of masking it behind generic failure messages.

## Operational Commands

Validation only:

```powershell
python scripts\portfolio_tracker_refresh.py --validate-only
```

Live refresh attempt:

```powershell
python scripts\portfolio_tracker_refresh.py --broker zerodha --market INDIA --portfolio-id zerodha_primary --account-name "Zerodha Primary"
```

## Exit Criteria For Full Green State

The subsystem will move closer to green when:

- MCP interactive login is completed and the same session is usable by the connector, or
- API fallback receives a valid `KITE_ACCESS_TOKEN` or `KITE_REQUEST_TOKEN`

Once either source authenticates successfully, the next refresh should create imported artifacts and move ingestion and analytics out of the empty state.
