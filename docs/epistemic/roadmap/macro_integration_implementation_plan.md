# Implementation Plan: Macro Integration (Phase 4.1 Activation)

**Status**: DRAFT  
**Phase**: Structural Activation (Phase 4.1)  
**Trigger**: Phase 4.1 Activation Request  
**Purpose**: Bridge the gap between latent macro definitions and governed decision inputs.

---

## 1. Objectives

1.  **Formalize Specification**: Enumerate exact indicators (QQQ, SPY, VIX, etc.) in code.
2.  **Bind Data Sources**: Connect to the Ingestion Layer as per the Minimal Regime Contract.
3.  **Wire to Decision Engine**: Expose macro context in the `DecisionSpec` object.
4.  **Enable Observability**: Ensure macro state is logged in all shadow decision traces.

---

## 2. Theoretical Constraints (Non-Negotiable)

- **READ-ONLY**: Macro data is for context, not signaling.
- **NO-DECISION**: No logic (if/else) may branch on macro values in this phase.
- **DIAGNOSTIC-FIRST**: The implementation must focus on visibility and auditability.

---

## 3. Tasks

### SA-4.1.1: Macro Indicator Specification
- Define indicators in `src/layers/macro/specification.py`.
- Map roles (Equity, Vol, Rates, Credit) to symbols.
- Set lookback requirements for each.

### SA-4.1.2: Macro Data Source Binding
- Implement binding logic in `src/layers/macro/binding.py`.
- Verify presence of symbols in Ingestion Layer.
- Validate temporal alignment (intersection-only).

### SA-4.1.3: Macro Decision Wiring
- Update `DecisionSpec` to include `macro_context`.
- Update Task Graph to pass macro state to strategy task nodes.
- Verify that `DecisionSpec` remains descriptive.

### SA-4.1.4: Macro Observability Trace
- Integrate macro state into `shadow_sink.py`.
- Update Replay Engine to display macro context.
- Generate first "Macro Integration Report".

---

## 4. Obligations

- **OBL-SA-MI-SPEC**: 🔴 UNMET
- **OBL-SA-MI-BIND**: 🔴 UNMET
- **OBL-SA-MI-WIRING**: 🔴 UNMET
- **OBL-SA-MI-TRACE**: 🔴 UNMET

---

## 5. Success Criteria

- Decision objects in the Shadow Sink show correctly populated macro context.
- Auditor can verify the source of macro data for any decision.
- Zero signaling logic is introduced.
