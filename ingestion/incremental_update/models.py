"""Incremental Update - Models"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class UpdateStatus:
    symbol: str
    last_attempt: str
    last_success: Optional[str]
    status: str  # success/failed/skipped/up_to_date
    error_reason: Optional[str]
    
    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "last_attempt": self.last_attempt,
            "last_success": self.last_success,
            "status": self.status,
            "error_reason": self.error_reason,
        }
    
    @classmethod
    def success(cls, symbol: str):
        now = datetime.utcnow().isoformat()
        return cls(symbol, now, now, "success", None)
    
    @classmethod
    def up_to_date(cls, symbol: str):
        return cls(symbol, datetime.utcnow().isoformat(), None, "up_to_date", None)
    
    @classmethod
    def failed(cls, symbol: str, error: str):
        return cls(symbol, datetime.utcnow().isoformat(), None, "failed", error)
    
    @classmethod
    def skipped(cls, symbol: str, reason: str):
        return cls(symbol, datetime.utcnow().isoformat(), None, "skipped", reason)
