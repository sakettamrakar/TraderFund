# Integration Reality Run - UI Violation Audit

## Executed Checks
- Backend inspection verification: `python scripts/verify_inspection_backend.py`
- Static keyword scan over dashboard sources for direct buy/sell/recommend terms.

## Results
| Check | Result | Evidence |
|---|---|---|
| System status API reachable | PASS | `docs/irr/runtime/IRR-2026-02-09-001/13_ui_backend_verify.log` |
| Execution gate displayed as CLOSED | PASS | `docs/irr/runtime/IRR-2026-02-09-001/13_ui_backend_verify.log` |
| Inspection scenarios (`S1-S4`) available | PASS | `docs/irr/runtime/IRR-2026-02-09-001/13_ui_backend_verify.log` |
| Direct buy/sell action text in frontend components | PASS (none found in component source) | source scan output during IRR |

## UI Epistemic Failure Findings
| ID | Severity | Observation | Evidence |
|---|---|---|---|
| `UIE-001` | MEDIUM | Epoch-truth inconsistency across data sources can present conflicting temporal truth in UI (`TRUTH_EPOCH_2026-02-07_01` vs `TE-2026-01-30`). | `docs/epistemic/truth_epoch.json`, `docs/intelligence/execution_gate_status.json`, `docs/intelligence/temporal/temporal_state_US.json` |

## Conclusion
UI transport and inspection endpoints are operational. Epistemic consistency of displayed temporal truth is not guaranteed due upstream source divergence.
