# Runtime & Execution Model

> [!IMPORTANT]
> **Authoritative Source**: `docs/memory/03_domain/domain_model.md` is CANONICAL.
> This document describes runtime *intent* — how the system is designed to behave at execution time.
> No implementation details. No scripts. No code.

---

## 1. Orchestration Principles

The system is a **human-operated, locally-hosted intelligence platform**. There is no autonomous trading, no cloud-managed orchestrator, and no event-driven microservice fabric. The runtime model is deliberately simple and observable.

**Core Principle**: The system observes, analyzes, and suggests. It does not act autonomously.

| Principle | Description |
| :--- | :--- |
| **Local-First** | All processing runs on a single Windows machine. No cloud dependencies for core logic. |
| **Batch-Primary** | US pipeline is batch-scheduled. India pipeline is streaming during market hours only. |
| **Shadow-Only Execution** | No real market orders. All execution paths terminate at logging, not at a broker endpoint. |
| **Human-Triggered Advancement** | System time (Truth Epoch) does not auto-advance. Requires explicit governance gate passage. |
| **Idempotent Re-runs** | Any pipeline stage can be re-run on the same input with identical results. |

*(Sources: `docs/contracts/execution_harness_contract.md`, `docs/epistemic/bounded_automation_contract.md`)*

---

## 2. Runtime Modes

### 2.1 Batch Mode (US Market)

The US pipeline operates as a sequence of scheduled batch jobs. Each job runs to completion, produces artifacts, and exits. There is no long-running process during non-market hours.

**Characteristics**:
- REST API polling (Alpha Vantage)
- Discrete job boundaries (one job = one data-fetch cycle)
- Strict rate limiting (token-bucket: calls/minute, calls/day)
- Failed symbols logged to retry queue for secondary pass
- Append-only raw storage; idempotent Silver/Gold rebuilds

**Scheduling Intent**:

| Job | Frequency | Trigger | Purpose |
| :--- | :--- | :--- | :--- |
| Symbol Refresh | Weekly (Monday) | Scheduled Task | Update US symbol universe from `LISTING_STATUS` |
| Daily Close Fetch | Daily (~17:00 ET) | Scheduled Task | Fetch `TIME_SERIES_DAILY_ADJUSTED` (compact) |
| Intraday Catchup | Hourly (market hours) | Scheduled Task | Fetch `TIME_SERIES_INTRADAY` (5min), rate-permitting |
| Backfill Worker | Manual trigger | Operator | Full-history fetch (`outputsize=full`), strict rate limiting |

**Execution Sequence** (per daily cycle):
1. Ingestion job fetches raw data → `data/raw/us/`
2. Normalization produces staged Parquet → `data/staging/us/`
3. Curation applies quality checks → `data/analytics/us/`
4. CTT (Canonical Truth Time) updated upon successful validation
5. TE (Truth Epoch) advancement requires separate governance gate

*(Sources: `docs/us_market_engine_design.md`, `docs/governance/truth_advancement_gates.md`)*

---

### 2.2 Streaming Mode (India Market)

The India pipeline operates as a long-running process during market hours only. It receives real-time ticks via WebSocket and aggregates them into 1-minute OHLCV candles.

**Characteristics**:
- Single WebSocket connection, ~200 instrument tokens subscribed
- Binary tick protocol (SmartAPI v2, LTP mode)
- In-memory state per symbol (SymbolState: price, volume, VWAP, HOD candle accumulation)
- Timer-based minute-boundary candle finalization (not tick-count)
- Candles persisted to Parquet on each finalization
- Momentum signal computation follows each candle batch

**Lifecycle Intent**:

| Phase | Time (IST) | Trigger | Behavior |
| :--- | :--- | :--- | :--- |
| **Start** | 09:00 | Scheduled Task | Authenticate, connect WebSocket, subscribe |
| **Market Open** | 09:15 | First ticks arrive | Begin tick aggregation and candle finalization |
| **Intraday** | 09:15–15:30 | Continuous | Tick → SymbolState → Candle → Signal pipeline |
| **Close** | 15:45 | Scheduled Task | Unsubscribe, disconnect, finalize remaining candles, run EOD review |

