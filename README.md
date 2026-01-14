# TraderFund Platform

TraderFund is a disciplined algorithmic trading research and observation platform. It implements a multi-layer data pipeline—from raw ingestion to processed analytics—focused on momentum-based intraday strategies.

## Core Modules

### 1. Data Ingestion (`ingestion/`)

#### India Market (WebSocket-Based)
- **WebSocket Ingestion (`india_ingestion/`)**: Real-time tick data via SmartAPI WebSocket v2
- **Supports ~200 symbols** (NIFTY 50 + Midcap + Smallcap) without REST rate-limit constraints
- **In-Memory Candle Aggregation**: Tick-to-candle conversion with minute-boundary finalization
- **Zero REST Polling**: All live data via WebSocket; REST only for authentication and instrument master

#### US Market (REST-Based)
- **Alpha Vantage Integration**: Batch polling for historical and daily updates
- **Research Pipeline**: Symbol filtering funnel from ~500 symbols to ~5-15 confirmed momentum
- **Completely Separate**: No code sharing with India market infrastructure

### 2. Processed Data Layer (`processing/`)
- **Silver Layer**: Raw JSONL data is cleaned, deduplicated, and converted to high-performance Parquet format.
- **Idempotency**: Processing logic ensures that re-running on the same data produces identical results.

### 3. Momentum Engine (`src/core_modules/momentum_engine/`)
- **V0 Strategy**: High-probability momentum detection using VWAP, Relative Volume, and High-of-Day (HOD) proximity.
- **Live Readiness**: Designed to consume standardized dataframes, making it compatible with both live feeds and historical datasets.

### 4. Live Observation (`observations/`)
- **Clinical Review**: Automated logging of generated signals into CSV templates for post-trade review.
- **Signal Validation**: Automated T+5 and T+15 performance tracking and classification (A/B/C/D).
- **Daily Review**: Automated generation of EOD reports summarizing signal quality and failure patterns.

### 5. Historical Replay (`historical_replay/`)
- **Diagnostic Replay**: Minute-by-minute historical simulation without lookahead bias.
- **Learning Tool**: Designed for studying past price action through the lens of the same engine used in live markets.
- **Batch Processing**: Supports replaying entire months or watchlist groups with a single command.

## Getting Started

1. **Setup**:
   ```bash
   pip install -r requirements.txt
   # Configure .env with Angel One credentials
   ```

2. **Ingest Data**:
   ```bash
   python -m ingestion.api_ingestion.angel_smartapi.market_data_ingestor
   ```

3. **Process Candles**:
   ```bash
   python processing/intraday_candles_processor.py
   ```

4. **Run Replay**:
   ```bash
   python historical_replay/momentum_intraday/cli.py --symbol ALL --date 2025-12
   ```

## Governance & Safety
- **PHASE LOCK**: All modules adhere to strict Phase-Lock restrictions.
- **Diagnostic Only**: Historical Replay and Paper Trading modules are strictly for learning and observation, not for live trading or parameter optimization.
- **No Lookahead**: Core abstractions like `CandleCursor` prevent any future-data leakage during simulations.

