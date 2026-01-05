"""Angel One Historical Data Ingestor (Daily Candles Only).

This module provides a DORMANT, ON-DEMAND utility for fetching historical
daily candle data from Angel One SmartAPI.

CRITICAL ISOLATION NOTICE:
========================
This module is NOT part of the live trading pipeline.
Historical data fetched here must NEVER influence momentum trading decisions.
It is intended ONLY for:
- Future context and diagnostics
- Risk analysis
- Compliance record-keeping

DO NOT integrate this into any live scheduler or momentum engine.
"""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timedelta, date, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

from .auth import AngelAuthManager
from .config import config
from .instrument_master import InstrumentMaster

logger = logging.getLogger(__name__)

# IST timezone offset
IST = timezone(timedelta(hours=5, minutes=30))

# Fixed interval - ONLY daily candles allowed
DAILY_INTERVAL = "ONE_DAY"
INTERVAL_LABEL = "1D"

# API constraints
MAX_DAILY_HISTORY_DAYS = 2000  # Angel API allows up to 2000 days for daily data
DEFAULT_LOOKBACK_YEARS = 1

# Retry configuration
MAX_RETRIES = 3
BASE_RETRY_DELAY_SECONDS = 2
MAX_RETRY_DELAY_SECONDS = 60


class HistoricalDataIngestor:
    """On-demand utility for fetching historical daily candle data.

    ISOLATION NOTICE:
    -----------------
    This class is DORMANT and must NEVER be wired into live trading.
    Use only for manual backfill operations via CLI.

    API constraints:
    ----------------
    - Daily data: max 2000 days history
    - Rate limits apply - use bounded retry logic
    """

    def __init__(
        self,
        auth_manager: Optional[AngelAuthManager] = None,
        instrument_master: Optional[InstrumentMaster] = None,
        cfg: Optional[object] = None,
    ):
        """Initialize the historical data ingestor.

        Args:
            auth_manager: Auth manager instance. Creates new one if not provided.
            instrument_master: Instrument master instance. Creates new one if not provided.
            cfg: Configuration object. Uses default config if not provided.
        """
        self._config = cfg or config
        self._auth = auth_manager or AngelAuthManager(self._config, use_historical=True)
        self._instruments = instrument_master or InstrumentMaster(self._config)
        self._historical_path = Path(self._config.historical_path)

    def _ensure_directories(self) -> None:
        """Ensure output directories exist."""
        self._historical_path.mkdir(parents=True, exist_ok=True)

    def _get_historical_file_path(self, symbol: str, exchange: str) -> Path:
        """Get file path for historical data.

        File naming convention: {EXCHANGE}_{SYMBOL}_1d.jsonl
        """
        return self._historical_path / f"{exchange}_{symbol}_1d.jsonl"

    def _calculate_date_range(
        self,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        lookback_years: int = DEFAULT_LOOKBACK_YEARS,
    ) -> tuple[date, date]:
        """Calculate and validate date range for historical fetch.

        Args:
            from_date: Start date. Defaults to lookback_years ago.
            to_date: End date. Defaults to today.
            lookback_years: Years of history to fetch if from_date not specified.

        Returns:
            Tuple of (from_date, to_date).
        """
        today = date.today()

        if not to_date:
            to_date = today

        if not from_date:
            from_date = to_date - timedelta(days=lookback_years * 365)

        # Validate date range against API constraint
        days_requested = (to_date - from_date).days
        if days_requested > MAX_DAILY_HISTORY_DAYS:
            logger.warning(
                f"Date range ({days_requested} days) exceeds max {MAX_DAILY_HISTORY_DAYS} days. "
                f"Adjusting from_date."
            )
            from_date = to_date - timedelta(days=MAX_DAILY_HISTORY_DAYS)

        return from_date, to_date

    def _make_api_request_with_retry(
        self, client: Any, params: Dict
    ) -> Optional[Dict]:
        """Make API request with bounded exponential backoff retry.

        Args:
            client: Authenticated SmartConnect client.
            params: Request parameters for getCandleData.

        Returns:
            API response dict or None on failure.
        """
        delay = BASE_RETRY_DELAY_SECONDS

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = client.getCandleData(params)

                # Check for rate limit errors
                if response.get("message", "").lower().find("rate limit") >= 0:
                    if attempt < MAX_RETRIES:
                        logger.warning(
                            f"Rate limit hit (attempt {attempt}/{MAX_RETRIES}). "
                            f"Retrying in {delay}s..."
                        )
                        time.sleep(delay)
                        delay = min(delay * 2, MAX_RETRY_DELAY_SECONDS)
                        continue
                    else:
                        logger.error("Rate limit exceeded after max retries")
                        return None

                return response

            except Exception as exc:
                if attempt < MAX_RETRIES:
                    logger.warning(
                        f"API error (attempt {attempt}/{MAX_RETRIES}): {exc}. "
                        f"Retrying in {delay}s..."
                    )
                    time.sleep(delay)
                    delay = min(delay * 2, MAX_RETRY_DELAY_SECONDS)
                else:
                    logger.exception(f"API error after max retries: {exc}")
                    return None

        return None

    def fetch_daily_candles(
        self,
        symbol: str,
        exchange: str = "NSE",
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        lookback_years: int = DEFAULT_LOOKBACK_YEARS,
    ) -> List[Dict]:
        """Fetch historical daily candle data for a symbol.

        Args:
            symbol: Trading symbol (e.g., RELIANCE).
            exchange: Exchange segment (default: NSE).
            from_date: Start date. Defaults to lookback_years ago.
            to_date: End date. Defaults to today.
            lookback_years: Years of history if from_date not specified.

        Returns:
            List of daily candle records.
        """
        client = self._auth.get_client()
        if not client:
            logger.error("Failed to get authenticated client")
            return []

        self._instruments.ensure_loaded()
        token = self._instruments.get_token(symbol, exchange)

        if not token:
            logger.error(f"Token not found for {symbol} on {exchange}")
            return []

        from_date, to_date = self._calculate_date_range(
            from_date, to_date, lookback_years
        )

        # Angel API expects datetime strings with time component
        from_str = from_date.strftime("%Y-%m-%d") + " 09:15"
        to_str = to_date.strftime("%Y-%m-%d") + " 15:30"

        # Get timezone-aware ingestion timestamp
        ingestion_ts = datetime.now(IST).isoformat()

        results = []

        historic_param = {
            "exchange": exchange,
            "symboltoken": token,
            "interval": DAILY_INTERVAL,
            "fromdate": from_str,
            "todate": to_str,
        }

        logger.info(
            f"Fetching daily candles for {symbol} ({exchange}) "
            f"from {from_date} to {to_date}..."
        )

        response = self._make_api_request_with_retry(client, historic_param)

        if response and response.get("status") and response.get("data"):
            for candle in response["data"]:
                # Parse timestamp and extract date only
                candle_ts = candle[0]  # Format: "2025-01-02T00:00:00+05:30"
                try:
                    # Extract date part from timestamp
                    candle_date = candle_ts.split("T")[0]
                except (IndexError, AttributeError):
                    candle_date = str(candle_ts)[:10]

                record = {
                    "symbol": symbol,
                    "exchange": exchange,
                    "interval": INTERVAL_LABEL,
                    "date": candle_date,
                    "open": float(candle[1]),
                    "high": float(candle[2]),
                    "low": float(candle[3]),
                    "close": float(candle[4]),
                    "volume": int(candle[5]),
                    "source": "ANGEL_SMARTAPI",
                    "ingestion_ts": ingestion_ts,
                }
                results.append(record)

            logger.info(
                f"Fetched {len(results)} daily candles for {symbol} "
                f"({from_date} to {to_date})"
            )
        else:
            error_msg = response.get("message", "Unknown error") if response else "No response"
            logger.warning(f"No historical data for {symbol}: {error_msg}")

        return results

    def save_daily_candles(
        self, data: List[Dict], symbol: str, exchange: str
    ) -> int:
        """Persist historical daily candles to append-only JSONL file.

        Args:
            data: List of daily candle records.
            symbol: Trading symbol.
            exchange: Exchange segment.

        Returns:
            Number of records written.
        """
        if not data:
            return 0

        self._ensure_directories()
        file_path = self._get_historical_file_path(symbol, exchange)

        try:
            # CRITICAL: Use append mode ('a') for append-only guarantee
            with open(file_path, "a", encoding="utf-8") as f:
                for record in data:
                    f.write(json.dumps(record) + "\n")

            logger.info(f"Appended {len(data)} daily records to {file_path}")
            return len(data)

        except IOError as exc:
            logger.error(f"Failed to save historical data to {file_path}: {exc}")
            return 0

    def fetch_and_save(
        self,
        symbol: str,
        exchange: str = "NSE",
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        lookback_years: int = DEFAULT_LOOKBACK_YEARS,
    ) -> int:
        """Convenience method to fetch and persist daily candles in one call.

        Args:
            symbol: Trading symbol.
            exchange: Exchange segment.
            from_date: Start date.
            to_date: End date.
            lookback_years: Years of history if from_date not specified.

        Returns:
            Number of records saved.
        """
        data = self.fetch_daily_candles(
            symbol, exchange, from_date, to_date, lookback_years
        )
        return self.save_daily_candles(data, symbol, exchange)

    def fetch_watchlist(
        self,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        lookback_years: int = DEFAULT_LOOKBACK_YEARS,
    ) -> Dict[str, int]:
        """Fetch historical daily candles for all watchlist symbols.

        Args:
            from_date: Start date.
            to_date: End date.
            lookback_years: Years of history if from_date not specified.

        Returns:
            Dict mapping symbol to record count.
        """
        results = {}
        symbols = self._config.symbol_watchlist
        exchange = self._config.exchanges[0] if self._config.exchanges else "NSE"

        logger.info(f"Starting historical backfill for {len(symbols)} symbols...")

        for symbol in symbols:
            count = self.fetch_and_save(
                symbol, exchange, from_date, to_date, lookback_years
            )
            results[symbol] = count

            # Small delay between symbols to avoid rate limiting
            if count > 0:
                time.sleep(0.5)

        total = sum(results.values())
        logger.info(f"Backfilled {total} total daily records for {len(symbols)} symbols")
        return results

    def get_existing_dates(self, symbol: str, exchange: str) -> set:
        """Get set of dates already present in historical file.

        Useful for deduplication before appending.

        Args:
            symbol: Trading symbol.
            exchange: Exchange segment.

        Returns:
            Set of date strings already in file.
        """
        file_path = self._get_historical_file_path(symbol, exchange)
        existing_dates = set()

        if not file_path.exists():
            return existing_dates

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        if "date" in record:
                            existing_dates.add(record["date"])
                    except json.JSONDecodeError:
                        continue
        except IOError:
            pass

        return existing_dates
