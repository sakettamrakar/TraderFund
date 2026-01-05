"""Replay Logger - Historical Replay Variant of ObservationLogger.

This logger writes signal data to the historical replay output directory,
clearly labeling all outputs as HISTORICAL_REPLAY.
"""

import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ReplayLogger:
    """Logs signals during historical replay.
    
    Similar to ObservationLogger but:
    - Writes to observations/historical_replay/<date>/
    - Adds 'mode=HISTORICAL_REPLAY' to all outputs
    - Clearly segregated from live observation data
    """
    
    MODE = "HISTORICAL_REPLAY"
    
    def __init__(self, replay_date: str, base_dir: str = "observations/historical_replay"):
        """Initialize the replay logger.
        
        Args:
            replay_date: The date being replayed (YYYY-MM-DD format).
            base_dir: Base directory for replay outputs.
        """
        self.replay_date = replay_date
        self.base_dir = Path(base_dir)
        self.output_dir = self.base_dir / replay_date
        
        self.header = [
            "mode", "timestamp", "symbol", "signal_type", "confidence", "reason",
            "price_t0", "price_t5", "price_t15",
            "volume_t0", "volume_t5_change", "volume_continuation",
            "market_index_trend", "vix",
            "outcome", "classification", "reviewer_notes"
        ]
        
        self._ensure_paths()
        self._signal_count = 0
    
    def _ensure_paths(self):
        """Ensure output directories exist."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def get_review_file_path(self) -> Path:
        """Get the review file path for this replay date."""
        return self.output_dir / f"signals_for_review_{self.replay_date}.csv"
    
    def log_signal(self, signal_data: Dict[str, Any]):
        """Append a signal to the replay review CSV.
        
        Args:
            signal_data: Dictionary containing signal attributes.
        """
        file_path = self.get_review_file_path()
        file_exists = file_path.exists()
        
        try:
            with open(file_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=self.header)
                if not file_exists:
                    writer.writeheader()
                
                row = {
                    "mode": self.MODE,
                    "timestamp": signal_data.get("timestamp"),
                    "symbol": signal_data.get("symbol"),
                    "signal_type": signal_data.get("signal_type", "MOMENTUM_LONG"),
                    "confidence": signal_data.get("confidence"),
                    "reason": signal_data.get("reason"),
                    "price_t0": signal_data.get("price_t0", ""),
                    "price_t5": "",
                    "price_t15": "",
                    "volume_t0": signal_data.get("volume_t0", ""),
                    "volume_t5_change": "",
                    "volume_continuation": "",
                    "market_index_trend": "",
                    "vix": "",
                    "outcome": "",
                    "classification": "",
                    "reviewer_notes": ""
                }
                writer.writerow(row)
            
            self._signal_count += 1
            logger.info(f"[{self.MODE}] Signal for {signal_data.get('symbol')} logged @ {signal_data.get('timestamp')}")
            
        except Exception as e:
            logger.error(f"Failed to log replay signal: {e}")
    
    @property
    def signal_count(self) -> int:
        """Number of signals logged in this session."""
        return self._signal_count
