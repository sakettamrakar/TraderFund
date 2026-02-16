import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

from automation.jules.config import JULES_MIN_FILES
from automation.automation_config import config
from automation.intent.intent_translation import load_intent_override
from automation.history.drift_tracker import compute_stability_index
from automation.history.regression_detector import detect_regressions

class TaskRouter:
    """
    Routes tasks to either Antigravity (AG), Jules execution planes, or Gemini (Fallback).
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def route(self, task: Dict[str, Any]) -> Tuple[str, str]:
        """
        Determines the execution plane for a given task.
        Returns: ("AG" | "JULES" | "GEMINI", reason)
        """
        task_id = task.get("task_id", "unknown")

        # Check for Test Invariant
        test_suffix = ""
        if getattr(config, "test_router", False):
            test_suffix = " [TEST_ROUTER active]"
            logger.info(f"Task {task_id} routing with TEST_ROUTER active")

        # 1. Check for Human Override
        force_executor = task.get("force_executor")
        if force_executor in ["AG", "JULES", "GEMINI"]:
            reason = f"Forced by user via force_executor={force_executor}{test_suffix}"
            logger.info(f"Task {task_id} {reason}")
            return force_executor, reason

        # 1.5. Check for Intent Override (Phase X)
        run_id = task.get("run_id", task_id)
        intent_override = load_intent_override(run_id)
        if intent_override:
            scope_limits = intent_override.get("scope_limits", "")
            logger.info(
                f"Task {task_id} has intent override from human. "
                f"Scope limits: {scope_limits}"
            )
            reason = f"Intent override detected — routing to AG for human-supervised execution{test_suffix}"
            logger.info(f"Task {task_id} routed to AG. Reason: {reason}")
            return "AG", reason

        # 1.6. Stability-Aware Routing (Phase AB)
        stability_decision = self._evaluate_stability(
            task, run_id, test_suffix
        )
        if stability_decision is not None:
            return stability_decision

        # 2. Inspect changed memory files
        changed_files = task.get("changed_memory_files", [])
        if not changed_files:
            reason = f"No memory files changed{test_suffix}"
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

            reason = f"Mechanical batch job (Unambiguous, Large Scope, No Visual/Arch constraints){test_suffix}"
            logger.info(f"Task {task_id} routed to JULES. Reason: {reason}")
            return "JULES", reason

        reasons = []
        if is_ambiguous: reasons.append("Ambiguous intent")
        if not is_mechanical: reasons.append("Not mechanical")
        if not is_large_scope: reasons.append("Small scope")
        if requires_visual: reasons.append("Requires visual inspection")
        if requires_arch: reasons.append("Requires architectural reasoning")

        reason = f"Cognitive/Interactive task: {', '.join(reasons)}{test_suffix}"
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

    # ── Stability-Aware Routing (Phase AB) ──────────────────

    def _evaluate_stability(
        self,
        task: Dict[str, Any],
        run_id: str,
        test_suffix: str,
    ):
        """
        Evaluate component stability indices and apply routing policy.

        Returns (executor, reason) tuple if stability override applies,
        or None to fall through to normal routing.
        """
        task_id = task.get("task_id", "unknown")

        # Extract impacted components from action plan
        action_plan = task.get("action_plan", {})
        target_components = action_plan.get("target_components", [])

        if not target_components:
            # No components to evaluate — fall through
            return None

        # Compute stability index for each component
        component_indices = {}
        for comp in target_components:
            idx = compute_stability_index(comp)
            component_indices[comp] = idx
            logger.info(f"Stability index for {comp}: {idx:.4f}")

        worst_stability = min(component_indices.values())

        # Determine execution mode
        if worst_stability < 0.60:
            execution_mode = "risk_controlled"
            executor = "AG"
            reason = (
                f"Stability-aware routing: worst_stability={worst_stability:.4f} < 0.60 "
                f"— forcing AG (risk_controlled){test_suffix}"
            )
        elif worst_stability < 0.85:
            execution_mode = "guarded_autonomy"
            # Allow Jules but require high semantic score
            executor = None  # Fall through to normal routing
            reason = None
        else:
            execution_mode = "normal"
            executor = None  # Fall through to normal routing
            reason = None

        # ── Regression soft-control (Phase C / D3) ───────────
        # If regression is detected, override execution_mode to
        # risk_controlled but do NOT override the executor selection.
        try:
            regression = detect_regressions(run_id=run_id)
            if regression.get("regression_detected"):
                execution_mode = "risk_controlled"
                logger.info(
                    f"Task {task_id}: regression detected — "
                    f"execution_mode forced to risk_controlled"
                )
        except Exception as e:
            logger.warning(f"Regression detection failed (non-blocking): {e}")

        # Write stability decision artifact
        self._write_stability_decision(
            run_id, worst_stability, target_components, execution_mode
        )

        if executor is not None:
            logger.info(f"Task {task_id} routed to {executor}. Reason: {reason}")
            return executor, reason

        return None

    def _write_stability_decision(
        self,
        run_id: str,
        worst_stability: float,
        components: List[str],
        execution_mode: str,
    ):
        """Write stability decision artifact for the run."""
        try:
            run_dir = self.project_root / "automation" / "runs" / run_id
            run_dir.mkdir(parents=True, exist_ok=True)

            decision = {
                "worst_stability": round(worst_stability, 6),
                "components": components,
                "execution_mode": execution_mode,
            }

            decision_path = run_dir / "stability_decision.json"
            decision_path.write_text(
                json.dumps(decision, indent=2), encoding="utf-8"
            )
            logger.info(f"Stability decision written: {decision_path}")
        except Exception as e:
            logger.warning(f"Failed to write stability decision: {e}")
