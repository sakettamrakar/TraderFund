# Portfolio Intelligence Subsystem — Architecture Document

**Version**: 1.0.0  
**Status**: DESIGN APPROVED (DRY_RUN)  
**Author**: Governed Execution — ChatGPT → Antigravity  
**Truth Epoch**: `TRUTH_EPOCH_2026-03-06_01` (FROZEN)  
**Scope**: US, INDIA (multi-market parity)  
**Date**: 2026-03-08

---

## 0. Governance Envelope Compliance

| Rule | Status |
|------|--------|
| INV-NO-EXECUTION | ✅ Read-only analytical layer — zero execution hooks |
| INV-NO-CAPITAL | ✅ No capital allocation, no sizing, no commitment |
| INV-NO-SELF-ACTIVATION | ✅ No autonomous triggering — advisory only |
| INV-PROXY-CANONICAL | ✅ All data sourced via canonical proxies |
| INV-READ-ONLY-DASHBOARD | ✅ Dashboard adapter is strictly GET-only |
| OBL-DATA-PROVENANCE-VISIBLE | ✅ Every metric traces to source artifact |
| OBL-TRUTH-EPOCH-DISCLOSED | ✅ Epoch embedded in every output |
| OBL-REGIME-GATE-EXPLICIT | ✅ Regime compatibility is always surfaced |
| OBL-MARKET-PARITY | ✅ US/INDIA symmetric subsystem design |
| OBL-HONEST-STAGNATION | ✅ Stale/missing data surfaced, never hidden |

---

## 1. Executive Summary

The Portfolio Intelligence Subsystem (PIS) is a **pure-observer analytical layer** that ingests user portfolio holdings from multiple brokers across US and Indian markets, normalizes them, and produces institutional-grade diagnostics at both the holding-level and portfolio-level.

**It does NOT:**
- Execute trades or route orders
- Allocate capital or suggest sizing
- Activate strategies or trigger decisions
- Modify any upstream TraderFund layer state

**It DOES:**
- Ingest and normalize multi-broker holdings
- Compute fundamental, technical, factor, and sentiment metrics per-holding
- Produce portfolio-level diversification, risk, and structural diagnostics
- Generate advisory strategic insights (conviction scoring, regime compatibility)
- Feed the Dashboard with read-only portfolio intelligence panels

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                       PORTFOLIO INTELLIGENCE SUBSYSTEM (PIS)                    │
│                         Layers Affected: RESEARCH, MACRO,                       │
│                      FACTOR, INTELLIGENCE, EVOLUTION, DASHBOARD                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐    ┌──────────────────────┐    ┌──────────────────────┐    │
│  │  PORTFOLIO       │    │  HOLDINGS             │    │  MARKET DATA         │    │
│  │  INGESTION       │───▶│  NORMALIZATION         │───▶│  ENRICHMENT          │    │
│  │  ENGINE          │    │  ENGINE                │    │  LAYER               │    │
│  │                  │    │                        │    │                      │    │
│  │  Multi-broker    │    │  Ticker mapping        │    │  Fundamentals API    │    │
│  │  CSV/API ingest  │    │  Cost basis calc       │    │  Technical compute   │    │
│  │  US + INDIA      │    │  Weight computation    │    │  Factor scores       │    │
│  │  Metadata mgmt   │    │  Sector/Geo tagging    │    │  Sentiment feed      │    │
│  └─────────────────┘    └──────────────────────┘    └──────────────────────┘    │
│           │                        │                          │                  │
│           ▼                        ▼                          ▼                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐    │
│  │                    INTELLIGENCE SCORING ENGINE                            │    │
│  │                                                                          │    │
│  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐  │    │
│  │   │ Fundamental   │  │ Technical     │  │ Factor       │  │ Sentiment  │  │    │
│  │   │ Module        │  │ Module        │  │ Exposure     │  │ Module     │  │    │
│  │   │              │  │              │  │ Module       │  │            │  │    │
│  │   │ PE, EPS,     │  │ Trend, Momo, │  │ Growth, Val, │  │ News flow, │  │    │
│  │   │ Revenue,     │  │ Vol regime,  │  │ Quality,     │  │ Catalysts, │  │    │
│  │   │ Margins,     │  │ Supp/Resist  │  │ Macro sens.  │  │ Earnings   │  │    │
│  │   │ Balance      │  │              │  │              │  │            │  │    │
│  │   └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘  │    │
│  │                                                                          │    │
│  │   Per-Holding Intelligence Summary:                                      │    │
│  │     • Opportunity Classification                                         │    │
│  │     • Risk Flags                                                         │    │
│  │     • Conviction Score [0.0 – 1.0]                                       │    │
│  │     • Regime Compatibility                                               │    │
│  └──────────────────────────────────────────────────────────────────────────┘    │
│           │                                                                      │
│           ▼                                                                      │
│  ┌──────────────────────────────────────────────────────────────────────────┐    │
│  │                    PORTFOLIO ANALYTICS ENGINE                             │    │
│  │                                                                          │    │
│  │   ┌───────────────────┐  ┌───────────────────┐  ┌──────────────────┐    │    │
│  │   │ Diversification    │  │ Risk Diagnostics   │  │ Portfolio         │    │    │
│  │   │ Analysis           │  │                    │  │ Structure          │    │    │
│  │   │                   │  │ Drawdown sens.     │  │                   │    │    │
│  │   │ Sector conc.      │  │ Macro exposure     │  │ Core vs Satellite │    │    │
│  │   │ Geo exposure      │  │ Correlation clust. │  │ Concentration     │    │    │
│  │   │ Factor conc.      │  │                    │  │ Over/underweight  │    │    │
│  │   └───────────────────┘  └───────────────────┘  └──────────────────┘    │    │
│  │                                                                          │    │
│  │   ┌───────────────────┐  ┌──────────────────────────────────────────┐    │    │
│  │   │ Performance        │  │ Strategic Insights Generator            │    │    │
│  │   │ Analytics          │  │                                          │    │    │
│  │   │                   │  │ Diversification gaps · Factor imbalance  │    │    │
│  │   │ PnL breakdown     │  │ Macro vulnerability · Hidden conc.      │    │    │
│  │   │ Winners/Laggards  │  │ Resilience score · Advisory list        │    │    │
│  │   │ Contribution       │  │                                          │    │    │
│  │   └───────────────────┘  └──────────────────────────────────────────┘    │    │
│  └──────────────────────────────────────────────────────────────────────────┘    │
│           │                                                                      │
│           ▼                                                                      │
│  ┌──────────────────────────────────────────────────────────────────────────┐    │
│  │                       DASHBOARD ADAPTER (Read-Only)                       │    │
│  │                                                                          │    │
│  │   GET /api/portfolio/overview/{market}                                   │    │
│  │   GET /api/portfolio/holdings/{market}/{portfolio_id}                    │    │
│  │   GET /api/portfolio/diversification/{market}/{portfolio_id}            │    │
│  │   GET /api/portfolio/risk/{market}/{portfolio_id}                       │    │
│  │   GET /api/portfolio/insights/{market}/{portfolio_id}                   │    │
│  │   GET /api/portfolio/combined                                            │    │
│  └──────────────────────────────────────────────────────────────────────────┘    │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Component Design

