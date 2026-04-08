from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List


class MutualFundResearchEngine:
    """Deterministic research builder for mutual fund sleeve analysis."""

    def build_intelligence(
        self,
        mutual_fund_holdings: List[Dict[str, Any]],
        *,
        total_portfolio_value: float,
    ) -> Dict[str, Any]:
        if not mutual_fund_holdings:
            return {
                "summary": "No mutual fund allocations are currently present.",
                "insights": [],
                "top_fund_narratives": [],
                "allocation_mix": {},
                "fund_profiles": [],
            }

        allocation_mix: Dict[str, float] = defaultdict(float)
        profiles: List[Dict[str, Any]] = []
        sorted_funds = sorted(mutual_fund_holdings, key=lambda item: float(item.get("weight_pct", 0.0)), reverse=True)

        for fund in sorted_funds:
            allocation_mix[fund.get("sector", "Mutual Funds")] += float(fund.get("weight_pct", 0.0))
            profiles.append(self._build_profile(fund))

        total_mf_value = sum(float(item.get("market_value") or 0.0) for item in mutual_fund_holdings)
        mf_alloc_pct = round(total_mf_value / total_portfolio_value * 100.0, 4) if total_portfolio_value else 0.0
        insights = self._build_insights(sorted_funds, allocation_mix)
        top_narratives = [
            {
                "ticker": profile["ticker"],
                "security_name": profile["security_name"],
                "weight_pct": profile["portfolio_weight"],
                "narrative": profile["narrative"],
            }
            for profile in profiles[:5]
        ]

        return {
            "summary": f"Mutual funds account for {mf_alloc_pct:.2f}% of the overall portfolio across {len(mutual_fund_holdings)} holdings.",
            "insights": insights,
            "top_fund_narratives": top_narratives,
            "allocation_mix": {key: round(value, 4) for key, value in allocation_mix.items()},
            "fund_profiles": profiles,
        }

    def _build_profile(self, fund: Dict[str, Any]) -> Dict[str, Any]:
        weight = float(fund.get("weight_pct", 0.0))
        pnl_pct = float(fund.get("pnl_pct", 0.0))
        sector = fund.get("sector", "Mutual Funds")
        industry = fund.get("industry", "Mutual Fund")
        security_name = fund.get("security_name", fund.get("ticker"))

        risk_flags = self._risk_flags(fund)
        opportunity_signals = self._opportunity_signals(fund)
        risk_level = "HIGH" if len(risk_flags) >= 2 or weight >= 20.0 else "MEDIUM" if risk_flags else "LOW"

        return {
            "ticker": fund.get("ticker"),
            "security_name": security_name,
            "portfolio_weight": round(weight, 4),
            "fund_category": sector,
            "strategy_type": industry,
            "portfolio_role": self._portfolio_role(weight, sector),
            "risk_level": risk_level,
            "performance_snapshot": {
                "market_value": round(float(fund.get("market_value") or 0.0), 2),
                "pnl": round(float(fund.get("pnl") or 0.0), 2),
                "pnl_pct": round(pnl_pct, 4),
            },
            "risk_flags": risk_flags,
            "opportunity_signals": opportunity_signals,
            "narrative": self._narrative(security_name, sector, industry, weight, risk_flags, opportunity_signals),
        }

    def _build_insights(self, sorted_funds: List[Dict[str, Any]], allocation_mix: Dict[str, float]) -> List[Dict[str, Any]]:
        insights: List[Dict[str, Any]] = []
        top = sorted_funds[0]
        top_weight = float(top.get("weight_pct", 0.0))
        if top_weight >= 20.0:
            insights.append(
                {
                    "category": "fund_concentration",
                    "headline": f"{top.get('security_name', top.get('ticker'))} dominates fund allocation.",
                    "detail": f"The largest mutual fund contributes {top_weight:.2f}% of total portfolio weight.",
                }
            )
        if allocation_mix.get("Global Funds", 0.0) >= 8.0:
            insights.append(
                {
                    "category": "global_fund_exposure",
                    "headline": "Mutual fund sleeve carries meaningful global diversification exposure.",
                    "detail": f"Global fund allocation contributes {allocation_mix.get('Global Funds', 0.0):.2f}% of total portfolio weight.",
                }
            )
        if allocation_mix.get("Sector Funds", 0.0) >= 10.0:
            insights.append(
                {
                    "category": "sector_fund_concentration",
                    "headline": "Sector-focused funds add thematic concentration to the sleeve.",
                    "detail": f"Sector fund allocation contributes {allocation_mix.get('Sector Funds', 0.0):.2f}% of total portfolio weight.",
                }
            )
        if allocation_mix.get("Hybrid Funds", 0.0) >= 3.0:
            insights.append(
                {
                    "category": "hybrid_ballast",
                    "headline": "Hybrid fund exposure provides some diversification ballast.",
                    "detail": f"Hybrid fund allocation contributes {allocation_mix.get('Hybrid Funds', 0.0):.2f}% of total portfolio weight.",
                }
            )
        return insights

    def _risk_flags(self, fund: Dict[str, Any]) -> List[Dict[str, Any]]:
        flags: List[Dict[str, Any]] = []
        weight = float(fund.get("weight_pct", 0.0))
        pnl_pct = float(fund.get("pnl_pct", 0.0))
        sector = fund.get("sector", "Mutual Funds")
        industry = fund.get("industry", "Mutual Fund")

        if weight >= 15.0:
            flags.append(
                {
                    "flag": "fund_concentration_risk",
                    "explanation": f"Fund weight at {weight:.2f}% makes it a major sleeve concentration driver.",
                }
            )
        if sector == "Sector Funds":
            flags.append(
                {
                    "flag": "thematic_concentration_risk",
                    "explanation": f"{industry} exposure adds thematic concentration to the broader portfolio.",
                }
            )
        if sector == "Global Funds":
            flags.append(
                {
                    "flag": "international_market_risk",
                    "explanation": "Global fund exposure introduces external market and currency path dependence.",
                }
            )
        if pnl_pct <= -5.0:
            flags.append(
                {
                    "flag": "negative_performance_trend",
                    "explanation": f"Fund sleeve performance is weak with PnL at {pnl_pct:.2f}%.",
                }
            )
        return flags

    def _opportunity_signals(self, fund: Dict[str, Any]) -> List[Dict[str, Any]]:
        signals: List[Dict[str, Any]] = []
        pnl_pct = float(fund.get("pnl_pct", 0.0))
        sector = fund.get("sector", "Mutual Funds")
        industry = fund.get("industry", "Mutual Fund")

        if sector == "Global Funds":
            signals.append(
                {
                    "signal": "global_diversification",
                    "explanation": "Global fund exposure diversifies domestic single-market concentration.",
                }
            )
        if sector == "Hybrid Funds":
            signals.append(
                {
                    "signal": "defensive_ballast",
                    "explanation": "Hybrid allocation can reduce sleeve-level volatility versus pure equity funds.",
                }
            )
        if sector == "Sector Funds":
            signals.append(
                {
                    "signal": "thematic_upside",
                    "explanation": f"{industry} exposure can amplify returns if the theme remains supported.",
                }
            )
        if pnl_pct >= 3.0:
            signals.append(
                {
                    "signal": "positive_performance_trend",
                    "explanation": f"Fund sleeve performance is constructive with PnL at {pnl_pct:.2f}%.",
                }
            )
        return signals

    def _portfolio_role(self, weight: float, sector: str) -> str:
        if weight >= 20.0:
            return "core fund anchor"
        if sector == "Global Funds":
            return "global diversification sleeve"
        if sector == "Hybrid Funds":
            return "defensive ballast"
        if sector == "Sector Funds":
            return "thematic satellite"
        return "supporting allocation"

    def _narrative(
        self,
        security_name: str,
        sector: str,
        industry: str,
        weight: float,
        risk_flags: List[Dict[str, Any]],
        opportunity_signals: List[Dict[str, Any]],
    ) -> str:
        lead_risk = risk_flags[0]["explanation"] if risk_flags else "No dominant risk flag is active."
        lead_opportunity = opportunity_signals[0]["explanation"] if opportunity_signals else "No dominant opportunity signal is active."
        return (
            f"{security_name} contributes {weight:.2f}% of portfolio weight through the {sector.lower()} sleeve ({industry.lower()}). "
            f"Primary risk view: {lead_risk} Primary opportunity view: {lead_opportunity}"
        )