# Narrative-Driven Market Research Product Architecture

**Version**: 1.0 (Draft)
**Status**: APPROVED for Implementation

---

## 1. Product Philosophy

The **TraderFund Research Product** is an institutional-grade intelligence service derived strictly from the automated Intelligence Stack (Signals > Narratives > Alpha).

**Core Axioms:**
1.  **Context Over Calls**: We provide "why" the market is moving, not "what" to buy.
2.  **Uncertainty as a Feature**: Confidence scores are front-and-center. We do not feign certainty.
3.  **Auditable Logic**: Every narrative statement traces back to specific, immutable events.
4.  **Neutral Stance**: Tone is observational ("Bullish momentum detected") rather than advisory ("We recommend buying").

---

## 2. Research Output Types

### A. Daily Market Brief ("The Pulse")
*   **Purpose**: Tactical awareness of active market drivers.
*   **Frequency**: Daily (Market Close).
*   **Content**:
    *   Top 3 Active Narratives (High Confidence only).
    *   Significant new Signals (Severity > 0.7).
    *   Reliability check on yesterday's activity.
*   **Target Audience**: Traders requiring situational awareness.

### B. Weekly Intelligence Synthesis ("The Context")
*   **Purpose**: Strategic view of evolving market stories.
*   **Frequency**: Weekly (Sunday).
*   **Content**:
    *   Lifecycle review of major narratives (Born -> Reinforced -> Resolved).
    *   Multi-asset correlation analysis (Cluster visualizations).
    *   Emerging themes (Low confidence, high severity events).
*   **Target Audience**: Portfolio Managers, Strategists.

### C. Thematic Deep Dive ("The Alpha Note")
*   **Purpose**: Research into structural cross-market phenomena.
*   **Frequency**: Ad-hoc (Triggered by Alpha Discovery).
*   **Content**:
    *   Specific hypothesis (e.g., "US Tech leading India IT").
    *   Statistical evidence (Confidence, Decay, Lag).
    *   Historical validation metrics.
*   **Target Audience**: Quants, Researchers.

### D. Cross-Market Flash ("The Bridge")
*   **Purpose**: Immediate notification of inter-marker spillover.
*   **Frequency**: Real-time / Event-driven.
*   **Content**:
    *   "US Event X impacts India Sector Y."
    *   Quantified lag and correlation strength.

---

## 3. Canonical Report Structure

All reports must adhere to this JSON-compatible schema structure ensuring readability and consistency.

### Section 1: Header
*   **Title**: Standardized Narrative Title (e.g., "Narrative Update: Tech Sector Rotation").
*   **Date/Time**: UTC with Local conversions.
*   **Global Confidence Score**: Aggregate score (0-100) of all underlying components.
*   **Sentiment Badge**: Neutral / Bullish Lean / Bearish Lean (derived, not predicted).

### Section 2: Executive Summary (The "What")
*   **Format**: Maximum 3 sentences.
*   **Source**: LLM summarization of the highest-weight Narrative.
*   **Constraint**: No speculative verbiage.

### Section 3: Core Narratives (The "Why")
*   **Structure**: List of defined Narratives.
*   **For each Narrative**:
    *   *Headline*
    *   *Confidence & Lifecyle State*
    *   *Supporting Assets* (e.g., AAPL, MSFT)
    *   *Key Events* (e.g., "Momentum Signal @ 14:00", "Volume Spike @ 14:30")

### Section 4: Signal Evidence Drill-Down
*   **Purpose**: Audit trail.
*   **Content**: Table of top 5 signals contributing to the Narratives.
*   **Fields**: Asset, Signal Type, Raw Strength, Discovery Time.

### Section 5: Uncertainty & Risk
*   **Purpose**: Intellectual honesty.
*   **Content**:
    *   "Confidence Decay": How much the data has aged.
    *   "Conflicting Signals": Evidence contradicting the main narrative.
    *   "Reliability Score": Historical accuracy of similar patterns.

---

## 4. Confidence Semantics

### Roll-Up Logic
1.  **Signal Confidence**: Base layer. Calculated by Context Engine (Vol, Regime).
2.  **Narrative Confidence**:
    $$ C_{narrative} = \min(100, \text{Avg}(C_{signals}) + \text{ReinforcementBonus}) \times \text{DecayFactor} $$
3.  **Report Confidence**:
    $$ C_{report} = \text{WeightedAvg}(C_{narratives}) $$

### Visual Representation
*   **High (80-100)**: Solid, Bold.
*   **Medium (50-79)**: Standard opacity.
*   **Low (<50)**: Translucent, explicit "Low Confidence" warning icon.

---

## 5. Lifecycle & Versioning

*   **Immutability**: Once published, a report ID is frozen.
*   **Corrections**: Errors generate a **New Report** (v2) which explicitly links to and marks v1 as `SUPERSEDED`.
*   **Retractions**: If an underlying signal is `INVALIDATED` post-publication, the digital version of the report must display a "Recall" banner linking to the invalidation event.

---

## 6. Commercialization Guardrails

To ensure regulatory safety and product integrity:

| Allowable | Forbidden |
| :--- | :--- |
| "Bullish Momentum Detected" | "Buy Now" |
| "Historical probability is 60%" | "You will make money" |
| "Price is extending" | "Price target is $150" |
| "Confidence is Low" | Ignored/Hidden confidence |
| "Similar to 2008 pattern" | "Crash imminent" |

**Mandatory Disclaimer Footer**:
> *This report is generated by an automated intelligence system for informational research purposes only. It is not financial advice. Past performance of signals does not guarantee future results.*

---

## 7. Explicit Non-Goals

1.  **No Portfolio Management**: We do not track PnL, suggest sizing, or manage risk limits.
2.  **No Execution**: We do not route orders.
3.  **No Prediction**: We do not forecast *future* prices; we characterize *current* and *recent* behavior.
