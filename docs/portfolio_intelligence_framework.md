# Portfolio Intelligence Framework

Truth epoch: TRUTH_EPOCH_2026-03-06_01

## Architecture

The portfolio intelligence framework extends the existing exposure engine with stock research and portfolio-level synthesis.

Architecture:

Portfolio Data
-> Exposure Engine
-> Stock Research Engine
-> Portfolio Intelligence Engine
-> Dashboard

## Portfolio Intelligence Responsibilities

- Convert stock research into portfolio-level suggestions
- Detect portfolio-wide risk concentrations
- Aggregate stock-level risk flags into risk alerts
- Produce stock intelligence summaries suitable for dashboard display
- Generate valuation overview across holdings
- Produce an advisory narrative synthesis layer

## Portfolio-Level Outputs

- `portfolio_suggestions`
- `portfolio_risk_alerts`
- `stock_research_profiles`
- `stock_intelligence_summaries`
- `valuation_overview`
- `research_synthesis`

## Suggestion Categories

- `sector_overexposure`
- `macro_regime_misalignment`
- `excessive_growth_exposure`
- `correlated_risk_cluster`
- `research_follow_up`

## Advisory Boundary

Outputs are analytical guidance only. They never include:

- trade instructions
- capital sizing recommendations
- self-activation logic
- execution hooks

## Backward Compatibility

Existing analytics artifacts may predate the new intelligence fields. To preserve dashboard continuity, the backend loaders compute intelligence on demand when the persisted analytics payload lacks the new fields.
