# Trust & Security Model

> [!IMPORTANT]
> **Authoritative Source**: `docs/memory/03_domain/domain_model.md` is CANONICAL.
> This document describes trust boundaries, access assumptions, credential handling, and user separation.
> Intent only. No implementation.

---

## 1. Core Trust Principles

The system operates on a principle of **progressive trust** — nothing is trusted by default; trust is earned through observation, validation, and governance gates.

| Principle | Description |
| :--- | :--- |
| **Trust is Earned, Not Assumed** | Research modules, strategies, and data sources must prove themselves before promotion |
| **Capital Preservation Supremacy** | Capital protection always overrides feature velocity |
| **Human Authority is Final** | Humans are the supreme authority on all specifications and decisions |
| **Fail Closed** | Unknown trust state → deny access, not grant default access |
| **Audit Everything** | All actions, decisions, and state transitions are logged with provenance |

*(Sources: `docs/governance/RESEARCH_MODULE_GOVERNANCE.md`, `docs/epistemic/bounded_automation_contract.md`)*

---

## 2. Trust Domains

### 2.1 Execution Trust

| Property | Current State | Invariant |
| :--- | :--- | :--- |
| Live Execution | **FORBIDDEN** | `INV-NO-EXECUTION` — System does not execute trades |
| Capital Movement | **FORBIDDEN** | `INV-NO-CAPITAL` — System does not move money |
| Self-Promotion | **FORBIDDEN** | `INV-NO-SELF-ACTIVATION` — System cannot promote itself to production |
| Execution Requires | Explicit human sign-off AND governance gate passage | Non-negotiable |

### 2.2 Data Trust

| Data Source | Trust Level | Treatment |
| :--- | :--- | :--- |
| **External API responses** (Alpha Vantage, Angel One) | **UNTRUSTED** | Must be validated (schema, range, continuity) before canonical acceptance |
| **Raw data layer (Bronze)** | **UNTRUSTED** | Append-only; may contain duplicates, gaps, or errors |
| **Canonical data store (Silver)** | **TRUSTED within system** | Validated, deduplicated, schema-conforming |
| **Derived analytics (Gold)** | **Conditionally trusted** | Trust depends on upstream canonical completeness |
| **Synthetic / Surrogate data** | **LABELED DISTRUST** | Must be explicitly marked ("SURROGATE" / "SYNTHETIC") in all surfaces |

**Temporal Trust Rule**: The system only "knows" about time up to the declared Truth Epoch (TE). Time beyond TE is epistemically invisible.

### 2.3 Module Trust (Research → Production Path)

Research modules exist in an isolated sandbox and must earn their way to production through a multi-gate process:

| Gate | Requirement | Purpose |
| :--- | :--- | :--- |
| **Observation** | 30 trading days error-free in Research state | Prove stability |
| **Paper Trading** | 100 consecutive simulated trades with < 5% slippage variance | Prove accuracy |
| **Human Approval** | Explicit architectural sign-off in `ACTIVATION_LOG.md` | Prove intent |
| **Coverage** | ≥ 90% unit test coverage + integration tests pass | Prove reliability |
| **Single PR** | Promotion via dedicated PR tagged `[PROMOTION]` | Prove traceability |

**Promotion is Reversible**: Anomalous behavior → immediate revert to Research-Only via global kill-switch.

### 2.4 Strategy Trust

| Trust Level | Description | Allowed Actions |
| :--- | :--- | :--- |
| **REGISTERED** | Strategy exists in registry | Metadata only |
| **EVALUATED** | Strategy has evaluation results | Shadow execution |
| **SHADOW_ACTIVE** | Strategy produces shadow decisions | Paper trading only |
| **PRODUCTION** | Strategy is live | NOT AVAILABLE in current phase |

No strategy may auto-promote itself. All trust transitions require Decision Ledger entries.

*(Sources: `docs/governance/RESEARCH_MODULE_GOVERNANCE.md`, `docs/memory/11_deployment/evolution.md`)*

