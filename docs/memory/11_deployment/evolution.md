# Deployment & Evolution

> [!IMPORTANT]
> **Authoritative Source**: `docs/memory/03_domain/domain_model.md` is CANONICAL.
> **Conflict Handling**: Where legacy source docs conflict with Domain Model, mark OPEN_CONFLICT.

> This document describes environments, evolution plans, migration paths, and release assumptions.
> Intent only. No implementation.

---

## 1. Evolution Principles

| Principle | Description |
| :--- | :--- |
| **Trust is Earned** | Research insight ≠ trading authority; every capability must prove itself before promotion |
| **Freeze by Default** | Default state for all subsystems is FROZEN; unfreeze requires explicit justification and DID |
| **Boring is Beautiful** | Production remains slow-changing, conservative, and boring by design |
| **Evolution ≠ Drift** | Authorized change through governance is evolution; silent unauthorized change is drift |
| **One-Skill-at-a-Time** | Development focuses on a single skill until authoritative completion; parallel work is forbidden |
| **Audit Before Scale** | No new capability is added until the previous one is fully verifiable |
| **Rollback First** | Workflows prioritize recoverability over speed |

*(Sources: `docs/architecture/DWBS.md`, `docs/epistemic/roadmap/dwbs_post_freeze.md`, `docs/VISION_BACKLOG.md`)*

---

## 2. The Three Worlds

These boundaries are non-negotiable. Violation corrupts the entire system.

| World | Purpose | Characteristics | Transition Rule |
| :--- | :--- | :--- | :--- |
| **Production** | Live capital operations | Stable, conservative, slow-changing, boring by design | Only accepts GOVERNANCE-PROMOTED modules |
| **Research** | Experimental validation | Failure-tolerant, isolated, requires governance passage | Promotes via 5-gate process (see §6.2) |
| **Vision** | Conceptual exploration | Non-actionable, awareness-only | NEVER leaks into Production or Research code |

**Critical Rules**:
- Vision items MUST NOT leak into Production
- Research items MUST pass governance before Production
- Production remains boring by design

*(Source: `docs/VISION_BACKLOG.md`, `docs/memory/01_scope/boundaries.md`)*

---

## 3. Runtime Environment

### 3.1 Current Deployment Model

| Component | Runtime | Port / Schedule | Notes |
| :--- | :--- | :--- | :--- |
| **Backend API** | Python / FastAPI | Port 8000 | Serves dashboard data |
| **Frontend Dashboard** | Vite / React | Port 5173 | Truth surface (read-only) |
| **US Data Pipeline** | Python scripts (batch) | Daily scheduled | Alpha Vantage REST |
| **India Data Pipeline** | Python scripts (batch + WebSocket) | Market hours | Angel One SmartAPI |
| **Scheduler** | Windows Scheduled Tasks | Active (Daily/Weekly) | Local orchestration |
| **EV-TICK** | Python CRON job | Configurable interval | Passive system state polling |

### 3.2 Environment Assumptions

| Assumption | Description |
| :--- | :--- |
| **Local-first** | All computation runs on a single Windows machine |
| **No cloud dependencies** | System does not depend on cloud infrastructure for core operations |
| **No database server** | Data stored in files (Parquet, JSON, JSONL); no RDBMS, no separate DB process |
| **Single-operator** | System designed for single operator; multi-human governance defined but not enforced at infrastructure level |
| **No containerization** | Python virtualenv + Node.js; no Docker in current phase |
| **Network required** | Only for external API calls (Alpha Vantage, Angel One); system operates without network for analysis |

### 3.3 Data Layer Structure

| Layer | Storage | Mutability | Purpose |
| :--- | :--- | :--- | :--- |
| **Bronze (Raw)** | `data/raw/` JSONL | Append-only | External API responses, unvalidated |
| **Silver (Canonical)** | `data/processed/` Parquet | Immutable after validation | Deduplicated, schema-conforming |
| **Gold (Analytics)** | `data/decisions/`, `data/narratives/` | Immutable once generated | Regime, narrative, factor artifacts |
| **Epistemic** | `docs/epistemic/ledger/` Markdown | Append-only (permanent) | Decisions, evolution, assumptions |
| **Audit** | `logs/` JSON | 90-day active lifecycle | Operational telemetry |

