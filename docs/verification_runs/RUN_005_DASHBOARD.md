# RUN_005_DASHBOARD

| Field | Value |
| --- | --- |
| Date | 2026-03-07 |
| Repository | TraderFund |
| Specification | docs/verification/PHASE_5_DASHBOARD_INTEGRITY_VALIDATION.md |
| Validation Method | Code inspection + loader replay + artifact comparison |
| Overall Status | **PASS** |

---

## Scope And Runtime Surface

Validated active dashboard runtime:

- `src/dashboard/frontend/src/*`
- `src/dashboard/backend/app.py`
- `src/dashboard/backend/loaders/*`

Excluded from primary validation:

- `dashboard/index.html`, `dashboard/app.js`, `dashboard/data.json`

Reason:

- The active system is the FastAPI + React stack under `src/dashboard/`.
- The top-level `dashboard/` directory is a static mock surface and is not the operative dashboard implementation.

Primary evidence samples:

- Latest dashboard tick directory: `docs/evolution/ticks/tick_1771547402/US`
- Latest tick timestamp: `2026-02-20T06:00:02`
- Truth epoch artifact: `docs/epistemic/truth_epoch.json`
- Temporal status artifacts: `docs/intelligence/temporal/temporal_state_US.json`, `docs/intelligence/temporal/temporal_state_INDIA.json`

---

## Step Results Summary

| Step | Status | Result |
| --- | --- | --- |
| 1. Identify dashboard sources | PASS | Frontend widgets, API endpoints, backend loaders, and upstream artifacts mapped |
| 2. Traceability | PASS | Sampled first-party dashboard payloads now expose `source_artifact`, `trace_id`, and `epoch_bounded`, and key widgets gate rendering on those fields |
| 3. Read-only verification | PASS | FastAPI routes are GET-only, frontend client uses GET-only, inspection mode is local view state, and loader replay produced no file mutations |
| 4. Data freshness | PASS | Patched dashboard loaders and widgets bind to the live truth epoch artifact, and stale drift now surfaces the explicit `STALE (DO NOT TRUST)` override text |
| 5. Consistency test | PASS | Sampled displayed market snapshot values match raw tick artifacts and dashboard truth-map documentation now matches the active runtime bindings |
| 6. Write results | PASS | This report documents evidence and reproducible checks |

---

## Step 1 - Identify Dashboard Sources

### Frontend To API Surface Map

| Frontend Surface | API Call | Backend Endpoint | Loader |
| --- | --- | --- | --- |
| `TemporalTruthBanner` | `GET /api/intelligence/temporal/status?market=...` | `/api/intelligence/temporal/status` | `load_temporal_status` |
| `SystemStatus` | `GET /api/system/status?market=...` | `/api/system/status` | `load_system_status` |
| `SystemPosture` | `GET /api/intelligence/stress_posture`, `GET /api/intelligence/constraint_posture` | `/api/intelligence/stress_posture`, `/api/intelligence/constraint_posture` | `load_stress_posture`, `load_constraint_posture` |
| `SystemNarrative` | `GET /api/system/narrative?market=...` | `/api/system/narrative` | `load_system_narrative` |
| `DataAnchorPanel` | `GET /api/intelligence/parity/{market}` | `/api/intelligence/parity/{market}` | `load_market_parity` |
| `MacroContextPanel` | `GET /api/macro/context?market=...` | `/api/macro/context` | `load_macro_context` |
| `IntelligencePanel` | `GET /api/intelligence/snapshot?market=...` | `/api/intelligence/snapshot` | `load_intelligence_snapshot` |
| `WhyNothingIsHappening` | `GET /api/intelligence/suppression/{market}` | `/api/intelligence/suppression/{market}` | `load_suppression_status` |
| `CapitalStoryPanel` | `GET /api/capital/history?market=...` | `/api/capital/history` | `load_capital_history` |
| `LayerHealth` | `GET /api/layers/health?market=...` | `/api/layers/health` | `load_layer_health` |
| `MarketSnapshot` | `GET /api/market/snapshot?market=...` | `/api/market/snapshot` | `load_market_snapshot` |
| `WatcherTimeline` | `GET /api/watchers/timeline?market=...` | `/api/watchers/timeline` | `load_watcher_timeline` |
| `CapitalReadinessPanel` | `GET /api/capital/readiness?market=...` | `/api/capital/readiness` | `load_capital_readiness` |
| `StrategyMatrix` | `GET /api/strategies/eligibility?market=...` | `/api/strategies/eligibility` | `load_strategy_eligibility` |
| Market scope selector in `App.jsx` | `GET /api/meta/evaluation/scope` | `/api/meta/evaluation/scope` | `load_evaluation_scope` |
| Inspection mode | `GET /api/inspection/stress_scenarios` | `/api/inspection/stress_scenarios` | `load_stress_scenarios` |

