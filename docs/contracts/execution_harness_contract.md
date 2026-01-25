# Execution Harness Contract

**Status:** Constitutional — Binding  
**Scope:** Execution Architecture  
**Authority:** This document defines how execution happens. Violating skills are rejected, not accommodated.

---

## 1. Role of the Execution Harness

### What the Execution Harness Does

The Execution Harness is the **runtime orchestrator** that transforms epistemic state into coordinated action. It is a **scheduler and enforcer**, not a decision-maker.

| Responsibility | Description |
|:---------------|:------------|
| **Consume Epistemic State** | Read regime, factor, signal, and belief states from upstream layers |
| **Build Task Graph** | Construct an ordered graph of executable tasks based on current state |
| **Resolve Dependencies** | Ensure tasks execute only when preconditions are satisfied |
| **Execute Tasks** | Invoke skill implementations in correct order |
| **Enforce Invariants** | Reject tasks that violate layer interaction contract |
| **Audit Trail** | Log every decision, skip, and execution with full provenance |

### What the Execution Harness Does NOT Do

| Anti-Pattern | Why It's Prohibited |
|:-------------|:--------------------|
| Generate beliefs | Beliefs come from Belief Layer (L9). Harness receives, does not create. |
| Infer regime | Regime comes from Regime Layer (L6). Harness receives, does not infer. |
| Optimize strategies | Strategy selection is Strategy Layer (L10). Harness executes, does not optimize. |
| Override permissions | Factor permissions are constraints. Harness enforces, does not relax. |
| Cache and reuse stale state | Every execution cycle receives fresh state snapshots. |
| Make market judgments | The harness is market-agnostic. It knows tasks, not tickers. |

> **Guiding Principle:** The execution harness is powerful only because it is obedient.

---

## 2. Inputs to the Harness

### State Objects the Harness May Read

| State Object | Source Layer | Required | Contents |
|:-------------|:-------------|:---------|:---------|
| `RegimeState` | L6 (Regime) | ✅ Yes | behavior, bias, confidence, is_stable |
| `FactorPermission` | L6.5 (Factor) | ⚠️ When implemented | permitted flags, exposure limits |
| `SignalSet` | L8 (Signal) | ✅ Yes | active signals with context |
| `BeliefSet` | L9 (Belief) | ✅ Yes | synthesized beliefs with conviction |
| `MacroState` | L5.5 (Macro) | ⏸️ Latent | macro environment (when available) |
| `FlowState` | L5.7 (Flow) | ⏸️ Latent | flow conditions (when available) |

### Expected Formats

All state objects MUST be:

1. **Immutable** — Frozen after creation, no modification during execution
2. **Timestamped** — Include creation timestamp for staleness detection
3. **Context-Wrapped** — Include upstream context (regime carries macro, signal carries regime)
4. **Serializable** — JSON-compatible for audit logging

```python
class HarnessInput:
    timestamp: datetime           # When this input bundle was assembled
    regime_state: RegimeState     # Required
    factor_permission: Optional[FactorPermission]  # When implemented
    active_beliefs: List[Belief]  # From Belief Layer
    
    def is_valid(self) -> bool:
        """Validate all required fields are present and not stale."""
        ...
```

### Semantics of "Unknown" States

| Condition | Harness Behavior |
|:----------|:-----------------|
| `regime_state` is None | **HALT** — Cannot execute without regime context |
| `regime_state.confidence < MIN_THRESHOLD` | **DEGRADE** — Execute with reduced scope, log warning |
| `factor_permission` is None (not implemented) | **ASSUME PERMISSIVE** — Log that factor layer is bypassed |
| `beliefs` is empty | **SKIP** — Nothing to execute, log clean exit |
| Any state older than `MAX_STALENESS` | **REJECT** — Refuse to execute on stale data |

---

## 3. Task Graph Model

### Definition of a Task

A **Task** is an atomic unit of work that the harness schedules and executes. Tasks do NOT contain market logic — they invoke skills that contain market logic.

