from __future__ import annotations

import os
import re
from typing import Any, Dict

from src.dashboard.backend.loaders.provenance import attach_provenance
from src.portfolio_intelligence.exposure_engine import PortfolioExposureEngine
from src.portfolio_intelligence.mutual_fund_research_engine import MutualFundResearchEngine
from src.portfolio_intelligence.news_event_intelligence import PortfolioEventIntelligenceBuilder
from src.portfolio_intelligence.portfolio_intelligence_engine import PortfolioIntelligenceEngine
from src.portfolio_intelligence.portfolio_strategy_engine import PortfolioStrategyEngine
from src.portfolio_intelligence.refresh_runtime import PortfolioRefreshRuntime
from src.portfolio_intelligence.service import PortfolioIntelligenceService
from src.portfolio_intelligence.stock_research_engine import StockResearchEngine
from src.portfolio_intelligence.synthesis import PortfolioNarrativeSynthesizer


SERVICE = PortfolioIntelligenceService()
_EXPOSURE_ENGINE = PortfolioExposureEngine()
_MUTUAL_FUND_RESEARCH_ENGINE = MutualFundResearchEngine()
_EVENT_INTELLIGENCE_BUILDER = PortfolioEventIntelligenceBuilder()
_STOCK_RESEARCH_ENGINE = StockResearchEngine()
_PORTFOLIO_INTELLIGENCE_ENGINE = PortfolioIntelligenceEngine()
_PORTFOLIO_STRATEGY_ENGINE = PortfolioStrategyEngine()
_SYNTHESIS = PortfolioNarrativeSynthesizer()


