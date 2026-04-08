# Stock Research Dashboard Panels

## Dashboard Sections Added

### Portfolio Risk Alerts

Displays aggregated portfolio and stock-level risk alerts.

Fields:

- ticker (optional)
- flag
- explanation
- confidence_level
- severity

### Portfolio Intelligence Insights

Displays advisory portfolio suggestions and the research narrative synthesis.

Fields:

- category
- headline
- detail
- confidence_level

### Valuation Overview

Displays valuation distribution across holdings.

Fields:

- counts by valuation status
- undervalued ticker list
- fairly valued ticker list
- overvalued ticker list

### Stock Research Profiles

Displays holding-level research using a chip selector for the largest positions.

Fields:

- portfolio role
- confidence
- valuation status
- macro alignment score
- fundamental view
- valuation view
- technical and risk view
- stock intelligence summary
- risk flags

## Data Sources

The dashboard consumes:

- `/api/portfolio/research/{market}/{portfolio_id}`
- `/api/portfolio/advisory/{market}/{portfolio_id}`
- existing portfolio overview / holdings / exposure endpoints

## Rendering Guarantees

- Advisory only
- Truth epoch visible in parent portfolio panel
- No execution controls
- Compatible with backfilled intelligence from older analytics artifacts
