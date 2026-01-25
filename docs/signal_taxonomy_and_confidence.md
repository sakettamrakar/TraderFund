# Signal Taxonomy & Confidence Scoring System

## 1. Signal Philosophy & Design Goals

### Definitions
- **Signal**: A discrete, probabilistic observation of a specific market condition at a specific time (e.g., "RSI(14) < 30 on AAPL implies oversold").
- **NOT a Signal**: Raw data (Price), Derived Data (Indicator Value), or an Action (Buy Order).
- **Purpose**: To convert continuous, noisy market data into discrete, semantic events that can be reasoned about, scored, and composed into narratives.

### Core Principles
1.  **Probabilistic, Not Deterministic**: A signal represents a tilt in probability, not a guarantee of future price action.
2.  **State, Not Prediction**: Signals describe the *current state* (e.g., "Trend is Strong"), which *implies* a prediction but is grounded in present facts.
3.  **Decay is Fundamental**: Information has a half-life. A signal generated at T=0 loses value with every passing minute.
4.  **Explainability First**: If a signal cannot explain *why* it fired (e.g., "Triggered by localized volume spike > 3 sigma"), it is rejected.

---

## 2. Signal Classification Framework

### A. Momentum Signals
*   **Purpose**: Identify the strength and speed of price movement.
*   **Time Horizon**: Short to Medium (Intraday to Days).
*   **Typical Indicators**: RSI, MACD, ROC, Stochastic.
*   **Examples**: `RSI_Oversold`, `MACD_Bullish_Crossover`, `Mom_Deceleration`.
*   **Failure Mode**: Range-bound markets (whipsaws).

### B. Trend Confirmation Signals
*   **Purpose**: Confirm the persistence of a directional move.
*   **Time Horizon**: Medium to Long (Days to Weeks).
*   **Typical Indicators**: SMA/EMA Crossovers, ADX, SuperTrend.
*   **Examples**: `Golden_Cross`, `Price_Above_SMA200`, `ADX_High_Trend`.
*   **Failure Mode**: Late detection (lag) at trend reversals.

### C. Mean Reversion Signals
*   **Purpose**: Identify overextended prices likely to snap back to an average.
*   **Time Horizon**: Short (Hours to Days).
*   **Typical Indicators**: Bollinger Bands, Keltner Channels, Deviation from VWAP.
*   **Examples**: `BBand_Lower_Breach`, `VWAP_2Std_Deviation`.
*   **Failure Mode**: Trending markets (attempting to catch falling knives).

