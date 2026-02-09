# Truth Advancement Gates

**Version**: 1.0.0
**Epoch**: TE-2026-01-30
**Intent**: Define the specific conditions and validation gates required to advance Temporal Truth (`TE`) from Raw Data (`RDT`).

## 1. Raw → Canonical (Ingestion Gate)

**Trigger**: Ingestion Pipeline Execution (`data_acquisition.py`)
**Source**: External API / Raw CSV
**Target**: Validated DataFrame (`canonical/US_SPY.csv`)

### Gate Conditions (Automatic Check)
1.  **Schema Validity**: All required columns (`Date`, `Open`, `High`, `Low`, `Close`, `Volume`) present and typed correctly.
2.  **Temporal Continuity**:
    - No gaps greater than `MAX_GAP` (e.g., weekend/holiday).
    - `Next_Date == Previous_Date + 1 Day` (Business Days logic).
3.  **Data Integrity**:
    - No `NaN` or `Inf` values in critical columns.
    - `High >= Low`, `High >= Open/Close`, `Low <= Open/Close`.
    - `Volume >= 0`.
4.  **Drift Check**:
    - Price change < `X%` (Circuit Breaker check). **Manual Review** if exceeded.

**Outcome**:
- **PASS**: Append to Canonical Store. Update `CTT`.
- **FAIL**: Reject ingestion. Raise Alert. `CTT` remains at `T-1`.

## 2. Canonical → Evaluation (Intelligence Gate)

**Trigger**: Intelligence/Decision Engine (`run_pipeline.py`)
**Source**: Canonical Data (`CTT`)
**Target**: System State (`TE`)

### Gate Conditions (Governance Check)
1.  **Data Completeness**:
    - All *required* symbols for the market (e.g., `SPY`, `VIX`, `TNX` for US) must have `CTT >= Target_TE`.
    - Partial updates block advancement.
2.  **Epistemic Health**:
    - No outstanding critical alerts in `audit_log`.
    - Inspection Mode is **INACTIVE**.
    - No unauthorized manual overrides active.
3.  **Policy Compliance**:
    - Strategy Eligibility check passes.
    - Risk/Position sizing constraints valid.

**Outcome**:
- **PASS**:
    - Execute Factor Models.
    - Execute Strategy Logic.
    - Execute Governance Checks.
    - **Update `TE` to match `CTT`**.
- **FAIL**:
    - **System Halt**.
    - `TE` remains at `T-1`.
    - Dashboard shows "STALE / EVALUATION PENDING".

## 3. Global Synchronization (Sanity Gate)

**Trigger**: Cross-Market Correlation check (Optional but recommended)

### Condition
- `abs(TE_US - TE_INDIA) <= 1 Day` (Timezone accounting).
- Prevents one market running weeks ahead of another if cross-market signals exist.

**Failure Mode**: If Drift > Threshold, warn operator but allow independent operation *unless* explicit dependency exists.

## 4. Manual Override (Emergency Gate)
**Role**: Admin / Operator
**Action**: Force `TE` advancement or rollback.
**Requirement**:
- Must log stringent justification in `audit_log`.
- Must be performed via CLI with explicit confirmation flag.
