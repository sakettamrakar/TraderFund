# Evolution Evaluation Bundle

**Generated**: 2026-01-25T09:48:28.849806
**Execution Context**: Bull Volatile (BULL_VOL)
**Context Version**: 1.0.0

## 1. Strategy Activation
| strategy_id | decisions | shadow | failures | regime | timestamp |
| --- | --- | --- | --- | --- | --- |
| STRATEGY_MOMENTUM_V1 | 1 | 1 | 0 | Bull Volatile | 2026-01-25T09:48:26.453157 |
| STRATEGY_VALUE_QUALITY_V1 | 1 | 1 | 0 | Bull Volatile | 2026-01-25T09:48:26.453157 |
| STRATEGY_FACTOR_ROTATION_V1 | 1 | 1 | 0 | Bull Volatile | 2026-01-25T09:48:26.453157 |

## 2. Decision Trace Log
| timestamp | strategy_id | decision_id | action | regime | outcome |
| --- | --- | --- | --- | --- | --- |
| 2026-01-25 09:48:27.117750 | STRATEGY_MOMENTUM_V1 | DEC-001 | BUY | Bull Volatile | SHADOW_FILLED |
| 2026-01-25 09:48:27.117750 | STRATEGY_VALUE_QUALITY_V1 | DEC-002 | HOLD | Bull Volatile | SHADOW_REJECTED |

## 3. Paper P&L Summary
| strategy_id | total_pnl | sharpe | max_drawdown | regime |
| --- | --- | --- | --- | --- |
| STRATEGY_MOMENTUM_V1 | 0.0 | 0.0 | 0.0 | Bull Volatile |
| STRATEGY_VALUE_QUALITY_V1 | 0.0 | 0.0 | 0.0 | Bull Volatile |

## 4. Coverage Diagnostics
# Coverage Diagnostics Report

**Generated**: 2026-01-25T09:48:27.833981
**Active Regime**: Bull Volatile

## Regime Coverage
Status: DIAGNOSTIC_PASS for Bull Volatile
Metrics: <Pending Real Integration>


## 5. Rejection Analysis
| strategy_id | reason | count | context_regime |
| --- | --- | --- | --- |
| STRATEGY_MOMENTUM_V1 | REGIME_MISMATCH | 15 | Bull Volatile |

