# Observability & Metrics

> [!IMPORTANT]
> **Authoritative Source**: `docs/memory/03_domain/domain_model.md` is CANONICAL.
> This document describes logging intent, metrics concepts, dashboard surfaces, and validation checks.
> Intent only. No implementation.

---

## 1. Core Observability Principle

**Glass-Box**: Every threshold, decision, and magic number is configurable and observable. No hidden logic. The system's internal state machine must be machine-readable and audit-ready at all times.

| Principle | Description |
| :--- | :--- |
| **Total Transparency** | Every computation, decision, and state transition is visible |
| **Structured over Ad-Hoc** | Machine-parseable structured logs, not debug text dumps |
| **Provenance Always** | Every displayed value traces back to an artifact path and timestamp |
| **Silence is Forbidden** | Missing data surfaces as explicit "UNKNOWN" or "UNAVAILABLE", never as blank or zero |
| **Staleness is Amplified** | Stale data rendered with dominant warning overlays, not muted |

*(Sources: `docs/epistemic/project_intent.md`, `docs/dashboard/dashboard_truth_contract.md`)*

---

## 2. What Is Measured

### 2.1 Signal Validation & Performance

Measures effectiveness of signals against definitions in `domain_model.md` and grading in `success_criteria.md`.

| Metric | Description | Source |
| :--- | :--- | :--- |
| Signal grade distribution | A/B/C/D grades over time | Momentum Engine output |
| Genesis acceptance ratio | Historical acceptance rate | Strategy Selector |
| Signal confidence scores | Per-signal confidence with decay | Meta Engine |
| Trust scores per signal | Validity, confidence modifier, staleness, conflicts | Meta Engine |

**Signal Grade Definitions**:

| Grade | Meaning |
| :--- | :--- |
| **A** | High-quality signal, validated by T+5 and T+15 performance |
| **B** | Acceptable signal, partial validation |
| **C** | Marginal signal, inconclusive validation |
| **D** | Failed signal, negative outcome |

### 2.2 Data Pipeline Health

| Metric | Description | Source |
| :--- | :--- | :--- |
| Rows ingested per market per run | Volume tracking for each ingestion cycle | Ingestion components |
| Rows before/after merge | Delta auditing (bronze → silver) | Data pipeline |
| API call counts | Per-key, per-endpoint usage | Ingestion US/India |
| Rate limit utilization | Percentage of daily API budget consumed | Key rotation pool |
| Orphan count | Data gaps where expected records are missing | Data quality checks |
| Schema validation pass/fail | Per-batch schema conformance | Ingestion Gate |
| Price drift magnitude | Deviation from expected range | Circuit breaker check |

### 2.3 Temporal State

| Metric | Description | Display |
| :--- | :--- | :--- |
| **RDT** (Raw Data Time) | When raw data was last received | Per-market on dashboard |
| **CTT** (Canonical Truth Time) | When canonical store was last updated | Per-market on dashboard |
| **TE** (Truth Epoch) | What the system "knows" as truth | Global dashboard header |
| Drift magnitude | `CTT - TE` in days | Color-coded badge |
| Drift direction | Which markets are ahead/behind | Per-market indicator |

**Status Badges**:

| Badge | Condition | Color |
| :--- | :--- | :--- |
| `[SYNC]` | `TE == RDT` | Green |
| `[EVAL PENDING]` | `TE < RDT` (within threshold) | Yellow |
| `[STALE]` | `TE << RDT` (drift > 2 days) | Red |
| `[HALTED]` | Governance freeze active | Red |
| `[INSPECTION MODE]` | Simulation/visualization active | Purple |

### 2.4 Regime State

| Metric | Description | Source |
| :--- | :--- | :--- |
| Current regime classification | Per-market (BULLISH, BEARISH, NEUTRAL, UNCERTAIN) | Regime Engine |
| Regime confidence score | 0.0–1.0 with confidence band | Regime Engine |
| Regime transition alerts | State changes logged with before/after | Regime Engine |
| Regime stability indicator | Flapping detection (transition count in lookback) | Regime Engine |
| Proxy status | CANONICAL / DEGRADED / NOT_EVALUATED per market | Proxy Set engine |

### 2.5 Governance Integrity & Compliance

Tracks real-time activation of limits and gates defined in `failure_model.md`.

| Metric | Description | Source |
| :--- | :--- | :--- |
| Active holds | Currently active governance holds with reasons | Governance component |
| Active suppressions | Policy-driven action blocks with attribution | Decision/Fragility Policy |
| Gate pass/fail history | Ingestion Gate, Intelligence Gate, Sync Gate results | Truth Advancement Gates |
| Circuit breaker state | CLOSED / OPEN / HALF-OPEN per breaker | Fragility Policy |
| Obligation compliance | Per-obligation SATISFIED / UNMET status | Obligation Index |
| Drift detection alerts | Configuration, structural, epistemic drift reports | Drift Detector |

