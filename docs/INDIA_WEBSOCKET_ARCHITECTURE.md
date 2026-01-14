# India Market WebSocket Architecture

## Overview

The India Momentum Runner uses WebSocket-based real-time data ingestion to support ~200 symbols (NIFTY 50 + Midcap + Smallcap) without REST API rate-limit constraints.

## Why WebSocket?

### REST API Limitations
- **Rate Limits**: SmartAPI REST endpoints have rate limits (~3 requests/second)
- **Polling Overhead**: Fetching OHLC for 200 symbols every minute = 200 requests/minute
- **Latency**: REST polling introduces 30-60 second delays
- **API Budget**: Exceeds daily API call limits quickly

### WebSocket Advantages
- **Single Connection**: One WebSocket connection handles all 200 symbols
- **Real-Time**: Tick-level data with <1 second latency
- **No Rate Limits**: WebSocket has no per-request rate limits
- **Scalable**: Supports up to 1000 instrument tokens per session

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     India Momentum System                        │
│                     (WebSocket-Based)                            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  SmartAPI WebSocket v2                                          │
│  ws://smartapisocket.angelone.in/smart-stream                   │
│  - LTP Mode (Last Traded Price)                                 │
│  - Up to 1000 token subscriptions                               │
│  - Binary tick format                                           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼ (ticks: symbol, price, volume, timestamp)
┌─────────────────────────────────────────────────────────────────┐
│  IndiaWebSocketClient                                           │
│  - Connection management                                        │
│  - Auto-reconnect with exponential backoff                      │
│  - Binary tick parsing                                          │
│  - Token-to-symbol mapping                                      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼ (tick callback)
┌─────────────────────────────────────────────────────────────────┐
│  CandleAggregator                                               │
│  - Maintains SymbolState for each symbol                        │
│  - Aggregates ticks into 1-minute candles                       │
│  - Minute-boundary finalization (timer-based)                   │
│  - Persists to Parquet (schema-compatible)                      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼ (candles finalized every minute)
┌─────────────────────────────────────────────────────────────────┐
│  MomentumEngine (UNCHANGED)                                     │
│  - VWAP calculation                                             │
│  - HOD proximity check                                          │
│  - Relative volume analysis                                     │
│  - Signal generation                                            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼ (signals)
┌─────────────────────────────────────────────────────────────────┐
│  ObservationLogger                                              │
│  - Signal logging                                               │
│  - EOD review generation                                        │
│  - Executive dashboard data                                     │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Market Open (09:00 IST)
- Windows Scheduled Task triggers `start_india_momentum.ps1`
- Script starts `india_momentum_runner.py`
- Runner authenticates with SmartAPI
- Loads 200-symbol watchlist from config
- Connects to WebSocket
- Subscribes to all 200 instrument tokens (LTP mode)
- Starts candle aggregator timer

### 2. During Market Hours (09:15 - 15:30 IST)
- **Tick Reception**: WebSocket receives ticks (price, volume, timestamp)
- **State Update**: Each tick updates corresponding `SymbolState`
  - Updates: last_price, cumulative_volume, VWAP components, HOD
  - Aggregates into current 1-minute candle (OHLC)
- **Minute Finalization** (every minute on the minute boundary):
  - Timer triggers `CandleAggregator.finalize_candles()`
  - All symbols finalize their current candle
  - Candles persisted to Parquet: `data/processed/candles/intraday/NSE_{SYMBOL}_1m.parquet`
  - Callback invokes `MomentumEngine.run_on_all(watchlist)`
  - Signals logged via `ObservationLogger`
  - Executive dashboard data updated

### 3. Market Close (15:45 IST)
- Windows Scheduled Task triggers `stop_india_momentum.ps1`
- Script sends graceful shutdown signal to runner
- Runner unsubscribes from all symbols
- Disconnects WebSocket
- Finalizes any remaining candles
- Runs EOD review generator
- Exits cleanly

## Component Details

### SymbolState (In-Memory)
Each symbol maintains:
```python
{
    "last_price": float,
    "cumulative_volume": int,
    "vwap_numerator": float,  # sum(price * volume)
    "vwap_denominator": float,  # sum(volume)
    "high_of_day": float,
    "low_of_day": float,
    "current_1m_open": float,
    "current_1m_high": float,
    "current_1m_low": float,
    "current_1m_close": float,
    "current_1m_volume": int,
    "current_candle_start": datetime,
    "tick_count": int,
    "candles_generated": int
}
```

### Candle Schema (Output)
Compatible with existing processed data:
```python
{
    "symbol": str,
    "exchange": str,
    "timestamp": datetime,  # Minute-aligned (e.g., 09:15:00, 09:16:00)
    "open": float,
    "high": float,
    "low": float,
    "close": float,
    "volume": int
}
```

## WebSocket Subscription Limits

### SmartAPI WebSocket v2 Limits
- **Max Tokens per Session**: 1000
- **Max Concurrent Connections**: 3 per client code
- **Subscription Modes**:
  - LTP (1): Last Traded Price + Volume
  - QUOTE (2): LTP + OHLC
  - SNAP_QUOTE (3): Full market depth

