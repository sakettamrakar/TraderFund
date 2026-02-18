from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Tuple

# ── Canonical lens vocabulary ─────────────────────────────────────────────────
LensName = Literal[
    "TECHNICAL",
    "MOMENTUM",
    "FUNDAMENTAL",
    "SENTIMENT",
    "FLOW",
    "VOLATILITY",
]

# Direction space is intentionally closed — no "NEUTRAL" to prevent waffling
Direction = Literal["LONG", "SHORT"]

ConvictionGrade = Literal["A", "B", "C", "D"]

ConvergenceStatus = Literal[
    "OK",
    "LOW_CONFIDENCE",           # < 3 independent lenses
    "DIRECTION_CONFLICT",       # mixed LONG/SHORT
    "REGIME_MISMATCH",          # avg_regime_compatibility < 0.50
    "HIGH_DISPERSION",          # variance of lens confidence > 0.22
    "INSUFFICIENT_CONVERGENCE", # fail-safe: meta_trust==0, regime undefined, <2 lenses
    "LATENCY_VIOLATION",        # computation exceeded 1000ms
    "WATCHLIST",                # < 3 lens scores >= 0.60 (minimum confluence rule)
]

VALID_LENS_NAMES: frozenset[str] = frozenset(
    {"TECHNICAL", "MOMENTUM", "FUNDAMENTAL", "SENTIMENT", "FLOW", "VOLATILITY"}
)


@dataclass(frozen=True)
class LensSignal:
    symbol: str
    direction: Direction
    confidence: float           # raw lens confidence in [0.0, 1.0]
    regime_compatibility: float # how well this lens fits the current regime, in [0.0, 1.0]
    lens_name: LensName


@dataclass(frozen=True)
class ConvergenceResult:
    symbol: str
    direction: str                  # "LONG" | "SHORT" | "CONFLICT" | "NONE"
    lens_count: int
    aligned_lenses: int             # lenses whose direction matches the winning direction
    mean_confidence: float
    meta_trust: float
    avg_regime_compatibility: float
    score_dispersion: float         # variance of lens confidence values
    final_score: float
    conviction_grade: ConvictionGrade
    status: ConvergenceStatus
    latency_ms: float
    input_hash: str                 # SHA-256 first 16 hex chars for determinism audit
    # ── Adaptive feedback fields (defaults preserve backward compatibility) ──
    base_score: float = 0.0         # lens-only score before performance modifier
    performance_modifier: float = 0.0  # ∈ [-0.20, +0.20]; 0.0 when no context provided
    # ── Phase E/F convergence math fields ──
    lens_weights: str = "{}"        # JSON dict: {lens_name: normalised_weight}
    dispersion_penalty: float = 0.0 # penalty applied for very low or high variance
    portfolio_bias: float = 0.0     # from PortfolioFeedbackEngine ∈ [-0.40, 0.0]
