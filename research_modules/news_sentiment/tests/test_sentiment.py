"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
Unit tests for news sentiment module.
##############################################################################
"""

import pytest
from datetime import datetime


class TestTextCleaner:
    """Tests for text cleaning functions."""

    def test_clean_html(self):
        """Should remove HTML tags."""
        from research_modules.news_sentiment.processing.text_cleaner import clean_html
        result = clean_html("<p>Hello <b>World</b></p>")
        assert "<" not in result
        assert ">" not in result

    def test_normalize_whitespace(self):
        """Should collapse multiple spaces."""
        from research_modules.news_sentiment.processing.text_cleaner import normalize_whitespace
        result = normalize_whitespace("hello    world\n\ttab")
        assert result == "hello world tab"

    def test_clean_text_full(self):
        """Should apply full cleaning pipeline."""
        from research_modules.news_sentiment.processing.text_cleaner import clean_text
        result = clean_text("<p>Hello   https://example.com World</p>")
        assert "http" not in result
        assert "<" not in result


class TestSentimentModel:
    """Tests for sentiment analysis."""

    def test_positive_sentiment(self):
        """Positive text should have positive polarity."""
        from research_modules.news_sentiment.processing.sentiment_model import analyze_sentiment
        score = analyze_sentiment("stock surge profit growth bullish rally")
        assert score.polarity > 0

    def test_negative_sentiment(self):
        """Negative text should have negative polarity."""
        from research_modules.news_sentiment.processing.sentiment_model import analyze_sentiment
        score = analyze_sentiment("crash plunge loss decline bearish recession")
        assert score.polarity < 0

    def test_neutral_sentiment(self):
        """Neutral text should have zero polarity."""
        from research_modules.news_sentiment.processing.sentiment_model import analyze_sentiment
        score = analyze_sentiment("the quick brown fox jumps over the lazy dog")
        assert score.polarity == 0

    def test_empty_text(self):
        """Empty text should return zero polarity with zero confidence."""
        from research_modules.news_sentiment.processing.sentiment_model import analyze_sentiment
        score = analyze_sentiment("")
        assert score.polarity == 0
        assert score.confidence == 0


class TestEventClassifier:
    """Tests for event classification."""

    def test_earnings_classification(self):
        """Should detect earnings events."""
        from research_modules.news_sentiment.processing.event_classifier import classify_events, EventTag
        tags = classify_events("Company reports Q3 earnings beat with strong revenue")
        assert EventTag.EARNINGS in tags

    def test_macro_classification(self):
        """Should detect macro events."""
        from research_modules.news_sentiment.processing.event_classifier import classify_events, EventTag
        tags = classify_events("Fed raises interest rates amid inflation concerns")
        assert EventTag.MACRO in tags

    def test_management_classification(self):
        """Should detect management changes."""
        from research_modules.news_sentiment.processing.event_classifier import classify_events, EventTag
        tags = classify_events("CEO announces resignation, new chairman appointed")
        assert EventTag.MANAGEMENT in tags

    def test_unknown_classification(self):
        """Should return UNKNOWN for unmatched text."""
        from research_modules.news_sentiment.processing.event_classifier import classify_events, EventTag
        tags = classify_events("lorem ipsum dolor sit amet")
        assert EventTag.UNKNOWN in tags


class TestNewsArticle:
    """Tests for news article dataclass."""

    def test_article_creation(self):
        """Should create article with all fields."""
        from research_modules.news_sentiment.ingestion.news_sources import NewsArticle
        article = NewsArticle(
            source="test",
            title="Test Title",
            content="Test Content",
            published_at=datetime.now(),
            fetched_at=datetime.now(),
        )
        assert article.title == "Test Title"

    def test_article_to_dict(self):
        """Should convert to dictionary."""
        from research_modules.news_sentiment.ingestion.news_sources import NewsArticle
        article = NewsArticle(
            source="test",
            title="Test",
            content="Content",
            published_at=datetime.now(),
            fetched_at=datetime.now(),
        )
        d = article.to_dict()
        assert "title" in d
        assert "source" in d
