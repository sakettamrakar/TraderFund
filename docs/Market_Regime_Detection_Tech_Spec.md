# Market Regime Detection — Technical Specification (Implementation Ready)

**Version:** 1.1.0  
**Blueprint Reference:** [v1.1.0 Charter](Market_Regime_Detection_Blueprint.md)  
**Status:** IMPLEMENTATION READY  
**Author:** Systems Engineering Team  
**Last Updated:** 2026-01-15

---

## 1. System Components

The Regime Detection System is designed as a standalone library (`regime_core`) that can be embedded into the execution engine or exposed as a microservice.

### Component Diagram
```text
[Input Sources]                 [Configuration Store]
      |                                 |
      v                                 v
[Data Normalizer] --> [Provider Aggregator] <--> [Config Loader]
                             |
                             v
                     [Regime Calculator]
                             |
                   [State Manager (Hysteresis)]
                             |
                             v
                     [Output Publisher]
```

### Core Classes
*   **`ProviderAggregator`**: Facade that polls all registered providers (`ITrendStrengthProvider`, etc.) for normalized values.
*   **`RegimeCalculator`**: Pure function mapping {Provider Outputs} -> {RawRegime}.
*   **`StateManager`**: Stateful wrapper handling persistence, transitions, and confidence buffers.
*   **`ConfigLoader`**: Handles hierarchy overrides (Market -> Sector -> Stock).

---

## 2. Data Contracts

### 2.1 Input Schema (Market Data)
The system expects standardized candle/tick data.
```json
{
  "symbol": "NIFTY50",
  "timestamp": "2026-01-15T10:00:00Z",
  "open": 21500.0,
  "high": 21550.0,
  "low": 21480.0,
  "close": 21525.0,
  "volume": 1500000,
  "timeframe": "5m"
}
```

### 2.2 Output Schema (Regime Payload)
This is the canonical output structure consumed by downstream strategies.
```json
{
  "meta": {
    "symbol": "NIFTY50",
    "timestamp": "2026-01-15T10:00:00Z",
    "version": "1.1.0"
  },
  "regime": {
    "behavior": "TRENDING_NORMAL_VOL",
    "bias": "BULLISH",
    "id": 101,
    "confidence_components": {
      "confluence_score": 0.9,
      "persistence_score": 0.8,
      "intensity_score": 0.7
    },
    "total_confidence": 0.82
  },
  "factors": {
    "trend_strength_norm": 0.72,
    "volatility_ratio": 1.15,
    "liquidity_status": "NORMAL",
    "event_pressure_norm": 0.1
  },
  "flags": {
    "is_event_locked": false,
    "is_stable": true,
    "risk_multiplier": 1.0
  }
}
```

### 2.3 Error Payload
```json
{
  "error": "INSUFFICIENT_DATA",
  "symbol": "NEW_IPO_TICKER",
  "action": "FORCE_NO_TRADE",
  "timestamp": "..."
}
```

---

## 3. Provider Implementations (Default)

The engine consumes standardized *Providers*. Logic inside providers can be swapped without altering the engine.

### 3.1 Trend Providers
*   **Role:** `ITrendStrengthProvider`
    *   **Default Impl:** ADX (Wilder).
    *   **Normalization:** Returns `0.0 - 1.0`. (ADX / 100).
*   **Role:** `ITrendAlignmentProvider`
    *   **Default Impl:** EMA Cloud (20/50/200).
    *   **Normalization:** Returns `Enum(BULLISH, BEARISH, NEUTRAL, MIXED)`.

### 3.2 Volatility Providers
*   **Role:** `IVolatilityRatioProvider`
    *   **Default Impl:** ATR Ratio.
    *   **Formula:** `Current_ATR(14) / SMA(ATR(14), 20)`.
    *   **Normalization:** Returns `float` (1.0 = Baseline).

### 3.3 Liquidity Providers
*   **Role:** `ILiquidityProvider`
    *   **Default Impl:** RVOL (Relative Volume).
    *   **Formula:** `Vol / SMA(Vol, 20)`.
    *   **Normalization:** Returns `float`. (< 0.2 = Dry).

### 3.4 Event Pressure Providers
*   **Role:** `IEventPressureProvider`
    *   **Default Impl:** Calendar Distance.
    *   **Formula:** `1.0 - (Minutes_To_Event / Max_Lookahead)`.
    *   **Normalization:** Returns `0.0` (No Event) to `1.0` (Imminent Impact).
    *   **Flags:** Returns `is_lock_window` (boolean) if T < 10 mins.

