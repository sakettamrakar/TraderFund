from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Tuple

import pandas as pd
import requests

from .config import PROJECT_ROOT, PortfolioIntelligenceConfig
from .normalization import INDIA_SECTOR_MAP, US_SECTOR_MAP


def enrich_portfolio(
    normalized_payload: Dict[str, Any],
    *,
    config: PortfolioIntelligenceConfig,
) -> Dict[str, Any]:
    market = normalized_payload["market"]
    macro_context = _load_latest_context(market, "macro_context.json")
    factor_context = _load_latest_context(market, "factor_context.json")
    fund_metadata_catalog = _load_fund_metadata_catalog(market)
    curated_benchmark_map = _load_curated_fund_benchmark_map(market)

    enriched_holdings: List[Dict[str, Any]] = []
    for holding in normalized_payload.get("holdings", []):
        price_frame, price_provenance = _load_price_history(holding["ticker"], market)
        pe_ratio = _lookup_india_pe(holding["ticker"]) if market == "INDIA" else None
        technicals = _compute_technicals(price_frame)
        exposures = _compute_factor_exposure(technicals, pe_ratio, holding["sector"], factor_context)
        coverage = _coverage_status(pe_ratio, technicals)

        enriched = dict(holding)
        enriched["fundamentals"] = {
            "pe_ratio": pe_ratio,
            "earnings_growth": None,
            "revenue_growth": None,
            "debt_ratio": None,
            "roe": None,
            "margins": None,
        }
        enriched["technicals"] = technicals
        enriched["sentiment"] = {
            "earnings_event": None,
            "news_catalysts": [],
            "analyst_sentiment": None,
            "coverage_status": "UNAVAILABLE",
        }
        enriched["macro_context"] = {
            "summary": macro_context.get("summary_narrative"),
            "risk": macro_context.get("risk", {}),
            "regime_hint": _infer_regime_hint(macro_context, factor_context),
        }
        enriched["factor_exposure"] = exposures
        enriched["enrichment"] = {
            "coverage_status": coverage,
            "price_history_points": int(len(price_frame)),
            "price_provenance": price_provenance,
            "macro_source": _context_source(market, "macro_context.json"),
            "factor_source": _context_source(market, "factor_context.json"),
        }
        enriched_holdings.append(enriched)

    enriched_mutual_funds: List[Dict[str, Any]] = []
    for fund in normalized_payload.get("mutual_fund_holdings", []):
        enriched_mutual_funds.append(
            _enrich_mutual_fund_holding(
                fund,
                market=market,
                factor_context=factor_context,
                config=config,
                fund_metadata_catalog=fund_metadata_catalog,
                curated_benchmark_map=curated_benchmark_map,
            )
        )

    payload = dict(normalized_payload)
    payload["holdings"] = enriched_holdings
    payload["mutual_fund_holdings"] = enriched_mutual_funds
    payload["macro_context"] = macro_context
    payload["factor_context"] = factor_context
    payload["fund_metadata_summary"] = {
        "fund_count": len(enriched_mutual_funds),
        "real_lookthrough_available": sum(1 for item in enriched_mutual_funds if item.get("lookthrough_mode") == "UNDERLYING_DISCLOSURE"),
        "benchmark_linked": sum(1 for item in enriched_mutual_funds if item.get("lookthrough_mode") == "BENCHMARK_COMPOSITION"),
        "stagnation_count": sum(1 for item in enriched_mutual_funds if item.get("lookthrough_status") == "REAL_LOOKTHROUGH_UNAVAILABLE"),
    }
    return payload


