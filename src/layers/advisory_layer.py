"""
Advisory Layer (L10) — Deterministic Institutional Suggestions
===============================================================
L10 consumes the L9 PortfolioDiagnosticReport and upstream state context,
and produces a structured AdvisoryReport of non-binding, non-executing
suggestions.

Hierarchy:
    L9  → Diagnose  (flags structural problems)
    L10 → Suggest   (translates flags into institutional commentary)
    L8  → Enforce   (acts — L10 never reaches here)

Guarantees:
  • No trade execution, no position mutation, no L8 limit override
  • No LLM calls — all text is deterministic template-driven prose
  • Identical inputs → identical AdvisoryReport
  • INSUFFICIENT_DIAGNOSTIC_CONTEXT on missing L9 report
  • Latency guard < 1 000 ms

Advisory modules (in evaluation order):
  1  Regime Advisory
  2  Narrative Advisory
  3  Factor Realignment Advisory
  4  Concentration Advisory
  5  Strategy Misuse Advisory
  6  Convergence Decay Advisory
  7  Stability Escalation Advisory
  8  Drawdown Advisory
  9  Constraint Friction Advisory
  10 Exposure Symmetry Advisory
"""
from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from src.models.portfolio_models import (
    DiagnosticFlag,
    PortfolioDiagnosticReport,
    SeverityLevel,
)
from src.models.advisory_models import (
    AdvisoryCategory,
    AdvisoryReport,
    AdvisorySeverity,
    AdvisorySuggestion,
    SystemRiskLevel,
)

# ── Constants ─────────────────────────────────────────────────────────────────

_LATENCY_LIMIT_MS = 1_000.0

# Confidence penalty weights
_PENALTY_PER_RED = 0.10
_PENALTY_PER_ORANGE = 0.05
_PENALTY_PER_YELLOW = 0.02

# System risk level thresholds (based on highest L9 severity + stability)
_STABILITY_SYSTEMIC = 0.20
_STABILITY_HIGH = 0.40
_STABILITY_ELEVATED = 0.60

# Severity ordering (shared with L9 vocabulary)
_SEVERITY_ORDER: Dict[str, int] = {
    "INFO": 0,
    "YELLOW": 1,
    "ORANGE": 2,
    "RED": 3,
    "CRITICAL": 4,
}

