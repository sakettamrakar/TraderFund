from enum import Enum, unique

@unique
class Market(str, Enum):
    US = "US"
    INDIA = "INDIA"

@unique
class SignalCategory(str, Enum):
    MOMENTUM = "MOMENTUM"
    TREND = "TREND"
    MEAN_REVERSION = "MEAN_REVERSION"
    VOLATILITY = "VOLATILITY"
    LIQUIDITY = "LIQUIDITY"
    EVENT = "EVENT"

@unique
class SignalDirection(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"

@unique
class SignalState(str, Enum):
    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    WEAKENED = "WEAKENED"
    EXPIRED = "EXPIRED"
    INVALIDATED = "INVALIDATED"
