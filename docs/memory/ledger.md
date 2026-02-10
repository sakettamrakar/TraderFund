# Ledger

> [!IMPORTANT]
> **Authoritative Source**: `docs/memory/03_domain/domain_model.md` is CANONICAL.
> This document defines the system's "Epistemic Memory" structure.
> **The Past Is Immutable.** The Future Is Governed.

---

## 1. Epistemic Authority Hierarchy

The global hierarchy of truth is strictly defined. Lower layers cannot override higher layers.

| Authority Level | Source | Mutable? | Purpose |
| :--- | :--- | :--- | :--- |
| **1. Human Command** | Real-time Decision | **Yes** | Ultimate override. "Stop everything." |
| **2. Decision Ledger** | `decisions.md` | **No** (Append-Only) | Architectural intent. "Why we separate US/India." |
| **3. Invariants** | `architectural_invariants.md` | **No** (Permanent) | Laws of physics. "No live execution." |
| **4. Constraints** | `active_constraints.md` | **Yes** (Governed) | Temporary rules. "Phase 1 limits." |
| **5. Assumptions** | `assumption_changes.md` | **Yes** (Tracked) | Working theories. "API allows 5 req/min." |
| **6. Evolution Log** | `evolution_log.md` | **No** (Append-Only) | History of what happened. "Tick 1045 processed." |

*(Source: `docs/epistemic/ledger/decisions.md`)*

---

## 2. Ledger Registry

| Ledger | Path | Content | Format |
| :--- | :--- | :--- | :--- |
| **Decision Ledger** | `docs/epistemic/ledger/decisions.md` | Irreversible architectural choices (D-series, EV-series). | Markdown (ADR ref) |
| **Evolution Log** | `docs/epistemic/ledger/evolution_log.md` | Chronological system states (ticks, regime shifts). | JSONL / Markdown |
| **Phase Lock** | `docs/phase_locks/*.md` | Artifact hashes proving a phase is complete/frozen. | Markdown + SHA256 |
| **Activation Log** | `docs/governance/ACTIVATION_LOG.md` | Module promotions (Research -> Production). | Markdown Table |
| **Impact Ledger** | `docs/epistemic/ledger/impact_ledger.md` | Documentation changes (DIDs) and their resolution. | Markdown List |
| **Assumption Log** | `docs/epistemic/ledger/assumption_changes.md` | Invalidated assumptions and new learnings. | Markdown Table |

---

## 3. Ledger Rules

### 3.1 Immutability
*   **The Past is Frozen**: Once an entry is committed to a ledger (Decision, Evolution, Activation), it **CANNOT BE DELETED OR MODIFIED**.
*   **Correction**: Errors are corrected by appending a new entry that references and supersedes the old one (e.g., `D005 SUPERSEDES D002`).
*   **Audit**: Deletion of ledger entries is a critical security violation.

### 3.2 Explicit Supersession
*   **No Implicit Changes**: A new decision cannot implicitly weaken an old one. It must explicitly state "Supersedes D-XXX".
*   **Traceability**: The chain of supersession must be unbroken.

### 3.3 Append-Only
*   All operational logs (Evolution, Audit) are strictly append-only.
*   Retries result in new entries, not overwrites.

### 3.4 Temporal Scoping (Truth Epochs)
*   **Version Lock**: Every `Truth Epoch` (snapshot of reality) is scoped to the `Proxy Set Version` that generated it.
*   **Invalidation**: Changing the definition of "The Market" (Proxy Set) invalidates all prior Truth Epochs for future decision-making. (History is preserved, but validity ends).

---

## 4. Policy Constraints (Memory)

### 4.1 Data Retention
*   **Epistemic Artifacts**: **PERMANENT**.
    *   Scope: Narratives, Decisions, Ledgers.
    *   Constraint: Must reconstruct context of every decision ever made.
*   **Audit Logs**: **Active (90 Days)** -> Archive (1 Year) -> Delete.
    *   Scope: Operational JSON logs.
    *   Rationale: Debugging vs compliance.
*   **Raw Input**: **Active (1 Year)** -> Cold Storage.
    *   Rationale: Re-ingestible, but kept for proof of "what we saw".

### 4.2 Automation Limits
*   **No Auto-Write**: Automation scripts (e.g., `drift_detector.py`) CANNOT write to the Decision Ledger.
*   **Draft Only**: Automation can propose a `Draft DID` or `Draft Decision`, but a HUMAN must commit it.
*   **Read-Only Metrics**: Dashboards read ledgers; they do not write to them.

### 4.3 Conflict Resolution (Ledger Level)
*   **Fork Prevention**: If multiple valid ledgers exist (e.g., git merge conflict), the **Human Maintainer** must manually reconcile and sign the unified state.
*   **Freshness**: In absence of manual resolution, the most recent `main` branch commit is Truth.

*(Sources: `docs/epistemic/truth_epoch_scoping.md`, `docs/epistemic/data_retention_policy.md`)*
