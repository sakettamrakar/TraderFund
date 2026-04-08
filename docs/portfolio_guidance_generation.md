# Portfolio Guidance Generation

Truth epoch: TRUTH_EPOCH_2026-03-06_01

## Guidance Logic

The portfolio guidance layer uses threshold-based synthesis from concentration, macro alignment, valuation posture, and stock-level research.

### diversify_sector_exposure

Triggered when dominant sector concentration is materially elevated.

### reduce_concentration

Triggered when the largest single position contributes disproportionate portfolio risk.

### strengthen_defensive_allocation

Triggered when macro regime compatibility is weak and portfolio resilience would benefit from defensive ballast.

### review_overvalued_positions

Triggered when a set of holdings screens as overvalued versus sector anchors.

### review_macro_sensitive_holdings

Triggered when too many holdings cluster in rate-sensitive, capex-sensitive, or commodity-sensitive buckets.

## Strengthening Insights

Separate from suggestions, strengthening insights describe what would make the portfolio structurally better, such as reducing cluster risk or improving diversification quality.

## Output Style

Guidance is concrete but non-executable. Examples:

- consider diversifying sector exposure toward defensive areas
- review macro-sensitive holdings for concentration of economic path risk
- reduce single-name concentration over time to improve resilience
