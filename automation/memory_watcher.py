#!/usr/bin/env python3
"""
Memory Watcher
==============
Monitors docs/memory/ for changes and creates task files in automation/tasks/.
Tracks file modification times to detect changes.
"""

import os
import json
import time
import uuid
import datetime
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MEMORY_DIR = PROJECT_ROOT / "docs" / "memory"
TASKS_DIR = PROJECT_ROOT / "automation" / "tasks"
STATE_FILE = PROJECT_ROOT / "automation" / ".memory_watch_state.json"

def get_memory_state():
    """
    Scans the memory directory recursively and returns a dictionary of
    {relative_path: mtime}.
    """
    state = {}
    if not MEMORY_DIR.exists():
        logger.warning(f"{MEMORY_DIR} does not exist.")
        return state

    for root, _, files in os.walk(MEMORY_DIR):
        for file in files:
            file_path = Path(root) / file
            # Get relative path from project root
            try:
                rel_path = file_path.relative_to(PROJECT_ROOT)
                mtime = file_path.stat().st_mtime
                state[str(rel_path)] = mtime
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
    return state

def load_previous_state():
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load state file: {e}")
    return {}

def save_state(state):
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save state file: {e}")

def create_task(changed_files):
    task_id = str(uuid.uuid4())
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    task_data = {
        "task_id": task_id,
        "created_at": timestamp,
        "changed_memory_files": changed_files,
        "status": "NEW",
        "origin": "human",
        "phase": "PHASE_1"
    }

    task_file = TASKS_DIR / f"task_{task_id}.json"

    try:
        with open(task_file, 'w') as f:
            json.dump(task_data, f, indent=2)
        logger.info(f"Created task {task_id} for changes in {len(changed_files)} files.")
        return True
    except Exception as e:
        logger.error(f"Failed to create task file: {e}")
        return False

def main():
    logger.info("Starting Memory Watcher...")

    # Ensure tasks directory exists
    TASKS_DIR.mkdir(parents=True, exist_ok=True)

    # Initial load
    previous_state = load_previous_state()

    current_state = get_memory_state()

    if not previous_state:
        logger.info("No previous state found. Setting current state as baseline.")
        save_state(current_state)
        previous_state = current_state

    while True:
        try:
            current_state = get_memory_state()
            changed_files = []

            # Check for modified or new files
            for path, mtime in current_state.items():
                if path not in previous_state:
                    changed_files.append(path) # New file
                elif mtime != previous_state[path]:
                    changed_files.append(path) # Modified file

            # Check for deleted files
            for path in previous_state:
                if path not in current_state:
                    changed_files.append(path) # Deleted file

            if changed_files:
                logger.info(f"Detected changes: {changed_files}")
                if create_task(changed_files):
                    previous_state = current_state
                    save_state(previous_state)

            time.sleep(1)

        except KeyboardInterrupt:
            logger.info("Stopping Memory Watcher.")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
