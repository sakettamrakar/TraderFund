"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
Sentiment Snapshot

Read-only data container for sentiment analysis results.
These are OBSERVATIONS, not RECOMMENDATIONS.
##############################################################################
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from .processing.sentiment_model import SentimentScore
from .processing.event_classifier import EventTag


@dataclass(frozen=True)
class SentimentSnapshot:
    """Aggregated sentiment snapshot for a symbol.

    This is a READ-ONLY observation of news sentiment.
    It does NOT recommend any trading action.

    IMPORTANT: Sentiment must NEVER override price/volume signals.
    """
    symbol: str
    time_window_start: datetime
    time_window_end: datetime
    article_count: int
    sentiment_score: SentimentScore
    dominant_topics: List[str]
    event_tags: List[EventTag]
    snapshot_time: datetime
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert snapshot to dictionary."""
        return {
            "symbol": self.symbol,
            "time_window_start": self.time_window_start.isoformat(),
            "time_window_end": self.time_window_end.isoformat(),
            "article_count": self.article_count,
            "sentiment": {
                "polarity": self.sentiment_score.polarity,
                "confidence": self.sentiment_score.confidence,
                "method": self.sentiment_score.method,
            },
            "dominant_topics": self.dominant_topics,
            "event_tags": [t.value for t in self.event_tags],
            "snapshot_time": self.snapshot_time.isoformat(),
            "notes": self.notes,
        }

    def __str__(self) -> str:
        polarity_desc = "positive" if self.sentiment_score.polarity > 0.1 else \
                       "negative" if self.sentiment_score.polarity < -0.1 else "neutral"
        return (
            f"SentimentSnapshot({self.symbol})\n"
            f"  Articles: {self.article_count}\n"
            f"  Sentiment: {polarity_desc} ({self.sentiment_score.polarity:.2f})\n"
            f"  Topics: {', '.join(self.dominant_topics[:3])}\n"
            f"  Events: {', '.join(t.value for t in self.event_tags[:3])}"
        )
