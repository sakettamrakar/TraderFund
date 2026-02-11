#!/usr/bin/env python3
"""
List Tasks
==========
Lists pending tasks in automation/tasks/.
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = PROJECT_ROOT / "automation" / "tasks"

def list_tasks():
    if not TASKS_DIR.exists():
        print("No tasks directory found.")
        return

    task_files = list(TASKS_DIR.glob("task_*.json"))

    if not task_files:
        print("No tasks found.")
        return

    tasks = []
    for tf in task_files:
        try:
            with open(tf, 'r') as f:
                task = json.load(f)
                tasks.append(task)
        except Exception as e:
            print(f"Error reading {tf}: {e}")

    # Sort by created_at descending
    tasks.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    print(f"{'TASK ID':<38} | {'CREATED AT':<25} | {'STATUS':<10} | {'FILES'}")
    print("-" * 100)
    for t in tasks:
        files = ", ".join(t.get("changed_memory_files", []))
        if len(files) > 50:
            files = files[:47] + "..."

        print(f"{t.get('task_id'):<38} | {t.get('created_at'):<25} | {t.get('status'):<10} | {files}")

if __name__ == "__main__":
    list_tasks()
