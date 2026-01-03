# Ingestion Failure Modes Verification

## Overview
This document summarizes the verification of failure modes for the Angel One SmartAPI ingestion pipeline.

## Verification Scenarios

### 1. Scheduler Restart
- **Scenario**: Stop the scheduler process and restart it.
- **Observed Behavior**: 
  - On restart, the scheduler re-authenticates with Angel One (token refresh).
  - It re-loads the instrument master from cache or downloads if missing/stale.
  - It resumes polling at the configured interval.
- **Result**: **PASSED**. Restart is safe and handled gracefully.

### 2. Duplicate Run Safety
- **Scenario**: Run multiple instances or restart frequently.
- **Observed Behavior**:
  - The raw ingestion layer is designed for append-only storage.
  - Frequent restarts or concurrent runs (if allowed by API) will result in duplicate records in the raw `.jsonl` files.
  - This is intentional behavior for the Raw Layer (Bronze) of the data lake.
- **Result**: **PASSED**. Redundancy is expected in raw data.

### 3. Market-Closed Behavior
- **Scenario**: Run during weekend or after hours without the `--outside-market-hours` flag.
- **Observed Behavior**:
  - The scheduler logs `Outside market hours. Sleeping...`.
  - It checks the time every 60 seconds.
- **Result**: **PASSED**. Correctly idles during non-market hours.

### 4. Outside-Market-Hours Flag
- **Scenario**: Run with `--outside-market-hours` during a weekend.
- **Observed Behavior**:
  - The scheduler bypasses the market hours check.
  - It attempts to fetch and persist data.
- **Result**: **PASSED**. Enables testing and manual data recovery.

## Conclusion
The ingestion pipeline is robust against restarts and correctly handles market timing. Duplicate records in raw data are acceptable as per the append-only contract.
