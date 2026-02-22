# Architectural Convergence Audit — V3 Memory Layers (All 13 Layers)

**Generated**: 2026-02-20
**Scope**: All V3 layers `00_vision` through `12_orchestration`
**Batch**: Full (Layers 00–12)
**V2 Comparators**: `architecture/`, `audit/`, `capital/`, `contracts/`, `dashboard/`, `diagnostics/`, `epistemic/`, `evolution/`, `intelligence/`, `meta/`

---

> **Critical Architectural Finding (Pre-Audit)**: V3 memory layers are designed as a **canonical consolidation layer** over V2 scattered documentation. Each layer explicitly declares a `Legacy Source Mapping` section identifying V2 docs as authoritative sources for specific sub-topics. This audit evaluates the fidelity of that consolidation and identifies where V3 adds, degrades, or fails to capture V2 contract depth. The V3 layers are NOT a replacement system — they are a structured reference architecture intended to become the canonical memory for the system. This shapes every assessment below.

---

## SECTION 1 — LAYER PURPOSE EXTRACTION (V3)

### Layer 00_vision

| Attribute | Description |
|:---|:---|
| **Responsibility** | Declares the system's north star: situational clarity over prediction. Defines the 13-level cognitive hierarchy (L0–L12) and establishes the product philosophy (Diagnostics Over Commands, Glass-Box, Uncertainty as Feature, Human-in-the-Loop, Conditional Intelligence). |
| **Declared Contracts** | None formal. Four anti-patterns listed (Level Skipping, Black-Box, Future Prediction, Hidden Uncertainty). Aspirational statements only. |
| **Memory Interactions** | Seeds all 12 downstream V3 layers conceptually. Referenced by 01_scope for Three Worlds justification. Referenced by 11_deployment for evolution principles. |
| **Dependencies** | None declared. Foundational. |
| **Governance Rules** | None operative. Anti-patterns stated but not enforced by any mechanism within this layer. |

---

### Layer 01_scope

