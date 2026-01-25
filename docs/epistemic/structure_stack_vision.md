# Structure Stack Vision Document

**Status:** Living Truth  
**Scope:** Architecture & Epistemology  
**Audience:** System Architects & Strategy Developers  

---

## 1. Executive Summary

This document defines the **Structure Stack** of the investment intelligence engine—the immutable vertical hierarchy that transforms raw chaos into structured action.

Single-strategy variables and signal-only systems fail because they conflate **observation** with **execution**. They treat "RSI < 30" as a trade instruction rather than a discrete fact about the world. This collapse of layers prevents the system from distinguishing between *what is happening* (the market state) and *what we should do about it* (the strategy).

The Structure Stack solves this by imposing strict separation. It ensures that Truth (what the market did) is never contaminated by Opinion (what we want to earn). By explicitly modeling 14 distinct layers, we ensure that every module answers exactly one irreducible question, preventing "spaghetti logic" where execution engines secretly bake in macro assumptions.

## 2. Design Philosophy

### 2.1 Markets as Adaptive Systems
We view the market not as a static dataset to must be fit, but as an evolving complex system. Therefore, the structure must be rigid enough to preserve truth, but modular enough to allow the *intelligence* within the layers to evolve without breaking the backbone.

### 2.2 Truth vs. Utility
Every layer must choose between **Truth** (fidelity to reality) and **Utility** (usefulness for trading).
- **Lower Layers (1-5)**: Must prioritize Truth. They cannot hallucinate data to make it "cleaner."
- **Upper Layers (6-14)**: Must prioritize Utility. They effectively "compress" truth into actionable decisions.

### 2.3 Explaining "Why"
A signal without context is a gamble. A signal with **Regime**, **Narrative**, and **State** context is a **Belief**. The stack exists to assemble these disparate inputs into a coherent rationale before a single dollar is risked.

---

## 3. Structure Stack Overview

The system is composed of **14 Layers**, grouped into three Functional Zones.

### Zone A: The Structural Backbone (Truth)
These layers represent the physical reality of the world. They are objective, immutable, and strategy-agnostic.
1. **The Reality Layer**: Raw Ingestion.
2. **The Time Layer**: Alignment & Ordering.
3. **The Object Layer**: Entity Resolution.
4. **The Feature Layer**: Atomic Measurement.

### Zone B: Interpretive Intelligence (Understanding)
These layers impose meaning onto the raw data. They are subjective, model-dependent, and where "Edge" is created.
5. **The Event Layer**: Discrete Change Detection.
6. **The Regime Layer**: Environmental Classification.
7. **The Narrative Layer**: Contextual Clustering.
8. **The Signal Layer**: Probabilistic Observation.
9. **The Belief Layer**: Synthesis & Conviction.

### Zone C: Expression & Execution (Action)
These layers translate internal belief into external interaction. They are constrained by physics, capital, and regulation.
10. **The Strategy Layer**: Alpha & Constraints.
11. **The Optimization Layer**: Sizing & Portfolio Construction.
12. **The Execution Layer**: Order Management.
13. **The Settlement Layer**: Accounting & Realization.
14. **The Audit Layer**: The Immutable Record.

---

## 4. Layer-by-Layer Specification

### LAYER 1: The Reality Layer (Ingestion)
* **Primary Question**: "What exactly did the external world say?"
* **Inputs**: Market APIs, RSS Feeds, Websockets, PDF Reports.
* **Outputs**: Raw JSON/Bytes (Bronze Data).
* **Time Horizon**: Immediate (Event Time).
* **Failure Mode**: Data Loss / Blindness.
* **Truth**: Purest representation of external inputs.
* **MUST NOT**: Clean, filter, or interpret data. It must log the noise exactly as received.

### LAYER 2: The Time Layer (Alignment)
* **Primary Question**: "When did we know it?"
* **Inputs**: Raw Data with messy timestamps.
* **Outputs**: UTC-aligned, Event-Time stamped data.
* **Time Horizon**: Immediate.
* **Failure Mode**: Look-ahead Bias (Fatal).
* **Truth**: The temporal ordering of reality.
* **Upstream**: Layer 1.
* **Downstream**: All layers.

### LAYER 3: The Object Layer (Identity)
* **Primary Question**: "What thing are we talking about?"
* **Inputs**: Symbols, Counters, Strings ("Apple", "AAPL", "APPL").
* **Outputs**: Canonical Entity IDs (UUIDs).
* **Time Horizon**: Slow (Reference Data).
* **Failure Mode**: Split-Brain (Treating AAPL and Apple as distinct).
* **Truth**: The mapping of names to unique entities.

