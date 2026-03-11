from __future__ import annotations

import json
from typing import Any, Dict, List, Tuple

import pandas as pd

from .config import PROJECT_ROOT, PortfolioIntelligenceConfig


def enrich_portfolio(
    normalized_payload: Dict[str, Any],
    *,
    config: PortfolioIntelligenceConfig,
) -> Dict[str, Any]:
    market = normalized_payload["market"]
    macro_context = _load_latest_context(market, "macro_context.json")
    factor_context = _load_latest_context(market, "factor_context.json")

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

    payload = dict(normalized_payload)
    payload["holdings"] = enriched_holdings
    payload["macro_context"] = macro_context
    payload["factor_context"] = factor_context
    return payload


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
