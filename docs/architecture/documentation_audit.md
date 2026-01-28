# Documentation Audit & Cleanup Plan

**Authority**: `ARCH-1.3`
**Status**: ACTIVE
**Date**: 2026-01-30

## 3.1 Audit Strategy
This audit classifies all documentation artifacts into four categories:
- ✅ **Canonical**: authoritative, keep as-is.
- 🔄 **Merge**: valuable content to be moved to a canonical home.
- 🟡 **Deprecated**: outdated but preserved for context (mark as `[DEPRECATED]`).
- ❌ **Delete**: safe to remove (duplicates, noise).

---

## 3.2 Root Documentation
| File | Status | Action / Notes |
| :--- | :--- | :--- |
| `README.md` | ✅ Canonical | Project entry point. |
| `Architecture_Overview.md` | 🔄 Merge | Merge into `docs/architecture/system_landscape.md`. |
| `vantage_api.md` | ✅ Canonical | API Reference for Vantage. |
| `vantage_api copy.md` | ❌ Delete | **Duplicate**. Safe to delete immediately. |

---

## 3.3 Architecture & Epistemic
| File | Status | Action / Notes |
| :--- | :--- | :--- |
| `docs/architecture/*` | ✅ Canonical | The new source of truth. |
| `docs/epistemic/*` | ✅ Canonical | Meta-knowledge, skills, and roadmap. |
| `docs/impact/*` | ✅ Canonical | Historical records of decisions and evolution. **DO NOT MODIFY**. |
| `docs/audits/*` | ✅ Canonical | System audits and verdicts. |

---

## 3.4 Domain Documentation
| File | Status | Action / Notes |
| :--- | :--- | :--- |
| `docs/macro/*` | ✅ Canonical | Ring-1 Macro Context documentation. |
| `docs/strategy/*` | ✅ Canonical | Ring-1 Strategy Registry documentation. |
| `docs/dashboard/*` | ✅ Canonical | Ring-3 Dashboard specifications. |
| `docs/diagnostics/*` | ✅ Canonical | Generated reports and diagnostics. |
| `docs/RUNBOOK.md` | ✅ Canonical | Operational procedures. |

---

## 3.5 Legacy & Floating Docs (To Be Consolidated)
| File | Status | Action / Notes |
| :--- | :--- | :--- |
| `docs/Accumulation_Logic.md` | 🔄 Merge | Review for Strategy Registry or Ring-3 logic. |
| `docs/Market_Regime_Detection_*.md` | 🔄 Merge | Merge into `docs/macro/`. |
| `docs/Narrative_System_Summary.md` | 🔄 Merge | Merge into `docs/architecture/system_landscape.md` (Ring 3). |
| `docs/Regime_*.md` | 🔄 Merge | Merge into `docs/macro/`. |
| `docs/INDIA_WEBSOCKET_ARCHITECTURE.md` | ✅ Canonical | Keep as reference for Ring-2 India Adapter. |
| `docs/TECHNICAL_SCANNER.md` | 🔄 Merge | Merge into `src/core_modules/screening/` docs. |
| `docs/us_market_engine_design.md` | 🟡 Deprecated | Mark as Reference. |
| `docs/us_market_next_steps.md` | 🟡 Deprecated | Mark as Reference. |
| `docs/Genesis_Production_Rules.md` | 🟡 Deprecated | Check if superseded by `src/governance`. |
| `docs/intelligence_and_alpha_layer.md` | 🔄 Merge | Merge into `docs/architecture/system_landscape.md` (Ring 3 definition). |
| `docs/research_product_architecture.md` | 🔄 Merge | Merge into `docs/architecture/system_landscape.md`. |
| `docs/Semantic_Enrichment_Spec.md` | 🟡 Deprecated | Review for utility. |
| `docs/Severity_Ownership_and_Boundaries.md` | ✅ Canonical | Keep for Incident Response. |

---

## 3.6 Module Documentation (In-Place)
| Location | Status | Action / Notes |
| :--- | :--- | :--- |
| `src/core_modules/momentum_engine/README.md` | ✅ Canonical | Ring-3 Component Docs. |
| `src/dashboard/frontend/README.md` | ✅ Canonical | Frontend Docs. |
| `research_modules/*/README.md` | 🟡 Deprecated | Legacy modules. Review and move valid logic to `src/`. |
| `ingestion/*/README.md` | ✅ Canonical | Data pipeline documentation. |

---

## 3.7 Execution Plan
1.  **Immediate**: Delete `vantage_api copy.md`.
2.  **Phase 1**: Move `docs/Market_Regime_*.md` and `docs/Regime_*.md` to `docs/macro/archive/` or merge content.
3.  **Phase 2**: Consolidate "floating" architecture docs (`Architecture_Overview.md`, `research_product_architecture.md`) into the new `docs/architecture/` folder.
