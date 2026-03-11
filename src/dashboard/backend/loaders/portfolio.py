from __future__ import annotations

from typing import Any, Dict

from src.dashboard.backend.loaders.provenance import attach_provenance
from src.portfolio_intelligence.service import PortfolioIntelligenceService


SERVICE = PortfolioIntelligenceService()


def load_portfolio_overview(market: str) -> Dict[str, Any]:
    payload = SERVICE.load_overview(market)
    return attach_provenance(payload, f"data/portfolio_intelligence/analytics/{market}")


def load_portfolio_holdings(market: str, portfolio_id: str) -> Dict[str, Any]:
    payload = SERVICE.load_portfolio(market, portfolio_id)
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
