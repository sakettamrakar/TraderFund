"""Signal models for Momentum Engine."""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any

@dataclass
class MomentumSignal:
    """Structured momentum signal."""
    symbol: str
    timestamp: str  # ISO8601 string
    signal_type: str = "MOMENTUM_LONG"
    confidence: float = 0.0
    entry_hint: str = ""
    stop_hint: str = ""
    reason: str = ""
    price_t0: float = 0.0
    volume_t0: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert signal to dictionary."""
        return asdict(self)
