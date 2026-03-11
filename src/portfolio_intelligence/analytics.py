from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List


def analyze_portfolio(payload: Dict[str, Any], *, usd_inr_rate: float = 0.0) -> Dict[str, Any]:
    holdings = payload.get("holdings", [])
    total_value = sum(float(item.get("market_value") or 0.0) for item in holdings)
    total_cost = sum(float(item.get("cost_basis") or 0.0) for item in holdings)
    total_pnl = sum(float(item.get("pnl") or 0.0) for item in holdings)

    holding_cards: List[Dict[str, Any]] = []
    sector_allocation: Dict[str, float] = defaultdict(float)
    geography_allocation: Dict[str, float] = defaultdict(float)
    factor_distribution: Dict[str, float] = defaultdict(float)
    top_weights: List[float] = []

    regime_backdrop = payload.get("macro_context", {})
    factor_backdrop = payload.get("factor_context", {})
    regime_gate_state = _regime_gate_state(regime_backdrop, factor_backdrop)

    for holding in holdings:
        card = _score_holding(holding, total_value=total_value, regime_gate_state=regime_gate_state)
        holding_cards.append(card)
        sector_allocation[holding["sector"]] += float(holding["weight_pct"])
        geography_allocation[holding["geography"]] += float(holding["weight_pct"])
        for key in ("growth", "value", "momentum", "quality"):
            factor_distribution[key] += float(holding.get("factor_exposure", {}).get(key, 0.0)) * float(holding["weight_pct"]) / 100.0
        top_weights.append(float(holding["weight_pct"]))

    top_weights.sort(reverse=True)
    winners = sorted(holding_cards, key=lambda item: item["pnl_pct"], reverse=True)[:5]
    laggards = sorted(holding_cards, key=lambda item: item["pnl_pct"])[:5]

    diversification_score = round(max(0.0, 1.0 - _hhi(sector_allocation) / 10000.0), 4)
    concentration_score = round(max(0.0, 1.0 - sum(top_weights[:3]) / 100.0), 4)
    regime_alignment_score = round(
        sum(card["regime_alignment_score"] * card["weight_pct"] / 100.0 for card in holding_cards),
        4,
    ) if holding_cards else 0.0
    momentum_health = round(
        sum(float(card["factor_exposure"]["momentum"]) * card["weight_pct"] / 100.0 for card in holding_cards),
        4,
    ) if holding_cards else 0.0
    resilience_score = round(
        (diversification_score + concentration_score + regime_alignment_score + momentum_health) / 4.0,
        4,
    )

    insights = _build_insights(
        holding_cards=holding_cards,
        sector_allocation=dict(sector_allocation),
        factor_distribution=dict(factor_distribution),
        regime_gate_state=regime_gate_state,
    )

    return {
        "portfolio_id": payload["portfolio_id"],
        "broker": payload["broker"],
        "account_name": payload["account_name"],
        "market": payload["market"],
        "truth_epoch": payload["truth_epoch"],
        "data_as_of": payload["data_as_of"],
        "portfolio_data_source": payload.get("portfolio_data_source", "UNAVAILABLE"),
        "source_provenance": payload.get("source_provenance", payload["broker"].lower()),
        "portfolio_refresh_timestamp": payload.get("portfolio_refresh_timestamp", payload["data_as_of"]),
        "refresh_diagnostics": payload.get("refresh_diagnostics", {}),
        "portfolio_summary": payload.get("portfolio_summary", {}),
        "regime_gate_state": regime_gate_state,
        "overview": {
            "total_value": round(total_value, 2),
            "total_cost_basis": round(total_cost, 2),
            "total_pnl": round(total_pnl, 2),
            "total_pnl_pct": round((total_pnl / total_cost * 100.0), 4) if total_cost else 0.0,
            "holding_count": len(holding_cards),
        },
        "holdings": holding_cards,
        "diversification": {
            "sector_allocation": _round_map(sector_allocation),
            "geography_allocation": _round_map(geography_allocation),
            "factor_distribution": _round_map(factor_distribution),
            "diversification_score": diversification_score,
            "effective_positions": round(1.0 / max(_hhi(sector_allocation) / 10000.0, 0.0001), 2),
        },
        "risk": {
            "concentration_score": concentration_score,
            "top_3_weight_pct": round(sum(top_weights[:3]), 4),
            "top_5_weight_pct": round(sum(top_weights[:5]), 4),
            "correlation_clustering": _correlation_cluster(sector_allocation),
            "macro_sensitivity": round(
                sum(float(card["factor_exposure"]["macro_sensitivity"]) * card["weight_pct"] / 100.0 for card in holding_cards),
                4,
            ) if holding_cards else 0.0,
        },
        "performance": {
            "winners": winners,
            "laggards": laggards,
            "top_contributors": sorted(
                holding_cards,
                key=lambda item: item["contribution_to_return"],
                reverse=True,
            )[:5],
            "bottom_contributors": sorted(
                holding_cards,
                key=lambda item: item["contribution_to_return"],
            )[:5],
        },
        "insights": insights,
        "resilience": {
            "overall_score": resilience_score,
            "classification": _resilience_classification(resilience_score),
            "components": {
                "diversification": diversification_score,
                "concentration": concentration_score,
                "regime_alignment": regime_alignment_score,
                "momentum_health": momentum_health,
            },
        },
        "combined_view": _combined_stub(payload["market"], total_value, usd_inr_rate),
        "trace": {
            "source": f"data/portfolio_intelligence/analytics/{payload['market']}/{payload['portfolio_id']}/latest.json",
            "analytics_engine": "portfolio_intelligence.analytics",
            "data_source": payload.get("portfolio_data_source", "UNAVAILABLE"),
        },
    }


