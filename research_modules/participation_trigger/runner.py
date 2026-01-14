"""Stage 3: Participation Trigger - Runner"""
import argparse, json, logging, sys
from datetime import datetime
from typing import List, Optional
import pandas as pd
from . import config
from .aggregator import ParticipationAggregator
from .models import ParticipationTrigger

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)

def load_energy_score(symbol: str, date_str: str) -> Optional[float]:
    path = config.ENERGY_PATH / date_str / f"{symbol}_energy.parquet"
    if not path.exists():
        return None
    try:
        df = pd.read_parquet(path)
        return float(df["energy_setup_score"].iloc[0]) if "energy_setup_score" in df.columns else None
    except:
        return None

def load_price_data(symbol: str) -> Optional[pd.DataFrame]:
    path = config.STAGING_PATH / f"{symbol}.parquet"
    if not path.exists():
        return None
    try:
        return pd.read_parquet(path).reset_index()
    except:
        return None

def save_result(result: ParticipationTrigger, date_str: str):
    out_dir = config.OUTPUT_PATH / date_str
    out_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([result.to_dict()]).to_parquet(out_dir / f"{result.symbol}_trigger.parquet", index=False)

def run_participation_evaluation(symbols: Optional[List[str]] = None, dry_run: bool = False) -> List[ParticipationTrigger]:
    logger.info("=" * 60)
    logger.info("STAGE 3: PARTICIPATION TRIGGER - Starting")
    logger.info("=" * 60)
    
    if not symbols:
        from research_modules.universe_hygiene import config as uh
        if uh.ELIGIBILITY_OUTPUT_PATH.exists():
            df = pd.read_parquet(uh.ELIGIBILITY_OUTPUT_PATH)
            symbols = df[df["eligibility_status"] == "eligible"]["symbol"].tolist()
    
    if not symbols:
        logger.error("No symbols")
        return []
    
    aggregator = ParticipationAggregator()
    results = []
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    
    for i, sym in enumerate(symbols):
        logger.info(f"[{i+1}/{len(symbols)}] {sym}...")
        df = load_price_data(sym)
        if df is None:
            continue
        energy = load_energy_score(sym, date_str)
        result = aggregator.evaluate_symbol(sym, df, energy)
        results.append(result)
        logger.info(f"  → {result.participation_score:.1f} ({result.trigger_state})")
        if not dry_run:
            save_result(result, date_str)
    
    logger.info("=" * 60)
    for r in results:
        logger.info(f"  {r.symbol}: {r.participation_score:.1f} [{r.trigger_state}]")
    logger.info("STAGE 3: Complete")
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--evaluate", action="store_true")
    parser.add_argument("--symbols", type=str)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    
    if not args.evaluate:
        parser.print_help()
        sys.exit(0)
    
    symbols = args.symbols.split(",") if args.symbols else None
    results = run_participation_evaluation(symbols, args.dry_run)
    if args.json:
        print(json.dumps([r.to_dict() for r in results], indent=2))

if __name__ == "__main__":
    main()