**Connection Resilience**:
- Auto-reconnect with exponential backoff on WebSocket disconnect
- REST fallback available if WebSocket is unstable
- Restart recovery: fetches last 5 minutes of data (overlap handled by downstream dedup)

**Capacity**:
- Max tokens per session: 1000 (current: ~200, headroom: ~800)
- Max concurrent connections: 3 per client code
- Subscription modes: LTP (1), QUOTE (2), SNAP_QUOTE (3) — currently using LTP

*(Sources: `docs/INDIA_WEBSOCKET_ARCHITECTURE.md`, `docs/contracts/RAW_ANGEL_INTRADAY_SCHEMA.md`)*

---

### 2.3 Evaluation Mode (EV-TICK)

The evaluation pipeline is a discrete, governed advancement cycle that processes validated data through the cognitive hierarchy. It is the mechanism by which the system "thinks" — advancing from raw observation to structured intelligence.

**Characteristics**:
- Triggered manually or via scheduled task
- Each tick produces a discrete window ID (`TICK-<timestamp>`)
- Strictly passive: no strategy execution, no capital allocation
- Diagnostic watchers run read-only analysis
- Every tick is logged to the evolution ledger

**EV-TICK Cycle**:
1. **Time Advancement**: Generate window ID, snapshot current CTT
2. **Data Ingestion Check**: Verify all required symbols have data at CTT
3. **Regime Context**: Compute or load regime state for the window
4. **Factor Context**: Compute observational factor state
5. **Watcher Diagnostics**: Run all passive watchers:
   - Momentum Emergence Watcher
   - Liquidity Compression Watcher
   - Expansion Transition Watcher
   - Dispersion Breakout Watcher
6. **Artifact Persistence**: Write per-tick artifacts to `docs/evolution/ticks/`
7. **Ledger Entry**: Log tick outcome to `docs/epistemic/ledger/evolution_log.md`

**Safety Invariants**:
- No import or invocation of `StrategyRunner` or `OrderManager`
- No access to `CapitalState`
- No feedback loop to parameters
- Watchers are strictly read-only

*(Sources: `docs/impact/2026-01-27__evolution__ev_tick.md`, `docs/evolution/evaluation_profiles/schema.md`)*

---

### 2.4 Shadow Execution Mode

Shadow mode is the system's mechanism for testing execution logic without real-world consequences. All execution paths terminate at a log sink, never at a broker endpoint.

**Intent**: Prove that the decision pipeline generates correct, auditable outputs under real data conditions without risking capital.

**Characteristics**:
- `ShadowExecutionSink` replaces real broker API client
- All decisions logged with full provenance (regime, factor, signal context)
- Strategy activation matrices produced per market
- Decision trace logs persisted as Parquet

**Shadow Run Artifacts**:

| Artifact | Format | Purpose |
| :--- | :--- | :--- |
| Strategy Activation Matrix | CSV | Which strategies triggered under what conditions |
| Decision Trace Log | Parquet | Full decision chain with context snapshot |
| Shadow Run Log | Markdown | Human-readable run summary with findings |

**Shadow Run Sequence**:
1. Load regime context for target market (US or India)
2. Execute bulk evaluator (all strategies against current context)
3. Execute decision replay (simulate downstream decision logic)
4. Persist artifacts per-market under shadow run ID
5. Verify safety invariants: no real execution, no broker calls, no capital state mutation

**Enforcement State Model**:

| State | Description | Impact |
| :--- | :--- | :--- |
| **SHADOW** | Logging only, no blocking | Regime does not affect any external system |
| **ENFORCED** | Live strategy gating active | Regime state gates strategy eligibility (future) |

*(Sources: `docs/irr/shadow_reality_run_log.md`, `docs/Regime_Dashboard_Runbook.md`)*

---

## 3. Execution Harness

The Execution Harness is the runtime orchestrator that transforms epistemic state into coordinated action. It is a **scheduler and enforcer**, not a decision-maker.

### 3.1 Harness Responsibilities

| Does | Does NOT |
| :--- | :--- |
| Consume epistemic state (regime, factors, beliefs) | Generate beliefs or infer regime |
| Build and resolve task dependency graph (DAG) | Optimize strategies or override permissions |
| Execute tasks in topological order | Cache or reuse stale state across cycles |
| Enforce invariants and audit every action | Make market judgments or access raw data |

