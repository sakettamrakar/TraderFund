# Paper Trading Analytics Dashboard

## READ-ONLY - POST-TRADE ANALYSIS ONLY

> ⚠️ **WARNING**: This dashboard is for REFLECTION, not optimization.
> Do NOT use these metrics to change strategy or execution.

---

## Purpose

This dashboard helps you **REVIEW** paper trading behavior AFTER the session:

✅ How many trades were executed?
✅ What was the win rate?
✅ How did different confidence levels perform?
✅ Were there patterns by time of day?

---

## What This Dashboard is NOT For

| Misuse | Reality |
|--------|---------|
| Strategy optimization | Paper results don't prove real edge |
| Parameter tuning | You're curve-fitting to simulation |
| Confidence in profits | Paper P&L ≠ Real P&L |
| Ranking strategies | Noise dominates short samples |

---

## Common Misinterpretations

1. **High win rate is good** → Could be random or due to favorable conditions
2. **Positive P&L proves the strategy** → Paper ignores slippage, liquidity, emotions
3. **Low confidence trades losing** → Sample size may be too small
4. **Morning trades better** → Could be coincidence

---

## How to Use This Dashboard

1. **Review, don't react** - Note patterns but don't change behavior
2. **Look for obvious problems** - Excessive trading, zero winners, etc.
3. **Track over time** - One session is noise; 20 sessions is a pattern
4. **Be skeptical** - Assume any insight could be wrong

---

## Usage

```bash
# View summary for today
python -m paper_trading.analytics.cli --summary

# View summary for specific date
python -m paper_trading.analytics.cli --date 2026-01-05 --summary

# Generate plots
python -m paper_trading.analytics.cli --date 2026-01-05 --plots
```

---

## Metrics Explained

| Metric | Definition | Caveat |
|--------|------------|--------|
| Win Rate | % of trades with positive P&L | Ignores magnitude |
| Expectancy | Avg P&L per trade | Can be skewed by outliers |
| Max Drawdown | Largest peak-to-trough drop | Paper only |
| Profit Factor | Gross profit / Gross loss | Unstable in small samples |

---

## Safety Guardrails

- Requires `PHASE_6_PAPER` environment
- No imports into execution layer
- No strategy recommendations
- No automatic optimization
