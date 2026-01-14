import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Union
from ingestion.api_ingestion.alpha_vantage.client import AlphaVantageClient
from ingestion.api_ingestion.alpha_vantage import config

logger = logging.getLogger(__name__)

class USMarketIngestor:
    """
    Passive ingestor.
    Responsible for:
    1. Calling Client
    2. saving Raw JSON
    3. Returning status to Orchestrator
    """
    def __init__(self):
        self.client = AlphaVantageClient()
        self.today_str = datetime.utcnow().strftime('%Y-%m-%d')
        self.raw_dir = config.RAW_BASE_DIR / self.today_str

    def _save_raw(self, symbol: str, function: str, data: Dict):
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{symbol}_{function}.json"
        with open(self.raw_dir / filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def fetch_symbol_daily(self, symbol: str, full_history: bool = False) -> Dict[str, Any]:
        """
        Fetches daily data for a single symbol and saves it.
        Returns result dict: {'success': bool, 'note': str}
        """
        output_size = 'full' if full_history else 'compact'
        
        try:
            data = self.client.get_daily(symbol, outputsize=output_size)
            
            # Check for API Notes/Errors
            if "Note" in data:
                return {'success': False, 'status': 'RATE_LIMIT', 'msg': data['Note']}
            if "Error Message" in data:
                return {'success': False, 'status': 'API_ERROR', 'msg': data['Error Message']}
            if "Time Series (Daily)" not in data:
                # Could be empty symbol or unknown response
                return {'success': False, 'status': 'EMPTY', 'msg': f"Keys: {list(data.keys())}"}

            self._save_raw(symbol, 'daily', data)
            raw_path = str(self.raw_dir / f"{symbol}_daily.json")
            return {'success': True, 'status': 'OK', 'msg': 'Saved', 'raw_path': raw_path}

        except Exception as e:
            logger.error(f"Ingest Error {symbol}: {e}")
            return {'success': False, 'status': 'EXCEPTION', 'msg': str(e)}
