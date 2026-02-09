# F4 UI Epistemic Violation Remediation Design

## 1. Problem Restatement
F4 is the failure mode where UI presentation implies certainty, completeness, or directional confidence that is not warranted by TE-bound evidence.

Precise failure definition:
- UI epistemic violation occurs when display semantics (labels, colors, layout, badges, or omissions) overstate what the system can honestly claim.
- Violations include inconsistent epoch disclosure, missing provenance, and partial data presented as complete.

IRR and Shadow manifestation:
- Directly logged epoch inconsistency across UI-relevant truth sources:
  - `docs/irr/ui_violation_audit.md` (`UIE-001`)
  - `docs/epistemic/truth_epoch.json`
  - `docs/intelligence/execution_gate_status.json`
  - `docs/intelligence/temporal/temporal_state_US.json`
- Backend transport checks passed while epistemic inconsistency remained unresolved:
  - `docs/irr/runtime/IRR-2026-02-09-001/13_ui_backend_verify.log`
  - `docs/irr/ui_violation_audit.md`

Why epistemically dangerous:
- Operators trust visual consistency as truth consistency.
- A "healthy" UI can mask semantic contradiction and encourage mistaken decisions.
- Future Truth Advancement gating can be misjudged if display truth is non-singular.

## 2. Failure Taxonomy
| Subtype | Description | Observed Artifacts / Logs |
|---|---|---|
| `F4-T1 Epoch Disclosure Divergence` | Different surfaces can present incompatible epoch identifiers | `docs/irr/ui_violation_audit.md`, `docs/epistemic/truth_epoch.json`, `docs/intelligence/execution_gate_status.json`, `docs/intelligence/temporal/temporal_state_US.json` |
| `F4-T2 Transport vs Semantics Split` | API reachability checks pass while epistemic coherence fails | `docs/irr/runtime/IRR-2026-02-09-001/13_ui_backend_verify.log`, `docs/irr/ui_violation_audit.md` |
| `F4-T3 Partiality Visibility Gap` | Partial canonical state can be consumed without mandatory, centralized UI degradation semantics | `docs/governance/irr_failure_remediation_map.md`, `docs/irr/failure_log.md` (`UIE-001`, `GLK-004`) |
| `F4-T4 Provenance Fragmentation` | Operators must infer source-of-truth from multiple files and endpoints | `docs/irr/ui_violation_audit.md`, `docs/irr/failure_log.md` (`GLK-001`) |

## 3. Risk Propagation Analysis
Operator cognition:
- Mixed epoch labels create cognitive branch confusion ("Which truth is active?").
- Ambiguous partiality visuals create false confidence in state completeness.

Narratives:
- UI inconsistency can frame narrative text as more current than it is.
- Narrative honesty can be undermined by conflicting adjacent UI timestamps.

Trust:
- Repeated semantic contradiction with stable transport creates distrust in dashboards.
- Operators may bypass governance UI and rely on ad hoc file inspection.

Future Truth Advancement:
- Advancement decisions can be made from incoherent displays instead of canonical gates.
- Partial fixes are insufficient because isolated widget fixes do not resolve cross-widget semantic mismatch.

Why partial fixes fail:
- Fixing a single label does not enforce source singularity.
- Adding warning text without visual semantics contract still allows misleading emphasis.
- Provenance fields alone fail if not validated against a global truth contract.

## 4. Allowed Remediation Patterns (Design Options)
### Pattern A: UI Semantic Freeze Under Uncertainty
Description:
- When epoch inconsistency or degraded canonical state is detected, directional/confirmatory UI semantics freeze to explicit unknown/degraded representations.

Pros:
- Prevents accidental confidence signaling.
- Aligns strongly with honest stagnation obligations.

Cons:
- Lower immediacy for experienced operators.
- Requires robust uncertainty detectors.

Failure modes:
- Over-freeze from transient mismatches.
- Freeze state without clear reason messaging.

Interaction with F1 and F2:
- F1 drift breaches force freeze overlays until bounded conditions are restored.
- F2 degraded regime must force unknown regime visual semantics.

### Pattern B: Global Epistemic Banner and Source Binding
Description:
- Introduce a single mandatory top-level epistemic banner that declares TE, CTT, canonical state, and provenance source IDs used by all widgets.

