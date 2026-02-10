# Execution Phases

## Cross-Cutting
- Component: `Governance`
- Role: Constitutional policy enforcement across all phases.
- `OPEN_QUESTION`: Governance is not assigned a single numbered phase in the source contracts; it is modeled as an always-on control plane.

## Phase 0: Ingestion
- Purpose: Acquire and normalize market/event inputs for downstream cognition.
- Components:
  - `Data Ingestion (US)`
  - `Data Ingestion (India)`
  - `Event Ingestion`
- Gating rules:
  - L0 pipelines must publish usable/stale-explicit data before Phase 1.
  - Raw/event timestamps must remain source-authored (no silent temporal rewrite).
  - Missing or stale feeds must surface explicit degraded states (no silent continuation).

## Phase 1: Regime + Narrative
- Purpose: Establish market reality and causal explanation context.
- Components:
  - `Regime Engine`
  - `Narrative Engine`
- Gating rules:
  - `Regime Engine` must complete before `Narrative Engine`.
  - `Narrative Engine` must not execute without `RegimeState` context.
  - If regime input quality is insufficient, propagate `UNKNOWN`/`INSUFFICIENT_DATA` explicitly.

## Phase 2: Meta + Factor
- Purpose: Score trustworthiness, then define rewarded styles and permissions.
- Components:
  - `Meta-Analysis Engine`
  - `Factor Engine`
- Gating rules:
  - `Meta-Analysis Engine` requires Phase 1 outputs (`RegimeState`, `NarrativeObjects`).
  - `Factor Engine` requires trust-filtered context (`Meta-Analysis`) plus regime context.
  - Factor permissions are fail-closed; denied/unknown permissions block downstream style activation.
- `OPEN_QUESTION`: `Meta-Analysis Engine` lists `Scanners/Lenses (L6)` as an upstream source, which conflicts with strict L1->L9 ordering; treat this as non-blocking telemetry input until contract clarification.

## Phase 3: Strategy + Discovery
- Purpose: Activate eligible playbooks, then scan the universe in parallel lenses.
- Components:
  - `Strategy Selector`
  - `Momentum Engine`
  - `Narrative Lens`
  - `Factor Lens`
  - `Fundamental Lens`
  - `Technical Lens`
  - `Strategy Lens`
- Gating rules:
  - Discovery must never start before strategy selection state is available.
  - `Strategy Lens` must consume only `ACTIVE` playbooks.
  - Lens outputs remain candidate-only (no execution instructions).
  - `Fundamental Lens` may legally return `INSUFFICIENT_DATA` until RC-4 ingestion wiring is complete.

## Phase 4: Convergence
- Purpose: Merge lens candidates into scored, regime-aware assessments.
- Components:
  - `Convergence Engine`
- Gating rules:
  - Requires candidate inputs from L6 lenses plus strategy/regime context.
  - `HighConvictionIdeas` require >=3 independent lens confirmations.
  - Empty lens pools remain valid and must emit empty outputs explicitly.

## Phase 5: Constraints + Portfolio
- Purpose: Apply hard limits, then generate portfolio diagnostics.
- Components:
  - `Constraint Engine`
  - `Portfolio Intelligence`
- Gating rules:
  - `Constraint Engine` must run before `Portfolio Intelligence`.
  - `Portfolio Intelligence` is always diagnostic/advisory (no execution authority).
  - Portfolio stage is the final computational phase before dashboard publication.

## Phase 6: Dashboard
- Purpose: Read-only glass-box observation of complete system state.
- Components:
  - `Dashboard (Observer UI)`
- Gating rules:
  - Dashboard is terminal in orchestration order.
  - Must expose stale/disconnected/insufficient-data conditions explicitly.
  - No write path to upstream system state is permitted.
