"""
Stage 1: Structural Capability - Runner

CLI runner that orchestrates structural capability evaluation.
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import pandas as pd

from . import config
from .aggregator import StructuralAggregator
from .models import StructuralCapability

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


def load_eligible_symbols() -> List[str]:
    """Load eligible symbols from Stage 0 output."""
    path = config.ELIGIBILITY_PATH
    
    if not path.exists():
        logger.warning(f"Eligibility file not found: {path}")
        return []
    
    df = pd.read_parquet(path)
    eligible = df[df["eligibility_status"] == "eligible"]["symbol"].tolist()
    logger.info(f"Loaded {len(eligible)} eligible symbols")
    return eligible


def load_price_data(symbol: str) -> Optional[pd.DataFrame]:
    """Load staged price data for a symbol."""
    path = config.STAGING_PATH / f"{symbol}.parquet"
    
    if not path.exists():
        return None
    
    try:
        df = pd.read_parquet(path)
        df = df.reset_index()  # Ensure timestamp is a column
        
        # Rename if needed
        if "index" in df.columns:
            df.rename(columns={"index": "timestamp"}, inplace=True)
        
        return df
    except Exception as e:
        logger.warning(f"Error loading {symbol}: {e}")
        return None


def save_capability(cap: StructuralCapability, date_str: str):
    """Save capability result to parquet."""
    output_dir = config.OUTPUT_PATH / date_str
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / f"{cap.symbol}_capability.parquet"
    
    # Convert to DataFrame for parquet
    df = pd.DataFrame([cap.to_dict()])
    df.to_parquet(output_path, index=False)
    
    logger.debug(f"Saved {cap.symbol} to {output_path}")


def run_structural_evaluation(
    symbols: Optional[List[str]] = None,
    dry_run: bool = False,
) -> List[StructuralCapability]:
    """
    Run structural capability evaluation.
    
    Args:
        symbols: Explicit symbol list. If None, use eligible from Stage 0.
        dry_run: If True, don't save output files.
        
    Returns:
        List of StructuralCapability objects.
    """
    logger.info("=" * 60)
    logger.info("STAGE 1: STRUCTURAL CAPABILITY - Starting Evaluation")
    logger.info("=" * 60)
    
    # Get symbols to evaluate
    if symbols:
        symbol_list = symbols
        logger.info(f"Using explicit symbol list: {symbol_list}")
    else:
        symbol_list = load_eligible_symbols()
    
    if not symbol_list:
        logger.error("No symbols to evaluate")
        return []
    
    # Initialize aggregator
    aggregator = StructuralAggregator()
    results: List[StructuralCapability] = []
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    
    # Evaluate each symbol
    for idx, symbol in enumerate(symbol_list):
        logger.info(f"[{idx + 1}/{len(symbol_list)}] Evaluating {symbol}...")
        
        df = load_price_data(symbol)
        if df is None:
            logger.warning(f"  No price data for {symbol}")
            continue
        
        # Run evaluation
        capability = aggregator.evaluate_symbol(symbol, df)
        results.append(capability)
        
        # Log result
        logger.info(
            f"  → Score: {capability.structural_capability_score:.1f} "
            f"({capability.confidence_level})"
        )
        
        # Save if not dry run
        if not dry_run:
            save_capability(capability, date_str)
    
    # Summary
    logger.info("-" * 60)
    logger.info("EVALUATION SUMMARY")
    logger.info("-" * 60)
    
    for cap in results:
        logger.info(
            f"  {cap.symbol}: {cap.structural_capability_score:.1f} "
            f"[{cap.confidence_level}]"
        )
        for behavior, score in cap.behavior_breakdown.items():
            logger.info(f"    - {behavior}: {score:.1f}")
    
    logger.info("-" * 60)
    logger.info(f"Evaluated: {len(results)} symbols")
    logger.info("=" * 60)
    logger.info("STAGE 1: STRUCTURAL CAPABILITY - Complete")
    logger.info("=" * 60)
    
    return results


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Stage 1: Structural Capability Evaluation"
    )
    parser.add_argument(
        "--evaluate",
        action="store_true",
        help="Run structural capability evaluation",
    )
    parser.add_argument(
        "--symbols",
        type=str,
        help="Explicit symbols (comma-separated)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Evaluate without saving output",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    
    args = parser.parse_args()
    
    if not args.evaluate:
        parser.print_help()
        sys.exit(0)
    
    symbols = args.symbols.split(",") if args.symbols else None
    results = run_structural_evaluation(
        symbols=symbols,
        dry_run=args.dry_run,
    )
    
    if args.json:
        output = [r.to_dict() for r in results]
        print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
