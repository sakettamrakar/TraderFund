from enum import Enum, unique

@unique
class AlphaPatternType(str, Enum):
    LEAD_LAG = "LEAD_LAG"                 # Pattern A -> Pattern B (Time delay)
    REGIME_SPILLOVER = "REGIME_SPILLOVER" # Volatility spillover
    SECTOR_MOMENTUM = "SECTOR_MOMENTUM"   # Cross-border sector moves
    SIGNAL_ASYMMETRY = "SIGNAL_ASYMMETRY" # Same signal works differently

@unique
class ValidationState(str, Enum):
    PROPOSED = "PROPOSED"       # Newly generated
    VALIDATING = "VALIDATING"   # Undergoing paper testing
    CONFIRMED = "CONFIRMED"     # Statistically significant
    DECAYED = "DECAYED"         # Lost predictive power
    INVALIDATED = "INVALIDATED" # Proven false
