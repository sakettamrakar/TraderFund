"""Scheduler - Models"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable
from datetime import datetime

class TaskStatus:
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    NO_OP = "NO_OP"  # Success, but did nothing (e.g. no new data)

@dataclass
class Task:
    name: str
    module_path: str
    function_name: str
    kwargs: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    retries: int = 0
    timeout_sec: int = 300
    description: str = ""
    
    # Runtime state
    status: str = TaskStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error: Optional[str] = None
    retry_count: int = 0
    
    # Persistence state (loaded from state file)
    consecutive_failures: int = 0
    last_success_time: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "status": self.status,
            "start": self.start_time.isoformat() if self.start_time else None,
            "end": self.end_time.isoformat() if self.end_time else None,
            "error": self.error,
            "retries": self.retry_count,
            "consecutive_failures": self.consecutive_failures
        }
