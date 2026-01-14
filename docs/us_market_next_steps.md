# US Market Ingestion & Analytics Foundation: Strategic Design

## PART 1: US MARKET ENGINE & PIPELINE ARCHITECTURE

### 1. High-Level Architecture

The US Market Engine is designed as an autonomous subsystem within the `TraderFund` repository. While it shares the repository's root utilities (logging, core configuration loaders), it operates in complete isolation from the India (Angel SmartAPI) pipeline to prevent domain contamination.

**System Topology:**
- **Infrastructure Path**: `ingestion/api_ingestion/alpha_vantage/`
  - Completely separate Python namespace from `angel_smartapi`.
- **Data Path**:
  - Raw: `data/raw/us/` (JSON/CSV)
  - Staging: `data/staging/us/` (Parquet, lightly typed)
  - Analytics: `data/analytics/us/` (Parquet, fully typed, adjusted, indexed)

**Conceptual Alignment:**
The US engine mirrors the "Layered Data Lake" pattern used by the India pipeline but adapts the implementation details to fit Alpha Vantage's REST-heavy, rate-limited nature (opposed to SmartAPI's WebSocket-heavy nature).

### 2. US Market Engine Responsibilities

The engine has four distinct responsibilities:

1.  **API Gateway**: Managing the connection to Alpha Vantage, strictly enforcing authentication and rate limits. It is the *only* component allowed to make outbound HTTP requests to `alphavantage.co`.
2.  **Yield Maximization**: Given strict rate limits, the engine is responsible for prioritizing "high value" fetches (e.g., recent daily closes) over "low value" backfills during constrained windows.
3.  **Symbol Lifecycle**: Maintaining an independent registry of US symbols, tracking active status, delistings, and instrument metadata.
4.  **Audit & Lineage**: Every data point in `analytics` must be traceable to a specific raw JSON file and API request ID (if available), ensuring full reproducibility.

### 3. Pipeline Stages

| Stage | Component | Input | Output | Responsibility |
| :--- | :--- | :--- | :--- | :--- |
| **0. Master** | `SymbolMaster` | `LISTING_STATUS` API | `master/us/symbols.csv` | Universe definition and filtering. |
| **1. Ingest** | `USMarketIngestor` | `SymbolMaster` | `raw/us/{date}/{sym}.json` | Reliable fetch, rate limit handling, raw persistence. |
| **2. Normalize** | `USNormalizer` | Raw JSON | `staging/us/{freq}/{sym}.parquet` | Type casting, UTC standardization, schema alignment. |
| **3. Curate** | `USCurator` | Staging Parquet | `analytics/us/prices/{freq}.parquet` | De-duplication, quality checks, corporate action adjustments. |

### 4. Data Contracts

**Schema: US OHLCV (Analytics Layer)**
Explicitly different from India schema to reflect market specifics.

```python
class US_OHLCV:
    timestamp: datetime64[ns, UTC]  # Strict UTC
    symbol: string                  # Ticker (e.g., AAPL)
    open: float64
    high: float64
    low: float64
    close: float64
    volume: int64
    # US Specifics
    adjusted_close: float64         # Alpha Vantage specific
    dividend_amt: float64           # Captured at ingestion
    split_coefficient: float64      # Captured at ingestion
    ingest_timestamp: datetime64    # Audit trail
```

**Key Distinctions:**
- **Timezone**: US data is stored in UTC (market hours 13:30-20:00 UTC). India data is stored in IST. Cross-market comparison logic must handle this conversion at *read time*, not write time.
- **Adjustments**: US pipeline stores "Adjusted" columns natively as Alpha Vantage provides them. India pipeline typically calculates adjustments from corporate action logs.

### 5. Scheduling & Orchestration

- **`US_Daily_Close_Job`**: Runs at 17:00 EST (21:00 UTC). Fetches daily data for the active universe.
- **`US_Symbol_Refresh_Job`**: Runs weekly (Monday 08:00 EST). Updates the universe definition.
- **`US_Backfill_Job`**: Low-priority background worker. Fills gaps in history when rate limit tokens are available.
- **Recovery**: If a job fails (e.g., 50% completion), the next run detects missing raw files for today's date and resumes ONLY the missing symbols.

### 6. Explicit Non-Goals
- **Real-Time Data**: The engine is not designed for sub-minute latency or WebSocket streaming.
- **Order Management**: No execution capability.
- **Fundamental Data**: Initial scope is Price/Volume only (no Balance Sheets/Earnings).

---

## PART 2: US SYMBOL MASTER STRATEGY

### 1. Purpose of Symbol Master
The `SymbolMaster` decouples the *definition* of the market from the *fetching* of data. This prevents the ingestor from iterating blindly or relying on hardcoded lists. It serves as the single source of truth for "What is a valid US stock?"

### 2. Symbol Sources
- **Primary**: Alpha Vantage `LISTING_STATUS` endpoint (CSV).
- **Secondary (Future)**: Manual override file (`data/master/us/manual_overrides.csv`) to force-include/exclude specific tickers that the API might mislabel.

### 3. Symbol Metadata Model
The master registry (`symbols.csv`) contains:
- `symbol`: Unique identifier.
- `name`: Human-readable name (for UI/Reporting).
- `exchange`: NYSE, NASDAQ, AMEX.
- `assetType`: Stock, ETF.
- `status`: Active, Delisted.
- `ipoDate`: Listing date (helps optimize backfill start times).
- `last_active_date`: Date verification of trading.

