"""
Stage 0: Universe Hygiene - Eligibility Filter

Core filtering engine that evaluates each symbol and produces eligibility status.
This is the main orchestration logic for Stage 0.
"""

import logging
from datetime import date
from typing import Dict, List, Optional, Tuple

import pandas as pd

from . import config
from .models import (
    EligibilityRecord,
    EligibilityStatus,
    ExclusionReason,
    LiquidityBucket,
    PriceBucket,
)
from .liquidity_scorer import classify_liquidity, is_illiquid
from .price_classifier import classify_price, is_penny_stock

logger = logging.getLogger(__name__)


class EligibilityFilter:
    """
    Deterministic eligibility filter for US equity universe.
    
    Applies structural and liquidity criteria to reduce the universe
    from ~7,000 to 1,000-2,000 eligible symbols.
    
    This class does NOT:
    - Compute technical indicators
    - Detect price patterns
    - Generate trading signals
    - Apply subjective judgment
    """
    
    def __init__(
        self,
        exchange_allowlist: Optional[List[str]] = None,
        asset_type_allowlist: Optional[List[str]] = None,
    ):
        """
        Initialize the eligibility filter.
        
        Args:
            exchange_allowlist: List of allowed exchanges. Defaults to config.
            asset_type_allowlist: List of allowed asset types. Defaults to config.
        """
        self.exchange_allowlist = set(
            exchange_allowlist or config.EXCHANGE_ALLOWLIST
        )
        self.asset_type_allowlist = set(
            asset_type_allowlist or config.ASSET_TYPE_ALLOWLIST
        )
        self.evaluation_date = date.today()
    
    def evaluate_symbol(
        self,
        symbol: str,
        exchange: str,
        asset_type: str,
        delisting_date: Optional[str],
        price_data: Optional[pd.DataFrame],
    ) -> EligibilityRecord:
        """
        Evaluate a single symbol for eligibility.
        
        Args:
            symbol: Ticker symbol.
            exchange: Exchange code (NYSE, NASDAQ, etc.).
            asset_type: Asset type (Stock, ETF, etc.).
            delisting_date: Delisting date if symbol is delisted.
            price_data: DataFrame with columns [timestamp, close, volume].
                        Should contain data for evaluation window.
        
        Returns:
            EligibilityRecord with eligibility status and reason.
        """
        # Check 1: Exchange allowlist
        if exchange not in self.exchange_allowlist:
            return EligibilityRecord.create_excluded(
                symbol=symbol,
                exchange=exchange,
                reason=ExclusionReason.EXCHANGE_NOT_ALLOWED,
                evaluated_date=self.evaluation_date,
            )
        
        # Check 2: Asset type allowlist
        if asset_type not in self.asset_type_allowlist:
            return EligibilityRecord.create_excluded(
                symbol=symbol,
                exchange=exchange,
                reason=ExclusionReason.ASSET_TYPE_NOT_EQUITY,
                evaluated_date=self.evaluation_date,
            )
        
        # Check 3: Delisted status
        if delisting_date and pd.notna(delisting_date):
            return EligibilityRecord.create_excluded(
                symbol=symbol,
                exchange=exchange,
                reason=ExclusionReason.DELISTED,
                evaluated_date=self.evaluation_date,
            )
        
        # Check 4: Price data availability
        if price_data is None or price_data.empty:
            return EligibilityRecord.create_excluded(
                symbol=symbol,
                exchange=exchange,
                reason=ExclusionReason.NO_PRICE_DATA,
                evaluated_date=self.evaluation_date,
            )
        
        # Compute metrics
        trading_days = len(price_data)
        avg_volume = price_data["volume"].mean() if "volume" in price_data.columns else None
        avg_price = price_data["close"].mean() if "close" in price_data.columns else None
        
        # Check 5: Activity threshold (trading days in window)
        if trading_days < config.TRADING_DAYS_MIN:
            return EligibilityRecord.create_excluded(
                symbol=symbol,
                exchange=exchange,
                reason=ExclusionReason.INACTIVE,
                evaluated_date=self.evaluation_date,
                trading_days=trading_days,
                avg_volume=avg_volume,
                avg_price=avg_price,
            )
        
        # Check 6: Penny stock
        if is_penny_stock(avg_price):
            return EligibilityRecord.create_excluded(
                symbol=symbol,
                exchange=exchange,
                reason=ExclusionReason.PENNY_STOCK,
                evaluated_date=self.evaluation_date,
                trading_days=trading_days,
                avg_volume=avg_volume,
                avg_price=avg_price,
            )
        
        # Check 7: Illiquidity
        if is_illiquid(avg_volume):
            return EligibilityRecord.create_excluded(
                symbol=symbol,
                exchange=exchange,
                reason=ExclusionReason.ILLIQUID,
                evaluated_date=self.evaluation_date,
                trading_days=trading_days,
                avg_volume=avg_volume,
                avg_price=avg_price,
            )
        
        # Symbol is eligible - classify into buckets
        liquidity_bucket = classify_liquidity(avg_volume)
        price_bucket = classify_price(avg_price)
        
        return EligibilityRecord.create_eligible(
            symbol=symbol,
            exchange=exchange,
            liquidity=liquidity_bucket,
            price=price_bucket,
            avg_volume=avg_volume,
            avg_price=avg_price,
            trading_days=trading_days,
            evaluated_date=self.evaluation_date,
        )
    
    def evaluate_universe(
        self,
        symbols_df: pd.DataFrame,
        price_data_loader,
    ) -> List[EligibilityRecord]:
        """
        Evaluate the entire symbol universe.
        
        Args:
            symbols_df: DataFrame with columns [symbol, exchange, assetType, delistingDate].
            price_data_loader: Callable that takes symbol and returns price DataFrame.
        
        Returns:
            List of EligibilityRecord for all symbols.
        """
        records = []
        total = len(symbols_df)
        
        for idx, row in symbols_df.iterrows():
            symbol = row["symbol"]
            
            if idx % 500 == 0:
                logger.info(f"Evaluating symbol {idx + 1}/{total}: {symbol}")
            
            # Load price data for this symbol
            try:
                price_data = price_data_loader(symbol)
            except Exception as e:
                logger.warning(f"Failed to load price data for {symbol}: {e}")
                price_data = None
            
            record = self.evaluate_symbol(
                symbol=symbol,
                exchange=row.get("exchange", ""),
                asset_type=row.get("assetType", "Stock"),
                delisting_date=row.get("delistingDate"),
                price_data=price_data,
            )
            records.append(record)
        
        return records
    
    def summarize_results(self, records: List[EligibilityRecord]) -> Dict:
        """
        Generate summary statistics for eligibility results.
        
        Args:
            records: List of eligibility records.
            
        Returns:
            Dictionary with summary statistics.
        """
        total = len(records)
        eligible = sum(1 for r in records if r.eligibility_status == EligibilityStatus.ELIGIBLE.value)
        excluded = total - eligible
        
        # Count by exclusion reason
        exclusion_counts = {}
        for r in records:
            if r.exclusion_reason:
                exclusion_counts[r.exclusion_reason] = exclusion_counts.get(r.exclusion_reason, 0) + 1
        
        # Count by liquidity bucket (eligible only)
        liquidity_counts = {}
        for r in records:
            if r.liquidity_bucket:
                liquidity_counts[r.liquidity_bucket] = liquidity_counts.get(r.liquidity_bucket, 0) + 1
        
        # Count by price bucket (eligible only)
        price_counts = {}
        for r in records:
            if r.price_bucket:
                price_counts[r.price_bucket] = price_counts.get(r.price_bucket, 0) + 1
        
        return {
            "total_symbols": total,
            "eligible_count": eligible,
            "excluded_count": excluded,
            "eligibility_rate": eligible / total if total > 0 else 0,
            "exclusion_breakdown": exclusion_counts,
            "liquidity_breakdown": liquidity_counts,
            "price_breakdown": price_counts,
        }
