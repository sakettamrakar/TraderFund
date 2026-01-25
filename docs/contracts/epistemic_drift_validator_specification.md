# Epistemic Drift Validator Specification

**Status:** Audit Complete — Refinements Proposed  
**Scope:** Epistemic Enforcement Architecture  
**Authority:** This specification supersedes informal drift detection practices.

---

## Audit Summary

### Current Coverage

| Validator | Capability | Coverage |
|:----------|:-----------|:---------|
| **Drift Detector** | Configuration Drift | ✅ Covered — `.env` vs `.env.example` |
| **Drift Detector** | Structural Drift | ✅ Covered — Directory vs Architecture manifest |
| **Drift Detector** | Logic Drift (Hash) | ⚠️ Partial — Source hash integrity only |
| **Constraint Validator** | Narrative Integrity | ✅ Covered — Required fields, no future leaks |
| **Constraint Validator** | Signal-to-Regime | ✅ Covered — Signal validity per regime |
| **Constraint Validator** | Decision Logic | ✅ Covered — "Why" and "Stop" presence |
| **Cognitive Order Validator** | Layer Bypass | ⚠️ Partial — Checks Regime/Narrative bypass only |

### Missing Protections

| Drift Class | Current Status | Risk Level |
|:------------|:---------------|:-----------|
| **Ontological Drift** | ❌ NOT COVERED | HIGH |
| **Causal Drift** | ❌ NOT COVERED | HIGH |
| **Boundary Drift** | ❌ NOT COVERED | HIGH |
| **Permission Drift** | ❌ NOT COVERED | CRITICAL |
| **Temporal Drift** | ❌ NOT COVERED | MEDIUM |
| **Latent → Active Drift** | ❌ NOT COVERED | HIGH |
| **Macro/Factor Awareness** | ❌ NOT COVERED | CRITICAL |
| **Execution Harness Safety** | ❌ NOT COVERED | CRITICAL |

---

## STEP 1: Capability Inventory

### Drift Detector — Current State

| Mode | What It Checks | What It Misses |
|:-----|:---------------|:---------------|
| `config` | Key presence, type match | Semantic meaning of values |
| `structure` | File/folder existence | Layer responsibility mapping |
| `integrity` | Hash equality | Content semantic drift |

**Verdict:** Drift Detector is a **syntactic** tool. It cannot detect **semantic** or **epistemic** drift.

### Constraint Validator — Current State

| Mode | What It Checks | What It Misses |
|:-----|:---------------|:---------------|
| `narrative` | Required fields, no future timestamps | Layer dependency violations |
| `signal` | Signal-Regime compatibility | Factor permission checks |
| `decision` | "Why" and "Stop" presence | Upstream context validation |

**Verdict:** Constraint Validator has basic semantic checks but lacks **layer awareness** and **policy enforcement**.

### Gap Summary

The current validators can answer:
- "Did the file change?" ✅
- "Is this artifact structurally valid?" ✅

They CANNOT answer:
- "Did a layer assume another layer's responsibility?" ❌
- "Did a latent layer get silently activated?" ❌
- "Is execution logic inferring beliefs?" ❌

---

## STEP 2: Drift Taxonomy Alignment

### Drift Classes to Detect

| Drift Class | Definition | Current Coverage | Required Check |
|:------------|:-----------|:-----------------|:---------------|
| **Ontological Drift** | New concepts introduced without declaration | ❌ None | Concept registry validation |
| **Causal Drift** | Layers acting as causes instead of constraints | ❌ None | Dependency direction audit |
| **Boundary Drift** | Layer assuming responsibilities of another | ❌ None | Responsibility matrix check |
| **Permission Drift** | Signals/execution bypassing policy layers | ❌ None | Permission chain validation |
| **Temporal Drift** | Fast layers mutating slow beliefs | ❌ None | Temporal integrity audit |
| **Latent → Active Drift** | Latent layers silently activated | ❌ None | Activation declaration check |

### Proposed Detection Rules

#### OD-1: Ontological Drift Detection

```
RULE: Every concept used in epistemic documents must be declared in the concept registry.

CHECK: Parse epistemic files for key terms (layer names, state types, permission types).
       Compare against authoritative registry.
       Flag undeclared terms.

SEVERITY: WARNING (new concept) or FAIL (conflict with existing concept)
```

#### CD-1: Causal Drift Detection

```
RULE: Constraint layers (Regime, Factor) must not claim to CAUSE market behavior.

CHECK: Scan constraint layer documents for causal language:
       FORBIDDEN: "Regime causes...", "Factor drives..."
       ALLOWED: "Regime constrains...", "Factor permits..."

SEVERITY: FAIL
```

#### BD-1: Boundary Drift Detection

```
RULE: Each layer's responsibilities must match its declaration.

CHECK: Parse layer documents for responsibility claims.
       Compare against authoritative layer_interaction_contract.md.
       Flag responsibility claims outside declared scope.

SEVERITY: FAIL
```

#### PD-1: Permission Drift Detection

```
RULE: Downstream layers must not bypass permission layers.

CHECK: Trace data flow in code/docs.
       Verify Signals reference FactorPermission.
       Verify Execution references BeliefApproval.

SEVERITY: CRITICAL (hard fail, blocks deployment)
```