### 3.1 Portfolio Ingestion Engine

**Purpose**: Ingest holdings from multiple broker sources per market, maintaining portfolio metadata and version history.

**File**: `src/portfolio_intelligence/ingestion/portfolio_ingester.py`

#### Supported Sources (Phase 1)

| Market | Source | Format | Mechanism |
|--------|--------|--------|-----------|
| INDIA | Zerodha (Kite) | CSV Holdings Report | File upload |
| INDIA | Groww | CSV Export | File upload |
| INDIA | Angel One | CSV Export | File upload |
| US | Interactive Brokers | Flex Query XML/CSV | File upload |
| US | Schwab | CSV Positions Export | File upload |
| US | Robinhood | CSV Download | File upload |

#### Data Model: `RawPortfolioImport`

```python
@dataclass(frozen=True)
class RawPortfolioImport:
    """Raw broker import before normalization."""
    import_id: str                    # UUID
    portfolio_id: str                 # User-assigned portfolio name
    market: Literal["US", "INDIA"]
    broker: str                       # "ZERODHA", "IBKR", etc.
    import_timestamp: str             # ISO-8601
    raw_holdings: Tuple[RawHolding, ...]
    source_checksum: str              # SHA-256 of input file
    truth_epoch: str                  # Active epoch at import time
```

```python
@dataclass(frozen=True)
class RawHolding:
    """Single row from broker export."""
    raw_symbol: str                   # Broker-native ticker
    quantity: float
    average_cost: float               # Per-share cost basis
    last_price: Optional[float]       # If available from export
    currency: str                     # "INR", "USD"
    broker_metadata: Dict[str, Any]   # ISIN, exchange segment, etc.
```

#### Ingestion Rules
1. All imports are **append-only** — prior imports are never overwritten
2. Each import receives a unique `import_id` for audit trail
3. File checksums prevent duplicate ingestion
4. Holdings are stored raw until normalization
5. The ingestion engine does NOT fetch live prices — that is the enrichment layer's job

#### Portfolio Registry

