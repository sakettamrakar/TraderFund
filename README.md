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

5. **Run Validation (Single Phase)**:
   ```bash
   python -m traderfund.validation.validation_runner --phase ingestion --hook manual --market US
   ```

6. **Run Validation Sweep (PowerShell)**:
   ```powershell
   foreach ($phase in 'ingestion','memory','research','evaluation','dashboard') {
       python -m traderfund.validation.validation_runner --phase $phase --hook manual --market US
       if ($LASTEXITCODE -ne 0) { break }
   }
   ```

7. **Run Safe Auto-Remediation For One Phase**:
   ```bash
   python -m traderfund.validation.validation_runner --phase dashboard --hook manual --market US --auto-remediate
   ```
   Use this only after reviewing the failure and only for the specific phase you want the subsystem to repair.

8. **Run Daily Scheduler With Validation Review Enabled**:
   ```bash
   python infra_hardening/scheduler/wrapper.py --mode daily --enable-validation-review
   ```
   This adds an end-of-run validation review task that aggregates the latest phase summaries into `logs/validation/daily/`. It is opt-in and is not part of the default daily workflow unless you pass the flag.

9. **Start Dashboard API**:
   ```bash
   python scripts/start_dashboard_api.py --reload
   ```

10. **Start Dashboard Frontend**:
   ```bash
   cd src/dashboard/frontend
   npm run dev
   ```

11. **VS Code Tasks**:
   Use the workspace tasks in `.vscode/tasks.json` to run ingestion, processing, the dashboard API, and the dashboard frontend directly from VS Code.

## Local Port Management

TraderFund uses a dedicated local port range of `21000-21050` to avoid conflicts with other projects on the same machine.

- Default assignments live in `.env`.
- Runtime assignments are written to `.runtime/service_ports.json`.
- The optional global range registry is written to `~/.local_ports_registry.json`.
- If a preferred port is already in use, TraderFund automatically picks the next free port in range and logs the change before startup.

Useful commands:

```bash
python -m utils.port_manager show
python -m utils.port_manager assign dashboard_api dashboard_frontend
```

When adding this pattern to future projects:

1. Reserve a non-overlapping project range in `.env`.
2. Add a shared port manager that persists runtime assignments.
3. Make every startup path read env defaults and runtime assignments instead of hardcoded ports.
4. Keep frontend proxies and internal service URLs dynamic by reading the shared runtime assignment file.

## Governance & Safety
- **PHASE LOCK**: All modules adhere to strict Phase-Lock restrictions.
- **Diagnostic Only**: Historical Replay and Paper Trading modules are strictly for learning and observation, not for live trading or parameter optimization.
- **No Lookahead**: Core abstractions like `CandleCursor` prevent any future-data leakage during simulations.
- **Self-Healing Validation**: Automated remediation is limited to explicitly safe actions and must never modify capital, execution, or raw source data.

