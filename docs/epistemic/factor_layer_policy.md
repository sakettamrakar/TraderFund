# Factor Layer Policy

**Status:** Epistemic Declaration  
**Scope:** Architecture — Policy Layer Definition  
**Authority:** Constitutional — Binding for all signal and strategy systems

---

## Purpose

This document defines the **Factor / Style Risk Layer** as a **policy and constraint layer**, not a signal generator. The Factor Layer exists to gate, modulate, and constrain downstream systems — never to generate alpha directly.

> [!CAUTION]
> The Factor Layer is a permission system. It tells downstream layers what they are ALLOWED to do, not what they SHOULD do. Confusing these responsibilities is a critical architectural violation.

---

## Definition

**What is a Factor?**

A Factor is a persistent, economically meaningful source of systematic return variation. Examples:
- **Value**: Cheap assets vs expensive assets
- **Momentum**: Recent winners vs recent losers
- **Quality**: Profitable, stable companies vs unprofitable, volatile ones
- **Size**: Small-cap vs large-cap
- **Volatility**: Low-vol vs high-vol

**Position in Stack:** L6.5 — Between Regime Layer (L6) and Signal Layer (L8)

---

## Factor Layer Responsibilities

### What Factor Layer IS

| Responsibility | Description |
|:---------------|:------------|
| **Permission Layer** | Grants or revokes permission for downstream signal types |
| **Constraint Layer** | Sets maximum exposure limits by factor |
| **Risk-Shaping Layer** | Modulates position sizing based on factor loadings |
| **Policy Enforcement** | Ensures portfolio-level factor exposures stay within bounds |

### What Factor Layer is NOT

| Anti-Pattern | Why It's Wrong |
|:-------------|:---------------|
| Signal Generator | Factors describe risk characteristics, not entry/exit timing |
| Asset Selector | Factors constrain exposure, they don't pick individual assets |
| Timing Mechanism | Factor regimes change slowly; timing is not their purpose |
| Alpha Source | Factors explain returns, they don't guarantee positive returns |

---

## Hard Invariants

These invariants are **non-negotiable**. Any execution skill violating them is incorrect.

### INV-F1: No Signal May Bypass Factor Permissions

```
IF factor_permission(signal_type) == BLOCKED:
    signal MUST be rejected, regardless of strength
```

A momentum signal with 99% confidence MUST be rejected if the Factor Layer has blocked momentum exposure.

### INV-F2: Factors Do Not Select Assets

```
Factor Layer outputs:
    ✅ "Momentum exposure is PERMITTED up to 30%"
    ❌ "Buy AAPL because it has momentum"
```

Asset selection is a Signal Layer responsibility. Factors constrain exposure categories.

### INV-F3: Factor Policy Evaluation Precedes Signal Processing

```
Execution Order:
    1. Macro State → 2. Regime State → 3. Factor Permissions → 4. Signal Generation
```

Signals evaluated before factor permissions are architecturally invalid.

### INV-F4: Factor Permission Changes Require Decision Ledger Entry

Factor policy is not tunable by algorithms. Changes to factor permissions MUST be:
1. Recorded in the Decision Ledger
2. Authorized by a human operator
3. Accompanied by a rationale

---

## Factor Layer Outputs

The Factor Layer produces a **Factor Permission Object** consumed by downstream layers:

```python
class FactorPermission:
    timestamp: datetime           # When this permission was computed
    regime_context: str           # Current regime (for audit trail)
    
    # Permission flags
    momentum_permitted: bool      # Can momentum signals be processed?
    value_permitted: bool         # Can value signals be processed?
    quality_permitted: bool       # Can quality signals be processed?
    
    # Exposure constraints
    max_momentum_exposure: float  # Maximum portfolio % in momentum
    max_value_exposure: float     # Maximum portfolio % in value
    max_factor_concentration: float  # No single factor > this %
    
    # Risk modifiers
    size_multiplier: float        # Global sizing adjustment (0.0-1.0)
    
    # Audit
    rationale: str                # Why these permissions were set
```

---

## Interaction Contract

### Upstream Dependencies

| Layer | What Factor Layer Receives |
|:------|:---------------------------|
| Macro Layer | Macro environment determines factor regime (e.g., "Value favored in rising rates") |
| Regime Layer | Behavioral regime modulates factor confidence |

### Downstream Consumers

| Layer | What Factor Layer Provides |
|:------|:---------------------------|
| Signal Layer | Permission flags determining which signal types are allowed |
| Strategy Layer | Exposure constraints for position sizing |
| Optimization Layer | Factor concentration limits for portfolio construction |

---

## Factor-Regime Interaction Matrix

| Regime | Momentum | Value | Quality | Size |
|:-------|:---------|:------|:--------|:-----|
| TRENDING_NORMAL_VOL | ✅ Full | ⚠️ Reduced | ✅ Full | ✅ Full |
| TRENDING_HIGH_VOL | ⚠️ Reduced | ⚠️ Reduced | ✅ Full | ❌ Blocked |
| MEAN_REVERTING_LOW_VOL | ❌ Blocked | ✅ Full | ✅ Full | ✅ Full |
| MEAN_REVERTING_HIGH_VOL | ❌ Blocked | ⚠️ Reduced | ⚠️ Reduced | ❌ Blocked |
| EVENT_DOMINANT | ❌ Blocked | ❌ Blocked | ⚠️ Reduced | ❌ Blocked |
| EVENT_LOCK | ❌ ALL BLOCKED | ❌ ALL BLOCKED | ❌ ALL BLOCKED | ❌ ALL BLOCKED |
| UNDEFINED | ⚠️ Reduced | ⚠️ Reduced | ⚠️ Reduced | ⚠️ Reduced |

---

## Latent Status

| Aspect | Status |
|:-------|:-------|
| Epistemic Existence | ✅ EXISTS |
| Policy Definition | ✅ DEFINED (this document) |
| Implementation | ⏸️ DEFERRED |
| Downstream Anticipation | ✅ REQUIRED |

---

## Failure Modes

| Failure | Consequence | Prevention |
|:--------|:------------|:-----------|
| Factor bypass | Uncontrolled factor exposure → regime mismatch losses | Enforce INV-F1 at execution boundary |
| Factor as signal | Over-trading, false precision | Code review for signal/factor confusion |
| Stale permissions | Acting on outdated factor state | Timestamp validation on all permission objects |

---

## Version History

| Version | Date | Changes |
|:--------|:-----|:--------|
| v1.0 | 2026-01-24 | Initial Factor Layer policy definition |
