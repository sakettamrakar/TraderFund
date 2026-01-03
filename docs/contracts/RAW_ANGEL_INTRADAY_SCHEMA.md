# RAW_ANGEL_INTRADAY_SCHEMA.md

## Overview
This document defines the data contract for raw market data ingested via Angel One SmartAPI in the TraderFund system.

## Data Storage
- **Format**: JSON Lines (.jsonl)
- **Location**: `data/raw/api_based/angel/`
- **Sub-folders**:
  - `intraday_ohlc/`: Individual files per symbol, exchange, and date (e.g., `NSE_INFY_2026-01-03.jsonl`).
  - `ltp_snapshots/`: Daily files containing LTP snapshots for all watchlist symbols (e.g., `ltp_snapshot_2026-01-03.jsonl`).

## Field Definitions

### Intraday OHLC (`intraday_ohlc/`)
| Field | Type | Description |
|---|---|---|
| `symbol` | String | Trading symbol (e.g., INFY) |
| `exchange` | String | Exchange segment (e.g., NSE) |
| `interval` | String | Candle interval (e.g., ONE_MINUTE) |
| `timestamp` | ISO8601 String | Time of the candle (Includes timezone +05:30) |
| `open` | Float | Opening price |
| `high` | Float | Daily high during the interval |
| `low` | Float | Daily low during the interval |
| `close` | Float | Closing price |
| `volume` | Integer | Traded volume |
| `source` | String | Data source (Fixed: `ANGEL_SMARTAPI`) |
| `ingestion_ts` | ISO8601 String | System timestamp when data was persisted |

### LTP Snapshots (`ltp_snapshots/`)
| Field | Type | Description |
|---|---|---|
| `symbol` | String | Trading symbol |
| `exchange` | String | Exchange segment |
| `ltp` | Float | Last Traded Price |
| `open` | Float | Day's open price |
| `high` | Float | Day's high price |
| `low` | Float | Day's low price |
| `close` | Float | Previous day's close price |
| `timestamp` | ISO8601 String | Time of the snapshot |
| `source` | String | Data source (Fixed: `ANGEL_SMARTAPI`) |
| `ingestion_ts` | ISO8601 String | System timestamp when data was persisted |

## Guarantees

### Append-Only Guarantee
- Raw files are opened in `append` mode (`a`).
- Existing data is NEVER overwritten.
- Each ingestion cycle appends new records to the end of the file.

### Restart-Safety Guarantee
- The ingestor fetches the most recent 5 minutes of data by default.
- Upon restart, the ingestor will fetch and append data, ensuring no gaps if the downtime was less than the fetch window.
- **Note**: Redundant data (duplicates) may exist in raw files; these must be handled by the downstream processing layer.

### Timezone Assumptions
- All timestamps from Angel One API are in IST (Indian Standard Time, UTC+5:30).
- System ingestion timestamps (`ingestion_ts`) are in local system time.
