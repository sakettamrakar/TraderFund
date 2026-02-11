# Data Flow & Pipeline Architecture

> [!IMPORTANT]
> **Authoritative Source**: `docs/memory/03_domain/domain_model.md` is CANONICAL.
> **Conflict Handling**: Where legacy source docs conflict with Domain Model, mark OPEN_CONFLICT.

---

## End-to-End Pipeline

*(Original Diagram: `docs/memory/_appendix/data_flow_code.md`)*

1. **Ingestion (L0)**: US/India Market Data → Canonical Store (Immutable Parquet)
2. **Regime Engine (L1)**: Trend · Volatility · Liquidity · Event Pressure
3. **Narrative Engine (L2)**: Events → Stories (Born → Reinforced → Resolved)
4. **Meta Engine (L3)**: Trust Scores (Signal Validity, Staleness)
5. **Factor Engine (L4)**: Factor State (Reward Map)
6. **Strategy Selector (L5)**: Active Strategy Set (Gated by Regime/Factor)
7. **Opportunity Discovery (L6)**: Parallel Lenses (Narrative, Factor, Fundamental, Technical, Strategy) → Candidates
8. **Convergence Engine (L7)**: Candidate Ranking · Unified Score (HighConviction/Watchlist)
9. **Constraint Engine (L8)**: Position Sizing · Risk Limits · Drawdown Checks
10. **Portfolio Intelligence (L9)**: Diagnostics · Flags · Sizing Suggestions
11. **Output**: Dashboard · Reports · Human Operator

---

## Ingestion Pipelines (L0)

### US Pipeline

*(Source: us_market_engine_design.md)*

1. **Alpha Vantage API**
2. **Symbol Master** (Filter: Stock, NYSE/NASDAQ)
3. **Raw Ingestor** (Rate limited REST)
4. **Normalizer** (UTC, Split Adj)
5. **Curator** (Quality Checks → Parquet)

**Schedule**:
- `US_Symbol_Refresh`: Weekly (Monday)
- `US_Daily_Close_Fetch`: Daily (17:00 ET) — `outputsize=compact`
- `US_Backfill_Worker`: Manual trigger — `outputsize=full`

### India Pipeline

*(Source: INDIA_WEBSOCKET_ARCHITECTURE.md)*

1. **SmartAPI WebSocket v2** (LTP Mode)
2. **IndiaWebSocketClient** (Connection Mgmt)
3. **CandleAggregator** (Tick → 1m Candle)
4. **MomentumEngine** (VWAP, HOD, RVOL)
5. **ObservationLogger** (Signal Logging)

**Schedule**:
- Market Open (09:00 IST): Scheduled Task → `start_india_momentum.ps1`
- Market Close (15:45 IST): Scheduled Task → `stop_india_momentum.ps1`
- Rollback to REST available if WebSocket is unstable.

### Pipeline Invariants

| Rule | Enforcement |
| :--- | :--- |
| Raw data never mutated | Corrections as new versions only |
| India vs US physically separate | No shared state, no cross-imports |
| All timestamps event-time based | Processing time ignored in logic |
| Idempotent re-runs | Same input → identical output |

---

## Cognitive Processing Flow (L1-L5)

### Direction of Data Flow

*(Source: layer_interaction_contract.md)*

- **ALLOWED**: L1 → L2 → L3 → L4 → L5 (Downward Only)
- **FORBIDDEN**: L5 → L1 (Reverse Dependency)
- **FORBIDDEN**: L1 → L4 (Layer Skipping)

### Communication Mechanism

Layers communicate via **immutable state snapshots**:

- `RegimeState` → frozen after creation; downstream receives copies
- `FactorPermission` → binary grant flags; absence = denial (fail-closed)
- `ContextualSignal` → wraps raw signal + regime context + factor permission

### Prohibited Bypasses

| Ban | Rule | Rationale |
| :--- | :--- | :--- |
| BAN-1 | Signals must NOT infer regime directly | Regime classification is L1's exclusive responsibility |
| BAN-2 | Strategies must NOT query macro state directly | Macro flows through Regime; direct access is a bypass |
| BAN-3 | Execution must NOT evaluate signal confidence | Confidence evaluation belongs to Meta-Analysis (L3) |
| BAN-4 | No layer may mutate upstream state | Upstream state is immutable from downstream perspective |

### Feedback Channels (Exception)

Feedback flows **upward to DESIGN**, not to STATE:

| Channel | Direction | Purpose |
| :--- | :--- | :--- |
| Performance Attribution | L9 → Design | Did the system produce useful diagnostics? |
| Regret Analysis | L8 → Design | Did constraint decisions preserve capital? |
| Drift Detection | L9 → Design | Is the system behaving as designed? |

**Critical distinction**: Feedback influences future DESIGN (human review, parameter tuning). Feedback does NOT influence current STATE (no real-time adaptation).

---

## Data Object Lifecycle

### 1. Raw Data (Bronze)

| Property | Value |
| :--- | :--- |
| Source | External APIs (AlphaVantage, SmartAPI) |
| State | Unprocessed JSON/CSV |
| Store | `data/raw/{market}/{date}/{source}/` |
| Retention | 30 days (debugging/replay) |
| Mutation | NEVER |

