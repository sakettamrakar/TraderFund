# Stage 0: Universe Hygiene

> **Pipeline Stage:** 0 of 6  
> **Purpose:** Deterministic universe reduction from ~7,000 to 1,000–2,000 eligible symbols

## Overview

This module is the **first gate** in the research pipeline. It filters out structurally ineligible symbols using only cheap, deterministic criteria before any expensive analysis is performed.

## What This Module Does

✅ Filters by exchange (NYSE, NASDAQ, etc.)  
✅ Filters by asset type (equity only)  
✅ Excludes penny stocks (price < $1)  
✅ Excludes illiquid symbols (avg volume < 50K)  
✅ Excludes inactive symbols (< 20 trading days in 30-day window)  
✅ Classifies by liquidity and price buckets  

## What This Module Does NOT Do

❌ Compute technical indicators (SMA, RSI, momentum)  
❌ Detect price patterns or trends  
❌ Generate trading signals  
❌ Apply subjective judgment or ML  

## Usage

### Run Eligibility Evaluation (Weekly)

```powershell
python research_modules/universe_hygiene/eligibility_runner.py --evaluate
```

### Dry Run (No Output File)

```powershell
python research_modules/universe_hygiene/eligibility_runner.py --evaluate --dry-run
```

### Output as JSON

```powershell
python research_modules/universe_hygiene/eligibility_runner.py --evaluate --summary-json
```

## Output

**File:** `data/master/us/universe_eligibility.parquet`

| Column | Type | Description |
|:-------|:-----|:------------|
| `symbol` | string | Ticker symbol |
| `exchange` | string | Exchange code |
| `eligibility_status` | string | `eligible` or `excluded` |
| `exclusion_reason` | string | Reason code if excluded |
| `liquidity_bucket` | string | VERY_LOW / LOW / ACCEPTABLE / HIGH |
| `price_bucket` | string | EXTREME_LOW / LOW / ACCEPTABLE / HIGH |
| `avg_daily_volume` | float | 20-day average volume |
| `avg_price` | float | 20-day average close price |
| `trading_days_in_window` | int | Trading days observed |
| `last_evaluated_date` | string | ISO 8601 date |

## Configuration

All thresholds are configurable in `config.py`:

```python
PRICE_THRESHOLDS = {
    "penny_cutoff": 1.00,
    "extreme_low": 5.00,
    "low": 10.00,
    "acceptable": 50.00,
}

VOLUME_THRESHOLDS = {
    "illiquid": 50_000,
    "very_low": 100_000,
    "low": 500_000,
    "acceptable": 1_000_000,
}
```

## Exclusion Reason Codes

| Code | Description |
|:-----|:------------|
| `exchange_not_allowed` | Not on allowed exchange list |
| `asset_type_not_equity` | Not common stock |
| `penny_stock` | Price below $1 |
| `illiquid` | Avg volume < 50K |
| `inactive` | < 20 trading days in window |
| `delisted` | Has delisting date |
| `no_price_data` | No staged data available |

## Pipeline Integration

```
Stage 0 (This)          Stage 1
[Symbol Master] ──► [Eligibility Filter] ──► [universe_eligibility.parquet] ──► [Structural Checks]
```

## Execution Characteristics

- **Frequency:** Weekly (not daily)
- **Idempotent:** Yes (safe to rerun)
- **Dependencies:** Symbol master and staged price data must exist
