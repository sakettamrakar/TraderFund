"""
Post-Implementation Validation — Portfolio Exposure Engine
==========================================================
Validates that all exposure engine components are operational,
metrics compute correctly, and dashboard endpoints respond.

Governance: INV-READ-ONLY-DASHBOARD, INV-NO-EXECUTION
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def _check(label: str, passed: bool, detail: str = "") -> Dict[str, Any]:
    status = "PASS" if passed else "FAIL"
    print(f"  [{status}] {label}" + (f" — {detail}" if detail else ""))
    return {"check": label, "status": status, "detail": detail}


def validate_exposure_engine_importable() -> Dict[str, Any]:
    """Phase 7.1: Verify exposure engine module imports cleanly."""
    try:
        from src.portfolio_intelligence.exposure_engine import PortfolioExposureEngine
        engine = PortfolioExposureEngine()
        return _check("exposure_engine_importable", True, "PortfolioExposureEngine instantiated")
    except Exception as exc:
        return _check("exposure_engine_importable", False, str(exc))


def validate_exposure_computation() -> Dict[str, Any]:
    """Phase 7.2: Verify exposure computation produces correct structure."""
    try:
        from src.portfolio_intelligence.exposure_engine import PortfolioExposureEngine

        test_holdings = [
            {
                "ticker": "RELIANCE", "canonical_ticker": "RELIANCE.NS",
                "sector": "Energy", "industry": "Oil & Gas",
                "geography": "INDIA", "market": "INDIA",
                "weight_pct": 25.0, "market_value": 250000.0,
                "pnl": 10000.0, "pnl_pct": 4.17,
                "factor_exposure": {"growth": 0.6, "value": 0.4, "momentum": 0.55, "quality": 0.7, "macro_sensitivity": 0.65},
            },
            {
                "ticker": "TCS", "canonical_ticker": "TCS.NS",
                "sector": "Information Technology", "industry": "IT Services",
                "geography": "INDIA", "market": "INDIA",
                "weight_pct": 20.0, "market_value": 200000.0,
                "pnl": 8000.0, "pnl_pct": 4.17,
                "factor_exposure": {"growth": 0.7, "value": 0.35, "momentum": 0.6, "quality": 0.8, "macro_sensitivity": 0.4},
            },
            {
                "ticker": "HDFCBANK", "canonical_ticker": "HDFCBANK.NS",
                "sector": "Financials", "industry": "Banking",
                "geography": "INDIA", "market": "INDIA",
                "weight_pct": 18.0, "market_value": 180000.0,
                "pnl": 5000.0, "pnl_pct": 2.86,
                "factor_exposure": {"growth": 0.5, "value": 0.6, "momentum": 0.45, "quality": 0.75, "macro_sensitivity": 0.55},
            },
            {
                "ticker": "INFY", "canonical_ticker": "INFY.NS",
                "sector": "Information Technology", "industry": "IT Services",
                "geography": "INDIA", "market": "INDIA",
                "weight_pct": 15.0, "market_value": 150000.0,
                "pnl": 3000.0, "pnl_pct": 2.04,
                "factor_exposure": {"growth": 0.65, "value": 0.4, "momentum": 0.5, "quality": 0.7, "macro_sensitivity": 0.35},
            },
            {
                "ticker": "ITC", "canonical_ticker": "ITC.NS",
                "sector": "Consumer Staples", "industry": "FMCG",
                "geography": "INDIA", "market": "INDIA",
                "weight_pct": 12.0, "market_value": 120000.0,
                "pnl": 2000.0, "pnl_pct": 1.69,
                "factor_exposure": {"growth": 0.3, "value": 0.7, "momentum": 0.35, "quality": 0.6, "macro_sensitivity": 0.5},
            },
        ]

        engine = PortfolioExposureEngine()
        result = engine.compute_full_exposure(
            test_holdings,
            macro_context={"risk": {"appetite": "MIXED"}},
            factor_context={"factors": {"momentum": {"strength": "weak"}}},
            portfolio_id="test_portfolio",
            market="INDIA",
            truth_epoch="TRUTH_EPOCH_2026-03-06_01",
        )

        required_keys = [
            "sector_exposure", "industry_exposure", "geography_exposure",
            "factor_exposure", "macro_regime_exposure", "hidden_concentrations",
            "exposure_metrics", "exposure_insights", "trace",
        ]
        missing = [k for k in required_keys if k not in result]
        if missing:
            return _check("exposure_computation", False, f"Missing keys: {missing}")

        metrics = result["exposure_metrics"]
        for score_key in ("diversification_score", "concentration_score", "factor_balance_score", "regime_alignment_score", "composite_health"):
            val = metrics.get(score_key)
            if val is None or not (0.0 <= val <= 1.0):
                return _check("exposure_computation", False, f"{score_key} out of range: {val}")

        return _check("exposure_computation", True, f"All {len(required_keys)} keys present, metrics valid")
    except Exception as exc:
        return _check("exposure_computation", False, str(exc))


def validate_analytics_integration() -> Dict[str, Any]:
    """Phase 7.3: Verify analytics.py includes exposure_analysis in output."""
    try:
        from src.portfolio_intelligence import analytics
        import inspect
        source = inspect.getsource(analytics.analyze_portfolio)
        has_import = "PortfolioExposureEngine" in source or "exposure_engine" in source
        has_output = "exposure_analysis" in source
        passed = has_import and has_output
        detail = f"import={'OK' if has_import else 'MISSING'}, output_key={'OK' if has_output else 'MISSING'}"
        return _check("analytics_integration", passed, detail)
    except Exception as exc:
        return _check("analytics_integration", False, str(exc))


def validate_backend_endpoints() -> Dict[str, Any]:
    """Phase 7.4: Verify backend app.py has exposure routes registered."""
    try:
        app_path = PROJECT_ROOT / "src" / "dashboard" / "backend" / "app.py"
        content = app_path.read_text(encoding="utf-8")
        has_exposure = "/api/portfolio/exposure/" in content
        has_macro = "/api/portfolio/macro-alignment/" in content
        passed = has_exposure and has_macro
        detail = f"exposure_route={'OK' if has_exposure else 'MISSING'}, macro_route={'OK' if has_macro else 'MISSING'}"
        return _check("backend_endpoints", passed, detail)
    except Exception as exc:
        return _check("backend_endpoints", False, str(exc))


def validate_frontend_integration() -> Dict[str, Any]:
    """Phase 7.5: Verify frontend has exposure panel and API calls."""
    try:
        frontend_src = PROJECT_ROOT / "src" / "dashboard" / "frontend" / "src"
        api_file = frontend_src / "services" / "portfolioApi.js"
        panel_file = frontend_src / "components" / "PortfolioExposurePanel.jsx"
        main_panel = frontend_src / "components" / "PortfolioIntelligencePanel.jsx"

        api_content = api_file.read_text(encoding="utf-8")
        has_exposure_api = "getPortfolioExposure" in api_content
        has_macro_api = "getPortfolioMacroAlignment" in api_content
        panel_exists = panel_file.exists()
        main_content = main_panel.read_text(encoding="utf-8")
        has_panel_import = "PortfolioExposurePanel" in main_content

        passed = all([has_exposure_api, has_macro_api, panel_exists, has_panel_import])
        detail = (
            f"exposure_api={'OK' if has_exposure_api else 'MISSING'}, "
            f"macro_api={'OK' if has_macro_api else 'MISSING'}, "
            f"panel_component={'OK' if panel_exists else 'MISSING'}, "
            f"panel_integration={'OK' if has_panel_import else 'MISSING'}"
        )
        return _check("frontend_integration", passed, detail)
    except Exception as exc:
        return _check("frontend_integration", False, str(exc))


def validate_loader_functions() -> Dict[str, Any]:
    """Phase 7.6: Verify loader functions exist for exposure endpoints."""
    try:
        loader_path = PROJECT_ROOT / "src" / "dashboard" / "backend" / "loaders" / "portfolio.py"
        content = loader_path.read_text(encoding="utf-8")
        has_exposure = "load_portfolio_exposure" in content
        has_macro = "load_portfolio_macro_alignment" in content
        passed = has_exposure and has_macro
        detail = f"exposure_loader={'OK' if has_exposure else 'MISSING'}, macro_loader={'OK' if has_macro else 'MISSING'}"
        return _check("loader_functions", passed, detail)
    except Exception as exc:
        return _check("loader_functions", False, str(exc))


def run_full_validation() -> Dict[str, Any]:
    """Run complete post-implementation validation suite."""
    print("=" * 70)
    print("Portfolio Exposure Engine — Post-Implementation Validation")
    print("=" * 70)

    checks: List[Dict[str, Any]] = [
        validate_exposure_engine_importable(),
        validate_exposure_computation(),
        validate_analytics_integration(),
        validate_backend_endpoints(),
        validate_frontend_integration(),
        validate_loader_functions(),
    ]

    passed = sum(1 for c in checks if c["status"] == "PASS")
    failed = sum(1 for c in checks if c["status"] == "FAIL")

    print("=" * 70)
    print(f"Results: {passed}/{len(checks)} passed, {failed} failed")
    print("=" * 70)

    return {
        "validation_suite": "portfolio_exposure_engine",
        "truth_epoch": "TRUTH_EPOCH_2026-03-06_01",
        "checks": checks,
        "summary": {"total": len(checks), "passed": passed, "failed": failed},
        "overall": "PASS" if failed == 0 else "FAIL",
    }


if __name__ == "__main__":
    result = run_full_validation()
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["overall"] == "PASS" else 1)
