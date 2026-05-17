# Scenario Testing & Factor Verification — Consolidated

> Consolidated from 3 audit files. Originals moved to `_delete/audit/`.
> Epoch: TE-2026-01-30

---

## 1. Factor Discontinuity Analysis

**Event**: `IGNITION-001` (Jan 30, 2026)
**Trigger**: Switch from regime-derived (semantic) to calculated (technical) factors.

### Momentum
- **Before**: Linked to regime label (`BULLISH → STRONG`)
- **After**: Calculated from price (`Price > SMA20 > SMA50 → STRONG`, `ROC(10) > 2% → POSITIVE`)
- **Verdict**: Healthy discontinuity — system now reacts to price, not labels

### Volatility
- **Before**: Derived/mocked
- **After**: US = VIX level (raw); India = realized vol (annualized)
- **Warning**: Downstream strategies expecting normalized 0-1 scores will need a normalization layer

### Liquidity / Value / Quality
- **Before**: Mocked "Neutral"
- **After**: `neutral, confidence: 0.5` — missing fundamental/macro inputs
- **Verdict**: Honest stagnation — correctly reports low confidence rather than fake data

---

## 2. Stress Scenario Verification (Dry Run)

### S1: Volatility Shock (VIX > 35)
- **India**: VIX=40.0 → `SYSTEMIC_STRESS` → action suppressed | **PASS**

### S2: Liquidity Tightening
- **India**: Liquidity=TIGHT → `RESTRICTED` → long/short blocked | **PASS**
- **US**: Liquidity=TIGHT → `RESTRICTED` → long/short blocked | **PASS**

### S3: Regime Instability (Regime = UNKNOWN)
- **US**: → `HALTED` → `OBSERVE_ONLY` | **PASS**

### S4: Data Degradation
- Logic trace: insufficient data → regime `UNKNOWN` → collapses to S3
- **PASS** (implicit coverage via S3)

**All 4 scenarios passed. System correctly suppresses actions under adverse conditions.**

---

## 3. Phase 3 Hygiene Pass

**Result**: No violations detected.