### 4. Lifecycle Management
- **Onboarding**: A new symbol appearing in `LISTING_STATUS` is automatically added to the queue for "Historical Backfill".
- **Delisting**: Symbols disappearing from `active` status are marked `status=delisted` but RETAINED in the master file to preserve pointer integrity for historical data.
- **Renames**: Ticker changes (e.g., FB -> META) are handled by creating a new entry. Analytical linkage is a future feature (Mapping Layer).

### 5. Interaction with Pipelines
- **Ingestor Reader**: The ingestor reads `symbols.csv`, filters for `status='Active'`, and generates the fetch list.
- **Isolation**: If the `LISTING_STATUS` API fails, the ingestor uses the *last known good* local copy of `symbols.csv`, ensuring pipeline robustness.

---

## PART 3: RATE-LIMIT OPTIMIZED ALPHA VANTAGE INGESTION ALGORITHM

### 1. Rate Limit Constraints
- **Constraint**: 5 requests per minute, 500 requests per day (Standard Free).
- **Implication**: We can only ingest ~500 symbols daily. The US market has ~7000+ symbols.
- **Strategy**: We cannot ingest the *entire* market daily on the free tier. We must prioritize.

### 2. Ingestion Prioritization
Ranking logic for daily fetches:
1.  **Tier A (Core)**: S&P 500 + Nasdaq 100 components. (Always fetch).
2.  **Tier B (Watchlist)**: User-defined focus list. (Always fetch).
3.  **Tier C (Rotation)**: Remaining universe, rotated daily. It might take ~14 days to cycle through the entire liquidity tail.

### 3. Request Scheduling Strategy
We implement a **Token Bucket Scheduler**:
- **Bucket Capacity**: 5 tokens.
- **Refill Rate**: 1 token every 12 seconds.
- **Logic**:
  - Ingestor requests token.
  - If available, execute API call immediately.
  - If empty, sleep `refill_time`.
  - **Global Daily Counter**: Stop all execution after 490 calls (preserving 10 for emergency checks).

### 4. Incremental Fetch Logic
- **`outputsize=compact`**: Always usage for standard daily updates. Costs 1 call, returns 100 days.
- **Optimization**: Before fetching, check `raw/us/{today}/{symbol}_daily.json`. If exists, skip. This allows restarting crashed jobs without penalty.

### 5. Failure & Retry Design
- **Soft Limit (Note)**: If response contains "Note", treat as 429. Backoff exponentially (60s -> 120s -> 300s).
- **Hard Error**: If 5xx, retry 3 times.
- **Isolation**: A single symbol failure logs an error and *moves to the next*; it does not crash the batch.

### 6. Backfill Strategy (The "Constraint Problem")
Backfilling full history for 500 symbols (`outputsize=full`) consumes 500 calls.
- **Design**: Backfill is a dedicated mode.
- **Execution**: User explicitly triggers "Backfill S&P500". The system estimates days required (e.g., "This will take 1 day of quota") and executes.

---

## PART 4: UNIFIED ANALYTICS LAYER (INDIA + US) WITHOUT RAW DATA MIXING

### 1. Philosophy
**Integration at the Insight Level, Isolation at the Data Level.**
We never merge raw tables. We join *processed outputs*. A unified analytics layer acts as a "View" or "Interface" over distinct physics data silos.

### 2. Market-Agnostic Analytics Layer
We introduce an abstract **MarketDataAdapter** interface:

```python
class MarketDataAdapter:
    def get_returns(self, symbols: List[str], start: date, end: date) -> pd.DataFrame
    def get_volatility(self, symbols: List[str], window: int) -> pd.Series
```

**Implementations:**
- `IndiaSmartAPIAdapter`: Connects to `data/analytics/india/`
- `USAlphaVantageAdapter`: Connects to `data/analytics/us/`

The Analytics Engine instantiates the appropriate adapter based on the requested symbol's region (found via a Global Symbol Resolver).

### 3. Example Use Cases
- **Correlation Matrix**:
  - Request: `["AAPL" (US), "INFY" (IN)]`
  - Engine fetches AAPL (UTC times) and INFY (IST times).
  - Normalization: Aligns timestamps to a common axis (e.g., UTC dates), handling holiday mismatch via forward-fill.
  - Compute: Correlation on standard overlapping dates.
- **Strategy Backtest**:
  - A momentum strategy logic is written *once*.
  - It runs against the `MarketDataAdapter`.
  - Depending on config, it drives US execution or India execution simulation.

### 4. Data Access Patterns
- **Read-Only**: Analytics wrappers treats the Parquet stores as read-only.
- **Lazy Loading**: Using tools like Polars/DuckDB to query across partitioned Parquet files without loading full history into memory.

### 5. Future Readiness
- **Narrative Engines**: Can ingest news from US sources (Alpha Vantage) and India sources (local APIs) into a common "Event Stream" schema (Timestamp, Sentiment, Entity) which links back to the separated market data tickers.
- **Multi-Currency Portfolio**: The unified layer will handle FX conversion (USD <> INR) for consolidated P&L reporting, consuming an FX rate table managed by the US engine (Alpha Vantage FX endpoint).
