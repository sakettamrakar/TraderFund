"""Verify Intraday Processed Data.

This script validates the integrity of processed Parquet files for intraday candles.
"""

import logging
import os
from pathlib import Path
from typing import Dict

import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class IntradayVerification:
    """Verifies integrity and schema of processed intraday Parquet files."""

    def __init__(self, processed_path: str = "data/processed/candles/intraday"):
        """Initialize verification.

        Args:
            processed_path: Path to processed Parquet files.
        """
        self.processed_path = Path(processed_path)
        self.expected_columns = [
            "symbol", "exchange", "timestamp", "open", "high", "low", "close", "volume"
        ]

    def verify_file(self, file_path: Path) -> bool:
        """Verify a single Parquet file.

        Args:
            file_path: Path to the Parquet file.

        Returns:
            True if all checks pass, False otherwise.
        """
        logger.info(f"Verifying {file_path.name}")
        
        try:
            df = pd.read_parquet(file_path)
        except Exception as exc:
            logger.error(f"Failed to read {file_path}: {exc}")
            return False

        checks = []

        # 1. Schema Check
        schema_ok = all(col in df.columns for col in self.expected_columns)
        if not schema_ok:
            logger.error(f"Schema mismatch. Missing: {set(self.expected_columns) - set(df.columns)}")
        checks.append(schema_ok)

        # 2. Duplicate Timestamp Check
        dupes = df.duplicated(subset=["timestamp"]).sum()
        if dupes > 0:
            logger.error(f"Found {dupes} duplicate timestamps in {file_path.name}")
        checks.append(dupes == 0)

        # 3. Time Ordering Check
        is_sorted = df["timestamp"].is_monotonic_increasing
        if not is_sorted:
            logger.error(f"Timestamps are not strictly increasing in {file_path.name}")
        checks.append(is_sorted)

        # 4. Volume Validity Check
        negative_vol = (df["volume"] < 0).sum()
        if negative_vol > 0:
            logger.error(f"Found {negative_vol} negative volume values in {file_path.name}")
        checks.append(negative_vol == 0)

        # 5. Non-zero Volume Check (Optional, but often desirable)
        zero_vol = (df["volume"] == 0).sum()
        if zero_vol > 0:
            logger.warning(f"Found {zero_vol} zero volume candles in {file_path.name}")

        # 6. Check for large gaps (Optional - Market hours specific)
        # We don't have enough data yet to reliably check gaps, but we can log gaps > 15m
        if len(df) > 1:
            diffs = df["timestamp"].diff().dropna()
            large_gaps = diffs[diffs > pd.Timedelta(minutes=15)]
            if not large_gaps.empty:
                logger.info(f"Found {len(large_gaps)} gaps larger than 15 minutes")

        success = all(checks)
        if success:
            logger.info(f"Verification PASSED for {file_path.name}")
        else:
            logger.error(f"Verification FAILED for {file_path.name}")
        
        return success

    def verify_all(self) -> Dict[str, bool]:
        """Verify all Parquet files in the processed directory.

        Returns:
            Dict mapping filename to verification status.
        """
        files = list(self.processed_path.glob("*.parquet"))
        if not files:
            logger.warning(f"No processed Parquet files found in {self.processed_path}")
            return {}

        results = {}
        for file_path in files:
            results[file_path.name] = self.verify_file(file_path)
        
        return results

if __name__ == "__main__":
    verifier = IntradayVerification()
    results = verifier.verify_all()
    
    overall_success = all(results.values()) if results else False
    if overall_success:
        logger.info("ALL VERIFICATIONS PASSED")
    else:
        logger.error("SOME VERIFICATIONS FAILED OR NO FILES FOUND")
