# F3 Narrative Leakage Remediation Design

## 1. Problem Restatement
F3 is the failure mode where narrative surfaces imply actionability, causal certainty, or optimism beyond what TE-bound evidence supports.

Precise failure definition:
- Narrative leakage occurs when language exceeds epistemic permission under frozen truth (`TE-2026-01-30`), degraded regime state, or incomplete narrative inputs.
- Leakage includes direct action verbs, implied directional conviction, and unjustified causal closure.

IRR and Shadow manifestation:
- Live narrative path failed closed at source with `404`, producing zero narratives and no fallback governance narrative:
  - `docs/irr/runtime/IRR-2026-02-09-001/12_real_market_stories.log`
  - `docs/irr/narrative_failure_matrix.md`
- Shadow replay emitted declarative action tokens (`BUY`) while US regime context remained unknown:
  - `docs/irr/runtime/SHADOW-2026-02-09-001/US/decision_trace_log.parquet`
  - `docs/irr/shadow_reality_run_log.md` (`SH-002`)

Why epistemically dangerous:
- Operators can infer non-existent certainty from language even when policy is blocked.
- Missing narrative fallback creates an information vacuum that encourages unsafe interpretation from adjacent widgets.
- Leaked action language can reintroduce execution-like cognition in a no-execution system.

## 2. Failure Taxonomy
| Subtype | Description | Observed Artifacts / Logs |
|---|---|---|
| `F3-T1 Action Lexeme Leakage` | Action-implying tokens appear under uncertainty (`BUY`, `entry`, `conviction`) | `docs/irr/runtime/SHADOW-2026-02-09-001/US/decision_trace_log.parquet`, `docs/irr/shadow_reality_run_log.md` |
| `F3-T2 Narrative Availability Collapse` | No narrative output and no deterministic fallback when real source fails | `docs/irr/runtime/IRR-2026-02-09-001/12_real_market_stories.log`, `docs/irr/narrative_failure_matrix.md` |
| `F3-T3 Causal Over-Closure Risk` | Deterministic explanatory language can overstate evidence completeness when upstream is partial | `docs/governance/irr_failure_remediation_map.md`, `docs/irr/failure_log.md` (`GLK-004`, `NV-001`) |
| `F3-T4 Regime-Adjacent Optimism Risk` | Narrative tone can remain permissive while regime/policy context degrades by path | `docs/irr/suppression_events.md`, `docs/intelligence/decision_policy_US.json`, `docs/irr/runtime/IRR-2026-02-09-001/us_decision_policy.json` |

## 3. Risk Propagation Analysis
Operator cognition:
- Action words become de facto recommendations even if formal execution is disabled.
- Missing narratives shift operator attention to non-narrative cues, increasing inference errors.

Narratives:
- Without strict gating, narrative output can contradict degraded regime state.
- Without fallback narrative, narrative layer provides no explicit uncertainty context.

Trust:
- Contradictory language across Shadow and IRR paths reduces confidence in governance discipline.
- Trust erosion is amplified when narrative absence is silent rather than explained.

Future Truth Advancement:
- Truth Advancement decisions can be biased by narrative over-resolution or narrative silence.
- Partial fixes are insufficient because banning a few words does not prevent causal over-closure.

Why partial fixes fail:
- Lexical filters alone miss structural leakage (implicit optimism).
- Endpoint hardening alone does not enforce regime or drift gating.
- Fallback text alone can still leak recommendation semantics without source contracts.

## 4. Allowed Remediation Patterns (Design Options)
### Pattern A: Narrative Hard-Suppression Under Epistemic Unsafety
Description:
- Force narrative mode to `SUPPRESSED` when any blocking condition is true (`F1 breach`, `F2 degraded regime`, missing narrative source, unresolved epoch divergence).

Pros:
- Strongest prevention of action-language leakage.
- Clear alignment with `INV-HONEST-STAGNATION`.

Cons:
- Low informational richness during prolonged degraded periods.
- Operators may perceive reduced explainability.

Failure modes:
- Over-suppression during minor transient issues.
- Operators over-rely on non-narrative widgets.

Interaction with F1 and F2:
- Directly compatible with F1 drift holds and F2 degrade-on-partial.
- Must expose which blocker (`F1` vs `F2`) triggered suppression.

### Pattern B: Regime and Temporal Gated Narrative Silencing
Description:
- Narrative generation allowed only when declared `TE` scope, temporal status, and `canonical_state` satisfy a strict gate.

