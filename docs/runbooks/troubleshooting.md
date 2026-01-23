# Troubleshooting Guide

**Scope**: Common Operational Failures

## 1. API Connectivity Failure
**Symptom**: `ConnectionError` or `Timeout` in logs.
**Action**:
1.  Check local internet.
2.  Check vendor status page (AlphaVantage/AngelOne).
3.  Restart Ingestion script.

## 2. Pipeline Blockage (No Narratives)
**Symptom**: Raw events incoming, but no Narrative artifacts.
**Action**:
1.  Check `run_narrative.py` logs.
2.  Verify `vector_store` availability.
3.  Check for "System Freeze" flag blocking execution.

## 3. Decision Gap (No Decisions)
**Symptom**: Narratives exist, but `data/decisions/` is empty.
**Action**:
1.  Check `run_decision.py` logs.
2.  Verify Narrative confidence scores > 0.8 (Entry Threshold).
3.  Ensure `Constraint Validator` is not rejecting malformed narratives.

## 4. Data Corruption
**Symptom**: JSON decode errors or invalid timestamps.
**Action**:
1.  Isolate corrupt file in `data/quarantine/`.
2.  Run `Constraint Validator` on remaining files.
3.  Document in `evolution_log.md` if data was deleted.