```python
@dataclass(frozen=True)
class PortfolioRegistry:
    """Master registry of all ingested portfolios."""
    portfolios: Dict[str, PortfolioMeta]  # portfolio_id → metadata

@dataclass(frozen=True)
class PortfolioMeta:
    portfolio_id: str
    display_name: str
    market: Literal["US", "INDIA"]
    broker: str
    created_at: str
    last_import_at: str
    holding_count: int
    is_active: bool
```

**Storage**: `data/portfolio_intelligence/imports/{market}/{portfolio_id}/import_{timestamp}.json`

---

### 3.2 Holdings Normalization Engine

**Purpose**: Transform broker-specific raw holdings into a canonical normalized format suitable for intelligence computation.

**File**: `src/portfolio_intelligence/normalization/holdings_normalizer.py`

#### Canonical Holding Schema

```python
@dataclass(frozen=True)
class NormalizedHolding:
    """Canonical holding after normalization."""
    symbol: str                            # Canonical ticker (e.g., "AAPL", "RELIANCE.NS")
    isin: Optional[str]                    # International Securities ID
    name: str                              # Company name
    quantity: float
    cost_basis_per_share: float            # In local currency
    total_cost_basis: float                # quantity × cost_basis_per_share
    market_value: float                    # quantity × current_price
    current_price: float                   # Latest price (from enrichment)
    unrealized_pnl: float                  # market_value - total_cost_basis
    unrealized_pnl_pct: float              # unrealized_pnl / total_cost_basis × 100
    portfolio_weight_pct: float            # Allocation weight [0.0 – 100.0]
    sector: str                            # GICS Sector
    industry: str                          # GICS Industry
    geography: Literal["US", "INDIA"]      # Market geography
    currency: str                          # "USD", "INR"
    exchange: str                          # "NYSE", "NASDAQ", "NSE", "BSE"
    asset_class: Literal["EQUITY"]         # Phase 1: Equity only
    portfolio_id: str                      # Parent portfolio
    normalization_source: str              # "BROKER_EXPORT" | "MANUAL"
    last_updated: str                      # ISO-8601
```

#### Normalization Pipeline

```
Raw Import → Ticker Mapping → Price Fill → Weight Computation → Sector Tagging → Output
```

1. **Ticker Mapping**: Broker-specific symbols → canonical tickers
   - India: `RELIANCE` (Zerodha) → `RELIANCE.NS` (canonical)
   - US: Typically 1:1 mapping, with exchange suffix validation
   - ISIN cross-reference for disambiguation

2. **Price Fill**: Latest prices sourced from enrichment layer (never from broker export)

3. **Weight Computation**: `weight_pct = market_value / total_portfolio_value × 100`

4. **Sector Tagging**: GICS sector/industry from master reference data
   - India: NSE sector classification → GICS mapping
   - US: Direct GICS from data providers

---

### 3.3 Market Data Enrichment Layer

**Purpose**: Enrich normalized holdings with live/recent market data from canonical data sources.

**File**: `src/portfolio_intelligence/enrichment/market_data_enricher.py`

#### Enrichment Sources

| Data Type | US Source | India Source | Cadence |
|-----------|----------|-------------|---------|
| Prices | Alpha Vantage / Yahoo Finance | NSE EOD / BSE API | Daily |
| Fundamentals | Alpha Vantage Fundamentals | Screener.in / MoneyControl | Weekly |
| Technicals | Local compute (pandas-ta) | Local compute (pandas-ta) | Daily |
| Sector data | GICS reference | NSE sector reference | Static + refresh |

#### Integration with Existing Layers

The enrichment layer **reads from** (never writes to) existing TraderFund data stores:

- `data/analytics/us/prices/daily/` — US price data (from existing ingestion pipeline)
- `data/analytics/us/indicators/daily/` — US technical indicators (from existing indicator engine)
- `data/india/` or NSE data — India price data (from existing `india_market_loader.py`)
- `src/layers/macro_layer.py` — Macro regime context (read-only)
- `src/layers/factor_live.py` — Factor exposure context (read-only)
- `src/intelligence/engine.py` — Intelligence signals (read-only)

#### Data Provenance Contract

Every enriched data point must carry:

```python
@dataclass(frozen=True)
class DataProvenance:
    source: str                # "ALPHA_VANTAGE" | "NSE_EOD" | "LOCAL_COMPUTE"
    fetched_at: str            # ISO-8601
    staleness_hours: float     # Hours since last refresh
    confidence: float          # [0.0 – 1.0]; degraded if stale
    truth_epoch: str           # Active epoch
```

---

### 3.4 Intelligence Scoring Engine

**Purpose**: Compute holding-level intelligence metrics across fundamental, technical, factor, and sentiment dimensions.