### LAYER 4: The Feature Layer (Measurement)
* **Primary Question**: "What is the measurement of this state?"
* **Inputs**: Price, Volume, Text.
* **Outputs**: Indicators (RSI, Z-Score), Embeddings.
* **Time Horizon**: Fast (Stream) or Medium (Batch).
* **Failure Mode**: Garbage In, Garbage Out.
* **Truth**: Mathematical transformation of Layer 1.
* **MUST NOT**: Make predictions. It only measures "Current RSI is 80", not "RSI is too high".

### LAYER 5: The Event Layer (Detection)
* **Primary Question**: "Did something notable change?"
* **Inputs**: Features, Raw Text.
* **Outputs**: Discrete Events (`RSI_Cross`, `Earnings_Release`).
* **Time Horizon**: Fast.
* **Failure Mode**: Noise Flooding.
* **Truth**: Significant discrete moments in time.

### LAYER 6: The Regime Layer (Environment)
* **Primary Question**: "What game are we playing?"
* **Inputs**: Aggregate Volatility, Macro Data, Broad Indices.
* **Outputs**: Regime State (`high_vol_bear`, `trending_bull`).
* **Time Horizon**: Slow / Medium.
* **Failure Mode**: Wrong Game (Trading trend logic in chop).
* **Dependencies**: Layer 4 (Features) → Layer 6.

### LAYER 7: The Narrative Layer (Context)
* **Primary Question**: "Why is this happening?"
* **Inputs**: Events (L5), Text.
* **Outputs**: Narrative Clusters (Graphs of connected events).
* **Time Horizon**: Medium (Days/Weeks).
* **Failure Mode**: Hallucination / Apophenia (Seeing patterns where none exist).
* **Truth**: The semantic graph of causality.

### LAYER 8: The Signal Layer (Observation)
* **Primary Question**: "What represents an opportunity?"
* **Inputs**: Features (L4), Regimes (L6), Events (L5).
* **Outputs**: Signals (Direction, Strength, Confidence, Horizon).
* **Time Horizon**: Variable.
* **Failure Mode**: Overfitting.
* **Distinction**: A Signal is "This looks bullish". It is NOT "Buy this".

### LAYER 9: The Belief Layer (Synthesis)
* **Primary Question**: "Do I believe this signal right now?"
* **Inputs**: Signals (L8) + Narrative (L7) + Regime (L6).
* **Outputs**: Conviction Score (0.0 to 1.0) & Rationale.
* **Time Horizon**: Variable.
* **Responsibility**: Filtering valid signals that are wrong for the current context (e.g., ignoring a Bull signal in a Crash regime).

### LAYER 10: The Strategy Layer (Alpha)
* **Primary Question**: "How do we exploit this belief?"
* **Inputs**: Conviction (L9).
* **Outputs**: Target Positions / Alphas.
* **Truth**: The specific hypothesis being bet on.
* **Start of Subjectivity**: This is where "Science" becomes "Business".

### LAYER 11: The Optimization Layer (Sizing)
* **Primary Question**: "How much can we afford to bet?"
* **Inputs**: Targets (L10), Account Balance, Risk Limits, Correlations.
* **Outputs**: Portfolio Construction (Ideal Weights).
* **Failure Mode**: Ruin (Betting too big).
* **Constraint**: Must respect hard risk limits over strategy desires.

### LAYER 12: The Execution Layer (Transacting)
* **Primary Question**: "How do we get this done efficiently?"
* **Inputs**: Ideal Weights (L11) vs Current Weights.
* **Outputs**: Orders (Limit, Market, Algo).
* **Failure Mode**: Slippage / Leakage.

### LAYER 13: The Settlement Layer (Realization)
* **Primary Question**: "What do we actually own?"
* **Inputs**: Fills, Cash Flow.
* **Outputs**: Ledger, Holdings.
* **Truth**: The accountant's truth.

### LAYER 14: The Audit Layer (Memory)
* **Primary Question**: "Can we prove why we did this?"
* **Inputs**: All previous layers.
* **Outputs**: Immutable Logs, Replay Packets.
* **Failure Mode**: Legal/Epistemic Opacity.

---

## 4.1 Latent Structural Layers

