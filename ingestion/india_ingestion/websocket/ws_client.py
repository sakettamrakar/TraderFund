"""Simplified WebSocket Client for Staged Migration.

Stage 1: Single symbol test
Stage 2: NIFTY 50 expansion

This is a TEST-ONLY implementation.
"""

import logging
import time
import threading
from typing import List, Optional, Callable, Dict, Set
from datetime import datetime

from SmartApi import SmartConnect
from SmartApi.smartWebSocketV2 import SmartWebSocketV2

from ingestion.api_ingestion.angel_smartapi.auth import AngelAuthManager
from ingestion.api_ingestion.angel_smartapi.instrument_master import InstrumentMaster

logger = logging.getLogger(__name__)


class WebSocketClient:
    """Simplified WebSocket client for staged testing."""
    
    MODE_LTP = 1  # Last Traded Price mode
    EXCHANGE_NSE_CM = 1  # NSE Cash Market
    
    def __init__(
        self,
        auth_manager: AngelAuthManager,
        instrument_master: InstrumentMaster,
        on_tick_callback: Callable[[str, float, int, datetime], None]
    ):
        """Initialize WebSocket client.
        
        Args:
            auth_manager: Authenticated AngelAuthManager.
            instrument_master: InstrumentMaster for token lookups.
            on_tick_callback: Callback(symbol, price, volume, timestamp).
        """
        self.auth_manager = auth_manager
        self.instrument_master = instrument_master
        self.on_tick_callback = on_tick_callback
        
        self.ws: Optional[SmartWebSocketV2] = None
        self._connected = False
        self._subscribed_tokens: Set[str] = set()
        self._token_to_symbol: Dict[str, str] = {}
        
        # Statistics
        self.ticks_received = 0
        self.last_tick_time: Optional[datetime] = None
        
        self._lock = threading.Lock()
    
    def _on_open(self, ws_app):
        """WebSocket open callback."""
        logger.info("✓ WebSocket connection opened")
        with self._lock:
            self._connected = True
    
    def _on_close(self, ws_app):
        """WebSocket close callback."""
        logger.warning("WebSocket closed")
        with self._lock:
            self._connected = False
    
    def _on_error(self, ws_app, error):
        """WebSocket error callback."""
        logger.error("WebSocket error: %s", error)
    
    def _on_data(self, ws_app, message):
        """WebSocket data callback - parse ticks."""
        try:
            # Log first few ticks for validation
            if self.ticks_received < 5:
                logger.info("Sample tick received (raw length: %d bytes)", len(message))
            
            # Simplified parsing - actual implementation may need adjustment
            # For now, simulate tick data
            timestamp = datetime.now()
            
            # In real implementation, parse binary message properly
            # For testing, we'll use a placeholder
            for symbol in self._token_to_symbol.values():
                # Simulate tick (replace with actual parsing)
                price = 2500.0  # Placeholder
                volume = 100    # Placeholder
                
                with self._lock:
                    self.ticks_received += 1
                    self.last_tick_time = timestamp
                
                self.on_tick_callback(symbol, price, volume, timestamp)
                break  # Only one symbol per tick in real scenario
            
        except Exception as e:
            logger.exception("Error parsing tick: %s", e)
    
    def connect(self) -> bool:
        """Connect to WebSocket."""
        try:
            if not self.auth_manager.ensure_authenticated():
                logger.error("Authentication failed")
                return False
            
            feed_token = self.auth_manager._feed_token
            api_key = self.auth_manager._config.api_key
            client_code = self.auth_manager._config.client_id
            
            if not feed_token:
                logger.error("Feed token not available")
                return False
            
            # Create WebSocket instance
            self.ws = SmartWebSocketV2(
                auth_token=feed_token,
                api_key=api_key,
                client_code=client_code,
                feed_token=feed_token
            )
            
            self.ws.on_open = self._on_open
            self.ws.on_close = self._on_close
            self.ws.on_error = self._on_error
            self.ws.on_data = self._on_data
            
            # Connect
            self.ws.connect()
            
            # Wait for connection
            max_wait = 10
            start = time.time()
            while not self._connected and (time.time() - start) < max_wait:
                time.sleep(0.1)
            
            return self._connected
            
        except Exception as e:
            logger.exception("Connection error: %s", e)
            return False
    
    def subscribe(self, symbols: List[str], exchange: str = "NSE") -> bool:
        """Subscribe to symbols."""
        if not self._connected:
            logger.error("Cannot subscribe: not connected")
            return False
        
        try:
            self.instrument_master.ensure_loaded()
            
            subscription_list = []
            for symbol in symbols:
                token = self.instrument_master.get_token(symbol, exchange)
                if not token:
                    logger.warning("Token not found for %s", symbol)
                    continue
                
                subscription_list.append({
                    "exchangeType": self.EXCHANGE_NSE_CM,
                    "tokens": [token]
                })
                
                self._token_to_symbol[token] = symbol
                self._subscribed_tokens.add(token)
            
            if not subscription_list:
                logger.error("No valid tokens to subscribe")
                return False
            
            # Subscribe
            self.ws.subscribe(self.MODE_LTP, subscription_list)
            logger.info("✓ Subscribed to %d symbols", len(subscription_list))
            
            return True
            
        except Exception as e:
            logger.exception("Subscription error: %s", e)
            return False
    
    def unsubscribe(self, symbols: List[str], exchange: str = "NSE") -> bool:
        """Unsubscribe from symbols."""
        if not self._connected:
            return False
        
        try:
            unsubscription_list = []
            for symbol in symbols:
                token = self.instrument_master.get_token(symbol, exchange)
                if token and token in self._subscribed_tokens:
                    unsubscription_list.append({
                        "exchangeType": self.EXCHANGE_NSE_CM,
                        "tokens": [token]
                    })
                    self._token_to_symbol.pop(token, None)
                    self._subscribed_tokens.discard(token)
            
            if unsubscription_list:
                self.ws.unsubscribe(self.MODE_LTP, unsubscription_list)
            
            return True
            
        except Exception as e:
            logger.exception("Unsubscription error: %s", e)
            return False
    
    def disconnect(self) -> None:
        """Disconnect WebSocket."""
        if self.ws:
            try:
                self.ws.close()
            except:
                pass
            finally:
                with self._lock:
                    self._connected = False
                    self._subscribed_tokens.clear()
                    self._token_to_symbol.clear()
    
    def is_connected(self) -> bool:
        """Check if connected."""
        with self._lock:
            return self._connected
    
    def get_subscribed_count(self) -> int:
        """Get subscribed symbol count."""
        with self._lock:
            return len(self._subscribed_tokens)
    
    def get_stats(self) -> Dict:
        """Get statistics."""
        with self._lock:
            return {
                "connected": self._connected,
                "subscribed_count": len(self._subscribed_tokens),
                "ticks_received": self.ticks_received,
                "last_tick_time": self.last_tick_time.isoformat() if self.last_tick_time else None,
            }
