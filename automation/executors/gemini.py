import logging
from pathlib import Path
from typing import Dict, Any, Tuple
from .base import Executor
from .gemini_fallback import GeminiExecutor as LegacyGeminiExecutor

logger = logging.getLogger(__name__)

class GeminiExecutor(Executor):
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.legacy_executor = LegacyGeminiExecutor(project_root)

    @property
    def name(self) -> str:
        return "GEMINI"

    def is_available(self) -> bool:
        # User said: "Always returns True. Gemini is emergency only."
        return True

    def execute(self, action_plan: Dict[str, Any]) -> Tuple[str, str]:
        # Delegate
        return self.legacy_executor.execute(action_plan, self.project_root / "automation" / "runs" / "temp")
