"""Incremental Update - Runner"""
import argparse, logging, sys
from . import config
from .updater import IncrementalUpdater

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)

def run_incremental_update(budget: int = None, dry_run: bool = False):
    logger.info("=" * 60)
    logger.info("INCREMENTAL DAILY UPDATE - Starting")
    logger.info("=" * 60)
    
    budget = budget or config.DAILY_BUDGET
    updater = IncrementalUpdater()
    
    eligible = updater.get_eligible_symbols(limit=budget)
    
    if not eligible:
        logger.info("No eligible symbols for update")
        return {"status": "NO_OP", "reason": "no eligible symbols"}
    
    logger.info(f"Processing {len(eligible)} symbols (budget: {budget})")
    
    stats = {"success": 0, "up_to_date": 0, "failed": 0}
    
    for i, symbol in enumerate(eligible):
        logger.info(f"[{i+1}/{len(eligible)}] Updating {symbol}...")
        
        if dry_run:
            last = updater.get_last_stored_date(symbol)
            logger.info(f"  → DRY RUN: Last stored = {last}")
            continue
        
        status = updater.update_symbol(symbol)
        stats[status.status] = stats.get(status.status, 0) + 1
        
        if status.status == "success":
            logger.info(f"  → SUCCESS")
        elif status.status == "up_to_date":
            logger.info(f"  → UP TO DATE")
        else:
            logger.warning(f"  → FAILED: {status.error_reason}")
        
        if i < len(eligible) - 1:
            updater.wait_rate_limit()
    
    logger.info("=" * 60)
    logger.info("=" * 60)
    logger.info(f"UPDATE SUMMARY: {stats}")
    logger.info("=" * 60)
    
    if stats["success"] == 0:
        return {"status": "NO_OP", "reason": "all symbols up to date"}
    return {"status": "SUCCESS"}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--update", action="store_true")
    parser.add_argument("--budget", type=int, default=50)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    
    if not args.update:
        parser.print_help()
        sys.exit(0)
    
    run_incremental_update(args.budget, args.dry_run)

if __name__ == "__main__":
    main()
