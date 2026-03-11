# MCP Broker Connector Design

## Governance Boundary

- Truth epoch: `TRUTH_EPOCH_2026-03-06_01`
- Data mode: `REAL_ONLY`
- Execution mode: `REAL_RUN`
- Read/write constraint: read-only only

The MCP path is implemented only for portfolio extraction and diagnostics. No trade placement, order modification, cancellation, or capital-routing path is exposed through TraderFund even though the upstream Kite MCP tool catalog includes non-read-only tools.

## Implemented Connector

- MCP connector base: `src/portfolio_intelligence/broker_mcp_connectors/base.py`
- Zerodha implementation: `src/portfolio_intelligence/broker_mcp_connectors/kite_mcp.py`

`KiteMCPConnector` is now the primary read-only ingestion source for Zerodha portfolios.

## MCP Session Flow

1. `connect_to_mcp()` sends `initialize` to `https://mcp.kite.trade/mcp`
2. The connector captures the returned `mcp-session-id`
3. A best-effort `notifications/initialized` call is sent
4. `authenticate()` calls `get_profile`
5. If the server reports that login is required, the connector calls `login` and extracts the returned Kite login URL
6. If profile data is returned with account identity fields, the connector is treated as authenticated

This keeps credentials isolated to the broker connector and out of the analytics layer.

## Read-Only Tool Surface Used

The connector is restricted to these MCP tools:

- `login`
- `get_profile`
- `get_holdings`
- `get_positions`
- `get_orders`
- `search_instruments`

TraderFund does not call:

- `place_order`
- `modify_order`
- `cancel_order`
- `place_gtt_order`
- `modify_gtt_order`
- `delete_gtt_order`

## Canonical Mapping

MCP payloads are normalized into TraderFund broker records before entering the existing normalization pipeline.

### Holdings

- `tradingsymbol|symbol|ticker -> symbol`
- `exchange|exchange_segment -> exchange`
- `quantity + t1_quantity -> quantity`
- `average_price|price -> average_price`
- `last_price|close_price|price -> last_price`
- `pnl -> pnl`
- `instrument_token -> instrument_token`

### Positions

- `tradingsymbol|symbol|ticker -> symbol`
- `quantity -> quantity`
- `average_price|price -> average_price`
- `last_price|close_price|price -> last_price`
- `pnl -> pnl`
- `overnight_quantity -> overnight_quantity`
- `day_quantity|intraday_quantity -> intraday_quantity`

### Instruments

The MCP layer derives instrument metadata through `search_instruments` on the symbols present in holdings and positions. Missing instrument metadata does not block normalization.

## Validation Contract

The MCP path is accepted only when these conditions all pass:

- `data_complete`
- `positions_detected`
- `schema_valid`

Current implementation detail:

- `data_complete` means holdings and positions endpoints both returned list-shaped payloads
- `positions_detected` means the positions endpoint returned a list, even if empty
- `schema_valid` means every returned row contains at least symbol and quantity fields required by the downstream canonical model

If validation fails, control moves to the Kite Connect API fallback path.

## Provenance

When MCP is used successfully, persisted artifacts are tagged with:

- `portfolio_data_source: MCP`
- `source_provenance: kite_mcp`
- `refresh_diagnostics.mcp.*`
- `portfolio_refresh_timestamp`

These tags flow through raw snapshots, normalized payloads, analytics outputs, backend loaders, and the dashboard module.

## Future MCP Extensibility

The new package layout supports additional broker MCP connectors:

- `src/portfolio_intelligence/broker_mcp_connectors/kite_mcp.py`
- future `interactive_brokers_mcp.py`
- future `crypto_exchange_mcp.py`

All MCP connectors are expected to terminate into the same normalization and analytics pipeline rather than inventing broker-specific downstream logic.
