# Research Module Governance

## 1. PURPOSE OF THIS DOCUMENT

This document serves as the authoritative boundary between **Live Trading Operations** and **System Research**. The stability of the TraderFund platform and the safety of its capital rely on the absolute separation of experimental logic from production execution.

### Policy Objectives:
- **Capital Preservation:** Research modules must be technically incapable of accidentally initiating or modifying trades.
- **Architectural Integrity:** Prevent "feature creep" from eroding the simple, verifiable logic of the Momentum Engine.
- **Controlled Evolution:** Provide a clear, multi-stage path for research insights to earn their way into production.

**Philosophy:** Research insight does not equal trading authority. Capital protection always overrides feature velocity.

---

## 2. LIST OF RESEARCH MODULES (AUTHORITATIVE)

### 2.1 Backtesting Engine
- **Purpose:** To validate historical performance of strategies and signal logic using high-fidelity historical data.
- **Allowed:** 
    - Reading historical data from `data/processed/`.
    - Simulating order execution with realistic slippage and commission models.
    - Parameter optimization and sensitivity analysis.
- **Explicitly NOT Allowed:** 
    - Connecting to live broker APIs.
    - Accessing live market data streams.
    - Persisting results into production logs.
- **Current Status:** RESEARCH-ONLY
- **Planned Activation Phase:** Phase 6+ (Pre-production validation gate)

### 2.2 Volatility / Market Context Analysis
- **Purpose:** To categorize market regimes (Low Volatility, High Volatility, Trending, Range-bound) to provide context for signals.
- **Allowed:** 
    - Calculating ATR, VIX, and regime descriptors.
    - Offline correlation analysis between regimes and signal performance.
- **Explicitly NOT Allowed:** 
    - Modifying production signal thresholds at runtime.
    - Dynamically adjusting Momentum Engine parameters based on live volatility.
- **Current Status:** RESEARCH-ONLY
- **Planned Activation Phase:** Phase 7+

### 2.3 Risk Modeling & Position Sizing
- **Purpose:** To develop sophisticated capital allocation models (e.g., Kelly Criterion, Volatility-Adjusted Sizing).
- **Allowed:** 
    - Calculating theoretical "ideal" position sizes for past trades.
    - Stress-testing portfolios against historical "black swan" events.
- **Explicitly NOT Allowed:** 
    - Overriding the Momentum Engine's fixed position sizing logic.
    - Modifying `Max Account Risk` or `Max Symbol Risk` variables.
- **Current Status:** RESEARCH-ONLY
- **Planned Activation Phase:** Phase 8+

### 2.4 News & Sentiment Analysis
- **Purpose:** To gauge broader market sentiment and avoid trading into high-impact news events.
- **Allowed:** 
    - Ingesting external news feeds and social media data.
    - Generating sentiment scores for offline analysis.
- **Explicitly NOT Allowed:** 
    - Triggering emergency exits or "halt trading" signals.
    - Introducing external network latency into the core processing loop.
- **Current Status:** RESEARCH-ONLY
- **Planned Activation Phase:** Phase 9+

---

## 3. GLOBAL GUARDRAILS (NON-NEGOTIABLE)

The following structural guardrails are mandatory for all research modules. 

| Guardrail | Implementation | Rationale |
| :--- | :--- | :--- |
| **Physical Isolation** | Must reside in `research_modules/` | Prevents accidental inclusion in production builds or deployments. |
| **Import Barrier** | No `core_modules/` imports | Production code must be unaware of research code existence to prevent coupling. |
| **Execution Isolation**| No runtime hooks | Research modules cannot register callbacks or enter the main event loop. |
| **Runtime Kill-Switch**| `ACTIVE_PHASE` check | Any method with "side effects" must throw a `SecurityException` if `PHASE < 6`. |
| **Configuration Guard**| Explicit `ENABLED` flag | Deployment configs must default research flags to `FALSE`. |
| **Warning Headers** | Mandatory code headers | Every file must start with: `## RESEARCH ONLY - NOT FOR LIVE TRADING ##` |

---

## 4. ACTIVATION RULES (CRITICAL SECTION)

Removing a guardrail is a high-gravity event. The following conditions must be met for **EACH** module before it is promoted to production:

1.  **Phase Threshold:** The project must reach the module's defined "Planned Activation Phase."
2.  **Observation Period:** Minimum 30 trading days of error-free data logging in the "Research" state.
3.  **Paper Trading:** 100 consecutive successful simulated trades with < 5% slippage variance from the model.
4.  **Human Approval:** Explicit architectural sign-off recorded in `docs/governance/ACTIVATION_LOG.md`.
5.  **Audit Trail:** Promotion must be a single, dedicated PR tagged `[PROMOTION]`.
6.  **Test Coverage:** Minimum 90% unit test coverage and successful integration test pass.

**Promotion is Reversible:** Any module showing anomalous behavior in production will be immediately reverted to "Research-Only" status via the global kill-switch.

---

## 5. FORBIDDEN ACTIONS

These actions are NEVER allowed, regardless of the implementation phase:
- **Auto-Optimization:** AI or algorithms automatically updating production strategy parameters.
- **Signal Overriding:** Research modules logic overriding the core Momentum Engine signal logic.
- **Trusting Backtests:** Deploying any logic based on backtests without a live "observation" period.
- **Module Multi-Wiring:** Connecting more than one research module to the core loop simultaneously during the initial rollout.

---

## 6. CHANGE CONTROL & VERSIONING

- **Document Updates:** This document can only be modified via a Pull Request with a "Senior Architect" review.
- **Version Control:** All removals of guardrails must be documented in the version history.
- **Integrity Check:** Whenever a "shortcut" is proposed, refer back to the *Philosophy* in Section 1.

---

## 7. FINAL DECLARATION

**The preservation of capital is our foundational metric.** 

Feature richness is secondary to execution reliability. We acknowledge that research insights are hypotheses until proven in live market conditions. We commit to moving only as fast as our safety guardrails allow.

*Signed,*
*Senior Trading Platform Architect*
*TraderFund Project*
