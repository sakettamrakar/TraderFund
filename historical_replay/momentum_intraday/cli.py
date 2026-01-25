"""CLI for Historical Intraday Momentum Replay.

Usage:
    python historical_replay/momentum_intraday/cli.py --symbol RELIANCE --date 2026-01-03
    python historical_replay/momentum_intraday/cli.py --symbol TCS --date 2026-01-03 --interval 5
"""

import sys
import argparse
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from historical_replay.momentum_intraday.replay_runner import run_replay, run_batch_replay
from ingestion.api_ingestion.angel_smartapi.config import config as angel_config
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def get_dates_for_month(month_str: str, symbols: list) -> list:
    """Discover available trading dates for a month from processed Parquet files.
    
    Args:
        month_str: Format YYYY-MM
        symbols: List of symbols to check
    """
    processed_path = Path("data/processed/candles/intraday")
    available_dates = set()
    
    for symbol in symbols:
        file_path = processed_path / f"NSE_{symbol}_1m.parquet"
        if file_path.exists():
            try:
                # Read only timestamp column for speed
                df = pd.read_parquet(file_path, columns=['timestamp'])
                df['date_str'] = df['timestamp'].dt.strftime('%Y-%m-%d')
                # Filter indices starting with month_str
                month_dates = df[df['date_str'].str.startswith(month_str)]['date_str'].unique()
                available_dates.update(month_dates)
            except Exception as e:
                logging.error(f"Error reading dates for {symbol}: {e}")
                
    return sorted(list(available_dates))

def main():
    parser = argparse.ArgumentParser(
        description="Historical Intraday Momentum Replay - Diagnostic Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python historical_replay/momentum_intraday/cli.py --symbol RELIANCE --date 2026-01-03
  python historical_replay/momentum_intraday/cli.py --symbol ALL --date 2025-12
  python historical_replay/momentum_intraday/cli.py --symbol TCS --date 2025-12-15 --interval 5

WARNING: This is a DIAGNOSTIC tool only. Do not use for trading decisions.
        """
    )
    
    parser.add_argument(
        "--symbol",
        type=str,
        required=True,
        help="Trading symbol to replay (e.g., RELIANCE, TCS, or 'ALL')"
    )
    
    parser.add_argument(
        "--date",
        type=str,
        required=True,
        help="Date to replay in YYYY-MM-DD format, or YYYY-MM for an entire month"
    )
    
    parser.add_argument(
        "--interval",
        type=int,
        default=1,
        help="Evaluation interval in minutes (default: 1)"
    )
    
    parser.add_argument(
        "--no-sanity-checks",
        action="store_true",
        help="Skip sanity checks after replay"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Resolve Symbols
    if args.symbol.upper() == "ALL":
        symbols = angel_config.symbol_watchlist
    else:
        symbols = [s.strip().upper() for s in args.symbol.split(",")]

    # Resolve Dates
    if len(args.date) == 7:  # YYYY-MM
        dates = get_dates_for_month(args.date, symbols)
        if not dates:
            print(f"ERROR: No processed data found for month {args.date}")
            sys.exit(1)
    else:
        dates = [args.date]

    print()
    print("=" * 60)
    print("HISTORICAL INTRADAY MOMENTUM REPLAY")
    print("=" * 60)
    print(f"Symbols:  {', '.join(symbols)}")
    print(f"Dates:    {args.date} ({len(dates)} days found)")
    print(f"Interval: {args.interval}m")
    print("=" * 60)
    print()
    print("⚠️  WARNING: This is a DIAGNOSTIC tool only.")
    print("    Do not use for trading decisions or optimization.")
    print()
    
    try:
        if len(symbols) > 1 or len(dates) > 1:
            # Run batch
            results = run_batch_replay(
                symbols=symbols,
                dates=dates,
                interval_minutes=args.interval,
                run_sanity_checks=not args.no_sanity_checks
            )
            print()
            print("=" * 60)
            print("BATCH REPLAY RESULTS")
            print("=" * 60)
            print(f"Dates Processed:   {results['dates_processed']}")
            print(f"Symbols Processed: {results['symbols_processed']}")
            print(f"Total Signals:     {results['total_signals']}")
            print("=" * 60)
        else:
            # Run single
            results = run_replay(
                symbol=symbols[0],
                replay_date=dates[0],
                interval_minutes=args.interval,
                run_sanity_checks=not args.no_sanity_checks
            )
            
            print()
            print("=" * 60)
            print("REPLAY RESULTS")
            print("=" * 60)
            print(f"Total Candles:     {results.get('total_candles', 'N/A')}")
            print(f"Evaluation Points: {results.get('evaluation_points', 'N/A')}")
            print(f"Signals Generated: {results.get('signals_generated', 0)}")
            print(f"Output File:       {results.get('output_file', 'N/A')}")
            print("=" * 60)
            
            # Print sanity check results if available
            if 'sanity_checks' in results:
                print()
                print("SANITY CHECKS")
                print("-" * 40)
                for check in results['sanity_checks']:
                    status = "✓ PASS" if check['passed'] else "✗ FAIL"
                    print(f"  {status}: {check['check']}")
                print()
        
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        print("Make sure historical data exists in data/processed/candles/intraday/")
        sys.exit(1)
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        raise


if __name__ == "__main__":
    main()
