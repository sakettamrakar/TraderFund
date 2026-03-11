from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from .config import PortfolioIntelligenceConfig


def _json_default(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


class PortfolioArtifactStore:
    def __init__(self, config: PortfolioIntelligenceConfig) -> None:
        self.config = config
        self.config.ensure_directories()

    def load_registry(self) -> Dict[str, Any]:
        if not self.config.registry_path.exists():
            return {"portfolios": []}
        with open(self.config.registry_path, "r", encoding="utf-8") as handle:
            return json.load(handle)

    def update_registry(self, entry: Dict[str, Any]) -> None:
        registry = self.load_registry()
        portfolios = [item for item in registry.get("portfolios", []) if item.get("portfolio_id") != entry.get("portfolio_id")]
        portfolios.append(entry)
        registry["portfolios"] = sorted(portfolios, key=lambda item: item["portfolio_id"])
        self._write_json(self.config.registry_path, registry)

    def write_raw_snapshot(self, market: str, portfolio_id: str, payload: Dict[str, Any]) -> Path:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = self.config.raw_dir / market / portfolio_id / f"{stamp}.json"
        self._write_json(path, payload)
        self._write_json(self.config.raw_dir / market / portfolio_id / "latest.json", payload)
        return path

    def write_normalized(self, market: str, portfolio_id: str, payload: Dict[str, Any]) -> Path:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = self.config.normalized_dir / market / portfolio_id / f"{stamp}.json"
        self._write_json(path, payload)
        self._write_json(self.config.normalized_dir / market / portfolio_id / "latest.json", payload)
        return path

    def write_analytics(self, market: str, portfolio_id: str, payload: Dict[str, Any]) -> Path:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = self.config.analytics_dir / market / portfolio_id / f"{stamp}.json"
        self._write_json(path, payload)
        self._write_json(self.config.analytics_dir / market / portfolio_id / "latest.json", payload)
        self._write_json(self.config.base_dir / "history" / market / portfolio_id / f"{stamp}.json", payload)
        return path

    def load_latest_analytics(self, market: str, portfolio_id: str) -> Dict[str, Any]:
        return self._read_json(self.config.analytics_dir / market / portfolio_id / "latest.json")

    def list_market_analytics(self, market: str) -> List[Dict[str, Any]]:
        market_dir = self.config.analytics_dir / market
        if not market_dir.exists():
            return []
        results: List[Dict[str, Any]] = []
        for child in sorted([item for item in market_dir.iterdir() if item.is_dir()], key=lambda item: item.name):
            payload = self.load_latest_analytics(market, child.name)
            if payload:
                results.append(payload)
        return results

    def _read_json(self, path: Path) -> Dict[str, Any]:
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)

    def _write_json(self, path: Path, payload: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, default=_json_default)
