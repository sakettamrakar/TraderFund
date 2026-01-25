from enum import Enum, unique

@unique
class EventType(str, Enum):
    SIGNAL = "SIGNAL"
    NEWS = "NEWS"
    MACRO = "MACRO"
    HASHTAG = "HASHTAG"
    ANOMALY = "ANOMALY"

@unique
class NarrativeState(str, Enum):
    BORN = "BORN"
    REINFORCED = "REINFORCED"
    WEAKENED = "WEAKENED"
    RESOLVED = "RESOLVED"
    INVALIDATED = "INVALIDATED"

@unique
class NarrativeScope(str, Enum):
    ASSET = "ASSET"
    SECTOR = "SECTOR"
    MARKET = "MARKET"
