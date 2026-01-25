# What Counts as Progress

**Status**: Authoritative Epistemic Filter.
**Created**: 2026-01-24
**System State**: Epistemic Foundation Completion

This document defines the criteria by which all activity in the Trader Fund ecosystem is evaluated. It serves as the final filter to determine whether a change constitutes a constructive evolution or a destructive drift.

## 1. What Counts as Progress

In this system, progress is measured by the hardening of the epistemic foundation and the clarity of system behavior.

**Criteria for Legitimate Progress**:
*   **Improved Clarity**: A more precise understanding of why the system acted (or declined to act).
*   **Reduced Ambiguity**: The elimination of "it depends" in decision-making paths.
*   **Stronger Separation of Cognition**: Clearer boundaries between data ingestion, narrative synthesis, and execution logic.
*   **Better Observability**: Every system state and transition is perfectly auditable and explainable.
*   **Higher Quality Narratives**: Reducing signal-to-noise by producing fewer, but more resilient and verifiable, intelligence summaries.
*   **Increased Discipline**: Demonstrable patience and adherence to rules even when it "feels" suboptimal in the short term.
*   **Calm During Noise**: The system's ability to maintain its invariants during high-volatility or noisy market regimes.

**Progress is NOT**:
*   **NOT Speed**: Fast iteration at the cost of documented intent is a failure.
*   **NOT Feature Count**: More skills or modules are only useful if they increase governance clarity.
*   **NOT Performance Alone**: High backtest returns are secondary to the system's ability to explain *where* those returns originated and *why* they are expected to persist.

## 2. What Does NOT Count as Progress

False progress is any activity that increases system complexity while decreasing human control or understanding.

**Common Traps**:
*   **Intelligence without Governance**: Adding LLM or heuristic "smartness" that cannot be bounded by the Skill Authority Model.
*   **Automation without Clarity**: Automating steps that haven't been manually proven and documented as safe.
*   **Optimizing Metrics while Losing Explainability**: Improving a KPI if the underlying mechanism becomes a "black box."
*   **Survival-Optimized vs. Profit-Optimized**: Any gain that comes at the cost of survival (e.g., increasing leverage, ignoring regime context).
*   **Volume over Veracity**: Increasing the number of processed signals or narratives if it dilutes the auditability of the result.
*   **Short-Term Trust Erasure**: Gains achieved by "cutting a corner" in the documentation or ledger process.

## 3. Failures We Accept

Discipline has a cost. The following outcomes are not mistakes; they are the intentional price of our epistemic rigors.

**Acceptable Failure Modes**:
*   **Missed Trades**: We accept missing profitable opportunities if the narrative did not meet the validation threshold.
*   **Under-Reaction**: We accept slow reaction to news while waiting for regime confirmation.
*   **Extended Shadow Mode**: We accept staying in observation-only mode longer than expected to ensure link integrity.
*   **Rejection of "Obvious" Narratives**: We accept ignoring signals that lack sufficient lineage, even if they later prove correct.
*   **Iteration Friction**: We accept slow development when clarity or consensus has not been achieved.

## 4. Failures We Refuse

The following outcomes are categorical failures of the architecture and the team. They are non-negotiable red lines.

**Unacceptable Failure/Refusal Modes**:
*   **Acting sans Regime**: Acting without explicit confirmation of the current market regime.
*   **Unvalidated Narrative Trades**: Allowing a narrative-driven action without the required validation side-steps.
*   **Undocumented Changes**: Any code or structural change introduced without a DID or Ledger update.
*   **Governance Bypass**: Violating a constraint "just once" for expediency or emergency.
*   **Silent Assumption Reintroduction**: Allowing an invalidated assumption to creep back in without explicit ledger review.
*   **Loss of Auditability**: Any period of system activity where the "why" cannot be recovered from logs.
*   **Post-Hoc Rationalization**: Inventing an explanation for system behavior that was not captured at the time of execution.

## 5. Relationship to Epistemic Framework

This document is the final layer of the epistemic foundation.

*   **Lens for Evaluation**: It serves as a mandatory checklist for all future Work Breakdown Structures (WBS) and Implementation Plans.
*   **Overriding Authority**: This document overrides subjective or external notions of "doing more" or "moving faster."
*   **Complementary to Ledgers**: It informs the Decision Ledger (`decisions.md`) by defining the standard by which "good" decisions are made.
*   **No Authorization**: This document does NOT authorize code changes; it only provides the criteria for their rejection or acceptance.

## 6. Final Safety Check

When evaluating a proposed change, ask:
1.  **Does this make the system more or less explainable?**
2.  **Are we improving a metric at the cost of an invariant?**
3.  **Is this work aligned with 10-year survival or 10-day performance?**
4.  **Would we be comfortable explaining this change during a post-mortem of a total loss?**

In all cases, we prefer **RESTRICTION** over **OPTIMISM** and **CLARITY** over **CLEVERNESS**.
