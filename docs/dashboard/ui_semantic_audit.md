# Dashboard UI Semantic Audit

**Date**: 2026-01-28
**Auditor**: Principal UX + Epistemic Safety Architect
**Method**: Source-Code Audit (Static Analysis of React Modules)

## A. Strategy Eligibility Matrix (Audit)

### Findings
*   **Identity**: Each row uses `s.strategy` as the label. It lacks explicit distinction between strategy variants (e.g., "Momentum Strict" vs "Momentum Accelerating") if the backend returns the base name.
*   **Explanations**: The UI shows "Regime" and "Factor" tags with colors, but the `s.reason` is often technical (e.g., "Regime check failed"). It does not explain the *semantic* consequence for the layperson.
*   **Semantic Differentiation**: Multiple strategy rows look identical except for the name. There is no visual cue for "Strategy Family" grouping.

### Deficiencies
*   ❌ No explicit Strategy Identity (anonymous variant handling).
*   ❌ Technical jargon in indicators.
*   ❌ Lack of grouping by intent.

## B. "What Would Change My Mind?" Section (Audit)

### Findings
*   The current implementation in `ChangeConditions.jsx` is hardcoded with technical enumerations: `CONFIRMED_BREAKOUT`, `EMERGING_*`.
*   **Jargon Level**: High. Assumes the user knows what "Dispersion" or "Expansion EARLY" represents.
*   **Causal Reasoning**: Absent. It states the rule, but not the *reason* why the system is exercising restraint.

### Deficiencies
*   ❌ Jargon-heavy (Layman un-friendly).
*   ❌ Missing "Why it matters" context.

## C. Missing UX Signals (Audit)

### Deficiencies
*   ❌ **Conflated Signals**: Eligibility (Safety/Gating) and Confidence (Environmental Strength) are merged into a single "Eligible/Blocked" binary.
*   ❌ **Factor Opacity**: The reasons why a factor is blocked are not surfaced within the Strategy Matrix; the user must look at a different card.
*   ❌ **No Navigation Legend**: No explanation of visual tokens (tags, colors).
*   ❌ **No Interaction Depth**: No hover tooltips or expandable details to explain the "Reason".

## Final Verdict: LEGIBILITY REFACTOR REQUIRED
The UI currently describes "What" but fails to explain "Why". It satisfies the technical requirement but fails the Epistemic Safety requirement of being "impossible to misuse" via misunderstanding.
