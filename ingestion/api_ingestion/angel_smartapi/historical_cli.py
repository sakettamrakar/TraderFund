"""Historical Data CLI - Manual Backfill Utility.

This CLI provides a MANUAL, ON-DEMAND interface for backfilling
historical daily candle data from Angel One SmartAPI.

CRITICAL ISOLATION NOTICE:
========================
This utility is DORMANT and NOT part of any live scheduler.
Use only for manual backfill operations for:
- Future context and diagnostics
- Risk analysis
- Compliance record-keeping

Usage:
------
    # Single symbol
    python -m ingestion.api_ingestion.angel_smartapi.historical_cli --symbol RELIANCE --years 2

    # All watchlist symbols
    python -m ingestion.api_ingestion.angel_smartapi.historical_cli --all-watchlist --years 1

    # Dry run (show what would be fetched)
    python -m ingestion.api_ingestion.angel_smartapi.historical_cli --symbol TCS --years 1 --dry-run
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import date, timedelta

from .config import config
from .historical_data_ingestor import HistoricalDataIngestor, DEFAULT_LOOKBACK_YEARS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Maximum allowed lookback
MAX_LOOKBACK_YEARS = 3


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Historical Data Backfill CLI (Daily Candles Only)",
        epilog="NOTE: This is a DORMANT utility, NOT part of live trading.",
    )

    # Symbol selection
    symbol_group = parser.add_mutually_exclusive_group(required=True)
    symbol_group.add_argument(
        "--symbol",
        type=str,
        help="Single symbol to backfill (e.g., RELIANCE)",
    )
    symbol_group.add_argument(
        "--all-watchlist",
        action="store_true",
        help="Backfill all symbols in the watchlist",
    )

    # Exchange
    parser.add_argument(
        "--exchange",
        type=str,
        default="NSE",
        help="Exchange segment (default: NSE)",
    )

    # Date range
    parser.add_argument(
        "--years",
        type=int,
        default=DEFAULT_LOOKBACK_YEARS,
        choices=range(1, MAX_LOOKBACK_YEARS + 1),
        metavar=f"[1-{MAX_LOOKBACK_YEARS}]",
        help=f"Lookback period in years (default: {DEFAULT_LOOKBACK_YEARS}, max: {MAX_LOOKBACK_YEARS})",
    )

    parser.add_argument(
        "--from-date",
        type=str,
        help="Start date (YYYY-MM-DD). Overrides --years if specified.",
    )

    parser.add_argument(
        "--to-date",
        type=str,
        help="End date (YYYY-MM-DD). Defaults to today.",
    )

    # Execution control
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Skip confirmation prompt",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be fetched without executing",
    )

    return parser.parse_args()


def parse_date(date_str: str) -> date:
    """Parse date string in YYYY-MM-DD format."""
    try:
        return date.fromisoformat(date_str)
    except ValueError:
        logger.error(f"Invalid date format: {date_str}. Use YYYY-MM-DD.")
        sys.exit(1)


def get_confirmation(message: str) -> bool:
    """Prompt user for confirmation."""
    print(f"\n{message}")
    print("-" * 60)
    response = input("Proceed? [y/N]: ").strip().lower()
    return response in ("y", "yes")


def main() -> None:
    """Main CLI entry point."""
    args = parse_args()

    # Validate credentials
    if not config.validate_historical():
        missing = config.get_missing_credentials(mode="historical")
        logger.error(f"Missing Angel One historical credentials: {missing}")
        logger.error("Please set ANGEL_HIST_* credentials in .env file.")
        sys.exit(1)

    # Determine date range
    to_date = parse_date(args.to_date) if args.to_date else date.today()

    if args.from_date:
        from_date = parse_date(args.from_date)
    else:
        from_date = to_date - timedelta(days=args.years * 365)

    # Determine symbols to process
    if args.all_watchlist:
        symbols = config.symbol_watchlist
        exchange = args.exchange
    else:
        symbols = [args.symbol]
        exchange = args.exchange

    # Display operation summary
    print("\n" + "=" * 60)
    print("HISTORICAL DATA BACKFILL - DAILY CANDLES")
    print("=" * 60)
    print(f"\n  Mode:       {'DRY RUN' if args.dry_run else 'LIVE EXECUTION'}")
    print(f"  Symbols:    {', '.join(symbols)}")
    print(f"  Exchange:   {exchange}")
    print(f"  From:       {from_date}")
    print(f"  To:         {to_date}")
    print(f"  Days:       {(to_date - from_date).days}")
    print(f"  Output:     {config.historical_path}/")
    print("\n" + "-" * 60)
    print("  ⚠️  This data is for CONTEXT/DIAGNOSTICS only.")
    print("  ⚠️  It must NOT be used for momentum trading.")
    print("-" * 60)

    # Confirmation
    if not args.dry_run and not args.confirm:
        if not get_confirmation("Ready to fetch historical data?"):
            print("Aborted.")
            sys.exit(0)

    # Dry run - just show what would be done
    if args.dry_run:
        print("\n[DRY RUN] Would fetch the following:")
        for symbol in symbols:
            print(f"  - {exchange}_{symbol}_1d.jsonl ({(to_date - from_date).days} days)")
        print("\nNo data was fetched. Remove --dry-run to execute.")
        return

    # Execute backfill
    ingestor = HistoricalDataIngestor()
    results = {}

    print("\nStarting backfill...\n")

    for symbol in symbols:
        try:
            count = ingestor.fetch_and_save(
                symbol=symbol,
                exchange=exchange,
                from_date=from_date,
                to_date=to_date,
            )
            results[symbol] = count
            status = "✓" if count > 0 else "⚠️ No data"
            print(f"  {status} {symbol}: {count} records")
        except Exception as exc:
            results[symbol] = 0
            print(f"  ✗ {symbol}: ERROR - {exc}")
            logger.exception(f"Error backfilling {symbol}")

    # Summary
    total = sum(results.values())
    success_count = sum(1 for c in results.values() if c > 0)

    print("\n" + "=" * 60)
    print("BACKFILL COMPLETE")
    print("=" * 60)
    print(f"\n  Total records:     {total}")
    print(f"  Symbols processed: {len(symbols)}")
    print(f"  Symbols with data: {success_count}")
    print(f"\n  Output directory:  {config.historical_path}/")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
