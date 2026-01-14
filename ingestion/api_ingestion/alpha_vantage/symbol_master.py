import csv
import io
import logging
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime
from ingestion.api_ingestion.alpha_vantage.client import AlphaVantageClient
from ingestion.api_ingestion.alpha_vantage import config

logger = logging.getLogger(__name__)

class SymbolMaster:
    """
    Manages the universe of US Symbols.
    Merges live listing status with local metadata (priority, start dates).
    """
    
    COLUMNS = [
        'symbol', 'name', 'exchange', 'assetType', 
        'ipoDate', 'status', 'priority_tier', 'data_start_date', 'last_updated'
    ]

    def __init__(self):
        self.client = AlphaVantageClient()
        self.master_path = config.SYMBOLS_CSV_PATH
        self.allowed_exchanges = {'NYSE', 'NASDAQ', 'NYSE MKT', 'NYSE ARCA', 'BATS'}
        self.allowed_asset_types = {'Stock'}

    def _load_local_master(self) -> pd.DataFrame:
        if self.master_path.exists():
            return pd.read_csv(self.master_path)
        return pd.DataFrame(columns=self.COLUMNS)

    def fetch_and_update(self):
        """
        Fetches active listings, merges with local state, updates CSV.
        """
        logger.info("Fetching symbol listing status from Alpha Vantage...")
        
        try:
            csv_text = self.client.get_listing_status(state='active')
            # API returns: symbol,name,exchange,assetType,ipoDate,delistingDate,status
            api_df = pd.read_csv(io.StringIO(csv_text))
        except Exception as e:
            logger.error(f"Failed to fetch listing status: {e}")
            return

        # filter
        mask = (api_df['exchange'].isin(self.allowed_exchanges)) & \
               (api_df['assetType'].isin(self.allowed_asset_types))
        valid_df = api_df[mask].copy()

        # Load Local
        local_df = self._load_local_master()
        
        # Merge Logic: 
        # We want to keep local metadata (priority_tier, data_start_date) if it exists.
        # We assume 'symbol' is key.
        
        # Renaissance of validity: New set of symbols
        merged_list = []
        today_str = datetime.utcnow().strftime('%Y-%m-%d')

        # Convert local to dict for fast lookup
        local_map = local_df.set_index('symbol').to_dict('index')

        for _, row in valid_df.iterrows():
            sym = row['symbol']
            
            # Default values
            tier = 'C' # Standard rotation
            start_date = row['ipoDate']
            
            # Preserve local overrides
            if sym in local_map:
                existing = local_map[sym]
                if pd.notna(existing.get('priority_tier')):
                    tier = existing['priority_tier']
                if pd.notna(existing.get('data_start_date')):
                    start_date = existing['data_start_date']
            
            # Simple Tier Logic Override (Example: S&P 500 or Major Tech)
            # In a real system, we'd load an S&P list. Here we hardcode a few for demo.
            if sym in ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'SPY']:
                tier = 'A'
            elif sym in ['IBM', 'NVDA', 'META']:
                tier = 'B'

            merged_list.append({
                'symbol': sym,
                'name': row['name'],
                'exchange': row['exchange'],
                'assetType': row['assetType'],
                'ipoDate': row['ipoDate'],
                'status': 'Active',
                'priority_tier': tier,
                'data_start_date': start_date,
                'last_updated': today_str
            })

        # Create final DF
        final_df = pd.DataFrame(merged_list)
        
        # Sort by Tier (A, B, C) then Symbol
        final_df.sort_values(by=['priority_tier', 'symbol'], inplace=True)
        
        # Save
        self.master_path.parent.mkdir(parents=True, exist_ok=True)
        final_df.to_csv(self.master_path, index=False)
        logger.info(f"Saved {len(final_df)} symbols to {self.master_path}")

    def get_symbols_by_tier(self, tiers: List[str] = None) -> List[Dict]:
        """
        Returns list of symbol dicts filtering by tier.
        """
        df = self._load_local_master()
        if df.empty:
            return []
            
        if tiers:
            df = df[df['priority_tier'].isin(tiers)]
            
        return df.to_dict('records')

if __name__ == "__main__":
    SymbolMaster().fetch_and_update()
