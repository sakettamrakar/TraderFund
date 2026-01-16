# Market Regime Engine — Runbook

## 1. Purpose
This runbook defines how to operate, monitor, and troubleshoot the Market Regime Engine in production.
The Regime Engine is a decision-gating system, not a trading strategy. Its failure mode must always default to **NO TRADE / RISK-OFF**.

## 2. Normal Operating Modes

### 2.1 Modes

| Mode | Description | Impact |
| :--- | :--- | :--- |
| **OFF** | Regime engine disabled | Strategies run **unguarded** (Legacy Behavior) |
| **SHADOW** | Regime runs, no enforcement | Logging only; Signals executed normally |
| **ENFORCED** | Regime gates strategies | **Live risk control**; Signals blocked/throttled |

**Rule:** All new changes MUST run in `SHADOW` before `ENFORCED`.

## 3. Daily Startup Checklist (Pre-Market)

1.  [ ] **Verify System Clock:** Ensure time and timezone are correct (critical for event windows).
2.  [ ] **Verify Market Calendar:** Ensure events/holidays are loaded.
3.  [ ] **Verify Data Feeds:**
    *   OHLCV Data (Live)
    *   Volume Data
    *   Event Calendar
4.  [ ] **Verify Regime Engine Startup:** Run `warm-up`.
5.  [ ] **Verify Dashboard:** Confirm valid regime output.
6.  [ ] **Confirm Risk-On:** Ensure state is NOT `UNDEFINED` at open (after warm-up).

## 4. Intraday Monitoring

**Watch the Dashboard:**
*   **Regime State:** Is it updating?
*   **Confidence:** Is it stable?
*   **Cooldown:** Is it active/stuck?
*   **Blocked Strategies:** Are blocks reasonable?

**Red Flags (Immediate Attention):**

| Symptom | Action |
| :--- | :--- |
| Rapid regime flipping | Switch to **SHADOW** |
| Prolonged `UNDEFINED` | Check data feed latency/integrity |
| `EVENT_LOCK` stuck | Check calendar source / clock |
| Confidence always low | Investigate providers (ADX/ATR) |

## 5. End-of-Day Checklist

1.  [ ] **Verify Logs:** Ensure `regime_shadow.jsonl` exists and is populated.
2.  [ ] **Run Regret Analysis:** Execute Phase 10 analytics.
3.  [ ] **Record Metrics:**
    *   Block Rate (%)
    *   Net Regret Score
4.  [ ] **Backup:** Archive logs.

## 6. Failure Modes & Actions

### 6.1 Data Missing / Corrupt
*   **Expected Behavior:** Fail Safe -> **BLOCK** (or `UNDEFINED`).
*   **Action:** Do nothing immediately. Fix data source. Resume.

### 6.2 Regime Engine Crash
*   **Action:**
    1.  Switch to `OFF` (if trading must continue) or `SHADOW`.
    2.  Restart wrapper.
    3.  Verify dashboard.
    4.  Re-enable `ENFORCED` only after stability.

### 6.3 Unexpected Over-Blocking
*   **Action:**
    1.  Do **NOT** change thresholds live.
    2.  Analyze via Regret Analysis.
    3.  Adjust config post-market -> `SHADOW` test.

## 7. Change Management Rules
*   **No live code changes.**
*   Config changes -> `SHADOW` first.
*   Regime logic changes -> Forbidden without Spec revision (Phases 0-5 Frozen).

## 8. Emergency Kill Switch
To restore legacy trading behavior instantly:

```bash
set REGIME_MODE=OFF
```

## 9. Wrapper Architecture
We do not run the Regime Engine directly. A thin wrapper handles modes and safety.

### 9.1 Responsibilities
*   Load Config / Env Vars.
*   Set Mode (`OFF`/`SHADOW`/`ENFORCED`).
*   Start `ShadowRegimeRunner` (Telemetry).
*   Handle Warm-up.
*   Catch Crashes.

### 9.2 Architecture
*   **Entry Point:** `traderfund/run_regime.py`
*   **Strategies:** Independently check `REGIME_MODE` and consult `RegimeGuard`.

## 10. Scheduling (Windows Task Scheduler)

### 1. Pre-Market Warm-Up
*   **Time:** 30 min before market open.
*   **Command:** `python -m traderfund.run_regime --mode SHADOW`

### 2. Market Hours
*   **Trigger:** Market Open.
*   **Command:** `python -m traderfund.run_regime --mode ENFORCED`

### 3. Post-Market Analytics
*   **Time:** After market close (+15 min).
*   **Command:** `python -m traderfund.run_regime --mode ANALYTICS`
