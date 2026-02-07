# Task Graph: Dashboard Remediation & Trust Restoration

**Root Specification:** [DWS_DASHBOARD_TRUST_AND_SCOPE.md](./DWS_DASHBOARD_TRUST_AND_SCOPE.md)
**Status:** COMPLETED
**Priority:** P0 is BLOCKING for Execution.

---

## P0 — Structural Correctness (The Foundation)

### T-DASH-01: Root Market Scope Enforcement
- [x] **Status:** COMPLETED
*   **Description:** Refactor `App.jsx` to ensure `market` state is the absolute root of the data tree. Ensure `DashboardContext` (if exists) or prop drilling strictly enforces that changing the market at the top triggers a full re-fetch/re-render of all child components for that specific market.
*   **Inputs:** `App.jsx`, `DataAnchorPanel.jsx`
*   **Outputs:** Updated `App.jsx` with strict prop propagation.
*   **Acceptance Criteria:**
    *   Changing US->INDIA instantly clears all US-specific data from view.
    *   No "stale" US charts appear when INDIA is selected.
    *   URL parameter (if used) updates to reflect `?market=INDIA`.

### T-DASH-02: Regime Semantic Split
- [x] **Status:** COMPLETED
*   **Description:** Split the "Regime" display into two distinct UI elements: "Market Condition" (Observed) and "Execution Gate" (Governance).
*   **Inputs:** `regime_context.json`, `system_status.json`
*   **Outputs:** Refactored `SystemStatus.jsx` or new `RegimeDisplay.jsx`.
*   **Acceptance Criteria:**
    *   UI explicitly labels "Condition" (e.g., Bullish) separately from "Gate" (e.g., Locked).
    *   Tooltip explains distinction (Data vs Rules).

### T-DASH-03: System Health Definition
- [x] **Status:** COMPLETED
*   **Description:** Eliminate "N/A" states in System Health. Define explicit logic for "Healthy" when data is sufficient, even if inactive.
*   **Inputs:** `LayerHealth.jsx`
*   **Outputs:** Updated logic to treat "Inactive but Ready" as "Green/Healthy", not "Grey/Unknown".
*   **Acceptance Criteria:**
    *   0 occurrences of "N/A" for active layers.
    *   layers with sufficient data show "OK" or "HEALTHY".

### T-DASH-04: Market Proxy Sets UI Integration
- [x] **Status:** COMPLETED
*   **Description:** Update `MarketSnapshot` component to explicitly label the Proxy and Source being used, per DWS Section 3.
*   **Inputs:** `data_provenance_{market}.json`, `MarketSnapshot.jsx`
*   **Outputs:** UI labels showing "Proxy: S&P 500 (SPY.csv)".
*   **Acceptance Criteria:**
    *   US View shows "Proxy: S&P 500".
    *   India View shows "Proxy: Nifty 50 (Reliance Proxy)".
    *   Source file is visible on hover/tooltip.

---

## P1 — Transparency & Trust (The Explanation)

### T-DASH-05: Data Usage Declaration Per Layer
- [x] **Status:** COMPLETED
*   **Description:** Add "Info/Help" icons to each major panel (Momentum, Macro, Liquidity) detailing exactly which data lines feed it.
*   **Inputs:** `factor_context.json` (inputs_used field)
*   **Outputs:** Tooltips on panel headers.
*   **Acceptance Criteria:**
    *   Hovering "Momentum" header shows "Driven by: SPY Close Price (SMA50)".

### T-DASH-06: Macro Scope Labeling
- [x] **Status:** COMPLETED
*   **Description:** Tag all macro indicators with `[US]`, `[IN]`, or `[GL]`.
*   **Inputs:** `MacroContextPanel.jsx`
*   **Outputs:** Visual tags or icons next to VIX, Yields, etc.
*   **Acceptance Criteria:**
    *   Differentiation between US VIX and India VIX is visually obvious.

### T-DASH-07: Tick Duration & Timestamp Explanation
- [x] **Status:** COMPLETED
*   **Description:** Explain what "TICK" means in the UI (e.g., "Daily Close", "Intraday 5min").
*   **Inputs:** `truth_epoch.json` (or system config)
*   **Outputs:** Subtext in global header.
*   **Acceptance Criteria:**
    *   Header displays "Resolution: DAILY (End of Day)".

---

## P2 — Strategy & Capital Coherence (The Narrative)

### T-DASH-08: Resolve "Calculating" States
- [x] **Status:** COMPLETED
*   **Description:** Ensure strategy cards never get stuck in "Calculating...". If the backend returns valid data, show it. If processed, show result.
*   **Inputs:** `StrategyMatrix.jsx`
*   **Outputs:** Robust state handling for strategy cards.
*   **Acceptance Criteria:**
    *   Strategies are either ELIGIBLE, REJECTED, or INACTIVE.
    *   No infinite spinners.

### T-DASH-09: Enrich Strategy Stories
- [x] **Status:** COMPLETED
*   **Description:** Display the *reason* for rejection/acceptance clearly in the card footer.
*   **Inputs:** `strategy_eligibility.json`
*   **Outputs:** Text description in `StrategyMatrix` cards.
*   **Acceptance Criteria:**
    *   "Rejected: Low Volatility" is visible without clicking 3 levels deep.

### T-DASH-10: Capital Readiness Market Aware
- [x] **Status:** COMPLETED
*   **Description:** Ensure Capital panels explicitly state they are evaluating readiness for the *selected market*.
*   **Inputs:** `CapitalReadinessPanel.jsx`
*   **Outputs:** Header update "Capital Readiness (US)".
*   **Acceptance Criteria:**
    *   Switching markets updates capital readiness context or shows "Shared Pool".

---

## P3 — Validation & Governance (The Seal)

### T-DASH-11: Completeness Checklist Verification
- [x] **Status:** COMPLETED
*   **Description:** Perform a manual audit against the Completeness Checklist.
*   **Inputs:** `dashboard_completeness_checklist.md`, Running Dashboard
*   **Outputs:** Completed/Checked Markdown file.
*   **Acceptance Criteria:**
    *   All items checked off.
    *   Screenshots (optional) proving state.

