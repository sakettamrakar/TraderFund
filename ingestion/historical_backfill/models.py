"""Historical Backfill - Models"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class BackfillStatus:
    symbol: str
    status: str  # pending/success/failed
    history_depth_days: int
    history_start_date: Optional[str]
    history_end_date: Optional[str]
    last_attempt: str
    error_reason: Optional[str]
    
    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "status": self.status,
            "history_depth_days": self.history_depth_days,
            "history_start_date": self.history_start_date,
            "history_end_date": self.history_end_date,
            "last_attempt": self.last_attempt,
            "error_reason": self.error_reason,
        }
    
    @classmethod
    def pending(cls, symbol: str):
        return cls(
            symbol=symbol,
            status="pending",
            history_depth_days=0,
            history_start_date=None,
            history_end_date=None,
            last_attempt=datetime.utcnow().isoformat(),
            error_reason=None,
        )
    
    @classmethod
    def success(cls, symbol: str, depth: int, start: str, end: str):
        return cls(
            symbol=symbol,
            status="success",
            history_depth_days=depth,
            history_start_date=start,
            history_end_date=end,
            last_attempt=datetime.utcnow().isoformat(),
            error_reason=None,
        )
    
    @classmethod
    def failed(cls, symbol: str, error: str):
        return cls(
            symbol=symbol,
            status="failed",
            history_depth_days=0,
            history_start_date=None,
            history_end_date=None,
            last_attempt=datetime.utcnow().isoformat(),
            error_reason=error,
        )
