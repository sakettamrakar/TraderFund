from __future__ import annotations

import json
from pathlib import Path

from src.portfolio_intelligence.config import PortfolioIntelligenceConfig
from src.portfolio_intelligence.news_event_intelligence import PortfolioEventIntelligenceBuilder
from traderfund.narrative.adapters.market_story_adapter import MarketStory, MarketStoryAdapter


def test_market_story_adapter_persists_dedup_state(tmp_path: Path) -> None:
    adapter = MarketStoryAdapter(engine=None, state_path=str(tmp_path / "adapter_state.json"))
    story = MarketStory(
        id="story-1",
        headline="Market event",
        summary="A macro event happened.",
        published_at="2026-03-13T10:00:00+00:00",
        category="MARKET_SUMMARY",
        region="GLOBAL",
        severity_hint="HIGH",
        source="TraderNews",
    )

    first_count = adapter.ingest_stories([story])
    second_adapter = MarketStoryAdapter(engine=None, state_path=str(tmp_path / "adapter_state.json"))
    second_count = second_adapter.ingest_stories([story])

    assert first_count == 1
    assert second_count == 0


def test_event_builder_maps_hindustan_aeronautics_to_hal_from_cache(tmp_path: Path) -> None:
    config = PortfolioIntelligenceConfig(base_dir=tmp_path / "portfolio_intelligence")
    cache_dir = config.base_dir / "news" / "INDIA"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.joinpath("latest.json").write_text(
        json.dumps(
            [
                {
                    "id": "story-hal",
                    "headline": "Hindustan Aeronautics faces contract review",
                    "summary": "Reports indicate Hindustan Aeronautics may see contract visibility pressure.",
                    "published_at": "2026-03-13T09:00:00+00:00",
                    "category": "CORPORATE",
                    "region": "INDIA",
                    "severity_hint": "HIGH",
                    "source": "TraderNews",
                    "mentioned_entities": ["Hindustan Aeronautics"],
                }
            ],
            indent=2,
        ),
        encoding="utf-8",
    )

    builder = PortfolioEventIntelligenceBuilder(config=config)
    result = builder.build(
        holdings=[{"ticker": "HAL", "security_name": "HAL", "weight_pct": 8.0}],
        market="INDIA",
    )

    assert result.adapter_status["status"] == "CACHE_ONLY"
    assert "HAL" in result.stock_event_map
    assert result.stock_event_map["HAL"]["event_risk_flag"] is True
    assert result.portfolio_event_alerts[0]["ticker"] == "HAL"


def test_event_builder_maps_asml_entity_to_asml() -> None:
    builder = PortfolioEventIntelligenceBuilder()
    story = MarketStory(
        id="story-asml",
        headline="ASML shipment timing under review",
        summary="ASML may face temporary shipment timing pressure.",
        published_at="2026-03-13T09:00:00+00:00",
        category="CORPORATE",
        region="US",
        severity_hint="MEDIUM",
        source="TraderNews",
        mentioned_entities=["ASML"],
    )
    entity_index = builder._build_entity_index([{"ticker": "ASML", "security_name": "ASML Holding", "weight_pct": 5.0}])

    mapped = builder._map_story_to_tickers(story, entity_index)

    assert mapped == ["ASML"]
