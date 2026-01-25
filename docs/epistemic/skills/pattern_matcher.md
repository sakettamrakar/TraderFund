# Skill: Pattern Matcher

**Category**: Analysis (Informational)  
**Stability**: Core

## 1. Purpose
The `pattern-matcher` identifies historical precedents for current market conditions. It prevents "This time is different" thinking by forcing a comparison with historical base rates, connecting active signals to the historical replay database.

## 2. Inputs & Preconditions
- **Required Inputs**: Market Symbol, Lookback Window.
- **Required State**: Historical OHLCV database, `Regime_Taxonomy.md`.

## 3. Outputs & Side Effects
- **Outputs**: Similarity Similarity Report (Price correlation/Event sequence alignment).
- **Ledger Impact**: NONE (Read-Only).

## 4. Invariants & Prohibitions
- **No Prediction**: MUST NOT predict outcome; reports ONLY historical base rates.
- **Context-First**: Matches must be strictly filtered by the active Market Regime.
- **Non-Mutation**: Never writes to historical data.

## 5. Invocation Format

```
Invoke pattern-matcher
Mode: REAL_RUN
Target: SPY

ExecutionScope:
  mode: price

Options:
  lookback: 5
  threshold: 0.85
  metric: dtw
```

## 6. Failure Modes
- **Data Gap**: Historical data for the requested symbol/range is missing (Terminal).
- **Novel Regime**: No historical matches meet the threshold (Non-Fatal; indicates context novelty).

## 7. Notes for Operators
- **Reliability**: Higher thresholds (>0.9) provide better grounding but may return empty sets in volatile regimes.
- **Chaining**: Fed into the **Belief Layer** to generate conviction scores.
