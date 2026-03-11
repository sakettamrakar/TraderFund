# Broker Connector Architecture

## Design Goals

The broker layer provides live read-only portfolio ingestion while preserving TraderFund governance constraints:

- no trade placement
- no order modification
- no capital movement
- no self-activation from the dashboard

## Connector Interface

All broker integrations conform to `src/portfolio_intelligence/connectors/base.py`.

Required methods:

- `authenticate()`
- `fetch_holdings()`
- `fetch_positions()`
- `fetch_orders()`
- `fetch_instruments()`

The interface is intentionally narrow so that portfolio intelligence can ingest multiple brokers without redesigning the normalization or analytics core.

## Current Implementation: Zerodha

`src/portfolio_intelligence/connectors/zerodha.py` is the first live connector.

### Supported Read-Only Endpoints

- profile: `/user/profile`
- holdings: `/portfolio/holdings`
- positions: `/portfolio/positions`
- order history: `/orders`
- instrument dump: `/instruments`

### Authentication Paths

- API key plus existing access token
- API key plus request token plus API secret, exchanged through `/session/token`

### Controls

- request throttling through `max_requests_per_second`
- request timeout through `request_timeout_seconds`
- missing-credential reporting without secret logging
- explicit read-only implementation with no write endpoints present

## Credential Handling

Environment-backed configuration lives in `src/portfolio_intelligence/config.py`.

Supported variables:

- `KITE_API_KEY`
- `KITE_API_SECRET`
- `KITE_ACCESS_TOKEN`
- `KITE_REQUEST_TOKEN`
- `KITE_REDIRECT_URL`

Compatibility aliases are also accepted for `ZERODHA_*`.

The validation path reports:

- whether credentials are present
- whether authentication succeeded
- which logical credentials are missing
- whether a login URL is available

Secret values are not emitted to logs or markdown reports.

## Integration Boundary

Broker connectors return raw broker records only. They do not:

- infer portfolio weights
- map sectors
- compute factor exposures
- score conviction
- persist dashboard artifacts

Those responsibilities belong to:

- normalization
- enrichment
- analytics
- storage

This keeps broker-specific changes isolated.

## Failure Model

Expected failure classes:

- missing credentials
- token exchange failure
- expired access token
- broker rate limiting
- network timeout
- malformed broker payloads

Failures are surfaced through `BrokerAuthResult` or connector exceptions and are meant to terminate refresh cleanly rather than silently degrade imports.

## Extensibility Path

The same interface can support:

- Interactive Brokers
- Alpaca
- TD Ameritrade or Schwab migration targets
- crypto exchanges

Broker-specific work should stay inside a dedicated connector module that emits the shared raw dataclasses:

- `RawBrokerHolding`
- `RawBrokerPosition`
- `RawBrokerOrder`
- `InstrumentRecord`

## Operational Pattern

1. Build connector from environment-backed config.
2. Authenticate.
3. Fetch holdings, positions, orders, and instruments.
4. Hand raw objects to `PortfolioIntelligenceService.refresh_from_connector(...)`.
5. Persist raw, normalized, and analytics artifacts for dashboard consumption.

This pattern is already implemented for Zerodha and is the template for future US broker integrations.