---

## 3. Safety Invariants

These invariants are the bedrock security guarantees. Violation of any invariant requires immediate system halt.

| ID | Invariant | Description | Severity |
| :--- | :--- | :--- | :--- |
| `INV-NO-EXECUTION` | No Execution | System does not execute trades | **ABSOLUTE** |
| `INV-NO-CAPITAL` | No Capital | System does not move money | **ABSOLUTE** |
| `INV-NO-SELF-ACTIVATION` | No Self-Activation | System cannot promote itself to production | **ABSOLUTE** |
| `INV-PROXY-CANONICAL` | Proxy Canonical | All market data must come through canonical proxies | **ABSOLUTE** |
| `INV-TRUTH-EPOCH-EXPLICIT` | Truth Epoch Explicit | TE is never inferred from system clock | **ABSOLUTE** |
| `INV-NO-TEMPORAL-INFERENCE` | No Temporal Inference | "now" and "today" are banned concepts | **ABSOLUTE** |
| `INV-HONEST-STAGNATION` | Honest Stagnation | System admits when it has no new information | **ABSOLUTE** |

*(Sources: `docs/epistemic/architectural_invariants.md`, existing trust.md)*

---

## 4. Access Controls

### 4.1 Physical Isolation

| Boundary | Rule | Rationale |
| :--- | :--- | :--- |
| **Research ↔ Production** | Research modules reside in `research_modules/`; no imports from `core_modules/` | Prevents accidental inclusion in production |
| **Market ↔ Market** | US and India data pipelines share no runtime state | `INV-MARKET-SEPARATION` |
| **Intelligence ↔ Execution** | Intelligence layer produces beliefs; execution harness consumes but cannot modify them | Separation of concerns |
| **Dashboard ↔ System** | Dashboard is read-only; no write path exists from UI to system state | Observatory principle |
| **Shadow ↔ Real** | Shadow execution sinks produce artifacts that can never reach real broker endpoints | Capital protection |

### 4.2 Layer Authority Matrix

| Layer | May Read | May Write | May NOT Touch |
| :--- | :--- | :--- | :--- |
| **Ingestion (L0)** | External APIs, raw files | Raw data store | Canonical store, analytics |
| **Regime (L1)** | Canonical data | Regime state | Strategy decisions, execution |
| **Narrative (L2)** | Regime state, events | Narrative artifacts | Strategies, execution |
| **Strategy (L5)** | All upstream beliefs | Shadow decision proposals | Broker APIs, capital state |
| **Dashboard** | All read-only API endpoints | Nothing | Everything writable |
| **Governance** | Everything | Holds, suppressions, audit logs | Code logic, capital |

### 4.3 Skill Authority Hierarchy

All system skills operate within a strict precedence:

| Level | Authority | Description |
| :--- | :--- | :--- |
| **1 (Supreme)** | Human Decision | Humans decide; skills cannot override |
| **2** | Append-Only Ledger | Historical truth; skills may append, not modify |
| **3** | Structural Integrity | Format and consistency enforcement |
| **4** | Advisory | Recommendations and flags only |

**Skill Security Rules**:
- No skill may override a document or decision from a higher authority level
- No skill may escalate its own authority level
- All unresolvable conflicts escalate to human judgment
- No skill executes trades, allocates capital, or self-activates

*(Sources: `docs/epistemic/skills/skills_catalog.md`, `docs/dashboard/ui_guardrails.md`)*

---

## 5. Credential Handling

### 5.1 External API Credentials

| Vendor | Authentication Model | Storage | Rotation |
| :--- | :--- | :--- | :--- |
| **Alpha Vantage** | API key (stateless) | `.env` file (local, gitignored) | Pool of keys; daily rate limit per key |
| **Angel One SmartAPI** | Session-based (login → token) | `.env` file for client ID/PIN/TOTP; session token in memory | Token refreshed on each scheduler restart |

### 5.2 Credential Security Rules

