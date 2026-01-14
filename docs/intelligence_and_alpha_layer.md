# Intelligence & Alpha Layer Design

## PART 1: US INDICATOR ENGINE

### 1. Indicator Scope
The US Indicator Engine is a computed layer sitting strictly *above* the Curated OHLCV layer. It transforms price action into technical features.

**Core Indicators:**
- **Momentum**: RSI (14, 50), MACD (12, 26, 9), ROC (Rate of Change).
- **Trend**: SMA (20, 50, 200), EMA (9, 21), ADX (Average Directional Index).
- **Volatility**: ATR (Average True Range), BBANDS (Bollinger Bands).
- **Volume**: VWAP (Intraday only), OBV (On-Balance Volume), Relative Volume (RVOL).

**Timeframes:**
primary focus is **Daily (1D)** for swing/position analysis.
Secondary support for **Intraday (5m, 15m, 1h)** for execution timing, strictly separated in storage.

### 2. Compute Strategy Decision
**Decision: Local Computation (pandas-ta / talib) is PREFERRED.**

| Feature | Local Compute | Alpha Vantage API | Verdict |
| :--- | :--- | :--- | :--- |
| **Cost** | Free (CPU only) | Consumes API Quota | **Local** |
| **Control** | Full parameter control | Black-box defaults | **Local** |
| **Reproducibility** | Versioned code | API may change silently | **Local** |
| **Latency** | Milliseconds | Network RTT | **Local** |

**Role of API:**
The Alpha Vantage `Technical Indicators` API is used **solely** for:
1.  **Benchmarking**: Periodically validating local calculations against a third party.
2.  **Missing Data**: Gap-filling if local lookback windows are insufficient (edge cases only).

### 3. Architecture
- **Input**: Read-Only access to `data/analytics/us/prices/{freq}/`.
- **Compute**: Stateless Python workers/functions.
- **Output**: `data/analytics/us/indicators/{freq}/{indicator_group}/{symbol}.parquet`
  - *Example*: `data/analytics/us/indicators/daily/momentum/AAPL.parquet` containing RSI, MACD cols.

**Storage Strategy: Materialized on Schedule**
Indicators are computed and persisted immediately after the daily ingestion/curation job. This avoids "compute-on-read" latency during heavy signal scanning.

### 4. Indicator Metadata
To ensure reproducibility, every indicator file includes metadata in the Parquet schema or sidecar JSON:
- `lib_version`: e.g., `pandas-ta==0.3.14`
- `parameters`: e.g., `{"rsi_length": 14}`
- `source_data_hash`: Hash of the OHLCV file used.

### 5. Failure & Drift Handling
- **Missing Candles**: Indicators requiring contiguous data (EMA) reset or return NaN if gaps > threshold (e.g., 3 days).
- **Recomputations**: If the underlying OHLCV is patched (backfill), dependent indicators are automatically flagged for re-compute via dependency graph.

---

## PART 2: SIGNAL TAXONOMY & CONFIDENCE SCORING

### 1. Signal Philosophy
- **Signal ≠ Trade**: A signal is an observation of a market condition (e.g., "RSI Oversold"). It is *information*, not an *instruction*.
- **Probabilistic**: Signals provide a probability tilt, not a guarantee.

### 2. Signal Taxonomy
| Category | Example Signals | Context |
| :--- | :--- | :--- |
| **Momentum** | `RSI_Oversold_CrossUp`, `MACD_Bullish_Divergence` | Reversal candidates. |
| **Trend** | `Golden_Cross` (SMA50 > SMA200), `Price_Above_EMA20` | Trend following. |
| **Mean Reversion** | `Price_Outside_BBand_2Std`, `RSI_Extreme_80` | Extended states. |
| **Volatility** | `ATR_Expansion`, `Bollinger_Squeeze` | Breakout potential. |
| **Event** | `Earnings_Surprise`, `Gap_Up_On_Volume` | News/catalyst driven. |

### 3. Signal Structure
Every signal is a structured object:
```python
class Signal:
    id: str                 # UUID
    name: str               # "RSI_Bullish_Divergence"
    symbol: str             # "AAPL"
    timestamp: datetime     # Detection time
    direction: int          # 1 (Bull), -1 (Bear)
    horizon: str            # "3-5 days"
    strength: float         # 0.0 to 1.0 (Raw technical strength)
    confidence: float       # 0.0 to 1.0 (Meta-score)
    metadata: dict          # { "rsi_val": 28.5, "price": 150.0 }
```

### 4. Confidence Scoring
Confidence is a **Meta-Layer** derived from context, distinct from the raw signal strength.

**Inputs:**
- **Consensus**: Do other indicators agree? (e.g., RSI Oversold + Support Level = High Confidence).
- **Volume**: Is the signal supported by above-average volume?
- **Regime**: Is a counter-trend signal firing in a strong trend? (Low Confidence).