**File**: `src/portfolio_intelligence/scoring/intelligence_scorer.py`

#### 3.4.1 Fundamental Module

Compute for each holding:

| Metric | Source | Computation | Output Range |
|--------|--------|-------------|--------------|
| PE Ratio | Fundamentals API | Price / EPS | Numeric |
| Earnings Growth (YoY) | Fundamentals API | (EPS_curr - EPS_prev) / EPS_prev | % |
| Revenue Growth (YoY) | Fundamentals API | (Rev_curr - Rev_prev) / Rev_prev | % |
| Gross Margin | Fundamentals API | Gross Profit / Revenue | % |
| Operating Margin | Fundamentals API | Operating Income / Revenue | % |
| Net Margin | Fundamentals API | Net Income / Revenue | % |
| Debt-to-Equity | Fundamentals API | Total Debt / Shareholder Equity | Ratio |
| Current Ratio | Fundamentals API | Current Assets / Current Liabilities | Ratio |
| Balance Sheet Health Score | Composite | Weighted score of D/E + CR + margins | [0.0 – 1.0] |

**Fundamental Health Classification**:
- `STRONG`: Score > 0.75
- `ADEQUATE`: Score 0.50 – 0.75
- `WEAK`: Score 0.25 – 0.50
- `DISTRESSED`: Score < 0.25

#### 3.4.2 Technical Module

Leverages existing TraderFund indicator compute (pandas-ta):

| Metric | Indicators Used | Output |
|--------|----------------|--------|
| Trend Regime | SMA(20,50,200), ADX, EMA(9,21) | `TRENDING_UP` / `TRENDING_DOWN` / `RANGE_BOUND` |
| Momentum Score | RSI(14), MACD, ROC | [0.0 – 1.0] |
| Volatility Regime | ATR, Bollinger Band width | `LOW_VOL` / `NORMAL` / `HIGH_VOL` / `EXTREME` |
| Support Level | Pivot Points, recent swing lows | Price level |
| Resistance Level | Pivot Points, recent swing highs | Price level |
| Distance from Support | (price - support) / price | % |
| Distance from Resistance | (resistance - price) / price | % |

#### 3.4.3 Factor Exposure Module

Maps each holding to TraderFund's existing factor taxonomy:

```python
@dataclass(frozen=True)
class HoldingFactorExposure:
    symbol: str
    growth_score: float            # [0.0 – 1.0] — earnings/revenue growth
    value_score: float             # [0.0 – 1.0] — PE, PB, dividend yield
    momentum_score: float          # [0.0 – 1.0] — price momentum, RSI
    quality_score: float           # [0.0 – 1.0] — margins, ROE, stability
    macro_sensitivity: float       # [0.0 – 1.0] — beta to macro indices
    dominant_factor: FactorType    # Highest scoring factor
```

**Integration**: Reads from `src/layers/factor_live.py` for portfolio-level factor alignment comparison.

#### 3.4.4 Sentiment Module

| Data Point | Source | Update Cadence |
|-----------|--------|----------------|
| News Flow Intensity | News API aggregate | Daily |
| Sentiment Polarity | NLP classification | Per-article |
| Major Catalysts | Event detection | Real-time → daily digest |
| Earnings Events | Calendar | Static schedule |
| Analyst Consensus Changes | External data | Weekly |

**Output**:

```python
@dataclass(frozen=True)
class HoldingSentiment:
    symbol: str
    news_flow_intensity: Literal["HIGH", "NORMAL", "LOW", "SILENT"]
    sentiment_polarity: float         # [-1.0 – +1.0]
    upcoming_catalysts: Tuple[str, ...]
    days_to_earnings: Optional[int]   # None if > 60 days
    analyst_revision_trend: Literal["UPGRADING", "STABLE", "DOWNGRADING", "UNKNOWN"]
```

#### 3.4.5 Intelligence Summary (Per-Holding)

All four modules converge into a per-holding intelligence card:

```python
@dataclass(frozen=True)
class HoldingIntelligenceCard:
    symbol: str
    portfolio_id: str
    market: Literal["US", "INDIA"]
    
    # Dimensional scores
    fundamental_health: float          # [0.0 – 1.0]
    technical_score: float             # [0.0 – 1.0]
    factor_alignment: float            # [0.0 – 1.0] vs portfolio factor
    sentiment_score: float             # [0.0 – 1.0]
    
    # Composite
    conviction_score: float            # Weighted composite [0.0 – 1.0]
    opportunity_class: Literal[
        "CORE_HOLD",                   # Strong across all dimensions
        "MOMENTUM_PLAY",               # Technical/momentum driven
        "VALUE_OPPORTUNITY",            # Fundamentally cheap + positive catalysts
        "REGIME_ALIGNED",              # Fits current macro regime
        "UNDER_REVIEW",                # Mixed signals, needs attention
        "DETERIORATING",               # Weakening across dimensions
        "EXIT_CANDIDATE",              # Multiple red flags
    ]
    
    # Risk
    risk_flags: Tuple[str, ...]        # Machine-readable risk codes
    risk_summary: str                  # Human-readable summary
    
    # Regime
    regime_compatible: bool            # Is this holding aligned with current regime?
    regime_compatibility_reason: str
    
    # Provenance
    computed_at: str                   # ISO-8601
    truth_epoch: str
    data_staleness: Dict[str, float]   # module → hours since last refresh
```

