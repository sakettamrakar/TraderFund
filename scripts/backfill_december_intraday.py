import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta, date
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from ingestion.api_ingestion.angel_smartapi.auth import AngelAuthManager
from ingestion.api_ingestion.angel_smartapi.config import config
from ingestion.api_ingestion.angel_smartapi.market_data_ingestor import MarketDataIngestor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("BackfillDec2025")

def backfill():
    # Attempt to use historical credentials if available
    auth = AngelAuthManager(config, use_historical=config.validate_historical())
    if not auth.login():
        logger.error("Authentication failed. Use valid credentials in .env")
        return

    ingestor = MarketDataIngestor(auth_manager=auth)
    
    symbols = config.symbol_watchlist
    exchange = "NSE"
    
    # December 2025 range
    start_date = date(2025, 12, 1)
    end_date = date(2025, 12, 31)
    
    output_path = Path(config.intraday_ohlc_path)
    output_path.mkdir(parents=True, exist_ok=True)
    
    current_date = start_date
    while current_date <= end_date:
        # Skip weekends (5 = Saturday, 6 = Sunday)
        if current_date.weekday() >= 5:
            current_date += timedelta(days=1)
            continue
            
        date_str = current_date.strftime("%Y-%m-%d")
        logger.info(f"--- Processing {date_str} ---")
        
        # 09:15 to 15:30 IST
        from_time = datetime.combine(current_date, datetime.min.time().replace(hour=9, minute=15))
        to_time = datetime.combine(current_date, datetime.min.time().replace(hour=15, minute=30))
        
        # Fetch candles in a single batch for the day
        # Note: 1-minute data for one day is ~375 candles per symbol. 
        # Total for 10 symbols is ~3750 records. 
        # This is well within Angel API limits for a single day.
        
        candles = ingestor.fetch_candles(
            symbols=symbols,
            interval="ONE_MINUTE",
            exchange=exchange,
            from_time=from_time,
            to_time=to_time
        )
        
        if candles:
            # Group by symbol to save individual files
            for symbol in symbols:
                symbol_candles = [c for c in candles if c['symbol'] == symbol]
                if not symbol_candles:
                    continue
                
                # Sort candles by timestamp just in case
                symbol_candles.sort(key=lambda x: x['timestamp'])
                
                file_path = output_path / f"{exchange}_{symbol}_{date_str}.jsonl"
                
                with open(file_path, "w", encoding="utf-8") as f:
                    for record in symbol_candles:
                        f.write(json.dumps(record) + "\n")
                
                logger.info(f"  ✓ {symbol}: Saved {len(symbol_candles)} records to {file_path.name}")
        else:
            logger.warning(f"  ⚠️ No candles fetched for {date_str}")
            
        # Small delay between days
        time.sleep(1)
        current_date += timedelta(days=1)

    auth.logout()
    logger.info("Backfill completed.")

if __name__ == "__main__":
    backfill()
