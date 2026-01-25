"""Signal Logger Utility for Phase 4 Observation.

This script provides a lightweight logger to capture signals from the momentum engine
and store them in a reviewer-ready CSV format.
"""

import csv
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Configure local logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ObservationLogger:
    """Logs signals for Phase 4 live observation."""

    def __init__(self, base_dir: str = "observations"):
        self.base_dir = Path(base_dir)
        self.review_dir = self.base_dir / "signal_reviews"
        self.daily_log_dir = self.base_dir / "daily_logs"
        self.header = [
            "timestamp", "symbol", "signal_type", "confidence", "reason",
            "price_t0", "price_t5", "price_t15",
            "volume_t0", "volume_t5_change", "volume_continuation",
            "market_index_trend", "vix",
            "outcome", "classification", "reviewer_notes", "screenshot_path"
        ]
        self._ensure_paths()

    def _ensure_paths(self):
        """Ensure observation directories exist."""
        self.review_dir.mkdir(parents=True, exist_ok=True)
        self.daily_log_dir.mkdir(parents=True, exist_ok=True)

    def _get_review_file(self) -> Path:
        """Get the current day's review file path."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        return self.review_dir / f"signals_for_review_{date_str}.csv"

    def log_signal(self, signal_data: Dict[str, Any]):
        """Append a signal to the review CSV.

        Args:
            signal_data: Dictionary containing signal attributes.
                         Must match MomentumSignal structure.
        """
        file_path = self._get_review_file()
        file_exists = file_path.exists()

        try:
            with open(file_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=self.header)
                if not file_exists:
                    writer.writeheader()
                
                # Filter only relevant fields and add placeholders for reviewer
                row = {
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
                    "market_index_trend": signal_data.get("market_index_trend", ""),
                    "vix": signal_data.get("vix", ""),
                    "outcome": "",
                    "classification": "",
                    "reviewer_notes": "",
                    "screenshot_path": ""
                }
                writer.writerow(row)
            
            logger.info(f"Signal for {signal_data.get('symbol')} logged to {file_path}")
        except Exception as e:
            logger.error(f"Failed to log signal: {e}")

if __name__ == "__main__":
    # Example usage / smoke test
    obs_logger = ObservationLogger()
    sample_signal = {
        "symbol": "TEST",
        "timestamp": datetime.now().isoformat(),
        "signal_type": "MOMENTUM_LONG",
        "confidence": 0.85,
        "reason": "Synthetic price breakout"
    }
    obs_logger.log_signal(sample_signal)
