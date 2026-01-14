from enum import Enum, unique

@unique
class ActionType(str, Enum):
    ENTER = "ENTER"
    HOLD = "HOLD"
    EXIT = "EXIT"
    IGNORE = "IGNORE"

@unique
class OutcomeType(str, Enum):
    WIN = "WIN"
    LOSS = "LOSS"
    SCRATCH = "SCRATCH" # Break-even
    PENDING = "PENDING"
