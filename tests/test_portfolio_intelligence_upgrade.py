from __future__ import annotations

import json
from pathlib import Path

from src.dashboard.backend.loaders import portfolio as portfolio_loader
from src.portfolio_intelligence.config import PortfolioIntelligenceConfig
from src.portfolio_intelligence.exposure_engine import PortfolioExposureEngine
from src.portfolio_intelligence.portfolio_strategy_engine import PortfolioStrategyEngine
from src.portfolio_intelligence.refresh_runtime import PortfolioRefreshRuntime
from src.portfolio_intelligence.service import PortfolioIntelligenceService


def test_mutual_fund_lookthrough_exposure_adds_global_geography_and_trace() -> None:
	engine = PortfolioExposureEngine()
	holdings = [
		{
			"ticker": "LT",
			"sector": "Industrials",
			"industry": "Engineering",
			"geography": "INDIA",
			"market": "INDIA",
			"weight_pct": 20.0,
			"market_value": 200.0,
			"factor_exposure": {"growth": 0.4, "value": 0.5, "momentum": 0.35, "quality": 0.45, "macro_sensitivity": 0.55},
			"liquidity_risk": "MEDIUM",
		}
	]
	mutual_funds = [
		{
			"ticker": "INF247L01718",
			"security_name": "MOTILAL OSWAL NASDAQ 100 FUND OF FUND - DIRECT PLAN",
			"sector": "Global Funds",
			"industry": "GLOBAL_EQUITY_FUND",
			"market": "INDIA",
			"weight_pct": 80.0,
			"market_value": 800.0,
		}
	]

	exposure = engine.compute_full_exposure(
		holdings,
		mutual_fund_holdings=mutual_funds,
		market="INDIA",
		portfolio_id="p1",
		truth_epoch="TEST_EPOCH",
	)

	assert exposure["lookthrough_summary"]["lookthrough_enabled"] is True
	assert exposure["lookthrough_summary"]["synthetic_lookthrough_rows"] > 0
	assert exposure["geography_exposure"]["country_exposure_pct"]["US"] > 0
	assert exposure["sector_exposure"]["allocation_pct"]["Information Technology"] > 0
	assert exposure["exposure_insights"][0]["trace"]


def test_strategy_package_contains_explainability_traces_for_fund_and_equity_signals() -> None:
	engine = PortfolioStrategyEngine()
	research_profiles = [
		{
			"ticker": "LT",
			"portfolio_weight": 15.0,
			"valuation_status": "overvalued",
			"macro_sensitivity": "interest_rate_sensitive",
			"risk_flags": [{"flag": "concentration_risk", "explanation": "Position is large.", "confidence_level": "HIGH"}],
			"opportunity_signals": [{"signal": "quality_compounder", "explanation": "Quality remains intact.", "confidence_level": "MEDIUM"}],
			"macro_regime_alignment": {"score": 0.2},
		}
	]
	mutual_fund_intelligence = {
		"allocation_mix": {"Global Funds": 12.0},
		"fund_profiles": [
			{
				"ticker": "INF194K01X46",
				"security_name": "BANDHAN INFRASTRUCTURE FUND - DIRECT PLAN",
				"fund_category": "Sector Funds",
				"risk_level": "HIGH",
				"risk_flags": [{"flag": "fund_concentration_risk", "explanation": "Large fund sleeve weight."}],
				"opportunity_signals": [{"signal": "thematic_upside", "explanation": "Theme can outperform."}],
			}
		],
	}
	exposure_analysis = {
		"hidden_concentrations": {"sector_concentration": {"dominant_sector": "Industrials", "dominant_sector_weight": 35.0}, "cluster_count": 2},
		"sector_exposure": {"dominant_sector": "Industrials"},
		"macro_regime_exposure": {"regime_vulnerability_flags": ["HIGH_CYCLICAL_EXPOSURE_IN_DEFENSIVE_REGIME"]},
		"exposure_metrics": {"regime_alignment_score": 0.3, "diversification_score": 0.4},
	}

	bundle = engine.build_strategy_package(
		research_profiles=research_profiles,
		mutual_fund_intelligence=mutual_fund_intelligence,
		exposure_analysis=exposure_analysis,
		macro_context={"risk": {"appetite": "LOW"}},
		factor_context={},
		market="INDIA",
		truth_epoch="TEST_EPOCH",
	)

	assert bundle["portfolio_strategy_suggestions"]
	assert all("trace" in item and item["trace"] for item in bundle["portfolio_strategy_suggestions"])
	assert any(item.get("trace") for item in bundle["portfolio_risk_alerts"])
	assert any(item.get("trace") for item in bundle["portfolio_opportunity_signals"])


def test_trigger_portfolio_refresh_returns_in_progress_state(monkeypatch) -> None:
	def _raise_in_progress(**_: object) -> None:
		raise RuntimeError("Portfolio refresh already in progress for this portfolio.")

	monkeypatch.setattr(portfolio_loader.SERVICE, "refresh_zerodha_portfolio", _raise_in_progress)
	response = portfolio_loader.trigger_portfolio_refresh("INDIA", "zerodha_primary")

	assert response["status"] == "REFRESH_IN_PROGRESS"
	assert response["runtime"]["status"] in {"IDLE", "IN_PROGRESS", "FAILED"}


def test_load_portfolio_trend_returns_history_and_drift(tmp_path: Path, monkeypatch) -> None:
	config = PortfolioIntelligenceConfig(base_dir=tmp_path / "portfolio_intel")
	service = PortfolioIntelligenceService(config=config)
	history_dir = config.base_dir / "history" / "INDIA" / "zerodha_primary"
	history_dir.mkdir(parents=True, exist_ok=True)

	payload1 = {
		"portfolio_id": "zerodha_primary",
		"market": "INDIA",
		"truth_epoch": "TEST_EPOCH",
		"data_as_of": "2026-03-13T10:00:00+00:00",
		"portfolio_refresh_timestamp": "2026-03-13T10:00:00+00:00",
		"overview": {"total_value": 100.0},
		"mutual_fund_summary": {"allocation_pct": 40.0},
		"resilience": {"overall_score": 0.4, "classification": "VULNERABLE", "components": {"mutual_fund_support": 0.2, "equity_sleeve_resilience": 0.5, "mutual_fund_sleeve_resilience": 0.2}},
	}
	payload2 = {
		"portfolio_id": "zerodha_primary",
		"market": "INDIA",
		"truth_epoch": "TEST_EPOCH",
		"data_as_of": "2026-03-13T11:00:00+00:00",
		"portfolio_refresh_timestamp": "2026-03-13T11:00:00+00:00",
		"overview": {"total_value": 125.0},
		"mutual_fund_summary": {"allocation_pct": 45.0},
		"resilience": {"overall_score": 0.55, "classification": "ADEQUATE", "components": {"mutual_fund_support": 0.33, "equity_sleeve_resilience": 0.6, "mutual_fund_sleeve_resilience": 0.33}},
	}
	(history_dir / "20260313T100000Z.json").write_text(json.dumps(payload1), encoding="utf-8")
	(history_dir / "20260313T110000Z.json").write_text(json.dumps(payload2), encoding="utf-8")

	trend = service.load_portfolio_trend("INDIA", "zerodha_primary")

	assert len(trend["history"]) == 2
	assert trend["drift"]["resilience_change"] == 0.15
	assert trend["drift"]["value_change"] == 25.0
