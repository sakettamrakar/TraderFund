# Factor Remediation Implementation Digest

> Consolidated from individual factor implementation reports (F1, F2, F3, F5).
> Original reports moved to `_delete/audit/`.

- Execution mode: `REAL_RUN`
- Truth Epoch: `TE-2026-01-30` (frozen)
- Markets: `US`, `INDIA`
- Common invariants preserved: `INV-NO-EXECUTION`, `INV-NO-CAPITAL`, `INV-HONEST-STAGNATION`, `INV-TRUTH-EPOCH-EXPLICIT`, `INV-NO-TEMPORAL-INFERENCE`

---

## F1: Temporal Drift

**Remediation pattern**: Bounded drift with operator-mediated catch-up.

### Implemented Controls
1. **Drift Threshold Enforcement** (`scripts/temporal_orchestrator.py`)
   - Configurable via `config/temporal_drift_policy.json`
   - Per-market: `drift_days = CTT - TE`, default `max_drift_days = 7`
   - Breach emits `DRIFT_LIMIT_EXCEEDED` with `evaluation_hold = true`
   - No automatic evaluation trigger, no TE advancement

2. **Chunked Evaluation Window Metadata**
   - Persisted per market: `docs/intelligence/temporal/evaluation_windows/evaluation_window_<MARKET>.json`
   - Exposed in dashboard and audit payloads

3. **Operator-Mediated Catch-Up**
   - CLI: `python scripts/temporal_orchestrator.py request-window --market <US|INDIA> --window-start YYYY-MM-DD --window-end YYYY-MM-DD`
   - Validates: date format, ordering, boundedness (`TE <= start <= end <= CTT`)
   - Requests logged, persisted; do not trigger evaluation or advance TE

4. **Dashboard Visibility**
   - `src/dashboard/backend/loaders/temporal.py`
   - `src/dashboard/frontend/src/components/TemporalTruthBanner.jsx`
   - Shows drift days, max, breach badge, operator action required

5. **Audit Logging**: `docs/audit/f1_temporal_drift/` (drift_breaches.jsonl, evaluation_window_requests.jsonl)

### Runtime Artifacts
- `docs/intelligence/temporal/temporal_state_US.json`, `..._INDIA.json`
- `docs/intelligence/temporal/evaluation_windows/evaluation_window_US.json`, `..._INDIA.json`

### Validation Result
- INDIA: `DRIFT_LIMIT_EXCEEDED` (drift=10, max=7) — correct
- US: `EVALUATION_PENDING` (drift=7, max=7) — correct
- Out-of-bounds requests rejected with explicit reason

---

## F2: Regime Partiality

**Remediation pattern**: `DEGRADE-ON-PARTIAL` — degrade regime to UNKNOWN when canonical inputs are incomplete.

### Implemented Controls
1. **Canonical Partiality Detection** (`src/governance/canonical_partiality.py`)
   - States: `CANONICAL_COMPLETE`, `CANONICAL_PARTIAL`, `CANONICAL_MIXED`
   - Signals: required role presence, status from parity, freshness alignment to CTT, freshness skew
   - Persisted: `docs/intelligence/canonical_partiality_state_<MARKET>.json`

2. **Regime Degradation Logic** (`src/evolution/regime_context_builder.py`, `ev_tick.py`, `india_policy_evaluation.py`)
   - If `canonical_state != CANONICAL_COMPLETE`: regime → `UNKNOWN`, confidence → `DEGRADED`

3. **Downstream Propagation** (`src/intelligence/decision_policy_engine.py`)
   - Non-complete canonical → `policy_state = HALTED`, `permissions = [OBSERVE_ONLY]`
   - No regime inference path executed

4. **Dashboard Disclosure** (`MarketSnapshot.jsx`)
   - Displays `REGIME: UNKNOWN (PARTIAL DATA)`, canonical state, missing/stale roles

5. **Cross-Market Isolation**: Computed independently per market (no cross-market override)

6. **Audit Logging**: `docs/audit/f2_regime_partiality/` (partiality_detections.jsonl, regime_degradations.jsonl)

### Runtime Result
- US: `CANONICAL_PARTIAL` (rates role issue) → regime UNKNOWN
- INDIA: `CANONICAL_COMPLETE` → retained evaluated regime

---

## F3: Narrative Leakage