**Conviction Score Computation**:

```python
WEIGHTS = {
    "fundamental": 0.30,
    "technical": 0.25,
    "factor_alignment": 0.25,
    "sentiment": 0.20,
}

conviction = sum(
    score * WEIGHTS[dimension]
    for dimension, score in dimension_scores.items()
)
```

---

### 3.5 Portfolio Analytics Engine

**Purpose**: Compute portfolio-level diagnostics spanning diversification, risk, structure, performance, and strategic insights.

**File**: `src/portfolio_intelligence/analytics/portfolio_analyzer.py`

#### 3.5.1 Diversification Analysis

```python
@dataclass(frozen=True)
class DiversificationReport:
    # Sector
    sector_breakdown: Dict[str, float]        # sector → weight %
    sector_hhi: float                         # Herfindahl-Hirschman Index [0.0 – 1.0]
    sector_concentration_level: Literal["WELL_DIVERSIFIED", "MODERATE", "CONCENTRATED", "EXTREME"]
    top_sector: str
    top_sector_weight: float
    
    # Geography
    geo_breakdown: Dict[str, float]            # geography → weight %
    geo_concentration_level: Literal["SINGLE_MARKET", "MULTI_MARKET"]
    
    # Factor
    factor_breakdown: Dict[str, float]         # factor → weight-adjusted exposure
    factor_hhi: float
    factor_concentration_level: Literal["BALANCED", "TILTED", "CONCENTRATED"]
    dominant_factor: str
    dominant_factor_weight: float
    
    # Holding count
    total_holdings: int
    effective_positions: float                 # 1 / HHI of position weights
```

**HHI Computation**: `HHI = Σ(weight_i²)` where weights are fractions summing to 1.0.

- HHI < 0.10: Well Diversified
- HHI 0.10–0.25: Moderate
- HHI 0.25–0.50: Concentrated
- HHI > 0.50: Extreme

#### 3.5.2 Risk Diagnostics

```python
@dataclass(frozen=True)
class RiskDiagnosticReport:
    # Drawdown sensitivity
    portfolio_drawdown_sensitivity: float      # [0.0 – 1.0]
    max_single_holding_impact: float           # Max weight × volatility
    tail_risk_exposure: float                  # Weighted sum of high-vol large positions
    
    # Macro exposure
    macro_sensitivity_score: float             # Portfolio-weighted macro β
    rate_sensitivity: Literal["HIGH", "MODERATE", "LOW"]
    inflation_sensitivity: Literal["HIGH", "MODERATE", "LOW"]
    
    # Correlation clustering
    correlation_cluster_count: int             # Number of clusters
    largest_cluster_weight: float              # Weight of largest correlated group
    correlation_risk_level: Literal["LOW", "MODERATE", "HIGH", "CRITICAL"]
    
    # Combined risk score
    portfolio_risk_score: float                # [0.0 – 1.0]; 1.0 = highest risk
    risk_classification: Literal["CONSERVATIVE", "MODERATE", "AGGRESSIVE", "SPECULATIVE"]
```

#### 3.5.3 Portfolio Structure Analysis

```python
@dataclass(frozen=True)
class StructureReport:
    # Core vs Satellite
    core_holdings: Tuple[str, ...]             # High conviction, > 5% weight, diversified
    satellite_holdings: Tuple[str, ...]        # Tactical, < 3% weight
    unclassified_holdings: Tuple[str, ...]     # Middle ground
    core_weight_pct: float
    satellite_weight_pct: float
    
    # Concentration
    top_3_weight: float
    top_5_weight: float
    top_10_weight: float
    concentration_level: Literal["WELL_DISTRIBUTED", "TOP_HEAVY", "CONCENTRATED"]
    
    # Overweight / Underweight (vs benchmark or equal-weight)
    overweight_holdings: Tuple[OverweightEntry, ...]
    underweight_holdings: Tuple[OverweightEntry, ...]
```

#### 3.5.4 Performance Analytics

