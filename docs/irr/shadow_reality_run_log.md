# Shadow Reality Run Log

## Run Identity
- Run ID: `SHADOW-2026-02-09-001`
- Date: `2026-02-09`
- Start (IST): `2026-02-09T19:15:57+05:30`
- End (IST): `2026-02-09T19:15:59+05:30`
- Duration: `~2s`

## Inputs
- US context: `docs/irr/runtime/SHADOW-2026-02-09-001/US/regime_context.json` (`UNKNOWN`)
- INDIA context: `docs/irr/runtime/SHADOW-2026-02-09-001/INDIA/regime_context.json` (`BULLISH`)
- Execution mode: `ShadowExecutionSink` only

## Commands
| Step | Command | Exit | Evidence |
|---|---|---:|---|
| 01 | `python src/evolution/bulk_evaluator.py --context <US> --output <US>` | 0 | `docs/irr/runtime/SHADOW-2026-02-09-001/01_shadow_bulk_and_replay.log` |
| 02 | `python src/evolution/decision_replay.py --context <US> --output <US>` | 0 | `docs/irr/runtime/SHADOW-2026-02-09-001/01_shadow_bulk_and_replay.log` |
| 03 | `python src/evolution/bulk_evaluator.py --context <INDIA> --output <INDIA>` | 0 | `docs/irr/runtime/SHADOW-2026-02-09-001/01_shadow_bulk_and_replay.log` |
| 04 | `python src/evolution/decision_replay.py --context <INDIA> --output <INDIA>` | 0 | `docs/irr/runtime/SHADOW-2026-02-09-001/01_shadow_bulk_and_replay.log` |

## Outputs
- US strategy activation matrix: `docs/irr/runtime/SHADOW-2026-02-09-001/US/strategy_activation_matrix.csv`
- INDIA strategy activation matrix: `docs/irr/runtime/SHADOW-2026-02-09-001/INDIA/strategy_activation_matrix.csv`
- US decision trace parquet: `docs/irr/runtime/SHADOW-2026-02-09-001/US/decision_trace_log.parquet`
- INDIA decision trace parquet: `docs/irr/runtime/SHADOW-2026-02-09-001/INDIA/decision_trace_log.parquet`

## Shadow Findings
| ID | Category | Observation | Evidence |
|---|---|---|---|
| `SH-001` | Honest Stagnation | US shadow run executed across 24 strategies under `Unknown (Error)` regime context. | `docs/irr/runtime/SHADOW-2026-02-09-001/US/strategy_activation_matrix.csv` |
| `SH-002` | Governance Leakage | Replay output emitted declarative `BUY` actions despite unknown US regime (shadow-only, no real routing). | `docs/irr/runtime/SHADOW-2026-02-09-001/US/decision_trace_log.parquet` |
| `SH-003` | Temporal Drift carry-over | Shadow run consumed the same drifted TE environment from IRR; no temporal closure occurred. | `docs/irr/runtime/IRR-2026-02-09-001/post_state.json` |

## Safety Verification
- No real execution was performed.
- No broker endpoint was called.
- No capital state file was modified for live execution.
