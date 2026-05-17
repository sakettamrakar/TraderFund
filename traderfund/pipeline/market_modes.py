"""
Market Modes Configuration (RR-B.2)

Defines the supported market modes, their required inputs, fixture behavior,
and live-only prerequisites. Every pipeline stage and validator must resolve
its behavior through this module rather than ad-hoc string checks.

Supported modes:
    fixture  — Canonical test mode. Uses committed fixture data, no credentials needed.
    US       — US market mode.  Requires Alpha Vantage API key.
    INDIA    — India market mode.  Requires Angel One / Zerodha credentials.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class MarketMode(str, Enum):
    """Canonical market modes recognised by the pipeline."""
    FIXTURE = "fixture"
    US = "US"
    INDIA = "INDIA"

    @classmethod
    def from_str(cls, value: str) -> "MarketMode":
        """Case-insensitive lookup with an actionable error message."""
        upper = value.upper() if value != "fixture" else "FIXTURE"
        try:
            return cls(upper if upper != "FIXTURE" else "fixture")
        except ValueError:
            allowed = ", ".join(m.value for m in cls)
            raise ValueError(
                f"Unknown market mode '{value}'. Allowed modes: {allowed}"
            )


@dataclass(frozen=True)
class MarketModeSpec:
    """Declares what a market mode needs and where its artifacts live."""
    mode: MarketMode
    description: str
    requires_credentials: bool
    credential_env_vars: List[str] = field(default_factory=list)
    raw_data_pattern: str = ""
    processed_data_pattern: str = ""
    us_daily_pattern: str = ""
    is_fixture: bool = False
    notes: str = ""


# ── Registry ─────────────────────────────────────────────────────────────────

MARKET_MODE_SPECS: Dict[MarketMode, MarketModeSpec] = {
    MarketMode.FIXTURE: MarketModeSpec(
        mode=MarketMode.FIXTURE,
        description="Canonical test mode using committed fixture data",
        requires_credentials=False,
        raw_data_pattern="data/fixtures/raw/*.jsonl",
        processed_data_pattern="data/fixtures/processed/*.parquet",
        us_daily_pattern="data/fixtures/us/*.json",
        is_fixture=True,
        notes="Safe for CI, local dev, and dry-run testing.",
    ),
    MarketMode.US: MarketModeSpec(
        mode=MarketMode.US,
        description="US market — Alpha Vantage REST polling",
        requires_credentials=True,
        credential_env_vars=["ALPHA_VANTAGE_API_KEY"],
        raw_data_pattern="data/raw/us/*/*_daily.json",
        processed_data_pattern="data/processed/candles/us/*.parquet",
        us_daily_pattern="data/raw/us/*/*_daily.json",
        notes="Requires ALPHA_VANTAGE_API_KEY in .env",
    ),
    MarketMode.INDIA: MarketModeSpec(
        mode=MarketMode.INDIA,
        description="India market — Angel One SmartAPI WebSocket + REST",
        requires_credentials=True,
        credential_env_vars=[
            "ANGEL_API_KEY",
            "ANGEL_CLIENT_ID",
            "ANGEL_PASSWORD",
            "ANGEL_TOTP_SECRET",
        ],
        raw_data_pattern="data/raw/api_based/angel/intraday_ohlc/*.jsonl",
        processed_data_pattern="data/processed/candles/intraday/*.parquet",
        notes="Requires Angel One credentials in .env",
    ),
}


def get_mode_spec(mode: MarketMode | str) -> MarketModeSpec:
    """Return the spec for a given mode, accepting both enum and string."""
    if isinstance(mode, str):
        mode = MarketMode.from_str(mode)
    spec = MARKET_MODE_SPECS.get(mode)
    if spec is None:
        raise ValueError(f"No spec registered for market mode '{mode}'")
    return spec


def validate_credentials(mode: MarketMode | str) -> List[str]:
    """
    Return a list of missing credential env vars for the given mode.
    Empty list means all required credentials are present.
    """
    import os
    spec = get_mode_spec(mode)
    if not spec.requires_credentials:
        return []
    return [var for var in spec.credential_env_vars if not os.environ.get(var)]
