# Portfolio Intelligence Dashboard Specification

- Status: `DESIGN / DRY_RUN`
- Date: `2026-03-11`
- Truth epoch: `TRUTH_EPOCH_2026-03-06_01` (frozen)
- Scope: `US`, `INDIA`, `COMBINED`

## 1. Module Objective

Add a read-only Portfolio Intelligence module to the TraderFund dashboard so a user can inspect broker-held portfolios with the same governance standards used elsewhere in the system.

The module must:

- show portfolio and holding diagnostics
- keep provenance, truth epoch, and freshness visible
- make regime compatibility explicit
- support `US`, `INDIA`, and combined exposure views

The module must not:

- upload broker files from the dashboard
- trigger portfolio refreshes from the dashboard
- place orders, size capital, or activate strategies

The dashboard is an observer surface only. Import and refresh workflows remain outside the dashboard.

## 2. Placement in Existing UI

The module should be added as a new top-level dashboard section next to the current market intelligence views.

Suggested navigation:

- `Market Intelligence`
- `Portfolio Intelligence`

Within `Portfolio Intelligence`, the user can switch market scope:

- `US`
- `INDIA`
- `Combined`

## 3. Backend Contract

All portfolio routes are GET-only.

| Route | Purpose |
| --- | --- |
| `GET /api/portfolio/overview/{market}` | portfolio summaries for one market |
| `GET /api/portfolio/holdings/{market}/{portfolio_id}` | per-holding intelligence cards |
| `GET /api/portfolio/diversification/{market}/{portfolio_id}` | sector, geography, and factor concentration |
| `GET /api/portfolio/risk/{market}/{portfolio_id}` | drawdown, macro, and clustering diagnostics |
| `GET /api/portfolio/structure/{market}/{portfolio_id}` | core versus satellite and concentration structure |
| `GET /api/portfolio/performance/{market}/{portfolio_id}` | unrealized PnL and contribution analysis |
| `GET /api/portfolio/insights/{market}/{portfolio_id}` | advisory insight feed |
| `GET /api/portfolio/resilience/{market}/{portfolio_id}` | resilience score and component breakdown |
| `GET /api/portfolio/combined` | combined US plus INDIA analytical view |

All responses must include:

- `truth_epoch`
- `trace`
- `data_as_of`
- `market`
- `regime_gate_state` when the payload includes conviction or compatibility scoring

## 4. Primary Screens

### 4.1 Portfolio Overview

Purpose:

- summarize all imported portfolios for the selected market
- show total value, unrealized PnL, position count, and top allocation buckets

Required fields:

- `portfolio_id`
- `display_name`
- `broker`
- `market`
- `total_value`
- `total_cost_basis`
- `total_pnl`
- `total_pnl_pct`
- `holding_count`
- `resilience_score`
- `resilience_classification`
- `data_as_of`
- `truth_epoch`

Behavior:

- clicking a portfolio row opens the holdings view
- if no imported portfolios exist, show a read-only empty state with import instructions, not an upload control

### 4.2 Holdings Intelligence

Purpose:

- show each holding as a diagnostic row with expandable details

Required columns:

- symbol
- weight
- unrealized PnL
- conviction score
- opportunity classification
- regime compatibility
- risk flags count
- staleness indicator

Expanded detail sections:

- fundamentals
- technicals
- factor exposure
- sentiment and catalysts
- risk flags
- provenance

Behavior:

- sort by weight, PnL, conviction, or risk count
- filter by severity, classification, or regime compatibility
- keep risk and degraded-state tags visible even when collapsed

### 4.3 Diversification Panel

Purpose:

- visualize concentration and exposure distribution

Required visual elements:

- sector allocation chart
- geography allocation chart
- factor concentration bars
- effective positions count

Required callouts:

- highest concentration bucket
- diversification gap summary
- unknown or unresolved classification count

### 4.4 Risk Monitor

Purpose:

- display portfolio-level risk diagnostics

Required sections:

- drawdown sensitivity
- macro exposure
- correlation clustering
- single-position impact concentration

Required callouts:

- regime gate state
- weakest risk dimension
- top concentration warning

### 4.5 Performance Panel

Purpose:

- show unrealized gain or loss diagnostics without becoming a trade blotter

