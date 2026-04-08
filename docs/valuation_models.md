# Valuation Models

Truth epoch: TRUTH_EPOCH_2026-03-06_01

## Current Implementation

The valuation layer is inspired by institutional relative valuation workflows while remaining deterministic and data-bounded.

### 1. Sector PE Anchor Model

For holdings with observable PE ratio:

- compare company PE to sector benchmark PE
- compute premium/discount percentage
- assign one of:
  - `undervalued`
  - `fairly_valued`
  - `overvalued`

Formula:

premium_discount_pct = ((company_pe / sector_pe_benchmark) - 1) * 100

Thresholds:

- <= -15%: `undervalued`
- >= +20%: `overvalued`
- otherwise: `fairly_valued`

### 2. Intrinsic Value Estimate Proxy

Instead of a price target, the system produces a fair multiple estimate:

- if undervalued -> benchmark * 1.05
- if overvalued -> benchmark * 0.95
- else -> benchmark unchanged

This is intentionally conservative and advisory only.

## Planned Extensions

When deeper data coverage becomes available, the valuation layer can absorb:

- DCF approximation using earnings/cash-flow proxies
- EV/EBITDA sector multiple comparison
- price-to-book anchor for financials
- sum-of-the-parts models for conglomerates

## Coverage Handling

If PE ratio or sector benchmark is unavailable:

- `valuation_status = unknown`
- `relative_valuation = insufficient_data`
- `intrinsic_value_estimate = null`

This ensures honest partiality rather than synthetic precision.
