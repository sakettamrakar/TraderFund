# Belief Layer Policy

**Status:** Constitutional — Binding  
**Scope:** Layer 9 — Belief Synthesis  
**Authority:** This document defines what beliefs are, who may produce them, and how they may change. Violations mean the code is wrong, not the policy.

---

## 1. Definition of a Belief

### What Qualifies as a Belief

A **Belief** is a slow-moving, high-confidence assertion about market state that:

1. **Describes reality** — It claims something true about the current environment
2. **Has upstream provenance** — It is derived from observations, not invented
3. **Is inspectable** — Its origin, confidence, and age are always visible
4. **Is stable** — It changes only when evidence changes

### Belief vs Signal vs Observation

| Concept | Layer | Temporal Characteristic | Example |
|:--------|:------|:------------------------|:--------|
| **Observation** | L5 (Event) | Instantaneous | "Price crossed VWAP at 10:32" |
| **Signal** | L8 (Signal) | Short-lived | "Bullish momentum detected" |
| **Belief** | L9 (Belief) | Persistent | "Market is in TRENDING regime" |

**Key Distinctions:**

```
Observation: "What just happened?"
Signal:      "What might this mean?"
Belief:      "What do we know to be true?"
```

### What a Belief is NOT

| Anti-Pattern | Why It's Wrong |
|:-------------|:---------------|
| Prediction | Beliefs describe current state, not future state |
| Optimization | Beliefs are not tuned for profit |
| Opinion | Beliefs require evidence, not preference |
| Strategy | Beliefs do not prescribe action |

---

## 2. Belief Sources

### Layers That May PRODUCE Beliefs

| Layer | May Produce | Belief Type | Rationale |
|:------|:------------|:------------|:----------|
| L5.5 Macro Layer | ✅ Yes | `macro_state` | Systemic liquidity and policy environment |
| L6 Regime Layer | ✅ Yes | `regime_state` | Behavioral classification of market |
| L7 Narrative Layer | ✅ Yes | `narrative_context` | Contextual framing of events |
| L9 Belief Layer | ✅ Yes | Synthesized beliefs | Combination of upstream beliefs |

### Layers That May CONSUME Beliefs

| Layer | May Consume | Purpose |
|:------|:------------|:--------|
| L8 Signal Layer | ✅ Yes | Context for signal validity |
| L9 Belief Layer | ✅ Yes | Synthesis input |
| L10 Strategy Layer | ✅ Yes | Gating and compatibility |
| L11 Optimization Layer | ✅ Yes | Risk parameter adjustment |
| L12 Execution Layer | ✅ Yes | Execution blocking |

### Explicit Prohibitions

> [!CAUTION]
> The following layers are FORBIDDEN from producing beliefs:

| Layer | Prohibited Action | Rationale |
|:------|:------------------|:----------|
| L8 Signal Layer | ❌ Cannot produce beliefs | Signals observe, they do not assert truth |
| L10 Strategy Layer | ❌ Cannot produce beliefs | Strategies consume beliefs to act |
| L11 Optimization Layer | ❌ Cannot produce beliefs | Optimization is downstream of belief |
| L12 Execution Layer | ❌ Cannot produce beliefs | Execution is terminal, not cognitive |

**Invariant:** Data flows DOWN the stack. Beliefs flow from interpretive layers (L5.5-L7) into the Belief Layer (L9), then downstream to action layers. Reverse flow is forbidden.

---

## 3. Belief Synthesis Rules

### When Beliefs May Be Combined

Beliefs may be synthesized when:

1. **All upstream beliefs are present** — No synthesis with missing inputs
2. **All upstream beliefs are not stale** — Staleness triggers degradation, not synthesis
3. **Combination rules are explicit** — No implicit or ad-hoc synthesis

### Synthesis Modes

| Mode | Description | Example |
|:-----|:------------|:--------|
| **Conjunction** | All beliefs must agree | Regime=TRENDING AND Macro=EXPANSIONARY → Strong conviction |
| **Conditional** | One belief modifies another | Regime=TRENDING, but Macro=UNKNOWN → Degraded confidence |
| **Override** | Higher-layer belief supersedes | Macro=CRISIS overrides Regime=NORMAL |

### When Beliefs Must Remain Independent

Beliefs must NOT be combined when:

1. **Upstream layers are conceptually orthogonal** — e.g., Flow state is not a modifier of Regime
2. **Combination would create circular dependency** — Belief A depends on B depends on A
3. **No explicit synthesis rule exists** — Default is separation

### Conflict Handling

| Conflict Type | Resolution |
|:--------------|:-----------|
| **Upstream disagreement** | Degrade confidence, do not force agreement |
| **Stale vs fresh** | Prefer fresh, log staleness as degradation reason |
| **Missing upstream** | Do not synthesize; return partial belief with explicit gaps |

**Invariant:** The Belief Layer never "decides" between conflicting inputs. It degrades confidence and surfaces the conflict for human review.

---

## 4. Belief Mutation Constraints

### Who May Update Beliefs

| Entity | May Update | Constraints |
|:-------|:-----------|:------------|
| Upstream producing layer | ✅ Yes | Only via new snapshot, not mutation |
| Belief Layer (synthesis) | ✅ Yes | Only via declared synthesis rules |
| Downstream layers | ❌ No | Consumption is read-only |
| Skills | ❌ No | Skills observe beliefs, never modify |
| Execution harness | ❌ No | Harness consumes, never produces |

