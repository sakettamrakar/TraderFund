# Regime Integration Runbook

> **CHANGELOG**  
> - 2026-01-16: Added Runtime Narrative Enforcement section (FINAL wiring complete)  
> - 2026-01-16: Clarified that RegimeNarrativeAdapter is NOT YET WIRED into NarrativeGenesisEngine  
> - 2026-01-16: Added HARD enforcement documentation (for adapter behavior when used)  
> - 2026-01-16: Created from Phase A wiring

---

> **⚠️ IMPORTANT: INTEGRATION STATUS**
>
> The `RegimeNarrativeAdapter` exists and works correctly, but it is **NOT YET INTEGRATED** into the actual `NarrativeGenesisEngine`.
>
> - The adapter is available at `traderfund/regime/narrative_adapter.py`
> - Tests pass and the demo script works
> - BUT the core narrative pipeline (`narratives/genesis/engine.py`) does NOT call the adapter
> - Narrative confidence is **NOT** currently regime-adjusted
>
> This document describes how the adapter works and how to integrate it when ready.

---

## Purpose

This runbook defines **how** and **in what order** downstream systems may integrate with the Regime Engine.

---

## Approved Integration Order

Integration MUST follow this sequence:

```
1. US Narrative    ← Currently Phase A (SHADOW)
2. US Momentum     ← Not started
3. India Momentum  ← Not started
```

**Rule:** Do not skip steps. Each phase must complete SHADOW → SOFT → HARD before the next begins.

---

## Enforcement Progression

All integrations follow this lifecycle:

| Stage | Behavior | Config |
|-------|----------|--------|
| **SHADOW** | Log adjustments only | `NARRATIVE_REGIME_MODE=SHADOW` |
| **SOFT** | Apply weights, no hard blocks | `NARRATIVE_REGIME_MODE=SOFT` |
| **HARD** | Full enforcement | Future phase |

**Current State (2026-01-16):**
- US Narrative: SHADOW mode
- All others: Not wired

---

## What is Allowed

✅ **Allowed:**
- Read regime state via `get_current_us_market_regime()`
- Apply weight multipliers to scores
- Log adjustment decisions
- Use `RegimeNarrativeAdapter.adjust_signal()`

---

## What is Forbidden

❌ **Forbidden:**
- Modifying Regime Engine logic
- Modifying Dashboard display logic
- Hard-blocking signals without approval
- Overriding regime based on external factors
- Adding new indicators to regime detection

---

## Weight Multipliers

| Regime | Factor | Effect |
|--------|--------|--------|
| TRENDING_NORMAL_VOL | 1.0x | Full weight |
| TRENDING_HIGH_VOL | 0.3x | Strongly dampened |
| MEAN_REVERTING_LOW_VOL | 0.5x | Dampened |
| MEAN_REVERTING_HIGH_VOL | 0.3x | Strongly dampened |
| EVENT_DOMINANT | 1.5x | Boosted |
| EVENT_LOCK | 0.0x | **Blocked** |
| UNDEFINED | 0.5x | Fail-safe dampen |

---

## Fail-Safe Behavior

**Rule:** If regime is unavailable or unknown, default to **0.5x dampening**.

This ensures:
- No silent failures
- Conservative behavior under uncertainty
- System remains operational

---

## Rollback Procedure

If integration causes issues:

1. **Immediate:** Set `NARRATIVE_REGIME_MODE=SHADOW`
2. **Check:** Verify telemetry logs at `data/regime_narrative_telemetry.jsonl`
3. **Analyze:** Compare SHADOW predictions to actual outcomes
4. **Fix:** Adjust weights or logic as needed
5. **Re-enable:** Careful progression SHADOW → SOFT

**Emergency:** Set `REGIME_MODE=OFF` to disable all regime effects.

---

## Telemetry

All adjustments are logged to:
```
data/regime_narrative_telemetry.jsonl
```

Each entry contains:
```json
{
  "timestamp": "...",
  "type": "NARRATIVE_ADJUSTMENT",
  "symbol": "AAPL",
  "regime": "MEAN_REVERTING_LOW_VOL",
  "confidence": 0.78,
  "original_weight": 1.0,
  "adjusted_weight": 0.5,
  "factor": 0.5,
  "reason": "DAMPENED: MEAN_REVERTING_LOW_VOL (x0.5)",
  "enforcement_mode": "SOFT"
}
```

---

## Code Integration Example

```python
from traderfund.regime.narrative_adapter import (
    apply_regime_to_narrative,
    NarrativeSignal
)

# Create your signal
signal = NarrativeSignal(
    symbol="AAPL",
    weight=1.0,
    confidence=0.9,
    narrative_id="xyz",
    summary="..."
)

# Apply regime adjustment
result = apply_regime_to_narrative(signal)

# Use adjusted weight
final_weight = result.adjusted_weight
```

---

## What NOT To Do

- ❌ Do NOT wire new systems without following the order
- ❌ Do NOT skip SHADOW mode
- ❌ Do NOT hard-block without HARD enforcement approval
- ❌ Do NOT ignore telemetry during testing
- ❌ Do NOT modify regime logic to "fix" adjustment behavior

---

## Document Status

**STATUS: ACTIVE**

