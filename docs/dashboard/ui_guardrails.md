# Dashboard UI Guardrails

## 1. Purpose
This document defines the **hard constraints** and **soft constraints** that govern dashboard UI behavior.
These guardrails ensure the dashboard remains an **epistemic observatory**, not an **execution terminal**.

---

## 2. Hard Constraints (INVIOLABLE)

These rules can NEVER be violated. Any violation requires immediate rollback.

| ID | Guardrail | Rationale |
| :--- | :--- | :--- |
| `HG-001` | No execution buttons or forms | `INV-NO-EXECUTION` |
| `HG-002` | No position size display or input | `INV-NO-CAPITAL` |
| `HG-003` | No auto-trade or auto-alert toggles | `INV-NO-SELF-ACTIVATION` |
| `HG-004` | No recommendation language ("Buy", "Sell", "Should") | Observatory principle |
| `HG-005` | No portfolio value or PnL display | No capital implication |
| `HG-006` | No cross-market data mixing | Market isolation |
| `HG-007` | No synthetic data displayed as real | `REAL_ONLY` invariant |
| `HG-008` | All data must show provenance timestamp | `OBL-DATA-PROVENANCE-VISIBLE` |
| `HG-009` | Regime must be disclosed on all derived displays | `OBL-REGIME-GATE-EXPLICIT` |
| `HG-010` | Degraded states must be more visible, not less | `OBL-HONEST-STAGNATION` |

---

## 3. Soft Constraints (GUIDELINES)

These rules should be followed but may be relaxed with explicit justification.

| ID | Guardrail | Justification for Relaxation |
| :--- | :--- | :--- |
| `SG-001` | Prefer text over icons for status | Icons are faster to parse |
| `SG-002` | Avoid animations for data changes | Subtle pulse for transitions is acceptable |
| `SG-003` | Display at most 10 signals at once | Pagination with "show more" is acceptable |
| `SG-004` | Use monospace fonts for data values | Proportional fonts for labels are acceptable |
| `SG-005` | Dark mode by default | Light mode toggle is acceptable |

---

## 4. Color Semantics (STRICT)

Colors must communicate state consistently across all surfaces.

| Color | Meaning | Usage |
| :--- | :--- | :--- |
| **Green** | Healthy, Allowed, Active | Policy ACTIVE, permissions granted |
| **Yellow/Amber** | Caution, Elevated, Conditional | ELEVATED_STRESS, RESTRICTED policy |
| **Red** | Danger, Blocked, Critical | SYSTEMIC_STRESS, HALTED policy, DEGRADED |
| **Gray** | Unknown, Not Evaluated, Offline | NOT_EVALUATED, OFFLINE |
| **Blue** | Neutral, Informational | NEUTRAL regime, general info |
| **Purple** | Transition, Uncertainty | TRANSITION_UNCERTAIN |

### 4.1. Forbidden Color Usage
*   ❌ Green for DEGRADED or UNKNOWN states
*   ❌ Muted colors for critical warnings
*   ❌ Same color for permission and block

---

## 5. Interaction Guardrails

### 5.1. Allowed Interactions
*   ✅ Refresh data (re-fetch from backend)
*   ✅ Switch market (US ↔ INDIA)
*   ✅ Expand/collapse panels
*   ✅ Copy data to clipboard (for audit)
*   ✅ View historical context
*   ✅ Hover for details

### 5.2. Prohibited Interactions
*   ❌ Submit forms that modify state
*   ❌ Toggle execution modes
*   ❌ Subscribe to alerts
*   ❌ Connect to broker APIs
*   ❌ Input position sizes or prices

---

## 6. Text Content Guardrails

### 6.1. Allowed Language
| Pattern | Example |
| :--- | :--- |
| "Permission to..." | "Permission to hold positions under current regime" |
| "Allowed by policy" | "ALLOW_LONG_ENTRY is allowed by policy" |
| "Blocked due to..." | "Blocked due to SYSTEMIC_STRESS" |
| "Current state is..." | "Current regime state is NEUTRAL" |
| "Computed at..." | "Computed at 2026-01-30 05:23:43" |

### 6.2. Prohibited Language
| Pattern | Reason |
| :--- | :--- |
| "You should..." | Implies recommendation |
| "Buy/Sell..." | Implies action |
| "Opportunity..." | Implies forecast |
| "Profit/Loss..." | Implies capital |
| "Target price..." | Implies forecast |
| "Expected return..." | Implies forecast |

---

## 7. Error States and Fallbacks

### 7.1. Backend Unavailable
Display: "Unable to connect to data layer. Showing last known state."
Action: Gray out all derived displays, show staleness prominently.

### 7.2. Artifact Missing
Display: "Policy artifact not found. System OFFLINE."
Action: Show OFFLINE badge, prevent any actionable interpretation.

### 7.3. Parse Error
Display: "Data format error. Contact system administrator."
Action: Log error, show generic error card, never guess at data.

---

## 8. Audit Requirements
Every UI component must support:
1.  **Logging**: Record when displayed and what data was shown.
2.  **Snapshot**: Ability to export current view as JSON.
3.  **Traceability**: Link displayed values to artifact paths.
