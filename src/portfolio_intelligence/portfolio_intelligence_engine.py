from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List


class PortfolioIntelligenceEngine:
    """Aggregates stock research and exposure analytics into portfolio guidance."""

    def build_portfolio_intelligence(
        self,
        *,
        research_profiles: List[Dict[str, Any]],
        exposure_analysis: Dict[str, Any],
        market: str,
        truth_epoch: str,
    ) -> Dict[str, Any]:
        risk_alerts = self._build_risk_alerts(research_profiles, exposure_analysis)
        suggestions = self._build_suggestions(research_profiles, exposure_analysis)
        stock_summaries = [self._stock_summary(profile) for profile in research_profiles]
        valuation_overview = self._valuation_overview(research_profiles)
        return {
            "portfolio_suggestions": suggestions,
            "portfolio_risk_alerts": risk_alerts,
            "stock_research_profiles": research_profiles,
            "stock_intelligence_summaries": stock_summaries,
            "valuation_overview": valuation_overview,
            "trace": {
                "engine": "portfolio_intelligence.portfolio_intelligence_engine",
                "market": market,
                "truth_epoch": truth_epoch,
                "advisory_only": True,
            },
        }

    def _build_risk_alerts(self, research_profiles: List[Dict[str, Any]], exposure_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        alerts: List[Dict[str, Any]] = []
        for profile in research_profiles:
            for flag in profile.get("risk_flags", []):
                alerts.append(
                    {
                        "ticker": profile.get("ticker"),
                        "flag": flag["flag"],
                        "severity": "HIGH" if flag["flag"] in {"concentration_risk", "weak_technical_structure"} else "MEDIUM",
                        "explanation": flag["explanation"],
                        "confidence_level": flag["confidence_level"],
                    }
                )

        exposure_flags = exposure_analysis.get("macro_regime_exposure", {}).get("regime_vulnerability_flags", [])
        for flag in exposure_flags:
            alerts.append(
                {
                    "ticker": None,
                    "flag": "regime_vulnerability",
                    "severity": "MEDIUM",
                    "explanation": flag.replace("_", " ").title(),
                    "confidence_level": "MEDIUM",
                }
            )
        return alerts

    def _build_suggestions(self, research_profiles: List[Dict[str, Any]], exposure_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        suggestions: List[Dict[str, Any]] = []
        sector = exposure_analysis.get("sector_exposure", {})
        metrics = exposure_analysis.get("exposure_metrics", {})
        macro = exposure_analysis.get("macro_regime_exposure", {})
        concentration = exposure_analysis.get("hidden_concentrations", {}).get("sector_concentration", {})

        dominant_sector = sector.get("dominant_sector")
        dominant_weight = concentration.get("dominant_sector_weight", 0.0)
        if dominant_sector and dominant_weight >= 30.0:
            suggestions.append(
                {
                    "category": "sector_overexposure",
                    "headline": f"Portfolio is heavily exposed to {dominant_sector.lower()} sectors.",
                    "detail": f"{dominant_sector} accounts for {dominant_weight:.1f}% of portfolio weight; diversification into non-correlated sectors may improve resilience.",
                    "confidence_level": "HIGH",
                    "advisory_only": True,
                }
            )

        if metrics.get("regime_alignment_score", 1.0) < 0.45:
            suggestions.append(
                {
                    "category": "macro_regime_misalignment",
                    "headline": "Portfolio exposures are not well aligned with the current macro regime.",
                    "detail": "Defensive ballast or reduced cyclical dependence may improve stability while the macro backdrop remains mixed.",
                    "confidence_level": "MEDIUM",
                    "advisory_only": True,
                }
            )

        growth_heavy = [p for p in research_profiles if float(p.get("factor_exposure", {}).get("growth", 0.0)) >= 0.65]
        if len(growth_heavy) >= max(3, len(research_profiles) // 4):
            suggestions.append(
                {
                    "category": "excessive_growth_exposure",
                    "headline": "Portfolio has a pronounced growth tilt.",
                    "detail": "A broader mix of value or defensive quality exposures may reduce factor crowding.",
                    "confidence_level": "MEDIUM",
                    "advisory_only": True,
                }
            )

        if exposure_analysis.get("hidden_concentrations", {}).get("cluster_count", 0) >= 2:
            suggestions.append(
                {
                    "category": "correlated_risk_cluster",
                    "headline": "Multiple correlated clusters increase hidden concentration risk.",
                    "detail": "Holdings with similar sector or factor behavior may weaken diversification during stress episodes.",
                    "confidence_level": "MEDIUM",
                    "advisory_only": True,
                }
            )

        weak_fundamentals = [p for p in research_profiles if any(flag["flag"] == "deteriorating_fundamentals" for flag in p.get("risk_flags", []))]
        if weak_fundamentals:
            tickers = ", ".join(profile["ticker"] for profile in weak_fundamentals[:5])
            suggestions.append(
                {
                    "category": "research_follow_up",
                    "headline": "Certain holdings need deeper fundamental follow-up.",
                    "detail": f"Coverage remains partial for {tickers}; this limits confidence in the portfolio underwrite.",
                    "confidence_level": "LOW",
                    "advisory_only": True,
                }
            )

        return suggestions

    def _stock_summary(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        valuation = profile.get("valuation_analysis", {})
        risk_flags = profile.get("risk_flags", [])
        top_flag = risk_flags[0]["flag"].replace("_", " ") if risk_flags else "no primary flag"
        return {
            "ticker": profile.get("ticker"),
            "portfolio_weight": profile.get("portfolio_weight"),
            "fundamental_view": profile.get("fundamental_summary"),
            "valuation_view": valuation.get("summary"),
            "risk_flags": [flag["flag"] for flag in risk_flags],
            "portfolio_role": profile.get("portfolio_role"),
            "summary": (
                f"{profile.get('ticker')} is a {profile.get('portfolio_role', 'portfolio holding').lower()} with "
                f"{valuation.get('valuation_status', 'unknown')} valuation and {top_flag}."
            ),
        }

    def _valuation_overview(self, research_profiles: List[Dict[str, Any]]) -> Dict[str, Any]:
        counts = Counter(profile.get("valuation_analysis", {}).get("valuation_status", "unknown") for profile in research_profiles)
        return {
            "counts": dict(counts),
            "undervalued": [profile["ticker"] for profile in research_profiles if profile.get("valuation_analysis", {}).get("valuation_status") == "undervalued"],
            "fairly_valued": [profile["ticker"] for profile in research_profiles if profile.get("valuation_analysis", {}).get("valuation_status") == "fairly_valued"],
            "overvalued": [profile["ticker"] for profile in research_profiles if profile.get("valuation_analysis", {}).get("valuation_status") == "overvalued"],
        }