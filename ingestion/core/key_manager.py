
import os
import json
import logging
import datetime
from typing import List, Dict, Optional
from ingestion import config

logger = logging.getLogger(__name__)

class QuotaExhaustedException(Exception):
    """Raised when no API keys are available or global budget is reached."""
    pass

class ApiKeyManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ApiKeyManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.keys: List[str] = self._load_keys()
        self.max_calls_per_key = 450  # Safe buffer below 500
        self.global_daily_budget = config.GLOBAL_DAILY_BUDGET
        
        self.state_file = config.API_USAGE_STATE_FILE
        self.state: Dict = self._load_state()
        self._check_and_reset_daily_stats()
        
        self._initialized = True

    def _load_keys(self) -> List[str]:
        """Load keys from env vars."""
        keys_str = os.getenv(config.KEYS_ENV_VAR, "")
        keys = [k.strip() for k in keys_str.split(",") if k.strip()]
        
        if not keys and config.LEGACY_API_KEY:
             logger.warning("No pool keys found. Falling back to legacy single key.")
             keys = [config.LEGACY_API_KEY]
             
        if not keys:
            logger.error("No API keys found in environment variables.")
        
        return keys

    def _load_state(self) -> Dict:
        if self.state_file.exists():
            try:
                with open(self.state_file, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}
        
    def _save_state(self):
        with open(self.state_file, "w") as f:
            json.dump(self.state, f, indent=4)

    def _check_and_reset_daily_stats(self):
        today = datetime.date.today().isoformat()
        last_date = self.state.get("date")
        
        if last_date != today:
            logger.info(f"New day detected ({today}). Resetting API usage stats.")
            self.state = {
                "date": today,
                "global_usage": 0,
                "key_usage": {k: 0 for k in self.keys}  # Initialize for known keys
            }
            self._save_state()

    def get_usage_stats(self) -> Dict:
        """Return current usage stats."""
        return self.state

    def get_active_key(self) -> str:
        """
        Get the first available API key.
        Raises QuotaExhaustedException if globally or locally exhausted.
        """
        self._check_and_reset_daily_stats()
        
        # Check global budget
        global_usage = self.state.get("global_usage", 0)
        if global_usage >= self.global_daily_budget:
            msg = f"Global daily API budget exhausted ({global_usage}/{self.global_daily_budget})."
            logger.warning(msg)
            raise QuotaExhaustedException(msg)
            
        # Check individual keys
        key_usage_map = self.state.get("key_usage", {})
        
        for key in self.keys:
            used = key_usage_map.get(key, 0)
            if used < self.max_calls_per_key:
                return key
                
        msg = "All available API keys calculate as exhausted."
        logger.error(msg)
        raise QuotaExhaustedException(msg)

    def record_usage(self, key: str):
        """Increment usage for the specific key."""
        self.state["global_usage"] = self.state.get("global_usage", 0) + 1
        
        key_usage = self.state.get("key_usage", {})
        key_usage[key] = key_usage.get(key, 0) + 1
        self.state["key_usage"] = key_usage
        
        self._save_state()
