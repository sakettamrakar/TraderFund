# Evaluation Profile — Authoritative Schema

**Status**: Constitutional — Schema Definition  
**Version**: 1.0.0  
**Decision Reference**: D013  
**Date**: 2026-01-25

---

## 1. Purpose

This document defines the canonical schema for **Evaluation Profiles**—first-class configuration objects that parameterize EV-RUN execution without modifying the task graph.

### Core Semantics

| Principle | Description |
|:----------|:------------|
| **Profiles are Inputs** | Profiles configure execution; they are not tasks themselves. |
| **Profiles Parameterize, Not Expand** | A profile changes *how* EV-RUN operates, not *what* tasks exist. |
| **Profiles are Versioned** | Every profile has an immutable `profile_id` and `version`. |
| **Profiles are Auditable** | Every execution requires ledger + DID generation. |

---

## 2. Schema Definition (YAML)

```yaml
evaluation_profile:
  # ─────────────────────────────────────────────────────────────
  # IDENTITY
  # ─────────────────────────────────────────────────────────────
  profile_id: string          # Unique, immutable identifier (e.g., EV-HISTORICAL-ROLLING-V1)
  version: string             # Semantic version (e.g., 1.0.0)
  description: string         # Human-readable purpose statement

  # ─────────────────────────────────────────────────────────────
  # MODE
  # ─────────────────────────────────────────────────────────────
  mode:
    type: enum                # historical | forced_regime
                              # - historical: Observe and detect regime per window
                              # - forced_regime: Override regime classification

  # ─────────────────────────────────────────────────────────────
  # WINDOWING
  # ─────────────────────────────────────────────────────────────
  windowing:
    type: enum                # single | rolling | anchored
                              # - single: One evaluation window
                              # - rolling: Sliding windows with step
                              # - anchored: Fixed anchor dates
    window_size: duration     # ISO 8601 duration (e.g., 90d, P3M)
    step_size: duration | null  # Step between windows (rolling only)
    anchor_dates: [ISO8601] | null  # Specific dates (anchored only)

  # ─────────────────────────────────────────────────────────────
  # REGIME
  # ─────────────────────────────────────────────────────────────
  regime:
    detection: boolean        # If true, detect regime from data
    override:                 # Only valid if detection=false
      regime_code: string | null    # Forced regime code (e.g., BULL_CALM)
      rationale: string | null      # Why this regime is forced

  # ─────────────────────────────────────────────────────────────
  # FACTOR
  # ─────────────────────────────────────────────────────────────
  factor:
    observation: enum         # observe | disable
                              # - observe: Factors are read from data
                              # - disable: Factors are not loaded
    override: null            # EXPLICITLY FORBIDDEN — Factor forcing is not permitted

  # ─────────────────────────────────────────────────────────────
  # EXECUTION
  # ─────────────────────────────────────────────────────────────
  execution:
    shadow_only: true         # MANDATORY — No real execution permitted
    allow_replay: true        # Decision replay is permitted
    allow_parallel_windows: boolean  # Windows may run in parallel

  # ─────────────────────────────────────────────────────────────
  # OUTPUTS
  # ─────────────────────────────────────────────────────────────
  outputs:
    artifact_namespace: string      # Output path prefix (e.g., ev/historical/rolling/v1)
    persist_intermediate: boolean   # If true, save per-window artifacts

  # ─────────────────────────────────────────────────────────────
  # GOVERNANCE
  # ─────────────────────────────────────────────────────────────
  governance:
    decision_ref: D013        # Decision that authorizes this profile type
    ledger_required: true     # MANDATORY — Ledger entry per execution
    did_required: true        # MANDATORY — DID per execution

  # ─────────────────────────────────────────────────────────────
  # INVARIANTS
  # ─────────────────────────────────────────────────────────────
  invariants:
    forbid_real_execution: true       # ABSOLUTE — No real market interaction
    forbid_strategy_mutation: true    # ABSOLUTE — Strategies are read-only
    forbid_regime_fallback: true      # ABSOLUTE — No default regime on failure
```

