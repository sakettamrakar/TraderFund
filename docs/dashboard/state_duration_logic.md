# State Duration Logic

**Version**: 1.0
**Date**: 2026-01-29

## Objective
To answer the question: *"How long has the system been in this state?"*

## Calculation Algorithm
1. **Identify Current State**: Read the state $S_0$ at the latest tick $T_0$.
2. **Backward Scan**: Iterate backwards through ticks $T_{-1}, T_{-2}, ... T_{-n}$.
3. **Comparison**:
   - If State($T_{-k}$) == $S_0$, continue scanning.
   - If State($T_{-k}$) != $S_0$, stop.
4. **Start Time Determination**: The "Start Time" is the timestamp of the oldest contiguous matching tick.
5. **Duration**: $Duration = T_{now} - T_{start}$.

## Constraints
- **Scan Limit**: The backend limits backward scanning to avoid IO saturation (default: 100 ticks).
- **Resolution**: Duration is precise to the tick interval (cron frequency).
- **Persistence**: Since duration is computed from disk history, it persists across restarts and page reloads.

## Semantics
- **Metrics**: Displayed as "In State: Xd Yh Zm".
- **Meaning**: Represents *conviction* or *stagnation*.
  - Long `NONE` = Stagnation/Safety.
  - Long `CONFIRMED` = Trend Maturity.
