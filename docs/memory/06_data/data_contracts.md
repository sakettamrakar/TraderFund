# Data Contracts

> [!IMPORTANT]
> **Authoritative Source**: `docs/memory/03_domain/domain_model.md` is CANONICAL.
> **Conflict Handling**: Where legacy source docs conflict with Domain Model, mark OPEN_CONFLICT.

---

## 1. Source Systems

### 1.1 Alpha Vantage (US Market)

| Property | Value |
| :--- | :--- |
| **Owner** | Ingestion US (L0) |
| **Base URL** | `https://www.alphavantage.co/query` |
| **Auth** | API Key-based (stateless) |
| **Protocol** | REST (HTTPS) |
| **Rate Limits** | Token-bucket: `MAX_CALLS_PER_MINUTE`, `MAX_CALLS_PER_DAY` |
| **Markets Served** | US (NYSE, NASDAQ) |
| **Domain Entities** | Canonical Data (L0), RegimeState inputs (L1), FactorSignal inputs (L4) |

**Endpoints Used**:

| Endpoint | Purpose | Mapped Domain Entity | Refresh Cadence |
| :--- | :--- | :--- | :--- |
| `LISTING_STATUS` | Symbol universe (active stocks) | Symbol Master (L0) | Weekly (Monday) |
| `TIME_SERIES_DAILY_ADJUSTED` | Daily OHLCV + adjustments | Canonical Data (L0) | Daily (17:00 ET) |
| `TIME_SERIES_INTRADAY` | Intraday OHLCV (5min) | Canonical Data (L0) | Hourly / EOD (when rate permits) |
| `INCOME_STATEMENT` | Annual/quarterly income | Fundamental Lens input (L6) | Quarterly (deferred — RC-4) |
| `BALANCE_SHEET` | Balance sheet data | Fundamental Lens input (L6) | Quarterly (deferred — RC-4) |
| `CASH_FLOW` | Cash flow statement | Fundamental Lens input (L6) | Quarterly (deferred — RC-4) |

**Failure Modes**:
- Rate limit exceeded (HTTP 429) → retry with exponential backoff
- Symbol not found → log to retry queue, skip
- API key exhaustion → rotate to next key in pool

*(Sources: `docs/us_market_engine_design.md`, `docs/contracts/proxy_dependency_contracts.md`)*

---

### 1.2 Angel One SmartAPI (India Market)

| Property | Value |
| :--- | :--- |
| **Owner** | Ingestion India (L0) |
| **WebSocket URL** | `ws://smartapisocket.angelone.in/smart-stream` |
| **REST Base** | SmartAPI REST endpoints |
| **Auth** | Session-based (Login/Token) |
| **Protocol** | WebSocket v2 (LTP Mode, binary ticks) + REST fallback |
| **Capacity** | Up to 1000 instrument tokens per session |
| **Markets Served** | India (NSE) |
| **Domain Entities** | Canonical Data (L0), MomentumEngine signals (Scanner) |

**Data Streams**:

| Stream | Purpose | Mapped Domain Entity | Refresh Cadence |
| :--- | :--- | :--- | :--- |
| WebSocket LTP | Real-time tick data (~200 symbols) | Canonical Data (L0) | Continuous (market hours 09:00–15:45 IST) |
| REST Historical | Intraday OHLC backfill | Canonical Data (L0) | On-demand / restart recovery |
| `instrument_master.json` | Token-to-symbol mapping | Symbol Master (L0) | Daily (pre-market) |

**Failure Modes**:
- WebSocket disconnect → auto-reconnect with exponential backoff
- Binary parse error → skip tick, log anomaly
- REST fallback available if WebSocket is unstable

*(Sources: `docs/INDIA_WEBSOCKET_ARCHITECTURE.md`, `docs/contracts/RAW_ANGEL_INTRADAY_SCHEMA.md`)*

---

### 1.3 Event Sources (News / Macro)

