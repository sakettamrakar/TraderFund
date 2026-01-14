
import sys
import logging
import argparse
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from infra_hardening.control.switches import SystemSwitches
from orchestration.runner import run_orchestration

def setup_logging(mode: str) -> Path:
    log_dir = PROJECT_ROOT / "logs" / "scheduler"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = log_dir / f"{mode}_{timestamp}.log"
    
    # Configure root logger to capture ALL events
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Clear existing handlers to avoid duplication/conflicts
    if root_logger.handlers:
        root_logger.handlers.clear()
    
    # File Handler
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"))
    root_logger.addHandler(file_handler)
    
    # Stream Handler (Console)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"))
    root_logger.addHandler(console_handler)
    
    return log_file

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, required=True, choices=["daily", "weekly"])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    
    log_file = setup_logging(args.mode)
    logger = logging.getLogger("SchedulerWrapper")
    
    logger.info("="*60)
    logger.info(f"SCHEDULER WRAPPER: Starting {args.mode} run {'(DRY RUN)' if args.dry_run else ''}")
    logger.info(f"Log file: {log_file}")
    logger.info("="*60)
    
    # Check Kill Switch
    if SystemSwitches.READ_ONLY_MODE and not args.dry_run:
        logger.critical("KILL SWITCH ACTIVE: READ_ONLY_MODE is True. Aborting scheduled run.")
        sys.exit(1)
        
    try:
        run_orchestration(mode=args.mode, dry_run=args.dry_run)
        logger.info("Wrappper execution finished successfully.")
    except Exception as e:
        logger.exception(f"CRITICAL FAILURE in scheduled run: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
