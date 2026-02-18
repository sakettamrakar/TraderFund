"""
Dual-Pass Adversarial Drift Analyzer
======================================
Pass 1: Alignment Judge — evaluates whether implementation satisfies intent/plan.
Pass 2: Drift Prosecutor — adversarially searches for drift, overreach, gaps.

Both passes enforce STRICT JSON output. Non-JSON responses are rejected.
"""

import logging
import json
from typing import Dict, Any, Optional, List

from automation.executors.gemini_fallback import ask

logger = logging.getLogger(__name__)

# ── Structured JSON Schemas ──────────────────────────────────

ALIGNMENT_SCHEMA = {
    "intent_match": "float 0.0-1.0",
    "plan_match": "float 0.0-1.0",
    "component_scope_respected": "boolean",
}

DRIFT_SCHEMA = {
    "overreach_detected": "boolean",
    "missing_requirements": "list of strings",
    "unintended_modifications": "list of strings",
    "semantic_mismatch": "list of strings",
}

# ── Default Fail-Safe Results ────────────────────────────────

DEFAULT_ALIGNMENT = {
    "intent_match": 0.0,
    "plan_match": 0.0,
    "component_scope_respected": False,
}

DEFAULT_DRIFT = {
    "overreach_detected": True,
    "missing_requirements": ["Analysis failed — assumed worst case"],
    "unintended_modifications": [],
    "semantic_mismatch": [],
}