def _score_holding(holding: Dict[str, Any], *, total_value: float, regime_gate_state: str) -> Dict[str, Any]:
    technicals = holding.get("technicals", {})
    factor_exposure = holding.get("factor_exposure", {})
    pe_ratio = holding.get("fundamentals", {}).get("pe_ratio")
    value_score = max(min((30.0 - pe_ratio) / 30.0, 1.0), 0.0) if pe_ratio else 0.5
    technical_score = technicals.get("momentum_score") if technicals.get("momentum_score") is not None else 0.45
    quality_score = factor_exposure.get("quality", 0.5)
    coverage_state = holding.get("enrichment", {}).get("coverage_status", "WEAK")
    base_conviction = (value_score + technical_score + quality_score + factor_exposure.get("growth", 0.5)) / 4.0
    if regime_gate_state == "DEGRADED":
        base_conviction = min(base_conviction, 0.65)
    elif regime_gate_state == "BLOCKED":
        base_conviction = min(base_conviction, 0.45)

    risk_flags: List[str] = []
    if coverage_state in {"WEAK", "PARTIAL"}:
        risk_flags.append("FUNDAMENTAL_COVERAGE_GAP")
    if technicals.get("volatility_regime") == "HIGH":
        risk_flags.append("VOLATILITY_ELEVATED")
    if technicals.get("trend_regime") == "BEARISH":
        risk_flags.append("TREND_WEAKNESS")
    if float(holding.get("weight_pct") or 0.0) >= 12.0:
        risk_flags.append("POSITION_CONCENTRATION")

    regime_alignment_score = 0.8 if technicals.get("trend_regime") == "BULLISH" else 0.55 if technicals.get("trend_regime") == "TRANSITION" else 0.35
    contribution = (float(holding.get("market_value") or 0.0) / total_value * float(holding.get("pnl_pct") or 0.0)) if total_value else 0.0
    classification = (
        "HIGH_CONVICTION"
        if base_conviction >= 0.75 and not risk_flags
        else "REVIEW_REQUIRED"
        if len(risk_flags) >= 2
        else "MONITOR"
    )

    return {
        "ticker": holding["ticker"],
        "canonical_ticker": holding["canonical_ticker"],
        "weight_pct": round(float(holding["weight_pct"]), 4),
        "market_value": float(holding["market_value"]),
        "pnl": float(holding["pnl"]),
        "pnl_pct": float(holding["pnl_pct"]),
        "sector": holding["sector"],
        "industry": holding["industry"],
        "conviction_score": round(base_conviction, 4),
        "opportunity_classification": classification,
        "risk_flags": risk_flags,
        "regime_alignment_score": round(regime_alignment_score, 4),
        "regime_compatibility": "ALIGNED" if regime_alignment_score >= 0.7 else "MIXED" if regime_alignment_score >= 0.5 else "MISALIGNED",
        "factor_exposure": factor_exposure,
        "technicals": technicals,
        "fundamentals": holding.get("fundamentals", {}),
        "sentiment": holding.get("sentiment", {}),
        "liquidity_risk": "LOW" if holding["market"] == "US" or holding["sector"] in {"Financials", "Information Technology"} else "MEDIUM",
        "coverage_status": coverage_state,
        "contribution_to_return": round(contribution, 4),
        "trace": holding.get("trace", {}),
    }


