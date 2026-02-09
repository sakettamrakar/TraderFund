# Temporal Truth Dashboard Surface

**Version**: 1.0.0
**Epoch**: TE-2026-01-30
**Intent**: Define how Temporal Truth (`TE`) and its delta from Raw Data (`RDT`) is visualized on the Operator Dashboard to ensure clarity and prevent confusion.

## 1. Global Time Display

The Dashboard Header MUST display the current **Truth Epoch (TE)** prominently, separate from the system clock.

- **Label**: `TRUTH EPOCH:`
- **Format**: `YYYY-MM-DD` 
- **Style**: 
    - **Green**: `TE == RDT` (Synchronized)
    - **Yellow**: `TE < RDT` (Pending Evaluation)
    - **Red**: `TE << RDT` (Stale / Drift > 2 Days)

*Example*:
`TRUTH EPOCH: 2026-02-09 [SYNC]` 
*(System Clock: 2026-02-10 09:30)*

## 2. Market-Specific Temporal Status

Each Market Panel (US, INDIA) MUST show its relation to the Global TE.

- **US Status**:
    - `RDT: 2026-02-10`
    - `CTT: 2026-02-10`
    - `TE: 2026-02-09` 
    - **Display**: `[EVAL PENDING]` (Yellow Badge)

- **INDIA Status**:
    - `RDT: 2026-02-10`
    - `CTT: 2026-02-10`
    - `TE: 2026-02-10`
    - **Display**: `[SYNC]` (Green Badge)

## 3. Discrepancy Indicators

When a mismatch occurs, explicit messaging is required.

### 3.1 Pending Ingestion (`RDT > CTT`)
- **Indicator**: Loading Icon or "Ingesting..." badge.
- **Message**: "Raw data detected. Validating..."
- **Action**: Disable Strategy Execution until validation completes.

### 3.2 Pending Evaluation (`CTT > TE`)
- **Indicator**: "Ready for Intelligence" or "New Data Available".
- **Message**: "Canonical data advanced to `YYYY-MM-DD`. Awaiting Decision Engine."
- **Action**: Enable "Run Evaluation" button / Auto-trigger if configured.

### 3.3 Temporal Drift (`CTT >> TE`)
- **Indicator**: ⚠️ Warning Icon.
- **Message**: "System is STALE by X days. Last evaluated: `YYYY-MM-DD`."
- **Action**: 
    - Highlight impacted widgets in **Grey**.
    - Explicitly label data as "OLD".

## 4. Inspection Mode Handling
When `Inspection Mode` is active (`SIMULATION`):
- **TE Display**: `INSPECTION MODE [SIM]`
- **RDT/CTT**: Hidden or Greyed out.
- **Banner**: "Temporal Truth Suspended. Visualizing STATIC Scenario."

## 5. Explicit "Frozen" State
If governance explicitly halts time progression (e.g., during investigation):
- **Banner**: `🛑 TRUTH FROZEN BY GOVERNANCE`
- **Reason**: Display reason from `audit_log`.
- **TE**: Remains static regardless of RDT updates.

This surface ensures operators always know *when* the system thinks it is, preventing decisions based on stale or future data.