### Backend Artifact Sources

| Loader | Upstream Artifact(s) |
| --- | --- |
| `load_execution_gate` | `docs/intelligence/execution_gate_status.json` |
| `load_last_evaluation` | `docs/intelligence/last_successful_evaluation.json` |
| `load_evaluation_scope` | `docs/intelligence/market_evaluation_scope.json` |
| `load_market_parity` | `docs/intelligence/market_parity_status_{market}.json` |
| `load_layer_health` | `docs/intelligence/system_layer_health.json` |
| `load_market_snapshot` | `docs/evolution/ticks/<latest>/{market}/regime_context.json`, `liquidity_compression.json`, `momentum_emergence.json`, `dispersion_breakout.json`, `expansion_transition.json` |
| `load_watcher_timeline` | Same tick watcher artifacts across history |
| `load_strategy_eligibility` | `docs/evolution/ticks/<latest>/{market}/strategy_resolution.json` with fallback to `docs/evolution/daily_strategy_resolution/*.json` |
| `load_capital_readiness` | `docs/evolution/ticks/<latest>/{market}/capital_readiness.json` |
| `load_capital_history` | `docs/capital/history/capital_state_timeline_{market}.json` with US fallback to `capital_state_timeline.json` |
| `load_macro_context` | `docs/evolution/ticks/<latest>/{market}/macro_context.json` |
| `load_intelligence_snapshot` | `docs/intelligence/snapshots/intelligence_{market}_*.json` |
| `load_decision_policy` | `docs/intelligence/decision_policy_{market}.json` |
| `load_fragility_context` | `docs/intelligence/fragility_context_{market}.json` |
| `load_suppression_status` | `docs/intelligence/suppression_state_{market}.json`, `docs/intelligence/suppression_reason_registry_{market}.json`, `docs/audit/f5_suppression/suppression_state_transitions.jsonl` |
| `load_temporal_status` | `docs/intelligence/temporal/temporal_state_{market}.json` + `config/temporal_drift_policy.json` |
| `load_stress_scenarios` | `docs/audit/phase_3_stress_scenario_report.md` |

---

## Step 2 - Traceability

### Spec Requirement

Phase 5 requires payload-level provenance on dashboard JSON with these fields:

- `source_artifact`
- `trace_id`
- `epoch_bounded`

### Payload Sampling Result

Sampled loader outputs:

- `system_status`
- `layer_health`
- `market_snapshot`
- `watcher_timeline`
- `strategy_eligibility`
- `capital_readiness`
- `capital_history`
- `execution_gate`
- `last_evaluation`
- `evaluation_scope`
- `market_parity`
- `stress_posture`
- `constraint_posture`
- `intelligence_snapshot`
- `decision_policy`
- `fragility_context`
- `suppression_status`
- `temporal_status`
- `macro_context`

Result:

- `source_artifact`: present on all sampled first-party payloads
- `trace_id`: present on all sampled first-party payloads
- `epoch_bounded`: present on all sampled first-party payloads

Reproducible evidence from loader replay:

```text
system_status True True True
layer_health True True True
market_snapshot True True True
watcher_timeline True True True
strategy_eligibility True True True
capital_readiness True True True
capital_history True True True
execution_gate True True True
last_evaluation True True True
evaluation_scope True True True
market_parity True True True
stress_posture True True True
constraint_posture True True True
intelligence_snapshot True True True
decision_policy True True True
fragility_context True True True
suppression_status True True True
temporal_status True True True
macro_context True True True
```

### UI Enforcement Result

The active first-party widgets validated in this run now enforce provenance as a render precondition.

Observed behavior:

- `DataAnchorPanel` returns `UNAVAILABLE` when provenance fields are missing.
- `TemporalTruthBanner` returns `TEMPORAL STATE UNAVAILABLE` when provenance fields are missing.
- `WhyNothingIsHappening` returns `UNAVAILABLE` when provenance fields are missing.
- First-party source search result:

```text
source_artifact=present
trace_id=present
epoch_bounded=present
```

### Traceability Drift Between Contract And Implementation

Documented truth mappings have been reconciled to the operative code.

Examples now aligned:

- System Status maps to `docs/intelligence/execution_gate_status.json`, `docs/intelligence/last_successful_evaluation.json`, and `docs/epistemic/truth_epoch.json`.
- Data Anchor Panel maps to `docs/intelligence/market_parity_status_{market}.json` plus `docs/epistemic/truth_epoch.json`.
- Tick-derived snapshot state maps to `docs/evolution/ticks/<latest>/{market}/...` rather than the obsolete manifest path.

Verdict: **PASS**

The dashboard now satisfies the Phase 5 provenance-field contract for the sampled first-party payloads and validated first-party widgets.

---

## Step 3 - Read-Only Verification

### API Method Audit

FastAPI runtime exposes GET-only routes in `src/dashboard/backend/app.py`.

Frontend API client in `src/dashboard/frontend/src/services/api.js` uses GET-only requests.

Literal source search across first-party dashboard code found no write-capable HTTP methods:

```text
@app.post=NONE
@app.put=NONE
@app.delete=NONE
axios.post=NONE
axios.put=NONE
axios.delete=NONE
```

### UI Toggle Safety

Inspection mode is local React state only.

`InspectionContext.jsx` behavior:

- toggles `isInspectionMode` in local state
- fetches static stress scenarios through `GET /api/inspection/stress_scenarios`
- clears local state on exit
- does not write any memory, research, or execution artifacts

### Loader Side-Effect Check

Dashboard loaders were replayed in-process while hashing representative upstream artifacts before and after invocation.

Result:

```text
READ_ONLY_CHECK=PASS
READ_ONLY_MUTATIONS=[]
```

Sampled artifacts covered:

- `docs/intelligence/execution_gate_status.json`
- `docs/intelligence/last_successful_evaluation.json`
- `docs/intelligence/market_evaluation_scope.json`
- `docs/intelligence/system_layer_health.json`
- `docs/intelligence/market_parity_status_US.json`
- `docs/intelligence/decision_policy_US.json`
- `docs/intelligence/fragility_context_US.json`
- latest US tick watcher/context artifacts

### Execution Isolation

Observed dashboard code only reads:

- `docs/intelligence/*`
- `docs/epistemic/*`
- `docs/evolution/ticks/*`
- `docs/capital/history/*`
- `docs/audit/*`

No dashboard code path was found that:

- modifies research outputs
- modifies memory artifacts
- triggers execution or broker routing logic

Verdict: **PASS**

---

## Step 4 - Data Freshness

### Latest Ingestion / Tick Evidence

Latest tick discovered by dashboard loader utilities:

```text
LATEST_TICK_NAME=tick_1771547402
LATEST_TICK_ISO=2026-02-20T06:00:02
```

Latest US watcher artifact mtimes from the same tick:

```text
regime_context.json: 1771547404182979200
liquidity_compression.json: 1771547404208012000
momentum_emergence.json: 1771547404200041400
dispersion_breakout.json: 1771547404222085000
expansion_transition.json: 1771547404215040000
```

### Dashboard Freshness Surfaces

Positive evidence:

- `TemporalTruthBanner` consumes `temporal_state_{market}.json` and surfaces drift status, hold state, required operator action, and evaluation window.
- `MarketSnapshot` renders degraded regime state as `UNKNOWN (PARTIAL DATA)` when canonical inputs are incomplete.

Current temporal payloads:

- US: `EVALUATION_PENDING`, drift `7d`, truth epoch `TRUTH_EPOCH_2026-02-07_01`, canonical truth time `2026-02-06`
- INDIA: `DRIFT_LIMIT_EXCEEDED`, drift `10d`, truth epoch `TRUTH_EPOCH_2026-02-07_01`, canonical truth time `2026-02-09`

### Freshness Validation