# Advisory modules that map to each suggestion bucket
_PORTFOLIO_MODULES = {
    "REGIME_ALIGNMENT",
    "FACTOR_ALIGNMENT",
    "CONCENTRATION_CREEP",
    "EXPOSURE_SYMMETRY",
}
_POSITION_MODULES = {
    "NARRATIVE_DRIFT",
    "STRATEGY_MISAPPLICATION",
    "CONVERGENCE_HEALTH",
}
_RISK_MODULES = {
    "DRAWDOWN_BEHAVIOUR",
    "STABILITY_DRIFT",
    "CONSTRAINT_FRICTION",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def _l9_severity_to_advisory(s: SeverityLevel) -> AdvisorySeverity:
    # 1-to-1 mapping; vocabulary is identical
    return s  # type: ignore[return-value]


def _dominant_severity(flags: Tuple[DiagnosticFlag, ...]) -> Optional[str]:
    if not flags:
        return None
    return max((f.severity for f in flags), key=lambda s: _SEVERITY_ORDER[s])


def _compute_input_hash(report: PortfolioDiagnosticReport, stability_score: float) -> str:
    payload = {
        "l9_input_hash": report.input_hash,
        "l9_global_status": report.global_status,
        "stability_score": round(stability_score, 8),
    }
    raw = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _flags_by_module(
    flags: Tuple[DiagnosticFlag, ...], module: str
) -> List[DiagnosticFlag]:
    return [f for f in flags if f.module == module]


def _flags_with_prefix(
    flags: Tuple[DiagnosticFlag, ...], prefix: str
) -> List[DiagnosticFlag]:
    return [f for f in flags if f.code.startswith(prefix)]


# ── Advisory modules ──────────────────────────────────────────────────────────

class _RegimeAdvisory:
    CATEGORY: AdvisoryCategory = "REGIME_ADVISORY"

    def generate(
        self, flags: Tuple[DiagnosticFlag, ...], regime_score: float
    ) -> List[AdvisorySuggestion]:
        suggestions: List[AdvisorySuggestion] = []

        for flag in _flags_by_module(flags, "REGIME_ALIGNMENT"):
            if flag.code == "REGIME_CONFLICT_STRESS_LONG":
                suggestions.append(AdvisorySuggestion(
                    category=self.CATEGORY,
                    severity="RED",
                    rationale=(
                        f"Portfolio holds elevated net long exposure during STRESS regime. "
                        f"Regime alignment score is {regime_score:.2f}. "
                        "Structural conflict between directional bias and prevailing regime increases tail risk."
                    ),
                    suggested_action=(
                        "Consider recalibrating gross exposure toward the 40–50% range. "
                        "Defensive reallocation may improve portfolio alignment with prevailing regime conditions."
                    ),
                    confidence=_clamp(1.0 - regime_score),
                    linked_flag=flag.code,
                ))
            elif flag.code == "REGIME_TENSION_STRESS_LONG":
                suggestions.append(AdvisorySuggestion(
                    category=self.CATEGORY,
                    severity="ORANGE",
                    rationale=(
                        "Net long exposure is in tension with a STRESS regime. "
                        "Alignment is degraded but not yet critical."
                    ),
                    suggested_action=(
                        "Monitor net long positioning closely. "
                        "Incremental reduction of gross exposure toward more neutral levels "
                        "may reduce regime conflict risk."
                    ),
                    confidence=_clamp(0.8 - regime_score * 0.3),
                    linked_flag=flag.code,
                ))
            elif flag.code == "UNDEREXPOSED_RISK_ON":
                suggestions.append(AdvisorySuggestion(
                    category=self.CATEGORY,
                    severity="YELLOW",
                    rationale=(
                        "Portfolio net long exposure is below optimal for a Risk-On regime. "
                        "Underdeployment of capital in a trending environment may result in "
                        "underperformance relative to the regime opportunity set."
                    ),
                    suggested_action=(
                        "Review whether current exposure levels reflect deliberate defensiveness "
                        "or structural underdeployment. Incremental exposure increase may be warranted."
                    ),
                    confidence=_clamp(regime_score * 0.7),
                    linked_flag=flag.code,
                ))
        return suggestions


class _NarrativeAdvisory:
    CATEGORY: AdvisoryCategory = "NARRATIVE_ADVISORY"

    _SEVERITY_ACTION: Dict[str, Tuple[str, str]] = {
        "NARRATIVE_RESOLVED": (
            "ORANGE",
            "The original narrative catalyst for this position has been exhausted. "
            "Review thesis continuation; holding may be operating on residual momentum "
            "rather than a live investable thesis.",
        ),
        "NARRATIVE_REVERSED": (
            "RED",
            "The narrative underpinning this position has reversed direction. "
            "This represents a direct contradiction of the original thesis. "
            "Structural reassessment of the holding's continued presence is warranted.",
        ),
        "NARRATIVE_FADING": (
            "YELLOW",
            "The narrative supporting this position is weakening. "
            "Monitor for further lifecycle deterioration before it reaches exhaustion.",
        ),
    }

    def generate(
        self, flags: Tuple[DiagnosticFlag, ...]
    ) -> List[AdvisorySuggestion]:
        suggestions: List[AdvisorySuggestion] = []
        for flag in _flags_by_module(flags, "NARRATIVE_DRIFT"):
            for prefix, (sev, action) in self._SEVERITY_ACTION.items():
                if flag.code.startswith(prefix):
                    sym = flag.affected_symbol or ""
                    suggestions.append(AdvisorySuggestion(
                        category=self.CATEGORY,
                        severity=sev,  # type: ignore[arg-type]
                        rationale=flag.message,
                        suggested_action=action,
                        confidence=_clamp(
                            0.90 if sev == "RED" else (0.75 if sev == "ORANGE" else 0.55)
                        ),
                        linked_flag=flag.code,
                        affected_symbol=flag.affected_symbol,
                    ))
                    break
        return suggestions


class _FactorRealignmentAdvisory:
    CATEGORY: AdvisoryCategory = "FACTOR_REALIGNMENT"

    def generate(
        self, flags: Tuple[DiagnosticFlag, ...], factor_score: float
    ) -> List[AdvisorySuggestion]:
        suggestions: List[AdvisorySuggestion] = []
        for flag in _flags_by_module(flags, "FACTOR_ALIGNMENT"):
            sev = _l9_severity_to_advisory(flag.severity)
            suggestions.append(AdvisorySuggestion(
                category=self.CATEGORY,
                severity=sev,
                rationale=flag.message,
                suggested_action=(
                    "Portfolio appears underexposed to the prevailing dominant factor. "
                    "Incremental reallocation toward holdings aligned with the dominant factor "
                    "may improve factor-regime coherence over time."
                ),
                confidence=_clamp(1.0 - factor_score),
                linked_flag=flag.code,
            ))
        return suggestions


class _ConcentrationAdvisory:
    CATEGORY: AdvisoryCategory = "CONCENTRATION_ADVISORY"

    def generate(
        self, flags: Tuple[DiagnosticFlag, ...], concentration_score: float
    ) -> List[AdvisorySuggestion]:
        suggestions: List[AdvisorySuggestion] = []
        for flag in _flags_by_module(flags, "CONCENTRATION_CREEP"):
            sev = _l9_severity_to_advisory(flag.severity)
            if flag.severity in ("RED", "ORANGE"):
                action = (
                    "Concentration risk is elevated across the top holdings. "
                    "Structural diversification across additional names or sectors "
                    "would reduce idiosyncratic risk exposure."
                )
            else:
                action = (
                    "Mild concentration noted. "
                    "Monitoring breadth of position distribution is advised."
                )
            suggestions.append(AdvisorySuggestion(
                category=self.CATEGORY,
                severity=sev,
                rationale=flag.message,
                suggested_action=action,
                confidence=_clamp(1.0 - concentration_score),
                linked_flag=flag.code,
            ))
        return suggestions


class _StrategyMisuseAdvisory:
    CATEGORY: AdvisoryCategory = "STRATEGY_MISUSE"

    def generate(
        self, flags: Tuple[DiagnosticFlag, ...]
    ) -> List[AdvisorySuggestion]:
        suggestions: List[AdvisorySuggestion] = []
        for flag in _flags_by_module(flags, "STRATEGY_MISAPPLICATION"):
            sev = _l9_severity_to_advisory(flag.severity)
            if flag.code.startswith("HORIZON_VIOLATION"):
                action = (
                    "Strategy time horizon has been exceeded. "
                    "Reassess whether this position should be reclassified under a longer-horizon "
                    "strategy or whether an exit pathway should be considered."
                )
            else:
                action = (
                    "The assigned strategy may not be optimal for the current regime. "
                    "Reviewing strategy classification against prevailing conditions "
                    "may reduce misapplication risk."
                )
            suggestions.append(AdvisorySuggestion(
                category=self.CATEGORY,
                severity=sev,
                rationale=flag.message,
                suggested_action=action,
                confidence=0.80 if sev == "ORANGE" else 0.60,
                linked_flag=flag.code,
                affected_symbol=flag.affected_symbol,
            ))
        return suggestions


class _ConvergenceDecayAdvisory:
    CATEGORY: AdvisoryCategory = "CONVERGENCE_DECAY"

    def generate(
        self, flags: Tuple[DiagnosticFlag, ...], convergence_score: float
    ) -> List[AdvisorySuggestion]:
        suggestions: List[AdvisorySuggestion] = []
        for flag in _flags_by_module(flags, "CONVERGENCE_HEALTH"):
            sev = _l9_severity_to_advisory(flag.severity)
            if flag.code == "SYSTEMIC_CONVERGENCE_DECAY":
                action = (
                    "Multi-holding convergence deterioration indicates a broad-based weakening "
                    "of the original signal set. Portfolio-level conviction recalibration is advised. "
                    "Consider whether aggregate sizing reflects current evidence quality."
                )
            elif flag.severity == "ORANGE":
                action = (
                    "The original multi-lens confirmation for this position has substantially weakened. "
                    "Conviction recalibration is advised before increasing or maintaining "
                    "current position sizing."
                )
            else:
                action = (
                    "Early-stage convergence erosion detected. "
                    "Monitor for further deterioration before committing additional capital."
                )
            suggestions.append(AdvisorySuggestion(
                category=self.CATEGORY,
                severity=sev,
                rationale=flag.message,
                suggested_action=action,
                confidence=_clamp(1.0 - convergence_score),
                linked_flag=flag.code,
                affected_symbol=flag.affected_symbol,
            ))
        return suggestions


class _StabilityEscalationAdvisory:
    CATEGORY: AdvisoryCategory = "STABILITY_ESCALATION"

    def generate(
        self, flags: Tuple[DiagnosticFlag, ...], stability_score: float
    ) -> List[AdvisorySuggestion]:
        suggestions: List[AdvisorySuggestion] = []
        for flag in _flags_by_module(flags, "STABILITY_DRIFT"):
            sev = _l9_severity_to_advisory(flag.severity)
            if flag.severity == "RED":
                action = (
                    "Regime stability has collapsed to a critical level. "
                    "Aggressive position sizing is structurally inadvisable in this environment. "
                    "Consider temporarily reducing sizing aggressiveness until stability recovers."
                )
            elif flag.severity == "ORANGE":
                action = (
                    "Component instability is rising materially. "
                    "Position sizing aggressiveness should be moderated. "
                    "Defensive allocation posture is appropriate until stability improves."
                )
            else:
                action = (
                    "Early stability drift detected. "
                    "Monitor regime stability trajectory before increasing risk exposure."
                )
            suggestions.append(AdvisorySuggestion(
                category=self.CATEGORY,
                severity=sev,
                rationale=flag.message,
                suggested_action=action,
                confidence=_clamp(1.0 - stability_score),
                linked_flag=flag.code,
            ))
        return suggestions


class _DrawdownAdvisory:
    CATEGORY: AdvisoryCategory = "DRAWDOWN_ADVISORY"

    def generate(
        self, flags: Tuple[DiagnosticFlag, ...]
    ) -> List[AdvisorySuggestion]:
        suggestions: List[AdvisorySuggestion] = []
        for flag in _flags_by_module(flags, "DRAWDOWN_BEHAVIOUR"):
            sev = _l9_severity_to_advisory(flag.severity)
            if flag.code == "DRAWDOWN_REGIME_MISALIGNMENT":
                action = (
                    "Drawdown is occurring in the context of regime misalignment, "
                    "suggesting the loss may reflect structural rather than incidental causes. "
                    "Structural repositioning toward regime-consistent allocation may be required "
                    "before the drawdown trajectory reverses."
                )
            else:
                action = (
                    "Portfolio is experiencing a drawdown within an intact regime context. "
                    "Monitor drawdown trajectory relative to regime continuation. "
                    "If regime deteriorates, escalation to structural review is warranted."
                )
            suggestions.append(AdvisorySuggestion(
                category=self.CATEGORY,
                severity=sev,
                rationale=flag.message,
                suggested_action=action,
                confidence=0.85 if sev == "RED" else 0.70,
                linked_flag=flag.code,
            ))
        return suggestions


class _ConstraintFrictionAdvisory:
    CATEGORY: AdvisoryCategory = "CONSTRAINT_FRICTION"

    def generate(
        self, flags: Tuple[DiagnosticFlag, ...]
    ) -> List[AdvisorySuggestion]:
        suggestions: List[AdvisorySuggestion] = []
        for flag in _flags_by_module(flags, "CONSTRAINT_FRICTION"):
            sev = _l9_severity_to_advisory(flag.severity)
            suggestions.append(AdvisorySuggestion(
                category=self.CATEGORY,
                severity=sev,
                rationale=flag.message,
                suggested_action=(
                    "The constraint layer is frequently overriding intended sizing, "
                    "indicating that the portfolio's intended risk posture exceeds "
                    "current constraint boundaries. "
                    "Review whether intended sizing is calibrated appropriately to "
                    "current risk limits, or whether constraint parameters require reassessment."
                ),
                confidence=0.75,
                linked_flag=flag.code,
            ))
        return suggestions


class _ExposureSymmetryAdvisory:
    CATEGORY: AdvisoryCategory = "EXPOSURE_SYMMETRY"

    def generate(
        self, flags: Tuple[DiagnosticFlag, ...], exposure_score: float
    ) -> List[AdvisorySuggestion]:
        suggestions: List[AdvisorySuggestion] = []
        for flag in _flags_by_module(flags, "EXPOSURE_SYMMETRY"):
            sev = _l9_severity_to_advisory(flag.severity)
            suggestions.append(AdvisorySuggestion(
                category=self.CATEGORY,
                severity=sev,
                rationale=flag.message,
                suggested_action=(
                    "Sector or directional clustering has been detected. "
                    "Broadening exposure across additional sectors or reducing "
                    "concentration in the dominant cluster would improve portfolio symmetry "
                    "and reduce thematic correlation risk."
                ),
                confidence=_clamp(1.0 - exposure_score),
                linked_flag=flag.code,
            ))
        return suggestions


# ── Confidence computation ────────────────────────────────────────────────────

def _compute_confidence(
    report: PortfolioDiagnosticReport,
    stability_score: float,
) -> float:
    """
    Confidence = mean(regime_alignment, factor_alignment, convergence_health, stability)
    with downward penalty for high-severity flags.
    """
    base = (
        report.regime_alignment_score
        + report.factor_alignment_score
        + report.convergence_health_score
        + stability_score
    ) / 4.0

    # Apply severity penalties
    penalty = 0.0
    for flag in report.flags:
        if flag.severity == "RED" or flag.severity == "CRITICAL":
            penalty += _PENALTY_PER_RED
        elif flag.severity == "ORANGE":
            penalty += _PENALTY_PER_ORANGE
        elif flag.severity == "YELLOW":
            penalty += _PENALTY_PER_YELLOW

    return _clamp(base - penalty)


# ── System risk level ─────────────────────────────────────────────────────────

def _compute_system_risk_level(
    report: PortfolioDiagnosticReport,
    stability_score: float,
) -> SystemRiskLevel:
    dominant = _dominant_severity(report.flags)

    # Stability-driven floor
    if stability_score < _STABILITY_SYSTEMIC:
        return "SYSTEMIC_RISK"
    if stability_score < _STABILITY_HIGH:
        stability_floor = "HIGH"
    elif stability_score < _STABILITY_ELEVATED:
        stability_floor = "ELEVATED"
    else:
        stability_floor = "LOW"

    # Severity-driven level
    severity_level_map: Dict[Optional[str], SystemRiskLevel] = {
        None: "LOW",
        "INFO": "LOW",
        "YELLOW": "MODERATE",
        "ORANGE": "ELEVATED",
        "RED": "HIGH",
        "CRITICAL": "SYSTEMIC_RISK",
    }
    from_severity = severity_level_map.get(dominant, "LOW")

    # Take the higher of the two signals
    order: Dict[str, int] = {
        "LOW": 0, "MODERATE": 1, "ELEVATED": 2, "HIGH": 3, "SYSTEMIC_RISK": 4
    }
    return (
        from_severity
        if order.get(from_severity, 0) >= order.get(stability_floor, 0)
        else stability_floor  # type: ignore[return-value]
    )


# ── Recommendation summary ────────────────────────────────────────────────────

def _build_summary(
    system_risk: SystemRiskLevel,
    confidence: float,
    all_suggestions: List[AdvisorySuggestion],
) -> str:
    """Produces a single-paragraph institutional-tone summary."""
    count = len(all_suggestions)
    if count == 0:
        return (
            "Portfolio diagnostics indicate broadly aligned conditions across regime, "
            "factor, and convergence dimensions. No material advisory actions are "
            "currently indicated."
        )

    red_critical = [s for s in all_suggestions if s.severity in ("RED", "CRITICAL")]
    orange = [s for s in all_suggestions if s.severity == "ORANGE"]

    risk_phrase = {
        "LOW": "low overall risk posture",
        "MODERATE": "moderately elevated risk posture",
        "ELEVATED": "an elevated structural risk environment",
        "HIGH": "a high-risk structural environment",
        "SYSTEMIC_RISK": "a systemic risk environment requiring immediate attention",
    }.get(system_risk, "an undetermined risk environment")

    parts = [
        f"Portfolio intelligence analysis indicates {risk_phrase} "
        f"(confidence: {confidence:.0%})."
    ]

    if red_critical:
        categories = ", ".join(sorted({s.category for s in red_critical}))
        parts.append(
            f" {len(red_critical)} critical-to-red advisory signal(s) are active "
            f"across: {categories}."
        )
    if orange:
        categories = ", ".join(sorted({s.category for s in orange}))
        parts.append(
            f" {len(orange)} orange-level signal(s) warrant review: {categories}."
        )

    if system_risk in ("HIGH", "SYSTEMIC_RISK"):
        parts.append(
            " Structural reassessment of portfolio posture is warranted before "
            "committing additional risk capital."
        )
    elif system_risk == "ELEVATED":
        parts.append(
            " Monitoring of key alignment metrics is recommended; "
            "incremental de-risking may be appropriate."
        )

    return "".join(parts)


# ── Engine ────────────────────────────────────────────────────────────────────

class AdvisoryLayer:
    """
    L10 Advisory Layer.

    Usage::

        layer = AdvisoryLayer()
        report = layer.advise(diagnostic_report)

    Invariants:
      • No trade execution
      • No portfolio mutation
      • No L8 limit override
      • No LLM calls
      • Identical inputs → identical AdvisoryReport
      • INSUFFICIENT_DIAGNOSTIC_CONTEXT on None / failed L9 report
      • Latency > 1 000 ms → LATENCY_VIOLATION report
    """

    def __init__(self) -> None:
        self._regime = _RegimeAdvisory()
        self._narrative = _NarrativeAdvisory()
        self._factor = _FactorRealignmentAdvisory()
        self._concentration = _ConcentrationAdvisory()
        self._strategy = _StrategyMisuseAdvisory()
        self._convergence = _ConvergenceDecayAdvisory()
        self._stability = _StabilityEscalationAdvisory()
        self._drawdown = _DrawdownAdvisory()
        self._friction = _ConstraintFrictionAdvisory()
        self._exposure = _ExposureSymmetryAdvisory()

    # ── Public API ────────────────────────────────────────────────────────────

    def advise(
        self,
        diagnostic_report: Optional[PortfolioDiagnosticReport],
    ) -> AdvisoryReport:
        start = time.perf_counter()
        timestamp = datetime.now(timezone.utc).isoformat()

        # ── Required upstream guard ───────────────────────────────────────────
        if diagnostic_report is None or diagnostic_report.global_status in (
            "INSUFFICIENT_CONTEXT",
            "LATENCY_VIOLATION",
        ):
            return self._insufficient_context(start, timestamp)

        # Extract stability score from component_scores if present, else default 1.0
        stability_score = diagnostic_report.component_scores.get("STABILITY_DRIFT", 1.0)

        input_hash = _compute_input_hash(diagnostic_report, stability_score)
        flags = diagnostic_report.flags

        # ── Run advisory modules ──────────────────────────────────────────────
        portfolio_sugg: List[AdvisorySuggestion] = []
        position_sugg: List[AdvisorySuggestion] = []
        risk_sugg: List[AdvisorySuggestion] = []
        exposure_sugg: List[AdvisorySuggestion] = []

        # 1. Regime
        for s in self._regime.generate(flags, diagnostic_report.regime_alignment_score):
            exposure_sugg.append(s)

        # 2. Narrative
        for s in self._narrative.generate(flags):
            position_sugg.append(s)

        # 3. Factor realignment
        for s in self._factor.generate(flags, diagnostic_report.factor_alignment_score):
            portfolio_sugg.append(s)

        # 4. Concentration
        for s in self._concentration.generate(flags, diagnostic_report.concentration_score):
            portfolio_sugg.append(s)

        # 5. Strategy misuse
        for s in self._strategy.generate(flags):
            position_sugg.append(s)

        # 6. Convergence decay
        for s in self._convergence.generate(flags, diagnostic_report.convergence_health_score):
            position_sugg.append(s)

        # 7. Stability escalation
        for s in self._stability.generate(flags, stability_score):
            risk_sugg.append(s)

        # 8. Drawdown
        for s in self._drawdown.generate(flags):
            risk_sugg.append(s)

        # 9. Constraint friction
        for s in self._friction.generate(flags):
            risk_sugg.append(s)

        # 10. Exposure symmetry
        for s in self._exposure.generate(flags, diagnostic_report.exposure_balance_score):
            exposure_sugg.append(s)

        # ── Latency guard ─────────────────────────────────────────────────────
        latency_ms = (time.perf_counter() - start) * 1_000.0
        if latency_ms >= _LATENCY_LIMIT_MS:
            return self._latency_violation(latency_ms, input_hash, timestamp)

        # ── Aggregate ─────────────────────────────────────────────────────────
        confidence = _compute_confidence(diagnostic_report, stability_score)
        system_risk = _compute_system_risk_level(diagnostic_report, stability_score)

        all_suggestions = (
            portfolio_sugg + position_sugg + risk_sugg + exposure_sugg
        )
        summary = _build_summary(system_risk, confidence, all_suggestions)

        return AdvisoryReport(
            portfolio_suggestions=tuple(portfolio_sugg),
            position_suggestions=tuple(position_sugg),
            risk_suggestions=tuple(risk_sugg),
            exposure_adjustments=tuple(exposure_sugg),
            confidence_score=confidence,
            system_risk_level=system_risk,
            recommendation_summary=summary,
            latency_ms=latency_ms,
            input_hash=input_hash,
            timestamp=timestamp,
        )

    # ── Fail-safe constructors ────────────────────────────────────────────────

    def _insufficient_context(self, start: float, timestamp: str) -> AdvisoryReport:
        latency_ms = (time.perf_counter() - start) * 1_000.0
        return AdvisoryReport(
            portfolio_suggestions=(),
            position_suggestions=(),
            risk_suggestions=(),
            exposure_adjustments=(),
            confidence_score=0.0,
            system_risk_level="INSUFFICIENT_DIAGNOSTIC_CONTEXT",
            recommendation_summary=(
                "Advisory layer unable to generate suggestions: "
                "L9 diagnostic report is absent or in a failed state. "
                "Ensure the Portfolio Intelligence Engine has produced a valid report "
                "before requesting advisory output."
            ),
            latency_ms=latency_ms,
            input_hash="",
            timestamp=timestamp,
        )

    def _latency_violation(
        self, latency_ms: float, input_hash: str, timestamp: str
    ) -> AdvisoryReport:
        return AdvisoryReport(
            portfolio_suggestions=(),
            position_suggestions=(),
            risk_suggestions=(),
            exposure_adjustments=(),
            confidence_score=0.0,
            system_risk_level="LATENCY_VIOLATION",
            recommendation_summary=(
                f"Advisory layer latency guard breached: {latency_ms:.1f}ms exceeded "
                f"{_LATENCY_LIMIT_MS:.0f}ms limit. Report discarded."
            ),
            latency_ms=latency_ms,
            input_hash=input_hash,
            timestamp=timestamp,
        )
