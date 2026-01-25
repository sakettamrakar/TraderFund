"""Historical Backfill - Runner"""
import argparse, logging, sys
from . import config
from .queue import BackfillQueue
from .fetcher import HistoricalFetcher

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)

def run_backfill(budget: int = None, dry_run: bool = False):
    logger.info("=" * 60)
    logger.info("HISTORICAL DAILY BACKFILL - Starting")
    logger.info("=" * 60)
    
    budget = budget or config.DAILY_BUDGET
    queue = BackfillQueue()
    fetcher = HistoricalFetcher()
    
    pending = queue.get_pending_symbols(limit=budget)
    
    if not pending:
        logger.info("No pending symbols to backfill")
        return
    
    logger.info(f"Processing {len(pending)} symbols (budget: {budget})")
    
    success_count = 0
    fail_count = 0
    
    for i, symbol in enumerate(pending):
        logger.info(f"[{i+1}/{len(pending)}] Backfilling {symbol}...")
        
        if dry_run:
            logger.info(f"  → DRY RUN: Would fetch {symbol}")
            continue
        
        success, depth, info = fetcher.fetch_symbol(symbol)
        
        if success:
            # Parse dates from info
            parts = info.split(" to ")
            start_date = parts[0] if len(parts) == 2 else None
            end_date = parts[1] if len(parts) == 2 else None
            
            queue.mark_success(symbol, depth, start_date, end_date)
            logger.info(f"  → SUCCESS: {depth} days ({info})")
            success_count += 1
        else:
            queue.mark_failed(symbol, info)
            logger.warning(f"  → FAILED: {info}")
            fail_count += 1
        
        # Rate limit (except last)
        if i < len(pending) - 1:
            fetcher.wait_rate_limit()
    
    # Summary
    logger.info("=" * 60)
    logger.info("BACKFILL SUMMARY")
    logger.info(f"  Success: {success_count}")
    logger.info(f"  Failed: {fail_count}")
    stats = queue.get_stats()
    logger.info(f"  Total Tracked: {stats}")
    logger.info("=" * 60)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--backfill", action="store_true", help="Run backfill")
    parser.add_argument("--budget", type=int, default=25, help="Max symbols")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument("--status", action="store_true", help="Show queue status")
    args = parser.parse_args()
    
    if args.status:
        queue = BackfillQueue()
        print(queue.get_stats())
        sys.exit(0)
    
    if not args.backfill:
        parser.print_help()
        sys.exit(0)
    
    run_backfill(args.budget, args.dry_run)

if __name__ == "__main__":
    main()