> [!IMPORTANT]
> The following layers are epistemically unavoidable but may not be implemented. See [latent_structural_layers.md](file:///c:/GIT/TraderFund/docs/epistemic/latent_structural_layers.md) for full specification.

### Declared Latent Layers

| Layer | Position | Responsibility | Status |
|:------|:---------|:---------------|:-------|
| **Macro / Liquidity** | L5.5 | Central bank policy, credit conditions, systemic liquidity | LATENT |
| **Flow / Microstructure** | L5.7 | Forced flows, index rebalancing, margin calls | LATENT |
| **Volatility Geometry** | L5.8 | Term structure, skew, convexity, tail risk pricing | LATENT |
| **Factor / Style Risk** | L6.5 | Factor permissions, exposure constraints, policy layer | LATENT |

### Downstream Anticipation Requirement

Code consuming lower layers MUST anticipate that these latent layers will eventually exist. When unimplemented:
- Assume degraded confidence
- Proceed with baseline assumptions
- Do NOT assume these layers will never exist

### Related Documents

- [latent_structural_layers.md](file:///c:/GIT/TraderFund/docs/epistemic/latent_structural_layers.md) — Full layer declarations
- [factor_layer_policy.md](file:///c:/GIT/TraderFund/docs/epistemic/factor_layer_policy.md) — Factor Layer as policy layer
- [flow_microstructure_layer.md](file:///c:/GIT/TraderFund/docs/epistemic/flow_microstructure_layer.md) — Flow/Microstructure documentation

---

## 5. Structural Layers vs. Replaceable Engines

It is critical to distinguish between the **Slot** (The Layer) and the **Card** (The Engine).

*   **Non-Negotiable (The Slots)**:
    *   You generally **cannot remove** Layer 2 (Time), Layer 6 (Regime), or Layer 12 (Execution) without breaking the system's ability to function rationally.
    *   These structural boundaries are fixed.

*   **Replaceable (The Cards)**:
    *   **The Engine** inside Layer 7 (Narrative) can be an LLM today, a Graph DB tomorrow, or a human Analyst next year. The *interface* remains: `Events -> Narrative`.
    *   **The Engine** inside Layer 11 (Optimization) can be Mean-Variance today and Kelly Criterion tomorrow.

**Rule**: Improvements happen by swapping Engines *within* Layers, not by merging Layers.

---

## 6. Interaction Contracts

Because layers represent different types of truth, they communicate via strict contracts:

1.  **State Vectors Only**: Layers communicate via stateless data snapshots. Layer 8 passes a `Signal Object` to Layer 9, not a reference to its internal memory.
2.  **No Upstream Contamination**: Layer 10 (Strategy) cannot tell Layer 6 (Regime) "I want to trade, so please say it's a Bull Market." Data flows Down. Feedback flows to *Design*, not *State*.
3.  **The "Context" Wrapper**: When a lower layer passes data up, it is wrapped in context.
    *   *Bad*: `Price = 100`
    *   *Good*: `Price = 100, Regime = High_Vol, Time = 12:00 UTC, Conf = 0.9`

**Example Flow (Macro → Factor → Momentum)**:
1.  **Regime (L6)** detects `Inflationary_environment`.
2.  **Strategy (L10)** receives this context. It deprecates `Growth_Factor` signals and promotes `Value_Factor` signals.
3.  **Execution (L12)** sees valid `Value` orders and executes.

---

## 7. Common Misunderstandings

*   **Indicators ≠ Layers**: An RSI is a *Feature* (L4). It is not a layer itself.
*   **ML ≠ Intelligence**: Machine Learning is just an implementation detail (an Engine) that can live in Layer 4 (Prediction), Layer 6 (Cluster), or Layer 11 (Optimize). It is not a magic box that replaces the stack.
*   **Narratives ≠ Opinions**: A Narrative (L7) is a structural cluster of events ("Stocks fell because Rates rose"). An Opinion (L10) is a bet ("Therefore I short"). You can accept the Narrative and reject the Opinion.

---

## 8. Versioning & Evolution

Do not version the Stack (v1, v2). Version the **Engines**.

*   `RegimeEngine v1.0` (Simple Volatility Filter)
*   `RegimeEngine v2.0` (HMM Model)

**Adding a New Layer**:
Only add a layer if it answers a fundamentally *new* question that cannot be answered by an existing layer.
*   *Example*: "Sentiment Analysis" is NOT a new layer. It is a feature (L4) or an event (L5).
*   *Example*: "Compliance/Legal Check" might be a sub-layer of L11 (Optimization) or a new L11.5 if it vetoes perfectly valid portfolios.

**Safe Deprecation**:
To deprecate a layer (e.g., removing Narratives to run pure Quant), you effectively replace the Engine with a "Pass-Through" or "Null" engine that returns `Neutral/Empty` context, ensuring downstream consumers don't crash.

---

## 9. Guiding Principles

1.  **Truth Before Utility**: Never corrupt the data to make the backtest look better.
2.  **One Question Per Layer**: If a class answers "What is the trend?" AND "How much do we buy?", it is broken. Split it.
3.  **Context Flows Down, Capital Flows Up**: Information cascades down the stack to inform decisions; Risk/Capital constraints bubble up to limit exposure.
4.  **Implicit is Fatal**: If a rule isn't written in a Layer, it doesn't exist. Assumptions lead to ruin.
5.  **The Stack Survives the Strategy**: Strategies die. The system that observes reality and executes orders should outlive any single alpha.
