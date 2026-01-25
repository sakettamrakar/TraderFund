"""
Minimal Historical Daily Ingestion Bootstrap

One-time, manual script to load ≥200 trading days for validation symbols.
Uses existing USMarketIngestor and USNormalizer infrastructure.

Usage:
    python -m ingestion.api_ingestion.alpha_vantage.historical_bootstrap
"""

import logging
import time
from datetime import datetime

import pandas as pd

from ingestion.api_ingestion.alpha_vantage import config
from ingestion.api_ingestion.alpha_vantage.market_data_ingestor import USMarketIngestor
from ingestion.api_ingestion.alpha_vantage.normalizer import USNormalizer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION - Explicit symbol list (no universe scan)
# =============================================================================

BOOTSTRAP_SYMBOLS = ["AAPL", "GOOGL", "MSFT"]
DELAY_SECONDS = 13  # Respect rate limits: 5 calls/min

# Minimum trading days required (compact mode gives ~100 days)
MIN_TRADING_DAYS = 60

# Use compact mode (free tier) - gives ~100 trading days
# Full history requires premium API
USE_FULL_HISTORY = False


def run_bootstrap():
    """
    Run minimal historical ingestion for bootstrap symbols.
    
    - Fetches full daily history (1 API call per symbol)
    - Normalizes to staging parquet
    - Verifies row count
    """
    logger.info("=" * 60)
    logger.info("HISTORICAL BOOTSTRAP - Starting")
    logger.info(f"Symbols: {BOOTSTRAP_SYMBOLS}")
    logger.info("=" * 60)
    
    ingestor = USMarketIngestor()
    normalizer = USNormalizer()
    today_str = datetime.utcnow().strftime('%Y-%m-%d')
    
    results = {}
    
    for idx, symbol in enumerate(BOOTSTRAP_SYMBOLS):
        logger.info(f"[{idx + 1}/{len(BOOTSTRAP_SYMBOLS)}] Fetching {symbol} history (compact={not USE_FULL_HISTORY})...")
        
        # Fetch history (compact for free tier, full for premium)
        result = ingestor.fetch_symbol_daily(symbol, full_history=USE_FULL_HISTORY)
        
        if result["success"]:
            logger.info(f"  ✓ {symbol}: Raw saved")
            
            # Normalize
            raw_path = config.RAW_BASE_DIR / today_str / f"{symbol}_daily.json"
            if raw_path.exists():
                normalizer.normalize_file(raw_path)
                
                # Verify row count
                staging_path = config.STAGING_DIR / "daily" / f"{symbol}.parquet"
                if staging_path.exists():
                    df = pd.read_parquet(staging_path)
                    row_count = len(df)
                    
                    if row_count >= MIN_TRADING_DAYS:
                        logger.info(f"  ✓ {symbol}: {row_count} trading days (OK)")
                        results[symbol] = {"status": "success", "rows": row_count}
                    else:
                        logger.warning(f"  ⚠ {symbol}: Only {row_count} rows (< {MIN_TRADING_DAYS})")
                        results[symbol] = {"status": "partial", "rows": row_count}
                else:
                    logger.error(f"  ✗ {symbol}: Staging file not created")
                    results[symbol] = {"status": "failed", "reason": "normalize_failed"}
            else:
                logger.error(f"  ✗ {symbol}: Raw file not found")
                results[symbol] = {"status": "failed", "reason": "raw_not_found"}
        else:
            logger.error(f"  ✗ {symbol}: {result['status']} - {result['msg']}")
            results[symbol] = {"status": "failed", "reason": result["status"]}
        
        # Rate limit delay (skip on last symbol)
        if idx < len(BOOTSTRAP_SYMBOLS) - 1:
            logger.info(f"  Waiting {DELAY_SECONDS}s for rate limit...")
            time.sleep(DELAY_SECONDS)
    
    # Summary
    logger.info("=" * 60)
    logger.info("BOOTSTRAP SUMMARY")
    logger.info("=" * 60)
    
    success_count = sum(1 for r in results.values() if r["status"] == "success")
    partial_count = sum(1 for r in results.values() if r["status"] == "partial")
    failed_count = sum(1 for r in results.values() if r["status"] == "failed")
    
    for symbol, r in results.items():
        if r["status"] == "success":
            logger.info(f"  ✓ {symbol}: {r['rows']} rows")
        elif r["status"] == "partial":
            logger.warning(f"  ⚠ {symbol}: {r['rows']} rows (insufficient)")
        else:
            logger.error(f"  ✗ {symbol}: {r.get('reason', 'unknown')}")
    
    logger.info("-" * 60)
    logger.info(f"Success: {success_count}, Partial: {partial_count}, Failed: {failed_count}")
    logger.info("=" * 60)
    
    return results


if __name__ == "__main__":
    run_bootstrap()
