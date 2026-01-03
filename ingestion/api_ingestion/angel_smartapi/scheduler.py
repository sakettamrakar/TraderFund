"""Angel One SmartAPI Ingestion Scheduler.

This module provides a loop-based scheduler for continuous market data
ingestion with token refresh and error handling.
"""

from __future__ import annotations

import logging
import signal
import sys
import time
from datetime import datetime
from typing import Optional

from .auth import AngelAuthManager
from .config import config
from .instrument_master import InstrumentMaster
from .market_data_ingestor import MarketDataIngestor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


class IngestionScheduler:
    """Scheduler for continuous market data ingestion.

    Runs a polling loop that:
    1. Refreshes authentication token if needed
    2. Fetches candle data for watchlist
    3. Fetches LTP snapshots
    4. Persists raw data to files

    Implements graceful shutdown and exponential backoff on errors.
    """

    MAX_BACKOFF_SECONDS = 300  # 5 minutes max backoff
    INITIAL_BACKOFF_SECONDS = 5

    def __init__(self, cfg: Optional[object] = None):
        """Initialize the scheduler.

        Args:
            cfg: Configuration object. Uses default config if not provided.
        """
        self._config = cfg or config
        self._auth = AngelAuthManager(self._config)
        self._instruments = InstrumentMaster(self._config)
        self._ingestor = MarketDataIngestor(
            auth_manager=self._auth,
            instrument_master=self._instruments,
            cfg=self._config,
        )
        self._running = False
        self._consecutive_failures = 0

    def _is_market_hours(self) -> bool:
        """Check if current time is within market hours.

        Returns:
            True if within NSE market hours (9:00 - 15:30 IST, weekdays).
        """
        now = datetime.now()

        # Skip weekends
        if now.weekday() >= 5:
            return False

        # Check time (NSE: 9:00 - 15:30)
        market_open = now.replace(hour=9, minute=0, second=0, microsecond=0)
        market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)

        return market_open <= now <= market_close

    def _calculate_backoff(self) -> float:
        """Calculate exponential backoff delay.

        Returns:
            Delay in seconds.
        """
        if self._consecutive_failures == 0:
            return 0

        delay = self.INITIAL_BACKOFF_SECONDS * (2 ** (self._consecutive_failures - 1))
        return min(delay, self.MAX_BACKOFF_SECONDS)

    def _setup_signal_handlers(self) -> None:
        """Setup handlers for graceful shutdown."""

        def shutdown_handler(signum, frame):
            logger.info(f"Received signal {signum}. Initiating graceful shutdown...")
            self._running = False

        signal.signal(signal.SIGINT, shutdown_handler)
        signal.signal(signal.SIGTERM, shutdown_handler)

    def _poll_once(self) -> bool:
        """Execute one polling cycle.

        Returns:
            True if successful, False on error.
        """
        try:
            # Ensure authenticated
            if not self._auth.ensure_authenticated():
                logger.error("Authentication failed")
                return False

            # Ingest watchlist data
            results = self._ingestor.ingest_watchlist()

            logger.info(
                f"Ingestion cycle complete: "
                f"{results['candles']} candles, {results['ltp']} LTP records"
            )

            self._consecutive_failures = 0
            return True

        except Exception as exc:
            logger.exception(f"Error in polling cycle: {exc}")
            self._consecutive_failures += 1
            return False

    def run(self, run_outside_market_hours: bool = False) -> None:
        """Start the polling loop.

        Args:
            run_outside_market_hours: If True, runs even outside market hours.
        """
        self._running = True
        self._setup_signal_handlers()

        # Validate configuration
        if not self._config.validate():
            missing = self._config.get_missing_credentials()
            logger.error(f"Missing credentials: {missing}")
            logger.error("Set environment variables and restart.")
            return

        logger.info("Starting Angel SmartAPI ingestion scheduler")
        logger.info(f"Polling interval: {self._config.polling_interval_seconds}s")
        logger.info(f"Watchlist: {self._config.symbol_watchlist}")

        # Pre-load instrument master
        if not self._instruments.ensure_loaded():
            logger.error("Failed to load instrument master")
            return

        # Initial login
        if not self._auth.login():
            logger.error("Initial login failed")
            return

        while self._running:
            cycle_start = time.time()

            # Check market hours
            if not run_outside_market_hours and not self._is_market_hours():
                logger.info("Outside market hours. Sleeping...")
                time.sleep(60)
                continue

            # Execute polling cycle
            success = self._poll_once()

            # Calculate next sleep duration
            if success:
                sleep_duration = self._config.polling_interval_seconds
            else:
                backoff = self._calculate_backoff()
                sleep_duration = max(backoff, self._config.polling_interval_seconds)
                logger.warning(
                    f"Applying backoff: {backoff:.1f}s "
                    f"(failures: {self._consecutive_failures})"
                )

            # Account for time spent in cycle
            elapsed = time.time() - cycle_start
            actual_sleep = max(0, sleep_duration - elapsed)

            if self._running and actual_sleep > 0:
                logger.debug(f"Sleeping for {actual_sleep:.1f}s until next cycle")
                time.sleep(actual_sleep)

        # Cleanup
        logger.info("Scheduler stopped. Logging out...")
        self._auth.logout()
        logger.info("Shutdown complete")

    def run_single_cycle(self) -> bool:
        """Run a single ingestion cycle.

        Useful for testing or manual triggers.

        Returns:
            True if successful, False on error.
        """
        if not self._config.validate():
            missing = self._config.get_missing_credentials()
            logger.error(f"Missing credentials: {missing}")
            return False

        if not self._instruments.ensure_loaded():
            logger.error("Failed to load instrument master")
            return False

        if not self._auth.login():
            logger.error("Login failed")
            return False

        success = self._poll_once()

        self._auth.logout()
        return success


def main():
    """Main entry point for the scheduler."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Angel SmartAPI Market Data Ingestion Scheduler"
    )
    parser.add_argument(
        "--outside-market-hours",
        action="store_true",
        help="Run even outside market hours (for testing)",
    )
    parser.add_argument(
        "--single-cycle",
        action="store_true",
        help="Run a single ingestion cycle and exit",
    )
    args = parser.parse_args()

    scheduler = IngestionScheduler()

    if args.single_cycle:
        success = scheduler.run_single_cycle()
        sys.exit(0 if success else 1)
    else:
        scheduler.run(run_outside_market_hours=args.outside_market_hours)


if __name__ == "__main__":
    main()
