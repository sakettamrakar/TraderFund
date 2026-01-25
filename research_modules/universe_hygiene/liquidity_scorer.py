"""
Stage 0: Universe Hygiene - Liquidity Scorer

Classifies symbols into liquidity buckets based on average daily volume.
"""

import logging
from typing import Optional

from . import config
from .models import LiquidityBucket

logger = logging.getLogger(__name__)


def classify_liquidity(avg_daily_volume: Optional[float]) -> Optional[LiquidityBucket]:
    """
    Classify a symbol's liquidity based on average daily volume.
    
    Args:
        avg_daily_volume: Average daily trading volume over evaluation window.
        
    Returns:
        LiquidityBucket enum value, or None if volume data unavailable.
        
    Note:
        Symbols with volume below ILLIQUID threshold should be excluded
        before calling this function. This function only classifies
        eligible symbols into buckets.
    """
    if avg_daily_volume is None:
        return None
    
    thresholds = config.VOLUME_THRESHOLDS
    
    # Should already be filtered out, but defensive check
    if avg_daily_volume < thresholds["illiquid"]:
        logger.warning(
            f"classify_liquidity called with illiquid volume: {avg_daily_volume}"
        )
        return None
    
    if avg_daily_volume < thresholds["very_low"]:
        return LiquidityBucket.VERY_LOW
    
    if avg_daily_volume < thresholds["low"]:
        return LiquidityBucket.LOW
    
    if avg_daily_volume < thresholds["acceptable"]:
        return LiquidityBucket.ACCEPTABLE
    
    return LiquidityBucket.HIGH


def is_illiquid(avg_daily_volume: Optional[float]) -> bool:
    """
    Check if a symbol should be excluded due to low liquidity.
    
    Args:
        avg_daily_volume: Average daily trading volume.
        
    Returns:
        True if symbol should be excluded as illiquid.
    """
    if avg_daily_volume is None:
        return True  # No volume data = treat as illiquid
    
    return avg_daily_volume < config.VOLUME_THRESHOLDS["illiquid"]
