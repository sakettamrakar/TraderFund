# Documentation Impact Declaration (DID)

**Date**: 2026-01-29  
**Scope**: Capital Storytelling & Observability  
**Type**: OBSERVABILITY / GOVERNANCE

## Summary

Enhanced the dashboard with a **Capital Storytelling** layer. This enhancement explains *why* capital acts (or remains idle) through a narrative history, explicit blockers, and counterfactual reasoning, all without enabling execution.

## Changes

### 1. Capital History Architecture
- **New History Recorder**: `src/capital/capital_history_recorder.py` persists symbolic capital states to `docs/capital/history/capital_state_timeline.json`.
- **Pipeline Integration**: `ev_tick.py` Step 7 now appends a new state entry for every tick.
- **API**: Exposed `/api/capital/history` to serve this timeline.

### 2. Dashboard Components
- **CapitalStoryPanel**:
    - **Narrative**: "Capital Posture: IDLE..."
    - **Timeline**: Scrolls through recent historical states.
    - **Checklist**: "Why Capital Has Not Moved" (e.g., "Execution Authorization: ❌ NO").
    - **Counterfactual**: Explains that even if eligible, limits would apply.
- **CapitalInvariants**: Fixed panel listing hard constraints (No Leverage, Observer Only).

## Safety Invariants Verified
✅ **Inertness**: All capital visuals are based on symbolic paper capital (100 units).  
✅ **Explanation vs. Action**: The system explains its state but provides no buttons or controls to change it.  
✅ **Trust**: Hard constraints are prominently displayed as invariants.

## Validation Results
- **Backend**: Verified `ev_tick.py` logs "History Updated" with correct state and reason.
- **Frontend**: Components integrated into `App.jsx`. Manual verification required for render details due to environment limitation.
