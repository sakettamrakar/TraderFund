# Temporal Truth Contract & Definitions

**Version**: 1.0.0
**Status**: DRAFT
**Epoch**: TE-2026-01-30
**Intent**: Formalize the representation and flow of time within the TraderFund system to ensure epistemic honesty and prevent implicit temporal inference.

## 1. Core Definitions

The system explicitly rejects ambiguous terms such as "current", "latest", or "today". Instead, it operates on three distinct temporal planes:

### 1.1 Raw Data Time (RDT)
**Definition**: The timestamp of the most recent available data point in the external world or raw ingestion layer.
- **Source**: External APIs (Yahoo Finance), Raw CSVs (`data/us_market/SPY.csv`).
- **Nature**: Chaotic, potentially incomplete, unverified.
- **Responsibility**: Ingestion Layer.
- **Example**: `SPY.csv` has a row for `2026-02-10`. RDT = `2026-02-10`.

### 1.2 Canonical Truth Time (CTT)
**Definition**: The timestamp of the most recent data point that has been **validated**, **cleaned**, and **accepted** into the system's canonical data store.
- **Source**: Internal DataFrames after validation schema checks.
- **Nature**: Clean, trusted, immutable for that epoch.
- **Responsibility**: Validation Layer (Data Integrity).
- **Example**: `SPY.csv` row for `2026-02-10` passed all checks. CTT = `2026-02-10`.

### 1.3 Truth Epoch / Evaluation Time (TE)
**Definition**: The timestamp for which the system has performed a full, governed evaluation cycle. This is the **System Time**.
- **Source**: `truth.json` or Global State.
- **Nature**: The *only* time the Intelligence and Governance layers "know" about.
- **Responsibility**: Orchestrator / Governance Layer.
- **Example**: System ran a full cycle for `2026-02-09`. TE = `2026-02-09`.
    * Even if CTT is `2026-02-10`, the system *does not know* about the 10th until TE advances.

## 2. Invariants & Prohibitions

### 2.1 No Implicit Inference
The system MUST NOT infer "now" or "today" from the system clock (`datetime.now()`). All temporal logic must be relative to the **Truth Epoch (TE)**.

### 2.2 No "Latest" Without Context
The term "latest" is banned in code and UI unless strictly scoped (e.g., "latest_ingested_price"). The UI must explicitly label timestamps as RDT, CTT, or TE.

### 2.3 Explicit Advancement Only
Time (TE) does not flow automatically. Validated CTT does not automatically become TE.
- **Advancement requires an explicit Trigger Event.**
- **Advancement requires passing all Governance Gates.**

## 3. Temporal States

Relationship between the three times defines the system state:

| State | Condition | Description |
| :--- | :--- | :--- |
| **SYNCHRONIZED** | `RDT == CTT == TE` | System is fully up-to-date and evaluated. |
| **PENDING INGESTION** | `RDT > CTT` | Raw data exists but has not been validated. |
| **PENDING EVALUATION** | `CTT > TE` | Data is validated but Intelligence/Decisions have not run. |
| **STALE / DRIFT** | `CTT >> TE` | System has fallen significantly behind validated data. |
| **CORRUPT / INVALID** | `TE > CTT` | System believes it is in a future that has not been validated. (Impossible State) |

## 4. Market-Specific Temporal Streams
Each market (US, INDIA) maintains its own RDT and CTT.
However, **TE is Global** or **Market-Specific** depending on the Scope.
- Ideally, `TE_US` and `TE_INDIA` can move independently.
- Global Scope requires synchronization (`min(TE_US, TE_INDIA)`).

## 5. Persistence
- **RDT**: File System (Raw).
- **CTT**: File System (Canonical/Cleaned).
- **TE**: `global_state.json` or `truth_manifest.json`.

This contract ensures that the system never "hallucinates" a decision for a time it hasn't formally processed.