---

## 3. Field Constraints

### 3.1 Required Fields

All top-level fields are **required**. A profile missing any field is **invalid**.

### 3.2 Mode Constraints

| Mode | Detection | Override |
|:-----|:----------|:---------|
| `historical` | Must be `true` | Must be `null` |
| `forced_regime` | Must be `false` | Must specify `regime_code` |

### 3.3 Windowing Constraints

| Type | window_size | step_size | anchor_dates |
|:-----|:------------|:----------|:-------------|
| `single` | Required | `null` | `null` |
| `rolling` | Required | Required | `null` |
| `anchored` | Required | `null` | Required (non-empty) |

### 3.4 Immutable Invariants

The following fields are **hard-coded** and cannot be overridden:

| Field | Value | Rationale |
|:------|:------|:----------|
| `execution.shadow_only` | `true` | D013 authorizes shadow execution only |
| `factor.override` | `null` | Factor forcing violates epistemic policy |
| `governance.ledger_required` | `true` | All executions must be audited |
| `governance.did_required` | `true` | All executions require impact declaration |
| `invariants.*` | All `true` | These are non-negotiable safety constraints |

---

## 4. Output Structure

Profile execution produces artifacts under:

```
docs/evolution/evaluation/{artifact_namespace}/{window_id}/
```

### Window ID Format

```
WINDOW-{start_date}-{end_date}
```

Example: `WINDOW-2023-01-01-2023-03-31`

### Context Path

Each window produces a regime context at:

```
docs/evolution/context/{profile_id}/{window_id}/regime_context.json
```

---

## 5. Validation Rules

A profile loader MUST enforce:

1. **Schema Completeness**: All required fields present
2. **Mode Consistency**: Detection/Override match mode type
3. **Windowing Validity**: Type-specific fields are present
4. **Invariant Integrity**: All invariants are `true`
5. **Decision Reference**: `governance.decision_ref` is a valid, committed decision

### Failure Behavior

| Condition | Result |
|:----------|:-------|
| Missing required field | `ProfileValidationError` — HARD FAILURE |
| Invalid mode/detection combo | `ProfileValidationError` — HARD FAILURE |
| Invariant set to `false` | `ProfileValidationError` — HARD FAILURE |
| Invalid decision reference | `ProfileValidationError` — HARD FAILURE |

---

## 6. Governance Integration

### Per-Execution Requirements

Every profile execution MUST produce:

1. **Ledger Entry** in `docs/epistemic/ledger/evolution_log.md`:
   - `profile_id`, `version`
   - Execution timestamp
   - Window range
   - Outcome (SUCCESS/FAILURE)

2. **Documentation Impact Declaration (DID)** in `docs/impact/`:
   - Links to profile definition
   - Links to generated artifacts
   - Regime(s) evaluated
   - Window count

### Evidence Chain

```
Profile Definition → Profile Execution → Regime Context(s) → EV-RUN Artifacts → Ledger + DID
```

---

## 7. Relationship to Task Graph

```
┌─────────────────────────────────────────────────────────────┐
│                     TASK GRAPH (FROZEN)                     │
│                                                             │
│   EV-RUN-0 ─► EV-RUN-1 ─► EV-RUN-2 ─► ... ─► EV-RUN-6      │
│                                                             │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ parameterizes
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   EVALUATION PROFILE                        │
│                                                             │
│   • Mode (historical/forced)                                │
│   • Windowing (rolling/anchored)                            │
│   • Regime (detect/override)                                │
│   • Output namespace                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Key Invariant**: Profiles do NOT add tasks. They configure how existing tasks behave.

---

## 8. Change Log

| Version | Date | Changes |
|:--------|:-----|:--------|
| 1.0.0 | 2026-01-25 | Initial schema definition |
