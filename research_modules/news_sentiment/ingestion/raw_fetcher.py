"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
Raw News Fetcher

Fetches and timestamps articles from configured sources.
No filtering based on perceived importance.
##############################################################################
"""

import logging
from datetime import datetime
from typing import List, Iterator

from .news_sources import NewsSource, NewsArticle

logger = logging.getLogger(__name__)


class RawNewsFetcher:
    """Fetches raw news from multiple sources.

    This fetcher performs NO filtering or prioritization.
    All articles are ingested verbatim.
    """

    def __init__(self, sources: List[NewsSource] = None):
        """Initialize with news sources.

        Args:
            sources: List of NewsSource instances.
        """
        self.sources = sources or []

    def add_source(self, source: NewsSource) -> None:
        """Add a news source."""
        self.sources.append(source)
        logger.info(f"Added news source: {source.name}")

    def fetch_all(self) -> List[NewsArticle]:
        """Fetch articles from all sources.

        Returns:
            List of all fetched articles, unfiltered.
        """
        all_articles = []

        for source in self.sources:
            try:
                articles = list(source.fetch())
                logger.info(f"Fetched {len(articles)} articles from {source.name}")
                all_articles.extend(articles)
            except Exception as e:
                logger.error(f"Error fetching from {source.name}: {e}")

        return all_articles

    def fetch_by_symbol(self, symbol: str) -> List[NewsArticle]:
        """Fetch articles for a specific symbol.

        Note: This only filters articles that have symbol metadata.
        It does NOT perform text matching.

        Args:
            symbol: Symbol to filter by.

        Returns:
            Articles with matching symbol.
        """
        all_articles = self.fetch_all()
        return [a for a in all_articles if a.symbol and a.symbol.upper() == symbol.upper()]

    def fetch_recent(self, hours: int = 24) -> List[NewsArticle]:
        """Fetch articles from the last N hours.

        Args:
            hours: Lookback period in hours.

        Returns:
            Recent articles.
        """
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(hours=hours)
        all_articles = self.fetch_all()
        return [a for a in all_articles if a.published_at >= cutoff]
