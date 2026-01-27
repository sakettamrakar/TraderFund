# Factor Context Schema

**Version**: 1.2.0
**Type**: Observational Context
**Layer**: Execution (Evolution Phase)

## Overview
The Factor Context provides a resolved, observational view of market factors (Momentum, Value, Quality, Volatility) for specific evaluation windows. It explains "suitability" for strategy deployment.

## Schema Definition

### 1. Metadata
```yaml
version: "1.3.0"
computed_at: ISO8601_TIMESTAMP
window:
  start: ISO8601_TIMESTAMP
  end: ISO8601_TIMESTAMP
```

### 2. Factors

#### Momentum `momentum`
Describes the strength and character of price persistency.
```yaml
momentum:
  level:
    state: enum [strong | neutral | weak | absent]
    confidence: float [0.0-1.0]
    # v1 Compatibility: 'strength' maps to 'level.state'
  acceleration:
    state: enum [accelerating | decelerating | flat]
    confidence: float
  persistence:
    state: enum [persistent | intermittent | fading]
    confidence: float
  breadth:
    state: enum [broad | narrow | isolated]
    confidence: float
    description: >
      Cross-asset or cross-symbol confirmation of momentum.
  dispersion:
    state: enum [expanding | contracting | stable]
    confidence: float
    description: >
      Distribution spread of returns; distinguishes leadership vs noise.
  time_in_state:
    state: enum [short | medium | long]
    confidence: float
    description: >
      Duration momentum has remained in its current state.
```

#### Value `value`
Describes the attractiveness of relative pricing.
```yaml
value:
  spread:
    state: enum [wide | neutral | narrow]
    confidence: float
    # v1 Compatibility: 'spread' exists at root
  trend:
    state: enum [improving | deteriorating | flat]
    confidence: float
  dispersion:
    state: enum [expanding | contracting | stable]
    confidence: float
    description: >
      Cross-sectional valuation dispersion; proxy for value opportunity set.
  mean_reversion_pressure:
    state: enum [high | medium | low]
    confidence: float
    description: >
      Degree to which extreme valuations are reverting.
```

#### Quality `quality`
Describes the fundamental stability/integrity of the asset universe.
```yaml
quality:
  signal:
    state: enum [positive | neutral | negative]
    confidence: float
    # v1 Compatibility: 'signal' exists at root
  stability:
    state: enum [stable | volatile]
    confidence: float
  defensiveness:
    state: enum [defensive | neutral | cyclical]
    confidence: float
    description: >
      Indicates whether quality assets behave defensively in stress.
  drawdown_resilience:
    state: enum [high | medium | low]
    confidence: float
```

#### Volatility `volatility`
Describes the risk environment character.
```yaml
volatility:
  regime:
    state: enum [expanding | contracting | stable]
    confidence: float
    # v1 Compatibility: 'state' maps to 'regime.state'
  dispersion:
    state: enum [high | medium | low]
    confidence: float
```

#### Meta `meta`
Explanatory context for human operators or high-level reasoning.
```yaml
meta:
  factor_alignment: enum [aligned | mixed | conflicting]
  momentum_quality: enum [clean | noisy | transitional]
  alpha_environment: enum [momentum_friendly | value_friendly | quality_defensive | mixed]
  notes: string | null
```

## Usage Guidelines
1.  **Observational Only**: These fields describe *what is happening*, not *what to do*.
2.  **Compatibility**: v1 consumers may continue to read root-level keys (e.g., `momentum.strength`), which are aliases for `momentum.level.state`.
3.  **No Gating**: Strategies must not gate execution on v1.1 fields (acceleration, etc.) without explicit governance approval.
