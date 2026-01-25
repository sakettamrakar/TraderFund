from datetime import datetime, timedelta
import math

class DecayCalculator:
    """
    Computes time-based decay for confidence scores.
    Formula: C(t) = C0 * 2^(-t/half_life)
    """

    # Map Horizon Strings to Half-Life (Minutes)
    HORIZON_MAP_MINUTES = {
        "1H": 30,    # 1 Hour Horizon -> 30m Half Life
        "4H": 120,   # 4 Hour Horizon -> 2h Half Life
        "1D": 720,   # 1 Day Horizon -> 12h Half Life (aggressive) 
        "2D": 1440,  # 2 Day Horizon -> 24h Half Life
        "1W": 2880,  # 1 Week (Trading) -> ~2 Days Half Life
    }
    
    DEFAULT_HALF_LIFE = 720 # 12 Hours

    def calculate_decayed_score(self, 
                              initial_score: float, 
                              trigger_time: datetime, 
                              current_time: datetime,
                              horizon: str) -> float:
        
        if initial_score <= 0:
            return 0.0

        elapsed_seconds = (current_time - trigger_time).total_seconds()
        if elapsed_seconds < 0:
            return initial_score # Should not happen unless clock skew

        half_life_minutes = self.HORIZON_MAP_MINUTES.get(horizon, self.DEFAULT_HALF_LIFE)
        half_life_seconds = half_life_minutes * 60.0
        
        # Exponential Decay
        # Fraction of half-lives elapsed
        ratio = elapsed_seconds / half_life_seconds
        
        decayed_score = initial_score * math.pow(0.5, ratio)
        
        # Floor at 0, Clamp ceiling (though decay shouldn't increase)
        return max(0.0, min(initial_score, decayed_score))