| Rule | Description |
| :--- | :--- |
| **No hardcoded credentials** | All API keys and secrets stored in `.env`, never in source code |
| **`.env` is gitignored** | Environment file excluded from version control |
| **Drift detection** | Drift Detector compares `.env` against `.env.example` for key presence and type |
| **Memory-only tokens** | Session tokens (Angel One) held in process memory; discarded on exit |
| **No credential sharing** | Each operator instance uses its own credential set |
| **Credential rotation** | API keys rotated when rate limits change; session tokens refreshed on restart |

### 5.3 Forbidden Credential Behaviors

| Behavior | Status |
| :--- | :--- |
| Committing `.env` to Git | **FORBIDDEN** |
| Loading broker trading credentials | **FORBIDDEN** (`INV-NO-EXECUTION`) |
| Passing credentials across market boundaries | **FORBIDDEN** |
| Auto-rotating credentials without operator awareness | **FORBIDDEN** |
| Using credentials in research modules | **FORBIDDEN** |

*(Sources: `docs/INDIA_WEBSOCKET_ARCHITECTURE.md`, `docs/verification/historical_ingestion_verification.md`)*

---

## 6. Operator Model & User Separation

### 6.1 Operator Authority

| Authority | Description |
| :--- | :--- |
| **Specifications** | Humans are final authority on all specifications and decisions |
| **Governance Holds** | Only operators can release governance holds |
| **Kill Switches** | Operator-accessible at all times; three-tier hierarchy (Global, Family, Strategy) |
| **Truth Advancement** | Only operators can advance Truth Epoch through gate passage |
| **Module Promotion** | Only operators can promote research modules to production |
| **Credential Management** | Only operators manage `.env` and credential rotation |

### 6.2 Kill-Switch Hierarchy

| Level | Reach | Trigger | Reset Authority |
| :--- | :--- | :--- | :--- |
| **Global** | ALL system activity | Manual operator command; drawdown > 10%; 3+ consecutive data integrity failures | **Human only** — diagnose root cause, modify state file, restart services |
| **Family** | Specific strategy family | Family drawdown > 3%; manual operator command | **Human only** |
| **Strategy** | Specific strategy ID | Strategy drawdown > 2%; 3 consecutive stop-losses (symbolic) | **Human only** |

**No automated resets are permitted for ANY kill-switch activation.**

### 6.3 Chat Execution Contract (AI Interface Security)

The chat interface has strict security boundaries:

| Rule | Description |
| :--- | :--- |
| **Chat Only Drafts** | Chat may draft commands but has ZERO execution authority |
| **Human Confirmation** | All chat-drafted commands require explicit yes/no in CLI bridge |
| **No Silent Execution** | Running any command without user notification is forbidden |
| **No Auto-Correction** | Cannot modify a command after human has seen it |
| **No Hidden Chaining** | Cannot silently trigger secondary commands |
| **No Privilege Escalation** | Cannot use bridge to run commands outside `bin/run-skill` scope |

### 6.4 Multi-Human Governance

| Scenario | Resolution Policy |
| :--- | :--- |
| **Conflicting updates to same artifact** | "Freshness Rule" — update from most recent `main` state takes precedence |
| **Disagreement on foundational documents** | "Maintainer Veto" — original author holds veto power |
| **Overrule of veto** | Requires Decision Ledger entry signed by quorum or Project Owner |
| **Operator attribution** | All governance actions attributed to the acting operator |

*(Sources: `docs/epistemic/chat_execution_contract.md`, `docs/epistemic/impact_resolution_contract.md`, `docs/capital/kill_switch.md`)*

---

## 7. Survivability Obligations

The Scale & Safety Plane defines non-negotiable survivability guarantees that must be satisfied before any execution capability opens:

