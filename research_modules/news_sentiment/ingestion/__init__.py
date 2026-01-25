"""Ingestion package for news sources."""

from .news_sources import NewsSource, FileNewsSource, RSSNewsSource
from .raw_fetcher import RawNewsFetcher

__all__ = [
    "NewsSource",
    "FileNewsSource",
    "RSSNewsSource",
    "RawNewsFetcher",
]
