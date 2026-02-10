# Data Flow Diagrams (Original ASCII)

## End-to-End Pipeline

```
┌──────────────┐    ┌──────────────┐
│  US Market   │    │ India Market │
│  (AV REST)   │    │  (WS + REST) │
└──────┬───────┘    └──────┬───────┘
       │     L0: INGEST    │
       ▼                   ▼
┌─────────────────────────────────┐
│       CANONICAL STORE           │
│  Parquet · Symbol/Date-Part.    │
│  Invariant: Immutable Raw       │
│  Invariant: Event-Time Only     │
└──────────────┬──────────────────┘
               │
               ▼  L1: REGIME
┌─────────────────────────────────┐
│       REGIME ENGINE             │
│  Trend · Volatility · Liquidity │
│  · Event Pressure               │
│  Output: RegimeState            │
│    {behavior, bias, confidence, │
│     is_stable}                  │
└────────┬───────────┬────────────┘
         │           │
         ▼           ▼  L2: NARRATIVE
┌─────────────────────────────────┐
│       NARRATIVE ENGINE          │
│  Events → Clustering → Stories  │
│  Lifecycle: Born → Reinforced   │
│    → Mutated → Resolved         │
│  Output: NarrativeObject        │
│    {headline, confidence,       │
│     lifecycle, related_assets}  │
│                                 │
│  MUST receive RegimeState (L1)  │
└────────┬────────────────────────┘
         │
         ▼  L3: META-ANALYSIS
┌─────────────────────────────────┐
│       META ENGINE               │
│  Assesses trust of signals      │
│  and narratives                 │
│  Output: TrustScore             │
│    {validity, confidence_mod,   │
│     staleness, conflicts}       │
└────────┬────────────────────────┘
         │
         ▼  L4: FACTOR ANALYSIS
┌─────────────────────────────────┐
│       FACTOR ENGINE             │
│  What is being rewarded?        │
│  Output: FactorState            │
│    {momentum, value, quality,   │
│     size — strength/direction}  │
│  Issues: FactorPermission       │
│    {permitted, max_exposure}    │
└────────┬────────────────────────┘
         │
         ▼  L5: STRATEGY SELECTION
┌─────────────────────────────────┐
│       STRATEGY SELECTOR         │
│  Gate: Regime + Factor compat.  │
│  Lifecycle: DRAFT → ACTIVE →   │
│    SUSPENDED → RETIRED          │
│  Output: ActiveStrategySet      │
│  Invariant: Human authorization │
│    required for all transitions │
└────────┬────────────────────────┘
         │
         ▼  L6: OPPORTUNITY DISCOVERY
┌─────────────────────────────────┐
│       PARALLEL LENS ENGINE      │
│                                 │
│  ┌────────┐  ┌────────┐        │
│  │Narrative│  │ Factor │        │
│  │  Lens   │  │  Lens  │        │
│  └────┬───┘  └───┬────┘        │
│       │          │              │
│  ┌────▼───────────▼────┐        │
│  │   CANDIDATE POOL    │        │
│  └────▲───────────▲────┘        │
│       │          │              │
│  ┌────┴───┐  ┌───┴────┐        │
│  │Fundamt.│  │Techncl.│        │
│  │  Lens  │  │  Lens  │        │
│  └────────┘  └────────┘        │
│       ┌──────────┐              │
│       │ Strategy │              │
│       │   Lens   │              │
│       └──────────┘              │
│                                 │
│  Each Lens Output:              │
│    OpportunityCandidate         │
│      {symbol, source_lens,     │
│       preliminary_score,        │
│       horizon, rationale}       │
└────────┬────────────────────────┘
         │
         ▼  L7: CONVERGENCE
┌─────────────────────────────────┐
│       CONVERGENCE ENGINE        │
│                                 │
│  Step 1: Collect all candidates │
│  Step 2: Apply regime-dependent │
│          weighting per lens     │
│  Step 3: Calculate UnifiedScore │
│  Step 4: Classify:              │
│    ≥3 lenses → HighConviction   │
│    1-2 lenses → Watchlist       │
│    0 lenses → Discard           │
│                                 │
│  Output: RankedCandidatePool    │
│    {symbol, unified_score,      │
│     contributing_lenses,        │
│     regime_alignment}           │
└────────┬────────────────────────┘
         │
         ▼  L8: CONSTRAINTS
┌─────────────────────────────────┐
│       CONSTRAINT ENGINE         │
│                                 │
│  Check: max_position_size       │
│  Check: exposure_caps           │
│  Check: drawdown_limits         │
│  Check: risk_budget             │
│                                 │
│  Pass → Forward to L9           │
│  Fail → Block with reason       │
└────────┬────────────────────────┘
         │
         ▼  L9: PORTFOLIO INTELLIGENCE
┌─────────────────────────────────┐
│       PORTFOLIO DIAG. ENGINE    │
│                                 │
│  Scan: RegimeConflict           │
│  Scan: NarrativeDecay           │
│  Scan: FactorMismatch           │
│  Scan: HorizonMismatch          │
│  Scan: ConcentrationRisk        │
│                                 │
│  Output: FlaggedWatchlist       │
│    {symbol, total_score,        │
│     flags[], severity,          │
│     sizing_suggestion}          │
└────────┬────────────────────────┘
         │
         ▼  OUTPUT
┌─────────────────────────────────┐
│       DASHBOARD / REPORTS       │
│                                 │
│  Watchlist (JSON)               │
│  Daily Brief ("The Pulse")      │
│  Weekly Synthesis ("The Context")│
│  Thematic Deep Dive (Ad-hoc)    │
│                                 │
│  → HUMAN OPERATOR DECIDES       │
└─────────────────────────────────┘
```

