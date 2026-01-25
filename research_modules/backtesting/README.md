# Backtesting Engine (Module A)

## RESEARCH-ONLY

> ⚠️ **WARNING**: This module is strictly for research purposes.
> It MUST NOT be used to make live trading decisions.

---

## Purpose

This backtesting engine is designed to answer a single class of questions:

> "How would [Strategy X] have performed on [Historical Data Y]?"

It provides a controlled, event-driven simulation environment for:
- Validating signal logic against historical data.
- Measuring performance metrics (win rate, expectancy, drawdown).
- Comparing strategy variations in a controlled setting.

---

## What This Engine CAN Answer

✅ Relative performance of strategy variations.
✅ Approximate win rate and expectancy on historical data.
✅ Maximum drawdown behavior.
✅ Trade frequency and distribution.

---

## What This Engine CANNOT Answer

❌ **Future Performance**: Backtest results are NOT predictive.
❌ **Live Execution Quality**: Slippage/fill models are approximations.
❌ **Market Impact**: The engine assumes infinite liquidity.
❌ **Regime Shifts**: Historical regimes may not repeat.

---

## Why Results Must Not Be Trusted Blindly

1. **Overfitting Risk**: Parameters tuned to past data often fail live.
2. **Survivorship Bias**: Historical data may not include delisted stocks.
3. **Look-Ahead Bias**: Subtle coding errors can leak future data.
4. **Execution Differences**: Real fills differ from simulated fills.

**Rule**: All backtest insights MUST be validated through a minimum 30-day observation period before any production consideration.

---

## Usage

```bash
# Run with explicit research-mode flag
python -m research_modules.backtesting.cli \
    --data-path data/processed/intraday \
    --data-file NSE_ITC.parquet \
    --research-mode
```

The `--research-mode` flag is **REQUIRED**. The CLI will refuse to run without it.

---

## Safety Guardrails

| Guardrail | Description |
|-----------|-------------|
| Phase Lock | Engine raises `RuntimeError` if `ACTIVE_PHASE < 6`. |
| CLI Safety | `--research-mode` flag required. |
| No Live Data | `HistoricalDataAdapter` blocks paths with "live" or "stream". |
| No Production Output | Results are printed to stdout only, never to production logs. |

---

## See Also

- [PHASE_LOCK.md](./PHASE_LOCK.md) - Activation requirements.
- [docs/governance/RESEARCH_MODULE_GOVERNANCE.md](../../docs/governance/RESEARCH_MODULE_GOVERNANCE.md) - Global governance policy.
