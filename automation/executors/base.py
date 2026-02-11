from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Tuple

class BaseExecutor(ABC):
    """
    Abstract base class for all execution backends.
    """
    def __init__(self, project_root: Path):
        self.project_root = project_root

    @abstractmethod
    def execute(self, task: Dict[str, Any], run_dir: Path) -> Tuple[str, str]:
        """
        Executes the task and returns a diff and execution logs.

        Args:
            task: The task definition dictionary.
            run_dir: The directory for this execution run (for logs, diffs, etc).

        Returns:
            Tuple[str, str]: A tuple containing the unified diff of changes and the execution logs.
        """
        pass
