# F2 Regime Partiality Remediation Design

## 1. Problem Restatement
F2 is regime instability caused by evaluating regime state when canonical inputs are partially updated, heterogeneous in freshness, or inconsistently bound across paths.

Precise definition:
- Regime instability occurs when identical nominal evaluation context yields materially different regime or policy outcomes because input-role completeness/freshness is not consistent.
- Instability is structural, not market-driven, when it is induced by input partiality rather than authentic market transitions.

Partial-canonical scenarios in scope:
- Equity updated, rates stale.
- Volatility updated, breadth stale.
- Cross-market asynchrony (`US` and `INDIA` at different canonical completeness states).

Observed IRR symptoms:
- Flip: Same day produced incompatible INDIA policy outcomes (`HALTED/UNKNOWN` vs `ACTIVE/BULLISH`) across paths.
- Degrade: US path failed closed to `UNKNOWN` despite partial ingestion success.
- Oscillation risk: Path-dependent schema/binding behavior creates alternating degraded vs active interpretations across sequential runs.

Evidence anchors:
- `docs/irr/regime_instability_report.md`
- `docs/irr/failure_log.md`
- `docs/irr/runtime/IRR-2026-02-09-001/us_decision_policy.json`
- `docs/irr/runtime/IRR-2026-02-09-001/india_decision_policy_via_core_engine.json`
- `docs/intelligence/decision_policy_INDIA.json`

## 2. Epistemic Risk Analysis
Why partial updates corrupt regime inference:
- Role incompleteness changes factor composition invisibly unless explicitly declared.
- Heterogeneous freshness causes mixed-time inference where some roles describe newer reality than others.
- Schema or binding divergence can silently reclassify market context as `UNKNOWN` or contradictory states.

Propagation risks:
- Narratives: Regime descriptors become unstable, producing overconfident language or missing-attribution outputs.
- Policy gating: Permission sets diverge across routes, creating contradictory suppression/grant behavior.
- Operator trust: Repeated mismatch between expected and observed regime state degrades confidence in governance surfaces.

Why best-effort inference is unsafe:
- Best-effort mode hides uncertainty by producing a seemingly decisive regime from incomplete evidence.
- Under freeze and bounded drift governance, hidden substitution violates honest stagnation and temporal clarity obligations.
- It can appear to reduce friction while actually increasing epistemic error and decision misinterpretation.

## 3. Canonical Partiality Taxonomy
Design declares canonical partiality as first-class state before regime evaluation.

### State Definitions
- `CANONICAL_COMPLETE`
  - All required regime roles present and freshness-qualified within policy bounds.
- `CANONICAL_PARTIAL`
  - One or more required roles missing or non-qualified; missing roles must be explicitly listed.
- `CANONICAL_MIXED`
  - Required roles present but freshness dispersion exceeds allowed skew; heterogeneous-time inputs detected.

### Detection & Declaration (Design-Only)
- Role inventory:
  - Each market defines required roles and role-to-source bindings.
- Freshness metadata:
  - Each role carries `last_canonical_timestamp` and freshness age.
- Partiality detector output:
  - `partiality_state`
  - `missing_roles`
  - `stale_roles`
  - `freshness_skew_days`
  - `declaration_reason`
- Declaration contract:
  - Regime evaluation must consume declared partiality state.
  - Dashboard and policy layers must surface declared partiality unchanged.

## 4. Allowed Regime Behavior Patterns (Design Options)

### Option A: Regime HOLD-ON-PARTIAL
Behavior:
- Freeze last stable regime when `CANONICAL_PARTIAL` or `CANONICAL_MIXED`.

Pros:
- Reduces oscillation under transient data partiality.
- Preserves continuity for operator interpretation.

Cons:
- Can mask stale regime context if hold duration grows.
- May imply confidence not warranted by current canonical coverage.

Failure modes:
- Regime appears active while supporting roles are stale.
- Long hold periods drift away from authentic market state.

Interaction with F1 drift bounds:
- Must inherit F1 caps; hold cannot override drift-limit breach handling.
- When F1 is exceeded, HOLD mode must display explicit freeze reason and required operator action.

