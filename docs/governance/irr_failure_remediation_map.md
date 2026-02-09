# IRR Failure Remediation Map

## 1. Overview
This document consolidates Integration Reality Run (IRR) and Shadow Reality Run findings into a single governance remediation map.

Purpose:
- Create one canonical view of failure classes (`F1`-`F5`) for Phase-7 readiness decisions.
- Preserve epistemic legibility by tying each class to concrete observed evidence.
- Define remediation priority without implementing fixes.

Explicit status:
- No remediation is implemented by this document.
- No Truth Epoch advancement is authorized by this document.
- No execution/capital capability is altered by this document.

## 2. Failure Class Definitions (F1-F5)

### F1 - Temporal Drift Accumulation
- Name: Temporal Drift Accumulation
- Observed evidence:
  - `US`: `CTT 2026-02-06` vs frozen `TE 2026-01-30` (`+7d`), from `docs/irr/runtime/IRR-2026-02-09-001/post_state.json`
  - `INDIA`: `CTT 2026-02-09` vs frozen `TE 2026-01-30` (`+10d`), from `docs/irr/runtime/IRR-2026-02-09-001/post_state.json`
  - US temporal refresh failure (`Could not determine RDT for US`), from `docs/irr/runtime/IRR-2026-02-09-001/03_temporal_orchestrator.log`
- Why it matters epistemically:
  - Unbounded `CTT > TE` drift weakens trust that policy/narrative outputs represent evaluated reality at the declared epoch.
  - Drift accumulation increases stale-state interpretation risk and makes evidence-age ambiguity operator-hostile.
- Governance verdict: UNSATISFIED (`INV-TRUTH-EPOCH-EXPLICIT` at operational level; explicit freeze exists but bounded staleness control is missing).
- Phase-7 blocking status: BLOCKING

### F2 - Regime Instability Under Partial Canonical Updates
- Name: Regime Instability Under Partial Canonical Updates
- Observed evidence:
  - Same-day incompatible INDIA policy states (`HALTED/UNKNOWN` vs `ACTIVE/BULLISH`) across paths, from:
    - `docs/irr/runtime/IRR-2026-02-09-001/india_decision_policy_via_core_engine.json`
    - `docs/intelligence/decision_policy_INDIA.json`
  - Core policy path schema mismatch resolving market to `UNKNOWN`, from:
    - `docs/irr/runtime/IRR-2026-02-09-001/us_decision_policy.json`
    - `docs/irr/runtime/IRR-2026-02-09-001/india_decision_policy_via_core_engine.json`
  - EV-TICK cross-market binding leakage signal (`No benchmark binding for US` while processing INDIA), from `docs/irr/runtime/IRR-2026-02-09-001/08_ev_tick.log`
- Why it matters epistemically:
  - Identical evaluation day yields path-dependent regime truth, violating determinism and operator legibility.
  - Regime-as-source-of-truth cannot be trusted if canonicalization and schema contracts diverge by path.
- Governance verdict: UNSATISFIED (deterministic truth-to-policy binding is not stable).
- Phase-7 blocking status: BLOCKING

### F3 - Narrative Over-Resolution in Stagnation
- Name: Narrative Over-Resolution in Stagnation
- Observed evidence:
  - Real narrative path produced no narratives due endpoint failure (`404`), from `docs/irr/runtime/IRR-2026-02-09-001/12_real_market_stories.log`
  - Shadow replay still emits declarative action strings (e.g., `BUY`) under weak/unknown context, from `docs/irr/runtime/SHADOW-2026-02-09-001/US/decision_trace_log.parquet`
- Why it matters epistemically:
  - In stagnation, the system should resolve to explicit uncertainty; over-resolved action framing can imply unjustified decisiveness.
  - Absence of narrative truth plus action-like outputs distorts operator interpretation.
- Governance verdict: PARTIALLY UNSATISFIED (no live narrative hallucination observed, but stagnation semantics are not consistently conservative across outputs).
- Phase-7 blocking status: CONDITIONAL BLOCKER (must be constrained before controlled truth advancement)

### F4 - UI Epistemic Leakage
- Name: UI Epistemic Leakage
- Observed evidence:
  - Temporal truth source divergence can surface conflicting epoch references (`TRUTH_EPOCH_2026-02-07_01` vs `TE-2026-01-30`), from:
    - `docs/epistemic/truth_epoch.json`
    - `docs/intelligence/execution_gate_status.json`
    - `docs/intelligence/temporal/temporal_state_US.json`
  - UI transport checks pass while epistemic consistency remains unresolved, from `docs/irr/runtime/IRR-2026-02-09-001/13_ui_backend_verify.log`
- Why it matters epistemically:
  - A UI can be technically healthy while truth labels are semantically inconsistent.
  - Conflicting epoch disclosure undermines `OBL-TRUTH-EPOCH-DISCLOSED` and operator trust.
- Governance verdict: UNSATISFIED (truth disclosure not singular across surfaces).
- Phase-7 blocking status: BLOCKING

### F5 - Suppression Dominance Opacity
- Name: Suppression Dominance Opacity
- Observed evidence:
  - Suppression is present but split across multiple outputs (manual context path, canonical INDIA path, tick-context path) requiring cross-file reconstruction, from:
    - `docs/irr/suppression_events.md`
    - `docs/irr/runtime/IRR-2026-02-09-001/us_decision_policy_manual.json`
    - `docs/intelligence/decision_policy_INDIA.json`
    - `docs/irr/runtime/IRR-2026-02-09-001/india_decision_policy_via_core_engine.json`
  - Tick-context path suppresses everything through `market=UNKNOWN`, obscuring whether suppression is policy-intent or schema failure.
- Why it matters epistemically:
  - Operators must distinguish intentional safety suppression from pipeline breakage suppression.
  - Without transparent suppression attribution, stagnation can be misread as valid strategic caution.
- Governance verdict: PARTIALLY UNSATISFIED (monotonic suppression holds, attribution legibility does not).
- Phase-7 blocking status: P1 blocker (must be remediated before any broad truth advancement)

## 3. Remediation Priority Matrix

| Priority | Failure Classes | Rationale | Phase-7 Gate Impact |
|---|---|---|---|
| `P0` | `F1`, `F2`, `F4` | Core truth-time integrity, deterministic regime binding, and UI truth disclosure are foundational controls. | Hard blockers. No Truth Advancement while unresolved. |
| `P1` | `F5` | Suppression explainability is required for operator trust and correct stagnation interpretation. | Blocker for controlled expansion beyond minimal audit mode. |
| `P2` | `F3` | Narrative conservatism and stagnation-language hardening after foundational truth-path stabilization. | Required before narrative-dependent advancement decisions. |

Required before any controlled Truth Advancement:
- All `P0` classes (`F1`, `F2`, `F4`) must be resolved and verified.
- `F5` must have operator-legible suppression attribution.
- `F3` must enforce conservative stagnation semantics in narrative/decision surfaces.

## 4. Explicit Non-Goals
This remediation map explicitly excludes:
- Implementing fixes in ingestion, factor, policy, or dashboard code.
- Advancing `TE` or changing Truth Epoch freeze state.
- Enabling execution, broker connectivity, or capital deployment.
- Strategy optimization, ranking, or performance tuning.
- Root-cause implementation details for `F2`-`F5` (tracked separately; not designed in this file).
