"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
Volatility Context CLI

Command-line interface for generating context snapshots.
REQUIRES explicit --research-mode flag for safety.
##############################################################################
"""

import argparse
import sys
import os
import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main(argv=None):
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="TraderFund Volatility Context Analysis (RESEARCH-ONLY)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
##############################################################################
## WARNING: THIS IS A RESEARCH TOOL
##
## Context snapshots are OBSERVATIONS, not trade recommendations.
## Do NOT use volatility labels to filter or size trades without
## completing the full governance activation process.
##
## See docs/governance/RESEARCH_MODULE_GOVERNANCE.md for activation rules.
##############################################################################
""",
    )

    parser.add_argument(
        "--data-path",
        required=True,
        help="Path to the historical data file (Parquet or CSV)",
    )
    parser.add_argument(
        "--symbol",
        required=True,
        help="Symbol to analyze",
    )
    parser.add_argument(
        "--atr-period",
        type=int,
        default=14,
        help="ATR calculation period (default: 14)",
    )
    parser.add_argument(
        "--lookback",
        type=int,
        default=20,
        help="Historical lookback period (default: 20)",
    )
    parser.add_argument(
        "--research-mode",
        action="store_true",
        help="REQUIRED: Explicitly acknowledge this is research-only",
    )

    args = parser.parse_args(argv)

    # Safety gate: require explicit research mode flag
    if not args.research_mode:
        print("\n" + "=" * 70)
        print("🚫 ERROR: --research-mode flag is REQUIRED")
        print("=" * 70)
        print("\nThis volatility context tool is strictly RESEARCH-ONLY.")
        print("Context labels must NOT be used for live trade decisions")
        print("without explicit governance approval.")
        print("\nExample:")
        print(f"  python -m research_modules.volatility_context.cli --data-path {args.data_path} --symbol {args.symbol} --research-mode")
        print("=" * 70 + "\n")
        sys.exit(1)

    # Print research mode banner
    print("\n" + "#" * 70)
    print("## RESEARCH-ONLY MODE ACTIVATED ##")
    print("#" * 70)
    print("⚠️  Context labels are OBSERVATIONS, not trade recommendations.")
    print("⚠️  See PHASE_LOCK.md for activation requirements.")
    print("#" * 70 + "\n")

    # Import here to trigger phase lock check
    try:
        from .runner import ContextRunner
    except RuntimeError as e:
        print(f"\n🚫 PHASE LOCK ERROR: {e}\n")
        sys.exit(1)

    # Load data
    data_path = Path(args.data_path)
    if not data_path.exists():
        print(f"\n🚫 ERROR: Data file not found: {data_path}\n")
        sys.exit(1)

    try:
        if str(data_path).endswith(".parquet"):
            df = pd.read_parquet(data_path)
        else:
            df = pd.read_csv(data_path)
    except Exception as e:
        print(f"\n🚫 ERROR: Failed to load data: {e}\n")
        sys.exit(1)

    # Run analysis
    runner = ContextRunner(
        atr_period=args.atr_period,
        lookback_period=args.lookback,
    )

    try:
        snapshot = runner.analyze(df, symbol=args.symbol)
        runner.print_snapshot(snapshot)
    except Exception as e:
        print(f"\n🚫 ERROR: Analysis failed: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
