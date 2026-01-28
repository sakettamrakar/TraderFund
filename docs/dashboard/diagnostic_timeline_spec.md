# Diagnostic Timeline Specification

**Version**: 1.1
**Date**: 2026-01-29
**Status**: ACTIVE

## Purpose
To provide an unambiguous, verifiable history of system state transitions without inferring or simulating data. The timeline serves as the primary audit trail for the "Observer" role.

## Data Source
- **Origin**: `docs/evolution/ticks/tick_{timestamp}/`
- **Integrity**: Read-only access to immutable JSON artifacts.
- **Normalization**: Timestamps are parsed from directory names (unix epoch) and converted to ISO 8601 `YYYY-MM-DD HH:MM:SS`.

## Display Contract
1. **Timestamp**:
   - Must show full date and time.
   - Must include Timezone (or explicit UTC marker).
   - *Rationale*: Ambiguity across day boundaries is unacceptable for financial forensics.

2. **Columns**:
   - **Time**: High-precision timestamp.
   - **Momentum**: `NONE` | `EMERGING` | `CONFIRMED`
   - **Expansion**: `NONE` | `EARLY` | `CONFIRMED`
   - **Dispersion**: `NONE` | `BREAKOUT`
   - **Liquidity**: `NEUTRAL` | `COMPRESSED` | `STRESSED`

## UX Invariants
- **Sort Order**: Strictly descending (newest top).
- **Scanning**: The backend may scan up to `N` ticks to display history, but the frontend pagination should handle performance.
- **No Actions**: The timeline is purely diagnostic; clicking a row triggers no state change.
