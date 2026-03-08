from __future__ import annotations

import argparse
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .diagnosis_engine import DiagnosisEngine
from .remediation_engine import RemediationEngine
from .validation_engine import ValidationContext, ValidationEngine
from .validation_registry import ValidationRegistry

logger = logging.getLogger(__name__)


class ValidationRunner:
    def __init__(self, repo_root: str | None = None, report_dir: str | None = None):
        self.repo_root = str(Path(repo_root or Path(__file__).resolve().parents[2]).resolve())
        self.report_dir = Path(report_dir or Path(self.repo_root) / "logs" / "validation")
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.registry = ValidationRegistry(self.repo_root)
        self.engine = ValidationEngine()
        self.diagnosis_engine = DiagnosisEngine()
        self.remediation_engine = RemediationEngine(self.repo_root, self.registry.skills)

    def component_map(self) -> Dict[str, List[str]]:
        return self.registry.component_map()

    def run_phase(
        self,
        phase: str,
        *,
        hook: str | None = None,
        metadata: Optional[Dict[str, Any]] = None,
        auto_remediate: bool = False,
        fail_fast: bool = False,
    ) -> Dict[str, Any]:
        metadata = metadata or {}
        context = ValidationContext(repo_root=self.repo_root, phase=phase, hook=hook, metadata=metadata)
        tasks = self.registry.tasks_for_phase(phase)
        started_at = datetime.now(timezone.utc).isoformat()
        results = self.engine.run_tasks(tasks, context)
        diagnoses = self.diagnosis_engine.diagnose(results)
        remediations = self.remediation_engine.propose(diagnoses, metadata)
        applied = self.remediation_engine.apply_safe_actions(remediations) if auto_remediate else []

        summary = {
            "phase": phase,
            "hook": hook or "manual",
            "started_at": started_at,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata,
            "component_map": self.registry.component_map(),
            "results": [result.to_dict() for result in results],
            "diagnoses": [diagnosis.to_dict() for diagnosis in diagnoses],
            "remediations": [action.to_dict() for action in remediations],
            "applied_remediations": applied,
            "has_failures": any(result.status == "FAIL" for result in results),
        }
        self._persist_summary(summary)

        if summary["has_failures"]:
            logger.warning("Validation failures detected for phase=%s hook=%s", phase, hook or "manual")
            if fail_fast:
                raise RuntimeError(f"Validation failed for phase={phase} hook={hook or 'manual'}")
        else:
            logger.info("Validation passed for phase=%s hook=%s", phase, hook or "manual")

        return summary

    def run_loop(
        self,
        phases: Iterable[str],
        *,
        interval_seconds: int = 60,
        max_iterations: int = 0,
        auto_remediate: bool = False,
    ) -> List[Dict[str, Any]]:
        summaries: List[Dict[str, Any]] = []
        iteration = 0
        while True:
            iteration += 1
            for phase in phases:
                summaries.append(
                    self.run_phase(
                        phase,
                        hook="loop",
                        metadata={"iteration": iteration},
                        auto_remediate=auto_remediate,
                    )
                )
            if max_iterations and iteration >= max_iterations:
                break
            time.sleep(interval_seconds)
        return summaries

    def run_post_ingestion(self, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        ingestion_summary = self.run_phase("ingestion", hook="post_ingestion", metadata=metadata)
        memory_summary = self.run_phase("memory", hook="post_ingestion", metadata=metadata)
        return {
            "phase": "post_ingestion",
            "hook": "post_ingestion",
            "summaries": {
                "ingestion": ingestion_summary,
                "memory": memory_summary,
            },
            "has_failures": bool(ingestion_summary.get("has_failures") or memory_summary.get("has_failures")),
        }

    def run_post_research(self, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.run_phase("research", hook="post_research", metadata=metadata)

    def run_post_evaluation(self, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.run_phase("evaluation", hook="post_evaluation", metadata=metadata)

    def run_pre_dashboard_refresh(self, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.run_phase("dashboard", hook="pre_dashboard_refresh", metadata=metadata)

    def _persist_summary(self, summary: Dict[str, Any]) -> None:
        phase = str(summary["phase"])
        hook = str(summary.get("hook") or "manual")
        path = self.report_dir / f"{phase}_{hook}_latest.json"
        path.write_text(json.dumps(summary, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="TraderFund self-healing validation runner")
    parser.add_argument("--phase", choices=["ingestion", "memory", "research", "evaluation", "dashboard"], required=True)
    parser.add_argument("--hook", default="manual")
    parser.add_argument("--auto-remediate", action="store_true")
    parser.add_argument("--profile", default="")
    parser.add_argument("--market", default="US")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s")
    runner = ValidationRunner()
    metadata: Dict[str, Any] = {"market": args.market}
    if args.profile:
        metadata["profile"] = args.profile
    summary = runner.run_phase(
        args.phase,
        hook=args.hook,
        metadata=metadata,
        auto_remediate=args.auto_remediate,
    )
    print(json.dumps({"phase": summary["phase"], "hook": summary["hook"], "has_failures": summary["has_failures"]}, indent=2))
    return 1 if summary["has_failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())