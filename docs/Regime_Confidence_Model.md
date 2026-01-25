# Regime Confidence Model

> **CHANGELOG**  
> - 2026-01-16: Created from live implementation  
> - Source: `traderfund/regime/narrative_adapter.py`, Dashboard v1.1

---

## What is Confidence?

Confidence is **NOT** a measure of opportunity. It is a measure of **signal quality**.

> High confidence ≠ High opportunity  
> High confidence = High certainty about the current state

---

## Three Components

### 1. Confluence

**What it measures:** Agreement between indicators

**High Confluence (1.0):**
- All sub-models agree on the state
- Example: ADX, ATR, and volume all say "trending"

**Low Confluence (0.3):**
- Indicators disagree
- Example: ADX says trending, ATR says low vol

**Implication:** Low confluence = UNDEFINED or reduced confidence

---

### 2. Persistence

**What it measures:** Temporal stability

**High Persistence (1.0):**
- Regime has been stable for multiple cycles
- No recent transitions or near-transitions

**Low Persistence (0.3):**
- Regime is new or just transitioned
- May still be forming

**Implication:** Low persistence = wait for confirmation

---

### 3. Intensity

**What it measures:** Signal magnitude / force

**This is where traders get confused.**

| Regime Type | Expected Intensity |
|-------------|-------------------|
| TRENDING_HIGH_VOL | 0.80 - 1.00 |
| TRENDING_NORMAL_VOL | 0.60 - 0.80 |
| MEAN_REVERTING_HIGH_VOL | 0.50 - 0.70 |
| **MEAN_REVERTING_LOW_VOL** | **0.30 - 0.50** |

**Key insight:**  
In a `MEAN_REVERTING_LOW_VOL` regime, low intensity is **correct and expected**.

> Seeing Intensity = 0.35 in a low-vol regime is **not a bug**.  
> It would be a bug if Intensity = 1.0 in a low-vol regime.

---

## Live Example (US Market, 2026-01-16)

```
REGIME : MEAN_REVERTING_LOW_VOL
BIAS   : NEUTRAL

CONFIDENCE (Total: 0.78)
- Confluence  : [##########] 1.00 (All indices aligned)
- Persistence : [##########] 1.00 (Stable for 9 cycles)
- Intensity   : [###-------] 0.35 (Low vol = low force)
```

**Interpretation:**
- We are **highly confident** this is a mean-reverting regime
- The low intensity is **consistent with** low volatility
- This is a **valid, actionable** regime classification

---

## Common Misinterpretations

| What you see | Wrong interpretation | Correct interpretation |
|--------------|---------------------|------------------------|
| Intensity = 0.35 | "Weak signal, don't trust" | "Low vol regime, intensity is correctly low" |
| Total = 0.78 | "Not confident enough" | "Very confident, intensity just reflects vol level" |
| Intensity = 1.0 in LOW_VOL | N/A | **BUG** — intensity should be low |

---

## What NOT To Do

- ❌ Do NOT interpret low intensity as "regime is wrong"
- ❌ Do NOT override regime because confidence "looks low"
- ❌ Do NOT expect 1.0 confidence in all components
- ❌ Do NOT treat confidence as opportunity signal

---

## Document Status

**STATUS: FROZEN**

This model matches Dashboard v1.1 and `RegimeNarrativeAdapter`.
