# Portfolio Metric Tooltips — Dashboard Specification

Tooltip definitions implemented in the dashboard for all portfolio intelligence metrics.

---

## Implementation

### Component: `Tooltip`
Location: `PortfolioIntelligencePanel.jsx` (inline component)

Hover-triggered popup showing:
1. **Label** — metric name (bold, accent color)
2. **Short description** — what the metric measures
3. **Interpretation guide** — how to read the value (italic)

### Component: `ExposureTooltip`
Location: `PortfolioExposurePanel.jsx` (inline component)

Same pattern, with exposure-specific definitions.

---

## Tooltip Definitions

### Risk and Resilience Panel

| Metric | Tooltip |
|--------|---------|
| Resilience Score | "Ability to withstand macro and market shocks. < 0.4 fragile · 0.4–0.7 adequate · > 0.7 strong" |
| Concentration Score | "How concentrated the portfolio is in a few holdings. Lower = more concentrated. Higher = better diversified." |
| Macro Sensitivity | "Sensitivity to macro regime changes (rates, inflation, liquidity). Higher value = more exposed to macro shocks." |

### Exposure Engine Panel

| Metric | Tooltip |
|--------|---------|
| Diversification | "Spread of holdings across sectors — 1.0 = perfectly diversified. Based on Herfindahl-Hirschman Index (HHI) of sector weights." |
| Concentration | "Inverse of top-3 position weight concentration. Lower = more concentrated in few positions." |
| Factor Balance | "Evenness of factor exposure across growth, value, momentum, quality. Higher = more balanced. Low value = single-factor dominance." |
| Regime Alignment | "How well portfolio tilt matches current macro regime. Higher = portfolio positioned for current conditions." |
| Composite Health | "Average of diversification, concentration, factor, regime scores. > 0.7 strong · 0.4–0.7 adequate · < 0.4 fragile" |
| Correlated Risk Clusters | "Holdings that move together due to sector or factor correlation. More clusters = higher hidden concentration risk." |
| Regime Vulnerability | "Portfolio exposures that could suffer under current macro regime. Flags indicate positional risks given current regime state." |

---

## Score Color Coding

| Score Range | Color | CSS Class | Label |
|-------------|-------|-----------|-------|
| ≥ 0.7 | Green (#4caf50) | `.score-strong` | strong |
| 0.4 – 0.7 | Orange (#ff9800) | `.score-adequate` | adequate |
| < 0.4 | Red (#f44336) | `.score-fragile` | fragile |

---

## Example Rendering

```
Resilience Score ⓘ
0.5822
adequate

[Hovering ⓘ shows:]
┌──────────────────────────────────┐
│ Resilience Score                 │
│ Ability to withstand macro and   │
│ market shocks.                   │
│ < 0.4 fragile · 0.4–0.7         │
│ adequate · > 0.7 strong          │
└──────────────────────────────────┘
```