| Property | Value |
| :--- | :--- |
| **Owner** | Ingestion Events (L0 sub-pipeline) |
| **Sources** | Financial news APIs, macro event calendars, earnings announcements |
| **Protocol** | REST / RSS / Push (source-dependent) |
| **Markets Served** | US, India (cross-market) |
| **Domain Entities** | NarrativeObject inputs (L2) |
| **Status** | Implementation deferred (RQ-6) |

**Invariants**:
- Events timestamped at source publication time, not ingestion time
- Events are immutable after ingestion
- Interpretation is Narrative Engine's responsibility, not the ingestion layer's

*(Source: `docs/memory/05_components/ingestion_events.yaml`)*

---

## 2. Data Schemas

### 2.1 US Market OHLCV — Daily (Canonical)

| Column | Type | Description | Nullable |
| :--- | :--- | :--- | :--- |
| `timestamp` | `datetime64[ns, UTC]` | Candle open time (UTC) | NO |
| `symbol` | `string` | Ticker symbol (e.g., AAPL) | NO |
| `open` | `float64` | Raw open price | NO |
| `high` | `float64` | Raw high price | NO |
| `low` | `float64` | Raw low price | NO |
| `close` | `float64` | Raw close price | NO |
| `volume` | `int64` | Session volume | NO |
| `adj_close` | `float64` | Adjusted close (from AV) | NO |
| `dividend_amt` | `float64` | Dividend amount | YES (default 0.0) |
| `split_coef` | `float64` | Split coefficient | YES (default 1.0) |

**Storage**: `data/analytics/us/prices/{frequency}/`
**Format**: Apache Parquet
**Timezone**: UTC (strict)
**Mapped Domain Entity**: Canonical Data (L0)

*(Source: `docs/us_market_engine_design.md`)*

---

### 2.2 India Market — Raw Intraday OHLC

| Column | Type | Description | Nullable |
| :--- | :--- | :--- | :--- |
| `symbol` | `string` | Trading symbol (e.g., INFY) | NO |
| `exchange` | `string` | Exchange segment (e.g., NSE) | NO |
| `interval` | `string` | Candle interval (e.g., ONE_MINUTE) | NO |
| `timestamp` | `ISO8601` | Time of candle (IST, UTC+05:30) | NO |
| `open` | `float` | Opening price | NO |
| `high` | `float` | High price | NO |
| `low` | `float` | Low price | NO |
| `close` | `float` | Closing price | NO |
| `volume` | `integer` | Traded volume | NO |
| `source` | `string` | Fixed: `ANGEL_SMARTAPI` | NO |
| `ingestion_ts` | `ISO8601` | System persistence timestamp | NO |

**Storage**: `data/raw/api_based/angel/intraday_ohlc/`
**Format**: JSON Lines (.jsonl)
**Naming**: `{exchange}_{symbol}_{date}.jsonl`
**Timezone**: IST (UTC+05:30)
**Mapped Domain Entity**: Canonical Data (L0)

*(Source: `docs/contracts/RAW_ANGEL_INTRADAY_SCHEMA.md`)*

---

### 2.3 India Market — Processed Intraday (Canonical)

| Column | Type | Description | Nullable |
| :--- | :--- | :--- | :--- |
| `symbol` | `string` | Trading symbol | NO |
| `exchange` | `string` | Exchange segment | NO |
| `timestamp` | `Datetime64[ns, UTC+05:30]` | Standardized timezone-aware | NO |
| `open` | `Float64` | Opening price | NO |
| `high` | `Float64` | Highest price | NO |
| `low` | `Float64` | Lowest price | NO |
| `close` | `Float64` | Closing price | NO |
| `volume` | `Int64` | Traded volume | NO |

**Storage**: `data/processed/candles/intraday/`
**Format**: Apache Parquet
**Naming**: `{exchange}_{symbol}_1m.parquet`
**Dedup Key**: `(symbol, timestamp)` — latest `ingestion_ts` wins
**Sort Order**: `timestamp ASC` (strict)
**Mapped Domain Entity**: Canonical Data (L0)

**Processing Rules**:
- Idempotent: same raw input → same Parquet output
- Source metadata (`source`, `ingestion_ts`) stripped at processing
- No strategy-specific fields (no RSI, VWAP — those belong to Technical Lens L6)
- Volume must be non-negative

