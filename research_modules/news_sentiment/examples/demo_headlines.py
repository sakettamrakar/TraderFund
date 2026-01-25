"""
Minimal demo: Print 3 sample news headlines with timestamps.
RESEARCH-MODE ONLY
"""
import os
os.environ["TRADERFUND_ACTIVE_PHASE"] = "6"  # Required for research module

from datetime import datetime, timedelta
from research_modules.news_sentiment.ingestion.news_sources import NewsArticle, MockNewsSource
from research_modules.news_sentiment.ingestion.raw_fetcher import RawNewsFetcher

# Create sample articles
sample_articles = [
    NewsArticle(
        source="economic_times",
        title="ITC Reports Strong Q3 Earnings, Beats Street Estimates",
        content="ITC Limited reported a 15% increase in net profit for Q3.",
        published_at=datetime.now() - timedelta(hours=2),
        fetched_at=datetime.now(),
        symbol="ITC",
    ),
    NewsArticle(
        source="moneycontrol",
        title="RBI Holds Rates Steady Amid Inflation Concerns",
        content="The Reserve Bank of India maintained policy rates unchanged.",
        published_at=datetime.now() - timedelta(hours=5),
        fetched_at=datetime.now(),
        symbol="NIFTY",
    ),
    NewsArticle(
        source="livemint",
        title="HDFC Bank Announces Interim Dividend of Rs 19",
        content="HDFC Bank declared an interim dividend for shareholders.",
        published_at=datetime.now() - timedelta(hours=8),
        fetched_at=datetime.now(),
        symbol="HDFCBANK",
    ),
]

# Fetch and print
source = MockNewsSource(sample_articles)
fetcher = RawNewsFetcher([source])
articles = fetcher.fetch_all()

print("\n" + "=" * 60)
print("SAMPLE NEWS HEADLINES (RESEARCH-MODE)")
print("=" * 60)

for i, article in enumerate(articles[:3], 1):
    print(f"\n[{i}] {article.title}")
    print(f"    Source: {article.source}")
    print(f"    Symbol: {article.symbol}")
    print(f"    Published: {article.published_at.strftime('%Y-%m-%d %H:%M')}")

print("\n" + "=" * 60)
