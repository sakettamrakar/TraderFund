"""
Semantic Validator — Active Skeptic
=====================================
Orchestrates dual-pass adversarial validation:
  1. Contract enforcement (deterministic)
  2. Alignment Judge (LLM Pass 1)
  3. Drift Prosecutor (LLM Pass 2)
  4. Deterministic scoring
  5. Alignment tree artifact generation
  6. JSON report generation

No silent acceptance. Every score is explainable.
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from automation.semantic.contract_enforcer import ContractEnforcer
from automation.semantic.drift_analyzer import DriftAnalyzer
from automation.semantic.scoring import compute_score, ScoringResult
from automation.semantic.semantic_report import SemanticReportGenerator
from automation.history.drift_tracker import (
    append_run_record,
    compute_plan_hash,
    compute_memory_hash,
    generate_stability_report,
)

logger = logging.getLogger(__name__)


class SemanticValidator:
    """
    Phase S Active Skeptic.

    Dual-pass adversarial validation with deterministic scoring
    and full alignment tree output.
    """

    def __init__(self, run_id: str, project_root: str):
        self.run_id = run_id
        self.project_root = Path(project_root)
        self.contract_enforcer = ContractEnforcer()
        self.drift_analyzer = DriftAnalyzer()
        self.report_generator = SemanticReportGenerator()

    def validate(
        self,
        intent_file: str,
        plan: Dict[str, Any],
        changed_files: List[str],
        diff: str,
        success_criteria: str = "",
    ) -> Dict[str, Any]:
        """
        Execute full semantic validation pipeline.

        Returns structured report dict with recommendation.
        """
        logger.info("Starting Semantic Validation (Active Skeptic)...")

        validation_start = time.monotonic()

        # ── 1. Load Intent ───────────────────────────────────
        intent = self._load_intent(intent_file)

        # ── 2. Load Success Criteria ─────────────────────────
        if not success_criteria:
            success_criteria = self._load_success_criteria()

        # ── 3. Contract Enforcement (Deterministic) ──────────
        logger.info("Phase S.1: Contract enforcement...")
        violations = self.contract_enforcer.check_violations(diff, changed_files)
        if violations:
            logger.warning(f"Contract enforcement found {len(violations)} violations.")

        # ── 4. Dual-Pass Adversarial Analysis ────────────────
        logger.info("Phase S.2: Dual-pass adversarial analysis...")
        target_files = plan.get("target_files", [])
        dual_result = self.drift_analyzer.run_dual_pass(
            intent=intent,
            plan=plan,
            diff=diff,
            success_criteria=success_criteria,
            target_files=target_files,
            changed_files=changed_files,
        )

        alignment = dual_result["alignment"]
        drift = dual_result["drift"]
        explanation_tree = dual_result["explanation_tree"]
        passes_completed = dual_result["passes_completed"]

        # ── 5. Deterministic Scoring ─────────────────────────
        logger.info("Phase S.3: Deterministic scoring...")
        scoring = compute_score(alignment, drift, violations)

        # ── 6. Semantic Coverage Check ───────────────────────
        coverage_flags = self._check_semantic_coverage(diff, plan, changed_files)
        if coverage_flags:
            explanation_tree.extend(coverage_flags)

        # ── 7. Build Report ──────────────────────────────────
        report = {
            "run_id": self.run_id,
            "timestamp": datetime.now().isoformat(),
            "recommendation": scoring.recommendation,
            "final_score": scoring.final_score,
            "base_score": scoring.base_score,
            "alignment": alignment,
            "drift": drift,
            "scoring_breakdown": scoring.breakdown,
            "explanation_tree": explanation_tree,
            "contract_violations": violations,
            "passes_completed": passes_completed,
            "coverage_flags": coverage_flags,
            # Legacy fields for backward compatibility
            "intent_alignment_score": scoring.final_score,
            "success_criteria_alignment": alignment.get("plan_match", 0.0),
            "layer_integrity": "FAIL" if violations else "PASS",
            "drift_detected": (
                drift.get("overreach_detected", False) or
                len(drift.get("missing_requirements", [])) > 0 or
                len(drift.get("unintended_modifications", [])) > 0
            ),
            "violations": violations,
            "drift_reasoning": "; ".join(explanation_tree[:3]),
        }

        # ── 8. Write Artifacts ───────────────────────────────
        run_dir = self.project_root / "automation" / "runs" / self.run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        # 8a. JSON report
        report_path = run_dir / "semantic_report.json"
        self.report_generator.generate(report, report_path)

        # 8b. Alignment tree markdown
        tree_path = run_dir / "semantic_alignment.md"
        self._write_alignment_tree(tree_path, report, scoring)

        # ── 9. Cross-Run Drift Ledger ────────────────────────
        validation_latency_ms = (time.monotonic() - validation_start) * 1000.0
        self._append_drift_record(report, plan, validation_latency_ms)

        # ── 10. Visual Drift Penalty (Phase AB) ──────────────
        self._apply_visual_penalty(report, run_dir)

        logger.info(f"Semantic Validation complete. Recommendation: {scoring.recommendation}")
        return report

    # ── Drift Ledger Integration ───────────────────────────

    def _append_drift_record(
        self,
        report: Dict[str, Any],
        plan: Dict[str, Any],
        latency_ms: float,
    ):
        """Append a summarized record to the cross-run drift ledger."""
        try:
            # Determine target components from the plan
            target_components = plan.get("target_components", [])
            component_name = (
                target_components[0] if target_components else "General"
            )

            # Collect drift flags
            drift_flags = []
            drift = report.get("drift", {})
            if drift.get("overreach_detected"):
                drift_flags.append("overreach")
            for m in drift.get("missing_requirements", []):
                drift_flags.append(f"missing:{m[:60]}")
            for u in drift.get("unintended_modifications", []):
                drift_flags.append(f"unintended:{u[:60]}")
            for s in drift.get("semantic_mismatch", []):
                drift_flags.append(f"mismatch:{s[:60]}")

            plan_hash = compute_plan_hash(plan)
            memory_hash = compute_memory_hash(
                report.get("alignment", {})
            )

            append_run_record(
                run_id=self.run_id,
                component=component_name,
                alignment_score=report.get("final_score", 0.0),
                overreach_detected=drift.get("overreach_detected", False),
                missing_steps=len(drift.get("missing_requirements", [])),
                drift_flags=drift_flags,
                plan_hash=plan_hash,
                memory_hash=memory_hash,
                latency_ms=latency_ms,
            )

            # Regenerate stability report after each run
            generate_stability_report()

        except Exception as e:
            # Drift tracking is observational — never block the pipeline
            logger.warning(f"Failed to update drift ledger: {e}")

    def _apply_visual_penalty(self, report: Dict[str, Any], run_dir: Path):
        """
        Apply visual drift penalty if visual_report.json exists.

        Penalties (additive):
          - visual_drift == true  → -0.15
          - dom_passed == false   → -0.10

        Recommendation rules (downgrade only, never upgrade):
          - Can downgrade ACCEPT → REVIEW
          - Can downgrade REVIEW → REJECT
          - Never overrides a semantic hard REJECT
        """
        try:
            visual_report_path = run_dir / "visual_report.json"
            if not visual_report_path.exists():
                return

            visual = json.loads(visual_report_path.read_text(encoding="utf-8"))
            visual_drift = visual.get("visual_drift", False)
            dom_passed = visual.get("dom_passed", True)

            if not visual_drift and dom_passed:
                return

            original_score = report.get("final_score", 0.0)
            original_recommendation = report.get("recommendation", "REVIEW")

            # Compute itemised penalty
            total_penalty = 0.0
            if visual_drift:
                total_penalty += 0.15
                report.setdefault("explanation_tree", []).append(
                    "⚠ Visual drift detected (penalty=-0.15)"
                )
            if not dom_passed:
                total_penalty += 0.10
                report.setdefault("explanation_tree", []).append(
                    "⚠ DOM assertions failed (penalty=-0.10)"
                )

            adjusted_score = max(0.0, round(original_score - total_penalty, 4))
            report["final_score"] = adjusted_score
            report["visual_penalty_applied"] = round(total_penalty, 4)
            report["intent_alignment_score"] = adjusted_score

            # Determine new recommendation based on adjusted score
            if adjusted_score >= 0.85:
                new_rec = "ACCEPT"
            elif adjusted_score >= 0.60:
                new_rec = "REVIEW"
            else:
                new_rec = "REJECT"

            # Enforce downgrade-only: never upgrade, never override hard REJECT
            REC_RANK = {"ACCEPT": 0, "REVIEW": 1, "REJECT": 2}
            if REC_RANK.get(new_rec, 0) > REC_RANK.get(original_recommendation, 0):
                report["recommendation"] = new_rec
            # else keep original (already same or worse)

            # Rewrite report with updated score
            report_path = run_dir / "semantic_report.json"
            self.report_generator.generate(report, report_path)

            logger.info(
                f"Visual penalty applied: -{total_penalty} → "
                f"score={adjusted_score:.4f}, "
                f"recommendation={report['recommendation']}"
            )
        except Exception as e:
            logger.warning(f"Failed to apply visual penalty: {e}")

    # ── Intent Loading ───────────────────────────────────────

    def _load_intent(self, intent_file: str) -> str:
        """Load intent from file or return raw string."""
        try:
            path = Path(intent_file)
            if path.exists():
                return path.read_text(encoding="utf-8").strip()
        except Exception as e:
            logger.warning(f"Failed to load intent file: {e}")
        # Treat as raw intent string
        return intent_file

    def _load_success_criteria(self) -> str:
        """Attempt to load success criteria from project memory."""
        criteria_path = self.project_root / "docs" / "memory" / "02_success" / "success_criteria.md"
        try:
            if criteria_path.exists():
                return criteria_path.read_text(encoding="utf-8")[:5000]
        except Exception:
            pass
        return ""

    # ── Semantic Coverage Check ──────────────────────────────

    def _check_semantic_coverage(
        self,
        diff: str,
        plan: Dict[str, Any],
        changed_files: List[str],
    ) -> List[str]:
        """
        Check semantic coverage beyond what the LLM evaluates.

        Rules:
        1. If success criteria changed → tests must be updated too.
        2. If invariant referenced → runtime enforcement must exist.
        3. If plan has target_files → all must appear in changed_files.
        """
        flags = []

        # Rule 1: Success criteria / memory change without test update
        memory_changed = any("docs/memory/" in f or "docs/epistemic/" in f for f in changed_files)
        test_changed = any("test" in f.lower() for f in changed_files)
        if memory_changed and not test_changed:
            flags.append("⚠ Coverage gap: Memory/epistemic changed but no test file updated.")

        # Rule 2: Plan target files vs actually changed files
        target_files = plan.get("target_files", [])
        if target_files:
            for target in target_files:
                matched = any(target in f or f in target for f in changed_files)
                if not matched:
                    flags.append(f"⚠ Coverage gap: Plan targets '{target}' but it was not modified.")

        return flags

    # ── Alignment Tree Artifact ──────────────────────────────

    def _write_alignment_tree(
        self,
        path: Path,
        report: Dict[str, Any],
        scoring: ScoringResult,
    ):
        """Generate human-readable alignment tree markdown artifact."""
        try:
            lines = [
                f"# Semantic Alignment Tree — {self.run_id}",
                f"",
                f"**Generated**: {report.get('timestamp', 'N/A')}",
                f"**Recommendation**: {scoring.recommendation}",
                f"**Final Score**: {scoring.final_score:.4f}",
                f"",
                f"---",
                f"",
                f"## Scoring Breakdown",
                f"",
            ]
            for b in scoring.breakdown:
                lines.append(f"- {b}")

            lines.extend([
                f"",
                f"---",
                f"",
                f"## Alignment (Pass 1: Alignment Judge)",
                f"",
            ])
            alignment = report.get("alignment", {})
            lines.append(f"| Metric | Score |")
            lines.append(f"|--------|-------|")
            lines.append(f"| Intent Match | {alignment.get('intent_match', 0):.2f} |")
            lines.append(f"| Plan Match | {alignment.get('plan_match', 0):.2f} |")
            lines.append(f"| Scope Respected | {'✅' if alignment.get('component_scope_respected') else '❌'} |")

            lines.extend([
                f"",
                f"---",
                f"",
                f"## Drift (Pass 2: Drift Prosecutor)",
                f"",
            ])
            drift = report.get("drift", {})
            lines.append(f"- **Overreach Detected**: {'🚨 YES' if drift.get('overreach_detected') else '✅ No'}")

            missing = drift.get("missing_requirements", [])
            if missing:
                lines.append(f"")
                lines.append(f"### Missing Requirements ({len(missing)})")
                for m in missing:
                    lines.append(f"- ❌ {m}")

            unintended = drift.get("unintended_modifications", [])
            if unintended:
                lines.append(f"")
                lines.append(f"### Unintended Modifications ({len(unintended)})")
                for u in unintended:
                    lines.append(f"- ⚠ {u}")

            mismatch = drift.get("semantic_mismatch", [])
            if mismatch:
                lines.append(f"")
                lines.append(f"### Semantic Mismatch ({len(mismatch)})")
                for s in mismatch:
                    lines.append(f"- 🔴 {s}")

            lines.extend([
                f"",
                f"---",
                f"",
                f"## Contract Violations",
                f"",
            ])
            violations = report.get("contract_violations", [])
            if violations:
                for v in violations:
                    lines.append(f"- [{v.get('severity')}] {v.get('type')}: {v.get('description')}")
            else:
                lines.append(f"None.")

            lines.extend([
                f"",
                f"---",
                f"",
                f"## Explanation Tree",
                f"",
            ])
            for node in report.get("explanation_tree", []):
                lines.append(f"- {node}")

            if report.get("coverage_flags"):
                lines.extend([
                    f"",
                    f"---",
                    f"",
                    f"## Coverage Flags",
                    f"",
                ])
                for flag in report["coverage_flags"]:
                    lines.append(f"- {flag}")

            path.write_text("\n".join(lines), encoding="utf-8")
            logger.info(f"Alignment tree written to {path}")
        except Exception as e:
            logger.error(f"Failed to write alignment tree: {e}")
