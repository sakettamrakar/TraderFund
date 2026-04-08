# Exposure Calculation Methods — Technical Reference

**Module:** `src/portfolio_intelligence/exposure_engine.py`

---

## Sector Exposure

For each holding $h_i$ with sector $s_i$ and weight $w_i$:

$$\text{sector\_allocation}[s] = \sum_{i: s_i = s} w_i$$

Dominant sector: $s^* = \arg\max_s \text{sector\_allocation}[s]$

## Industry Exposure

Identical methodology to sector exposure at the industry sub-classification level.

## Geography Exposure

For each holding $h_i$ with geography $g_i$ and weight $w_i$:

$$\text{country\_exposure}[g] = \sum_{i: g_i = g} w_i$$

## Factor Exposure

Five factor dimensions: growth ($F_g$), value ($F_v$), momentum ($F_m$), quality ($F_q$), volatility ($F_\sigma$).

Weighted average factor loading for factor $k$:

$$\bar{F}_k = \frac{\sum_i w_i \cdot F_{k,i}}{\sum_i w_i}$$

**Factor Balance Score**: Measures how evenly distributed factor exposures are.

$$\mu = \frac{1}{5}\sum_k \bar{F}_k$$

$$\sigma^2 = \frac{1}{5}\sum_k (\bar{F}_k - \mu)^2$$

$$\text{factor\_balance\_score} = \max\left(0, 1 - 2\sigma\right)$$

## Herfindahl-Hirschman Index (HHI)

Used for sector concentration measurement:

$$\text{HHI} = \sum_s (\text{sector\_allocation}[s])^2$$

- $\text{HHI} > 2500$: Concentrated portfolio
- $\text{HHI} < 1500$: Well-diversified portfolio

## Diversification Score

$$\text{diversification\_score} = \max\left(0, 1 - \frac{\text{HHI}}{10000}\right)$$

## Concentration Score

Based on top-3 position weight:

$$\text{concentration\_score} = \max\left(0, 1 - \frac{\sum_{i=1}^{3} w_{(i)}}{100}\right)$$

where $w_{(i)}$ are the weights sorted in descending order.

## Macro Regime Exposure

### Regime Inference
- If `risk_appetite = MIXED` AND `momentum_strength = weak` → DEFENSIVE
- If `risk_appetite = HIGH` → RISK_ON
- Otherwise → BALANCED

### Sensitivity Dimensions

| Dimension | Computation |
|-----------|-------------|
| Growth sensitivity | $0.8 \times \bar{F}_\sigma$ (weighted macro sensitivity) |
| Interest rate sensitivity | Cyclical sector weight / 100 |
| Inflation sensitivity | (Energy + Materials + Staples weight) / 100 |
| Liquidity sensitivity | Medium-liquidity holdings weight / 100 |

### Macro Alignment Score

Regime-dependent computation:
- **RISK_ON**: $\min(1, 1.2 \times \bar{F}_\sigma)$
- **DEFENSIVE**: $\min(1, 1.1 \times (1 - \bar{F}_\sigma) + \frac{w_{defensive}}{200})$
- **BALANCED**: $\min(1, 0.5 + \frac{w_{defensive} - w_{sensitive}}{400})$

## Composite Health

$$\text{composite\_health} = \frac{1}{4}\left(\text{diversification} + \text{concentration} + \text{factor\_balance} + \text{regime\_alignment}\right)$$

## Hidden Concentration Detection

| Detection | Condition |
|-----------|-----------|
| Correlated cluster | $\geq 3$ holdings share a sector |
| Sector concentrated | $\text{HHI} > 2500$ |
| Factor overexposed | $\max_k \bar{F}_k > 0.7$ |
