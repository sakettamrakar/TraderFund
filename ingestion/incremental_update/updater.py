"""Incremental Update - Updater"""
import logging
import time
from typing import List, Tuple, Optional, Dict
from datetime import datetime
import pandas as pd
from . import config
from .models import UpdateStatus

logger = logging.getLogger(__name__)

class IncrementalUpdater:
    """Handles incremental daily updates."""
    
    def __init__(self):
        self.delay = config.DELAY_SECONDS
        self.tracker: Dict[str, UpdateStatus] = {}
        self._load_tracker()
    
    def _load_tracker(self):
        if config.UPDATE_TRACKER.exists():
            df = pd.read_parquet(config.UPDATE_TRACKER)
            for _, row in df.iterrows():
                self.tracker[row["symbol"]] = UpdateStatus(
                    symbol=row["symbol"],
                    last_attempt=row["last_attempt"],
                    last_success=row.get("last_success"),
                    status=row["status"],
                    error_reason=row.get("error_reason"),
                )
    
    def _save_tracker(self):
        config.UPDATE_TRACKER.parent.mkdir(parents=True, exist_ok=True)
        records = [s.to_dict() for s in self.tracker.values()]
        pd.DataFrame(records).to_parquet(config.UPDATE_TRACKER, index=False)
    
    def get_eligible_symbols(self, limit: int = None) -> List[str]:
        """Get symbols eligible for incremental update (not already updated today)."""
        if not config.BACKFILL_TRACKER.exists():
            return []
        
        backfill = pd.read_parquet(config.BACKFILL_TRACKER)
        eligible_master = set(backfill[backfill["status"] == "success"]["symbol"].tolist())
        
        # Filter out those already attempted today
        today = datetime.utcnow().date().isoformat()
        already_attempted = set()
        for sym, status in self.tracker.items():
            if status.last_attempt and status.last_attempt.split("T")[0] == today:
                 already_attempted.add(sym)
        
        eligible = sorted(list(eligible_master - already_attempted))
        
        if limit:
            eligible = eligible[:limit]
        
        return eligible
    
    def get_last_stored_date(self, symbol: str) -> Optional[str]:
        """Get last date in staged data."""
        path = config.STAGING_PATH / f"{symbol}.parquet"
        if not path.exists():
            return None
        try:
            df = pd.read_parquet(path)
            return str(df.index.max().date())
        except:
            return None
    
    def fetch_latest(self, symbol: str) -> Tuple[bool, str]:
        """Fetch latest candle and append if newer."""
        try:
            from ingestion.api_ingestion.alpha_vantage.client import AlphaVantageClient
            
            client = AlphaVantageClient()
            data = client.get_daily(symbol, outputsize="compact")
            
            if "Time Series (Daily)" not in data:
                return False, data.get("Note", "No data returned")
            
            ts = data["Time Series (Daily)"]
            latest_date = max(ts.keys())
            
            last_stored = self.get_last_stored_date(symbol)
            if last_stored and latest_date <= last_stored:
                return True, f"Up to date ({last_stored})"
            
            # Append new data
            path = config.STAGING_PATH / f"{symbol}.parquet"
            if path.exists():
                df = pd.read_parquet(path)
                new_row = {
                    "open": float(ts[latest_date]["1. open"]),
                    "high": float(ts[latest_date]["2. high"]),
                    "low": float(ts[latest_date]["3. low"]),
                    "close": float(ts[latest_date]["4. close"]),
                    "volume": int(ts[latest_date]["5. volume"]),
                }
                new_df = pd.DataFrame([new_row], index=pd.to_datetime([latest_date], utc=True))
                df = pd.concat([df, new_df]).sort_index()
                df = df[~df.index.duplicated(keep='last')]
                df.to_parquet(path)
                
            return True, f"Updated to {latest_date}"
            
        except Exception as e:
            return False, str(e)
    
    def update_symbol(self, symbol: str) -> UpdateStatus:
        """Update a single symbol."""
        success, info = self.fetch_latest(symbol)
        
        if success:
            if "Up to date" in info:
                status = UpdateStatus.up_to_date(symbol)
            else:
                status = UpdateStatus.success(symbol)
        else:
            status = UpdateStatus.failed(symbol, info)
        
        self.tracker[symbol] = status
        self._save_tracker()
        return status
    
    def wait_rate_limit(self):
        time.sleep(self.delay)
