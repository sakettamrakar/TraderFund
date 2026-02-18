"""
Advisory Models (L10) — Input and Output Contracts
===================================================
All models are frozen dataclasses — zero mutation, full determinism.

L10 sits above L9 in the observation hierarchy:

    L9  → Diagnose (PortfolioDiagnosticReport)
    L10 → Suggest  (AdvisoryReport)
    L8  → Enforce  (ConstraintDecision)

Nothing in this module mutates portfolio state or issues execution directives.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Literal, Optional, Tuple

# ── Vocabulary ────────────────────────────────────────────────────────────────

AdvisoryCategory = Literal[
    "REGIME_ADVISORY",
    "NARRATIVE_ADVISORY",
    "FACTOR_REALIGNMENT",
    "CONCENTRATION_ADVISORY",
    "STRATEGY_MISUSE",
    "CONVERGENCE_DECAY",
    "STABILITY_ESCALATION",
    "DRAWDOWN_ADVISORY",
    "CONSTRAINT_FRICTION",
    "EXPOSURE_SYMMETRY",
]

AdvisorySeverity = Literal["INFO", "YELLOW", "ORANGE", "RED", "CRITICAL"]

SystemRiskLevel = Literal[
    "LOW",
    "MODERATE",
    "ELEVATED",
    "HIGH",
    "SYSTEMIC_RISK",
    "INSUFFICIENT_DIAGNOSTIC_CONTEXT",
    "LATENCY_VIOLATION",
]

AdvisoryStatus = Literal[
    "OK",
    "INSUFFICIENT_DIAGNOSTIC_CONTEXT",
    "LATENCY_VIOLATION",
]


# ── Per-suggestion model ──────────────────────────────────────────────────────

@dataclass(frozen=True)
class AdvisorySuggestion:
    """
    A single structured advisory observation.

    Fields
    ------
    category        : which advisory module produced this
    severity        : mapped from the linked L9 flag severity
    rationale       : why this suggestion is raised (factual, deterministic)
    suggested_action: institutional-tone, non-instructional recommendation text
    confidence      : [0.0, 1.0] — how strongly the evidence supports this suggestion
    linked_flag     : the L9 DiagnosticFlag.code that triggered this suggestion
                      (None for portfolio-level synthesised suggestions)
    affected_symbol : symbol this applies to; None = portfolio-level
    """
    category: AdvisoryCategory
    severity: AdvisorySeverity
    rationale: str
    suggested_action: str
    confidence: float               # [0.0, 1.0]
    linked_flag: Optional[str]      # L9 flag code
    affected_symbol: Optional[str] = None


# ── Output contract ───────────────────────────────────────────────────────────

@dataclass(frozen=True)
class AdvisoryReport:
    """
    L10 output — fully deterministic, serialisable.

    Suggestion vectors
    ------------------
    portfolio_suggestions : portfolio-level structural observations
    position_suggestions  : per-symbol advisory notes
    risk_suggestions      : risk-management observations (drawdown, stability, friction)
    exposure_adjustments  : directional or gross exposure recalibration hints

    Aggregate fields
    ----------------
    confidence_score      : mean alignment across key L9 scores, [0.0, 1.0]
    system_risk_level     : coarse risk classification for downstream consumption
    recommendation_summary: single-paragraph institutional summary
    """
    portfolio_suggestions: Tuple[AdvisorySuggestion, ...]
    position_suggestions: Tuple[AdvisorySuggestion, ...]
    risk_suggestions: Tuple[AdvisorySuggestion, ...]
    exposure_adjustments: Tuple[AdvisorySuggestion, ...]

    confidence_score: float
    system_risk_level: SystemRiskLevel
    recommendation_summary: str

    latency_ms: float
    input_hash: str         # SHA-256 first 16 hex chars of diagnostic report hash + regime
    timestamp: str          # ISO-8601 UTC
