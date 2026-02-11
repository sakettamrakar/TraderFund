# F5 Suppression and Honest Stagnation Remediation Design

## 1. Problem Restatement
F5 is the failure mode where suppression exists but is not sufficiently explicit, attributable, or narratively legible as honest stagnation.

Precise failure definition:
- Suppression gap: permissions are blocked or absent without a clear, operator-legible blocker hierarchy.
- Honest stagnation gap: inactivity is visible but reason causality and required operator action are ambiguous or fragmented.

IRR and Shadow manifestation:
- Suppression evidence is split across manual, canonical, and schema-leakage paths:
  - `docs/irr/suppression_events.md`
  - `docs/irr/runtime/IRR-2026-02-09-001/us_decision_policy_manual.json`
  - `docs/intelligence/decision_policy_INDIA.json`
  - `docs/irr/runtime/IRR-2026-02-09-001/india_decision_policy_via_core_engine.json`
- Tick-context schema mismatch forced full suppression through `market=UNKNOWN`, blurring whether blocker is policy intent or pipeline fault:
  - `docs/irr/runtime/IRR-2026-02-09-001/us_decision_policy.json`
  - `docs/irr/runtime/IRR-2026-02-09-001/india_decision_policy_via_core_engine.json`
  - `docs/irr/failure_log.md` (`GLK-004`)
- Shadow run carried drifted environment without closure:
  - `docs/irr/shadow_reality_run_log.md` (`SH-003`)

Why epistemically dangerous:
- Operators cannot distinguish safety suppression from data/schema breakage suppression.
- "Nothing happening" can be misread as strategic patience rather than enforced governance block.
- Unclear suppression provenance degrades trust and weakens Truth Advancement readiness decisions.

## 2. Failure Taxonomy
| Subtype | Description | Observed Artifacts / Logs |
|---|---|---|
| `F5-T1 Silent Suppression` | Blocked action space is present but not surfaced with loud, unified blocker semantics | `docs/irr/suppression_events.md`, `docs/irr/daily_reality_observation_log.md` |
| `F5-T2 Ambiguous Blocker Origin` | Suppression caused by schema/context failure can appear identical to intentional policy gating | `docs/irr/runtime/IRR-2026-02-09-001/us_decision_policy.json`, `docs/irr/runtime/IRR-2026-02-09-001/india_decision_policy_via_core_engine.json`, `docs/irr/failure_log.md` (`GLK-004`) |
| `F5-T3 Suppression Fragmentation` | Operator must reconstruct suppression state by joining multiple artifacts manually | `docs/irr/suppression_events.md`, `docs/governance/irr_failure_remediation_map.md` |
| `F5-T4 Inactivity Interpretation Drift` | Inactive system state lacks consistent explanation linking blockers to required action | `docs/irr/daily_reality_observation_log.md`, `docs/irr/final_readiness_summary.md` |
| `F5-T5 Temporal Carry-Over Stagnation` | Stagnation persists across Shadow with no explicit closure path in suppression surface | `docs/irr/shadow_reality_run_log.md` (`SH-003`) |

## 3. Risk Propagation Analysis
Operator cognition:
- Ambiguous suppression source creates false choice architecture ("wait vs repair").
- Fragmented blocker evidence increases cognitive load and decision latency.

Narratives:
- Narrative layer may not explain inactivity with blocker causality.
- Inactivity framing can drift toward optimism if blocker detail is absent.

Trust:
- Suppression without transparent provenance appears arbitrary.
- Repeated opaque inactivity reduces confidence in governance integrity.

Future Truth Advancement:
- Advancement can be attempted before blocker classes are actually cleared.
- Partial fixes are insufficient because surface-level messaging without reason codification cannot guarantee attribution integrity.

Why partial fixes fail:
- Adding a single warning banner does not establish blocker precedence.
- Logging alone does not help operators if not surfaced coherently.
- Suppression transparency must include timeline, root cause class, and required action.

## 4. Allowed Remediation Patterns (Design Options)
### Pattern A: Loud Suppression State Machine
Description:
- Define explicit suppression states (`OBSERVE_ONLY_ENFORCED`, `HALTED_SCHEMA`, `HALTED_TEMPORAL`, `HALTED_PARTIALITY`) with deterministic render rules.

Pros:
- Converts generic inactivity into interpretable governance states.
- Enables consistent escalation semantics.

Cons:
- Requires formal state model governance.
- Potential state proliferation if uncontrolled.

