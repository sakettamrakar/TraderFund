# Dashboard Truth Contract

## 1. Purpose of the Dashboard
The TraderFund dashboard is a truth surface, not a control panel. Its primary and only purpose is to project the internal state of the system's governance and intelligence layers to human operators.
- It answers "what is true now" based on the bound truth epoch.
- It never answers "what to do" or "what might happen".
- It is a passive observer of system state, not an interface for execution or intervention.

## 2. Truth vs Explanation vs Interpretation
To maintain epistemic integrity, the dashboard must distinguish between levels of data abstraction:

- **Raw Truth (Pass-through only)**: Direct values from canonical artifacts (e.g., price, volume, regime code). These must be rendered without modification.
- **Traceable Explanation (Allowed)**: Narrative or logic summaries that directly cite the specific rules or data points used to reach a state (e.g., "Regime is NEUTRAL because SMA200 > Price").
- **Interpretation / Recommendation (Forbidden)**: Any semantic layer that suggests a subjective quality or future action.

**Hard Prohibitions**:
- No "buy/sell" or "entry/exit" language.
- No "opportunity" framing or "profit potential" narratives.
- No "readiness" framing (e.g., "System is ready to trade").
- No "confidence escalation" (marketing a state as more certain than the underlying logic suggests).

## 3. Widget Binding Rules
Every widget rendered on the dashboard must be strictly bound to a backend source.
- A widget MUST bind to exactly one backend artifact.
- A widget MUST bind to exactly one system layer (e.g., DATA, INTELLIGENCE, GOVERNANCE).
- A widget MUST bind to exactly one truth epoch (TE-2026-01-30).
- **Unbound widgets are invalid** and must be removed or rendered with an error state.

## 4. Explanation Contract
Summaries or "one-liners" are permitted only under the following conditions:
- They must be expandable to show the full logic.
- They must cite the exact artifacts and line items used.
- They must preserve uncertainty; if a factor is "mixed", it must not be summarized as "positive" or "negative".
- Source and epoch disclosure is mandatory for every explanation.

## 5. Trace Badge Requirement
Every data-bearing widget must include an inspectable Trace Badge. This badge must explicitly map the data lineage:
`[Data Role] → [Source Artifact] → [Upstream Provider]`
Example: `[Regime] → [market_regime.json] → [FactorContextEngine]`

## 6. Degradation & Staleness Rules
- **Silence is forbidden**: If data is missing or a process failed, the dashboard must not show "0" or "N/A" without explanation.
- **Explicit Staleness**: Stale data (from a previous epoch) must be rendered with an explicit and dominant warning overlay.
- **Normalization of Constraints**: States like `HOLD` or `OBSERVE_ONLY` must be treated as nominal operating conditions, not as "broken" or "stopped" states.

## 7. Forbidden Semantics (Hard Ban List)
The following visual and semantic elements are strictly forbidden:
- **Rankings**: Lists comparing "best" or "worst" assets.
- **Scores**: Arbitrary 1-10 or 0-100 scores that hide underlying complexity.
- **Arrows**: Directional indicators that imply future movement.
- **Green/Red Directional Cues**: Using color to imply "Good" (Green) or "Bad" (Red) for market direction. Color may only be used for system health (e.g., Error vs. Success).
- **"ACTIVE" without context**: Using the word "ACTIVE" in isolation. It must always be qualified ( e.g., "ACTIVE (UNDER CONSTRAINTS)").

---
*This document is immutable for Epoch TE-2026-01-30.*
