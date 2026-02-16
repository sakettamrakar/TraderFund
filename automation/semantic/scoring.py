"""
Deterministic Scoring Engine for Phase S Semantic Validation
=============================================================
Pure math. No LLM. Takes structured alignment + drift data and
produces a final score with an explainable breakdown.

Acceptance Policy:
  ACCEPT  → final_score >= 0.85 AND zero drift flags
  REVIEW  → 0.60 <= final_score < 0.85
  REJECT  → final_score < 0.60 OR overreach_detected
"""

import logging
from typing import Dict, Any, List
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ScoringResult:
    """Immutable result of deterministic scoring."""
    base_score: float
    scope_penalty: float
    overreach_penalty: float
    missing_penalty: float
    unintended_penalty: float
    final_score: float
    recommendation: str  # ACCEPT | REVIEW | REJECT
    breakdown: List[str] = field(default_factory=list)


def compute_score(
    alignment: Dict[str, Any],
    drift: Dict[str, Any],
    contract_violations: List[Dict[str, str]],
) -> ScoringResult:
    """
    Deterministic scoring from structured LLM outputs.

    Parameters
    ----------
    alignment : dict with keys:
        intent_match        (float 0-1)
        plan_match           (float 0-1)
        component_scope_respected (bool)
    drift : dict with keys:
        overreach_detected         (bool)
        missing_requirements       (list[str])
        unintended_modifications   (list[str])
        semantic_mismatch          (list[str])
    contract_violations : list of violation dicts from ContractEnforcer
    """
    breakdown = []

    # ── Base Score ────────────────────────────────────────────
    intent_match = float(alignment.get("intent_match", 0.0))
    plan_match = float(alignment.get("plan_match", 0.0))
    base_score = (intent_match + plan_match) / 2.0
    breakdown.append(f"Base score = mean({intent_match:.2f}, {plan_match:.2f}) = {base_score:.2f}")

    # ── Scope Penalty ────────────────────────────────────────
    scope_respected = alignment.get("component_scope_respected", True)
    scope_penalty = 0.0
    if not scope_respected:
        scope_penalty = 0.30
        breakdown.append(f"Scope penalty: -0.30 (component_scope_respected=false)")

    # ── Overreach Penalty ────────────────────────────────────
    overreach = drift.get("overreach_detected", False)
    overreach_penalty = 0.0
    if overreach:
        overreach_penalty = 0.20
        breakdown.append(f"Overreach penalty: -0.20 (overreach_detected=true)")

    # ── Missing Requirements Penalty ─────────────────────────
    missing = drift.get("missing_requirements", [])
    missing_penalty = 0.10 * len(missing)
    if missing:
        breakdown.append(f"Missing requirements penalty: -0.10 × {len(missing)} = -{missing_penalty:.2f}")
        for m in missing:
            breakdown.append(f"  ▸ Missing: {m}")

    # ── Unintended Modifications Penalty ─────────────────────
    unintended = drift.get("unintended_modifications", [])
    unintended_penalty = 0.10 * len(unintended)
    if unintended:
        breakdown.append(f"Unintended modifications penalty: -0.10 × {len(unintended)} = -{unintended_penalty:.2f}")
        for u in unintended:
            breakdown.append(f"  ▸ Unintended: {u}")

    # ── Contract Violation Penalty ───────────────────────────
    contract_penalty = 0.0
    high_violations = [v for v in contract_violations if v.get("severity") == "HIGH"]
    medium_violations = [v for v in contract_violations if v.get("severity") == "MEDIUM"]
    if high_violations:
        contract_penalty += 0.25 * len(high_violations)
        breakdown.append(f"Contract violation penalty (HIGH): -0.25 × {len(high_violations)} = -{0.25 * len(high_violations):.2f}")
    if medium_violations:
        contract_penalty += 0.10 * len(medium_violations)
        breakdown.append(f"Contract violation penalty (MEDIUM): -0.10 × {len(medium_violations)} = -{0.10 * len(medium_violations):.2f}")

    # ── Semantic Mismatch Penalty ────────────────────────────
    mismatch = drift.get("semantic_mismatch", [])
    mismatch_penalty = 0.05 * len(mismatch)
    if mismatch:
        breakdown.append(f"Semantic mismatch penalty: -0.05 × {len(mismatch)} = -{mismatch_penalty:.2f}")

    # ── Final Score ──────────────────────────────────────────
    total_penalty = (scope_penalty + overreach_penalty + missing_penalty +
                     unintended_penalty + contract_penalty + mismatch_penalty)
    final_score = max(0.0, base_score - total_penalty)
    final_score = round(final_score, 4)
    breakdown.append(f"Total penalty = {total_penalty:.2f}")
    breakdown.append(f"Final score = max(0, {base_score:.2f} - {total_penalty:.2f}) = {final_score:.4f}")

    # ── Recommendation ───────────────────────────────────────
    drift_flags_present = (
        overreach or
        len(missing) > 0 or
        len(unintended) > 0 or
        len(mismatch) > 0
    )

    if final_score >= 0.85 and not drift_flags_present and not high_violations:
        recommendation = "ACCEPT"
    elif final_score < 0.60 or overreach:
        recommendation = "REJECT"
    else:
        recommendation = "REVIEW"

    breakdown.append(f"Recommendation = {recommendation}")

    return ScoringResult(
        base_score=round(base_score, 4),
        scope_penalty=scope_penalty,
        overreach_penalty=overreach_penalty,
        missing_penalty=missing_penalty,
        unintended_penalty=unintended_penalty,
        final_score=final_score,
        recommendation=recommendation,
        breakdown=breakdown,
    )