---

## 4. State Machine Design

The core `StateManager` maintains the continuity of regimes and confidence.

### 4.1 Transition Logic
Transitions occur when the `RegimeCalculator` outputs a *new* state distinct from the *current* state.

**Pseudo-Code:**
```python
def update(provider_data):
    # 1. Calculate Raw Regime
    raw_behavior, raw_bias = calculate_regime(provider_data)
    
    # 2. Check Event Overrides
    if provider_data.event.is_lock_window:
         raw_behavior = EVENT_LOCK
    elif provider_data.event.pressure > 0.8:
         raw_behavior = EVENT_DOMINANT

    # 3. Transitions & Hysteresis
    if raw_behavior == current_behavior:
        persistence_score += increment_step
    else:
        pending_counter += 1
        if pending_counter >= CONFIG.get_hysteresis(raw_behavior):
            current_behavior = raw_behavior
            persistence_score = 0.0
            
    # 4. Compute Composite Confidence
    confidence = (confluence * 0.4) + (persistence * 0.4) + (intensity * 0.2)
```

### 4.2 Hysteresis Constraints
*   **Standard Switch:** Requires `3` consecutive confirmations.
*   **Risk-Off Switch:** (To `HIGH_VOL`, `SHOCK`, `EVENT_LOCK`) requires `1` confirmation (Immediate).
*   **Risk-On Switch:** (From `NO_TRADE` to `TRENDING`) requires `5` consecutive confirmations.

### 4.3 Cooldown
After a `SHOCK` or `EVENT_LOCK` regime, a cooldown timer prevents entry into `NORMAL_VOL` regimes for `N` minutes, forcing `HIGH_VOL` or `UNCERTAIN` intermediate states.

---

## 5. Configuration Model

Configurations are hierarchical.

### 5.1 Base Config (`base_config.yaml`)
```yaml
market_defaults:
  timeframe: "5m"
  history_required: 200

providers:
  trend_strength:
    impl: "adx_standard"
    period: 14
    threshold_trending: 0.25 # Normalized
  volatility_ratio:
    impl: "atr_ratio"
    period: 14
    baseline: 20
    threshold_expansion: 1.5
    
hysteresis:
  default: 3
  risk_off: 1
  risk_on: 5
```

### 5.2 Override Mechanism
*   **Load Order:** Base -> AssetClass -> Symbol.
*   **Example:** `Symbol: TSLA` overrides `threshold_expansion` to `2.0`.

---

## 6. Performance Constraints

*   **Latency Budget:**
    *   Provider Aggregation: < 5ms
    *   State Transition: < 1ms
    *   Total End-to-End: **< 10ms acceptable**, < 2ms target.
*   **Memory:**
    *   Rolling windows utilize `numpy` arrays for O(1) updates.
    *   Stateless Providers (keep state in Engine only).
*   **Throughput:**
    *   500 symbols @ 1 update/sec on single core.

---

## 7. Testing Strategy

### 7.1 Unit Tests
*   **Provider Verification:** Feed arrays to ADX Provider, assert normalized output.
*   **State Machine:** Mock Provider outputs, assert `pending_counter` increments and resets correctly.

### 7.2 Historical Replay
*   **Dataset:** 1 Year of 5m OHLCV.
*   **Metric:** "Flicker Rate" (Regimes lasting < 15 mins) must be < 5%.
*   **Metric:** "Event Lock Accuracy" (Did it lock before every Earnings call?).

### 7.3 Chaos Testing
*   **Null Data:** Inject `NaN`. Expect `NO_TRADE` / `UNCERTAIN`.
*   **Zero Volume:** Inject 0 volume. Expect `LIQUIDITY_DRY`.
*   **Time Gaps:** Skip 2 hours. Expect State Reset / Warm-up.

---

## 8. Deployment Model

*   **Artifact:** Python Package `traderfund.regime`.
*   **Versioning:** Semantic Versioning (1.1.0).
*   **Interface:**
    ```python
    from traderfund.regime import RegimeEngine
    
    engine = RegimeEngine(config="config/market_conf.yaml")
    engine.push_tick(tick_data)
    state = engine.current_state()
    ```
