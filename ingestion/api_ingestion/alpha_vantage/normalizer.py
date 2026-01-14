import json
import logging
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from ingestion.api_ingestion.alpha_vantage import config

# Configure logging
logger = logging.getLogger(__name__)

class USNormalizer:
    def __init__(self):
        self.staging_dir = config.STAGING_DIR / "daily"
        self.staging_dir.mkdir(parents=True, exist_ok=True)

    def _parse_daily_json(self, data: Dict[str, Any]) -> pd.DataFrame:
        """
        Converts Alpha Vantage Daily Adjusted JSON to DataFrame.
        """
        ts_key = "Time Series (Daily)"
        if ts_key not in data:
            raise ValueError(f"Key '{ts_key}' not found in data.")

        # Load into DataFrame (Orientation: index is date string, columns are fields)
        df = pd.DataFrame.from_dict(data[ts_key], orient='index')
        
        # Renaissance mapping
        # "1. open": "119.37", ...
        rename_map = {
            "1. open": "open",
            "2. high": "high",
            "3. low": "low",
            "4. close": "close",
            "5. volume": "volume"
        }
        df.rename(columns=rename_map, inplace=True)
        
        # Type Conversion
        float_cols = ['open', 'high', 'low', 'close']
        for col in float_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce').fillna(0).astype('int64')

        # Index Handling
        df.index = pd.to_datetime(df.index)
        df.index.name = 'timestamp'
        df.sort_index(inplace=True)
        
        # Localize to UTC (Assuming AV daily dates are market close dates, usually timezone naive in JSON)
        # We implicitly treat them as close-of-day UTC for simplicity or market-local. 
        # For strict correctness we might assign US/Eastern closing time, but let's stick to UTC midnight for daily dates
        # or just timezone aware UTC.
        if df.index.tz is None:
            df.index = df.index.tz_localize('UTC')
        else:
            df.index = df.index.tz_convert('UTC')
            
        return df

    def normalize_file(self, json_path: Path):
        """
        Reads a raw JSON file and writes a parquet file to staging.
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract symbol from filename or metadata
            # Filename format: SYMBOL_daily_adjusted.json
            filename_stem = json_path.stem
            symbol = filename_stem.split('_')[0]
            
            df = self._parse_daily_json(data)
            df['symbol'] = symbol
            
            # Reorder columns
            cols = ['symbol', 'open', 'high', 'low', 'close', 'volume']
            df = df[cols]
            
            # Save to Parquet
            output_path = self.staging_dir / f"{symbol}.parquet"
            df.to_parquet(output_path, compression='snappy')
            
            # logger.info(f"Normalized {symbol} -> {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to normalize {json_path}: {e}")
            return False

    def normalize_daily(self, symbol: str, raw_path: str) -> Optional[str]:
        """Wrapper for single-file normalization returning output path."""
        path = Path(raw_path)
        if self.normalize_file(path):
            return str(self.staging_dir / f"{symbol}.parquet")
        return None

    def run_normalization_batch(self, date_str: str):
        """
        Normalizes all files for a specific crawl date.
        """
        raw_date_dir = config.RAW_BASE_DIR / date_str
        if not raw_date_dir.exists():
            logger.error(f"Raw directory not found: {raw_date_dir}")
            return

        json_files = list(raw_date_dir.glob("*.json"))
        logger.info(f"Found {len(json_files)} files to normalize for {date_str}")
        
        count = 0
        for f in json_files:
            if self.normalize_file(f):
                count += 1
                
        logger.info(f"Normalization Complete. Processed {count}/{len(json_files)} files.")

if __name__ == "__main__":
    # Dry run
    from datetime import datetime
    today = datetime.utcnow().strftime('%Y-%m-%d')
    norm = USNormalizer()
    norm.run_normalization_batch(today)
