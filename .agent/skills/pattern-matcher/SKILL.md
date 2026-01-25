---
name: pattern-matcher
description: A skill to search historical data for price, volume, or event patterns similar to the current context.
---

# Pattern Matcher Skill

**Status:** Operational  
**Skill Category:** Analysis (Informational)

## 1. Skill Purpose
The `pattern-matcher` identifies historical precedents for the current market state. It answers the question: "When have we seen this before?" by connecting live signals to the historical replay database.

## 2. Invocation Contract

### Standard Grammar
```
Invoke pattern-matcher
Mode: <REAL_RUN | VERIFY>
Target: <symbol | market_id>
ExecutionScope:
  mode: <price | event | hybrid>
  [lookback: <n>]
Options:
  metric: <correlation | dtw>
  threshold: <0.0-1.0>
```

## 3. Supported Modes & Selectors
- **REAL_RUN**: Search historical data and return a list of similarity-scored "Similar Epochs."
- **VERIFY**: Check the integrity of the pattern database for the target symbol.
- **Selectors**:
    - `price`: Match based on OHLCV sequences.
    - `event`: Match based on Narrative event sequences.
    - `hybrid`: Match based on concurrent price and event alignment.

## 4. Hook & Skill Chaining
- **Chained From**: Invoked by the **Narrative Engine** or during **Strategy Mapping**.
- **Chained To**: Results are used to populate signal conviction in the **Belief Layer**.

## 5. Metadata & State
- **Inputs**: Live OHLCV, historical database, [Regime_Taxonomy.md](file:///c:/GIT/TraderFund/docs/Regime_Taxonomy.md).
- **Outputs**: Similarity report with outcome distributions.

## 6. Invariants & Prohibitions
1.  **Read-Only**: NEVER modifies historical data or live signals.
2.  **No Prediction**: Does NOT predict future outcomes; only reports historical base rates.
3.  **Context Before Signal**: Matches MUST be filtered by the active Regime.

## 7. Example Invocation
```
Invoke pattern-matcher
Mode: REAL_RUN
Target: SPY
ExecutionScope:
  mode: price
  lookback: 5
Options:
  metric: dtw
  threshold: 0.85
```
