"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
Comprehensive Validation Tests for News & Sentiment Module

Tests cover:
1. Ingestion sanity
2. Sentiment determinism
3. Event tagging sanity
4. Guardrail enforcement
5. Output isolation
##############################################################################
"""

import os
import sys
import pytest
import json
import tempfile
from datetime import datetime, timedelta
from unittest.mock import patch
from pathlib import Path


# =============================================================================
# TEST 1: INGESTION SANITY
# =============================================================================

class TestIngestionSanity:
    """Verify raw text is stored verbatim with correct timestamps."""

    @pytest.fixture
    def sample_news_file(self, tmp_path):
        """Create a sample news JSON file."""
        articles = [
            {
                "title": "ITC Reports Strong Q3 Earnings",
                "content": "ITC Limited reported a 15% increase in net profit for Q3.",
                "published_at": "2026-01-02T10:30:00",
                "symbol": "ITC",
                "url": "https://example.com/itc-q3"
            },
            {
                "title": "HDFC Bank Announces Dividend",
                "content": "HDFC Bank declared an interim dividend of Rs 19 per share.",
                "published_at": "2026-01-02T11:00:00",
                "symbol": "HDFCBANK",
                "url": "https://example.com/hdfc-dividend"
            }
        ]
        file_path = tmp_path / "test_news.json"
        with open(file_path, "w") as f:
            json.dump(articles, f)
        return file_path

    def test_raw_text_stored_verbatim(self, sample_news_file):
        """Text should be stored exactly as received."""
        from research_modules.news_sentiment.ingestion.news_sources import FileNewsSource

        source = FileNewsSource(str(sample_news_file), "test")
        articles = list(source.fetch())

        assert len(articles) == 2
        # Verify verbatim storage
        assert articles[0].title == "ITC Reports Strong Q3 Earnings"
        assert articles[0].content == "ITC Limited reported a 15% increase in net profit for Q3."
        print(f"\n✅ Raw text stored verbatim: '{articles[0].title}'")

    def test_timestamps_correct(self, sample_news_file):
        """Published timestamps should be parsed correctly."""
        from research_modules.news_sentiment.ingestion.news_sources import FileNewsSource

        source = FileNewsSource(str(sample_news_file), "test")
        articles = list(source.fetch())

        assert articles[0].published_at.year == 2026
        assert articles[0].published_at.month == 1
        assert articles[0].published_at.day == 2
        print(f"\n✅ Timestamp correct: {articles[0].published_at}")

    def test_no_symbol_leakage(self, sample_news_file):
        """Symbol filter should not leak articles from other symbols."""
        from research_modules.news_sentiment.ingestion.news_sources import FileNewsSource
        from research_modules.news_sentiment.ingestion.raw_fetcher import RawNewsFetcher

        source = FileNewsSource(str(sample_news_file), "test")
        fetcher = RawNewsFetcher([source])

        itc_articles = fetcher.fetch_by_symbol("ITC")
        hdfc_articles = fetcher.fetch_by_symbol("HDFCBANK")

        assert len(itc_articles) == 1
        assert len(hdfc_articles) == 1
        assert itc_articles[0].symbol == "ITC"
        assert hdfc_articles[0].symbol == "HDFCBANK"
        print("\n✅ No symbol leakage: ITC gets 1, HDFC gets 1")


# =============================================================================
# TEST 2: SENTIMENT DETERMINISM
# =============================================================================

class TestSentimentDeterminism:
    """Verify same input produces same output."""

    @pytest.fixture
    def test_texts(self):
        return [
            "Stock surges on strong earnings beat, bullish momentum continues",
            "Market crashes as recession fears grow, investors sell in panic",
            "Company reports quarterly results, revenue flat year-over-year",
        ]

    def test_same_scores_on_repeat(self, test_texts):
        """Running twice should produce identical scores."""
        from research_modules.news_sentiment.processing.sentiment_model import analyze_sentiment

        for text in test_texts:
            score1 = analyze_sentiment(text)
            score2 = analyze_sentiment(text)

            assert score1.polarity == score2.polarity, f"Polarity differs for: {text[:30]}..."
            assert score1.confidence == score2.confidence, f"Confidence differs for: {text[:30]}..."

        print("\n✅ Sentiment scores are deterministic")

    def test_same_tags_on_repeat(self, test_texts):
        """Event tags should be consistent."""
        from research_modules.news_sentiment.processing.event_classifier import classify_events

        for text in test_texts:
            tags1 = classify_events(text)
            tags2 = classify_events(text)

            assert tags1 == tags2, f"Tags differ for: {text[:30]}..."

        print("\n✅ Event tags are deterministic")

    def test_same_ordering(self):
        """Multiple texts should produce same order."""
        from research_modules.news_sentiment.processing.sentiment_model import analyze_batch

        texts = ["positive surge growth", "negative crash decline", "neutral text here"]

        results1 = analyze_batch(texts)
        results2 = analyze_batch(texts)

        for i, (r1, r2) in enumerate(zip(results1, results2)):
            assert r1.polarity == r2.polarity
            assert r1.confidence == r2.confidence

        print("\n✅ Batch ordering is consistent")


# =============================================================================
# TEST 3: EVENT TAGGING SANITY
# =============================================================================

class TestEventTaggingSanity:
    """Manually verify classification correctness."""

    def test_earnings_tagged_correctly(self):
        """Earnings-related text should be tagged as EARNINGS."""
        from research_modules.news_sentiment.processing.event_classifier import classify_events, EventTag

        earnings_texts = [
            "Company reports Q3 earnings with 20% revenue growth",
            "EPS beats estimates, quarterly results exceed guidance",
            "Annual profit forecast raised after strong performance",
        ]

        for text in earnings_texts:
            tags = classify_events(text)
            assert EventTag.EARNINGS in tags, f"Failed to tag as earnings: {text[:40]}..."

        print("\n✅ Earnings articles correctly tagged")

    def test_regulation_tagged_correctly(self):
        """Regulatory news should be tagged as REGULATION."""
        from research_modules.news_sentiment.processing.event_classifier import classify_events, EventTag

        regulation_texts = [
            "SEBI announces new compliance requirements for brokers",
            "RBI regulatory policy update affects banking sector",
            "Government ministry issues new license approval rules",
        ]

        for text in regulation_texts:
            tags = classify_events(text)
            assert EventTag.REGULATION in tags, f"Failed to tag as regulation: {text[:40]}..."

        print("\n✅ Regulation articles correctly tagged")

    def test_macro_tagged_correctly(self):
        """Macro economic news should be tagged as MACRO."""
        from research_modules.news_sentiment.processing.event_classifier import classify_events, EventTag

        macro_texts = [
            "Fed raises interest rates amid inflation concerns",
            "GDP growth slows as economy enters recession",
            "Central bank announces monetary policy changes",
        ]

        for text in macro_texts:
            tags = classify_events(text)
            assert EventTag.MACRO in tags, f"Failed to tag as macro: {text[:40]}..."

        print("\n✅ Macro articles correctly tagged")

    def test_management_tagged_correctly(self):
        """Management changes should be tagged correctly."""
        from research_modules.news_sentiment.processing.event_classifier import classify_events, EventTag

        management_texts = [
            "CEO announces resignation effective immediately",
            "Board appoints new chairman after leadership search",
            "CFO departure triggers management reshuffle",
        ]

        for text in management_texts:
            tags = classify_events(text)
            assert EventTag.MANAGEMENT in tags, f"Failed to tag as management: {text[:40]}..."

        print("\n✅ Management articles correctly tagged")

    def test_unknown_for_unrelated_text(self):
        """Unrelated text should get UNKNOWN tag."""
        from research_modules.news_sentiment.processing.event_classifier import classify_events, EventTag

        text = "The quick brown fox jumps over the lazy dog"
        tags = classify_events(text)
        assert EventTag.UNKNOWN in tags

        print("\n✅ Unrelated text tagged as UNKNOWN")


# =============================================================================
# TEST 4: GUARDRAIL ENFORCEMENT
# =============================================================================

class TestGuardrailEnforcement:
    """Verify misuse fails loudly."""

    def test_fails_at_phase_5(self):
        """Module MUST raise RuntimeError at Phase 5."""
        import subprocess

        result = subprocess.run(
            ["python", "-c",
             "import os; os.environ['TRADERFUND_ACTIVE_PHASE']='5'; "
             "from research_modules.news_sentiment import SentimentRunner"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent.parent.parent),
            encoding='utf-8',
            errors='replace'
        )

        assert result.returncode != 0, "Should fail at Phase 5!"
        assert "PHASE LOCK" in result.stderr or "RuntimeError" in result.stderr

        print(f"\n✅ LOUD FAILURE at Phase 5")

    def test_cli_fails_without_research_mode(self):
        """CLI MUST exit with error without --research-mode."""
        import subprocess

        result = subprocess.run(
            ["python", "-m", "research_modules.news_sentiment.cli",
             "--symbol", "TEST"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent.parent.parent),
            encoding='utf-8',
            errors='replace'
        )

        assert result.returncode != 0, "CLI should exit with error!"
        output = result.stdout + result.stderr
        assert "research-mode" in output.lower(), "Error should mention --research-mode"

        print(f"\n✅ CLI LOUD FAILURE: Exit code {result.returncode}")

    def test_error_message_is_clear(self):
        """Error messages should be informative."""
        import subprocess

        result = subprocess.run(
            ["python", "-m", "research_modules.news_sentiment.cli",
             "--symbol", "TEST"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent.parent.parent),
            encoding='utf-8',
            errors='replace'
        )

        output = result.stdout + result.stderr
        # Should mention research-mode requirement
        assert "research-mode" in output.lower(), f"Error should mention research-mode, got: {output[:200]}"

        print("\n✅ Error message is clear and actionable")


# =============================================================================
# TEST 5: OUTPUT ISOLATION
# =============================================================================

class TestOutputIsolation:
    """Verify no production side effects."""

    def test_no_files_written_to_production(self, tmp_path):
        """Sentiment analysis should not create any production files."""
        from research_modules.news_sentiment.ingestion.news_sources import MockNewsSource, NewsArticle
        from research_modules.news_sentiment.runner import SentimentRunner

        # Track production directories
        production_dirs = [
            Path("logs"),
            Path("observations"),
            Path("data/processed"),
        ]
        files_before = {}
        for d in production_dirs:
            if d.exists():
                files_before[str(d)] = len(list(d.rglob("*")))

        # Create mock source with test article
        mock_articles = [
            NewsArticle(
                source="test",
                title="Test Article",
                content="Test content with earnings and profit",
                published_at=datetime.now(),
                fetched_at=datetime.now(),
                symbol="TEST",
            )
        ]
        mock_source = MockNewsSource(mock_articles)

        # Run analysis
        runner = SentimentRunner([mock_source])
        snapshot = runner.analyze("TEST", hours=24)

        # Verify no new files
        for d in production_dirs:
            if d.exists():
                files_after = len(list(d.rglob("*")))
                assert files_after == files_before.get(str(d), 0), f"New files in {d}!"

        print("\n✅ NO PRODUCTION FILES WRITTEN")

    def test_snapshot_is_read_only(self):
        """Snapshot should be immutable (frozen dataclass)."""
        from research_modules.news_sentiment.sentiment_snapshot import SentimentSnapshot
        from research_modules.news_sentiment.processing.sentiment_model import SentimentScore
        from research_modules.news_sentiment.processing.event_classifier import EventTag

        snapshot = SentimentSnapshot(
            symbol="TEST",
            time_window_start=datetime.now() - timedelta(hours=24),
            time_window_end=datetime.now(),
            article_count=5,
            sentiment_score=SentimentScore(0.5, 0.8, "test"),
            dominant_topics=["earnings", "growth"],
            event_tags=[EventTag.EARNINGS],
            snapshot_time=datetime.now(),
        )

        # Should raise FrozenInstanceError
        with pytest.raises(Exception):  # dataclasses.FrozenInstanceError
            snapshot.symbol = "MODIFIED"

        print("\n✅ SNAPSHOT IS IMMUTABLE")

    def test_no_signal_objects_touched(self):
        """Module should not import or modify signal objects."""
        # Check that no momentum/signal imports exist
        import research_modules.news_sentiment.runner as runner_module
        import research_modules.news_sentiment.sentiment_snapshot as snapshot_module

        with open(runner_module.__file__, encoding='utf-8') as f:
            runner_source = f.read()
        with open(snapshot_module.__file__, encoding='utf-8') as f:
            snapshot_source = f.read()

        forbidden_imports = ["momentum_engine", "core_modules"]
        for imp in forbidden_imports:
            assert imp not in runner_source, f"Found forbidden import: {imp}"
            assert imp not in snapshot_source, f"Found forbidden import: {imp}"

        print("\n✅ NO SIGNAL OBJECTS TOUCHED")
