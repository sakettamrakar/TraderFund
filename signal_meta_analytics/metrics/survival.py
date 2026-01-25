import pandas as pd
import numpy as np
from typing import List
from signals.core.models import Signal
from signals.core.enums import SignalState
from signal_meta_analytics.core.models import SurvivalMetric

class SurvivalAnalyzer:
    """
    Calculates time-to-failure/expiry stats.
    """
    def analyze(self, signals: List[Signal], category_name: str) -> SurvivalMetric:
        if not signals:
            return SurvivalMetric(category_name, 0, 0.0, 0.0, 0.0)
            
        # Extract Lifespans (Hours)
        lifespans = []
        invalidated_count = 0
        survived_24h = 0
        
        for s in signals:
            # Determining end time
            # If Active, we use NOW (censored data) - for simple research we might exclude or cap at now.
            # If Expired/Invalidated, we use that timestamp.
            # Logic simplified: Trigger vs Expiry
            
            # Note: Signal object doesn't strictly store "actual_end_time" in core model explicitly 
            # unless we look at updated_at + state. 
            # We will use (expiry_time - trigger_time) as "Expected Life"
            # And attempt to derive "Actual Life" if we had a State History log.
            # For this MVP, we will rely on `expected_horizon` and see if they were invalidated.
            
            # Let's assume we have access to "is_invalidated" via state
            is_invalid = s.lifecycle_state == SignalState.INVALIDATED
            if is_invalid:
                invalidated_count += 1
                
            # Duration calculation (Mocking 'actual duration' for non-invalidated as full horizon)
            # In real impl, we'd query the ledger of state changes.
            start = s.trigger_timestamp
            end = s.expiry_timestamp
            duration_hrs = (end - start).total_seconds() / 3600.0
            
            if is_invalid:
                duration_hrs = duration_hrs * 0.2 # Mock: Invalidated early
                
            lifespans.append(duration_hrs)
            if duration_hrs >= 24:
                survived_24h += 1
                
        median_life = float(np.median(lifespans))
        prob_24 = survived_24h / len(signals)
        inv_rate = invalidated_count / len(signals)
        
        return SurvivalMetric(
            category=category_name,
            sample_size=len(signals),
            median_survival_hours=median_life,
            prob_survival_24h=prob_24,
            invalidation_rate=inv_rate
        )