### 2.6 Execution & Strategy Metrics

| Metric | Description | Source |
| :--- | :--- | :--- |
| Strategy activation set | Which strategies are currently eligible | Strategy Selector |
| Shadow decision count | Decisions produced in shadow mode | Shadow Execution Sink |
| Decision routing | HITL vs SHADOW distribution | Decision Plane |
| Task graph completion | Per-cycle task pass/fail/skip status | Execution Harness |
| Watcher diagnostics | Per-watcher state changes, anomaly flags | EV-TICK |

*(Sources: component YAMLs, `docs/memory/02_success/success_criteria.md`, `docs/dashboard/temporal_truth_surface.md`)*

---

## 3. Logging Architecture

### 3.1 Log Categories

| Category | Location | Format | Retention | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Structured logs** | `logs/` per-component | JSON (machine-parseable) | 90 days active → 1 year archive | Operational debugging, automated post-mortems |
| **Audit logs** | `logs/*.json` | JSON with operator attribution | 90 days active → 1 year archive | Governance actions, hold/release events, operator decisions |
| **Ingestion logs** | Per-run log files | Structured | 90 days active → 1 year archive | Symbol, endpoint, status, records fetched, latency |
| **Evolution logs** | `docs/epistemic/ledger/evolution_log.md` | Markdown | **PERMANENT** | System lifecycle changes ("What" and "Why") |
| **Decision Ledger** | `docs/epistemic/ledger/decisions.md` | Markdown | **PERMANENT** | Authoritative human decisions |
| **IRR/Shadow logs** | `docs/irr/runtime/` | JSON + Markdown | **PERMANENT** | Reality run observations and failure evidence |

### 3.2 Structured Logging Intent

The system is transitioning from ad-hoc debug text to structured audit trails:

| Property | Requirement |
| :--- | :--- |
| **Machine-parseable** | JSON format with consistent schema per component |
| **Timestamped** | ISO8601 with timezone on every entry |
| **Attributed** | Operator identity, skill identity, or component identity on every entry |
| **Contextual** | Market, TE, regime state context attached to each entry |
| **Bounded** | `MAX_LEDGER_ENTRIES_PER_HOUR` enforced to prevent unbounded growth |
| **Provable** | Audit data loss is FORBIDDEN (`OBL-SS-AUDIT`) |

### 3.3 Ingestion-Specific Logging

| Field | Description |
| :--- | :--- |
| `symbol` | What instrument was ingested |
| `endpoint` | Which API endpoint was called |
| `status` | HTTP status / success indicator |
| `records_fetched` | Count of records returned |
| `latency` | Time to complete the request |
| `key_used` | Which API key (anonymized) was used |
| `retry_count` | How many retries were attempted |

### 3.4 What is NOT Logged

| Exclusion | Reason |
| :--- | :--- |
| API keys / secrets | Security — never in logs |
| Raw price data in log entries | Volume — stored separately in data layer |
| Performance predictions | Epistemic — system does not predict |
| Recommendation language | Invariant — observatory principle |

*(Sources: `docs/us_market_engine_design.md`, `docs/epistemic/data_retention_policy.md`, `docs/epistemic/governance/scale_safety_obligations.md`)*

---

## 4. Dashboard Surfaces

### 4.1 Dashboard Purpose

The dashboard is a **truth surface**, not a control panel. It projects the internal state of governance and intelligence layers to human operators.

| It Answers | It Does NOT Answer |
| :--- | :--- |
| "What is true now" (based on bound TE) | "What to do" |
| "What state is the system in" | "What might happen" |
| "What constraints are active" | "How to profit" |

### 4.2 Dashboard Panels & Surfaces

| Surface | Content | Data Source |
| :--- | :--- | :--- |
| **Temporal Truth Banner** | TE, CTT, RDT per market with color-coded badges | `temporal_state_{market}.json` |
| **Regime State Panel** | Current classification, confidence, stability, proxy status | `regime_context_{market}.json` |
| **Decision Policy Panel** | Active permissions, blocked actions, reasons | `decision_policy_{market}.json` |
| **Fragility Policy Panel** | Stress state, active constraints, signal details | `fragility_context_{market}.json` |
| **Signal Quality Heatmap** | Grade distribution over time | Momentum Engine output |
| **Governance Hold Panel** | Active holds, suppressions, circuit breaker status | Governance component |
| **Capital Readiness Panel** | Ceilings, drawdown state, kill-switch status | Capital readiness artifacts |
| **Watcher Diagnostics** | Per-watcher state changes, EV-TICK cycle status | EV-TICK output |
| **Narrative Panel** | Current narratives with source binding and confidence | Narrative Engine output |

