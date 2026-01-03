"""Angel One Instrument Master Manager.

This module handles downloading, caching, and querying the Angel One
instrument master list for symbol-to-token mapping.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests

from .config import config

logger = logging.getLogger(__name__)

# Angel One instrument master URL
INSTRUMENT_MASTER_URL = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"


class InstrumentMaster:
    """Manages the Angel One instrument master list.

    Downloads and caches the instrument list, providing utilities to
    map symbols to tokens and vice versa.
    """

    def __init__(self, cfg: Optional[object] = None):
        """Initialize the instrument master.

        Args:
            cfg: Configuration object. Uses default config if not provided.
        """
        self._config = cfg or config
        self._instruments: List[Dict] = []
        self._symbol_index: Dict[Tuple[str, str], Dict] = {}  # (symbol, exchange) -> instrument
        self._token_index: Dict[str, Dict] = {}  # token -> instrument
        self._cache_path = Path(self._config.instrument_master_path)
        self._cache_date: Optional[date] = None

    def _ensure_cache_dir(self) -> None:
        """Ensure the cache directory exists."""
        self._cache_path.parent.mkdir(parents=True, exist_ok=True)

    def download_master(self) -> bool:
        """Download the instrument master from Angel One.

        Returns:
            True if download successful, False otherwise.
        """
        try:
            logger.info("Downloading instrument master from Angel One...")
            response = requests.get(INSTRUMENT_MASTER_URL, timeout=60)
            response.raise_for_status()

            self._instruments = response.json()
            self._build_indices()
            self._save_cache()

            logger.info(f"Downloaded {len(self._instruments)} instruments")
            return True

        except requests.RequestException as exc:
            logger.error(f"Failed to download instrument master: {exc}")
            return False
        except json.JSONDecodeError as exc:
            logger.error(f"Failed to parse instrument master JSON: {exc}")
            return False

    def _build_indices(self) -> None:
        """Build lookup indices for fast symbol/token resolution."""
        self._symbol_index.clear()
        self._token_index.clear()

        for inst in self._instruments:
            symbol = inst.get("symbol", "")
            exchange = inst.get("exch_seg", "")
            token = inst.get("token", "")

            if symbol and exchange:
                # Store with tradingsymbol for exact match
                key = (symbol, exchange)
                self._symbol_index[key] = inst

                # Also index by name for user-friendly lookups
                name = inst.get("name", "")
                if name:
                    self._symbol_index[(name, exchange)] = inst

            if token:
                self._token_index[token] = inst

        logger.debug(
            f"Built indices: {len(self._symbol_index)} symbols, {len(self._token_index)} tokens"
        )

    def _save_cache(self) -> None:
        """Save instruments to local cache file."""
        try:
            self._ensure_cache_dir()
            cache_data = {
                "date": datetime.now().isoformat(),
                "count": len(self._instruments),
                "instruments": self._instruments,
            }
            with open(self._cache_path, "w", encoding="utf-8") as f:
                json.dump(cache_data, f)
            self._cache_date = date.today()
            logger.info(f"Saved instrument cache to {self._cache_path}")
        except IOError as exc:
            logger.warning(f"Failed to save instrument cache: {exc}")

    def load_cached(self) -> bool:
        """Load instruments from local cache.

        Returns:
            True if cache loaded successfully, False otherwise.
        """
        if not self._cache_path.exists():
            logger.info("No cached instrument master found")
            return False

        try:
            with open(self._cache_path, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            self._instruments = cache_data.get("instruments", [])
            cache_date_str = cache_data.get("date", "")

            if cache_date_str:
                self._cache_date = datetime.fromisoformat(cache_date_str).date()

            self._build_indices()
            logger.info(
                f"Loaded {len(self._instruments)} instruments from cache "
                f"(dated {self._cache_date})"
            )
            return True

        except (IOError, json.JSONDecodeError) as exc:
            logger.warning(f"Failed to load instrument cache: {exc}")
            return False

    def is_cache_stale(self) -> bool:
        """Check if cache is from a previous day.

        Returns:
            True if cache is stale or doesn't exist.
        """
        if not self._cache_date:
            return True
        return self._cache_date < date.today()

    def ensure_loaded(self) -> bool:
        """Ensure instrument master is loaded.

        Loads from cache if available and fresh, otherwise downloads.

        Returns:
            True if instruments are available, False otherwise.
        """
        if self._instruments and not self.is_cache_stale():
            return True

        if self.load_cached() and not self.is_cache_stale():
            return True

        return self.download_master()

    def get_token(self, symbol: str, exchange: str = "NSE") -> Optional[str]:
        """Get instrument token for a symbol.

        Args:
            symbol: Trading symbol (e.g., 'RELIANCE', 'RELIANCE-EQ')
            exchange: Exchange segment (NSE, BSE, NFO, etc.)

        Returns:
            Instrument token string, or None if not found.
        """
        self.ensure_loaded()

        # Try exact match first
        key = (symbol, exchange)
        inst = self._symbol_index.get(key)

        # Try with -EQ suffix for equity
        if not inst and exchange in ("NSE", "BSE") and not symbol.endswith("-EQ"):
            inst = self._symbol_index.get((f"{symbol}-EQ", exchange))

        if inst:
            return inst.get("token")

        logger.warning(f"Token not found for {symbol} on {exchange}")
        return None

    def get_symbol(self, token: str) -> Optional[Dict]:
        """Get instrument details by token.

        Args:
            token: Instrument token string.

        Returns:
            Instrument dictionary, or None if not found.
        """
        self.ensure_loaded()
        return self._token_index.get(token)

    def get_instrument(self, symbol: str, exchange: str = "NSE") -> Optional[Dict]:
        """Get full instrument details for a symbol.

        Args:
            symbol: Trading symbol.
            exchange: Exchange segment.

        Returns:
            Instrument dictionary, or None if not found.
        """
        self.ensure_loaded()

        key = (symbol, exchange)
        inst = self._symbol_index.get(key)

        if not inst and exchange in ("NSE", "BSE") and not symbol.endswith("-EQ"):
            inst = self._symbol_index.get((f"{symbol}-EQ", exchange))

        return inst

    def search_symbols(self, query: str, exchange: Optional[str] = None) -> List[Dict]:
        """Search for instruments matching a query.

        Args:
            query: Search string (partial match on symbol or name).
            exchange: Optional exchange filter.

        Returns:
            List of matching instrument dictionaries.
        """
        self.ensure_loaded()
        query_lower = query.lower()
        results = []

        for inst in self._instruments:
            if exchange and inst.get("exch_seg") != exchange:
                continue

            symbol = inst.get("symbol", "").lower()
            name = inst.get("name", "").lower()

            if query_lower in symbol or query_lower in name:
                results.append(inst)

        return results[:100]  # Limit results
