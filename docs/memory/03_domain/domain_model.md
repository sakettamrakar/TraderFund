# Domain Model

## Cognitive Hierarchy Concepts

### Level 0: Purpose
- **Situational Awareness**: The existential goal. Clarity over prediction.

### Level 1: Regime (Market Reality)
- **Characterizes**: Volatility, Trend, Liquidity.
- **Output**: Risk-On / Risk-Off / Transition / Stress.
- **Function**: Supervisory gate for all downstream layers.

### Level 2: Narrative (Change Explanation)
- **Causal explanation**: Reconstructs market change (e.g., Policy, Geopolitics).
- **Attributes**:
    - `stage`: Born / Reinforced / Resolved
    - `confidence`: Probability of impact
    - `scope`: Market / Sector / Asset
    - `horizon`: Duration of effect

### Level 3: Meta-Analysis (Trust Filter)
- **Signal reliability**: Evaluation of tool effectiveness in current regime.
- **Output**:
    - `validity_scores`: Is this signal trustworthy?
    - `confidence_modifiers`: Adjusting conviction.

### Level 4: Factor Analysis (Reward Map)
- **FactorSignal**:
    - `strength`: Magnitude of factor return.
    - `direction`: Long or Short bias.
    - `stability`: Persistence of factor.
    - `horizon`: Relevance timeframe.

### Level 5: Strategy Selection (Playbook)
- **Conditional playbooks**: Activated by Regime + Factors (e.g., "Deep Value Playbook").

### Level 6: Opportunity Discovery (Parallel Lenses)
- **Parallel Idea Generation**: Each lens produces an `OpportunityCandidate`.
- **Primary Lenses**:
    1.  **Narrative Lens**: Theme-driven (Geopolitics, Macro).
    2.  **Factor Lens**: Statistical reward patterns.
    3.  **Fundamental Lens**: Valuation dislocation.
    4.  **Technical Lens**: Price action setups.
    5.  **Strategy Lens**: Playbook screens.
- **OpportunityCandidate**:
    - `symbol`: Ticker.
    - `source_lenses`: Which lenses triggered?
    - `horizon`: Tactical/Strategic.
    - `preliminary_scores`: Initial signal strength.

### Level 7: Convergence & Scoring
- **CandidateAssessment**:
    - `narrative_score`: Alignment with themes.
    - `factor_score`: Alignment with rewarded styles.
    - `fundamental_score`: Structural quality.
    - `technical_score`: Timing efficiency.
    - `regime_alignment`: Gating multiplier.
    - `horizon`: Unification of timeframes.
- **Output**:
    - `HighConvictionIdeas`: Multi-lens convergence.
    - `Watchlist`: Single-lens candidates requiring monitoring.

### Level 8: Execution Constraints
- **ExecutionEnvelope**:
    - `max_position_size`: Hard cap per asset.
    - `exposure_caps`: Sector/Factor limits.
    - `drawdown_limits`: Stop-loss thresholds.
    - `risk_budget`: Total allowable VaR.

### Level 9: Portfolio Intelligence
- **PortfolioDiagnostic**:
    - `RegimeConflict`: Holding risk-off assets in risk-on regime?
    - `NarrativeDecay`: Holding assets whose story has ended?
    - `FactorMismatch`: Fighting the tape?
    - `HorizonMismatch`: Trading short-term signals with long-term capital?
    - `ConcentrationRisk`: Too much exposure to one driver.
- **Output**: Red / Orange / Yellow / Green flags (Advisory Intelligence).

## Shared Concepts

### TimeHorizon
- **UltraShort**: Intraday / Hours.
- **Short**: Days - Weeks.
- **Medium**: Months - Quarters.
- **Long**: 1 - 5 Years.




## Relationships

```
```
Regime (L1) → Meta (L3) → Factor (L4) → Strategy Selection (L5)
Regime (L1) → Opportunity Discovery (L6)
Regime (L1) → Convergence & Scoring (L7)

[Narrative, Factor, Fundamental, Technical, Strategy] → Opportunity Candidates (L6)

Candidates → Convergence & Scoring (L7) → Ranked Pool

Ranked Pool + ExecutionEnvelope (L8) + PortfolioDiagnostics (L9) → Actionable Watchlists
```





## Terminology Conventions

- **Glass-Box**: Opposite of black-box; all logic observable and explainable
- **Shadow Mode**: System runs but does not execute real trades
- **Clinical Review**: Human post-trade analysis of generated signals
- **Orphan**: A data gap — missing expected data in a time series
- **Genesis**: The signal generation and narrative creation process
