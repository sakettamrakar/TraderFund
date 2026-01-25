"""
##############################################################################
## PAPER TRADING ONLY - NO REAL ORDERS
##############################################################################
Paper Trading CLI

Command-line interface for paper trading.
REQUIRES --paper-mode flag for safety.
##############################################################################
"""

import argparse
import sys
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main(argv=None):
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="TraderFund Paper Trading (PHASE 6 ONLY)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
##############################################################################
## WARNING: THIS IS A SIMULATION
##
## Paper trading simulates order execution without real orders.
## Results are NOT proof of real performance.
##
## This module:
## - Consumes Momentum Engine signals
## - Simulates fills with optional slippage
## - Logs trades for review
##
## This module does NOT:
## - Place real orders
## - Connect to broker APIs
## - Risk real capital
##############################################################################
""",
    )

    parser.add_argument(
        "--paper-mode",
        action="store_true",
        help="REQUIRED: Acknowledge this is paper trading only",
    )
    parser.add_argument("--session", default="intraday", help="Session name for logs")
    parser.add_argument("--exit-minutes", type=float, default=5.0, help="Time-based exit (minutes)")
    parser.add_argument("--slippage", type=float, default=0.0, help="Slippage percentage")
    parser.add_argument("--quantity", type=int, default=1, help="Default quantity per trade")

    args = parser.parse_args(argv)

    # Safety gate: require --paper-mode
    if not args.paper_mode:
        print("\n" + "=" * 70)
        print("🚫 ERROR: --paper-mode flag is REQUIRED")
        print("=" * 70)
        print("\nPaper trading must be explicitly acknowledged.")
        print("This prevents accidental execution assumptions.")
        print("\nExample:")
        print(f"  python -m paper_trading.execution.cli --paper-mode --session {args.session}")
        print("=" * 70 + "\n")
        sys.exit(1)

    # Print paper mode banner
    print("\n" + "#" * 70)
    print("## PAPER TRADING MODE ACTIVATED ##")
    print("#" * 70)
    print("⚠️  NO REAL ORDERS will be placed.")
    print("⚠️  Results are SIMULATED, not real performance.")
    print("#" * 70 + "\n")

    # Check phase lock
    try:
        from . import _check_phase_lock
        _check_phase_lock()
    except RuntimeError as e:
        print(f"\n🚫 PHASE LOCK ERROR: {e}\n")
        sys.exit(1)

    # Import executor
    from .trade_executor import PaperTradeExecutor

    # Initialize executor
    executor = PaperTradeExecutor(
        slippage_pct=args.slippage,
        default_quantity=args.quantity,
        exit_minutes=args.exit_minutes,
        session_name=args.session,
    )

    print(f"Session: {args.session}")
    print(f"Exit after: {args.exit_minutes} minutes")
    print(f"Slippage: {args.slippage}%")
    print(f"Default quantity: {args.quantity}")
    print("\nReady to receive momentum signals.")
    print("(In production, this would connect to the signal stream.)")
    print("\n" + "=" * 70)

    # In a real implementation, this would:
    # 1. Subscribe to momentum signal stream
    # 2. Execute signals as they arrive
    # 3. Check time-based exits periodically
    # For now, just print the summary

    executor.print_summary()


if __name__ == "__main__":
    main()
