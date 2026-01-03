"""Angel One Market Data Ingestor.

This module fetches live OHLC candles and LTP snapshots from Angel One
SmartAPI and persists them to append-only files.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from .auth import AngelAuthManager
from .config import config
from .instrument_master import InstrumentMaster

logger = logging.getLogger(__name__)


class MarketDataIngestor:
    """Fetches and persists live market data from Angel One SmartAPI.

    Supports fetching:
    - OHLC candles (1m, 5m, etc.)
    - LTP (Last Traded Price) snapshots
    """

    def __init__(
        self,
        auth_manager: Optional[AngelAuthManager] = None,
        instrument_master: Optional[InstrumentMaster] = None,
        cfg: Optional[object] = None,
    ):
        """Initialize the market data ingestor.

        Args:
            auth_manager: Auth manager instance. Creates new one if not provided.
            instrument_master: Instrument master instance. Creates new one if not provided.
            cfg: Configuration object. Uses default config if not provided.
        """
        self._config = cfg or config
        self._auth = auth_manager or AngelAuthManager(self._config)
        self._instruments = instrument_master or InstrumentMaster(self._config)
        self._ohlc_path = Path(self._config.intraday_ohlc_path)
        self._ltp_path = Path(self._config.ltp_snapshots_path)

    def _ensure_directories(self) -> None:
        """Ensure output directories exist."""
        self._ohlc_path.mkdir(parents=True, exist_ok=True)
        self._ltp_path.mkdir(parents=True, exist_ok=True)

    def _get_candle_file_path(self, symbol: str, exchange: str, date_str: str) -> Path:
        """Get file path for candle data."""
        return self._ohlc_path / f"{exchange}_{symbol}_{date_str}.jsonl"

    def _get_ltp_file_path(self, date_str: str) -> Path:
        """Get file path for LTP snapshots."""
        return self._ltp_path / f"ltp_snapshot_{date_str}.jsonl"

    def fetch_candles(
        self,
        symbols: List[str],
        interval: str = "ONE_MINUTE",
        exchange: str = "NSE",
        from_time: Optional[datetime] = None,
        to_time: Optional[datetime] = None,
    ) -> List[Dict]:
        """Fetch OHLC candle data for given symbols.

        Args:
            symbols: List of trading symbols.
            interval: Candle interval (ONE_MINUTE, FIVE_MINUTE, etc.)
            exchange: Exchange segment.
            from_time: Start time. Defaults to 1 interval ago.
            to_time: End time. Defaults to now.

        Returns:
            List of candle records with metadata.
        """
        client = self._auth.get_client()
        if not client:
            logger.error("Failed to get authenticated client")
            return []

        self._instruments.ensure_loaded()

        now = datetime.now()
        if not to_time:
            to_time = now
        if not from_time:
            # Default to fetching last few candles
            from_time = to_time - timedelta(minutes=5)

        from_str = from_time.strftime("%Y-%m-%d %H:%M")
        to_str = to_time.strftime("%Y-%m-%d %H:%M")
        ingestion_ts = now.isoformat()

        results = []

        for symbol in symbols:
            token = self._instruments.get_token(symbol, exchange)
            if not token:
                logger.warning(f"Skipping {symbol}: token not found")
                continue

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
                        # Candle format: [timestamp, open, high, low, close, volume]
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
                else:
                    logger.warning(
                        f"No data for {symbol}: {response.get('message', 'Unknown error')}"
                    )

            except Exception as exc:
                logger.exception(f"Error fetching candles for {symbol}: {exc}")

        logger.info(f"Fetched {len(results)} candle records for {len(symbols)} symbols")
        return results

    def fetch_ltp(self, symbols: List[str], exchange: str = "NSE") -> List[Dict]:
        """Fetch Last Traded Price for given symbols.

        Args:
            symbols: List of trading symbols.
            exchange: Exchange segment.

        Returns:
            List of LTP records with metadata.
        """
        client = self._auth.get_client()
        if not client:
            logger.error("Failed to get authenticated client")
            return []

        self._instruments.ensure_loaded()
        now = datetime.now()
        ingestion_ts = now.isoformat()

        results = []

        for symbol in symbols:
            token = self._instruments.get_token(symbol, exchange)
            if not token:
                logger.warning(f"Skipping {symbol}: token not found")
                continue

            try:
                ltp_param = {
                    "exchange": exchange,
                    "tradingsymbol": symbol,
                    "symboltoken": token,
                }

                response = client.ltpData(exchange, symbol, token)

                if response.get("status") and response.get("data"):
                    data = response["data"]
                    record = {
                        "symbol": symbol,
                        "exchange": exchange,
                        "ltp": float(data.get("ltp", 0)),
                        "open": float(data.get("open", 0)),
                        "high": float(data.get("high", 0)),
                        "low": float(data.get("low", 0)),
                        "close": float(data.get("close", 0)),
                        "timestamp": now.isoformat(),
                        "source": "ANGEL_SMARTAPI",
                        "ingestion_ts": ingestion_ts,
                    }
                    results.append(record)
                else:
                    logger.warning(
                        f"No LTP data for {symbol}: {response.get('message', 'Unknown error')}"
                    )

            except Exception as exc:
                logger.exception(f"Error fetching LTP for {symbol}: {exc}")

        logger.info(f"Fetched LTP for {len(results)} symbols")
        return results

    def persist_candles(self, candles: List[Dict]) -> int:
        """Persist candle data to append-only JSON Lines files.

        Args:
            candles: List of candle records.

        Returns:
            Number of records written.
        """
        if not candles:
            return 0

        self._ensure_directories()
        date_str = datetime.now().strftime("%Y-%m-%d")
        written = 0

        # Group by symbol and exchange
        grouped: Dict[str, List[Dict]] = {}
        for candle in candles:
            key = f"{candle['exchange']}_{candle['symbol']}"
            grouped.setdefault(key, []).append(candle)

        for key, records in grouped.items():
            parts = key.split("_", 1)
            exchange, symbol = parts[0], parts[1]
            file_path = self._get_candle_file_path(symbol, exchange, date_str)

            try:
                with open(file_path, "a", encoding="utf-8") as f:
                    for record in records:
                        f.write(json.dumps(record) + "\n")
                        written += 1
            except IOError as exc:
                logger.error(f"Failed to write candles to {file_path}: {exc}")

        logger.info(f"Persisted {written} candle records")
        return written

    def persist_ltp(self, ltp_records: List[Dict]) -> int:
        """Persist LTP snapshots to append-only JSON Lines file.

        Args:
            ltp_records: List of LTP records.

        Returns:
            Number of records written.
        """
        if not ltp_records:
            return 0

        self._ensure_directories()
        date_str = datetime.now().strftime("%Y-%m-%d")
        file_path = self._get_ltp_file_path(date_str)

        try:
            with open(file_path, "a", encoding="utf-8") as f:
                for record in ltp_records:
                    f.write(json.dumps(record) + "\n")
            logger.info(f"Persisted {len(ltp_records)} LTP records to {file_path}")
            return len(ltp_records)
        except IOError as exc:
            logger.error(f"Failed to write LTP to {file_path}: {exc}")
            return 0

    def ingest_watchlist(self, interval: Optional[str] = None) -> Dict[str, int]:
        """Fetch and persist data for configured watchlist.

        Args:
            interval: Candle interval. Uses config default if not specified.

        Returns:
            Dict with counts of ingested candles and LTP records.
        """
        interval = interval or self._config.default_candle_interval
        symbols = self._config.symbol_watchlist
        exchange = self._config.exchanges[0] if self._config.exchanges else "NSE"

        # Fetch and persist candles
        candles = self.fetch_candles(symbols, interval, exchange)
        candle_count = self.persist_candles(candles)

        # Fetch and persist LTP
        ltp_records = self.fetch_ltp(symbols, exchange)
        ltp_count = self.persist_ltp(ltp_records)

        return {"candles": candle_count, "ltp": ltp_count}