| Attribute | Description |
|:---|:---|
| **Responsibility** | Defines the Three Worlds (Production / Research / Vision) as non-negotiable boundaries. Specifies current phase (Research & Validation / Shadow Mode). Declares in-scope (L0–L9) and out-of-scope items. Defines user profile (≤₹1Cr, Research-Lead Discretionary). Specifies time bands. States Research Exit Criteria. |
| **Declared Contracts** | Three Worlds separation rules ("Vision MUST NOT leak into Production"). Research Exit Criteria (3 criteria: regime stability, lens consensus, drawdown control). Sources explicitly cited (`docs/epistemic/current_phase.md`, `docs/VISION_BACKLOG.md`). |
| **Memory Interactions** | Constrains all layers 02–12. Defines what is in scope for 03_domain. Referenced by 11_deployment (Three Worlds), 12_orchestration (shadow mode scope). |
| **Dependencies** | 00_vision (references vision's cognitive hierarchy). Cites V2 `epistemic/current_phase.md` and `research_product_architecture.md`. |
| **Governance Rules** | Three Worlds boundary rules (stated). Research Exit Criteria (stated but not machine-enforced within this layer). |

---

### Layer 02_success

| Attribute | Description |
|:---|:---|
| **Responsibility** | Defines behavioral completion conditions for trusting the system. Specifies success criteria per cognitive layer (L1 Regime, L6–L7 Discovery, L8–L9 Portfolio Intelligence). Defines Phase Exit Criteria for Shadow Mode. Defines Dashboard & Observability success. Defines L3 Meta-Analysis invariants (4 formal invariants embedded directly). Signal quality grading (A/B/C/D). |
| **Declared Contracts** | Formal invariants for L3 (Regime Dependency, Trust Score Boundaries [0.0, 1.0], Regime-Aware Adjustment, Explainability Requirement). Quantified thresholds: ≥60% factor alignment, ≥3 lenses for High-Conviction, ≤5% false regime flip rate, ≥80% predictive diagnostic accuracy, 100% idempotency. |
| **Memory Interactions** | Referenced by 10_observability (success metrics), 11_deployment (phase exit criteria), 12_orchestration (shadow promotion criteria). References 03_domain as CANONICAL. |
| **Dependencies** | 00_vision, 01_scope, 03_domain (declared CANONICAL). |
| **Governance Rules** | Phase exit criteria with explicit quantified thresholds. TEST_ROUTER invariant. Commit trigger invariants. |

---

### Layer 03_domain

| Attribute | Description |
|:---|:---|
| **Responsibility** | Canonical domain entity definitions for all cognitive levels L0–L9. Defines `RegimeState`, `NarrativeObject`, `FactorSignal`, `OpportunityCandidate`, `CandidateAssessment`, `ExecutionEnvelope`, `PortfolioDiagnostic`. Specifies entity relationships (dependency graph). Defines terminology conventions. |
| **Declared Contracts** | Entity schemas with field names, types, enumerations. Relationship graph (`Regime → Meta → Factor → Strategy`). Terminology definitions (Glass-Box, Shadow Mode, Orphan, Genesis). |
| **Memory Interactions** | Declared as CANONICAL for all other V3 layers. All layers must defer to this document in case of conflict. |
| **Dependencies** | None. Foundational canonical. |
| **Governance Rules** | Declared CANONICAL authority — all other layers must align to this model. |

---

### Layer 04_architecture

| Attribute | Description |
|:---|:---|
| **Responsibility** | Defines end-to-end pipeline (L0–L9 + Dashboard + Human), ingestion pipelines (US REST batch, India WebSocket streaming), cognitive processing flow (L1–L5), prohibited bypasses (BAN-1 through BAN-4), feedback channels (upward to DESIGN only, never to STATE), data object lifecycle (Bronze/Silver/Gold/Transient/Final), research report types, daily cycle, resolved conflicts and questions (RC-4, RC-5, RC-6, RQ-5, RQ-6, RQ-7). |
| **Declared Contracts** | Pipeline invariants (raw data immutability, market isolation, event-time integrity, idempotency). BAN rules enforced by contract. Communication via immutable state snapshots. Feedback allowed upward to DESIGN only. Conflict log maintained. |
| **Memory Interactions** | Referenced by 05_components, 06_data, 07_execution, 12_orchestration. Cites `docs/memory/03_domain/domain_model.md` as CANONICAL. |
| **Dependencies** | 03_domain. |
| **Governance Rules** | BAN-1 through BAN-4 prohibitions. Pipeline invariant table. |

---

### Layer 05_components

| Attribute | Description |
|:---|:---|
| **Responsibility** | Universal component health contract applicable to ALL system components. Defines required health fields (`health_status`, `last_success_timestamp`, `failure_count`, `degraded_reason`). Defines state machine (OK → DEGRADED → FAILED). Defines OK/DEGRADED/FAILED conditions, recovery protocol, required observability signals (6 signal types). Specifies YAML integration requirements. References canonical implementation (`src/layers/macro_layer.py`). |
| **Declared Contracts** | CANONICAL health interface — all components MUST comply. State transition rules (specific conditions for each transition). Recovery requirements (all conditions must resolve, failure_count resets to 0). Observability signals with types and frequencies. YAML integration schema. |
| **Memory Interactions** | Referenced by all component YAMLs in `docs/memory/05_components/`. YAML health_contract field points to this document. |
| **Dependencies** | 04_architecture (component context). |
| **Governance Rules** | Canonical authority declared. "All components MUST comply." Reference implementation with unit tests cited. FAILED state triggers Fail-Closed behavior. |

---

### Layer 06_data

| Attribute | Description |
|:---|:---|
| **Responsibility** | Comprehensive data contracts: source system contracts (Alpha Vantage, Angel One SmartAPI, Event Sources), data schemas (10 schemas defined), proxy sets (US + India), proxy dependency binding rules, data lineage rules (isolation, immutability, Bronze/Silver/Gold layers), temporal truth model (three planes: RDT/CTT/TE), retention & archival policy, ingestion guarantees (US + India), dashboard API contract (read-only endpoints), coverage gaps (US + India with priorities), evaluation profile contract. |
| **Declared Contracts** | Temporal invariant (`TE ≤ CTT ≤ RDT`; `TE > CTT = CORRUPT`). Proxy role abstraction rule (no direct raw file access). Evaluation profile constraints (`shadow_only: true`, `execution_disabled: true`). Deletion protocol (human approval required). Market isolation invariant. Immutability rules. Dedup key rules. |
| **Memory Interactions** | Referenced by 07_execution, 08_reliability, 10_observability. Consolidates V2 contracts as source via Legacy Source Mapping. |
| **Dependencies** | 04_architecture, 03_domain. |
| **Governance Rules** | Temporal invariant enforcement. Deletion protocol. Nine sectioned governance rules across temporal, lineage, retention, evaluation. |

---

### Layer 07_execution

| Attribute | Description |
|:---|:---|
| **Responsibility** | Runtime model: orchestration principles, four runtime modes (Batch/Streaming/EV-TICK/Shadow), execution harness (responsibilities, prohibitions, task graph model, state machine), truth epoch advancement (three gates: Ingestion/Intelligence/Global Sync + Emergency Override), automation limits (bounded automation contract), operator workflow (SOD/EOD/Post-Market cycles), dashboard runtime contract, skill registration model (lifecycle, invariants, violation handling), cross-pipeline invariants. |
| **Declared Contracts** | Nine cross-pipeline invariants (market separation, event time integrity, no lookahead, idempotency, shadow enforcement, no autonomous TE advancement, append-only audit, proxy versioning). Harness prohibitions (6 explicitly listed). Skill invariants (no upstream inference, idempotent, decision-authorized). Gate protocols with explicit pass/fail criteria. Automation limits (read-only monitors). |
| **Memory Interactions** | References 06_data (temporal truth model). References 08_reliability (failure handling). Consolidates V2 execution harness contract. |
| **Dependencies** | 03_domain, 04_architecture, 06_data. |
| **Governance Rules** | Truth epoch advancement gates. Bounded automation contract. Skill lifecycle states (REGISTERED → ACTIVE → DEPRECATED → REMOVED). Emergency override requiring stringent justification. |

---

### Layer 08_reliability

| Attribute | Description |
|:---|:---|
| **Responsibility** | Comprehensive failure model: design approach (Fail Closed, No Silent Degradation, Monotonic Suppression), temporal failures (five drift states), ingestion failures per pipeline (US + India + restart behaviors), regime failures with ingestion obligations (OBL-RG-ING-OBL), narrative failures with hallucination controls (6 controls), factor/meta failures, strategy/convergence failures, execution harness failures, circuit breakers (Decision Policy + Fragility Policy + EVENT_LOCK), degraded state registry (two authorized degraded states), dashboard/UI failures, shadow mode failures (five failure types), IRR failure taxonomy (F1–F5 with P-levels), epistemic drift detection (6 drift classes), component failure summary table, troubleshooting quick reference. |
| **Declared Contracts** | IRR failure taxonomy with explicit P0/P1/P2 blocking criteria. Degraded state authorization (DEG-IN-001, DEG-US-001 with explicit authorization scope). Hallucination controls (6 formally listed). Fragility Policy permission formula (`Final = DecisionPolicy − FragilityPolicy.Revocations`). Epistemic drift severity levels (INFO/WARNING/FAIL/CRITICAL). Five narrative failure response patterns. |
| **Memory Interactions** | References 07_execution, 09_security. Consolidates V2 audit, IRR, and contracts documentation. |
| **Dependencies** | All other layers (cross-cutting reliability concern). |
| **Governance Rules** | IRR remediation priority table (P0 must resolve before any controlled Truth Advancement). Degraded state authorization requirements. Shadow safety verification (mandatory 4-step check). |

---

### Layer 09_security

| Attribute | Description |
|:---|:---|
| **Responsibility** | Trust & security model: core trust principles, trust domains (execution/data/module/strategy), seven ABSOLUTE safety invariants, access controls (physical isolation, layer authority matrix, skill authority hierarchy), credential handling (vendor-specific, security rules, forbidden behaviors), operator model (authorities, kill-switch hierarchy, chat execution contract, multi-human governance), survivability obligations (OBL-SS-*), data deletion/retention security, research module security guardrails. |
| **Declared Contracts** | Seven ABSOLUTE invariants: `INV-NO-EXECUTION`, `INV-NO-CAPITAL`, `INV-NO-SELF-ACTIVATION`, `INV-PROXY-CANONICAL`, `INV-TRUTH-EPOCH-EXPLICIT`, `INV-NO-TEMPORAL-INFERENCE`, `INV-HONEST-STAGNATION`. Kill-switch hierarchy (Global/Family/Strategy) with no automated resets. Chat execution contract (6 rules). Survivability obligations (6 OBL-SS-*). Five research module security guardrails. |
| **Memory Interactions** | References 07_execution (automation trust), 11_deployment (module promotion). Consolidates V2 capital and epistemic security docs. |
| **Dependencies** | 03_domain (trust hierarchy). |
| **Governance Rules** | Kill-switch reset authority (human only — no automated resets for any level). Credential handling rules (10 stated). Multi-human governance policy (Freshness Rule, Maintainer Veto). |

---

### Layer 10_observability

| Attribute | Description |
|:---|:---|
| **Responsibility** | Observability and metrics: six categories of metrics (signal, pipeline, temporal, regime, governance, execution), logging architecture (8 log categories, structured logging intent, exclusions), dashboard surfaces (9 panels with data sources), widget binding rules (4 rules + forbidden semantics list), alerting (6 alert definitions with severity/color), validation checks (data/regime/narrative/governance/harness), observability success criteria. |
| **Declared Contracts** | Widget binding rules: single artifact binding, single layer binding, single epoch binding, trace badge requirement. Forbidden dashboard semantics (8 explicit prohibitions). Alert definitions with severity levels. Validation check tables with failure responses. Glass-box principle as non-negotiable. Structure over ad-hoc (machine-parseable JSON required). |
| **Memory Interactions** | References 02_success (success metrics), 04_architecture (pipeline health), 07_execution (harness metrics). Consolidates V2 dashboard docs. |
| **Dependencies** | All other layers (cross-cutting observability concern). |
| **Governance Rules** | Forbidden dashboard semantics prohibitions. Bounded ledger growth. Provenance requirement on all displayed values. No silent zeros or blanks. |

---

### Layer 11_deployment

| Attribute | Description |
|:---|:---|
| **Responsibility** | Deployment & evolution: evolution principles (7 principles), three worlds (complete boundary definition), runtime environment (components, ports, assumptions), foundation phase model (Phases 1–3B, CLOSED), structural plane model (Planes 1–7, all COMPLETE), migration paths (module authority matrix + 5-gate promotion process + activation schedule), phase lock governance (locked artifacts vs mutable registries + lock-breaking protocol), truth advancement gates (Gates 1–4), DWBS post-freeze roadmap (P1–P7), release assumptions, evolution rules (add/extend/deprecate/anti-patterns). |
| **Declared Contracts** | Phase lock contract (3 locked artifacts: `CON-001`, `CON-002`, `CON-003 NEVER`). 5-gate promotion process. Lock-breaking protocol (5-step). Evolution vs. drift distinction (formal classification). Anti-patterns table (10 forbidden evolutionary actions). Release assumptions (15 explicit). Phase exit criteria (6 quantified criteria). Blocked items with blocking conditions. |
| **Memory Interactions** | References 01_scope (Three Worlds), 04_architecture (data layers), 07_execution (truth gates). |
| **Dependencies** | 01_scope, 07_execution. |
| **Governance Rules** | Freeze Discipline (FROZEN by default). One-Skill-at-a-Time rule. Audit-Before-Scale rule. Rollback-First rule. Phase lock breaking protocol. Module promotion gates. |

---

### Layer 12_orchestration

| Attribute | Description |
|:---|:---|
| **Responsibility** | Execution phases (0–6: Ingestion → Regime+Narrative → Meta+Factor → Strategy+Discovery → Convergence → Constraints+Portfolio → Dashboard), retry policy per component (all 18 components with retryable flag, max_attempts, backoff strategy, fail_behavior), shadow mode scope (per-phase shadow behavior), shadow promotion criteria (global + phase-specific gates). |
| **Declared Contracts** | Retry policy table (18 components; explicit non-retryable components: Meta-Analysis, Strategy Selector, Narrative/Technical/Strategy Lens, Convergence Engine, Portfolio Intelligence). Phase gating rules (Regime must complete before Narrative; Factor requires Meta outputs; Discovery must not start before Strategy selection). Shadow promotion criteria cross-referenced to 02_success. OPEN_QUESTIONs honestly flagged (3 identified). |
| **Memory Interactions** | References 02_success (shadow promotion criteria), 05_components (component definitions). Consolidates V2 component YAMLs. |
| **Dependencies** | 05_components, 07_execution. |
| **Governance Rules** | Phase gating rules. Shadow promotion requires both global and phase-specific criteria. OPEN_QUESTIONs logged (not silently ignored). |

---

## SECTION 2 — V2 EQUIVALENCE MAPPING

### Layer 00_vision

| V3 Layer | V2 Folder | Specific File/Module | Responsibility Overlap | Depth in V2 (1–10) | Notes |
|:---|:---|:---|:---|:---|:---|
| 00_vision | epistemic/ | `project_intent.md` | System purpose declaration | 7 | V2 project_intent is operationally tighter; references concrete phase goals |
| 00_vision | architecture/ | `DWBS.md` (preamble) | High-level system philosophy | 7 | V2 DWBS binds philosophy to build sequence |
| 00_vision | epistemic/ | `structure_stack_vision.md` | Vision of system structure | 5 | V2 structure vision is loose/conceptual |
| 00_vision | docs/ | `VISION_BACKLOG.md` | Vision items and Three Worlds | 4 | Non-operative; awareness-only |
| 00_vision | epistemic/ | `what_counts_as_progress.md` | Anti-patterns and progress criteria | 6 | V2 more operationally grounded |

### Layer 01_scope

| V3 Layer | V2 Folder | Specific File/Module | Responsibility Overlap | Depth in V2 (1–10) | Notes |
|:---|:---|:---|:---|:---|:---|
| 01_scope | epistemic/ | `current_phase.md` | Current phase scope and exit criteria | 8 | V2 is operationally authoritative for current phase |
| 01_scope | contracts/ | `layer_interaction_contract.md` | Boundary enforcement between layers | 9 | V2 contract is constitutional; V3 scope is intent |
| 01_scope | architecture/ | `DWBS.md` (scope sections) | What the system builds/includes | 8 | V2 DWBS has build-scope formally gated |
| 01_scope | epistemic/ | `latent_structural_layers.md` | Out-of-scope latent layers | 7 | V2 explicitly classifies latent layers |
| 01_scope | docs/ | `research_product_architecture.md` | Research scope and output types | 6 | V2 research architecture partially overlaps |

### Layer 02_success

| V3 Layer | V2 Folder | Specific File/Module | Responsibility Overlap | Depth in V2 (1–10) | Notes |
|:---|:---|:---|:---|:---|:---|
| 02_success | epistemic/ | `current_phase.md` | Phase exit criteria | 8 | V2 has operational phase exit tracking |
| 02_success | audit/ | `full_system_audit.md` | Success validation in operation | 8 | V2 validates success criteria against real runs |
| 02_success | audit/ | `FULL_SYSTEM_AUDIT_POST_INTELLIGENCE.md` | Post-intelligence success validation | 8 | V2 evaluates decision layer success operationally |
| 02_success | diagnostics/ | `regime_observability_summary.md` | Regime success measurement | 7 | V2 has concrete observed regime metrics |
| 02_success | epistemic/ | `what_counts_as_progress.md` | Progress criteria | 6 | V2 qualitative progress definition |

### Layer 03_domain

| V3 Layer | V2 Folder | Specific File/Module | Responsibility Overlap | Depth in V2 (1–10) | Notes |
|:---|:---|:---|:---|:---|:---|
| 03_domain | epistemic/ | `belief_layer_policy.md` | Belief entity policy | 8 | V2 has more specific belief layer policy |
| 03_domain | epistemic/ | `factor_layer_policy.md` | Factor entity definitions | 8 | V2 factor policy is enforcement-level |
| 03_domain | epistemic/ | `strategy_layer_policy.md` | Strategy entity definitions | 8 | V2 strategy policy has lifecycle rules |
| 03_domain | architecture/ | `system_landscape.md` | High-level entity map | 7 | V2 landscape is component-focused |
| 03_domain | architecture/ | `DWBS_SYSTEM_LANDSCAPE.md` | System component definitions | 7 | V2 landscape describes components in build context |

### Layer 04_architecture

| V3 Layer | V2 Folder | Specific File/Module | Responsibility Overlap | Depth in V2 (1–10) | Notes |
|:---|:---|:---|:---|:---|:---|
| 04_architecture | contracts/ | `layer_interaction_contract.md` | Communication model, BAN rules | 9 | V2 contract is constitutional for layer interactions |
| 04_architecture | architecture/ | `DWBS.md` | System build architecture | 8 | V2 DWBS is the primary build architecture doc |
| 04_architecture | architecture/ | `ingestion_proxy_wiring.md` | Ingestion pipeline wiring | 8 | V2 has specific wiring verification |
| 04_architecture | docs/ | `us_market_engine_design.md` | US pipeline architecture | 8 | V2 is detailed operational pipeline spec |
| 04_architecture | docs/ | `INDIA_WEBSOCKET_ARCHITECTURE.md` | India WebSocket pipeline | 8 | V2 is detailed operational pipeline spec |

### Layer 05_components

| V3 Layer | V2 Folder | Specific File/Module | Responsibility Overlap | Depth in V2 (1–10) | Notes |
|:---|:---|:---|:---|:---|:---|
| 05_components | epistemic/ | `skills_catalog.md` | Component/skill capability catalog | 7 | V2 defines skills; V3 defines health abstraction |
| 05_components | audit/ | `full_system_audit.md` | Component health validation | 7 | V2 audits component status; not same as health contract |
| 05_components | docs/memory/ | `05_components/*.yaml` | Individual component specs | 8 | Source of retry_policy, failure_modes per component |
| 05_components | architecture/ | `DWBS_INTELLIGENCE_IMPLEMENTATION.md` | Intelligence component implementation | 7 | V2 describes intelligence component structure |

### Layer 06_data

| V3 Layer | V2 Folder | Specific File/Module | Responsibility Overlap | Depth in V2 (1–10) | Notes |
|:---|:---|:---|:---|:---|:---|
| 06_data | contracts/ | `RAW_ANGEL_INTRADAY_SCHEMA.md` | India raw data schema | 9 | V2 is the authoritative schema; V3 consolidates it |
| 06_data | contracts/ | `PROCESSED_INTRADAY_SCHEMA.md` | India processed schema | 9 | V2 authoritative processed schema |
| 06_data | contracts/ | `market_proxy_sets.md` | Proxy set definitions | 9 | V2 locked contract (`CON-001`); V3 references it |
| 06_data | contracts/ | `proxy_dependency_contracts.md` | Proxy binding rules | 9 | V2 locked contract (`CON-002`); V3 references it |
| 06_data | contracts/ | `RAW_DATA_LINEAGE_RULES.md` | Data lineage rules | 9 | V2 is the authoritative lineage contract |
| 06_data | epistemic/ | `data_retention_policy.md` | Retention and archival | 8 | V2 operationally governs retention |
| 06_data | governance/ | `temporal_truth_contract.md` | Temporal truth model (RDT/CTT/TE) | 9 | V2 is authoritative; `CON-003: NEVER` breaks |
| 06_data | dashboard/ | `api_schema.md` | Dashboard API contract | 8 | V2 defines API schema operationally |
| 06_data | data/ | `coverage_gap_register.md` | Coverage gaps | 8 | V2 is the live gap register |

### Layer 07_execution

| V3 Layer | V2 Folder | Specific File/Module | Responsibility Overlap | Depth in V2 (1–10) | Notes |
|:---|:---|:---|:---|:---|:---|
| 07_execution | contracts/ | `execution_harness_contract.md` | Execution harness model | 10 | V2 is Constitutional/Binding; V3 intent layer |
| 07_execution | epistemic/ | `bounded_automation_contract.md` | Automation limits | 9 | V2 is the operative automation constraint |
| 07_execution | governance/ | `truth_advancement_gates.md` | Gate protocols | 9 | V2 is the operative gate documentation |
| 07_execution | runbooks/ | `start_of_day.md`, `end_of_day.md` | Operator workflow | 7 | V2 runbooks are the operational procedures |
| 07_execution | epistemic/ | `current_phase.md` | Current execution mode (shadow only) | 8 | V2 defines operative phase constraints |

### Layer 08_reliability

| V3 Layer | V2 Folder | Specific File/Module | Responsibility Overlap | Depth in V2 (1–10) | Notes |
|:---|:---|:---|:---|:---|:---|
| 08_reliability | audit/ | `temporal_drift_failure_modes.md` | Temporal drift failure taxonomy | 8 | V2 has observed real failure modes; V3 codifies them |
| 08_reliability | audit/ | `f1_temporal_drift_implementation_report.md` | F1 failure implementation | 8 | V2 contains root cause analysis |
| 08_reliability | contracts/ | `fragility_policy_contract.md` | Circuit breaker policy | 9 | V2 is constitutional for fragility |
| 08_reliability | contracts/ | `decision_policy_contract.md` | Decision circuit breaker | 9 | V2 is constitutional for decision policy |
| 08_reliability | data/ | `degraded_state_registry.md` | Degraded state registry | 8 | V2 maintains the live degraded state list |
| 08_reliability | contracts/ | `epistemic_drift_validator_specification.md` | Drift detection | 9 | V2 specification for the drift validator |
| 08_reliability | narrative/ | `failure_and_hallucination_controls.md` | Narrative failure controls | 8 | V2 has operative hallucination prevention |

### Layer 09_security

| V3 Layer | V2 Folder | Specific File/Module | Responsibility Overlap | Depth in V2 (1–10) | Notes |
|:---|:---|:---|:---|:---|:---|
| 09_security | capital/ | `kill_switch.md` | Kill-switch governance | 9 | V2 is the operative kill-switch specification |
| 09_security | capital/ | `risk_envelopes.md` | Risk limits and envelopes | 8 | V2 defines risk envelope rules |
| 09_security | epistemic/ | `architectural_invariants.md` | Safety invariants | 9 | V2 is the authoritative invariant list |
| 09_security | epistemic/ | `bounded_automation_contract.md` | Automation security limits | 9 | V2 is operative constraint doc |
| 09_security | epistemic/ | `chat_execution_contract.md` | AI interface security | 8 | V2 defines chat security boundaries |
| 09_security | epistemic/governance/ | `scale_safety_obligations.md` | Survivability obligations | 9 | V2 is the operative obligation list |
| 09_security | governance/ | `RESEARCH_MODULE_GOVERNANCE.md` | Module security guardrails | 8 | V2 is operative governance policy |

### Layer 10_observability

| V3 Layer | V2 Folder | Specific File/Module | Responsibility Overlap | Depth in V2 (1–10) | Notes |
|:---|:---|:---|:---|:---|:---|
| 10_observability | dashboard/ | `dashboard_truth_contract.md` | Dashboard truth principles | 9 | V2 is constitutional for dashboard |
| 10_observability | dashboard/ | `ui_guardrails.md` | Forbidden UI elements | 9 | V2 defines hard guardrails |
| 10_observability | dashboard/ | `alerting_rules.md` | Alert definitions | 8 | V2 defines operative alerting |
| 10_observability | dashboard/ | `temporal_truth_surface.md` | Temporal display rules | 8 | V2 defines temporal state badges |
| 10_observability | dashboard/ | `dashboard_binding_ledger.md` | Widget binding rules | 8 | V2 maintains the actual binding ledger |
| 10_observability | dashboard/ | `surface_catalog.md` | All dashboard surfaces | 8 | V2 has full surface catalog (28 files deep) |
| 10_observability | epistemic/ | `data_retention_policy.md` | Log retention | 8 | V2 governs retention operationally |
| 10_observability | dashboard/ | `stress_inspection_mode_contract.md` | Inspection mode behavior | 8 | V2 has detailed inspection mode spec |
| 10_observability | dashboard/ | `provenance_matrix.md` | Data provenance tracking | 8 | V2 maintains provenance matrix; V3 lacks this |

### Layer 11_deployment

| V3 Layer | V2 Folder | Specific File/Module | Responsibility Overlap | Depth in V2 (1–10) | Notes |
|:---|:---|:---|:---|:---|:---|
| 11_deployment | architecture/ | `DWBS.md` | Primary build/deployment system | 9 | V2 DWBS is the authoritative build specification |
| 11_deployment | epistemic/roadmap/ | `dwbs_post_freeze.md` | Post-freeze roadmap | 8 | V2 roadmap is operative plan |
| 11_deployment | governance/ | `MODULE_AUTHORITY_MATRIX.md` | Module classification | 8 | V2 is the operative authority matrix |
| 11_deployment | governance/ | `RESEARCH_MODULE_GOVERNANCE.md` | Research module lifecycle | 8 | V2 is the operative governance policy |
| 11_deployment | governance/ | `phase_lock_registry.md` | Phase lock tracking | 8 | V2 is the live phase lock registry |
| 11_deployment | governance/ | `truth_advancement_gates.md` | Truth epoch gates | 9 | V2 governs truth advancement operationally |

### Layer 12_orchestration

| V3 Layer | V2 Folder | Specific File/Module | Responsibility Overlap | Depth in V2 (1–10) | Notes |
|:---|:---|:---|:---|:---|:---|
| 12_orchestration | architecture/ | `DWBS.md` (orchestration sections) | Build orchestration sequence | 8 | V2 DWBS defines plane build order |
| 12_orchestration | docs/memory/ | `05_components/*.yaml` | Per-component retry/failure policies | 8 | V2 YAMLs are the operative component specs |
| 12_orchestration | contracts/ | `execution_harness_contract.md` | Task execution model | 9 | V2 is constitutional for task execution |
| 12_orchestration | epistemic/roadmap/ | `task_graph.md` | Task graph design | 8 | V2 defines task graph semantics |
| 12_orchestration | irr/ | `shadow_reality_run_log.md` | Shadow execution behavior | 7 | V2 contains observed shadow run behavior |

---

## SECTION 3 — COMPARATIVE DEPTH MATRIX

### Layer 00_vision

| Metric | V2 Score (1–10) | V3 Score (1–10) | Gap | Risk Level | Commentary |
|:---|:---:|:---:|:---:|:---:|:---|
| Contract Clarity | 7 | 2 | −5 | CRITICAL | V2 `project_intent.md` tightly bounds purpose to phase goals; V3 vision is pure aspiration |
| Schema Determinism | 5 | 1 | −4 | CRITICAL | V3 vision has no schema whatsoever; V2 DWBS at least binds to build artifacts |
| Epistemic Discipline | 8 | 2 | −6 | CRITICAL | V2 epistemic governance enforces discipline through invariants; V3 vision states philosophy only |
| Invariant Enforcement | 7 | 1 | −6 | CRITICAL | No invariants declared in V3 vision; V2 `architectural_invariants.md` has 9 binding invariants |
| Evaluation Rigor | 6 | 1 | −5 | CRITICAL | V3 vision cannot be evaluated against pass/fail criteria; V2 DWBS has plane completion gates |
| Data Lineage Traceability | 5 | 1 | −4 | HIGH | No lineage concept in vision; V2 lineage rules are separate and contractual |
| Regime Gating Explicitness | 6 | 1 | −5 | CRITICAL | Vision defines regime concept but no gating rules; V2 has explicit regime gate contracts |
| Memory Mutation Safety | 5 | 2 | −3 | HIGH | V3 vision has no mutation rules; v2 policies govern change |
| Dashboard Integration Readiness | 4 | 1 | −3 | HIGH | V3 vision not designed for dashboard integration; V2 dashboard has truth contracts |

### Layer 01_scope

| Metric | V2 Score (1–10) | V3 Score (1–10) | Gap | Risk Level | Commentary |
|:---|:---:|:---:|:---:|:---:|:---|
| Contract Clarity | 8 | 5 | −3 | HIGH | V3 scope has stated Three Worlds rules; V2 `layer_interaction_contract.md` has binding enforcement |
| Schema Determinism | 7 | 4 | −3 | HIGH | V3 scope has structured tables but no machine-readable schema; V2 contracts are schema-bound |
| Epistemic Discipline | 8 | 5 | −3 | HIGH | V3 scope cites V2 epistemic docs as sources; authority defers to V2 |
| Invariant Enforcement | 8 | 3 | −5 | CRITICAL | V3 states "MUST NOT" rules; no enforcement mechanism within this layer; V2 has gate enforcement |
| Evaluation Rigor | 7 | 5 | −2 | MEDIUM | V3 has quantified Research Exit Criteria (3 criteria); V2 has operational validation |
| Data Lineage Traceability | 6 | 3 | −3 | HIGH | V3 scope doesn't address lineage; V2 lineage rules are contract-level |
| Regime Gating Explicitness | 7 | 4 | −3 | HIGH | V3 scope mentions regime in in-scope list but no gating logic; V2 contracts gate regime explicitly |
| Memory Mutation Safety | 7 | 4 | −3 | HIGH | V3 scope defines "frozen"/"not current focus" items but no mutation protocol |
| Dashboard Integration Readiness | 6 | 4 | −2 | MEDIUM | V3 scope mentions dashboard as output; not wired to dashboard contract |

### Layer 02_success

| Metric | V2 Score (1–10) | V3 Score (1–10) | Gap | Risk Level | Commentary |
|:---|:---:|:---:|:---:|:---:|:---|
| Contract Clarity | 8 | 7 | −1 | LOW | V3 success has quantified thresholds and 4 embedded L3 invariants; close to V2 depth |
| Schema Determinism | 7 | 6 | −1 | LOW | V3 success criteria are structured with grading tables; slightly less formal than V2 schemas |
| Epistemic Discipline | 7 | 6 | −1 | LOW | V3 references V2 epistemic docs; L3 invariants formally declared |
| Invariant Enforcement | 7 | 6 | −1 | LOW | Four L3 invariants explicitly embedded with HARD FAILURE conditions; other layers lack this |
| Evaluation Rigor | 8 | 7 | −1 | LOW | V3 signal grading (A/B/C/D) with quantified criteria; V2 audits validate these operationally |
| Data Lineage Traceability | 6 | 4 | −2 | MEDIUM | Success metrics reference sources but no lineage chain to raw data |
| Regime Gating Explicitness | 7 | 6 | −1 | LOW | V3 success criteria include regime stability metric (≤5% false flip rate) |
| Memory Mutation Safety | 6 | 5 | −1 | LOW | Success criteria relatively frozen; appendix note indicates evolution via commit triggers |
| Dashboard Integration Readiness | 7 | 6 | −1 | LOW | Dashboard success criteria defined (latency, traceability, completeness, alert visibility) |

### Layer 03_domain

| Metric | V2 Score (1–10) | V3 Score (1–10) | Gap | Risk Level | Commentary |
|:---|:---:|:---:|:---:|:---:|:---|
| Contract Clarity | 8 | 8 | 0 | LOW | V3 domain entities are clearly defined; comparable to V2 policy docs per domain |
| Schema Determinism | 8 | 7 | −1 | LOW | V3 entity schemas have field names, types, enumerations; V2 policy docs slightly more formal |
| Epistemic Discipline | 8 | 8 | 0 | LOW | V3 domain is CANONICAL — all layers defer to it; equivalent epistemic authority |
| Invariant Enforcement | 7 | 5 | −2 | MEDIUM | V2 policy docs have role-specific enforcement rules; V3 domain model is definition-only |
| Evaluation Rigor | 7 | 6 | −1 | LOW | V3 domain defines evaluation criteria per entity; V2 policy docs have stricter enforcement |
| Data Lineage Traceability | 7 | 6 | −1 | LOW | V3 domain maps entities to layers; full lineage in V2 lineage contracts |
| Regime Gating Explicitness | 8 | 7 | −1 | LOW | V3 domain model shows regime as L1 gatekeeper with dependency graph |
| Memory Mutation Safety | 7 | 7 | 0 | LOW | V3 declares CANONICAL authority; mutation requires explicit conflict resolution |
| Dashboard Integration Readiness | 7 | 7 | 0 | LOW | V3 domain entities map to dashboard data objects naturally |

### Layer 04_architecture

| Metric | V2 Score (1–10) | V3 Score (1–10) | Gap | Risk Level | Commentary |
|:---|:---:|:---:|:---:|:---:|:---|
| Contract Clarity | 9 | 7 | −2 | MEDIUM | V3 has BAN rules and pipeline invariants; V2 `layer_interaction_contract.md` is constitutional |
| Schema Determinism | 8 | 7 | −1 | LOW | V3 data lifecycle stages well-defined; V2 schemas more formally typed |
| Epistemic Discipline | 8 | 8 | 0 | LOW | V3 explicitly references V2 as sources; conflict tracking via Resolved Conflicts log |
| Invariant Enforcement | 8 | 6 | −2 | MEDIUM | V3 BAN rules stated; enforcement code is in V2 execution harness (not V3) |
| Evaluation Rigor | 7 | 6 | −1 | LOW | V3 has Resolved Questions log; V2 has operational verification reports |
| Data Lineage Traceability | 8 | 8 | 0 | LOW | V3 data lifecycle (Bronze/Silver/Gold + Transient/Final) maps lineage explicitly |
| Regime Gating Explicitness | 8 | 7 | −1 | LOW | V3 shows regime as L1 supervisory gate; feedback only upward to DESIGN |
| Memory Mutation Safety | 8 | 7 | −1 | LOW | V3 data lifecycle immutability rules; V2 contracts more formally enforce |
| Dashboard Integration Readiness | 7 | 7 | 0 | LOW | V3 shows Dashboard as terminal output; pipeline wired through human operator |

### Layer 05_components

| Metric | V2 Score (1–10) | V3 Score (1–10) | Gap | Risk Level | Commentary |
|:---|:---:|:---:|:---:|:---:|:---|
| Contract Clarity | 7 | 9 | +2 | **IMPROVEMENT** | V3 health contract is a CANONICAL improvement; V2 had no universal health interface |
| Schema Determinism | 7 | 8 | +1 | **IMPROVEMENT** | V3 defines required YAML schema for health_contract, health_fields, health_invariants |
| Epistemic Discipline | 7 | 8 | +1 | **IMPROVEMENT** | V3 backed by reference implementation in `src/layers/macro_layer.py` |
| Invariant Enforcement | 7 | 8 | +1 | **IMPROVEMENT** | V3 health invariants are explicit: FAILED = Fail-Closed, recovery requirements stated |
| Evaluation Rigor | 7 | 8 | +1 | **IMPROVEMENT** | Tests cited (`tests/test_macro_layer.py`); canonical compliance measurable |
| Data Lineage Traceability | 6 | 7 | +1 | **IMPROVEMENT** | Health observability signals trace component states with timestamps |
| Regime Gating Explicitness | 6 | 7 | +1 | **IMPROVEMENT** | DEGRADED state explicitly includes "Upstream Degradation" as condition |
| Memory Mutation Safety | 6 | 7 | +1 | **IMPROVEMENT** | State transitions are one-directional with explicit recovery requirements |
| Dashboard Integration Readiness | 7 | 8 | +1 | **IMPROVEMENT** | Six observability signals defined (gauge, timestamp, counter, event, histogram) |

### Layer 06_data

| Metric | V2 Score (1–10) | V3 Score (1–10) | Gap | Risk Level | Commentary |
|:---|:---:|:---:|:---:|:---:|:---|
| Contract Clarity | 9 | 8 | −1 | LOW | V3 consolidates V2 contracts with cross-linking; V2 individual contracts remain authoritative source |
| Schema Determinism | 9 | 8 | −1 | LOW | V3 has 10 schemas with typed fields; V2 contracts have signature authority |
| Epistemic Discipline | 8 | 8 | 0 | LOW | V3 references V2 as legacy sources; temporal invariant cross-referenced to V2 governance contract |
| Invariant Enforcement | 8 | 8 | 0 | LOW | Temporal invariant (`TE ≤ CTT ≤ RDT`) explicitly stated with CORRUPT state detection |
| Evaluation Rigor | 8 | 7 | −1 | LOW | V3 has coverage gap tracking; V2 gap register is the live operational document |
| Data Lineage Traceability | 9 | 8 | −1 | LOW | V3 has four lineage rules; V2 `RAW_DATA_LINEAGE_RULES.md` is the authoritative contract |
| Regime Gating Explicitness | 8 | 8 | 0 | LOW | V3 defines Regime Input Contract with BLOCKING symbols and `NOT_VIABLE` failure mode |
| Memory Mutation Safety | 9 | 8 | −1 | LOW | V3 deletion protocol requires human approval; V2 retention policy governs operationally |
| Dashboard Integration Readiness | 8 | 8 | 0 | LOW | V3 defines read-only Dashboard API contract with 7 endpoints and invariants |

### Layer 07_execution

| Metric | V2 Score (1–10) | V3 Score (1–10) | Gap | Risk Level | Commentary |
|:---|:---:|:---:|:---:|:---:|:---|
| Contract Clarity | 10 | 8 | −2 | MEDIUM | V2 `execution_harness_contract.md` is "Constitutional — Binding"; V3 declares "intent only" |
| Schema Determinism | 9 | 8 | −1 | LOW | V3 harness state machine, task outcomes, precondition checks all formally structured |
| Epistemic Discipline | 9 | 8 | −1 | LOW | V3 explicitly references V2 contract; "intent" vs "binding" distinction creates authority gap |
| Invariant Enforcement | 9 | 8 | −1 | LOW | V3 9 cross-pipeline invariants stated; V2 contract enforces them programmatically |
| Evaluation Rigor | 8 | 7 | −1 | LOW | V3 has gate pass/fail criteria; V2 has operational verification |
| Data Lineage Traceability | 8 | 8 | 0 | LOW | V3 truth epoch gates with explicit CTT tracking |
| Regime Gating Explicitness | 9 | 8 | −1 | LOW | V3 Gate 2 requires regime health check; V2 contract enforces this as prerequisite |
| Memory Mutation Safety | 9 | 8 | −1 | LOW | V3 audit append-only invariant; TE never auto-advances |
| Dashboard Integration Readiness | 8 | 7 | −1 | LOW | V3 dashboard runtime contract (read-only, SHADOW vs ENFORCED visible) |

### Layer 08_reliability

| Metric | V2 Score (1–10) | V3 Score (1–10) | Gap | Risk Level | Commentary |
|:---|:---:|:---:|:---:|:---:|:---|
| Contract Clarity | 9 | 8 | −1 | LOW | V3 synthesizes V2 failure audit reports; IRR taxonomy is cleaner than V2's scattered docs |
| Schema Determinism | 8 | 8 | 0 | LOW | V3 has structured failure tables with detection, degradation, response for every component |
| Epistemic Discipline | 8 | 9 | +1 | **IMPROVEMENT** | V3 IRR failure taxonomy (F1–F5 with P-levels) adds formal classification not in any V2 doc |
| Invariant Enforcement | 8 | 8 | 0 | LOW | V3 has explicit obligation enforcement (OBL-RG-ING-ENFORCEMENT table) |
| Evaluation Rigor | 8 | 8 | 0 | LOW | V3 component failure summary table cross-references all 15 components |
| Data Lineage Traceability | 7 | 7 | 0 | LOW | V3 temporal failure states (RDT/CTT/TE drift) traced explicitly |
| Regime Gating Explicitness | 8 | 8 | 0 | LOW | V3 regime ingestion obligations table prevents silent failures |
| Memory Mutation Safety | 8 | 8 | 0 | LOW | V3 hallucination controls (6) for narrative; no silent interpolation |
| Dashboard Integration Readiness | 8 | 8 | 0 | LOW | V3 dashboard/UI failures section with hard guardrails |

### Layer 09_security

| Metric | V2 Score (1–10) | V3 Score (1–10) | Gap | Risk Level | Commentary |
|:---|:---:|:---:|:---:|:---:|:---|
| Contract Clarity | 9 | 8 | −1 | LOW | V3 has 7 ABSOLUTE invariants; V2 `architectural_invariants.md` is the authoritative binding list |
| Schema Determinism | 8 | 8 | 0 | LOW | V3 trust domain tables, layer authority matrix, skill authority hierarchy all structured |
| Epistemic Discipline | 9 | 8 | −1 | LOW | V3 cites V2 sources; V2 capital and epistemic docs are the operative security enforcement |
| Invariant Enforcement | 9 | 8 | −1 | LOW | V3 7 ABSOLUTE invariants; V2 `architectural_invariants.md` enforces 9 binding invariants |
| Evaluation Rigor | 8 | 8 | 0 | LOW | V3 module promotion 5-gate process; V2 governance policies test these operationally |
| Data Lineage Traceability | 7 | 7 | 0 | LOW | V3 trust data model (Bronze=UNTRUSTED → Silver=TRUSTED → Gold=CONDITIONAL) |
| Regime Gating Explicitness | 8 | 7 | −1 | LOW | V3 kill-switch triggers regime-sensitive; V2 capital docs specify exact trigger conditions |
| Memory Mutation Safety | 9 | 8 | −1 | LOW | V3 append-only ledger, no self-activation; V2 capital governance enforces operationally |
| Dashboard Integration Readiness | 8 | 8 | 0 | LOW | V3 defines chat execution contract, observatory principle; dashboard read-only invariant |

### Layer 10_observability

| Metric | V2 Score (1–10) | V3 Score (1–10) | Gap | Risk Level | Commentary |
|:---|:---:|:---:|:---:|:---:|:---|
| Contract Clarity | 9 | 7 | −2 | MEDIUM | V2 `dashboard_truth_contract.md` is constitutional; V3 intent layer misses granular V2 widgets |
| Schema Determinism | 8 | 7 | −1 | LOW | V3 has metric categories; V2 has 28-file dashboard specification with provenance matrix |
| Epistemic Discipline | 8 | 7 | −1 | LOW | V3 references V2 dashboard docs; V2 remains operative for specific surface specifications |
| Invariant Enforcement | 9 | 7 | −2 | MEDIUM | V2 `ui_guardrails.md` has hard guardrails (INV-NO-EXECUTION etc.); V3 lists them but V2 enforces |
| Evaluation Rigor | 8 | 7 | −1 | LOW | V3 observability success criteria (6); V2 audits validate these against real dashboard state |
| Data Lineage Traceability | 8 | 7 | −1 | LOW | V3 widget binding rules require trace badges; V2 `provenance_matrix.md` maintains actual matrix |
| Regime Gating Explicitness | 8 | 7 | −1 | LOW | V3 regime state panel defined; V2 `regime_visibility_rules.md` and `staleness_and_honesty_checks.md` have detail |
| Memory Mutation Safety | 8 | 7 | −1 | LOW | V3 log retention rules; V2 operative retention policy governs |
| Dashboard Integration Readiness | 9 | 8 | −1 | LOW | V3 9 dashboard panels with data sources; V2 has complete wiring specification |

### Layer 11_deployment

| Metric | V2 Score (1–10) | V3 Score (1–10) | Gap | Risk Level | Commentary |
|:---|:---:|:---:|:---:|:---:|:---|
| Contract Clarity | 9 | 8 | −1 | LOW | V3 has phase locks, promotion gates, evolution rules; V2 `DWBS.md` is the operative build spec |
| Schema Determinism | 8 | 8 | 0 | LOW | V3 phase status tables, migration matrix, anti-patterns all formally structured |
| Epistemic Discipline | 9 | 8 | −1 | LOW | V3 cites V2 DWBS and governance as sources; V2 remains operative |
| Invariant Enforcement | 8 | 8 | 0 | LOW | V3 lock-breaking protocol (5-step); One-Skill-at-a-Time rule; anti-patterns explicitly listed |
| Evaluation Rigor | 8 | 8 | 0 | LOW | V3 Phase Exit Criteria (6 quantified criteria); historical phase completion record maintained |
| Data Lineage Traceability | 7 | 7 | 0 | LOW | V3 module migration tracking (completed + pending migrations) |
| Regime Gating Explicitness | 7 | 7 | 0 | LOW | V3 blocked items list (Execution Plane permanently blocked) |
| Memory Mutation Safety | 8 | 8 | 0 | LOW | V3 Freeze Discipline principle; FROZEN by default; Phase Lock system operational |
| Dashboard Integration Readiness | 7 | 7 | 0 | LOW | V3 runtime component table with ports; dashboard port 5173 explicitly declared |

### Layer 12_orchestration

| Metric | V2 Score (1–10) | V3 Score (1–10) | Gap | Risk Level | Commentary |
|:---|:---:|:---:|:---:|:---:|:---|
| Contract Clarity | 8 | 7 | −1 | LOW | V3 retry table with 18 components and explicit fail behaviors; V2 YAMLs are operative source |
| Schema Determinism | 8 | 7 | −1 | LOW | V3 retry policy table is structured; V2 component YAMLs have more detailed failure_modes |
| Epistemic Discipline | 8 | 7 | −1 | LOW | V3 has 3 OPEN_QUESTIONs honestly flagged; V2 YAMLs are operative contracts |
| Invariant Enforcement | 8 | 7 | −1 | LOW | V3 phase gating rules stated; enforcement is in execution harness (V2 contract) |
| Evaluation Rigor | 7 | 7 | 0 | LOW | V3 shadow promotion criteria linked to 02_success; V2 shadow logs validate |
| Data Lineage Traceability | 7 | 7 | 0 | LOW | V3 retry policy includes data pipeline components (US/India ingestion) |
| Regime Gating Explicitness | 7 | 7 | 0 | LOW | V3 Phase 1 requires Regime Engine before Narrative Engine explicitly |
| Memory Mutation Safety | 7 | 7 | 0 | LOW | V3 shadow scope table prevents premature production output |
| Dashboard Integration Readiness | 7 | 7 | 0 | LOW | V3 Phase 6 Dashboard is terminal phase with explicit gating rules |

---

## SECTION 4 — CONTRACT DRIFT ANALYSIS

| Issue | V3 Layer | Type | Description |
|:---|:---|:---|:---|
| Vision has no formal contracts | 00_vision | CONTRACT LOSS | V3 vision layer declares philosophy without any binding contracts. Anti-patterns are aspirational. V2 `project_intent.md` tightly binds purpose to phase-level governance. |
| Vision hierarchy not schema-bound | 00_vision | CONTRACT LOSS | V3 defines 13-level cognitive hierarchy as narrative. V2 `architectural_invariants.md` and `layer_interaction_contract.md` bind hierarchy to enforceable ordering rules. V3 vision does not reference these invariants. |
| Vision anti-patterns not enforced | 00_vision | CONTRACT LOSS | V3 lists 4 anti-patterns but has no mechanism to detect or block violations. V2 `epistemic_drift_validator_specification.md` and `cognitive_order_validator.md` (skill) operationalize anti-pattern detection. |
| Scope Three Worlds rules stated only | 01_scope | CONTRACT DRIFT | V3 states "Vision items MUST NOT leak into Production" but has no enforcement. V2 governance, phase locks, and import barriers provide actual enforcement. Scope layer is an intent declaration over an operative V2 enforcement system. |
| Scope exit criteria not machine-gated | 01_scope | CONTRACT DRIFT | V3 Research Exit Criteria (3 criteria) are defined in prose. V2 `current_phase.md` and truth advancement gates operationalize these as governance checkpoints. V3 does not wire to these gates. |
| Scope user profile lacks binding | 01_scope | CONTRACT LOSS | V3 states "≤₹1 Cr" capital profile and "Human always decides." V2 `capital/risk_envelopes.md` and `capital/kill_switch.md` operationalize capital constraints. V3 scope has no reference to these enforcement mechanisms. |
| Success invariants only for L3 | 02_success | CONTRACT DRIFT | V3 success layer has 4 formal invariants for L3 Meta-Analysis. Other layers (L1, L6–L7, L8–L9) have quantified criteria but no embedded invariant enforcement. Creates asymmetric rigor. |
| Phase exit criteria not gated in layer | 02_success | CONTRACT DRIFT | V3 Phase Exit Criteria are stated in 02_success but the actual gate mechanism is in `governance/truth_advancement_gates.md` (V2). V3 success layer performs no gate checking itself. |
| Test invariants embedded in success doc | 02_success | CONTRACT DUPLICATION | Two commit-trigger test invariants embedded in success_criteria.md are testing scaffolding, not system success criteria. Contaminates the canonical success definition. |
| Domain model CANONICAL — no enforcement chain | 03_domain | CONTRACT DRIFT | V3 03_domain declares itself CANONICAL but defines no mechanism by which violations are detected. V2 epistemic policy docs have enforcement logic; V3 domain model does not. |
| Domain entity schemas lack validation rules | 03_domain | CONTRACT LOSS | V3 domain entities have field names but no schema validation rules (range checks, required fields, null handling). V2 `epistemic/belief_layer_policy.md` and `factor_layer_policy.md` have enforcement-level policy. |
| Architecture BAN rules not self-enforcing | 04_architecture | CONTRACT DRIFT | V3 declares BAN-1 through BAN-4 but these are enforced in V2 `execution_harness_contract.md` (Harness Prohibitions) and `layer_interaction_contract.md`. Dual source of truth for identical rules creates maintenance risk. |
| Resolved Conflict log improves over V2 | 04_architecture | CONTRACT IMPROVEMENT | V3 04_architecture maintains explicit Resolved Conflicts (RC-4, RC-5, RC-6) and Resolved Questions (RQ-5, RQ-6, RQ-7). V2 had no equivalent single-document conflict tracking. |
| Component health contract — genuine V3 addition | 05_components | CONTRACT IMPROVEMENT | V3 05_components introduces a universal health interface (OK/DEGRADED/FAILED state machine with 6 observability signals). V2 had no equivalent universal health contract. This is a net new bounded contract. |
| Component health backed by implementation | 05_components | CONTRACT IMPROVEMENT | V3 health contract cites reference implementation (`src/layers/macro_layer.py`) and tests (`tests/test_macro_layer.py`). This is stronger than most V3 contracts. |
| Data layer consolidation adds cross-linking | 06_data | CONTRACT IMPROVEMENT | V3 06_data cross-links schemas to domain entities, proxies to layer dependencies, retention categories to entity types. V2 had separate contracts with no cross-mapping. |
| Temporal invariant strength maintained | 06_data | CONTRACT IMPROVEMENT | V3 temporal truth model (RDT/CTT/TE planes, five temporal states, CORRUPT detection) is as rigorous as V2 `governance/temporal_truth_contract.md` and adds explicit state names. |
| Authority ambiguity: intent vs. binding | 07_execution | CONTRACT DRIFT | V3 07_execution declares "Intent only. No implementation." V2 `execution_harness_contract.md` is "Constitutional — Binding." Both documents contain identical rules (e.g., harness prohibitions). Consumers reading only V3 may not realize V2 is the operative constraint. |
| Skill lifecycle defined in V3 | 07_execution | CONTRACT IMPROVEMENT | V3 defines skill lifecycle (REGISTERED → ACTIVE → DEPRECATED → REMOVED) with explicit violation handling table. This is cleaner and more formal than V2's scattered skill registration documentation. |
| IRR failure taxonomy — V3 synthesis | 08_reliability | CONTRACT IMPROVEMENT | V3 formalizes 5 IRR failure classes (F1–F5) with P-level priorities (P0/P1/P2). V2 had separate implementation reports per failure class. V3 synthesis creates a unified failure taxonomy not present in any V2 document. |
| Degraded state authorization in both systems | 08_reliability | CONTRACT DUPLICATION | DEG-IN-001 and DEG-US-001 are defined in V3 08_reliability AND in V2 `data/degraded_state_registry.md`. Two sources for degraded state authorization; synchronization risk if either is updated without the other. |
| Narrative adapter gap honestly flagged | 08_reliability | CONTRACT IMPROVEMENT | V3 explicitly flags `Narrative Engine includes "Regime adapter NOT_WIRED"` in retry_policy.md. This gap was not formally classified in V2. |
| 7 ABSOLUTE invariants — slight undercount | 09_security | CONTRACT DRIFT | V3 lists 7 ABSOLUTE invariants. V2 `epistemic/architectural_invariants.md` lists 9 architectural invariants with broader scope (also covering "No Lookahead", "Immutability of Raw Data"). V3 security invariants subsume some but not all V2 architectural invariants. |
| Chat execution contract well-modeled | 09_security | CONTRACT IMPROVEMENT | V3 defines the chat execution contract (6 rules) as a security concern. V2 had this in `epistemic/chat_execution_contract.md` without the security framing. V3 correctly elevates it. |
| Dashboard forbidden semantics list complete | 10_observability | CONTRACT IMPROVEMENT | V3 forbidden semantics list (8 items) is more complete and better organized than V2's `ui_guardrails.md`. Clarity improvement for dashboard implementers. |
| V3 observability misses V2 provenance matrix | 10_observability | CONTRACT LOSS | V3 10_observability defines provenance requirement (trace badges) but V2 maintains an actual `dashboard/provenance_matrix.md`. V3 does not reference or consolidate this specific artifact. Missing lineage to operative provenance tracking. |
| V3 misses stress inspection mode detail | 10_observability | CONTRACT LOSS | V3 mentions Inspection Mode badge but V2 has `dashboard/stress_inspection_mode_contract.md` (full contract). V3 does not consolidate this contract, creating an observability gap for stress-mode behavior. |
| Phase lock system — V3 strong addition | 11_deployment | CONTRACT IMPROVEMENT | V3 formally classifies locked artifacts (`CON-001`, `CON-002`, `CON-003 NEVER`) vs mutable registries. Lock-breaking protocol (5-step) is more formally stated than V2's scattered governance docs. |
| Anti-patterns table comprehensive | 11_deployment | CONTRACT IMPROVEMENT | V3 10-item anti-patterns table is more organized and complete than V2's DWBS anti-pattern references. Useful for code review and onboarding. |
| OPEN_QUESTIONs honestly declared | 12_orchestration | CONTRACT IMPROVEMENT | V3 12_orchestration explicitly flags 3 OPEN_QUESTIONs (governance shadow enforcement mode, Meta-Analysis upstream source conflict, Narrative Engine adapter gap). V2 had these as implicit gaps. Transparency improvement. |
| Governance enforcement in shadow not specified | 12_orchestration | CONTRACT DRIFT | V3 12_orchestration flags that "Governance enforcement mode in shadow is not explicitly specified." This is an unresolved contract gap that V2 does not fully resolve either. Affects shadow mode correctness. |

---

## SECTION 5 — REDUNDANCY & STRUCTURAL COLLISION

### Layer 00_vision

| Redundant With | Level | Semantic Overlap |
|:---|:---:|:---|
| `epistemic/project_intent.md` | PARTIAL | Both declare system purpose; V2 is more operationally grounded |
| `architecture/DWBS.md` (preamble) | PARTIAL | Both define system philosophy; V2 DWBS binds philosophy to build sequence |
| `docs/VISION_BACKLOG.md` | HIGH | Both define Three Worlds, vision items, anti-patterns; V3 is the intended consolidation |
| `epistemic/structure_stack_vision.md` | PARTIAL | Both explore structural vision; V2 is more loosely scoped |

**HIGH Redundancy Details (00_vision vs VISION_BACKLOG.md)**: Both documents declare the Three Worlds (Production/Research/Vision), anti-patterns, and future phases gated by system maturity. V3 vision is intended to be the canonical consolidation of VISION_BACKLOG but has not eliminated the V2 document, creating dual maintenance risk for the Three Worlds concept.

---

### Layer 01_scope

| Redundant With | Level | Semantic Overlap |
|:---|:---:|:---|
| `epistemic/current_phase.md` | HIGH | Current in-scope items, phase state, exit criteria — near-identical semantic content |
| `contracts/layer_interaction_contract.md` | PARTIAL | Scope layer defines layer boundaries; V2 contract enforces them |
| `architecture/DWBS.md` | PARTIAL | Build scope partially overlaps; V2 DWBS is the authoritative build specification |
| `epistemic/latent_structural_layers.md` | PARTIAL | Out-of-scope latent layers defined in both contexts |

**HIGH Redundancy Details (01_scope vs current_phase.md)**: `current_phase.md` defines exactly what is in scope for the current phase (Research & Validation), the exit criteria, and what is out of scope — the same content as V3 01_scope. V3 scope explicitly cites `current_phase.md` as source, meaning V3 is a consolidation wrapper. If `current_phase.md` advances to the next phase and V3 scope is not updated, they diverge.

---

### Layer 02_success

| Redundant With | Level | Semantic Overlap |
|:---|:---:|:---|
| `epistemic/current_phase.md` | HIGH | Phase exit criteria appear in both; V2 is the operative governance document |
| `audit/full_system_audit.md` | PARTIAL | V2 audit evaluates success criteria operationally against real runs |
| `diagnostics/regime_observability_summary.md` | PARTIAL | Regime success metrics overlap with V2 regime diagnostics |

**HIGH Redundancy Details (02_success vs current_phase.md)**: Phase Exit Criteria (shadow mode stability, signal quality, idempotency, regime robustness) are defined in both V3 02_success and V2 `epistemic/current_phase.md`. V3 cites V2 as source, but the quantified thresholds are duplicated. The authoritative gate mechanism lives in V2 truth advancement. If thresholds are updated in V2, V3 may silently drift.

---

### Layer 03_domain

| Redundant With | Level | Semantic Overlap |
|:---|:---:|:---|
| `epistemic/belief_layer_policy.md` | PARTIAL | Belief entity definitions; V2 has role-specific enforcement |
| `epistemic/factor_layer_policy.md` | PARTIAL | Factor entity definitions; V2 has permission enforcement |
| `epistemic/strategy_layer_policy.md` | PARTIAL | Strategy entity definitions; V2 has lifecycle rules |
| `architecture/DWBS_SYSTEM_LANDSCAPE.md` | PARTIAL | Component map; V2 describes components in build context |

**Note**: V3 03_domain is the INTENTIONAL consolidation of scattered V2 entity definitions. Redundancy is architectural by design. The key risk is not the overlap but the enforcement gap — V3 consolidates definitions while V2 holds enforcement logic.

---

### Layer 04_architecture

| Redundant With | Level | Semantic Overlap |
|:---|:---:|:---|
| `contracts/layer_interaction_contract.md` | HIGH | BAN rules and communication model are near-identical; V2 is constitutional |
| `architecture/DWBS.md` | HIGH | Pipeline architecture, build sequence; V2 is the authoritative spec |
| `docs/us_market_engine_design.md` | PARTIAL | US pipeline detail; V2 has more operational specifics |
| `docs/INDIA_WEBSOCKET_ARCHITECTURE.md` | PARTIAL | India pipeline detail; V2 has more operational specifics |

**HIGH Redundancy Details**: BAN-1 through BAN-4 appear in V3 04_architecture. The identical prohibitions appear as "Harness Prohibitions" in V2 `execution_harness_contract.md`. Two specifications of the same prohibitions creates synchronization risk. V3 frames them as architecture (design rule); V2 as contract enforcement (runtime rule).

---

### Layer 05_components

| Redundant With | Level | Semantic Overlap |
|:---|:---:|:---|
| `docs/memory/05_components/*.yaml` | PARTIAL | Component health fields overlap with per-component failure_modes |
| `epistemic/skills_catalog.md` | PARTIAL | Component/skill capabilities overlap conceptually |

**NONE for universal health contract**: V2 has no equivalent universal health interface. V3 05_components is not redundant with any single V2 document — it's a genuine addition. The PARTIAL redundancy with component YAMLs is additive, not duplicative.

---

### Layer 06_data

| Redundant With | Level | Semantic Overlap |
|:---|:---:|:---|
| `contracts/RAW_ANGEL_INTRADAY_SCHEMA.md` | HIGH | India raw schema consolidated; V2 contract is authoritative source |
| `contracts/market_proxy_sets.md` | HIGH | Proxy set definitions consolidated; V2 locked contract |
| `contracts/RAW_DATA_LINEAGE_RULES.md` | HIGH | Lineage rules consolidated; V2 is authoritative |
| `governance/temporal_truth_contract.md` | HIGH | Temporal truth model consolidated; V2 `CON-003 NEVER` |
| `epistemic/data_retention_policy.md` | HIGH | Retention policy consolidated; V2 is operative |

**HIGH Redundancy Details**: V3 06_data is an intentional consolidation of 9+ V2 source contracts into one reference document. The redundancy is architectural: V3 is the summary reference; V2 contracts are the operative sources. Risk occurs if V2 contracts are updated and V3 is not — the consolidation becomes stale. No synchronization mechanism exists.

---

### Layer 07_execution

| Redundant With | Level | Semantic Overlap |
|:---|:---:|:---|
| `contracts/execution_harness_contract.md` | HIGH | Harness model, prohibitions, task graph; V2 is Constitutional |
| `epistemic/bounded_automation_contract.md` | HIGH | Automation limits; V2 is the operative contract |
| `governance/truth_advancement_gates.md` | HIGH | Gate protocols; V2 is the operative governance doc |

**HIGH Redundancy Details**: V3 07_execution and V2 `execution_harness_contract.md` have near-identical content for the Harness Responsibilities, Task Graph Model, and Prohibitions sections. The critical difference is V2 is labeled "Constitutional — Binding" while V3 is "Intent only." Both documents will need to be maintained in sync permanently unless one is deprecated.

---

### Layer 08_reliability

| Redundant With | Level | Semantic Overlap |
|:---|:---:|:---|
| `contracts/fragility_policy_contract.md` | HIGH | Circuit breaker policy; V2 is constitutional |
| `contracts/decision_policy_contract.md` | HIGH | Decision circuit breaker; V2 is constitutional |
| `data/degraded_state_registry.md` | HIGH | Degraded state registry; dual maintenance risk |
| `audit/` (multiple) | PARTIAL | Individual failure reports consolidated; V2 has root cause detail |

**HIGH Redundancy Note**: Degraded states DEG-IN-001 and DEG-US-001 exist in both V3 08_reliability and V2 `data/degraded_state_registry.md`. If a new degraded state is authorized, it must be added to both documents. No synchronization protocol exists.

---

### Layer 09_security

| Redundant With | Level | Semantic Overlap |
|:---|:---:|:---|
| `epistemic/architectural_invariants.md` | HIGH | Safety invariants; V2 has 9 binding invariants; V3 has 7 |
| `capital/kill_switch.md` | HIGH | Kill-switch governance; V2 is the operative kill-switch contract |
| `epistemic/bounded_automation_contract.md` | HIGH | Automation security limits; V2 is operative |

**HIGH Redundancy — Invariant Count Mismatch**: V2 `architectural_invariants.md` declares 9 architectural invariants. V3 09_security declares 7 ABSOLUTE invariants. The sets are not identical — V2 includes "No Lookahead" and "Immutability of Raw Data" which V3 does not. V3 includes `INV-PROXY-CANONICAL` and `INV-HONEST-STAGNATION` which V2 does not. Neither set is a superset of the other, creating potential invariant coverage gaps.

---

### Layer 10_observability

| Redundant With | Level | Semantic Overlap |
|:---|:---:|:---|
| `dashboard/dashboard_truth_contract.md` | HIGH | Dashboard principles; V2 is constitutional |
| `dashboard/ui_guardrails.md` | HIGH | Hard guardrails; V2 is operative |
| `dashboard/alerting_rules.md` | HIGH | Alert definitions; V2 is operative |
| `dashboard/` (all 28 files) | PARTIAL | Dashboard surfaces consolidated at summary level |

**HIGH Redundancy Details**: V2 dashboard folder has 28 specification files vs. V3 10_observability's single layer. V3 correctly consolidates the principles and key rules. However, V2 `provenance_matrix.md`, `stress_inspection_mode_contract.md`, `regime_visibility_rules.md`, `staleness_and_honesty_checks.md`, and `diagnostic_timeline_spec.md` contain detail not captured in V3. The V2-to-V3 consolidation is partial (estimated 60–70% coverage of V2 dashboard depth).

---

### Layer 11_deployment

| Redundant With | Level | Semantic Overlap |
|:---|:---:|:---|
| `architecture/DWBS.md` | HIGH | Build system, planes, anti-patterns; V2 is the authoritative DWBS |
| `epistemic/roadmap/dwbs_post_freeze.md` | HIGH | Post-freeze roadmap; V2 is the operative roadmap |
| `governance/MODULE_AUTHORITY_MATRIX.md` | HIGH | Module classification; V2 is operative |
| `governance/phase_lock_registry.md` | HIGH | Phase locks; V2 registry is the live tracking document |

**HIGH Redundancy Details**: V3 11_deployment summarizes the DWBS build history (Planes 1–7 status table) and phase lock categorization. V2 `DWBS.md` remains the authoritative specification with full plane engineering details. Both need to be maintained in sync for phase completions, new planes, and anti-pattern additions.

---

### Layer 12_orchestration

| Redundant With | Level | Semantic Overlap |
|:---|:---:|:---|
| `docs/memory/05_components/*.yaml` | HIGH | Retry policies consolidated from component YAMLs |
| `contracts/execution_harness_contract.md` | PARTIAL | Task execution model |
| `architecture/DWBS.md` | PARTIAL | Build orchestration sequence |

**HIGH Redundancy Details**: V3 retry policy table (18 components) consolidates retry_policy sections from individual component YAMLs. V2 YAMLs remain the source-of-truth for failure_modes detail. If a component YAML is updated with new retry behavior, V3 retry_policy.md must also be updated. No synchronization mechanism exists.

---

## SECTION 6 — STABILITY ASSESSMENT (V3 Layers)

| V3 Layer | Stability Score (0–10) | Blocking Issues | Critical Weakness |
|:---|:---:|:---|:---|
| **00_vision** | 4 | No contracts at all; depends on downstream layers correctly interpreting philosophy | Purely narrative; anti-patterns stated but not enforced. Any downstream layer can drift from vision silently. |
| **01_scope** | 6 | Three Worlds enforcement lives in V2 governance, not in this layer | Scope drift risk: if V2 `current_phase.md` advances to next phase, V3 scope is not automatically updated. Phase-sensitive scope will become stale. |
| **02_success** | 7 | L3 has 4 invariants; other cognitive layers (L1, L6–L9) have quantified thresholds only — no embedded invariants | Test invariants embedded in success document contaminate canonical success definition. Phase exit criteria not machine-gated within V3 layer. |
| **03_domain** | 8 | No enforcement chain for CANONICAL declaration | Domain model is well structured but "CANONICAL" authority has no violation detection. If a layer contradicts the domain model, no automated detection occurs. |
| **04_architecture** | 7 | BAN rules duplicated in V3 and V2 contracts; dual maintenance | Long document with many sub-topics increases surface area for stale sub-sections. Conflict log (RC/RQ tracking) is a strength. |
| **05_components** | 8 | Requires all component YAMLs to declare `health_contract` field | Reference implementation cited but only for `MacroLayer`. Other components may not have implemented the health interface. Compliance verification not systematic. |
| **06_data** | 8 | Temporal invariant strong but CoverageGap sections must stay in sync with V2 live gap register | 10 schemas consolidated from V2 contracts. If V2 contracts update, V3 data layer may become stale without a trigger notification. |
| **07_execution** | 8 | "Intent only" declaration creates authority gap vs V2 "Constitutional – Binding" | If developers read V3 as the execution specification, they may not consult V2 contract which has the binding authority. Authority confusion risk. |
| **08_reliability** | 8 | Degraded state registry defined in two locations | IRR failure taxonomy (F1–F5) adds genuine value. Main weakness: `Narrative Engine Regime adapter NOT_WIRED` is flagged as OPEN_QUESTION in V2 and not resolved. |
| **09_security** | 8 | Invariant set (7 V3 vs 9 V2) creates partial coverage | Kill-switch hierarchy well-defined. Main weakness: "no automated resets" is stated in V3 but the enforcement mechanism is in V2 `capital/kill_switch.md`. |
| **10_observability** | 7 | V2 dashboard folder (28 files) not fully consolidated; provenance matrix missing | "In progress" items noted (structured logging, dashboard completeness). V3 observability is a summary layer, not the full specification. |
| **11_deployment** | 8 | V2 `DWBS.md` remains the authoritative deployment specification; V3 is a consolidation | Strong freeze discipline. Anti-patterns table comprehensive. Main risk: if DWBS adds a new plane, V3 11_deployment must be manually updated. |
| **12_orchestration** | 7 | 3 OPEN_QUESTIONs unresolved; governance in shadow mode not specified | Retry policy table is a good consolidation. Shadow mode governance is an active contract gap. Narrative adapter gap affects Phase 1 orchestration correctness. |

---

## SECTION 7 — MIGRATION STRATEGY DECISION

| V3 Layer | Recommended Action | Justification |
|:---|:---|:---|
| **00_vision** | REINFORCE WITH V2 CONTRACTS | Vision layer must be explicitly linked to V2 `epistemic/architectural_invariants.md` and `contracts/layer_interaction_contract.md`. Add a "Binding Contracts" section that names the V2 enforcement documents for each anti-pattern. The layer remains aspirational but must not float free of operative constraints. |
| **01_scope** | WRAP V2 LOGIC VIA ADAPTER | V3 scope is an intent layer over V2 `epistemic/current_phase.md`. Add explicit adapter declaration: "Scope enforcement is delegated to V2 governance gates (see truth_advancement_gates.md)." Create a synchronization trigger: when `current_phase.md` version changes, V3 01_scope must be reviewed. |
| **02_success** | REINFORCE WITH V2 CONTRACTS | Strongest of the foundational layers. Extend L3 invariant pattern to other cognitive layers (L1, L6, L8–L9). Remove test invariants (TEST_ROUTER, commit trigger T2, T4) to a separate testing contract. Link phase exit criteria to V2 gate documents. |
| **03_domain** | KEEP V3 AS-IS | V3 domain model is a genuine consolidation improvement over V2's scattered entity definitions. It correctly declares CANONICAL authority. Reinforce by adding a "Violation Detection" reference pointing to V2 `epistemic/cognitive_order_validator.md` skill. |
| **04_architecture** | WRAP V2 LOGIC VIA ADAPTER | V3 correctly identifies V2 as source via Legacy Source Mapping. Formalize the adapter relationship: BAN rules should reference V2 contract section numbers. Mark V3 BAN rules as "Design Declaration" vs V2 "Runtime Enforcement" to eliminate authority confusion. |
| **05_components** | KEEP V3 AS-IS | V3 component health contract is an architectural improvement with no V2 equivalent. Extend by: (1) auditing all component YAMLs for health_contract field compliance, (2) adding a YAML compliance checklist. This is a V3 strength that should be back-ported awareness into V2 operational audits. |
| **06_data** | WRAP V2 LOGIC VIA ADAPTER | V3 data layer consolidates V2 contracts. Add explicit version locking: each V2 contract reference should include the version/date last validated against V3. Three locked V2 contracts (`CON-001`, `CON-002`, `CON-003 NEVER`) must be explicitly flagged in V3 as immutable external dependencies. |
| **07_execution** | WRAP V2 LOGIC VIA ADAPTER | V3 execution layer must resolve the "intent vs. constitutional" authority ambiguity. Add a prominent notice: "Runtime authority is `docs/contracts/execution_harness_contract.md` (Constitutional — Binding). This document is the reference summary." Add section-by-section cross-references to the V2 contract. |
| **08_reliability** | KEEP V3 AS-IS | V3 reliability layer provides the best synthesis in the V3 memory system. IRR taxonomy adds genuine value. ONLY change needed: resolve the degraded state registry duplication by declaring V2 `data/degraded_state_registry.md` as the live registry and V3 as the summary with a "last synced" timestamp. |
| **09_security** | REINFORCE WITH V2 CONTRACTS | Reconcile invariant sets: V3 has 7, V2 has 9. Conduct an invariant reconciliation audit and maintain a unified invariant list with provenance. Add V2 `capital/kill_switch.md` as explicit enforcement reference for kill-switch invariant. |
| **10_observability** | REFACTOR V3 USING V2 DEPTH | V3 10_observability does not fully consolidate V2 dashboard folder (28 files). Missing: `provenance_matrix.md`, `stress_inspection_mode_contract.md`, `regime_visibility_rules.md`, `staleness_and_honesty_checks.md`. Extend V3 to reference these V2 artifacts explicitly or restructure V3 to link to the V2 dashboard folder as the specification layer. |
| **11_deployment** | WRAP V2 LOGIC VIA ADAPTER | V3 is a good consolidation. The main risk is DWBS evolution. Add an explicit synchronization rule: "When `architecture/DWBS.md` adds or completes a plane, V3 11_deployment §5.1 Plane Summary must be updated within the same PR." Also link migration pending items to V2 `MODULE_AUTHORITY_MATRIX.md`. |
| **12_orchestration** | REINFORCE WITH V2 CONTRACTS | Three OPEN_QUESTIONs must become formal issues. Resolve the governance-in-shadow-mode question by referencing V2 decision policy contract. The retry policy consolidation is valuable — add a "Source Version" column to the retry table tracking which component YAML version was consolidated. Resolve Narrative Engine adapter gap as a formal OPEN_ISSUE with owner and resolution target. |

---

## SECTION 8 — BATCH SUMMARY

### 8.1 Overall Epistemic Depth Comparison (V2 Average vs V3 All Layers)

| Dimension | V2 Average Score | V3 Layers 00–02 Avg | V3 Layers 03–12 Avg | V3 Net Gap (full) |
|:---|:---:|:---:|:---:|:---:|
| Contract Clarity | 8.5 | 4.7 | 7.6 | −0.9 |
| Schema Determinism | 8.0 | 3.7 | 7.5 | −0.8 |
| Epistemic Discipline | 8.5 | 4.3 | 7.7 | −0.5 |
| Invariant Enforcement | 8.5 | 3.3 | 7.7 | −0.8 |
| Evaluation Rigor | 7.8 | 4.3 | 7.3 | −0.2 |
| Data Lineage Traceability | 7.8 | 2.7 | 7.3 | −0.5 |
| Regime Gating Explicitness | 7.8 | 3.7 | 7.4 | −0.3 |
| Memory Mutation Safety | 7.8 | 3.7 | 7.4 | −0.3 |
| Dashboard Integration Readiness | 7.5 | 3.7 | 7.4 | −0.1 |

> **Critical Finding**: The V3 memory system is NOT uniformly shallow. Layers 00–02 (foundational) average 3.6/10 across all dimensions — a CRITICAL gap vs V2 average of 8.2/10. Layers 03–12 (operational) average 7.6/10 — within 0.8 points of V2 average depth. The system has a **bimodal maturity distribution**: weak foundations (00–02), strong operational layers (03–12).

---

### 8.2 Structural Maturity Rating

**Overall V3 Memory System Maturity: 68 / 100**

| Sub-Rating | Score | Basis |
|:---|:---:|:---|
| Foundational Layers (00–02) | 40/100 | Narrative-only vision; intent-only scope; partial success invariants |
| Domain & Architecture (03–04) | 75/100 | Strong canonical model; BAN rules declared; slight enforcement gap |
| Component & Data Contracts (05–06) | 82/100 | Health contract is a genuine improvement; data layer comprehensive |
| Execution & Reliability (07–08) | 80/100 | Authority ambiguity on harness; excellent failure taxonomy |
| Security & Observability (09–10) | 78/100 | Invariant coverage gap; observability partially consolidated |
| Deployment & Orchestration (11–12) | 78/100 | Strong DWBS synthesis; open questions in orchestration |

---

### 8.3 Is V3 Ready to Absorb V2 for These Layers?

| Layer Group | Ready to Absorb V2? | Verdict |
|:---|:---:|:---|
| 00_vision, 01_scope, 02_success | **NO** | Foundational layers are narrative/intent without enforcement. V2 governance, epistemic, and contracts folders cannot be retired until V3 adds enforcement chains. |
| 03_domain, 04_architecture | **PARTIAL** | V3 domain model is an improvement; architecture is an intent layer over V2 contracts. V2 `layer_interaction_contract.md` must remain operative. |
| 05_components | **YES (for health contract)** | V3 health contract is a new universal standard with no V2 equivalent. Should become V2's health specification. |
| 06_data, 07_execution | **PARTIAL** | V3 consolidates V2 contracts well. V2 source contracts (`CON-001`, `CON-002`, `CON-003`, `execution_harness_contract.md`) must remain authoritative. V3 must become the public reference with V2 as implementation ground truth. |
| 08_reliability, 09_security | **PARTIAL** | V3 synthesis is strong. The invariant coverage gap (7 vs 9) and degraded state duplication must be resolved before V3 can replace V2. |
| 10_observability | **NO (yet)** | V3 observability is a partial consolidation (60–70%). Four V2 dashboard contracts not captured. Extend V3 before absorbing V2 dashboard specification. |
| 11_deployment, 12_orchestration | **PARTIAL** | V3 DWBS synthesis is good. V2 `DWBS.md`, `phase_lock_registry.md`, and component YAMLs must remain operative sources until synchronization mechanisms are in place. |

**Overall Verdict**: **PARTIAL** — V3 layers 03–12 represent a genuine consolidation architecture that could absorb most V2 documentation with targeted reinforcement. V3 layers 00–02 are not ready and will require contract additions before V2 foundational docs can be retired.

---

### 8.4 Top 5 Risks Discovered

1. **Bimodal Maturity Risk (P0)**: V3 layers 00–02 are narrative structures with average depth score of 3.6/10 against V2's 8.2/10. The entire V3 memory system's legitimacy as a canonical reference rests on these foundational layers. A weak foundation undermines all downstream layers that cite "CANONICAL" authority. Must be addressed before V3 is promoted as the system's primary reference.

2. **Authority Ambiguity Risk (P0)**: V3 07_execution declares "intent only" while V2 `execution_harness_contract.md` declares "Constitutional — Binding." Both contain identical rules. Developers reading V3 may not consult the operative V2 contract. This is an invisible enforcement gap — the system appears to have harness constraints but may not enforce them beyond the V2 contract's reach.

3. **Synchronization Drift Risk (P1)**: V3 layers 06_data, 07_execution, 08_reliability, 11_deployment, and 12_orchestration all consolidate V2 source documents. No synchronization mechanism exists. If V2 contracts are updated (e.g., `market_proxy_sets.md`, component YAMLs, `degraded_state_registry.md`), V3 layers silently become stale. The V2-to-V3 consolidation has no version-lock protocol.

4. **Invariant Coverage Gap Risk (P1)**: V3 09_security declares 7 ABSOLUTE invariants; V2 `epistemic/architectural_invariants.md` declares 9. The sets do not subsume each other. Combined, there are 11 unique invariants spanning both lists. No single document maintains the complete invariant set. Neither list is the authoritative union. System safety guarantees are split across two non-synchronized inventories.

5. **Shadow Mode Governance Gap (P2)**: V3 12_orchestration explicitly flags that governance enforcement mode during shadow promotion runs is unspecified. This means the system can produce shadow outputs under conditions where governance holds should apply but are not enforced. IRR runs (observed in V2 audit docs) have surfaced governance leakage in shadow mode. This gap remains open in both V3 and V2.

---

### 8.5 Top 5 Architectural Improvements in V3

1. **Universal Component Health Contract (05_components)**: V3 introduces a universal OK/DEGRADED/FAILED health interface applicable to all 18+ components. V2 had per-component implicit health handling with no consistent interface. V3 health contract includes observability signals, state transition rules, and a reference implementation. This is the most structurally significant V3 addition — it should be adopted as the V2 standard.

2. **IRR Failure Taxonomy Formalization (08_reliability)**: V3 condenses scattered V2 IRR audit reports (5 separate implementation reports) into a unified F1–F5 failure taxonomy with P0/P1/P2 priority levels, required resolution before Truth Advancement, and a troubleshooting quick reference table. This synthesis is more operationally useful than V2's fragmented reports.

3. **Phase Lock Governance System (11_deployment)**: V3 formally classifies V2 locked artifacts into `CON-001`, `CON-002`, `CON-003 NEVER` and mutable registries (`REG-001`, `REG-002`, `REG-003`). The lock-breaking protocol (5-step with audit trail) is more formal than V2's ad-hoc governance documentation. This is a genuine governance improvement.

4. **Temporal Truth Model Centralization (06_data)**: V3 consolidates the temporal truth model (RDT/CTT/TE three planes, five temporal states, eight temporal rules) from V2's `governance/temporal_truth_contract.md` and adds a cross-layer mapping that V2 lacked. The explicit CORRUPT state, market-specific TE tracking (`TE_US` / `TE_INDIA`), and unified temporal persistence table provide clearer guidance than V2's scattered temporal handling.

5. **OPEN_QUESTION Transparency (12_orchestration)**: V3 explicitly flags 3 unresolved architecture questions with enough context to make them actionable. V2 documents left equivalent gaps implicit or buried in lengthy audit reports. The practice of explicit OPEN_QUESTION declarations should be standardized across all V3 layers as part of living documentation governance.

---

### 8.6 Critical Architectural Observation

V3 memory layers occupy a well-defined architectural role: they are **canonical reference consolidators**, not operational enforcement systems. The appropriate abstraction is:

```
V3 Memory Layers  =  What the system is (reference architecture)
V2 Source Docs    =  How the system works (operative enforcement)
```

The audit reveals that V3 has achieved this role cleanly for layers 03–12. The foundational layers (00–02) are below the expected reference quality — they read as position papers, not architectural specifications. Every downstream layer will be stronger when 00_vision, 01_scope, and 02_success are brought to the same rigor standard as 06_data and 08_reliability.

The V3 memory system is **architecturally coherent but foundationally incomplete**. It is the correct long-term structure for this system's documentation — but it is not ready to replace V2 as the operative enforcement system. The migration path is clear and sequenced by the stability scores above.

---

*Audit completed: 2026-02-20*
*Layers analyzed: 00_vision, 01_scope, 02_success, 03_domain, 04_architecture, 05_components, 06_data, 07_execution, 08_reliability, 09_security, 10_observability, 11_deployment, 12_orchestration*
*V2 folders audited: architecture/, audit/, capital/, contracts/, dashboard/, diagnostics/, epistemic/, evolution/, intelligence/, meta/*
