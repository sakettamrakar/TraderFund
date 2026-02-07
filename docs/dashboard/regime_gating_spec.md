# Dashboard Regime Gating Specification

## 1. Purpose
This specification defines how dashboard displays are **gated** by regime state.
No signal, permission, or recommendation should be shown without explicit regime context.

---

## 2. Regime Gate Principle
> "The Regime is the Master Clock."

Every displayed element must declare:
1.  **Under what regime was this computed?**
2.  **Is this regime still valid?**
3.  **What changes if the regime flips?**

---

## 3. Regime States and UI Behavior

### 3.1. BULLISH Regime
| UI Element | Behavior |
| :--- | :--- |
| Policy Card | Green accent, "ACTIVE" badge |
| Long permissions | Displayed prominently |
| Short permissions | May be hidden or grayed |
| Risk warnings | Minimal |

### 3.2. BEARISH Regime
| UI Element | Behavior |
| :--- | :--- |
| Policy Card | Yellow/Orange accent, "ACTIVE" badge |
| Short permissions | Displayed prominently |
| Long permissions | Grayed with "Regime Discouraged" tag |
| Risk warnings | Elevated |

### 3.3. NEUTRAL Regime
| UI Element | Behavior |
| :--- | :--- |
| Policy Card | Blue/Gray accent, "ACTIVE" badge |
| Hold/Rebalance permissions | Displayed |
| Entry permissions | Hidden |
| Risk warnings | "Range-bound conditions" message |

### 3.4. UNKNOWN Regime
| UI Element | Behavior |
| :--- | :--- |
| Policy Card | Red accent, "HALTED" badge |
| All permissions | Hidden or grayed |
| Risk warnings | "Regime Unknown — System Halted" |
| Action | No actionable data displayed |

---

## 4. Regime Transition Handling

### 4.1. Transition Detection
*   Compare current `regime_context.regime_code` with previous.
*   If changed, display a **Transition Alert** banner.

### 4.2. Transition Alert Content
```
⚠️ REGIME TRANSITION DETECTED
Previous: BULLISH → Current: NEUTRAL
Policy permissions may have changed. Review before any action.
```

### 4.3. Transition Cooldown
*   After a regime flip, signals computed under the old regime are marked `STALE`.
*   Dashboard displays "Recalculating..." until new artifacts are generated.

---

## 5. Regime Disclosure on All Cards

Every dashboard card must display its regime context:
```
Computed under: NEUTRAL regime | 2026-01-30 05:23:43
```

This ensures the operator knows the context under which the displayed data was derived.

---

## 6. Cross-Market Regime Isolation
*   US regime MUST NOT influence India display.
*   India regime MUST NOT influence US display.
*   If switching markets, the entire UI reloads with the new market's regime context.