```python
@dataclass(frozen=True)
class PerformanceReport:
    total_invested: float                      # Total cost basis
    total_market_value: float                  # Total current value
    total_unrealized_pnl: float
    total_unrealized_pnl_pct: float
    
    # Winners vs Laggards
    winners: Tuple[PerformanceEntry, ...]       # Holdings with positive PnL, sorted desc
    laggards: Tuple[PerformanceEntry, ...]      # Holdings with negative PnL, sorted asc
    
    # Contribution to portfolio return
    top_contributors: Tuple[ContributionEntry, ...]   # Sorted by contribution
    bottom_contributors: Tuple[ContributionEntry, ...]
    
    # Portfolio-level
    weighted_avg_gain: float                   # Weight-adjusted average gain %
    win_rate: float                            # Fraction of holdings with positive PnL
```

#### 3.5.5 Strategic Insights Generator

**Purpose**: Generate actionable analytical insights from the combined intelligence. These are **advisory only** and carry explicit disclaimers.

```python
@dataclass(frozen=True)
class StrategicInsight:
    insight_id: str                 # UUID
    category: Literal[
        "DIVERSIFICATION_GAP",
        "FACTOR_IMBALANCE",
        "MACRO_VULNERABILITY",
        "HIDDEN_CONCENTRATION",
        "REGIME_CONFLICT",
        "DETERIORATING_FUNDAMENTAL",
        "IMPROVING_MOMENTUM",
        "REVIEW_REQUIRED",
    ]
    severity: Literal["INFO", "YELLOW", "ORANGE", "RED"]
    headline: str                   # Human-readable title
    detail: str                     # Explanation with data
    affected_holdings: Tuple[str, ...]
    suggested_action: str           # Advisory text (never imperative)
    confidence: float               # [0.0 – 1.0]
    data_provenance: Dict[str, str] # source → artifact path
```

```python
@dataclass(frozen=True)
class PortfolioResilienceScore:
    overall_resilience: float               # [0.0 – 1.0]
    diversification_score: float
    risk_management_score: float
    regime_alignment_score: float
    fundamental_quality_score: float
    momentum_health_score: float
    
    classification: Literal[
        "ROBUST",       # > 0.75
        "ADEQUATE",     # 0.50 – 0.75
        "VULNERABLE",   # 0.25 – 0.50
        "FRAGILE",      # < 0.25
    ]
```

---

### 3.6 Dashboard Adapter

**Purpose**: Expose portfolio intelligence as read-only REST endpoints consumed by the frontend dashboard.

**File**: `src/dashboard/backend/portfolio_api.py`

#### API Endpoints

All endpoints are **GET-only** (aligned with `INV-READ-ONLY-DASHBOARD`):

| Endpoint | Description | Response | 
|----------|-------------|----------|
| `GET /api/portfolio/overview/{market}` | All portfolios for a market with summary stats | `PortfolioOverview` |
| `GET /api/portfolio/holdings/{market}/{portfolio_id}` | Normalized holdings with intelligence cards | `HoldingsIntelligence` |
| `GET /api/portfolio/diversification/{market}/{portfolio_id}` | Diversification analysis | `DiversificationReport` |
| `GET /api/portfolio/risk/{market}/{portfolio_id}` | Risk diagnostics | `RiskDiagnosticReport` |
| `GET /api/portfolio/structure/{market}/{portfolio_id}` | Core/satellite structure | `StructureReport` |
| `GET /api/portfolio/performance/{market}/{portfolio_id}` | PnL and contribution | `PerformanceReport` |
| `GET /api/portfolio/insights/{market}/{portfolio_id}` | Strategic insights | `List[StrategicInsight]` |
| `GET /api/portfolio/resilience/{market}/{portfolio_id}` | Resilience scoring | `PortfolioResilienceScore` |
| `GET /api/portfolio/combined` | Cross-market combined view | `CombinedPortfolioView` |

#### Combined Portfolio View

For cross-market analysis, the combined endpoint merges US and India portfolios:

```python
@dataclass(frozen=True)
class CombinedPortfolioView:
    us_portfolio_value: float
    india_portfolio_value: float
    combined_value_usd: float       # INR → USD conversion at latest rate
    us_weight_pct: float
    india_weight_pct: float
    
    # Cross-market diagnostics
    combined_sector_breakdown: Dict[str, float]
    combined_factor_breakdown: Dict[str, float]
    geo_concentration: Dict[str, float]
    
    # Cross-market insights
    cross_market_insights: Tuple[StrategicInsight, ...]
    combined_resilience: PortfolioResilienceScore
    
    fx_rate_used: float             # INR/USD
    fx_source: str                  # Provenance
    computed_at: str
    truth_epoch: str
```

---

## 4. Integration with Existing TraderFund Layers

