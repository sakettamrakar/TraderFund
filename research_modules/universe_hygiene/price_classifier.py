"""
Stage 0: Universe Hygiene - Price Classifier

Classifies symbols into price range buckets.
"""

import logging
from typing import Optional

from . import config
from .models import PriceBucket

logger = logging.getLogger(__name__)


def classify_price(avg_price: Optional[float]) -> Optional[PriceBucket]:
    """
    Classify a symbol's price bucket based on average close price.
    
    Args:
        avg_price: Average closing price over evaluation window.
        
    Returns:
        PriceBucket enum value, or None if price data unavailable.
        
    Note:
        Symbols with price below PENNY_CUTOFF should be excluded
        before calling this function. This function only classifies
        eligible symbols into buckets.
    """
    if avg_price is None:
        return None
    
    thresholds = config.PRICE_THRESHOLDS
    
    # Should already be filtered out, but defensive check
    if avg_price < thresholds["penny_cutoff"]:
        logger.warning(
            f"classify_price called with penny stock price: {avg_price}"
        )
        return None
    
    if avg_price < thresholds["extreme_low"]:
        return PriceBucket.EXTREME_LOW
    
    if avg_price < thresholds["low"]:
        return PriceBucket.LOW
    
    if avg_price < thresholds["acceptable"]:
        return PriceBucket.ACCEPTABLE
    
    return PriceBucket.HIGH


def is_penny_stock(avg_price: Optional[float]) -> bool:
    """
    Check if a symbol should be excluded as a penny stock.
    
    Args:
        avg_price: Average closing price.
        
    Returns:
        True if symbol should be excluded as penny stock.
    """
    if avg_price is None:
        return False  # No price data handled separately
    
    return avg_price < config.PRICE_THRESHOLDS["penny_cutoff"]
