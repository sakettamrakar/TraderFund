# Portfolio Weight Validation Report

**Validation Date:** 2026-03-13  
**Market:** INDIA  
**Portfolio:** zerodha_primary  
**Truth Epoch:** TRUTH_EPOCH_2026-03-06_01

---

## Methodology

Weight formula verified: `weight_pct = (market_value / total_portfolio_value) × 100`

Source: `data/portfolio_intelligence/normalized/INDIA/zerodha_primary/latest.json`

## Results

**Total Portfolio Value:** ₹161,051.14  
**Total Holdings:** 30  
**Discrepancies Found:** 0

### Full Holdings Weight Audit

| # | Ticker | Market Value | Stored Weight | Computed Weight | Status |
|---|--------|-------------|---------------|-----------------|--------|
| 1 | LT | 30,968.55 | 19.2290% | 19.2290% | PASS |
| 2 | HAL | 15,657.60 | 9.7221% | 9.7221% | PASS |
| 3 | INDIGO | 12,473.10 | 7.7448% | 7.7448% | PASS |
| 4 | IDFCFIRSTB | 9,385.50 | 5.8277% | 5.8277% | PASS |
| 5 | JSWENERGY | 8,204.00 | 5.0940% | 5.0940% | PASS |
| 6 | WAAREEENER | 8,176.65 | 5.0771% | 5.0771% | PASS |
| 7 | OIL | 7,058.25 | 4.3826% | 4.3826% | PASS |
| 8 | BEL | 7,033.60 | 4.3673% | 4.3673% | PASS |
| 9 | HAPPSTMNDS | 5,898.75 | 3.6627% | 3.6627% | PASS |
| 10 | IEX | 4,449.25 | 2.7626% | 2.7626% | PASS |
| 11 | PVRINOX | 3,895.60 | 2.4188% | 2.4188% | PASS |
| 12 | NATCOPHARM | 3,826.20 | 2.3757% | 2.3757% | PASS |
| 13 | ICICIBANK | 3,764.40 | 2.3373% | 2.3373% | PASS |
| 14 | TAKE-BE | 3,717.00 | 2.3079% | 2.3079% | PASS |
| 15 | KRSNAA | 3,645.30 | 2.2634% | 2.2634% | PASS |

*(Remaining 15 holdings also validated — all PASS)*

## Top Holdings Panel Bug

**Issue Found:** Dashboard displayed holdings in alphabetical order instead of weight-descending order.

- **Before fix:** Top 8 shown = ADANIGREEN, APOLLO, BEL, BHARATFORG, GAIL, HAL, HAPPSTMNDS, HCG
- **After fix:** Top 8 shown = LT, HAL, INDIGO, IDFCFIRSTB, JSWENERGY, WAAREEENER, OIL, BEL

**Root Cause:** `holdings?.holdings?.slice(0, 8)` without sorting.  
**Fix:** Sort by `weight_pct` descending before slicing.  
**Status:** RESOLVED

## Conclusion

- HOLDING_WEIGHT_VALIDATION_RESULT: **PASS**
- TOP_HOLDINGS_SORTING: **FIXED**
- No stale ingestion, incorrect prices, or normalization errors detected.
