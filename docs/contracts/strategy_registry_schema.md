# Strategy Registry Schema

**Status**: Constitutional — Frozen  
**Scope**: Strategy Plane (Phase 3)  
**Governing Decision**: D011  
**Date**: 2026-01-25

---

## 1. Purpose

This document defines the **conceptual schema** for the Strategy Registry—the only legal place where strategies may exist. The registry enforces governance, lifecycle discipline, and prevents executable or inferential logic from entering the strategy layer.

**Guiding Principle**: If a strategy can execute, it does not belong in the registry.

---

## 2. Registry Entry Schema

### 2.1 Identity Block

| Field | Type | Required | Description |
|:------|:-----|:---------|:------------|
| `strategy_id` | String | YES | Unique, stable identifier (e.g., `STR-001`). Immutable after registration. |
| `name` | String | YES | Human-readable name. Mutable via lifecycle transition. |
| `version` | SemVer | YES | Semantic version (`MAJOR.MINOR.PATCH`). New version = new entry. |
| `owner` | String | YES | Human author responsible for the strategy. |

**Invariants**:
- `strategy_id` MUST be unique across all registry entries.
- `version` changes create new registry entries (immutable versions).

---

### 2.2 Governance Block

| Field | Type | Required | Description |
|:------|:-----|:---------|:------------|
| `lifecycle_state` | Enum | YES | One of: `DRAFT`, `ACTIVE`, `SUSPENDED`, `RETIRED`. |
| `created_at` | Timestamp | YES | Registration timestamp. Immutable. |
| `created_under_decision` | DecisionRef | YES | Reference to authorizing decision (e.g., `D011`). |
| `last_modified_at` | Timestamp | YES | Last lifecycle transition timestamp. |
| `last_modified_decision` | DecisionRef | NO | Decision authorizing the last transition (if any). |

**Lifecycle State Definitions**:

| State | Meaning | Executable | Transitions To |
|:------|:--------|:-----------|:---------------|
| `DRAFT` | Under development, not yet authorized for execution. | NO | `ACTIVE`, `RETIRED` |
| `ACTIVE` | Authorized for execution via Orchestration Plane. | YES (via harness) | `SUSPENDED`, `RETIRED` |
| `SUSPENDED` | Temporarily disabled, can be resumed. | NO | `ACTIVE`, `RETIRED` |
| `RETIRED` | Permanently invalid. Cannot be reinstated. | NO | *(terminal)* |

**Invariants**:
- Strategies MUST begin in `DRAFT` state.
- Transition from `DRAFT` to `ACTIVE` requires a Decision Ledger entry.
- `RETIRED` is permanent and irreversible.

---

### 2.3 Epistemic Dependencies Block

| Field | Type | Required | Description |
|:------|:-----|:---------|:------------|
| `required_beliefs` | List[BeliefRef] | YES | Beliefs the strategy depends on (e.g., `regime.current`, `macro.inflation_trend`). |
| `required_policies` | List[PolicyRef] | YES | Policies that govern this strategy (e.g., `factor_layer_policy`, `strategy_layer_policy`). |
| `required_factors` | List[FactorPermission] | YES | Factor permissions required (e.g., `momentum_permitted: true`). |

**Invariants**:
- Strategies CANNOT execute without all `required_beliefs` available.
- Strategies CANNOT execute without all `required_factors` granted.
- References are declarative—strategies do not compute these values.

---

### 2.4 Orchestration Binding Block

| Field | Type | Required | Description |
|:------|:-----|:---------|:------------|
| `task_graph_ref` | TaskGraphRef | YES | Reference to the execution graph (e.g., `graph:momentum_alpha_v1`). |
| `allowed_selectors` | List[SelectorType] | NO | Selectors permitted for this strategy (e.g., `range`, `list`). Default: all. |
| `forbidden_selectors` | List[SelectorType] | NO | Selectors explicitly forbidden (e.g., `first_n` for critical strategies). |
| `execution_mode` | Enum | NO | Preferred mode: `DRY_RUN` or `REAL_RUN`. Default: `DRY_RUN`. |

**Invariants**:
- `task_graph_ref` MUST reference a valid, registered task graph.
- Strategies CANNOT be bound to undeclared or orphan task graphs.
- Execution mode is advisory; harness has final authority.