*(Sources: `docs/memory/04_architecture/data_flow.md`, `docs/epistemic/data_retention_policy.md`)*

---

## 4. Phase Model — Foundation Phases (Closed)

These phases are completed and locked. Modifications require explicit lock-breaking.

### 4.1 Phase 1: API-Based Ingestion

| Property | Value |
| :--- | :--- |
| **Status** | ✅ CLOSED (2026-01-03) |
| **Scope** | Angel One SmartAPI ingestion for live OHLC and LTP data |
| **Lock File** | `docs/phase_locks/PHASE_1_INGESTION_LOCK.md` |
| **Maintenance** | No new ingestion features permitted |
| **Break Policy** | Justification document + senior engineer review |

### 4.2 Phase 1B: Historical Data Ingestion

| Property | Value |
| :--- | :--- |
| **Status** | ✅ CLOSED (2026-01-03) |
| **Scope** | Historical daily candle ingestion via Angel One (ON-DEMAND CLI only) |
| **Lock File** | `docs/phase_locks/PHASE_1B_HISTORICAL_INGESTION_LOCK.md` |
| **Critical Restriction** | Historical data NEVER influences live momentum engine; NEVER wired into scheduler |
| **Break Policy** | Phase Unlock Request + justification + isolation guarantee + re-lock after changes |

### 4.3 Phase 2: Processed Data Layer

| Property | Value |
| :--- | :--- |
| **Status** | ✅ CLOSED (2026-01-03) |
| **Scope** | Deterministic, idempotent JSONL → Parquet transformation |
| **Lock File** | `docs/phase_locks/PHASE_2_PROCESSING_LOCK.md` |
| **Frozen Logic** | No indicators or strategies in this layer |
| **Enhancement Rule** | New data enhancements MUST occur in downstream Gold/Strategy layer |

### 4.4 Phase 3: Momentum Engine v0

| Property | Value |
| :--- | :--- |
| **Status** | ✅ CLOSED (2026-01-03) |
| **Scope** | Minimalist momentum (VWAP, HOD proximity, Relative Volume) |
| **Lock File** | `docs/phase_locks/PHASE_3_MOMENTUM_LOCK.md` |
| **Frozen Logic** | No new indicators, ML models, or backtesting logic |
| **Enhancement Rule** | RSI, threshold changes, etc. require explicit lock-breaking |

---

## 5. Phase Model — Structural Planes (Completed)

These represent the DWBS-governed structural build, completed sequentially with gate validation.

### 5.1 Plane Summary

| # | Plane | Status | Gate | Key Milestone |
| :--- | :--- | :--- | :--- | :--- |
| **1** | Control Plane | ✅ COMPLETE | Belief + Factor + Strategy policy operational | Epistemic foundation established |
| **2** | Orchestration Plane | ✅ COMPLETE | Task abstraction + graph + harness binding | Governed execution infrastructure |
| **3** | Strategy Plane | ✅ COMPLETE | Registry + lifecycle + single-strategy mapping | Governed strategy registration |
| **4** | Structural Activation | ✅ COMPLETE | Macro + Factor layers activation (latent → referenced) | Live state production |
| **5** | Scale & Safety | ✅ COMPLETE | Kill-switch + bounds + determinism + circuit breakers + audit | **STRUCTURALLY PRODUCTION-READY** |
| **6** | Decision Plane | ✅ COMPLETE | Decision spec + HITL + Shadow + Audit | **CHOICE FORMATION AUTHORIZED** (HITL + Shadow) |
| **7** | Evolution Phase | ✅ COMPLETE | Bulk eval + replay + paper P&L + diagnostics + rejection | **STRATEGY EVALUATION AUTHORIZED** |

### 5.2 Plane Build Order (Mandatory Sequence)

*(Original Diagram: `docs/memory/_appendix/evolution_code.md`)*

1. **Control Plane**: Belief → Factor Policy → Strategy Policy → Validator Gate
2. **Orchestration Plane**: Task Abstraction → Task Graph → Harness Binding
3. **Strategy Plane**: Strategy Mapping → Registry → Lifecycle
4. **Structural Activation Plane**: Macro Activation → Factor Activation
5. **Scale & Safety Plane**: Multi-Strategy Coexistence → Failure Modes → Permission Revocation
6. **Decision Plane (HITL + Shadow)**: Decision Spec → HITL Gate → Shadow Sink → Decision Audit
7. **Evolution Phase (Learning & Debugging)**: Bulk Registration → Replay → Paper P&L → Diagnostics → Rejection Analysis

