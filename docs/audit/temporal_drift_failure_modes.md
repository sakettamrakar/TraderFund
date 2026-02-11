# Temporal Drift Failure Modes & Handling

**Version**: 1.0.0
**Epoch**: TE-2026-01-30
**Intent**: Define system behavior in response to temporal drift (asynchrony between RDT, CTT, and TE), ensuring safe failure states and explicit operator guidance.

## 1. Classification of Drift

### 1.1 Ingestion Drift (`RDT > CTT`)
**Definition**: Raw data is available but has not been successfully validated into the canonical store.
- **Cause**: Schema validation failure, missing critical columns, network interruption during fetch.
- **System Response**:
    - **Status**: `INGESTION_FAILED` / `STALE`
    - **Action**: Alert Operator. Reject partial data.
    - **TE**: Remains `T-1`.
    - **Dashboard**: "Data Validation Failed. Check Logs."

### 1.2 Evaluation Drift (`CTT > TE`)
**Definition**: Canonical data is current, but system evaluation (Intelligence/Governance) has not run or failed.
- **Cause**: Decision Engine error, Policy constraint violation, resource exhaustion.
- **System Response**:
    - **Status**: `EVALUATION_PENDING` / `STALE`
    - **Action**: Highlight "Pending Evaluation" state. Disable new trades.
    - **Dashboard**: "New Data Ready. Awaiting Evaluation."

### 1.3 Asymmetric Market Drift (`TE_US != TE_INDIA`)
**Definition**: One market has advanced significantly ahead of another (e.g., US: T, India: T-5).
- **Cause**: Regional holiday, feed failure for specific region.
- **System Response**:
    - **Status**: `market_drift_detected`
    - **Action**: 
        - If drift > 2 days: **Audit Required**. 
        - Check cross-market correlations.
    - **Dashboard**: Show drift warning on laggard market.

## 2. Failure Scenarios

### Scenario A: Partial Update (Critical Data Missing)
- **Context**: `SPY` updated to T, but `VIX` remains at T-1.
- **Risk**: Decision Engine runs with stale volatility data -> Incorrect sizing.
- **Handling**:
    - **Check**: `verify_data_completeness()`
    - **Response**: BLOCK Evaluation for US Market.
    - **Log**: "Missing critical dependency: VIX [T-1]. Evaluation blocked."

### Scenario B: Future Leakage (Impossible State)
- **Context**: `TE > CTT` (System advanced without data).
- **Risk**: Hallucination.
- **Handling**:
    - **Immediate HALT**.
    - **Alert**: "CRITICAL EPISTEMIC FAILURE: Future Leakage."
    - **Recovery**: Manual Rollback Required.

### Scenario C: Stale Threshold Breached
- **Context**: `TE < RDT - 3 Days` (System ignored data for >3 days).
- **Handling**:
    - **Status**: `SYSTEM_OBSOLETE`
    - **Action**: Force re-initialization / Full Re-Ingest.

## 3. Operator Resolution Runbook

| Failure Mode | Operator Action |
| :--- | :--- |
| **Ingestion Drift** | Check `data_acquisition.log` -> Fix source/schema -> Re-run Ingestion. |
| **Evaluation Drift** | Check `decision_engine.log` -> Resolve logic error -> Manually trigger Evaluation. |
| **Asymmetric Drift** | Verify holiday calendar. If not holiday, investigate data feed for lagging market. |
| **Future Leakage** | **STOP SYSTEM IMMEDIATELY**. Audit `truth.json`. Perform forensic analysis. |

This ensures that temporal drift never silently propagates errors into trading decisions.
