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
- **A**: Clean momentum continuation. Target reached quickly (>0.3% move within 15m).
- **B**: Messy but eventually hit target.
- **C**: Sideways/Choppy. Stop hint would have been hit or time-decayed.
- **D**: Instant reversal (Fakeout).

## Automated Validation
The platform now includes a `SignalValidator` that automatically tracks price action at T+5 and T+15 for every signal. It assigns the preliminary classification based on hard price targets (e.g., Target > 0.3% for 'Clean').

## EOD Reporting
Daily summaries are automatically generated using `EodReviewGenerator`. This provides a high-level view of:
- Total signals generated.
- Quality distribution (Buckets A/B/C/D).
- Top failing symbols.
- Confidence vs. Outcome analysis.

## Workflow
1. **Live Feed**: Run `momentum_live_runner.py` to capture real-time signals.
2. **Automated Validation**: Run `signal_validator.py` periodically (or at EOD) to populate price action and outcomes.
3. **Report Generation**: Run `eod_review_generator.py` to create the final markdown summary for the day.