*(Source: `docs/contracts/PROCESSED_INTRADAY_SCHEMA.md`)*

---

### 2.4 India Market — LTP Snapshots

| Column | Type | Description | Nullable |
| :--- | :--- | :--- | :--- |
| `symbol` | `string` | Trading symbol | NO |
| `exchange` | `string` | Exchange segment | NO |
| `ltp` | `float` | Last Traded Price | NO |
| `open` | `float` | Day's open | NO |
| `high` | `float` | Day's high | NO |
| `low` | `float` | Day's low | NO |
| `close` | `float` | Previous day's close | NO |
| `timestamp` | `ISO8601` | Snapshot time | NO |
| `source` | `string` | Fixed: `ANGEL_SMARTAPI` | NO |
| `ingestion_ts` | `ISO8601` | System persistence timestamp | NO |

**Storage**: `data/raw/api_based/angel/ltp_snapshots/`
**Format**: JSON Lines (.jsonl)
**Mapped Domain Entity**: Canonical Data (L0)

*(Source: `docs/contracts/RAW_ANGEL_INTRADAY_SCHEMA.md`)*

---

### 2.5 Factor Context (Cognitive State)

| Section | Fields | Type | Mapped Domain Entity |
| :--- | :--- | :--- | :--- |
| `momentum` | `level`, `acceleration`, `breadth`, `dispersion`, `persistence`, `time_in_state` | `{state: enum, confidence: float}` | FactorSignal (L4) |
| `value` | `spread`, `trend`, `dispersion`, `mean_reversion_pressure` | `{state: enum, confidence: float}` | FactorSignal (L4) |
| `quality` | `signal`, `stability`, `defensiveness`, `drawdown_resilience` | `{state: enum, confidence: float}` | FactorSignal (L4) |
| `volatility` | `regime`, `dispersion` | `{state: enum, confidence: float}` | FactorSignal (L4) |
| `meta` | `factor_alignment`, `momentum_quality`, `alpha_environment`, `notes` | `enum / string` | Meta-Analysis (L3) |

**Storage**: `docs/evolution/context/{profile_id}/{window_id}/`
**Format**: YAML / JSON
**Refresh**: Per evaluation window
**Invariant**: Observational only — describes *what is*, not *what to do*

*(Source: `docs/evolution/context/factor_context_schema.md`)*

---

### 2.6 Regime Input Contract (Minimal Required)

| Symbol | Role | Description | Criticality |
| :--- | :--- | :--- | :--- |
| **SPY** | Equity Proxy | S&P 500 ETF | BLOCKING |
| **QQQ** | Equity Proxy | NASDAQ 100 ETF | BLOCKING |
| **VIX** | Volatility Proxy | CBOE Volatility Index | BLOCKING |
| **^TNX** | Rates Proxy | 10-Year Treasury Yield | BLOCKING |
| **^TYX** | Rates Proxy | 30-Year Treasury Yield | BLOCKING |
| **HYG** | Credit Proxy | High Yield Corporate Bond ETF | BLOCKING |
| **LQD** | Credit Proxy | Investment Grade Bond ETF | BLOCKING |

**Mapped Domain Entity**: RegimeState (L1)
**Minimum History**: ≥ 3 years (756 trading days)
**Frequency**: Daily bars only (close prices)
**Temporal Alignment**: Intersection only — no forward-fill, no interpolation
**Failure**: Missing symbol OR insufficient history → `regime = NOT_VIABLE`

*(Source: `docs/epistemic/contracts/minimal_regime_input_contract.md`)*

---

### 2.7 Strategy Registry Entry (Schema)

| Block | Key Fields | Mapped Domain Entity |
| :--- | :--- | :--- |
| Identity | `strategy_id`, `name`, `version`, `owner` | Strategy Selection (L5) |
| Governance | `lifecycle_state`, `created_under_decision` | Strategy Selection (L5) |
| Dependencies | `required_beliefs`, `required_policies`, `required_factors` | Meta-Analysis (L3), FactorSignal (L4) |
| Orchestration | `task_graph_ref`, `execution_mode` | Strategy Selection (L5) |
| Audit | `registration_ledger_entry`, `dids`, `audit_log` | Governance (cross-cutting) |

