from dataclasses import dataclass, field
from typing import List, Dict, Optional, Literal

DirectionType = Literal["LONG", "SHORT"]
StatusType = Literal["APPROVE", "ADJUST", "REJECT", "LATENCY_VIOLATION"]

@dataclass(frozen=True)
class StrategyDecision:
    symbol: str
    direction: DirectionType
    selected_strategy: str
    convergence_score: float
    time_horizon: str  # e.g., "SCALP", "SWING"
    regime: str
    sector: Optional[str] = None # Added for Sector Exposure Law

@dataclass(frozen=True)
class PortfolioState:
    total_equity: float
    current_drawdown_pct: float
    positions: List[Dict[str, float]]  # List of dicts with symbol, size_pct, etc.
    sector_exposure_map: Dict[str, float] # sector -> exposure_pct
    gross_exposure_pct: float
    net_exposure_pct: float

@dataclass(frozen=True)
class RiskConfig:
    max_position_pct: float
    max_sector_exposure_pct: float
    max_gross_exposure_pct: float
    max_net_exposure_pct: float
    max_drawdown_pct: float
    stress_scaling_factor: float
    transition_scaling_factor: float

@dataclass(frozen=True)
class ConstraintDecision:
    symbol: str
    status: StatusType
    approved_size_pct: float
    adjustment_reason: str
    rejection_reason: str
    risk_flags: List[str]
    regime_scaling_applied: bool
    latency_ms: float
    input_hash: str
