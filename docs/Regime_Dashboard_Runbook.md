# Regime Dashboard Runbook (Operator Guide)

> **CHANGELOG**  
> - 2026-01-16: Created for Dashboard v1.1 (Decision-Complete)  
> - This is a **human decision guide**, not a developer doc

---

## Purpose

This runbook explains how to **read and act on** the Regime Operations Dashboard.

---

## Dashboard Panels Explained

### 1. STATUS

```
STATUS: ACTIVE
Last Run: 23:16:45 | Cycles Today: 3
```

| Value | Meaning | Action |
|-------|---------|--------|
| ACTIVE | Runner is healthy | None |
| LATE | Runner delayed | Monitor |
| STALE | Runner not updating | **Do not trust regime** |

---

### 2. MODULE HEALTH

```
MODULE HEALTH
- API Key Pool        : OK
- Data Ingestion      : OK
- History Store       : OK
```

| Icon | Meaning |
|------|---------|
| OK | Module healthy |
| X | Module unhealthy |

**Rule:** If any module shows X, regime may be unreliable.

---

### 3. REGIME STATE

```
REGIME : MEAN_REVERTING_LOW_VOL
BIAS   : NEUTRAL
DRIVERS: SPY, QQQ, IWM, VIXY
```

- **REGIME:** Current behavioral state
- **BIAS:** Directional overlay (BULLISH/BEARISH/NEUTRAL)
- **DRIVERS:** Which symbols contributed to this classification

---

### 4. STABILITY vs MATURITY

```
STABILITY
- Status   : STABLE
- Maturity : INITIALIZING
- Cooldown : OFF
```

| Field | What it means |
|-------|---------------|
| Status = STABLE | Regime is not actively transitioning |
| Status = UNSTABLE | Regime may change soon |
| Maturity = INITIALIZING | Regime is new (< 10 cycles) |
| Maturity = NEW | 10-30 cycles |
| Maturity = DEVELOPING | 30-100 cycles |
| Maturity = MATURE | > 100 cycles |
| Cooldown = ON | Transition lock active |

**Guidance:**
- INITIALIZING = wait for confirmation
- MATURE = higher conviction

---

### 5. CONFIDENCE

```
CONFIDENCE (Total: 0.78)
- Confluence  : [##########] 1.00
- Persistence : [##########] 1.00
- Intensity   : [###-------] 0.35
```

| Component | Meaning |
|-----------|---------|
| Confluence | Indicator agreement |
| Persistence | Temporal stability |
| Intensity | Signal force/magnitude |

**Critical:** Low intensity in LOW_VOL regimes is **correct**.

See [Regime_Confidence_Model.md](Regime_Confidence_Model.md) for details.

---

### 6. ENFORCEMENT STATUS

```
ENFORCEMENT STATUS: SHADOW
```

| Value | Meaning |
|-------|---------|
| SHADOW | Logging only, no blocking |
| ENFORCED | Live strategy gating active |

**Rule:** SHADOW mode = regime does not affect trading.

---

### 7. STRATEGY SUITABILITY MATRIX

```
Mean Reversion (Intraday)     : OK 85  PREFERRED
Statistical Arb / Pairs       : OK 78  PREFERRED
Momentum                      : X  20  DISCOURAGED
```

| Label | Meaning |
|-------|---------|
| PREFERRED | Strategy compatible with regime |
| CONDITIONAL | May work with adjustments |
| DISCOURAGED | Strategy incompatible |

---

### 8. EDGE / AVOID / EXPECTATION

```
EDGE
- Fade range extremes
- VWAP deviations

AVOID
- Momentum chasing
- Breakout anticipation

EXPECTATION
- Small edges
- High patience required
```

These are **human-readable guidance** for the current regime.

---

## Example: MEAN_REVERTING_LOW_VOL (US)

**What the dashboard tells you:**
- Market is range-bound
- Mean reversion strategies preferred
- Momentum/breakout strategies discouraged
- Small edges, high patience

**What you should do:**
- Favor fade strategies at extremes
- Avoid trend-following entries
- Size positions conservatively

**What you should NOT do:**
- Chase price
- Expect large moves
- Override regime because "it feels trending"

---

## Example: STALE India Dashboard

```
STATUS: STALE (127.4m since last update)
ACTION: DO NOT TRUST REGIME | STAND DOWN
```

**What this means:**
- India regime data is not updating
- Likely outside market hours (09:15-15:30 IST)
- Or WebSocket connection issue

**What you should do:**
- Check if market is open
- If market is open: check runner logs
- Do not rely on stale regime data

---

## What NOT To Do

- ❌ Do NOT manually override regime during trading
- ❌ Do NOT ignore STALE warnings
- ❌ Do NOT trade against regime out of frustration
- ❌ Do NOT treat regime as a trade signal
- ❌ Do NOT add new indicators without review

---

## Document Status

**STATUS: ACTIVE**

This runbook applies to Dashboard v1.1 (Decision-Complete).
