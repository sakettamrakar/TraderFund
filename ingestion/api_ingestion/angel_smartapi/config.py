"""Angel One SmartAPI Configuration.

This module manages API credentials and configurable parameters for
the Angel SmartAPI ingestion pipeline.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List

from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()


@dataclass
class AngelConfig:
    """Configuration for Angel One SmartAPI ingestion.

    Credentials are loaded from environment variables:
    - ANGEL_API_KEY: API key from Angel One developer portal
    - ANGEL_CLIENT_ID: Your Angel One client ID
    - ANGEL_PIN: Your trading PIN
    - ANGEL_TOTP_SECRET: TOTP secret for 2FA (base32 encoded)
    """

    # API Credentials (loaded from environment)
    api_key: str = field(default_factory=lambda: os.getenv("ANGEL_API_KEY", ""))
    client_id: str = field(default_factory=lambda: os.getenv("ANGEL_CLIENT_ID", ""))
    pin: str = field(default_factory=lambda: os.getenv("ANGEL_PIN", ""))
    totp_secret: str = field(default_factory=lambda: os.getenv("ANGEL_TOTP_SECRET", ""))

    # Polling Configuration
    polling_interval_seconds: int = 60

    # Candle Interval Configuration
    # Valid values: ONE_MINUTE, THREE_MINUTE, FIVE_MINUTE, TEN_MINUTE,
    #               FIFTEEN_MINUTE, THIRTY_MINUTE, ONE_HOUR, ONE_DAY
    default_candle_interval: str = "ONE_MINUTE"

    # Exchanges to fetch data from
    exchanges: List[str] = field(default_factory=lambda: ["NSE", "BSE", "NFO"])

    # Symbol watchlist - symbols to track for live data
    symbol_watchlist: List[str] = field(
        default_factory=lambda: [
            "RELIANCE",
            "TCS",
            "INFY",
            "HDFCBANK",
            "ICICIBANK",
            "SBIN",
            "BHARTIARTL",
            "ITC",
            "KOTAKBANK",
            "LT",
        ]
    )

    # Data output paths
    base_data_path: str = "data/raw/api_based/angel"
    intraday_ohlc_path: str = "data/raw/api_based/angel/intraday_ohlc"
    ltp_snapshots_path: str = "data/raw/api_based/angel/ltp_snapshots"
    historical_path: str = "data/raw/api_based/angel/historical"
    instrument_master_path: str = "data/raw/api_based/angel/instrument_master.json"

    # API constraints
    max_1m_history_days: int = 30  # 1-minute data limited to 30 days
    max_5m_history_days: int = 2000  # 5-minute+ data up to 2000 days

    def validate(self) -> bool:
        """Check if all required credentials are present."""
        return all([self.api_key, self.client_id, self.pin, self.totp_secret])

    def get_missing_credentials(self) -> List[str]:
        """Return list of missing credential names."""
        missing = []
        if not self.api_key:
            missing.append("ANGEL_API_KEY")
        if not self.client_id:
            missing.append("ANGEL_CLIENT_ID")
        if not self.pin:
            missing.append("ANGEL_PIN")
        if not self.totp_secret:
            missing.append("ANGEL_TOTP_SECRET")
        return missing


# Default configuration instance
config = AngelConfig()
