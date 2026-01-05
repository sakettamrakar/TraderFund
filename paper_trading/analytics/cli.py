"""
##############################################################################
## PAPER TRADING ANALYTICS - READ ONLY
##############################################################################
Analytics CLI

Command-line interface for paper trading analytics.
##############################################################################
"""

import argparse
import sys
import os
import logging
from datetime import datetime, date
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main(argv=None):
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="TraderFund Paper Trading Analytics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
##############################################################################
## THIS IS A READ-ONLY ANALYTICS TOOL
##
## Use this dashboard to REVIEW paper trading behavior AFTER the session.
## It does NOT feed back into strategy or execution.
##
## Common misinterpretations:
## - High win rate does NOT mean the strategy works
## - Positive P&L could be luck
## - Past paper results do NOT predict future real results
##############################################################################
""",
    )

    parser.add_argument("--date", help="Date to analyze (YYYY-MM-DD)")
    parser.add_argument("--start-date", help="Start of date range (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="End of date range (YYYY-MM-DD)")
    parser.add_argument("--log-dir", help="Directory containing trade logs")
    parser.add_argument("--summary", action="store_true", help="Show summary dashboard")
    parser.add_argument("--plots", action="store_true", help="Generate plots")
    parser.add_argument("--output-dir", help="Directory for plot output")

    args = parser.parse_args(argv)

    # Check phase lock
    try:
        from . import _check_phase_lock
        _check_phase_lock()
    except RuntimeError as e:
        print(f"\n🚫 PHASE LOCK ERROR: {e}\n")
        sys.exit(1)

    # Import components
    from .data_loader import load_trade_logs
    from .dashboard import print_dashboard
    from .plots import generate_all_plots

    # Parse dates
    date_filter = None
    start_date = None
    end_date = None

    if args.date:
        date_filter = datetime.strptime(args.date, "%Y-%m-%d").date()
    if args.start_date:
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d").date()
    if args.end_date:
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d").date()

    # Load data
    log_dir = Path(args.log_dir) if args.log_dir else None
    df = load_trade_logs(
        log_dir=log_dir,
        date_filter=date_filter,
        start_date=start_date,
        end_date=end_date,
    )

    if df.empty:
        print("\n⚠️  No trade data found for the specified criteria.\n")
        sys.exit(0)

    # Generate summary
    if args.summary or not args.plots:
        print_dashboard(df)

    # Generate plots
    if args.plots:
        output_dir = Path(args.output_dir) if args.output_dir else None
        plots = generate_all_plots(df, output_dir)
        if plots:
            print("\n📊 Generated plots:")
            for name, path in plots.items():
                print(f"   • {name}: {path}")
            print()
        else:
            print("\n⚠️  No plots generated (matplotlib may not be available)\n")


if __name__ == "__main__":
    main()
