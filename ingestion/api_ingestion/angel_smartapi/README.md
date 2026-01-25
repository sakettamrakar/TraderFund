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
ANGEL_API_KEY=your_live_api_key_here
ANGEL_CLIENT_ID=your_live_client_id
ANGEL_PIN=your_live_trading_pin
ANGEL_TOTP_SECRET=your_live_totp_secret_base32

# Separate credentials for Historical Ingestion (Phase 1B)
ANGEL_HIST_API_KEY=your_hist_api_key_here
ANGEL_HIST_CLIENT_ID=your_hist_client_id
ANGEL_HIST_PIN=your_hist_trading_pin
ANGEL_HIST_TOTP_SECRET=your_hist_totp_secret_base32
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

---

## Historical Data Ingestion (Phase 1B)

> ⚠️ **ISOLATION NOTICE**: Historical data ingestion is a **DORMANT, ON-DEMAND** utility.
> It is **NOT** part of the live trading pipeline and must **NEVER** influence momentum trading decisions.

### Purpose

The historical data ingestor fetches **daily OHLCV candles** for configured symbols.
This data is intended **ONLY** for:

- Future context and diagnostics
- Risk analysis and compliance
- Post-market research (manually triggered)

**NOT FOR:**
- Live trading signals
- Momentum engine integration
- Automated scheduled execution

### API Endpoint

Uses `getCandleData` with `interval=ONE_DAY` for daily candles only.
Maximum lookback: 2000 days (~5.5 years).

### CLI Usage

```powershell
# Single symbol backfill (1 year)
python -m ingestion.api_ingestion.angel_smartapi.historical_cli --symbol RELIANCE --years 1

# All watchlist symbols (2 years)
python -m ingestion.api_ingestion.angel_smartapi.historical_cli --all-watchlist --years 2

# Dry run (show what would be fetched)
python -m ingestion.api_ingestion.angel_smartapi.historical_cli --symbol TCS --years 1 --dry-run

# Skip confirmation prompt
python -m ingestion.api_ingestion.angel_smartapi.historical_cli --symbol INFY --years 1 --confirm
```

### Data Output

Historical data is stored in append-only JSONL format:

```
data/raw/api_based/angel/historical/
├── NSE_RELIANCE_1d.jsonl
├── NSE_TCS_1d.jsonl
└── NSE_INFY_1d.jsonl
```

### Record Schema

```json
{
  "symbol": "RELIANCE",
  "exchange": "NSE",
  "interval": "1D",
  "date": "2025-01-02",
  "open": 1234.50,
  "high": 1250.00,
  "low": 1230.00,
  "close": 1245.75,
  "volume": 5000000,
  "source": "ANGEL_SMARTAPI",
  "ingestion_ts": "2026-01-03T15:55:00+05:30"
}
```

### Re-run Safety

- Historical files use **append mode** (`a`)
- Running twice will append duplicate records
- Use `get_existing_dates()` method to check for existing data before fetching
- Deduplication is the responsibility of downstream processing

### Phase Lock

See: `docs/phase_locks/PHASE_1B_HISTORICAL_INGESTION_LOCK.md`
