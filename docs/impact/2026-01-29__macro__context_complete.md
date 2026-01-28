# Documentation Impact Declaration (DID)

**Date**: 2026-01-29  
**Scope**: Macro Context Layer  
**Type**: OBSERVABILITY / GOVERNANCE

## Summary

Introduced the **Macro Context Layer**, a read-only explanatory subsystem that answers *why* the market environment looks the way it does. It adds narrative depth (Monetary, Liquidity, Growth, Risk) without influencing execution or strategy logic.

## Changes

### 1. Macro Ontology (Docs)
- **New**: [macro_layer_principles.md](file:///c:/GIT/TraderFund/docs/macro/macro_layer_principles.md) - Defines the "Explanatory-Only" philosophy.
- **New**: [macro_signal_catalog.md](file:///c:/GIT/TraderFund/docs/macro/macro_signal_catalog.md) - Defines the complete signal universe (e.g., Policy Stance, Liquidity Impulse).
- **New**: [macro_integration_obligations.md](file:///c:/GIT/TraderFund/docs/epistemic/governance/macro_integration_obligations.md) - Formalizes the "Non-Gating" constraint.

### 2. Backend Logic (Read-Only)
- **New**: `src/macro/macro_context_builder.py` - Computes daily macro states from ingested data proxies.
- **Updated**: `ev_tick.py` - Added **Step 3b** to build macro context.
- **Schema**: Defined `docs/macro/context/macro_context.json`.

### 3. Dashboard Integration
- **New API**: `/api/macro/context` serving the daily snapshot.
- **New Panel**: `MacroContextPanel.jsx` displaying the "Macro Weather Report".
- **Updated**: `App.jsx` to include the macro panel.

## Safety Invariants Verified
✅ **No Execution**: Macro logic is strictly isolated from trade execution.  
✅ **No Gating**: Strategies do not read `macro_context.json`.  
✅ **Read-Only**: The builder consumes data but modifies only its own context file.

## Validation Results
- **EV-TICK**: Successfully generated `macro_context.json`.
- **API**: Endpoint returns valid JSON with narrative summary.
