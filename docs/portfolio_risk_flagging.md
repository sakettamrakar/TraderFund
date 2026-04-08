# Portfolio Risk Flagging

Truth epoch: TRUTH_EPOCH_2026-03-06_01

## Objective

The risk flagging layer identifies stock-level and portfolio-level risks that materially shape the current portfolio profile.

## Stock-Level Risk Flags

### concentration_risk

Triggered when a single holding weight is 10% or greater.

### valuation_risk

Triggered when valuation status is `overvalued`.

### macro_sensitive_position

Triggered when stock macro alignment score is 0.4 or lower.

### deteriorating_fundamentals

Triggered when fundamental coverage is too incomplete to underwrite confidently.

### weak_technical_structure

Triggered when trend regime is bearish.

## Portfolio-Level Risk Alerts

The portfolio intelligence engine converts stock risk flags and exposure vulnerabilities into a flat portfolio alert surface suitable for dashboard consumption.

Each alert includes:

- `ticker` or portfolio-wide scope
- `flag`
- `severity`
- `explanation`
- `confidence_level`

## Exposure-Derived Risks

Portfolio-wide exposure vulnerabilities are also surfaced, including:

- sector concentration
- correlated cluster concentration
- macro regime vulnerability flags
- factor crowding

## Governance

Risk flags remain descriptive. They do not imply liquidation, rotation, or execution.
