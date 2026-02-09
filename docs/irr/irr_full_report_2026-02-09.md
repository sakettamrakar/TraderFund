# Integration Reality Run - Full Report (2026-02-09)

## Objective
Execute an Integration Reality Run (IRR) and immediate Shadow Reality Run to test governance behavior under frozen truth, disabled execution, and real ingestion pressure.

## What Was Executed
- Real ingestion for US and INDIA data pipelines.
- Temporal orchestration for RDT/CTT updates without TE advancement.
- Factor/regime/policy/fragility paths through both core and market-specific runners.
- Narrative runtime against real endpoint.
- UI inspection backend checks.
- Shadow decision replay using `ShadowExecutionSink` paths.

## Key Outcomes
- Governance invariants held at execution layer:
  - TE file hash unchanged.
  - Execution gate file hash unchanged.
  - No execution enablement occurred.
- Major epistemic and integration failures were surfaced:
  - Persistent temporal drift (`US +7d`, `INDIA +10d`).
  - Truth-source divergence (`TRUTH_EPOCH_2026-02-07_01` vs `TE-2026-01-30`).
  - Synthetic IN10Y injected in a reality run.
  - Context schema mismatch causing core policies to evaluate as `UNKNOWN/HALTED`.
  - Narrative endpoint failure (404) resulted in zero narrative output.

## Taxonomy Summary
| Taxonomy | Count |
|---|---:|
| Temporal Drift | 3 |
| Governance Leakage | 4 |
| Narrative Violations | 1 |
| UI Epistemic Failures | 1 |
| Honest Stagnation | 3 |

## Evidence Index
- IRR runtime bundle: `docs/irr/runtime/IRR-2026-02-09-001/`
- Shadow runtime bundle: `docs/irr/runtime/SHADOW-2026-02-09-001/`
- Daily log: `docs/irr/daily_reality_observation_log.md`
- Failure taxonomy: `docs/irr/failure_log.md`

## Final Verdict
System is not ready for controlled Truth Advancement.
