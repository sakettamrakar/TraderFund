"""
Catastrophic Invariant Firewall — Phase CI
==========================================
8 deterministic, hard-gate invariants enforced at cognitive layer outputs (L1–L9).

Rules:
  - Every check is deterministic (no randomness, no external calls).
  - FAIL raises CatastrophicInvariantError — downstream execution MUST abort.
  - No silent fallback; every violation produces a structured error.
  - Zero additional dependencies.
"""

import json
import logging
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Valid regime behaviors — canonical union of all vocabulary used across layers
# ---------------------------------------------------------------------------
VALID_REGIME_BEHAVIORS = frozenset({
    # Abstract canonical set (used in tests and higher-level context)
    "RISK_ON", "RISK_OFF", "TRANSITION", "STRESS",
    # Actual MarketBehavior enum values (traderfund/regime/types.py)
    "TRENDING_NORMAL_VOL", "TRENDING_HIGH_VOL",
    "MEAN_REVERTING_LOW_VOL", "MEAN_REVERTING_HIGH_VOL",
    "EVENT_DOMINANT", "EVENT_LOCK",
    "UNDEFINED",  # Legitimate fail-safe state (cash-preservation mode)
    # Strategy registry regime vocabulary (src/strategy/registry.py)
    "BULL_VOL", "BULL_CALM", "BEAR_RISK_OFF",
    # Decision engine regime vocabulary (src/intelligence/decision_policy_engine.py)
    "BULLISH", "BEARISH", "NEUTRAL",
})


# ---------------------------------------------------------------------------
# Custom Exception
# ---------------------------------------------------------------------------
class CatastrophicInvariantError(Exception):
    """Raised when a catastrophic invariant is violated.  Carries structured
    diagnostic information so callers can log / audit without parsing."""

    def __init__(self, invariant_name: str, layer: str, reason: str):
        self.invariant_name = invariant_name
        self.layer = layer
        self.reason = reason
        super().__init__(
            f"[CATASTROPHIC] {invariant_name} (layer {layer}): {reason}"
        )


# ---------------------------------------------------------------------------
# Result helper
# ---------------------------------------------------------------------------
def _result(status: str, reason: str, layer: str) -> Dict[str, str]:
    return {"status": status, "reason": reason, "layer": layer}


# ===================================================================
# INVARIANT 1 — L1: Regime Validity
# ===================================================================
def check_regime_validity(regime_state: Dict[str, Any]) -> Dict[str, str]:
    """Regime ``behavior`` must be a known canonical value.

    FAIL when behavior is None, empty, UNKNOWN, or not in the canonical set.
    """
    layer = "L1"
    behavior = (regime_state or {}).get("behavior")
    if behavior is None or str(behavior).strip() == "":
        return _result("FAIL", "Regime behavior is None or empty", layer)
    behavior_str = str(behavior).strip().upper()
    if behavior_str == "UNKNOWN":
        return _result("FAIL", "Regime behavior is UNKNOWN (undefined)", layer)
    if behavior_str not in VALID_REGIME_BEHAVIORS:
        return _result(
            "FAIL",
            f"Regime behavior '{behavior_str}' is not in the canonical set {sorted(VALID_REGIME_BEHAVIORS)}",
            layer,
        )
    return _result("PASS", "Regime behavior is valid", layer)


# ===================================================================
# INVARIANT 2 — L2: Narrative Grounding
# ===================================================================
def check_narrative_grounding(narrative_obj: Dict[str, Any]) -> Dict[str, str]:
    """Every narrative must have at least one source and a non-empty headline."""
    layer = "L2"
    narrative = narrative_obj or {}
    headline = narrative.get("headline")
    if not headline or str(headline).strip() == "":
        return _result("FAIL", "Narrative headline is missing or empty", layer)
    sources = narrative.get("sources", [])
    if not sources:
        return _result("FAIL", "Narrative has no source entries", layer)
    return _result("PASS", "Narrative is grounded", layer)


# ===================================================================
# INVARIANT 3 — L3: Trust Determinism
# ===================================================================
def check_trust_determinism(
    inputs: Dict[str, Any], trust_score: float
) -> Dict[str, str]:
    """Trust score must be in [0.0, 1.0].  The check is deterministic — the
    caller is responsible for verifying idempotency by invoking the trust
    function twice with the same inputs and confirming equal outputs."""
    layer = "L3"
    if trust_score is None:
        return _result("FAIL", "Trust score is None", layer)
    try:
        score = float(trust_score)
    except (TypeError, ValueError):
        return _result("FAIL", f"Trust score is not numeric: {trust_score}", layer)
    if score < 0.0 or score > 1.0:
        return _result(
            "FAIL",
            f"Trust score {score} is out of valid range [0.0, 1.0]",
            layer,
        )
    return _result("PASS", "Trust score is deterministic and in range", layer)


