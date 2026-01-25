from datetime import timedelta
from typing import List, Dict
from signals.core.models import Signal
from signals.core.enums import Market, SignalCategory
from alpha_discovery.core.models import AlphaHypothesis, AlphaPatternType
from alpha_discovery.patterns.base import AlphaPatternDetector

class LeadLagDetector(AlphaPatternDetector):
    """
    Detects if US Signals consistently precede India Signals.
    Simplistic implementation:
    - Matches on Sector/Category
    - Checks for time delta in [0, 24 hours]
    """
    
    def detect(self, signals: List[Signal]) -> List[AlphaHypothesis]:
        # Split by market
        us_signals = [s for s in signals if s.market == Market.US]
        in_signals = [s for s in signals if s.market == Market.INDIA]
        
        hypotheses = []
        
        # Simple Pair Matching logic
        # Ideally this uses statistical Granger Causality on time series.
        # Here we do discrete event matching for the "Signal" layer.
        
        for us_sig in us_signals:
            for in_sig in in_signals:
                # 1. Check Causality Timeframe (US leads India by 0-24h)
                delta = in_sig.trigger_timestamp - us_sig.trigger_timestamp
                # US Close ~21:00 UTC. India Open ~03:45 UTC next day.
                # Delta should be roughly 6-20 hours.
                if timedelta(hours=4) <= delta <= timedelta(hours=24):
                    
                    # 2. Check Semantic Similarity
                    # e.g., Same Category & Direction
                    if (us_sig.signal_category == in_sig.signal_category and 
                        us_sig.direction == in_sig.direction):
                        
                        # Proposed Alpha
                        evidence = {
                            "trigger_us": us_sig.trigger_timestamp.isoformat(),
                            "trigger_in": in_sig.trigger_timestamp.isoformat(),
                            "time_lag_hours": delta.total_seconds() / 3600,
                            "match_type": "Direct Category Match"
                        }
                        
                        hypotheses.append(AlphaHypothesis.create(
                            title=f"US {us_sig.asset_id} leads India {in_sig.asset_id} ({us_sig.signal_category})",
                            pattern=AlphaPatternType.LEAD_LAG,
                            source=Market.US,
                            target=Market.INDIA,
                            assets=[us_sig.asset_id, in_sig.asset_id],
                            confidence=50.0, # Initial guess
                            evidence=evidence
                        ))
                        
        return hypotheses
