from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class ConfidenceContext:
    """
    Contextual data required to compute confidence.
    Normalized values should be pre-computed by the caller.
    """
    # 1. Volume
    volume_ratio: float = 1.0       # Current Vol / Avg Vol. 1.0 = Average.
    
    # 2. Volatility
    volatility_z_score: float = 0.0 # How many std devs from mean volatility. 0 = Normal.
    
    # 3. Agreement
    indicator_agreement_count: int = 0 # How many other indicators confirm this signal.
    
    # 4. Regime
    market_trend_score: float = 0.0 # -1.0 (Bear) to 1.0 (Bull). 0 = Neutral.
    
    def to_dict(self):
        return {
            "volume_ratio": self.volume_ratio,
            "volatility_z_score": self.volatility_z_score,
            "indicator_agreement_count": self.indicator_agreement_count,
            "market_trend_score": self.market_trend_score
        }
