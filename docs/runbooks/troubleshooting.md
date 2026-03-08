# Troubleshooting Guide

**Scope**: Common Operational Failures

## 0. First Response Rule
Before manually retrying broad pipelines, run validation for the affected phase so the system produces a structured diagnosis and any safe remediation options.

Single-phase validation:
```powershell
python -m traderfund.validation.validation_runner --phase <phase> --hook troubleshooting --market US
```

Safe auto-remediation for that same phase:
```powershell
python -m traderfund.validation.validation_runner --phase <phase> --hook troubleshooting --market US --auto-remediate
```

Inspect the resulting summary in `logs/validation/<phase>_troubleshooting_latest.json`.

## 1. API Connectivity Failure
**Symptom**: `ConnectionError` or `Timeout` in logs.
**Action**:
1.  Check local internet.
2.  Check vendor status page (AlphaVantage/AngelOne).
3.  Run `ingestion` validation.
4.  Restart the ingestion script only after validation confirms the issue is operational rather than schema or timestamp drift.

## 2. Pipeline Blockage (No Narratives)
**Symptom**: Raw events incoming, but no Narrative artifacts.
**Action**:
1.  Run `research` validation.
2.  Check `run_narrative.py` logs.
3.  Verify `vector_store` availability.
4.  Check for "System Freeze" flag blocking execution.

## 3. Decision Gap (No Decisions)
**Symptom**: Narratives exist, but `data/decisions/` is empty.
**Action**:
1.  Run `evaluation` validation.
2.  Check `run_decision.py` logs.
3.  Verify Narrative confidence scores > 0.8 (Entry Threshold).
4.  Ensure `Constraint Validator` is not rejecting malformed narratives.

## 4. Data Corruption
**Symptom**: JSON decode errors or invalid timestamps.
**Action**:
1.  Run `ingestion` validation and inspect the `schema_validation`, `timestamp_validation`, and `null_handling` results.
2.  Isolate corrupt file in `data/quarantine/` only if the validation evidence identifies a concrete bad artifact.
3.  Run `Constraint Validator` on remaining files.
4.  Document in `evolution_log.md` if data was deleted.

## 5. Dashboard Looks Wrong But API Is Up
**Symptom**: Dashboard loads, but values are stale, missing provenance, or obviously inconsistent.
**Action**:
1.  Run `dashboard` validation.
2.  Inspect `logs/validation/dashboard_troubleshooting_latest.json`.
3.  If `traceability` or `freshness` fails and a safe remediation is offered, rerun `dashboard` validation with `--auto-remediate`.
4.  Re-run `dashboard` validation without auto-remediation to confirm PASS.

## 6. Historical Replay Drift
**Symptom**: Evaluation outputs differ between replay runs.
**Action**:
1.  Run `evaluation` validation.
2.  Confirm whether the drift is only in timestamp-like fields.
3.  Treat replay determinism as semantic, not raw-hash-based, because evaluation outputs embed runtime timestamps.
4.  If semantic content differs, rerun the specific evaluation profile and inspect downstream artifacts under `docs/evolution/evaluation/`.
