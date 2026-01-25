"""Historical Backfill - Fetcher (uses existing ingestor)"""
import logging
import time
from typing import Optional, Tuple
import pandas as pd
from . import config

logger = logging.getLogger(__name__)

class HistoricalFetcher:
    """Fetches daily OHLCV using existing Alpha Vantage ingestor."""
    
    def __init__(self):
        self.delay = config.DELAY_SECONDS
    
    def fetch_symbol(self, symbol: str) -> Tuple[bool, Optional[int], str]:
        """
        Fetch daily history for a symbol.
        Returns: (success, depth_days, error_or_info)
        """
        try:
            from ingestion.api_ingestion.alpha_vantage.market_data_ingestor import USMarketIngestor
            from ingestion.api_ingestion.alpha_vantage.normalizer import USNormalizer
            
            ingestor = USMarketIngestor()
            normalizer = USNormalizer()
            
            # Fetch raw data
            result = ingestor.fetch_symbol_daily(symbol, full_history=False)
            
            if not result.get("success"):
                return False, None, result.get("error", "Unknown error")
            
            raw_path = result.get("raw_path")
            if not raw_path:
                return False, None, "No raw path returned"
            
            # Normalize to parquet
            staged_path = normalizer.normalize_daily(symbol, raw_path)
            if not staged_path:
                return False, None, "Normalization failed"
            
            # Count depth
            df = pd.read_parquet(staged_path)
            depth = len(df)
            start_date = str(df.index.min().date()) if hasattr(df.index, 'min') else "unknown"
            end_date = str(df.index.max().date()) if hasattr(df.index, 'max') else "unknown"
            
            return True, depth, f"{start_date} to {end_date}"
            
        except Exception as e:
            return False, None, str(e)
    
    def wait_rate_limit(self):
        """Wait between API calls."""
        time.sleep(self.delay)