### 2. Canonical Data (Silver)

| Property | Value |
| :--- | :--- |
| Source | Ingestion Engine (L0) |
| State | Cleaned, time-aligned, ticker-mapped Parquet |
| Store | `data/analytics/{market}/prices/{freq}/` |
| Retention | Indefinite (Source of Truth) |
| Schema | `timestamp(UTC), symbol, OHLCV, adj_close, split_coef` |

### 3. Cognitive State (Gold)

| Property | Value |
| :--- | :--- |
| Source | Cognitive Core (L1-L5) |
| State | `RegimeState`, `NarrativeObject`, `FactorState` |
| Store | `data/state/` and `docs/intelligence/` |
| Lifecycle | Refreshed per evaluation cycle |
| Invariant | Frozen after creation; copies only downstream |

### 4. Opportunity Candidate (Transient)

| Property | Value |
| :--- | :--- |
| Source | Any Discovery Lens (L6) |
| State | `{symbol, source_lens, score, rationale, horizon}` |
| Lifecycle | Created in L6, scored in L7, discarded after convergence |
| Persistence | Ephemeral unless promoted to Watchlist |

### 5. Watchlist Item (Final Output)

| Property | Value |
| :--- | :--- |
| Source | Portfolio Intelligence (L9) |
| State | `{symbol, unified_score, regime_alignment, flags[], sizing_suggestion}` |
| Store | `data/output/watchlist_{date}.json` |
| Consumer | Dashboard → Human Operator |

---

## Research Output Types

*(Source: research_product_architecture.md)*

| Report | Frequency | Content | Audience |
| :--- | :--- | :--- | :--- |
| **Daily Brief** ("The Pulse") | Daily (Market Close) | Top 3 Active Narratives, Significant Signals, Reliability Check | Traders |
| **Weekly Synthesis** ("The Context") | Weekly (Sunday) | Narrative Lifecycle Review, Correlation Analysis, Emerging Themes | Portfolio Managers |
| **Thematic Deep Dive** ("The Alpha Note") | Ad-hoc (Alpha Discovery trigger) | Specific Hypothesis, Statistical Evidence, Historical Validation | Quants, Researchers |
| **Cross-Market Flash** ("The Bridge") | Event-driven | Inter-market Spillover Alert, Quantified Lag/Correlation | All |

**Confidence Semantics**:
- Signal Confidence (base) → Narrative Confidence (aggregated + decay) → Report Confidence (weighted average)
- Visual: High (80-100) = Bold, Medium (50-79) = Standard, Low (<50) = Translucent + Warning

---

## Process Flow (Daily Cycle)

*(Original Detail: `docs/memory/_appendix/data_flow_code.md`)*

1. **WAKE UP**: Scheduled Task triggers
2. **INGEST (L0)**: Fetch US/India data → Canonical Store
3. **CONTEXTUALIZE (L1-L3)**: Update Regime, Narrative, Trust Scores
4. **ANALYZE (L4-L5)**: Update Factors, Select Strategies
5. **DISCOVER (L6)**: Run Parallel Lenses → Candidates
6. **CONVERGE (L7)**: Merge & Rank Candidates
7. **CONSTRAIN (L8)**: Apply Risk Limits
8. **DIAGNOSE (L9)**: Run Portfolio Diagnostics
9. **PUBLISH**: Watchlist, Reports, Dashboard
10. **HUMAN DECIDES**: Final Authority

---

## Resolved Conflicts

| ID | Conflict | Resolution | Date |
| :--- | :--- | :--- | :--- |
| **RC-4** | US Pipeline has no Fundamental Data ingestion. | **AlphaVantage FUNDAMENTAL_DATA endpoint** identified. Implementation deferred. Fundamental Lens returns `INSUFFICIENT_DATA` until wired. | 2026-02-10 |
| **RC-5** | Indicator Engine described as separate layer. | **CLOSED.** Indicators are an internal detail of Technical Lens (L6). | 2026-02-10 |
| **RC-6** | Cross-Market Alpha Discovery unmapped. | **Mapped to Factor Lens (L6).** Statistical reward patterns, not narratives. | 2026-02-10 |

## Resolved Questions

| ID | Question | Resolution | Date |
| :--- | :--- | :--- | :--- |
| **RQ-5** (was OQ-5) | MomentumEngine integration — standalone or Technical Lens feeder? | **MomentumEngine feeds into Technical Lens (L6)** as signal source. Outputs signals only, not ideas. Remains a scanner. | 2026-02-10 |
| **RQ-6** (was OQ-6) | Event ingestion — separate L0 sub-pipeline? | **Yes.** Markets (OHLCV) and Events (News/Macro) are distinct L0 streams. Events converge at Narrative Engine (L2). New component: `ingestion_events.yaml`. | 2026-02-10 |
| **RQ-7** (was OQ-7) | Cognitive State retention policy. | Aligned with `data_retention_policy.md`: Regime/Narrative/Factor state → **PERMANENT** (epistemic). Trust scores → **1 year active → archive**. Transient candidates → **Volatile** (regenerable). | 2026-02-10 |
