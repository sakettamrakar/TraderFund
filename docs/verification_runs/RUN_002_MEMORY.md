# RUN 002 - Memory Binding Validation

Date: 2026-03-07

Spec consulted: `docs/verification/PHASE_2_MEMORY_BINDING_VALIDATION.md`

Validation mode: read-only

Constraint: live memory was not mutated. Any validation step that would require writing malformed or replayed payloads into live state was replaced with static contract inspection or read-only routing analysis.

## Scope

Goal: verify that ingestion outputs bind correctly into the V3 memory layer architecture.

Method:

- Read the V3 memory architecture in `docs/memory/`
- Trace live datasets through the concrete writer paths in code
- Run the repo's storage classification logic twice on the same live datasets
- Inspect cross-layer persistence targets for contamination
- Inspect mutation contracts for overwrite control and prior-state preservation
- Compare `docs/intelligence` and `docs/meta` for duplication drift

## Step 1 - Memory Layers Identified

Documented layers from `docs/memory/03_domain/domain_model.md`:

| Layer | Responsibility |
| :--- | :--- |
| L0 | Situational data foundation and ingestion inputs |
| L1 | Regime / market reality |
| L2 | Narrative / causal explanation |
| L3 | Meta-analysis / trust filter |
| L4 | Factor analysis |
| L5 | Strategy selection |
| L6 | Opportunity discovery |
| L7 | Convergence and scoring |
| L8 | Execution constraints |
| L9 | Portfolio intelligence |

Documented storage lifecycle from `docs/memory/04_architecture/data_flow.md` and `docs/memory/11_deployment/evolution.md`:

| Storage Layer | Intended Role | Intended Store |
| :--- | :--- | :--- |
| Bronze | Raw external payloads, append-only | `data/raw/` |
| Silver | Canonical validated market data | `data/analytics/{market}/prices/{freq}/` for canonical daily bars and `data/processed/candles/intraday/` for canonical intraday bars |
| Gold | Derived cognitive state / analytics | `data/state/`, `docs/intelligence/`, `data/decisions/`, `data/narratives/` |
| Epistemic | Permanent governance / truth artifacts | `docs/epistemic/ledger/` |
| Audit | Operational telemetry / append logs | `logs/`, `docs/audit/` |

Assessment:

- The cognitive hierarchy is clearly defined.
- The storage hierarchy is now converged. `docs/memory/04_architecture/data_flow.md` and `docs/memory/11_deployment/evolution.md` both describe Silver as the canonical Parquet layer spanning daily market bars in `data/analytics/` and canonical intraday bars in `data/processed/candles/intraday/`.

## Step 2 - Ingestion to Memory Mapping

Real datasets used:

| Dataset | Path | SHA256 |
| :--- | :--- | :--- |
| US raw daily sample | `data/raw/us/2026-02-20/SPY_daily.json` | `a2cc7be44f7a0449181d196c4fc8683f070a4a0884af28e0b8b4e89f50a27738` |
| US canonical sample | `data/analytics/us/prices/daily/AAPL.parquet` | `21f00ca6016e2f29dab45c8b2e675c13ce0d24e0c7704e1b2a0253e34afcc397` |
| India raw intraday sample | `data/raw/api_based/angel/intraday_ohlc/NSE_RELIANCE_2026-01-12.jsonl` | `8469855670cd58abbe283eddcaedd22f1eb70aedb8f8838424fa2bf7619d0dd2` |
| India canonical intraday sample | `data/processed/candles/intraday/NSE_RELIANCE_1m.parquet` | `809925221911c269f29340ec97a21e977fa8cb3b40ad16b290f1244d907584ab` |

Observed writer paths:

| Dataset Family | Writer Path | Observed Storage | Expected Layer | Result |
| :--- | :--- | :--- | :--- | :--- |
| US raw daily snapshots | `ingestion/api_ingestion/alpha_vantage/market_data_ingestor.py` | `data/raw/us/{date}/{symbol}_daily.json` | Bronze / L0 | PASS |
| US staging daily | `ingestion/api_ingestion/alpha_vantage/normalizer.py` | `data/staging/us/daily/{symbol}.parquet` | Internal transitional Silver-like stage | PASS with note |
| US analytics daily | `ingestion/api_ingestion/alpha_vantage/curator.py` | `data/analytics/us/prices/daily/{symbol}.parquet` | Canonical market data / Silver by architecture docs | PASS |
| India raw intraday OHLC | `ingestion/api_ingestion/angel_smartapi/market_data_ingestor.py` | `data/raw/api_based/angel/intraday_ohlc/{exchange}_{symbol}_{date}.jsonl` | Bronze / L0 | PASS |
| India raw LTP snapshots | `ingestion/api_ingestion/angel_smartapi/market_data_ingestor.py` | `data/raw/api_based/angel/ltp_snapshots/ltp_snapshot_{date}.jsonl` | Bronze / L0 | PASS |
| India processed intraday | `ingestion/india_ingestion/candle_aggregator.py` and `processing/intraday_candles_processor.py` | `data/processed/candles/intraday/{exchange}_{symbol}_1m.parquet` | Silver / L0 | PASS |

