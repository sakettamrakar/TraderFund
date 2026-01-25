# Paper Trading Execution Layer

## SIMULATION ONLY - NO REAL ORDERS

> ⚠️ **WARNING**: This module simulates trading.
> It does NOT place real orders or risk real capital.

---

## Purpose

The Paper Trading module allows you to:

✅ **Test signal execution** without real risk
✅ **Validate trade logging** before going live
✅ **Practice the execution workflow** safely

---

## What Paper Trading SIMULATES

| Aspect | Simulation |
|--------|------------|
| Order fills | At requested price + slippage |
| Position tracking | One position per symbol |
| P&L calculation | Based on simulated fills |
| Trade logging | Append-only CSV |

---

## What Paper Trading Does NOT Simulate

| Aspect | Reality |
|--------|---------|
| Liquidity | Real orders may not fill |
| Partial fills | We assume full fills |
| Market impact | Real orders move prices |
| Latency | Real execution has delays |
| Broker errors | Real APIs can fail |

---

## Why Results Are NOT Performance Proof

1. **Slippage is estimated**, not real.
2. **Fills are guaranteed**, which doesn't happen in real markets.
3. **No emotional factors** like fear or greed.
4. **No capital constraints** like margin or buying power.

**Rule**: Paper trading validates mechanics, not profitability.

---

## Usage

```bash
python -m paper_trading.execution.cli \
    --paper-mode \
    --session intraday \
    --exit-minutes 5 \
    --slippage 0.05
```

The `--paper-mode` flag is **REQUIRED**.

---

## Trade Log Format

Logs are saved to `paper_trading/logs/` as CSV:

| Field | Description |
|-------|-------------|
| timestamp | When trade was logged |
| symbol | Instrument traded |
| entry_price | Simulated entry fill |
| exit_price | Simulated exit fill |
| quantity | Shares traded |
| holding_minutes | Time in position |
| gross_pnl | P&L before costs |
| net_pnl | P&L after slippage |
| signal_confidence | From Momentum Engine |
| signal_reason | Why signal triggered |
| exit_reason | Why trade exited |

---

## Safety Guardrails

| Guard | Description |
|-------|-------------|
| Phase Lock | Requires `PHASE_6_PAPER` |
| CLI Flag | `--paper-mode` required |
| No Broker SDK | Zero broker imports |
| No API Keys | No credential usage |

---

## How to Review Logs Safely

1. Open the CSV in a spreadsheet.
2. Sort by `net_pnl` to see best/worst trades.
3. Filter by `exit_reason` to understand exits.
4. Check `signal_confidence` vs outcome correlation.

**Do NOT** assume paper results will match real results.
