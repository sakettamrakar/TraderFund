# Portfolio Strategy Engine

Truth epoch: TRUTH_EPOCH_2026-03-06_01

## Purpose

The Portfolio Strategy Engine upgrades portfolio intelligence from descriptive analytics to prescriptive, advisory-only guidance.

Architecture:

Portfolio Data
-> Exposure Engine
-> Stock Research Engine
-> Portfolio Strategy Engine
-> Dashboard

## Inputs

- exposure analysis
- stock research profiles
- macro regime context
- factor context
- correlation cluster outputs

## Outputs

- `portfolio_strategy_summary`
- `portfolio_strategy_suggestions`
- `portfolio_risk_alerts`
- `portfolio_opportunity_signals`
- `portfolio_strengthening_insights`

## Prescriptive Suggestion Categories

- `diversify_sector_exposure`
- `reduce_concentration`
- `strengthen_defensive_allocation`
- `review_overvalued_positions`
- `review_macro_sensitive_holdings`

## Advisory Boundary

The engine may recommend reviewing, diversifying, strengthening, or reducing concentration, but it never emits trade instructions, target sizes, or executable orders.
