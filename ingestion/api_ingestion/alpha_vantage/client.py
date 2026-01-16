import requests
import logging
from typing import Dict, Any, Optional
from ingestion.api_ingestion.alpha_vantage import config
from ingestion.core.key_manager import ApiKeyManager

logger = logging.getLogger(__name__)

class AlphaVantageClient:
    """
    Thin client for Alpha Vantage API with Key Pool Management.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.static_key = api_key
        self.manager = ApiKeyManager()
        self.base_url = config.BASE_URL

    def _make_request(self, params: Dict[str, Any]) -> requests.Response:
        """
        Execute raw HTTP request with automatic key rotation.
        """
        if self.static_key:
            key = self.static_key
        else:
            # Dynamically get a fresh key for each request
            key = self.manager.get_active_key()
            
        params['apikey'] = key
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            # Record usage only if using the pool
            if not self.static_key:
                self.manager.record_usage(key)
            
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP Request failed: {e}")
            raise e

    def get_listing_status(self, date: Optional[str] = None, state: str = 'active') -> str:
        """Fetch LISTING_STATUS CSV string."""
        params = {'function': 'LISTING_STATUS', 'state': state}
        if date:
            params['date'] = date
        return self._make_request(params).text

    def get_daily(self, symbol: str, outputsize: str = 'compact') -> Dict[str, Any]:
        """Fetch TIME_SERIES_DAILY (Free Tier)."""
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'outputsize': outputsize
        }
        return self._make_request(params).json()

    def get_intraday(self, symbol: str, interval: str = '5min', outputsize: str = 'compact') -> Dict[str, Any]:
        """Fetch TIME_SERIES_INTRADAY (Free Tier)."""
        params = {
            'function': 'TIME_SERIES_INTRADAY',
            'symbol': symbol,
            'interval': interval,
            'outputsize': outputsize
        }
        return self._make_request(params).json()

    def get_quote(self, symbol: str) -> Dict[str, Any]:
        """Fetch GLOBAL_QUOTE."""
        params = {'function': 'GLOBAL_QUOTE', 'symbol': symbol}
        return self._make_request(params).json()