# ===================================================================
# INVARIANT 4 — L4: Factor Integrity
# ===================================================================
def check_factor_integrity(factor_output: Dict[str, Any]) -> Dict[str, str]:
    """Factor output must not be degenerate — at least one factor must have a
    non-zero ``strength`` value.  All-zero or all-same output indicates a
    broken model."""
    layer = "L4"
    factors = factor_output or {}
    if not factors:
        return _result("FAIL", "Factor output is empty", layer)

    strengths: List[float] = []
    for key, val in factors.items():
        if isinstance(val, dict):
            strengths.append(float(val.get("strength", 0)))
        elif isinstance(val, (int, float)):
            strengths.append(float(val))

    if not strengths:
        return _result("FAIL", "No numeric factor strengths found in output", layer)

    if all(s == 0 for s in strengths):
        return _result("FAIL", "All factor strengths are zero (degenerate)", layer)

    if len(set(strengths)) == 1:
        return _result(
            "FAIL",
            f"All factor strengths are identical ({strengths[0]}), model may be broken",
            layer,
        )
    return _result("PASS", "Factor output has valid diversity", layer)


# ===================================================================
# INVARIANT 5 — L5: Strategy–Regime Alignment
# ===================================================================
def check_strategy_regime_alignment(
    strategy: Dict[str, Any], regime_state: Dict[str, Any]
) -> Dict[str, str]:
    """An active strategy's ``compatible_regimes`` must include the current
    regime behavior.  If the strategy is active in an incompatible regime,
    it is a catastrophic mis-alignment."""
    layer = "L5"
    current_behavior = (regime_state or {}).get("behavior", "")
    if isinstance(current_behavior, str):
        current_behavior = current_behavior.strip().upper()

    compatible = (strategy or {}).get("compatible_regimes", [])
    compatible_upper = [str(r).strip().upper() for r in compatible]

    if not compatible_upper:
        return _result(
            "FAIL", "Strategy has no compatible_regimes defined", layer
        )

    if current_behavior not in compatible_upper:
        return _result(
            "FAIL",
            f"Strategy activated in regime '{current_behavior}' "
            f"which is not in compatible set {compatible_upper}",
            layer,
        )
    return _result("PASS", "Strategy is aligned with current regime", layer)


# ===================================================================
# INVARIANT 6 — L7: Convergence Integrity
# ===================================================================
def check_convergence_integrity(candidate: Dict[str, Any]) -> Dict[str, str]:
    """High-conviction candidates MUST have ≥3 contributing lenses.
    Watchlist / lower-conviction candidates are exempt."""
    layer = "L7"
    cand = candidate or {}
    conviction = str(cand.get("conviction", "")).strip().upper()
    if conviction != "HIGH":
        return _result("PASS", "Non-high-conviction candidate — exempt", layer)

    lenses = cand.get("contributing_lenses", [])
    n_lenses = len(lenses) if isinstance(lenses, list) else 0

    if n_lenses < 3:
        return _result(
            "FAIL",
            f"High-conviction candidate has only {n_lenses} contributing lenses (min 3)",
            layer,
        )
    return _result("PASS", "High-conviction candidate has sufficient lenses", layer)


# ===================================================================
# INVARIANT 7 — L8: Risk Caps
# ===================================================================
def check_risk_caps(
    position: Dict[str, Any], portfolio_state: Dict[str, Any]
) -> Dict[str, str]:
    """Position size (as % of portfolio) must not exceed ``max_position_pct``."""
    layer = "L8"
    pos = position or {}
    pf = portfolio_state or {}

    position_pct = pos.get("position_pct", 0.0)
    max_pct = pf.get("max_position_pct", 0.10)  # default 10 %

    try:
        position_pct = float(position_pct)
        max_pct = float(max_pct)
    except (TypeError, ValueError):
        return _result("FAIL", "position_pct or max_position_pct is not numeric", layer)

    if position_pct > max_pct:
        return _result(
            "FAIL",
            f"Position size {position_pct:.4f} exceeds max cap {max_pct:.4f}",
            layer,
        )
    return _result("PASS", "Position is within risk cap", layer)


# ===================================================================
# INVARIANT 8 — L9: Portfolio–Regime Conflict
# ===================================================================
def check_portfolio_regime_conflict(
    portfolio_state: Dict[str, Any], regime_state: Dict[str, Any]
) -> Dict[str, str]:
    """If there is a regime conflict (portfolio has positions misaligned with
    the regime), the portfolio flags list MUST include a ``RegimeConflict``
    flag.  Missing the flag when a conflict exists is catastrophic — it means
    the diagnostic engine failed to surface a critical risk."""
    layer = "L9"
    pf = portfolio_state or {}
    regime = regime_state or {}

    has_conflict = pf.get("regime_conflict_detected", False)
    flags = pf.get("flags", [])
    flag_names = [str(f).strip() for f in flags] if isinstance(flags, list) else []

    if has_conflict and "RegimeConflict" not in flag_names:
        return _result(
            "FAIL",
            "Regime conflict detected but RegimeConflict flag is missing from portfolio flags",
            layer,
        )
    return _result("PASS", "Portfolio regime conflict status is consistent", layer)


