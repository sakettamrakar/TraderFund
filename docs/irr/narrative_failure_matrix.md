# Integration Reality Run - Narrative Failure Matrix

## Reality Inputs
- Narrative runtime command: `python scripts/run_real_market_stories.py`
- Endpoint used: `http://localhost:8000/api/public/market-stories?limit=10`
- Result: `404` response, `0` stories ingested, `0` narratives persisted.

## Matrix
| Check | Result | Classification | Evidence |
|---|---|---|---|
| Real source reachable | FAIL | Narrative Violations | `docs/irr/runtime/IRR-2026-02-09-001/12_real_market_stories.log` |
| Narrative generation occurred | FAIL | Honest Stagnation | `docs/irr/runtime/IRR-2026-02-09-001/12_real_market_stories.log` |
| Recommendation language present in generated narratives | NOT TESTABLE (no narratives) | Narrative Violations | `docs/irr/runtime/IRR-2026-02-09-001/12_real_market_stories.log` |
| Regime-tagged explainability attached | NOT TESTABLE (no narratives) | Narrative Violations | `docs/irr/runtime/IRR-2026-02-09-001/12_real_market_stories.log` |

## Interpretation
Narrative layer did not fail by hallucinating output; it failed by absence of real narrative intake. This is a governance-relevant failure because the system cannot produce auditable narrative truth under live endpoint conditions.
