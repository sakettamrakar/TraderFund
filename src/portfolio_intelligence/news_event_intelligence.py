from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from traderfund.narrative.adapters.market_story_adapter import MarketStory, MarketStoryAdapter

from .config import PROJECT_ROOT, PortfolioIntelligenceConfig


MANUAL_ENTITY_ALIASES: Dict[str, List[str]] = {
    "HAL": ["hindustan aeronautics", "hindustan aeronautics limited", "hal"],
    "ASML": ["asml", "asml holding", "asml holdings"],
    "LT": ["larsen and toubro", "larsen & toubro", "lt"],
}


@dataclass(frozen=True)
class EventIntelligenceResult:
    adapter_status: Dict[str, Any]
    stock_event_map: Dict[str, Dict[str, Any]]
    portfolio_event_alerts: List[Dict[str, Any]]
    portfolio_event_timeline: List[Dict[str, Any]]


class PortfolioEventIntelligenceBuilder:
    def __init__(self, config: PortfolioIntelligenceConfig | None = None) -> None:
        self.config = config or PortfolioIntelligenceConfig()
        self.cache_dir = self.config.base_dir / "news"
        self.state_path = self.config.base_dir / "news_adapter" / "processed_story_ids.json"

    def build(self, *, holdings: List[Dict[str, Any]], market: str) -> EventIntelligenceResult:
        stories, adapter_status = self._load_stories(market)
        if not stories:
            return EventIntelligenceResult(
                adapter_status=adapter_status,
                stock_event_map={},
                portfolio_event_alerts=[],
                portfolio_event_timeline=[],
            )

        entity_index = self._build_entity_index(holdings)
        stock_event_map: Dict[str, Dict[str, Any]] = {}
        portfolio_alerts: List[Dict[str, Any]] = []
        timeline: List[Dict[str, Any]] = []

        for story in stories:
            matched = self._map_story_to_tickers(story, entity_index)
            if not matched:
                continue
            for ticker in matched:
                event = self._build_event_record(story, ticker)
                stock_event_map.setdefault(ticker, self._empty_stock_event_record(ticker))
                stock_event_map[ticker]["events"].append(event)
                stock_event_map[ticker]["event_count"] += 1
                stock_event_map[ticker]["event_risk_flag"] = stock_event_map[ticker]["event_risk_flag"] or event["risk_level"] in {"HIGH", "MEDIUM"}
                stock_event_map[ticker]["monitoring_status"] = self._monitoring_status(stock_event_map[ticker]["events"])
                stock_event_map[ticker]["narrative_summary"] = self._narrative_summary(ticker, stock_event_map[ticker]["events"])
                stock_event_map[ticker]["portfolio_relevance"] = f"{ticker} is a direct holding in the current portfolio."
                stock_event_map[ticker]["potential_risk_implications"] = self._risk_implication(stock_event_map[ticker]["events"])
                stock_event_map[ticker]["monitoring_recommendation"] = self._monitoring_recommendation(stock_event_map[ticker]["events"])
                stock_event_map[ticker]["sentiment"] = self._aggregate_sentiment(stock_event_map[ticker]["events"])
                timeline.append({"ticker": ticker, **event})

        for ticker, record in stock_event_map.items():
            latest = record["events"][0]
            portfolio_alerts.append(
                {
                    "ticker": ticker,
                    "headline": latest["headline"],
                    "event_summary": latest["event_summary"],
                    "portfolio_relevance": record["portfolio_relevance"],
                    "potential_risk_implications": record["potential_risk_implications"],
                    "monitoring_recommendation": record["monitoring_recommendation"],
                    "risk_level": latest["risk_level"],
                    "published_at": latest["published_at"],
                    "trace": latest["trace"],
                }
            )

        portfolio_alerts.sort(key=lambda item: item["published_at"], reverse=True)
        timeline.sort(key=lambda item: item["published_at"], reverse=True)
        return EventIntelligenceResult(
            adapter_status=adapter_status,
            stock_event_map=stock_event_map,
            portfolio_event_alerts=portfolio_alerts,
            portfolio_event_timeline=timeline,
        )

    def _load_stories(self, market: str) -> tuple[List[MarketStory], Dict[str, Any]]:
        api_url = self.config.trader_news_api_url
        state = {
            "status": "NO_FEED_CONFIGURED",
            "source": "UNAVAILABLE",
            "story_count": 0,
            "market": market,
        }
        stories: List[MarketStory] = []
        adapter = MarketStoryAdapter(engine=None, state_path=str(self.state_path))

        if api_url:
            url = f"{api_url}?market={market}"
            fetched = adapter.fetch_stories_from_api(url, hours=self.config.trader_news_lookback_hours)
            if fetched:
                self._write_cache(market, fetched)
                stories = fetched
                state = {
                    "status": "FETCH_OK",
                    "source": url,
                    "story_count": len(fetched),
                    "market": market,
                }
            else:
                state = {
                    "status": "FETCH_EMPTY_OR_FAILED",
                    "source": url,
                    "story_count": 0,
                    "market": market,
                }

        if not stories:
            cached = self._load_cached_stories(market)
            if cached:
                stories = cached
                state = {
                    "status": "CACHE_ONLY",
                    "source": _display_path(self.cache_dir / market / "latest.json"),
                    "story_count": len(cached),
                    "market": market,
                }
        return stories, state

    def _load_cached_stories(self, market: str) -> List[MarketStory]:
        path = self.cache_dir / market / "latest.json"
        if not path.exists():
            return []
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return []
        stories = []
        for item in payload if isinstance(payload, list) else payload.get("stories", []):
            try:
                stories.append(MarketStory(**item))
            except Exception:
                continue
        return sorted(stories, key=lambda item: item.published_at, reverse=True)

    def _write_cache(self, market: str, stories: List[MarketStory]) -> None:
        path = self.cache_dir / market / "latest.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = [story.model_dump() for story in stories]
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _build_entity_index(self, holdings: List[Dict[str, Any]]) -> Dict[str, str]:
        index: Dict[str, str] = {}
        for holding in holdings:
            ticker = str(holding.get("ticker") or "").upper().strip()
            if not ticker:
                continue
            aliases = {ticker.lower()}
            security_name = str(holding.get("security_name") or ticker)
            aliases.add(_normalize_text(security_name))
            aliases.add(_normalize_text(security_name.replace("LIMITED", "")))
            aliases.update(MANUAL_ENTITY_ALIASES.get(ticker, []))
            for alias in aliases:
                norm = _normalize_text(alias)
                if norm:
                    index[norm] = ticker
        return index

    def _map_story_to_tickers(self, story: MarketStory, entity_index: Dict[str, str]) -> List[str]:
        matched: set[str] = set()
        text_parts = [story.headline, story.summary]
        if story.mentioned_entities:
            text_parts.extend(story.mentioned_entities)
        if story.semantic_tags:
            text_parts.extend(story.semantic_tags)
        normalized_text = _normalize_text(" ".join(filter(None, text_parts)))
        for alias, ticker in entity_index.items():
            if alias and alias in normalized_text:
                matched.add(ticker)
        return sorted(matched)

    def _build_event_record(self, story: MarketStory, ticker: str) -> Dict[str, Any]:
        risk_level = self._risk_level(story)
        return {
            "headline": story.headline,
            "event_summary": story.summary or story.headline,
            "published_at": story.published_at,
            "source": story.source,
            "event_type": story.event_type or story.category,
            "risk_level": risk_level,
            "portfolio_relevance": f"{ticker} is a direct holding in the portfolio.",
            "potential_risk_implications": self._risk_text(story, risk_level),
            "monitoring_recommendation": self._monitoring_text(story),
            "trace": {
                "source": story.source,
                "url": story.url,
                "adapter": "traderfund.narrative.adapters.market_story_adapter",
                "market": story.region,
            },
        }

    def _risk_level(self, story: MarketStory) -> str:
        severity = (story.severity_hint or "LOW").upper()
        return "HIGH" if severity == "HIGH" else "MEDIUM" if severity == "MEDIUM" else "LOW"

    def _risk_text(self, story: MarketStory, risk_level: str) -> str:
        event_type = (story.event_type or story.category or "EVENT").replace("_", " ").lower()
        return f"{event_type.title()} development may affect near-term sentiment and forward expectations for the holding. Risk level assessed as {risk_level.lower()}."

    def _monitoring_text(self, story: MarketStory) -> str:
        event_type = (story.event_type or story.category or "event").replace("_", " ").lower()
        return f"Monitor follow-up disclosures, management commentary, and sector reaction related to this {event_type}."

    def _empty_stock_event_record(self, ticker: str) -> Dict[str, Any]:
        return {
            "ticker": ticker,
            "events": [],
            "event_count": 0,
            "event_risk_flag": False,
            "monitoring_status": "NO_ACTIVE_EVENT",
            "narrative_summary": None,
            "portfolio_relevance": None,
            "potential_risk_implications": None,
            "monitoring_recommendation": None,
            "sentiment": {},
        }

    def _monitoring_status(self, events: List[Dict[str, Any]]) -> str:
        if any(item["risk_level"] == "HIGH" for item in events):
            return "ACTIVE_MONITOR_HIGH"
        if events:
            return "ACTIVE_MONITOR"
        return "NO_ACTIVE_EVENT"

    def _narrative_summary(self, ticker: str, events: List[Dict[str, Any]]) -> str:
        latest = events[0]
        return (
            f"EVENT_INTELLIGENCE\n\n"
            f"Ticker: {ticker}\n\n"
            f"Event Summary:\n{latest['event_summary']}\n\n"
            f"Portfolio Relevance:\n{latest['portfolio_relevance']}\n\n"
            f"Implication:\n{latest['potential_risk_implications']}\n\n"
            f"Recommendation:\n{latest['monitoring_recommendation']}"
        )

    def _risk_implication(self, events: List[Dict[str, Any]]) -> str:
        return events[0]["potential_risk_implications"] if events else "No active event implication."

    def _monitoring_recommendation(self, events: List[Dict[str, Any]]) -> str:
        return events[0]["monitoring_recommendation"] if events else "No event-specific monitoring required."

    def _aggregate_sentiment(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not events:
            return {"article_count": 0, "sentiment_label": "none", "confidence": 0.0}
        level_scores = {"LOW": 0.2, "MEDIUM": 0.5, "HIGH": 0.8}
        avg = sum(level_scores.get(item["risk_level"], 0.2) for item in events) / len(events)
        label = "negative" if avg >= 0.5 else "neutral"
        return {"article_count": len(events), "sentiment_label": label, "confidence": round(avg, 4)}


def _normalize_text(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9\s]", " ", value.lower())
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except Exception:
        return str(path)
