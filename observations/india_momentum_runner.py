"""India Momentum Runner - WebSocket Based.

This script orchestrates the India momentum engine using WebSocket-based
real-time data ingestion, supporting up to 200 symbols without REST API
rate-limit constraints.

CRITICAL: This is INDIA MARKET ONLY. Does not touch US market code.
"""

import os
import sys
import time
import logging
import argparse
import signal
from datetime import datetime
from pathlib import Path
from typing import List, Dict

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from ingestion.india_ingestion.websocket_client import IndiaWebSocketClient
from ingestion.india_ingestion.candle_aggregator import CandleAggregator
from ingestion.api_ingestion.angel_smartapi.auth import AngelAuthManager
from ingestion.api_ingestion.angel_smartapi.instrument_master import InstrumentMaster
from ingestion.api_ingestion.angel_smartapi.config import AngelConfig
from src.core_modules.momentum_engine.momentum_engine import MomentumEngine
from observations.signal_logger import ObservationLogger
from traderfund.regime.integration_guards import MomentumRegimeGuard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/india_momentum_runner.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("IndiaRunner")

# Global state for graceful shutdown
shutdown_requested = False


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    global shutdown_requested
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    shutdown_requested = True


def is_market_hours() -> bool:
    """Check if current time is within IST market hours (9:15 AM - 3:30 PM)."""
    now = datetime.now()
    
    # Skip weekends
    if now.weekday() > 4:  # 0=Mon, 4=Fri
        return False
    
    start_time = now.replace(hour=9, minute=15, second=0, microsecond=0)
    end_time = now.replace(hour=15, minute=30, second=0, microsecond=0)
    
    return start_time <= now <= end_time


def load_watchlist(config: AngelConfig) -> List[str]:
    """Load India market watchlist (~200 symbols).
    
    Args:
        config: AngelConfig instance.
    
    Returns:
        List of trading symbols.
    """
    # For now, use existing watchlist
    # TODO: Expand to full NIFTY 50 + Midcap + Smallcap (~200 symbols)
    watchlist = config.symbol_watchlist
    
    logger.info(f"Loaded watchlist with {len(watchlist)} symbols")
    return watchlist


def on_candles_finalized(candles: List[Dict], engine: MomentumEngine, 
                         obs_logger: ObservationLogger, watchlist: List[str],
                         regime_guard: MomentumRegimeGuard) -> None:
    """Callback when candles are finalized.
    
    Runs momentum engine on latest candles and logs signals.
    
    Args:
        candles: List of finalized candle dicts.
        engine: MomentumEngine instance.
        obs_logger: ObservationLogger instance.
        watchlist: List of symbols to evaluate.
        regime_guard: MomentumRegimeGuard instance (Phase 7 Integration).
    """
    try:
        logger.info(f"Running momentum evaluation on {len(watchlist)} symbols...")
        
        # Run momentum engine
        signals = engine.run_on_all(watchlist)
        
        if signals:
            logger.info(f"Generated {len(signals)} raw momentum signals!")
            executed_count = 0
            
            for sig in signals:
                signal_dict = sig.to_dict()
                
                # Phase 7: Regime Guard Check
                decision = regime_guard.check_signal(signal_dict)
                
                if decision.allowed:
                    # Enforce Size Multiplier (if < 1.0)
                    if decision.size_multiplier < 1.0:
                        signal_dict['constraints'] = f"THROTTLED: {decision.reason} Size x{decision.size_multiplier}"
                        logger.warning(f"Strategy THROTTLED for {sig.symbol}: {decision.reason}")
                    
                    # Log execution
                    obs_logger.log_signal(signal_dict)
                    executed_count += 1
                else:
                    # Log Blockage
                    logger.warning(f"Strategy BLOCKED for {sig.symbol}: {decision.reason}")
                    # Optionally log to a 'blocked_signals.log' or similar if needed
            
            logger.info(f"Executed {executed_count}/{len(signals)} signals after Regime Check.")
        else:
            logger.debug("No momentum signals generated in this cycle")
        
        # Generate executive dashboard data
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, "observations/executive_data_generator.py"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                logger.debug("Executive dashboard data updated")
            else:
                logger.warning(f"Executive dashboard update failed: {result.stderr}")
        except Exception as e:
            logger.warning(f"Failed to update executive dashboard: {e}")
            
    except Exception as e:
        logger.exception(f"Error in candle finalization callback: {e}")


