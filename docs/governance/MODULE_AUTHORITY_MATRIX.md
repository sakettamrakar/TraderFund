# Module Authority Matrix

## 1. PURPOSE OF THIS DOCUMENT

In a high-frequency or algorithmic trading environment, ambiguity is the primary cause of catastrophic capital loss. This document establishes the **Authority Hierarchy** for the TraderFund codebase. By explicitly defining which modules are permitted to influence live trading and which are restricted to research, we eliminate the "accidental authority" problem.

### Objectives:
- **Prevent Cross-Contamination:** Ensure research logic never inadvertently modifies production state.
- **Enforce Audit Trails:** Require explicit promotion of modules across authority boundaries.
- **Clarify Responsibility:** Define which modules require production-grade testing vs. research-grade flexibility.

---

## 2. AUTHORITY CLASSIFICATION DEFINITIONS

| Classification | Influence Live Trading? | Imported by Core? | Modified Freely? | Description |
| :--- | :--- | :--- | :--- | :--- |
| **PRODUCTION-ACTIVE** | **YES** | YES | **NO** | Authoritative code powering live execution. Requires 100% test pass and architect sign-off. |
| **PRODUCTION-DORMANT** | **NO** | YES | **NO** | Core infrastructure logic currently bypassed or in "Monitor-Only" mode. |
| **RESEARCH-ONLY** | **NO** | **NO** | **YES** | Analytical modules for insight generation. Physically isolated from core. |
| **EXPERIMENTAL** | **NO** | **NO** | **YES** | Scratchpad logic, unverified ideas, or loose scripts. High risk. |
| **DEPRECATED** | **NO** | **NO** | **NO** | Legacy or overlapping code targeted for removal. |

---

## 3. COMPLETE MODULE INVENTORY

| Module Name | Current Location | Purpose | Current Status | Overlap? | Planned Action |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Momentum Engine** | `src/core_modules/` | Live signal calculation (VWAP, Relative Volume). | PRODUCTION-ACTIVE | No | Keep as-is. |
| **Screening** | `src/core_modules/` | Periodic asset selection and filtering. | PRODUCTION-ACTIVE | No | Keep as-is. |
| **Watchlist Mgmt** | `src/core_modules/` | Real-time tracking of active symbols. | PRODUCTION-ACTIVE | No | Keep as-is. |
| **Trade Notifications**| `src/core_modules/` | Alerting and signal persistence. | PRODUCTION-ACTIVE | No | Keep as-is. |
| **Risk Estimation** | `src/core_modules/` | Placeholder for position sizing logic. | PRODUCTION-DORMANT | **Yes** | Move to `research_modules/`. |
| **Data Ingestion** | `src/data_ingestion/`| Generic ingestion utilities. | PRODUCTION-ACTIVE | No | Keep as-is. |
| **Data Processing** | `src/data_processing/`| Post-ingestion cleaning and normalization. | PRODUCTION-ACTIVE | No | Keep as-is. |
| **Data Storage** | `src/data_storage/` | Local DB and Parquet persistence logic. | PRODUCTION-ACTIVE | No | Keep as-is. |
| **Angel SmartAPI** | `ingestion/api_ingestion/`| Market data and auth provider for Angel. | PRODUCTION-ACTIVE | No | Keep as-is. |
| **Intraday Processor** | `processing/` | Specific Parquet conversion scripts. | PRODUCTION-ACTIVE | No | Keep as-is. |
| **Backtesting** | `research_modules/backtesting/` | Historical simulation and verification. | RESEARCH-ONLY | N/A | ✅ Migration Complete. |
| **Volatility Context** | `research_modules/volatility_context/` | Market regime and ATR analysis. | RESEARCH-ONLY | N/A | ✅ Migration Complete. |
| **News Sentiment** | `research_modules/news_sentiment/` | Sentiment analysis from news feeds. | RESEARCH-ONLY | N/A | ✅ Migration Complete. |
| **Portfolio Opt** | `src/institutional_modules/` | Capital allocation and optimization.| RESEARCH-ONLY | **Yes** | Move to `research_modules/`. |
| **Risk Models** | `research_modules/risk_models/` | Position sizing and risk simulation. | RESEARCH-ONLY | N/A | ✅ Migration Complete. |
| **OMS / EMS** | `src/institutional_modules/` | Order and Execution Management System. | PRODUCTION-DORMANT | No | Move to `src/core_modules/infra`. |
| **Compliance Engine**| `src/institutional_modules/` | Pre-trade risk rule validation. | PRODUCTION-DORMANT | No | Move to `src/core_modules/infra`. |
| **Technical Scanner** | `src/pro_modules/strategy_engines/` | Experimental technical indicators. | EXPERIMENTAL | No | Deprecate; merge into Research. |

---

## 4. OVERLAP & MIGRATION POLICY

To maintain the architectural boundary defined in `RESEARCH_MODULE_GOVERNANCE.md`, the following policy is enforced:

1.  **Mandatory Migration:** Any module in `src/core_modules`, `src/pro_modules`, or `src/institutional_modules` that overlaps with the four designated Research Modules (Backtesting, Volatility, Risk, Sentiment) **MUST** be migrated to `research_modules/`.
2.  **Authority Stripping:** Upon migration, the module's status changes to **RESEARCH-ONLY**. It must be technically decoupled from any production call stacks.
3.  **Single Authority Source:** No duplicate implementation of logic (e.g., ATR calculation) may exist in both `core_modules` and `research_modules`. Core MUST use its own minimal, audited version; Research may use its own experimental version.

---

## 5. ENFORCEMENT RULES

- **Import Lockdown:** Any PR introducing a `research_modules` import into `core_modules` or `ingestion` shall be automatically rejected.
- **Phase Checking:** All Research modules must include a `PhaseLock` check:
  ```python
  if ACTIVE_PHASE < 6:
      raise IllegalAuthorityError("Research modules restricted in Phase < 6")
  ```
- **Registry Requirement:** No new functional directory may be created without a corresponding entry in this matrix.

---

## 6. CHANGE CONTROL

- **Authority Elevation:** Promoting a module from RESEARCH-ONLY to PRODUCTION-ACTIVE requires a **Promotion Audit** as defined in the Governance document.
- **Log of Changes:** All status changes in this matrix must be timestamped and linked to a specific PR.
- **Review Frequency:** This matrix is reviewed at the start of every development Phase (e.g., entering Phase 6).

---

## 7. FINAL DECLARATION

This matrix is not a suggestion; it is a structural constraint of the TraderFund platform. By signing off on this document, we commit to a system where **authority is earned through verification**, not granted by convenience.

*Senior Trading Platform Architect*  
*TraderFund Project Governance Board*
