# India Market Parity Flow

## 1. Current State: DEGRADED
```
RELIANCE.NS (Single Stock) 
    ↓ 
Regime Context (Low Confidence)
    ↓
Factor Context (Partial/Inferred)
    ↓
Decision Policy → OBSERVE_ONLY (Forced)
    ↓
Fragility Policy → NOT_EVALUATED
```

## 2. Target State: CANONICAL
```
NIFTY50 + BANKNIFTY + INDIAVIX + IN10Y
    ↓ 
Regime Context (High Confidence)
    ↓
Factor Context (Full Coverage)
    ↓
Decision Policy → Dynamic Evaluation
    ↓
Fragility Policy → Full Stress Detection
```

## 3. Transition Logic

### 3.1. Parity Check Engine
A new component `IndiaParityChecker` will be added to the pipeline.
*   **Inputs**: `india_proxy_sets.json`, Data manifest.
*   **Logic**: For each canonical proxy, check:
    1.  File exists in `data/regime/raw/` or `data/india/`.
    2.  Row count >= `required_history_days`.
    3.  Latest date is within 2 trading days.
*   **Output**: `parity_status.json` with `{status: CANONICAL | DEGRADED, gaps: [...]}`.

### 3.2. Decision Policy Gate Update
The `DecisionPolicyEngine` for India will consult `parity_status.json`.
*   If `status == DEGRADED`: Return `OBSERVE_ONLY` (Current behavior).
*   If `status == CANONICAL`: Proceed to dynamic evaluation (Future).

### 3.3. Dashboard Indicator
The `DataAnchorPanel` will display a "Parity Readiness" indicator for India:
*   **Red**: DEGRADED (Current).
*   **Yellow**: PARTIAL (Some proxies active).
*   **Green**: CANONICAL (All proxies active).

## 4. Safeguards
*   **No Automatic Promotion**: The transition from DEGRADED to CANONICAL requires explicit operator acknowledgment (Phase 11+).
*   **Fail-Closed**: If `parity_status.json` is missing or corrupt, default to DEGRADED.