### 3.2 Task Graph Model

Tasks are atomic units of work organized as a Directed Acyclic Graph (DAG). The harness resolves dependencies and executes in topological order.

**Task Outcomes**:

| Outcome | Meaning | Harness Response |
| :--- | :--- | :--- |
| `SUCCESS` | Task completed, output produced | Continue to dependent tasks |
| `SKIPPED` | Preconditions not met, no error | Log skip reason, continue |
| `FAILED` | Error during execution | Log error, evaluate failure policy |

**Precondition Checks** (before every task):
1. All required state objects present and valid
2. All required permissions granted
3. All dependency tasks completed successfully
4. Input state not stale (within `MAX_STALENESS` window)
5. Skill implementation registered and valid

### 3.3 Minimal Task Graph (V1)

```
T1: VALIDATE STATE  →  T2: CHECK REGIME  →  T3: FILTER BELIEFS  →  T4: EMIT ACTIONS
```

| Task | Purpose | Gate |
| :--- | :--- | :--- |
| **T1: Validate State** | Verify all required state present, not stale | `regime_state == None` → HALT |
| **T2: Check Regime** | Evaluate regime gate | `EVENT_LOCK` or low confidence → SKIP |
| **T3: Filter Beliefs** | Apply factor permission constraints | Remove blocked beliefs |
| **T4: Emit Actions** | Output to audit log (shadow) or orders (future) | Shadow mode: log only |

### 3.4 Harness State Machine

```
IDLE → VALIDATE → BUILD GRAPH → EXECUTE LOOP → FINALIZE → IDLE
                    ↓ (invalid)                    ↓ (task fail)
                  LOG + HALT              HANDLE FAILURE → EXECUTE LOOP
```

**Failure Handling**:

| Failure Type | Policy |
| :--- | :--- |
| Single non-critical task fails | Mark `FAILED`, continue independent tasks |
| Critical-path task fails | Mark cycle `DEGRADED`, log prominently |
| Harness-level error | HALT — require human intervention |
| Timeout exceeded | Terminate task, mark `FAILED`, continue |

### 3.5 Harness Prohibitions

| Prohibited | Correct Source |
| :--- | :--- |
| Infer regime from features | Receive from Regime (L1) |
| Override factor permissions | Receive from Factor Analysis (L4) |
| Generate beliefs from signals | Receive from Meta-Analysis (L3) |
| Cache state across cycles | Require fresh state per cycle |
| Reorder tasks for performance | Ordering is semantically meaningful |
| Batch executions across cycles | Each cycle is atomic with fresh state |

*(Source: `docs/contracts/execution_harness_contract.md`)*

---

## 4. Truth Epoch Advancement

The system's temporal heartbeat is governed by a three-gate advancement protocol. Time does not flow automatically.

### 4.1 Gate 1: Ingestion Gate (Raw → Canonical)

**Trigger**: Ingestion pipeline completion
**Outcome**: CTT (Canonical Truth Time) advancement

| Check | Description | Failure |
| :--- | :--- | :--- |
| Schema validity | All required columns present and typed | Reject ingestion |
| Temporal continuity | No unexpected gaps | Reject ingestion |
| Data integrity | No NaN/Inf, High ≥ Low, Volume ≥ 0 | Reject ingestion |
| Drift check | Price change < circuit breaker threshold | Manual review required |

### 4.2 Gate 2: Intelligence Gate (Canonical → Evaluation)

**Trigger**: Intelligence / decision engine run
**Outcome**: TE (Truth Epoch) advancement

| Check | Description | Failure |
| :--- | :--- | :--- |
| Data completeness | All required symbols at CTT ≥ target TE | System halt |
| Epistemic health | No critical audit alerts, inspection mode inactive | System halt |
| Policy compliance | Strategy eligibility checks pass | System halt |

### 4.3 Gate 3: Global Synchronization (Cross-Market)

| Check | Description | Failure |
| :--- | :--- | :--- |
| Market alignment | `abs(TE_US - TE_INDIA) ≤ 1 Day` | Warn operator, allow independent operation |

### 4.4 Emergency Override