#### TD-1: Temporal Drift Detection

```
RULE: Fast layers (Flow, Signal) must not mutate slow beliefs (Regime, Narrative).

CHECK: Verify slow state objects are immutable.
       Verify fast layers receive copies, not references.

SEVERITY: FAIL
```

#### LD-1: Latent-to-Active Drift Detection

```
RULE: Activating a latent layer requires Decision Ledger entry.

CHECK: Compare latent_structural_layers.md declarations against code imports.
       If latent layer is imported/used → check for D00X authorization.

SEVERITY: CRITICAL (unauthorized activation is forbidden)
```

---

## STEP 3: Macro & Factor Awareness Check

### Current State

| Check | Drift Detector | Constraint Validator | Gap |
|:------|:---------------|:---------------------|:----|
| Regime declares Macro dependency | ❌ | ❌ | **MISSING** |
| Factor not a signal generator | ❌ | ❌ | **MISSING** |
| Execution cannot infer upstream | ❌ | ⚠️ Partial | **INCOMPLETE** |
| Silent defaults detection | ❌ | ❌ | **MISSING** |

### Proposed New Rules

#### MF-1: Macro Dependency Validation

```
RULE: Regime Layer must declare upstream dependency on Macro.

CHECK: Parse Regime_Taxonomy.md and Market_Regime_Detection_Blueprint.md.
       Verify presence of "Upstream Dependency" section.
       Verify macro_state → regime_classification declaration.

SEVERITY: FAIL if undeclared
```

#### MF-2: Factor Policy Enforcement

```
RULE: Factor Layer must never generate signals.

CHECK: Scan factor_layer_policy.md implementation (when exists).
       Verify outputs are FactorPermission objects, not Signal objects.
       Flag any Signal generation in Factor Layer code.

SEVERITY: CRITICAL
```

#### MF-3: Execution Inference Prevention

```
RULE: Execution code must not compute upstream state.

CHECK: Parse execution harness code for:
       FORBIDDEN: "if volatility > X" (regime inference)
       FORBIDDEN: "macro_service.get_state()" (direct macro access)
       REQUIRED: State passed as parameter

SEVERITY: CRITICAL
```

#### MF-4: Silent Default Detection

```
RULE: No layer may assume neutral/default for upstream state.

CHECK: Scan for patterns like:
       FORBIDDEN: "liquidity = liquidity or 'NORMAL'"
       FORBIDDEN: "macro_state = macro_state or MacroState()"
       REQUIRED: Explicit handling of None with confidence degradation

SEVERITY: WARNING
```

---

## STEP 4: Execution Harness Safety

### Validation Rules for Task Graphs

#### EH-1: Task Belief Inference Detection

```
RULE: Tasks must consume beliefs, not infer them.

CHECK: Parse task definitions.
       Verify `required_inputs` includes `BeliefSet`.
       Flag tasks that compute beliefs internally.

SEVERITY: CRITICAL
```

#### EH-2: Factor Permission Bypass Detection

```
RULE: Tasks must not bypass factor permissions.

CHECK: Verify task graph includes permission check node before action nodes.
       Verify FactorPermission is in `required_inputs` for action tasks.

SEVERITY: CRITICAL
```

#### EH-3: Implicit Strategy Detection

```
RULE: Skills must not encode strategy logic.

CHECK: Scan skill implementations for:
       FORBIDDEN: Price comparisons ("if price > X")
       FORBIDDEN: Indicator calculations ("rsi = ...")
       FORBIDDEN: Direction logic ("if bullish")
       
       Strategy logic belongs in Strategy Layer, not skills.

SEVERITY: CRITICAL
```

#### EH-4: Skill Declaration Completeness

```
RULE: All skill side effects must be declared.

CHECK: Compare skill `side_effects` declaration against actual writes.
       Flag undeclared writes.

SEVERITY: CRITICAL
```

---

## STEP 5: Refinement Proposal

### Updated Validator Specification

#### A. Unified Epistemic Drift Validator

Merge drift detection capabilities into a single coherent validator with multiple modes:

| Mode | Scope | Source Rules |
|:-----|:------|:-------------|
| `syntax` | File/config/hash | Current Drift Detector |
| `semantic` | Artifact validity | Current Constraint Validator |
| `epistemic` | Layer integrity | NEW rules (this spec) |
| `harness` | Task graph safety | NEW rules (this spec) |

#### B. Rule Categories

| Category | Rules | Severity |
|:---------|:------|:---------|
| Ontological | OD-1 | WARNING/FAIL |
| Causal | CD-1 | FAIL |
| Boundary | BD-1 | FAIL |
| Permission | PD-1 | CRITICAL |
| Temporal | TD-1 | FAIL |
| Latent-Active | LD-1 | CRITICAL |
| Macro-Factor | MF-1 to MF-4 | FAIL/CRITICAL |
| Harness | EH-1 to EH-4 | CRITICAL |

#### C. Severity Levels