```python
class Task:
    task_id: str                  # Unique identifier (UUID)
    task_type: str                # e.g., "signal_scan", "belief_synthesis", "order_submit"
    skill_ref: str                # Reference to skill that implements this task
    
    # Preconditions
    required_state: List[str]     # State objects that must be present
    required_permissions: List[str]  # Permissions that must be granted
    depends_on: List[str]         # Task IDs that must complete first
    
    # Execution
    inputs: Dict[str, Any]        # Inputs passed to the skill
    timeout_ms: int               # Maximum execution time
    
    # Outputs
    output_schema: str            # Expected output type
    side_effects: List[str]       # Declared side effects (e.g., "write_to_audit_log")
```

### Preconditions

Before executing a task, the harness MUST verify:

| Precondition | Check |
|:-------------|:------|
| **State Presence** | All `required_state` objects are present and valid |
| **Permission Granted** | All `required_permissions` are satisfied by current FactorPermission |
| **Dependencies Complete** | All `depends_on` tasks have completed successfully |
| **Not Stale** | Input state timestamps are within `MAX_STALENESS` window |
| **Skill Registered** | `skill_ref` maps to a registered, valid skill |

### Outputs

Tasks produce **one of three outcomes**:

| Outcome | Meaning | Harness Action |
|:--------|:--------|:---------------|
| `SUCCESS` | Task completed, output produced | Continue to dependent tasks |
| `SKIPPED` | Preconditions not met, no error | Log skip reason, continue |
| `FAILED` | Error during execution | Log error, evaluate failure policy |

### Dependency Resolution

The harness builds a **Directed Acyclic Graph (DAG)** of tasks:

```
    ┌─────────────┐
    │ regime_check│
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │ signal_scan │
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │belief_synth │
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │ order_prep  │
    └─────────────┘
```

**Resolution Rules:**
- Tasks with no dependencies execute first
- A task executes only when ALL dependencies have `SUCCESS` or `SKIPPED` status
- Circular dependencies are **rejected at graph construction time**

### Failure Handling

| Failure Type | Policy |
|:-------------|:-------|
| Single task fails | Mark task `FAILED`, continue with tasks that don't depend on it |
| Critical path task fails | Mark entire execution cycle `DEGRADED`, log prominently |
| Harness-level error | **HALT** — Stop all execution, require human intervention |
| Timeout exceeded | Terminate task, mark `FAILED`, log timeout |

---

## 4. Execution Rules

### Task Ordering

Tasks execute in **topological order** based on the DAG:

1. All tasks with zero dependencies are candidates for execution
2. Among candidates, execute in **declaration order** (deterministic)
3. After each completion, re-evaluate candidates
4. Continue until all tasks are complete or blocked

**Parallelism Rule:** The harness MAY execute independent tasks in parallel, but MUST ensure:
- No shared mutable state between parallel tasks
- Audit log preserves causal ordering

### Conditional Execution

Tasks may declare **conditional gates**:

```python
class ConditionalGate:
    condition: str              # e.g., "regime.behavior == 'TRENDING_NORMAL_VOL'"
    if_true: str                # Task ID to execute if true
    if_false: str               # Task ID to execute if false, or "SKIP"
```

**Rules:**
- Conditions reference state objects, not task outputs
- Conditions MUST NOT contain market logic (e.g., no "if price > 100")
- Conditions are evaluated **before** task execution, not during

### Skipping Logic

A task is skipped (not executed, not failed) when:

| Condition | Skip Reason |
|:----------|:------------|
| Permission denied | Factor layer blocked this task type |
| State missing | Required upstream state is None |
| Confidence too low | Regime or belief confidence below threshold |
| Explicit skip gate | Conditional gate evaluates to SKIP |

**Skip Logging:**
Every skip MUST be logged with:
- Task ID
- Skip reason
- State snapshot at skip time

### Idempotency Rules

The harness enforces **execution idempotency**:

