"""
US Universe Metadata Runner

CLI runner for metadata ingestion with batch processing and rate limiting.
Provides minimum required data for Stage 0 (Universe Hygiene) validation.
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import pandas as pd

from ingestion.api_ingestion.alpha_vantage import config
from ingestion.api_ingestion.alpha_vantage.metadata_ingestor import (
    MetadataIngestor,
    SymbolMetadata,
    save_metadata_to_parquet,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


def load_symbols(
    tiers: Optional[List[str]] = None,
    limit: Optional[int] = None,
    symbols: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Load symbols from master CSV.
    
    Args:
        tiers: Filter by priority tier (A, B, C)
        limit: Limit number of symbols
        symbols: Explicit list of symbols to fetch
        
    Returns:
        DataFrame with symbol metadata
    """
    path = config.SYMBOLS_CSV_PATH
    
    if not path.exists():
        raise FileNotFoundError(
            f"Symbol master not found at {path}. "
            f"Run 'python ingestion/api_ingestion/alpha_vantage/scheduler.py symbols' first."
        )
    
    df = pd.read_csv(path)
    logger.info(f"Loaded {len(df)} symbols from {path}")
    
    # Filter by explicit symbol list
    if symbols:
        df = df[df["symbol"].isin(symbols)]
        logger.info(f"Filtered to {len(df)} specified symbols")
    
    # Filter by tier
    if tiers and "priority_tier" in df.columns:
        df = df[df["priority_tier"].isin(tiers)]
        logger.info(f"Filtered to {len(df)} symbols in tiers {tiers}")
    
    # Apply limit
    if limit:
        df = df.head(limit)
        logger.info(f"Limited to {len(df)} symbols")
    
    return df


def run_metadata_ingestion(
    tiers: Optional[List[str]] = None,
    limit: Optional[int] = None,
    symbols: Optional[List[str]] = None,
    dry_run: bool = False,
    delay_seconds: float = 12.0,  # Respect rate limit: 5 calls/min
) -> dict:
    """
    Run metadata ingestion for specified symbols.
    
    Args:
        tiers: Filter by priority tier
        limit: Limit number of symbols
        symbols: Explicit list of symbols
        dry_run: If True, don't save output
        delay_seconds: Delay between API calls (rate limiting)
        
    Returns:
        Summary statistics
    """
    logger.info("=" * 60)
    logger.info("US UNIVERSE METADATA INGESTION - Starting")
    logger.info("=" * 60)
    
    # Load symbols
    symbols_df = load_symbols(tiers=tiers, limit=limit, symbols=symbols)
    total = len(symbols_df)
    
    if total == 0:
        logger.warning("No symbols to process")
        return {"total": 0, "success": 0, "failed": 0}
    
    # Initialize ingestor
    ingestor = MetadataIngestor()
    records: List[SymbolMetadata] = []
    success_count = 0
    failed_count = 0
    
    # Process each symbol with rate limiting
    for idx, row in symbols_df.iterrows():
        symbol = row["symbol"]
        exchange = row.get("exchange", "")
        asset_type = row.get("assetType", "Stock")
        
        logger.info(f"[{idx + 1}/{total}] Fetching {symbol}...")
        
        record = ingestor.fetch_symbol_metadata(
            symbol=symbol,
            exchange=exchange,
            asset_type=asset_type,
        )
        records.append(record)
        
        if record.last_close_price is not None:
            success_count += 1
            logger.info(f"  ✓ {symbol}: ${record.last_close_price:.2f}, vol={record.last_trade_volume}")
        else:
            failed_count += 1
            logger.warning(f"  ✗ {symbol}: {record.data_source}")
        
        # Rate limiting delay (skip on last symbol)
        if idx < total - 1:
            time.sleep(delay_seconds)
    
    # Save results
    if not dry_run:
        save_metadata_to_parquet(records)
    else:
        logger.info("DRY RUN: Skipping output file write")
    
    # Summary
    summary = {
        "total": total,
        "success": success_count,
        "failed": failed_count,
        "success_rate": success_count / total if total > 0 else 0,
    }
    
    logger.info("-" * 60)
    logger.info("INGESTION SUMMARY")
    logger.info("-" * 60)
    logger.info(f"Total Symbols:  {summary['total']}")
    logger.info(f"Success:        {summary['success']}")
    logger.info(f"Failed:         {summary['failed']}")
    logger.info(f"Success Rate:   {summary['success_rate']:.1%}")
    logger.info("=" * 60)
    logger.info("US UNIVERSE METADATA INGESTION - Complete")
    logger.info("=" * 60)
    
    return summary


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="US Universe Metadata Ingestion"
    )
    parser.add_argument(
        "--tier",
        type=str,
        help="Filter by tier (comma-separated, e.g., A,B)",
    )
    parser.add_argument(
        "--symbols",
        type=str,
        help="Explicit symbols (comma-separated, e.g., AAPL,MSFT)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of symbols to process",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=12.0,
        help="Delay between API calls in seconds (default: 12)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without saving output",
    )
    parser.add_argument(
        "--summary-json",
        action="store_true",
        help="Output summary as JSON",
    )
    
    args = parser.parse_args()
    
    # Parse filters
    tiers = args.tier.split(",") if args.tier else None
    symbols = args.symbols.split(",") if args.symbols else None
    
    # Run ingestion
    summary = run_metadata_ingestion(
        tiers=tiers,
        limit=args.limit,
        symbols=symbols,
        dry_run=args.dry_run,
        delay_seconds=args.delay,
    )
    
    if args.summary_json:
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