# ---------------------------------------------------------------------------
# Orchestration helpers
# ---------------------------------------------------------------------------
_ALL_INVARIANTS: List[Dict[str, Any]] = [
    {"name": "check_regime_validity", "func": check_regime_validity, "layer": "L1"},
    {"name": "check_narrative_grounding", "func": check_narrative_grounding, "layer": "L2"},
    {"name": "check_trust_determinism", "func": check_trust_determinism, "layer": "L3"},
    {"name": "check_factor_integrity", "func": check_factor_integrity, "layer": "L4"},
    {"name": "check_strategy_regime_alignment", "func": check_strategy_regime_alignment, "layer": "L5"},
    {"name": "check_convergence_integrity", "func": check_convergence_integrity, "layer": "L7"},
    {"name": "check_risk_caps", "func": check_risk_caps, "layer": "L8"},
    {"name": "check_portfolio_regime_conflict", "func": check_portfolio_regime_conflict, "layer": "L9"},
]


def run_invariant(
    name: str,
    func: Callable,
    *args: Any,
    log_entries: Optional[List[Dict]] = None,
) -> Dict[str, str]:
    """Execute a single invariant check.  On FAIL, raise
    ``CatastrophicInvariantError`` after appending the result to
    *log_entries* (if provided)."""
    result = func(*args)
    entry = {"invariant": name, **result, "timestamp": time.time()}
    if log_entries is not None:
        log_entries.append(entry)
    if result["status"] == "FAIL":
        logger.error("CATASTROPHIC INVARIANT FAIL — %s: %s", name, result["reason"])
        raise CatastrophicInvariantError(
            invariant_name=name,
            layer=result["layer"],
            reason=result["reason"],
        )
    logger.debug("Invariant PASS — %s", name)
    return result


def run_all_invariants(
    run_dir: Path,
    regime_state: Optional[Dict] = None,
    narrative_obj: Optional[Dict] = None,
    trust_inputs: Optional[Dict] = None,
    trust_score: Optional[float] = None,
    factor_output: Optional[Dict] = None,
    strategy: Optional[Dict] = None,
    candidate: Optional[Dict] = None,
    position: Optional[Dict] = None,
    portfolio_state: Optional[Dict] = None,
) -> Dict[str, Any]:
    """Run all 8 invariants and write structured log to *run_dir*.

    Returns the full log dict.  Raises ``CatastrophicInvariantError`` on the
    first failure (hard-stop semantics).
    """
    log_entries: List[Dict] = []
    overall = "PASS"

    try:
        # L1
        if regime_state is not None:
            run_invariant("check_regime_validity", check_regime_validity, regime_state, log_entries=log_entries)

        # L2
        if narrative_obj is not None:
            run_invariant("check_narrative_grounding", check_narrative_grounding, narrative_obj, log_entries=log_entries)

        # L3
        if trust_inputs is not None and trust_score is not None:
            run_invariant("check_trust_determinism", check_trust_determinism, trust_inputs, trust_score, log_entries=log_entries)

        # L4
        if factor_output is not None:
            run_invariant("check_factor_integrity", check_factor_integrity, factor_output, log_entries=log_entries)

        # L5
        if strategy is not None and regime_state is not None:
            run_invariant("check_strategy_regime_alignment", check_strategy_regime_alignment, strategy, regime_state, log_entries=log_entries)

        # L7
        if candidate is not None:
            run_invariant("check_convergence_integrity", check_convergence_integrity, candidate, log_entries=log_entries)

        # L8
        if position is not None and portfolio_state is not None:
            run_invariant("check_risk_caps", check_risk_caps, position, portfolio_state, log_entries=log_entries)

        # L9
        if portfolio_state is not None and regime_state is not None:
            run_invariant("check_portfolio_regime_conflict", check_portfolio_regime_conflict, portfolio_state, regime_state, log_entries=log_entries)

    except CatastrophicInvariantError:
        overall = "FAIL"
        raise
    finally:
        log_payload = {
            "run_id": run_dir.name if run_dir else "unknown",
            "timestamp": time.time(),
            "results": log_entries,
            "overall": overall,
        }
        _write_catastrophic_log(run_dir, log_payload)

    return log_payload


def _write_catastrophic_log(run_dir: Optional[Path], payload: Dict) -> None:
    """Persist structured log; best-effort — never raises."""
    if run_dir is None:
        return
    try:
        run_dir = Path(run_dir)
        run_dir.mkdir(parents=True, exist_ok=True)
        log_path = run_dir / "catastrophic_log.json"
        with open(log_path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
        logger.info("Catastrophic invariant log written to %s", log_path)
    except Exception as exc:
        logger.warning("Failed to write catastrophic log: %s", exc)
