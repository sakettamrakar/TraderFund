"""
Portfolio Exposure Engine — Institutional-Grade Exposure Analytics
===================================================================
Computes portfolio exposures across sectors, industries, geographies,
factors, and macro regime dimensions.  Detects hidden concentration
risks, correlated holdings clusters, and factor imbalances.

Governance:
  - Read-only analytical module (INV-NO-EXECUTION, INV-NO-CAPITAL)
  - All outputs include truth_epoch and data provenance
  - Regime gate state is disclosed on every output (OBL-REGIME-GATE-EXPLICIT)
  - No trade recommendations or capital actions

Markets: US, INDIA
"""
from __future__ import annotations

import math
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple


LOOKTHROUGH_DEFAULTS: Dict[str, List[Dict[str, Any]]] = {
    "Global Funds": [
        {"sector": "Information Technology", "geography": "US", "ratio": 0.55, "factors": {"growth": 0.82, "momentum": 0.78, "quality": 0.68, "macro_sensitivity": 0.62}},
        {"sector": "Communication Services", "geography": "US", "ratio": 0.2, "factors": {"growth": 0.74, "momentum": 0.7, "quality": 0.62, "macro_sensitivity": 0.58}},
        {"sector": "Consumer Discretionary", "geography": "GLOBAL", "ratio": 0.25, "factors": {"growth": 0.69, "momentum": 0.63, "quality": 0.52, "macro_sensitivity": 0.56}},
    ],
    "Sector Funds": [
        {"sector": "Industrials", "geography": "INDIA", "ratio": 0.5, "factors": {"growth": 0.58, "momentum": 0.54, "quality": 0.46, "macro_sensitivity": 0.71}},
        {"sector": "Basic Materials", "geography": "INDIA", "ratio": 0.25, "factors": {"growth": 0.42, "momentum": 0.48, "quality": 0.38, "macro_sensitivity": 0.77}},
        {"sector": "Utilities", "geography": "INDIA", "ratio": 0.25, "factors": {"growth": 0.35, "momentum": 0.36, "quality": 0.45, "macro_sensitivity": 0.61}},
    ],
    "Hybrid Funds": [
        {"sector": "Financials", "geography": "INDIA", "ratio": 0.3, "factors": {"growth": 0.44, "momentum": 0.4, "quality": 0.56, "macro_sensitivity": 0.39}},
        {"sector": "Consumer Staples", "geography": "INDIA", "ratio": 0.25, "factors": {"growth": 0.32, "momentum": 0.35, "quality": 0.59, "macro_sensitivity": 0.28}},
        {"sector": "Healthcare", "geography": "INDIA", "ratio": 0.2, "factors": {"growth": 0.48, "momentum": 0.42, "quality": 0.61, "macro_sensitivity": 0.31}},
        {"sector": "Utilities", "geography": "INDIA", "ratio": 0.25, "factors": {"growth": 0.25, "momentum": 0.26, "quality": 0.53, "macro_sensitivity": 0.24}},
    ],
    "Tax Saver Funds": [
        {"sector": "Financials", "geography": "INDIA", "ratio": 0.25, "factors": {"growth": 0.5, "momentum": 0.46, "quality": 0.5, "macro_sensitivity": 0.47}},
        {"sector": "Information Technology", "geography": "INDIA", "ratio": 0.25, "factors": {"growth": 0.63, "momentum": 0.57, "quality": 0.56, "macro_sensitivity": 0.43}},
        {"sector": "Industrials", "geography": "INDIA", "ratio": 0.25, "factors": {"growth": 0.49, "momentum": 0.44, "quality": 0.42, "macro_sensitivity": 0.59}},
        {"sector": "Consumer Discretionary", "geography": "INDIA", "ratio": 0.25, "factors": {"growth": 0.52, "momentum": 0.49, "quality": 0.41, "macro_sensitivity": 0.53}},
    ],
    "Equity Funds": [
        {"sector": "Financials", "geography": "INDIA", "ratio": 0.3, "factors": {"growth": 0.47, "momentum": 0.45, "quality": 0.5, "macro_sensitivity": 0.48}},
        {"sector": "Industrials", "geography": "INDIA", "ratio": 0.25, "factors": {"growth": 0.51, "momentum": 0.47, "quality": 0.43, "macro_sensitivity": 0.56}},
        {"sector": "Healthcare", "geography": "INDIA", "ratio": 0.2, "factors": {"growth": 0.45, "momentum": 0.41, "quality": 0.54, "macro_sensitivity": 0.34}},
        {"sector": "Consumer Discretionary", "geography": "INDIA", "ratio": 0.25, "factors": {"growth": 0.49, "momentum": 0.46, "quality": 0.4, "macro_sensitivity": 0.51}},
    ],
    "Mutual Funds": [
        {"sector": "Financials", "geography": "INDIA", "ratio": 0.25, "factors": {"growth": 0.43, "momentum": 0.4, "quality": 0.48, "macro_sensitivity": 0.45}},
        {"sector": "Information Technology", "geography": "INDIA", "ratio": 0.2, "factors": {"growth": 0.56, "momentum": 0.52, "quality": 0.55, "macro_sensitivity": 0.41}},
        {"sector": "Industrials", "geography": "INDIA", "ratio": 0.2, "factors": {"growth": 0.46, "momentum": 0.44, "quality": 0.41, "macro_sensitivity": 0.55}},
        {"sector": "Healthcare", "geography": "INDIA", "ratio": 0.15, "factors": {"growth": 0.39, "momentum": 0.37, "quality": 0.53, "macro_sensitivity": 0.32}},
        {"sector": "Consumer Staples", "geography": "INDIA", "ratio": 0.2, "factors": {"growth": 0.28, "momentum": 0.31, "quality": 0.5, "macro_sensitivity": 0.27}},
    ],
}


