"""Phase 5 Diagnostics: Data Loader.

Loads Phase-4 signal observation logs, validates schema, and normalizes timestamps.
Original logs are NEVER mutated.
"""

import logging
import pandas as pd
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

EXPECTED_COLUMNS = [
    "timestamp", "symbol", "signal_type", "confidence", "reason",
    "market_context", "result_5m", "result_15m", "classification", "reviewer_notes"
]

class SignalLogLoader:
    """Loads and validates Phase-4 observation logs."""

    def __init__(self, log_dir: str = "observations/signal_reviews"):
        self.log_dir = Path(log_dir)

    def load_all_logs(self) -> pd.DataFrame:
        """Load and concatenate all CSV logs in the directory.

        Returns:
            DataFrame with all signal records.
        """
        files = list(self.log_dir.glob("*.csv"))
        if not files:
            logger.warning(f"No CSV logs found in {self.log_dir}")
            return pd.DataFrame(columns=EXPECTED_COLUMNS)

        all_dfs = []
        for file_path in files:
            try:
                df = pd.read_csv(file_path)
                all_dfs.append(df)
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")

        if not all_dfs:
            return pd.DataFrame(columns=EXPECTED_COLUMNS)

        combined = pd.concat(all_dfs, ignore_index=True)
        return self._validate_and_normalize(combined)

    def _validate_and_normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate schema and normalize timestamps.

        Args:
            df: Raw loaded DataFrame.

        Returns:
            Validated and normalized DataFrame.
        """
        # Check for missing columns
        missing = [col for col in EXPECTED_COLUMNS if col not in df.columns]
        if missing:
            logger.warning(f"Missing columns in log data: {missing}")
            for col in missing:
                df[col] = None

        # Normalize timestamp
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

        # Ensure classification is uppercase
        if "classification" in df.columns:
            df["classification"] = df["classification"].str.upper().str.strip()

        return df

    def load_single_file(self, filename: str) -> pd.DataFrame:
        """Load a single log file by name.

        Args:
            filename: Name of the CSV file.

        Returns:
            Validated DataFrame.
        """
        file_path = self.log_dir / filename
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return pd.DataFrame(columns=EXPECTED_COLUMNS)

        df = pd.read_csv(file_path)
        return self._validate_and_normalize(df)
