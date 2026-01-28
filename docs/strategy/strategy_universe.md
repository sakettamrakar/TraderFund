# Strategy Universe — Complete Taxonomy

**Version**: 1.0  
**Date**: 2026-01-29  
**Status**: EVOLUTION_ONLY (All strategies)

## Purpose

This document defines the **complete universe of strategy families** that the system can observe, evaluate, and (when evolutionarily validated) eventually execute. Every strategy exists in "paper" form—observable but not executable until explicitly authorized.

---

## Family A: Trend / Momentum

**Philosophy**: Capture directional persistence in price movements.

| Strategy ID | Name | Intent |
|-------------|------|--------|
| `STRAT_MOM_TIMESERIES_V1` | Time-Series Momentum | Follow absolute trend direction in individual assets |
| `STRAT_MOM_CROSSSECTION_V1` | Cross-Sectional Momentum | Rank and select winners vs losers across universe |
| `STRAT_MOM_BREAKOUT_V1` | Breakout / Trend-Following | Enter on range expansion, ride established trends |

**Current Status**: BLOCKED (Momentum: NONE, Expansion: NONE)

---

## Family B: Mean Reversion

**Philosophy**: Exploit temporary deviations from equilibrium.

| Strategy ID | Name | Intent |
|-------------|------|--------|
| `STRAT_REVERT_SHORTTERM_V1` | Short-Term Mean Reversion | Fade 1-5 day overextensions |
| `STRAT_REVERT_STATISTICAL_V1` | Statistical Reversion | Trade Z-score extremes with defined lookback |
| `STRAT_REVERT_VOLADJ_V1` | Volatility-Adjusted Reversion | Scale reversion bets by realized volatility |

**Current Status**: BLOCKED (Volatility structure undefined)

---

## Family C: Value

**Philosophy**: Buy undervalued assets, sell overvalued.

| Strategy ID | Name | Intent |
|-------------|------|--------|
| `STRAT_VALUE_DEEP_V1` | Deep Value | Extreme P/E, P/B, or FCF discounts |
| `STRAT_VALUE_RELATIVE_V1` | Relative Value | Compare similar assets on valuation metrics |
| `STRAT_VALUE_SPREAD_V1` | Valuation Spread Trades | Long cheap vs short expensive within sector |

**Current Status**: ELIGIBLE (Regime-robust, no factor dependency)

---

## Family D: Quality / Defensive

**Philosophy**: Tilt toward stable, high-quality earnings.

| Strategy ID | Name | Intent |
|-------------|------|--------|
| `STRAT_QUALITY_TILT_V1` | Quality Tilt | Overweight high ROE, low debt, stable margins |
| `STRAT_QUALITY_LOWVOL_V1` | Low Volatility | Select low-beta, low-realized-vol stocks |
| `STRAT_QUALITY_DEFENSIVE_V1` | Defensive Carry | Combine quality with dividend yield |

**Current Status**: ELIGIBLE (Regime-robust)

---

## Family E: Carry / Yield

**Philosophy**: Harvest income from asset holding.

| Strategy ID | Name | Intent |
|-------------|------|--------|
| `STRAT_CARRY_EQUITY_V1` | Equity Carry | Dividend yield + buyback yield |
| `STRAT_CARRY_VOL_V1` | Volatility Carry | Short implied volatility vs realized |
| `STRAT_CARRY_RATE_V1` | Rate / Curve Carry | Capture term premium along yield curve |

**Current Status**: BLOCKED (Carry slope undefined, VRP not measured)

---

## Family F: Volatility Strategies

**Philosophy**: Trade volatility as an asset class.

| Strategy ID | Name | Intent |
|-------------|------|--------|
| `STRAT_VOL_HARVEST_V1` | Volatility Harvesting | Systematic short vol with defined hedges |
| `STRAT_VOL_VRP_V1` | Variance Risk Premium | Capture IV > RV spread |
| `STRAT_VOL_CONVEXITY_V1` | Convexity / Tail Hedges | Long options for tail protection |

**Current Status**: BLOCKED (VRP undefined, convexity not priced)

---

## Family G: Relative / Spread Strategies

**Philosophy**: Exploit relative mispricings between assets.

| Strategy ID | Name | Intent |
|-------------|------|--------|
| `STRAT_SPREAD_PAIR_V1` | Pair Trading | Co-integrated pairs, mean-revert spread |
| `STRAT_SPREAD_SECTOR_V1` | Sector Spreads | Long/short within sectors on relative value |
| `STRAT_SPREAD_FACTOR_V1` | Factor Spreads | Trade factor exposures (e.g., growth vs value) |

**Current Status**: BLOCKED (Dispersion: NONE)

---

## Family H: Liquidity / Stress Strategies

**Philosophy**: Profit from liquidity events and stress regimes.

| Strategy ID | Name | Intent |
|-------------|------|--------|
| `STRAT_STRESS_CRISIS_V1` | Crisis Alpha | Long convexity, short risk in stress |
| `STRAT_STRESS_LIQUIDITY_V1` | Liquidity Provision | Market-make in illiquid conditions |
| `STRAT_STRESS_RISKOFF_V1` | Risk-Off Protection | Systematic de-risking triggers |

**Current Status**: BLOCKED (Liquidity: NEUTRAL, no stress detected)

---

## Summary

| Family | Count | Expected Eligible |
|--------|-------|-------------------|
| Trend/Momentum | 3 | 0 |
| Mean Reversion | 3 | 0 |
| Value | 3 | 3 |
| Quality/Defensive | 3 | 3 |
| Carry/Yield | 3 | 0 |
| Volatility | 3 | 0 |
| Relative/Spread | 3 | 0 |
| Liquidity/Stress | 3 | 0 |
| **Total** | **24** | **6** |

---

## Governance

- All strategies have `evolution_status: EVOLUTION_ONLY`
- No strategy may execute without explicit Decision Ledger authorization
- Dashboard exposes all strategies, regardless of eligibility