class DriftAnalyzer:
    """
    Dual-pass adversarial analyzer using structured LLM evaluation.

    Pass 1 (Alignment Judge): Measures how well the diff matches intent + plan.
    Pass 2 (Drift Prosecutor): Adversarially searches for failures.
    """

    def run_dual_pass(
        self,
        intent: str,
        plan: Dict[str, Any],
        diff: str,
        success_criteria: str = "",
        target_files: Optional[List[str]] = None,
        changed_files: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Execute both passes and return combined structured result.

        Returns dict with keys:
            alignment: dict (Pass 1 result)
            drift: dict (Pass 2 result)
            explanation_tree: list[str]
            passes_completed: int (0, 1, or 2)
        """
        if not diff or not diff.strip():
            return {
                "alignment": {
                    "intent_match": 1.0,
                    "plan_match": 1.0,
                    "component_scope_respected": True,
                },
                "drift": {
                    "overreach_detected": False,
                    "missing_requirements": [],
                    "unintended_modifications": [],
                    "semantic_mismatch": [],
                },
                "explanation_tree": ["No code changes to analyze — trivially aligned."],
                "passes_completed": 0,
            }

        # Sanitize inputs
        intent = intent or "No explicit intent provided."
        plan = plan or {"status": "NO_PLAN", "objective": "Unknown"}
        target_files = target_files or plan.get("target_files", [])

        # Log if diff will be truncated so the caller is always aware
        if len(diff) > 12000:
            logger.warning(
                "DriftAnalyzer: DIFF_TRUNCATED=true original_len=%d truncated_to=12000",
                len(diff),
            )

        # ── Pass 1: Alignment Judge ──────────────────────────
        logger.info("Pass 1: Alignment Judge starting...")
        alignment = self._pass_alignment_judge(intent, plan, diff, success_criteria)

        # ── Pass 2: Drift Prosecutor ─────────────────────────
        logger.info("Pass 2: Drift Prosecutor starting...")
        drift = self._pass_drift_prosecutor(intent, plan, diff, target_files, changed_files)

        # ── Overreach Detection (Deterministic) ──────────────
        overreach_from_files = self._detect_file_overreach(target_files, changed_files)
        if overreach_from_files and not drift.get("overreach_detected"):
            drift["overreach_detected"] = True
            drift.setdefault("unintended_modifications", []).extend(overreach_from_files)

        # ── Build Explanation Tree ───────────────────────────
        explanation_tree = self._build_explanation_tree(alignment, drift, intent, plan)

        passes_completed = 2
        if alignment == DEFAULT_ALIGNMENT:
            passes_completed -= 1
        if drift == DEFAULT_DRIFT:
            passes_completed -= 1

        return {
            "alignment": alignment,
            "drift": drift,
            "explanation_tree": explanation_tree,
            "passes_completed": passes_completed,
        }

    # ── Legacy compatibility ─────────────────────────────────
    def detect_drift(self, intent, plan, diff, success_criteria=""):
        """Legacy API — wraps dual_pass for backward compatibility."""
        result = self.run_dual_pass(intent, plan, diff, success_criteria)
        alignment = result["alignment"]
        drift = result["drift"]
        score = (alignment.get("intent_match", 0) + alignment.get("plan_match", 0)) / 2
        drift_detected = (
            drift.get("overreach_detected", False) or
            len(drift.get("missing_requirements", [])) > 0 or
            len(drift.get("unintended_modifications", [])) > 0
        )
        return {
            "drift_detected": drift_detected,
            "reasoning": "; ".join(result.get("explanation_tree", [])),
            "alignment_score": score,
            "missing_elements": drift.get("missing_requirements", []),
        }

    # ── Pass 1: Alignment Judge ──────────────────────────────

    def _pass_alignment_judge(
        self, intent: str, plan: Dict, diff: str, success_criteria: str
    ) -> Dict[str, Any]:
        prompt = (
            "You are an Alignment Judge. Your job is to evaluate whether a code implementation "
            "satisfies the stated memory intent and action plan.\n\n"
            "DO NOT assume correctness. Evaluate critically.\n\n"
            f"## Intent\n{intent}\n\n"
            f"## Success Criteria\n{success_criteria or 'None provided.'}\n\n"
            f"## Action Plan\n{json.dumps(plan, indent=2)}\n\n"
            f"## Code Changes (Diff)\n{diff[:12000]}\n\n"
            "## Instructions\n"
            "Return STRICT JSON with exactly these fields:\n"
            "```json\n"
            "{\n"
            '  "intent_match": <float 0.0 to 1.0>,\n'
            '  "plan_match": <float 0.0 to 1.0>,\n'
            '  "component_scope_respected": <true or false>\n'
            "}\n"
            "```\n"
            "Rules:\n"
            "- intent_match: How well the diff fulfills the stated intent (0=not at all, 1=perfectly).\n"
            "- plan_match: How well the diff follows each step of the action plan.\n"
            "- component_scope_respected: false if the diff modifies things outside the plan's target scope.\n"
            "Return ONLY the JSON object. No commentary."
        )
        return self._call_llm_structured(prompt, DEFAULT_ALIGNMENT, "Alignment Judge")

    # ── Pass 2: Drift Prosecutor ─────────────────────────────

    def _pass_drift_prosecutor(
        self,
        intent: str,
        plan: Dict,
        diff: str,
        target_files: List[str],
        changed_files: Optional[List[str]],
    ) -> Dict[str, Any]:
        files_context = ""
        if target_files:
            files_context = f"Planned target files: {', '.join(target_files)}\n"
        if changed_files:
            files_context += f"Actually changed files: {', '.join(changed_files)}\n"

        prompt = (
            "You are a Drift Prosecutor. Your job is to ADVERSARIALLY search for failures, "
            "drift, overreach, and missing enforcement in a code implementation.\n\n"
            "ASSUME the implementation is INCORRECT. Try to prove it.\n\n"
            f"## Intent\n{intent}\n\n"
            f"## Action Plan\n{json.dumps(plan, indent=2)}\n\n"
            f"## File Context\n{files_context}\n"
            f"## Code Changes (Diff)\n{diff[:12000]}\n\n"
            "## Instructions\n"
            "Return STRICT JSON with exactly these fields:\n"
            "```json\n"
            "{\n"
            '  "overreach_detected": <true or false>,\n'
            '  "missing_requirements": ["list of plan steps or intent requirements NOT implemented"],\n'
            '  "unintended_modifications": ["list of changes NOT requested by the plan"],\n'
            '  "semantic_mismatch": ["list of cases where implementation contradicts intent"]\n'
            "}\n"
            "```\n"
            "Rules:\n"
            "- overreach_detected: true if the diff modifies files or logic beyond the plan scope.\n"
            "- missing_requirements: each plan step or intent requirement that is absent from the diff.\n"
            "- unintended_modifications: each change in the diff that was NOT requested.\n"
            "- semantic_mismatch: cases where the implementation does the OPPOSITE of what was intended.\n"
            "Be thorough. Be adversarial. Return ONLY the JSON object."
        )
        return self._call_llm_structured(prompt, DEFAULT_DRIFT, "Drift Prosecutor")

    # ── Deterministic Overreach Detection ────────────────────

    def _detect_file_overreach(
        self,
        target_files: List[str],
        changed_files: Optional[List[str]],
    ) -> List[str]:
        """
        Check if changed files include files NOT in the plan's target list.
        Returns list of overreaching file paths.
        """
        if not target_files or not changed_files:
            return []

        overreach = []
        for f in changed_files:
            if not any(target in f or f in target for target in target_files):
                overreach.append(f"File '{f}' modified but not in plan targets: {target_files}")
        return overreach

    # ── LLM Call with Strict JSON Enforcement ────────────────

    def _call_llm_structured(
        self, prompt: str, default: Dict, pass_name: str
    ) -> Dict[str, Any]:
        """Call LLM, enforce JSON, return default on failure."""
        response = ""
        try:
            response = ask(prompt)
            parsed = self._extract_json(response)
            if parsed is None:
                logger.error(f"{pass_name}: LLM returned non-JSON response. Rejecting.")
                return dict(default)
            # Validate required keys exist
            for key in default:
                if key not in parsed:
                    logger.warning(f"{pass_name}: Missing key '{key}' in LLM response. Using default.")
                    parsed[key] = default[key]
            return parsed
        except Exception as e:
            logger.error(f"{pass_name} failed: {e}")
            if "MOCK_RESPONSE" in str(response):
                # Mock mode — return neutral result
                return dict(default)
            return dict(default)

    def _extract_json(self, response: str) -> Optional[Dict]:
        """Extract JSON from LLM response, handling markdown fences."""
        clean = response.strip()

        # Strip markdown code fences
        if "```json" in clean:
            clean = clean.split("```json")[1].split("```")[0].strip()
        elif "```" in clean:
            parts = clean.split("```")
            if len(parts) >= 3:
                clean = parts[1].strip()

        # Find JSON braces
        if "{" in clean:
            start = clean.find("{")
            end = clean.rfind("}") + 1
            clean = clean[start:end]

        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            return None

    # ── Explanation Tree Builder ──────────────────────────────

    def _build_explanation_tree(
        self,
        alignment: Dict,
        drift: Dict,
        intent: str,
        plan: Dict,
    ) -> List[str]:
        """Build human-readable explanation tree from structured results."""
        tree = []
        tree.append(f"Intent: {intent[:120]}")
        tree.append(f"Plan Objective: {plan.get('objective', 'Unknown')}")

        im = alignment.get("intent_match", 0)
        pm = alignment.get("plan_match", 0)
        tree.append(f"Alignment Judge: intent_match={im:.2f}, plan_match={pm:.2f}")

        if not alignment.get("component_scope_respected", True):
            tree.append("⚠ Scope violation: implementation touches components outside plan")

        if drift.get("overreach_detected"):
            tree.append("🚨 Overreach detected: diff modifies beyond authorized scope")

        for m in drift.get("missing_requirements", []):
            tree.append(f"❌ Missing: {m}")

        for u in drift.get("unintended_modifications", []):
            tree.append(f"⚠ Unintended: {u}")

        for s in drift.get("semantic_mismatch", []):
            tree.append(f"🔴 Mismatch: {s}")

        return tree
