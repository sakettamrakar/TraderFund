"""Angel One Historical Data Ingestor.

This module provides utilities for backfilling historical candle data
from Angel One SmartAPI.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import Dict, List, Optional

from .auth import AngelAuthManager
from .config import config
from .instrument_master import InstrumentMaster

logger = logging.getLogger(__name__)


class HistoricalDataIngestor:
    """Backfill utility for fetching historical candle data.

    API constraints:
    - 1-minute data: max 30 days history
    - 3-minute and above: max 2000 days history
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
        self._auth = auth_manager or AngelAuthManager(self._config)
        self._instruments = instrument_master or InstrumentMaster(self._config)
        self._historical_path = Path(self._config.historical_path)

    def _ensure_directories(self) -> None:
        """Ensure output directories exist."""
        self._historical_path.mkdir(parents=True, exist_ok=True)

    def _get_max_days(self, interval: str) -> int:
        """Get maximum history days for given interval.

        Args:
            interval: Candle interval string.

        Returns:
            Maximum days of historical data available.
        """
        if interval == "ONE_MINUTE":
            return self._config.max_1m_history_days
        return self._config.max_5m_history_days

    def _get_historical_file_path(
        self, symbol: str, exchange: str, interval: str
    ) -> Path:
        """Get file path for historical data."""
        return self._historical_path / f"{exchange}_{symbol}_{interval}.jsonl"

    def backfill(
        self,
        symbol: str,
        exchange: str = "NSE",
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        interval: str = "ONE_MINUTE",
    ) -> List[Dict]:
        """Fetch historical candle data for a symbol.

        Args:
            symbol: Trading symbol.
            exchange: Exchange segment.
            from_date: Start date. Defaults to max allowed history.
            to_date: End date. Defaults to today.
            interval: Candle interval.

        Returns:
            List of historical candle records.
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

        today = date.today()
        max_days = self._get_max_days(interval)

        if not to_date:
            to_date = today
        if not from_date:
            from_date = today - timedelta(days=max_days)

        # Validate date range
        if (to_date - from_date).days > max_days:
            logger.warning(
                f"Date range exceeds max {max_days} days for {interval}. "
                f"Adjusting from_date."
            )
            from_date = to_date - timedelta(days=max_days)

        from_str = from_date.strftime("%Y-%m-%d") + " 09:15"
        to_str = to_date.strftime("%Y-%m-%d") + " 15:30"
        ingestion_ts = datetime.now().isoformat()

        results = []

        try:
            historic_param = {
                "exchange": exchange,
                "symboltoken": token,
                "interval": interval,
                "fromdate": from_str,
                "todate": to_str,
            }

            response = client.getCandleData(historic_param)

            if response.get("status") and response.get("data"):
                for candle in response["data"]:
                    record = {
                        "symbol": symbol,
                        "exchange": exchange,
                        "interval": interval,
                        "timestamp": candle[0],
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
                    f"Fetched {len(results)} historical candles for {symbol} "
                    f"({from_date} to {to_date})"
                )
            else:
                logger.warning(
                    f"No historical data for {symbol}: "
                    f"{response.get('message', 'Unknown error')}"
                )

        except Exception as exc:
            logger.exception(f"Error fetching historical data for {symbol}: {exc}")

        return results

    def save_historical(self, data: List[Dict], symbol: str, exchange: str, interval: str) -> int:
        """Persist historical data to file.

        Args:
            data: List of candle records.
            symbol: Trading symbol.
            exchange: Exchange segment.
            interval: Candle interval.

        Returns:
            Number of records written.
        """
        if not data:
            return 0

        self._ensure_directories()
        file_path = self._get_historical_file_path(symbol, exchange, interval)

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                for record in data:
                    f.write(json.dumps(record) + "\n")

            logger.info(f"Saved {len(data)} historical records to {file_path}")
            return len(data)

        except IOError as exc:
            logger.error(f"Failed to save historical data to {file_path}: {exc}")
            return 0

    def backfill_and_save(
        self,
        symbol: str,
        exchange: str = "NSE",
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        interval: str = "ONE_MINUTE",
    ) -> int:
        """Convenience method to backfill and persist in one call.

        Args:
            symbol: Trading symbol.
            exchange: Exchange segment.
            from_date: Start date.
            to_date: End date.
            interval: Candle interval.

        Returns:
            Number of records saved.
        """
        data = self.backfill(symbol, exchange, from_date, to_date, interval)
        return self.save_historical(data, symbol, exchange, interval)

    def backfill_watchlist(
        self,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        interval: str = "ONE_MINUTE",
    ) -> Dict[str, int]:
        """Backfill historical data for all watchlist symbols.

        Args:
            from_date: Start date.
            to_date: End date.
            interval: Candle interval.

        Returns:
            Dict mapping symbol to record count.
        """
        results = {}
        symbols = self._config.symbol_watchlist
        exchange = self._config.exchanges[0] if self._config.exchanges else "NSE"

        for symbol in symbols:
            count = self.backfill_and_save(symbol, exchange, from_date, to_date, interval)
            results[symbol] = count

        total = sum(results.values())
        logger.info(f"Backfilled {total} total records for {len(symbols)} symbols")
        return results
