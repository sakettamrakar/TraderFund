"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
Backtest CLI

Command-line interface for running backtests.
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
        description="TraderFund Backtesting Engine (RESEARCH-ONLY)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
##############################################################################
## WARNING: THIS IS A RESEARCH TOOL
##
## Results from this backtesting engine MUST NOT be used to make live
## trading decisions without extensive validation through observation
## and paper trading phases.
##
## See docs/governance/RESEARCH_MODULE_GOVERNANCE.md for activation rules.
##############################################################################
""",
    )

    parser.add_argument(
        "--data-path",
        required=True,
        help="Path to the historical data directory (e.g., data/processed/intraday/)",
    )
    parser.add_argument(
        "--data-file",
        required=True,
        help="Name of the data file (e.g., NSE_ITC.parquet)",
    )
    parser.add_argument(
        "--initial-capital",
        type=float,
        default=100000.0,
        help="Initial capital for the simulation (default: 100000)",
    )
    parser.add_argument(
        "--research-mode",
        action="store_true",
        help="REQUIRED: Explicitly acknowledge this is research-only",
    )
    parser.add_argument(
        "--strategy",
        default="example",
        help="Strategy to run (default: example)",
    )

    args = parser.parse_args(argv)

    # Safety gate: require explicit research mode flag
    if not args.research_mode:
        print("\n" + "=" * 70)
        print("🚫 ERROR: --research-mode flag is REQUIRED")
        print("=" * 70)
        print("\nThis backtesting engine is strictly RESEARCH-ONLY.")
        print("You must explicitly acknowledge this by adding --research-mode.")
        print("\nExample:")
        print(f"  python -m research_modules.backtesting.cli --data-path {args.data_path} --data-file {args.data_file} --research-mode")
        print("=" * 70 + "\n")
        sys.exit(1)

    # Print research mode banner
    print("\n" + "#" * 70)
    print("## RESEARCH-ONLY MODE ACTIVATED ##")
    print("#" * 70)
    print("⚠️  Results from this backtest MUST NOT influence live trading.")
    print("⚠️  See PHASE_LOCK.md for activation requirements.")
    print("#" * 70 + "\n")

    # Import here to trigger phase lock check
    try:
        from .runner import BacktestRunner, RunnerConfig
        from .engine import StrategyBase
    except RuntimeError as e:
        print(f"\n🚫 PHASE LOCK ERROR: {e}\n")
        sys.exit(1)

    # Example strategy for demonstration
    class ExampleStrategy(StrategyBase):
        """Simple example strategy: buy on volume spike, sell after 5 candles."""
        def __init__(self):
            self.candle_count = 0
            self.in_trade = False

        def on_candle(self, candle, state):
            self.candle_count += 1

            if not self.in_trade and candle.get("volume", 0) > 2000:
                self.in_trade = True
                self.entry_candle = self.candle_count
                return {"action": "BUY", "quantity": 10}

            if self.in_trade and self.candle_count >= self.entry_candle + 5:
                self.in_trade = False
                return {"action": "SELL"}

            return None

    # Run backtest
    config = RunnerConfig(
        data_path=args.data_path,
        data_file=args.data_file,
        initial_capital=args.initial_capital,
    )

    runner = BacktestRunner(config)
    report = runner.run(ExampleStrategy())
    runner.print_report(report)


if __name__ == "__main__":
    main()
