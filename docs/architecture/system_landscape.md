# System Landscape Inventory

**Authority**: `ARCH-1.2`
**Status**: FROZEN (Landscape v1)
**Date**: 2026-01-30

## 2.1 Executive Summary

### What the system is
TraderFund is a "Three-Ring" architecture system designed to separate Core Research (Truth) from Market Adapters and Intelligence/Decision Support. It currently operates in **Observer Mode**, meaning it generates insights, signals, and decisions but does not execute live trades.

### What the system is not
- It is NOT a black-box trading bot.
- It is NOT a monolithic script.
- It is NOT mixing market-specific heuristics with core truth.

### Why separation matters
Separating the "Truth Engine" (Ring 1) from "Market Adapters" (Ring 2) and "Intelligence" (Ring 3) ensures that core research remains pure, slow-moving, and robust, while market-specific logic and noisy heuristics can evolve rapidly without destabilizing the core.

---

## 2.2 Component Inventory Table

| Component Name | File / Folder | Ring | Market | Purpose | Status | Depends On | Feeds Into |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Macro Context** | `src/macro/` | 1 | Global | Define macroeconomic states and regimes. | Active | Data Ingestion | Truth Engine, Strategy Eligibility |
| **Evolution Engine** | `src/evolution/` | 1 | Global | Evaluate strategy readiness, conduct regime audits, and run watchers. | Active | Macro Context, Strategy Registry | Decision Engine, Reports |
| **Strategy Registry** | `src/strategy/` | 1 | Global | Declarative definitions of strategies and their eligibility rules. | Active | None | Evolution Engine, Harness |
| **Governance** | `src/governance/` | 1 | Global | Enforce policy, DIDs, and architectural rules. | Active | None | All Rings |
| **Harness** | `src/harness/` | 1 | Global | System orchestration, task graph execution, and safety checks. | Active | All Ring 1 | System Execution |
| **Layers** | `src/layers/` | 1 | Global | Abstract logic layers (Belief, Factor, Macro). | Active | Macro Context | Harness |
| **Capital Core** | `src/capital/` | 1 | Global | Manage capital readiness, allocation plans, and history. | Active | None | Decision Engine |
| **Inter-Module Comm** | `src/inter_module_comm/` | 1 | Global | Messaging and communication infrastructure. | Active | None | All Components |
| **Utils** | `src/utils/` | 1 | Global | Shared utilities (Logging, etc.). | Active | None | All Components |
| **NSE Data Adapter** | `src/data_ingestion/` | 2 | India | Download and normalize NSE EOD data. | Active | External APIs | Data Storage, Ring 3 Scanners |
| **Data Ingestion** | `src/ingestion/` | 2 | Global/India | General data ingestion and contract enforcement. | Active | External APIs | Ring 1, Ring 3 |
| **Data Processing** | `src/data_processing/` | 2 | Global | Clean and process raw data. | Active | Ingestion | Data Storage |
| **Data Storage** | `src/data_storage/` | 2 | Global | Persistence layer (TimeSeries, Relational, Lake). | Active | Ingestion | All Rings |
| **Narrative Core** | `narratives/` (Root) | 3 | Global | Core logic for narrative generation and management. | Active | Data | Decision Engine |
| **Momentum Engine** | `src/core_modules/momentum_engine/` | 3 | US/India | Heuristic scanner for momentum setups (VWAP, HOD). | Active | Data Storage | Narratives |
| **Screening** | `src/core_modules/screening/` | 3 | US/India | Fundamental and technical screening tools. | Active | Data Storage | Narratives |
| **Watchlist Mgmt** | `src/core_modules/watchlist_management/` | 3 | Global | Tools for managing symbol lists. | Active | None | Scanners, Dashboard |
| **Dashboard** | `src/dashboard/` | 3 | Global | User Interface for observation and monitoring. | Active | Backend API | Human Operator |
| **Decision Engine** | `src/decision/` | 3 | Global | Evaluates narratives and proposes decisions (Observer Mode). | Active | Narratives, Evolution | Dashboard, Logs |
| **Institutional Mods** | `src/institutional_modules/` | 3 | Global | Stubs/Structure for Compliance, OMS, EMS. | Dormant | None | None |
| **Narratives (Src)** | `src/narratives/` | ? | ? | **Orphan/Duplicate**. Contains `bad_logic.py`. | Orphan | None | None |

---

## 2.3 Market Coverage Summary

### US Market
- **Status**: Logic definition exists in Strategy Registry (Market Agnostic).
- **Data**: Partial/Missing in current ingestion paths (mostly NSE focused).
- **Research**: US-specific adapters are minimal or shared.

### India Market
- **Status**: **Data Rich, Logic Pending**.
- **Data**: `src/data_ingestion` provides NSE EOD data.
- **Research**: Logic (Strategy instantiation for India) is NOT yet formally introduced in Ring 2, though `MomentumEngine` is likely testing on India data.

### Global / Shared
- **Ring 1**: Completely shared (Macro, Evolution, Strategy Definitions).
- **Ring 3**: Dashboard and Decision Engine are market-neutral in design but currently visualize available (India) data.

### Missing
- Formal **Ring 2 India Research Adapter** to bridge the gap between NSE Data and Ring 1 Strategy Eligibility.
- Explicit mapping of US data sources if US market is to be active.
