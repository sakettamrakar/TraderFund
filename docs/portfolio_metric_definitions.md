# Portfolio Metric Definitions

All metrics displayed in the TraderFund Portfolio Intelligence dashboard.

---

## Risk and Resilience Metrics

### Resilience Score
- **Definition:** Measures portfolio ability to withstand macro and market shocks.
- **Computation:** Average of diversification, concentration, regime alignment, and momentum health scores.
- **Range:** 0.0 – 1.0
- **Interpretation:**
  - < 0.4 = FRAGILE — portfolio vulnerable to market stress
  - 0.4 – 0.7 = ADEQUATE — moderately resilient
  - \> 0.7 = STRONG — robust positioning

### Concentration Score
- **Definition:** Measures how concentrated the portfolio is in few holdings.
- **Computation:** `1 - (top_3_position_weight / 100)`
- **Range:** 0.0 – 1.0
- **Interpretation:** Higher value = less concentrated = better diversified. Lower value = top 3 positions dominate.

### Macro Sensitivity
- **Definition:** How sensitive the portfolio is to macro regime changes such as interest rate shocks, inflation, and liquidity tightening.
- **Computation:** Weighted average of per-holding macro_sensitivity factor across all positions.
- **Range:** 0.0 – 1.0
- **Interpretation:** Higher = more exposed to macro shocks.

### Regime Gate State
- **Definition:** Status of macro and factor context availability.
- **Values:**
  - COMPLETE — full macro and factor context available
  - DEGRADED — partial context, conviction scores are capped
  - BLOCKED — no context available, analytics limited

---

## Exposure Engine Metrics

### Diversification Score
- **Definition:** Spread of holdings across sectors and industries.
- **Computation:** `1 - (HHI / 10000)` where HHI = Herfindahl-Hirschman Index of sector weights.
- **Range:** 0.0 – 1.0
- **Interpretation:** 1.0 = perfectly diversified across many sectors. Closer to 0 = single-sector concentration.

### Factor Balance Score
- **Definition:** Evenness of portfolio factor exposure distribution across growth, value, momentum, quality, and volatility.
- **Computation:** `max(0, 1 - 2 × stddev(factor_loadings))`
- **Range:** 0.0 – 1.0
- **Interpretation:** Higher = more balanced. Low value = single-factor dominance risk.

### Regime Alignment Score
- **Definition:** How well portfolio exposures match the current macro regime detected by TraderFund macro intelligence.
- **Computation:** Regime-dependent: favors growth tilt in RISK_ON, defensive tilt in DEFENSIVE.
- **Range:** 0.0 – 1.0
- **Interpretation:** Higher = portfolio is positioned well for current conditions.

### Composite Health
- **Definition:** Overall portfolio health metric.
- **Computation:** Average of diversification, concentration, factor balance, and regime alignment scores.
- **Range:** 0.0 – 1.0
- **Interpretation:** > 0.7 strong · 0.4–0.7 adequate · < 0.4 fragile.

---

## Concentration and Correlation Metrics

### Correlated Risk Clusters
- **Definition:** Groups of holdings that move together due to sector or factor correlation.
- **Detection:** Any sector with ≥ 3 holdings is flagged as a correlated cluster.
- **Implication:** Clusters increase hidden concentration risk — multiple positions may decline simultaneously.

### Sector HHI (Herfindahl-Hirschman Index)
- **Definition:** Numerical measure of sector concentration.
- **Computation:** Sum of squared sector weight percentages.
- **Thresholds:**
  - < 1500 = well-diversified
  - 1500 – 2500 = moderately concentrated
  - \> 2500 = highly concentrated

### Factor Overexposure
- **Definition:** Detection of disproportionate loading on a single investment factor.
- **Threshold:** Any factor weighted loading > 0.7 triggers the flag.

---

## Macro Regime Metrics

### Regime Hint
- **Definition:** Inferred macro regime state from evolution tick context.
- **Values:** DEFENSIVE, BALANCED, RISK_ON

### Regime Vulnerability
- **Definition:** Identifies portfolio exposures that could suffer under the current macro regime.
- **Flags:**
  - HIGH_CYCLICAL_EXPOSURE_IN_DEFENSIVE_REGIME
  - EXCESSIVE_DEFENSIVE_TILT_IN_RISK_ON
  - PORTFOLIO_MACRO_SENSITIVITY_ELEVATED
  - CYCLICAL_CONCENTRATION_RISK

### Macro Sensitivity Dimensions
- **Growth Regime Sensitivity:** Exposure to growth cycle changes
- **Interest Rate Sensitivity:** Cyclical sector weight as rate proxy
- **Inflation Sensitivity:** Commodity and staples weight
- **Liquidity Sensitivity:** Proportion of medium-liquidity holdings

---

## Data Provenance Fields

### Data Source
- **Values:** MCP (Model Context Protocol) | API (Kite Connect REST API)
- **Meaning:** How portfolio data was fetched from the broker.

### Portfolio Last Refresh
- **Meaning:** Timestamp of the latest portfolio data snapshot ingestion.

### Truth Epoch
- **Meaning:** System knowledge baseline. Frozen reference epoch for all analytical outputs.
- **Current:** TRUTH_EPOCH_2026-03-06_01

### Source Provenance
- **Meaning:** Canonical broker connector that produced the data.
