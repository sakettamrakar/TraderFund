# Scope & Boundaries

## The Three Worlds

> These boundaries are non-negotiable. Violation corrupts the entire system.

| World | Purpose | Characteristics |
| :--- | :--- | :--- |
| **Production** | Live capital operations | Stable, conservative, slow-changing, boring by design |
| **Research** | Experimental validation | Failure-tolerant, isolated, requires governance passage |
| **Vision** | Conceptual exploration | Non-actionable, awareness-only, strictly no execution wiring |


**Critical Rules:**
- Vision items MUST NOT leak into Production
- Research items MUST pass governance before Production
- Production remains boring by design

*Source: `docs/VISION_BACKLOG.md`*

## Current Phase: Research & Validation (Shadow Mode)

*Source: `docs/epistemic/current_phase.md`*

### In Scope (Levels 0-9)

- **Foundation (L1-L3)**:
    - **Regime**: Volatility, Liquidity, Risk State (Gatekeeper).
    - **Narrative**: News, Earnings, Macro Events (Context).
    - **Meta-Analysis**: Signal Trust Scores.
- **Strategy & Discovery (L4-L7)**:
    - **Factor**: Momentum, Value, Quality, Volatility factors.
    - **Strategy**: Playbook matching (e.g., "Deep Value in Bull Market").
    - **Discovery Lenses**:
        - *Narrative*: Theme-driven ideas.
        - *Factor*: Statistical reward patterns.
        - *Fundamental*: Balance Sheet, Valuation, Margins.
        - *Technical*: Price Action, Breakouts.
    - **Convergence**: Scoring and Merging into unified candidates.
- **Constraints (L8-L9)**:
    - **Execution**: Risk Limits, Position Sizing.
    - **Portfolio**: Diagnostic checks ("Fighting Regime", "Narrative Risk").
- **Output**: Curated Watchlists & Diagnostic Reports (Reasoning First).



### Out of Scope (Current Phase)

- Automated live execution (no live money orders)
- Portfolio optimization (covariance matrices, risk parity)
- Complex derivatives
- External investor reporting

## Explicit Non-Goals (System-Wide)

- **Live Execution (Level 12)**: No live money orders (Strictly Out of Scope).
- **Advisory / Simulation (Levels 10-11)**: Future phases, not current focus.
- **Price Prediction**: Characterize current probability, not forecast future price points.
- **"Black Box"**: No unexplainable logic.
- **High-Frequency Trading**: Not a microsecond arbitrage system.


*Sources: `docs/epistemic/project_intent.md`, `docs/research_product_architecture.md`*

## Primary User & Capital Profile
- **Capital**: ≤ ₹1 Cr (Small-Mid Cap Institutional).
- **Style**: Research-Lead Discretionary.
- **Authority**: Human always decides. System advises.
- **Goal**: Superior risk-adjusted returns through situational clarity.
- **Constraints**: 
    - No HFT / Latency dependency.
    - No excessive leverage.

## Time Horizon Bands
| Band | Typology | Focus |
| :--- | :--- | :--- |
| **Tactical** | Days - Weeks | Momentum / Flow / Technicals |
| **Strategic** | Months - Quarters | Narrative / Earnings / Seasonal |
| **Structural** | 1 - 5 Years | Valuation / Secular Transformation |
*Max Horizon: 5 Years.*

## Portfolio Intelligence & Advisory
- **Scope**: Diagnostic + Advisory Intelligence.
- **Function**:
    - Detects regime misalignment ("Holding Defensive in Risk-On").
    - Suggests exposure adjustments ("Trim Tech").
    - Monitors horizons drift ("Tactical trade became bag-holding").
- **Constraint**: No automated execution of rebalancing.

## Research Exit Criteria
To graduate from Research to Production Candidate:
1.  **Regime Stability**: Strategy performs predictably across 2+ distinct regimes.
2.  **Lens Consensus**: High-conviction ideas consistently outperform baseline.
3.  **Drawdown Control**: Max DD < defined threshold in simulation.


*Source: `docs/us_market_engine_design.md`*