def main():
    """Main entry point for India momentum runner."""
    global shutdown_requested
    
    parser = argparse.ArgumentParser(description="India Momentum Runner (WebSocket)")
    parser.add_argument("--force", action="store_true", help="Force run outside market hours")
    parser.add_argument("--hod-dist", type=float, default=0.5, help="HOD proximity percentage")
    parser.add_argument("--vol-mult", type=float, default=2.0, help="Volume multiplier")
    parser.add_argument("--symbols", type=str, help="Comma-separated symbols (overrides config)")
    args = parser.parse_args()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Check market hours
    if not args.force and not is_market_hours():
        logger.info("Outside market hours. Use --force to run anyway.")
        return
    
    # Initialize components
    logger.info("Initializing India Momentum Runner (WebSocket)...")
    
    config = AngelConfig()
    auth_manager = AngelAuthManager(config)
    instrument_master = InstrumentMaster(config)
    
    # Load watchlist
    if args.symbols:
        watchlist = args.symbols.split(",")
    else:
        watchlist = load_watchlist(config)
    
    logger.info(f"Watchlist: {len(watchlist)} symbols")
    
    # Initialize momentum engine
    engine = MomentumEngine(
        hod_proximity_pct=args.hod_dist,
        vol_multiplier=args.vol_mult
    )
    obs_logger = ObservationLogger()
    regime_guard = MomentumRegimeGuard()
    
    # Initialize candle aggregator with callback
    def candle_callback(candles: List[Dict]):
        on_candles_finalized(candles, engine, obs_logger, watchlist, regime_guard)
    
    aggregator = CandleAggregator(on_candle_callback=candle_callback)
    
    # Add all symbols to aggregator
    for symbol in watchlist:
        aggregator.add_symbol(symbol, exchange="NSE")
    
    # Initialize WebSocket client
    def tick_callback(symbol: str, price: float, volume: int, timestamp: datetime):
        aggregator.update_tick(symbol, price, volume, timestamp)
    
    ws_client = IndiaWebSocketClient(
        auth_manager=auth_manager,
        instrument_master=instrument_master,
        on_tick_callback=tick_callback,
        mode=IndiaWebSocketClient.MODE_LTP
    )
    
    # Connect to WebSocket
    logger.info("Connecting to WebSocket...")
    if not ws_client.connect():
        logger.error("Failed to connect to WebSocket. Exiting.")
        return
    
    # Subscribe to symbols
    logger.info(f"Subscribing to {len(watchlist)} symbols...")
    if not ws_client.subscribe(watchlist, exchange="NSE"):
        logger.error("Failed to subscribe to symbols. Exiting.")
        ws_client.disconnect()
        return
    
    logger.info(f"Successfully subscribed to {ws_client.get_subscribed_count()} symbols")
    
    # Start candle aggregator
    aggregator.start()
    logger.info("Candle aggregator started")
    
    # Main loop
    logger.info("India Momentum Runner is now active. Press Ctrl+C to stop.")
    
    try:
        while not shutdown_requested:
            # Check if still market hours (unless forced)
            if not args.force and not is_market_hours():
                logger.info("Market hours ended. Shutting down...")
                break
            
            # Check WebSocket health
            if not ws_client.is_connected():
                logger.warning("WebSocket disconnected. Attempting reconnect...")
                if not ws_client.connect():
                    logger.error("Reconnection failed. Exiting.")
                    break
                if not ws_client.subscribe(watchlist, exchange="NSE"):
                    logger.error("Re-subscription failed. Exiting.")
                    break
            
            # Log statistics every 5 minutes
            time.sleep(300)
            ws_stats = ws_client.get_stats()
            agg_stats = aggregator.get_stats()
            logger.info(f"WebSocket: {ws_stats['ticks_received']} ticks, "
                       f"Aggregator: {agg_stats['total_candles_generated']} candles")
    
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    
    finally:
        # Graceful shutdown
        logger.info("Shutting down India Momentum Runner...")
        
        # Stop aggregator
        aggregator.stop()
        logger.info("Candle aggregator stopped")
        
        # Unsubscribe and disconnect
        ws_client.unsubscribe(watchlist, exchange="NSE")
        ws_client.disconnect()
        logger.info("WebSocket disconnected")
        
        # Run EOD review generator
        logger.info("Running EOD review generator...")
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, "observations/eod_review_generator.py"],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                logger.info("EOD review generated successfully")
            else:
                logger.warning(f"EOD review generation failed: {result.stderr}")
        except Exception as e:
            logger.warning(f"Failed to run EOD review: {e}")
        
        logger.info("India Momentum Runner shutdown complete")


if __name__ == "__main__":
    main()
