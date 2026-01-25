from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from signals.core.enums import SignalCategory, Market

@dataclass
class ReliabilityMetric:
    """
    Statistical performance of a signal group.
    Descriptive only. No alpha claims.
    """
    sample_size: int
    directional_accuracy: float # % of time price moved in signal direction (>0)
    
    # Excursion Metrics (Normalized % change)
    mean_favorable_excursion: float # Avg max move in signal direction
    mean_adverse_excursion: float   # Avg max move against signal
    
    # Consistency
    follow_through_rate: float      # % of time move > threshold (e.g. 0.5%)
    
    # Context
    confidence_bucket: str          # e.g., "HIGH", "MED", "LOW"
    
@dataclass
class ReliabilityReport:
    """
    Aggregated report for a specific slice of analysis.
    """
    report_id: str
    generated_at: datetime
    
    # Scope
    market: Market
    signal_category: Optional[SignalCategory]
    period_start: datetime
    period_end: datetime
    
    # Metrics
    metrics_by_confidence: Dict[str, ReliabilityMetric]
    
    # Summary
    overall_metric: ReliabilityMetric
