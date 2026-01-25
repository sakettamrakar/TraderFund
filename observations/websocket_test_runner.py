"""WebSocket Test Runner for India Momentum.

STAGE 1: Single symbol test (RELIANCE)
STAGE 2: NIFTY 50 expansion

This is a TEST-ONLY runner. NOT for production use.
Requires explicit --ws-test-mode flag.
"""

import os
import sys
import time
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Add project root
sys.path.append(str(Path(__file__).parent.parent))

from ingestion.india_ingestion.websocket.ws_client import WebSocketClient
from ingestion.india_ingestion.websocket.candle_builder import CandleBuilder
from ingestion.india_ingestion.websocket.ws_healthcheck import HealthCheck
from ingestion.api_ingestion.angel_smartapi.auth import AngelAuthManager
from ingestion.api_ingestion.angel_smartapi.instrument_master import InstrumentMaster
from ingestion.api_ingestion.angel_smartapi.config import AngelConfig
from src.core_modules.momentum_engine.momentum_engine import MomentumEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/websocket_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("WSTestRunner")


def main():
    """Main entry point for WebSocket test runner."""
    parser = argparse.ArgumentParser(description="WebSocket Test Runner (India Momentum)")
    parser.add_argument("--ws-test-mode", action="store_true", required=True,
                       help="REQUIRED: Explicit flag to enable WebSocket test mode")
    parser.add_argument("--stage", type=int, choices=[1, 2], default=1,
                       help="Stage 1: Single symbol, Stage 2: NIFTY 50")
    parser.add_argument("--duration", type=int, default=15,
                       help="Test duration in minutes (default: 15)")
    args = parser.parse_args()
    
    if not args.ws_test_mode:
        logger.error("SAFETY: --ws-test-mode flag is REQUIRED to run this test")
        logger.error("This prevents accidental execution in production mode")
        sys.exit(1)
    
    logger.info("="*60)
    logger.info("WebSocket Test Runner - STAGE %d", args.stage)
    logger.info("="*60)
    logger.info("TEST MODE ONLY - NOT PRODUCTION")
    logger.info("Duration: %d minutes", args.duration)
    logger.info("="*60)
    
    # Initialize components
    config = AngelConfig()
    auth_manager = AngelAuthManager(config)
    instrument_master = InstrumentMaster(config)
    
    # Authenticate
    logger.info("Authenticating with SmartAPI...")
    if not auth_manager.ensure_authenticated():
        logger.error("Authentication failed")
        sys.exit(1)
    
    feed_token = auth_manager._feed_token
    if not feed_token:
        logger.error("Feed token not available")
        sys.exit(1)
    
    logger.info("✓ Authentication successful")
    logger.info("✓ Feed token obtained")
    
    # Determine symbols for this stage
    if args.stage == 1:
        test_symbols = ["RELIANCE"]  # Single symbol test
        logger.info("STAGE 1: Testing with single symbol: %s", test_symbols[0])
    else:
        # Load NIFTY 50 from instrument master
        instrument_master.ensure_loaded()
        # For now, use a subset - user can expand later
        test_symbols = [
            "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK",
            "SBIN", "BHARTIARTL", "ITC", "KOTAKBANK", "LT"
        ]
        logger.info("STAGE 2: Testing with %d symbols (NIFTY 50 subset)", len(test_symbols))
    
    # Initialize WebSocket client
    candle_builder = CandleBuilder(output_path="data/test/websocket_candles")
    
    def on_tick(symbol, price, volume, timestamp):
        candle_builder.update_tick(symbol, price, volume, timestamp)
    
    ws_client = WebSocketClient(
        auth_manager=auth_manager,
        instrument_master=instrument_master,
        on_tick_callback=on_tick
    )
    
    # Initialize health check
    health_check = HealthCheck(ws_client, candle_builder, test_symbols)
    
    # Connect WebSocket
    logger.info("Connecting to WebSocket...")
    if not ws_client.connect():
        logger.error("✗ WebSocket connection failed")
        sys.exit(1)
    
    logger.info("✓ WebSocket connected")
    
    # Subscribe to symbols
    logger.info("Subscribing to %d symbols...", len(test_symbols))
    if not ws_client.subscribe(test_symbols, exchange="NSE"):
        logger.error("✗ Subscription failed")
        ws_client.disconnect()
        sys.exit(1)
    
    logger.info("✓ Subscribed to %d symbols", ws_client.get_subscribed_count())
    
    # Start candle builder
    candle_builder.start()
    logger.info("✓ Candle builder started")
    
    # Initialize momentum engine (dry-run mode)
    momentum_engine = MomentumEngine()
    
    # Test loop
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=args.duration)
    
    logger.info("")
    logger.info("="*60)
    logger.info("TEST STARTED - Running for %d minutes", args.duration)
    logger.info("Start: %s", start_time.strftime("%H:%M:%S"))
    logger.info("End:   %s", end_time.strftime("%H:%M:%S"))
    logger.info("="*60)
    logger.info("")
    
    try:
        while datetime.now() < end_time:
            # Run health check every minute
            time.sleep(60)
            
            health_status = health_check.run_check()
            
            if not health_status["overall_healthy"]:
                logger.warning("Health check FAILED:")
                for key, value in health_status.items():
                    if key != "overall_healthy":
                        logger.warning("  %s: %s", key, value)
            
            # Run momentum evaluation (dry-run)
            logger.info("Running momentum evaluation (dry-run)...")
            signals = momentum_engine.run_on_all(test_symbols)
            logger.info("  Generated %d signals (test mode - not logged)", len(signals))
            
            remaining = (end_time - datetime.now()).total_seconds() / 60
            logger.info("  Time remaining: %.1f minutes", remaining)
    
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    
    finally:
        logger.info("")
        logger.info("="*60)
        logger.info("TEST COMPLETE - Shutting down")
        logger.info("="*60)
        
        # Stop candle builder
        candle_builder.stop()
        logger.info("✓ Candle builder stopped")
        
        # Disconnect WebSocket
        ws_client.unsubscribe(test_symbols, exchange="NSE")
        ws_client.disconnect()
        logger.info("✓ WebSocket disconnected")
        
        # Final health report
        logger.info("")
        logger.info("="*60)
        logger.info("FINAL HEALTH REPORT")
        logger.info("="*60)
        final_health = health_check.run_check()
        for key, value in final_health.items():
            logger.info("  %s: %s", key, value)
        
        logger.info("")
        logger.info("Test logs saved to: logs/websocket_test.log")
        logger.info("Test candles saved to: data/test/websocket_candles/")
        logger.info("")
        logger.info("="*60)
        logger.info("WebSocket Test Runner - COMPLETE")
        logger.info("="*60)


if __name__ == "__main__":
    main()
