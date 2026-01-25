"""Narrative Diff - Runner"""
import argparse, json, logging, sys
from datetime import datetime, timedelta
from typing import List, Optional
import pandas as pd
from . import config
from .models import NarrativeDiff
from .detector import DiffDetector

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)

def load_narrative(symbol: str, date_str: str) -> Optional[dict]:
    path = config.NARRATIVE_PATH / date_str / f"{symbol}_narrative.parquet"
    if not path.exists():
        return None
    try:
        df = pd.read_parquet(path)
        return df.iloc[0].to_dict()
    except:
        return None

def load_previous_narrative(symbol: str, current_date_str: str) -> Optional[dict]:
    """Load previous day's narrative."""
    current = datetime.strptime(current_date_str, "%Y-%m-%d")
    for days_back in range(1, 8):  # Look back up to 7 days
        prev_date = (current - timedelta(days=days_back)).strftime("%Y-%m-%d")
        narrative = load_narrative(symbol, prev_date)
        if narrative:
            return narrative
    return None

def save_diff(diff: NarrativeDiff, date_str: str):
    out_dir = config.DIFF_PATH / date_str
    out_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([diff.to_dict()]).to_parquet(out_dir / f"{diff.symbol}_diff.parquet", index=False)

def run_diff_detection(symbols: Optional[List[str]] = None, 
                       dry_run: bool = False) -> List[NarrativeDiff]:
    logger.info("=" * 60)
    logger.info("NARRATIVE DIFF LAYER - Starting")
    logger.info("=" * 60)
    
    if not symbols:
        from research_modules.universe_hygiene import config as uh
        if uh.ELIGIBILITY_OUTPUT_PATH.exists():
            df = pd.read_parquet(uh.ELIGIBILITY_OUTPUT_PATH)
            symbols = df[df["eligibility_status"] == "eligible"]["symbol"].tolist()
    
    if not symbols:
        logger.error("No symbols")
        return []
    
    detector = DiffDetector()
    results = []
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    
    for i, sym in enumerate(symbols):
        logger.info(f"[{i+1}/{len(symbols)}] {sym}...")
        
        current = load_narrative(sym, date_str)
        if not current:
            logger.warning(f"  No current narrative for {sym}")
            continue
        
        previous = load_previous_narrative(sym, date_str)
        diff = detector.detect(current, previous)
        results.append(diff)
        
        if diff.change_detected:
            logger.info(f"  → CHANGE: {diff.change_type} - {diff.change_summary}")
        else:
            logger.info(f"  → No change")
        
        if not dry_run:
            save_diff(diff, date_str)
    
    logger.info("=" * 60)
    changes = [r for r in results if r.change_detected]
    logger.info(f"Changes detected: {len(changes)}/{len(results)}")
    for c in changes:
        logger.info(f"  {c.symbol}: {c.change_type} - {c.change_summary}")
    logger.info("=" * 60)
    
    if not changes:
         return {"status": "NO_OP", "reason": "no narrative diffs detected"}
    return {"status": "SUCCESS"}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--detect", action="store_true")
    parser.add_argument("--symbols", type=str)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    
    if not args.detect:
        parser.print_help()
        sys.exit(0)
    
    symbols = args.symbols.split(",") if args.symbols else None
    results = run_diff_detection(symbols, args.dry_run)
    if args.json:
        print(json.dumps([r.to_dict() for r in results], indent=2))

if __name__ == "__main__":
    main()