| Level | Meaning | Action |
|:------|:--------|:-------|
| **INFO** | Minor discrepancy, low risk | Log only |
| **WARNING** | Potential drift, review recommended | Log + flag for review |
| **FAIL** | Confirmed drift, deployment blocked | Block + require resolution |
| **CRITICAL** | Safety violation, immediate halt | Halt + require Decision Ledger entry |

### Validator Extension Points

#### For Future Layers

When a latent layer becomes active, add to validator:

1. **Layer Registration**:
   ```yaml
   layer_id: macro_liquidity
   status: ACTIVE
   activation_decision: D00X
   upstream: [feature_layer]
   downstream: [regime_layer]
   ```

2. **Dependency Check**:
   Validator automatically adds:
   - Downstream layers must declare upstream dependency
   - Upstream layers must not reference downstream

3. **Permission Chain Extension**:
   If layer issues permissions, add to permission chain validation.

#### For New Skills

Skills auto-audited on registration:

```python
def audit_skill_registration(skill: SkillRegistration):
    # Check 1: Decision Ledger authorization
    verify_decision_ledger_entry(skill.decision_ledger_ref)
    
    # Check 2: Layer dependency validity
    for dep in skill.layer_dependencies:
        verify_layer_exists(dep)
        verify_no_bypass(dep, skill.task_types)
    
    # Check 3: Side effect declaration
    verify_side_effects_declared(skill)
    
    # Check 4: Prohibited patterns
    scan_for_forbidden_patterns(skill.skill_ref)
```

### Failure Mode Examples

#### Example 1: Boundary Drift (FAIL)

**Scenario:** Signal Layer document states "Signal Layer determines market regime based on volatility."

**Detection:** BD-1 flags responsibility claim "determines market regime" as belonging to Regime Layer.

**Message:**
```
BOUNDARY_DRIFT_DETECTED
Location: docs/epistemic/signal_layer.md:45
Violation: Signal Layer claiming Regime Layer responsibility
Expected: Regime classification is Regime Layer responsibility
Remediation: Remove regime inference from Signal Layer
```

#### Example 2: Permission Drift (CRITICAL)

**Scenario:** Execution harness code executes signal without checking FactorPermission.

**Detection:** PD-1 traces data flow and finds Signal → Execution with no FactorPermission check.

**Message:**
```
PERMISSION_BYPASS_DETECTED
Location: src/harness/executor.py:112
Violation: Signal processed without FactorPermission validation
Required: FactorPermission must be checked before execution
Remediation: Add permission validation step to task graph
Severity: CRITICAL — Deployment blocked
```

#### Example 3: Latent-Active Drift (CRITICAL)

**Scenario:** Developer imports `MacroStateService` without Decision Ledger entry.

**Detection:** LD-1 finds import of latent layer component without D00X authorization.

**Message:**
```
UNAUTHORIZED_LAYER_ACTIVATION
Location: src/regime/detector.py:5
Violation: Macro Layer imported without Decision Ledger authorization
Layer Status: LATENT (per latent_structural_layers.md)
Required: Decision Ledger entry authorizing activation
Remediation: Either remove import or create D00X entry
Severity: CRITICAL — Deployment blocked
```

#### Example 4: Execution Inference (CRITICAL)

**Scenario:** Task computes regime internally: `if self.volatility > 0.3: regime = "HIGH_VOL"`

**Detection:** MF-3/EH-1 flags regime inference in execution code.

**Message:**
```
UPSTREAM_INFERENCE_DETECTED
Location: src/tasks/signal_processor.py:78
Violation: Task inferring regime state instead of receiving as input
Forbidden: Direct regime computation in execution layer
Required: Receive RegimeState from Regime Layer as input
Remediation: Add RegimeState to task inputs, remove inference logic
Severity: CRITICAL — Deployment blocked
```

---

## Readiness Assessment

### Is the Validator Sufficient for Execution Harness Onboarding?

| Requirement | Current State | After Refinement |
|:------------|:--------------|:-----------------|
| Detect layer bypass | ⚠️ Partial | ✅ Complete |
| Detect permission drift | ❌ Missing | ✅ Complete |
| Detect belief inference | ❌ Missing | ✅ Complete |
| Detect latent activation | ❌ Missing | ✅ Complete |
| Detect strategy leakage | ❌ Missing | ✅ Complete |
| Block unsafe deployments | ⚠️ Weak | ✅ Strong |

### Verdict

**Current State:** NOT READY for execution harness onboarding.

**After Refinement:** READY — Validator will correctly enforce:
- Layer separation
- Permission chains
- Belief consumption (not inference)
- Latent layer discipline
- Deployment safety

---

## Implementation Priority

| Priority | Rule Set | Rationale |
|:---------|:---------|:----------|
| P0 | PD-1, EH-1, EH-2 | Permission bypass is highest risk |
| P1 | LD-1, MF-3 | Latent activation and inference are architectural violations |
| P2 | BD-1, CD-1, TD-1 | Boundary/causal/temporal drift corrupt documentation |
| P3 | OD-1, MF-4 | Ontological and silent default are lower severity |

---

## Version History

| Version | Date | Changes |
|:--------|:-----|:--------|
| v1.0 | 2026-01-24 | Initial audit and refinement specification |
