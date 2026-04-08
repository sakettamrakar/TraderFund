from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def _check(label: str, passed: bool, detail: str) -> dict:
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {label} — {detail}")
    return {"check": label, "status": status, "detail": detail}


def validate_stock_research_engine() -> dict:
    try:
        from src.dashboard.backend.loaders.portfolio import load_portfolio_research

        payload = load_portfolio_research("INDIA", "zerodha_primary")
        profiles = payload.get("stock_research_profiles", [])
        first = profiles[0] if profiles else {}
        required = {
            "ticker",
            "sector",
            "market",
            "portfolio_weight",
            "portfolio_role_category",
            "fundamental_summary",
            "fundamental_outlook",
            "growth_outlook",
            "profitability_profile",
            "balance_sheet_strength",
            "valuation_status",
            "valuation_analysis",
            "technical_structure",
            "technical_trend",
            "macro_sensitivity",
            "macro_regime_alignment",
            "factor_exposure",
            "risk_flags",
            "opportunity_signals",
            "research_narrative",
        }
        missing = sorted(required - set(first.keys())) if first else sorted(required)
        return _check(
            "STOCK_INTELLIGENCE_UPDATED",
            bool(profiles) and not missing,
            f"profiles={len(profiles)}, missing={missing or 'NONE'}",
        )
    except Exception as exc:
        return _check("STOCK_INTELLIGENCE_UPDATED", False, str(exc))


def validate_lookthrough_ingestion() -> dict:
    try:
        from src.dashboard.backend.loaders.portfolio import load_portfolio_holdings

        payload = load_portfolio_holdings("INDIA", "zerodha_primary")
        funds = payload.get("mutual_fund_holdings", [])
        passed = bool(funds) and all("benchmark_reference" in fund and "lookthrough_status" in fund for fund in funds)
        return _check(
            "LOOKTHROUGH_DATA_INGESTION_OK",
            passed,
            f"funds={len(funds)}",
        )
    except Exception as exc:
        return _check("LOOKTHROUGH_DATA_INGESTION_OK", False, str(exc))


def validate_exposure_engine_lookthrough() -> dict:
    try:
        from src.dashboard.backend.loaders.portfolio import load_portfolio_exposure

        payload = load_portfolio_exposure("INDIA", "zerodha_primary")
        summary = payload.get("lookthrough_summary", {})
        insights = payload.get("exposure_insights", [])
        passed = bool(summary.get("lookthrough_enabled")) and all(item.get("trace") for item in insights)
        return _check(
            "EXPOSURE_ENGINE_LOOKTHROUGH_OK",
            passed,
            f"summary={summary}",
        )
    except Exception as exc:
        return _check("EXPOSURE_ENGINE_LOOKTHROUGH_OK", False, str(exc))


def validate_portfolio_intelligence_layer() -> dict:
    try:
        from src.dashboard.backend.loaders.portfolio import load_portfolio_advisory

        payload = load_portfolio_advisory("INDIA", "zerodha_primary")
        suggestions = payload.get("portfolio_suggestions", [])
        alerts = payload.get("portfolio_risk_alerts", [])
        summary = payload.get("portfolio_strategy_summary", {})
        opportunity_signals = payload.get("portfolio_opportunity_signals", [])
        narrative = payload.get("research_synthesis", {})
        passed = bool(suggestions or alerts) and bool(narrative.get("portfolio_narrative")) and bool(summary) and bool(opportunity_signals)
        return _check(
            "PORTFOLIO_STRATEGY_ENGINE_OK",
            passed,
            f"suggestions={len(suggestions)}, alerts={len(alerts)}, summary={bool(summary)}, opportunity_signals={len(opportunity_signals)}",
        )
    except Exception as exc:
        return _check("PORTFOLIO_STRATEGY_ENGINE_OK", False, str(exc))


def validate_dashboard_panels() -> dict:
    try:
        panel_path = PROJECT_ROOT / "src" / "dashboard" / "frontend" / "src" / "components" / "PortfolioIntelligencePanel.jsx"
        content = panel_path.read_text(encoding="utf-8")
        required_tokens = [
            "PortfolioRiskAlertsPanel",
            "PortfolioSuggestionsPanel",
            "PortfolioStrategySummaryPanel",
            "OpportunitySignalsPanel",
            "ValuationOverviewPanel",
            "StockResearchPanel",
            "PortfolioTrendPanel",
            "LookthroughCoveragePanel",
        ]
        missing = [token for token in required_tokens if token not in content]
        return _check(
            "DASHBOARD_LOOKTHROUGH_ANALYTICS_OK",
            not missing,
            f"missing={missing or 'NONE'}",
        )
    except Exception as exc:
        return _check("DASHBOARD_LOOKTHROUGH_ANALYTICS_OK", False, str(exc))


def main() -> int:
    results = [
        validate_lookthrough_ingestion(),
        validate_exposure_engine_lookthrough(),
        validate_stock_research_engine(),
        validate_portfolio_intelligence_layer(),
        validate_dashboard_panels(),
    ]
    overall = all(item["status"] == "PASS" for item in results)
    print(json.dumps({"results": results, "overall": "PASS" if overall else "FAIL"}, indent=2))
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())