### Temporal Constraints

| Category | Update Frequency | Rationale |
|:---------|:-----------------|:----------|
| **Macro beliefs** | Hours to days | Macro conditions are slow-moving |
| **Regime beliefs** | Minutes to hours | Regime transitions are deliberate |
| **Narrative beliefs** | Hours | Narratives persist beyond individual events |
| **Synthesized beliefs** | On upstream change | Reactive, not proactive |

**Invariant:** Beliefs are **slow by design**. High-frequency belief updates indicate a design flaw, not responsiveness.

### Prohibition on Silent or Implicit Mutation

> [!WARNING]
> The following mutation patterns are FORBIDDEN:

| Pattern | Example | Why Forbidden |
|:--------|:--------|:--------------|
| **Silent default** | `belief = belief or default_belief` | Hides missing data |
| **In-place mutation** | `belief.confidence = 0.9` | Destroys provenance |
| **Cross-layer mutation** | Signal layer updating regime_state | Violates layer boundaries |
| **Feedback mutation** | Execution result changing belief | Reverse data flow |

**Required Pattern:**

```python
# WRONG: In-place mutation
current_belief.confidence = new_confidence

# RIGHT: New snapshot with provenance
new_belief = Belief(
    source=current_belief.source,
    value=current_belief.value,
    confidence=new_confidence,
    timestamp=now(),
    predecessor_id=current_belief.id
)
```

---

## 5. Failure Modes

### Belief Drift

**Definition:** Belief state diverges from reality without detection.

| Symptom | Cause | Detection |
|:--------|:------|:----------|
| Stale beliefs treated as current | Missing staleness check | TD-1 (Temporal Drift) validator |
| Beliefs updated without provenance | Silent mutation | BD-1 (Boundary Drift) validator |
| Synthesized belief contradicts inputs | Buggy synthesis logic | Unit tests + audit log |

### Belief Inflation

**Definition:** System holds more beliefs than evidence supports.

| Symptom | Cause | Detection |
|:--------|:------|:----------|
| Beliefs created without upstream source | Downstream layer producing beliefs | PD-1 (Permission Drift) validator |
| Beliefs persisting after upstream invalidation | Missing invalidation propagation | Staleness monitoring |
| Synthesized beliefs duplicating source beliefs | Over-synthesis | Belief count audit |

### Surfacing Violations

All belief violations are surfaced via:

1. **Audit log** — Every belief creation, mutation, and consumption logged
2. **Epistemic Drift Validator** — Automated detection of violation patterns
3. **Confidence degradation** — System-wide visibility into belief quality

---

## 6. Hard Invariants

The following rules are **non-negotiable** and must never be violated:

### BEL-1: Beliefs Are Immutable Snapshots

```
Once created, a belief object is frozen.
Updates create new snapshots, not mutations.
All snapshots are retained for audit.
```

### BEL-2: Beliefs Require Provenance

```
Every belief must declare:
  - source_layer: Which layer produced it
  - source_id: Specific producer within layer
  - timestamp: When it was created
  - predecessor_id: Previous belief it supersedes (if any)
```

### BEL-3: Downstream Cannot Produce Beliefs

```
Layers L8 (Signal), L10-L14 (Strategy through Audit) may ONLY consume beliefs.
Production of beliefs by these layers is an architectural violation.
```

### BEL-4: Staleness Degrades, Does Not Block

```
A stale belief does not crash the system.
It degrades confidence and surfaces the staleness.
Downstream consumers must handle degraded confidence.
```

### BEL-5: No Belief Without Evidence

```
Beliefs are derived from upstream observations and classifications.
No belief may be invented, assumed, or defaulted into existence.
If evidence is missing, the belief is ABSENT, not defaulted.
```

### BEL-6: Beliefs Describe, They Do Not Prescribe

```
Beliefs answer: "What is true about the current state?"
Beliefs never answer: "What should we do?" (Strategy)
Beliefs never answer: "What will happen?" (Prediction)
```

---

## Appendix A: Belief Schema (Reference)

```python
@dataclass(frozen=True)
class Belief:
    belief_id: str                   # Unique identifier
    belief_type: str                 # e.g., "regime_state", "macro_state"
    value: Any                       # The belief content
    confidence: float                # 0.0 to 1.0
    timestamp: datetime              # Creation time
    source_layer: str                # Producing layer ID
    source_id: str                   # Specific producer
    predecessor_id: Optional[str]    # Previous belief superseded
    is_stale: bool                   # Staleness flag
    staleness_reason: Optional[str]  # Why stale (if applicable)
```

---

## Appendix B: Cross-Reference

| Related Document | Relationship |
|:-----------------|:-------------|
| [layer_interaction_contract.md](file:///c:/GIT/TraderFund/docs/contracts/layer_interaction_contract.md) | Defines allowed data flows |
| [latent_structural_layers.md](file:///c:/GIT/TraderFund/docs/epistemic/latent_structural_layers.md) | Defines upstream Macro layer |
| [factor_layer_policy.md](file:///c:/GIT/TraderFund/docs/epistemic/factor_layer_policy.md) | Factor as constraint, not belief |
| [execution_harness_contract.md](file:///c:/GIT/TraderFund/docs/contracts/execution_harness_contract.md) | Harness consumes beliefs |

---

## Version History

| Version | Date | Changes |
|:--------|:-----|:--------|
| v1.0 | 2026-01-24 | Initial Belief Layer Policy |