### 4.1 Integration Map

```
┌──────────────────────────────────────────────────────────────────┐
│                    EXISTING TRADERFUND LAYERS                     │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  L1: Regime Detection ─────────┐                                 │
│  (src/layers/macro_layer.py)   │                                 │
│                                │  ┌────────────────────────┐     │
│  L2: Narrative Engine ─────────┼──│  PIS reads from these  │     │
│  (src/governance/narrative)    │  │  layers via canonical   │     │
│                                │  │  data contracts.        │     │
│  L3: Factor Layer ─────────────┤  │  Zero write-back.       │     │
│  (src/layers/factor_live.py)   │  └────────────────────────┘     │
│                                │                                 │
│  L6-L7: Intelligence ──────────┤                                 │
│  (src/intelligence/engine.py)  │                                 │
│                                │                                 │
│  L8: Constraint Engine ────────┤                                 │
│  (src/layers/constraint_eng.)  │                                 │
│                                │                                 │
│  L9: Portfolio Intelligence ───┘  ← EXISTING (Structural Diag.) │
│  (src/layers/portfolio_intel.)    ← PIS EXTENDS this concept     │
│                                                                  │
│  Evolution Layer ──────────────── PIS reads paper portfolio data  │
│  (src/evolution/)                                                │
│                                                                  │
│  Dashboard Backend ────────────── PIS registers new API routes   │
│  (src/dashboard/backend/api.py)                                  │
│                                                                  │
│  Dashboard Frontend ───────────── PIS adds new React components  │
│  (src/dashboard/frontend/)                                       │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 4.2 Relationship to Existing L9

The existing `src/layers/portfolio_intelligence.py` (L9) is a **structural diagnostic engine** focused on:
- Regime alignment, narrative drift, factor alignment
- Strategy misapplication, concentration creep, convergence decay
- Operates on the **system's own positions** (paper/evolution portfolio)

The new Portfolio Intelligence Subsystem (PIS) is **distinct but complementary**:
- PIS operates on **user-owned broker portfolios** (real holdings)
- PIS computes **holding-level fundamental/technical/factor intelligence**
- PIS produces **portfolio-level institutional diagnostics**

**Bridge**: PIS reads L9's regime/factor/narrative signals as contextual inputs for its own scoring. PIS does NOT replace L9 — it extends the intelligence surface to cover user portfolios.

### 4.3 Data Flow Invariants

1. **Unidirectional Read**: PIS reads from L1, L3, L6-L7, L9 — never writes back
2. **No Shared Mutation**: PIS maintains its own data store under `data/portfolio_intelligence/`
3. **Epoch Binding**: Every PIS output is stamped with the active Truth Epoch
4. **Market Parity**: Every PIS component is market-parameterised (US/INDIA)
5. **Determinism**: Given identical inputs (holdings + market data + regime state), PIS produces identical output

---

## 5. File System Layout

```
c:\GIT\TraderFund\
├── src\
│   └── portfolio_intelligence\          ← NEW: Main PIS package
│       ├── __init__.py
│       ├── ingestion\
│       │   ├── __init__.py
│       │   ├── portfolio_ingester.py     ← Multi-broker import engine
│       │   ├── broker_adapters\
│       │   │   ├── __init__.py
│       │   │   ├── zerodha_adapter.py
│       │   │   ├── groww_adapter.py
│       │   │   ├── ibkr_adapter.py
│       │   │   ├── schwab_adapter.py
│       │   │   └── base_adapter.py       ← Abstract broker adapter
│       │   └── ticker_mapping.py         ← Cross-broker ticker resolution
│       ├── normalization\
│       │   ├── __init__.py
│       │   ├── holdings_normalizer.py    ← Raw → Canonical normalization
│       │   └── sector_classifier.py      ← GICS/NSE sector mapping
│       ├── enrichment\
│       │   ├── __init__.py
│       │   ├── market_data_enricher.py   ← Price/fundamental enrichment
│       │   ├── technical_enricher.py     ← Technical indicator compute
│       │   └── provenance_tracker.py     ← Data freshness monitoring
│       ├── scoring\
│       │   ├── __init__.py
│       │   ├── intelligence_scorer.py    ← Orchestrator
│       │   ├── fundamental_module.py     ← PE, margins, balance sheet
│       │   ├── technical_module.py       ← Trend, momentum, volume
│       │   ├── factor_module.py          ← Factor exposure scoring
│       │   └── sentiment_module.py       ← News, catalysts, earnings
│       ├── analytics\
│       │   ├── __init__.py
│       │   ├── portfolio_analyzer.py     ← Master analytics orchestrator
│       │   ├── diversification.py        ← Sector/factor/geo analysis
│       │   ├── risk_diagnostics.py       ← Drawdown, correlation, macro
│       │   ├── structure_analysis.py     ← Core/satellite classification
│       │   ├── performance.py            ← PnL, winners/laggards
│       │   └── strategic_insights.py     ← Insight generation
│       ├── models\
│       │   ├── __init__.py
│       │   ├── ingestion_models.py       ← Data contracts: ingestion
│       │   ├── holding_models.py         ← Data contracts: normalized
│       │   ├── intelligence_models.py    ← Data contracts: scores
│       │   └── analytics_models.py       ← Data contracts: analytics
│       └── contracts\
│           ├── __init__.py
│           └── api_contracts.py          ← API response schemas
├── data\
│   └── portfolio_intelligence\            ← NEW: PIS data store
│       ├── imports\                       ← Raw broker imports
│       │   ├── US\
│       │   └── INDIA\
│       ├── normalized\                    ← Canonical holdings
│       │   ├── US\
│       │   └── INDIA\
│       ├── enriched\                      ← Market-data enriched
│       │   ├── US\
│       │   └── INDIA\
│       ├── intelligence\                  ← Holding intelligence cards
│       │   ├── US\
│       │   └── INDIA\
│       ├── analytics\                     ← Portfolio-level reports
│       │   ├── US\
│       │   └── INDIA\
│       └── registry\                      ← Portfolio metadata
│           └── portfolio_registry.json
└── docs\
    ├── portfolio_intelligence_architecture.md     ← THIS FILE
    ├── portfolio_intelligence_task_graph.md        ← Implementation task graph
    └── dashboard\
        └── portfolio_intelligence_spec.md         ← Dashboard component spec
