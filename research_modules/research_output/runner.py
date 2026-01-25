"""Research Output - Runner"""
import argparse, logging, sys
from datetime import datetime
from typing import List, Optional
from pathlib import Path
from . import config
from .generator import ReportGenerator

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)

def run_research_output(report_type: str = "daily", 
                        symbols: Optional[List[str]] = None, 
                        dry_run: bool = False):
    logger.info("=" * 60)
    logger.info(f"RESEARCH OUTPUT GENERATOR ({report_type.upper()}) - Starting")
    logger.info("=" * 60)
    
    if not symbols:
        # Load from eligibility or diffs
        # For reporting, we usually want to look at everything we tracked
        from research_modules.universe_hygiene import config as uh
        if uh.ELIGIBILITY_OUTPUT_PATH.exists():
            import pandas as pd
            df = pd.read_parquet(uh.ELIGIBILITY_OUTPUT_PATH)
            # Filter for eligible only? Or all we have data for?
            # Let's start with eligible
            symbols = df[df["eligibility_status"] == "eligible"]["symbol"].tolist()
    
    if not symbols:
        logger.error("No symbols found.")
        return

    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    generator = ReportGenerator()
    
    if report_type == "daily":
        report = generator.generate_daily_brief(date_str, symbols)
        text_output = generator.format_text_report(report)
        
        logger.info("\n" + text_output)
        
        if not dry_run:
            out_dir = config.OUTPUT_PATH / date_str
            out_dir.mkdir(parents=True, exist_ok=True)
            path = out_dir / f"daily_brief_{date_str}.txt"
            with open(path, "w", encoding="utf-8") as f:
                f.write(text_output)
            logger.info(f"Saved report to {path}")
            
        if not report.key_changes:
            logger.info("No key changes detected - Returning NO_OP")
            return {"status": "NO_OP", "reason": "no narrative changes detected"}
        return {"status": "SUCCESS"}
            
    # Weekly logic would go here
    
    logger.info("=" * 60)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate", action="store_true")
    parser.add_argument("--type", type=str, default="daily", help="daily/weekly")
    parser.add_argument("--symbols", type=str)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    
    if not args.generate:
        parser.print_help()
        sys.exit(0)
    
    symbols = args.symbols.split(",") if args.symbols else None
    run_research_output(args.type, symbols, args.dry_run)

if __name__ == "__main__":
    main()
