# Stage 1: Structural Capability

> **Pipeline Stage:** 1 of 6  
> **Purpose:** Evaluate structural health, directional bias, and volatility suitability  

## Philosophy

**BEHAVIOR-first design:** Indicators are optional evidence providers, not hard dependencies.

## Structural Behaviors

| Behavior | Question |
|:---------|:---------|
| Long-Term Bias | Is the stock aligned with its long-term structure? |
| Medium-Term Alignment | Is medium-term coherent with long-term? |
| Institutional Acceptance | Does price action suggest accumulation? |
| Volatility Suitability | Is volatility compatible with sustained moves? |

## Usage

```powershell
# Evaluate all eligible symbols from Stage 0
python -m research_modules.structural_capability.runner --evaluate

# Evaluate specific symbols
python -m research_modules.structural_capability.runner --evaluate --symbols AAPL,GOOGL,MSFT

# Output as JSON
python -m research_modules.structural_capability.runner --evaluate --symbols AAPL --json
```

## Output

**Path:** `data/structural/us/{YYYY-MM-DD}/{SYMBOL}_capability.parquet`

| Field | Type | Description |
|:------|:-----|:------------|
| `structural_capability_score` | float | 0-100 composite score |
| `behavior_breakdown` | dict | Individual behavior scores |
| `confidence_level` | string | low / moderate / high |
| `evidence_summary` | dict | Raw evidence values |

## Non-Goals

❌ Breakout detection  
❌ Momentum claims  
❌ Trading decisions  
