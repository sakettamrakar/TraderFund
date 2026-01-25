# Strategy Layer Policy

**Status:** Constitutional — Binding  
**Scope:** Layer 10 — Strategy Governance  
**Authority:** This document defines what strategies are, how they exist, and when they may act. Violations mean the strategy is invalid, not the policy.

---

## 1. Definition of a Strategy

### What Qualifies as a Strategy

A **Strategy** is a permissioned intent to act within specific market conditions. It is:

1. **Governed** — Registered with explicit metadata and dependencies
2. **Constrained** — Operates only within permitted regimes and factor exposures
3. **Subordinate** — Consumes beliefs; does not produce or modify them
4. **Auditable** — Every activation, decision, and outcome is logged

### A Strategy is Permissioned Intent

```
Strategy = Belief Context + Factor Permission + Action Mapping

A strategy does NOT decide what is true.
A strategy decides what to DO given what is true.
```

### What Explicitly Does NOT Qualify as a Strategy

| Anti-Pattern | Why It's Not a Strategy |
|:-------------|:------------------------|
| Signal generator | Signals observe; strategies act on observations |
| Regime classifier | Regime is upstream epistemic layer, not strategy |
| Belief synthesizer | Beliefs are produced by Belief Layer (L9) |
| Optimizer | Optimization (L11) is downstream of strategy |
| Execution script | Execution (L12) implements strategy decisions |
| Heuristic | Heuristics without governance are not strategies |

**Invariant:** If it produces beliefs, classifies regime, or generates signals, it is NOT a strategy — even if it calls itself one.

---

## 2. Strategy Registration Requirements

### Required Metadata

Every strategy MUST be registered with:

```yaml
strategy_id: "STR-001"              # Unique identifier
strategy_name: "Momentum Breakout"  # Human-readable name
version: "1.0.0"                    # Semantic version
author: "human@org"                 # Human author (required)
created_at: "2026-01-24"            # Registration date
decision_ledger_ref: "D00X"         # Decision authorizing this strategy
status: "DRAFT | ACTIVE | SUSPENDED | RETIRED"
```

### Required Epistemic Dependencies

Every strategy MUST declare what beliefs it consumes:

```yaml
epistemic_dependencies:
  required:
    - regime_state       # From Regime Layer (L6)
    - belief_set         # From Belief Layer (L9)
  optional:
    - macro_state        # From Macro Layer (L5.5) when implemented
    - flow_state         # From Flow Layer (L5.7) when implemented
```

**Invariant:** A strategy with undeclared dependencies is INVALID.

### Required Factor Permissions

Every strategy MUST declare factor exposure requirements:

```yaml
factor_requirements:
  momentum: REQUIRED        # Strategy requires momentum permission
  value: NOT_REQUIRED       # Strategy does not use value signals
  volatility: CONDITIONAL   # Strategy may use if available
  
  max_exposure:
    momentum: 0.8           # Maximum factor load
```

**Invariant:** A strategy operating outside its declared factor permissions is INVALID.

### Required Task Graph Reference

Every strategy MUST map to a registered task graph:

```yaml
task_graph_ref: "TASK-GRAPH-MOMENTUM-V1"
skill_dependencies:
  - constraint_validator
  - cognitive_order_validator
```

---

## 3. Strategy Validation Rules

### Preconditions for Activation

A strategy may ONLY transition to ACTIVE when:

| Precondition | Validation |
|:-------------|:-----------|
| Decision Ledger entry exists | D00X authorizes this strategy |
| All required beliefs available | Belief Layer provides required inputs |
| Factor permissions granted | Factor Layer permits declared exposures |
| Regime compatibility satisfied | Current regime is in compatibility list |
| Task graph registered | Execution harness can invoke strategy |

### Epistemic Compatibility Checks

| Check | Enforcement |
|:------|:------------|
| Declared dependencies match actual consumption | Drift Validator (PD-1) |
| Strategy does not infer regime | Drift Validator (MF-3) |
| Strategy does not produce beliefs | Drift Validator (EH-1) |
| Strategy does not bypass factor permissions | Drift Validator (EH-2) |

