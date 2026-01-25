# Narrative System Summary

> **Date:** 2026-01-16  
> **Status:** AUDIT DOCUMENT  
> **Purpose:** Factual analysis of current Narrative system and Regime integration

---

## 1. What the Narrative System Does

### 1.1 Core Components

| Module | Location | Purpose |
|--------|----------|---------|
| `NarrativeGenesisEngine` | `narratives/genesis/engine.py` | Converts events into narratives |
| `Narrative` model | `narratives/core/models.py` | Data structure for narratives |
| `Event` model | `narratives/core/models.py` | Atomic market events |
| `narrative_prompt.py` | `llm_integration/prompts/` | LLM explanation prompts |
| `NarrativeTimeline` | `visualization/views/` | Streamlit UI display |

### 1.2 Narrative Flow

```
Events → NarrativeGenesisEngine → Narratives → Repository → UI/LLM
```

1. **Event ingestion**: Events with severity scores arrive
2. **Clustering**: Engine matches events to existing narratives by asset
3. **Genesis**: If no match and severity >= 60, create new narrative
4. **Reinforcement**: If match found, reinforce existing narrative
5. **Storage**: Narratives saved to Parquet files

### 1.3 Key Fields

**Narrative:**
- `narrative_id`, `title`, `market`, `scope`
- `confidence_score` (derived from event severity)
- `lifecycle_state` (BORN, REINFORCED, MUTATED, DEAD)
- `supporting_events`, `related_assets`

---

## 2. What the Narrative System Does NOT Do

- ❌ Does NOT generate trade signals
- ❌ Does NOT allocate capital
- ❌ Does NOT execute trades
- ❌ Does NOT predict future prices
- ❌ Does NOT currently query Market Regime

---

## 3. Regime Integration Status

### 3.1 Current State: **WIRED (v1.0)**

**Update 2026-01-16:** Runtime wiring is now complete.

The `RegimeEnforcedRepository` wrapper ensures ALL narratives pass through regime adaptation.

| Component | Uses Regime? |
|-----------|--------------|
| `NarrativeGenesisEngine` | ✅ YES (auto-wrapped) |
| `RegimeEnforcedRepository` | ✅ YES (applies regime) |
| `Narrative` model | ✅ YES (metadata attached) |
| `narrative_prompt.py` | ❌ NO (future enhancement) |
| `NarrativeTimeline` (UI) | ❌ NO (reads stored data) |

### 3.2 Where Regime Adapter IS Used

| Location | Usage |
|----------|-------|
| `traderfund/regime/dashboard.py` | Display weight multipliers |
| `traderfund/regime/tests/` | Unit tests |
| `scripts/demo_narrative_enforcement.py` | Demo script |

### 3.3 What the Adapter Does (When Used)

The `RegimeNarrativeAdapter` is designed to:
1. Query current US market regime
2. Apply weight multipliers to narrative signals
3. Dampen narratives in mean-reverting regimes
4. Mute narratives during EVENT_LOCK
5. Log all adjustments

But this is **not yet called** by the narrative pipeline.

---

## 4. Documentation vs Implementation

### 4.1 Documentation States

- `Regime_Integration_Runbook.md` describes how to use the adapter
- `intelligence_and_alpha_layer.md` describes narrative engine design
- `Regime_Confidence_Model.md` references `RegimeNarrativeAdapter`

### 4.2 Discrepancies Found

| Document | Claim | Reality |
|----------|-------|---------|
| Regime_Integration_Runbook.md | "Narrative is always regime-aware" | **FALSE** - adapter exists but not wired |
| Regime_Integration_Runbook.md | "HARD enforcement" | **FALSE** - no enforcement in narrative code |

### 4.3 Accurate Documentation

| Document | Status |
|----------|--------|
| `intelligence_and_alpha_layer.md` | ACCURATE (describes narrative engine correctly) |
| `Regime_Engine_Overview.md` | ACCURATE |
| `Regime_Taxonomy.md` | ACCURATE |

---

## 5. Gap List

### 5.1 Integration Gaps (Not Implemented)

1. **NarrativeGenesisEngine does not call RegimeNarrativeAdapter**
   - The adapter is built but not wired
   - Narrative confidence is NOT regime-adjusted

2. **No regime field in Narrative model**
   - Narratives do not store the regime at creation time

3. **LLM prompts do not include regime context**
   - Narrative explanations have no regime awareness

### 5.2 What Would Need to Change (NOT DOING NOW)

If regime integration were to be completed:
1. `NarrativeGenesisEngine._create_narrative()` would call adapter
2. `Narrative.confidence_score` would be regime-adjusted
3. `narrative_prompt.py` would include regime context

---

## 6. Conclusion

**Documentation is PARTIALLY aligned with implementation.**

- The `RegimeNarrativeAdapter` exists and works correctly
- Tests pass and demo script shows expected behavior
- BUT the adapter is **not wired** into the actual narrative pipeline
- Documentation claims "HARD enforcement" which is **not true**

### Required Documentation Update

The `Regime_Integration_Runbook.md` must be updated to clarify that:
1. The adapter is **available** but **not yet integrated**
2. Narrative confidence is **not** currently regime-adjusted
3. Integration requires wiring into `NarrativeGenesisEngine`

---

## 7. Recommendation (Not Implemented)

This audit recommends:
1. Updating docs to reflect current reality
2. Clearly marking adapter integration as **PENDING**
3. No code changes at this time
