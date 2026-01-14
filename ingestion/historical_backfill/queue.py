"""Historical Backfill - Priority Queue"""
import logging
from typing import List, Dict
import pandas as pd
from . import config
from .models import BackfillStatus

logger = logging.getLogger(__name__)

class BackfillQueue:
    """Manages prioritized backfill queue."""
    
    def __init__(self):
        self.tracker: Dict[str, BackfillStatus] = {}
        self._load_tracker()
    
    def _load_tracker(self):
        """Load existing tracker state."""
        if config.TRACKER_PATH.exists():
            df = pd.read_parquet(config.TRACKER_PATH)
            for _, row in df.iterrows():
                self.tracker[row["symbol"]] = BackfillStatus(
                    symbol=row["symbol"],
                    status=row["status"],
                    history_depth_days=row["history_depth_days"],
                    history_start_date=row.get("history_start_date"),
                    history_end_date=row.get("history_end_date"),
                    last_attempt=row["last_attempt"],
                    error_reason=row.get("error_reason"),
                )
            logger.info(f"Loaded {len(self.tracker)} tracked symbols")
    
    def _save_tracker(self):
        """Persist tracker state."""
        config.TRACKER_PATH.parent.mkdir(parents=True, exist_ok=True)
        records = [s.to_dict() for s in self.tracker.values()]
        pd.DataFrame(records).to_parquet(config.TRACKER_PATH, index=False)
    
    def get_pending_symbols(self, limit: int = None) -> List[str]:
        """Get symbols needing backfill, prioritized."""
        # Load symbol master
        if not config.SYMBOL_MASTER.exists():
            logger.error("Symbol master not found")
            return []
        
        from ingestion.universe_expansion.config import MANUAL_INCLUSIONS
        
        master = pd.read_parquet(config.SYMBOL_MASTER)
        all_symbols = master["symbol"].tolist()
        
        # Filter: not yet successfully backfilled
        pending = [s for s in all_symbols if self.tracker.get(s, BackfillStatus.pending(s)).status != "success"]
        
        # Sort logic: 
        # 1. Manual Inclusions (BDSX)
        # 2. Alphabetical (deterministic)
        
        manual_set = set(MANUAL_INCLUSIONS)
        pending.sort(key=lambda s: (0 if s in manual_set else 1, s))
        
        if limit:
            pending = pending[:limit]
        
        logger.info(f"Pending symbols: {len(pending)}")
        return pending
    
    def mark_success(self, symbol: str, depth: int, start: str, end: str):
        """Mark symbol as successfully backfilled."""
        self.tracker[symbol] = BackfillStatus.success(symbol, depth, start, end)
        self._save_tracker()
    
    def mark_failed(self, symbol: str, error: str):
        """Mark symbol as failed."""
        self.tracker[symbol] = BackfillStatus.failed(symbol, error)
        self._save_tracker()
    
    def get_stats(self) -> Dict:
        """Get queue statistics."""
        stats = {"pending": 0, "success": 0, "failed": 0, "total": 0}
        for s in self.tracker.values():
            stats[s.status] = stats.get(s.status, 0) + 1
            stats["total"] += 1
        return stats
