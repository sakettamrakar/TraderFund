# System Architecture (Macro) - Original Diagram

```
┌─────────────────────────────────────────┐
│              HUMAN OPERATOR             │
│        (Final Authority, Always)        │
22: └────────────────▲────────────────────────┘
                 │  Diagnostics, Watchlists
┌────────────────▼────────────────────────┐
│            DASHBOARD (UI)               │
│       (Glass-Box Observation)           │
│  Regime │ Narratives │ Signals │ Flags  │
└────────────────▲────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│     PORTFOLIO INTELLIGENCE (L9)         │
│  PortfolioDiagnostic:                   │
│    RegimeConflict, NarrativeDecay,      │
│    FactorMismatch, HorizonMismatch,     │
│    ConcentrationRisk                    │
│  Output: Red/Orange/Yellow/Green Flags  │
└────────────────▲────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│     EXECUTION CONSTRAINTS (L8)          │
│  ExecutionEnvelope:                     │
│    max_position_size, exposure_caps,    │
│    drawdown_limits, risk_budget         │
└────────────────▲────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│     CONVERGENCE ENGINE (L7)             │◄─── Regime Gate (L1)
│  CandidateAssessment:                   │
│    narrative_score, factor_score,       │
│    fundamental_score, technical_score,  │
│    regime_alignment, horizon            │
│  Output: HighConvictionIdeas, Watchlist │
└────────────────▲────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│     OPPORTUNITY DISCOVERY (L6)          │
│     (Parallel Lenses Engine)            │
│  ┌──────┬───────┬───────┬──────┬─────┐  │
│  │Narr. │Factor │Fund.  │Tech. │Strat│  │
│  │  Lens  │Lens   │Lens   │Lens  │Lens │  │
│  └──────┴───────┴───────┴──────┴─────┘  │
│  Output: OpportunityCandidates          │
│    {symbol, source_lenses, horizon,     │
│     preliminary_scores}                 │
└────────────────▲────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│     COGNITIVE CORE (L1-L5)              │
│                                         │
│  L5: Strategy Selector ─ Playbooks      │
│  L4: Factor Engine ─── Reward Map       │
│  L3: Meta Engine ────── Trust Filter    │
│  L2: Narrative Engine ─ Context         │
│  L1: Regime Engine ──── Gatekeeper      │
└────────────────▲────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│     INGESTION LAYER (L0)                │
│  ┌─────────────┬──────────────────────┐ │
│  │  US Pipeline │  India Pipeline     │ │
│  │  AlphaVantage│  SmartAPI WebSocket │ │
│  │  REST Batch  │  + REST Historical  │ │
│  └─────────────┴──────────────────────┘ │
│  Output: Canonical Store (Parquet)      │
│  Invariant: Pipelines are SEPARATE      │
└─────────────────────────────────────────┘
```
