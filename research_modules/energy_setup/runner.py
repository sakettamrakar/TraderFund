"""
Stage 2: Energy Setup - Runner

CLI runner for energy setup evaluation.
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
from .aggregator import EnergyAggregator
from .models import EnergySetup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


def load_structural_score(symbol: str, date_str: str) -> Optional[float]:
    """Load structural capability score from Stage 1."""
    path = config.STRUCTURAL_PATH / date_str / f"{symbol}_capability.parquet"
    
    if not path.exists():
        return None
    
    try:
        df = pd.read_parquet(path)
        if "structural_capability_score" in df.columns:
            return float(df["structural_capability_score"].iloc[0])
    except Exception as e:
        logger.debug(f"Error loading structural score for {symbol}: {e}")
    
    return None


def load_price_data(symbol: str) -> Optional[pd.DataFrame]:
    """Load staged price data."""
    path = config.STAGING_PATH / f"{symbol}.parquet"
    
    if not path.exists():
        return None
    
    try:
        df = pd.read_parquet(path).reset_index()
        if "index" in df.columns:
            df.rename(columns={"index": "timestamp"}, inplace=True)
        return df
    except Exception as e:
        logger.warning(f"Error loading {symbol}: {e}")
        return None


def save_energy_result(result: EnergySetup, date_str: str):
    """Save energy result to parquet."""
    output_dir = config.OUTPUT_PATH / date_str
    output_dir.mkdir(parents=True, exist_ok=True)
    
    path = output_dir / f"{result.symbol}_energy.parquet"
    df = pd.DataFrame([result.to_dict()])
    df.to_parquet(path, index=False)


def run_energy_evaluation(
    symbols: Optional[List[str]] = None,
    dry_run: bool = False,
) -> List[EnergySetup]:
    """Run energy setup evaluation."""
    logger.info("=" * 60)
    logger.info("STAGE 2: ENERGY SETUP - Starting Evaluation")
    logger.info("=" * 60)
    
    # Get symbols from Stage 0 eligibility if not specified
    if not symbols:
        from research_modules.universe_hygiene import config as uh_config
        if uh_config.ELIGIBILITY_OUTPUT_PATH.exists():
            df = pd.read_parquet(uh_config.ELIGIBILITY_OUTPUT_PATH)
            symbols = df[df["eligibility_status"] == "eligible"]["symbol"].tolist()
    
    if not symbols:
        logger.error("No symbols to evaluate")
        return []
    
    logger.info(f"Evaluating {len(symbols)} symbols")
    
    aggregator = EnergyAggregator()
    results: List[EnergySetup] = []
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    
    for idx, symbol in enumerate(symbols):
        logger.info(f"[{idx + 1}/{len(symbols)}] Evaluating {symbol}...")
        
        df = load_price_data(symbol)
        if df is None:
            logger.warning(f"  No price data for {symbol}")
            continue
        
        structural_score = load_structural_score(symbol, date_str)
        
        result = aggregator.evaluate_symbol(symbol, df, structural_score)
        results.append(result)
        
        logger.info(f"  → Score: {result.energy_setup_score:.1f} ({result.energy_state})")
        
        if not dry_run:
            save_energy_result(result, date_str)
    
    # Summary
    logger.info("-" * 60)
    logger.info("ENERGY SUMMARY")
    logger.info("-" * 60)
    
    for r in results:
        logger.info(f"  {r.symbol}: {r.energy_setup_score:.1f} [{r.energy_state}]")
        for behavior, score in r.behavior_breakdown.items():
            logger.info(f"    - {behavior}: {score:.1f}")
    
    logger.info("=" * 60)
    logger.info("STAGE 2: ENERGY SETUP - Complete")
    logger.info("=" * 60)
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Stage 2: Energy Setup Evaluation")
    parser.add_argument("--evaluate", action="store_true", help="Run evaluation")
    parser.add_argument("--symbols", type=str, help="Comma-separated symbols")
    parser.add_argument("--dry-run", action="store_true", help="No output files")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    if not args.evaluate:
        parser.print_help()
        sys.exit(0)
    
    symbols = args.symbols.split(",") if args.symbols else None
    results = run_energy_evaluation(symbols=symbols, dry_run=args.dry_run)
    
    if args.json:
        print(json.dumps([r.to_dict() for r in results], indent=2))


if __name__ == "__main__":
    main()