**Invariant**: No executable logic (functions, imports, thresholds, conditions) permitted in registry entries
**Lifecycle**: `DRAFT → ACTIVE → SUSPENDED → RETIRED` (terminal, irreversible)

*(Source: `docs/contracts/strategy_registry_schema.md`)*

---

### 2.8 Paper Portfolio (Diagnostic Output)

| Field | Type | Mapped Domain Entity |
| :--- | :--- | :--- |
| `strategy_id` | `string` | Strategy Selection (L5) |
| `activated` | `boolean` | Strategy Selection (L5) |
| `weight` | `float` | Convergence (L7) |
| `overlap_score` | `float` | PortfolioDiagnostic (L9) |
| `diversification_score` | `float` | PortfolioDiagnostic (L9) |
| `redundancy_clusters` | `list[strategy_id]` | PortfolioDiagnostic (L9) |

**Invariant**: `execution_disabled: true`, `capital_committed: 0.0`

*(Source: `docs/evolution/portfolio/paper_portfolio_schema.md`)*

---

### 2.9 Watchlist Item (Final Output)

| Field | Type | Mapped Domain Entity |
| :--- | :--- | :--- |
| `symbol` | `string` | OpportunityCandidate (L6) |
| `unified_score` | `float` | CandidateAssessment (L7) |
| `regime_alignment` | `float` | RegimeState (L1) |
| `flags[]` | `list[string]` | PortfolioDiagnostic (L9) |
| `severity` | `enum` | PortfolioDiagnostic (L9) |
| `sizing_suggestion` | `string` | ExecutionEnvelope (L8) |

**Storage**: `data/output/watchlist_{date}.json`
**Consumer**: Dashboard → Human Operator

*(Source: `docs/memory/04_architecture/data_flow.md`)*

---

### 2.10 Watcher Diagnostic Schemas

| Watcher | Output File | Key Fields | Mapped Domain Entity |
| :--- | :--- | :--- | :--- |
| Momentum Emergence | `momentum_emergence.json` | `state` (NONE/EMERGING_ATTEMPT/CONFIRMING/PERSISTENT), `contributing_factors`, `confidence` | FactorSignal (L4) |
| Dispersion Breakout | `dispersion_breakout.json` | `state` (NONE/EARLY_BREAKOUT/CONFIRMED_BREAKOUT), `contributing_factors`, `confidence` | FactorSignal (L4) |

**Storage**: `docs/evolution/evaluation/{namespace}/{window_id}/`
**Invariant**: Diagnostic only — does not trigger action

*(Sources: `docs/evolution/watchers/momentum_emergence_schema.md`, `docs/evolution/watchers/dispersion_breakout_schema.md`)*

---

## 3. Proxy Sets & Dependencies

### 3.1 US Market Proxy Set

| Category | Symbol | Semantic Role | Mapped Domain Entity | Ingestion Status |
| :--- | :--- | :--- | :--- | :--- |
| Equity | **SPY** | Benchmark | RegimeState (L1) | ACTIVE |
| Equity | **QQQ** | Growth/Tech | RegimeState (L1) | ACTIVE |
| Equity | **IWM** | Small-Cap / Breadth | RegimeState (L1) | COVERAGE GAP |
| Equity | **DIA** | Blue Chip / Cyclical | RegimeState (L1) | COVERAGE GAP |
| Volatility | **VIX** | Fear Gauge | RegimeState (L1) | ACTIVE |
| Rates | **US02Y** | Fed Policy Anchor | RegimeState (L1) | COVERAGE GAP |
| Rates | **US10Y** | Valuation Anchor | RegimeState (L1) | ACTIVE |
| Macro | **DXY** | Dollar / Liquidity | RegimeState (L1) | COVERAGE GAP |
| Macro | **USOIL** | Inflation / Energy | RegimeState (L1) | COVERAGE GAP |