| Rule | Enforcement |
|:-----|:------------|
| Same input → Same execution graph | Given identical state, harness produces identical task graph |
| Re-running same cycle is safe | If a cycle is interrupted and rerun, no duplicate side effects |
| Task IDs include input hash | Tasks are identified by (task_type, input_hash) to detect duplicates |

---

## 5. Prohibited Behaviors

### What the Harness Must NEVER Infer

| Prohibited Inference | Correct Source |
|:---------------------|:---------------|
| Regime from features | Receive from Regime Layer |
| Factor permissions from regime | Receive from Factor Layer |
| Beliefs from signals | Receive from Belief Layer |
| Market direction | Receive from Signal/Belief Layer |
| Optimal position size | Receive from Optimization Layer |

**Enforcement:** The harness has no access to raw market data. It receives pre-computed state objects only.

### What the Harness Must NEVER Override

| Prohibition | Rationale |
|:------------|:----------|
| Factor permission denial | Factor Layer is the authority on exposure constraints |
| Regime-blocked execution | Regime Layer is the authority on "is it safe to play" |
| Belief confidence threshold | Belief Layer is the authority on conviction |
| Staleness rejection | Time integrity is a system safety property |

**Enforcement:** Override attempts trigger `HARNESS_VIOLATION` audit event and immediate halt.

### What the Harness Must NEVER Optimize

| Anti-Pattern | Why It's Wrong |
|:-------------|:---------------|
| Reorder tasks for performance | Ordering is semantically meaningful, not just performance |
| Batch executions across cycles | Each cycle is an atomic unit with fresh state |
| Cache state across cycles | Staleness detection requires fresh reads |
| Prune "unnecessary" tasks | Task graph is authoritative; harness has no pruning authority |

---

## 6. Minimal v1 Task Graph

The smallest meaningful task graph that respects all constraints:

```
┌─────────────────────────────────────────────────────────────────┐
│                     V1 MINIMAL TASK GRAPH                       │
└─────────────────────────────────────────────────────────────────┘

     ┌──────────────┐
     │ T1: VALIDATE │  Verify all required state is present
     │    STATE     │  Verify nothing is stale
     └──────┬───────┘  Verify regime confidence meets threshold
            │
            ▼
     ┌──────────────┐
     │ T2: CHECK    │  Evaluate regime gate
     │   REGIME     │  If EVENT_LOCK or UNDEFINED with low conf → SKIP REST
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐
     │ T3: FILTER   │  Apply factor permissions (when implemented)
     │   BELIEFS    │  Remove beliefs blocked by factor constraints
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐
     │ T4: EMIT     │  For each surviving belief, emit to audit log
     │   ACTIONS    │  In shadow mode: log only, no execution
     └──────────────┘
```

### Why Each Node Exists

| Task | Justification |
|:-----|:--------------|
| **T1: VALIDATE STATE** | EXE-1, EXE-2 require context presence. Staleness rejection is architectural invariant. |
| **T2: CHECK REGIME** | Regime gating is the core purpose of the Regime Layer. Cannot be skipped. |
| **T3: FILTER BELIEFS** | Factor Layer constrains what beliefs can proceed. Prepares for future implementation. |
| **T4: EMIT ACTIONS** | The terminal action. In shadow mode, "emit" means log. In live mode, "emit" means order. |

### V1 Scope Limitations

| What V1 Does | What V1 Does NOT Do |
|:-------------|:--------------------|
| Validate state | Generate signals |
| Check regime gate | Synthesize beliefs |
| Log actions | Execute orders |
| Respect permissions | Size positions |

V1 is a **harness skeleton** that proves the architecture before adding complexity.

---

## 7. Contract with Future Skills

### How New Skills Plug In

Skills are **registered implementations** that the harness invokes. Registration requires:

```python
class SkillRegistration:
    skill_id: str                 # Unique identifier
    skill_version: str            # Semantic version
    
    # Interface Declaration
    task_types: List[str]         # Task types this skill handles
    required_inputs: List[str]    # State objects skill needs
    output_schema: str            # What skill produces
    
    # Constraints Declaration
    requires_permissions: List[str]  # Factor permissions needed
    layer_dependencies: List[str]    # Upstream layers skill depends on
    side_effects: List[str]          # What skill writes (e.g., "audit_log", "signal_db")
    
    # Metadata
    author: str
    decision_ledger_ref: str      # D00X entry authorizing this skill
```

### What Skills Must Declare

| Declaration | Purpose |
|:------------|:--------|
| `required_inputs` | Harness verifies inputs are present before invocation |
| `requires_permissions` | Harness checks factor permissions before invocation |
| `layer_dependencies` | Harness validates no layer bypass |
| `side_effects` | Harness coordinates writes, prevents conflicts |

**Undeclared Side Effects Are Violations:**
If a skill writes to a resource it didn't declare, the harness MUST:
1. Log `SKILL_VIOLATION` event
2. Quarantine skill for review
3. Halt execution cycle

### Skill Invariants

Every skill MUST obey:

| Invariant | Enforcement |
|:----------|:------------|
| `SK-1`: Skill does not infer upstream state | Code review + runtime validation |
| `SK-2`: Skill does not bypass factor permissions | Harness pre-check |
| `SK-3`: Skill declares all side effects | Runtime monitoring |
| `SK-4`: Skill is idempotent | Testing requirement |
| `SK-5`: Skill has Decision Ledger authorization | Registration gate |

### How Violations Are Handled

| Violation Type | Response |
|:---------------|:---------|
| Undeclared output | Quarantine skill, log violation, halt cycle |
| Permission bypass attempt | Reject execution, log violation, continue cycle |
| Layer bypass detected | Quarantine skill, log violation, require review |
| Timeout exceeded | Terminate skill, mark failed, continue cycle |
| Repeated violations | Permanent skill deregistration |

### Skill Lifecycle

```
REGISTERED → ACTIVE → DEPRECATED → REMOVED
     │          │          │
     │          │          └── Skill no longer invoked
     │          └── Decision Ledger deprecation entry
     └── Decision Ledger authorization entry
```

---

## Appendix A: Harness State Machine

```
┌─────────┐
│  IDLE   │ ◄───────────────────────────────────────┐
└────┬────┘                                         │
     │ Receive HarnessInput                         │
     ▼                                              │
┌─────────┐                                         │
│VALIDATE │ ──── State invalid ──► [LOG + HALT] ───┘
└────┬────┘
     │ State valid
     ▼
┌─────────┐
│  BUILD  │  Construct task DAG
│  GRAPH  │
└────┬────┘
     │
     ▼
┌─────────┐
│ EXECUTE │ ──── Task fails ──► [HANDLE FAILURE]
│  LOOP   │ ◄───────────────────────────┘
└────┬────┘
     │ All tasks complete
     ▼
┌─────────┐
│ FINALIZE│  Write audit log, return to IDLE
└─────────┘
```

---

## Appendix B: Cross-Reference to Epistemic Documents

| Harness Behavior | Epistemic Authority |
|:-----------------|:--------------------|
| Regime gate enforcement | [Regime_Taxonomy.md](file:///c:/GIT/TraderFund/docs/Regime_Taxonomy.md) |
| Factor permission checking | [factor_layer_policy.md](file:///c:/GIT/TraderFund/docs/epistemic/factor_layer_policy.md) |
| Layer bypass prohibition | [layer_interaction_contract.md](file:///c:/GIT/TraderFund/docs/contracts/layer_interaction_contract.md) |
| Execution invariants (EXE-1 to EXE-4) | [layer_interaction_contract.md](file:///c:/GIT/TraderFund/docs/contracts/layer_interaction_contract.md) |
| Staleness rejection | [architectural_invariants.md](file:///c:/GIT/TraderFund/docs/epistemic/architectural_invariants.md) |

---

## Version History

| Version | Date | Changes |
|:--------|:-----|:--------|
| v1.0 | 2026-01-24 | Initial Execution Harness Contract |