Evidence from the repo's own validation helper (`scripts/validate_ingestion_run.py`):

- `US raw daily snapshots` classified as `bronze`
- `US staging daily` classified as `silver`
- `US analytics daily` classified as `silver`
- `India raw intraday OHLC` classified as `bronze`
- `India raw LTP snapshots` classified as `bronze`
- `India processed intraday` classified as `silver`

Assessment:

- India ingestion binding is internally consistent: raw JSONL lands in Bronze and canonical Parquet lands in Silver.
- US ingestion binding is now architecturally and operationally consistent:
  - `docs/memory/04_architecture/data_flow.md` treats canonical market Parquet as Silver.
  - `docs/memory/11_deployment/evolution.md` matches that contract and explicitly includes the canonical daily and intraday stores.
  - `scripts/validate_ingestion_run.py` now classifies `data/analytics/us/prices/daily/*.parquet` as Silver.
- Conclusion: memory binding for the inspected live datasets is deterministic and contract-aligned.

## Step 3 - Layer Routing Determinism

Read-only routing check executed twice against the same live datasets by calling `inventory_rows()` from `scripts/validate_ingestion_run.py`.

Results:

- Run 1 hash: `42e58ea7107f5f7ba7c2a86207bdea4d10b974cbd51c59a86679ddaa1f76ad4b`
- Run 2 hash: `42e58ea7107f5f7ba7c2a86207bdea4d10b974cbd51c59a86679ddaa1f76ad4b`
- Determinism: PASS

Routing snapshot:

| Family | Classified Canonical Layer |
| :--- | :--- |
| India processed intraday | silver |
| India raw LTP snapshots | bronze |
| India raw intraday OHLC | bronze |
| US analytics daily | silver |
| US raw daily snapshots | bronze |
| US staging daily | silver |

Assessment:

- Routing is deterministic for the inspected live datasets.
- The routing output now matches the documented canonical contract for both US daily and India intraday artifacts.

## Step 4 - Cross-Layer Contamination

Checks performed:

| Check | Evidence | Result |
| :--- | :--- | :--- |
| Macro data does not enter research layers | `src/macro/macro_context_builder.py` writes to market-specific `macro_context.json`; dashboard reads macro from `docs/macro/context/...`; research output config writes to `data/research/us` | PASS |
| Research output does not enter macro layers | `research_modules/research_output/config.py` targets `data/research/us`; no research writers found targeting `docs/macro` | PASS |
| Evaluation results do not overwrite raw memory | `src/intelligence/decision_policy_engine.py`, `src/governance/suppression_state.py`, and `src/governance/narrative_guard.py` write to `docs/intelligence/` and audit logs, not `data/raw/` | PASS |

Assessment:

- No direct evidence was found that macro snapshots are persisted into research storage.
- No direct evidence was found that research outputs are persisted into macro storage.
- No direct evidence was found that evaluation artifacts write into Bronze/raw storage.

## Step 5 - Mutation Control

Memory update operations identified:

| Operation | Implementation | Contract Shape | Result |
| :--- | :--- | :--- | :--- |
| Raw India ingestion | append mode in `persist_candles()` / `persist_ltp()` | append-only Bronze | PASS |
| Raw US ingestion | new dated JSON file writes | immutable per-date raw snapshot | PASS |
| India canonical rebuild | Parquet rewrite after dedup | contract-defined deterministic canonical overwrite | PASS |
| US curated canonical write | Parquet rewrite from staging | contract-defined deterministic canonical overwrite | PASS with note |
| Canonical partiality state | overwrite current JSON + append audit JSONL | controlled state refresh | PASS with note |
| Suppression state | overwrite current JSON + append snapshots/transitions | controlled, previous state signature preserved | PASS |
| Narrative state | overwrite current JSON + preserve baseline hash/epoch + append audits | controlled, previous state preserved where required | PASS |

Notes:

- `src/governance/suppression_state.py` preserves prior reason timing via `since_timestamp` and appends transition logs.
- `src/governance/narrative_guard.py` preserves previous baseline semantics through `previous_epoch`, `previous_hash`, `material_facts_hash`, and append-only transition / suppression logs.
- `src/governance/canonical_partiality.py` overwrites the current artifact and appends an audit line, but it does not keep a full prior artifact snapshot in the same store.
- `relay.py` contains mutation-oriented test code, including unlink and repeated writes, but that is a validation harness and was not executed against live memory for this run.

Assessment:

- No uncontrolled writes were identified in the inspected production paths.
- Raw memory is protected by append-only behavior in the live ingestion writers.
- Current-state overwrite is used intentionally for intelligence artifacts, with audit trails preserving history where the contract explicitly requires it.

## Step 6 - Meta Layer Authority

Compared live artifacts:

| Artifact Name | Folder A | Hash A | Folder B | Hash B | Result |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `last_successful_evaluation.json` | `docs/intelligence` | `FE444FC9E4493279B8E0ED3459DAD01F795AEE2E51E09C2FA518CA10CCB3240D` | `docs/meta` | absent | PASS |
| `market_evaluation_scope.json` | `docs/intelligence` | `DB4D780FFC9852A653E828EF0708502F3ABC68A995E6BAA2A421CF436898FD36` | `docs/meta` | absent | PASS |

Observed authority state:

- `docs/intelligence/last_successful_evaluation.json` is the sole live artifact for evaluation-time status.
- `docs/intelligence/market_evaluation_scope.json` is the sole live artifact for evaluated-market scope.
- `src/dashboard/backend/api.py` now reads both endpoints from `docs/intelligence/`, matching the existing dashboard loaders.

Assessment:

- Evaluation meta authority is singular and explicit.
- No active code path in the dashboard backend reads from `docs/meta`.
- The duplication drift identified in the original run is resolved.

## Pass/Fail Summary

| Validation Area | Result |
| :--- | :--- |
| Memory layers identified | PASS |
| Ingestion mapping correctness | PASS |
| Layer routing determinism | PASS |
| Cross-layer contamination | PASS |
| Mutation control | PASS with notes |
| Meta layer authority | PASS |

## Final Verdict

Overall result: PASS

Reason:

- Live routing remains deterministic and is now architecturally unambiguous for the inspected canonical stores.
- US canonical market data is classified consistently across the memory docs and repo validation logic.
- Evaluation meta artifacts now have a single live authority under `docs/intelligence`.

## Reproducible Evidence

Read-only routing probe:

```powershell
@'
import json, hashlib
from scripts.validate_ingestion_run import inventory_rows

families = {
    'US raw daily snapshots',
    'US staging daily',
    'US analytics daily',
    'India raw intraday OHLC',
    'India raw LTP snapshots',
    'India processed intraday',
}

rows = sorted(
    [r for r in inventory_rows() if r['family'] in families],
    key=lambda r: r['family'],
)
payload = json.dumps(rows, sort_keys=True)
print(hashlib.sha256(payload.encode()).hexdigest())
print(payload)
'@ | python -
```

Live artifact hashing:

```powershell
Get-FileHash data/raw/us/2026-02-20/SPY_daily.json -Algorithm SHA256
Get-FileHash data/analytics/us/prices/daily/AAPL.parquet -Algorithm SHA256
Get-FileHash data/raw/api_based/angel/intraday_ohlc/NSE_RELIANCE_2026-01-12.jsonl -Algorithm SHA256
Get-FileHash data/processed/candles/intraday/NSE_RELIANCE_1m.parquet -Algorithm SHA256
Get-FileHash docs/intelligence/last_successful_evaluation.json -Algorithm SHA256
Get-FileHash docs/intelligence/market_evaluation_scope.json -Algorithm SHA256
Test-Path docs/meta/last_successful_evaluation.json
Test-Path docs/meta/market_evaluation_scope.json
```

## Remediation Results

### Fixes Applied

- Reconciled the Silver memory contract across `docs/memory/04_architecture/data_flow.md`, `docs/memory/11_deployment/evolution.md`, and `scripts/validate_ingestion_run.py`.
- Updated `src/dashboard/backend/api.py` so evaluation status and evaluation scope resolve from `docs/intelligence/` instead of `docs/meta/`.
- Updated `docs/dashboard/dashboard_binding_ledger.md` so the dashboard binding contract reflects the live intelligence authority.
- Removed the stale duplicate files under `docs/meta/` to eliminate split authority for evaluation metadata.

### New Validation Results

| Check | Result | Evidence |
| :--- | :--- | :--- |
| Canonical storage contract convergence | PASS | Memory docs and validator now agree that US canonical daily Parquet and India canonical intraday Parquet are Silver. |
| Routing determinism rerun | PASS | Two consecutive `inventory_rows()` runs produced the same hash `42e58ea7107f5f7ba7c2a86207bdea4d10b974cbd51c59a86679ddaa1f76ad4b`. |
| Evaluation meta authority | PASS | `docs/meta/last_successful_evaluation.json` and `docs/meta/market_evaluation_scope.json` are absent, and dashboard API reads the intelligence artifacts only. |

### Remaining Failures

None.

### Stabilization Check

- Phase 2 memory binding checks now pass for the inspected live datasets.
- Canonical storage authority is singular and documented consistently.
- Evaluation metadata authority is singular and enforced by the active dashboard backend.