**Constraint**: If `Benchmark Equity` or `Volatility Gauge` missing → `RegimeState = UNKNOWN` (Fail Closed)

*(Sources: `docs/contracts/market_proxy_sets.md`, `docs/data/coverage_gap_register.md`)*

---

### 3.2 India Market Proxy Set

| Category | Symbol | Semantic Role | Mapped Domain Entity | Ingestion Status |
| :--- | :--- | :--- | :--- | :--- |
| Equity | **NIFTY50** | Benchmark | RegimeState (L1) | NOT INGESTED (P0 Gap) |
| Equity | **BANKNIFTY** | Financials / Breadth | RegimeState (L1) | NOT INGESTED (P1 Gap) |
| Equity | **CNXIT** | Tech / Export | FactorSignal (L4) | NOT INGESTED |
| Equity | **NIFTYSMLCAP100** | Retail Sentiment | FactorSignal (L4) | NOT INGESTED |
| Volatility | **INDIAVIX** | Fear Gauge | RegimeState (L1) | NOT INGESTED (P1 Gap) |
| Rates | **IN10Y** | Valuation Anchor | RegimeState (L1) | NOT INGESTED |
| Macro | **USDINR** | FII Flows / Currency | RegimeState (L1) | NOT INGESTED |
| Macro | **UKOIL** | Import Bill / Inflation | RegimeState (L1) | NOT INGESTED |
| Pre-Market | **GIFTNIFTY** | Gap Indicator | RegimeState (L1) | NOT INGESTED |

**Regime Confidence**: LOW — current India regime uses Reliance as single-stock surrogate (deprecated)
**Upgrade Criteria**: All canonical proxies ACTIVE + ≥ `required_history_days` + no stale data (> 2 trading days)

*(Sources: `docs/contracts/market_proxy_sets.md`, `docs/contracts/india_proxy_sets.json`, `docs/data/coverage_gap_register.md`)*

---

### 3.3 Proxy Dependency Binding Rules

| Layer | Required Proxy Roles | Fallback Policy |
| :--- | :--- | :--- |
| Regime (L1) | Benchmark Equity, Volatility Gauge | Fail Closed (`UNKNOWN`) |
| Factor (L4) — Momentum | Benchmark Equity + Growth Proxy | Use Benchmark Only |
| Factor (L4) — Volatility | Volatility Gauge | Computed StdDev |
| Factor (L4) — Liquidity | Rates Anchor + Liquidity Proxy | `UNAVAILABLE` |
| Factor (L4) — Breadth | Benchmark vs Sector Proxies | `UNAVAILABLE` |

**Invariant**: No layer may access raw data directly (e.g., `SPY.csv`). Must use proxy role abstraction: `get_proxy(market, 'benchmark_equity')`

*(Source: `docs/contracts/proxy_dependency_contracts.md`)*

---

## 4. Data Lineage Rules

### 4.1 Isolation Rules

| Rule | Description |
| :--- | :--- |
| **Strategy Code Isolation** | Strategy modules must NOT read from `data/raw/`. Consume only `data/processed/` or `data/analytics/`. |
| **Ingestion Path Isolation** | API-based (`data/raw/api_based/`) and File-based (`data/raw/file_based/`) remain in separate hierarchies. |
| **Market Isolation** | India and US data are physically separate. No shared state, no cross-imports. |
| **Merging Rule** | Merging across sources happens only in the processing layer, never in raw. |

### 4.2 Immutability

| Rule | Description |
| :--- | :--- |
| **Raw Immutability** | Once written to `data/raw/`, data is immutable. Append-only growth allowed. |
| **Correction via Versioning** | Corrections are new versions, not in-place edits. |
| **Staleness over Fabrication** | Mocking data to fill gaps is STRICTLY PROHIBITED. |

### 4.3 Data Lake Layers

| Layer | Alias | Content | Format | Mutation |
| :--- | :--- | :--- | :--- | :--- |
| **Raw** | Bronze | Direct API output, duplicates present | JSONL, CSV | Append-only |
| **Processed** | Silver | Cleaned, deduped, standardized | Parquet | Overwrite-partition |
| **Analytics** | Gold | Enriched, quality-checked, indicators | Parquet | Idempotent rebuild |