**Invariant**: Planes are sequentially gated. Cross-plane shortcuts are forbidden.

### 5.3 Post-Plane Evolution Activities (Completed)

| Activity | Scope | Status |
| :--- | :--- | :--- |
| Regime Observability Audit | Data sufficiency + alignment + viability | ✅ COMPLETE |
| Regime Data Ingestion | 7 symbols, 756+ trading days each | ✅ SATISFIED |
| Strategy Universe Finalization | 8 families, 24 strategies, all EVOLUTION_ONLY | ✅ COMPLETE |
| Momentum Specialization | 3 Momentum variants (Strict, Accelerating, Persistent) | ✅ COMPLETE |
| Governance Layer Implementation | Decision Policy + Fragility + Parity + Narrative + Reality Runs | ✅ COMPLETE |
| UI Multifold Expansion (Phase 8) | Full dashboard surfaces, power user controls, provenance | ✅ COMPLETE |

*(Sources: `docs/architecture/DWBS.md`, `docs/epistemic/ledger/evolution_log.md`)*

---

## 6. Migration Paths

### 6.1 Module Authority Migration

Modules migrate through explicit authority classifications:

| Classification | Live Influence | Core Import | Free Modification | Description |
| :--- | :--- | :--- | :--- | :--- |
| **PRODUCTION-ACTIVE** | YES | YES | NO | Powers live execution; requires 100% test pass + sign-off |
| **PRODUCTION-DORMANT** | NO | YES | NO | Core infrastructure, currently bypassed or monitor-only |
| **RESEARCH-ONLY** | NO | NO | YES | Analytical modules, physically isolated |
| **EXPERIMENTAL** | NO | NO | YES | Scratchpad logic, unverified ideas |
| **DEPRECATED** | NO | NO | NO | Legacy code targeted for removal |

**Migration Policy**:
- Modules in `core_modules/` overlapping with Research MUST migrate to `research_modules/`
- Upon migration, status changes to RESEARCH-ONLY with technical decoupling from production call stacks
- No duplicate implementation across production and research (Single Authority Source)
- Import lockdown: `research_modules` imports into `core_modules` are auto-rejected

**Completed Migrations**:

| Module | From | To | Status |
| :--- | :--- | :--- | :--- |
| Backtesting | Various | `research_modules/backtesting/` | ✅ Complete |
| Volatility Context | Various | `research_modules/volatility_context/` | ✅ Complete |
| News Sentiment | Various | `research_modules/news_sentiment/` | ✅ Complete |
| Risk Models | Various | `research_modules/risk_models/` | ✅ Complete |

**Pending Migrations**:

| Module | Current Location | Target | Reason |
| :--- | :--- | :--- | :--- |
| Portfolio Opt | `src/institutional_modules/` | `research_modules/` | Overlaps with Research |
| Risk Estimation | `src/core_modules/` | `research_modules/` | Placeholder; overlaps with Risk Models |
| OMS / EMS | `src/institutional_modules/` | `src/core_modules/infra` | Production-Dormant infrastructure |
| Compliance Engine | `src/institutional_modules/` | `src/core_modules/infra` | Production-Dormant infrastructure |
| Technical Scanner | `src/pro_modules/` | Deprecate → merge into Research | Experimental; overlapping |

### 6.2 Research → Production Promotion Path

A 5-gate sequential promotion process:

| Gate | Requirement | Purpose |
| :--- | :--- | :--- |
| **1. Phase Threshold** | Project reaches module's defined Activation Phase | Prevents premature promotion |
| **2. Observation (30 days)** | Error-free data logging in Research state for 30 trading days | Proves stability |
| **3. Paper Trading (100 trades)** | 100 consecutive simulated trades with < 5% slippage variance | Proves accuracy |
| **4. Human Approval** | Explicit sign-off in `ACTIVATION_LOG.md` | Proves intent |
| **5. Test Coverage (90%)** | Unit + integration tests pass | Proves reliability |

**Promotion Execution**:
- Single dedicated PR tagged `[PROMOTION]`
- Import barriers removed only for promoted module
- Phase lock check (`ACTIVE_PHASE`) removed for promoted module