## US Pipeline

```
[Alpha Vantage API]
       │
       ▼
[Symbol Master] ─── Weekly refresh from LISTING_STATUS endpoint
       │               Filter: assetType=Stock, exchange∈[NYSE,NASDAQ]
       ▼
[Raw Ingestor] ──── REST calls: TIME_SERIES_DAILY_ADJUSTED
       │               Rate limiter: Token bucket, MAX_CALLS_PER_MINUTE
       │               Output: data/raw/us/{date}/{symbol}.json
       ▼
[Normalizer] ─────── Parse JSON, UTC timestamps, type conversions
       │               Handle: Adjusted Close, Split Coefficients
       │               Output: data/staging/us/{freq}/{symbol}.parquet
       ▼
[Curator] ────────── Quality checks, dedup, gap detection
                       Output: data/analytics/us/prices/{freq}/
```

## India Pipeline

```
[SmartAPI WebSocket v2]
       │  ws://smartapisocket.angelone.in/smart-stream
       │  LTP Mode, up to 1000 tokens
       ▼
[IndiaWebSocketClient] ── Connection mgmt, auto-reconnect,
       │                    binary tick parsing, token-to-symbol map
       ▼
[CandleAggregator] ────── SymbolState per symbol,
       │                    tick → 1m candle aggregation,
       │                    minute-boundary finalization
       │                    Output: data/processed/candles/intraday/
       ▼
[MomentumEngine] ─────── VWAP, HOD proximity, RVOL analysis
       │                    Output: Signals
       ▼
[ObservationLogger] ───── Signal logging, EOD review
```

## Process Flow (Daily Cycle)

```
1. WAKE UP
   │  Scheduled Task triggers pipeline
   │
2. INGEST (L0)
   │  US: Fetch latest Daily Close from AlphaVantage
   │  India: WebSocket auto-connects at market open
   │  Both: Validate, normalize, store to Canonical
   │
3. CONTEXTUALIZE (L1-L3)
   │  L1: Update RegimeState (Trend, Vol, Liquidity, Events)
   │  L2: Update NarrativeState (new events → cluster/reinforce)
   │  L3: Update Trust Scores (signal validity, staleness)
   │
4. ANALYZE (L4-L5)
   │  L4: Update FactorState (what's being rewarded)
   │  L5: Select Active Strategies (regime + factor gated)
   │
5. DISCOVER (L6) — PARALLEL
   │  Run all 5 Lenses concurrently
   │  Collect OpportunityCandidates
   │
6. CONVERGE (L7)
   │  Merge all candidates
   │  Apply regime-dependent lens weights
   │  Calculate UnifiedScore per symbol
   │  Classify: HighConviction / Watchlist / Discard
   │
7. CONSTRAIN (L8)
   │  Apply risk limits (position size, exposure, drawdown)
   │  Block non-compliant candidates
   │
8. DIAGNOSE (L9)
   │  Run portfolio diagnostics
   │  Flag: RegimeConflict, NarrativeDecay, etc.
   │  Generate severity flags (Red → Green)
   │
9. PUBLISH
   │  Generate Watchlist JSON
   │  Generate Daily Brief / Reports
   │  Update Dashboard
   │
10. HUMAN REVIEWS & DECIDES
```
