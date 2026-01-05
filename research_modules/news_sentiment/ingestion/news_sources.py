"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
News Sources

Abstract and concrete adapters for ingesting news from various sources.
##############################################################################
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Iterator
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class NewsArticle:
    """Raw news article representation."""
    source: str
    title: str
    content: str
    published_at: datetime
    fetched_at: datetime
    url: Optional[str] = None
    symbol: Optional[str] = None
    raw_data: Optional[dict] = None

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "title": self.title,
            "content": self.content,
            "published_at": self.published_at.isoformat(),
            "fetched_at": self.fetched_at.isoformat(),
            "url": self.url,
            "symbol": self.symbol,
        }


class NewsSource(ABC):
    """Abstract base class for news sources."""

    @abstractmethod
    def fetch(self) -> Iterator[NewsArticle]:
        """Fetch articles from the source."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Source identifier."""
        pass


class FileNewsSource(NewsSource):
    """Load news from local JSON files.

    Expected format: List of dicts with title, content, published_at, etc.
    """

    def __init__(self, file_path: str, source_name: str = "file"):
        self.file_path = Path(file_path)
        self._name = source_name

    @property
    def name(self) -> str:
        return self._name

    def fetch(self) -> Iterator[NewsArticle]:
        """Load articles from JSON file."""
        if not self.file_path.exists():
            logger.warning(f"News file not found: {self.file_path}")
            return

        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        articles = data if isinstance(data, list) else data.get("articles", [])
        now = datetime.now()

        for item in articles:
            try:
                published = item.get("published_at") or item.get("timestamp")
                if isinstance(published, str):
                    published = datetime.fromisoformat(published.replace("Z", "+00:00"))
                else:
                    published = now

                yield NewsArticle(
                    source=self.name,
                    title=item.get("title", ""),
                    content=item.get("content", item.get("body", "")),
                    published_at=published,
                    fetched_at=now,
                    url=item.get("url"),
                    symbol=item.get("symbol"),
                    raw_data=item,
                )
            except Exception as e:
                logger.error(f"Error parsing article: {e}")


class RSSNewsSource(NewsSource):
    """Placeholder for RSS feed ingestion.

    Actual RSS parsing would require feedparser or similar.
    """

    def __init__(self, feed_url: str, source_name: str = "rss"):
        self.feed_url = feed_url
        self._name = source_name

    @property
    def name(self) -> str:
        return self._name

    def fetch(self) -> Iterator[NewsArticle]:
        """Fetch from RSS feed (stub implementation)."""
        logger.warning("RSSNewsSource is a stub. Use FileNewsSource for research.")
        return iter([])


class MockNewsSource(NewsSource):
    """Mock source for testing."""

    def __init__(self, articles: List[NewsArticle] = None):
        self._articles = articles or []

    @property
    def name(self) -> str:
        return "mock"

    def fetch(self) -> Iterator[NewsArticle]:
        return iter(self._articles)
