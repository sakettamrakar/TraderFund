# Dashboard Allowed vs. Blocked Matrix

## 1. Purpose
This matrix defines what dashboard elements are **ALLOWED**, **CONDITIONALLY ALLOWED**, or **BLOCKED** under various system states.

---

## 2. Legend
*   ✅ **ALLOWED**: Always visible, no restrictions.
*   ⚠️ **CONDITIONAL**: Visible only when specific conditions are met.
*   ❌ **BLOCKED**: Never visible, prohibited by invariant.

---

## 3. Surface Visibility by System State

### 3.1. By Policy State

| Surface | ACTIVE | RESTRICTED | HALTED | OFFLINE |
| :--- | :--- | :--- | :--- | :--- |
| PolicyStateCard | ✅ | ✅ | ✅ | ✅ (shows OFFLINE) |
| FragilityStateCard | ✅ | ✅ | ✅ | ⚠️ (shows stale) |
| IntelligencePanel | ✅ | ⚠️ (muted) | ❌ | ❌ |
| SignalCards | ✅ | ⚠️ (grayed) | ❌ | ❌ |
| FactorSummary | ✅ | ✅ | ⚠️ | ❌ |

### 3.2. By Stress State

| Surface | NORMAL | ELEVATED | SYSTEMIC | NOT_EVALUATED |
| :--- | :--- | :--- | :--- | :--- |
| FragilityStateCard | ✅ (green) | ✅ (yellow) | ✅ (red) | ✅ (gray) |
| IntelligencePanel | ✅ | ⚠️ | ❌ | ❌ |
| Entry Permissions | ✅ | ⚠️ | ❌ | ❌ |
| Hold Permissions | ✅ | ✅ | ✅ | ⚠️ |

### 3.3. By Parity Status

| Surface | CANONICAL | DEGRADED | UNKNOWN |
| :--- | :--- | :--- | :--- |
| PolicyStateCard | ✅ (dynamic) | ⚠️ (forced OBSERVE) | ❌ |
| FragilityStateCard | ✅ | ⚠️ (NOT_EVALUATED) | ❌ |
| FactorSummary | ✅ | ⚠️ (partial) | ❌ |
| ParityStatusCard | ⚠️ (minimal) | ✅ (prominent) | ✅ (error) |

---

## 4. Action Element Visibility

| Element | Allowed? | Condition |
| :--- | :--- | :--- |
| Market Selector (US/INDIA) | ✅ | Always |
| Refresh Button | ✅ | Refreshes data, no side effects |
| Collapse/Expand Panel | ✅ | UI convenience |
| Copy to Clipboard | ✅ | For audit purposes |
| Export JSON | ⚠️ | Only for read-only artifacts |
| Buy/Sell Button | ❌ | **PROHIBITED** |
| Position Entry Form | ❌ | **PROHIBITED** |
| Alert Toggle | ❌ | **PROHIBITED** |
| Auto-Execute Switch | ❌ | **PROHIBITED** |

---

## 5. Data Display Permissions

| Data Type | Display Allowed? | Condition |
| :--- | :--- | :--- |
| Historical Prices | ✅ | Always |
| Computed Factors | ✅ | With staleness indicator |
| Regime Labels | ✅ | With timestamp |
| Policy Permissions | ✅ | Read-only |
| Signal List | ⚠️ | Only if regime is not UNKNOWN |
| Recommendations | ❌ | **PROHIBITED** |
| Price Targets | ❌ | **PROHIBITED** |
| Position Sizes | ❌ | **PROHIBITED** |
| Expected Returns | ❌ | **PROHIBITED** |

---

## 6. Language Permissions

| Language | Allowed? | Example |
| :--- | :--- | :--- |
| "Permission to..." | ✅ | "Permission to hold positions" |
| "Allowed to..." | ✅ | "Allowed: ALLOW_POSITION_HOLD" |
| "Blocked due to..." | ✅ | "Blocked due to SYSTEMIC_STRESS" |
| "You should..." | ❌ | Implies recommendation |
| "Buy now..." | ❌ | Implies action |
| "Profit potential..." | ❌ | Implies forecast |
| "Opportunity..." | ❌ | Implies recommendation |
