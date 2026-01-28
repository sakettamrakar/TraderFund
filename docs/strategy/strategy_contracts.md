# Strategy Contracts — Regime & Factor Requirements

**Version**: 1.0  
**Date**: 2026-01-29

## Purpose

Each strategy declares explicit **Regime Contracts** (allowed/forbidden market regimes) and **Factor Contracts** (required factor states). These contracts gate eligibility—no strategy may activate without satisfying both.

---

## Contract Definitions

### Regime States (Observed)
- `BULL_CALM`: Uptrend, low volatility
- `BULL_VOL`: Uptrend, high volatility
- `BEAR_RISK_OFF`: Downtrend, risk aversion
- `UNDEFINED`: Regime not determinable

### Factor States (Observed)
- **Momentum**: `NONE` | `EMERGING` | `CONFIRMED`
- **Expansion**: `NONE` | `EARLY` | `CONFIRMED`
- **Dispersion**: `NONE` | `BREAKOUT`
- **Liquidity**: `NEUTRAL` | `COMPRESSED` | `STRESSED`

---

## Family A: Trend / Momentum

| Strategy | Allowed Regimes | Forbidden Regimes | Factor Requirements | Safety |
|----------|----------------|-------------------|---------------------|--------|
| `STRAT_MOM_TIMESERIES_V1` | BULL_VOL, BULL_CALM | BEAR_RISK_OFF | Momentum ≥ EMERGING, Expansion ≥ EARLY | Reject |
| `STRAT_MOM_CROSSSECTION_V1` | BULL_VOL, BULL_CALM | BEAR_RISK_OFF | Momentum ≥ EMERGING, Dispersion = BREAKOUT | Reject |
| `STRAT_MOM_BREAKOUT_V1` | BULL_VOL | BEAR_RISK_OFF, BULL_CALM | Expansion = CONFIRMED | Reject |

---

## Family B: Mean Reversion

| Strategy | Allowed Regimes | Forbidden Regimes | Factor Requirements | Safety |
|----------|----------------|-------------------|---------------------|--------|
| `STRAT_REVERT_SHORTTERM_V1` | BULL_CALM | BULL_VOL, BEAR_RISK_OFF | Momentum = NONE, Liquidity = NEUTRAL | Degrade |
| `STRAT_REVERT_STATISTICAL_V1` | BULL_CALM, BULL_VOL | BEAR_RISK_OFF | Dispersion = NONE | Degrade |
| `STRAT_REVERT_VOLADJ_V1` | ALL | — | Expansion = NONE | Degrade |

---

## Family C: Value

| Strategy | Allowed Regimes | Forbidden Regimes | Factor Requirements | Safety |
|----------|----------------|-------------------|---------------------|--------|
| `STRAT_VALUE_DEEP_V1` | ALL | — | None (Regime-robust) | Reject |
| `STRAT_VALUE_RELATIVE_V1` | ALL | — | None (Regime-robust) | Reject |
| `STRAT_VALUE_SPREAD_V1` | ALL | — | None (Regime-robust) | Reject |

---

## Family D: Quality / Defensive

| Strategy | Allowed Regimes | Forbidden Regimes | Factor Requirements | Safety |
|----------|----------------|-------------------|---------------------|--------|
| `STRAT_QUALITY_TILT_V1` | ALL | — | None (Regime-robust) | Reject |
| `STRAT_QUALITY_LOWVOL_V1` | ALL | — | None (Regime-robust) | Reject |
| `STRAT_QUALITY_DEFENSIVE_V1` | ALL | — | None (Regime-robust) | Reject |

---

## Family E: Carry / Yield

| Strategy | Allowed Regimes | Forbidden Regimes | Factor Requirements | Safety |
|----------|----------------|-------------------|---------------------|--------|
| `STRAT_CARRY_EQUITY_V1` | BULL_CALM | BEAR_RISK_OFF | Liquidity = NEUTRAL | Degrade |
| `STRAT_CARRY_VOL_V1` | BULL_CALM | BULL_VOL, BEAR_RISK_OFF | Expansion = NONE | Reject |
| `STRAT_CARRY_RATE_V1` | ALL | — | (Yield curve: Positive slope) | Reject |

---

## Family F: Volatility Strategies

| Strategy | Allowed Regimes | Forbidden Regimes | Factor Requirements | Safety |
|----------|----------------|-------------------|---------------------|--------|
| `STRAT_VOL_HARVEST_V1` | BULL_CALM | BEAR_RISK_OFF | Expansion = NONE, Liquidity = NEUTRAL | Reject |
| `STRAT_VOL_VRP_V1` | BULL_CALM, BULL_VOL | BEAR_RISK_OFF | (VRP > 0) | Reject |
| `STRAT_VOL_CONVEXITY_V1` | BEAR_RISK_OFF | BULL_CALM | Liquidity = STRESSED | Reject |

---

## Family G: Relative / Spread Strategies

| Strategy | Allowed Regimes | Forbidden Regimes | Factor Requirements | Safety |
|----------|----------------|-------------------|---------------------|--------|
| `STRAT_SPREAD_PAIR_V1` | BULL_CALM | BEAR_RISK_OFF | Dispersion = NONE | Degrade |
| `STRAT_SPREAD_SECTOR_V1` | ALL | — | Dispersion = BREAKOUT | Reject |
| `STRAT_SPREAD_FACTOR_V1` | ALL | — | Dispersion = BREAKOUT | Reject |

---

## Family H: Liquidity / Stress Strategies

| Strategy | Allowed Regimes | Forbidden Regimes | Factor Requirements | Safety |
|----------|----------------|-------------------|---------------------|--------|
| `STRAT_STRESS_CRISIS_V1` | BEAR_RISK_OFF | BULL_CALM, BULL_VOL | Liquidity = STRESSED | Reject |
| `STRAT_STRESS_LIQUIDITY_V1` | BEAR_RISK_OFF | BULL_CALM | Liquidity = COMPRESSED or STRESSED | Reject |
| `STRAT_STRESS_RISKOFF_V1` | BEAR_RISK_OFF | BULL_CALM, BULL_VOL | Momentum = NONE | Reject |

---

## Safety Behaviors

| Behavior | Definition |
|----------|------------|
| **Reject** | Do not activate under any circumstance if contract violated |
| **Degrade** | Reduce position size / exposure but allow partial activation |
| **Hedge** | Activate with mandatory hedge overlay |

---

## Activation Conditions (Human-Readable)

### Momentum Strategies
> "Momentum strategies activate when the market is expanding (volatility opening up), dispersion is increasing (winners separating from losers), and momentum is confirmed (not just emerging)."

### Mean Reversion Strategies
> "Mean reversion strategies activate when volatility is contracting, momentum is absent, and dispersion is low. They fade overextensions in quiet markets."

### Value/Quality Strategies
> "Value and Quality strategies are always eligible because they do not depend on short-term market structure. They are regime-robust by design."

### Carry Strategies
> "Carry strategies activate when yield curves are positively sloped, implied volatility exceeds realized, and liquidity is normal. They harvest income in calm conditions."

### Volatility Strategies
> "Volatility strategies activate based on the variance risk premium (VRP). Harvesting requires calm; convexity hedges require stress."

### Spread Strategies
> "Spread strategies activate when dispersion is high enough to create meaningful relative mispricings between assets or factors."

### Stress Strategies
> "Stress strategies are designed for crisis. They activate ONLY in BEAR_RISK_OFF regimes with compressed or stressed liquidity."