**Promotion is Reversible**: Anomalous production behavior → immediate revert to Research-Only via global kill-switch.

### 6.3 Planned Research Module Activation Schedule

| Module | Planned Activation Phase | Current Status |
| :--- | :--- | :--- |
| Backtesting Engine | Phase 6+ | RESEARCH-ONLY |
| Volatility / Market Context | Phase 7+ | RESEARCH-ONLY |
| Risk Modeling & Position Sizing | Phase 8+ | RESEARCH-ONLY |
| News & Sentiment Analysis | Phase 9+ | RESEARCH-ONLY |

*(Sources: `docs/governance/MODULE_AUTHORITY_MATRIX.md`, `docs/governance/RESEARCH_MODULE_GOVERNANCE.md`)*

---

## 7. Phase Lock Governance

### 7.1 Phase Lock Concept

Phase Locks are structural freezes that preserve system integrity during mutation phases. They track documents and subsystems that are frozen and may not be modified without governance action.

### 7.2 Locked Contracts (Epistemic Foundation)

| Artifact ID | Name | Owner | Expiration | Exception Policy |
| :--- | :--- | :--- | :--- | :--- |
| `CON-001` | `market_proxy_sets.md` | Governance | Indefinite | Requires `SYSTEM_MUTATION` |
| `CON-002` | `proxy_dependency_contracts.md` | Architecture | Indefinite | Requires `SYSTEM_MUTATION` |
| `CON-003` | `truth_epoch_scoping.md` | Epistemic | Indefinite | **NEVER** |

### 7.3 Mutable Registries (Operational State)

| Artifact ID | Registry | Owner | Mutability | Trigger |
| :--- | :--- | :--- | :--- | :--- |
| `REG-001` | `coverage_gap_register.md` | Data | **Open** | Discovery of new gap |
| `REG-002` | `data_source_governance.md` | Data | **Open** | New ingestion source |
| `REG-003` | `degraded_state_registry.md` | Logic | **Open** | Detection of failure mode |

### 7.4 Lock Breaking Protocol

To modify a locked artifact:

1. Create a Phase Unlock Request document with explicit justification
2. Identify all downstream impacts (DID)
3. Obtain senior engineer / architect review
4. Perform changes with audit trail
5. Re-lock after changes with updated verification documentation
6. Log lock break in `phase_lock_registry.md` audit trail

*(Source: `docs/governance/phase_lock_registry.md`)*

---

## 8. Truth Advancement Gates (Release Gates)

Truth Epoch advancement is the system's equivalent of a "release" — it advances what the system considers true. Each advancement passes through explicit gates.

### 8.1 Gate 1: Raw → Canonical (Ingestion Gate)

| Check | Description |
| :--- | :--- |
| Schema validity | All required columns present and typed correctly |
| Temporal continuity | No gaps greater than `MAX_GAP` (weekend/holiday tolerance) |
| Data integrity | No NaN/Inf; `High ≥ Low`; `Volume ≥ 0` |
| Drift check | Price change within circuit breaker threshold (manual review if exceeded) |

**PASS** → Append to Canonical Store, update CTT.
**FAIL** → Reject ingestion, raise alert, CTT remains at T−1.

### 8.2 Gate 2: Canonical → Evaluation (Intelligence Gate)

| Check | Description |
| :--- | :--- |
| Data completeness | All required proxy symbols have CTT ≥ target TE |
| Epistemic health | No outstanding critical alerts; Inspection Mode INACTIVE |
| Policy compliance | Strategy eligibility and risk constraints valid |

**PASS** → Execute Factor/Strategy/Governance, update TE to match CTT.
**FAIL** → System Halt; TE remains at T−1; dashboard shows STALE.

### 8.3 Gate 3: Global Synchronization (Sanity Gate)

| Check | Description |
| :--- | :--- |
| Cross-market drift | `abs(TE_US − TE_INDIA) ≤ 1 Day` |
| Failure | Warn operator; allow independent operation unless explicit dependency |

### 8.4 Gate 4: Manual Override (Emergency Gate)

| Property | Description |
| :--- | :--- |
| Authority | Admin / Operator only |
| Actions | Force TE advancement or rollback |
| Requirements | Logged justification in audit_log; CLI with explicit confirmation flag |

