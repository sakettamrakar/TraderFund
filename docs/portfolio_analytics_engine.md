# Portfolio Analytics Engine

## Purpose

`src/portfolio_intelligence/analytics.py` converts enriched canonical holdings into advisory portfolio intelligence. It does not execute trades, generate orders, or call any broker write APIs.

## Inputs

The analytics engine consumes the enriched payload produced by:

- `src/portfolio_intelligence/normalization.py`
- `src/portfolio_intelligence/enrichment.py`

Expected input sections:

- portfolio metadata
- canonical holdings with weights and market values
- fundamentals
- technicals
- sentiment placeholders
- macro context
- factor context

## Holding-Level Intelligence

Each holding is transformed into a holding card with:

- `ticker`
- `canonical_ticker`
- `weight_pct`
- `market_value`
- `pnl`
- `pnl_pct`
- `sector`
- `industry`
- `conviction_score`
- `opportunity_classification`
- `risk_flags`
- `regime_alignment_score`
- `regime_compatibility`
- `factor_exposure`
- `technicals`
- `fundamentals`
- `sentiment`
- `liquidity_risk`
- `coverage_status`
- `contribution_to_return`

### Conviction Logic

Conviction is a blend of:

- valuation proxy from PE when available
- technical momentum score
- quality proxy from factor exposure
- growth proxy from trend regime

The score is explicitly capped when macro or factor regime context is incomplete:

- `COMPLETE`: no cap
- `DEGRADED`: capped at `0.65`
- `BLOCKED`: capped at `0.45`

### Risk Flags

The current engine raises:

- `FUNDAMENTAL_COVERAGE_GAP`
- `VOLATILITY_ELEVATED`
- `TREND_WEAKNESS`
- `POSITION_CONCENTRATION`

### Opportunity Classification

- `HIGH_CONVICTION`
- `MONITOR`
- `REVIEW_REQUIRED`

These are advisory labels only.

## Portfolio-Level Diagnostics

The engine computes:

- total value
- total cost basis
- total unrealized PnL
- sector allocation
- geography allocation
- factor distribution
- diversification score
- effective positions
- concentration score
- top-3 and top-5 weight concentration
- correlation clustering by dominant sector grouping
- macro sensitivity
- winners and laggards
- contribution ranking
- resilience score

## Strategic Insights

The engine emits structured insights under `insights[]`. Current rules detect:

- hidden sector concentration
- factor imbalance
- macro vulnerability when regime context is degraded
- review-required holdings with multiple flags

Each insight contains:

- category
- severity
- headline
- detail
- affected holdings

## Regime Gate

`regime_gate_state` is central to portfolio honesty.

- `COMPLETE`: canonical macro and factor context are present with sufficient confidence
- `DEGRADED`: context exists but factor confidence is below threshold
- `BLOCKED`: canonical context is missing

This state is returned to the dashboard and used to cap downstream conviction rather than hiding the data quality problem.

## Combined View

The analytics payload includes a combined-view stub:

- US portfolios are native USD
- India portfolios require `PORTFOLIO_USDINR_RATE` for USD conversion
- when FX is absent, combined USD value is suppressed and a warning is emitted

## Data Provenance

Analytics artifacts are persisted under:

- `data/portfolio_intelligence/analytics/<MARKET>/<PORTFOLIO_ID>/latest.json`
- `data/portfolio_intelligence/history/<MARKET>/<PORTFOLIO_ID>/<STAMP>.json`

Each payload includes:

- `truth_epoch`
- `data_as_of`
- `trace.source`
- `trace.analytics_engine`

## Current Coverage Limits

- India fundamental coverage uses local PE data today; other fundamental fields remain `None`.
- Sentiment is scaffolded but not yet backed by a canonical news or event provider.
- Correlation clustering is currently heuristic and sector-based, not covariance-matrix based.
- Factor exposures are modelled proxies, not Barra-style institutional factors.

These limits are surfaced by design and should remain visible until deeper canonical feeds are integrated.
