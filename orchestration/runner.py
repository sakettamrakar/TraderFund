"""Scheduler - Runner"""
import argparse, logging, sys
from .engine import SchedulerEngine
from .workflows import get_daily_workflow, get_weekly_workflow

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)

def run_orchestration(mode: str = "daily", dry_run: bool = False):
    engine = SchedulerEngine()
    
    if mode == "daily":
        tasks = get_daily_workflow()
    elif mode == "weekly":
        tasks = get_weekly_workflow()
    else:
        logger.error(f"Unknown mode: {mode}")
        return

    # In dry run, we just print the plan
    if dry_run:
        logger.info(f"--- DRY RUN PLAN ({mode}) ---")
        for t in tasks:
            print(f"- {t.name}: {t.description} (Deps: {t.dependencies})")
        return

    # Load tasks into engine
    for t in tasks:
        engine.add_task(t)
        
    engine.run_flow(mode)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, default="daily", help="daily/weekly")
    parser.add_argument("--dry-run", action="store_true", help="Print plan only")
    args = parser.parse_args()
    
    run_orchestration(args.mode, args.dry_run)

if __name__ == "__main__":
    main()
