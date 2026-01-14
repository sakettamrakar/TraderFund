# WebSocket Test Migration - README

## Overview

This directory contains **TEST-ONLY** WebSocket ingestion components for staged migration from REST polling to WebSocket streaming.

**Status**: NOT PRODUCTION ENABLED

## Staged Migration Approach

### Stage 1: Single Symbol Test
- Test with ONE symbol only (RELIANCE)
- Validate tick → candle → momentum pipeline
- Duration: 10-15 minutes
- Output: Separate test directory

### Stage 2: NIFTY 50 Expansion
- Expand to NIFTY 50 symbols (50 symbols)
- Same WebSocket connection
- Independent state per symbol
- Duration: 10-15 minutes

## Why WebSocket?

**REST Limitations:**
- Rate limits (~3 req/sec)
- Polling overhead for 50+ symbols
- 30-60 second latency

**WebSocket Advantages:**
- Single connection for all symbols
- Real-time tick data (<1 second)
- No rate-limit constraints
- Scales to 1000 tokens per session

## Components

### ws_client.py
Simplified WebSocket client for SmartAPI v2:
- LTP mode (Last Traded Price)
- Auto-reconnect
- Explicit validation logging

### symbol_state.py
In-memory state per symbol:
- Tick aggregation
- VWAP calculation
- HOD tracking
- 1-minute OHLC building

### candle_builder.py
Minute-boundary candle finalization:
- Timer-based finalization
- Schema-compatible output
- Test output separation

### ws_healthcheck.py
Explicit validation checks:
- WebSocket connected
- Subscription count
- Ticks received
- Candles finalized
- NO REST calls

## Running Tests

### Stage 1: Single Symbol
```bash
python observations/websocket_test_runner.py --ws-test-mode --stage 1 --duration 15
```

**Expected Output:**
- ✓ WebSocket connected
- ✓ Subscribed to 1 symbol (RELIANCE)
- ✓ Ticks received (sample logged)
- ✓ Candle finalized at minute boundary
- ✓ Momentum evaluation executed (dry-run)
- ✓ NO REST calls

### Stage 2: NIFTY 50
```bash
python observations/websocket_test_runner.py --ws-test-mode --stage 2 --duration 15
```

**Expected Output:**
- ✓ WebSocket connected
- ✓ Subscribed to 10 symbols (NIFTY 50 subset)
- ✓ Ticks received for all symbols
- ✓ Candles finalized for all symbols
- ✓ Momentum evaluation executed (dry-run)
- ✓ NO REST calls

## Safety Guards

1. **Explicit Flag Required**: `--ws-test-mode` must be provided
2. **Test Output Separation**: Candles saved to `data/test/websocket_candles/`
3. **No Live CSV Writes**: Test mode does NOT write to observation CSVs
4. **Short Duration**: Test runs for 10-15 minutes only
5. **No Scheduling**: No Task Scheduler integration in test mode

## Validation Checklist

### Stage 1 Validation
- [ ] WebSocket connects successfully
- [ ] Subscription count = 1
- [ ] Sample ticks logged
- [ ] 1-minute candle finalized
- [ ] Candle schema matches existing processed data
- [ ] Momentum evaluation runs without errors
- [ ] Zero REST API calls for live data
- [ ] Test output saved to correct directory

### Stage 2 Validation
- [ ] WebSocket connects successfully
- [ ] Subscription count = 50 (or subset)
- [ ] Ticks received for all symbols
- [ ] Candles finalized for all symbols
- [ ] Momentum evaluation runs for all symbols
- [ ] Zero REST API calls for live data
- [ ] Performance acceptable (CPU, memory)

## Rollback

To disable WebSocket test mode:
- Simply stop running the test runner
- No scheduled tasks to disable
- No production impact

## Next Steps (After Validation)

1. **Stage 1 Complete** → Proceed to Stage 2
2. **Stage 2 Complete** → Consider production rollout
3. **Production Rollout** → Separate implementation plan required

## Files

- `__init__.py` - Package init
- `ws_client.py` - WebSocket client
- `symbol_state.py` - In-memory state
- `candle_builder.py` - Candle finalization
- `ws_healthcheck.py` - Health validation

## Logs

Test logs saved to:
- `logs/websocket_test.log`

Test candles saved to:
- `data/test/websocket_candles/NSE_{SYMBOL}_1m_test.parquet`

## Important Notes

- **NOT for production use**
- **Requires --ws-test-mode flag**
- **Test output separate from live data**
- **No impact on existing REST-based system**
- **US market code completely untouched**
