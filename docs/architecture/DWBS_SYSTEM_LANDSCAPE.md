# DWBS: System Landscape & Architecture Freeze

**Status**: ACTIVE
**Type**: Foundational / One-Time
**Plane**: Architecture & Governance
**Affects**: Documentation only
**Risk**: Zero
**Reversibility**: N/A

---

## 1. Purpose & Non-Goals

### Purpose
To produce a structural legibility of the TraderFund system by mapping all existing components into a "Three-Ring Architecture". This serves as an authoritative architectural freeze to ensure no floating documentation or unclear ownership exists before further capability is added.

### Non-Goals
- Refactoring existing code.
- Adding new features or execution paths.
- Implementing India research logic.
- Implementing Intelligence Layer logic.

---

## 2. Three-Ring Architecture Definition

The system is defined by three immutable rings:

### Ring-1: Core Research (Truth Engine)
**Properties**:
- Market-agnostic
- Symbol-free
- Slow-moving
- Explanatory
- Gating allowed
- Frozen semantics

**Examples**: Macro Context, Regime Engine, Factor Context, Strategy Eligibility, Evolution / Watchers, Governance / DIDs.

### Ring-2: Market Research Adapters
**Properties**:
- Market-specific
- Still research-grade
- Proxy-based (indices, volatility)
- No symbol ranking
- No heuristics

**Examples**: US research instantiation, India research instantiation, Data contracts & proxies.

### Ring-3: Intelligence / Decision Support
**Properties**:
- Human-facing
- Symbol-level
- Heuristic allowed
- Noisy allowed
- **NEVER executes**
- **NEVER gates research**

**Examples**: Watchlists, Breakout scanners, Narrative candidates, “Interesting activity” views.

---

## 3. Documentation Canon Rules

1.  **Authority**: `docs/architecture/system_landscape.md` is the single source of truth for component existence and ownership.
2.  **No Floating Docs**: Every documentation file must be linked or classified in the audit.
3.  **Ring-Bound**: New components must declare their Ring and Market in the landscape inventory.
4.  **Legibility First**: "We do not add capability until the system is legible. Legibility precedes power."

---

## 4. Landscape Deliverables

1.  **System Landscape Inventory** (Section 7 below): The map of what exists.
2.  **Documentation Audit** (`docs/architecture/documentation_audit.md`): The cleanup plan.
3.  **Convergence Map** (`docs/architecture/convergence_map.md`): The bridge between legacy/future and current state.
4.  **Task Graph** (`docs/epistemic/roadmap/task_graph_landscape.md`): The execution tracking for this work.
5.  **Obligation Index Update** (`docs/governance/obligation_index.md`): Tracking architectural obligations.

---

## 5. Task Graph

See `docs/epistemic/roadmap/task_graph_landscape.md` for the detailed execution graph.
Key Nodes:
- ARCH-1.1: Three-Ring Architecture Definition
- ARCH-1.2: System Component Inventory
- ARCH-1.3: Documentation Audit
- ARCH-1.4: Convergence Mapping
- ARCH-1.5: Architecture Freeze Declaration

---

## 6. Completion Criteria

- [x] New DWBS exists (`docs/architecture/DWBS_SYSTEM_LANDSCAPE.md`).
- [x] Complete system landscape inventory exists (Section 7).
- [x] Documentation audit exists.
- [x] Convergence map exists.
- [x] Task graph exists.
- [x] Obligation index updated.
- [x] **No code touched.**

---

## 7. System Landscape Inventory

> Previously `docs/architecture/system_landscape.md` (ARCH-1.2). Consolidated here as the canonical component map.

**Authority**: `ARCH-1.2` | **Status**: FROZEN (Landscape v1) | **Date**: 2026-01-30

### 7.1 Executive Summary

TraderFund is a "Three-Ring" architecture system designed to separate Core Research (Truth) from Market Adapters and Intelligence/Decision Support. It currently operates in **Observer Mode** — generates insights, signals, and decisions but does not execute live trades.

