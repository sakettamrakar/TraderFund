# Multi-Strategy Coexistence Policy

**Status**: Constitutional — Frozen  
**Scope**: Scale & Safety Plane (SS)  
**Governing Decision**: D012.5  
**Date**: 2026-01-25

---

## 1. Purpose

This policy defines the rules for multi-strategy coexistence within a shared belief and permission space. It ensures that:

- Multiple strategies can operate without conflict
- Resource contention is managed deterministically
- No strategy can monopolize system resources
- Failure isolation is maintained

---

## 2. Coexistence Rules

### 2.1 Resource Isolation

| Rule ID | Rule | Enforcement |
|:--------|:-----|:------------|
| **COE-1** | Each strategy operates in an isolated execution context. | Harness enforcement. |
| **COE-2** | Strategies cannot directly communicate with each other. | Static analysis. |
| **COE-3** | Shared state access is read-only and via approved API only. | API enforcement. |

### 2.2 Belief Space Rules

| Rule ID | Rule | Enforcement |
|:--------|:-----|:------------|
| **BEL-COE-1** | Multiple strategies may read the same belief. | Permitted. |
| **BEL-COE-2** | No strategy may modify a belief. | Belief Layer is read-only. |
| **BEL-COE-3** | Conflicting belief dependencies are flagged at registration. | Registry validation. |

### 2.3 Permission Space Rules

| Rule ID | Rule | Enforcement |
|:--------|:-----|:------------|
| **PER-COE-1** | Factor permissions are shared, not exclusive. | Policy design. |
| **PER-COE-2** | Permission denial for one strategy does not affect others. | Isolation. |
| **PER-COE-3** | Permission revocation affects only the target strategy. | Revocation API. |

### 2.4 Conflict Detection

| Conflict Type | Detection | Resolution |
|:--------------|:----------|:-----------|
| **Resource Contention** | Bounds check at registration. | Reject if limits exceeded. |
| **Belief Conflict** | Dependency graph analysis. | Flag but allow with warning. |
| **Permission Overlap** | Registry scan. | Permitted (non-exclusive). |

---

## 3. Hard Limits (Coexistence Bounds)

| Limit | Value | Authority |
|:------|:------|:----------|
| **MAX_ACTIVE_STRATEGIES** | 10 | D012.5 |
| **MAX_CONCURRENT_EXECUTIONS** | 5 | D012.5 |
| **MAX_SHARED_BELIEFS** | 50 | Policy |
| **MAX_PERMISSION_REQUESTS** | 100/hour | Policy |

These limits are **non-configurable at runtime** without D-level authorization.

---

## 4. Kill-Switch Integration

When the global kill-switch is activated:

1. All strategies transition to SUSPENDED immediately.
2. No new strategy execution may begin.
3. Coexistence state is frozen for audit.
4. Manual reset required for recovery.

---

## 5. Cross-Reference

| Document | Relationship |
|:---------|:-------------|
| [D012.5](file:///c:/GIT/TraderFund/docs/impact/2026-01-25__decision__D012.5_scale_safety_authorization.md) | Governing decision |
| [scale_safety_obligations.md](file:///c:/GIT/TraderFund/docs/epistemic/governance/scale_safety_obligations.md) | Obligation bindings |
| [strategy_registry_schema.md](file:///c:/GIT/TraderFund/docs/contracts/strategy_registry_schema.md) | Registry constraints |
