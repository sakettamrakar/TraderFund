# Impact Resolution Contract

**Status**: Authoritative.

This document defines the rules for resolving **Documentation Impact Declarations (DIDs)**. Resolution is the process of reviewing a declared impact and either applying the necessary changes or dismissing the declaration.

## 1. Resolution Principles

1.  **Human Supremacy**: Only **Humans** may resolve or dismiss a DID.
2.  **Explicit Judgment**: Resolution requires an active decision. Status cannot be inferred or tacitly accepted.
3.  **Assistance Limits**: Automated tools may surfac information, generate checklists, and highlight discrepancies, but they **cannot** make the final toggle of status from "Draft" to "Applied".
4.  **No Implied Correctness**: Resolving a DID means the *documentation* has been updated to reflect reality. It does NOT imply the reality itself (the code change) is correct or approved.

## 2. Assistance Boundaries

To ensure human decision-making remains supreme, assistance tools must adhere to the following borders:

*   **No Auto-Resolution**: A script can never set `Status: Applied` or `Status: Dismissed`.
*   **No Document Mutation**: Assistance tools may read the DID and source files, but they must NOT modify the documentation itself.
*   **No Suggestion of Decision**: Tools can ask "Have you updated `Architecture.md`?", but they cannot say "You *should* update `Architecture.md`".
*   **No Chaining**: Assistance tools must not trigger follow-on actions (like merges or deployments) upon resolution.
*   **Foreground Only**: Resolution assistance runs synchronously and interactively with the human.

## 3. Resolution Outcomes

| Outcome | Description | Status |
| :--- | :--- | :--- |
| **Applied** | The human has manually updated all impacted documents. The DID is now a closed record of that work. | `Status: Applied` |
| **Dismissed** | The human has decided no documentation changes are actually needed (e.g., false positive impact detection). | `Status: Dismissed` |
| **Draft** | The DID is pending review. | `Status: Draft` |

## 4. Multi-User Conflict Resolution

In a multi-human governance model, disagreements on impact scope or resolution may arise.

### 4.1. The "freshness" Rule
If two operators propose conflicting updates to the same epistemic artifact:
*   The update branching from the **most recent** `main` state takes precedence.
*   "Stale" branches must rebase and re-assess impact.

### 4.2. The "Maintainer Veto"
For foundational documents (Invariants, Intent), the original author (or designated Primary Maintainer) holds **Veto Power** over changes proposed by secondary operators.
*   **Veto Effect**: A vetoed DID is marked `Status: Rejected`.
*   **Overrule**: A veto can only be overruled by a **Decision Ledger** entry signed by a quorum (if defined) or the Project Owner.

## 5. Verification Check

Before resolving a DID, the human operator must answer:
1.  Is the Change Summary accurate?
2.  Have all "Potentially Impacted Documents" been checked?
3.  Are the epistemic ledgers (Decisions, Assumptions) in sync?
