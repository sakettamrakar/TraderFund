import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

from automation.jules.config import JULES_MIN_FILES

class TaskRouter:
    """
    Routes tasks to either Antigravity (AG) or Jules execution planes.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def route(self, task: Dict[str, Any]) -> Tuple[str, str]:
        """
        Determines the execution plane for a given task.
        Returns: ("AG" or "JULES", reason)
        """
        task_id = task.get("task_id", "unknown")

        # 1. Check for Human Override
        force_executor = task.get("force_executor")
        if force_executor in ["AG", "JULES"]:
            reason = f"Forced by user via force_executor={force_executor}"
            logger.info(f"Task {task_id} {reason}")
            return force_executor, reason

        # 2. Inspect changed memory files
        changed_files = task.get("changed_memory_files", [])
        if not changed_files:
            reason = "No memory files changed"
            logger.info(f"Task {task_id} routed to AG. Reason: {reason}")
            return "AG", reason

        # Read memory content to analyze intent
        memory_content = self._read_memory_files(changed_files)

        # 3. Analyze Characteristics
        is_mechanical = self._is_mechanical(memory_content)
        is_large_scope = self._is_large_scope(memory_content)
        is_ambiguous = self._is_ambiguous(memory_content)
        requires_visual = self._requires_visual(memory_content)
        requires_arch = self._requires_architectural_reasoning(memory_content)

        # Log analysis
        logger.info(f"Task {task_id} analysis: Mechanical={is_mechanical}, Large={is_large_scope}, "
                    f"Ambiguous={is_ambiguous}, Visual={requires_visual}, Arch={requires_arch}")

        # 4. Apply Rules
        # Route to JULES if ALL are true:
        # - No ambiguity detected
        # - Memory change is structural/mechanical
        # - Touches > N files OR large refactor (we use is_large_scope as proxy)
        # - Does not require visual inspection
        # - Does not require architectural reasoning

        if (not is_ambiguous and
            is_mechanical and
            is_large_scope and
            not requires_visual and
            not requires_arch):

            reason = "Mechanical batch job (Unambiguous, Large Scope, No Visual/Arch constraints)"
            logger.info(f"Task {task_id} routed to JULES. Reason: {reason}")
            return "JULES", reason

        reasons = []
        if is_ambiguous: reasons.append("Ambiguous intent")
        if not is_mechanical: reasons.append("Not mechanical")
        if not is_large_scope: reasons.append("Small scope")
        if requires_visual: reasons.append("Requires visual inspection")
        if requires_arch: reasons.append("Requires architectural reasoning")

        reason = f"Cognitive/Interactive task: {', '.join(reasons)}"
        logger.info(f"Task {task_id} routed to AG. Reason: {reason}")
        return "AG", reason

    def _read_memory_files(self, files: List[str]) -> str:
        content = []
        for f in files:
            path = self.project_root / f
            if path.exists():
                content.append(path.read_text())
        return "\n".join(content)

    def _is_mechanical(self, content: str) -> bool:
        keywords = ["refactor", "migrate", "rename", "move", "format", "standardize", "boilerplate"]
        content_lower = content.lower()
        return any(k in content_lower for k in keywords)

    def _is_large_scope(self, content: str) -> bool:
        # Heuristic: Count explicitly mentioned files or blocks
        # Assuming ### FILE: pattern usage in memory
        file_count = content.count("### FILE:")
        if file_count >= JULES_MIN_FILES:
            return True

        # Also check for "large refactor" keywords
        if "large refactor" in content.lower():
            return True

        return False

    def _is_ambiguous(self, content: str) -> bool:
        keywords = ["maybe", "explore", "investigate", "unsure", "unknown", "open question", "TBD"]
        content_lower = content.lower()
        return any(k in content_lower for k in keywords)

    def _requires_visual(self, content: str) -> bool:
        keywords = ["css", "style", "ui", "frontend", "visual", "layout", "responsive", "html"]
        content_lower = content.lower()
        return any(k in content_lower for k in keywords)

    def _requires_architectural_reasoning(self, content: str) -> bool:
        keywords = ["architecture", "design pattern", "system design", "tradeoff", "strategy"]
        content_lower = content.lower()
        # Check if modifying architectural docs
        if "docs/architecture" in content:
            return True
        return any(k in content_lower for k in keywords)
