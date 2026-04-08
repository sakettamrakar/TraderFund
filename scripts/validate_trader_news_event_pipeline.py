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


def validate_news_adapter() -> dict:
    try:
        from src.dashboard.backend.loaders.portfolio import load_portfolio_research

        payload = load_portfolio_research("INDIA", "zerodha_primary")
        status = payload.get("news_adapter_status", {})
        passed = bool(status) and "status" in status and "source" in status
        return _check("NEWS_ADAPTER_OK", passed, f"adapter_status={status}")
    except Exception as exc:
        return _check("NEWS_ADAPTER_OK", False, str(exc))


def validate_entity_mapping() -> dict:
    try:
        from src.portfolio_intelligence.news_event_intelligence import PortfolioEventIntelligenceBuilder
        from traderfund.narrative.adapters.market_story_adapter import MarketStory

        builder = PortfolioEventIntelligenceBuilder()
        entity_index = builder._build_entity_index([{"ticker": "HAL", "security_name": "HAL"}, {"ticker": "ASML", "security_name": "ASML Holding"}])
        hal_story = MarketStory(id="1", headline="Hindustan Aeronautics under review", summary="Hindustan Aeronautics sees program uncertainty.", published_at="2026-03-13T10:00:00+00:00", category="CORPORATE", region="INDIA", severity_hint="HIGH", source="test")
        asml_story = MarketStory(id="2", headline="ASML shipment timing slips", summary="ASML shipment timing faces pressure.", published_at="2026-03-13T10:00:00+00:00", category="CORPORATE", region="US", severity_hint="MEDIUM", source="test")
        passed = builder._map_story_to_tickers(hal_story, entity_index) == ["HAL"] and builder._map_story_to_tickers(asml_story, entity_index) == ["ASML"]
        return _check("ENTITY_MAPPING_OK", passed, "HAL and ASML entity mapping validated")
    except Exception as exc:
        return _check("ENTITY_MAPPING_OK", False, str(exc))


def validate_narrative_layer() -> dict:
    try:
        from src.dashboard.backend.loaders.portfolio import load_portfolio_research

        payload = load_portfolio_research("INDIA", "zerodha_primary")
        synthesis = payload.get("research_synthesis", {})
        passed = "portfolio_narrative" in synthesis and "event_narrative" in synthesis
        return _check("NARRATIVE_LAYER_OK", passed, f"event_narrative={bool(synthesis.get('event_narrative'))}")
    except Exception as exc:
        return _check("NARRATIVE_LAYER_OK", False, str(exc))


def validate_portfolio_event_linkage() -> dict:
    try:
        from src.dashboard.backend.loaders.portfolio import load_portfolio_research

        payload = load_portfolio_research("INDIA", "zerodha_primary")
        profiles = payload.get("stock_research_profiles", [])
        passed = all("monitoring_status" in profile and "event_intelligence" in profile for profile in profiles)
        return _check("PORTFOLIO_EVENT_LINKAGE_OK", passed, f"profiles={len(profiles)}")
    except Exception as exc:
        return _check("PORTFOLIO_EVENT_LINKAGE_OK", False, str(exc))


def validate_dashboard_event_display() -> dict:
    try:
        panel_path = PROJECT_ROOT / "src" / "dashboard" / "frontend" / "src" / "components" / "PortfolioIntelligencePanel.jsx"
        stock_panel_path = PROJECT_ROOT / "src" / "dashboard" / "frontend" / "src" / "components" / "StockResearchPanel.jsx"
        content = panel_path.read_text(encoding="utf-8") + stock_panel_path.read_text(encoding="utf-8")
        required_tokens = ["PortfolioEventIntelligencePanel", "Event Timeline", "monitoring_status"]
        missing = [token for token in required_tokens if token not in content]
        return _check("DASHBOARD_EVENT_DISPLAY_OK", not missing, f"missing={missing or 'NONE'}")
    except Exception as exc:
        return _check("DASHBOARD_EVENT_DISPLAY_OK", False, str(exc))


def main() -> int:
    results = [
        validate_news_adapter(),
        validate_entity_mapping(),
        validate_narrative_layer(),
        validate_portfolio_event_linkage(),
        validate_dashboard_event_display(),
    ]
    overall = all(item["status"] == "PASS" for item in results)
    print(json.dumps({"results": results, "overall": "PASS" if overall else "FAIL"}, indent=2))
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
