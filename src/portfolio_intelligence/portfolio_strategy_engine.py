from __future__ import annotations

from typing import Any, Dict, List


class PortfolioStrategyEngine:
    """Converts portfolio analytics into concrete advisory-only strategy guidance."""

    def build_strategy_package(
        self,
        *,
        research_profiles: List[Dict[str, Any]],
        mutual_fund_intelligence: Dict[str, Any],
        exposure_analysis: Dict[str, Any],
        macro_context: Dict[str, Any],
        factor_context: Dict[str, Any],
        market: str,
        truth_epoch: str,
    ) -> Dict[str, Any]:
        summary = self._strategy_summary(research_profiles, mutual_fund_intelligence, exposure_analysis, macro_context)
        suggestions = self._strategy_suggestions(research_profiles, mutual_fund_intelligence, exposure_analysis, macro_context, factor_context)
        risk_alerts = self._risk_alerts(research_profiles, mutual_fund_intelligence, exposure_analysis)
        opportunity_signals = self._opportunity_signals(research_profiles, mutual_fund_intelligence)
        strengthening_insights = self._strengthening_insights(exposure_analysis, research_profiles, mutual_fund_intelligence)
        return {
            "portfolio_strategy_summary": summary,
            "portfolio_strategy_suggestions": suggestions,
            "portfolio_risk_alerts": risk_alerts,
            "portfolio_opportunity_signals": opportunity_signals,
            "portfolio_strengthening_insights": strengthening_insights,
            "trace": {
                "engine": "portfolio_intelligence.portfolio_strategy_engine",
                "market": market,
                "truth_epoch": truth_epoch,
                "advisory_only": True,
            },
        }

    def _strategy_summary(
        self,
        research_profiles: List[Dict[str, Any]],
        mutual_fund_intelligence: Dict[str, Any],
        exposure_analysis: Dict[str, Any],
        macro_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        concentration = exposure_analysis.get("hidden_concentrations", {}).get("sector_concentration", {})
        dominant_sector = concentration.get("dominant_sector") or exposure_analysis.get("sector_exposure", {}).get("dominant_sector", "UNKNOWN")
        dominant_weight = concentration.get("dominant_sector_weight", 0.0)
        regime_alignment = exposure_analysis.get("exposure_metrics", {}).get("regime_alignment_score", 0.0)
        resilience = exposure_analysis.get("exposure_metrics", {}).get("composite_health", 0.0)
        risk_appetite = ((macro_context.get("risk") or {}).get("appetite") or "UNKNOWN")
        mf_summary = mutual_fund_intelligence.get("summary", "")
        mf_profiles = mutual_fund_intelligence.get("fund_profiles", [])
        hybrid_ballast = any(profile.get("fund_category") == "Hybrid Funds" for profile in mf_profiles)
        global_diversification = any(profile.get("fund_category") == "Global Funds" for profile in mf_profiles)

        adjusted_resilience = resilience
        if hybrid_ballast:
            adjusted_resilience += 0.04
        if global_diversification:
            adjusted_resilience += 0.03
        if any(profile.get("risk_level") == "HIGH" for profile in mf_profiles):
            adjusted_resilience -= 0.03
        adjusted_resilience = max(0.0, min(1.0, adjusted_resilience))

        narrative = (
            f"Portfolio resilience is {'strong' if adjusted_resilience >= 0.7 else 'moderate' if adjusted_resilience >= 0.45 else 'fragile'} "
            f"with dominant exposure to {dominant_sector.lower()} at {dominant_weight:.1f}% of weight. "
            f"Macro compatibility is {'supportive' if regime_alignment >= 0.6 else 'mixed' if regime_alignment >= 0.4 else 'weak'} "
            f"against the current {risk_appetite.lower()} backdrop. "
            f"Mutual fund sleeve context: {mf_summary}"
        )
        return {
            "resilience_assessment": narrative,
            "sector_concentration_analysis": f"{dominant_sector} is the largest sector bucket and shapes portfolio cyclicality.",
            "macro_regime_compatibility": f"Regime alignment score is {regime_alignment:.2f}, indicating {'good' if regime_alignment >= 0.6 else 'partial' if regime_alignment >= 0.4 else 'weak'} compatibility with the current macro state.",
            "factor_imbalance_detection": self._factor_imbalance_text(exposure_analysis),
            "mutual_fund_sleeve_assessment": mf_summary or "No mutual fund sleeve influence detected.",
        }

    def _strategy_suggestions(
        self,
        research_profiles: List[Dict[str, Any]],
        mutual_fund_intelligence: Dict[str, Any],
        exposure_analysis: Dict[str, Any],
        macro_context: Dict[str, Any],
        factor_context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        suggestions: List[Dict[str, Any]] = []
        concentration = exposure_analysis.get("hidden_concentrations", {}).get("sector_concentration", {})
        dominant_sector = concentration.get("dominant_sector") or exposure_analysis.get("sector_exposure", {}).get("dominant_sector")
        dominant_weight = concentration.get("dominant_sector_weight", 0.0)
        if dominant_sector and dominant_weight >= 30.0:
            suggestions.append(
                self._prescriptive_suggestion(
                    "diversify_sector_exposure",
                    f"Portfolio is heavily concentrated in {dominant_sector.lower()} sectors.",
                    "Consider diversifying exposure toward defensive sectors such as healthcare or consumer staples to improve resilience.",
                    "HIGH",
                    trace={
                        "threshold": 30.0,
                        "observed": round(dominant_weight, 4),
                        "source": "exposure_analysis.hidden_concentrations.sector_concentration.dominant_sector_weight",
                    },
                )
            )

        top_name, top_weight = self._largest_position(research_profiles)
        if top_name and top_weight >= 12.0:
            suggestions.append(
                self._prescriptive_suggestion(
                    "reduce_concentration",
                    f"{top_name} contributes disproportionate portfolio risk at {top_weight:.1f}% weight.",
                    "Gradual reduction of concentration or balancing with non-correlated holdings may reduce single-name risk.",
                    "HIGH",
                    trace={
                        "threshold": 12.0,
                        "observed": round(top_weight, 4),
                        "source": "research_profiles.portfolio_weight",
                        "ticker": top_name,
                    },
                )
            )

        regime_alignment = exposure_analysis.get("exposure_metrics", {}).get("regime_alignment_score", 1.0)
        if regime_alignment < 0.45:
            suggestions.append(
                self._prescriptive_suggestion(
                    "strengthen_defensive_allocation",
                    "Portfolio macro compatibility is weak in the current regime.",
                    "Adding more defensive ballast or reducing macro-sensitive cyclicals may improve stability under slower growth conditions.",
                    "MEDIUM",
                    trace={
                        "threshold": 0.45,
                        "observed": round(regime_alignment, 4),
                        "source": "exposure_analysis.exposure_metrics.regime_alignment_score",
                    },
                )
            )

        overvalued = [profile["ticker"] for profile in research_profiles if profile.get("valuation_status") == "overvalued"]
        if overvalued:
            suggestions.append(
                self._prescriptive_suggestion(
                    "review_overvalued_positions",
                    "Several holdings trade above their current sector valuation anchors.",
                    f"Review overvalued positions such as {', '.join(overvalued[:5])} for risk/reward balance if macro conditions deteriorate.",
                    "MEDIUM",
                    trace={
                        "observed": len(overvalued),
                        "source": "research_profiles.valuation_status=overvalued",
                        "tickers": overvalued[:5],
                    },
                )
            )

        macro_sensitive = [profile["ticker"] for profile in research_profiles if profile.get("macro_sensitivity") in {"interest_rate_sensitive", "capex_cycle_sensitive", "commodity_sensitive"}]
        if len(macro_sensitive) >= max(4, len(research_profiles) // 5):
            suggestions.append(
                self._prescriptive_suggestion(
                    "review_macro_sensitive_holdings",
                    "Portfolio contains a meaningful cluster of macro-sensitive holdings.",
                    f"Review macro-sensitive names such as {', '.join(macro_sensitive[:5])} to ensure the portfolio is not overly exposed to one economic path.",
                    "MEDIUM",
                    trace={
                        "threshold": max(4, len(research_profiles) // 5),
                        "observed": len(macro_sensitive),
                        "source": "research_profiles.macro_sensitivity",
                        "tickers": macro_sensitive[:5],
                    },
                )
            )

        mf_profiles = mutual_fund_intelligence.get("fund_profiles", [])
        high_risk_funds = [profile for profile in mf_profiles if profile.get("risk_level") == "HIGH"]
        if high_risk_funds:
            names = ", ".join(profile.get("security_name", profile.get("ticker")) for profile in high_risk_funds[:3])
            suggestions.append(
                self._prescriptive_suggestion(
                    "review_fund_concentration",
                    "Mutual fund sleeve contains concentrated or thematic risk.",
                    f"Review high-risk fund exposures such as {names} to avoid hidden sleeve concentration overwhelming direct equity diversification.",
                    "MEDIUM",
                    trace={
                        "observed": len(high_risk_funds),
                        "source": "mutual_fund_intelligence.fund_profiles.risk_level=HIGH",
                        "funds": [profile.get("ticker") for profile in high_risk_funds[:3]],
                    },
                )
            )

        has_hybrid = any(profile.get("fund_category") == "Hybrid Funds" for profile in mf_profiles)
        regime_alignment = exposure_analysis.get("exposure_metrics", {}).get("regime_alignment_score", 1.0)
        if regime_alignment < 0.45 and not has_hybrid:
            suggestions.append(
                self._prescriptive_suggestion(
                    "add_defensive_ballast",
                    "Portfolio lacks sufficient defensive ballast while macro alignment is weak.",
                    "A hybrid or less cyclical fund sleeve could improve resilience when direct equity exposure is macro-sensitive.",
                    "MEDIUM",
                    trace={
                        "threshold": 0.45,
                        "observed": round(regime_alignment, 4),
                        "source": "exposure_analysis.exposure_metrics.regime_alignment_score",
                        "hybrid_present": has_hybrid,
                    },
                )
            )

        global_mix = float((mutual_fund_intelligence.get("allocation_mix") or {}).get("Global Funds", 0.0))
        if global_mix >= 8.0:
            suggestions.append(
                self._prescriptive_suggestion(
                    "preserve_global_diversification",
                    "Global fund exposure is providing meaningful geographic diversification.",
                    "Avoid removing all global fund exposure unless you intend to increase domestic concentration elsewhere in the portfolio.",
                    "LOW",
                    trace={
                        "threshold": 8.0,
                        "observed": round(global_mix, 4),
                        "source": "mutual_fund_intelligence.allocation_mix.Global Funds",
                    },
                )
            )
        
        return suggestions

    def _risk_alerts(
        self,
        research_profiles: List[Dict[str, Any]],
        mutual_fund_intelligence: Dict[str, Any],
        exposure_analysis: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        alerts: List[Dict[str, Any]] = []
        for profile in research_profiles:
            for flag in profile.get("risk_flags", []):
                alerts.append(
                    {
                        "ticker": profile.get("ticker"),
                        "flag": flag.get("flag"),
                        "severity": "HIGH" if flag.get("flag") in {"concentration_risk", "weakening_momentum"} else "MEDIUM",
                        "explanation": flag.get("explanation"),
                        "confidence_level": flag.get("confidence_level"),
                        "trace": {"source": "research_profiles.risk_flags", "ticker": profile.get("ticker")},
                    }
                )
        for flag in exposure_analysis.get("macro_regime_exposure", {}).get("regime_vulnerability_flags", []):
            alerts.append(
                {
                    "ticker": None,
                    "flag": "regime_vulnerability",
                    "severity": "MEDIUM",
                    "explanation": flag.replace("_", " ").lower(),
                    "confidence_level": "MEDIUM",
                    "trace": {"source": "exposure_analysis.macro_regime_exposure.regime_vulnerability_flags", "flag": flag},
                }
            )
        for profile in mutual_fund_intelligence.get("fund_profiles", []):
            for flag in profile.get("risk_flags", []):
                alerts.append(
                    {
                        "ticker": profile.get("ticker"),
                        "flag": flag.get("flag"),
                        "severity": "HIGH" if flag.get("flag") in {"fund_concentration_risk", "thematic_concentration_risk"} else "MEDIUM",
                        "explanation": flag.get("explanation"),
                        "confidence_level": "MEDIUM",
                        "trace": {"source": "mutual_fund_intelligence.fund_profiles.risk_flags", "ticker": profile.get("ticker")},
                    }
                )
        return alerts

    def _opportunity_signals(self, research_profiles: List[Dict[str, Any]], mutual_fund_intelligence: Dict[str, Any]) -> List[Dict[str, Any]]:
        signals: List[Dict[str, Any]] = []
        for profile in research_profiles:
            for signal in profile.get("opportunity_signals", []):
                signals.append(
                    {
                        "ticker": profile.get("ticker"),
                        "portfolio_role": profile.get("portfolio_role_category"),
                        "signal": signal.get("signal"),
                        "explanation": signal.get("explanation"),
                        "confidence_level": signal.get("confidence_level"),
                        "trace": {"source": "research_profiles.opportunity_signals", "ticker": profile.get("ticker")},
                    }
                )
        for profile in mutual_fund_intelligence.get("fund_profiles", []):
            for signal in profile.get("opportunity_signals", []):
                signals.append(
                    {
                        "ticker": profile.get("ticker"),
                        "portfolio_role": profile.get("portfolio_role"),
                        "signal": signal.get("signal"),
                        "explanation": signal.get("explanation"),
                        "confidence_level": "MEDIUM",
                        "trace": {"source": "mutual_fund_intelligence.fund_profiles.opportunity_signals", "ticker": profile.get("ticker")},
                    }
                )
        return signals[:20]

    def _strengthening_insights(
        self,
        exposure_analysis: Dict[str, Any],
        research_profiles: List[Dict[str, Any]],
        mutual_fund_intelligence: Dict[str, Any],
    ) -> List[str]:
        insights: List[str] = []
        diversification = exposure_analysis.get("exposure_metrics", {}).get("diversification_score", 0.0)
        if diversification < 0.55:
            insights.append("Diversification remains below target; adding low-correlation exposures would strengthen portfolio resilience.")
        if exposure_analysis.get("hidden_concentrations", {}).get("cluster_count", 0) >= 2:
            insights.append("Correlated sector clusters reduce the portfolio's effective diversification during stress periods.")
        favorable = sum(1 for profile in research_profiles if profile.get("macro_regime_alignment", {}).get("score", 0.0) >= 0.7)
        if favorable >= 3:
            insights.append("Several holdings remain aligned with the current macro regime, providing a base for portfolio resilience.")
        if any(profile.get("fund_category") == "Global Funds" for profile in mutual_fund_intelligence.get("fund_profiles", [])):
            insights.append("Global mutual fund exposure improves geographic diversification beyond the direct equity sleeve.")
        if any(profile.get("fund_category") == "Hybrid Funds" for profile in mutual_fund_intelligence.get("fund_profiles", [])):
            insights.append("Hybrid mutual fund allocation provides defensive ballast that can soften direct equity volatility.")
        return insights

    def _factor_imbalance_text(self, exposure_analysis: Dict[str, Any]) -> str:
        factor_exposure = exposure_analysis.get("factor_exposure", {})
        dominant = factor_exposure.get("dominant_factor", "unknown")
        balance = exposure_analysis.get("exposure_metrics", {}).get("factor_balance_score", 0.0)
        return f"Dominant factor is {dominant}; factor balance score is {balance:.2f}, indicating {'balanced' if balance >= 0.6 else 'some crowding'} factor posture."

    def _largest_position(self, research_profiles: List[Dict[str, Any]]) -> tuple[str | None, float]:
        if not research_profiles:
            return None, 0.0
        top = max(research_profiles, key=lambda item: float(item.get("portfolio_weight", 0.0)))
        return top.get("ticker"), float(top.get("portfolio_weight", 0.0))

    def _prescriptive_suggestion(self, category: str, headline: str, detail: str, confidence: str, trace: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return {
            "category": category,
            "headline": headline,
            "detail": detail,
            "confidence_level": confidence,
            "advisory_only": True,
            "trace": trace or {},
        }