# Skill Catalog

**Status**: Authoritative Definition of System Capabilities.

This document defines the *allowed* skills within the Trader Fund ecosystem. A skill is a specialized cognitive function with defined scope, authority, and constraints.

## Global Constraints
1.  **No Direct Execution**: Skills defined here must NOT execute live trades or move real capital.
2.  **No Code Mutation**: Skills must NOT modify source code logic directly without human approval (represented by "Advisory" authority).
3.  **No Intent Mutation**: Skills must NOT alter `project_intent.md` content, only review against it.

### Skill Authority & Precedence

All skills must operate within a strict hierarchy of authority.

1.  **Human Decision** (Supreme Authority)
2.  **Append-Only Ledger** (Historical Truth)
3.  **Structural Integrity** (Format & Consistency)
4.  **Advisory** (Recommendations & Flags)

**Rules:**
*   **No Override**: No skill may override a document or decision from a higher authority level.
*   **No Escalation**: No skill may escalate its own authority level; it is fixed by this catalog.
*   **Conflict Resolution**: All unresolvable conflicts between skills must be escalated to **Human Judgment**.

---

## 1. Intent Consistency Reviewer
- **Documentation**: [intent_consistency_reviewer.md](file:///c:/GIT/TraderFund/docs/epistemic/skills/intent_consistency_reviewer.md)
*   **Purpose**: To ensure that all proposed changes align with the Core Project Intent and Trading Philosophy.
*   **Responsibilities**:
    *   Review proposed code or documentation changes.
    *   Flag violations of "Glass-Box" or "Context Before Signal" principles.
    *   Verify that new features do not violate Non-Goals (e.g., HFT, Black-Box).
*   **Read Scope**: `docs/epistemic/project_intent.md`, Pull Requests, Change Diffs.
*   **Write Scope**: Implementation Review Reports (Commentary).
*   **Authority Level**: **Advisory** (Blocker for merge if flagged).
*   **Non-Responsibilities**: Code style checking, performance profiling.

## 2. Cognitive Order Validator
- **Documentation**: [cognitive_order_validator.md](file:///c:/GIT/TraderFund/docs/epistemic/skills/cognitive_order_validator.md)
*   **Purpose**: To enforce the strict cognitive hierarchy rooted in `architectural_invariants.md`.
*   **Responsibilities**:
    *   Verify that no strategy logic attempts to bypass Regime or Narrative context.
    *   Identify "leakage" of execution concerns into signal generation logic.
    *   Ensure Event Time Integrity is respected in new modules.
*   **Read Scope**: `docs/epistemic/architectural_invariants.md`, Source Code.
*   **Write Scope**: Validation Reports.
*   **Authority Level**: **Advisory** (Must be resolved before deployment).
*   **Non-Responsibilities**: Business logic verification, pnl optimization.

## 3. Decision Ledger Curator
- **Documentation**: [decision_ledger_curator.md](file:///c:/GIT/TraderFund/docs/epistemic/skills/decision_ledger_curator.md)
*   **Purpose**: To maintain the integrity and chronological order of the Decision Ledger.
*   **Responsibilities**:
    *   Format and append new Authoritative Decisions to `decisions.md`.
    *   Ensure new decisions explicitly reference superseded ones if applicable.
    *   Reject decisions that implicitly weaken prior invariants.
*   **Read Scope**: `docs/epistemic/ledger/decisions.md`.
*   **Write Scope**: `docs/epistemic/ledger/decisions.md` (Append-Only).
*   **Authority Level**: **Structural**.
*   **Non-Responsibilities**: Making said decisions (Human responsibility).
*   **Hardening**:
    *   **Format Only**: The Curator manages format and integrity ONLY.
    *   **Zero Content Authority**: It has ZERO authority to decide the content of a decision.
    *   **Human Origin**: All decisions must originate from humans.

## 4. Evolution Recorder
- **Documentation**: [evolution_recorder.md](file:///c:/GIT/TraderFund/docs/epistemic/skills/evolution_recorder.md)
*   **Purpose**: To capture the "What" and "Why" of system lifecycle changes for historical continuity.
*   **Responsibilities**:
    *   Append significant lifecycle events to `evolution_log.md`.
    *   Categorize changes by scope (Code, Data, Ops, Cognition).
*   **Read Scope**: System Logs, Release Notes.
*   **Write Scope**: `docs/epistemic/ledger/evolution_log.md` (Append-Only).
*   **Authority Level**: **Append-Only** (Record of truth).
*   **Non-Responsibilities**: Judging the quality of the evolution.
*   **Hardening**:
    *   **Descriptive Only**: Evolution logs are descriptive, not prescriptive.
    *   **No Justification**: They cannot be used to justify or trigger system changes.
    *   **Subservience**: They do not supersede Decisions or Invariants.

## 5. Assumption Tracker
- **Documentation**: [assumption_tracker.md](file:///c:/GIT/TraderFund/docs/epistemic/skills/assumption_tracker.md)
*   **Purpose**: To prevent regression by explicitly tracking invalidated assumptions and their permanent outcomes.
*   **Responsibilities**:
    *   Record invalidated assumptions in `assumption_changes.md`.
    *   Define "Permanent Outcome" constraints derived from learned failures.
*   **Read Scope**: Post-Mortems, Debug Logs.
*   **Write Scope**: `docs/epistemic/ledger/assumption_changes.md` (Append-Only).
*   **Authority Level**: **Append-Only** (Critical Memory).
*   **Non-Responsibilities**: Predicting future assumptions.
*   **Hardening**:
    *   **Permanent Death**: Retired assumptions are permanently invalid.
    *   **No Resurrection**: Reintroducing a retired assumption requires a new Decision Ledger entry.
    *   **Silence Forbidden**: Silent resurrection of failed assumptions is explicitly forbidden.

## 6. Runbook Generator
- **Documentation**: [runbook_generator.md](file:///c:/GIT/TraderFund/docs/epistemic/skills/runbook_generator.md)
*   **Purpose**: To convert implicit operational knowledge into explicit executable runbooks.
*   **Responsibilities**:
    *   Draft operational procedures based on successful execution logs.
    *   Update runbooks when tools or key paths change.
*   **Read Scope**: Command History, `active_constraints.md`.
*   **Write Scope**: `docs/runbooks/*.md`.
*   **Authority Level**: **Advisory** (Drafting for human approval).
*   **Non-Responsibilities**: Executing the runbooks automatically.
*   **Hardening**:
    *   **Draft Status**: Runbooks are drafts until explicitly human-approved.
    *   **No Auto-Execution**: No runbook may be auto-executed by this skill.
    *   **Constraint Respect**: Runbooks cannot override `active_constraints.md`.

## 7. Change Summarizer
- **Documentation**: [change_summarizer.md](file:///c:/GIT/TraderFund/docs/epistemic/skills/change_summarizer.md)
*   **Purpose**: To provide high-level, intent-focused summaries of complex changes for human consumption.
*   **Responsibilities**:
    *   Synthesize diffs into natural language narratives.
    *   Highlight impact on "Active Constraints".
*   **Read Scope**: `current_phase.md`, `active_constraints.md`, File Diffs.
*   **Write Scope**: Pull Request Descriptions, Milestone Summaries.
*   **Authority Level**: **Informational**.
*   **Non-Responsibilities**: Approval or rejection.

## 8. Drift Detector
- **Documentation**: [drift_detector.md](file:///c:/GIT/TraderFund/docs/epistemic/skills/drift_detector.md)
*   **Purpose**: To detect unauthorized or unintentional drift in system configuration, structure, and epistemic integrity.
*   **Responsibilities**:
    *   Compare current `.env` and directory structure against baselines.
    *   Report syntactic drift (missing keys, new files).
    *   Validate epistemic contracts and layer invariants (13 rules).
    *   Detect permission bypass (PD-1), layer boundary violations (BD-1), latent layer activation (LD-1).
    *   Flag CRITICAL violations that block deployment.
*   **Read Scope**: `.env`, Project Root, `docs/epistemic/`, `src/`.
*   **Write Scope**: Logs / Drift Reports (JSON).
*   **Authority Level**: **Structural** (Gatekeeper for epistemic integrity).
*   **Non-Responsibilities**: Fixing the drift automatically. Making PASS/FAIL judgments on strategy quality.
*   **Scripts**: `drift_detector.py` (config/structure), `epistemic_validator.py` (13 epistemic rules).

## 9. Pattern Matcher
- **Documentation**: [pattern_matcher.md](file:///c:/GIT/TraderFund/docs/epistemic/skills/pattern_matcher.md)
*   **Purpose**: To provide historical context by identifying price/volume patterns similar to the current regime.
*   **Responsibilities**:
    *   Search historical data for correlated segments.
    *   Return "Similar Epochs" to aid human context.
*   **Read Scope**: `data/processed/candles`.
*   **Write Scope**: Analysis Reports.
*   **Authority Level**: **Informational** (Context only).
*   **Non-Responsibilities**: Predicting future price action.

## 10. Constraint Validator
- **Documentation**: [constraint_validator.md](file:///c:/GIT/TraderFund/docs/epistemic/skills/constraint_validator.md)
*   **Purpose**: To mechanically enforce the epistemic and logical constraints defined in the system.
*   **Responsibilities**:
    *   Validate artifacts (Narratives, Decisions) against schema and logic rules (e.g. No Future Timestamps).
    *   Ensure "Brain" (Logic) output matches "Body" (Schema) expectations.
*   **Read Scope**: JSON Artifacts (`data/narratives`, `data/decisions`).
*   **Write Scope**: Validation Reports (Pass/Fail).
*   **Authority Level**: **Structural** (Gatekeeper).
*   **Non-Responsibilities**: judging the *quality* of the trade, only the *validity* of the artifact.

## 11. Audit Log Viewer
- **Documentation**: [audit_log_viewer.md](file:///c:/GIT/TraderFund/docs/epistemic/skills/audit_log_viewer.md)
*   **Purpose**: To provide a human-readable view of the machine-parseable JSON audit logs (Glass Box Verification).
*   **Responsibilities**:
    *   Parse and filter JSON logs from `logs/`.
    *   Display structured history by User, Time, or Skill.
*   **Read Scope**: `logs/*.json`.
*   **Write Scope**: Stdout (ReadOnly).
*   **Authority Level**: **Informational**.
*   **Non-Responsibilities**: Modifying logs or alerting (Passive view only).

## 12. Monitor Trigger
- **Documentation**: [monitor_trigger.md](file:///c:/GIT/TraderFund/docs/epistemic/skills/monitor_trigger.md)
*   **Purpose**: To continuously observe the system state and suggest interventions (Passive).
*   **Responsibilities**:
    *   Scan Inbox for new files.
    *   Scan Gap between Narratives and Decisions.
    *   Log `[SUGGESTION]` entries.
*   **Read Scope**: `data/events`, `data/narratives`.
*   **Write Scope**: Logs only.
*   **Authority Level**: **Advisory**.
*   **Non-Responsibilities**: Executing any actions.

## 13. Design/Build Execution Harness
- **Documentation**: [design_build_harness.md](file:///c:/GIT/TraderFund/docs/epistemic/skills/design_build_harness.md)
- **Contract**: [execution_contract.md](file:///c:/GIT/TraderFund/docs/epistemic/skills/execution_contract.md)
*   **Purpose**: To deterministically execute the Design/Build Task Graph while obeying epistemic, policy, and validator constraints.
*   **Responsibilities**:
    *   Ingest `task_graph.md` and resolve dependencies.
    *   Verify DWBS plane gates and task preconditions.
    *   Invoke meta-engineering skills in correct order.
    *   Coordinate ledger updates and post-execution verification.
*   **Read Scope**: `docs/architecture/DWBS.md`, `docs/epistemic/roadmap/task_graph.md`, `docs/epistemic/ledger/`.
*   **Write Scope**: `docs/epistemic/roadmap/task_graph.md`, `docs/epistemic/ledger/evolution_log.md`.
*   **Authority Level**: **Structural** (Orchestration).
*   **Non-Responsibilities**: Performing market execution, trading, or belief inference.

## Explicit Skill Non-Goals

To prevent agentic drift, the following are explicitly OUT OF SCOPE for all skills:

1.  **No Negotiation**: Skills do not negotiate with each other; they follow the hierarchy.
2.  **No Auto-Resolution**: Skills do not automatically resolve fundamental conflicts; they escalate to humans.
3.  **No Mutation**: Skills do not mutate code, capital, or intent.
4.  **No Self-Learning**: Skills do not learn or self-modify. They are static definitions.