This runbook applies to Phase A (US Narrative wiring).
Updated as new integrations are approved.

---

## Regime → Narrative Enforcement (HARD)

> **Added:** 2026-01-16  
> **Status:** FROZEN

### Enforcement Mode

Narrative enforcement runs in **HARD mode only**.

There is:
- ❌ No SHADOW mode
- ❌ No SOFT mode
- ❌ No bypass flag
- ❌ No config toggle

### Weight Mapping (FROZEN)

| Regime | Factor | Reason |
|--------|--------|--------|
| TRENDING_NORMAL_VOL | 1.0x | Full weight |
| TRENDING_HIGH_VOL | 0.2x | Dampened (vol risk) |
| MEAN_REVERTING_LOW_VOL | 0.5x | Dampened |
| MEAN_REVERTING_HIGH_VOL | 0.3x | Strongly dampened |
| EVENT_DOMINANT | 1.0x | Capped at 1.0 |
| EVENT_LOCK | **0.0x** | **MUTED** |
| UNDEFINED | 0.5x | Fail-safe |

### Fail-Safe Rules

If any of these conditions are true:
- Regime unavailable
- Confidence < 0.3
- Lifecycle = TRANSITION

Then:
- Narrative weight = 0.5x
- Reason = "FAIL_SAFE_DAMPEN"

### Explicit Guarantees

1. **Narrative MUST always query Regime Engine**
2. **Narrative MUST NOT bypass regime**
3. **EVENT_LOCK MUST mute narrative completely**
4. **Missing regime MUST fail-safe (dampen)**
5. **All adjustments MUST be logged**

### Telemetry Format

Every adjustment is logged to `data/regime_narrative_telemetry.jsonl`:

```json
{
  "timestamp": "2026-01-16T01:45:00Z",
  "type": "NARRATIVE_ENFORCEMENT",
  "symbol": "AAPL",
  "original_weight": 1.0,
  "final_weight": 0.5,
  "regime": "MEAN_REVERTING_LOW_VOL",
  "confidence": 0.78,
  "lifecycle": "STABLE",
  "enforcement_reason": "REGIME_APPLIED: MEAN_REVERTING_LOW_VOL (x0.5)"
}
```

### What NOT To Do

- ❌ Do NOT try to disable enforcement
- ❌ Do NOT add bypass flags
- ❌ Do NOT modify weight mappings without version bump
- ❌ Do NOT ignore telemetry warnings
- ❌ Do NOT trade narratives during EVENT_LOCK

---

## Runtime Narrative Enforcement (FINAL)

> **Added:** 2026-01-16  
> **Status:** FROZEN v1.0

### How Enforcement Works

1. `NarrativeGenesisEngine` automatically wraps its repository with `RegimeEnforcedRepository`
2. Every call to `save_narrative()` passes through regime adaptation
3. Regime metadata is attached to every narrative
4. Telemetry is logged for every narrative

```python
# This happens automatically:
NarrativeGenesisEngine(repo)  # repo is wrapped with regime enforcement
```

### Canonical Output Path

```
NarrativeGenesisEngine
    → _create_narrative() / _reinforce_narrative()
        → repo.save_narrative()
            → RegimeEnforcedRepository.save_narrative()
                → Regime applied
                → Metadata attached
                → Telemetry logged
                → Inner repository saves
```

**There is NO other path.**

### Confidence vs Conviction (Clarification)
There are two distinct confidence metrics:

1. **`NARRATIVE_CONFIDENCE` (Score)**
   - **Type:** Unbounded / Raw Score
   - **Meaning:** How "complete" or "severe" the story is internally.
   - **Not** a probability. **Not** actionable conviction.

2. **`REGIME_CONFIDENCE` (Probability)**
   - **Type:** Normalized (0.0 - 1.0)
   - **Meaning:** How sure the Regime Engine is about the current market state.

**Actionable Conviction** = `Final Weight` (Not confidence)

### Attached Metadata

Every persisted narrative includes:

```json
{
  "explainability_payload": {
    "regime_enforcement": {
      "regime": "MEAN_REVERTING_LOW_VOL",
      "bias": "NEUTRAL",
      "regime_confidence": 0.78,
      "lifecycle": "STABLE",
      "original_weight": 0.8,
      "final_weight": 0.4,
      "multiplier": 0.5,
      "enforcement_reason": "REGIME_APPLIED: MEAN_REVERTING_LOW_VOL (x0.5)",
      "enforced_at": "2026-01-16T02:50:00Z"
    }
  }
}
```

### Guarantees

1. **ALL narratives are regime-adjusted** — No exceptions
2. **NO bypass path exists** — Wrapper is mandatory
3. **Telemetry is always logged** — Machine-parseable
4. **Fail-safe on missing regime** — 0.5x dampening

### Files Modified

| File | Change |
|------|--------|
| `narratives/genesis/engine.py` | Auto-wraps repo with enforcement |
| `narratives/repository/regime_enforced.py` | NEW — Wrapper implementation |
| `narratives/tests/test_regime_enforcement.py` | NEW — 7 tests |

### This Behavior is FROZEN

Do NOT:
- Remove the wrapper
- Add bypass flags
- Skip regime for "special" cases