# ── Exposure Categories ───────────────────────────────────────────────────────

def compute_sector_exposure(holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute portfolio exposure by GICS-style sector."""
    allocation: Dict[str, float] = defaultdict(float)
    value_by_sector: Dict[str, float] = defaultdict(float)
    count_by_sector: Dict[str, int] = defaultdict(int)

    for h in holdings:
        sector = h.get("sector", "UNKNOWN")
        weight = float(h.get("weight_pct", 0.0))
        value = float(h.get("market_value", 0.0))
        allocation[sector] += weight
        value_by_sector[sector] += value
        count_by_sector[sector] += 1

    return {
        "allocation_pct": _round_map(allocation),
        "value_by_sector": _round_map(value_by_sector),
        "count_by_sector": dict(count_by_sector),
        "dominant_sector": max(allocation, key=allocation.get) if allocation else "NONE",
        "sector_count": len(allocation),
        "explainability": {
            "method": "weight_aggregation",
            "input_count": len(holdings),
            "dominant_sector_weight": round(allocation.get(max(allocation, key=allocation.get), 0.0), 4) if allocation else 0.0,
        },
    }


def compute_industry_exposure(holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute portfolio exposure by industry sub-classification."""
    allocation: Dict[str, float] = defaultdict(float)
    count_by_industry: Dict[str, int] = defaultdict(int)

    for h in holdings:
        industry = h.get("industry", "UNKNOWN")
        weight = float(h.get("weight_pct", 0.0))
        allocation[industry] += weight
        count_by_industry[industry] += 1

    return {
        "weight_distribution": _round_map(allocation),
        "count_by_industry": dict(count_by_industry),
        "dominant_industry": max(allocation, key=allocation.get) if allocation else "NONE",
        "industry_count": len(allocation),
    }


def compute_geography_exposure(holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute country and geography exposure distribution."""
    allocation: Dict[str, float] = defaultdict(float)
    value_by_geography: Dict[str, float] = defaultdict(float)

    for h in holdings:
        geography = h.get("geography", h.get("market", "UNKNOWN"))
        weight = float(h.get("weight_pct", 0.0))
        value = float(h.get("market_value", 0.0))
        allocation[geography] += weight
        value_by_geography[geography] += value

    return {
        "country_exposure_pct": _round_map(allocation),
        "value_by_geography": _round_map(value_by_geography),
        "geography_count": len(allocation),
        "dominant_geography": max(allocation, key=allocation.get) if allocation else "NONE",
        "explainability": {
            "method": "weight_aggregation",
            "input_count": len(holdings),
        },
    }


# ── Factor Exposure Decomposition ────────────────────────────────────────────

FACTOR_KEYS = ("growth", "value", "momentum", "quality", "volatility")


def compute_factor_exposure(holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Decompose portfolio factor exposure using weighted-average factor loadings.

    Factor dimensions: growth, value, momentum, quality, volatility (macro_sensitivity).
    """
    factor_sums: Dict[str, float] = defaultdict(float)
    total_weight = 0.0

    for h in holdings:
        weight = float(h.get("weight_pct", 0.0))
        factor_data = h.get("factor_exposure", {})
        total_weight += weight
        for key in FACTOR_KEYS:
            raw = key if key != "volatility" else "macro_sensitivity"
            factor_sums[key] += float(factor_data.get(raw, 0.0)) * weight

    if total_weight <= 0:
        total_weight = 1.0

    weighted_factors = {k: round(v / total_weight, 4) for k, v in factor_sums.items()}
    dominant = max(weighted_factors, key=weighted_factors.get) if weighted_factors else "NONE"

    # Factor balance: how evenly distributed are factor exposures?
    values = list(weighted_factors.values())
    mean_factor = sum(values) / len(values) if values else 0.0
    variance = sum((v - mean_factor) ** 2 for v in values) / len(values) if values else 0.0
    balance_score = round(max(0.0, 1.0 - math.sqrt(variance) * 2.0), 4)

    return {
        "growth_factor": weighted_factors.get("growth", 0.0),
        "value_factor": weighted_factors.get("value", 0.0),
        "momentum_factor": weighted_factors.get("momentum", 0.0),
        "quality_factor": weighted_factors.get("quality", 0.0),
        "volatility_factor": weighted_factors.get("volatility", 0.0),
        "dominant_factor": dominant,
        "factor_balance_score": balance_score,
        "weighted_factors": weighted_factors,
        "explainability": {
            "method": "weighted_average_factor_loading",
            "input_count": len(holdings),
            "total_weight": round(total_weight, 4),
        },
    }


# ── Macro Regime Exposure ─────────────────────────────────────────────────────

def compute_macro_regime_exposure(
    holdings: List[Dict[str, Any]],
    macro_context: Dict[str, Any],
    factor_context: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Evaluate portfolio alignment against current macro regime conditions.

    Sensitivity dimensions:
      - growth regime sensitivity
      - interest rate sensitivity
      - inflation sensitivity
      - liquidity sensitivity
    """
    regime_hint = _infer_regime(macro_context, factor_context)
    risk_appetite = (macro_context.get("risk") or {}).get("appetite", "UNKNOWN")

    # Compute weighted macro sensitivity across holdings
    total_weight = sum(float(h.get("weight_pct", 0.0)) for h in holdings) or 1.0
    weighted_macro_sensitivity = sum(
        float(h.get("factor_exposure", {}).get("macro_sensitivity", 0.5))
        * float(h.get("weight_pct", 0.0))
        for h in holdings
    ) / total_weight

    # Sector-based regime sensitivity heuristics
    sensitive_sectors = {"Energy", "Financials", "Industrials", "Basic Materials", "Utilities"}
    defensive_sectors = {"Consumer Staples", "Healthcare", "Information Technology"}
    sensitive_weight = sum(
        float(h.get("weight_pct", 0.0))
        for h in holdings
        if h.get("sector") in sensitive_sectors
    )
    defensive_weight = sum(
        float(h.get("weight_pct", 0.0))
        for h in holdings
        if h.get("sector") in defensive_sectors
    )

    growth_sensitivity = round(weighted_macro_sensitivity * 0.8, 4)
    rate_sensitivity = round(sensitive_weight / 100.0, 4) if sensitive_weight else 0.0
    inflation_sensitivity = round(
        sum(
            float(h.get("weight_pct", 0.0))
            for h in holdings
            if h.get("sector") in {"Energy", "Basic Materials", "Consumer Staples"}
        ) / 100.0,
        4,
    )
    liquidity_sensitivity = round(
        sum(
            float(h.get("weight_pct", 0.0))
            for h in holdings
            if h.get("liquidity_risk", "MEDIUM") == "MEDIUM"
        ) / 100.0,
        4,
    )

    # Macro alignment score: higher when portfolio tilt matches regime
    alignment = _compute_macro_alignment(
        regime_hint, risk_appetite,
        weighted_macro_sensitivity, sensitive_weight, defensive_weight,
    )

    # Vulnerability flags
    vulnerability_flags = _detect_regime_vulnerabilities(
        regime_hint, risk_appetite,
        sensitive_weight, defensive_weight,
        weighted_macro_sensitivity,
    )

    return {
        "regime_hint": regime_hint,
        "risk_appetite": risk_appetite,
        "growth_regime_sensitivity": growth_sensitivity,
        "interest_rate_sensitivity": rate_sensitivity,
        "inflation_sensitivity": inflation_sensitivity,
        "liquidity_sensitivity": liquidity_sensitivity,
        "macro_alignment_score": alignment,
        "regime_vulnerability_flags": vulnerability_flags,
        "sensitive_sector_weight_pct": round(sensitive_weight, 4),
        "defensive_sector_weight_pct": round(defensive_weight, 4),
        "explainability": {
            "method": "heuristic_regime_alignment",
            "weighted_macro_sensitivity": round(weighted_macro_sensitivity, 4),
            "sensitive_sector_weight_pct": round(sensitive_weight, 4),
            "defensive_sector_weight_pct": round(defensive_weight, 4),
        },
    }


def _infer_regime(
    macro_context: Dict[str, Any],
    factor_context: Dict[str, Any],
) -> str:
    risk = (macro_context.get("risk") or {}).get("appetite")
    factor_strength = (
        (factor_context.get("factors") or {}).get("momentum") or {}
    ).get("strength")
    if risk == "MIXED" and factor_strength == "weak":
        return "DEFENSIVE"
    if risk == "HIGH":
        return "RISK_ON"
    return "BALANCED"


def _compute_macro_alignment(
    regime: str,
    risk_appetite: str,
    macro_sensitivity: float,
    sensitive_weight: float,
    defensive_weight: float,
) -> float:
    """Score how well portfolio composition aligns with macro conditions."""
    if regime == "RISK_ON":
        # Risk-on favors growth/sensitivity tilt
        return round(min(1.0, macro_sensitivity * 1.2), 4)
    if regime == "DEFENSIVE":
        # Defensive favors lower sensitivity
        return round(min(1.0, (1.0 - macro_sensitivity) * 1.1 + defensive_weight / 200.0), 4)
    # Balanced — moderate alignment
    return round(min(1.0, 0.5 + (defensive_weight - sensitive_weight) / 400.0), 4)


def _detect_regime_vulnerabilities(
    regime: str,
    risk_appetite: str,
    sensitive_weight: float,
    defensive_weight: float,
    macro_sensitivity: float,
) -> List[str]:
    flags: List[str] = []
    if regime == "DEFENSIVE" and sensitive_weight > 40.0:
        flags.append("HIGH_CYCLICAL_EXPOSURE_IN_DEFENSIVE_REGIME")
    if regime == "RISK_ON" and defensive_weight > 60.0:
        flags.append("EXCESSIVE_DEFENSIVE_TILT_IN_RISK_ON")
    if macro_sensitivity > 0.75 and regime == "DEFENSIVE":
        flags.append("PORTFOLIO_MACRO_SENSITIVITY_ELEVATED")
    if sensitive_weight > 70.0:
        flags.append("CYCLICAL_CONCENTRATION_RISK")
    return flags


# ── Hidden Concentration Detection ────────────────────────────────────────────

def detect_hidden_concentrations(
    holdings: List[Dict[str, Any]],
    sector_exposure: Dict[str, Any],
    factor_exposure: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Detect non-obvious concentration risks across multiple dimensions:
      - Correlated holdings clusters (same sector)
      - Sector concentration (HHI-based)
      - Factor overexposure (single factor dominance)
    """
    # 1. Correlated holdings clusters: group by sector, flag clusters > 3
    sector_groups: Dict[str, List[str]] = defaultdict(list)
    for h in holdings:
        sector_groups[h.get("sector", "UNKNOWN")].append(h.get("ticker", "?"))
    correlated_clusters = {
        sector: tickers
        for sector, tickers in sector_groups.items()
        if len(tickers) >= 3 and sector != "UNKNOWN"
    }

    # 2. Sector concentration via HHI
    sector_alloc = sector_exposure.get("allocation_pct", {})
    hhi = sum(v ** 2 for v in sector_alloc.values())
    sector_concentration_flag = hhi > 2500  # HHI > 2500 indicates high concentration

    # 3. Factor overexposure: any single factor > 0.7 of the weighted average
    weighted_factors = factor_exposure.get("weighted_factors", {})
    max_factor_value = max(weighted_factors.values()) if weighted_factors else 0.0
    factor_overexposure = max_factor_value > 0.7

    return {
        "correlated_holdings_clusters": {
            sector: {"count": len(tickers), "tickers": tickers}
            for sector, tickers in correlated_clusters.items()
        },
        "sector_concentration": {
            "hhi": round(hhi, 2),
            "concentrated": sector_concentration_flag,
            "dominant_sector": sector_exposure.get("dominant_sector", "NONE"),
            "dominant_sector_weight": round(
                sector_alloc.get(sector_exposure.get("dominant_sector", ""), 0.0), 4
            ),
        },
        "factor_overexposure": {
            "detected": factor_overexposure,
            "max_factor": max(weighted_factors, key=weighted_factors.get) if weighted_factors else "NONE",
            "max_factor_value": round(max_factor_value, 4),
        },
        "cluster_count": len(correlated_clusters),
        "explainability": {
            "sector_hhi_threshold": 2500,
            "factor_overexposure_threshold": 0.7,
            "observed_hhi": round(hhi, 2),
            "max_factor_value": round(max_factor_value, 4),
        },
    }


# ── Composite Exposure Metrics ────────────────────────────────────────────────

def compute_exposure_metrics(
    holdings: List[Dict[str, Any]],
    sector_exposure: Dict[str, Any],
    factor_exposure: Dict[str, Any],
    macro_exposure: Dict[str, Any],
    concentrations: Dict[str, Any],
) -> Dict[str, Any]:
    """Compute composite exposure health metrics."""
    sector_alloc = sector_exposure.get("allocation_pct", {})
    hhi = concentrations.get("sector_concentration", {}).get("hhi", 0.0)

    # Diversification: 1.0 - normalized HHI
    diversification_score = round(max(0.0, 1.0 - hhi / 10000.0), 4)

    # Concentration: penalize top-3 position weight
    weights = sorted(
        [float(h.get("weight_pct", 0.0)) for h in holdings], reverse=True
    )
    top3_weight = sum(weights[:3])
    concentration_score = round(max(0.0, 1.0 - top3_weight / 100.0), 4)

    # Factor balance score
    factor_balance_score = factor_exposure.get("factor_balance_score", 0.5)

    # Regime alignment score
    regime_alignment_score = macro_exposure.get("macro_alignment_score", 0.5)

    return {
        "diversification_score": diversification_score,
        "concentration_score": concentration_score,
        "factor_balance_score": factor_balance_score,
        "regime_alignment_score": regime_alignment_score,
        "composite_health": round(
            (diversification_score + concentration_score + factor_balance_score + regime_alignment_score) / 4.0,
            4,
        ),
        "explainability": {
            "diversification_formula": "1 - sector_hhi/10000",
            "concentration_formula": "1 - top3_weight/100",
            "composite_formula": "mean(diversification, concentration, factor_balance, regime_alignment)",
        },
    }


# ── Exposure Insights ─────────────────────────────────────────────────────────

def generate_exposure_insights(
    sector_exposure: Dict[str, Any],
    industry_exposure: Dict[str, Any],
    factor_exposure: Dict[str, Any],
    macro_exposure: Dict[str, Any],
    concentrations: Dict[str, Any],
    metrics: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Generate advisory insights from exposure analysis.
    Each insight is marked as analytical guidance only.
    """
    insights: List[Dict[str, Any]] = []

    # Sector overconcentration
    dominant_weight = concentrations.get("sector_concentration", {}).get("dominant_sector_weight", 0.0)
    if dominant_weight > 30.0:
        insights.append({
            "category": "sector_overconcentration",
            "severity": "HIGH" if dominant_weight > 50.0 else "MEDIUM",
            "explanation": f"Dominant sector accounts for {dominant_weight:.1f}% of portfolio weight.",
            "exposure_metric": dominant_weight,
            "confidence_level": "HIGH",
            "advisory_only": True,
            "trace": {
                "threshold": 30.0,
                "observed": round(dominant_weight, 4),
                "source": "hidden_concentrations.sector_concentration.dominant_sector_weight",
            },
        })

    # Hidden factor exposure
    if concentrations.get("factor_overexposure", {}).get("detected"):
        max_f = concentrations["factor_overexposure"]["max_factor"]
        max_v = concentrations["factor_overexposure"]["max_factor_value"]
        insights.append({
            "category": "hidden_factor_exposure",
            "severity": "MEDIUM",
            "explanation": f"Portfolio has disproportionate {max_f} factor loading ({max_v:.2f}).",
            "exposure_metric": max_v,
            "confidence_level": "MEDIUM",
            "advisory_only": True,
            "trace": {
                "threshold": 0.7,
                "observed": round(max_v, 4),
                "source": "hidden_concentrations.factor_overexposure.max_factor_value",
            },
        })

    # Regime misalignment
    alignment = macro_exposure.get("macro_alignment_score", 0.5)
    if alignment < 0.4:
        insights.append({
            "category": "regime_misalignment",
            "severity": "HIGH",
            "explanation": f"Portfolio alignment with current macro regime is low ({alignment:.2f}).",
            "exposure_metric": alignment,
            "confidence_level": "MEDIUM",
            "advisory_only": True,
            "trace": {
                "threshold": 0.4,
                "observed": round(alignment, 4),
                "source": "macro_regime_exposure.macro_alignment_score",
            },
        })

    # Diversification gap
    div_score = metrics.get("diversification_score", 0.5)
    if div_score < 0.5:
        insights.append({
            "category": "diversification_gap",
            "severity": "MEDIUM",
            "explanation": f"Portfolio diversification is below target ({div_score:.2f}).",
            "exposure_metric": div_score,
            "confidence_level": "HIGH",
            "advisory_only": True,
            "trace": {
                "threshold": 0.5,
                "observed": round(div_score, 4),
                "source": "exposure_metrics.diversification_score",
            },
        })

    # Correlated risk clusters
    cluster_count = concentrations.get("cluster_count", 0)
    if cluster_count >= 2:
        insights.append({
            "category": "correlated_risk_clusters",
            "severity": "MEDIUM",
            "explanation": f"{cluster_count} correlated holding clusters detected across sectors.",
            "exposure_metric": cluster_count,
            "confidence_level": "MEDIUM",
            "advisory_only": True,
            "trace": {
                "threshold": 2,
                "observed": cluster_count,
                "source": "hidden_concentrations.cluster_count",
            },
        })

    # Regime vulnerability
    vuln_flags = macro_exposure.get("regime_vulnerability_flags", [])
    for flag in vuln_flags:
        insights.append({
            "category": "regime_vulnerability",
            "severity": "MEDIUM",
            "explanation": f"Regime vulnerability detected: {flag.replace('_', ' ').lower()}.",
            "exposure_metric": flag,
            "confidence_level": "MEDIUM",
            "advisory_only": True,
            "trace": {
                "source": "macro_regime_exposure.regime_vulnerability_flags",
                "flag": flag,
            },
        })

    return insights


# ── Main Engine ───────────────────────────────────────────────────────────────

class PortfolioExposureEngine:
    """
    Institutional-grade Portfolio Exposure Engine.

    Computes sector, industry, geography, factor, and macro regime exposures.
    Detects hidden concentration risks and generates exposure insights.

    Invariants:
      - INV-NO-EXECUTION: no trade or order actions
      - INV-NO-CAPITAL: no capital allocation
      - INV-READ-ONLY-DASHBOARD: outputs are observer-only
    """

    def compute_full_exposure(
        self,
        holdings: List[Dict[str, Any]],
        *,
        mutual_fund_holdings: Optional[List[Dict[str, Any]]] = None,
        macro_context: Optional[Dict[str, Any]] = None,
        factor_context: Optional[Dict[str, Any]] = None,
        portfolio_id: str = "",
        market: str = "",
        truth_epoch: str = "",
        data_as_of: str = "",
    ) -> Dict[str, Any]:
        """
        Compute the complete exposure analysis for a portfolio.

        Returns a structured payload containing all exposure categories,
        hidden concentration detection, composite metrics, and insights.
        """
        macro_ctx = macro_context or {}
        factor_ctx = factor_context or {}
        mutual_funds = mutual_fund_holdings or []
        lookthrough_holdings = _expand_mutual_fund_lookthrough(mutual_funds, market=market)
        exposure_holdings = holdings + lookthrough_holdings

        sector_exp = compute_sector_exposure(exposure_holdings)
        industry_exp = compute_industry_exposure(exposure_holdings)
        geography_exp = compute_geography_exposure(exposure_holdings)
        factor_exp = compute_factor_exposure(exposure_holdings)
        macro_exp = compute_macro_regime_exposure(exposure_holdings, macro_ctx, factor_ctx)
        concentrations = detect_hidden_concentrations(exposure_holdings, sector_exp, factor_exp)
        exposure_metrics = compute_exposure_metrics(
            exposure_holdings, sector_exp, factor_exp, macro_exp, concentrations,
        )
        insights = generate_exposure_insights(
            sector_exp, industry_exp, factor_exp, macro_exp, concentrations, exposure_metrics,
        )

        return {
            "portfolio_id": portfolio_id,
            "market": market,
            "truth_epoch": truth_epoch,
            "data_as_of": data_as_of,
            "computed_at": datetime.now(timezone.utc).isoformat(),
            "lookthrough_summary": {
                "mutual_fund_input_count": len(mutual_funds),
                "synthetic_lookthrough_rows": len(lookthrough_holdings),
                "lookthrough_enabled": bool(mutual_funds),
                "real_disclosure_funds": sum(1 for fund in mutual_funds if str(fund.get("lookthrough_mode")) == "UNDERLYING_DISCLOSURE"),
                "benchmark_linked_funds": sum(1 for fund in mutual_funds if str(fund.get("lookthrough_mode")) == "BENCHMARK_COMPOSITION"),
                "fallback_funds": sum(1 for fund in mutual_funds if str(fund.get("lookthrough_mode")) == "HEURISTIC_FALLBACK"),
                "blocked_funds": sum(1 for fund in mutual_funds if str(fund.get("lookthrough_mode")) == "UNAVAILABLE"),
            },
            "sector_exposure": sector_exp,
            "industry_exposure": industry_exp,
            "geography_exposure": geography_exp,
            "factor_exposure": factor_exp,
            "macro_regime_exposure": macro_exp,
            "hidden_concentrations": concentrations,
            "exposure_metrics": exposure_metrics,
            "exposure_insights": insights,
            "trace": {
                "engine": "portfolio_intelligence.exposure_engine",
                "version": "1.0.0",
                "advisory_only": True,
                "input_holdings": len(holdings),
                "lookthrough_rows": len(lookthrough_holdings),
            },
        }


# ── Utilities ─────────────────────────────────────────────────────────────────

def _round_map(values: Dict[str, float]) -> Dict[str, float]:
    return {k: round(v, 4) for k, v in values.items()}


def _expand_mutual_fund_lookthrough(mutual_fund_holdings: List[Dict[str, Any]], *, market: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for fund in mutual_fund_holdings:
        mix, lookthrough_mode = _lookthrough_mix_for_fund(fund, market=market)
        fund["lookthrough_mode"] = lookthrough_mode
        for idx, slice_info in enumerate(mix):
            ratio_weight = float(slice_info.get("underlying_weight") or slice_info.get("ratio") or 0.0)
            rows.append(
                {
                    "ticker": slice_info.get("underlying_ticker") or f"{fund.get('ticker', 'MF')}_LT_{idx + 1}",
                    "sector": slice_info.get("sector", "UNKNOWN"),
                    "industry": slice_info.get("industry", fund.get("industry", "LOOKTHROUGH")),
                    "geography": slice_info.get("geography", market),
                    "market": fund.get("market", market),
                    "weight_pct": round(float(fund.get("weight_pct", 0.0)) * ratio_weight / 100.0 if ratio_weight > 1 else float(fund.get("weight_pct", 0.0)) * ratio_weight, 4),
                    "market_value": round(float(fund.get("market_value", 0.0)) * ratio_weight / 100.0 if ratio_weight > 1 else float(fund.get("market_value", 0.0)) * ratio_weight, 2),
                    "factor_exposure": slice_info.get("factor_profile") or slice_info.get("factor_exposure") or slice_info.get("factors", {}),
                    "liquidity_risk": "LOW" if slice_info.get("geography", market) in {"US", "GLOBAL"} else "MEDIUM",
                    "lookthrough_source": fund.get("ticker"),
                    "trace": {
                        "source": "portfolio_intelligence.exposure_engine.lookthrough",
                        "fund_ticker": fund.get("ticker"),
                        "fund_category": fund.get("sector"),
                        "lookthrough_mode": lookthrough_mode,
                        "benchmark_reference": fund.get("benchmark_reference"),
                    },
                }
            )
    return rows


def _lookthrough_mix_for_fund(fund: Dict[str, Any], *, market: str) -> tuple[List[Dict[str, Any]], str]:
    actual_underlyings = fund.get("underlying_holdings") or []
    if actual_underlyings:
        return actual_underlyings, str(fund.get("lookthrough_mode") or "UNDERLYING_DISCLOSURE")
    category = fund.get("sector", "Mutual Funds")
    security_name = str(fund.get("security_name") or "").upper()
    if category == "Global Funds" and "CHINA" in security_name:
        return [
            {"sector": "Consumer Discretionary", "geography": "CHINA", "ratio": 0.45, "industry": "China Consumer", "factors": {"growth": 0.71, "momentum": 0.6, "quality": 0.46, "macro_sensitivity": 0.67}},
            {"sector": "Communication Services", "geography": "CHINA", "ratio": 0.3, "industry": "China Internet", "factors": {"growth": 0.69, "momentum": 0.58, "quality": 0.42, "macro_sensitivity": 0.7}},
            {"sector": "Information Technology", "geography": "CHINA", "ratio": 0.25, "industry": "China Technology", "factors": {"growth": 0.73, "momentum": 0.62, "quality": 0.48, "macro_sensitivity": 0.68}},
        ], "HEURISTIC_FALLBACK"
    base = LOOKTHROUGH_DEFAULTS.get(category) or LOOKTHROUGH_DEFAULTS["Mutual Funds"]
    return [
        {
            **item,
            "geography": market if item["geography"] == "INDIA" and market else item["geography"],
        }
        for item in base
    ], "HEURISTIC_FALLBACK"
