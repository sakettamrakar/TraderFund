"""Universe Expansion - Expander (filters and creates symbol master)"""
import logging
from typing import List
import pandas as pd
from . import config
from .models import SymbolMaster

logger = logging.getLogger(__name__)

class UniverseExpander:
    """Expands symbol universe from CSV to filtered master."""
    
    def __init__(self):
        self.min_symbols = config.MIN_SYMBOLS
        self.max_symbols = config.MAX_SYMBOLS
        self.valid_exchanges = config.VALID_EXCHANGES
        self.valid_types = config.VALID_ASSET_TYPES
    
    def load_source_symbols(self) -> pd.DataFrame:
        """Load symbols from CSV."""
        if not config.SYMBOLS_CSV.exists():
            raise FileNotFoundError(f"Symbols CSV not found: {config.SYMBOLS_CSV}")
        
        df = pd.read_csv(config.SYMBOLS_CSV)
        logger.info(f"Loaded {len(df)} symbols from CSV")
        return df
    
    def filter_symbols(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply filtering rules."""
        original = len(df)
        
        # Identify manual inclusions present in the source DF
        manual_present = df[df["symbol"].isin(config.MANUAL_INCLUSIONS)].copy()
        
        # If any manual inclusions are MISSING from source, we must synthesise them
        # (This handles the case where BDSX might not be in the CSV source)
        for ticker in config.MANUAL_INCLUSIONS:
            if ticker not in manual_present["symbol"].values:
                logger.info(f"Injecting missing manual symbol: {ticker}")
                new_row = {
                    "symbol": ticker,
                    "name": f"{ticker} [Manual]",
                    "exchange": "NASDAQ", # Default guess
                    "assetType": "Stock",
                    "ipoDate": "2000-01-01",
                    "status": "Active"
                }
                manual_present = pd.concat([manual_present, pd.DataFrame([new_row])], ignore_index=True)

        logger.info(f"Manual inclusions ready: {len(manual_present)}")

        # Filter regular universe
        # Filter by status
        df = df[df["status"] == "Active"]
        # Filter by exchange
        df = df[df["exchange"].isin(self.valid_exchanges)]
        # Filter by asset type
        df = df[df["assetType"].isin(self.valid_types)]
        
        # Limit to max symbols (minus manual slots)
        remaining_slots = self.max_symbols - len(manual_present)
        df_limited = df.sort_values("symbol").head(remaining_slots)
        
        # Combine
        combined = pd.concat([manual_present, df_limited]).drop_duplicates(subset=["symbol"])
        
        logger.info(f"Final Selection: {len(combined)} (Manual: {len(manual_present)})")
        return combined
    
    def create_master_records(self, df: pd.DataFrame) -> List[SymbolMaster]:
        """Convert filtered DataFrame to SymbolMaster records."""
        records = []
        for _, row in df.iterrows():
            try:
                record = SymbolMaster.from_csv_row(row.to_dict())
                records.append(record)
            except Exception as e:
                logger.warning(f"Error processing {row.get('symbol', 'unknown')}: {e}")
        
        logger.info(f"Created {len(records)} master records")
        return records
    
    def save_master(self, records: List[SymbolMaster]):
        """Save to parquet."""
        config.SYMBOL_MASTER_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        df = pd.DataFrame([r.to_dict() for r in records])
        df.to_parquet(config.SYMBOL_MASTER_PATH, index=False)
        logger.info(f"Saved {len(records)} symbols to {config.SYMBOL_MASTER_PATH}")
    
    def expand(self) -> List[SymbolMaster]:
        """Run full expansion pipeline."""
        df = self.load_source_symbols()
        df = self.filter_symbols(df)
        records = self.create_master_records(df)
        self.save_master(records)
        return records