Pros:
- Prevents narratives from outrunning truth-time or partial canonical state.
- Explicitly binds narrative to declared epistemic context.

Cons:
- Requires a robust gate contract and state synchronization.
- Adds complexity in cross-surface consistency checks.

Failure modes:
- Gate misconfiguration can silently block all markets.
- Incomplete gate observability can hide root cause.

Interaction with F1 and F2:
- F1 status contributes gate input (`DRIFT_LIMIT_EXCEEDED`, `EVALUATION_PENDING`).
- F2 degraded regime enforces narrative silence or evidence-only fallback.

### Pattern C: Evidence-Only Narrative Mode
Description:
- Restrict output to source-bound statements with explicit field lineage; no interpreted causal language.

Pros:
- Preserves informational utility without recommendation semantics.
- Auditable sentence-to-source mapping.

Cons:
- Lower readability for non-technical operators.
- Can feel repetitive or sparse.

Failure modes:
- Template drift reintroduces interpretive phrases.
- Source map omissions create hidden hallucination risk.

Interaction with F1 and F2:
- Under F1/F2 stress, evidence-only remains valid if it includes degraded state disclosure.
- Must never reframe degraded state as directional bias.

### Pattern D: Narrative Diffing Against Last Truth Epoch
Description:
- Show only what changed versus last emitted TE-bound narrative and explicitly mark unknown/unavailable deltas.

Pros:
- Reduces over-resolution by anchoring on explicit deltas.
- Supports operator auditability over time.

Cons:
- Requires reliable last-epoch narrative baseline.
- Diff noise possible during frequent minor updates.

Failure modes:
- False delta when schemas diverge.
- Missing baseline can produce misleading "no change" output.

Interaction with F1 and F2:
- F1 drift can force "diff unavailable due temporal gate" state.
- F2 degraded regime must force degraded diff semantics, not directional diffing.

## 5. Dashboard and Disclosure Requirements
Must be shown:
- Narrative mode (`SUPPRESSED`, `EVIDENCE_ONLY`, `DIFF_ONLY`).
- Active blockers with reason codes and source artifacts.
- Per-sentence or per-block provenance references.
- Explicit market scope and TE disclosure.

Must be suppressed:
- Action-implying language under unknown/degraded contexts.
- Causal claims not directly represented in source artifacts.
- Any ranking, recommendation, or future-state framing.

Language bans (explicit):
- `buy`, `sell`, `enter`, `exit`, `conviction`, `opportunity`, `upside`, `downside`, `likely`, `expected`, `target`, `should`, `must buy`, `favorable setup`.

Visual semantics constraints:
- No green "healthy narrative" indicator when `F1` or `F2` blockers are active.
- Suppressed narrative state must be persistent and non-dismissible.
- Narrative card must not be visually merged with policy/capital-adjacent surfaces.

## 6. Operator Control and Overrides
Operator may choose:
- Narrative operating mode policy (`Hard Suppress`, `Evidence Only`, `Diff`).
- Minimum source completeness requirement for non-suppressed output.
- Market-specific narrative strictness (US and INDIA independently).

System must never infer:
- Missing causal links.
- Action recommendations from policy permissions.
- Cross-market narrative conclusions.

Required confirmations and holds:
- Explicit operator acknowledgment before unsuppressing narrative mode after blocker clearance.
- Confirmation that unsuppression does not imply execution enablement.
- Hold remains active while blocker source is unresolved.

## 7. Explicit Constraints
- No recommendation, ranking, or predictive narrative outputs.
- No automatic narrative unsuppression on ingestion refresh alone.
- No regime inference from system clock.
- No TE advancement side effects.
- No execution or capital semantics in narrative text.
- No cross-market narrative contamination.

## 8. Open Design Decisions
- Default mode under mixed uncertainty: `SUPPRESSED` vs `EVIDENCE_ONLY`.
- Minimum artifact set required for narrative emission.
- Whether sentence-level provenance must be operator-visible by default.
- Maximum narrative length under degraded states.
- Whether manual unsuppression expires automatically after N hours.

## 9. Mandatory Non-Goals
- This design does not implement narrative runtime logic.
- This design does not alter policy, factor, or ingestion algorithms.
- This design does not advance Truth Epoch.
- This design does not add execution or capital pathways.
- This design does not resolve F1 or F2 directly.
- This design does not optimize narrative style or engagement.

