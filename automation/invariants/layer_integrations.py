"""
Layer Integration Adapters — Phase CI
======================================
Thin adapters that bridge each cognitive layer's native output format into
the canonical invariant signatures expected by catastrophic_firewall.py.

Usage:  import the relevant gate function and call it at the END of the
        corresponding layer output method.  The gate raises
        CatastrophicInvariantError on violation — callers must not swallow it.

One function per invariant (L1 → L9, no L6 gap):
  gate_l1_regime          — traderfund/regime/core.py  StateManager.update()
  gate_l2_narrative       — src/governance/narrative_guard.py  compute_narrative_for_market()
  gate_l3_trust           — src/intelligence/meta_analysis.py  MetaAnalysis.analyze()
  gate_l4_factor          — src/layers/factor_live.py  FactorLayerLive.update_snapshot()
  gate_l5_strategy_regime — src/intelligence/decision_policy_engine.py  _evaluate_*_policy()
  gate_l7_convergence     — src/intelligence/engine.py  IntelligenceEngine.run_cycle()
  gate_l8_risk_caps       — src/capital/capital_readiness.py  check_capital_readiness()
  gate_l9_portfolio_regime— src/intelligence/decision_policy_engine.py  evaluate() / capital
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from automation.invariants.catastrophic_firewall import (
    CatastrophicInvariantError,  # re-export for callers
    check_convergence_integrity,
    check_factor_integrity,
    check_narrative_grounding,
    check_portfolio_regime_conflict,
    check_regime_validity,
    check_risk_caps,
    check_strategy_regime_alignment,
    check_trust_determinism,
    run_invariant,
)

logger = logging.getLogger(__name__)

__all__ = [
    "CatastrophicInvariantError",
    "gate_l1_regime",
    "gate_l2_narrative",
    "gate_l3_trust",
    "gate_l4_factor",
    "gate_l5_strategy_regime",
    "gate_l7_convergence",
    "gate_l8_risk_caps",
    "gate_l9_portfolio_regime",
]


# ───────────────────────────────────────────────────────────────────────────
# L1 — Regime Validity
# ───────────────────────────────────────────────────────────────────────────
def gate_l1_regime(regime_state_obj: Any) -> None:
    """Hard gate after StateManager.update().

    Accepts either a Pydantic RegimeState (with ``.behavior`` attribute) or a
    plain dict with key ``"behavior"``.
    """
    if hasattr(regime_state_obj, "behavior"):
        behavior = str(regime_state_obj.behavior.value) if hasattr(regime_state_obj.behavior, "value") else str(regime_state_obj.behavior)
    else:
        behavior = str((regime_state_obj or {}).get("behavior", ""))
    run_invariant("check_regime_validity", check_regime_validity, {"behavior": behavior})


# ───────────────────────────────────────────────────────────────────────────
# L2 — Narrative Grounding
# ───────────────────────────────────────────────────────────────────────────
def gate_l2_narrative(narrative_payload: Dict[str, Any]) -> None:
    """Hard gate after compute_narrative_for_market().

    Maps:
      headline → ``gating_reason`` (always populated by narrative guard)
      sources  → ``provenance_references`` / ``citations``
    """
    payload = narrative_payload or {}
    headline = (
        payload.get("gating_reason")
        or payload.get("summary")
        or payload.get("regime_state")
        or ""
    )
    sources = payload.get("provenance_references") or payload.get("citations") or []
    run_invariant(
        "check_narrative_grounding",
        check_narrative_grounding,
        {"headline": headline, "sources": list(sources)},
    )


# ───────────────────────────────────────────────────────────────────────────
# L3 — Trust Determinism
# ───────────────────────────────────────────────────────────────────────────
def gate_l3_trust(trust_score: Any) -> None:
    """Hard gate after MetaAnalysis.analyze().

    Validates that trust_score is a float in [0.0, 1.0].
    """
    run_invariant("check_trust_determinism", check_trust_determinism, {}, trust_score)


# ───────────────────────────────────────────────────────────────────────────
# L4 — Factor Integrity
# ───────────────────────────────────────────────────────────────────────────
def gate_l4_factor(factor_snapshot: Any) -> None:
    """Hard gate after FactorLayerLive.update_snapshot().

    Normalises FactorSnapshot.exposures to {name: {"strength": value}}.
    Skips check when fewer than 2 factor exposures are present (not enough
    data to assess diversity — conservative pass to avoid false positives
    during bootstrap).
    """
    if factor_snapshot is None:
        return
    exposures = getattr(factor_snapshot, "exposures", None) or {}
    if len(exposures) < 2:
        logger.debug("gate_l4_factor: skipped — fewer than 2 exposures")
        return
    factor_output: Dict[str, Any] = {
        name: {"strength": getattr(exp, "exposure_value", 0.0)}
        for name, exp in exposures.items()
    }
    run_invariant("check_factor_integrity", check_factor_integrity, factor_output)


# ───────────────────────────────────────────────────────────────────────────
# L5 — Strategy–Regime Alignment
# ───────────────────────────────────────────────────────────────────────────
def gate_l5_strategy_regime(
    permissions: List[str],
    regime_code: str,
    policy_status: str = "ACTIVE",
) -> None:
    """Hard gate after _evaluate_*_policy() in DecisionPolicyEngine.

    Skips check when policy is HALTED (no strategies are active).
    Constructs a strategy proxy from the granted permissions:
      • ALLOW_LONG_ENTRY → strategy compatible with BULLISH / NEUTRAL
      • ALLOW_SHORT_ENTRY → strategy compatible with BEARISH / NEUTRAL / BEAR_RISK_OFF
      • OBSERVE_ONLY      → strategy compatible with any regime (observatory mode)
    """
    if policy_status == "HALTED":
        logger.debug("gate_l5_strategy_regime: skipped — policy is HALTED")
        return

    if "ALLOW_LONG_ENTRY" in permissions:
        compatible = ["BULLISH", "NEUTRAL", "BULL_VOL", "BULL_CALM", "RISK_ON", "TRENDING_NORMAL_VOL"]
    elif "ALLOW_SHORT_ENTRY" in permissions:
        compatible = ["BEARISH", "NEUTRAL", "BEAR_RISK_OFF", "RISK_OFF", "TRENDING_HIGH_VOL",
                      "MEAN_REVERTING_HIGH_VOL", "STRESS"]
    else:
        # OBSERVE_ONLY or REBALANCING — no directional strategy is active
        logger.debug("gate_l5_strategy_regime: skipped — no directional strategy active")
        return

    strategy_proxy = {"compatible_regimes": compatible}
    regime_proxy = {"behavior": str(regime_code).strip().upper()}
    run_invariant(
        "check_strategy_regime_alignment",
        check_strategy_regime_alignment,
        strategy_proxy,
        regime_proxy,
    )


# ───────────────────────────────────────────────────────────────────────────
# L7 — Convergence Integrity
# ───────────────────────────────────────────────────────────────────────────
def gate_l7_convergence(candidate: Dict[str, Any]) -> None:
    """Hard gate after IntelligenceEngine.run_cycle() for each signal/candidate.

    Passes the candidate dict directly.  Signals without a ``conviction``
    field default to ``"WATCHLIST"`` which is exempt from the ≥3 lenses rule,
    so this gate is a no-op unless a caller explicitly marks conviction="HIGH".
    """
    cand = candidate or {}
    if "conviction" not in cand:
        cand = dict(cand, conviction="WATCHLIST")
    run_invariant("check_convergence_integrity", check_convergence_integrity, cand)


# ───────────────────────────────────────────────────────────────────────────
# L8 — Risk Caps
# ───────────────────────────────────────────────────────────────────────────
def gate_l8_risk_caps(total_exposure: float, max_exposure: float = 1.0) -> None:
    """Hard gate after check_capital_readiness().

    Maps total portfolio exposure (0.0–1.0 fraction) to the invariant's
    position_pct / max_position_pct contract.
    """
    run_invariant(
        "check_risk_caps",
        check_risk_caps,
        {"position_pct": float(total_exposure)},
        {"max_position_pct": float(max_exposure)},
    )


# ───────────────────────────────────────────────────────────────────────────
# L9 — Portfolio–Regime Conflict
# ───────────────────────────────────────────────────────────────────────────
def gate_l9_portfolio_regime(
    regime_conflict_detected: bool,
    flags: List[str],
    regime_behavior: str,
) -> None:
    """Hard gate for portfolio regime conflict consistency.

    Invariant: if a regime conflict is detected, ``"RegimeConflict"`` MUST
    appear in the flags list.  Missing the flag while a conflict exists is a
    catastrophic observability failure.
    """
    portfolio_proxy = {
        "regime_conflict_detected": bool(regime_conflict_detected),
        "flags": list(flags),
    }
    regime_proxy = {"behavior": str(regime_behavior).strip().upper()}
    run_invariant(
        "check_portfolio_regime_conflict",
        check_portfolio_regime_conflict,
        portfolio_proxy,
        regime_proxy,
    )
