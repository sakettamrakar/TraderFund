# Dashboard Regime Visibility Rules

## 1. Purpose
This document specifies how each regime state (BULLISH, BEARISH, NEUTRAL, UNKNOWN) affects the visibility, emphasis, and behavior of dashboard surfaces.

---

## 2. Core Principle
> The regime determines what the operator **should pay attention to**, not what they **should do**.

---

## 3. Visibility Rules by Regime

### 3.1. BULLISH Regime

| Surface | Visibility | Emphasis | Notes |
| :--- | :--- | :--- | :--- |
| Long Permissions | ✅ Visible | High | Green highlight |
| Short Permissions | ✅ Visible | Low | Muted, gray text |
| Hold Permissions | ✅ Visible | Normal | — |
| Entry Signals | ✅ Visible | High | If any exist |
| Exit Signals | ✅ Visible | Low | Muted |
| Risk Warnings | ✅ Visible | Low | Minimal display |

**UI Accent**: Green / Positive

### 3.2. BEARISH Regime

| Surface | Visibility | Emphasis | Notes |
| :--- | :--- | :--- | :--- |
| Long Permissions | ✅ Visible | Low | Muted, "Regime Discouraged" tag |
| Short Permissions | ✅ Visible | High | Yellow highlight |
| Hold Permissions | ✅ Visible | Normal | — |
| Entry Signals | ⚠️ Conditional | Medium | Only short-biased shown prominently |
| Exit Signals | ✅ Visible | High | Emphasize exit opportunities |
| Risk Warnings | ✅ Visible | High | Amber/Yellow banners |

**UI Accent**: Yellow / Caution

### 3.3. NEUTRAL Regime

| Surface | Visibility | Emphasis | Notes |
| :--- | :--- | :--- | :--- |
| Long Permissions | ⚠️ Hidden | — | Not granted in NEUTRAL |
| Short Permissions | ⚠️ Hidden | — | Not granted in NEUTRAL |
| Hold Permissions | ✅ Visible | High | Primary action |
| Rebalance Permissions | ✅ Visible | High | Secondary action |
| Entry Signals | ❌ Suppressed | — | "No new entries in NEUTRAL regime" |
| Exit Signals | ⚠️ Conditional | Low | Only if positions exist |
| Risk Warnings | ✅ Visible | Medium | "Range-bound conditions" note |

**UI Accent**: Blue / Neutral

### 3.4. UNKNOWN Regime

| Surface | Visibility | Emphasis | Notes |
| :--- | :--- | :--- | :--- |
| All Permissions | ❌ Suppressed | — | Only OBSERVE_ONLY shown |
| Entry Signals | ❌ Suppressed | — | "System Halted" |
| Exit Signals | ❌ Suppressed | — | No actionable data |
| Risk Warnings | ✅ Visible | Maximum | Red alert, full-width banner |
| Diagnostic Info | ✅ Visible | High | Why is regime unknown? |

**UI Accent**: Red / Alert

---

## 4. Regime Transition Rules

### 4.1. On Transition Detected
1.  Display a **Transition Alert** banner.
2.  Mark all signals computed under old regime as `STALE`.
3.  Show "Recalculating..." until new artifacts are available.
4.  Do NOT auto-dismiss the alert — require acknowledgment or timeout (5 min).

### 4.2. Transition Alert Content
```
⚠️ REGIME TRANSITION
[Old Regime] → [New Regime]
Permissions and signals may have changed.
Last computed: [timestamp]
```

### 4.3. Transition Emphasis by Type

| Transition | Severity | Display |
| :--- | :--- | :--- |
| BULLISH → BEARISH | High | Red banner, 3 beeps (audio optional) |
| BEARISH → BULLISH | High | Green banner |
| NEUTRAL → BULLISH/BEARISH | Medium | Yellow banner |
| Any → UNKNOWN | Critical | Full-screen overlay |
| UNKNOWN → Any | Info | Blue banner, "Regime Restored" |

---

## 5. Regime Disclosure Requirements
Every surface that displays derived data MUST include:
*   The regime under which it was computed.
*   The timestamp of computation.
*   A staleness indicator if applicable.

**Example Footer**:
```
Computed under NEUTRAL regime | 2026-01-30 05:23:43 IST
```
