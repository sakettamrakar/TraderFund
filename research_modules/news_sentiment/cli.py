"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
News Sentiment CLI

Command-line interface for sentiment analysis.
REQUIRES explicit --research-mode flag for safety.
##############################################################################
"""

import argparse
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main(argv=None):
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="TraderFund News Sentiment Analysis (RESEARCH-ONLY)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
##############################################################################
## WARNING: THIS IS A RESEARCH TOOL
##
## Sentiment analysis is NOISY and LAGGING. It must NEVER:
## - Override price/volume signals
## - Block or boost trades based on sentiment
## - Be used as a primary decision factor
##
## Common traps: confirmation bias, hindsight narrative fitting.
##
## See docs/governance/RESEARCH_MODULE_GOVERNANCE.md for guidelines.
##############################################################################
""",
    )

    parser.add_argument("--symbol", required=True, help="Symbol to analyze")
    parser.add_argument("--news-file", help="Path to JSON file with news articles")
    parser.add_argument("--hours", type=int, default=24, help="Lookback hours (default: 24)")
    parser.add_argument(
        "--research-mode",
        action="store_true",
        help="REQUIRED: Explicitly acknowledge this is research-only",
    )

    args = parser.parse_args(argv)

    # Safety gate
    if not args.research_mode:
        print("\n" + "=" * 70)
        print("🚫 ERROR: --research-mode flag is REQUIRED")
        print("=" * 70)
        print("\nThis sentiment analysis tool is strictly RESEARCH-ONLY.")
        print("Sentiment scores must NOT influence trade decisions")
        print("without explicit governance approval.")
        print("\nExample:")
        print(f"  python -m research_modules.news_sentiment.cli --symbol {args.symbol} --news-file news.json --research-mode")
        print("=" * 70 + "\n")
        sys.exit(1)

    # Print research mode banner
    print("\n" + "#" * 70)
    print("## RESEARCH-ONLY MODE ACTIVATED ##")
    print("#" * 70)
    print("⚠️  Sentiment analysis is NOISY and LAGGING.")
    print("⚠️  Do NOT use to override price/volume signals.")
    print("#" * 70 + "\n")

    # Import here to trigger phase lock
    try:
        from .runner import SentimentRunner
        from .ingestion.news_sources import FileNewsSource
    except RuntimeError as e:
        print(f"\n🚫 PHASE LOCK ERROR: {e}\n")
        sys.exit(1)

    # Set up runner
    runner = SentimentRunner()

    if args.news_file:
        source = FileNewsSource(args.news_file, "file_input")
        runner.add_source(source)

    # Run analysis
    try:
        snapshot = runner.analyze(symbol=args.symbol, hours=args.hours)
        runner.print_snapshot(snapshot)
    except Exception as e:
        print(f"\n🚫 ERROR: Analysis failed: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
