from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.portfolio_intelligence.config import PortfolioIntelligenceConfig
from src.portfolio_intelligence.enrichment import _fetch_alpha_vantage_etf_profile, _load_curated_fund_benchmark_map


def main() -> int:
    config = PortfolioIntelligenceConfig()
    market = "INDIA"
    mappings = _load_curated_fund_benchmark_map(market)
    if not mappings:
        print("No curated fund benchmark mappings found.")
        return 1

    config.ensure_directories()
    seeded_funds = 0
    seeded_benchmarks = 0

    for ticker, mapping in sorted(mappings.items()):
        fund_path = config.fund_metadata_dir / market / f"{ticker}.json"
        fund_path.parent.mkdir(parents=True, exist_ok=True)
        fund_payload = {
            "ticker": ticker,
            "benchmark_reference": mapping.get("benchmark_reference"),
            "benchmark_provider": mapping.get("benchmark_provider"),
            "benchmark_proxy_symbol": mapping.get("benchmark_proxy_symbol"),
            "underlying_holdings": [],
            "status": "SEEDED_MAPPING",
            "notes": mapping.get("notes"),
            "metadata_source": str((PROJECT_ROOT / "data" / "portfolio_intelligence" / "reference" / "fund_benchmark_mappings.json").relative_to(PROJECT_ROOT)),
        }
        fund_path.write_text(json.dumps(fund_payload, indent=2), encoding="utf-8")
        seeded_funds += 1

        benchmark_reference = mapping.get("benchmark_reference")
        benchmark_proxy_symbol = mapping.get("benchmark_proxy_symbol")
        if not benchmark_reference:
            continue

        benchmark_key = _slugify(benchmark_reference)
        benchmark_path = config.benchmark_metadata_dir / market / f"{benchmark_key}.json"
        benchmark_path.parent.mkdir(parents=True, exist_ok=True)

        benchmark_payload = {
            "benchmark_reference": benchmark_reference,
            "provider": mapping.get("benchmark_provider"),
            "provider_symbol": benchmark_proxy_symbol,
            "underlying_holdings": [],
            "status": "UNRESOLVED",
            "notes": mapping.get("notes"),
        }

        if benchmark_proxy_symbol and config.alpha_vantage_api_key:
            provider_payload = _fetch_alpha_vantage_etf_profile(benchmark_proxy_symbol, config.alpha_vantage_api_key)
            provider_holdings = provider_payload.get("underlying_holdings", [])
            if provider_holdings:
                benchmark_payload = {
                    "benchmark_reference": benchmark_reference,
                    "provider": provider_payload.get("provider", mapping.get("benchmark_provider")),
                    "provider_symbol": benchmark_proxy_symbol,
                    "underlying_holdings": provider_holdings,
                    "status": "BENCHMARK_LOOKTHROUGH_OK",
                    "raw": provider_payload.get("raw", {}),
                }
        benchmark_path.write_text(json.dumps(benchmark_payload, indent=2), encoding="utf-8")
        seeded_benchmarks += 1

    print(json.dumps({
        "market": market,
        "seeded_fund_metadata": seeded_funds,
        "seeded_benchmark_metadata": seeded_benchmarks,
        "fund_metadata_dir": str(config.fund_metadata_dir),
        "benchmark_metadata_dir": str(config.benchmark_metadata_dir),
    }, indent=2))
    return 0


def _slugify(value: str) -> str:
    return "_".join("".join(ch if ch.isalnum() else " " for ch in value.upper()).split())


if __name__ == "__main__":
    raise SystemExit(main())
