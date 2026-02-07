# Dashboard Completeness Checklist
**Target:** TraderFund Dashboard (Epistemic Restoration)
**Status:** VERIFIED

---

## Foundation
- [x] **Market Scope at Root**: Changing the market toggle strictly changes all data contexts (Regime, Macro, Strategy).
- [x] **Data Anchor Panel**: Visible at the top, showing Truth Epoch and Provenance.
- [x] **No Mock Data**: All metrics are driven by file-based ingestion or explicitly marked as "Purged/Empty".

## Epistemic Clarity
- [x] **Market Proxy Sets Visible**: Snapshot explicitly names "S&P 500" or "Nifty 50" (and source file hint).
- [x] **Data Source vs Proxy**: UI distinguishes between the *ideal* proxy and the *actual* source file.
- [x] **Detected vs Actionable Regime**: "Market Condition" is distinct from "Execution Gate".
- [x] **Macro Scope Explicit**: Macro indicators are tagged `[US]`, `[IN]`, or `[GL]`.

## Coherence
- [x] **System Health Never NA**: Active layers show specific status (OK/ERROR), not generic N/A.
- [x] **Strategy States Terminal**: Strategies are Eligible/Rejected/Inactive, never "Calculating" indefinitely.
- [x] **Capital Narrative Market-Aware**: Capital readiness explicitly frames itself within the selected market context.
- [x] **Confidence Justified**: Confidence Gauge (High/Med/Low) matches the logic defined in DWS.
