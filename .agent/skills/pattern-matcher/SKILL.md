---
name: pattern-matcher
description: A skill to search historical data for price, volume, or event patterns similar to the current context.
---

# Pattern Matcher Skill

**Status**: Defined (Phase 2 Unfreeze)
**Authority**: Epistemic Explorer (Read-Only)

## 1. Purpose
The Pattern Matcher is responsible for finding historical precedents. It answers the question: "When have we seen this before?" It connects the current moment to the historical replay database.

## 2. Core Capabilities

### A. Price Action Matching
*   **Input**: Current OHLCV sequence (e.g., last 5 days).
*   **Action**: Search historical database (Parquet/SQL) for high-correlation sequences.
*   **Output**: List of dates with >0.8 correlation (Pearson/DTW).

### B. Event Sequence Matching (Future)
*   **Input**: Sequence of Narrative Events (e.g., "Earnings Beat" -> "Gap Up").
*   **Action**: Find historical instances of similar event chains.
*   **Output**: List of matching narrative chains.

## 3. Operational Constraints

1.  **Read-Only**: This skill **NEVER** modifies historical data.
2.  **No Prediction**: It does not predict "what happens next." It only reports "what happened last time."
3.  **No Trading**: It does not generate signals or orders. It generates **context**.

## 4. Input Schema

```json
{
  "mode": "price | event",
  "symbol": "SPY",
  "lookback_window": 5,
  "metric": "correlation | dtw"
}
```

## 5. Output Schema

```json
{
  "matches": [
    {
      "date": "2022-03-15",
      "similarity_score": 0.92,
      "outcome_next_5d": "+3.4%"
    }
  ],
  "sample_size": 1500,
  "execution_time_ms": 45
}
```

## 6. Failure Behavior
*   If data is missing: **FAIL** (Cannot match).
*   If no matches found: **RETURN EMPTY** (Novel regime).
*   If correlation calculation fails: **ERROR**.

## 7. Relationship to Epistemic Framework
*   **Matching = Contextual Grounding**.
*   This skill prevents "this time is different" thinking by forcing a comparison to base rates.
*   It feeds the **Narrative Engine** with historical evidence.