*(Sources: `docs/contracts/RAW_DATA_LINEAGE_RULES.md`, `docs/epistemic/data_retention_policy.md`)*

---

## 5. Temporal Truth Model

### 5.1 Three Temporal Planes

| Plane | Abbreviation | Definition | Owner | Mapped Domain Entity |
| :--- | :--- | :--- | :--- | :--- |
| Raw Data Time | **RDT** | Timestamp of most recent external data | Ingestion (L0) | Canonical Data |
| Canonical Truth Time | **CTT** | Latest validated, cleaned, accepted timestamp | Validation (L0→L1 boundary) | Canonical Data |
| Truth Epoch | **TE** | Timestamp of last complete governed evaluation | Governance (cross-cutting) | RegimeState, NarrativeObject |

**Invariant**: `TE ≤ CTT ≤ RDT` always. `TE > CTT` is a corrupt state.

### 5.2 Temporal States

| State | Condition | Description |
| :--- | :--- | :--- |
| **SYNCHRONIZED** | `RDT == CTT == TE` | System fully up-to-date |
| **PENDING INGESTION** | `RDT > CTT` | Raw data exists, not yet validated |
| **PENDING EVALUATION** | `CTT > TE` | Data validated, intelligence not yet run |
| **STALE / DRIFT** | `CTT >> TE` | System significantly behind |
| **CORRUPT** | `TE > CTT` | Impossible state — system integrity violation |

### 5.3 Temporal Rules

| Rule | Enforcement |
| :--- | :--- |
| No `datetime.now()` | All temporal logic relative to TE |
| No "latest" without context | Must scope as RDT, CTT, or TE |
| Explicit advancement only | TE does not auto-advance; requires governance gate |
| Market-specific streams | `TE_US` and `TE_INDIA` move independently |
| No mixed-frequency | Daily bars only for regime; no intraday for regime computation |

### 5.4 Temporal Persistence

| Time | Store |
| :--- | :--- |
| RDT | File system (raw layer) |
| CTT | File system (canonical/cleaned layer) |
| TE | `global_state.json` or `truth_manifest.json` |

*(Source: `docs/governance/temporal_truth_contract.md`)*

---

## 6. Retention & Archival Policy

| Data Category | Scope | Retention | Mapped Domain Entity |
| :--- | :--- | :--- | :--- |
| **Epistemic Artifacts** | Narratives, Decisions, Journals | **PERMANENT** (archive after 3 years, never delete) | NarrativeObject (L2), all decision state |
| **Cognitive State** | RegimeState, FactorState, NarrativeObject | **PERMANENT** (epistemic — decision context) | RegimeState (L1), FactorSignal (L4) |
| **Trust Scores** | Meta-Analysis intermediate outputs | **1 year active → archive** | Meta-Analysis (L3) |
| **Audit Logs** | JSON logs (`logs/*.json`) | **90 days active → 1 year archive → delete** | Governance |
| **Raw Input Data** | Ingested JSON/Parquet (`data/raw/`) | **1 year active → cold storage** | Canonical Data (L0) |
| **Canonical Data** | Processed Parquet (`data/analytics/`) | **Indefinite** (Source of Truth) | Canonical Data (L0) |
| **Derived / Cache** | Intermediate signals (`data/cache/`) | **Volatile** (regenerable) | Transient |
| **Opportunity Candidates** | L6 lens outputs | **Volatile** (ephemeral unless promoted) | OpportunityCandidate (L6) |
| **Watchlist Items** | Final output JSON | **Indefinite** (decision record) | CandidateAssessment (L7) |

**Deletion Protocol**: Use of `rm` or `delete` on covered paths requires:
1. Verification against retention policy
2. Human approval (via Drift Detector flag or explicit command)

*(Sources: `docs/epistemic/data_retention_policy.md`, `docs/memory/04_architecture/data_flow.md` RQ-7)*

