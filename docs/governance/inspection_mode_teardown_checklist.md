# Inspection Mode Teardown Checklist
**Version**: 1.0.0
**Epoch**: TE-2026-01-30
**Intent**: Ensure ZERO RESIDUE after Stress Investigation.

## 1. Prerequisites
Before closing the Inspection panel, ensure no background tasks are still parsing or rendering stress data.

## 2. Checklist

### 2.1 Frontend Cleanliness
- [ ] **State Flag**: Verify `inspection_mode` is reset to `false`.
- [ ] **Store Sanitization**: Confirm `InspectionStore` object is `null` or empty.
- [ ] **DOM Cleanup**: Ensure all "SIMULATION" watermarks and "SCENARIO" badges are removed from the DOM.
- [ ] **Event Listeners**: Ensure scenario-specific click listeners (e.g., S1 toggle) are unbound.

### 2.2 Backend Integrity
- [ ] **Log Check**: Verify no "Stress Scenario" logs were written to the `LiveTradeLog` (e.g., `logs/decision_engine.log`).
- [ ] **Database**: Verify no new rows were inserted into `regime_narrative` or `market_snapshots` during the inspection interval.
- [ ] **File System**: Ensure no temporary JSON files (e.g., `temp_s1.json`) remain in `data/staging/`.

### 2.3 Dashboard Restoration
- [ ] **Re-Fetch**: The dashboard MUST trigger a fresh `GET /api/system/status` immediately upon exit.
- [ ] **Visual Check**:
    - [ ] Regime Widget shows current LIVE status (not S1-S4).
    - [ ] Policy Card shows true eligibility (not suppressed).
    - [ ] Header/Footer confirms "LIVE TRUTH" epoch.

### 2.4 Alert Quietness
- [ ] **Verify**: No PagerDuty or email alerts were dispatched for the simulated stress conditions.

## 3. Failure Protocol
If any artifact remains:
1.  **Stop Dashboard**: Halt the frontend server.
2.  **Purge Cache**: Clear browser cache/local storage.
3.  **Investigate logs**: Check backend logs for leakage.
4.  **Restart**: Reboot frontend with clean state.
5.  **Report**: File a `governance_breach` report.
