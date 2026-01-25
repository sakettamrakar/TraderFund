# Layer Interaction Contract

**Status:** Constitutional — Binding  
**Scope:** Architecture — Execution Constraints  
**Authority:** This document is the authoritative contract for all layer interactions. Violation means the skill is wrong, not the contract.

---

## Purpose

This document defines the allowed and prohibited data flows between layers of the investment intelligence system. It serves as a binding contract that all future execution skills, harnesses, and decision pipelines MUST obey.

> [!CAUTION]
> This is not a guideline. This is a constraint. Code that violates these contracts is architecturally invalid and must be rejected at review.

---

## Layer Ordering

### Canonical Layer Sequence

```
Zone A: Structural Backbone (Truth)
  L1: Reality Layer (Ingestion)
  L2: Time Layer (Alignment)
  L3: Object Layer (Identity)
  L4: Feature Layer (Measurement)

Zone B: Interpretive Intelligence (Understanding)
  L5:   Event Layer (Detection)
  L5.5: Macro Layer [LATENT]
  L5.7: Flow Layer [LATENT]
  L5.8: Volatility Geometry Layer [LATENT]
  L6:   Regime Layer (Environment)
  L6.5: Factor Layer [LATENT]
  L7:   Narrative Layer (Context)
  L8:   Signal Layer (Observation)
  L9:   Belief Layer (Synthesis)

Zone C: Expression & Execution (Action)
  L10: Strategy Layer (Alpha)
  L11: Optimization Layer (Sizing)
  L12: Execution Layer (Transacting)
  L13: Settlement Layer (Realization)
  L14: Audit Layer (Memory)
```

---

## Allowed Direction of Influence

### Data Flow Rules

```
ALLOWED: Data flows DOWN the stack
         L1 → L2 → L3 → L4 → L5 → L6 → L7 → L8 → L9 → L10 → L11 → L12 → L13 → L14

PROHIBITED: Data flowing UP the stack (reverse dependency)
            L10 → L6 is FORBIDDEN
            
PROHIBITED: Data skipping layers (bypass)
            L4 → L8 without L6 context is FORBIDDEN
```

### Context Enrichment

Each layer receives data from upstream and ENRICHES it with its own computation before passing downstream:

```
L4 (Features) → L6 (Regime) → L8 (Signals)

Signal receives:
  - Raw feature values (from L4)
  - Regime context (from L6)
  - Factor permissions (from L6.5)

Signal MUST NOT receive:
  - Direct raw data bypassing regime
  - Execution feedback changing signal logic
```

---

## Prohibited Bypasses

These specific bypasses are explicitly forbidden:

### BAN-1: Signals Must Not Infer Regime Directly

```
FORBIDDEN:
  Signal Layer computing "if volatility > X, assume HIGH_VOL regime"

REQUIRED:
  Signal Layer receiving regime state from Regime Layer as input
```

**Rationale:** Regime classification is a distinct responsibility. Signals that infer regime are conflating two layers and creating hidden dependencies.

### BAN-2: Strategies Must Not Query Macro State Directly

```
FORBIDDEN:
  Strategy Layer calling macro_state_service.get_current_state()

REQUIRED:
  Strategy Layer receiving macro context via Regime Layer
```

**Rationale:** Macro state flows through Regime. Strategies accessing Macro directly create a bypass around Regime's gating function.

### BAN-3: Execution Must Not Evaluate Signal Confidence

```
FORBIDDEN:
  Execution Layer filtering signals by confidence score

REQUIRED:
  Belief Layer filtering signals; Execution receives only approved beliefs
```

**Rationale:** Confidence evaluation is the Belief Layer's responsibility. Execution should execute, not evaluate.

### BAN-4: No Layer May Mutate Upstream State

```
FORBIDDEN:
  Strategy Layer modifying regime_state object
  Execution Layer writing to signal database
  
REQUIRED:
  All upstream state is immutable from downstream perspective
```

**Rationale:** Downstream layers consume upstream state; they do not modify it. Modification creates feedback loops that corrupt the cognitive hierarchy.

---

## Communication Mechanisms

### 1. State Objects

Layers communicate via **immutable state snapshots**:

```python
class RegimeState:
    timestamp: datetime
    behavior: str           # TRENDING_NORMAL_VOL, etc.
    bias: str               # BULLISH, BEARISH, NEUTRAL
    confidence: float
    is_stable: bool
    # State objects are frozen after creation
```

**Rules:**
- State objects are frozen after creation
- Downstream layers receive copies, not references
- No downstream layer may modify a state object

### 2. Permission Flags

Constraint layers (Factor, Regime) issue **permission flags**:

```python
class FactorPermission:
    momentum_permitted: bool
    value_permitted: bool
    max_exposure: Dict[str, float]
```

**Rules:**
- Permission flags are binary grants
- Downstream layers MUST check permissions before proceeding
- Absence of permission = denial (fail-closed)

### 3. Context Wrappers

Data passed between layers is wrapped in **context envelopes**:

```python
class ContextualSignal:
    signal: Signal
    regime_context: RegimeState
    factor_permission: FactorPermission
    macro_state: MacroState  # When implemented
    flow_state: FlowState    # When implemented
```

**Rules:**
- Raw data must not be passed without context
- Context wrappers enable auditability
- Missing context fields default to "degraded confidence"

---

## Invariants for Execution Code

These invariants MUST be enforced by any execution harness:

### EXE-1: Every Signal Must Carry Regime Context

```python
# VALID
signal = Signal(data, regime_context=current_regime)

# INVALID - missing context
signal = Signal(data)
```

### EXE-2: Every Trade Proposal Must Carry Factor Permission

```python
# VALID
proposal = TradeProposal(signal, factor_permission=permission)

# INVALID - missing permission
proposal = TradeProposal(signal)
```

### EXE-3: Every Execution Must Be Traceable to Source Layer

```python
# Required audit fields
execution.source_signal_id
execution.source_regime_state_id
execution.source_belief_id
```

### EXE-4: No Execution May Proceed if Upstream Confidence is Degraded

```python
if regime_state.confidence < MIN_REGIME_CONFIDENCE:
    raise ExecutionBlocked("Regime confidence too low")

if factor_permission.size_multiplier == 0:
    raise ExecutionBlocked("Factor layer blocked execution")
```

---

## Feedback Channels (The Exception)

While data flows down, there are specific **feedback channels** that flow up to DESIGN, not STATE:

| Channel | Direction | Purpose |
|:--------|:----------|:--------|
| Performance Attribution | L13 → Design | Did the system make money? |
| Regret Analysis | L12 → Design | Did blocking decisions save money? |
| Drift Detection | L14 → Design | Is the system behaving as designed? |

**Critical Distinction:**
- Feedback influences future DESIGN (human review, parameter tuning)
- Feedback does NOT influence current STATE (no real-time adaptation)

---

## Enforcement Points

| Layer | Enforcement Responsibility |
|:------|:---------------------------|
| Signal Layer | Verify regime context is present before processing |
| Belief Layer | Verify factor permissions before synthesis |
| Strategy Layer | Verify belief confidence meets threshold |
| Execution Layer | Verify all upstream contexts are valid and not stale |

---

## Version History

| Version | Date | Changes |
|:--------|:-----|:--------|
| v1.0 | 2026-01-24 | Initial layer interaction contract |
