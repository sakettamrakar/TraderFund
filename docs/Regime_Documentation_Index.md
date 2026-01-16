# Regime Documentation Index

> **Last Updated:** 2026-01-16  
> **Status:** AUTHORITATIVE

This index lists all regime-related documentation and their purposes.

---

## Core Documents

| Document | Purpose | Status |
|----------|---------|--------|
| [Regime_Engine_Overview.md](Regime_Engine_Overview.md) | What the system is and why it exists | FROZEN |
| [Regime_Taxonomy.md](Regime_Taxonomy.md) | All 7 regime states with behaviors | FROZEN |
| [Regime_Confidence_Model.md](Regime_Confidence_Model.md) | Confluence, Persistence, Intensity | FROZEN |
| [Regime_Dashboard_Runbook.md](Regime_Dashboard_Runbook.md) | Operator guide for dashboard v1.1 | ACTIVE |
| [Regime_Integration_Runbook.md](Regime_Integration_Runbook.md) | Wiring rules for downstream systems | ACTIVE |

---

## Reference Documents (Read-Only)

| Document | Purpose |
|----------|---------|
| [Market_Regime_Detection_Blueprint.md](Market_Regime_Detection_Blueprint.md) | Original architecture charter |
| [Market_Regime_Detection_Tech_Spec.md](Market_Regime_Detection_Tech_Spec.md) | Technical specification |
| [Regime_Implementation_Control_Plan.md](Regime_Implementation_Control_Plan.md) | Phase 0-10 control plan |

---

## Quick Reference

### Current Live State (2026-01-16)
- **US Market:** SHADOW mode, daily regime updates
- **India Market:** SHADOW mode, intraday 5m updates (market hours)
- **Dashboard:** v1.1 (Decision-Complete)
- **Narrative Wiring:** Phase A complete (SHADOW/SOFT)

### What is FROZEN
- Regime taxonomy (7 states)
- Confidence model (3 components)
- Dashboard v1.0 semantics

### What is EXTENSIBLE
- Strategy suitability scores
- Integration order
- Telemetry format