**Scoring Model (0-100):**
- Base: 50
- +10 for Volume Confirmation
- +20 for Multi-Timeframe Alignment
- -30 for Regime Conflict

**Decay**: Confidence follows a half-life decay. A 5-minute signal decays fast; a daily signal persists.

### 5. Signal Lifecycle
1.  **Creation**: Scanner identifies condition.
2.  **Validation**: Confidence Engine computes score. If Score < Threshold, discard or log as "Noise".
3.  **Active**: Available for strategies/narratives.
4.  **Expired**: Time horizon passed.
5.  **Invalidated**: Stop-loss condition met or opposite signal fired.

### 6. Explainability
Every signal must persist a "Narrative Snippet":
> "RSI Cross Up detected at 14:00. Confidence 75% due to alignment with Daily Trend and 2x average volume."

---

## PART 3: EVENT → NARRATIVE GENESIS ENGINE

### 1. Event Sources
The engine ingests discrete events from disparate streams:
- **Market Data**: "AAPL up 5% on 2x Vol".
- **News API**: "Apple releases Vision Pro".
- **Macro**: "Fed holds rates".
- **Signals**: "Tech Sector Bullish Breakout".

### 2. Event Normalization
All events are converted to a standard schema:
- `timestamp`: UTC.
- `entities`: list(`["AAPL", "Technology", "US"]`).
- `sentiment`: -1.0 to 1.0.
- `source_reliability`: 0.0 to 1.0.

### 3. Narrative Genesis Rules
A **Narrative** is a cluster of events that tell a coherent story.
**Clustering Logic:**
- **Semantic Similarity**: NLP embeddings closeness.
- **Temporal Proximity**: Events occurring within a sliding window (e.g., 24h).
- **Causal Chain**: (News) t0 -> (Price Action) t1 -> (Signal) t2.

### 4. Narrative Structure
```python
class Narrative:
    id: str
    headline: str           # LLM Generated: "Apple Rally driven by Vision Pro Launch"
    summary: str
    core_events: List[Event]
    related_assets: List[str]
    sentiment_score: float
    confidence: float
```

### 5. Narrative Lifecycle
- **Birth**: First significant event (Anchor).
- **Reinforcement**: Subsequent events map to the same cluster, boosting confidence.
- **Mutation**: New contradictory events shift the sentiment (e.g., "Rally Fades").
- **Death**: No new events for X periods, or explicit invalidation.

### 6. Guardrails
- **Noise Filter**: Single, low-impact events do NOT spawn narratives. They remain as "Orphans".
- **Hindsight Bias**: Narratives are constructed purely on *available* information at `t`. No look-ahead clustering.

---

## PART 4: CROSS-MARKET ALPHA DISCOVERY

### 1. Philosophy
**Separate Data, Unified Analysis.**
We search for correlations and lead-lag effects without physically merging the US and India datasets. We normalize *returns* and *features*, not prices.

### 2. Normalized Comparison Layer
To compare `AAPL` (USD) and `TCS` (INR):
- **Returns**: Log returns are currency-agnostic.
- **Volatility**: Z-Scores normalize the amplitude of moves.
- **Time**: All times aligned to UTC. Holidays in either market result in `NaN` or `Last Observation Carried Forward` (depending on analysis type).

### 3. Cross-Market Pattern Types
- **US Lead / India Lag**: Does a tech sell-off in NASDAQ (Close 20:00 UTC) predict a Gap Down in NIFTY IT (Open 03:45 UTC next day)?
- **Sector Rotation**: Does capital flow from US Risk-On to Emerging Markets Risk-On?
- **Supply Chain**: Does news effects on US Oil Giants propagate to Indian Paint/Airline stocks (Input cost sensitivity)?

### 4. Alpha Hypothesis Generation
The system systematically tests pairs and sectors:
1.  **Hypothesis**: "US Tech Indices Granger-Cause Indian IT Indices."
2.  **Test**: Rolling window Granger Causality test on normalized returns.
3.  **Filter**: Reject if p-value > 0.05 or if effect size is negligible.

### 5. Output Artifacts
- **Alpha Candidates**: JSON definition of the relationship.
  ```json
  {
    "source": "NASDAQ_100",
    "target": "NIFTY_IT",
    "type": "Lead_Lag",
    "lag": "1_day",
    "correlation": 0.85,
    "confidence": 0.9
  }
  ```
- **Live Monitor**: A dashboard widget tracking the live divergence from the historical correlation.

### 6. What This System Does NOT Do
- It does **NOT** execute trades. It outputs a "Signal" or "Alpha Candidate" for a Trading Engine to consume.
- It does **NOT** allocate capital. It provides confidence scores only.
