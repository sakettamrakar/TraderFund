"""
US Universe Metadata Ingestor

Ingests per-symbol reference data using Alpha Vantage GLOBAL_QUOTE endpoint.
Provides minimum required data for Stage 0 (Universe Hygiene) validation.

This is REFERENCE DATA only - no indicators, signals, or narratives.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

import pandas as pd

from ingestion.api_ingestion.alpha_vantage.client import AlphaVantageClient
from ingestion.api_ingestion.alpha_vantage import config

logger = logging.getLogger(__name__)


@dataclass
class SymbolMetadata:
    """
    Schema for universe metadata record.
    This is the contract between ingestion and Stage 0.
    """
    symbol: str
    exchange: str
    instrument_type: str
    listing_status: str
    last_close_price: Optional[float]
    last_trade_volume: Optional[int]
    rolling_avg_volume: Optional[float]  # Computed locally if available
    last_trade_date: Optional[str]
    data_source: str
    ingestion_timestamp: str
    
    def to_dict(self) -> dict:
        return asdict(self)


class MetadataIngestor:
    """
    Ingests symbol-level reference data for Stage 0 consumption.
    
    Uses GLOBAL_QUOTE endpoint to fetch:
    - Last close price
    - Last trade volume
    - Last trade date
    """
    
    def __init__(self):
        self.client = AlphaVantageClient()
        self.ingestion_time = datetime.utcnow().isoformat()
    
    def fetch_symbol_metadata(
        self,
        symbol: str,
        exchange: str = "",
        asset_type: str = "Stock",
    ) -> SymbolMetadata:
        """
        Fetch metadata for a single symbol via GLOBAL_QUOTE.
        
        Args:
            symbol: Ticker symbol
            exchange: Exchange code (from symbols.csv)
            asset_type: Asset type (from symbols.csv)
            
        Returns:
            SymbolMetadata record (may have null fields if fetch fails)
        """
        try:
            data = self.client.get_quote(symbol)
            
            # Check for API errors
            if "Note" in data:
                logger.warning(f"Rate limit hit for {symbol}: {data['Note']}")
                return self._create_empty_record(symbol, exchange, asset_type, "rate_limit")
            
            if "Error Message" in data:
                logger.warning(f"API error for {symbol}: {data['Error Message']}")
                return self._create_empty_record(symbol, exchange, asset_type, "api_error")
            
            quote = data.get("Global Quote", {})
            if not quote:
                logger.debug(f"Empty quote for {symbol}")
                return self._create_empty_record(symbol, exchange, asset_type, "empty")
            
            # Parse quote data
            # GLOBAL_QUOTE fields: 01. symbol, 02. open, 03. high, 04. low, 
            # 05. price, 06. volume, 07. latest trading day, 08. previous close,
            # 09. change, 10. change percent
            
            last_price = self._safe_float(quote.get("05. price"))
            last_volume = self._safe_int(quote.get("06. volume"))
            last_date = quote.get("07. latest trading day")
            
            return SymbolMetadata(
                symbol=symbol,
                exchange=exchange,
                instrument_type=asset_type,
                listing_status="active",  # If we got data, assume active
                last_close_price=last_price,
                last_trade_volume=last_volume,
                rolling_avg_volume=None,  # Would need historical data
                last_trade_date=last_date,
                data_source="alpha_vantage",
                ingestion_timestamp=self.ingestion_time,
            )
            
        except Exception as e:
            logger.error(f"Exception fetching {symbol}: {e}")
            return self._create_empty_record(symbol, exchange, asset_type, "exception")
    
    def _create_empty_record(
        self,
        symbol: str,
        exchange: str,
        asset_type: str,
        reason: str,
    ) -> SymbolMetadata:
        """Create a record with null data fields."""
        return SymbolMetadata(
            symbol=symbol,
            exchange=exchange,
            instrument_type=asset_type,
            listing_status="unknown",
            last_close_price=None,
            last_trade_volume=None,
            rolling_avg_volume=None,
            last_trade_date=None,
            data_source=f"alpha_vantage:{reason}",
            ingestion_timestamp=self.ingestion_time,
        )
    
    @staticmethod
    def _safe_float(value: Any) -> Optional[float]:
        """Safely convert to float."""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def _safe_int(value: Any) -> Optional[int]:
        """Safely convert to int."""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None


def save_metadata_to_parquet(
    records: List[SymbolMetadata],
    output_path=None,
) -> None:
    """
    Save metadata records to Parquet file.
    
    Args:
        records: List of SymbolMetadata records
        output_path: Override default output path
    """
    path = output_path or config.METADATA_PARQUET_PATH
    
    data = [r.to_dict() for r in records]
    df = pd.DataFrame(data)
    
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
    
    logger.info(f"Saved {len(df)} metadata records to {path}")