### D. Volatility Regime Signals
*   **Purpose**: Characterize the "weather" of the market (Stormy vs. Calm).
*   **Time Horizon**: Variable.
*   **Typical Indicators**: ATR, Bollinger Band Width, VIX (if available).
*   **Examples**: `Volatility_Squeeze`, `ATR_Expansion`, `High_Vol_Regime`.
*   **Failure Mode**: Volatility clustering (low vol begets low vol, until it doesn't).

### E. Liquidity / Volume Signals
*   **Purpose**: Validate price action through participation.
*   **Time Horizon**: Instantaneous to Daily.
*   **Typical Indicators**: RVOL (Relative Volume), OBV, Money Flow Index.
*   **Examples**: `High_Volume_Breakout`, `Volume_Drying_Up`.
*   **Failure Mode**: Dark pools/block trades skewing data.

### F. Event-Driven Signals
*   **Purpose**: React to discrete external or structural events.
*   **Time Horizon**: Variable.
*   **Examples**: `Earnings_Surprise`, `Gap_Up`, `New_52W_High`.
*   **Failure Mode**: Data latency or erroneous event tags.

---

## 3. Canonical Signal Definition Schema

Each signal must be serialized to a JSON-compatible object following this strict schema. This schema maps 1:1 to the `Signal` class in code.

```python
class Signal:
    # Identity
    signal_id: str              # UUID4
    signal_name: str            # e.g., "RSI_Bullish_Divergence"
    market: str                 # "US" or "IN"
    asset_id: str               # "AAPL" or "INFY"
    
    # Classification
    signal_category: str        # "Momentum" | "Trend" | ...
    direction: str              # "BULLISH" | "BEARISH" | "NEUTRAL"
    
    # Timing
    trigger_timestamp: datetime # UTC timestamp of detection
    expected_horizon: str       # "1D", "4H", "2W"
    expiry_timestamp: datetime  # UTC when signal becomes stale
    
    # Strength & Scoring
    raw_strength: float         # 0.0 to 1.0 (Technical magnitude)
    confidence_score: float     # 0.0 to 100.0 (Contextual reliability)
    
    # Logic
    invalidation_conditions: List[str] # e.g., ["Price < 145.0"]
    
    # Explainability
    explainability_payload: Dict[str, Any]
    # Example:
    # {
    #   "primary_factor": "RSI=28.5 (Oversold)",
    #   "supporting_factors": ["Volume +50% vs Avg"],
    #   "context": "Uptrend on Daily"
    # }
```

---

## 4. Confidence Scoring Model (Conceptual)

Confidence is a dynamic score reflecting how much we should "trust" a signal. It is distinct from `raw_strength` (which is just math).

### Inputs to Confidence
1.  **Indicator Agreement**: Do other indicators confirm? (e.g., RSI Bullish + MACD Bullish > Just RSI).
2.  **Volume Confirmation**: Is volume > 1.2x average? (+Score).
3.  **Regime Alignment**:
    *   Bull Signal in Bull Trend = High Confidence.
    *   Bull Signal in Bear Trend = Low Confidence.
4.  **Volatility Penalty**: Extreme volatility reduces confidence in directional signals (noise penalty).

### Scoring Scale (0 - 100)
*   **0-20 (Noise)**: Ignored.
*   **21-50 (Weak)**: Watchlist only, no strong conviction.
*   **51-75 (Moderate)**: Standard actionable signal.
*   **76-100 (High)**: Rare, multi-factor alignment (Confluence).

### Confidence Decay logic
Signals are organic matter; they rot.
*   **Formula**: $C(t) = C_{initial} \times e^{-\lambda t}$
*   **$\lambda$**: Determined by `expected_horizon`. A "Scalp" signal decays in minutes; a "Trend" signal decays in days.
*   **Update Frequency**: Confidence is re-evaluated on every new candle.

---

## 5. Signal Lifecycle Management

### Stages
1.  **Created**: Scanner detects condition. Object instantiated. Confidence calculated.
2.  **Active**: Signal pushed to downstream consumers (Narrative Engine, Dashboard).
3.  **Weakened**: Time has passed, confidence has decayed below threshold (e.g., < 40).
4.  **Expired**: `expiry_timestamp` reached. Signal moved to history/cold storage.
5.  **Invalidated**: Price action violated `invalidation_conditions` (e.g., Stop Loss hit). Signal marked `VOID` immediately.

### Transitions
*   `Created` -> `Active` (Immediate if Conf > Threshold)
*   `Active` -> `Weakened` (Decay)
*   `Active` -> `Invalidated` (Price shock)
*   `Weakened` -> `Expired` (Time)

---

## 6. Explainability & Auditability

### Self-Explanation
Every Signal object carries its own proof.
*   **"Why did you fire?"**: "Because RSI(14) was 28.5, crossing above 30."
*   **"Why is confidence high?"**: "Because Volume was 150% of 20-day Avg AND Price is above SMA200."
*   **"Why are you invalid?"**: "Price closed below 150.0 (Support Level)."

### Human Inspection
*   **Dashboard View**: Signals should be viewable as discrete events on a timeline, expandable to show the `explainability_payload`.
*   **Audit Log**: All state transitions (Active -> Weakened) are logged events, allowing replay of the signal's "life".

---

## 7. Market-Specific Customization Rules

### What Can Differ
*   **Thresholds**: Volatility thresholds for India might differ from US due to differing market caps/liquidity.
*   **Timezones**: Logic involving "Market Open" or "Close".
*   **Asset Classes**: US has strict "Day Pattern" rules; India has different circuit breaker logic.

### What Must Remain Agnostic
*   **Schema**: The JSON structure is immutable.
*   **Taxonomy**: "Momentum" means the same thing in Mumbai and New York.
*   **Scoring Logic**: The calculation *method* for confidence remains standard, even if weights vary slightly.

---

## 8. Explicit Non-Goals

1.  **No Trade Execution**: This system does not place orders. It outputs information.
2.  **No PnL Logic**: Signals do not track "profit". They track "correctness of direction" (Validation).
3.  **No Portfolio construction**: Signals are atomic. They do not know about portfolio beta or exposure.
4.  **No Blackbox ML**: Confidence scores are heuristic (rule-based) for now. No neural nets.
