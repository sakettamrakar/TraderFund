from dataclasses import dataclass
from typing import Literal, Tuple

StrategyType = Literal[
    "BREAKOUT",
    "PULLBACK",
    "MEAN_REVERSION",
    "TREND_FOLLOW",
    "VOLATILITY_EXPANSION",
    "SCALP",
    "SWING",
    "POSITIONAL",
]

DirectionType = Literal["LONG", "SHORT"]

RejectionReason = Literal[
    "Score below threshold",
    "Lens count insufficient",
    "Regime incompatible",
    "Direction not allowed",
]


@dataclass(frozen=True)
class ConvergenceResult:
    symbol: str
    direction: DirectionType
    convergence_score: float
    lens_count: int
    status: str  # VALID | INVALID | ...


@dataclass(frozen=True)
class StrategyTemplate:
    strategy_id: StrategyType
    compatible_regimes: Tuple[str, ...]
    min_score_threshold: float
    min_lens_count: int
    allowed_directions: Tuple[DirectionType, ...]
    risk_profile: str
    time_horizon: str


@dataclass(frozen=True)
class StrategyRejection:
    strategy_id: StrategyType
    rejection_reason: RejectionReason


@dataclass(frozen=True)
class StrategyDecision:
    symbol: str
    direction: str
    selected_strategy: str
    candidate_strategies: Tuple[StrategyType, ...]
    rejected_strategies: Tuple[StrategyRejection, ...]
    selection_reason: str
    regime: str
    convergence_score: float
    latency_ms: float
    input_hash: str
    status: str
