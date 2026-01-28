# Capital History

This directory contains the persistent audit trail of the system's symbolic capital state.

## Artifacts

- **`capital_state_timeline.json`**: An append-only log of every EV-TICK's capital posture.
- **`README.md`**: This file.

## Schema

Each entry in the timeline contains:

```json
{
  "timestamp": "ISO-8601",
  "tick_id": "TICK-YYYYMMDD...",
  "state": "IDLE | READY | RESTRICTED | FROZEN",
  "primary_blocker": "STRATEGY | REGIME | FACTOR | DRAWDOWN | NONE",
  "eligible_strategies": 0,
  "capital_ceiling_available": 100.0,
  "reason": "Plain English explanation"
}
```

## Immutable Nature

This history is **read-only** for all observation tools. It serves as the "System Narrative" for why capital behaved (or didn't behave) in a certain way historically.
