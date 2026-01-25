"""Universe Expansion - Runner"""
import argparse, json, logging, sys
from typing import List
from . import config
from .expander import UniverseExpander
from .models import SymbolMaster

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)

def run_universe_expansion(dry_run: bool = False) -> List[SymbolMaster]:
    logger.info("=" * 60)
    logger.info("SYMBOL UNIVERSE EXPANSION - Starting")
    logger.info("=" * 60)
    
    expander = UniverseExpander()
    
    if dry_run:
        # Just show what would be filtered
        df = expander.load_source_symbols()
        df = expander.filter_symbols(df)
        records = expander.create_master_records(df)
        logger.info(f"DRY RUN: Would create {len(records)} symbols")
        return records
    
    records = expander.expand()
    
    # Summary
    logger.info("=" * 60)
    logger.info("EXPANSION SUMMARY")
    logger.info("-" * 60)
    
    # Count by exchange
    exchanges = {}
    types = {}
    hints = {}
    
    for r in records:
        exchanges[r.exchange] = exchanges.get(r.exchange, 0) + 1
        types[r.instrument_type] = types.get(r.instrument_type, 0) + 1
        hints[r.eligibility_hint] = hints.get(r.eligibility_hint, 0) + 1
    
    logger.info(f"Total Symbols: {len(records)}")
    logger.info(f"By Exchange: {exchanges}")
    logger.info(f"By Type: {types}")
    logger.info(f"By Hint: {hints}")
    logger.info("=" * 60)
    
    return records

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--expand", action="store_true", help="Run expansion")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    if not args.expand:
        parser.print_help()
        sys.exit(0)
    
    records = run_universe_expansion(args.dry_run)
    if args.json:
        print(json.dumps([r.to_dict() for r in records[:10]], indent=2))  # First 10

if __name__ == "__main__":
    main()