---

## 7. Ingestion Guarantees

### 7.1 US Pipeline

| Guarantee | Description |
| :--- | :--- |
| **Append-Only Raw** | Raw JSON files never overwritten |
| **Idempotent Processing** | Same raw input → identical Parquet output |
| **Rate Limit Safety** | Token-bucket limiter; retry queue for failed symbols |
| **Dedup at Silver** | Dedup by `(symbol, timestamp)`; latest `ingestion_ts` wins |
| **Quality Checks** | Zero-volume removal, gap detection at Gold layer |

**Schedule**:

| Job | Frequency | Description |
| :--- | :--- | :--- |
| `US_Symbol_Refresh` | Weekly (Monday) | Updates `symbols.csv` from `LISTING_STATUS` |
| `US_Daily_Close_Fetch` | Daily (17:00 ET) | `TIME_SERIES_DAILY_ADJUSTED`, `outputsize=compact` |
| `US_Backfill_Worker` | Manual trigger | `outputsize=full`, strict rate limiting |

---

### 7.2 India Pipeline

| Guarantee | Description |
| :--- | :--- |
| **Append-Only Raw** | JSONL files opened in append mode |
| **Restart Recovery** | Fetches last 5 minutes on restart; duplicates handled downstream |
| **WebSocket Reconnect** | Auto-reconnect with exponential backoff |
| **Minute-Boundary Finalization** | Timer-based candle finalization (not tick-count) |

**Schedule**:

| Job | Frequency | Description |
| :--- | :--- | :--- |
| `start_india_momentum.ps1` | Market Open (09:00 IST) | Scheduled Task |
| `stop_india_momentum.ps1` | Market Close (15:45 IST) | Scheduled Task |
| REST fallback | On WebSocket instability | Manual switch |

---

### 7.3 Cross-Pipeline Invariants

| Invariant | Description |
| :--- | :--- |
| Raw data never mutated | Corrections as new versions only |
| India vs US physically separate | No shared state, no cross-imports |
| All timestamps event-time based | Processing time ignored in logic |
| Idempotent re-runs | Same input → identical output |
| No forward-fill across symbols | Only intersection timestamps |
| No mock data | Gaps are "Known Knowns"; mocking is PROHIBITED |

---

## 8. Dashboard API Contract (Read-Only)

| Endpoint | Method | Purpose | Mapped Domain Entity |
| :--- | :--- | :--- | :--- |
| `/api/system/status` | GET | System state, last TE, governance status | Governance |
| `/api/layers/health` | GET | Layer freshness (OK/STALE/ERROR) | All layers |
| `/api/market/snapshot` | GET | Regime, liquidity, dispersion, momentum | RegimeState (L1), FactorSignal (L4) |
| `/api/watchers/timeline` | GET | Historical watcher states | FactorSignal (L4) |
| `/api/strategies/eligibility` | GET | Strategy gating status | Strategy Selection (L5) |
| `/api/meta/summary` | GET | Meta-analysis findings | Meta-Analysis (L3) |
| `/api/system/activation_conditions` | GET | Static epistemic rules | Governance |

**Invariants**:
- All endpoints are **read-only** (no mutations)
- Provenance visible: exact tickers used in proxy roles displayed
- Stale proxies cause corresponding UI components to grey out
- No execution controls exposed

*(Source: `docs/dashboard/api_schema.md`)*

---

## 9. Coverage Gaps (Known)

### 9.1 US Market

| Symbol | Priority | Impact | Remediation |
| :--- | :--- | :--- | :--- |
| **IWM** | P2 | No breadth/domestic economy validation | Ingest via AlphaVantage |
| **DIA** | P3 | No industrial/cyclical rotation signal | Ingest via AlphaVantage |
| **US02Y** | P2 | Lower fidelity on Fed rate expectations | Ingest yield series |
| **DXY** | P2 | No direct FX headwinds signal | Ingest DXY or UUP ETF |
| **USOIL** | P2 | No inflation/energy input | Ingest WTI/USO |
| **Fundamental Data** | P2 | Fundamental Lens returns `INSUFFICIENT_DATA` | AlphaVantage FUNDAMENTAL_DATA (RC-4) |