### Prohibited Assumptions

Strategies must NOT assume:

| Prohibited Assumption | Required Behavior |
|:----------------------|:------------------|
| Regime is always known | Handle UNDEFINED regime explicitly |
| Beliefs are always fresh | Check staleness, handle degradation |
| Factor permissions always granted | Handle denial gracefully |
| Liquidity is always available | Respect Flow state when implemented |

---

## 4. Strategy Lifecycle States

### State Definitions

```
┌─────────┐
│  DRAFT  │  Strategy registered but not activated
└────┬────┘
     │ Activation approved
     ▼
┌─────────┐
│ ACTIVE  │  Strategy may generate decisions
└────┬────┘
     │ Violation or manual suspension
     ▼
┌───────────┐
│ SUSPENDED │  Strategy blocked from generating decisions
└────┬──────┘
     │ Cooldown complete or issue resolved
     ▼
┌─────────┐         ┌─────────┐
│ ACTIVE  │ ◄─or──► │ RETIRED │  Strategy permanently deactivated
└─────────┘         └─────────┘
```

### State Transition Rules

| From | To | Trigger | Authority |
|:-----|:---|:--------|:----------|
| DRAFT → ACTIVE | All preconditions met | Decision Ledger entry |
| ACTIVE → SUSPENDED | Violation detected | Automatic (validator) |
| ACTIVE → SUSPENDED | Manual intervention | Human operator |
| SUSPENDED → ACTIVE | Issue resolved | Human operator |
| SUSPENDED → RETIRED | Strategy deprecated | Decision Ledger entry |
| ACTIVE → RETIRED | Strategy deprecated | Decision Ledger entry |
| RETIRED → * | N/A | ❌ Forbidden — retirement is permanent |

### Cooldown (Optional)

If a strategy is suspended due to repeated violations:

```yaml
cooldown:
  enabled: true
  duration_hours: 24
  violation_threshold: 3
  reset_on_success: true
```

---

## 5. Activation & Suspension Rules

### What Activates a Strategy

A strategy is activated when:

1. **Human approval** — Decision Ledger entry (D00X) authorizes activation
2. **Preconditions met** — All validation checks pass
3. **Regime compatible** — Current regime is in strategy's compatibility list
4. **Factor permissions granted** — Factor Layer approves declared exposures

### What Forces Suspension

A strategy is AUTOMATICALLY suspended when:

| Trigger | Severity | Reinstatement |
|:--------|:---------|:--------------|
| Belief inference detected | CRITICAL | Human review required |
| Factor permission bypass | CRITICAL | Human review required |
| Regime incompatibility | WARNING | Automatic when regime changes |
| Staleness threshold exceeded | WARNING | Automatic when beliefs refresh |
| Repeated decision failures | WARNING | Cooldown period |

### What Is Explicitly Forbidden

> [!CAUTION]
> The following actions are FORBIDDEN for any strategy:

| Forbidden Action | Rationale |
|:-----------------|:----------|
| **Producing beliefs** | Beliefs come from L9; strategies consume |
| **Inferring regime** | Regime comes from L6; strategies receive |
| **Bypassing factor permissions** | Factor Layer is the authority |
| **Mutating epistemic state** | Epistemics are constitutional |
| **Self-activation** | Activation requires human authority |
| **Self-modification** | Strategy logic is frozen per version |
| **Overriding suspension** | Suspension requires human resolution |

---

## 6. Hard Invariants

The following rules are **non-negotiable**:

### STR-1: Strategies Cannot Infer Beliefs

```
Strategies receive beliefs as input.
Strategies do NOT compute, assume, or default beliefs.
If a required belief is missing, strategy MUST HALT, not guess.
```

### STR-2: Strategies Cannot Bypass Factor Permissions

```
Factor Layer grants permissions.
Strategies operate within granted permissions.
Exceeding permissions is a CRITICAL violation triggering suspension.
```

### STR-3: Strategies Cannot Mutate Epistemics