def _hhi(values: Dict[str, float]) -> float:
    return sum(weight ** 2 for weight in values.values())


def _round_map(values: Dict[str, float]) -> Dict[str, float]:
    return {key: round(value, 4) for key, value in values.items()}


def _correlation_cluster(sector_allocation: Dict[str, float]) -> Dict[str, Any]:
    if not sector_allocation:
        return {"cluster_count": 0, "dominant_cluster": "NONE"}
    dominant_sector = max(sector_allocation, key=sector_allocation.get)
    return {
        "cluster_count": len([value for value in sector_allocation.values() if value >= 10.0]),
        "dominant_cluster": dominant_sector,
        "dominant_cluster_weight_pct": round(sector_allocation[dominant_sector], 4),
    }


def _regime_gate_state(macro_context: Dict[str, Any], factor_context: Dict[str, Any]) -> str:
    if not macro_context or not factor_context:
        return "BLOCKED"
    confidence = (((factor_context.get("factors") or {}).get("liquidity") or {}).get("confidence")) or 0.0
    return "DEGRADED" if confidence < 0.7 else "COMPLETE"


def _build_insights(
    *,
    holding_cards: List[Dict[str, Any]],
    sector_allocation: Dict[str, float],
    factor_distribution: Dict[str, float],
    regime_gate_state: str,
) -> List[Dict[str, Any]]:
    insights: List[Dict[str, Any]] = []
    if sector_allocation:
        dominant_sector = max(sector_allocation, key=sector_allocation.get)
        if sector_allocation[dominant_sector] >= 35.0:
            insights.append(
                {
                    "category": "HIDDEN_CONCENTRATION",
                    "severity": "ORANGE",
                    "headline": f"{dominant_sector} concentration is elevated",
                    "detail": f"{dominant_sector} represents {sector_allocation[dominant_sector]:.2f}% of portfolio weight.",
                    "affected_holdings": [item["ticker"] for item in holding_cards if item["sector"] == dominant_sector],
                }
            )

    if factor_distribution:
        dominant_factor = max(factor_distribution, key=factor_distribution.get)
        if factor_distribution[dominant_factor] >= 0.6:
            insights.append(
                {
                    "category": "FACTOR_IMBALANCE",
                    "severity": "YELLOW",
                    "headline": f"{dominant_factor.title()} factor dominates portfolio",
                    "detail": f"Weighted {dominant_factor} exposure is {factor_distribution[dominant_factor]:.2f}.",
                    "affected_holdings": [item["ticker"] for item in holding_cards],
                }
            )

    if regime_gate_state != "COMPLETE":
        insights.append(
            {
                "category": "MACRO_VULNERABILITY",
                "severity": "YELLOW",
                "headline": "Regime context is degraded",
                "detail": "Conviction and compatibility metrics are capped because canonical macro or factor context is incomplete.",
                "affected_holdings": [item["ticker"] for item in holding_cards],
            }
        )

    for item in holding_cards:
        if item["opportunity_classification"] == "REVIEW_REQUIRED":
            insights.append(
                {
                    "category": "REVIEW_REQUIRED",
                    "severity": "ORANGE",
                    "headline": f"{item['ticker']} requires review",
                    "detail": f"{item['ticker']} has {len(item['risk_flags'])} active risk flags with conviction {item['conviction_score']:.2f}.",
                    "affected_holdings": [item["ticker"]],
                }
            )

    return insights


def _resilience_classification(score: float) -> str:
    if score >= 0.75:
        return "ROBUST"
    if score >= 0.5:
        return "ADEQUATE"
    if score >= 0.25:
        return "VULNERABLE"
    return "FRAGILE"


def _combined_stub(market: str, total_value: float, usd_inr_rate: float) -> Dict[str, Any]:
    if market == "US":
        return {"local_value": total_value, "combined_value_usd": total_value, "fx_source": "NATIVE_USD"}
    if usd_inr_rate > 0:
        return {
            "local_value": total_value,
            "combined_value_usd": round(total_value / usd_inr_rate, 2),
            "fx_source": "PORTFOLIO_USDINR_RATE",
        }
    return {
        "local_value": total_value,
        "combined_value_usd": None,
        "fx_source": "UNAVAILABLE",
        "warning": "USDINR rate unavailable; combined USD normalization is suppressed.",
    }