def _enrich_mutual_fund_holding(
    fund: Dict[str, Any],
    *,
    market: str,
    factor_context: Dict[str, Any],
    config: PortfolioIntelligenceConfig,
    fund_metadata_catalog: Dict[str, Dict[str, Any]],
    curated_benchmark_map: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    enriched = dict(fund)
    ticker = str(fund.get("ticker", "")).upper()
    metadata = {**fund_metadata_catalog.get(ticker, {}), **curated_benchmark_map.get(ticker, {})}
    benchmark_reference = metadata.get("benchmark_reference") or fund.get("benchmark_reference") or _parse_benchmark_reference(str(fund.get("security_name") or fund.get("ticker") or ""))
    security_type = metadata.get("security_type") or _infer_security_type(str(fund.get("security_name") or fund.get("ticker") or ""))
    benchmark_provider = metadata.get("benchmark_provider") or _benchmark_provider(benchmark_reference)
    underlying_holdings, lookthrough_mode, provenance = _resolve_real_lookthrough(
        fund,
        market=market,
        benchmark_reference=benchmark_reference,
        benchmark_proxy_symbol=metadata.get("benchmark_proxy_symbol"),
        config=config,
    )
    underlying_holdings = _materialize_underlying_holdings(underlying_holdings, market=market, factor_context=factor_context)
    sector, industry = _infer_fund_sector_industry(str(fund.get("security_name") or fund.get("ticker") or ""), benchmark_reference)
    factor_profile = _aggregate_underlying_factor_profile(underlying_holdings, factor_context, sector)

    enriched["security_type"] = security_type
    enriched["fund_family"] = metadata.get("fund_family")
    enriched["benchmark_reference"] = benchmark_reference
    enriched["benchmark_provider"] = benchmark_provider
    enriched["benchmark_proxy_symbol"] = metadata.get("benchmark_proxy_symbol")
    enriched["underlying_holdings"] = underlying_holdings
    enriched["lookthrough_mode"] = lookthrough_mode
    enriched["lookthrough_status"] = provenance["status"]
    enriched["lookthrough_provenance"] = provenance
    enriched["sector"] = sector
    enriched["industry"] = industry
    enriched["factor_exposure"] = factor_profile
    enriched["enrichment"] = {
        "coverage_status": "REAL_LOOKTHROUGH" if underlying_holdings else "PARTIAL",
        "metadata_source": metadata.get("metadata_source") or provenance.get("metadata_source") or "UNAVAILABLE",
        "underlying_count": len(underlying_holdings),
        "lookthrough_mode": lookthrough_mode,
    }
    trace = dict(enriched.get("trace") or {})
    trace["fund_metadata_source"] = metadata.get("metadata_source") or provenance.get("metadata_source") or "UNAVAILABLE"
    trace["benchmark_reference"] = benchmark_reference
    trace["lookthrough_mode"] = lookthrough_mode
    trace["lookthrough_status"] = provenance["status"]
    enriched["trace"] = trace
    return enriched


def _load_latest_context(market: str, filename: str) -> Dict[str, Any]:
    ticks_root = PROJECT_ROOT / "docs" / "evolution" / "ticks"
    if not ticks_root.exists():
        return {}
    tick_dirs = sorted([item for item in ticks_root.iterdir() if item.is_dir()], key=lambda item: item.name, reverse=True)
    for tick_dir in tick_dirs:
        path = tick_dir / market / filename
        if path.exists():
            with open(path, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
            if filename == "factor_context.json":
                return payload.get("factor_context", {})
            return payload
    return {}


def _context_source(market: str, filename: str) -> str:
    ticks_root = PROJECT_ROOT / "docs" / "evolution" / "ticks"
    if not ticks_root.exists():
        return "UNAVAILABLE"
    tick_dirs = sorted([item for item in ticks_root.iterdir() if item.is_dir()], key=lambda item: item.name, reverse=True)
    for tick_dir in tick_dirs:
        path = tick_dir / market / filename
        if path.exists():
            return str(path.relative_to(PROJECT_ROOT))
    return "UNAVAILABLE"


def _load_price_history(symbol: str, market: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    if market == "US":
        path = PROJECT_ROOT / "data" / "analytics" / "us" / "prices" / "daily" / f"{symbol.upper()}.parquet"
        if path.exists():
            frame = pd.read_parquet(path)
            frame = frame.rename(columns=str.lower)
            return frame, {"source": str(path.relative_to(PROJECT_ROOT)), "stale": False}
        return pd.DataFrame(), {"source": "UNAVAILABLE", "stale": True}

    path = PROJECT_ROOT / "data" / "raw" / "api_based" / "angel" / "historical" / f"NSE_{symbol.upper()}_1d.jsonl"
    if not path.exists():
        return pd.DataFrame(), {"source": "UNAVAILABLE", "stale": True}
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    frame = pd.DataFrame(rows)
    frame = frame.rename(columns=str.lower)
    return frame, {"source": str(path.relative_to(PROJECT_ROOT)), "stale": False}


def _lookup_india_pe(symbol: str) -> float | None:
    path = PROJECT_ROOT / "data" / "input" / "daily" / "Equities" / "PE_260625.csv"
    if not path.exists():
        return None
    table = pd.read_csv(path)
    row = table.loc[table["SYMBOL"].astype(str).str.upper() == symbol.upper()]
    if row.empty:
        return None
    try:
        return float(row.iloc[0]["ADJUSTED P/E"])
    except Exception:
        return None


def _compute_technicals(frame: pd.DataFrame) -> Dict[str, Any]:
    if frame.empty or "close" not in frame:
        return {
            "trend_regime": "UNAVAILABLE",
            "momentum_score": None,
            "volatility_regime": "UNAVAILABLE",
            "support": None,
            "resistance": None,
            "return_20d": None,
        }

    closes = frame["close"].astype(float)
    latest = float(closes.iloc[-1])
    sma20 = float(closes.tail(20).mean()) if len(closes) >= 20 else float(closes.mean())
    sma50 = float(closes.tail(50).mean()) if len(closes) >= 50 else float(closes.mean())
    returns = closes.pct_change().dropna()
    momentum_20d = float(closes.iloc[-1] / closes.iloc[-21] - 1.0) if len(closes) > 21 else float(returns.tail(5).mean()) if not returns.empty else 0.0
    volatility = float(returns.tail(20).std() * (252 ** 0.5)) if len(returns) >= 5 else 0.0
    trend = "BULLISH" if latest >= sma20 >= sma50 else "BEARISH" if latest <= sma20 <= sma50 else "TRANSITION"
    vol_regime = "HIGH" if volatility >= 0.35 else "MEDIUM" if volatility >= 0.2 else "LOW"
    support = float(closes.tail(20).min())
    resistance = float(closes.tail(20).max())
    return {
        "trend_regime": trend,
        "momentum_score": round(max(min(momentum_20d * 5 + 0.5, 1.0), 0.0), 4),
        "volatility_regime": vol_regime,
        "support": round(support, 4),
        "resistance": round(resistance, 4),
        "return_20d": round(momentum_20d, 4),
        "annualized_volatility": round(volatility, 4),
    }


def _compute_factor_exposure(
    technicals: Dict[str, Any],
    pe_ratio: float | None,
    sector: str,
    factor_context: Dict[str, Any],
) -> Dict[str, Any]:
    momentum = technicals["momentum_score"] if technicals.get("momentum_score") is not None else 0.5
    value = max(min((30.0 - pe_ratio) / 30.0, 1.0), 0.0) if pe_ratio else 0.5
    quality = 0.65 if sector in {"Information Technology", "Financials"} else 0.5
    growth = 0.7 if technicals.get("trend_regime") == "BULLISH" else 0.45
    macro_sensitivity = 0.8 if sector in {"Energy", "Financials", "Industrials"} else 0.5
    dominant_factor = ((factor_context.get("factors") or {}).get("momentum") or {}).get("strength", "unknown")
    return {
        "growth": round(growth, 4),
        "value": round(value, 4),
        "momentum": round(momentum, 4),
        "quality": round(quality, 4),
        "macro_sensitivity": round(macro_sensitivity, 4),
        "market_factor_backdrop": dominant_factor,
    }


def _coverage_status(pe_ratio: float | None, technicals: Dict[str, Any]) -> str:
    if pe_ratio is not None and technicals.get("momentum_score") is not None:
        return "PARTIAL_STRONG"
    if pe_ratio is not None or technicals.get("momentum_score") is not None:
        return "PARTIAL"
    return "WEAK"


def _infer_regime_hint(macro_context: Dict[str, Any], factor_context: Dict[str, Any]) -> str:
    risk = (macro_context.get("risk") or {}).get("appetite")
    factor_strength = ((factor_context.get("factors") or {}).get("momentum") or {}).get("strength")
    if risk == "MIXED" and factor_strength == "weak":
        return "DEFENSIVE"
    if risk == "HIGH":
        return "RISK_ON"
    return "BALANCED"


def _load_fund_metadata_catalog(market: str) -> Dict[str, Dict[str, Any]]:
    catalog: Dict[str, Dict[str, Any]] = {}
    if market != "INDIA":
        return catalog
    sec_list_candidates = sorted((PROJECT_ROOT / "data" / "input" / "daily" / "Equities").glob("sec_list_*.csv"), reverse=True)
    if not sec_list_candidates:
        return catalog
    frame = pd.read_csv(sec_list_candidates[0])
    for _, row in frame.iterrows():
        symbol = str(row.get("SYMBOL") or "").upper().strip()
        name = str(row.get("NAME OF COMPANY") or "").strip()
        if not symbol or not name:
            continue
        if "ETF" not in name.upper() and "MUTUAL FUND" not in name.upper():
            continue
        catalog[symbol] = {
            "registered_name": name,
            "fund_family": name.split("-")[0].strip() if "-" in name else None,
            "benchmark_reference": _parse_benchmark_reference(name),
            "benchmark_provider": _benchmark_provider(_parse_benchmark_reference(name)),
            "security_type": _infer_security_type(name),
            "metadata_source": str(sec_list_candidates[0].relative_to(PROJECT_ROOT)),
        }
    return catalog


def _load_curated_fund_benchmark_map(market: str) -> Dict[str, Dict[str, Any]]:
    path = PROJECT_ROOT / "data" / "portfolio_intelligence" / "reference" / "fund_benchmark_mappings.json"
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload.get(market, {})


def _parse_benchmark_reference(name: str) -> str | None:
    upper = name.upper()
    patterns = [
        r"(NASDAQ\s*100)",
        r"(NIFTY\s*BANK)",
        r"(NIFTY\s*NEXT\s*50)",
        r"(NIFTY\s*50)",
        r"(NIFTY\s*200)",
        r"(NIFTY\s*500)",
        r"(NIFTY\s*AUTO)",
        r"(NIFTY\s*IT)",
        r"(NIFTY\s*HEALTHCARE)",
        r"(NIFTY\s*INDIA\s*CONSUMPTION)",
        r"(S&P\s*BSE\s*SENSEX)",
        r"(BSE\s*500)",
        r"(NIFTY\s*PSU\s*BANK)",
        r"(NIFTY\s*FIN\s*SER\s*EX-BANK)",
        r"(NIFTY\s*TOTAL\s*MARKET)",
        r"(NIFTY\s*EV\s*&\s*NEW\s*AGE\s*AUTOMOTIVE)",
    ]
    for pattern in patterns:
        match = re.search(pattern, upper)
        if match:
            return re.sub(r"\s+", " ", match.group(1)).strip()
    return None


def _infer_security_type(name: str) -> str:
    upper = name.upper()
    if "ETF" in upper:
        return "ETF"
    if "FUND" in upper or "MUTUAL" in upper:
        return "MUTUAL_FUND"
    return "FUND"


def _benchmark_provider(benchmark_reference: str | None) -> str | None:
    if not benchmark_reference:
        return None
    upper = benchmark_reference.upper()
    if "NIFTY" in upper:
        return "NSE_INDICES"
    if "BSE" in upper or "SENSEX" in upper:
        return "BSE_INDICES"
    if "NASDAQ" in upper:
        return "NASDAQ"
    return "UNSPECIFIED"


def _benchmark_provider_symbol(benchmark_reference: str | None, *, market: str) -> str | None:
    if not benchmark_reference:
        return None
    normalized = re.sub(r"\s+", " ", benchmark_reference.upper()).strip()
    benchmark_map = {
        "NASDAQ 100": "QQQ",
    }
    return benchmark_map.get(normalized)


def _resolve_real_lookthrough(
    fund: Dict[str, Any],
    *,
    market: str,
    benchmark_reference: str | None,
    benchmark_proxy_symbol: str | None,
    config: PortfolioIntelligenceConfig,
) -> Tuple[List[Dict[str, Any]], str, Dict[str, Any]]:
    direct = fund.get("underlying_holdings") or []
    if direct:
        return direct, "UNDERLYING_DISCLOSURE", {
            "status": "REAL_LOOKTHROUGH_OK",
            "metadata_source": fund.get("metadata_source") or fund.get("trace", {}).get("metadata_source"),
            "source": "broker_payload",
        }

    ticker = str(fund.get("ticker") or "").upper()
    cached_fund = _load_json_if_exists(config.fund_metadata_dir / market / f"{ticker}.json")
    cached_holdings = cached_fund.get("underlying_holdings", []) if cached_fund else []
    if cached_holdings:
        return cached_holdings, "UNDERLYING_DISCLOSURE", {
            "status": "REAL_LOOKTHROUGH_OK",
            "metadata_source": str((config.fund_metadata_dir / market / f"{ticker}.json").relative_to(PROJECT_ROOT)),
            "source": "cached_fund_metadata",
        }

    if config.alpha_vantage_api_key and _infer_security_type(str(fund.get("security_name") or ticker)) == "ETF":
        provider_payload = _fetch_alpha_vantage_etf_profile(ticker, config.alpha_vantage_api_key)
        provider_holdings = provider_payload.get("underlying_holdings", [])
        if provider_holdings:
            path = config.fund_metadata_dir / market / f"{ticker}.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(provider_payload, indent=2), encoding="utf-8")
            return provider_holdings, "UNDERLYING_DISCLOSURE", {
                "status": "REAL_LOOKTHROUGH_OK",
                "metadata_source": str(path.relative_to(PROJECT_ROOT)),
                "source": "alpha_vantage_etf_profile",
            }

    benchmark_key = _slugify(benchmark_reference) if benchmark_reference else None
    if benchmark_key:
        cached_benchmark = _load_json_if_exists(config.benchmark_metadata_dir / market / f"{benchmark_key}.json")
        benchmark_holdings = cached_benchmark.get("underlying_holdings", []) if cached_benchmark else []
        if benchmark_holdings:
            return benchmark_holdings, "BENCHMARK_COMPOSITION", {
                "status": "BENCHMARK_LOOKTHROUGH_OK",
                "metadata_source": str((config.benchmark_metadata_dir / market / f"{benchmark_key}.json").relative_to(PROJECT_ROOT)),
                "source": "cached_benchmark_metadata",
            }

        benchmark_symbol = benchmark_proxy_symbol or _benchmark_provider_symbol(benchmark_reference, market=market)
        if benchmark_symbol and config.alpha_vantage_api_key:
            provider_payload = _fetch_alpha_vantage_etf_profile(benchmark_symbol, config.alpha_vantage_api_key)
            provider_holdings = provider_payload.get("underlying_holdings", [])
            if provider_holdings:
                path = config.benchmark_metadata_dir / market / f"{benchmark_key}.json"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    json.dumps(
                        {
                            "benchmark_reference": benchmark_reference,
                            "provider_symbol": benchmark_symbol,
                            "provider": provider_payload.get("provider", "ALPHA_VANTAGE"),
                            "underlying_holdings": provider_holdings,
                            "raw": provider_payload.get("raw", {}),
                        },
                        indent=2,
                    ),
                    encoding="utf-8",
                )
                return provider_holdings, "BENCHMARK_COMPOSITION", {
                    "status": "BENCHMARK_LOOKTHROUGH_OK",
                    "metadata_source": str(path.relative_to(PROJECT_ROOT)),
                    "source": "alpha_vantage_benchmark_proxy",
                }

    return [], "UNAVAILABLE", {
        "status": "REAL_LOOKTHROUGH_UNAVAILABLE",
        "metadata_source": "UNAVAILABLE",
        "source": "none",
        "benchmark_reference": benchmark_reference,
    }


def _fetch_alpha_vantage_etf_profile(ticker: str, api_key: str) -> Dict[str, Any]:
    try:
        response = requests.get(
            "https://www.alphavantage.co/query",
            params={"function": "ETF_PROFILE", "symbol": ticker, "apikey": api_key},
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
    except Exception:
        return {}
    holdings = payload.get("holdings") or payload.get("Holdings") or []
    normalized = []
    for item in holdings:
        symbol = str(item.get("symbol") or item.get("ticker") or "").upper().strip()
        if not symbol:
            continue
        weight = float(item.get("weight") or item.get("Weight") or 0.0)
        normalized.append(
            {
                "underlying_ticker": symbol,
                "underlying_weight": weight,
                "source": "alpha_vantage_etf_profile",
            }
        )
    return {
        "ticker": ticker,
        "provider": "ALPHA_VANTAGE",
        "underlying_holdings": normalized,
        "raw": payload,
    }


def _infer_fund_sector_industry(name: str, benchmark_reference: str | None) -> Tuple[str, str]:
    upper = name.upper()
    benchmark = (benchmark_reference or "").upper()
    if "NASDAQ 100" in benchmark:
        return "Global Funds", "NASDAQ_100"
    if "NIFTY BANK" in benchmark:
        return "Financials", "BANK_INDEX_FUND"
    if "NIFTY IT" in benchmark:
        return "Information Technology", "IT_INDEX_FUND"
    if "HEALTHCARE" in benchmark:
        return "Healthcare", "HEALTHCARE_INDEX_FUND"
    if "AUTO" in benchmark or "AUTOMOTIVE" in benchmark:
        return "Consumer Discretionary", "AUTO_INDEX_FUND"
    if "CONSUMPTION" in benchmark:
        return "Consumer Staples", "CONSUMPTION_INDEX_FUND"
    if "INFRA" in upper or "INFRASTRUCTURE" in upper:
        return "Sector Funds", "Infrastructure Fund"
    if "ELSS" in upper or "TAX" in upper:
        return "Tax Saver Funds", "ELSS Fund"
    if "IPO" in upper:
        return "Sector Funds", "IPO Fund"
    return str((name and "Mutual Funds") or "Mutual Funds"), str(benchmark_reference or "MUTUAL_FUND")


def _aggregate_underlying_factor_profile(
    underlying_holdings: List[Dict[str, Any]],
    factor_context: Dict[str, Any],
    default_sector: str,
) -> Dict[str, Any]:
    if not underlying_holdings:
        return _compute_factor_exposure(
            technicals={"trend_regime": "UNAVAILABLE", "momentum_score": None},
            pe_ratio=None,
            sector=default_sector,
            factor_context=factor_context,
        )
    profile = {"growth": 0.0, "value": 0.0, "momentum": 0.0, "quality": 0.0, "macro_sensitivity": 0.0}
    total = 0.0
    for item in underlying_holdings:
        weight = float(item.get("underlying_weight") or item.get("weight") or 0.0)
        factors = item.get("factor_profile") or item.get("factor_exposure") or {}
        total += weight
        for key in profile:
            profile[key] += float(factors.get(key, 0.0)) * weight
    if total <= 0:
        total = 1.0
    return {key: round(value / total, 4) for key, value in profile.items()}


def _materialize_underlying_holdings(
    underlying_holdings: List[Dict[str, Any]],
    *,
    market: str,
    factor_context: Dict[str, Any],
) -> List[Dict[str, Any]]:
    materialized: List[Dict[str, Any]] = []
    sector_map = INDIA_SECTOR_MAP if market == "INDIA" else US_SECTOR_MAP
    for item in underlying_holdings:
        ticker = str(item.get("underlying_ticker") or item.get("ticker") or "").upper().strip()
        sector, industry = sector_map.get(ticker, (item.get("sector") or "UNKNOWN", item.get("industry") or "UNKNOWN"))
        geography = item.get("geography") or ("US" if ticker.endswith(".US") or market == "US" else market)
        factor_profile = item.get("factor_profile") or item.get("factor_exposure")
        if not factor_profile:
            price_frame, _ = _load_price_history(ticker.replace(".NS", ""), market if geography not in {"US", "GLOBAL", "CHINA"} else "US" if geography == "US" else market)
            pe_ratio = _lookup_india_pe(ticker.replace(".NS", "")) if market == "INDIA" else None
            technicals = _compute_technicals(price_frame)
            factor_profile = _compute_factor_exposure(technicals, pe_ratio, sector, factor_context)
        materialized.append(
            {
                **item,
                "underlying_ticker": ticker,
                "sector": sector,
                "industry": industry,
                "geography": geography,
                "factor_profile": factor_profile,
            }
        )
    return materialized


def _load_json_if_exists(path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _slugify(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"[^A-Z0-9]+", "_", value.upper()).strip("_")
