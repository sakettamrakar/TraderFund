# F5 Suppression Implementation Report

## Scope
This report documents implementation of F5 remediation for explicit suppression and honest stagnation semantics.

- Execution mode: `REAL_RUN`
- Truth Epoch: `TE-2026-01-30` (frozen)
- Markets: `US`, `INDIA`
- Invariants preserved: `INV-NO-EXECUTION`, `INV-NO-CAPITAL`, `INV-HONEST-STAGNATION`, `INV-TRUTH-EPOCH-EXPLICIT`, `INV-NO-TEMPORAL-INFERENCE`, `INV-PROXY-CANONICAL`

## 1. Suppression State Model
Implemented explicit enumerable suppression states in:
- `src/governance/suppression_state.py`

State set implemented:
- `NONE`
- `POLICY_BLOCKED`
- `REGIME_DEGRADED`
- `DATA_PARTIAL`
- `TEMPORAL_DRIFT`
- `FRAGILITY_CONSTRAINT`
- `MULTI_CAUSAL`

State behavior:
- Suppression state is computed per market.
- `MULTI_CAUSAL` is emitted when more than one blocker is active.
- State is persisted to `docs/intelligence/suppression_state_<MARKET>.json`.

## 2. Suppression Reason Registry
Implemented reason registry persistence with required fields:
- `blocking_layer`
- `blocking_condition`
- `since_timestamp`
- `affected_actions`
- `clearing_condition`

Artifacts:
- `docs/intelligence/suppression_reason_registry_US.json`
- `docs/intelligence/suppression_reason_registry_INDIA.json`

Guarantee enforced:
- No non-`NONE` suppression state is produced without at least one registered reason.

## 3. Loud Stagnation Semantics
Implemented explicit blocker language for narrative/blocker surfaces.

Updated:
- `src/dashboard/backend/loaders/narrative.py`

Behavior:
- If `suppression_state != NONE`, narrative is forced to causal form:
  - `ACTION BLOCKED DUE TO: <reason>`
- Forward-looking narrative output is suppressed under active suppression.
- Narrative payload now includes source citations from suppression reasons.

## 4. Narrative Interaction Rules
Implemented suppression-aware narrative rules:
- Active suppression disables forward-looking text.
- Narrative text references suppression reason IDs, blocking layers, and clearing conditions.

Endpoint wiring:
- `/api/system/narrative?market=<US|INDIA>` now returns market-scoped suppression-aware narrative.

## 5. Dashboard Panel: Why Nothing Is Happening
Implemented dedicated panel backed by suppression state + reason registry.

Updated:
- `src/dashboard/frontend/src/components/WhyNothingIsHappening.jsx`
- `src/dashboard/frontend/src/components/WhyNothingIsHappening.css`
- `src/dashboard/frontend/src/services/api.js`
- `src/dashboard/backend/app.py`
- `src/dashboard/backend/loaders/suppression.py`

Panel fields now display:
- `suppression_state`
- primary reason
- secondary reasons (when `MULTI_CAUSAL`)
- `since_timestamp`
- clearing condition

Language semantics:
- Uses explicit block phrasing.
- Does not use motivational or euphemistic inactivity language.

## 6. Audit and Evolution Logging
Implemented F5 audit logging under:
- `docs/audit/f5_suppression/suppression_state_snapshots.jsonl`
- `docs/audit/f5_suppression/suppression_state_transitions.jsonl`
- `docs/audit/f5_suppression/README.md`

Evolution first-class treatment:
- `src/evolution/orchestration/ev_tick.py` now computes suppression per market each tick.
- EV ledger entries now include:
  - suppression state
  - suppression reason

## 7. Runtime Artifacts Produced
Suppression state artifacts:
- `docs/intelligence/suppression_state_US.json`
- `docs/intelligence/suppression_state_INDIA.json`

Reason registries:
- `docs/intelligence/suppression_reason_registry_US.json`
- `docs/intelligence/suppression_reason_registry_INDIA.json`

Observed runtime states:
- `US`: `MULTI_CAUSAL` (temporal drift, data partiality, regime degraded, policy blocked, fragility constraint)
- `INDIA`: `TEMPORAL_DRIFT`

## Validation Executed
Commands run:
- `python -m py_compile src/governance/suppression_state.py scripts/suppression_state_orchestrator.py src/dashboard/backend/loaders/suppression.py src/dashboard/backend/loaders/narrative.py src/dashboard/backend/app.py src/evolution/orchestration/ev_tick.py`
- `python scripts/suppression_state_orchestrator.py --markets US INDIA`
- `python src/evolution/orchestration/ev_tick.py`
- Loader runtime checks for suppression and narrative outputs
- `npm --prefix src/dashboard/frontend run build`

Validation outcome:
- Suppression states persisted for both markets.
- Transition and snapshot logs persisted under F5 audit path.
- Evolution ledger includes suppression state/reason lines.
- Frontend build passes with updated panel wiring.

## Non-Goals Compliance
Confirmed not implemented:
- No automatic execution unblocking.
- No intent inference from inactivity.
- No language softening for comfort semantics.
- No override of F1/F2 constraints.
- No Truth Epoch advancement.
- No execution or capital enablement.
