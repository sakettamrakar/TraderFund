from typing import Dict, Any

# Symbolic Capital Definition
TOTAL_PAPER_CAPITAL = 100.0

# Family Ceilings (Hard Limits)
FAMILY_BUCKETS = {
    "momentum": 0.25,
    "mean_reversion": 0.0, # Currently disabled in envelopes if expansion
    "value": 0.35,
    "quality": 0.35,
    "carry": 0.15,
    "volatility": 0.25,
    "spread": 0.15,
    "stress": 0.10
}

# Drawdown Thresholds
DRAWDOWN_TRIGGERS = {
    "WARNING": 0.02,
    "CRITICAL": 0.05,
    "FROZEN": 0.10
}

def get_capital_config() -> Dict[str, Any]:
    return {
        "total_capital": TOTAL_PAPER_CAPITAL,
        "buckets": FAMILY_BUCKETS,
        "drawdown_triggers": DRAWDOWN_TRIGGERS,
        "mode": "PAPER_ONLY"
    }