Failure modes:
- Misclassified state can mislead operator response.
- Legacy paths bypass state machine.

Interaction with F1 and F2:
- F1 and F2 statuses become first-class suppression states.
- No suppression state can imply TE advancement or execution release.

### Pattern B: Enumerated Blocker Reason Stack
Description:
- Attach ordered blocker codes (`primary`, `secondary`) with source artifact references and operator actions.

Pros:
- Makes root cause attribution explicit and auditable.
- Distinguishes policy-intent suppression from structural failure.

Cons:
- Requires reason-code taxonomy governance.
- Can overwhelm UI if not compactly rendered.

Failure modes:
- Reason-code drift across components.
- Conflicting precedence across markets.

Interaction with F1 and F2:
- F1/F2 blockers must appear with highest precedence when active.
- Market-specific stacks must remain isolated.

### Pattern C: Explicit Stagnation Narrative Contract
Description:
- Mandatory stagnation message template declares: what is blocked, why, since when, and what operator action is required.

Pros:
- Prevents motivational or optimistic inactivity framing.
- Improves operator actionability without enabling execution.

Cons:
- Template rigidity can reduce readability.
- Needs strict upkeep with blocker schema.

Failure modes:
- Template fields missing from source artifacts.
- Stagnation message stale relative to blocker updates.

Interaction with F1 and F2:
- Must explicitly state F1 drift hold and F2 degraded-regime suppression when present.
- Must never suggest bypassing temporal or partiality gates.

### Pattern D: Suppression Timeline and Change Ledger
Description:
- Persist suppression transitions with timestamps, reason deltas, and market scope; expose in dashboard timeline.

Pros:
- Provides traceability and audit-grade chronology.
- Helps distinguish chronic vs transient suppression.

Cons:
- Additional storage and retention policy complexity.
- Timeline noise if state churn is high.

Failure modes:
- Missing transitions from legacy paths.
- Timeline interpreted as performance metric instead of governance metric.

Interaction with F1 and F2:
- F1/F2 transitions must be explicit timeline events.
- Timeline must not infer causality beyond declared reason stack.

## 5. Dashboard and Disclosure Requirements
Must be shown:
- Current suppression state and reason stack (with precedence).
- Blocking reason classes: temporal (`F1`), canonical partiality (`F2`), schema/governance, narrative source failure.
- "Since" timestamp and last transition event.
- Required operator action and confirmation status.

Must be suppressed:
- Ambiguous "system waiting" or "stand by" phrasing without reason codes.
- Optimistic inactivity framing (`patience`, `setups forming`, `ready soon`).
- Any implied capital readiness while suppression remains active.

Language bans (explicit):
- `patient`, `opportunity building`, `ready when market opens`, `soon actionable`, `keep waiting`, `confidence intact`, `just noise`.

Visual semantics constraints:
- Suppression state must be high salience and persistent.
- Suppression source class must be visible without extra clicks.
- Different suppression classes must be visually distinguishable.
- No green status rendering for any active suppression.

## 6. Operator Control and Overrides
Operator may choose:
- Suppression detail level (`summary` vs `full reason stack`).
- Timeline range and market scope view.
- Acknowledgment workflow for blocker review.

System must never infer:
- That inactivity implies strategic confidence.
- That suppression is intentional policy behavior when origin is schema failure.
- That one market's clearance implies other market clearance.

Required confirmations and holds:
- Explicit acknowledgment required before collapsing suppression details.
- Hold remains until blocker reason stack is cleared by declared conditions.
- Confirmation that any acknowledgment does not unlock execution or capital.

## 7. Explicit Constraints
- No silent suppression state transitions.
- No suppression reason without source artifact reference.
- No motivational or reassuring language during active suppression.
- No cross-market suppression coupling unless explicitly declared.
- No automatic TE advancement or evaluation trigger.
- No execution/capital enablement.

## 8. Open Design Decisions
- Canonical suppression reason-code taxonomy and precedence model.
- Maximum acceptable reason-stack depth for operator legibility.
- Default retention window for suppression timeline.
- Whether unresolved schema-failure suppression should hard-block all narrative surfaces.
- Escalation policy for prolonged unresolved suppression.

## 9. Mandatory Non-Goals
- This design does not implement suppression logic changes.
- This design does not alter factor, ingestion, or strategy computations.
- This design does not relax governance holds.
- This design does not advance Truth Epoch.
- This design does not enable execution or capital flows.
- This design does not resolve F1 or F2 directly.

