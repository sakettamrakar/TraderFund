from __future__ import annotations

from typing import Any, Dict, List


INDIA_SECTOR_PE_BENCHMARKS: Dict[str, float] = {
    "Energy": 15.0,
    "Information Technology": 24.0,
    "Financials": 18.0,
    "Industrials": 28.0,
    "Utilities": 20.0,
    "Healthcare": 22.0,
    "Consumer Staples": 32.0,
    "Consumer Discretionary": 30.0,
    "Basic Materials": 16.0,
}

US_SECTOR_PE_BENCHMARKS: Dict[str, float] = {
    "Information Technology": 28.0,
    "Communication Services": 24.0,
    "Consumer Discretionary": 30.0,
    "Financials": 16.0,
    "Healthcare": 22.0,
    "Industrials": 20.0,
    "Energy": 14.0,
}


class StockResearchEngine:
    """Deterministic stock-level research builder for portfolio holdings."""

    def build_profiles(
        self,
        holdings: List[Dict[str, Any]],
        *,
        market: str,
        macro_context: Dict[str, Any] | None = None,
        regime_gate_state: str = "BLOCKED",
        event_intelligence_map: Dict[str, Dict[str, Any]] | None = None,
    ) -> List[Dict[str, Any]]:
        macro_context = macro_context or {}
        event_intelligence_map = event_intelligence_map or {}
        profiles: List[Dict[str, Any]] = []
        for holding in holdings:
            profiles.append(
                self._build_profile(
                    holding,
                    market=market,
                    macro_context=macro_context,
                    regime_gate_state=regime_gate_state,
                    event_intelligence=event_intelligence_map.get(holding.get("ticker"), {}),
                )
            )
        return profiles

    def _build_profile(
        self,
        holding: Dict[str, Any],
        *,
        market: str,
        macro_context: Dict[str, Any],
        regime_gate_state: str,
        event_intelligence: Dict[str, Any],
    ) -> Dict[str, Any]:
        fundamentals = holding.get("fundamentals", {})
        technicals = holding.get("technicals", {})
        factor_exposure = holding.get("factor_exposure", {})
        pe_ratio = fundamentals.get("pe_ratio")
        sector = holding.get("sector", "UNKNOWN")
        valuation = self._valuation_analysis(pe_ratio=pe_ratio, sector=sector, market=market)
        fundamental_summary = self._fundamental_summary(fundamentals, sector)
        growth_outlook = self._growth_outlook(technicals, factor_exposure)
        profitability_profile = self._profitability_profile(fundamentals, sector)
        balance_sheet_strength = self._balance_sheet_strength(fundamentals, sector)
        technical_structure = self._technical_structure(technicals)
        macro_alignment = self._macro_alignment(holding, macro_context, regime_gate_state)
        risk_flags = self._risk_flags(
            holding,
            valuation_status=valuation["valuation_status"],
            macro_alignment=macro_alignment,
            fundamentals=fundamentals,
            technicals=technicals,
            event_intelligence=event_intelligence,
        )

        return {
            "ticker": holding.get("ticker"),
            "sector": sector,
            "market": market,
            "portfolio_weight": round(float(holding.get("weight_pct", 0.0)), 4),
            "portfolio_role_category": self._portfolio_role_category(holding),
            "fundamental_summary": fundamental_summary,
            "fundamental_outlook": self._fundamental_outlook(fundamentals, technicals, valuation),
            "growth_outlook": growth_outlook,
            "profitability_profile": profitability_profile,
            "balance_sheet_strength": balance_sheet_strength,
            "valuation_status": valuation["valuation_status"],
            "valuation_analysis": valuation,
            "relative_valuation": valuation["relative_valuation"],
            "intrinsic_value_estimate": valuation["intrinsic_value_estimate"],
            "technical_structure": technical_structure,
            "technical_trend": technical_structure["technical_trend"],
            "trend_strength": technical_structure["trend_strength"],
            "volatility_profile": technical_structure["volatility_profile"],
            "macro_sensitivity": self._macro_sensitivity_label(sector),
            "macro_regime_alignment": macro_alignment,
            "factor_exposure": {
                "growth": round(float(factor_exposure.get("growth", 0.0)), 4),
                "value": round(float(factor_exposure.get("value", 0.0)), 4),
                "momentum": round(float(factor_exposure.get("momentum", 0.0)), 4),
                "quality": round(float(factor_exposure.get("quality", 0.0)), 4),
            },
            "risk_flags": risk_flags,
            "opportunity_signals": self._opportunity_signals(
                technicals=technicals,
                valuation_status=valuation["valuation_status"],
                macro_alignment=macro_alignment,
                factor_exposure=factor_exposure,
            ),
            "event_intelligence": event_intelligence,
            "event_risk_flag": bool(event_intelligence.get("event_risk_flag")),
            "monitoring_status": event_intelligence.get("monitoring_status", "NO_ACTIVE_EVENT"),
            "narrative_summary": event_intelligence.get("narrative_summary"),
            "research_narrative": self._research_narrative(
                holding=holding,
                valuation=valuation,
                technical_structure=technical_structure,
                macro_alignment=macro_alignment,
                risk_flags=risk_flags,
                event_intelligence=event_intelligence,
            ),
            "confidence_level": self._confidence_level(pe_ratio, technicals, regime_gate_state),
            "portfolio_role": self._portfolio_role(holding),
            "trace": {
                "source_ticker": holding.get("ticker"),
                "coverage_status": holding.get("coverage_status"),
                "research_engine": "portfolio_intelligence.stock_research_engine",
                "advisory_only": True,
            },
        }

    def _valuation_analysis(self, *, pe_ratio: float | None, sector: str, market: str) -> Dict[str, Any]:
        benchmark_map = INDIA_SECTOR_PE_BENCHMARKS if market == "INDIA" else US_SECTOR_PE_BENCHMARKS
        sector_benchmark = benchmark_map.get(sector)
        if pe_ratio is None or not sector_benchmark:
            return {
                "valuation_status": "unknown",
                "summary": "Valuation coverage incomplete; sector benchmark or PE ratio unavailable.",
                "pe_ratio": pe_ratio,
                "sector_pe_benchmark": sector_benchmark,
                "relative_valuation": "insufficient_data",
                "intrinsic_value_estimate": None,
            }

        premium_pct = ((float(pe_ratio) / sector_benchmark) - 1.0) * 100.0
        if premium_pct <= -15.0:
            status = "undervalued"
        elif premium_pct >= 20.0:
            status = "overvalued"
        else:
            status = "fairly_valued"

        intrinsic_multiple = sector_benchmark * (1.05 if status == "undervalued" else 0.95 if status == "overvalued" else 1.0)
        return {
            "valuation_status": status,
            "summary": f"PE {pe_ratio:.2f} vs sector benchmark {sector_benchmark:.2f} ({premium_pct:+.1f}% premium/discount).",
            "pe_ratio": round(float(pe_ratio), 4),
            "sector_pe_benchmark": round(float(sector_benchmark), 4),
            "relative_valuation": "discount" if premium_pct < 0 else "premium",
            "intrinsic_value_estimate": {
                "method": "sector_pe_anchor",
                "fair_multiple": round(intrinsic_multiple, 4),
                "premium_discount_pct": round(premium_pct, 4),
            },
        }

    def _fundamental_summary(self, fundamentals: Dict[str, Any], sector: str) -> str:
        pe_ratio = fundamentals.get("pe_ratio")
        if pe_ratio is None:
            return f"Fundamental coverage is partial for this {sector.lower()} holding; valuation inputs are limited."
        if pe_ratio < 18:
            return f"Valuation appears disciplined for {sector.lower()} peers, supporting a balanced fundamental profile."
        if pe_ratio > 32:
            return f"Current valuation embeds elevated expectations, leaving less room for execution disappointment."
        return f"Fundamental profile is broadly consistent with sector peers, with no extreme valuation signal."

    def _growth_outlook(self, technicals: Dict[str, Any], factor_exposure: Dict[str, Any]) -> str:
        growth = float(factor_exposure.get("growth", 0.5))
        trend = technicals.get("trend_regime", "UNAVAILABLE")
        if growth >= 0.65 and trend == "BULLISH":
            return "Positive growth backdrop with trend confirmation from recent price structure."
        if growth <= 0.4 and trend == "BEARISH":
            return "Growth outlook is subdued and price action does not currently offset that weakness."
        return "Growth outlook is balanced; further confirmation depends on incoming fundamentals and regime support."

    def _profitability_profile(self, fundamentals: Dict[str, Any], sector: str) -> str:
        pe_ratio = fundamentals.get("pe_ratio")
        if pe_ratio is None:
            return f"Profitability coverage is incomplete; using sector-quality proxy for {sector.lower()} exposure."
        if pe_ratio < 20:
            return "Profitability profile appears efficient relative to current valuation."
        return "Profitability expectations are embedded in valuation and require stable execution to sustain."

    def _balance_sheet_strength(self, fundamentals: Dict[str, Any], sector: str) -> str:
        if sector in {"Financials", "Information Technology", "Consumer Staples"}:
            return "Balance-sheet resilience is inferred as above average based on sector quality profile."
        return "Balance-sheet profile is neutral; explicit leverage and cash-flow coverage remain partially observed."

    def _technical_structure(self, technicals: Dict[str, Any]) -> Dict[str, Any]:
        trend = technicals.get("trend_regime", "UNAVAILABLE")
        momentum = technicals.get("momentum_score")
        volatility_regime = technicals.get("volatility_regime", "UNAVAILABLE")
        if trend == "BULLISH" and (momentum or 0.0) >= 0.6:
            summary = "Trend structure is constructive with supportive momentum."
            strength = "strong"
            technical_trend = "strong uptrend"
        elif trend == "BEARISH":
            summary = "Technical structure is weak; price trend remains unsupportive."
            strength = "weak"
            technical_trend = "downtrend"
        elif trend == "TRANSITION" and (momentum or 0.0) < 0.45:
            summary = "Technical structure is softening and the trend is weakening."
            strength = "balanced"
            technical_trend = "weakening trend"
        else:
            summary = "Technical structure is mixed and needs further confirmation."
            strength = "balanced"
            technical_trend = "consolidation"
        return {
            "summary": summary,
            "trend_regime": trend,
            "trend_strength": strength,
            "technical_trend": technical_trend,
            "momentum_score": momentum,
            "volatility_profile": volatility_regime.lower() if isinstance(volatility_regime, str) else "unknown",
            "return_20d": technicals.get("return_20d"),
        }

    def _macro_alignment(
        self,
        holding: Dict[str, Any],
        macro_context: Dict[str, Any],
        regime_gate_state: str,
    ) -> Dict[str, Any]:
        risk_appetite = ((macro_context.get("risk") or {}).get("appetite") or "UNKNOWN")
        sector = holding.get("sector", "UNKNOWN")
        cyclical = sector in {"Industrials", "Energy", "Financials", "Basic Materials"}
        defensive = sector in {"Healthcare", "Consumer Staples", "Utilities"}
        if regime_gate_state != "COMPLETE":
            score = 0.4
            summary = "Macro alignment is partially observed because regime context is degraded or blocked."
        elif risk_appetite == "HIGH" and cyclical:
            score = 0.78
            summary = "Holding is aligned with a pro-cyclical macro backdrop."
        elif risk_appetite == "MIXED" and defensive:
            score = 0.68
            summary = "Holding offers defensive ballast in a mixed macro backdrop."
        elif risk_appetite == "LOW" and cyclical:
            score = 0.32
            summary = "Holding is exposed to macro downside if the backdrop remains defensive."
        else:
            score = 0.55
            summary = "Macro alignment is balanced rather than strongly directional."
        return {
            "score": round(score, 4),
            "summary": summary,
            "risk_appetite": risk_appetite,
            "regime_gate_state": regime_gate_state,
        }

    def _risk_flags(
        self,
        holding: Dict[str, Any],
        *,
        valuation_status: str,
        macro_alignment: Dict[str, Any],
        fundamentals: Dict[str, Any],
        technicals: Dict[str, Any],
        event_intelligence: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        flags: List[Dict[str, Any]] = []
        weight = float(holding.get("weight_pct", 0.0))
        if weight >= 10.0:
            flags.append({
                "flag": "concentration_risk",
                "explanation": f"Position weight at {weight:.2f}% makes this a top concentration driver.",
                "confidence_level": "HIGH",
            })
        if valuation_status == "overvalued":
            flags.append({
                "flag": "valuation_risk",
                "explanation": "Valuation trades above sector anchor, increasing execution-risk sensitivity.",
                "confidence_level": "MEDIUM",
            })
        if macro_alignment.get("score", 0.0) <= 0.4:
            flags.append({
                "flag": "macro_risk",
                "explanation": macro_alignment.get("summary", "Macro sensitivity is elevated."),
                "confidence_level": "MEDIUM",
            })
        if fundamentals.get("pe_ratio") is None:
            flags.append({
                "flag": "deteriorating_fundamentals",
                "explanation": "Fundamental coverage is partial, reducing confidence in underwriting quality.",
                "confidence_level": "LOW",
            })
        if technicals.get("trend_regime") == "BEARISH":
            flags.append({
                "flag": "weakening_momentum",
                "explanation": "Trend regime is bearish and does not currently support portfolio stability.",
                "confidence_level": "HIGH",
            })
        if event_intelligence.get("event_risk_flag"):
            flags.append({
                "flag": "event_risk_flag",
                "explanation": event_intelligence.get("potential_risk_implications", "Material news flow requires active monitoring."),
                "confidence_level": "MEDIUM",
            })
        return flags

    def _confidence_level(self, pe_ratio: float | None, technicals: Dict[str, Any], regime_gate_state: str) -> str:
        score = 0
        if pe_ratio is not None:
            score += 1
        if technicals.get("momentum_score") is not None:
            score += 1
        if regime_gate_state == "COMPLETE":
            score += 1
        return "HIGH" if score >= 3 else "MEDIUM" if score == 2 else "LOW"

    def _portfolio_role(self, holding: Dict[str, Any]) -> str:
        weight = float(holding.get("weight_pct", 0.0))
        sector = holding.get("sector", "UNKNOWN")
        if weight >= 10.0:
            return f"Core {sector.lower()} exposure"
        if weight >= 4.0:
            return f"Meaningful satellite {sector.lower()} position"
        return f"Tactical residual {sector.lower()} exposure"

    def _portfolio_role_category(self, holding: Dict[str, Any]) -> str:
        weight = float(holding.get("weight_pct", 0.0))
        conviction = float(holding.get("conviction_score", 0.0))
        if weight >= 10.0:
            return "core holding"
        if conviction >= 0.7:
            return "high conviction"
        if weight <= 2.0 or conviction < 0.4:
            return "speculative position"
        return "tactical exposure"

    def _fundamental_outlook(
        self,
        fundamentals: Dict[str, Any],
        technicals: Dict[str, Any],
        valuation: Dict[str, Any],
    ) -> str:
        if valuation.get("valuation_status") == "undervalued" and technicals.get("trend_regime") == "BULLISH":
            return "Constructive outlook with valuation support and healthy trend confirmation."
        if valuation.get("valuation_status") == "overvalued":
            return "Outlook is more dependent on execution strength because valuation already discounts optimism."
        if fundamentals.get("pe_ratio") is None:
            return "Outlook is partially observed; deeper company fundamentals are still needed for stronger conviction."
        return "Outlook is balanced with no extreme fundamental signal overriding the current portfolio role."

    def _macro_sensitivity_label(self, sector: str) -> str:
        if sector in {"Financials", "Utilities"}:
            return "interest_rate_sensitive"
        if sector in {"Industrials", "Materials", "Basic Materials"}:
            return "capex_cycle_sensitive"
        if sector in {"Energy"}:
            return "commodity_sensitive"
        return "consumption_driven"

    def _opportunity_signals(
        self,
        *,
        technicals: Dict[str, Any],
        valuation_status: str,
        macro_alignment: Dict[str, Any],
        factor_exposure: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        signals: List[Dict[str, Any]] = []
        if (technicals.get("momentum_score") or 0.0) >= 0.6 and technicals.get("trend_regime") == "BULLISH":
            signals.append({
                "signal": "improving_technical_trend",
                "explanation": "Momentum and price structure are aligned in a supportive uptrend.",
                "confidence_level": "HIGH",
            })
        if valuation_status == "undervalued":
            signals.append({
                "signal": "valuation_support",
                "explanation": "Relative valuation is favorable versus current sector anchor levels.",
                "confidence_level": "MEDIUM",
            })
        if macro_alignment.get("score", 0.0) >= 0.7:
            signals.append({
                "signal": "favorable_macro_exposure",
                "explanation": "Current macro backdrop is supportive for this holding's sector profile.",
                "confidence_level": "MEDIUM",
            })
        if float(factor_exposure.get("growth", 0.0)) >= 0.65 and float(factor_exposure.get("momentum", 0.0)) >= 0.55:
            signals.append({
                "signal": "strong_earnings_momentum_proxy",
                "explanation": "Growth and momentum factors jointly support a constructive opportunity profile.",
                "confidence_level": "LOW",
            })
        return signals

    def _research_narrative(
        self,
        *,
        holding: Dict[str, Any],
        valuation: Dict[str, Any],
        technical_structure: Dict[str, Any],
        macro_alignment: Dict[str, Any],
        risk_flags: List[Dict[str, Any]],
        event_intelligence: Dict[str, Any],
    ) -> str:
        risk_text = risk_flags[0]["explanation"] if risk_flags else "No dominant stock-level risk flag is active."
        event_text = event_intelligence.get("narrative_summary")
        if not event_text:
            event_text = "No portfolio-relevant event narrative is currently active."
        return (
            f"{holding.get('ticker')} is a {self._portfolio_role(holding).lower()}. "
            f"Valuation is {valuation.get('valuation_status', 'unknown')} relative to sector peers. "
            f"Technical trend is {technical_structure.get('technical_trend', 'mixed')}. "
            f"Macro sensitivity is framed by: {macro_alignment.get('summary', 'macro alignment is balanced')}. "
            f"Primary risk view: {risk_text} "
            f"Event intelligence: {event_text}"
        )