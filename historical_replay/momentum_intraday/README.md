# Historical Intraday Momentum Replay

> ⚠️ **DIAGNOSTIC TOOL ONLY** — Do not use for trading decisions or optimization.

## Purpose

This module provides a **Historical Intraday Replay** system for the Momentum Engine. It replays historical 1-minute candle data minute-by-minute, simulating real-time arrival of data, to analyze how the momentum engine would have behaved on a past trading day.

This is a **diagnostic and learning tool**, NOT a backtesting or optimization system.

---

## Key Concepts

### What This Module Does

1. **Simulates Real-Time Data Arrival**: Candles are exposed progressively using the `CandleCursor` abstraction, ensuring the momentum engine only sees data up to the current evaluation timestamp.

2. **Prevents Lookahead Bias**: The `CandleCursor.get_candles_up_to(T)` method guarantees that no future candles are accessible at evaluation time T.

3. **Uses Identical Momentum Logic**: The replay calls the **same** `MomentumEngine.generate_signals_from_df()` method used in live observation—no duplicated or alternate logic.

4. **Produces Familiar Outputs**: Signals are logged in the same CSV format as live observation, and the same EOD report template is generated.

---

## How This Differs From...

### Generic Historical Analytics (`analysis/phase5_diagnostics/`)

| Aspect | Historical Analytics | This Module |
|--------|---------------------|-------------|
| Purpose | Post-hoc metric calculation | Real-time simulation |
| Data Access | Full dataset | Progressive (no lookahead) |
| Momentum Logic | Separate analysis | Same as live |
| Output Format | Custom reports | Same as live observation |

### Live Phase-4 Observation (`observations/momentum_live_runner.py`)

| Aspect | Live Observation | Historical Replay |
|--------|-----------------|-------------------|
| Data Source | Live broker API | Historical Parquet files |
| Time Progression | Real-time | Simulated |
| T+5/T+15 Validation | Waits real-time | Instant lookup |
| Broker API Calls | Yes | **NEVER** |

### Backtesting

| Aspect | Backtesting | Historical Replay |
|--------|------------|-------------------|
| Goal | Optimize parameters | Understand behavior |
| P&L Calculation | Yes | **NO** |
| Parameter Tuning | Allowed | **FORBIDDEN** |
| Decision Making | Trade entry/exit | Observation only |

---

## Why Historical Replay ≠ Backtesting

1. **No P&L calculation**: We do not simulate profits, losses, or trade execution.

2. **No optimization**: Parameters are frozen. You MUST NOT use replay results to tune parameters.

3. **Observation focus**: The goal is to understand signal quality, not to find "winning" settings.

4. **Single-path analysis**: We replay what happened, not what could have happened with different settings.

---

## Usage

### Basic Replay (Single Symbol, Single Date)

```bash
python historical_replay/momentum_intraday/cli.py \
  --symbol RELIANCE \
  --date 2026-01-03
```

### Batch Replay (All Watchlist Symbols)

Use the `ALL` keyword to process all symbols in the configured watchlist.

```bash
python historical_replay/momentum_intraday/cli.py \
  --symbol ALL \
  --date 2026-01-03
```

### Monthly Replay (All Available Trading Days)

Provide the date in `YYYY-MM` format to automatically replay all trading days for that month that exist in your processed Parquet data.

```bash
# Process a single symbol for the entire month
python historical_replay/momentum_intraday/cli.py \
  --symbol RELIANCE \
  --date 2025-12

# Process ALL symbols for the entire month
python historical_replay/momentum_intraday/cli.py \
  --symbol ALL \
  --date 2025-12
```

### Multiple Symbols (Comma-Separated)

```bash
python historical_replay/momentum_intraday/cli.py \
  --symbol RELIANCE,TCS,HDFCBANK \
  --date 2025-12-15
```

### With Custom Interval

```bash
python historical_replay/momentum_intraday/cli.py \
  --symbol TCS \
  --date 2026-01-03 \
  --interval 5
```

### Skip Sanity Checks

```bash
python historical_replay/momentum_intraday/cli.py \
  --symbol INFY \
  --date 2026-01-03 \
  --no-sanity-checks
```

---

## Output Structure

```
observations/
└── historical_replay/
    └── 2026-01-03/
        ├── signals_for_review_2026-01-03.csv
        └── eod_report_2026-01-03.md
```

All outputs include a `mode=HISTORICAL_REPLAY` label and clear warnings that this is not live data.

---

## Sanity Checks

The replay automatically runs sanity checks to verify correctness:

1. **No Future Candles**: Verifies no signal timestamp is from the future.
2. **VWAP Progression**: Verifies VWAP evolves progressively (not static).
3. **Timestamp Alignment**: Verifies signal timestamps align with candle boundaries.
4. **Determinism**: Verifies replay produces identical results on re-run.

---

## When to Use This Tool

✅ **Appropriate Uses**:
- Understanding how signals formed on a specific day
- Analyzing signal timing relative to market events
- Comparing signal patterns across multiple days
- Training your intuition for the momentum strategy

❌ **Inappropriate Uses**:
- Optimizing momentum parameters
- Making trading decisions
- Comparing P&L between configurations
- Any form of curve-fitting

---

## Architecture

```
historical_replay/momentum_intraday/
├── candle_cursor.py       # Lookahead prevention abstraction
├── replay_controller.py   # Minute-by-minute orchestration
├── replay_logger.py       # Signal logging to replay directory
├── replay_validator.py    # Instant T+5/T+15 validation
├── replay_runner.py       # Top-level orchestration
├── cli.py                 # Command-line interface
└── validation/
    └── replay_sanity_checks.py  # Correctness verification
```

---

## See Also

- [PHASE_LOCK.md](./PHASE_LOCK.md) — Governance and usage restrictions
- [observations/README.md](../../observations/README.md) — Live Phase-4 observation