Pros:
- Establishes one authoritative display context.
- Simplifies operator verification.

Cons:
- Needs strict backend consistency contract.
- Banner overuse can reduce attention if overly verbose.

Failure modes:
- Banner stale while widgets refresh independently.
- Source map drift if contracts are weak.

Interaction with F1 and F2:
- Banner must include F1 drift status and F2 canonical partiality state per market.
- Banner cannot claim synchronized truth while any market is degraded or drift-breached.

### Pattern C: Widget-Level Truth Contracts
Description:
- Each widget declares required fields, completeness predicates, and forbidden render states; missing predicates force degraded rendering.

Pros:
- Localizes semantic correctness checks.
- Prevents partial-as-complete presentation.

Cons:
- Contract maintenance overhead.
- Requires version discipline across frontend and backend.

Failure modes:
- Contract bypass paths in legacy components.
- Conflicting contracts across widgets.

Interaction with F1 and F2:
- F1/F2 become mandatory contract inputs for all derived widgets.
- Widgets must fail closed when F1/F2 states are unresolved.

### Pattern D: Visual Degradation Contract
Description:
- Standardize degraded visual semantics so uncertainty is more visible than normal state, never muted.

Pros:
- Consistent interpretation across surfaces.
- Reduces hidden partiality risk.

Cons:
- Can feel alarm-heavy in prolonged degraded conditions.
- Requires careful tuning to avoid alert fatigue.

Failure modes:
- Inconsistent color mapping across components.
- Degraded badges rendered but ignored due weak hierarchy.

Interaction with F1 and F2:
- F1 and F2 degraded states must share deterministic severity precedence.
- Per-market degradation must remain isolated (no global downgrade without explicit rule).

## 5. Dashboard and Disclosure Requirements
Must be shown:
- Per-market `TE`, `CTT`, `RDT`, drift status, and canonical state.
- Source artifact path (or source ID) and `computed_at` for every derived widget.
- Explicit missing/stale role disclosure when `canonical_state != CANONICAL_COMPLETE`.
- Explicit statement of what the UI cannot currently know.

Must be suppressed:
- Directional arrows, confidence-like wording, or success colors under degraded/partial state.
- Any display that merges market states without explicit per-market labeling.
- Any "all clear" summary when blocker states exist.

Language bans (explicit):
- `latest` (without scope), `current` (without TE qualifier), `confirmed`, `stable`, `fully canonical` (unless complete), `greenlight`, `ready to act`.

Visual semantics constraints:
- Degraded states must have higher salience than nominal states.
- Unknown/degraded states must never render in green.
- Critical epistemic warnings must be persistent and non-dismissible.
- Layout must not place epistemically uncertain widgets adjacent to action-like metaphors.

## 6. Operator Control and Overrides
Operator may choose:
- Display verbosity profile (`compact`, `audit`, `forensic`).
- Whether provenance is inline or expandable by default.
- Market focus pinning (US or INDIA) for isolated review.

System must never infer:
- Epoch alignment from clock time.
- Completeness from non-required fields.
- Cross-market equivalence from one market's canonical completeness.

Required confirmations and holds:
- Explicit acknowledgment before hiding provenance details in compact mode.
- Mandatory hold banner if epoch sources diverge.
- Confirmation that any temporary UI override does not alter governance state.

## 7. Explicit Constraints
- No aesthetic simplification that reduces epistemic honesty.
- No convenience shortcut that hides degraded or unknown states.
- No silent substitution of unavailable provenance fields.
- No implicit normalization of partial data to complete state.
- No TE advancement side effects.
- No execution or capital affordances.

## 8. Open Design Decisions
- Canonical "single source" authority for UI epoch display.
- Severity precedence when F1 and F2 are both active but with different markets impacted.
- Whether compact mode is allowed when any blocker is active.
- Required provenance granularity (widget-level vs sentence-level vs card-level).
- Whether unresolved epoch divergence should hard-block the full dashboard.

## 9. Mandatory Non-Goals
- This design does not implement frontend or backend code changes.
- This design does not redesign visual style for aesthetics.
- This design does not alter ingestion, factor, or policy logic.
- This design does not advance Truth Epoch.
- This design does not enable execution or capital flows.
- This design does not resolve F1 or F2 controls directly.