Manual TE advancement or rollback is permitted only with:
- Stringent justification logged in audit
- Explicit CLI confirmation flag
- Operator attribution recorded

### 4.5 Truth Epoch Definition

Each Truth Epoch is bound to the Proxy Set version that generated it.

| Rule | Description |
| :--- | :--- |
| **Version Lock** | Every `truth_epoch.json` includes the `proxy_set_version` used |
| **Invalidation on Change** | Proxy Set definition change invalidates prior TE for forward use |
| **Historical Preservation** | Old definitions and epochs preserved in evolution log |

*(Sources: `docs/governance/truth_advancement_gates.md`, `docs/epistemic/truth_epoch_scoping.md`)*

---

## 5. Automation Limits

### 5.1 Current Phase: Passive Automation Only

The system operates under a **Bounded Automation Contract**. Monitors may observe and suggest but must never act.

| Constraint | Description |
| :--- | :--- |
| **Read-Only** | Monitors read filesystem only; never write to business data paths |
| **No Side Effects** | No alert muting, file deletion, or external API calls |
| **Suggestion Logging** | Only valid output: `[SUGGESTION]` log entry (INFO/WARN) |
| **Idempotent** | Running a monitor 100x has identical state to running 1x |

### 5.2 Escalation Protocol

When a monitor detects a critical state (drift, stalling, failure):
1. Log a high-priority suggestion
2. Rely on human operator (via Audit Log Viewer) to see and act

### 5.3 Graduation Criteria (Passive → Active)

A passive monitor may graduate to an active automator only when:
1. Passive mode sustained > 1 week with 100% suggestion accuracy
2. Specific Decision Ledger entry authorizes the upgrade
3. Bounded Automation Contract updated to allow the exception

*(Source: `docs/epistemic/bounded_automation_contract.md`)*

---

## 6. Operator Workflow

### 6.1 Start of Day (SOD)

**Trigger**: ~08:30 IST (Market Open − 45 minutes)
**Owner**: Operator (Human)

| Step | Action |
| :--- | :--- |
| 1 | Verify network, API credits, disk space |
| 2 | Start ingestion process |
| 3 | Start momentum engine (if applicable) |
| 4 | Verify logs for immediate errors |
| 5 | Verify `data/raw/` is populating |
| 6 | Log "SOD Complete" in daily journal |

### 6.2 End of Day (EOD)

**Trigger**: ~15:45 IST (Market Close + 15 minutes)
**Owner**: Operator (Human)

| Step | Action |
| :--- | :--- |
| 1 | Gracefully stop ingestion and momentum processes |
| 2 | Check orphan count (failed processing events) |
| 3 | Verify decision artifacts for today |
| 4 | Archive daily data |
| 5 | Generate change summary |
| 6 | Log "EOD Complete" in daily journal |

### 6.3 Post-Market Intelligence Run

**Trigger**: After EOD data validation complete
**Owner**: Operator (Human)

| Step | Action |
| :--- | :--- |
| 1 | Run narrative engine (per market) |
| 2 | Run decision engine (per market) |
| 3 | Review dashboard for regime state |
| 4 | Review strategy suitability matrix |
| 5 | Advance TE if all gates pass |

*(Sources: `docs/runbooks/start_of_day.md`, `docs/runbooks/end_of_day.md`)*

---

## 7. Dashboard Runtime Contract

The dashboard is a **read-only observability surface**. It renders system state for human consumption but has zero authority over execution.

### 7.1 Runtime Components

| Component | Runtime | Port | Role |
| :--- | :--- | :--- | :--- |
| Backend API | Python / FastAPI | 8000 | Serves read-only JSON endpoints |
| Frontend | Vite / React | 5173 | Renders dashboard UI |

### 7.2 Dashboard Behavioral Rules

| Rule | Description |
| :--- | :--- |
| Read-only | No mutation endpoints exposed |
| Staleness visible | Stale data greys out affected UI components |
| Provenance visible | Exact tickers used in proxy roles displayed |
| Enforcement state visible | SHADOW vs ENFORCED clearly labeled |
| No execution controls | Dashboard cannot trigger ingestion, evaluation, or trading |

### 7.3 Dashboard Staleness States

