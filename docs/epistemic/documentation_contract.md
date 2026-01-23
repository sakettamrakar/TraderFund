# Documentation Contract

**Status**: Authoritative.

This document defines the rules for documentation generation within the Trader Fund ecosystem. Documentation is treated as a mandatory side effect of meaningful system activity, not an afterthought.

## 1. Documentation Principles
1.  **Mandatory Side Effect**: No meaningful code, configuration, or structural change is considered complete without its corresponding documentation artifact.
2.  **No Authority**: Documentation does NOT grant authority or permission to violate invariants. It only records what happened.
3.  **No Justification**: Documentation cannot be used to justify a change that violates the Project Intent or Decision Ledger.
4.  **Failure State**: A code change without a Documentation Impact Declaration (DID) is considered a process failure and must be reverted or remediated immediately.

## 2. Change Classification

### Editorial Documentation Changes
*   **Definition**: Changes to spelling, grammar, formatting, or clarity that do not alter the meaning, obligation, or technical behavior of the system.
*   **Requirement**: Standard commit message.
*   **Impact**: **None**. No further documentation required.

### Epistemic Documentation Changes
*   **Definition**: Changes that alter the intent, authority, obligation, or epistemic status of any component.
*   **Requirement**: Must be recorded in the appropriate **Epistemic Ledger** (e.g., `decisions.md`, `assumption_changes.md`).
*   **Impact**: **High**. Requires human review and explicit ledger entry.

### Explicit Exemptions
The following do **NOT** require a DID:
*   **Test-Only**: Changes to test code with no behavioral impact on the system.
*   **Pure Refactor**: Internal refactoring with ZERO external or epistemic side effects.
*   **Comment/Format**: Changes strictly limited to comments or code formatting.

**Rule**: Ambiguity defaults to requiring a DID. If it is unclear if a change has behavioral impact, a DID is **MANDATORY**.

## 3. Documentation Impact Declarations (DID)

A **Documentation Impact Declaration (DID)** is a required artifact for all:
*   Code changes
*   Module additions
*   Integration changes
*   Configuration changes

### Location
All DIDs must be stored in: `docs/impact/`

### Constraints
*   **Declaration Only**: DIDs declare potentially impacted operational documents (e.g., Runbooks, Architecture).
*   **No Auto-Update**: DIDs do NOT automatically update the target documents.
*   **No Authority**: DIDs do NOT grant authority to proceed with a dangerous change.

### Temporal Requirement
*   **Rule of Presence**: A DID must exist **BEFORE** or **AT THE TIME** a change is introduced.
*   **Remediation Marking**: Retroactive DIDs are allowed ONLY for emergency remediation and must be explicitly marked as such.
*   **No Post-Hoc Documentation**: Silent post-hoc documentation (documenting after the fact) is strictly forbidden.

## 4. DID Naming & Structure

### Naming Convention
`YYYY-MM-DD__<scope>__<short-description>.md`
*   Example: `2026-01-18__ingestion__switch-to-websocket.md`

### Required Structure
```markdown
# Documentation Impact Declaration

**Change Summary**: [One line description]
**Change Type**: [Code / Config / Architecture / Invariant]

## Impact Analysis
*   **Potentially Impacted Documents**: [List of files]
*   **Impact Nature**: [Description of what needs to change in those files]

## Required Actions
*   [ ] Update [File A]
*   [ ] Create [File B]

## Epistemic Impact
*   **Invariants Affected**: [None / List]
*   **Constraints Affected**: [None / List]

**Status**: [Draft / Applied / Rejected]
```

## 5. Relationship to Skills

*   **Drafting**: Skills (specifically the **Change Summarizer**) are permitted to *draft* Documentation Impact Declarations based on observed activity.
*   **Resolution**: Only **Humans** may finalize, resolve, or apply the actions listed in a DID.
*   **Exclusive Right**: The `Change Summarizer` relates primarily to generating these summaries; other skills should not be generating DIDs.

## 6. Relationship to Epistemic Ledgers

A Documentation Impact Declaration (DID) is **declarative**, not **authoritative**.

*   **No Substitution**: A DID does NOT replace a Decision Ledger entry (`decisions.md`).
*   **No Substitution**: A DID does NOT replace an Assumption Change (`assumption_changes.md`).
*   **Escalation Mandate**: If a change alters intent, authority, or invariants, it **MUST escalate** to the appropriate ledger. A DID is a downstream artifact describing the *impact* of a decision, not the decision itself.

## 7. Governance and Consistency

1.  **No Justification**: Documentation cannot be used to justify violations of the Project Intent or existing constraints.
2.  **No Authorization**: Documentation does not authorize change; it only records the intent and impact for human audit.
3.  **No Substitution**: Documentation is a side effect of governance, not a substitute for it.

In all cases, this contract prefers **RESTRICTION** over **FLEXIBILITY**.

## 8. Non-Goals

1.  **No Auto-Cascading**: Documentation must NOT automatically trigger updates in other documents. "Magic links" are forbidden.
2.  **No Escalation**: Documentation must NOT trigger system behavior or escalate privileges.
3.  **No Ghostwriting**: Documentation changes must be traceable to a specific DID or Ledger Entry; silent edits are forbidden.
