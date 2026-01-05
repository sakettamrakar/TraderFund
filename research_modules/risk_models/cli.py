"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
Risk Models CLI

Command-line interface for risk simulations.
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
        description="TraderFund Risk Modeling (RESEARCH-ONLY)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
##############################################################################
## WARNING: THIS IS A RESEARCH TOOL
##
## Risk simulations are for analysis only. Position sizes and stop prices
## calculated here must NOT be used for live trading without completing
## the full governance activation process.
##
## See docs/governance/RESEARCH_MODULE_GOVERNANCE.md for activation rules.
##############################################################################
""",
    )

    parser.add_argument("--symbol", required=True, help="Symbol to analyze")
    parser.add_argument("--entry", type=float, required=True, help="Entry price")
    parser.add_argument("--stop", type=float, help="Stop price (for fixed risk model)")
    parser.add_argument("--atr", type=float, help="ATR value (for ATR-based model)")
    parser.add_argument("--atr-mult", type=float, default=2.0, help="ATR multiplier")
    parser.add_argument("--capital", type=float, default=100000, help="Account capital")
    parser.add_argument("--risk-pct", type=float, default=1.0, help="Risk percentage")
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
        print("\nThis risk modeling tool is strictly RESEARCH-ONLY.")
        print("Simulated positions must NOT be used for live trading")
        print("without explicit governance approval.")
        print("\nExample:")
        print(f"  python -m research_modules.risk_models.cli --symbol {args.symbol} --entry {args.entry} --stop 95 --research-mode")
        print("=" * 70 + "\n")
        sys.exit(1)

    # Print research mode banner
    print("\n" + "#" * 70)
    print("## RESEARCH-ONLY MODE ACTIVATED ##")
    print("#" * 70)
    print("⚠️  Risk simulations are for ANALYSIS only.")
    print("⚠️  Do NOT use these values for live trading.")
    print("#" * 70 + "\n")

    # Import here to trigger phase lock
    try:
        from .simulator import RiskSimulator
    except RuntimeError as e:
        print(f"\n🚫 PHASE LOCK ERROR: {e}\n")
        sys.exit(1)

    # Run simulation
    simulator = RiskSimulator(capital=args.capital, default_risk_pct=args.risk_pct)

    if args.atr:
        snapshot = simulator.simulate_atr_risk(
            symbol=args.symbol,
            entry_price=args.entry,
            atr=args.atr,
            atr_multiplier=args.atr_mult,
        )
    elif args.stop:
        snapshot = simulator.simulate_fixed_risk(
            symbol=args.symbol,
            entry_price=args.entry,
            stop_price=args.stop,
        )
    else:
        print("\n🚫 ERROR: Must provide either --stop or --atr\n")
        sys.exit(1)

    simulator.print_snapshot(snapshot)


if __name__ == "__main__":
    main()