def _ensure_exposure(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Return exposure_analysis from payload or compute it on-the-fly."""
    existing = payload.get("exposure_analysis") or {}
    if existing.get("lookthrough_summary") and all(item.get("trace") for item in existing.get("exposure_insights", [])):
        return existing
    return _EXPOSURE_ENGINE.compute_full_exposure(
        payload.get("holdings", []),
        mutual_fund_holdings=payload.get("mutual_fund_holdings", []),
        macro_context=payload.get("macro_context", {}),
        factor_context=payload.get("factor_context", {}),
        portfolio_id=payload.get("portfolio_id", ""),
        market=payload.get("market", ""),
        truth_epoch=payload.get("truth_epoch", ""),
        data_as_of=payload.get("data_as_of", ""),
    )


def _ensure_intelligence(payload: Dict[str, Any]) -> Dict[str, Any]:
    event_intelligence = payload.get("portfolio_event_alerts")
    event_map = {}
    if payload.get("portfolio_event_timeline") or payload.get("news_adapter_status"):
        for profile in payload.get("stock_research_profiles", []):
            event_payload = profile.get("event_intelligence")
            if event_payload:
                event_map[profile.get("ticker")] = event_payload
    if not event_map:
        built_event_intelligence = _EVENT_INTELLIGENCE_BUILDER.build(holdings=payload.get("holdings", []), market=payload.get("market", ""))
        event_map = built_event_intelligence.stock_event_map
    existing_profiles = payload.get("stock_research_profiles") or []
    needs_profile_rebuild = not existing_profiles or any("event_intelligence" not in item for item in existing_profiles)
    research_profiles = existing_profiles if not needs_profile_rebuild else _STOCK_RESEARCH_ENGINE.build_profiles(
        payload.get("holdings", []),
        market=payload.get("market", ""),
        macro_context=payload.get("macro_context", {}),
        regime_gate_state=payload.get("regime_gate_state", "BLOCKED"),
        event_intelligence_map=event_map,
    )
    exposure_analysis = _ensure_exposure(payload)
    intelligence_bundle = {
        "stock_research_profiles": research_profiles,
        "stock_intelligence_summaries": payload.get("stock_intelligence_summaries"),
        "valuation_overview": payload.get("valuation_overview"),
        "research_synthesis": payload.get("research_synthesis"),
    }
    if not intelligence_bundle["stock_intelligence_summaries"] or not intelligence_bundle["valuation_overview"]:
        recomputed_intelligence = _PORTFOLIO_INTELLIGENCE_ENGINE.build_portfolio_intelligence(
            research_profiles=research_profiles,
            exposure_analysis=exposure_analysis,
            market=payload.get("market", ""),
            truth_epoch=payload.get("truth_epoch", ""),
        )
        intelligence_bundle["stock_intelligence_summaries"] = recomputed_intelligence.get("stock_intelligence_summaries", [])
        intelligence_bundle["valuation_overview"] = recomputed_intelligence.get("valuation_overview", {})
    mutual_fund_intelligence = _ensure_mutual_fund_intelligence(payload)
    strategy_bundle = _PORTFOLIO_STRATEGY_ENGINE.build_strategy_package(
        research_profiles=research_profiles,
        mutual_fund_intelligence=mutual_fund_intelligence,
        exposure_analysis=exposure_analysis,
        macro_context=payload.get("macro_context", {}),
        factor_context=payload.get("factor_context", {}),
        market=payload.get("market", ""),
        truth_epoch=payload.get("truth_epoch", ""),
    )
    intelligence_bundle["research_synthesis"] = _SYNTHESIS.synthesize(
        suggestions=strategy_bundle["portfolio_strategy_suggestions"],
        research_profiles=research_profiles,
        portfolio_event_alerts=payload.get("portfolio_event_alerts", []),
        enable_llm=False,
    )
    intelligence_bundle["portfolio_risk_alerts"] = strategy_bundle["portfolio_risk_alerts"]
    intelligence_bundle["portfolio_suggestions"] = strategy_bundle["portfolio_strategy_suggestions"]
    intelligence_bundle["portfolio_strategy_summary"] = strategy_bundle["portfolio_strategy_summary"]
    intelligence_bundle["portfolio_strengthening_insights"] = strategy_bundle["portfolio_strengthening_insights"]
    intelligence_bundle["portfolio_opportunity_signals"] = strategy_bundle["portfolio_opportunity_signals"]
    return intelligence_bundle


def _ensure_mutual_fund_intelligence(payload: Dict[str, Any]) -> Dict[str, Any]:
    existing = payload.get("mutual_fund_intelligence")
    if existing and existing.get("fund_profiles"):
        return existing
    return _MUTUAL_FUND_RESEARCH_ENGINE.build_intelligence(
        payload.get("mutual_fund_holdings", []),
        total_portfolio_value=float((payload.get("overview") or {}).get("total_value") or 0.0),
    )


def _ensure_portfolio_event_intelligence(payload: Dict[str, Any]) -> Dict[str, Any]:
    if payload.get("portfolio_event_alerts") is not None and payload.get("news_adapter_status") is not None:
        return {
            "news_adapter_status": payload.get("news_adapter_status", {}),
            "portfolio_event_alerts": payload.get("portfolio_event_alerts", []),
            "portfolio_event_timeline": payload.get("portfolio_event_timeline", []),
        }
    built = _EVENT_INTELLIGENCE_BUILDER.build(holdings=payload.get("holdings", []), market=payload.get("market", ""))
    return {
        "news_adapter_status": built.adapter_status,
        "portfolio_event_alerts": built.portfolio_event_alerts,
        "portfolio_event_timeline": built.portfolio_event_timeline,
    }


def _ensure_mutual_fund_metadata(payload: Dict[str, Any]) -> list[Dict[str, Any]]:
    funds = []
    for fund in payload.get("mutual_fund_holdings", []):
        row = dict(fund)
        if not row.get("benchmark_reference"):
            row["benchmark_reference"] = _parse_benchmark_reference(str(row.get("security_name") or row.get("ticker") or ""))
        if not row.get("lookthrough_mode"):
            row["lookthrough_mode"] = "UNDERLYING_DISCLOSURE" if row.get("underlying_holdings") else "HEURISTIC_FALLBACK"
        if not row.get("lookthrough_status"):
            row["lookthrough_status"] = "REAL_LOOKTHROUGH_OK" if row.get("underlying_holdings") else "REAL_LOOKTHROUGH_UNAVAILABLE"
        funds.append(row)
    return funds


def _parse_benchmark_reference(name: str) -> str | None:
    upper = name.upper()
    patterns = [
        r"(NASDAQ\s*100)",
        r"(NIFTY\s*BANK)",
        r"(NIFTY\s*NEXT\s*50)",
        r"(NIFTY\s*50)",
        r"(NIFTY\s*200)",
        r"(NIFTY\s*500)",
        r"(S&P\s*BSE\s*SENSEX)",
        r"(BSE\s*500)",
    ]
    for pattern in patterns:
        match = re.search(pattern, upper)
        if match:
            return re.sub(r"\s+", " ", match.group(1)).strip()
    return None


def load_portfolio_overview(market: str) -> Dict[str, Any]:
    payload = SERVICE.load_overview(market)
    return attach_provenance(payload, f"data/portfolio_intelligence/analytics/{market}")


def load_portfolio_holdings(market: str, portfolio_id: str) -> Dict[str, Any]:
    payload = SERVICE.load_portfolio(market, portfolio_id)
    payload = dict(payload)
    payload["mutual_fund_holdings"] = _ensure_mutual_fund_metadata(payload)
    return attach_provenance(payload, f"data/portfolio_intelligence/analytics/{market}/{portfolio_id}/latest.json")


def load_portfolio_diversification(market: str, portfolio_id: str) -> Dict[str, Any]:
    payload = SERVICE.load_portfolio(market, portfolio_id)
    body = {
        "portfolio_id": portfolio_id,
        "market": market,
        "truth_epoch": payload["truth_epoch"],
        "data_as_of": payload["data_as_of"],
        "regime_gate_state": payload["regime_gate_state"],
        "diversification": payload["diversification"],
    }
    return attach_provenance(body, f"data/portfolio_intelligence/analytics/{market}/{portfolio_id}/latest.json")


def load_portfolio_risk(market: str, portfolio_id: str) -> Dict[str, Any]:
    payload = SERVICE.load_portfolio(market, portfolio_id)
    body = {
        "portfolio_id": portfolio_id,
        "market": market,
        "truth_epoch": payload["truth_epoch"],
        "data_as_of": payload["data_as_of"],
        "regime_gate_state": payload["regime_gate_state"],
        "risk": payload["risk"],
    }
    return attach_provenance(body, f"data/portfolio_intelligence/analytics/{market}/{portfolio_id}/latest.json")


def load_portfolio_structure(market: str, portfolio_id: str) -> Dict[str, Any]:
    payload = SERVICE.load_portfolio(market, portfolio_id)
    holdings = payload.get("holdings", [])
    top_holdings = sorted(holdings, key=lambda item: item.get("weight_pct", 0), reverse=True)
    structure = {
        "top_3": top_holdings[:3],
        "core_holdings": [item for item in top_holdings if item.get("conviction_score", 0) >= 0.7],
        "satellite_holdings": [item for item in top_holdings if item.get("conviction_score", 0) < 0.7],
    }
    body = {
        "portfolio_id": portfolio_id,
        "market": market,
        "truth_epoch": payload["truth_epoch"],
        "data_as_of": payload["data_as_of"],
        "regime_gate_state": payload["regime_gate_state"],
        "structure": structure,
    }
    return attach_provenance(body, f"data/portfolio_intelligence/analytics/{market}/{portfolio_id}/latest.json")


def load_portfolio_performance(market: str, portfolio_id: str) -> Dict[str, Any]:
    payload = SERVICE.load_portfolio(market, portfolio_id)
    body = {
        "portfolio_id": portfolio_id,
        "market": market,
        "truth_epoch": payload["truth_epoch"],
        "data_as_of": payload["data_as_of"],
        "performance": payload["performance"],
        "overview": payload["overview"],
    }
    return attach_provenance(body, f"data/portfolio_intelligence/analytics/{market}/{portfolio_id}/latest.json")


def load_portfolio_insights(market: str, portfolio_id: str) -> Dict[str, Any]:
    payload = SERVICE.load_portfolio(market, portfolio_id)
    body = {
        "portfolio_id": portfolio_id,
        "market": market,
        "truth_epoch": payload["truth_epoch"],
        "data_as_of": payload["data_as_of"],
        "regime_gate_state": payload["regime_gate_state"],
        "insights": payload["insights"],
    }
    return attach_provenance(body, f"data/portfolio_intelligence/analytics/{market}/{portfolio_id}/latest.json")


def load_portfolio_resilience(market: str, portfolio_id: str) -> Dict[str, Any]:
    payload = SERVICE.load_portfolio(market, portfolio_id)
    body = {
        "portfolio_id": portfolio_id,
        "market": market,
        "truth_epoch": payload["truth_epoch"],
        "data_as_of": payload["data_as_of"],
        "regime_gate_state": payload["regime_gate_state"],
        "resilience": payload["resilience"],
    }
    return attach_provenance(body, f"data/portfolio_intelligence/analytics/{market}/{portfolio_id}/latest.json")


def load_combined_portfolio_view() -> Dict[str, Any]:
    payload = SERVICE.load_combined()
    return attach_provenance(payload, "data/portfolio_intelligence/analytics")


def load_portfolio_exposure(market: str, portfolio_id: str) -> Dict[str, Any]:
    payload = SERVICE.load_portfolio(market, portfolio_id)
    exposure = _ensure_exposure(payload)
    body = {
        "portfolio_id": portfolio_id,
        "market": market,
        "truth_epoch": payload.get("truth_epoch", ""),
        "data_as_of": payload.get("data_as_of", ""),
        "regime_gate_state": payload.get("regime_gate_state", ""),
        "lookthrough_summary": exposure.get("lookthrough_summary", {}),
        "sector_exposure": exposure.get("sector_exposure", {}),
        "industry_exposure": exposure.get("industry_exposure", {}),
        "geography_exposure": exposure.get("geography_exposure", {}),
        "factor_exposure": exposure.get("factor_exposure", {}),
        "hidden_concentrations": exposure.get("hidden_concentrations", {}),
        "exposure_metrics": exposure.get("exposure_metrics", {}),
        "exposure_insights": exposure.get("exposure_insights", []),
    }
    return attach_provenance(body, f"data/portfolio_intelligence/analytics/{market}/{portfolio_id}/latest.json")


def load_portfolio_macro_alignment(market: str, portfolio_id: str) -> Dict[str, Any]:
    payload = SERVICE.load_portfolio(market, portfolio_id)
    exposure = _ensure_exposure(payload)
    body = {
        "portfolio_id": portfolio_id,
        "market": market,
        "truth_epoch": payload.get("truth_epoch", ""),
        "data_as_of": payload.get("data_as_of", ""),
        "regime_gate_state": payload.get("regime_gate_state", ""),
        "macro_regime_exposure": exposure.get("macro_regime_exposure", {}),
        "exposure_metrics": exposure.get("exposure_metrics", {}),
    }
    return attach_provenance(body, f"data/portfolio_intelligence/analytics/{market}/{portfolio_id}/latest.json")


def load_portfolio_research(market: str, portfolio_id: str) -> Dict[str, Any]:
    payload = SERVICE.load_portfolio(market, portfolio_id)
    intelligence = _ensure_intelligence(payload)
    event_intelligence = _ensure_portfolio_event_intelligence(payload)
    body = {
        "portfolio_id": portfolio_id,
        "market": market,
        "truth_epoch": payload.get("truth_epoch", ""),
        "data_as_of": payload.get("data_as_of", ""),
        "regime_gate_state": payload.get("regime_gate_state", ""),
        "stock_research_profiles": intelligence.get("stock_research_profiles", []),
        "stock_intelligence_summaries": intelligence.get("stock_intelligence_summaries", []),
        "valuation_overview": intelligence.get("valuation_overview", {}),
        "mutual_fund_intelligence": _ensure_mutual_fund_intelligence(payload),
        "news_adapter_status": event_intelligence.get("news_adapter_status", {}),
        "portfolio_event_alerts": event_intelligence.get("portfolio_event_alerts", []),
        "portfolio_event_timeline": event_intelligence.get("portfolio_event_timeline", []),
        "research_synthesis": intelligence.get("research_synthesis", {}),
    }
    return attach_provenance(body, f"data/portfolio_intelligence/analytics/{market}/{portfolio_id}/latest.json")


def load_portfolio_advisory(market: str, portfolio_id: str) -> Dict[str, Any]:
    payload = SERVICE.load_portfolio(market, portfolio_id)
    intelligence = _ensure_intelligence(payload)
    event_intelligence = _ensure_portfolio_event_intelligence(payload)
    body = {
        "portfolio_id": portfolio_id,
        "market": market,
        "truth_epoch": payload.get("truth_epoch", ""),
        "data_as_of": payload.get("data_as_of", ""),
        "regime_gate_state": payload.get("regime_gate_state", ""),
        "portfolio_strategy_summary": intelligence.get("portfolio_strategy_summary", {}),
        "portfolio_risk_alerts": intelligence.get("portfolio_risk_alerts", []),
        "portfolio_suggestions": intelligence.get("portfolio_suggestions", []),
        "portfolio_strengthening_insights": intelligence.get("portfolio_strengthening_insights", []),
        "portfolio_opportunity_signals": intelligence.get("portfolio_opportunity_signals", []),
        "portfolio_event_alerts": event_intelligence.get("portfolio_event_alerts", []),
        "news_adapter_status": event_intelligence.get("news_adapter_status", {}),
        "research_synthesis": intelligence.get("research_synthesis", {}),
    }
    return attach_provenance(body, f"data/portfolio_intelligence/analytics/{market}/{portfolio_id}/latest.json")


def load_portfolio_refresh_status(market: str, portfolio_id: str) -> Dict[str, Any]:
    payload = SERVICE.load_portfolio(market, portfolio_id)
    diagnostics = payload.get("refresh_diagnostics", {})
    runtime = PortfolioRefreshRuntime.snapshot(market, portfolio_id)
    return attach_provenance(
        {
            "portfolio_id": portfolio_id,
            "market": market,
            "truth_epoch": payload.get("truth_epoch", ""),
            "data_as_of": payload.get("data_as_of", ""),
            "portfolio_refresh_timestamp": payload.get("portfolio_refresh_timestamp"),
            "portfolio_data_source": payload.get("portfolio_data_source", "UNAVAILABLE"),
            "refresh_diagnostics": diagnostics,
            "mutual_fund_count": len(payload.get("mutual_fund_holdings", [])),
            "holding_count": len(payload.get("holdings", [])),
            "runtime": runtime,
        },
        f"data/portfolio_intelligence/analytics/{market}/{portfolio_id}/latest.json",
    )


def load_portfolio_trend(market: str, portfolio_id: str, limit: int = 20) -> Dict[str, Any]:
    payload = SERVICE.load_portfolio_trend(market, portfolio_id, limit=limit)
    return attach_provenance(payload, f"data/portfolio_intelligence/history/{market}/{portfolio_id}")


def trigger_portfolio_refresh(
    market: str,
    portfolio_id: str,
    *,
    account_name: str | None = None,
    headless_auth: bool = False,
) -> Dict[str, Any]:
    previous = os.getenv("KITE_HEADLESS_AUTH")
    if headless_auth:
        os.environ["KITE_HEADLESS_AUTH"] = "true"
    try:
        result = SERVICE.refresh_zerodha_portfolio(
            portfolio_id=portfolio_id,
            account_name=account_name,
            market=market,
            trigger="dashboard_api",
            headless_auth=headless_auth,
        )
    except RuntimeError as exc:
        if "already in progress" in str(exc).lower():
            return attach_provenance(
                {
                    "status": "REFRESH_IN_PROGRESS",
                    "portfolio_id": portfolio_id,
                    "market": market,
                    "runtime": PortfolioRefreshRuntime.snapshot(market, portfolio_id),
                },
                f"data/portfolio_intelligence/analytics/{market}/{portfolio_id}/latest.json",
            )
        raise
    finally:
        if headless_auth:
            if previous is None:
                os.environ.pop("KITE_HEADLESS_AUTH", None)
            else:
                os.environ["KITE_HEADLESS_AUTH"] = previous
    return attach_provenance(
        {
            "status": "REFRESH_OK",
            "portfolio_id": result.get("portfolio_id"),
            "market": result.get("market"),
            "portfolio_refresh_timestamp": result.get("portfolio_refresh_timestamp"),
            "portfolio_data_source": result.get("portfolio_data_source"),
            "holding_count": len(result.get("holdings", [])),
            "mutual_fund_count": len(result.get("mutual_fund_holdings", [])),
            "refresh_diagnostics": result.get("refresh_diagnostics", {}),
            "runtime": PortfolioRefreshRuntime.snapshot(market, portfolio_id),
        },
        f"data/portfolio_intelligence/analytics/{market}/{portfolio_id}/latest.json",
    )
