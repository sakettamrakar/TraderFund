# Dashboard Staleness and Honesty Checks

## 1. Purpose
This document defines the mechanisms for detecting and displaying data staleness, uncertainty, and honest stagnation.
The dashboard must **never hide bad news** — it must make stale or degraded states more visible, not less.

---

## 2. Staleness Detection Rules

### 2.1. Data Staleness
| Data Type | Stale Threshold | Action |
| :--- | :--- | :--- |
| Daily Price Data | > 2 trading days old | Yellow warning banner |
| Real-time Tick | > 20 minutes old | Red alert banner |
| Factor Context | > 24 hours old | "Recalculation Needed" badge |
| Decision Policy | > 24 hours old | "Policy may be outdated" warning |
| Fragility Context | > 24 hours old | "Stress assessment pending" |

### 2.2. Staleness Display
```
⚠️ DATA STALE: Last update was 48 hours ago.
Factor and Policy outputs may not reflect current market conditions.
```

---

## 3. Honest Stagnation Policy

### 3.1. Definition
**Honest Stagnation** means acknowledging when the system cannot proceed due to missing inputs, rather than fabricating or inferring.

### 3.2. Stagnation Triggers
*   Missing proxy data (e.g., IN10Y not ingested)
*   Parity status = DEGRADED
*   Regime = UNKNOWN
*   Factor sufficiency = false

### 3.3. Stagnation Display
When stagnation is detected, the dashboard MUST show:
```
SYSTEM STAGNATION: Cannot proceed due to missing canonical data.
Reason: [Explicit reason from parity/factor artifact]
This is intentional governance, not an error.
```

---

## 4. Uncertainty Disclosure

### 4.1. Confidence Levels
| Confidence | Display |
| :--- | :--- |
| > 0.8 | Green checkmark, "High Confidence" |
| 0.5 - 0.8 | Yellow dot, "Moderate Confidence" |
| < 0.5 | Red warning, "Low Confidence — Exercise Caution" |

### 4.2. Unknown States
If any factor is marked `unknown` or `null`, display:
```
⚡ INCOMPLETE DATA: [Factor Name] could not be computed.
```

---

## 5. Degraded State Emphasis

### 5.1. Visual Treatment
Degraded states (DEGRADED proxy, SYSTEMIC_STRESS, HALTED policy) must be:
*   **Larger** than normal states
*   **Brighter** (not muted)
*   **Persistent** (cannot be dismissed)

### 5.2. Example: India DEGRADED
```
╔═══════════════════════════════════════════════════════════════╗
║  ⛔ INDIA MARKET: DEGRADED STATE                              ║
║                                                               ║
║  Reason: Single-stock surrogate (RELIANCE) insufficient.     ║
║  Action Required: Ingest canonical proxies (NIFTY50, etc.)   ║
║                                                               ║
║  Permissions: OBSERVE_ONLY                                    ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## 6. Implementation Checklist

| Check | Description | Component |
| :--- | :--- | :--- |
| ☐ | Display `computed_at` on all cards | All Policy/Factor cards |
| ☐ | Compare `computed_at` vs current time | SystemStatus |
| ☐ | Show staleness alert if threshold exceeded | SystemStatus |
| ☐ | Never hide DEGRADED/HALTED states | PolicyStateCard |
| ☐ | Display confidence for each factor | FactorCard (future) |
| ☐ | Show explicit reason for any blocked action | FragilityCard |

---

## 7. Anti-Patterns (FORBIDDEN)

*   ❌ Hiding DEGRADED markets behind a toggle
*   ❌ Using green color for uncertain/low-confidence data
*   ❌ Auto-dismissing staleness warnings
*   ❌ Showing "No Issues" when data is missing
*   ❌ Displaying stale data as current
