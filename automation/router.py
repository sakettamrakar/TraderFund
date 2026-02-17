import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from automation.automation_config import config
from automation.executors.registry import (
    get_available_autonomous_executors,
    get_human_executor,
)
from automation.history.drift_tracker import compute_stability_index
from automation.history.regression_detector import detect_regressions
from automation.intent.intent_translation import load_intent_override

logger = logging.getLogger(__name__)


class TaskRouter:
    """
    Deterministic executor router with modular registry integration.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def route(self, task: Dict[str, Any]) -> Tuple[str, str]:
        """
        Resolve executor selection deterministically.
        Returns (executor_name, reason).
        """
        task_id = task.get("task_id", "unknown")
        run_id = task.get("run_id", task_id)

        human_flag = bool(getattr(config, "HUMAN_SUPERVISED", False))
        priority_list = list(getattr(config, "EXECUTOR_PRIORITY", ["JULES", "GEMINI"]))

        available_autonomous = get_available_autonomous_executors(project_root=self.project_root)
        available_names = [executor.name for executor in available_autonomous]

        forced = str(task.get("force_executor", "")).strip().upper()

        reason: str
        selected_executor_name: str
        execution_mode: str

        if forced:
            selected_executor_name, execution_mode, reason = self._resolve_forced_executor(
                forced=forced,
                available_names=available_names,
            )
        else:
            stability_override = self._evaluate_stability(task, run_id)
            intent_override = load_intent_override(run_id)

            if human_flag:
                selected_executor_name = get_human_executor(project_root=self.project_root).name
                execution_mode = "HUMAN_SUPERVISED"
                reason = "HUMAN_SUPERVISED flag enabled."
            elif intent_override:
                selected_executor_name = get_human_executor(project_root=self.project_root).name
                execution_mode = "HUMAN_SUPERVISED"
                reason = "Intent override detected; human supervision required."
            elif stability_override:
                selected_executor_name = stability_override[0]
                execution_mode = "HUMAN_SUPERVISED" if selected_executor_name == "HUMAN_SUPERVISED" else "AUTONOMOUS"
                reason = stability_override[1]
            else:
                ordered = self._sort_by_priority(available_autonomous, priority_list)
                if not ordered:
                    raise RuntimeError("No autonomous executor available")
                selected = ordered[0]
                selected_executor_name = selected.name
                execution_mode = "AUTONOMOUS"
                reason = f"Selected by priority order: {selected.name}"

        # Append test_router invariant suffix when active
        if getattr(config, "test_router", False):
            reason = f"{reason} [TEST_ROUTER active]"

        self._write_router_audit(
            run_id=run_id,
            available_executors=available_names,
            selected_executor=selected_executor_name,
            priority_list=priority_list,
            human_flag=human_flag,
            execution_mode=execution_mode,
            reason=reason,
        )

        logger.info("Task %s routed to %s (%s)", task_id, selected_executor_name, reason)
        return selected_executor_name, reason

    def _resolve_forced_executor(
        self,
        forced: str,
        available_names: List[str],
    ) -> Tuple[str, str, str]:
        forced_upper = forced.upper()
        if forced_upper in {"HUMAN_SUPERVISED", "HUMAN"}:
            return "HUMAN_SUPERVISED", "HUMAN_SUPERVISED", "Forced executor set to HUMAN_SUPERVISED."

        if forced_upper not in {name.upper() for name in available_names}:
            raise RuntimeError(f"Forced executor '{forced_upper}' is not available.")

        return forced_upper, "AUTONOMOUS", f"Forced executor set to {forced_upper}."

    def _sort_by_priority(self, executors: List[Any], priority_list: List[str]) -> List[Any]:
        rank = {name.upper(): i for i, name in enumerate(priority_list)}
        default_rank = len(priority_list) + 1
        return sorted(
            executors,
            key=lambda executor: (rank.get(executor.name.upper(), default_rank), executor.name),
        )

    def _write_router_audit(
        self,
        run_id: str,
        available_executors: List[str],
        selected_executor: str,
        priority_list: List[str],
        human_flag: bool,
        execution_mode: str,
        reason: str,
    ) -> None:
        run_dir = self.project_root / "automation" / "runs" / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        (run_dir / "executor_used.txt").write_text(selected_executor, encoding="utf-8")
        (run_dir / "execution_mode.txt").write_text(execution_mode, encoding="utf-8")

        decision = {
            "available_executors": available_executors,
            "selected_executor": selected_executor,
            "priority_list": priority_list,
            "human_flag": human_flag,
            "execution_mode": execution_mode,
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        (run_dir / "router_decision.json").write_text(
            json.dumps(decision, indent=2),
            encoding="utf-8",
        )

    # Stability-aware logic preserved from existing flow.
    def _evaluate_stability(self, task: Dict[str, Any], run_id: str) -> Optional[Tuple[str, str]]:
        task_id = task.get("task_id", "unknown")
        action_plan = task.get("action_plan", {})
        target_components = action_plan.get("target_components", [])

        if not target_components:
            return None

        component_indices = {}
        for comp in target_components:
            idx = compute_stability_index(comp)
            component_indices[comp] = idx
            logger.info("Stability index for %s: %.4f", comp, idx)

        worst_stability = min(component_indices.values())

        if worst_stability < 0.60:
            execution_mode = "risk_controlled"
            executor = "HUMAN_SUPERVISED"
            reason = (
                f"Stability-aware routing: worst_stability={worst_stability:.4f} < 0.60; "
                "forcing HUMAN_SUPERVISED (risk_controlled)."
            )
        elif worst_stability < 0.85:
            execution_mode = "guarded_autonomy"
            executor = None
            reason = None
        else:
            execution_mode = "normal"
            executor = None
            reason = None

        try:
            regression = detect_regressions(run_id=run_id)
            if regression.get("regression_detected"):
                execution_mode = "risk_controlled"
                logger.info(
                    "Task %s: regression detected; execution_mode forced to risk_controlled",
                    task_id,
                )
        except Exception as exc:
            logger.warning("Regression detection failed (non-blocking): %s", exc)

        self._write_stability_decision(
            run_id=run_id,
            worst_stability=worst_stability,
            components=target_components,
            execution_mode=execution_mode,
        )

        if executor:
            return executor, reason
        return None

    def _write_stability_decision(
        self,
        run_id: str,
        worst_stability: float,
        components: List[str],
        execution_mode: str,
    ) -> None:
        try:
            run_dir = self.project_root / "automation" / "runs" / run_id
            run_dir.mkdir(parents=True, exist_ok=True)

            decision = {
                "worst_stability": round(worst_stability, 6),
                "components": components,
                "execution_mode": execution_mode,
            }
            (run_dir / "stability_decision.json").write_text(
                json.dumps(decision, indent=2),
                encoding="utf-8",
            )
            logger.info("Stability decision written for run %s", run_id)
        except Exception as exc:
            logger.warning("Failed to write stability decision: %s", exc)