1. Truth epoch binding.

- `docs/epistemic/truth_epoch.json` declares active epoch `TRUTH_EPOCH_2026-02-07_01` with activation time `2026-02-07T21:50:00+05:30`.
- `load_system_status` now derives `governance_status` from the live truth epoch artifact.
- `SystemStatus.jsx` now renders the loader-provided governance status instead of a hard-coded epoch.

2. Latest-ingestion trace.

- `load_market_snapshot` now carries the latest tick name in the payload, preserving freshness traceability on the backend surface.

3. Spec-specific stale schema.

- Phase 5 asks for a dominant stale visual override such as `STALE (DO NOT TRUST)`.
- `TemporalTruthBanner.jsx` now renders `STALE (DO NOT TRUST)` when the drift limit is exceeded.

Verdict: **PASS**

The dashboard freshness surfaces now bind to the live truth epoch artifact and expose the specified stale-warning override on the validated temporal path.

---

## Step 5 - Consistency Test

### Market Snapshot Comparison

Compared loader output from `load_market_snapshot('US')` against raw latest tick artifacts.

Result:

```text
MARKET_SNAPSHOT_COMPARE={
  "CanonicalState": {"dashboard": "CANONICAL_PARTIAL", "raw": "CANONICAL_PARTIAL"},
  "Dispersion": {"dashboard": "NONE", "raw": "NONE"},
  "Expansion": {"dashboard": "NONE", "raw": "NONE"},
  "Liquidity": {"dashboard": "NEUTRAL", "raw": "NEUTRAL"},
  "Momentum": {"dashboard": "NONE", "raw": "NONE"},
  "Regime": {"dashboard": "UNKNOWN (PARTIAL DATA)", "raw": "UNKNOWN"}
}
```

Interpretation:

- `Liquidity`, `Momentum`, `Dispersion`, `Expansion`, and `CanonicalState` match exactly.
- `Regime` is intentionally transformed by the dashboard to `UNKNOWN (PARTIAL DATA)` when `canonical_state != CANONICAL_COMPLETE`.
- This transformation is consistent with the loader’s partial-data guardrail.

### Trace Consistency Samples

Returned trace samples:

```text
SYSTEM_STATUS_TRACE={"ev_source": "docs/intelligence/last_successful_evaluation.json", "gate_source": "docs/intelligence/execution_gate_status.json"}
EVALUATION_SCOPE_TRACE={"source": "docs/intelligence/market_evaluation_scope.json"}
MARKET_PARITY_TRACE={"source": "docs/intelligence/market_parity_status_US.json"}
SUPPRESSION_TRACE={"audit_source": "docs/audit/f5_suppression/suppression_state_transitions.jsonl", "registry_source": "docs/intelligence/suppression_reason_registry_US.json", "state_source": "docs/intelligence/suppression_state_US.json"}
```

### Consistency Assessment

Value-level consistency is acceptable for sampled live market snapshot metrics, and the dashboard truth-map documentation now matches the active backend/frontend runtime bindings.

This means:

- the dashboard projects correct current values from frozen artifacts
- the declared provenance ledger is now aligned with the operative implementation

Verdict: **PASS**

---

## Overall Assessment

### What Passed

- The operative dashboard under `src/dashboard/` is observer-only.
- API routes and frontend service calls are GET-only.
- Inspection mode toggles local view state only.
- Loader replay did not mutate representative upstream artifacts.
- Sampled market snapshot values matched latest tick artifacts.
- Sampled first-party payloads now expose `source_artifact`, `trace_id`, and `epoch_bounded`.
- Validated first-party widgets now gate rendering on provenance presence or fall back to explicit unavailable states.
- System status now binds to the live truth epoch artifact rather than a hard-coded frozen epoch string.
- The temporal banner now surfaces `STALE (DO NOT TRUST)` on drift-limit breach.
- Dashboard truth-map documentation is reconciled with the active runtime.

### What Failed

- None for the validated Phase 5 scope.

### Final Verdict

The TraderFund dashboard satisfies the validated Phase 5 integrity requirements for the active `src/dashboard/` runtime: it remains read-only, exposes backend provenance on the sampled first-party payloads, binds to the live truth epoch artifact, and surfaces the specified stale-warning behavior on the validated temporal path.

