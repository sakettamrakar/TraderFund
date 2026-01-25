import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any, List, Optional
from signals.core.enums import Market, SignalCategory

@dataclass(frozen=True)
class MetaInsight:
    """
    Descriptive observation about signal behavior.
    """
    insight_id: str
    generated_at: datetime
    
    # Context
    market: Market
    signal_category: SignalCategory
    regime_context: str # e.g., "HIGH_VOLATILITY", "TRENDING"
    
    # The Insight
    observation: str # "Trend signals in High Volatility decay 2x faster"
    confidence_level: str # "HIGH", "MEDIUM", "LOW" (Statistical significance)
    
    # Evidence
    metrics_payload: Dict[str, Any] # {"median_survival_hours": 4, "failure_rate": 0.6}
    
    version: int
    
    @classmethod
    def create(cls, market: Market, category: SignalCategory, regime: str, obs: str, conf: str, metrics: Dict) -> 'MetaInsight':
        return cls(
            insight_id=str(uuid.uuid4()),
            generated_at=datetime.utcnow(),
            market=market,
            signal_category=category,
            regime_context=regime,
            observation=obs,
            confidence_level=conf,
            metrics_payload=metrics,
            version=1
        )
        
    def to_dict(self):
        d = asdict(self)
        d['generated_at'] = d['generated_at'].isoformat()
        d['market'] = d['market'].value
        d['signal_category'] = d['signal_category'].value
        return d

@dataclass(frozen=True)
class SurvivalMetric:
    """
    Stats on signal longevity.
    """
    category: str
    sample_size: int
    median_survival_hours: float
    prob_survival_24h: float
    invalidation_rate: float
