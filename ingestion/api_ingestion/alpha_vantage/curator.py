import pandas as pd
from pathlib import Path
import logging
from ingestion.api_ingestion.alpha_vantage import config

logger = logging.getLogger(__name__)

class USCurator:
    """
    Promotes data from Staging -> Analytics.
    Enforces schema contracts and data quality.
    """
    def __init__(self):
        self.staging_dir = config.STAGING_DIR / "daily"
        self.analytics_dir = config.ANALYTICS_DIR / "prices" / "daily"
        self.analytics_dir.mkdir(parents=True, exist_ok=True)

    def curate_symbol(self, symbol: str):
        staging_path = self.staging_dir / f"{symbol}.parquet"
        if not staging_path.exists():
            # logger.warning(f"No staging data for {symbol}")
            return False

        try:
            df = pd.read_parquet(staging_path)
            
            # 1. Deduplication
            df = df[~df.index.duplicated(keep='last')]
            
            # 2. Schema Validation / Type Enforcement
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            if not all(col in df.columns for col in required_cols):
                logger.error(f"Schema Mismatch {symbol}: Missing columns")
                return False
                
            # 3. Sanity Checks
            # e.g. Negative prices
            if (df[required_cols] < 0).any().any():
                logger.warning(f"Data Quality Warning {symbol}: Negative prices detected")
            
            # 4. Partitioning Logic
            # Analysis layer often partitioned by Symbol or Date. 
            # For backtesting ease, 'By Symbol' single file is often best for mid-size data.
            # Storing as single parquet file per symbol in analytics.
            
            out_path = self.analytics_dir / f"{symbol}.parquet"
            df.to_parquet(out_path, compression='snappy')
            return True
            
        except Exception as e:
            logger.error(f"Curate Failed {symbol}: {e}")
            return False

    def run_curation_batch(self):
        """
        Iterates all staged files and updates analytics layer.
        """
        files = list(self.staging_dir.glob("*.parquet"))
        logger.info(f"Curating {len(files)} symbols...")
        
        count = 0
        for f in files:
            sym = f.stem
            if self.curate_symbol(sym):
                count += 1
                
        logger.info(f"Curation Complete. Promoted {count}/{len(files)} symbols.")

if __name__ == "__main__":
    USCurator().run_curation_batch()
