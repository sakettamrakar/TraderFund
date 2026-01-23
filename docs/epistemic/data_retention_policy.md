# Data Retention Policy
**Status**: Authoritative.

## 1. Philosophy
Trader Fund operates on the principle of **Epistemic Permanence**. All data contributing to a decision must be retrievable to reconstruct that decision's context. However, purely operational telemetry can be rotated to manage storage costs.

## 2. Retention Schedules

### 2.1. Epistemic Artifacts
**Scope**: Narratives (`data/narratives`), Decisions (`data/decisions`), Journals (`docs/epistemic/ledger`).
**Policy**: **PERMANENT**.
**Constraint**: These files must NEVER be deleted. They form the system's long-term memory.
**Archival**: May be moved to `data/archive` after 3 years, but must remain readable.

### 2.2. Audit Logs
**Scope**: JSON Logs (`logs/*.json`).
**Policy**: **Active (90 Days) -> Archive (1 Year) -> Delete**.
**Rationale**: Operational debugging requires recent specific logs. Compliance requires medium-term retention.
**Implementation**: Log rotation should move files to `logs/archive/` monthly.

### 2.3. Raw Input Data
**Scope**: Ingested JSON/Parquet (`data/raw/`).
**Policy**: **Active (1 Year) -> Cold Storage**.
**Rationale**: We can re-ingest market data from vendors, but we keep our copy to prove *what we saw at the time*.

### 2.4. Derived Data
**Scope**: Intermediate signals, cache (`data/cache/`).
**Policy**: **Volatile**.
**Rationale**: Can be regenerated from Raw Data + Code.

## 3. Deletion Protocol
**Authorization**: Use of `rm` or `delete` on covered paths requires:
1.  Verification against this policy.
2.  Human approval (via `Drift Detector` flag or explicit command).
