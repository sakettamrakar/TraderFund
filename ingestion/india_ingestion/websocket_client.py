"""WebSocket Client for India Market Data.

Manages SmartAPI WebSocket v2 connection for real-time tick data ingestion.
Supports up to 1000 instrument token subscriptions per session.
"""

import logging
import time
import threading
from typing import List, Optional, Callable, Dict, Set
from datetime import datetime
import struct

from SmartApi import SmartConnect
from SmartApi.smartWebSocketV2 import SmartWebSocketV2

from ingestion.api_ingestion.angel_smartapi.auth import AngelAuthManager
from ingestion.api_ingestion.angel_smartapi.instrument_master import InstrumentMaster

logger = logging.getLogger(__name__)


class IndiaWebSocketClient:
    """WebSocket client for India market real-time data.
    
    Connects to SmartAPI WebSocket v2 and subscribes to instrument tokens
    for LTP (Last Traded Price) streaming.
    """
    
    # WebSocket modes
    MODE_LTP = 1  # Last Traded Price
    MODE_QUOTE = 2  # Quote (LTP + OHLC)
    MODE_SNAP_QUOTE = 3  # Snap Quote (Full market depth)
    
    # Exchange types
    EXCHANGE_NSE_CM = 1  # NSE Cash Market
    EXCHANGE_NSE_FO = 2  # NSE Futures & Options
    EXCHANGE_BSE_CM = 3  # BSE Cash Market
    EXCHANGE_BSE_FO = 4  # BSE Futures & Options
    
    def __init__(
        self,
        auth_manager: AngelAuthManager,
        instrument_master: InstrumentMaster,
        on_tick_callback: Callable[[str, float, int, datetime], None],
        mode: int = MODE_LTP
    ):
        """Initialize WebSocket client.
        
        Args:
            auth_manager: Authenticated AngelAuthManager instance.
            instrument_master: InstrumentMaster for token lookups.
            on_tick_callback: Callback function(symbol, price, volume, timestamp).
            mode: Subscription mode (LTP, QUOTE, SNAP_QUOTE).
        """
        self.auth_manager = auth_manager
        self.instrument_master = instrument_master
        self.on_tick_callback = on_tick_callback
        self.mode = mode
        
        # WebSocket instance
        self.ws: Optional[SmartWebSocketV2] = None
        
        # Connection state
        self._connected = False
        self._subscribed_tokens: Set[str] = set()
        self._token_to_symbol: Dict[str, str] = {}  # token -> symbol mapping
        
        # Statistics
        self.ticks_received = 0
        self.connection_attempts = 0
        self.last_tick_time: Optional[datetime] = None
        
        # Thread safety
        self._lock = threading.Lock()
    
    def _on_open(self, ws_app, *args):
        """WebSocket open callback."""
        # args might contain 'response' or nothing depending on library version
        logger.info(f"WebSocket connection opened. Args: {args}")
        with self._lock:
            self._connected = True
    
    def _on_close(self, ws_app, *args):
        """WebSocket close callback."""
        # args might contain code, reason
        logger.warning(f"WebSocket connection closed: {args}")
        with self._lock:
            self._connected = False
    
    def _on_error(self, ws_app, error):
        """WebSocket error callback."""
        logger.error(f"WebSocket error: {error}")
    
    def _on_data(self, ws_app, message):
        """WebSocket data callback.
        
        Parses binary tick data and invokes the tick callback.
        """
        try:
            # SmartAPI v2 sends binary data
            # Format: [exchange_type(1), token(25), sequence(8), timestamp(8), 
            #          ltp(8), volume(8), ...]
            
            # Parse binary message (simplified - actual format may vary)
            # For LTP mode, we primarily need: token, ltp, volume, timestamp
            
            if len(message) < 50:
                logger.warning(f"Received short message: {len(message)} bytes")
                return
            
            # Parse token (bytes 1-26, null-terminated string)
            token = message[1:26].decode('utf-8').rstrip('\x00')
            
            # Parse LTP (bytes 34-42, double)
            ltp = struct.unpack('>d', message[34:42])[0]
            
            # Parse volume (bytes 42-50, long)
            volume = struct.unpack('>Q', message[42:50])[0]
            
            # Timestamp
            timestamp = datetime.now()
            
            # Lookup symbol
            symbol = self._token_to_symbol.get(token)
            if not symbol:
                logger.warning(f"Received tick for unknown token: {token}")
                return
            
            # Update statistics
            with self._lock:
                self.ticks_received += 1
                self.last_tick_time = timestamp
            
            # Invoke callback
            self.on_tick_callback(symbol, ltp, volume, timestamp)
            
        except Exception as e:
            logger.exception(f"Error parsing tick data: {e}")
    
    def connect(self) -> bool:
        """Connect to WebSocket server.
        
        Returns:
            True if connection successful, False otherwise.
        """
        try:
            # Ensure authenticated
            if not self.auth_manager.ensure_authenticated():
                logger.error("Failed to authenticate for WebSocket")
                return False
            
            client = self.auth_manager.get_client()
            if not client:
                logger.error("Failed to get SmartConnect client")
                return False
            
            # Get feed token
            feed_token = self.auth_manager._feed_token
            if not feed_token:
                logger.error("Feed token not available")
                return False
            
            # Get client code
            client_code = self.auth_manager._config.client_id
            
            # Create WebSocket instance
            self.ws = SmartWebSocketV2(
                auth_token=feed_token,
                api_key=self.auth_manager._config.api_key,
                client_code=client_code,
                feed_token=feed_token
            )
            
            # Set callbacks
            self.ws.on_open = self._on_open
            self.ws.on_close = self._on_close
            self.ws.on_error = self._on_error
            self.ws.on_data = self._on_data
            
            # Connect (non-blocking)
            self.ws.connect()
            
            # Wait for connection
            max_wait = 10  # seconds
            start_time = time.time()
            while not self._connected and (time.time() - start_time) < max_wait:
                time.sleep(0.1)
            
            if self._connected:
                logger.info("WebSocket connected successfully")
                self.connection_attempts += 1
                return True
            else:
                logger.error("WebSocket connection timeout")
                return False
            
        except Exception as e:
            logger.exception(f"WebSocket connection error: {e}")
            return False
    
    def subscribe(self, symbols: List[str], exchange: str = "NSE") -> bool:
        """Subscribe to symbols for real-time data.
        
        Args:
            symbols: List of trading symbols.
            exchange: Exchange segment.
        
        Returns:
            True if subscription successful, False otherwise.
        """
        if not self._connected:
            logger.error("Cannot subscribe: WebSocket not connected")
            return False
        
        try:
            # Ensure instrument master loaded
            self.instrument_master.ensure_loaded()
            
            # Build subscription list
            subscription_list = []
            exchange_type = self._get_exchange_type(exchange)
            
            for symbol in symbols:
                token = self.instrument_master.get_token(symbol, exchange)
                if not token:
                    logger.warning(f"Token not found for {symbol}, skipping")
                    continue
                
                subscription_list.append({
                    "exchangeType": exchange_type,
                    "tokens": [token]
                })
                
                # Store mapping
                self._token_to_symbol[token] = symbol
                self._subscribed_tokens.add(token)
            
            if not subscription_list:
                logger.error("No valid tokens to subscribe")
                return False
            
            # Subscribe via WebSocket
            self.ws.subscribe(self.mode, subscription_list)
            
            logger.info(f"Subscribed to {len(subscription_list)} symbols in {exchange}")
            return True
            
        except Exception as e:
            logger.exception(f"Subscription error: {e}")
            return False
    
    def unsubscribe(self, symbols: List[str], exchange: str = "NSE") -> bool:
        """Unsubscribe from symbols.
        
        Args:
            symbols: List of trading symbols.
            exchange: Exchange segment.
        
        Returns:
            True if unsubscription successful, False otherwise.
        """
        if not self._connected:
            logger.warning("Cannot unsubscribe: WebSocket not connected")
            return False
        
        try:
            unsubscription_list = []
            exchange_type = self._get_exchange_type(exchange)
            
            for symbol in symbols:
                token = self.instrument_master.get_token(symbol, exchange)
                if not token or token not in self._subscribed_tokens:
                    continue
                
                unsubscription_list.append({
                    "exchangeType": exchange_type,
                    "tokens": [token]
                })
                
                # Remove mapping
                self._token_to_symbol.pop(token, None)
                self._subscribed_tokens.discard(token)
            
            if unsubscription_list:
                self.ws.unsubscribe(self.mode, unsubscription_list)
                logger.info(f"Unsubscribed from {len(unsubscription_list)} symbols")
            
            return True
            
        except Exception as e:
            logger.exception(f"Unsubscription error: {e}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from WebSocket server."""
        if self.ws:
            try:
                self.ws.close()
                logger.info("WebSocket disconnected")
            except Exception as e:
                logger.warning(f"Error during disconnect: {e}")
            finally:
                with self._lock:
                    self._connected = False
                    self._subscribed_tokens.clear()
                    self._token_to_symbol.clear()
    
    def is_connected(self) -> bool:
        """Check if WebSocket is connected.
        
        Returns:
            True if connected, False otherwise.
        """
        with self._lock:
            return self._connected
    
    def get_subscribed_count(self) -> int:
        """Get count of subscribed tokens.
        
        Returns:
            Number of subscribed tokens.
        """
        with self._lock:
            return len(self._subscribed_tokens)
    
    def get_stats(self) -> Dict:
        """Get WebSocket statistics.
        
        Returns:
            Dict with WebSocket statistics.
        """
        with self._lock:
            return {
                "connected": self._connected,
                "subscribed_count": len(self._subscribed_tokens),
                "ticks_received": self.ticks_received,
                "connection_attempts": self.connection_attempts,
                "last_tick_time": self.last_tick_time.isoformat() if self.last_tick_time else None,
            }
    
    def _get_exchange_type(self, exchange: str) -> int:
        """Map exchange string to SmartAPI exchange type.
        
        Args:
            exchange: Exchange segment (NSE, BSE, NFO, etc.).
        
        Returns:
            SmartAPI exchange type integer.
        """
        exchange_map = {
            "NSE": self.EXCHANGE_NSE_CM,
            "BSE": self.EXCHANGE_BSE_CM,
            "NFO": self.EXCHANGE_NSE_FO,
            "BFO": self.EXCHANGE_BSE_FO,
        }
        return exchange_map.get(exchange, self.EXCHANGE_NSE_CM)