Required sections:

- total unrealized PnL
- winners versus laggards
- contribution to portfolio return
- top and bottom contributors

### 4.6 Strategic Insights Feed

Purpose:

- render advisory portfolio observations

Allowed categories:

- diversification gap
- factor imbalance
- macro vulnerability
- hidden concentration risk
- positions requiring review
- regime-aligned holdings
- deteriorating fundamentals
- improving momentum

Rules:

- insights are sorted by severity
- language remains observational only
- each insight shows affected holdings, confidence, and provenance

### 4.7 Resilience Score

Purpose:

- summarize portfolio robustness across multiple dimensions

Required dimensions:

- diversification
- risk management
- regime alignment
- fundamental quality
- momentum health

Required callouts:

- overall classification
- weakest dimension
- strongest dimension

### 4.8 Combined Market View

Purpose:

- provide a cross-market lens over `US` and `INDIA`

Required sections:

- local-currency totals by market
- normalized combined value
- combined sector exposure
- combined factor exposure
- cross-market insights
- FX provenance

Rules:

- if FX is stale, show a warning banner
- if FX is unavailable, keep markets separate and suppress combined resilience scoring

## 5. Visual Language

The portfolio module should follow the established dashboard design language rather than introducing a separate visual system.

Severity mapping:

- `INFO`: blue
- `YELLOW`: amber
- `ORANGE`: orange
- `RED`: red
- `CRITICAL`: magenta

Semantic colors:

- positive PnL: green
- negative PnL: red
- stale or partial data: amber
- blocked or unavailable context: gray with explicit label

Required visible tags:

- `truth epoch`
- `data as of`
- `trace`
- `regime gate`
- `stale`
- `partial`

## 6. Empty, Loading, and Degraded States

### Loading

- use skeleton placeholders
- keep layout stable to avoid visual shifts

### Empty

If no portfolios exist for a scope, show:

- `No imported portfolios available for this market.`
- last successful import time if known
- operator guidance path for manual import workflow

### Partial

If some holdings cannot be fully enriched:

- keep them visible
- show `partial coverage`
- display which analytical blocks are unavailable

### Degraded

If macro or factor context is stale:

- show an amber banner
- downgrade conviction display
- label regime compatibility as degraded rather than silently omitting it

### Blocked

If canonical regime context is unavailable:

- suppress regime-derived scoring
- keep descriptive holding data visible
- explain the blocked reason in-panel

## 7. Interaction Rules

- no write controls
- no upload controls
- no rebalance actions
- no execution verbs in labels or copy
- row expansion must preserve keyboard access
- filters must not hide degraded-state warnings by default

## 8. Accessibility and Responsiveness

Accessibility requirements:

- severity cannot be color-only; every chip includes text
- table rows and expansion controls are keyboard navigable
- charts require text summaries
- banners and degraded-state labels are screen-reader visible

Responsive behavior:

- desktop: two-column analytics layout
- tablet: stacked panels with full-width charts
- mobile: cards instead of dense tables for holdings

## 9. Suggested Frontend Composition

Suggested component set:

- `PortfolioIntelligenceTab`
- `PortfolioOverview`
- `HoldingsIntelligenceGrid`
- `DiversificationPanel`
- `RiskMonitor`
- `PerformancePanel`
- `StrategicInsightsFeed`
- `ResilienceScoreCard`
- `CombinedMarketView`

Suggested service layer:

- `portfolioApi.js` for GET requests only

Suggested state:

- selected market scope
- selected portfolio id
- selected holdings filters
- latest route payloads and staleness metadata

## 10. Copy Rules

Allowed copy examples:

- `This portfolio shows elevated technology concentration.`
- `Three holdings are misaligned with the current regime gate.`
- `Momentum is improving for two holdings, subject to stale macro context.`

Disallowed copy examples:

- `Sell these holdings.`
- `Reduce this allocation now.`
- `Buy the strongest names.`

## 11. Acceptance Criteria

- every screen is read-only
- every payload shows provenance and truth epoch
- every conviction-bearing view shows regime gate state
- `US` and `INDIA` render with the same component contracts
- combined view includes explicit FX provenance
- empty and degraded states are honest and visible
