"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
Historical Data Adapter

Provides a clean interface for loading historical data for backtesting.
MUST NOT connect to any live data sources.
##############################################################################
"""

import os
import logging
from pathlib import Path
from typing import Optional, List

import pandas as pd

logger = logging.getLogger(__name__)


class DataSourceError(Exception):
    """Raised when data loading fails."""
    pass


class HistoricalDataAdapter:
    """Adapter for loading historical market data.

    This adapter is explicitly designed to read ONLY from local files.
    It will NEVER connect to live APIs or streaming data sources.

    Attributes:
        data_root: Root directory for historical data.
    """

    # Forbidden path patterns (safety check)
    FORBIDDEN_PATTERNS = ["live", "realtime", "stream", "api"]

    def __init__(self, data_root: str):
        """Initialize the adapter.

        Args:
            data_root: Absolute path to the data directory.

        Raises:
            ValueError: If the path is empty or contains forbidden patterns.
        """
        if not data_root:
            raise ValueError("data_root cannot be empty. Explicit path required.")

        lower_path = data_root.lower()
        for pattern in self.FORBIDDEN_PATTERNS:
            if pattern in lower_path:
                raise ValueError(
                    f"Data path '{data_root}' contains forbidden pattern '{pattern}'. "
                    f"HistoricalDataAdapter is for offline data only."
                )

        self.data_root = Path(data_root)
        if not self.data_root.exists():
            logger.warning(f"Data root {self.data_root} does not exist.")

    def load_parquet(self, filename: str) -> pd.DataFrame:
        """Load a Parquet file from the data root.

        Args:
            filename: Name of the Parquet file (e.g., "NSE_ITC.parquet").

        Returns:
            DataFrame with historical OHLCV data.

        Raises:
            DataSourceError: If the file cannot be loaded.
        """
        filepath = self.data_root / filename
        if not filepath.exists():
            raise DataSourceError(f"File not found: {filepath}")

        try:
            df = pd.read_parquet(filepath)
            logger.info(f"Loaded {len(df)} rows from {filepath}")
            return df
        except Exception as e:
            raise DataSourceError(f"Failed to load {filepath}: {e}") from e

    def load_csv(self, filename: str, **kwargs) -> pd.DataFrame:
        """Load a CSV file from the data root.

        Args:
            filename: Name of the CSV file.
            **kwargs: Additional arguments passed to pd.read_csv.

        Returns:
            DataFrame with historical data.

        Raises:
            DataSourceError: If the file cannot be loaded.
        """
        filepath = self.data_root / filename
        if not filepath.exists():
            raise DataSourceError(f"File not found: {filepath}")

        try:
            df = pd.read_csv(filepath, **kwargs)
            logger.info(f"Loaded {len(df)} rows from {filepath}")
            return df
        except Exception as e:
            raise DataSourceError(f"Failed to load {filepath}: {e}") from e

    def list_available_files(self, extension: str = ".parquet") -> List[str]:
        """List available data files in the data root.

        Args:
            extension: File extension to filter by.

        Returns:
            List of filenames.
        """
        if not self.data_root.exists():
            return []
        return [f.name for f in self.data_root.glob(f"*{extension}")]