```
Epistemic documents are constitutional.
Strategies may not modify any epistemic state.
Output of strategies flows to Optimization/Execution, not back to epistemics.
```

### STR-4: Strategies Require Human Authorization

```
Every strategy requires:
  - Decision Ledger entry for registration
  - Decision Ledger entry for activation
  - Decision Ledger entry for retirement
No strategy may self-authorize.
```

### STR-5: Strategies Declare All Dependencies

```
Every belief, permission, and skill a strategy uses MUST be declared.
Undeclared dependencies are INVALID.
Discovered undeclared dependencies trigger suspension.
```

### STR-6: Strategy Logic Is Frozen Per Version

```
A strategy version is immutable once ACTIVE.
Changes require a new version with new Decision Ledger entry.
No hot-patching of active strategies.
```

---

## 7. Strategy Compatibility Matrix

### Regime Compatibility Declaration

Every strategy must declare regime compatibility:

```yaml
regime_compatibility:
  TRENDING_NORMAL_VOL: PERMITTED
  TRENDING_HIGH_VOL: RESTRICTED      # Reduced sizing
  MEAN_REVERTING_LOW_VOL: PROHIBITED
  MEAN_REVERTING_HIGH_VOL: PROHIBITED
  EVENT_DOMINANT: SUSPENDED          # Wait for resolution
  EVENT_LOCK: SUSPENDED
  UNDEFINED: PROHIBITED
```

### Compatibility Semantics

| Status | Meaning |
|:-------|:--------|
| PERMITTED | Strategy may operate normally |
| RESTRICTED | Strategy may operate with constraints (e.g., reduced size) |
| SUSPENDED | Strategy pauses until regime changes |
| PROHIBITED | Strategy is invalid for this regime |

---

## Appendix A: Strategy Registration Schema

```yaml
# Example Strategy Registration
strategy_id: "STR-001-MOM-BREAKOUT"
strategy_name: "Momentum Breakout V1"
version: "1.0.0"
author: "operator@traderfund"
created_at: "2026-01-24"
decision_ledger_ref: "D009"
status: "DRAFT"

epistemic_dependencies:
  required:
    - regime_state
    - belief_set
  optional:
    - macro_state

factor_requirements:
  momentum: REQUIRED
  value: NOT_REQUIRED
  volatility: CONDITIONAL
  max_exposure:
    momentum: 0.8

regime_compatibility:
  TRENDING_NORMAL_VOL: PERMITTED
  TRENDING_HIGH_VOL: RESTRICTED
  MEAN_REVERTING_LOW_VOL: PROHIBITED
  MEAN_REVERTING_HIGH_VOL: PROHIBITED
  EVENT_DOMINANT: SUSPENDED
  EVENT_LOCK: SUSPENDED
  UNDEFINED: PROHIBITED

task_graph_ref: "TASK-GRAPH-MOMENTUM-V1"
skill_dependencies:
  - constraint_validator
  - cognitive_order_validator
```

---

## Appendix B: Cross-Reference

| Related Document | Relationship |
|:-----------------|:-------------|
| [belief_layer_policy.md](file:///c:/GIT/TraderFund/docs/epistemic/belief_layer_policy.md) | Strategies consume beliefs from this layer |
| [factor_layer_policy.md](file:///c:/GIT/TraderFund/docs/epistemic/factor_layer_policy.md) | Strategies require factor permissions |
| [layer_interaction_contract.md](file:///c:/GIT/TraderFund/docs/contracts/layer_interaction_contract.md) | Defines allowed data flows |
| [execution_harness_contract.md](file:///c:/GIT/TraderFund/docs/contracts/execution_harness_contract.md) | Harness executes strategy decisions |
| [Regime_Taxonomy.md](file:///c:/GIT/TraderFund/docs/Regime_Taxonomy.md) | Defines regime states for compatibility |

---

## Version History

| Version | Date | Changes |
|:--------|:-----|:--------|
| v1.0 | 2026-01-24 | Initial Strategy Layer Policy |
