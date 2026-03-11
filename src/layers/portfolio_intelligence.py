"""
Portfolio Intelligence Engine (L9) — Deterministic Structural Diagnostics
==========================================================================
L9 is a pure observer.  It:
  • Consumes upstream state snapshots (L1, L2, L3, L6, L7, L8)
  • Produces a PortfolioDiagnosticReport
  • Never mutates portfolio state
  • Never calls an LLM
  • Guarantees: identical inputs → identical report
  • Enforces latency guard < 1 000 ms
  • Raises INSUFFICIENT_CONTEXT on any missing required upstream

Diagnostic modules (in evaluation order):
  1  Regime Alignment Monitor
  2  Narrative Drift Detector
  3  Factor Alignment Drift
  4  Strategy Misapplication Detector
  5  Concentration Creep Monitor
  6  Exposure Symmetry Check
  7  Convergence Health Monitor
  8  Constraint Friction Analysis
  9  Drawdown Behaviour Intelligence
  10 Stability Drift Integration
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from src.models.portfolio_models import (
    ConstraintActivitySummary,
    ConvergenceSnapshot,
    DiagnosticFlag,
    FactorState,
    GlobalStatus,
    HoldingMeta,
    NarrativeLifecycle,
    NarrativeState,
    PortfolioDiagnosticReport,
    PortfolioSnapshot,
    RegimeState,
    SeverityLevel,
)

# ── Module-level constants ────────────────────────────────────────────────────
_LATENCY_LIMIT_MS = 1_000.0

# Regime alignment thresholds
_STRESS_LONG_EXPOSURE_RED = 0.50        # net long > 50% in STRESS → RED
_STRESS_LONG_EXPOSURE_ORANGE = 0.30     # net long > 30% in STRESS → ORANGE
_TRENDING_LOW_EXPOSURE_YELLOW = 0.20    # net long < 20% in TRENDING → YELLOW

# Strategy horizon max days
_HORIZON_MAX_DAYS: Dict[str, int] = {
    "SCALP": 3,
    "SWING": 20,
    "POSITIONAL": 90,
}

# Concentration thresholds (weight_pct, not fractional)
_CONC_TOP3_RED = 60.0
_CONC_TOP3_ORANGE = 45.0
_CONC_TOP5_YELLOW = 70.0

# Convergence decay thresholds (fraction of initial score lost)
_CONV_DECAY_ORANGE = 0.50
_CONV_DECAY_YELLOW = 0.30
_SYSTEMIC_DECAY_COUNT = 3               # ≥ this many decaying → RED systemic flag

# Stability score thresholds
_STABILITY_RED = 0.20
_STABILITY_ORANGE = 0.40
_STABILITY_YELLOW = 0.60

# Constraint friction thresholds
_FRICTION_ADJUSTED_ORANGE_RATIO = 0.50  # adjusted / total ≥ 0.5 → ORANGE
_FRICTION_ADJUSTED_YELLOW_RATIO = 0.25
_FRICTION_REJECTED_ORANGE_RATIO = 0.20

# Exposure asymmetry threshold
_SECTOR_ASYMMETRY_ORANGE = 0.70         # single sector > 70% of gross → ORANGE
_SECTOR_ASYMMETRY_YELLOW = 0.50

# Severity ordering for global status resolution
_SEVERITY_ORDER: Dict[str, int] = {
    "INFO": 0,
    "YELLOW": 1,
    "ORANGE": 2,
    "RED": 3,
    "CRITICAL": 4,
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def _compute_input_hash(
    portfolio: PortfolioSnapshot,
    regime: RegimeState,
    narrative: Optional[NarrativeState],
    factor: Optional[FactorState],
    convergence: Optional[ConvergenceSnapshot],
    constraint_activity: Optional[ConstraintActivitySummary],
) -> str:
    payload = {
        "portfolio": _safe_asdict(portfolio),
        "regime": _safe_asdict(regime),
        "narrative": _safe_asdict(narrative) if narrative else None,
        "factor": _safe_asdict(factor) if factor else None,
        "convergence": _safe_asdict(convergence) if convergence else None,
        "constraint_activity": _safe_asdict(constraint_activity) if constraint_activity else None,
    }
    raw = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _safe_asdict(obj) -> dict:
    """Recursively convert frozen dataclasses and tuples to dicts/lists."""
    if obj is None:
        return {}
    if hasattr(obj, "__dataclass_fields__"):
        return {k: _safe_asdict(getattr(obj, k)) for k in obj.__dataclass_fields__}
    if isinstance(obj, (list, tuple)):
        return [_safe_asdict(i) for i in obj]
    if isinstance(obj, dict):
        return {k: _safe_asdict(v) for k, v in obj.items()}
    return obj


def _dominant_severity(flags: List[DiagnosticFlag]) -> Optional[str]:
    if not flags:
        return None
    return max((f.severity for f in flags), key=lambda s: _SEVERITY_ORDER[s])


def _to_global_status(dominant: Optional[str]) -> GlobalStatus:
    if dominant is None:
        return "OK"
    mapping: Dict[str, GlobalStatus] = {
        "INFO": "OK",
        "YELLOW": "DEGRADED",
        "ORANGE": "DEGRADED",
        "RED": "CRITICAL",
        "CRITICAL": "CRITICAL",
    }
    return mapping[dominant]


# ── Diagnostic Modules ────────────────────────────────────────────────────────

class _RegimeAlignmentMonitor:
    """Module 1 — Regime vs net exposure."""

    MODULE = "REGIME_ALIGNMENT"

    def evaluate(
        self,
        portfolio: PortfolioSnapshot,
        regime: RegimeState,
    ) -> Tuple[List[DiagnosticFlag], float]:
        flags: List[DiagnosticFlag] = []
        net = portfolio.net_exposure_pct          # signed percent (e.g. 70 = 70% long)
        r = regime.regime

        if r == "STRESS":
            if net > _STRESS_LONG_EXPOSURE_RED * 100:
                flags.append(DiagnosticFlag(
                    code="REGIME_CONFLICT_STRESS_LONG",
                    module=self.MODULE,
                    severity="RED",
                    message=(
                        f"Fighting Regime: net long exposure {net:.1f}% is dangerously high "
                        f"in a STRESS regime (threshold {_STRESS_LONG_EXPOSURE_RED * 100:.0f}%). "
                        "Portfolio is long while regime signals severe risk-off."
                    ),
                ))
            elif net > _STRESS_LONG_EXPOSURE_ORANGE * 100:
                flags.append(DiagnosticFlag(
                    code="REGIME_TENSION_STRESS_LONG",
                    module=self.MODULE,
                    severity="ORANGE",
                    message=(
                        f"Regime Tension: net long {net:.1f}% is elevated versus STRESS regime "
                        f"(caution threshold {_STRESS_LONG_EXPOSURE_ORANGE * 100:.0f}%)."
                    ),
                ))

        elif r in ("TRENDING", "ACCUMULATION"):
            if 0 < net < _TRENDING_LOW_EXPOSURE_YELLOW * 100:
                flags.append(DiagnosticFlag(
                    code="UNDEREXPOSED_RISK_ON",
                    module=self.MODULE,
                    severity="YELLOW",
                    message=(
                        f"Underexposed in Risk-On: net long only {net:.1f}% while regime is "
                        f"{r}. Portfolio may be missing the prevailing trend."
                    ),
                ))

        # Score: fraction of net exposure that is appropriate for the regime.
        score = self._score(net, r)
        return flags, score

    def _score(self, net: float, regime: str) -> float:
        net_frac = net / 100.0
        if regime == "STRESS":
            # Ideal = fully short (net_frac = -1.0 → score 1.0; net_frac = +1.0 → score 0.0)
            return _clamp(1.0 - (net_frac + 1.0) / 2.0)
        if regime in ("TRENDING", "ACCUMULATION"):
            # Ideal = fully long
            return _clamp((net_frac + 1.0) / 2.0)
        # Neutral regimes — penalise extremes mildly
        return _clamp(1.0 - abs(net_frac) * 0.5)


class _NarrativeDriftDetector:
    """Module 2 — Narrative lifecycle vs active holdings."""

    MODULE = "NARRATIVE_DRIFT"

    _DECAY_SEVERITIES: Dict[NarrativeLifecycle, SeverityLevel] = {
        "RESOLVED": "ORANGE",
        "REVERSED": "RED",
        "FADING": "YELLOW",
    }

    def evaluate(
        self,
        portfolio: PortfolioSnapshot,
        narrative: NarrativeState,
    ) -> Tuple[List[DiagnosticFlag], float]:
        flags: List[DiagnosticFlag] = []
        symbols = {h.symbol for h in portfolio.holdings}
        total = len(symbols)
        decayed = 0

        for tag in narrative.tags:
            if tag.holding_symbol not in symbols:
                continue
            severity = self._DECAY_SEVERITIES.get(tag.lifecycle)
            if severity:
                decayed += 1
                flags.append(DiagnosticFlag(
                    code=f"NARRATIVE_{tag.lifecycle}_{tag.holding_symbol}",
                    module=self.MODULE,
                    severity=severity,
                    message=(
                        f"Narrative Decay on {tag.holding_symbol}: "
                        f"narrative '{tag.narrative_id}' lifecycle is {tag.lifecycle}. "
                        "The original thesis justifying this holding is no longer valid."
                    ),
                    affected_symbol=tag.holding_symbol,
                ))

        score = _clamp(1.0 - decayed / total) if total > 0 else 1.0
        return flags, score


class _FactorAlignmentDrift:
    """Module 3 — Dominant factor vs per-holding factor assignments."""

    MODULE = "FACTOR_ALIGNMENT"

    def evaluate(
        self,
        portfolio: PortfolioSnapshot,
        factor: FactorState,
    ) -> Tuple[List[DiagnosticFlag], float]:
        flags: List[DiagnosticFlag] = []
        total_weight = sum(h.weight_pct for h in portfolio.holdings)
        if total_weight == 0:
            return flags, 1.0

        aligned_weight = sum(
            h.weight_pct
            for h in portfolio.holdings
            if factor.holding_factors.get(h.symbol) == factor.dominant_factor
        )
        alignment = aligned_weight / total_weight

        if alignment < 0.40:
            flags.append(DiagnosticFlag(
                code="FACTOR_MISALIGNMENT_SEVERE",
                module=self.MODULE,
                severity="ORANGE",
                message=(
                    f"Factor Misalignment: only {alignment * 100:.1f}% of portfolio weight "
                    f"is aligned with dominant factor '{factor.dominant_factor}'. "
                    "Portfolio holdings are predominantly in a conflicting factor."
                ),
            ))
        elif alignment < 0.60:
            flags.append(DiagnosticFlag(
                code="FACTOR_MISALIGNMENT_MODERATE",
                module=self.MODULE,
                severity="YELLOW",
                message=(
                    f"Factor Drift: {alignment * 100:.1f}% of portfolio weight aligned with "
                    f"dominant factor '{factor.dominant_factor}'. "
                    "Alignment is below optimal (60%+ expected)."
                ),
            ))

        return flags, _clamp(alignment)


class _StrategyMisapplicationDetector:
    """Module 4 — Horizon violations and regime-strategy mismatches."""

    MODULE = "STRATEGY_MISAPPLICATION"

    _REGIME_COMPATIBLE_STRATEGIES: Dict[str, List[str]] = {
        "STRESS":       ["POSITIONAL"],
        "VOLATILE":     ["SWING", "POSITIONAL"],
        "CHOP":         ["SWING", "SCALP"],
        "TRENDING":     ["SCALP", "SWING", "POSITIONAL"],
        "TRANSITION":   ["SWING", "POSITIONAL"],
        "ACCUMULATION": ["SWING", "POSITIONAL"],
        "DISTRIBUTION": ["SWING", "POSITIONAL"],
    }

    def evaluate(
        self,
        portfolio: PortfolioSnapshot,
        regime: RegimeState,
    ) -> Tuple[List[DiagnosticFlag], float]:
        flags: List[DiagnosticFlag] = []
        total = len(portfolio.holdings)
        misapplied = 0

        for h in portfolio.holdings:
            max_days = _HORIZON_MAX_DAYS.get(h.strategy, 999)
            if h.days_held > max_days:
                misapplied += 1
                flags.append(DiagnosticFlag(
                    code=f"HORIZON_VIOLATION_{h.symbol}",
                    module=self.MODULE,
                    severity="ORANGE",
                    message=(
                        f"Horizon Violation on {h.symbol}: "
                        f"strategy '{h.strategy}' has been held {h.days_held} days "
                        f"(max allowed: {max_days}). "
                        "Position has outlived its intended time horizon."
                    ),
                    affected_symbol=h.symbol,
                ))
            else:
                allowed = self._REGIME_COMPATIBLE_STRATEGIES.get(regime.regime, [])
                if allowed and h.strategy not in allowed:
                    flags.append(DiagnosticFlag(
                        code=f"STRATEGY_REGIME_MISMATCH_{h.symbol}",
                        module=self.MODULE,
                        severity="YELLOW",
                        message=(
                            f"Strategy Mismatch on {h.symbol}: "
                            f"strategy '{h.strategy}' is not in the compatible set "
                            f"{allowed} for regime '{regime.regime}'."
                        ),
                        affected_symbol=h.symbol,
                    ))

        score = _clamp(1.0 - misapplied / total) if total > 0 else 1.0
        return flags, score


class _ConcentrationCreepMonitor:
    """Module 5 — Top-N weight and sector cap breaches."""

    MODULE = "CONCENTRATION_CREEP"

    def evaluate(
        self,
        portfolio: PortfolioSnapshot,
    ) -> Tuple[List[DiagnosticFlag], float]:
        flags: List[DiagnosticFlag] = []
        holdings = sorted(portfolio.holdings, key=lambda h: h.weight_pct, reverse=True)
        top3_weight = sum(h.weight_pct for h in holdings[:3])
        top5_weight = sum(h.weight_pct for h in holdings[:5])

        if top3_weight > _CONC_TOP3_RED:
            flags.append(DiagnosticFlag(
                code="CONCENTRATION_TOP3_RED",
                module=self.MODULE,
                severity="RED",
                message=(
                    f"Extreme Concentration: top-3 holdings represent {top3_weight:.1f}% of "
                    f"portfolio (threshold: {_CONC_TOP3_RED:.0f}%). "
                    "Idiosyncratic risk is dangerously elevated."
                ),
            ))
        elif top3_weight > _CONC_TOP3_ORANGE:
            flags.append(DiagnosticFlag(
                code="CONCENTRATION_TOP3_ORANGE",
                module=self.MODULE,
                severity="ORANGE",
                message=(
                    f"Concentration Creep: top-3 holdings at {top3_weight:.1f}% "
                    f"(threshold: {_CONC_TOP3_ORANGE:.0f}%). "
                    "Portfolio is becoming overly concentrated in its largest positions."
                ),
            ))

        if top5_weight > _CONC_TOP5_YELLOW and top3_weight <= _CONC_TOP3_ORANGE:
            flags.append(DiagnosticFlag(
                code="CONCENTRATION_TOP5_YELLOW",
                module=self.MODULE,
                severity="YELLOW",
                message=(
                    f"Mild Concentration: top-5 holdings at {top5_weight:.1f}% "
                    f"(threshold: {_CONC_TOP5_YELLOW:.0f}%)."
                ),
            ))

        # Sector cap checks
        sector_totals: Dict[str, float] = {}
        for h in portfolio.holdings:
            sector_totals[h.sector] = sector_totals.get(h.sector, 0.0) + h.weight_pct

        for sector, total_weight in sector_totals.items():
            cap = portfolio.sector_caps.get(sector)
            if cap is None:
                continue
            if total_weight > cap:
                flags.append(DiagnosticFlag(
                    code=f"SECTOR_CAP_BREACH_{sector.upper()}",
                    module=self.MODULE,
                    severity="RED",
                    message=(
                        f"Sector Cap Breach: {sector} exposure {total_weight:.1f}% exceeds "
                        f"cap of {cap:.1f}%. Constraint boundary violated."
                    ),
                ))
            elif total_weight > cap * 0.9:
                flags.append(DiagnosticFlag(
                    code=f"SECTOR_CAP_WARNING_{sector.upper()}",
                    module=self.MODULE,
                    severity="YELLOW",
                    message=(
                        f"Sector Cap Warning: {sector} exposure {total_weight:.1f}% is within "
                        f"10% of cap ({cap:.1f}%). Approaching limit."
                    ),
                ))

        # Score: linear penalty for top3 excess; 1.0 when top3 < 30%
        top3_frac = top3_weight / 100.0
        score = _clamp(1.0 - max(0.0, top3_frac - 0.30) / 0.70)
        return flags, score


class _ExposureSymmetryCheck:
    """Module 6 — Long/short imbalance and sector clustering."""

    MODULE = "EXPOSURE_SYMMETRY"

    def evaluate(
        self,
        portfolio: PortfolioSnapshot,
    ) -> Tuple[List[DiagnosticFlag], float]:
        flags: List[DiagnosticFlag] = []
        gross = portfolio.gross_exposure_pct
        if gross == 0:
            return flags, 1.0

        # Sector asymmetry
        sector_totals: Dict[str, float] = {}
        for h in portfolio.holdings:
            sector_totals[h.sector] = sector_totals.get(h.sector, 0.0) + h.weight_pct

        max_sector_weight = max(sector_totals.values(), default=0.0)
        sector_ratio = max_sector_weight / gross if gross > 0 else 0.0
        dominant_sector = max(sector_totals, key=sector_totals.get) if sector_totals else ""

        if sector_ratio > _SECTOR_ASYMMETRY_ORANGE:
            flags.append(DiagnosticFlag(
                code="SECTOR_CLUSTERING_ORANGE",
                module=self.MODULE,
                severity="ORANGE",
                message=(
                    f"Sector Clustering: '{dominant_sector}' represents "
                    f"{sector_ratio * 100:.1f}% of gross exposure "
                    f"(threshold: {_SECTOR_ASYMMETRY_ORANGE * 100:.0f}%). "
                    "Portfolio is dangerously concentrated in one sector."
                ),
            ))
        elif sector_ratio > _SECTOR_ASYMMETRY_YELLOW:
            flags.append(DiagnosticFlag(
                code="SECTOR_CLUSTERING_YELLOW",
                module=self.MODULE,
                severity="YELLOW",
                message=(
                    f"Sector Asymmetry: '{dominant_sector}' is {sector_ratio * 100:.1f}% "
                    f"of gross exposure (threshold: {_SECTOR_ASYMMETRY_YELLOW * 100:.0f}%)."
                ),
            ))

        # Net vs gross imbalance (high net/gross = very directional)
        net_abs = abs(portfolio.net_exposure_pct)
        imbalance = net_abs / gross if gross > 0 else 0.0
        if imbalance > 0.85:
            flags.append(DiagnosticFlag(
                code="DIRECTIONAL_ASYMMETRY",
                module=self.MODULE,
                severity="YELLOW",
                message=(
                    f"Directional Asymmetry: net/gross ratio is {imbalance:.2f}. "
                    "Portfolio is highly one-sided with minimal hedge offset."
                ),
            ))

        score = _clamp(1.0 - sector_ratio * 0.8)
        return flags, score


class _ConvergenceHealthMonitor:
    """Module 7 — Per-holding convergence decay detection."""

    MODULE = "CONVERGENCE_HEALTH"

    def evaluate(
        self,
        portfolio: PortfolioSnapshot,
        convergence: ConvergenceSnapshot,
    ) -> Tuple[List[DiagnosticFlag], float]:
        flags: List[DiagnosticFlag] = []
        decay_counts = {"severe": 0, "moderate": 0}
        ratio_sum = 0.0
        evaluated = 0

        for h in portfolio.holdings:
            entry = convergence.scores.get(h.symbol)
            if entry is None:
                continue
            initial, current = entry
            if initial <= 0:
                continue
            evaluated += 1
            ratio = current / initial
            ratio_sum += ratio
            decay = 1.0 - ratio

            if decay > _CONV_DECAY_ORANGE:
                decay_counts["severe"] += 1
                flags.append(DiagnosticFlag(
                    code=f"CONVERGENCE_DECAY_SEVERE_{h.symbol}",
                    module=self.MODULE,
                    severity="ORANGE",
                    message=(
                        f"Convergence Decay on {h.symbol}: score dropped from "
                        f"{initial:.2f} to {current:.2f} "
                        f"({decay * 100:.1f}% decay, threshold: {_CONV_DECAY_ORANGE * 100:.0f}%). "
                        "The signal confirming this thesis has substantially weakened."
                    ),
                    affected_symbol=h.symbol,
                ))
            elif decay > _CONV_DECAY_YELLOW:
                decay_counts["moderate"] += 1
                flags.append(DiagnosticFlag(
                    code=f"CONVERGENCE_DECAY_MODERATE_{h.symbol}",
                    module=self.MODULE,
                    severity="YELLOW",
                    message=(
                        f"Convergence Erosion on {h.symbol}: score dropped from "
                        f"{initial:.2f} to {current:.2f} "
                        f"({decay * 100:.1f}% decay, threshold: {_CONV_DECAY_YELLOW * 100:.0f}%)."
                    ),
                    affected_symbol=h.symbol,
                ))

        if decay_counts["severe"] >= _SYSTEMIC_DECAY_COUNT:
            flags.append(DiagnosticFlag(
                code="SYSTEMIC_CONVERGENCE_DECAY",
                module=self.MODULE,
                severity="RED",
                message=(
                    f"Systemic Convergence Decay: {decay_counts['severe']} holdings show "
                    f">50% convergence decay. This indicates a broad-based thesis breakdown, "
                    "not an isolated position issue."
                ),
            ))

        mean_ratio = ratio_sum / evaluated if evaluated > 0 else 1.0
        score = _clamp(mean_ratio)
        return flags, score


class _ConstraintFrictionAnalysis:
    """Module 8 — L8 adjustment/rejection pressure signal."""

    MODULE = "CONSTRAINT_FRICTION"

    def evaluate(
        self,
        activity: ConstraintActivitySummary,
    ) -> Tuple[List[DiagnosticFlag], float]:
        flags: List[DiagnosticFlag] = []
        total = activity.approved_count + activity.adjusted_count + activity.rejected_count
        if total == 0:
            return flags, 1.0

        adjusted_ratio = activity.adjusted_count / total
        rejected_ratio = activity.rejected_count / total

        if rejected_ratio >= _FRICTION_REJECTED_ORANGE_RATIO:
            flags.append(DiagnosticFlag(
                code="CONSTRAINT_FRICTION_REJECTIONS",
                module=self.MODULE,
                severity="ORANGE",
                message=(
                    f"High Constraint Friction: {activity.rejected_count}/{total} recent "
                    f"decisions ({rejected_ratio * 100:.1f}%) were rejected by L8. "
                    "System is persistently blocked by risk constraints."
                ),
            ))
        elif adjusted_ratio >= _FRICTION_ADJUSTED_ORANGE_RATIO:
            flags.append(DiagnosticFlag(
                code="CONSTRAINT_FRICTION_ADJUSTMENTS_HIGH",
                module=self.MODULE,
                severity="ORANGE",
                message=(
                    f"System Pressured by Constraints: {activity.adjusted_count}/{total} "
                    f"decisions ({adjusted_ratio * 100:.1f}%) required L8 adjustment. "
                    "Intended sizing is systematically overridden by constraint logic."
                ),
            ))
        elif adjusted_ratio >= _FRICTION_ADJUSTED_YELLOW_RATIO:
            flags.append(DiagnosticFlag(
                code="CONSTRAINT_FRICTION_ADJUSTMENTS_MILD",
                module=self.MODULE,
                severity="YELLOW",
                message=(
                    f"Mild Constraint Pressure: {adjusted_ratio * 100:.1f}% of decisions "
                    "adjusted by L8. Worth monitoring for constraint boundary proximity."
                ),
            ))

        pressure = adjusted_ratio + rejected_ratio
        score = _clamp(1.0 - pressure)
        return flags, score


class _DrawdownBehaviourIntelligence:
    """Module 9 — Drawdown trajectory vs regime alignment."""

    MODULE = "DRAWDOWN_BEHAVIOUR"

    _DRAWDOWN_RISING_THRESHOLD = 10.0   # drawdown > 10% is notable

    def evaluate(
        self,
        portfolio: PortfolioSnapshot,
        regime: RegimeState,
        regime_flags: List[DiagnosticFlag],
    ) -> Tuple[List[DiagnosticFlag], float]:
        flags: List[DiagnosticFlag] = []
        dd = portfolio.current_drawdown_pct

        if dd <= 0:
            return flags, 1.0

        regime_misaligned = any(
            f.module == "REGIME_ALIGNMENT" and f.severity in ("RED", "ORANGE")
            for f in regime_flags
        )

        if dd > self._DRAWDOWN_RISING_THRESHOLD and regime_misaligned:
            flags.append(DiagnosticFlag(
                code="DRAWDOWN_REGIME_MISALIGNMENT",
                module=self.MODULE,
                severity="RED",
                message=(
                    f"Drawdown + Regime Misalignment: portfolio drawdown is {dd:.1f}% "
                    "while simultaneously misaligned with regime. "
                    "Combined signal indicates elevated structural risk."
                ),
            ))
        elif dd > self._DRAWDOWN_RISING_THRESHOLD:
            flags.append(DiagnosticFlag(
                code="DRAWDOWN_RISING",
                module=self.MODULE,
                severity="ORANGE",
                message=(
                    f"Drawdown Alert: portfolio drawdown is {dd:.1f}% "
                    "while regime alignment is intact. Monitor for acceleration."
                ),
            ))

        score = _clamp(1.0 - dd / 100.0)
        return flags, score


class _StabilityDriftIntegration:
    """Module 10 — Regime stability score from L1 drift tracker."""

    MODULE = "STABILITY_DRIFT"

    def evaluate(
        self,
        regime: RegimeState,
    ) -> Tuple[List[DiagnosticFlag], float]:
        flags: List[DiagnosticFlag] = []
        s = regime.stability_score

        if s < _STABILITY_RED:
            flags.append(DiagnosticFlag(
                code="STABILITY_CRITICAL",
                module=self.MODULE,
                severity="RED",
                message=(
                    f"Stability Collapse: stability score is {s:.2f} "
                    f"(threshold: {_STABILITY_RED}). "
                    "Regime structural integrity is severely degraded."
                ),
            ))
        elif s < _STABILITY_ORANGE:
            flags.append(DiagnosticFlag(
                code="STABILITY_DEGRADED",
                module=self.MODULE,
                severity="ORANGE",
                message=(
                    f"Stability Degraded: stability score is {s:.2f} "
                    f"(threshold: {_STABILITY_ORANGE}). "
                    "Regime instability is elevating regime-based model risk."
                ),
            ))
        elif s < _STABILITY_YELLOW:
            flags.append(DiagnosticFlag(
                code="STABILITY_WARNING",
                module=self.MODULE,
                severity="YELLOW",
                message=(
                    f"Stability Warning: stability score is {s:.2f} "
                    f"(threshold: {_STABILITY_YELLOW}). "
                    "Early-stage regime drift detected."
                ),
            ))

        return flags, _clamp(s)


# ── Engine ────────────────────────────────────────────────────────────────────

class PortfolioIntelligenceEngine:
    """
    L9 Portfolio Intelligence Engine.

    Usage::

        engine = PortfolioIntelligenceEngine()
        report = engine.evaluate(
            portfolio=snapshot,
            regime=regime_state,
            narrative=narrative_state,
            factor=factor_state,
            convergence=convergence_snapshot,
            constraint_activity=activity_summary,
        )

    Guarantees:
      • No mutation of any input
      • No LLM calls
      • Identical inputs → identical report (determinism invariant)
      • Missing required inputs → INSUFFICIENT_CONTEXT report
      • Latency > 1 000 ms → LATENCY_VIOLATION report
    """

    def __init__(self) -> None:
        self._regime_monitor = _RegimeAlignmentMonitor()
        self._narrative_drift = _NarrativeDriftDetector()
        self._factor_drift = _FactorAlignmentDrift()
        self._strategy_misapp = _StrategyMisapplicationDetector()
        self._concentration = _ConcentrationCreepMonitor()
        self._exposure_sym = _ExposureSymmetryCheck()
        self._conv_health = _ConvergenceHealthMonitor()
        self._constraint_friction = _ConstraintFrictionAnalysis()
        self._drawdown_intel = _DrawdownBehaviourIntelligence()
        self._stability_drift = _StabilityDriftIntegration()

    # ── Public API ────────────────────────────────────────────────────────────

    def evaluate(
        self,
        portfolio: Optional[PortfolioSnapshot],
        regime: Optional[RegimeState],
        narrative: Optional[NarrativeState] = None,
        factor: Optional[FactorState] = None,
        convergence: Optional[ConvergenceSnapshot] = None,
        constraint_activity: Optional[ConstraintActivitySummary] = None,
    ) -> PortfolioDiagnosticReport:
        start = time.perf_counter()
        timestamp = datetime.now(timezone.utc).isoformat()

        # ── Required upstream guard ───────────────────────────────────────────
        if portfolio is None or regime is None:
            return self._insufficient_context(start, timestamp)

        input_hash = _compute_input_hash(
            portfolio, regime, narrative, factor, convergence, constraint_activity
        )

        # ── Run all diagnostic modules ────────────────────────────────────────
        all_flags: List[DiagnosticFlag] = []
        scores: Dict[str, float] = {}

        # 1. Regime alignment
        regime_flags, regime_score = self._regime_monitor.evaluate(portfolio, regime)
        all_flags.extend(regime_flags)
        scores["REGIME_ALIGNMENT"] = regime_score

        # 2. Narrative drift
        if narrative is not None:
            narr_flags, narr_score = self._narrative_drift.evaluate(portfolio, narrative)
            all_flags.extend(narr_flags)
            scores["NARRATIVE_DRIFT"] = narr_score
        else:
            scores["NARRATIVE_DRIFT"] = 1.0

        # 3. Factor alignment
        if factor is not None:
            factor_flags, factor_score = self._factor_drift.evaluate(portfolio, factor)
            all_flags.extend(factor_flags)
            scores["FACTOR_ALIGNMENT"] = factor_score
        else:
            scores["FACTOR_ALIGNMENT"] = 1.0

        # 4. Strategy misapplication
        strat_flags, strat_score = self._strategy_misapp.evaluate(portfolio, regime)
        all_flags.extend(strat_flags)
        scores["STRATEGY_MISAPPLICATION"] = strat_score

        # 5. Concentration creep
        conc_flags, conc_score = self._concentration.evaluate(portfolio)
        all_flags.extend(conc_flags)
        scores["CONCENTRATION_CREEP"] = conc_score

        # 6. Exposure symmetry
        exp_flags, exp_score = self._exposure_sym.evaluate(portfolio)
        all_flags.extend(exp_flags)
        scores["EXPOSURE_SYMMETRY"] = exp_score

        # 7. Convergence health
        if convergence is not None:
            conv_flags, conv_score = self._conv_health.evaluate(portfolio, convergence)
            all_flags.extend(conv_flags)
            scores["CONVERGENCE_HEALTH"] = conv_score
        else:
            scores["CONVERGENCE_HEALTH"] = 1.0

        # 8. Constraint friction
        if constraint_activity is not None:
            fric_flags, fric_score = self._constraint_friction.evaluate(constraint_activity)
            all_flags.extend(fric_flags)
            scores["CONSTRAINT_FRICTION"] = fric_score
        else:
            scores["CONSTRAINT_FRICTION"] = 1.0

        # 9. Drawdown behaviour (uses regime flags from module 1 for context)
        dd_flags, dd_score = self._drawdown_intel.evaluate(portfolio, regime, regime_flags)
        all_flags.extend(dd_flags)
        scores["DRAWDOWN_BEHAVIOUR"] = dd_score

        # 10. Stability drift
        stab_flags, stab_score = self._stability_drift.evaluate(regime)
        all_flags.extend(stab_flags)
        scores["STABILITY_DRIFT"] = stab_score

        # ── Latency guard ─────────────────────────────────────────────────────
        latency_ms = (time.perf_counter() - start) * 1_000.0
        if latency_ms >= _LATENCY_LIMIT_MS:
            return self._latency_violation(latency_ms, input_hash, timestamp)

        # ── Build output ──────────────────────────────────────────────────────
        dominant = _dominant_severity(all_flags)
        global_status = _to_global_status(dominant)
        severity_map = {f.code: f.severity for f in all_flags}
        flags_tuple = tuple(all_flags)

        return PortfolioDiagnosticReport(
            regime_alignment_score=scores["REGIME_ALIGNMENT"],
            narrative_alignment_score=scores["NARRATIVE_DRIFT"],
            factor_alignment_score=scores["FACTOR_ALIGNMENT"],
            strategy_alignment_score=scores["STRATEGY_MISAPPLICATION"],
            concentration_score=scores["CONCENTRATION_CREEP"],
            exposure_balance_score=scores["EXPOSURE_SYMMETRY"],
            convergence_health_score=scores["CONVERGENCE_HEALTH"],
            global_status=global_status,
            flags=flags_tuple,
            severity_map=severity_map,
            component_scores=scores,
            latency_ms=latency_ms,
            input_hash=input_hash,
            timestamp=timestamp,
        )

    # ── Fail-safe constructors ────────────────────────────────────────────────

    def _insufficient_context(
        self, start: float, timestamp: str
    ) -> PortfolioDiagnosticReport:
        latency_ms = (time.perf_counter() - start) * 1_000.0
        flag = DiagnosticFlag(
            code="INSUFFICIENT_CONTEXT",
            module="ENGINE",
            severity="CRITICAL",
            message="Missing required upstream state: portfolio or regime is None. "
                    "L9 cannot produce a valid diagnostic report without L1 regime and "
                    "portfolio snapshot.",
        )
        return PortfolioDiagnosticReport(
            regime_alignment_score=0.0,
            narrative_alignment_score=0.0,
            factor_alignment_score=0.0,
            strategy_alignment_score=0.0,
            concentration_score=0.0,
            exposure_balance_score=0.0,
            convergence_health_score=0.0,
            global_status="INSUFFICIENT_CONTEXT",
            flags=(flag,),
            severity_map={"INSUFFICIENT_CONTEXT": "CRITICAL"},
            component_scores={},
            latency_ms=latency_ms,
            input_hash="",
            timestamp=timestamp,
        )

    def _latency_violation(
        self, latency_ms: float, input_hash: str, timestamp: str
    ) -> PortfolioDiagnosticReport:
        flag = DiagnosticFlag(
            code="LATENCY_VIOLATION",
            module="ENGINE",
            severity="CRITICAL",
            message=f"Latency guard breached: {latency_ms:.1f}ms exceeded "
                    f"{_LATENCY_LIMIT_MS:.0f}ms limit. Report discarded to preserve "
                    "determinism guarantee.",
        )
        return PortfolioDiagnosticReport(
            regime_alignment_score=0.0,
            narrative_alignment_score=0.0,
            factor_alignment_score=0.0,
            strategy_alignment_score=0.0,
            concentration_score=0.0,
            exposure_balance_score=0.0,
            convergence_health_score=0.0,
            global_status="LATENCY_VIOLATION",
            flags=(flag,),
            severity_map={"LATENCY_VIOLATION": "CRITICAL"},
            component_scores={},
            latency_ms=latency_ms,
            input_hash=input_hash,
            timestamp=timestamp,
        )


# Dry-run subsystem blueprint for user-owned broker portfolios.
_PORTFOLIO_INTELLIGENCE_TRUTH_EPOCH = "TRUTH_EPOCH_2026-03-06_01"
_PORTFOLIO_INTELLIGENCE_MARKETS: Tuple[str, ...] = ("US", "INDIA")
_PORTFOLIO_INTELLIGENCE_AFFECTED_LAYERS: Tuple[str, ...] = (
    "RESEARCH",
    "MACRO",
    "FACTOR",
    "INTELLIGENCE",
    "EVOLUTION",
    "DASHBOARD",
)
_PORTFOLIO_INTELLIGENCE_INVARIANTS: Tuple[str, ...] = (
    "INV-NO-EXECUTION",
    "INV-NO-CAPITAL",
    "INV-NO-SELF-ACTIVATION",
    "INV-PROXY-CANONICAL",
    "INV-READ-ONLY-DASHBOARD",
)
_PORTFOLIO_INTELLIGENCE_OBLIGATIONS: Tuple[str, ...] = (
    "OBL-DATA-PROVENANCE-VISIBLE",
    "OBL-TRUTH-EPOCH-DISCLOSED",
    "OBL-REGIME-GATE-EXPLICIT",
    "OBL-MARKET-PARITY",
    "OBL-HONEST-STAGNATION",
)


@dataclass(frozen=True)
class PortfolioIntelligenceComponentSpec:
    """Read-only component contract for the broker portfolio subsystem."""

    name: str
    role: str
    inputs: Tuple[str, ...]
    outputs: Tuple[str, ...]
    provenance_fields: Tuple[str, ...]
    degraded_state: str


@dataclass(frozen=True)
class PortfolioIntelligenceIntegrationPoint:
    """Describes how the subsystem consumes existing TraderFund layers."""

    layer: str
    interface: str
    reads: Tuple[str, ...]
    writes_back: bool
    governance_note: str


@dataclass(frozen=True)
class PortfolioIntelligenceEndpointSpec:
    """Dashboard endpoint contract for the portfolio intelligence surface."""

    method: str
    path: str
    response_contract: str
    market_scoped: bool
    read_only: bool


@dataclass(frozen=True)
class PortfolioIntelligenceDashboardSpec:
    """Read-only dashboard surface for multi-market portfolio intelligence."""

    module_name: str
    panels: Tuple[str, ...]
    endpoints: Tuple[PortfolioIntelligenceEndpointSpec, ...]
    disclaimers: Tuple[str, ...]
    truth_epoch_visible: bool
    provenance_visible: bool


@dataclass(frozen=True)
class PortfolioIntelligenceBlueprint:
    """Deterministic dry-run blueprint for the user portfolio subsystem."""

    name: str
    intent: str
    truth_epoch: str
    frozen_epoch: bool
    data_mode: str
    execution_mode: str
    markets: Tuple[str, ...]
    affected_layers: Tuple[str, ...]
    invariants: Tuple[str, ...]
    obligations: Tuple[str, ...]
    components: Tuple[PortfolioIntelligenceComponentSpec, ...]
    integrations: Tuple[PortfolioIntelligenceIntegrationPoint, ...]
    dashboard: PortfolioIntelligenceDashboardSpec
    future_extensions: Tuple[str, ...]
    notes: Tuple[str, ...]
    blueprint_hash: str

    def as_dict(self) -> Dict[str, Any]:
        """Return a serializable representation for docs and inspection."""
        return asdict(self)


def _compute_blueprint_hash(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


class PortfolioIntelligenceDesignBridge:
    """
    Dry-run integration bridge for user-owned broker portfolios.

    This bridge does not ingest broker files, compute signals, or expose any
    execution behavior. It only publishes the governed subsystem shape so the
    architecture, dashboard, and future implementation tracks remain aligned
    with the existing L9 engine.
    """

    def build_blueprint(self) -> PortfolioIntelligenceBlueprint:
        components = (
            PortfolioIntelligenceComponentSpec(
                name="Portfolio Ingestion Engine",
                role="Read broker exports and canonicalize import metadata per portfolio.",
                inputs=("broker_export", "portfolio_registry", "market_scope"),
                outputs=("raw_holdings", "portfolio_metadata", "import_audit_record"),
                provenance_fields=("source_path", "broker", "imported_at", "checksum"),
                degraded_state="Reject import and surface provenance gap.",
            ),
            PortfolioIntelligenceComponentSpec(
                name="Holdings Normalization Engine",
                role="Map raw positions into a canonical holding schema with weights and taxonomy.",
                inputs=("raw_holdings", "ticker_mapping", "sector_taxonomy"),
                outputs=("normalized_holdings", "classification_flags"),
                provenance_fields=("symbol_source", "taxonomy_version", "normalization_timestamp"),
                degraded_state="Emit UNKNOWN fields and explicit normalization flags.",
            ),
            PortfolioIntelligenceComponentSpec(
                name="Market Data Enrichment Layer",
                role="Attach price, fundamentals, technicals, events, and freshness metadata.",
                inputs=("normalized_holdings", "canonical_market_data", "truth_epoch"),
                outputs=("enriched_holdings", "staleness_report"),
                provenance_fields=("price_source", "fundamental_source", "technical_source", "data_as_of"),
                degraded_state="Mark degraded confidence and preserve raw observations.",
            ),
            PortfolioIntelligenceComponentSpec(
                name="Intelligence Scoring Engine",
                role="Produce holding-level diagnostics across fundamental, technical, factor, and sentiment lenses.",
                inputs=("enriched_holdings", "macro_context", "factor_context", "research_context"),
                outputs=("holding_intelligence_cards", "risk_flags", "regime_compatibility"),
                provenance_fields=("score_inputs_hash", "model_version", "computed_at"),
                degraded_state="Suppress conviction uplift and emit insufficient-context flags.",
            ),
            PortfolioIntelligenceComponentSpec(
                name="Portfolio Analytics Engine",
                role="Aggregate diversification, risk, structure, performance, and strategic insights.",
                inputs=("holding_intelligence_cards", "portfolio_metadata", "evolution_feedback"),
                outputs=("portfolio_diagnostics", "strategic_insights", "resilience_score"),
                provenance_fields=("analysis_hash", "fx_source", "analysis_timestamp"),
                degraded_state="Return partial analytics with honest stagnation disclosure.",
            ),
            PortfolioIntelligenceComponentSpec(
                name="Dashboard Adapter",
                role="Expose governed portfolio intelligence through GET-only dashboard contracts.",
                inputs=("portfolio_diagnostics", "holding_intelligence_cards", "truth_epoch"),
                outputs=("overview_payload", "holdings_payload", "combined_market_payload"),
                provenance_fields=("trace", "truth_epoch", "data_as_of"),
                degraded_state="Return read-only degraded payloads with traceable reasons.",
            ),
        )

        integrations = (
            PortfolioIntelligenceIntegrationPoint(
                layer="RESEARCH",
                interface="Research snapshots and issuer metadata",
                reads=("coverage status", "sector or industry labels", "issuer fundamentals"),
                writes_back=False,
                governance_note="Read-only enrichment input for holding summaries.",
            ),
            PortfolioIntelligenceIntegrationPoint(
                layer="MACRO",
                interface="Macro and regime context",
                reads=("regime state", "regime confidence", "rate environment", "macro provenance"),
                writes_back=False,
                governance_note="Regime compatibility must be explicit on every portfolio output.",
            ),
            PortfolioIntelligenceIntegrationPoint(
                layer="FACTOR",
                interface="Factor exposure state",
                reads=("dominant factor", "per-symbol factor context", "permission state"),
                writes_back=False,
                governance_note="Factor context informs diagnostics only, never ranking or execution.",
            ),
            PortfolioIntelligenceIntegrationPoint(
                layer="INTELLIGENCE",
                interface="Canonical intelligence and fragility artifacts",
                reads=("decision policy", "fragility posture", "suppression state", "truth epoch"),
                writes_back=False,
                governance_note="Subsystem must inherit canonical provenance and stale-state disclosure.",
            ),
            PortfolioIntelligenceIntegrationPoint(
                layer="EVOLUTION",
                interface="Paper portfolio and evaluation feedback",
                reads=("strategy evaluation context", "portfolio feedback", "regime evaluation history"),
                writes_back=False,
                governance_note="Used for comparative diagnostics and not for user portfolio mutation.",
            ),
            PortfolioIntelligenceIntegrationPoint(
                layer="DASHBOARD",
                interface="FastAPI GET surfaces and frontend read models",
                reads=("viewer market scope", "selected portfolio id"),
                writes_back=False,
                governance_note="Adapter remains GET-only and read-only under dashboard governance.",
            ),
        )

        dashboard = PortfolioIntelligenceDashboardSpec(
            module_name="Portfolio Intelligence",
            panels=(
                "Portfolio overview",
                "Holdings intelligence",
                "Diversification visualization",
                "Risk monitor",
                "Opportunity and risk monitor",
                "Multi-market combined view",
            ),
            endpoints=(
                PortfolioIntelligenceEndpointSpec("GET", "/api/portfolio/overview/{market}", "PortfolioOverview", True, True),
                PortfolioIntelligenceEndpointSpec("GET", "/api/portfolio/holdings/{market}/{portfolio_id}", "HoldingsIntelligence", True, True),
                PortfolioIntelligenceEndpointSpec("GET", "/api/portfolio/diversification/{market}/{portfolio_id}", "DiversificationReport", True, True),
                PortfolioIntelligenceEndpointSpec("GET", "/api/portfolio/risk/{market}/{portfolio_id}", "RiskDiagnosticReport", True, True),
                PortfolioIntelligenceEndpointSpec("GET", "/api/portfolio/structure/{market}/{portfolio_id}", "StructureReport", True, True),
                PortfolioIntelligenceEndpointSpec("GET", "/api/portfolio/performance/{market}/{portfolio_id}", "PerformanceReport", True, True),
                PortfolioIntelligenceEndpointSpec("GET", "/api/portfolio/insights/{market}/{portfolio_id}", "StrategicInsightFeed", True, True),
                PortfolioIntelligenceEndpointSpec("GET", "/api/portfolio/resilience/{market}/{portfolio_id}", "PortfolioResilienceScore", True, True),
                PortfolioIntelligenceEndpointSpec("GET", "/api/portfolio/combined", "CombinedPortfolioView", False, True),
            ),
            disclaimers=(
                "Advisory only. No trading, sizing, or activation is permitted.",
                "Truth epoch, provenance, and staleness must remain visible.",
                "Degraded or missing inputs must remain visible as honest stagnation.",
            ),
            truth_epoch_visible=True,
            provenance_visible=True,
        )

        notes = (
            "This blueprint extends the existing L9 structural diagnostic engine to user-owned broker portfolios without replacing L9.",
            "US and INDIA share identical contracts, differing only in source adapters and canonical symbol or taxonomy mappings.",
            "Combined market views remain analytical and require explicit FX provenance.",
            "Regime gates cap confidence and surface degraded state when macro context is partial or stale.",
        )

        payload = {
            "name": "Portfolio Intelligence Subsystem",
            "intent": "Institutional-grade multi-market portfolio analysis",
            "truth_epoch": _PORTFOLIO_INTELLIGENCE_TRUTH_EPOCH,
            "frozen_epoch": True,
            "data_mode": "REAL_ONLY",
            "execution_mode": "DRY_RUN",
            "markets": _PORTFOLIO_INTELLIGENCE_MARKETS,
            "affected_layers": _PORTFOLIO_INTELLIGENCE_AFFECTED_LAYERS,
            "invariants": _PORTFOLIO_INTELLIGENCE_INVARIANTS,
            "obligations": _PORTFOLIO_INTELLIGENCE_OBLIGATIONS,
            "components": [asdict(component) for component in components],
            "integrations": [asdict(integration) for integration in integrations],
            "dashboard": asdict(dashboard),
            "future_extensions": (
                "crypto portfolios",
                "derivatives exposure",
                "options strategies",
                "cross-portfolio optimization",
                "institutional risk models",
            ),
            "notes": notes,
        }
        blueprint_hash = _compute_blueprint_hash(payload)
        return PortfolioIntelligenceBlueprint(
            name=payload["name"],
            intent=payload["intent"],
            truth_epoch=payload["truth_epoch"],
            frozen_epoch=payload["frozen_epoch"],
            data_mode=payload["data_mode"],
            execution_mode=payload["execution_mode"],
            markets=payload["markets"],
            affected_layers=payload["affected_layers"],
            invariants=payload["invariants"],
            obligations=payload["obligations"],
            components=components,
            integrations=integrations,
            dashboard=dashboard,
            future_extensions=payload["future_extensions"],
            notes=payload["notes"],
            blueprint_hash=blueprint_hash,
        )


def build_portfolio_intelligence_blueprint() -> PortfolioIntelligenceBlueprint:
    """Convenience constructor for documentation and dry-run integration checks."""

    return PortfolioIntelligenceDesignBridge().build_blueprint()
