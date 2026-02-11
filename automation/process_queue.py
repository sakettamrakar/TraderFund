#!/usr/bin/env python3
"""
Process Queue
=============
Consumes tasks from automation/tasks/ and executes them using the TaskExecutor.
"""

import sys
import time
import logging
import json
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from automation.execution.executor import TaskExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

TASKS_DIR = PROJECT_ROOT / "automation" / "tasks"

def main():
    logger.info("Starting Process Queue...")

    if not TASKS_DIR.exists():
        logger.error(f"Tasks directory {TASKS_DIR} does not exist.")
        sys.exit(1)

    executor = TaskExecutor()

    try:
        while True:
            # Find NEW tasks
            tasks = list(TASKS_DIR.glob("task_*.json"))
            new_tasks = []

            for task_file in tasks:
                try:
                    with open(task_file, 'r') as f:
                        data = json.load(f)
                        if data.get("status") == "NEW":
                            new_tasks.append(task_file)
                except Exception as e:
                    logger.error(f"Error reading task {task_file}: {e}")

            if new_tasks:
                logger.info(f"Found {len(new_tasks)} new tasks.")
                for task_file in new_tasks:
                    executor.process_task(task_file)
            else:
                # logger.debug("No new tasks found.")
                pass

            time.sleep(2)

    except KeyboardInterrupt:
        logger.info("Stopping Process Queue.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
