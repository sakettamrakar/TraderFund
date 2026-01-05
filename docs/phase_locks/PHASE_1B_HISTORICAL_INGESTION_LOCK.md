# PHASE_1B_HISTORICAL_INGESTION_LOCK.md

## Phase Status: CLOSED ✅

### Declaration

As of 2026-01-03, Phase 1B (Historical Data Ingestion) of the TraderFund project is hereby declared **LOCKED** and **CLOSED**.

### Scope and Constraints

- **Functionality**: Historical daily candle ingestion via Angel One SmartAPI is fully implemented.
- **Maintenance Model**: No new historical ingestion features are permitted within this phase's scope.
- **Execution Mode**: ON-DEMAND ONLY via CLI. Must never be wired into live scheduler.
- **Data Usage**: Historical data is for context, diagnostics, and risk analysis ONLY.

### Critical Restrictions

> [!CAUTION]
> Historical data must NEVER influence live trading decisions or momentum engine signals.

The following are **STRICTLY PROHIBITED**:

1. ❌ Integration into live scheduler (`scheduler.py`)
2. ❌ Use by momentum engine or signal generation
3. ❌ Automated execution on any timer or cron
4. ❌ Intraday historical data (1-min, 5-min, etc.)
5. ❌ Backtesting using this data

### Permitted Uses

✅ Manual CLI execution for backfill
✅ Future context research (post-market)
✅ Risk analysis and compliance
✅ Data quality verification

### API Endpoint

- `getCandleData` with `interval=ONE_DAY`
- Maximum lookback: 2000 days

### Output Location

```
data/raw/api_based/angel/historical/
├── NSE_RELIANCE_1d.jsonl
├── NSE_TCS_1d.jsonl
└── ...
```

### Verification

- **Schema Contract**: See `docs/verification/historical_ingestion_verification.md`
- **Append-Only Guarantee**: Verified by code inspection

### Authorization

This lock is applied by the Senior Data-Platform Engineer (AI Assistant) after implementation and verification of the historical ingestion module.

> [!IMPORTANT]
> DO NOT integrate historical data into live trading workflows WITHOUT:
> 1. Explicit unlock of this phase
> 2. Documented justification
> 3. Senior engineer review

### Modification Policy

To modify or extend this module:

1. Create a Phase Unlock Request document
2. Justify the change with clear business need
3. Ensure isolation from live trading is maintained
4. Update verification documentation
5. Re-lock after changes