### Current Usage
- **Symbols**: ~200 (NIFTY 50 + Midcap + Smallcap)
- **Mode**: LTP (1) - Minimal bandwidth
- **Headroom**: 800 tokens available for future expansion

## Rollback Procedure

If WebSocket proves unstable, rollback to REST-based approach:

### Step 1: Stop WebSocket Runner
```powershell
# Stop scheduled task
Unregister-ScheduledTask -TaskName "India_Momentum_Start" -Confirm:$false
Unregister-ScheduledTask -TaskName "India_Momentum_Stop" -Confirm:$false

# Stop running process
Get-Process -Name python | Where-Object {$_.CommandLine -like "*india_momentum_runner*"} | Stop-Process -Force
```

### Step 2: Revert to REST Runner
```bash
# Use original REST-based runner
python observations/momentum_live_runner.py --interval 5
```

### Step 3: Restore Scheduled Tasks (Optional)
```powershell
# Modify start script to use REST runner
# Edit: scripts/india_scheduler/start_india_momentum.ps1
# Change: observations\india_momentum_runner.py
# To: observations\momentum_live_runner.py --interval 5
```

## Troubleshooting

### WebSocket Connection Failures
**Symptom**: "Failed to connect to WebSocket"

**Causes**:
1. Invalid authentication token
2. Network connectivity issues
3. SmartAPI server downtime

**Solutions**:
1. Check `.env` credentials (ANGEL_API_KEY, ANGEL_CLIENT_ID, etc.)
2. Verify internet connection
3. Check SmartAPI status page
4. Review logs: `logs/india_momentum_runner.log`

### Tick Gaps
**Symptom**: No ticks received for extended period

**Causes**:
1. WebSocket disconnected silently
2. Market closed/holiday
3. Symbol suspended

**Solutions**:
1. Check `india_health_check.py` output
2. Verify market hours
3. Check NSE/BSE announcements for suspensions

### Candle Mismatches
**Symptom**: Generated candles don't match broker data

**Causes**:
1. Tick aggregation logic error
2. Timestamp alignment issues
3. Missing ticks during reconnection

**Solutions**:
1. Compare with REST-based candles (if available)
2. Check for gaps in tick timestamps
3. Verify minute-boundary alignment
4. Review `SymbolState.update_tick()` logic

### Memory Issues
**Symptom**: High memory usage, process crashes

**Causes**:
1. Too many symbols (>1000)
2. Memory leak in tick processing
3. Parquet file accumulation

**Solutions**:
1. Reduce symbol count
2. Monitor with `psutil` or Task Manager
3. Implement periodic memory cleanup
4. Archive old Parquet files

## Performance Metrics

### Expected Performance (200 Symbols)
- **Ticks per Second**: ~50-200 (market-dependent)
- **Candles per Minute**: 200 (one per symbol)
- **Memory Usage**: ~200-500 MB
- **CPU Usage**: <10% (single core)
- **Network Bandwidth**: ~10-50 KB/s

### Health Check Thresholds
- **WebSocket Connected**: Must be `true`
- **Subscribed Count**: Must equal expected count (200)
- **Candles Generated**: Must be >0 per minute during market hours
- **REST API Calls**: Must be 0 for live OHLC/LTP
- **Tick Flow**: Must have ticks in last 60 seconds

## Safety Guarantees

### Code Isolation
- **India Code**: `ingestion/india_ingestion/`, `observations/india_momentum_runner.py`
- **US Code**: `research_modules/`, `data_pipeline/`, Alpha Vantage ingestion
- **No Cross-Imports**: Verified via grep search
- **Separate Configs**: India uses `AngelConfig`, US uses separate config

### Momentum Logic Unchanged
- **Engine**: `src/core_modules/momentum_engine/momentum_engine.py` - UNTOUCHED
- **Thresholds**: VWAP, HOD proximity, volume multiplier - UNCHANGED
- **Signal Validation**: Existing logic preserved
- **EOD Review**: Existing generator unchanged

### Data Integrity
- **Schema Compatibility**: WebSocket candles match REST candles exactly
- **Idempotency**: Parquet deduplication on (symbol, timestamp)
- **Auditability**: All ticks logged, candles timestamped
- **Rollback**: Can revert to REST without data loss

## Future Enhancements

### Phase 2 (Optional)
- **Multi-Timeframe**: Aggregate 1m candles into 5m, 15m, 1h
- **QUOTE Mode**: Upgrade to QUOTE mode for OHLC ticks (reduce aggregation complexity)
- **Tick Replay**: Store raw ticks for backtesting and debugging
- **Advanced Health**: Integrate with monitoring tools (Prometheus, Grafana)

### Phase 3 (Optional)
- **Order Execution**: Integrate with SmartAPI order placement
- **Risk Management**: Real-time position tracking and limits
- **Multi-Account**: Support multiple client codes for scaling
