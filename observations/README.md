# Phase 4: Live Observation (NO TRADING)

## Purpose
The purpose of Phase 4 is to observe the output of the Momentum Engine (v0) in real-time or near-real-time without committing capital. This phase is critical for validating the signal quality, identifying obvious failure modes, and training the observation discipline.

## Directory Structure
- `daily_logs/`: Raw logs from signal generation runs.
- `signal_reviews/`: Standardized CSV files containing generated signals with placeholders for clinical review.
- `screenshots/`: Visual evidence of price action at the time of signal generation.
- `notes/`: Qualitative observations about market behavior and regime.

## Rules of Engagement
1. **NO TRADING**: No orders are to be placed based on these signals.
2. **NO TUNING**: The momentum engine logic (v0) is locked. We do not "fix" the logic during this phase; we observe its current state.
3. **MANDATORY REVIEW**: Every signal logged in `signal_reviews/` should be retroactively classified (A/B/C/D) based on price action 5m/15m after the signal.

## Review Classification
- **A**: Clean momentum continuation. Target reached quickly.
- **B**: Messy but eventually hit target.
- **C**: Sideways/Choppy. Stop hint would have been hit or time-decayed.
- **D**: Instant reversal (Fakeout).

## Logging Workflow
1. Run the `momentum_engine` on processed data.
2. Use `observations/signal_logger.py` to capture candidates into the daily review CSV.
3. End of day: Open the CSV and fill in the `result_5m`, `result_15m`, and `classification` columns.
