from dataclasses import dataclass
from typing import Literal

RegimeType = Literal[
    "TRENDING",
    "CHOP",
    "TRANSITION",
    "STRESS",
    "VOLATILE",
    "ACCUMULATION",
    "DISTRIBUTION",
]


@dataclass(frozen=True)
class RegimeState:
    regime: RegimeType
    volatility: float


@dataclass(frozen=True)
class SignalInput:
    signal_type: str        # e.g. "TECHNICAL_BREAKOUT", "MOMENTUM"
    base_confidence: float  # Raw score from L6 in [0.0, 1.0]
    factor_alignment: bool


@dataclass(frozen=True)
class TrustResult:
    trust_score: float
    status: str                    # OK | INSUFFICIENT_CONTEXT | INVALID_REGIME | LATENCY_VIOLATION
    regime_context: str            # regime name or "STRESS" for fail-safe paths
    adjustment_reason: str
    computation_latency_ms: float
    signal_type: str               # mirrors input for explainability (Invariant 4)
    base_confidence: float         # mirrors input for explainability (Invariant 4)
    deterministic_input_hash: str  # SHA-256 prefix of (regime, signal_type, base, alignment)
    structured_log: str            # JSON string — full explainability payload
    # ── Stability dampening fields (defaults preserve backward compatibility) ─
    raw_trust: float = 0.0          # regime-adjusted trust before stability dampening
    stability_score: float = 1.0    # component stability ∈ [0.0, 1.0]; 1.0 = fully stable
    effective_trust: float = 0.0    # raw_trust * stability_score — downstream-consumed value
