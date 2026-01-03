# PROCESSED_INTRADAY_SCHEMA.md

## Overview
This document defines the data contract for the processed intraday candle layer in the TraderFund system.

## Data Storage
- **Format**: Apache Parquet
- **Location**: `data/processed/candles/intraday/`
- **Naming Convention**: `{exchange}_{symbol}_1m.parquet`

## Field Definitions

| Field | Type | Description |
|---|---|---|
| `symbol` | String | Trading symbol (e.g., RELIANCE) |
| `exchange` | String | Exchange segment (e.g., NSE) |
| `timestamp` | Datetime64[ns, UTC+05:30] | Standardized timezone-aware timestamp |
| `open` | Float64 | Opening price of the candle |
| `high` | Float64 | Highest price during the interval |
| `low` | Float64 | Lowest price during the interval |
| `close` | Float64 | Closing price of the candle |
| `volume` | Int64 | Total traded volume during the interval |

## Processing Rules

### Idempotency
- The processor is idempotent. Running it multiple times on the same raw data set produces the same Parquet output.
- Deduplication is performed by `(symbol, timestamp)`. In case of multiple raw entries for the same timestamp, the record with the latest `ingestion_ts` is retained.

### Data Integrity
- Rows are strictly sorted by `timestamp` in ascending order.
- Volume must be non-negative.
- No strategy-specific fields or indicators (e.g., RSI, VWAP) are included in this layer.

### Metadata Removal
- Source-specific fields like `source` and system-specific fields like `ingestion_ts` are removed during processing to maintain a clean domain model.