**Remediation pattern**: Regime-gated narrative safety — suppress forward-looking narrative when system state is degraded or suppressed.

### Implemented Controls
1. **Narrative Gating** (`src/governance/narrative_guard.py`, `src/dashboard/backend/loaders/narrative.py`)
   - Gated by: suppression_state (F5), regime_state/confidence (F2), canonical_state
   - Active suppression → no forward-looking narrative
   - Degraded regime → no explanatory narrative
   - Non-complete canonical → explanatory mode blocked

2. **Narrative Modes** (persisted to `docs/intelligence/narrative_state_<MARKET>.json`)
   - `SILENCED`, `CAUSAL_ONLY`, `EVIDENCE_ONLY`, `EXPLANATORY`
   - Payload: mode, gating_reason, silence_reason, provenance_references, narrative_diff

3. **Hard Language Ban**
   - Banned categories: action verbs (buy/sell), confidence escalation (strong/likely), temporal promises (soon/setting up), optimization (best/opportunity), causal closure (therefore/hence)
   - Violation → `SILENCED` + logged to `docs/audit/f3_narrative/language_violations.jsonl`

4. **Narrative Diffing** vs last TE-bound state
   - No material change → `SILENCED` with explicit reason

5. **Dashboard Binding** (`SystemNarrative.jsx`)
   - Silence visible and explained; provenance operator-visible

6. **Audit Logging**: `docs/audit/f3_narrative/` (narrative_suppressions, language_violations, mode_transitions)

### Runtime Result
- First pass: `CAUSAL_ONLY` (active suppression)
- Subsequent unchanged pass: `SILENCED` (NO_MATERIAL_FACT_CHANGE)

---

## F5: Suppression State

**Remediation pattern**: Explicit suppression with honest stagnation semantics — make inactivity visible and explained.

### Implemented Controls
1. **Suppression State Model** (`src/governance/suppression_state.py`)
   - States: `NONE`, `POLICY_BLOCKED`, `REGIME_DEGRADED`, `DATA_PARTIAL`, `TEMPORAL_DRIFT`, `FRAGILITY_CONSTRAINT`, `MULTI_CAUSAL`
   - `MULTI_CAUSAL` when >1 blocker active; computed per market
   - Persisted: `docs/intelligence/suppression_state_<MARKET>.json`

2. **Suppression Reason Registry** (persisted per market)
   - Required fields: blocking_layer, blocking_condition, since_timestamp, affected_actions, clearing_condition
   - Artifacts: `docs/intelligence/suppression_reason_registry_<MARKET>.json`
   - Guarantee: no non-NONE state without at least one registered reason

3. **Loud Stagnation Semantics** (`src/dashboard/backend/loaders/narrative.py`)
   - Active suppression → `ACTION BLOCKED DUE TO: <reason>`
   - Forward-looking output suppressed; source citations from reasons

4. **"Why Nothing Is Happening" Dashboard Panel**
   - `src/dashboard/frontend/src/components/WhyNothingIsHappening.jsx`
   - Displays: suppression_state, primary/secondary reasons, since_timestamp, clearing condition
   - Uses explicit block phrasing (no euphemistic language)

5. **Audit Logging**: `docs/audit/f5_suppression/` (state_snapshots, state_transitions)

### Runtime Result
- US: `MULTI_CAUSAL` (temporal drift + data partiality + regime degraded + policy blocked + fragility constraint)
- INDIA: `TEMPORAL_DRIFT`

---

## Cross-Factor Dependencies

```
F1 (Temporal Drift)
  └─→ F5 (triggers TEMPORAL_DRIFT suppression)
       └─→ F3 (suppression gates narrative to CAUSAL_ONLY or SILENCED)

F2 (Regime Partiality)
  └─→ F5 (triggers REGIME_DEGRADED suppression)
  └─→ F3 (degraded regime blocks EXPLANATORY narrative)

F5 (Suppression)
  └─→ F3 (any active suppression disables forward-looking narrative)
  └─→ Dashboard ("Why Nothing Is Happening" panel)
```

## Common Non-Goals Compliance (All Factors)
- No Truth Epoch advancement
- No automatic evaluation trigger
- No execution or capital enablement
- No ingestion cadence changes
- No silent factor recomputation
- No language softening or engagement optimization
