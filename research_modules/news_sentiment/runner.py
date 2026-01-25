"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
Sentiment Runner

Orchestrates ingestion → processing → snapshot generation.
##############################################################################
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional
from collections import Counter

from .sentiment_snapshot import SentimentSnapshot
from .ingestion.news_sources import NewsArticle, NewsSource
from .ingestion.raw_fetcher import RawNewsFetcher
from .processing.text_cleaner import clean_text
from .processing.sentiment_model import analyze_sentiment, aggregate_sentiment, SentimentScore
from .processing.event_classifier import classify_events, extract_topics, EventTag

logger = logging.getLogger(__name__)


class SentimentRunner:
    """Orchestrates sentiment analysis.

    This runner produces RESEARCH-ONLY snapshots.
    Outputs must NOT influence trade decisions without governance approval.
    """

    def __init__(self, sources: List[NewsSource] = None):
        """Initialize with news sources.

        Args:
            sources: List of NewsSource instances.
        """
        self.fetcher = RawNewsFetcher(sources or [])

    def add_source(self, source: NewsSource) -> None:
        """Add a news source."""
        self.fetcher.add_source(source)

    def analyze(
        self,
        symbol: str,
        hours: int = 24,
        notes: Optional[str] = None,
    ) -> SentimentSnapshot:
        """Analyze sentiment for a symbol.

        Args:
            symbol: Symbol to analyze.
            hours: Lookback period in hours.
            notes: Optional analyst notes.

        Returns:
            SentimentSnapshot with aggregated results.
        """
        now = datetime.now()
        time_start = now - timedelta(hours=hours)

        # Fetch articles
        articles = self.fetcher.fetch_by_symbol(symbol)
        logger.info(f"Found {len(articles)} articles for {symbol}")

        if not articles:
            return SentimentSnapshot(
                symbol=symbol,
                time_window_start=time_start,
                time_window_end=now,
                article_count=0,
                sentiment_score=SentimentScore(0.0, 0.0, "none"),
                dominant_topics=[],
                event_tags=[EventTag.UNKNOWN],
                snapshot_time=now,
                notes=notes,
            )

        # Process articles
        scores = []
        all_topics = []
        all_events = []

        for article in articles:
            # Clean and analyze
            clean_content = clean_text(f"{article.title} {article.content}")
            score = analyze_sentiment(clean_content)
            events = classify_events(clean_content)
            topics = extract_topics(clean_content)

            scores.append(score)
            all_events.extend(events)
            all_topics.extend(topics)

        # Aggregate
        agg_sentiment = aggregate_sentiment(scores)

        # Get most common topics and events
        topic_counts = Counter(all_topics)
        event_counts = Counter(all_events)

        dominant_topics = [t for t, _ in topic_counts.most_common(5)]
        dominant_events = [e for e, _ in event_counts.most_common(3)]

        return SentimentSnapshot(
            symbol=symbol,
            time_window_start=time_start,
            time_window_end=now,
            article_count=len(articles),
            sentiment_score=agg_sentiment,
            dominant_topics=dominant_topics,
            event_tags=dominant_events,
            snapshot_time=now,
            notes=notes,
        )

    def print_snapshot(self, snapshot: SentimentSnapshot) -> None:
        """Print a formatted snapshot to stdout."""
        print("\n" + "=" * 60)
        print("## RESEARCH SENTIMENT SNAPSHOT ##")
        print("=" * 60)
        print(f"Symbol: {snapshot.symbol}")
        print(f"Time Window: {snapshot.time_window_start} to {snapshot.time_window_end}")
        print(f"Articles Analyzed: {snapshot.article_count}")
        print("-" * 60)
        print("SENTIMENT:")
        print(f"  Polarity: {snapshot.sentiment_score.polarity:.2f}")
        print(f"  Confidence: {snapshot.sentiment_score.confidence:.2f}")
        print("-" * 60)
        print("TOPICS: " + ", ".join(snapshot.dominant_topics[:5]))
        print("EVENTS: " + ", ".join(t.value for t in snapshot.event_tags[:3]))
        print("=" * 60)
        print("⚠️  This is an OBSERVATION. Do NOT use to override price/volume signals.")
        print("=" * 60 + "\n")
