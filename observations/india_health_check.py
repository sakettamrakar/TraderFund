"""India WebSocket Health Check Monitor.

Monitors the health of the India WebSocket momentum runner, verifying:
- WebSocket connection status
- Subscribed symbol count
- Candle generation rate
- Absence of REST API rate-limit errors
- Tick flow continuity
"""

import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("IndiaHealthCheck")


class IndiaHealthMonitor:
    """Health monitor for India WebSocket momentum system."""
    
    def __init__(self, health_log_path: str = "logs/health/india_websocket_health.log"):
        """Initialize health monitor.
        
        Args:
            health_log_path: Path to health log file.
        """
        self.health_log_path = Path(health_log_path)
        self.health_log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def check_websocket_connected(self) -> bool:
        """Check if WebSocket is connected.
        
        Returns:
            True if connected, False otherwise.
        """
        # This would check the actual WebSocket client status
        # For now, we'll check if the runner process is active
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline and 'india_momentum_runner' in ' '.join(cmdline):
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return False
        except ImportError:
            logger.warning("psutil not installed, cannot check process status")
            return False
    
    def check_subscription_count(self, expected_count: int = 200) -> Dict:
        """Check subscribed symbol count.
        
        Args:
            expected_count: Expected number of subscribed symbols.
        
        Returns:
            Dict with subscription status.
        """
        # This would query the actual WebSocket client
        # For now, return a placeholder
        return {
            "expected": expected_count,
            "actual": 0,  # Would be populated from actual client
            "status": "unknown"
        }
    
    def check_candle_generation(self) -> Dict:
        """Check if candles are being generated.
        
        Returns:
            Dict with candle generation status.
        """
        try:
            # Check processed data directory for recent updates
            processed_path = Path("data/processed/candles/intraday")
            if not processed_path.exists():
                return {
                    "status": "no_data",
                    "last_update": None,
                    "candles_last_minute": 0
                }
            
            # Find most recently modified file
            parquet_files = list(processed_path.glob("NSE_*_1m.parquet"))
            if not parquet_files:
                return {
                    "status": "no_files",
                    "last_update": None,
                    "candles_last_minute": 0
                }
            
            most_recent = max(parquet_files, key=lambda p: p.stat().st_mtime)
            last_modified = datetime.fromtimestamp(most_recent.stat().st_mtime)
            
            # Check if updated in last 2 minutes
            age = datetime.now() - last_modified
            if age < timedelta(minutes=2):
                status = "active"
            elif age < timedelta(minutes=10):
                status = "stale"
            else:
                status = "inactive"
            
            return {
                "status": status,
                "last_update": last_modified.isoformat(),
                "age_seconds": age.total_seconds(),
                "candles_last_minute": len(parquet_files)  # Approximate
            }
            
        except Exception as e:
            logger.exception(f"Error checking candle generation: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def check_rest_api_calls(self) -> Dict:
        """Check for REST API rate-limit errors.
        
        Returns:
            Dict with REST API status.
        """
        try:
            # Check logs for rate-limit errors
            log_file = Path("logs/india_momentum_runner.log")
            if not log_file.exists():
                return {
                    "status": "no_log",
                    "rate_limit_errors": 0
                }
            
            # Read last 1000 lines
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()[-1000:]
            
            # Count rate-limit errors
            rate_limit_count = sum(
                1 for line in lines
                if 'rate limit' in line.lower() or 'too many requests' in line.lower()
            )
            
            return {
                "status": "ok" if rate_limit_count == 0 else "rate_limited",
                "rate_limit_errors": rate_limit_count
            }
            
        except Exception as e:
            logger.exception(f"Error checking REST API calls: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def check_tick_flow(self) -> Dict:
        """Check if ticks are being received.
        
        Returns:
            Dict with tick flow status.
        """
        # This would check the actual WebSocket client statistics
        # For now, we infer from candle generation
        candle_status = self.check_candle_generation()
        
        if candle_status.get("status") == "active":
            return {
                "status": "active",
                "ticks_received": "unknown"  # Would be from actual client
            }
        else:
            return {
                "status": "inactive",
                "ticks_received": 0
            }
    
    def run_health_check(self, expected_symbol_count: int = 200) -> Dict:
        """Run complete health check.
        
        Args:
            expected_symbol_count: Expected number of subscribed symbols.
        
        Returns:
            Dict with complete health status.
        """
        logger.info("Running India WebSocket health check...")
        
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "websocket_connected": self.check_websocket_connected(),
            "subscription": self.check_subscription_count(expected_symbol_count),
            "candle_generation": self.check_candle_generation(),
            "rest_api": self.check_rest_api_calls(),
            "tick_flow": self.check_tick_flow(),
        }
        
        # Determine overall health
        overall_healthy = (
            health_status["websocket_connected"] and
            health_status["candle_generation"].get("status") == "active" and
            health_status["rest_api"].get("status") == "ok"
        )
        
        health_status["overall_status"] = "healthy" if overall_healthy else "unhealthy"
        
        # Log to file
        self._log_health(health_status)
        
        return health_status
    
    def _log_health(self, health_status: Dict) -> None:
        """Log health status to file.
        
        Args:
            health_status: Health status dict.
        """
        try:
            with open(self.health_log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(health_status) + '\n')
            logger.info(f"Health status logged to {self.health_log_path}")
        except Exception as e:
            logger.exception(f"Failed to log health status: {e}")


def main():
    """Main entry point for health check."""
    monitor = IndiaHealthMonitor()
    health_status = monitor.run_health_check()
    
    # Print summary
    print("\n" + "="*50)
    print("India WebSocket Health Check")
    print("="*50)
    print(f"Timestamp: {health_status['timestamp']}")
    print(f"Overall Status: {health_status['overall_status'].upper()}")
    print(f"WebSocket Connected: {health_status['websocket_connected']}")
    print(f"Candle Generation: {health_status['candle_generation'].get('status')}")
    print(f"REST API Status: {health_status['rest_api'].get('status')}")
    print(f"Tick Flow: {health_status['tick_flow'].get('status')}")
    print("="*50)
    
    # Exit with appropriate code
    if health_status['overall_status'] == 'healthy':
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
