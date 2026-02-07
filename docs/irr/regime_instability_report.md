# Integration Reality Run — Regime Instability Report

## 1. Purpose
This report documents regime edge cases, transitions, and instability patterns detected during the IRR.

---

## 2. Current Regime States

| Market | Regime Code | Regime Label | Computed At | Confidence |
| :--- | :--- | :--- | :--- | :--- |
| US | BEARISH | Bearish Trend | 2026-01-30 04:45 | 0.8 |
| INDIA | NEUTRAL | Range-Bound / Mixed | 2026-01-30 05:23 | 0.8 |

---

## 3. Regime Transition History (Last 7 Days)

### 3.1. US Market

| Date | From | To | Trigger |
| :--- | :--- | :--- | :--- |
| 2026-01-25 | NEUTRAL | BEARISH | SPY < SMA50 < SMA200 |
| (No other transitions detected) | | | |

### 3.2. India Market

| Date | From | To | Trigger |
| :--- | :--- | :--- | :--- |
| 2026-01-28 | BULLISH | NEUTRAL | NIFTY crossed below SMA50 |
| (No other transitions detected) | | | |

---

## 4. Instability Indicators

### 4.1. Proximity to Gate
How close is the current price to triggering a regime change?

| Market | Current State | Nearest Boundary | Distance | Risk Level |
| :--- | :--- | :--- | :--- | :--- |
| US | BEARISH | SMA50 | -3.2% | LOW |
| INDIA | NEUTRAL | SMA50/SMA200 cross | 1.1% | MEDIUM |

**Interpretation**: India is closer to a potential regime flip than US.

### 4.2. Whipsaw Risk
Has the market recently oscillated between regimes?

| Market | Flips in Last 30 Days | Whipsaw Risk |
| :--- | :--- | :--- |
| US | 1 | LOW |
| INDIA | 1 | MEDIUM |

---

## 5. Regime-Related Governance Impact

### 5.1. Permissions Affected by Regime

| Market | Regime | Permissions Granted | Permissions Blocked |
| :--- | :--- | :--- | :--- |
| US | BEARISH | SHORT, HOLD | LONG |
| INDIA | NEUTRAL | HOLD, REBALANCE | LONG, SHORT |

### 5.2. Regime Uncertainty Propagation
If regime were to flip:

| Scenario | New Regime | Permission Change |
| :--- | :--- | :--- |
| US BEARISH → NEUTRAL | NEUTRAL | SHORT blocked, only HOLD |
| INDIA NEUTRAL → BULLISH | BULLISH | LONG permitted |
| INDIA NEUTRAL → BEARISH | BEARISH | SHORT permitted |

---

## 6. Recommendations

| Issue | Recommendation |
| :--- | :--- |
| India near regime boundary | Monitor NIFTY vs SMA50 daily |
| US VIX anomaly | Verify VIX data freshness |
| No TRANSITION_UNCERTAIN handling | Implement transition cooldown logic |

---

## 7. Stability Assessment

| Market | Stability Rating | Notes |
| :--- | :--- | :--- |
| US | STABLE | Clear bearish trend, no imminent flip |
| INDIA | MODERATE | Near boundary, flip possible |
