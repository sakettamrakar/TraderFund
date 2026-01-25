# Risk Modeling & Position Sizing Module (Module C)

## RESEARCH-ONLY

> ⚠️ **WARNING**: This module is strictly for research purposes.
> It MUST NOT be used to size live positions or place stops.

---

## Purpose

This module answers a single question:

> "What could go wrong, and how bad could it be?"

It provides **simulations** and **calculations** for risk analysis. It does NOT place trades.

---

## What This Module SIMULATES

✅ **Position Sizing Models:**
- Fixed fractional risk (% of capital per trade)
- ATR-based stop distance
- Percent of equity limits

✅ **Risk Metrics:**
- R-multiple calculation
- Worst-case loss scenarios
- Capital at risk percentage
- Kelly Criterion (for reference only)

✅ **Loss Guards:**
- Daily loss limit checks
- Per-trade loss limit checks
- Drawdown threshold checks

---

## Assumptions (Important!)

| Assumption | Reality |
|------------|---------|
| Stops are always filled at stop price | Slippage can cause worse fills |
| Position can always be entered | Liquidity may not exist |
| Historical parameters hold forward | Markets change |

---

## Why Simulated Risk ≠ Live Risk

1. **Slippage**: Live stops may fill at worse prices.
2. **Gaps**: Overnight gaps can blow past stops.
3. **Liquidity**: You may not get the size you want.
4. **Execution**: Orders may be delayed or rejected.

**Rule**: Simulations are optimistic. Live risk is typically worse.

---

## Usage

```bash
python -m research_modules.risk_models.cli \
    --symbol ITC \
    --entry 100 \
    --stop 95 \
    --capital 100000 \
    --risk-pct 1.0 \
    --research-mode
```

---

## See Also

- [PHASE_LOCK.md](./PHASE_LOCK.md)
- [docs/governance/RESEARCH_MODULE_GOVERNANCE.md](../../docs/governance/RESEARCH_MODULE_GOVERNANCE.md)