*(Source: `docs/governance/truth_advancement_gates.md`)*

---

## 9. DWBS Post-Freeze Roadmap (Future Phases)

These represent potential future work inventory. Inclusion does NOT imply execution.

| Phase | Objective | Status | Exit Condition |
| :--- | :--- | :--- | :--- |
| **P1 — Execution Bridging** | Safe Chat → CLI bridge | ✅ Executed | Bridge operational, contract authoritative |
| **P2 — Skill Portfolio** | Drift Detector, Pattern Matcher, Constraint Validator | ✅ Executed | Skills specified and implemented |
| **P3 — Workflow Stabilization** | SOD/EOD standardization, troubleshooting runbooks | ✅ Executed | Operator has paved paths for routine ops |
| **P4 — Multi-Human Governance** | Concurrent DID conflict resolution, operator attribution | Defined | System handles multi-user attribution |
| **P5 — Observability Hardening** | Structured logging, Audit Log Viewer, retention policy | ✅ Executed | All system actions irrevocably traceable |
| **P6 — Selective Automation** | Bounded automation contract, Monitor Trigger prototype | ✅ Executed | Strict containment proven |
| **P7 — Institutionalization** | Finalize ledgers, freeze Skill Catalog v1.0, archive dev artifacts | Frozen | System requires zero dev maintenance |

### 9.1 Global Control Rules

| Rule | Description |
| :--- | :--- |
| **Freeze Discipline** | Default state is FROZEN; unfreeze requires justification + DID |
| **One-Skill-at-a-Time** | Focus on single skill until authoritative completion |
| **Audit-Before-Scale** | Previous capability fully verifiable before adding new |
| **Rollback-First** | Recoverability over speed |
| **No Autonomy** | No autonomous loops without dedicated, isolated milestone |

*(Source: `docs/epistemic/roadmap/dwbs_post_freeze.md`)*

---

## 10. Release Assumptions

### 10.1 Current Phase Assumptions

| Assumption | Description |
| :--- | :--- |
| **Shadow Mode only** | System operates in Research & Validation; no live money |
| **Local execution** | All pipelines and services run on a single Windows machine |
| **Single operator** | One human operator; multi-human governance defined but not enforced |
| **API availability** | Alpha Vantage and Angel One APIs remain accessible with current key pools |
| **No production execution pathway** | `INV-NO-EXECUTION` and `INV-NO-CAPITAL` are absolute |
| **Idempotent processing** | Same input → same output for all pipelines |
| **Core layers frozen** | Genesis, Regime, Accumulation cognitive layers are structurally frozen |

### 10.2 Phase Exit Criteria (Current → Next)

| Criterion | Threshold |
| :--- | :--- |
| **Stability** | Zero orphans (data gaps) and zero critical crashes for 2 weeks sustained |
| **Signal Quality** | Consistent A or B grade signals in Shadow Mode |
| **Idempotency** | Live signals match Historical Replay signals 100% for same data period |
| **Regime Stability** | Strategy performs predictably across 2+ distinct regimes |
| **Lens Consensus** | High-conviction ideas consistently outperform baseline |
| **Drawdown Control** | Max drawdown < defined threshold in simulation |

### 10.3 What Cannot Be Released (Blocked)

| Item | Blocking Condition | Status |
| :--- | :--- | :--- |
| **Optimization Phase** | Blocked until Evolution closure and all IRR findings resolved | 🔴 BLOCKED |
| **Execution Plane (D014+)** | Permanently blocked in current architecture | 🔴 PERMANENTLY BLOCKED |
| **Broker connectivity** | Requires all OBL-DE-* satisfied + explicit D014 decision | 🔴 BLOCKED |
| **Auto-optimization** | Forbidden action regardless of phase | 🔴 FORBIDDEN |
| **Signal overriding** | Forbidden action regardless of phase | 🔴 FORBIDDEN |

### 10.4 Release Process Assumptions

| Assumption | Description |
| :--- | :--- |
| **No CI/CD** | Current deployment is manual; no automated build/deploy pipeline |
| **Git-based versioning** | All artifacts version-controlled in Git |
| **PR-based promotion** | Module promotions via dedicated tagged PRs |
| **DID accompaniment** | Every significant change produces a Documentation Impact Declaration |
| **Execution Plan required** | Tasks must be whitelisted in an Execution Plan before execution |
| **Stop-on-failure** | If any task in a plan fails, the entire plan halts |
| **Human verification** | Mode A tasks require explicit human sign-off in bridge log |
| **Rollback baseline** | Failed execution reverts to last known frozen state |