### Option B: Regime DEGRADE-ON-PARTIAL
Behavior:
- Force regime to `UNKNOWN` or `UNSTABLE` whenever partiality detected.

Pros:
- Maximizes epistemic honesty and avoids hidden inference.
- Strongly aligns with honest stagnation obligation.

Cons:
- Can over-degrade during short-lived ingestion lag.
- May reduce operator utility when partiality is minor and well-understood.

Failure modes:
- Excessive `UNKNOWN` periods causing operational noise.
- Overly conservative suppression dominating normal observation.

Interaction with F1 drift bounds:
- Compatible with F1 by design; both enforce explicit pause semantics.
- Requires clear distinction between drift-driven degrade and partiality-driven degrade.

### Option C: Regime ROLE-WEIGHTED
Behavior:
- Evaluate regime only if critical roles are fresh; auxiliary roles may be stale within bounded tolerance.

Pros:
- Balances strictness and continuity.
- Preserves evaluation capability when non-critical lag exists.

Cons:
- Requires governance agreement on critical vs auxiliary role classification.
- Adds policy complexity and potential disputes about role criticality.

Failure modes:
- Misclassified auxiliary role silently degrades inference quality.
- Critical-role freshness threshold gaming if definitions are weak.

Interaction with F1 drift bounds:
- Must include hard stop when F1 drift breaches limit, regardless of role weighting.
- Role-weighted tolerances cannot bypass TE freeze or operator-mediated catch-up requirements.

### Option D: Regime MARKET-SCOPED
Behavior:
- Allow each market to hold its own partiality/regime state independently, with explicit cross-market disclosure.

Pros:
- Avoids forced coupling between `US` and `INDIA` when update cadences differ.
- Preserves market-local truth while exposing divergence.

Cons:
- Requires strong UI labeling to prevent cross-market contamination.
- Increases cognitive load for operators comparing markets.

Failure modes:
- Operators infer global regime from one market while another is partial/degraded.
- Cross-market policy consumers accidentally consume out-of-scope regime state.

Interaction with F1 drift bounds:
- Each market must enforce its own F1 bound first.
- Cross-market views must disclose drift + partiality for both markets before comparative interpretation.

## 5. Dashboard & Disclosure Requirements
Partiality must be surfaced as explicit state, not inferred from secondary artifacts.

Required operator-visible fields:
- `partiality_state`
- `missing_roles`
- `stale_roles`
- `freshness_skew_days`
- `regime_behavior_mode` (`HOLD`, `DEGRADE`, `ROLE_WEIGHTED`, `MARKET_SCOPED`)
- `required_operator_action`

Regime label rules under partiality:
- If `DEGRADE-ON-PARTIAL`: label must be `UNKNOWN` or `UNSTABLE`.
- If `HOLD-ON-PARTIAL`: label must include hold qualifier, for example `BULLISH (HELD_PARTIAL)`.
- If `ROLE-WEIGHTED`: label must include role qualification status.
- If `MARKET-SCOPED`: each market label must carry independent partiality annotation.

Required language bans:
- Do not display `stable` when `CANONICAL_PARTIAL` or `CANONICAL_MIXED`.
- Do not display `fully canonical` unless `CANONICAL_COMPLETE`.
- Do not display recommendation wording from partiality state alone.

## 6. Explicit Constraints
- No auto-repair and no silent backfilling.
- No regime inference from system clock.
- No cross-market contamination of role bindings or state labels.
- No Truth Epoch advancement.
- No execution or capital enablement.

## 7. Open Design Decisions (Operator Choices)
- Regime behavior pattern choice: `HOLD`, `DEGRADE`, `ROLE_WEIGHTED`, or hybrid policy.
- Critical vs auxiliary role classification by market.
- Freshness skew threshold that separates `CANONICAL_PARTIAL` from `CANONICAL_MIXED`.
- Whether cross-market summaries are allowed when one market is partial.
- Required operator action semantics for each partiality state.

## Non-Goals (Mandatory)
This design does not:
- implement regime logic,
- change factor computations,
- modify ingestion cadence,
- advance Truth Epoch,
- enable execution or capital,
- resolve `F3`-`F5` remediation.
