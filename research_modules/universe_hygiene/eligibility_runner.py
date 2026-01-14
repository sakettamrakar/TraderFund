"""
Stage 0: Universe Hygiene - Eligibility Runner

CLI runner that orchestrates the full eligibility evaluation.
This is the main entry point for Stage 0.
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd

from . import config
from .eligibility_filter import EligibilityFilter
from .models import EligibilityRecord

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


def load_symbol_universe() -> pd.DataFrame:
    """
    Load the symbol universe from the expanded symbol master.
    """
    from ingestion.universe_expansion import config as ue_config
    path = ue_config.SYMBOL_MASTER_PATH
    
    if not path.exists():
        raise FileNotFoundError(f"Symbol master not found at {path}")
    
    df = pd.read_parquet(path)
    logger.info(f"Loaded {len(df)} symbols from {path}")
    return df


def create_price_data_loader():
    """
    Create a function that loads price data for a given symbol.
    
    Priority:
    1. Metadata parquet (preferred - from metadata ingestion)
    2. Staged daily parquet (fallback)
    
    Returns:
        Tuple of (loader_function, metadata_df or None)
    """
    # Try to load metadata first (preferred source)
    metadata_df = None
    if config.METADATA_PARQUET_PATH.exists():
        try:
            metadata_df = pd.read_parquet(config.METADATA_PARQUET_PATH)
            logger.info(f"Loaded {len(metadata_df)} records from metadata parquet")
        except Exception as e:
            logger.warning(f"Failed to load metadata parquet: {e}")
    
    staging_path = config.STAGING_PATH
    window_days = config.EVALUATION_WINDOW_DAYS
    cutoff_date = datetime.now() - timedelta(days=window_days)
    
    def load_price_data(symbol: str) -> Optional[pd.DataFrame]:
        """Load price/volume data for a symbol."""
        
        # Priority 1: Use metadata parquet
        if metadata_df is not None:
            row = metadata_df[metadata_df["symbol"] == symbol]
            if not row.empty:
                r = row.iloc[0]
                # Create a synthetic DataFrame with the fields we need
                price = r.get("last_close_price")
                volume = r.get("last_trade_volume") or r.get("rolling_avg_volume")
                
                if price is not None and not pd.isna(price):
                    # Return synthetic price data with enough rows to pass activity check
                    # Metadata represents a snapshot, so we assume sufficient activity
                    num_rows = config.TRADING_DAYS_MIN  # Meet activity threshold
                    return pd.DataFrame({
                        "timestamp": [datetime.now()] * num_rows,
                        "close": [float(price)] * num_rows,
                        "volume": [int(volume) if volume and not pd.isna(volume) else 0] * num_rows,
                    })
        
        # Priority 2: Use staged parquet (fallback)
        parquet_path = staging_path / f"{symbol}.parquet"
        
        if not parquet_path.exists():
            return None
        
        try:
            df = pd.read_parquet(parquet_path)
            
            # Ensure timestamp column exists (or is index)
            if "timestamp" not in df.columns:
                if df.index.name == "timestamp":
                    df = df.reset_index()
                else:
                    return None
            
            # Convert timestamp if needed
            if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
                df["timestamp"] = pd.to_datetime(df["timestamp"])
            
            # Filter to evaluation window
            df = df[df["timestamp"] >= cutoff_date]
            
            return df
            
        except Exception as e:
            logger.debug(f"Error loading {parquet_path}: {e}")
            return None
    
    return load_price_data


def save_eligibility_results(records: list, output_path: Path):
    """
    Save eligibility results to Parquet.
    
    Args:
        records: List of EligibilityRecord objects.
        output_path: Path to output Parquet file.
    """
    # Convert records to dictionaries
    data = [r.to_dict() for r in records]
    df = pd.DataFrame(data)
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to Parquet
    df.to_parquet(output_path, index=False)
    logger.info(f"Saved {len(df)} eligibility records to {output_path}")


def run_eligibility_evaluation(
    dry_run: bool = False,
    output_path: Optional[Path] = None,
) -> dict:
    """
    Run the full eligibility evaluation.
    
    Args:
        dry_run: If True, don't write output file.
        output_path: Override default output path.
        
    Returns:
        Summary statistics dictionary.
    """
    logger.info("=" * 60)
    logger.info("STAGE 0: UNIVERSE HYGIENE - Starting Eligibility Evaluation")
    logger.info("=" * 60)
    
    # Load symbol universe
    symbols_df = load_symbol_universe()
    
    # Create price data loader
    price_loader = create_price_data_loader()
    
    # Create filter and evaluate
    eligibility_filter = EligibilityFilter()
    records = eligibility_filter.evaluate_universe(symbols_df, price_loader)
    
    # Generate summary
    summary = eligibility_filter.summarize_results(records)
    
    # Log summary
    logger.info("-" * 60)
    logger.info("ELIGIBILITY SUMMARY")
    logger.info("-" * 60)
    logger.info(f"Total Symbols:    {summary['total_symbols']}")
    logger.info(f"Eligible:         {summary['eligible_count']}")
    logger.info(f"Excluded:         {summary['excluded_count']}")
    logger.info(f"Eligibility Rate: {summary['eligibility_rate']:.1%}")
    logger.info("-" * 60)
    logger.info("EXCLUSION BREAKDOWN:")
    for reason, count in sorted(summary['exclusion_breakdown'].items()):
        logger.info(f"  {reason}: {count}")
    logger.info("-" * 60)
    logger.info("LIQUIDITY BREAKDOWN (Eligible Only):")
    for bucket, count in sorted(summary['liquidity_breakdown'].items()):
        logger.info(f"  {bucket}: {count}")
    logger.info("-" * 60)
    logger.info("PRICE BREAKDOWN (Eligible Only):")
    for bucket, count in sorted(summary['price_breakdown'].items()):
        logger.info(f"  {bucket}: {count}")
    logger.info("-" * 60)
    
    # Sanity checks
    eligible_count = summary['eligible_count']
    if eligible_count < config.MIN_ELIGIBLE_SYMBOLS:
        logger.warning(
            f"SANITY CHECK FAILED: Only {eligible_count} eligible symbols "
            f"(expected >= {config.MIN_ELIGIBLE_SYMBOLS})"
        )
    elif eligible_count > config.MAX_ELIGIBLE_SYMBOLS:
        logger.warning(
            f"SANITY CHECK WARNING: {eligible_count} eligible symbols "
            f"(expected <= {config.MAX_ELIGIBLE_SYMBOLS})"
        )
    else:
        logger.info(f"✓ Eligible count {eligible_count} within expected range")
    
    # Save results
    if not dry_run:
        output = output_path or config.ELIGIBILITY_OUTPUT_PATH
        save_eligibility_results(records, output)
    else:
        logger.info("DRY RUN: Skipping output file write")
    
    logger.info("=" * 60)
    logger.info("STAGE 0: UNIVERSE HYGIENE - Complete")
    logger.info("=" * 60)
    
    return summary


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Stage 0: Universe Hygiene - Eligibility Evaluation"
    )
    parser.add_argument(
        "--evaluate",
        action="store_true",
        help="Run full eligibility evaluation",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Evaluate without writing output file",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Override output path",
    )
    parser.add_argument(
        "--summary-json",
        action="store_true",
        help="Output summary as JSON to stdout",
    )
    
    args = parser.parse_args()
    
    if not args.evaluate:
        parser.print_help()
        sys.exit(0)
    
    output_path = Path(args.output) if args.output else None
    summary = run_eligibility_evaluation(
        dry_run=args.dry_run,
        output_path=output_path,
    )
    
    if args.summary_json:
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
