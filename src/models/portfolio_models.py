"""
Portfolio Intelligence Models (L9) — Input and Output Contracts
===============================================================
All models are frozen dataclasses — zero mutation, full determinism.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional, Tuple

# ── Vocabulary ────────────────────────────────────────────────────────────────

SeverityLevel = Literal["INFO", "YELLOW", "ORANGE", "RED", "CRITICAL"]

GlobalStatus = Literal[
    "OK",
    "DEGRADED",
    "CRITICAL",
    "INSUFFICIENT_CONTEXT",
    "LATENCY_VIOLATION",
]

NarrativeLifecycle = Literal[
    "ACTIVE",
    "RESOLVED",
    "REVERSED",
    "FADING",
    "EMERGING",
]

StrategyHorizon = Literal["SCALP", "SWING", "POSITIONAL"]

# Imported vocabulary mirrors meta_models.RegimeType without creating a
# cross-dependency on a mutable model chain.
RegimeType = Literal[
    "TRENDING",
    "CHOP",
    "TRANSITION",
    "STRESS",
    "VOLATILE",
    "ACCUMULATION",
    "DISTRIBUTION",
]

FactorType = Literal[
    "MOMENTUM",
    "VALUE",
    "QUALITY",
    "VOLATILITY",
    "GROWTH",
    "SENTIMENT",
    "FLOW",
]


# ── Input Contracts ───────────────────────────────────────────────────────────

@dataclass(frozen=True)
class RegimeState:
    """L1 regime snapshot consumed by L9."""
    regime: RegimeType
    volatility: float               # normalised [0.0, 1.0]
    stability_score: float = 1.0    # [0.0, 1.0]; 1.0 = fully stable


@dataclass(frozen=True)
class NarrativeTag:
    """Attaches a narrative lifecycle state to a holding."""
    holding_symbol: str
    narrative_id: str
    lifecycle: NarrativeLifecycle


@dataclass(frozen=True)
class NarrativeState:
    """L2 narrative snapshot — all active narrative tags."""
    tags: Tuple[NarrativeTag, ...]


@dataclass(frozen=True)
class FactorState:
    """Current dominant factor and per-holding factor assignments."""
    dominant_factor: FactorType
    # symbol -> factor assigned to this holding
    holding_factors: Dict[str, FactorType]


@dataclass(frozen=True)
class HoldingMeta:
    """Per-holding metadata required for L9 diagnostic modules."""
    symbol: str
    weight_pct: float               # [0.0, 100.0]
    direction: Literal["LONG", "SHORT"]
    strategy: StrategyHorizon
    sector: str
    days_held: int
    initial_convergence_score: float    # score at entry, [0.0, 1.0]
    current_convergence_score: float    # latest score, [0.0, 1.0]


@dataclass(frozen=True)
class PortfolioSnapshot:
    """
    Full portfolio state consumed by L9.
    net_exposure_pct: signed; positive = net long, negative = net short.
    gross_exposure_pct: sum of absolute exposures.
    current_drawdown_pct: positive value = drawdown magnitude.
    """
    holdings: Tuple[HoldingMeta, ...]
    net_exposure_pct: float
    gross_exposure_pct: float
    current_drawdown_pct: float
    sector_caps: Dict[str, float]       # sector -> max allowed weight_pct


@dataclass(frozen=True)
class ConvergenceSnapshot:
    """Per-symbol convergence history for decay detection."""
    # symbol -> (initial_score, current_score)
    scores: Dict[str, Tuple[float, float]]


@dataclass(frozen=True)
class ConstraintActivitySummary:
    """
    Aggregated recent L8 activity — count of decisions by outcome.
    Used by Constraint Friction module.
    """
    approved_count: int
    adjusted_count: int
    rejected_count: int


# ── Output Contracts ──────────────────────────────────────────────────────────

@dataclass(frozen=True)
class DiagnosticFlag:
    """
    A single structured diagnostic observation.
    All fields are mandatory — no silent suppression.
    """
    code: str                       # machine-readable unique code
    module: str                     # which diagnostic module raised it
    severity: SeverityLevel
    message: str                    # human-readable explanation with why
    affected_symbol: Optional[str] = None   # None = portfolio-level flag


@dataclass(frozen=True)
class PortfolioDiagnosticReport:
    """
    L9 output contract — fully deterministic, serialisable.

    Component scores ∈ [0.0, 1.0]; 1.0 = perfectly aligned / healthy.
    """
    # ── Alignment scores ─────────────────────────────────────────────────────
    regime_alignment_score: float
    narrative_alignment_score: float
    factor_alignment_score: float
    strategy_alignment_score: float
    concentration_score: float
    exposure_balance_score: float
    convergence_health_score: float

    # ── Aggregate ─────────────────────────────────────────────────────────────
    global_status: GlobalStatus
    flags: Tuple[DiagnosticFlag, ...]
    severity_map: Dict[str, SeverityLevel]      # flag.code -> severity
    component_scores: Dict[str, float]          # module name -> score

    # ── Observability ─────────────────────────────────────────────────────────
    latency_ms: float
    input_hash: str                 # SHA-256 first 16 hex chars
    timestamp: str                  # ISO-8601 UTC at time of evaluation
