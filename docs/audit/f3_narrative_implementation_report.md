# F3 Narrative Leakage Implementation Report

## Scope
Implementation executed for `F3` remediation to eliminate narrative leakage and enforce regime-gated narrative safety.

- Execution mode: `REAL_RUN`
- Truth Epoch: `TE-2026-01-30` (frozen)
- Markets: `US`, `INDIA`
- Invariants preserved: `INV-NO-EXECUTION`, `INV-NO-CAPITAL`, `INV-HONEST-STAGNATION`, `INV-TRUTH-EPOCH-EXPLICIT`, `INV-NO-TEMPORAL-INFERENCE`

## 1. Narrative Gating Rules
Implemented explicit narrative gating by:
- `suppression_state` (F5)
- `regime_state` / `regime_confidence` (F2-compatible)
- `canonical_state`

Implemented in:
- `src/governance/narrative_guard.py`
- `src/dashboard/backend/loaders/narrative.py`

Behavior:
- If `suppression_state != NONE` then forward-looking narrative is disabled.
- If `regime_state` is `UNKNOWN/DEGRADED` or confidence is degraded, narrative is not explanatory.
- If `canonical_state != CANONICAL_COMPLETE`, explanatory mode is blocked.

## 2. Narrative Modes (Explicit + Persisted)
Implemented explicit persisted mode:
- `SILENCED`
- `CAUSAL_ONLY`
- `EVIDENCE_ONLY`
- `EXPLANATORY`

Persisted artifact:
- `docs/intelligence/narrative_state_<MARKET>.json`

Payload fields include:
- `narrative_mode`
- `gating_reason` + `gating_reasons`
- `silence_reason`
- `provenance_references`
- `narrative_diff`

## 3. Hard Language Ban Enforcement
Implemented hard bans for:
- Action verbs: `buy`, `sell`, `enter`, `exit`
- Confidence escalation: `strong`, `clear`, `likely`, `expected`
- Temporal promises: `soon`, `setting up`, `about to`
- Optimization language: `best`, `opportunity`, `edge`
- Causal closure: `therefore`, `hence`, `this means`

Behavior:
- If banned language is detected in generated narrative output:
  - Output is blocked (`narrative_mode = SILENCED`)
  - Violation event is logged

Audit path:
- `docs/audit/f3_narrative/language_violations.jsonl`

## 4. Narrative Diffing vs Last Truth-Epoch Narrative
Implemented material-fact diffing (`narrative_diff`) against the last persisted TE-bound narrative state.

Behavior:
- If no material factual change:
  - `narrative_mode := SILENCED`
  - Silence reason is explicit

Persisted diff fields:
- `status` (`NO_BASELINE` / `CHANGED` / `UNCHANGED`)
- `changed_fields`
- `baseline_truth_epoch`

## 5. Dashboard Binding
Updated narrative panel to expose governance semantics:
- `narrative_mode`
- gating reason (including silent-state explanation)
- provenance references

Updated files:
- `src/dashboard/frontend/src/components/SystemNarrative.jsx`
- `src/dashboard/frontend/src/components/SystemNarrative.css`

Result:
- Silence is visible and explained.
- Narrative source/provenance is operator-visible.

## 6. Audit and Evolution Logging
Implemented F3 logging under:
- `docs/audit/f3_narrative/narrative_suppressions.jsonl`
- `docs/audit/f3_narrative/language_violations.jsonl`
- `docs/audit/f3_narrative/narrative_mode_transitions.jsonl`
- `docs/audit/f3_narrative/README.md`

Evolution integration:
- `src/evolution/orchestration/ev_tick.py` now computes and persists narrative state per market (`narrative_state.json` in tick output).
- Evolution ledger entries now include:
  - narrative mode
  - narrative gate reason

## 7. Runtime Artifacts Produced
Narrative state artifacts:
- `docs/intelligence/narrative_state_US.json`
- `docs/intelligence/narrative_state_INDIA.json`

Observed runtime behavior:
- First pass: `CAUSAL_ONLY` (active suppression)
- Subsequent unchanged pass: `SILENCED` (`NO_MATERIAL_FACT_CHANGE`)

## Validation Executed
Commands run:
- `python -m py_compile src/governance/narrative_guard.py src/dashboard/backend/loaders/narrative.py src/evolution/orchestration/ev_tick.py scripts/narrative_guard_orchestrator.py`
- `python scripts/narrative_guard_orchestrator.py --markets US INDIA` (run twice to verify diff suppression)
- `python src/evolution/orchestration/ev_tick.py`
- `npm --prefix src/dashboard/frontend run build`

Validation outcome:
- Narrative mode artifacts persisted for `US` and `INDIA`.
- Narrative transition/suppression logs persisted under F3 audit path.
- Diffing enforces `SILENCED` when no material factual change.
- Dashboard build succeeds with narrative disclosure updates.

## Non-Goals Compliance
Confirmed not implemented:
- No advice/recommendation generation.
- No intent inference from blocked states.
- No softening language for engagement.
- No override of F5 suppression or F2 degradation.
- No Truth Epoch advancement.
- No execution or capital enablement.
