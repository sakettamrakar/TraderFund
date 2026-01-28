# Macro Context Schema

**File**: `docs/macro/context/macro_context.json`  
**Update Frequency**: Daily (EV-TICK)  
**Nature**: Read-Only / Explanatory

## Schema

```json
{
  "timestamp": "ISO-8601 Timestamp",
  "window_id": "TICK-{timestamp}",
  "monetary": {
    "policy_stance": "TIGHTENING | NEUTRAL | EASING",
    "rate_level": "HIGH | MID | LOW",
    "curve_shape": "INVERTED | FLAT | NORMAL",
    "real_rates": "POSITIVE | NEUTRAL | NEGATIVE"
  },
  "liquidity": {
    "impulse": "EXPANDING | STABLE | CONTRACTING",
    "credit_spreads": "TIGHT | NORMAL | WIDE",
    "funding_stress": "LOW | ELEVATED | CRISIS"
  },
  "growth_inflation": {
    "growth_trend": "ACCELERATING | STABLE | DECELERATING",
    "inflation_regime": "DISINFLATION | STABLE | INFLATION",
    "policy_growth_alignment": "SUPPORTIVE | NEUTRAL | RESTRICTIVE"
  },
  "risk": {
    "appetite": "RISK-ON | MIXED | RISK-OFF",
    "volatility": "SUPPRESSED | NORMAL | ELEVATED",
    "correlation": "LOW | NORMAL | HIGH"
  },
  "summary_narrative": "Human readable summary of the macro environment."
}
```

## Usage
- **Dashboard**: Consumes this file to render the Macro Weather Report.
- **Evolution**: Reads this file to attach context to performance windows.
- **Strategy**: **IGNORES** this file. Strategies must not read it.