### 4.3 Widget Binding Rules (Strict)

Every data-bearing widget must satisfy:

| Rule | Description |
| :--- | :--- |
| **Single artifact binding** | Each widget binds to exactly one backend artifact |
| **Single layer binding** | Each widget binds to exactly one system layer (DATA, INTELLIGENCE, GOVERNANCE) |
| **Single epoch binding** | Each widget binds to exactly one Truth Epoch |
| **Trace badge** | Inspectable lineage: `[Data Role] → [Source Artifact] → [Upstream Provider]` |
| **Unbound = invalid** | Unbound widgets must be removed or show error state |

### 4.4 Degradation & Staleness Display

| State | Dashboard Response |
| :--- | :--- |
| Data missing | Explicit "UNKNOWN" / "UNAVAILABLE" — never blank, never zero |
| Data stale | Dominant warning overlay: "STALE (Xm since last update) — DO NOT TRUST REGIME" |
| Process failed | Explicit error message with artifact path |
| Governance frozen | Banner: "🛑 TRUTH FROZEN BY GOVERNANCE" with reason |
| Inspection mode | Banner: "INSPECTION MODE: TE-XXXX-XX-XX" on all components; live bindings hidden |
| Constraint active (HOLD, OBSERVE_ONLY) | Treated as nominal — NOT displayed as "broken" or "stopped" |

### 4.5 Forbidden Dashboard Semantics

| Forbidden Element | Reason |
| :--- | :--- |
| Rankings ("best" / "worst") | Implies judgment |
| Arbitrary scores (1-10, 0-100) | Hides complexity |
| Directional arrows | Implies future movement |
| Green/Red for market direction | Color reserved for system health only |
| "ACTIVE" without context | Must always be qualified (e.g., "ACTIVE (UNDER CONSTRAINTS)") |
| "You should..." / "Buy" / "Sell" | Implies recommendation |
| "Opportunity" / "Profit" / "Target price" | Implies forecast |

*(Sources: `docs/dashboard/dashboard_truth_contract.md`, `docs/dashboard/temporal_truth_surface.md`, `docs/dashboard/ui_guardrails.md`)*

---

## 5. Alerting

### 5.1 Alerting Strategy

Alerts inform. They never act. Delivery is via dashboard visual badge (polling backend state).

### 5.2 Alert Definitions

| Alert | Trigger | Severity | Color | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Watcher State Change** | A watcher's state differs between ticks | Warning | 🟡 Yellow | Notify observer of regime shifts |
| **System State Change** | `system_status.status` transitions (e.g., IDLE → OBSERVING) | Info | 🟡 Yellow | Awareness of system mode changes |
| **Data Staleness** | Last EV-TICK timestamp > threshold (e.g., 15 min) | Error | 🔴 Red | Investigation required (manual) |
| **Governance Violation** | `governance_status != CLEAN` | Critical | 🔴 Red | HALT (passive — alert only) |
| **Temporal Drift** | `CTT >> TE` beyond 2-day threshold | Warning | 🟡 Yellow | Operator should evaluate |
| **Circuit Breaker Activation** | Fragility policy enters SYSTEMIC_STRESS | Critical | 🔴 Red | System in defensive posture |

### 5.3 Alerting Constraints

| Constraint | Description |
| :--- | :--- |
| **No auto-action** | Alerts never trigger automated responses |
| **No external notification** | Current phase: dashboard-only (no email, SMS, webhook) |
| **Log-based** | All alerts backed by structured log entries |
| **Bounded** | Alert frequency governed to prevent flooding |

*(Source: `docs/dashboard/alerting_rules.md`)*

---

## 6. Validation Checks

### 6.1 Data Validation

| Check | When | What | Failure Response |
| :--- | :--- | :--- | :--- |
| **Schema validation** | On every ingestion batch | Required fields, types, constraints (e.g., `high ≥ low`) | Reject batch; CTT does NOT advance |
| **Date continuity** | Post-ingestion | No unexpected gaps (allowing weekends/holidays) | Flag gaps for review |
| **Volume non-negativity** | Post-ingestion | All volumes ≥ 0 | Reject record |
| **Price range check** | Post-ingestion | No zero or negative prices; drift within circuit breaker | Quarantine anomalous records |
| **Duplicate detection** | Silver layer processing | Dedup by `(symbol, timestamp)` | Retain latest, log duplicate |
| **Append-only verification** | On write | Raw layer always appends, never overwrites | Structural invariant |