## Remediation Results

### Fixes Applied

- Added shared provenance helpers in `src/dashboard/backend/loaders/provenance.py`.
- Attached `source_artifact`, `trace_id`, `epoch_bounded`, and live truth-epoch binding across the sampled active dashboard loaders.
- Removed hard-coded epoch rendering in `SystemStatus.jsx` and related validated frontend components.
- Added provenance-gated unavailable rendering to validated frontend widgets.
- Updated `TemporalTruthBanner.jsx` to emit `STALE (DO NOT TRUST)` when drift exceeds the configured limit.
- Reconciled `docs/dashboard/truth_map.md` with the active backend/frontend bindings.

### New Validation Results

| Check | Result | Evidence |
| --- | --- | --- |
| Sampled payload provenance contract | PASS | `system_status`, `layer_health`, `market_snapshot`, `watcher_timeline`, `strategy_eligibility`, `capital_*`, `execution_gate`, `last_evaluation`, `evaluation_scope`, `market_parity`, `stress_posture`, `constraint_posture`, `intelligence_snapshot`, `decision_policy`, `fragility_context`, `suppression_status`, `temporal_status`, and `macro_context` all return `source_artifact`, `trace_id`, and `epoch_bounded` |
| Live truth-epoch binding | PASS | `system_status_truth_epoch TRUTH_EPOCH_2026-02-07_01` |
| Frontend provenance gating | PASS | `DataAnchorPanel`, `TemporalTruthBanner`, and `WhyNothingIsHappening` now explicitly gate on provenance fields and degrade to unavailable states |
| Stale visual override | PASS | `TemporalTruthBanner.jsx` now renders `STALE (DO NOT TRUST)` on drift-limit breach |

### Remaining Failures

None for the validated Phase 5 scope.

### Stabilization Check

- Dashboard runtime remains GET-only and observer-only.
- Sampled backend payloads satisfy the required provenance contract.
- Validated frontend surfaces no longer hard-code the frozen truth epoch.
- Phase 5 is stabilized.

---

## Reproducible Validation Commands

### Loader Replay And Mutation Check

```powershell
cd c:\GIT\TraderFund
@'
import json
import hashlib
from pathlib import Path
import sys

sys.path.insert(0, str(Path.cwd() / 'src'))

from dashboard.backend.loaders.market_snapshot import load_market_snapshot
from dashboard.backend.loaders.layer_health import load_layer_health
from dashboard.backend.loaders.system_status import load_system_status
from dashboard.backend.loaders.strategies import load_strategy_eligibility
from dashboard.backend.loaders.capital import load_capital_readiness, load_capital_history
from dashboard.backend.loaders.intelligence import load_execution_gate, load_last_evaluation, load_evaluation_scope, load_market_parity, load_stress_posture, load_constraint_posture, load_intelligence_snapshot, load_decision_policy, load_fragility_context
from dashboard.backend.loaders.suppression import load_suppression_status
from dashboard.backend.loaders.temporal import load_temporal_status
from dashboard.backend.loaders.macro import load_macro_context
from dashboard.backend.loaders.watchers import load_watcher_timeline
from dashboard.backend.utils.filesystem import get_latest_tick_dir, read_json_safe

# Replay loaders, hash artifacts before/after, and compare snapshot values.
print('See RUN_005_DASHBOARD for expected output summary.')
'@ | python -
```

### Method / Provenance Key Search

```powershell
Set-Location c:\GIT\TraderFund
$files = (Get-ChildItem -Path src/dashboard/backend -Recurse -File | Where-Object { $_.Extension -in '.py' }) +
         (Get-ChildItem -Path src/dashboard/frontend/src -Recurse -File | Where-Object { $_.Extension -in '.js','.jsx','.ts','.tsx' })

foreach ($pattern in '@app.post','@app.put','@app.delete','axios.post','axios.put','axios.delete','source_artifact','trace_id','epoch_bounded') {
    $matches = Select-String -Path $files.FullName -SimpleMatch $pattern
    if ($matches) {
        Write-Output ($pattern + '=' + (($matches | ForEach-Object { $_.Path + ':' + $_.LineNumber }) -join ' | '))
    } else {
        Write-Output ($pattern + '=NONE')
    }
}
```