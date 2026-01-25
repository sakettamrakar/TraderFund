"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
Sentiment Model

Probabilistic sentiment scoring. NO binary good/bad labels.
Outputs are descriptive, NOT prescriptive.
##############################################################################
"""

from dataclasses import dataclass
from typing import Optional, List
import re


@dataclass
class SentimentScore:
    """Probabilistic sentiment score.

    This is a DESCRIPTIVE observation, not a trade recommendation.
    """
    polarity: float  # -1.0 (negative) to +1.0 (positive)
    confidence: float  # 0.0 to 1.0
    method: str  # Which model/method was used

    def __str__(self) -> str:
        direction = "positive" if self.polarity > 0 else "negative" if self.polarity < 0 else "neutral"
        return f"SentimentScore({direction}, polarity={self.polarity:.2f}, conf={self.confidence:.2f})"


# Simple keyword-based sentiment (placeholder for VADER or ML models)
POSITIVE_WORDS = {
    "surge", "soar", "gain", "profit", "growth", "bullish", "upgrade",
    "outperform", "beat", "strong", "positive", "momentum", "rally",
    "record", "high", "buy", "success", "exceed", "boost", "optimistic",
}

NEGATIVE_WORDS = {
    "fall", "drop", "loss", "decline", "bearish", "downgrade", "miss",
    "weak", "negative", "crash", "plunge", "concern", "risk", "warning",
    "sell", "fail", "cut", "below", "trouble", "pessimistic", "recession",
}


def analyze_sentiment(
    text: str,
    method: str = "keyword",
) -> SentimentScore:
    """Analyze sentiment of text.

    This is a basic keyword-based approach for research purposes.
    For production, consider VADER, FinBERT, or custom models.

    Args:
        text: Text to analyze.
        method: Analysis method identifier.

    Returns:
        SentimentScore with polarity and confidence.
    """
    if not text:
        return SentimentScore(polarity=0.0, confidence=0.0, method=method)

    words = set(re.findall(r"\b\w+\b", text.lower()))

    positive_count = len(words & POSITIVE_WORDS)
    negative_count = len(words & NEGATIVE_WORDS)
    total_sentiment_words = positive_count + negative_count

    if total_sentiment_words == 0:
        return SentimentScore(polarity=0.0, confidence=0.0, method=method)

    # Calculate polarity: -1 to +1
    polarity = (positive_count - negative_count) / total_sentiment_words

    # Confidence based on count of sentiment words found
    confidence = min(1.0, total_sentiment_words / 10)

    return SentimentScore(
        polarity=polarity,
        confidence=confidence,
        method=method,
    )


def analyze_batch(texts: List[str]) -> List[SentimentScore]:
    """Analyze sentiment for multiple texts.

    Args:
        texts: List of texts to analyze.

    Returns:
        List of SentimentScores.
    """
    return [analyze_sentiment(text) for text in texts]


def aggregate_sentiment(scores: List[SentimentScore]) -> SentimentScore:
    """Aggregate multiple sentiment scores.

    Uses confidence-weighted average.

    Args:
        scores: List of individual scores.

    Returns:
        Aggregated SentimentScore.
    """
    if not scores:
        return SentimentScore(polarity=0.0, confidence=0.0, method="aggregate")

    total_weight = sum(s.confidence for s in scores)
    if total_weight == 0:
        return SentimentScore(polarity=0.0, confidence=0.0, method="aggregate")

    weighted_polarity = sum(s.polarity * s.confidence for s in scores) / total_weight
    avg_confidence = total_weight / len(scores)

    return SentimentScore(
        polarity=weighted_polarity,
        confidence=avg_confidence,
        method="aggregate",
    )
