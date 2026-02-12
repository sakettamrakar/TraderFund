import logging
from pathlib import Path
from typing import Dict, Any, Tuple
from .base import Executor
# We wrap the existing JulesAdapter/Executor logic?
# `jules_adapter.py` defines `JulesExecutor` which inherits from `BaseExecutor`.
# I should probably just alias it or wrap it to match specific checks.
# But `jules_adapter.py` has `execute(self, task, run_dir)`.
# I will create a new class here that uses the adapter.

from .jules_adapter import JulesExecutor as LegacyJulesExecutor

logger = logging.getLogger(__name__)

class JulesExecutor(Executor):
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.legacy_executor = LegacyJulesExecutor(project_root)

    @property
    def name(self) -> str:
        return "JULES"

    def is_available(self) -> bool:
        # Check 1: API Key presence (API-based execution via adapter)
        # We check environment or config.
        # Ideally, we should import from automation.jules.config to be sure what the adapter sees.
        try:
            from automation.jules.config import JULES_API_KEY
            if JULES_API_KEY:
                return True
        except ImportError:
            pass
            
        # Fallback to direct environment check
        import os
        if os.environ.get("JULES_API_KEY"):
            return True
            
        # Check 2: CLI fallback (if we were using CLI, but we are using adapter)
        # Verify CLI exists just in case adapter uses it for some ops?
        # Adapter uses `requests` but might use `git` commands.
        # But core session creation is API.
        
        return False

    def execute(self, action_plan: Dict[str, Any]) -> Tuple[str, str]:
        # Delegate to legacy
        # Pass dummy run_dir
        return self.legacy_executor.execute(action_plan, self.project_root / "automation" / "runs" / "temp")
