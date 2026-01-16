
import os
import time
import logging
import threading
from dotenv import load_dotenv
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class KeyPoolManager:
    """
    Manages a pool of AlphaVantage API Keys with aggressive rotation and usage tracking.
    Enforces Free Tier limits: 5 calls/min and 500 calls/day per key.
    """
    
    # Free Tier Limits
    MAX_CALLS_PER_MIN = 5
    MAX_CALLS_PER_DAY = 500
    
    def __init__(self):
        load_dotenv()
        self._lock = threading.Lock()
        
        # Load keys from env
        keys_str = os.getenv("ALPHA_VANTAGE_KEYS", "")
        self.primary_keys = [k.strip() for k in keys_str.split(",") if k.strip()]
        self.fallback_key = os.getenv("ALPHA_VANTAGE_API_KEY", "").strip()
        
        if not self.primary_keys:
            logger.warning("No primary ALPHA_VANTAGE_KEYS found in env. Pool is empty.")
            if self.fallback_key:
                 self.primary_keys = [self.fallback_key] # Use fallback as primary if empty
        
        self.pool_size = len(self.primary_keys)
        self.current_index = 0
        
        # Tracking State
        # key -> { 'minute_start': ts, 'minute_calls': int, 'day_start': day_str, 'day_calls': int, 'failed': bool }
        self.usage_stats: Dict[str, Dict] = {}
        
        self._init_stats()
        logger.info(f"Initialized KeyPool with {self.pool_size} keys + 1 fallback")

    def _init_stats(self):
        now = time.time()
        today = datetime.now().strftime('%Y-%m-%d')
        
        for k in self.primary_keys:
            self.usage_stats[k] = {
                'minute_start': now,
                'minute_calls': 0,
                'day_start': today,
                'day_calls': 0,
                'failed': False
            }
        
        if self.fallback_key:
             self.usage_stats[self.fallback_key] = {
                'minute_start': now,
                'minute_calls': 0,
                'day_start': today,
                'day_calls': 0,
                'failed': False
            }

    def _reset_counters_if_needed(self, key: str):
        stats = self.usage_stats[key]
        now = time.time()
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Reset Minute
        if now - stats['minute_start'] >= 60:
            stats['minute_start'] = now
            stats['minute_calls'] = 0
            
        # Reset Day
        if stats['day_start'] != today:
            stats['day_start'] = today
            stats['day_calls'] = 0

    def get_key(self) -> str:
        with self._lock:
            # Try finding a valid primary key
            start_index = self.current_index
            attempts = 0
            
            while attempts < self.pool_size:
                key = self.primary_keys[self.current_index]
                self._reset_counters_if_needed(key)
                stats = self.usage_stats[key]
                
                # Check Limits
                if not stats['failed'] and \
                   stats['minute_calls'] < self.MAX_CALLS_PER_MIN and \
                   stats['day_calls'] < self.MAX_CALLS_PER_DAY:
                    
                    # Found valid key
                    stats['minute_calls'] += 1
                    stats['day_calls'] += 1
                    
                    # Rotate index for next call (Round Robin)
                    self.current_index = (self.current_index + 1) % self.pool_size
                    return key
                
                # Try next key
                self.current_index = (self.current_index + 1) % self.pool_size
                attempts += 1
            
            # If all primary exhausted, check fallback
            if self.fallback_key:
                logger.warning("Primary Key Pool exhausted/rate-limited. Switching to Fallback.")
                self._reset_counters_if_needed(self.fallback_key)
                f_stats = self.usage_stats[self.fallback_key]
                if not f_stats['failed']:
                     f_stats['minute_calls'] += 1
                     f_stats['day_calls'] += 1
                     return self.fallback_key
            
            logger.error("ALL KEYS EXHAUSTED (Primary + Fallback).")
            raise Exception("RateLimitExceeded: All keys depleted")

    def mark_failure(self, key: str):
        """Mark a key as failed (e.g. 429 or 403 response). It won't be used again extensively."""
        with self._lock:
            if key in self.usage_stats:
                logger.warning(f"Marking key ending in ...{key[-4:]} as FAILED/RateLimited")
                # We treat failure as effectively "used up" for now, or maybe just for the minute?
                # For safety, let's mark it 'failed' flag.
                # But to allow recovery from temporary 429, maybe just max out its counters?
                # "Auto-Rotate on rate-limit" -> usually implies try another key.
                # Implementation: Set minute_calls to MAX.
                self.usage_stats[key]['minute_calls'] = self.MAX_CALLS_PER_MIN
                # Also set 'failed' purely for logging or aggressive pruning?
                # User prompt says "Mark failure (key)".
                # Let's set 'failed' = True if it's a hard error, but usually 429 is temporary.
                # Just maxing counters ensures we rotate.
                
    def get_stats(self):
        return {k: v['day_calls'] for k, v in self.usage_stats.items()}
