# Factor Context Schema

**Version**: 1.1.0
**Type**: Observational Context
**Layer**: Execution (Evolution Phase)

## Overview
The Factor Context provides a resolved, observational view of market factors (Momentum, Value, Quality, Volatility) for specific evaluation windows. It explains "suitability" for strategy deployment.

## Schema Definition

### 1. Metadata
```yaml
version: "1.1.0"
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
  notes: string | null
```

## Usage Guidelines
1.  **Observational Only**: These fields describe *what is happening*, not *what to do*.
2.  **Compatibility**: v1 consumers may continue to read root-level keys (e.g., `momentum.strength`), which are aliases for `momentum.level.state`.
3.  **No Gating**: Strategies must not gate execution on v1.1 fields (acceleration, etc.) without explicit governance approval.
