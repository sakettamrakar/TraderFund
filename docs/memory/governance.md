# Governance

> [!IMPORTANT]
> **Authoritative Source**: `docs/memory/03_domain/domain_model.md` is CANONICAL.
> This document aggregates all governance rules, approval flows, escalation paths, and policy constraints.
> **Human Authority is Supreme.** No automation may override a human decision.

---

## 1. Core Principles

| Principle | Description |
| :--- | :--- |
| **Human Supremacy** | Humans are the final authority on all specifications, decisions, and overrides. Algorithms advise; humans decide. |
| **Progressive Trust** | Trust is zero by default and earned through explicit gates (Observation → Paper → Production). |
| **Fail-Closed** | Ambiguity or error results in denial of action (halt/reject), never default permission. |
| **Separation of Powers** | Intelligence (Truth) is strictly separated from Execution (Action). |
| **Explicit Intent** | All state changes must be preceded by a recorded intent (Decision, DID, or Command). |

*(Sources: `docs/epistemic/impact_resolution_contract.md`, `docs/memory/09_security/trust.md`)*

---

## 2. Approval Flows

### 2.1 Truth Advancement (The "Release" of Time)

Time in the system does not flow automatically. It advances only when validity is proven.

| Gate | Check | Failure Consequence |
| :--- | :--- | :--- |
| **1. Ingestion Gate** | Schema, Range, Continuity, Drift | Reject Data, Halt Time (CTT steady) |
| **2. Intelligence Gate** | Completeness, Epistemic Health, Policy | Halt Time (TE steady), Alert Operator |
| **3. Synchronization Gate** | US/India Alignment check | Warn Operator (Allow split operation) |
| **4. Manual Override** | Human Command + Audit Log | **Force Advancement** (Emergency only) |

*(Source: `docs/governance/truth_advancement_gates.md`)*

### 2.2 Research Module Promotion (The "Release" of Code)

Research code must pass 5 strict gates to become Production code.

| Gate | Requirement | Proof |
| :--- | :--- | :--- |
| **1. Phase Compatibility** | Project Phase ≥ Module Activation Phase | Roadmap Check |
| **2. Observation** | 30 Trading Days error-free | Logs |
| **3. Paper Trading** | 100 Trades w/ <5% Slippage Variance | Shadow Run Artifacts |
| **4. Human Approval** | Explicit Sign-off in `ACTIVATION_LOG.md` | Git Commit |
| **5. Technical Rigor** | >90% Test Coverage + Integration Pass | CI/Test Report |

**Reversibility**: Any production anomaly triggers immediate revert to Research status via Global Kill-Switch.

*(Source: `docs/governance/RESEARCH_MODULE_GOVERNANCE.md`)*

### 2.3 Documentation Impact (The "Release" of Truth)

Changes to documentation (Epistemic Truth) follow the DID process.

1.  **Detect Impact**: Identify discrepancies between Reality (Code) and Truth (Docs).
2.  **Declare DID**: Create a `DID-XXXX` record with `Status: Draft`.
3.  **Human Resolution**: Operator reviews and applies changes.
    *   **Applied**: Docs updated. DID Closed.
    *   **Dismissed**: False positive. DID Closed.
    *   **Rejected**: Change violated invariants (Veto).

*(Source: `docs/epistemic/impact_resolution_contract.md`)*

---

## 3. Escalation Paths

### 3.1 Conflict Resolution

When operators or rules conflict, the system resolves upward.

| Priority | Resolution Rule |
| :--- | :--- |
| **Level 1 (Highest)** | **Human Decision** (Real-time override) |
| **Level 2** | **Project Owner / Quorum** (Decision Ledger Sign-off) |
| **Level 3** | **Primary Maintainer Veto** (Foundational Docs) |
| **Level 4** | **"Freshness" Rule** (Most recent `main` commit wins) |
| **Level 5 (Lowest)** | **Automated Default** (Fail-Closed) |

**The Veto**: The original author of a foundational document (Invariant, Intent) holds veto power over changes. Overruling requires Level 2 authority.

### 3.2 Automation Escalation

Under the **Bounded Automation Contract** (Active Phase 6):

1.  **Monitor Detects Issue**: Logs `[SUGGESTION]` (INFO/WARN).
2.  **Passive Wait**: Monitor does NOT act.
3.  **Human Review**: Operator sees suggestion in Audit Log.
4.  **Human Action**: Operator executes the suggestion (or ignores it).

**Escalation to Action**: A monitor can only self-escalate to action if it has graduated to "Active Automator" via a specific Decision Ledger entry.

### 3.3 Kill-Switches

Emergency halts escalate cleanly to prevent cascading damage.

| Reach | Trigger | Reset Authority |
| :--- | :--- | :--- |
| **Global** | Drawdown > 10% OR 3+ Integrity Failures | **Human Only** (Manual Restart) |
| **Family** | Family Drawdown > 3% | **Human Only** |
| **Strategy** | Strategy Drawdown > 2% | **Human Only** |

*(Source: `docs/capital/kill_switch.md`)*

---

## 4. Policy Constraints (The Laws)

### 4.1 Forbidden Actions (Invariants)

These actions are architecturally impossible or strictly banned.

1.  **INV-NO-EXECUTION**: No broker API calls for orders. No capital movement.
2.  **INV-NO-SELF-ACTIVATION**: System cannot promote itself to production.
3.  **INV-PROXY-CANONICAL**: No data ingestion bypassing the proxy/validation layer.
4.  **INV-TRUTH-EPOCH-EXPLICIT**: No use of `system_clock` for business logic ("Now" is forbidden).
5.  **INV-HONEST-STAGNATION**: If data is missing/bad, system HALTS. No interpolation/guessing.

### 4.2 Research Constraints

Research modules must remain in the "Research World".

*   **Physical Isolation**: Must reside in `research_modules/`.
*   **Import Barrier**: Cannot import into `core_modules/`.
*   **Execution Isolation**: No runtime hooks into the main loop.
*   **Configuration**: Defaults to `ENABLED=False`.

### 4.3 Credential Policy

*   **Zero Trust**: API keys are treated as toxic waste.
*   **Storage**: `.env` only (gitignored).
*   **Memory**: Session tokens strictly in-memory (swapped out on exit).
*   **Rotation**: Manual rotation by Operator Only.

### 4.4 Chat Interface Contract

*   **Draft Only**: AI Chat can draft commands.
*   **No Execution**: AI Chat CANNOT execute commands.
*   **Bridge**: Human must explicitly confirm (`Y/N`) on the CLI bridge.
*   **No Hidden Chains**: One command = One action.

*(Source: `docs/epistemic/chat_execution_contract.md`)*