```

---

## 6. Safety Architecture

### 6.1 Invariant Enforcement

The PIS enforces the same catastrophic invariants as the rest of TraderFund:

```python
# FORBIDDEN OPERATIONS (src/portfolio_intelligence/__init__.py)
#
# The following operations are EXPLICITLY FORBIDDEN:
# - execute_trade()           ← INV-NO-EXECUTION
# - allocate_capital()        ← INV-NO-CAPITAL  
# - trigger_strategy()        ← INV-NO-SELF-ACTIVATION
# - modify_upstream_state()   ← INV-PROXY-CANONICAL
# - write_to_dashboard()      ← INV-READ-ONLY-DASHBOARD (GET only)
#
# Any function that takes portfolio intelligence and produces
# a trade, allocation, or strategy activation is INVALID.
```

### 6.2 Data Integrity

- All data models are **frozen dataclasses** (immutable after creation)
- All outputs carry **SHA-256 input hashes** for determinism verification
- All computations have **latency guards** (< 2000ms per portfolio)
- **INSUFFICIENT_DATA** is surfaced explicitly when data is stale or missing

### 6.3 Advisory-Only Language

All strategic insights use **observational language**:

| ✅ Allowed | ❌ Forbidden |
|-----------|-------------|
| "This holding shows deteriorating fundamentals" | "Sell this stock" |
| "Portfolio is concentrated in Technology sector" | "Reduce your tech allocation" |
| "Regime conflict detected for 3 holdings" | "These positions must be closed" |
| "Conviction score is 0.35 (low)" | "This is a bad investment" |

---

## 7. Future Extensibility

The architecture is designed for phased expansion:

| Phase | Capability | Impact |
|-------|-----------|--------|
| Phase 2 | Crypto portfolio ingestion | New broker adapters, new asset_class |
| Phase 3 | Derivatives/options exposure | New normalization rules, Greeks computation |
| Phase 4 | Cross-portfolio optimisation | Read-only optimiser, no execution |
| Phase 5 | Institutional risk models (VaR, CVaR) | Advanced risk module |
| Phase 6 | Multi-currency exposure analysis | FX overlay layer |

All future phases maintain the same invariant envelope: **no execution, no capital, no self-activation**.

---

## 8. Success Criteria

| Criterion | Measurement |
|-----------|-------------|
| Multi-broker ingestion | ≥ 3 broker adapters operational (2 India, 1 US) |
| Holdings normalization | 100% of raw holdings normalised to canonical schema |
| Intelligence scoring | All 4 modules produce scores for every holding |
| Portfolio analytics | All 5 diagnostic reports generated per portfolio |
| Dashboard integration | 6 new dashboard components rendering data |
| Market parity | US and INDIA produce identical output schemas |
| Determinism | Identical inputs → identical outputs verified |
| Latency | < 2000ms per portfolio evaluation |
| Invariant compliance | Zero execution, zero capital commitment |

---

*This document is a design artifact produced under governed execution mode. No real trades, capital, or strategies were activated during its creation.*
