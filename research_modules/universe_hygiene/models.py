"""
Stage 0: Universe Hygiene - Data Models

Canonical output schema for eligibility results.
"""

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional
from datetime import date


class ExclusionReason(Enum):
    """Explicit reasons for symbol exclusion."""
    
    EXCHANGE_NOT_ALLOWED = "exchange_not_allowed"
    ASSET_TYPE_NOT_EQUITY = "asset_type_not_equity"
    PENNY_STOCK = "penny_stock"
    ILLIQUID = "illiquid"
    INACTIVE = "inactive"
    DELISTED = "delisted"
    NO_PRICE_DATA = "no_price_data"


class EligibilityStatus(Enum):
    """Eligibility determination."""
    
    ELIGIBLE = "eligible"
    EXCLUDED = "excluded"


class LiquidityBucket(Enum):
    """Liquidity classification based on average daily volume."""
    
    VERY_LOW = "very_low"       # < 100K
    LOW = "low"                 # 100K - 500K
    ACCEPTABLE = "acceptable"  # 500K - 1M
    HIGH = "high"              # > 1M


class PriceBucket(Enum):
    """Price classification based on average close price."""
    
    EXTREME_LOW = "extreme_low"  # $1 - $5
    LOW = "low"                  # $5 - $10
    ACCEPTABLE = "acceptable"    # $10 - $50
    HIGH = "high"                # > $50


@dataclass
class EligibilityRecord:
    """
    Canonical output record for universe eligibility evaluation.
    
    This is the contract between Stage 0 and Stage 1.
    """
    
    symbol: str
    exchange: str
    eligibility_status: str  # EligibilityStatus value
    exclusion_reason: Optional[str]  # ExclusionReason value if excluded
    liquidity_bucket: Optional[str]  # LiquidityBucket value
    price_bucket: Optional[str]  # PriceBucket value
    avg_daily_volume: Optional[float]
    avg_price: Optional[float]
    trading_days_in_window: int
    last_evaluated_date: str  # ISO 8601 date string
    
    def to_dict(self) -> dict:
        """Convert to dictionary for DataFrame creation."""
        return asdict(self)
    
    @classmethod
    def create_excluded(
        cls,
        symbol: str,
        exchange: str,
        reason: ExclusionReason,
        evaluated_date: date,
        trading_days: int = 0,
        avg_volume: Optional[float] = None,
        avg_price: Optional[float] = None,
    ) -> "EligibilityRecord":
        """Factory for excluded symbols."""
        return cls(
            symbol=symbol,
            exchange=exchange,
            eligibility_status=EligibilityStatus.EXCLUDED.value,
            exclusion_reason=reason.value,
            liquidity_bucket=None,
            price_bucket=None,
            avg_daily_volume=avg_volume,
            avg_price=avg_price,
            trading_days_in_window=trading_days,
            last_evaluated_date=evaluated_date.isoformat(),
        )
    
    @classmethod
    def create_eligible(
        cls,
        symbol: str,
        exchange: str,
        liquidity: LiquidityBucket,
        price: PriceBucket,
        avg_volume: float,
        avg_price: float,
        trading_days: int,
        evaluated_date: date,
    ) -> "EligibilityRecord":
        """Factory for eligible symbols."""
        return cls(
            symbol=symbol,
            exchange=exchange,
            eligibility_status=EligibilityStatus.ELIGIBLE.value,
            exclusion_reason=None,
            liquidity_bucket=liquidity.value,
            price_bucket=price.value,
            avg_daily_volume=avg_volume,
            avg_price=avg_price,
            trading_days_in_window=trading_days,
            last_evaluated_date=evaluated_date.isoformat(),
        )