---

### 2.5 Audit & Provenance Block

| Field | Type | Required | Description |
|:------|:-----|:---------|:------------|
| `registration_ledger_entry` | LedgerRef | YES | Ledger entry created on registration. |
| `dids` | List[DIDRef] | YES | DIDs generated for this strategy (one per lifecycle transition). |
| `audit_log` | List[AuditEntry] | YES | Immutable log of all state changes. |

**Invariants**:
- Every registration creates a Ledger entry.
- Every lifecycle transition creates a DID.
- Audit log is append-only.

---

## 3. Prohibited Fields (Explicit)

The following fields are **FORBIDDEN** in any registry entry:

| Prohibited | Rationale |
|:-----------|:----------|
| `logic` | Strategies do not execute. |
| `signals` | Signal generation is upstream (Belief Layer). |
| `indicators` | Indicator computation is upstream. |
| `thresholds` | Conditional thresholds imply logic. |
| `conditions` | Conditional branching implies logic. |
| `functions` | Callable functions imply execution. |
| `imports` | Code imports imply execution context. |
| `market_data` | Market data access implies computation. |

**Validation**: Any registry entry containing these fields is INVALID and rejected.

---

## 4. Validation Rules

### 4.1 Registration Validation

| Rule ID | Rule | Enforcement |
|:--------|:-----|:------------|
| **REG-1** | All required fields must be present. | Schema validation on registration. |
| **REG-2** | `lifecycle_state` must be `DRAFT` on initial registration. | State machine enforcement. |
| **REG-3** | `created_under_decision` must reference a valid Decision. | Ledger cross-reference. |
| **REG-4** | `task_graph_ref` must reference a registered task graph. | Registry cross-reference. |
| **REG-5** | No prohibited fields may be present. | Static analysis on registration. |

### 4.2 Lifecycle Transition Validation

| Rule ID | Rule | Enforcement |
|:--------|:-----|:------------|
| **LCT-1** | Transition requires `last_modified_decision` reference. | Ledger enforcement. |
| **LCT-2** | Transition must follow valid state machine edges. | State machine enforcement. |
| **LCT-3** | `RETIRED` is terminal; no further transitions allowed. | State machine enforcement. |
| **LCT-4** | `ACTIVE` strategies cannot be deleted, only `RETIRED`. | Registry protection. |

### 4.3 Execution Validation

| Rule ID | Rule | Enforcement |
|:--------|:-----|:------------|
| **EXE-1** | Only `ACTIVE` strategies may be executed. | Harness pre-check. |
| **EXE-2** | All `required_beliefs` must be available. | Belief Layer check. |
| **EXE-3** | All `required_factors` must be granted. | Factor Layer check. |
| **EXE-4** | Execution mode must respect harness authority. | Harness override. |

---

## 5. Audit & Provenance Behavior

### 5.1 On Registration

1. Create Ledger entry with strategy metadata.
2. Generate DID for `DRAFT` state.
3. Initialize audit log with registration event.

### 5.2 On Lifecycle Transition

1. Validate transition against state machine.
2. Create Ledger entry for transition decision.
3. Generate new DID for new state.
4. Append transition to audit log.

### 5.3 Immutability Rules

| Data | Mutability |
|:-----|:-----------|
| `strategy_id` | Immutable |
| `version` | Immutable (new version = new entry) |
| `created_at` | Immutable |
| `created_under_decision` | Immutable |
| `audit_log` | Append-only |
| `lifecycle_state` | Mutable via governed transition |
| `name` | Mutable via governed transition |

---

## 6. Cross-Reference

| Document | Relationship |
|:---------|:-------------|
| [D011](file:///c:/GIT/TraderFund/docs/impact/2026-01-25__decision__D011_strategy_plane_authorization.md) | Governing decision |
| [strategy_layer_policy.md](file:///c:/GIT/TraderFund/docs/epistemic/strategy_layer_policy.md) | Policy constraints |
| [strategy_plane_obligations.md](file:///c:/GIT/TraderFund/docs/epistemic/governance/strategy_plane_obligations.md) | Obligation bindings |
| [execution_harness_contract.md](file:///c:/GIT/TraderFund/docs/contracts/execution_harness_contract.md) | Execution interface |