### 9.2 India Market

| Symbol | Priority | Impact | Remediation |
| :--- | :--- | :--- | :--- |
| **NIFTY50** | **P0 CRITICAL** | Reliance as proxy is mathematically unsound | NSE Index Data feed required |
| **BANKNIFTY** | P1 | Banking sector (35% of market) invisible | Ingest Bank Nifty Index |
| **INDIAVIX** | P1 | No authentic fear metric for India | Ingest India VIX |
| **USDINR** | P2 | Currency risk unmodelled | Ingest USDINR pair |
| **NIFTYSMLCAP100** | P2 | Retail sentiment invisible | Ingest Smallcap 100 |

**Regime Confidence Impact**:
- **US**: HIGH (SPY/QQQ/VIX/10Y cover ~80% of signal variance)
- **India**: LOW (single-stock surrogate; treat India regime as "stock-specific" until index data is live)

*(Source: `docs/data/coverage_gap_register.md`, `docs/contracts/india_proxy_sets.json`)*

---

## 10. Evaluation Profile Contract

| Field | Constraint | Mapped Domain Entity |
| :--- | :--- | :--- |
| `execution.shadow_only` | ALWAYS `true` | Governance |
| `factor.override` | ALWAYS `null` (FORBIDDEN) | FactorSignal (L4) |
| `governance.ledger_required` | ALWAYS `true` | Governance |
| `governance.did_required` | ALWAYS `true` | Governance |
| `invariants.forbid_real_execution` | ALWAYS `true` | Governance |
| `invariants.forbid_strategy_mutation` | ALWAYS `true` | Strategy Selection (L5) |
| `invariants.forbid_regime_fallback` | ALWAYS `true` | RegimeState (L1) |

**Profile Modes**: `historical` (detect regime from data) | `forced_regime` (override with rationale)
**Windowing**: `single` | `rolling` (with step) | `anchored` (fixed dates)

*(Source: `docs/evolution/evaluation_profiles/schema.md`)*

---

## Legacy Source Mapping

| This Section | Legacy Source Document(s) |
| :--- | :--- |
| §1.1 Alpha Vantage | `docs/us_market_engine_design.md` |
| §1.2 SmartAPI | `docs/INDIA_WEBSOCKET_ARCHITECTURE.md`, `docs/contracts/RAW_ANGEL_INTRADAY_SCHEMA.md` |
| §1.3 Event Sources | `docs/memory/05_components/ingestion_events.yaml` (RQ-6) |
| §2.1 US OHLCV | `docs/us_market_engine_design.md` §4 |
| §2.2 India Raw | `docs/contracts/RAW_ANGEL_INTRADAY_SCHEMA.md` |
| §2.3 India Processed | `docs/contracts/PROCESSED_INTRADAY_SCHEMA.md` |
| §2.5 Factor Context | `docs/evolution/context/factor_context_schema.md` |
| §2.6 Regime Input | `docs/epistemic/contracts/minimal_regime_input_contract.md` |
| §2.7 Strategy Registry | `docs/contracts/strategy_registry_schema.md` |
| §2.8 Paper Portfolio | `docs/evolution/portfolio/paper_portfolio_schema.md` |
| §2.10 Watchers | `docs/evolution/watchers/*.md` |
| §3 Proxy Sets | `docs/contracts/market_proxy_sets.md`, `docs/contracts/proxy_dependency_contracts.md`, `docs/contracts/india_proxy_sets.json` |
| §4 Lineage | `docs/contracts/RAW_DATA_LINEAGE_RULES.md` |
| §5 Temporal Truth | `docs/governance/temporal_truth_contract.md` |
| §6 Retention | `docs/epistemic/data_retention_policy.md` |
| §8 Dashboard API | `docs/dashboard/api_schema.md` |
| §9 Coverage Gaps | `docs/data/coverage_gap_register.md` |
| §10 Eval Profiles | `docs/evolution/evaluation_profiles/schema.md` |
