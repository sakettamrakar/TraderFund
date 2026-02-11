# Component Health Contract
# Authority: Canonical — All components MUST implement this interface.
# Created: 2026-02-11

## Purpose

Every component in the cognitive hierarchy MUST expose a uniform health interface.
This contract ensures that degradation, failure, and recovery are observable, traceable,
and mechanically detectable — not inferred from silence.

---

## Required Health Fields

Every component MUST expose the following fields:

| Field | Type | Description |
|:---|:---|:---|
| `health_status` | `OK \| DEGRADED \| FAILED` | Current operational state of the component. |
| `last_success_timestamp` | `ISO-8601 UTC` | Timestamp of the last successful execution cycle. |
| `failure_count` | `int (≥ 0)` | Consecutive failure count since last OK state. |
| `degraded_reason` | `string \| null` | Human-readable reason if status is DEGRADED. Null when OK. |

---

## State Definitions

### OK

The component completed its most recent execution cycle without errors.
All invariants hold. Outputs are valid and within expected latency.

### DEGRADED

The component is operational but one or more of the following conditions apply:

- **Partial Input**: One or more upstream inputs are stale, incomplete, or missing.
- **Latency Breach**: Execution time exceeds the component's declared SLA.
- **Confidence Drop**: Output confidence scores fall below the declared minimum threshold.
- **Upstream Degradation**: A direct upstream component reports DEGRADED or FAILED.

When DEGRADED, the component MUST:
1. Continue producing output (best-effort).
2. Set `degraded_reason` to a non-null descriptive string.
3. Tag all outputs with `degraded: true` metadata.

### FAILED

The component cannot produce valid output. One or more of the following conditions apply:

- **Critical Input Missing**: A mandatory upstream input is unavailable.
- **Invariant Violation**: A declared invariant is breached.
- **Unrecoverable Error**: An exception or crash prevents execution.
- **Consecutive Failure Threshold**: `failure_count` exceeds the component's declared `max_consecutive_failures` (default: 3).

When FAILED, the component MUST:
1. Stop producing output (Fail-Closed).
2. Emit a `COMPONENT_FAILED` event to the observability bus.
3. Increment `failure_count`.

---

## Recovery Detection

A component transitions from FAILED → OK when:

1. All mandatory upstream inputs are available and fresh.
2. The component completes a full execution cycle without error.
3. All declared invariants hold.
4. `failure_count` resets to 0.

A component transitions from DEGRADED → OK when:

1. All conditions that caused DEGRADED are resolved.
2. `degraded_reason` is set back to null.

Recovery MUST be logged with the same visibility as failure.

---

## Required Observability Signals

Every component MUST emit:

| Signal | Type | Frequency |
|:---|:---|:---|
| `health.status` | Gauge (`OK=0, DEGRADED=1, FAILED=2`) | Every execution cycle |
| `health.last_success` | Timestamp | On each OK cycle |
| `health.failure_count` | Counter | On each failure |
| `health.degraded_reason` | String event | On DEGRADED entry/change |
| `health.recovery` | Event | On transition from DEGRADED/FAILED → OK |
| `health.latency_ms` | Histogram | Every execution cycle |

---

## Integration with Existing Component YAML

Each component YAML in `docs/memory/05_components/` MUST include:

```yaml
health_contract: docs/memory/05_components/component_health_contract.md

health_fields:
  - health_status
  - last_success_timestamp
  - failure_count
  - degraded_reason

health_observability:
  - health.status
  - health.last_success
  - health.failure_count
  - health.degraded_reason
  - health.recovery
  - health.latency_ms

health_invariants:
  - Health status must be evaluated every execution cycle.
  - FAILED status must trigger Fail-Closed behavior.
  - Recovery must be logged with equal visibility to failure.
  - degraded_reason must be non-null when status is DEGRADED.
```

---

## Non-Goals

- This contract does NOT define component-specific invariants (those remain in each YAML).
- This contract does NOT define alerting thresholds (those belong in observability configuration).
- This contract does NOT replace failure_modes (those are component-specific scenarios).

---

*Authority: Canonical. All components MUST comply.*

## Reference Implementation

For a canonical example of this contract in action, see:
- **Source**: `src/layers/macro_layer.py` (Class `MacroLayer`, `ComponentHealth`)
- **Tests**: `tests/test_macro_layer.py`