*(Sources: `docs/epistemic/current_phase.md`, `docs/memory/02_success/success_criteria.md`, `docs/epistemic/roadmap/execution_plan.md`)*

---

## 11. Evolution Rules

### 11.1 How New Layers May Be Added

1. **Declare** in epistemic documents (`latent_structural_layers.md`)
2. **Authorize** via Decision Ledger entry (D00X)
3. **Amend** DWBS to include in Structural Activation Plane
4. **Update** validator with new layer rules

### 11.2 How Planes May Be Extended

| Extension Type | Process |
| :--- | :--- |
| New DWBS items within existing plane | DWBS amendment with justification |
| New plane (rare) | Full design review |
| Dependency updates | Explicit re-mapping of build order |

### 11.3 How Deprecations Occur

1. **Decision Ledger entry** authorizing deprecation
2. **RETIRED status** — deprecated items move to RETIRED, not deleted
3. **Validator enforcement** — deprecated items produce WARNING, then FAIL
4. **Grace period** — announced deprecation → warning → hard fail

### 11.4 Evolution vs. Drift (Critical Distinction)

| Evolution | Drift |
| :--- | :--- |
| Authorized via Decision Ledger | Silent or unauthorized |
| Documented in DWBS amendment | Not reflected in DWBS |
| Validator-enforced | Validator-evaded |
| Announced and reversible | Hidden and persistent |

*(Source: `docs/architecture/DWBS.md` §8)*

---

## 12. Anti-Patterns (Forbidden Evolutionary Actions)

| Anti-Pattern | Why It's Wrong | Prevention Mechanism |
| :--- | :--- | :--- |
| "Quick strategy without registry" | Ungoverned strategy | Strategy Plane requires registry |
| "Infer regime from volatility" | Strategies cannot infer beliefs | STR-1 invariant |
| "Skip factor for MVP" | Factor bypass is architectural violation | Build order forbids |
| "Execute without harness" | Unbound execution has no audit | Orchestration is prerequisite |
| "Activate macro later" | Regime depends on macro | Structural Activation follows Strategy |
| "Hot-patch active strategy" | Strategy versions are frozen | STR-6 invariant |
| "Conflate research with production" | Governance gates exist for a reason | 5-gate promotion process |
| "Optimize for backtests over survival" | Backtests lie; survival is truth | Observation period mandatory |
| "Auto-tune thresholds" | Constants frozen for a reason | Phase Lock governance |
| "Feature without theory" | Every feature needs "why" before "how" | Decision Ledger requirement |

*(Sources: `docs/architecture/DWBS.md` §7, `docs/VISION_BACKLOG.md`)*

---

## Legacy Source Mapping

| Section | Legacy Source Document(s) |
| :--- | :--- |
| §1 Philosophy | `DWBS.md`, `dwbs_post_freeze.md`, `VISION_BACKLOG.md` |
| §2 Three Worlds | `VISION_BACKLOG.md`, `boundaries.md` |
| §3 Environment | `data_flow.md`, `data_retention_policy.md` |
| §4 Foundation Phases | `PHASE_1_INGESTION_LOCK.md`, `PHASE_1B_HISTORICAL_INGESTION_LOCK.md`, `PHASE_2_PROCESSING_LOCK.md`, `PHASE_3_MOMENTUM_LOCK.md` |
| §5 Structural Planes | `DWBS.md`, `evolution_log.md` |
| §6 Migration Paths | `MODULE_AUTHORITY_MATRIX.md`, `RESEARCH_MODULE_GOVERNANCE.md` |
| §7 Phase Lock | `phase_lock_registry.md` |
| §8 Truth Gates | `truth_advancement_gates.md` |
| §9 Roadmap | `dwbs_post_freeze.md`, `execution_plan.md` |
| §10 Release Assumptions | `current_phase.md`, `success_criteria.md`, `execution_plan.md` |
| §11 Evolution Rules | `DWBS.md` §8 |
| §12 Anti-Patterns | `DWBS.md` §7, `VISION_BACKLOG.md` |
