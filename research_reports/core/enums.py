from enum import Enum, unique

@unique
class ReportType(str, Enum):
    DAILY_BRIEF = "DAILY_BRIEF"
    WEEKLY_SYNTHESIS = "WEEKLY_SYNTHESIS"
    THEMATIC = "THEMATIC"
