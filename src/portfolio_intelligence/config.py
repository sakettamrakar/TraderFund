from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _first_env(*names: str) -> str:
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return value
    return ""


@dataclass(frozen=True)
class BrokerCredentialSet:
    api_key: str = ""
    api_secret: str = ""
    access_token: str = ""
    request_token: str = ""
    redirect_url: str = ""

    def missing(self) -> list[str]:
        missing: list[str] = []
        if not self.api_key:
            missing.append("KITE_API_KEY")
        if not self.access_token and not self.request_token:
            missing.append("KITE_ACCESS_TOKEN or KITE_REQUEST_TOKEN")
        if self.request_token and not self.api_secret:
            missing.append("KITE_API_SECRET")
        return missing

    def has_auth_material(self) -> bool:
        return bool(self.api_key and (self.access_token or (self.request_token and self.api_secret)))


@dataclass(frozen=True)
class PortfolioIntelligenceConfig:
    truth_epoch: str = "TRUTH_EPOCH_2026-03-06_01"
    data_mode: str = "REAL_ONLY"
    execution_mode: str = "REAL_RUN"
    base_dir: Path = PROJECT_ROOT / "data" / "portfolio_intelligence"
    kite_mcp_url: str = field(
        default_factory=lambda: _first_env("KITE_MCP_URL") or "https://mcp.kite.trade/mcp"
    )
    kite_mcp_protocol_version: str = field(
        default_factory=lambda: _first_env("KITE_MCP_PROTOCOL_VERSION") or "2025-03-26"
    )
    refresh_interval_seconds: int = field(
        default_factory=lambda: int(os.getenv("PORTFOLIO_TRACKER_REFRESH_SECONDS", "900"))
    )
    request_timeout_seconds: int = field(
        default_factory=lambda: int(os.getenv("PORTFOLIO_REQUEST_TIMEOUT_SECONDS", "20"))
    )
    max_requests_per_second: float = field(
        default_factory=lambda: float(os.getenv("PORTFOLIO_BROKER_RPS", "2.0"))
    )
    usd_inr_manual_rate: float = field(
        default_factory=lambda: float(os.getenv("PORTFOLIO_USDINR_RATE", "0"))
    )
    alpha_vantage_api_key: str = field(
        default_factory=lambda: _first_env("ALPHAVANTAGE_API_KEY", "ALPHA_VANTAGE_API_KEY")
    )
    trader_news_api_url: str = field(
        default_factory=lambda: _first_env("TRADER_NEWS_API_URL")
    )
    trader_news_lookback_hours: int = field(
        default_factory=lambda: int(os.getenv("TRADER_NEWS_LOOKBACK_HOURS", "72"))
    )

    @property
    def raw_dir(self) -> Path:
        return self.base_dir / "imports"

    @property
    def normalized_dir(self) -> Path:
        return self.base_dir / "normalized"

    @property
    def analytics_dir(self) -> Path:
        return self.base_dir / "analytics"

    @property
    def registry_path(self) -> Path:
        return self.base_dir / "registry" / "portfolio_registry.json"

    @property
    def fund_metadata_dir(self) -> Path:
        return self.base_dir / "fund_metadata"

    @property
    def benchmark_metadata_dir(self) -> Path:
        return self.base_dir / "benchmark_metadata"

    def ensure_directories(self) -> None:
        for path in (
            self.base_dir,
            self.raw_dir,
            self.normalized_dir,
            self.analytics_dir,
            self.fund_metadata_dir,
            self.benchmark_metadata_dir,
            self.base_dir / "history",
            self.base_dir / "registry",
        ):
            path.mkdir(parents=True, exist_ok=True)

    def zerodha_credentials(self) -> BrokerCredentialSet:
        return BrokerCredentialSet(
            api_key=_first_env("KITE_API_KEY", "ZERODHA_API_KEY"),
            api_secret=_first_env("KITE_API_SECRET", "ZERODHA_API_SECRET"),
            access_token=_first_env("KITE_ACCESS_TOKEN", "ZERODHA_ACCESS_TOKEN"),
            request_token=_first_env("KITE_REQUEST_TOKEN", "ZERODHA_REQUEST_TOKEN"),
            redirect_url=_first_env("KITE_REDIRECT_URL", "ZERODHA_REDIRECT_URL"),
        )

    def credential_presence(self) -> Dict[str, str]:
        creds = self.zerodha_credentials()
        return {
            "KITE_MCP_URL": "SET" if self.kite_mcp_url else "MISSING",
            "KITE_API_KEY": "SET" if creds.api_key else "MISSING",
            "KITE_API_SECRET": "SET" if creds.api_secret else "MISSING",
            "KITE_ACCESS_TOKEN": "SET" if creds.access_token else "MISSING",
            "KITE_REQUEST_TOKEN": "SET" if creds.request_token else "MISSING",
            "KITE_REDIRECT_URL": "SET" if creds.redirect_url else "MISSING",
        }
