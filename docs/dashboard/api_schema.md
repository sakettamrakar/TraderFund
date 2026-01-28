# Dashboard API Schema (Read-Only)

**Base URL**: `/api`
**Version**: v1
**Governance**: `OBL-DASHBOARD-READ-ONLY`

## 1. System Status
**Endpoint**: `GET /system/status`
**Description**: High-level system state based on the latest EV-TICK execution.

**Response**:
```json
{
  "system_state": "IDLE | OBSERVING | READY | ACTIVE",
  "reason": "String explaining the state (e.g., 'No expansion detected')",
  "last_ev_tick": "ISO8601 Timestamp (e.g., 2026-01-27T22:00:00)",
  "last_ingestion": "ISO8601 Timestamp or 'N/A'",
  "governance_status": "CLEAN | WARNING | ERROR"
}
```

## 2. Layer Health
**Endpoint**: `GET /layers/health`
**Description**: Status of critical data layers (Freshness check).

**Response**:
```json
{
  "layers": [
    {
      "name": "Regime Context",
      "last_updated": "ISO8601 Timestamp",
      "status": "OK | STALE | ERROR"
    },
    {
      "name": "Momentum Watcher",
      "last_updated": "ISO8601 Timestamp",
      "status": "OK | STALE | ERROR"
    }
    // ... other layers
  ]
}
```

## 3. Market Structure Snapshot
**Endpoint**: `GET /market/snapshot`
**Description**: Aggregated diagnostic states from the latest tick.

**Response**:
```json
{
  "regime": { 
      "state": "BULL_VOL", 
      "confidence": 0.82 
  },
  "liquidity": { 
      "state": "NEUTRAL", 
      "confidence": 0.74,
      "note": "Optional details"
  },
  "dispersion": { 
      "state": "STABLE", 
      "confidence": 0.69 
  },
  "momentum": { 
      "state": "ABSENT", 
      "confidence": 0.77 
  },
  "expansion": {
      "state": "NONE",
      "confidence": 0.0
  }
}
```

## 4. Watcher Timeline
**Endpoint**: `GET /watchers/timeline`
**Description**: Historical states of watchers for the last N ticks.

**Parameters**:
- `limit` (optional): Number of ticks to return (default 10).

**Response**:
```json
{
  "history": [
    { 
      "timestamp": "2026-01-27T22:00:00", 
      "momentum": "NONE", 
      "expansion": "NONE",
      "dispersion": "NONE",
      "liquidity": "NEUTRAL"
    }
    // ... older ticks
  ]
}
```

## 5. Strategy Eligibility
**Endpoint**: `GET /strategies/eligibility`
**Description**: Theoretical eligibility of strategies based *strictly* on observed state.

**Response**:
```json
{
  "strategies": [
    {
      "id": "STRATEGY_MOMENTUM_V1",
      "name": "Momentum (V1)",
      "regime_ok": true,
      "factor_ok": false,
      "eligible": false,
      "blocked_by": "Momentum neutral & flat"
    }
  ]
}
```

## 6. Meta-Analysis Summary
**Endpoint**: `GET /meta/summary`
**Description**: Summary content from the latest Meta-Analysis artifact.

**Response**:
```json
{
  "content": "Markdown string of evolution_comparative_summary.md",
  "key_findings": ["List of extracted findings..."], 
  "what_changed": ["List of changes..."]
}
```

## 7. Activation Conditions
**Endpoint**: `GET /system/activation_conditions`
**Description**: Static epistemic rules defining what is required for activation.

**Response**:
```json
{
  "momentum": [
    "ExpansionTransition != NONE",
    "DispersionBreakout != NONE",
    "MomentumEmergence != NONE"
  ]
}
```