**What the system is not**: a black-box trading bot, a monolithic script, or a system mixing market-specific heuristics with core truth.

### 7.2 Component Inventory Table

| Component Name | File / Folder | Ring | Market | Purpose | Status | Depends On | Feeds Into |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Macro Context** | `src/macro/` | 1 | Global | Define macroeconomic states and regimes | Active | Data Ingestion | Truth Engine, Strategy Eligibility |
| **Evolution Engine** | `src/evolution/` | 1 | Global | Evaluate strategy readiness, regime audits, watchers | Active | Macro Context, Strategy Registry | Decision Engine, Reports |
| **Strategy Registry** | `src/strategy/` | 1 | Global | Declarative strategy definitions and eligibility rules | Active | None | Evolution Engine, Harness |
| **Governance** | `src/governance/` | 1 | Global | Enforce policy, DIDs, and architectural rules | Active | None | All Rings |
| **Harness** | `src/harness/` | 1 | Global | System orchestration, task graph execution, safety checks | Active | All Ring 1 | System Execution |
| **Layers** | `src/layers/` | 1 | Global | Abstract logic layers (Belief, Factor, Macro) | Active | Macro Context | Harness |
| **Capital Core** | `src/capital/` | 1 | Global | Manage capital readiness, allocation plans, history | Active | None | Decision Engine |
| **Inter-Module Comm** | `src/inter_module_comm/` | 1 | Global | Messaging and communication infrastructure | Active | None | All Components |
| **Utils** | `src/utils/` | 1 | Global | Shared utilities (Logging, etc.) | Active | None | All Components |
| **NSE Data Adapter** | `src/data_ingestion/` | 2 | India | Download and normalize NSE EOD data | Active | External APIs | Data Storage, Ring 3 Scanners |
| **Data Ingestion** | `src/ingestion/` | 2 | Global/India | General data ingestion and contract enforcement | Active | External APIs | Ring 1, Ring 3 |
| **Data Processing** | `src/data_processing/` | 2 | Global | Clean and process raw data | Active | Ingestion | Data Storage |
| **Data Storage** | `src/data_storage/` | 2 | Global | Persistence layer (TimeSeries, Relational, Lake) | Active | Ingestion | All Rings |
| **Narrative Core** | `narratives/` (Root) | 3 | Global | Core logic for narrative generation and management | Active | Data | Decision Engine |
| **Momentum Engine** | `src/core_modules/momentum_engine/` | 3 | US/India | Heuristic scanner for momentum setups (VWAP, HOD) | Active | Data Storage | Narratives |
| **Screening** | `src/core_modules/screening/` | 3 | US/India | Fundamental and technical screening tools | Active | Data Storage | Narratives |
| **Watchlist Mgmt** | `src/core_modules/watchlist_management/` | 3 | Global | Tools for managing symbol lists | Active | None | Scanners, Dashboard |
| **Dashboard** | `src/dashboard/` | 3 | Global | User Interface for observation and monitoring | Active | Backend API | Human Operator |
| **Decision Engine** | `src/decision/` | 3 | Global | Evaluates narratives, proposes decisions (Observer Mode) | Active | Narratives, Evolution | Dashboard, Logs |
| **Institutional Mods** | `src/institutional_modules/` | 3 | Global | Stubs for Compliance, OMS, EMS | Dormant | None | None |
| **Narratives (Src)** | `src/narratives/` | ? | ? | **Orphan/Duplicate**. Contains `bad_logic.py` | Orphan | None | None |

### 7.3 Market Coverage Summary

| Market | Data | Logic | Notes |
| :--- | :--- | :--- | :--- |
| US | Partial/Missing (mostly NSE focused) | Strategy Registry (market-agnostic) | US-specific adapters minimal |
| India | Data Rich | Logic Pending | NSE EOD via `src/data_ingestion`; MomentumEngine likely testing on India data |
| Global/Shared | Ring 1 completely shared | Dashboard/Decision market-neutral | Missing: formal Ring 2 India Research Adapter, explicit US data source mapping |