| Status | Meaning | Operator Action |
| :--- | :--- | :--- |
| ACTIVE | System healthy, data current | None |
| LATE | Update delayed | Monitor |
| STALE | Data not updating | **Do not trust regime** |

*(Sources: `docs/Regime_Dashboard_Runbook.md`, `docs/dashboard/api_schema.md`)*

---

## 8. Skill Registration Model

Skills are registered implementations that the harness invokes. Registration is governed and auditable.

### 8.1 Registration Requirements

| Requirement | Purpose |
| :--- | :--- |
| Unique skill ID + version | Identity and traceability |
| Declared task types | Harness knows what the skill handles |
| Declared required inputs | Harness validates inputs before invocation |
| Declared permissions needed | Harness checks factor permissions |
| Declared side effects | Harness coordinates writes, prevents conflicts |
| Decision Ledger reference | Governance authorization |

### 8.2 Skill Invariants

| Invariant | Description |
| :--- | :--- |
| No upstream inference | Skill does not infer state it should receive |
| No permission bypass | Skill respects factor layer constraints |
| All side effects declared | Undeclared writes trigger quarantine |
| Idempotent | Same input → same output |
| Decision-authorized | Decision Ledger entry required for registration |

### 8.3 Skill Lifecycle

```
REGISTERED → ACTIVE → DEPRECATED → REMOVED
```

- Each transition requires a Decision Ledger entry
- `DEPRECATED` skills still invocable but flagged for removal
- `REMOVED` skills are never invoked

### 8.4 Violation Handling

| Violation | Response |
| :--- | :--- |
| Undeclared output | Quarantine skill, halt cycle |
| Permission bypass | Reject execution, log violation |
| Layer bypass | Quarantine skill, require review |
| Timeout | Terminate, mark failed, continue |
| Repeated violations | Permanent deregistration |

*(Source: `docs/contracts/execution_harness_contract.md`)*

---

## 9. Cross-Pipeline Invariants

| Invariant | Applicability | Description |
| :--- | :--- | :--- |
| **Market Separation** | All pipelines | US and India pipelines are physically distinct. No shared state. |
| **Event Time Integrity** | All processing | All logic proceeds on event time. System clock (`datetime.now()`) is never used for business logic. |
| **No Lookahead** | All processing | Core abstractions physically prevent access to future data. |
| **Idempotency** | All stages | Re-running on same input produces identical output. |
| **Shadow Enforcement** | Execution | No real market interaction until explicit graduation from shadow mode. |
| **No Autonomous TE Advancement** | Orchestration | Truth Epoch requires human-triggered governance gate passage. |
| **Append-Only Audit** | All execution | Audit logs are append-only. No deletion, no mutation. |
| **Proxy Versioning** | Evaluation | Truth Epoch is scoped to the proxy set version that generated it. |

---

## Legacy Source Mapping

| Section | Legacy Source Document(s) |
| :--- | :--- |
| §1 Orchestration | `docs/contracts/execution_harness_contract.md`, `docs/epistemic/bounded_automation_contract.md` |
| §2.1 Batch (US) | `docs/us_market_engine_design.md` §5 |
| §2.2 Streaming (India) | `docs/INDIA_WEBSOCKET_ARCHITECTURE.md` |
| §2.3 EV-TICK | `docs/impact/2026-01-27__evolution__ev_tick.md` |
| §2.4 Shadow Mode | `docs/irr/shadow_reality_run_log.md`, `docs/Regime_Dashboard_Runbook.md` |
| §3 Harness | `docs/contracts/execution_harness_contract.md` |
| §4 Truth Advancement | `docs/governance/truth_advancement_gates.md`, `docs/epistemic/truth_epoch_scoping.md` |
| §5 Automation | `docs/epistemic/bounded_automation_contract.md` |
| §6 Operator Workflow | `docs/runbooks/start_of_day.md`, `docs/runbooks/end_of_day.md` |
| §7 Dashboard | `docs/Regime_Dashboard_Runbook.md`, `docs/dashboard/api_schema.md` |
| §8 Skills | `docs/contracts/execution_harness_contract.md` §7 |
| §9 Invariants | `docs/epistemic/architectural_invariants.md`, `docs/governance/temporal_truth_contract.md` |
