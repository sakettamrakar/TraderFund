import argparse
import time
import logging
from datetime import datetime, timedelta
from typing import List
from ingestion.api_ingestion.alpha_vantage.symbol_master import SymbolMaster
from ingestion.api_ingestion.alpha_vantage.market_data_ingestor import USMarketIngestor
from ingestion.api_ingestion.alpha_vantage.normalizer import USNormalizer
# from ingestion.api_ingestion.alpha_vantage.curator import USCurator # To be implemented
from ingestion.api_ingestion.alpha_vantage import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("US_Orchestrator")

class TokenBucket:
    def __init__(self, capacity=config.BUCKET_CAPACITY, refill_rate=config.REFILL_RATE_SECONDS):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
    
    def wait_for_token(self):
        """Blocks until a token is available."""
        while True:
            now = time.time()
            elapsed = now - self.last_refill
            
            # Refill logic
            new_tokens = elapsed / self.refill_rate
            if new_tokens >= 1:
                self.tokens = min(self.capacity, self.tokens + new_tokens)
                self.last_refill = now
                
            if self.tokens >= 1:
                self.tokens -= 1
                return # Acquired
            
            # Sleep needed amount
            needed = 1 - self.tokens
            sleep_time = needed * self.refill_rate
            time.sleep(min(sleep_time, 1.0)) # Sleep in small chunks to be responsive

class RateLimitOrchestrator:
    def __init__(self):
        self.bucket = TokenBucket()
        self.master = SymbolMaster()
        self.ingestor = USMarketIngestor()
        self.daily_limit = config.MAX_CALLS_PER_DAY
        self.call_count = 0

    def run_ingestion_batch(self, symbols: List[str], label: str = "Batch"):
        """
        Runs ingestion for a list of symbols until done or daily limit reached.
        """
        logger.info(f"Starting {label}: {len(symbols)} symbols.")
        
        errors = 0
        
        for symbol in symbols:
            # Check Daily Limit
            if self.call_count >= self.daily_limit:
                logger.critical("Daily API Limit Reached. Stopping batch.")
                break
                
            # Wait for Pacing
            self.bucket.wait_for_token()
            
            # Execute
            result = self.ingestor.fetch_symbol_daily(symbol, full_history=False)
            self.call_count += 1
            
            # Handle Result
            if result['success']:
                logger.info(f"[{self.call_count}] FETCH OK: {symbol}")
            else:
                status = result['status']
                msg = result['msg']
                if status == 'RATE_LIMIT':
                    logger.warning(f"RATE LIMIT NOTE for {symbol}: {msg}. Backing off 60s.")
                    time.sleep(60) # Hard backoff
                elif status == 'API_ERROR':
                    logger.error(f"API Error {symbol}: {msg}")
                    errors += 1
                else:
                    logger.warning(f"Fetch Failed {symbol}: {msg}")
                    errors += 1
                    
        logger.info(f"Batch Complete. Calls made: {self.call_count}. Errors: {errors}")

    def run_daily_batch(self, tiers: List[str]):
        """Runs ingestion for specific tiers."""
        symbols_dicts = self.master.get_symbols_by_tier(tiers)
        symbols = [s['symbol'] for s in symbols_dicts]
        self.run_ingestion_batch(symbols, label=f"Tiers {tiers}")

def main():
    parser = argparse.ArgumentParser(description="US Market Orchestrator")
    parser.add_argument('task', choices=['refresh-master', 'symbols', 'ingest', 'daily-ingest', 'normalize', 'full-run'])
    parser.add_argument('--tiers', type=str, default='A,B', help="Comma separated tiers (A,B,C)")
    parser.add_argument('--symbols', type=str, help="Comma separated symbols (AAPL,MSFT)")
    parser.add_argument('--date', type=str, help="Target date for normalization (YYYY-MM-DD)")
    
    args = parser.parse_args()
    
    orch = RateLimitOrchestrator()
    
    if args.task in ['refresh-master', 'symbols']:
        orch.master.fetch_and_update()
        
    elif args.task == 'ingest':
        if not args.symbols:
            logger.error("Error: --symbols required for 'ingest' task.")
            return
        symbols = [s.strip().upper() for s in args.symbols.split(',')]
        orch.run_ingestion_batch(symbols, label="Manual Ingest")
        
    elif args.task == 'daily-ingest':
        tiers = args.tiers.split(',')
        orch.run_daily_batch(tiers)
        
    elif args.task == 'normalize':
        # Passive Normalizer Call
        date_str = args.date if args.date else datetime.utcnow().strftime('%Y-%m-%d')
        logger.info(f"Running normalization for {date_str}")
        USNormalizer().run_normalization_batch(date_str)
        
    elif args.task == 'full-run':
        # Sequence: Master -> Ingest -> Normalize
        logger.info("Starting Full Run")
        orch.master.fetch_and_update()
        tiers = args.tiers.split(',')
        orch.run_daily_batch(tiers)
        USNormalizer().run_normalization_batch(datetime.utcnow().strftime('%Y-%m-%d'))

if __name__ == "__main__":
    main()
