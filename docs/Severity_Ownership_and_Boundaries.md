# Severity Ownership and Cognitive Boundaries

**Status:** APPROVED
**Last Updated:** 2026-01-17

## 1. Ownership Definition

**Severity is an upstream editorial / classification signal, not a downstream analytical inference.**

- **Owner:** The NEWS / INGESTION layer (Upstream).
- **Consumer:** The Trader / Narrative Genesis System (Downstream).

The Trader System **NEVER** infers severity from text content. It treats severity as a given property of an event, similar to a timestamp.

## 2. Responsibility Split

| Layer | Responsibility | Details |
| :--- | :--- | :--- |
| **News Source** | Assign initial importance | Editorial judgment by Bloomberg, Reuters, etc. |
| **News Repo** | Normalize `severity_hint` | Maps various source scales to `LOW`, `MEDIUM`, `HIGH`. |
| **Trader Adapter** | Map `severity_hint` → Score | Converts enums to floats (e.g., `MEDIUM` → 70.0). |
| **Genesis** | Gate attention using Score | Decides if an event is "loud" enough to become a Narrative. |
| **Regime** | Modulate Conviction | Dampens or amplifies the final weight based on market state. |
| **Human** | Final Interpretation | Considers the context and nuance beyond the score. |

## 3. Explicit Non-Goals

The Narrative Genesis System will **NEVER**:

1.  **Parse text for importance.** (No NLP for severity)
2.  **Override `severity_hint`.** (The upstream signal is truth)
3.  **Infer urgency from language.** (No sentiment analysis for sizing)
4.  **Predict market impact.** (Severity ≠ Impact Prediction)