| Obligation | Description | Status |
| :--- | :--- | :--- |
| `OBL-SS-KILLSWITCH` | Global halt mechanism — reachable from any state, independent of processing | Binding |
| `OBL-SS-BOUNDS` | Hard execution limits — MAX_ACTIVE_STRATEGIES, MAX_EXECUTION_FREQUENCY, etc. | Binding |
| `OBL-SS-DETERMINISM` | Same input → same output regardless of load; race-free, reproducible | Binding |
| `OBL-SS-CIRCUIT` | Safe degradation — non-critical paths shut down first; no cascading failures | Binding |
| `OBL-SS-AUDIT` | Bounded, governed audit at scale — no data loss, bounded ledger growth | Binding |
| `OBL-SS-CLOSURE` | All above SATISFIED before any execution plane opens | Binding |

**Decision Plane Execution Guarantee** (`OBL-DE-NO-EXEC`): The system must provably prevent broker API calls, order placement, capital movement, position modification, and any market interaction. Verification requires static analysis showing no broker imports and no network calls to trading endpoints.

*(Sources: `docs/epistemic/governance/scale_safety_obligations.md`, `docs/epistemic/governance/decision_plane_obligations.md`)*

---

## 8. Data Deletion & Retention Security

| Category | Retention | Deletion Authority |
| :--- | :--- | :--- |
| **Epistemic Artifacts** (narratives, decisions, ledgers) | **PERMANENT** | NEVER deleted; may archive after 3 years |
| **Audit Logs** (JSON logs) | 90 days active → 1 year archive → delete | Human approval + drift detector flag |
| **Raw Input Data** | 1 year active → cold storage | Human approval required |
| **Derived Data** (cache, intermediates) | Volatile — regenerable | Standard cleanup |

**Deletion Protocol**: Use of `rm` or `delete` on covered paths requires:
1. Verification against retention policy
2. Human approval (via Drift Detector flag or explicit command)

*(Source: `docs/epistemic/data_retention_policy.md`)*

---

## 9. Research Module Security Guardrails

| Guardrail | Description | Rationale |
| :--- | :--- | :--- |
| **Physical Isolation** | Must reside in `research_modules/` | Prevents production contamination |
| **Import Barrier** | No `core_modules/` imports | Production code unaware of research existence |
| **Execution Isolation** | No runtime hooks or callbacks | Cannot enter main event loop |
| **Runtime Kill-Switch** | `ACTIVE_PHASE` check on side-effecting methods | `SecurityException` if `PHASE < 6` |
| **Configuration Guard** | Explicit `ENABLED` flag defaulting to `FALSE` | No accidental activation |
| **Warning Headers** | Mandatory code headers | Every file: `## RESEARCH ONLY - NOT FOR LIVE TRADING ##` |

**Forbidden Actions (regardless of phase)**:
- Auto-optimization of production parameters
- Signal overriding of core engine logic
- Deploying logic based solely on backtests
- Multi-wiring (>1 research module to core loop during initial rollout)

*(Source: `docs/governance/RESEARCH_MODULE_GOVERNANCE.md`)*

---

## Legacy Source Mapping

| Section | Legacy Source Document(s) |
| :--- | :--- |
| §1 Philosophy | `RESEARCH_MODULE_GOVERNANCE.md`, `bounded_automation_contract.md` |
| §2 Trust Domains | `RESEARCH_MODULE_GOVERNANCE.md`, `evolution.md`, component YAMLs |
| §3 Safety Invariants | `architectural_invariants.md` |
| §4 Access Boundaries | `skills_catalog.md`, `ui_guardrails.md`, `dashboard_truth_contract.md` |
| §5 Credentials | `INDIA_WEBSOCKET_ARCHITECTURE.md`, `historical_ingestion_verification.md` |
| §6 Operator Model | `chat_execution_contract.md`, `impact_resolution_contract.md`, `kill_switch.md` |
| §7 Survivability | `scale_safety_obligations.md`, `decision_plane_obligations.md` |
| §8 Retention | `data_retention_policy.md` |
| §9 Research Guardrails | `RESEARCH_MODULE_GOVERNANCE.md` |
