
import argparse
import sys
import subprocess
import logging
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]

logger = logging.getLogger("SchedulerManager")
logging.basicConfig(level=logging.INFO)

DAILY_TASK_NAME = "US_Market_Daily_Research_Run"
WEEKLY_TASK_NAME = "US_Market_Weekly_Maintenance_Run"

WRAPPER_SCRIPT = PROJECT_ROOT / "infra_hardening" / "scheduler" / "wrapper.py"
PYTHON_EXE = sys.executable

def run_schtasks(args: list):
    """Run schtasks command safely."""
    try:
        cmd = ["schtasks"] + args
        logger.info(f"Executing: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            logger.info("Success.")
            return True
        else:
            logger.error(f"Failed: {result.stderr.strip()}")
            return False
    except Exception as e:
        logger.error(f"Exception: {e}")
        return False

def register_daily():
    """Register daily task at 09:00."""
    logger.info(f"Registering {DAILY_TASK_NAME}...")
    
    # Command: python wrapper.py --mode daily
    action = f'"{PYTHON_EXE}" "{WRAPPER_SCRIPT}" --mode daily'
    
    # /SC DAILY /TN Name /TR Action /ST 09:00 /F
    args = [
        "/Create", 
        "/SC", "DAILY", 
        "/TN", DAILY_TASK_NAME, 
        "/TR", action, 
        "/ST", "09:00", 
        "/F" # Force overwrite
    ]
    run_schtasks(args)

def register_weekly():
    """Register weekly task on Saturday at 09:00."""
    logger.info(f"Registering {WEEKLY_TASK_NAME}...")
    
    action = f'"{PYTHON_EXE}" "{WRAPPER_SCRIPT}" --mode weekly'
    
    # /SC WEEKLY /D SAT /TN Name /TR Action /ST 09:00 /F
    args = [
        "/Create", 
        "/SC", "WEEKLY", 
        "/D", "SAT",
        "/TN", WEEKLY_TASK_NAME, 
        "/TR", action, 
        "/ST", "09:00", 
        "/F"
    ]
    run_schtasks(args)

def register_test_run():
    """Register a one-time test task for 20:40 (8:40 PM)."""
    task_name = "US_Market_TEST_Run"
    logger.info(f"Registering TEST task {task_name} at 20:40...")
    
    action = f'"{PYTHON_EXE}" "{WRAPPER_SCRIPT}" --mode daily'
    
    # /SC ONCE /TN Name /TR Action /ST 20:40 /F
    args = [
        "/Create", 
        "/SC", "ONCE", 
        "/TN", task_name, 
        "/TR", action, 
        "/ST", "20:40", 
        "/F"
    ]
    run_schtasks(args)

def delete_task(task_name: str):
    logger.info(f"Deleting {task_name}...")
    run_schtasks(["/Delete", "/TN", task_name, "/F"])

def list_tasks():
    logger.info("Checking system tasks...")
    run_schtasks(["/Query", "/TN", DAILY_TASK_NAME])
    run_schtasks(["/Query", "/TN", WEEKLY_TASK_NAME])

def main():
    parser = argparse.ArgumentParser(description="Manage Windows Scheduled Tasks for TraderFund")
    parser.add_argument("--register", action="store_true", help="Register tasks")
    parser.add_argument("--delete", action="store_true", help="Delete tasks")
    parser.add_argument("--query", action="store_true", help="Check status")
    parser.add_argument("--test", action="store_true", help="Register one-time TEST run at 20:00")
    parser.add_argument("--daily", action="store_true", help="Apply to Daily task")
    parser.add_argument("--weekly", action="store_true", help="Apply to Weekly task")
    
    args = parser.parse_args()
    
    if args.delete:
        if args.daily: delete_task(DAILY_TASK_NAME)
        if args.weekly: delete_task(WEEKLY_TASK_NAME)
        if args.test: delete_task("US_Market_TEST_Run")
        if not args.daily and not args.weekly and not args.test:
            delete_task(DAILY_TASK_NAME)
            delete_task(WEEKLY_TASK_NAME)
            
    elif args.register:
        if args.daily: register_daily()
        if args.weekly: register_weekly()
        if not args.daily and not args.weekly:
            register_daily()
            register_weekly()
            
    elif args.test:
        register_test_run()
            
    elif args.query:
        list_tasks()
        run_schtasks(["/Query", "/TN", "US_Market_TEST_Run"])
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
