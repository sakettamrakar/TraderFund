# System Backlog and Refinements

**Status:** LIVING DOCUMENT
**Last Updated:** 2026-01-17

This is the **single source of truth** for all future refinements to the regime-aware narrative intelligence platform.

---

## Current System State (v1 - FROZEN)

| Module | Status | Key Components |
| :--- | :--- | :--- |
| Market Ingestion | ✅ Live | RSS, API bridge, MarketStoryAdapter |
| Severity Mapping | ✅ Frozen | LOW=40, MED=70, HIGH=90 |
| Accumulation | ✅ v1 | 3-event threshold, 48h window |
| Genesis Engine | ✅ Production | Daily cap=5, MIN_SEVERITY=60 |
| Narrative Engine | ✅ Regime-Enforced | Hard enforcement, no bypass |
| Strategy Gates | ✅ Live | Compatibility matrix, posture mapping |
| Dashboards | ✅ v1.1 | Regime, Strategy, Observability panels |

---

## Refinement Backlog

### A) Ingestion Layer

| Refinement | Priority | Type | Prerequisites | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Multi-source ingestion (≥3 sources) | P1 | CORE | NPR/BBC already in | Enables cross-source validation |
| Rate-aware ingestion | P2 | CORE | ≥100 stories/day | Burst detection, throttling |
| Source credibility weighting | P2 | RESEARCH | 3 months data | Requires historical accuracy tracking |
| Burst vs steady feed handling | P3 | DEFERRED | ≥500 stories/day | Event storm protection |

---

### B) Severity Assignment (Upstream)

| Refinement | Priority | Type | Prerequisites | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Source-based severity scaling | P2 | RESEARCH | Multi-source | Bloomberg HIGH ≠ Blog HIGH |
| Event calendar overlays | P1 | CORE | Calendar integration | FOMC, NFP → expected severity boost |
| Expected vs unexpected differentiation | P2 | CORE | `expectedness` field | Already in schema, needs upstream population |
| Cross-source confirmation | P3 | RESEARCH | ≥3 sources, 30 days data | Same story from 3 sources → severity bump |

---

### C) Accumulation Logic (v2 Concepts)

| Refinement | Priority | Type | Prerequisites | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Accumulation decay | P1 | CORE | None | Older events contribute less weight |
| Cross-source accumulation | P2 | RESEARCH | Multi-source | Same theme from different sources = stronger |
| Weighted accumulation | P2 | CORE | Decay | HIGH events contribute more to threshold |
| Accumulation pressure indicators | P3 | DEFERRED | 100+ events/day | "Tension building" metrics |
| Theme saturation detection | P3 | RESEARCH | 3 months data | Prevent narrative fatigue |

---

### D) Genesis Engine

| Refinement | Priority | Type | Prerequisites | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Dynamic daily caps (rule-based) | P2 | CORE | Regime integration | Low-vol = lower cap, high-vol = higher cap |
| Deferred Genesis (delayed promotion) | P3 | RESEARCH | Decay logic | Wait 24h before committing |
| Genesis confidence bands | P2 | CORE | None | Report uncertainty range |
| Genesis audit summaries | P1 | CORE | None | Daily digest: what was accepted/rejected |

---

### E) Narrative Engine

| Refinement | Priority | Type | Prerequisites | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Narrative evolution over time | P2 | CORE | Version history | Track how narratives change |
| Narrative contradiction detection | P3 | RESEARCH | Semantic tags | Conflicting narratives in same market |
| Narrative clustering | P2 | RESEARCH | Embeddings | Group related narratives |
| Narrative decay / expiry | P1 | CORE | None | Stale narratives auto-demote |
| Narrative fatigue detection | P3 | RESEARCH | 3 months data | Too many similar narratives = suppress |

---

### F) Regime Engine

| Refinement | Priority | Type | Prerequisites | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Multi-timeframe regime overlay | P2 | RESEARCH | Daily + Weekly data | Short-term vs long-term regime |
| Sector-level regimes | P3 | DEFERRED | Sector classification | Tech vs Financials regime state |
| Regime transition early warnings | P1 | CORE | Confidence bands | Confidence dropping = transition risk |
| Regime disagreement diagnostics | P2 | CORE | None | When indicators conflict, explain |

---

### G) Strategy Gates

| Refinement | Priority | Type | Prerequisites | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Gradual re-enable after EVENT_LOCK | P2 | CORE | Timer logic | Ramp up exposure over 2h |
| Strategy confidence scaling | P2 | RESEARCH | Confidence bands | Lower confidence = smaller position |
| Strategy regret feedback loops | P3 | RESEARCH | 6 months trade data | Learn from gate decisions |
| Gate explainability metrics | P1 | CORE | None | Why was this strategy blocked? |

---

### H) Dashboards & Telemetry

| Refinement | Priority | Type | Prerequisites | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Historical Genesis ratios | P1 | CORE | 30 days data | Acceptance rate over time |
| Accumulation heatmaps | P2 | RESEARCH | Semantic tags | Visual tag activity |
| Narrative density over time | P2 | CORE | Time series | How many active narratives? |
| Regime–narrative correlation views | P3 | RESEARCH | 3 months data | Do regimes predict narrative volume? |

---

## Core vs Research Modules

### Core (Mandatory for Maturity)
These MUST be implemented for the system to be considered production-grade:
- Multi-source ingestion
- Event calendar overlays
- Accumulation decay
- Narrative decay / expiry
- Regime transition early warnings
- Gate explainability metrics
- Genesis audit summaries

### Research (Experimental)
These are exploratory and MUST NOT be promoted to Core without validation:
- Cross-source confirmation
- Theme saturation detection
- Narrative contradiction detection
- Strategy regret feedback loops
- Sector-level regimes

### Deferred (Needs Scale/Data)
These require more data or scale than currently available:
- Burst vs steady feed handling (needs ≥500 stories/day)
- Accumulation pressure indicators (needs ≥100 events/day)
- Sector-level regimes (needs sector classification)

---

## Explicit Non-Goals (What We Are NOT Doing Yet)

> [!CAUTION]
> The following are **explicitly out of scope** and MUST NOT be implemented without formal approval.

1.  **Semantic interpretation inside Genesis** - Genesis uses severity, not meaning.
2.  **ML-based severity inference** - Severity is upstream, rule-based only.
3.  **Automatic threshold tuning** - All thresholds are frozen constants.
4.  **Strategy execution from narratives** - Narratives inform, never execute.
5.  **LLM-based narrative generation** - Narratives are template-based only.
6.  **Predictive regime transitions** - Regime is reactive, not predictive.
7.  **Auto-scaling position sizes** - Position sizing is strategy-level, not narrative-level.

---

## Version History

| Version | Date | Changes |
| :--- | :--- | :--- |
| v1.0 | 2026-01-17 | Initial backlog creation |
