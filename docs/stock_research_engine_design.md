# Stock Research Engine Design

Truth epoch: TRUTH_EPOCH_2026-03-06_01

## Purpose

The Stock Research Engine adds deterministic, advisory-only research profiles for every portfolio holding. It sits above normalized and enriched holdings data and below the portfolio intelligence layer.

Pipeline:

Portfolio Data -> Enrichment -> Stock Research Engine -> Portfolio Intelligence Engine -> Dashboard

## Inputs

- Enriched holdings from portfolio analytics
- Fundamental coverage currently available in enrichment (`pe_ratio`, partial placeholders)
- Technical structure (`trend_regime`, `momentum_score`, `volatility_regime`, `return_20d`)
- Factor exposure (`growth`, `value`, `momentum`, `quality`, `macro_sensitivity`)
- Macro context and regime gate state

## Outputs

Each research profile includes:

- `ticker`, `sector`, `market`, `portfolio_weight`
- `fundamental_summary`
- `growth_outlook`
- `profitability_profile`
- `balance_sheet_strength`
- `valuation_analysis`
- `relative_valuation`
- `intrinsic_value_estimate`
- `technical_structure`
- `trend_strength`
- `volatility_profile`
- `macro_regime_alignment`
- `factor_exposure`
- `risk_flags`
- `portfolio_role`
- `confidence_level`

## Valuation Logic

The current implementation uses sector PE anchor models:

- India sector benchmark map for common sectors
- US benchmark map for common sectors
- `undervalued`: holding PE at least 15% below sector anchor
- `fairly_valued`: within a normal band around sector anchor
- `overvalued`: holding PE at least 20% above sector anchor

Intrinsic value is currently expressed as a fair multiple estimate, not a price target.

## Risk Flag Logic

The engine emits advisory stock-level flags:

- `concentration_risk`
- `valuation_risk`
- `macro_sensitive_position`
- `deteriorating_fundamentals`
- `weak_technical_structure`

Each flag carries:

- `explanation`
- `confidence_level`

## Governance

- Advisory only
- No order or capital outputs
- Explicit regime gate disclosure
- Compatible with partial coverage and degraded macro context
