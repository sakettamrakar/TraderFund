# Angel One SmartAPI Ingestion

This module provides API-based market data ingestion using Angel One SmartAPI. It fetches live OHLC candles and LTP snapshots for configured symbols and persists them as raw data files.

## Purpose

- Fetch live intraday OHLC candles (1m, 5m, etc.)
- Fetch LTP (Last Traded Price) snapshots
- Backfill historical candle data
- Persist data in append-only JSON Lines format

## APIs Used

| API | Purpose |
|-----|---------|
| `getCandleData` | Fetch historical/live OHLC candles |
| `ltpData` | Fetch last traded price |
| `generateSession` | Login with TOTP |
| `generateToken` | Refresh access token |

## Folder Structure

```
ingestion/api_ingestion/angel_smartapi/
├── __init__.py
├── config.py              # Configuration and credentials
├── auth.py                # Authentication manager
├── instrument_master.py   # Symbol-to-token mapping
├── market_data_ingestor.py    # Live data fetcher
├── historical_data_ingestor.py # Historical backfill
├── scheduler.py           # Polling loop
└── README.md
```

## Data Output

```
data/raw/api_based/angel/
├── intraday_ohlc/         # Daily OHLC files per symbol
│   └── NSE_RELIANCE_2026-01-03.jsonl
├── ltp_snapshots/         # Daily LTP snapshot files
│   └── ltp_snapshot_2026-01-03.jsonl
├── historical/            # Historical backfill files
│   └── NSE_RELIANCE_ONE_MINUTE.jsonl
└── instrument_master.json # Cached instrument list
```

## Environment Setup

Create a `.env` file in the project root:

```env
ANGEL_API_KEY=your_api_key_here
ANGEL_CLIENT_ID=your_client_id
ANGEL_PIN=your_trading_pin
ANGEL_TOTP_SECRET=your_totp_secret_base32
```

## Running Locally

### Install Dependencies

```powershell
pip install smartapi-python pyotp
```

### Run the Scheduler

```powershell
# Continuous polling (market hours only)
python -m ingestion.api_ingestion.angel_smartapi.scheduler

# Run outside market hours (for testing)
python -m ingestion.api_ingestion.angel_smartapi.scheduler --outside-market-hours

# Single cycle only
python -m ingestion.api_ingestion.angel_smartapi.scheduler --single-cycle
```

### Manual Backfill

```python
from datetime import date, timedelta
from ingestion.api_ingestion.angel_smartapi.historical_data_ingestor import HistoricalDataIngestor

ingestor = HistoricalDataIngestor()
ingestor.backfill_and_save(
    symbol="RELIANCE",
    exchange="NSE",
    from_date=date.today() - timedelta(days=7),
    to_date=date.today(),
    interval="FIVE_MINUTE"
)
```

## Configuration Options

Edit `config.py` or set environment variables:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `polling_interval_seconds` | 60 | Seconds between fetches |
| `default_candle_interval` | ONE_MINUTE | Candle interval |
| `symbol_watchlist` | Top 10 NSE stocks | Symbols to track |

## Notes

- Token auto-refreshes before expiry (5-hour validity)
- Market hours check: 9:00-15:30 IST, weekdays
- Exponential backoff on API errors (max 5 min)
- Graceful shutdown on SIGINT/SIGTERM