### 6.2 Regime Validation

| Check | When | What | Failure Response |
| :--- | :--- | :--- | :--- |
| **Symbol completeness** | Pre-computation | All required proxy symbols present | `NOT_VIABLE` — computation FORBIDDEN |
| **History depth** | Pre-computation | ≥ 756 trading days per symbol | `NOT_VIABLE` |
| **Temporal alignment** | Pre-computation | Intersection across symbols ≥ 756 days | Exclude misaligned symbols |
| **Data quality** | Pre-computation | No forward-fill, no interpolation, no synthetic | `NOT_VIABLE` |
| **Regime confidence** | Post-computation | Confidence above minimum threshold | Degrade downstream permissions |

### 6.3 Narrative Validation

| Check | When | What | Failure Response |
| :--- | :--- | :--- | :--- |
| **Source binding** | Pre-emission | Every sentence has a citation to input artifact | Reject sentence |
| **Grammar** | Pre-emission | Basic grammatical correctness | Reject sentence |
| **Regime compatibility** | Pre-emission | Narrative consistent with current regime state | Reject sentence |
| **Prohibited words** | Pre-emission | No recommendation language, no predictions | Reject sentence |
| **Confidence check** | Pre-emission | Low confidence → uncertainty warning appended | Append warning |
| **Staleness check** | Pre-emission | Data age within threshold | Prepend staleness warning |

### 6.4 Governance Validation

| Check | When | What | Failure Response |
| :--- | :--- | :--- | :--- |
| **Invariant check** | Continuous | All safety invariants hold | Immediate halt on violation |
| **Gate passage** | On advancement request | All gate prerequisites satisfied | Block advancement |
| **Obligation compliance** | On phase transition | All blocking obligations SATISFIED | Block transition |
| **Drift detection** | On demand / scheduled | Configuration, structural, epistemic drift | Flag for review or block deployment |
| **Kill-switch reachability** | System startup | Kill-switch mechanism operational | Block system start |

### 6.5 Execution Harness Validation

| Check | When | What | Failure Response |
| :--- | :--- | :--- | :--- |
| **Task graph DAG** | Before execution | No circular dependencies | Reject cycle |
| **State freshness** | Before task execution | All inputs within `MAX_STALENESS` | Reject stale state |
| **Skill side-effect declaration** | On skill registration | All outputs declared | Quarantine skill |
| **Permission chain** | Before action task | FactorPermission validated | Reject unauthorized action |
| **Shadow-only routing** | On every decision | All decisions route to shadow sink | Block if real endpoint detected |

*(Sources: `docs/verification/historical_ingestion_verification.md`, `docs/narrative/failure_and_hallucination_controls.md`, `docs/epistemic/governance/regime_ingestion_obligations.md`, `docs/contracts/execution_harness_contract.md`)*

---

## 7. Observability Success Criteria

| Criterion | Description | Status |
| :--- | :--- | :--- |
| **Glass-box** | All layers fully observable — no hidden logic | Required |
| **Zero orphans** | No unexplained data gaps for 2 weeks sustained | Phase exit criterion |
| **Idempotency** | Live signals match historical replay signals 100% for same data period | Phase exit criterion |
| **Structured logging** | All components emit JSON-structured logs | In progress |
| **Dashboard completeness** | All cognitive layers represented on dashboard | In progress |
| **Audit viewer** | Human-readable view of machine-parseable audit logs | Available (Skill #11) |

*(Source: `docs/memory/02_success/success_criteria.md`)*

---

## Legacy Source Mapping

| Section | Legacy Source Document(s) |
| :--- | :--- |
| §1 Principles | `docs/epistemic/project_intent.md`, `docs/dashboard/dashboard_truth_contract.md` |
| §2 Metrics | Component YAMLs, `docs/memory/02_success/success_criteria.md` |
| §3 Logging | `docs/us_market_engine_design.md`, `docs/epistemic/data_retention_policy.md`, `docs/epistemic/governance/scale_safety_obligations.md` |
| §4 Dashboard | `docs/dashboard/dashboard_truth_contract.md`, `docs/dashboard/temporal_truth_surface.md`, `docs/dashboard/ui_guardrails.md` |
| §5 Alerting | `docs/dashboard/alerting_rules.md` |
| §6 Validation | `docs/verification/historical_ingestion_verification.md`, `docs/narrative/failure_and_hallucination_controls.md`, `docs/epistemic/governance/regime_ingestion_obligations.md` |
| §7 Success | `docs/memory/02_success/success_criteria.md` |
