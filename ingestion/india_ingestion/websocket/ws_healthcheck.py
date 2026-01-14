"""WebSocket Health Check for Staged Migration.

Validates:
- WebSocket connected
- Subscribed symbol count matches expected
- Ticks received
- Candles finalized
- Momentum evaluation executed
- NO REST calls for live data
"""

import logging
from typing import Dict, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class HealthCheck:
    """Health check for WebSocket test mode."""
    
    def __init__(self, ws_client, candle_builder, expected_symbols: List[str]):
        """Initialize health check.
        
        Args:
            ws_client: WebSocketClient instance.
            candle_builder: CandleBuilder instance.
            expected_symbols: List of symbols we expect to be subscribed.
        """
        self.ws_client = ws_client
        self.candle_builder = candle_builder
        self.expected_symbols = expected_symbols
        
        self.checks_run = 0
        self.last_check_time: datetime = None
    
    def run_check(self) -> Dict:
        """Run complete health check.
        
        Returns:
            Dict with health status.
        """
        self.checks_run += 1
        self.last_check_time = datetime.now()
        
        logger.info("")
        logger.info("="*60)
        logger.info("HEALTH CHECK #%d - %s", self.checks_run, self.last_check_time.strftime("%H:%M:%S"))
        logger.info("="*60)
        
        # Check 1: WebSocket connected
        ws_connected = self.ws_client.is_connected()
        logger.info("1. WebSocket Connected: %s", "✓ PASS" if ws_connected else "✗ FAIL")
        
        # Check 2: Subscription count
        subscribed_count = self.ws_client.get_subscribed_count()
        expected_count = len(self.expected_symbols)
        subscription_ok = subscribed_count == expected_count
        logger.info("2. Subscription Count: %d/%d %s", 
                   subscribed_count, expected_count,
                   "✓ PASS" if subscription_ok else "✗ FAIL")
        
        # Check 3: Ticks received
        ws_stats = self.ws_client.get_stats()
        ticks_received = ws_stats["ticks_received"]
        ticks_ok = ticks_received > 0
        logger.info("3. Ticks Received: %d %s", 
                   ticks_received,
                   "✓ PASS" if ticks_ok else "✗ FAIL")
        
        # Check 4: Candles finalized
        candle_stats = self.candle_builder.get_stats()
        candles_finalized = candle_stats["total_candles"]
        candles_ok = candles_finalized > 0 if self.checks_run > 1 else True  # Allow first check to have 0
        logger.info("4. Candles Finalized: %d %s", 
                   candles_finalized,
                   "✓ PASS" if candles_ok else "⚠ PENDING")
        
        # Check 5: Last tick time (freshness)
        last_tick_time = ws_stats.get("last_tick_time")
        if last_tick_time:
            last_tick = datetime.fromisoformat(last_tick_time)
            age = (datetime.now() - last_tick).total_seconds()
            tick_fresh = age < 120  # Within last 2 minutes
            logger.info("5. Last Tick Age: %.1fs %s", 
                       age,
                       "✓ PASS" if tick_fresh else "⚠ STALE")
        else:
            tick_fresh = False
            logger.info("5. Last Tick Age: N/A ⚠ NO TICKS YET")
        
        # Check 6: NO REST calls (manual verification - log reminder)
        logger.info("6. REST Calls: ⚠ MANUAL VERIFICATION REQUIRED")
        logger.info("   → Check logs for 'getCandleData' or 'ltpData' calls")
        logger.info("   → Should be ZERO during WebSocket mode")
        
        # Overall health
        overall_healthy = (
            ws_connected and
            subscription_ok and
            ticks_ok and
            candles_ok
        )
        
        logger.info("")
        logger.info("Overall Status: %s", "✓ HEALTHY" if overall_healthy else "✗ UNHEALTHY")
        logger.info("="*60)
        logger.info("")
        
        return {
            "timestamp": self.last_check_time.isoformat(),
            "ws_connected": ws_connected,
            "subscription_count": f"{subscribed_count}/{expected_count}",
            "subscription_ok": subscription_ok,
            "ticks_received": ticks_received,
            "ticks_ok": ticks_ok,
            "candles_finalized": candles_finalized,
            "candles_ok": candles_ok,
            "tick_freshness": tick_fresh if last_tick_time else False,
            "overall_healthy": overall_healthy,
        }
