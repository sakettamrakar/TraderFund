# Narrative Regime Gating Rules

## 1. Purpose
This document specifies how the **regime context** gates the narrative output.
The narrative must always reflect the current regime, and must change when the regime changes.

---

## 2. Core Rule
> **Every narrative sentence must be valid under the current regime.**

A sentence that is true in a BULLISH regime may be misleading in a BEARISH regime.
The compiler must check regime compatibility before emitting any statement.

---

## 3. Regime-Specific Narrative Templates

### 3.1. BULLISH Regime Narrative

**Emphasis**: Trend continuation, long-side permissions.

```
## Summary
The market is in a BULLISH regime. Long-side permissions are active.

## Regime
The current regime is **BULLISH**, indicating sustained upward momentum.
This assessment is based on {benchmark} trading above key moving averages.

## Policy
Long entry is **permitted** under current conditions.
Short entry may be permitted but is **regime-discouraged**.
```

### 3.2. BEARISH Regime Narrative

**Emphasis**: Defensive posture, short-side or exit focus.

```
## Summary
The market is in a BEARISH regime. Defensive permissions are emphasized.

## Regime
The current regime is **BEARISH**, indicating sustained downward pressure.
This assessment is based on {benchmark} trading below key moving averages.

## Policy
Short entry may be **permitted** under current conditions.
Long entry is **regime-discouraged**.
```

### 3.3. NEUTRAL Regime Narrative

**Emphasis**: Range-bound conditions, no directional bias.

```
## Summary
The market is in a NEUTRAL regime. No directional entries are permitted.

## Regime
The current regime is **NEUTRAL**, indicating range-bound or mixed conditions.
Neither bulls nor bears have established clear control.

## Policy
Hold and rebalance actions are **permitted**.
New directional entries are **not permitted** under NEUTRAL regime.
```

### 3.4. UNKNOWN Regime Narrative

**Emphasis**: System halt, uncertainty surfaced.

```
## Summary
The regime could not be determined. System is in HALTED state.

## Regime
The current regime is **UNKNOWN**. Insufficient data or conflicting signals.
No policy evaluation is possible under this state.

## Policy
All permissions are **suspended**.
Only OBSERVE_ONLY is authorized.
```

---

## 4. Regime Transition Narrative

When a regime transition is detected, the narrative must include:

```
## Transition Alert
Regime has changed from {old_regime} to {new_regime}.
Policy permissions computed under the old regime may no longer be valid.
Recalculation is recommended.
```

---

## 5. Regime Gating Checks

### 5.1. Pre-Emission Checks
Before emitting any sentence, the compiler checks:

1.  **Regime Compatibility**: Is this sentence valid for current regime?
2.  **Staleness Check**: Was the regime computed recently enough?
3.  **Transition Check**: Has the regime changed since last narrative?

### 5.2. Rejection Criteria
A sentence is rejected if:
*   It implies BULLISH sentiment when regime is BEARISH (or vice versa).
*   It grants permissions that are blocked under current regime.
*   It references a regime state that is not the current state.

---

## 6. Cross-Regime Statement Handling

Some statements are regime-agnostic and can appear in any narrative:

*   Provenance timestamps
*   Factor values (without interpretation)
*   Parity status
*   Staleness warnings

Example:
```
"Volatility level: 25.4."  ← Regime-agnostic
"Volatility suggests caution." ← Regime-dependent (ALLOWED only in BEARISH/NEUTRAL)
```

---

## 7. Market Isolation
*   US regime MUST NOT appear in India narrative.
*   India regime MUST NOT appear in US narrative.
*   Cross-market comparisons are prohibited in narratives.
