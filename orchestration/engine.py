"""Scheduler - Engine (DAG execution)"""
import logging
import importlib
import time
from datetime import datetime
from typing import Dict, List
import pandas as pd
from . import config
from .models import Task, TaskStatus

logger = logging.getLogger(__name__)

class SchedulerEngine:
    """Lightweight Python DAG scheduler."""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self._load_state()
        
    def add_task(self, task: Task):
        # Restore persistent state
        if task.name in self.state_cache:
            saved = self.state_cache[task.name]
            task.consecutive_failures = saved.get("failures", 0)
            # Restore last success time if needed
        self.tasks[task.name] = task
        
    def _load_state(self):
        self.state_cache = {}
        if config.STATE_PATH.exists():
            try:
                df = pd.read_parquet(config.STATE_PATH)
                # Convert to dict for quick access: {task_name: {"failures": int}}
                for _, row in df.iterrows():
                    self.state_cache[row["task_name"]] = {"failures": row["consecutive_failures"]}
            except Exception as e:
                logger.error(f"Failed to load state: {e}")

    def _save_state(self):
        data = []
        for t in self.tasks.values():
            data.append({
                "task_name": t.name, 
                "consecutive_failures": t.consecutive_failures,
                "last_updated": datetime.utcnow()
            })
        if data:
            try:
                df = pd.DataFrame(data)
                config.STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
                df.to_parquet(config.STATE_PATH)
            except Exception as e:
                logger.error(f"Failed to save state: {e}")

    def _record_heartbeat(self, flow_name: str, status: str, start_time: datetime, end_time: datetime):
        """Append run record to history."""
        record = {
            "run_id": f"{flow_name}_{start_time.strftime('%Y%m%d_%H%M%S')}",
            "flow_name": flow_name,
            "status": status,
            "start_time": start_time,
            "end_time": end_time,
            "duration_sec": (end_time - start_time).total_seconds()
        }
        try:
            df = pd.DataFrame([record])
            config.RUN_HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
            if config.RUN_HISTORY_PATH.exists() and config.RUN_HISTORY_PATH.stat().st_size > 0:
                try:
                    existing = pd.read_parquet(config.RUN_HISTORY_PATH)
                    df = pd.concat([existing, df])
                except Exception as e:
                    logger.warning(f"Could not read existing history: {e}. Starting fresh.")
            df.to_parquet(config.RUN_HISTORY_PATH)
        except Exception as e:
            logger.error(f"Failed to record heartbeat: {e}")

    def _run_task(self, task: Task) -> bool:
        """Execute a single task dynamically."""
        logger.info(f"--- STARTING TASK: {task.name} ---")
        
        # Soft Failure Demotion check
        if task.consecutive_failures >= 3:
            logger.warning(f"Task {task.name} disabled due to 3 consecutive failures. Skipping.")
            task.status = TaskStatus.SKIPPED
            task.error = "Soft failure threshold exceeded"
            return True # Treat as "handled" so flow continues? Or False?
            # User said "Resume next day" implies we skip today but don't crash flow.
            # So return True (soft skip).

        task.start_time = datetime.utcnow()
        task.status = TaskStatus.RUNNING
        
        # Check dependencies
        for dep_name in task.dependencies:
            dep = self.tasks.get(dep_name)
            if not dep or dep.status not in [TaskStatus.SUCCESS, TaskStatus.NO_OP]: 
                # NO_OP is also a success
                logger.warning(f"Skipping {task.name} because dependency {dep_name} failed/skipped.")
                task.status = TaskStatus.SKIPPED
                task.end_time = datetime.utcnow()
                return False

        try:
            # Dynamic import
            module = importlib.import_module(task.module_path)
            func = getattr(module, task.function_name)
            
            # Execute
            result = func(**task.kwargs)
            
            # Handle return status
            if isinstance(result, dict) and result.get("status") == "NO_OP":
                task.status = TaskStatus.NO_OP
                logger.info(f"Task {task.name}: NO_OP ({result.get('reason', 'No action needed')})")
            else:
                task.status = TaskStatus.SUCCESS
                logger.info(f"--- COMPLETED TASK: {task.name} ---")
            
            # Reset failure count on success/no-op
            task.consecutive_failures = 0
            
        except Exception as e:
            logger.error(f"Task {task.name} failed: {e}")
            task.error = str(e)
            task.status = TaskStatus.FAILED
            task.consecutive_failures += 1
            
        task.end_time = datetime.utcnow()
        return task.status in [TaskStatus.SUCCESS, TaskStatus.NO_OP]

    def run_flow(self, flow_name: str) -> bool:
        """Run all tasks in defined order."""
        if config.ENABLE_KILL_SWITCH:
            logger.critical("KILL SWITCH ACTIVE - Orchestration aborted.")
            return False
            
        logger.info(f"Starting Flow: {flow_name}")
        flow_start = datetime.utcnow()
        success = True
        
        for name, task in self.tasks.items():
            # if previous task failed hard, do we continue?
            # _run_task checks dependencies. So we can just iterate.
            if not self._run_task(task):
                 # dependencies will handle downstream skipping
                 if task.status == TaskStatus.FAILED:
                     success = False
        
        self._save_state()
        self._log_summary()
        self._record_heartbeat(flow_name, "SUCCESS" if success else "FAILED", flow_start, datetime.utcnow())
        
        return success

    def _log_summary(self):
        logger.info("=" * 40)
        logger.info("EXECUTION SUMMARY")
        for t in self.tasks.values():
            logger.info(f"{t.name}: {t.status} ({t.error if t.error else ''})")
        logger.info("=" * 40)
